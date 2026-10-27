from copy import deepcopy

import pytest

from backend.affinity_manager import AffinityManager
from backend.errors import HalawaCoreError


class Processes:
    def __init__(self):
        self.ids = {100: '1000', 200: '2000'}
        self.tasks = {100: [(101, '1001'), (102, '1002')], 200: [(201, '2001')]}
        self.masks = {101: {0, 2, 8}, 102: {0, 2}, 201: {0, 8}}
        self.denied = set()

    def owned(self, pid, identity):
        if pid in self.denied:
            raise HalawaCoreError('Permission denied.', 403)
        if self.ids.get(pid) != identity:
            raise HalawaCoreError('Process identity changed.', 409)

    def identity(self, pid, tid=None):
        if tid is None:
            return self.ids.get(pid)
        return dict(self.tasks.get(pid, [])).get(tid)

    def threads(self, pid):
        return [{'tid': tid, 'identity': identity, 'affinity': sorted(self.masks[tid]) if self.masks[tid] is not None else None}
                for tid, identity in self.tasks[pid]]

    def related(self, pid):
        # These processes are unrelated; no implicit expansion is permitted.
        return {'related': [{'pid': pid, 'identity': self.ids[pid]}]}


class Control:
    def __init__(self, processes):
        self.processes = processes
        self.writes = []
        self.fail = None

    def get(self, pid, tid, identity=None):
        return set(self.processes.masks[tid])

    def set(self, task, cpus):
        self.writes.append((task['pid'], task['tid'], set(cpus)))
        if task['tid'] == self.fail:
            raise PermissionError('Task became inaccessible')
        self.processes.masks[task['tid']] = set(cpus)


@pytest.fixture
def batch(tmp_path):
    processes = Processes()
    control = Control(processes)
    manager = AffinityManager(processes, lambda: {'online_cpus': [0, 2, 8], 'generation': 'v1'}, tmp_path, control)
    targets = [{'pid': pid, 'identity': identity} for pid, identity in processes.ids.items()]
    return manager, processes, control, targets


def test_unrelated_processes_preview_apply_and_individual_restore(batch):
    manager, processes, control, targets = batch
    original = deepcopy(processes.masks)
    preview = manager.preview(100, '1000', [0], 'selected', selected=targets)
    assert {(t['pid'], t['tid']) for t in preview['tasks']} == {(100, 101), (100, 102), (200, 201)}
    assert preview['targets'] == targets
    assert control.writes == []
    with pytest.raises(HalawaCoreError, match='Read-only'):
        manager.apply(preview['preview_id'], True)
    manager.read_only = False
    with pytest.raises(HalawaCoreError, match='confirmation'):
        manager.apply(preview['preview_id'], False)
    record = manager.apply(preview['preview_id'], True)
    assert record['status'] == 'active' and record['targets'] == targets
    assert all(mask == {0} for mask in processes.masks.values())
    manager.read_only = True
    assert manager.restore(record['id'])['status'] == 'restored'
    assert processes.masks == original


@pytest.mark.parametrize('failure', ['reused', 'exited', 'thread_reused', 'mask_changed', 'denied'])
def test_entire_batch_validates_before_any_write(batch, failure):
    manager, processes, control, targets = batch
    preview = manager.preview(100, '1000', [0], 'selected', selected=targets)
    if failure == 'reused': processes.ids[200] = '9999'
    if failure == 'exited': del processes.ids[200]
    if failure == 'thread_reused': processes.tasks[200] = [(201, '9999')]
    if failure == 'mask_changed': processes.masks[201] = {8}
    if failure == 'denied': processes.denied.add(200)
    manager.read_only = False
    with pytest.raises(HalawaCoreError):
        manager.apply(preview['preview_id'], True)
    assert control.writes == []


@pytest.mark.parametrize('failure', ['duplicate', 'root_missing', 'empty', 'too_many', 'wrong_scope', 'mixed_scope', 'thread_mask', 'unverified'])
def test_invalid_batch_never_changes_any_task(batch, failure):
    manager, processes, control, targets = batch
    scope, related = 'selected', None
    if failure == 'duplicate': targets.append(targets[0])
    if failure == 'root_missing': targets = targets[1:]
    if failure == 'empty': targets = []
    if failure == 'too_many': targets = targets * 17
    if failure == 'wrong_scope': scope = 'threads'
    if failure == 'mixed_scope': related = [targets[0]]
    if failure == 'thread_mask': processes.masks[201] = {8}
    if failure == 'unverified': processes.masks[201] = None
    with pytest.raises(HalawaCoreError):
        manager.preview(100, '1000', [0], scope, related=related, selected=targets)
    assert control.writes == [] and manager.previews == {}


def test_partial_batch_keeps_every_original_available_for_restore(batch):
    manager, processes, control, targets = batch
    original = deepcopy(processes.masks)
    preview = manager.preview(100, '1000', [0], 'selected', selected=targets)
    manager.read_only = False
    control.fail = 201
    record = manager.apply(preview['preview_id'], True)
    assert record['status'] == 'partial'
    assert len(record['tasks']) == 3 and record['tasks'][-1]['error']
    control.fail = None
    assert manager.restore(record['id'])['status'] == 'restored'
    assert processes.masks == original


def test_batch_restore_never_writes_reused_process(batch):
    manager, processes, control, targets = batch
    preview = manager.preview(100, '1000', [0], 'selected', selected=targets)
    manager.read_only = False
    record = manager.apply(preview['preview_id'], True)
    processes.ids[200] = '9999'
    control.writes.clear()
    assert manager.restore(record['id'])['status'] == 'partial_restore'
    assert all(pid == 100 for pid, _, _ in control.writes)

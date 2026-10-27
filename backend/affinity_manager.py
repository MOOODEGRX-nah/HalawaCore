"""Confirmed task-scoped experiments. No BIOS, driver, sysfs or kernel writes exist here."""
from __future__ import annotations

import json
import os
import secrets
import threading
import time
from pathlib import Path

from .errors import HalawaCoreError
from .task_control import LinuxTaskControl


class AffinityManager:
    def __init__(self, processes, topology, data_dir: Path, control=None):
        self.processes, self.topology = processes, topology
        self.control = control or LinuxTaskControl()
        self.read_only = True
        self.previews = {}
        self.records = {}
        self.lock = threading.RLock()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    def audit(self, record):
        # No process names, arguments, environments, or credentials are persisted.
        with (self.data_dir / 'affinity-audit.jsonl').open('a', encoding='utf-8') as out:
            os.chmod(out.name, 0o600)
            out.write(json.dumps(record, sort_keys=True) + '\n')

    def preview(self, pid, identity, cpus, scope='main', related=None, task_tid=None, selected=None):
        with self.lock:
            if scope not in ('main', 'task', 'threads', 'related', 'selected'):
                raise HalawaCoreError('Unknown experiment scope.')
            if selected and scope != 'selected':
                raise HalawaCoreError('Explicit process targets require the selected-process scope.')
            if not cpus:
                raise HalawaCoreError('An empty CPU selection cannot be applied.')
            topology = self.topology()
            requested = set(cpus)
            if requested - set(topology['online_cpus']):
                raise HalawaCoreError('The selection contains offline or unknown CPUs.')
            self.processes.owned(pid, identity)
            targets = [(pid, identity)]
            if scope == 'selected':
                if not selected or len(selected) > 32 or related or task_tid is not None:
                    raise HalawaCoreError('Select between 1 and 32 explicit processes without another task scope.')
                targets = [(target['pid'], target['identity']) for target in selected]
                if len({target[0] for target in targets}) != len(targets):
                    raise HalawaCoreError('Each selected PID must appear exactly once.')
                if (pid, identity) not in targets:
                    raise HalawaCoreError('The primary process must be included in the explicit selection.')
            if scope == 'related':
                observed = {r['pid']: r['identity'] for r in self.processes.related(pid)['related']}
                for target in related or []:
                    if observed.get(target['pid']) != target['identity']:
                        raise HalawaCoreError('A selected related process changed or has no observed relationship.', 409)
                    if (target['pid'], target['identity']) not in targets:
                        targets.append((target['pid'], target['identity']))
            tasks = []
            for leader, start in targets:
                self.processes.owned(leader, start)
                rows = ([self.processes.main_task(leader)] if scope == 'main' and hasattr(self.processes, 'main_task') else
                        [{'tid': leader, 'identity': self.processes.identity(leader, leader),
                          'affinity': sorted(self.control.get(leader, leader))}] if scope == 'main' else self.processes.threads(leader))
                if scope == 'task':
                    rows = [r for r in rows if r['tid'] == task_tid]
                if not rows:
                    raise HalawaCoreError('No accessible tasks remain.', 409)
                for task in rows:
                    if task['affinity'] is None:
                        raise HalawaCoreError('An affected thread has an unsupported or unverified scheduling restriction.', 403)
                    if not requested <= set(task['affinity']):
                        raise HalawaCoreError(f"Requested CPUs exceed TID {task['tid']}'s existing affinity. Restore an earlier experiment before widening it.")
                    tasks.append({'pid': leader, 'process_identity': start, 'tid': task['tid'],
                                  'identity': task['identity'], 'original': task['affinity']})
            token = secrets.token_urlsafe(32)
            now = time.monotonic()
            self.previews = {k: v for k, v in self.previews.items() if v['expires'] > now}
            if len(self.previews) >= 128:
                self.previews.pop(next(iter(self.previews)))
            preview = {'preview_id': token, 'pid': pid, 'identity': identity, 'scope': scope,
                'targets': [{'pid': leader, 'identity': start} for leader, start in targets],
                'requested': sorted(requested), 'tasks': tasks, 'generation': topology['generation'],
                'expires': now + 60, 'expires_in_seconds': 60,
                'warnings': ['New threads and child processes are not tracked by this one-time operation.',
                             'Restoration requires this backend to remain running. Crash recovery is not implemented.']}
            if len(requested) == 1 and (len(tasks) > 1 or len(self.processes.threads(pid)) > 1):
                preview['warnings'].append('One logical CPU is selected for a multithreaded workload.')
            self.previews[token] = preview
            return preview

    def validate_task(self, task):
        self.processes.owned(task['pid'], task['process_identity'])
        if self.processes.identity(task['pid'], task['tid']) != task['identity']:
            raise HalawaCoreError('Thread identity changed; no operation performed.', 409)

    def apply(self, preview_id, confirmed):
        with self.lock:
            if self.read_only:
                raise HalawaCoreError('Read-only mode is enabled. Enable experiments in Settings first.', 403)
            if confirmed is not True:
                raise HalawaCoreError('Explicit confirmation is required.')
            preview = self.previews.pop(preview_id, None)
            if preview is None or preview['expires'] < time.monotonic():
                raise HalawaCoreError('Preview expired. Create and review a new preview.', 409)
            if preview['generation'] != self.topology()['generation']:
                raise HalawaCoreError('Topology or scheduling information changed. Review a fresh preview.', 409)
            # Validate every task before changing any. Recheck again immediately before each write.
            for task in preview['tasks']:
                self.validate_task(task)
                if set(self.control.get(task['pid'], task['tid'], task['identity'])) != set(task['original']):
                    raise HalawaCoreError('Task affinity changed since preview. Review a fresh preview.', 409)
            if any(r['status'] != 'restored' and any(
                    t['tid'] == n['tid'] and t['identity'] == n['identity']
                    for t in r['tasks'] for n in preview['tasks']) for r in self.records.values()):
                raise HalawaCoreError('Restore the active experiment on these tasks before starting another.', 409)
            ident = secrets.token_hex(12)
            record = {'id': ident, 'created_at': time.time(), 'scope': preview['scope'],
                'targets': preview['targets'],
                'requested': preview['requested'], 'tasks': [dict(t, state='pending') for t in preview['tasks']],
                'status': 'active'}
            self.records[ident] = record
            self.audit(dict(record, event='before_apply'))
            for task in record['tasks']:
                try:
                    self.validate_task(task)
                    if set(self.control.get(task['pid'], task['tid'], task['identity'])) != set(task['original']):
                        raise HalawaCoreError('Task affinity changed before application.', 409)
                    task['state'] = 'attempted'
                    self.control.set(task, set(record['requested']))
                    self.validate_task(task)
                    task['accepted'] = sorted(self.control.get(task['pid'], task['tid'], task['identity']))
                    if task['accepted'] != record['requested']:
                        raise HalawaCoreError('Kernel accepted a different CPU set; restoration remains available.', 409)
                    task['state'] = 'applied'
                except (OSError, HalawaCoreError) as exc:
                    task['error'] = str(exc)
                    # A failed set can still leave a changed mask; retain every attempted original.
                    task['state'] = 'failed'
            if any(t['state'] != 'applied' for t in record['tasks']):
                record['status'] = 'partial'
            self.audit(dict(record, event='after_apply'))
            return record

    def restore(self, experiment_id):
        # Restoration remains available after read-only mode is re-enabled.
        with self.lock:
            record = self.records.get(experiment_id)
            if record is None:
                raise HalawaCoreError('Unknown experiment in this backend session.', 404)
            for task in record['tasks']:
                if task['state'] == 'restored':
                    continue
                try:
                    self.validate_task(task)
                    self.control.set(task, set(task['original']))
                    self.validate_task(task)
                    task['restored_affinity'] = sorted(self.control.get(task['pid'], task['tid'], task['identity']))
                    if task['restored_affinity'] != sorted(task['original']):
                        raise HalawaCoreError('Original affinity could not be fully restored (CPU/cpuset availability may have changed).', 409)
                    task['state'] = 'restored'
                    task.pop('restore_error', None)
                except (OSError, HalawaCoreError) as exc:
                    task['restore_error'] = str(exc)
            record['status'] = 'restored' if all(t['state'] == 'restored' for t in record['tasks']) else 'partial_restore'
            self.audit(dict(record, event='restore'))
            return record

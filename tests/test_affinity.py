import os
import subprocess
from types import SimpleNamespace

import pytest

from backend.affinity_manager import AffinityManager
from backend.errors import HalawaCoreError
from backend.process_manager import ProcessManager


class FakeProcesses:
    def __init__(self):
        self.ids={100:'1000',101:'1001',102:'1002'}
        self.affinities={t:{0,2,8,10} for t in self.ids}
        self.deny=set()
    def identity(self,pid,tid=None):
        target=tid if tid is not None else pid
        if target not in self.ids:
            raise HalawaCoreError('Process disappeared.',409)
        return self.ids[target]
    def owned(self,pid,identity=None):
        if pid in self.deny:
            raise HalawaCoreError('Permission denied.',403)
        if self.identity(pid)!=identity:
            raise HalawaCoreError('PID reused.',409)
        return SimpleNamespace(num_threads=lambda:len(self.ids))
    def threads(self,pid):
        return [{'tid':t,'identity':self.ids[t],'affinity':sorted(a)} for t,a in self.affinities.items() if t in self.ids]
    def related(self,pid):
        return {'related':[{'pid':100,'identity':self.ids[100]}]}


@pytest.fixture
def fake_manager(tmp_path,monkeypatch):
    pm=FakeProcesses()
    topology={'online_cpus':[0,2,8,10],'generation':'v1'}
    monkeypatch.setattr(os,'sched_getaffinity',lambda tid:set(pm.affinities[tid]))
    monkeypatch.setattr(os,'sched_setaffinity',lambda tid,cpus:pm.affinities.__setitem__(tid,set(cpus)))
    manager=AffinityManager(pm,lambda:topology,tmp_path)
    return manager,pm,topology


def test_confirmation_readonly_per_thread_and_restore(fake_manager):
    manager,pm,_=fake_manager
    pm.affinities[102]={0,2}
    preview=manager.preview(100,'1000',[0],'threads')
    assert len(preview['tasks'])==3
    with pytest.raises(HalawaCoreError,match='Read-only'):
        manager.apply(preview['preview_id'],True)
    manager.read_only=False
    with pytest.raises(HalawaCoreError,match='confirmation'):
        manager.apply(preview['preview_id'],False)
    record=manager.apply(preview['preview_id'],True)
    assert record['status']=='active'
    assert all(a=={0} for a in pm.affinities.values())
    manager.read_only=True
    restored=manager.restore(record['id'])
    assert restored['status']=='restored'
    assert pm.affinities[102]=={0,2}
    assert pm.affinities[100]=={0,2,8,10}


@pytest.mark.parametrize('cpus',[[],[1],[0,999]])
def test_invalid_affinity(fake_manager,cpus):
    manager,_,_=fake_manager
    with pytest.raises(HalawaCoreError):
        manager.preview(100,'1000',cpus)


def test_per_thread_constraints(fake_manager):
    manager,pm,_=fake_manager
    pm.affinities[101]={2,10}
    with pytest.raises(HalawaCoreError,match='existing affinity'):
        manager.preview(100,'1000',[0],'threads')


def test_explicit_thread_scope_never_changes_other_threads(fake_manager):
    manager,pm,_=fake_manager
    preview=manager.preview(100,'1000',[0],'task',task_tid=102)
    assert [t['tid'] for t in preview['tasks']]==[102]
    manager.read_only=False
    record=manager.apply(preview['preview_id'],True)
    assert pm.affinities[102]=={0}
    assert pm.affinities[100]=={0,2,8,10}
    assert manager.restore(record['id'])['status']=='restored'
    with pytest.raises(HalawaCoreError):manager.preview(100,'1000',[0],'task',task_tid=999)


@pytest.mark.parametrize('failure',['exit','reuse','affinity','hotplug','permissions'])
def test_stale_preview_has_no_writes(fake_manager,failure):
    manager,pm,topology=fake_manager
    preview=manager.preview(100,'1000',[0],'threads')
    if failure=='exit':del pm.ids[100]
    if failure=='reuse':pm.ids[100]='99999'
    if failure=='affinity':pm.affinities[101]={2}
    if failure=='hotplug':topology['generation']='v2'
    if failure=='permissions':pm.deny.add(100)
    before={t:set(a) for t,a in pm.affinities.items()}
    manager.read_only=False
    with pytest.raises(HalawaCoreError):manager.apply(preview['preview_id'],True)
    assert pm.affinities==before


def test_thread_exit_during_apply_partial_restore_and_pid_reuse(fake_manager,monkeypatch):
    manager,pm,_=fake_manager
    preview=manager.preview(100,'1000',[0],'threads')
    def set_mask(tid,cpus):
        pm.affinities[tid]=set(cpus)
        if tid==100 and cpus=={0}:del pm.ids[101]
    monkeypatch.setattr(os,'sched_setaffinity',set_mask)
    manager.read_only=False
    record=manager.apply(preview['preview_id'],True)
    assert record['status']=='partial'
    assert record['tasks'][1]['state']=='failed'
    pm.ids[102]='reused'
    restored=manager.restore(record['id'])
    assert restored['status']=='partial_restore'
    assert pm.affinities[100]=={0,2,8,10}
    assert pm.affinities[102]=={0}  # Never restore a reused TID.


def test_permission_failure_during_apply_and_restore(fake_manager,monkeypatch):
    manager,pm,_=fake_manager
    preview=manager.preview(100,'1000',[0],'threads')
    def set_mask(tid,cpus):
        if tid==101:raise PermissionError('Insufficient permissions')
        pm.affinities[tid]=set(cpus)
    monkeypatch.setattr(os,'sched_setaffinity',set_mask)
    manager.read_only=False
    record=manager.apply(preview['preview_id'],True)
    assert record['status']=='partial'
    assert record['tasks'][1]['error']
    assert manager.restore(record['id'])['status']=='partial_restore'


def test_kernel_acceptance_is_verified(fake_manager,monkeypatch):
    manager,pm,_=fake_manager
    preview=manager.preview(100,'1000',[0,2])
    monkeypatch.setattr(os,'sched_setaffinity',lambda tid,cpus:pm.affinities.__setitem__(tid,{0}))
    manager.read_only=False
    record=manager.apply(preview['preview_id'],True)
    assert record['status']=='partial'
    assert 'Kernel accepted' in record['tasks'][0]['error']


def test_expiry_replay_and_nested_experiments(fake_manager):
    manager,_,_=fake_manager
    preview=manager.preview(100,'1000',[0])
    manager.previews[preview['preview_id']]['expires']=0
    manager.read_only=False
    with pytest.raises(HalawaCoreError,match='expired'):manager.apply(preview['preview_id'],True)
    preview=manager.preview(100,'1000',[0])
    manager.apply(preview['preview_id'],True)
    with pytest.raises(HalawaCoreError,match='expired'):manager.apply(preview['preview_id'],True)
    other=manager.preview(100,'1000',[0])
    with pytest.raises(HalawaCoreError,match='Restore'):manager.apply(other['preview_id'],True)


@pytest.mark.integration
def test_real_owned_sleep_apply_verify_restore(tmp_path):
    """Only the subprocess created here is modified. Always terminate it in finally."""
    child=subprocess.Popen(['sleep','30'])
    try:
        pm=ProcessManager()
        ident=pm.identity(child.pid)
        original=set(os.sched_getaffinity(child.pid))
        assert original
        manager=AffinityManager(pm,lambda:{'generation':'real-test','online_cpus':sorted(original)},tmp_path)
        preview=manager.preview(child.pid,ident,[min(original)],'threads')
        manager.read_only=False
        record=manager.apply(preview['preview_id'],True)
        assert record['status']=='active'
        assert os.sched_getaffinity(child.pid)=={min(original)}
        assert manager.restore(record['id'])['status']=='restored'
        assert os.sched_getaffinity(child.pid)==original
    finally:
        child.terminate()
        child.wait(timeout=5)

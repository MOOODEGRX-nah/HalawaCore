import os
import subprocess

import pytest

from backend.errors import HalawaCoreError
from backend.process_manager import ProcessManager


def test_parent_child_evidence_and_process_exit():
    pm=ProcessManager()
    child=subprocess.Popen(['sleep','30'])
    try:
        p=pm.detail(child.pid)
        assert p['pid']==child.pid
        assert p['uid']==os.getuid()
        assert p['affinity']==sorted(os.sched_getaffinity(child.pid))
        group=pm.related(child.pid)
        assert len(group['related'])==1
        assert group['integration']['game_process_candidates']==[]
        assert group['integration']['launch_topology_support']=='unverified'
        assert len(pm.threads(child.pid))==1
        with pytest.raises(HalawaCoreError,match='identity changed'):
            pm.owned(child.pid,'999999999999')
    finally:
        child.terminate();child.wait(timeout=5)
    with pytest.raises(HalawaCoreError):pm.identity(child.pid)


def test_same_name_is_not_process_relationship():
    pm=ProcessManager()
    first=subprocess.Popen(['sleep','30'])
    second=subprocess.Popen(['sleep','30'])
    try:
        ids={r['pid'] for r in pm.related(first.pid)['related']}
        assert first.pid in ids and second.pid not in ids
    finally:
        first.terminate();second.terminate();first.wait(timeout=5);second.wait(timeout=5)


def test_actual_wine_descendant_is_discoverable_without_environment_reads(monkeypatch):
    pm=ProcessManager()
    rows=[{'pid':10,'identity':'100','name':'steam','exe':'/usr/bin/steam','ppid':1,'uid':1000},
          {'pid':20,'identity':'200','name':'proton','exe':'/runtime/proton','ppid':10,'uid':1000},
          {'pid':30,'identity':'300','name':'Game.exe','exe':'/runtime/wine64-preloader','ppid':20,'uid':1000},
          {'pid':40,'identity':'400','name':'Game.exe','exe':'/runtime/wine64-preloader','ppid':1,'uid':1000}]
    monkeypatch.setattr(pm,'listing',lambda:rows)
    monkeypatch.setattr(pm,'detail',lambda pid:next(r for r in rows if r['pid']==pid))
    group=pm.related(10)
    assert {r['pid'] for r in group['related']}=={10,20,30}
    assert group['integration']['game_process_candidates']==[30]
    assert group['integration']['steam_ancestry_observed']
    assert group['integration']['wine_or_proton_observed']

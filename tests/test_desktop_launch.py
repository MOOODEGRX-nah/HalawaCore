import os
import subprocess
import sys
from unittest.mock import Mock

import desktop


def test_frozen_linux_restores_original_path_without_mutating_parent(monkeypatch):
    monkeypatch.setattr(sys,'platform','linux')
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.setenv('LD_LIBRARY_PATH','/tmp/_MEI_fixture:/opt/user-libs')
    monkeypatch.setenv('LD_LIBRARY_PATH_ORIG','/opt/user-libs')
    monkeypatch.setenv('DISPLAY',':0')
    parent=os.environ.copy()
    child=desktop.system_browser_environment()
    assert child['LD_LIBRARY_PATH']=='/opt/user-libs'
    assert child['DISPLAY']==':0'
    assert dict(os.environ)==parent


def test_frozen_linux_without_original_uses_system_libraries(monkeypatch):
    monkeypatch.setattr(sys,'platform','linux')
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.setenv('LD_LIBRARY_PATH','/tmp/_MEI_fixture')
    monkeypatch.delenv('LD_LIBRARY_PATH_ORIG',raising=False)
    assert 'LD_LIBRARY_PATH' not in desktop.system_browser_environment()
    assert os.environ['LD_LIBRARY_PATH']=='/tmp/_MEI_fixture'


def test_source_and_windows_keep_their_library_environment(monkeypatch):
    monkeypatch.setenv('LD_LIBRARY_PATH','/opt/user-libs')
    monkeypatch.setattr(sys,'platform','linux')
    monkeypatch.setattr(sys,'frozen',False,raising=False)
    assert desktop.system_browser_environment()['LD_LIBRARY_PATH']=='/opt/user-libs'
    monkeypatch.setattr(sys,'platform','win32')
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    assert desktop.system_browser_environment()['LD_LIBRARY_PATH']=='/opt/user-libs'


def test_linux_opener_receives_clean_child_environment_and_literal_url(monkeypatch):
    monkeypatch.setattr(sys,'platform','linux')
    monkeypatch.setattr(sys,'frozen',True,raising=False)
    monkeypatch.setenv('LD_LIBRARY_PATH','/tmp/_MEI_fixture')
    monkeypatch.delenv('LD_LIBRARY_PATH_ORIG',raising=False)
    monkeypatch.setattr(desktop.shutil,'which',lambda *a,**kw:'/usr/bin/xdg-open')
    process=Mock();process.wait.return_value=0
    launch=Mock(return_value=process);monkeypatch.setattr(desktop.subprocess,'Popen',launch)
    assert desktop.open_local_browser('http://127.0.0.1:54321')
    assert launch.call_args.args==(['/usr/bin/xdg-open','http://127.0.0.1:54321'],)
    assert 'LD_LIBRARY_PATH' not in launch.call_args.kwargs['env']
    assert not launch.call_args.kwargs.get('shell',False)
    assert os.environ['LD_LIBRARY_PATH']=='/tmp/_MEI_fixture'
    process.wait.return_value=127
    assert desktop.open_local_browser('http://127.0.0.1:54321') is False
    process.wait.side_effect=subprocess.TimeoutExpired('xdg-open',5)
    assert desktop.open_local_browser('http://127.0.0.1:54321') is True


def test_missing_opener_and_windows_browser_result(monkeypatch):
    monkeypatch.setattr(sys,'platform','linux')
    monkeypatch.setattr(desktop.shutil,'which',lambda *a,**kw:None)
    assert desktop.open_local_browser('http://127.0.0.1:54321') is False
    monkeypatch.setattr(sys,'platform','win32')
    browser=Mock(return_value=True);monkeypatch.setattr(desktop.webbrowser,'open',browser)
    assert desktop.open_local_browser('http://127.0.0.1:54321')
    browser.assert_called_once_with('http://127.0.0.1:54321')

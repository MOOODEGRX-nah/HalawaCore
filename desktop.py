"""One-click desktop entry. Runs the local UI without requiring a user-installed Python."""
from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


def system_browser_environment():
    """Restore the launcher's library path only in the external browser process."""
    environment=os.environ.copy()
    if sys.platform.startswith('linux') and getattr(sys,'frozen',False):
        original=environment.get('LD_LIBRARY_PATH_ORIG')
        if original is None:
            environment.pop('LD_LIBRARY_PATH',None)
        else:
            environment['LD_LIBRARY_PATH']=original
    return environment


def open_local_browser(url):
    if not sys.platform.startswith('linux'):
        try:return webbrowser.open(url)
        except (OSError,webbrowser.Error):return False
    environment=system_browser_environment()
    opener=shutil.which('xdg-open',path=environment.get('PATH'))
    if opener is None:return False
    try:
        process=subprocess.Popen([opener,url],env=environment,stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        try:return process.wait(timeout=5)==0
        except subprocess.TimeoutExpired:return True
    except OSError:return False


def storage_directory():
    if os.environ.get('HALAWACORE_DATA_DIR'):
        return Path(os.environ['HALAWACORE_DATA_DIR'])
    if os.name == 'nt':
        return Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'HalawaCore'
    return Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))) / 'halawacore'


def request_json(url, path, token=None, body=None):
    headers = {'Origin':url, 'Content-Type':'application/json'}
    if token:headers['X-HalawaCore-Token']=token
    req=urllib.request.Request(url+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)


def self_test(url):
    """Only change affinity on the disposable child created in this function."""
    session=request_json(url,'/api/session')
    token=session['token']
    topology=request_json(url,'/api/cpu/topology')
    assert topology['logical_cpu_count']>0
    args=[sys.executable,'--test-child'] if getattr(sys,'frozen',False) else [sys.executable,str(Path(__file__).resolve()),'--test-child']
    children=[subprocess.Popen(args) for _ in range(2)]
    result={'platform':platform.system(),'application':'HalawaCore','topology':'ok','logical_cpus':topology['logical_cpu_count'],'affinity':'not run'}
    try:
        processes=[request_json(url,f'/api/processes/{child.pid}')['root'] for child in children]
        originals={process['pid']:process['affinity'] for process in processes}
        if all(originals.values()) and topology.get('affinity_support')=='available':
            selected=min(set.intersection(*(set(cpus) for cpus in originals.values())))
            targets=[{'pid':process['pid'],'identity':process['identity']} for process in processes]
            preview=request_json(url,'/api/affinity/preview',token,{**targets[0],'cpus':[selected],'scope':'selected','targets':targets})
            assert {task['pid'] for task in preview['tasks']}==set(originals)
            request_json(url,'/api/settings',token,{'read_only':False,'display_offset':topology['display_cpu_offset']})
            record=request_json(url,'/api/affinity/apply',token,{'preview_id':preview['preview_id'],'confirmed':True})
            assert record['status']=='active',record
            assert all(task['accepted']==[selected] for task in record['tasks'])
            restored=request_json(url,'/api/affinity/restore',token,{'experiment_id':record['id']})
            assert restored['status']=='restored',restored
            for process in processes:
                assert request_json(url,f"/api/processes/{process['pid']}")['root']['affinity']==originals[process['pid']]
            result['affinity']='two explicitly selected owned children: apply, kernel verification and individual restore passed'
        else:
            result['affinity']='read-only: target scheduling state is unsupported or unverified'
    finally:
        for child in children:
            child.terminate();child.wait(timeout=10)
        request_json(url,'/api/settings',token,{'read_only':True,'display_offset':topology['display_cpu_offset']})
    return result


def run():
    parser=argparse.ArgumentParser()
    parser.add_argument('--no-browser',action='store_true',help='Print the local interface URL without opening a browser')
    parser.add_argument('--self-test',action='store_true',help='Verify packaged API using an owned disposable child')
    parser.add_argument('--self-test-file',help='Write the self-test JSON report here')
    parser.add_argument('--test-child',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.test_child:
        time.sleep(90);return 0
    if hasattr(os,'geteuid') and os.geteuid()==0:
        raise RuntimeError('Open HalawaCore as your normal desktop user, without sudo.')
    data=storage_directory();data.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.environ['HALAWACORE_DATA_DIR']=str(data)
    logging.basicConfig(filename=data/'desktop.log',level=logging.WARNING,format='%(asctime)s %(levelname)s %(message)s')
    import uvicorn
    from backend.main import create_app
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('127.0.0.1',0));sock.listen(128)
    port=sock.getsockname()[1];url=f'http://127.0.0.1:{port}'
    config=uvicorn.Config(create_app(data_dir=data,shutdown=lambda:setattr(server,'should_exit',True)),
        host='127.0.0.1',port=port,workers=1,access_log=False,log_config=None,loop='asyncio',http='h11',ws='none')
    server=uvicorn.Server(config)
    report={};errors=[]
    def ready():
        try:
            for _ in range(200):
                if server.started:break
                if server.should_exit:raise RuntimeError('Local backend did not start.')
                time.sleep(.05)
            else:raise RuntimeError('Local backend startup timed out.')
            if args.self_test:
                report.update(self_test(url));server.should_exit=True
            else:
                if sys.stdout:print(f'HalawaCore: {url}',flush=True)
                if not args.no_browser and not open_local_browser(url):
                    logging.warning('Browser could not be opened. Open this local address manually: %s',url)
                    if sys.stderr:print(f'Open this address in your browser: {url}',file=sys.stderr,flush=True)
        except Exception as exc:
            errors.append(str(exc));server.should_exit=True
    worker=threading.Thread(target=ready,daemon=True);worker.start()
    try:
        try:server.run(sockets=[sock])
        except KeyboardInterrupt:pass
    finally:sock.close();worker.join(timeout=15)
    if errors:report.update(error='; '.join(errors))
    if args.self_test_file:Path(args.self_test_file).write_text(json.dumps(report,indent=2))
    if args.self_test and sys.stdout:print(json.dumps(report))
    if errors:raise RuntimeError(errors[0])
    return 0


if __name__=='__main__':
    try:
        raise SystemExit(run())
    except Exception as exc:
        logging.exception('HalawaCore desktop failed')
        if os.name=='nt' and not any(a.startswith('--self-test') for a in sys.argv):
            import ctypes
            ctypes.windll.user32.MessageBoxW(None,str(exc),'HalawaCore',0x10)
        elif sys.stderr:
            print(f'HalawaCore: {exc}',file=sys.stderr)
        raise SystemExit(1)

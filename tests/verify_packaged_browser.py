"""Exercise a frozen Linux launcher without opening or controlling a user's browser."""
import json
import os
import queue
import threading
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def request(url,path,token=None,body=None):
    headers={'Origin':url,'Content-Type':'application/json'}
    if token:headers['X-HalawaCore-Token']=token
    req=urllib.request.Request(url+path,headers=headers,data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req,timeout=5) as response:return json.load(response)


def verify(binary):
    if sys.platform!='linux':raise RuntimeError('This launcher regression is Linux-only.')
    binary=Path(binary).resolve()
    for mode in ('browser','failed-browser','no-browser','interrupt'):
        with tempfile.TemporaryDirectory(prefix='halawacore-browser-') as temporary:
            base=Path(temporary);tools=base/'bin';tools.mkdir();marker=base/'opened.txt'
            opener=tools/'xdg-open'
            opener.write_text('#!/bin/sh\nprintf "%s\\n%s\\n" "$1" "${LD_LIBRARY_PATH-}" > "$HALAWACORE_TEST_BROWSER_MARKER"\n'+('exit 127\n' if mode=='failed-browser' else 'exit 0\n'))
            opener.chmod(0o700)
            environment={**os.environ,'PATH':str(tools)+os.pathsep+os.environ.get('PATH',''),
                'HALAWACORE_DATA_DIR':str(base/'data'),'HALAWACORE_TEST_BROWSER_MARKER':str(marker)}
            arguments=[str(binary)]+(['--no-browser'] if mode=='no-browser' else [])
            process=subprocess.Popen(arguments,env=environment,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                # The URL is flushed as soon as the server is ready, in every normal launch mode.
                lines=queue.Queue()
                thread=threading.Thread(target=lambda:[lines.put(line) for line in process.stdout],daemon=True);thread.start()
                first=lines.get(timeout=30).strip()
                assert first.startswith('HalawaCore: http://127.0.0.1:'),first
                url=first.removeprefix('HalawaCore: ')
                assert urlparse(url).hostname=='127.0.0.1'
                deadline=time.monotonic()+10
                while mode!='no-browser' and not marker.exists() and time.monotonic()<deadline:time.sleep(.05)
                if mode=='no-browser':assert not marker.exists()
                else:
                    observed=marker.read_text().splitlines()
                    assert observed[0]==url
                    assert observed[1]==environment.get('LD_LIBRARY_PATH',''),observed
                assert request(url,'/api/health')['read_only'] is True
                session=request(url,'/api/session')
                assert session['settings']['read_only'] is True
                if mode=='interrupt':process.send_signal(signal.SIGINT)
                else:assert request(url,'/api/shutdown',session['token'],{})['status']=='closing'
                assert process.wait(timeout=15)==0
                thread.join(timeout=3)
                stderr=process.stderr.read()
                assert 'Traceback' not in stderr and 'symbol lookup error' not in stderr and '[PYI-' not in stderr,stderr
                if mode=='failed-browser':assert url in stderr
            finally:
                if process.poll() is None:process.terminate();process.wait(timeout=10)
                process.stdout.close();process.stderr.close()
    print('Packaged Linux browser regression passed: clean system shell, manual fallback, --no-browser and Ctrl+C; no real browser or affinity experiment used.')


if __name__=='__main__':verify(sys.argv[1])

"""Exercise the actual bundled version probe and portable file replacement in an owned temp folder."""
import hashlib
import io
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

import psutil

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from backend.app_version import VERSION
from backend.updater import Updater, REPOSITORY, atomic_json, external_environment, sha256, probe


def stop_owned(process):
    if process.poll() is not None:return
    try:children=psutil.Process(process.pid).children(recursive=True)
    except psutil.NoSuchProcess:children=[]
    for child in reversed(children):
        try:child.terminate()
        except psutil.NoSuchProcess:pass
    process.terminate()
    try:process.wait(timeout=15)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=10)
    psutil.wait_procs(children,timeout=5)


def verify(binary):
    binary=Path(binary).resolve();windows=platform.system()=='Windows'
    with tempfile.TemporaryDirectory(prefix='halawacore-portable-update-') as folder:
        root=Path(folder);app=root/'app';app.mkdir();target=app/binary.name
        shutil.copy2(binary,target);(app/'LICENSE.txt').write_text('old license')
        probe(binary,VERSION)
        original=sha256(target)
        old=subprocess.Popen([str(target),'--test-child'],env=external_environment(),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        helper=None
        try:
            if windows:
                job=root/'data/updates'/('job-'+uuid.uuid4().hex);stage=job/'staged';stage.mkdir(parents=True)
                shutil.copy2(binary,stage/binary.name);(stage/'LICENSE.txt').write_text('new license')
                plan={'protocol':1,'kind':'portable','version':VERSION,'target':str(target),
                      'hashes':{name:sha256(stage/name) for name in [binary.name,'LICENSE.txt']},
                      'original_hash':original,'parent_pid':old.pid,'parent_identity':psutil.Process(old.pid).create_time(),'restart':False}
                atomic_json(job/'plan.json',plan)
                helper=subprocess.Popen([str(stage/binary.name),'--finish-update',str(job/'plan.json')],env=external_environment())
                time.sleep(1)
                assert not Path(str(target)+'.previous').exists(),'Helper replaced an image before the old app exited'
                stop_owned(old)
                assert helper.wait(timeout=60)==0,'Packaged Windows helper failed'
                assert json.loads((root/'data/update-result.json').read_text())['status']=='updated'
            else:
                stream=io.BytesIO()
                with tarfile.open(fileobj=stream,mode='w:gz') as bundle:
                    bundle.add(binary,arcname=binary.name)
                    data=b'new license';info=tarfile.TarInfo('LICENSE.txt');info.size=len(data);bundle.addfile(info,io.BytesIO(data))
                payload=stream.getvalue();digest=hashlib.sha256(payload).hexdigest()
                name='HalawaCore-Linux-x64.tar.gz'
                class Client:
                    def latest(self):return {'tag_name':'v'+VERSION,'draft':False,'prerelease':False,'body':'Owned native updater test','assets':[{'name':name,'size':len(payload),'digest':'sha256:'+digest,'state':'uploaded','browser_download_url':f'https://github.com/{REPOSITORY}/releases/download/v{VERSION}/{name}'}]}
                    def download(self,url,destination,size,progress):Path(destination).write_bytes(payload);progress(size);return digest
                service=Updater(root/'data',target,current_version='0.0.0',client=Client(),capability={'kind':'portable','supported':True,'reason':'owned fixture'})
                assert service.check()['can_download']
                service.download();service.worker.join(60);assert service.phase=='ready',service.error
                service.install(service.job_id,True);service.worker.join(60);assert service.phase=='restart_required',service.error
                assert old.poll() is None,'The running owned test process was unexpectedly terminated'
            assert sha256(target)==sha256(binary)
            assert sha256(Path(str(target)+'.previous'))==original
            assert (app/'LICENSE.txt').read_text()=='new license'
            assert (app/'LICENSE.txt.previous').read_text()=='old license'
            probe(target,VERSION)
        finally:
            stop_owned(old)
            if helper is not None:stop_owned(helper)
    print('Packaged portable update passed: private version probe, actual file replacement, backup and owned-process handling; no installed app or system package changed.')


if __name__=='__main__':verify(sys.argv[1])

"""Package the already verified native artifact; used identically in CI and local builds."""
import hashlib
import os
import platform
import shutil
import tarfile
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def package():
    system=platform.system();windows=system=='Windows'
    name=os.environ.get('RELEASE_ASSET','HalawaCore-Windows-x64.zip' if windows else 'HalawaCore-Linux-x64.tar.gz')
    out=ROOT/'dist/releases';out.mkdir(parents=True,exist_ok=True)
    stage=ROOT/'build/release-stage'
    if stage.exists():shutil.rmtree(stage)
    stage.mkdir(parents=True,exist_ok=True)
    executable='HalawaCore.exe' if windows else 'HalawaCore'
    shutil.copy2(ROOT/'dist/desktop'/executable,stage/executable)
    shutil.copy2(ROOT/'LICENSE',stage/'LICENSE.txt')
    shutil.copy2(ROOT/'docs/QUICKSTART.txt',stage/'READ-ME-FIRST.txt')
    report=ROOT/f'dist/self-test-{system}.json'
    if report.exists():shutil.copy2(report,stage/'verification.json')
    target=out/name
    if windows:
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
            for path in stage.iterdir():archive.write(path,path.name)
    else:
        with tarfile.open(target,'w:gz') as archive:
            for path in stage.iterdir():archive.add(path,arcname=path.name)
    (out/(name+'.sha256')).write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+name+'\n')
    return target


if __name__=='__main__':print(package())

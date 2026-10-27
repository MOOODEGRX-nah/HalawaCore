"""Prepare the existing Arch recipe from the verified Linux CI artifact, before publishing its tag."""
import hashlib
import re
import shutil
import sys
import subprocess
import tarfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def prepare(archive, output):
    archive, output=Path(archive).resolve(), Path(output).resolve()
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    recorded=Path(str(archive)+'.sha256').read_text().split()[0]
    if digest!=recorded:raise RuntimeError('Linux CI artifact checksum mismatch')
    version=(ROOT/'VERSION').read_text().strip()
    output.mkdir(parents=True,exist_ok=True)
    recipe=ROOT/'packaging/arch/halawacore-bin'
    for name in ['PKGBUILD','halawacore.desktop','halawacore.svg','LICENSE']:
        shutil.copy2(recipe/name,output/name)
    text=(output/'PKGBUILD').read_text()
    text=re.sub(r'^pkgver=.*$',f'pkgver={version}',text,flags=re.M)
    text=re.sub(r"(sha256sums=\(\s*')[0-9a-f]{64}",lambda match:match[1]+digest,text,count=1)
    (output/'PKGBUILD').write_text(text)
    shutil.copy2(archive,output/f'HalawaCore-{version}-Linux-x64.tar.gz')
    return output


def verify(package, archive):
    with tarfile.open(archive,'r:gz') as bundle:
        expected=hashlib.sha256(bundle.extractfile('HalawaCore').read()).digest()
    payload=subprocess.run(['bsdtar','-xOf',str(package),'opt/halawacore/HalawaCore'],check=True,capture_output=True).stdout
    if hashlib.sha256(payload).digest()!=expected:raise RuntimeError('Arch package changed the verified executable')
    print('Arch package payload exactly matches the verified Linux executable.')


if __name__=='__main__':
    if sys.argv[1:2]==['--verify']:verify(*sys.argv[2:])
    else:print(prepare(*sys.argv[1:]))

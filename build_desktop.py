"""Build on each target OS (or a Windows Python runtime under Wine)."""
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def build():
    os.chdir(ROOT)
    windows=platform.system()=='Windows'
    command=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--onefile',
        '--name','HalawaCore','--distpath',str(ROOT/'dist/desktop'),
        '--workpath',str(ROOT/'build/desktop'),'--specpath',str(ROOT/'build'),
        '--add-data',str(ROOT/'frontend')+os.pathsep+'frontend',
        '--paths',str(ROOT),'--collect-submodules','backend','--collect-submodules','uvicorn',
        '--hidden-import','psutil','--exclude-module','pytest','--exclude-module','tkinter']
    if windows:command+=['--windowed']
    command+=[str(ROOT/'desktop.py')]
    subprocess.run(command,check=True)


if __name__=='__main__':build()

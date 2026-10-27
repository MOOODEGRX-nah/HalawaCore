import os
import subprocess
import sys
from pathlib import Path


def test_desktop_self_test_only_owned_child(tmp_path):
    import json
    source=Path(__file__).resolve().parents[1]
    report=tmp_path/'self-test.json'
    result=subprocess.run([sys.executable,str(source/'desktop.py'),'--self-test','--self-test-file',str(report)],
        env={**os.environ,'HALAWACORE_DATA_DIR':str(tmp_path/'data')},capture_output=True,text=True,timeout=45)
    assert result.returncode==0,result.stderr
    data=json.loads(report.read_text())
    assert data['application']=='HalawaCore'
    assert data['topology']=='ok'
    if sys.platform!='win32':
        assert 'passed' in data['affinity']
        assert 'comparison passed' in data['comparison']

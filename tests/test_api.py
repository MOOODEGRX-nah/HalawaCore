import os
import subprocess
import time

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as c:
        yield c


def headers(client):
    return {'Origin':'http://127.0.0.1:8000','X-HalawaCore-Token':client.get('/api/session').json()['token']}


def test_real_read_endpoints(client):
    for path in ['/','/api/health','/api/system','/api/cpu/topology','/api/cpu/metrics','/api/processes','/api/applications','/api/profiles','/api/experiments','/openapi.json']:
        response=client.get(path)
        assert response.status_code==200,path
        assert 'Content-Security-Policy' in response.headers
    topo=client.get('/api/cpu/topology').json()
    assert set(topo['analyzer_allowed_cpus'])<=os.sched_getaffinity(0)


def test_csrf_origin_token_rebinding(client):
    body={'read_only':True,'display_offset':1}
    assert client.post('/api/settings',json=body).status_code==403
    h=headers(client)
    assert client.post('/api/settings',json=body,headers={**h,'Origin':'http://attacker.example'}).status_code==403
    assert client.post('/api/settings',json=body,headers={**h,'X-HalawaCore-Token':'wrong'}).status_code==403
    assert client.get('/api/health',headers={'Host':'attacker.example:8000'}).status_code==403
    assert client.get('/api/session',headers={'Sec-Fetch-Site':'cross-site'}).status_code==403
    assert client.post('/api/settings',json=body,headers=h).status_code==200
    assert client.get('/api/session',headers={'Origin':'http://attacker.example'}).headers.get('access-control-allow-origin') is None


def test_input_and_no_system_mode_write_route(client):
    h=headers(client)
    assert client.post('/api/affinity/preview',json={'pid':1,'identity':'1','cpus':[]},headers=h).status_code==422
    assert client.post('/api/affinity/preview',json={'pid':1,'identity':'1','cpus':[True]},headers=h).status_code==422
    assert client.post('/api/settings',json={'read_only':True,'display_offset':2},headers=h).status_code==422
    assert client.post('/api/x3d/mode',json={'mode':'cache'},headers=h).status_code==404
    assert client.post('/api/execute',json={'command':'anything'},headers=h).status_code==404


def test_profiles_create_list_delete(client):
    h=headers(client)
    created=client.post('/api/profiles',json={'name':'Test profile','cpus':[0,8],'generation':'test','note':'manual only'},headers=h)
    assert created.status_code==200
    ident=created.json()['id']
    assert client.get('/api/profiles').json()['profiles'][0]['cpus']==[0,8]
    assert client.delete('/api/profiles/'+ident,headers=h).status_code==200
    assert client.get('/api/profiles').json()['profiles']==[]


def test_recording_real_owned_subprocess(client):
    child=subprocess.Popen(['sleep','30'])
    try:
        p=client.get(f'/api/processes/{child.pid}').json()['root']
        assert 'command_summary' in p and 'cmdline' not in p and 'environ' not in p
        assert client.get(f'/api/processes/{child.pid}/threads').json()['threads']
        response=client.post('/api/experiments/start',json={'pid':child.pid,'identity':p['identity'],'phase':'baseline','interval':.5},headers=headers(client))
        assert response.status_code==200
        time.sleep(.6)
        recordings=client.post('/api/experiments/stop',json={},headers=headers(client)).json()['recordings']
        assert recordings[0]['summary']['sample_count']>=1
        assert recordings[0]['samples'][0]['affinity']==sorted(os.sched_getaffinity(child.pid))
        assert os.sched_getaffinity(child.pid)==set(p['affinity'])
    finally:
        child.terminate();child.wait(timeout=5)

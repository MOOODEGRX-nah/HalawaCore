import os
import json
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


def test_language_preference_survives_new_session_without_enabling_affinity(tmp_path):
    with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as first:
        assert first.get('/api/session').json()['preferences']['language'] is None
        assert first.post('/api/preferences',json={'language':'ar'}).status_code==403
        assert first.post('/api/preferences',json={'language':'ar'},headers=headers(first)).json()=={'language':'ar'}
        assert first.post('/api/preferences',json={'language':'fr'},headers=headers(first)).status_code==422
        assert first.post('/api/preferences',json={'language':'en','read_only':False},headers=headers(first)).status_code==422
        assert first.get('/api/health').json()['read_only'] is True
        assert first.get('/api/experiments').json()['affinity']==[]
    assert json.loads((tmp_path/'preferences.json').read_text())=={'language':'ar'}
    with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as second:
        session=second.get('/api/session').json()
        assert session['preferences']=={'language':'ar'}
        assert session['settings']['read_only'] is True
        assert second.post('/api/preferences',json={'language':'en'},headers=headers(second)).status_code==200
    with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as third:
        assert third.get('/api/session').json()['preferences']=={'language':'en'}


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
        sample=recordings[0]['samples'][-1]
        assert sample['online_cpus']
        assert sample['process_cpu_percent_device']==sample['process_cpu_percent']/len(sample['online_cpus'])
        assert os.sched_getaffinity(child.pid)==set(p['affinity'])
    finally:
        child.terminate();child.wait(timeout=5)


def test_comparison_api_is_local_readonly_and_rejects_mismatched_processes(client):
    from test_measurements import recording
    before,after=recording(),recording('b','experiment',40,400)
    client.app.state.lab.records=[before,after]
    body={'before_id':before['id'],'after_id':after['id']}
    assert client.post('/api/experiments/compare',json=body).status_code==403
    response=client.post('/api/experiments/compare',json=body,headers=headers(client))
    assert response.status_code==200
    assert response.json()['metrics']['average_process_device_percent']['difference']==-25
    assert client.get('/api/health').json()['read_only'] is True
    assert client.get('/api/experiments').json()['affinity']==[]
    after['identity']='reused'
    assert client.post('/api/experiments/compare',json=body,headers=headers(client)).status_code==409
    assert client.post('/api/experiments/compare',json={**body,'after_id':'c'*32},headers=headers(client)).status_code==404
    assert client.post('/api/experiments/compare',json={**body,'after_id':'bad'},headers=headers(client)).status_code==422


def test_process_list_exposes_raw_and_device_share_without_changing_affinity(client):
    response=client.get(f'/api/processes?q={os.getpid()}').json()
    count=response['cpu_capacity']['logical_cpu_count']
    assert count==len(set(response['cpu_capacity']['online_cpus']))
    for row in response['processes']:
        if row['cpu_percent'] is None: assert row['cpu_percent_device'] is None
        else: assert row['cpu_percent_device']==row['cpu_percent']/count
        assert row['cpu_capacity_logical_count']==count

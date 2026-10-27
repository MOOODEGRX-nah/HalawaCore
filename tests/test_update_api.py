from fastapi.testclient import TestClient

from backend.main import create_app
from test_updater import updater


def test_update_routes_are_explicit_local_and_blocked_by_active_work(tmp_path):
    service=updater(tmp_path)
    app=create_app(tmp_path/'backend',updater=service,shutdown=lambda:None)
    with TestClient(app,base_url='http://127.0.0.1:8000') as client:
        headers={'Origin':'http://127.0.0.1:8000','X-HalawaCore-Token':client.get('/api/session').json()['token']}
        assert client.get('/api/updates').status_code==200 and service.client.calls==[]
        assert client.post('/api/updates/check',json={}).status_code==403
        assert client.post('/api/updates/check',json={'url':'https://evil.test'},headers=headers).status_code==422
        assert client.post('/api/updates/check',json={},headers=headers).json()['available']
        client.post('/api/updates/download',json={},headers=headers)
        service.worker.join(10);assert service.phase=='ready'
        body={'job_id':service.job_id,'confirmed':True}
        app.state.lab.active={'test':True}
        assert client.post('/api/updates/install',json=body,headers=headers).status_code==409
        app.state.lab.active=None
        app.state.affinity.records['test']={'status':'active'}
        assert client.post('/api/updates/install',json=body,headers=headers).status_code==409
        app.state.affinity.records.clear()
        assert client.post('/api/updates/install',json={**body,'confirmed':False},headers=headers).status_code==400
        service.phase='installing'
        assert client.post('/api/affinity/apply',json={'preview_id':'a'*32,'confirmed':True},headers=headers).status_code==409
        assert client.post('/api/experiments/start',json={'pid':1,'identity':'1','phase':'baseline','interval':1},headers=headers).status_code==409
        assert client.post('/api/shutdown',json={},headers=headers).status_code==409
        service.phase='ready'
        assert client.post('/api/updates/install',json=body,headers=headers).status_code==200
        service.worker.join(10)
        assert service.phase=='restart_required' and client.get('/api/health').json()['read_only'] is True

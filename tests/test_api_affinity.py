import os
import subprocess

from fastapi.testclient import TestClient

from backend.main import create_app


def test_confirmed_api_apply_and_restore_only_disposable_child(tmp_path):
    child=subprocess.Popen(['sleep','30'])
    original=set(os.sched_getaffinity(child.pid))
    try:
        with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as client:
            token=client.get('/api/session').json()['token']
            headers={'Origin':'http://127.0.0.1:8000','X-HalawaCore-Token':token}
            process=client.get(f'/api/processes/{child.pid}').json()['root']
            selected=min(original)
            preview=client.post('/api/affinity/preview',json={'pid':child.pid,'identity':process['identity'],'cpus':[selected],'scope':'threads'},headers=headers).json()
            assert client.post('/api/affinity/apply',json={'preview_id':preview['preview_id'],'confirmed':True},headers=headers).status_code==403
            settings=client.post('/api/settings',json={'read_only':False,'display_offset':1},headers=headers)
            assert settings.status_code==200
            record=client.post('/api/affinity/apply',json={'preview_id':preview['preview_id'],'confirmed':True},headers=headers)
            assert record.status_code==200 and record.json()['status']=='active'
            assert os.sched_getaffinity(child.pid)=={selected}
            client.post('/api/settings',json={'read_only':True,'display_offset':1},headers=headers)
            restored=client.post('/api/affinity/restore',json={'experiment_id':record.json()['id']},headers=headers)
            assert restored.status_code==200 and restored.json()['status']=='restored'
            assert os.sched_getaffinity(child.pid)==original
    finally:
        child.terminate();child.wait(timeout=5)


def test_batch_api_only_changes_explicit_owned_children(tmp_path):
    children=[subprocess.Popen(['sleep','30']) for _ in range(3)]
    originals={child.pid:set(os.sched_getaffinity(child.pid)) for child in children}
    try:
        with TestClient(create_app(tmp_path),base_url='http://127.0.0.1:8000') as client:
            headers={'Origin':'http://127.0.0.1:8000','X-HalawaCore-Token':client.get('/api/session').json()['token']}
            targets=[{'pid':child.pid,'identity':client.get(f'/api/processes/{child.pid}').json()['root']['identity']} for child in children[:2]]
            common=set.intersection(*(originals[target['pid']] for target in targets))
            body={**targets[0],'scope':'selected','targets':targets,'cpus':[min(common)]}
            preview=client.post('/api/affinity/preview',json=body,headers=headers)
            assert preview.status_code==200 and preview.json()['targets']==targets
            assert {task['pid'] for task in preview.json()['tasks']}=={child.pid for child in children[:2]}
            assert client.post('/api/affinity/preview',json={**body,'targets':targets*17},headers=headers).status_code==422
            assert client.post('/api/affinity/apply',json={'preview_id':preview.json()['preview_id'],'confirmed':True},headers=headers).status_code==403
            client.post('/api/settings',json={'read_only':False,'display_offset':1},headers=headers)
            record=client.post('/api/affinity/apply',json={'preview_id':preview.json()['preview_id'],'confirmed':True},headers=headers).json()
            assert record['status']=='active'
            for child in children[:2]: assert os.sched_getaffinity(child.pid)=={min(common)}
            assert os.sched_getaffinity(children[2].pid)==originals[children[2].pid]
            client.post('/api/settings',json={'read_only':True,'display_offset':1},headers=headers)
            assert client.post('/api/affinity/restore',json={'experiment_id':record['id']},headers=headers).json()['status']=='restored'
            for child in children: assert os.sched_getaffinity(child.pid)==originals[child.pid]
    finally:
        for child in children: child.terminate();child.wait(timeout=5)

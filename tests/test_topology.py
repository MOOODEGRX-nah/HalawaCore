import pytest

from backend.cpu_topology import TopologyReader, cache_bytes, cpulist, cpumask
from conftest import CASES


@pytest.mark.parametrize('name', list(CASES))
def test_architecture_matrix(fixture_system, name):
    reader, domains = fixture_system(name)
    t = reader.discover()
    assert t['physical_core_count'] == sum(CASES[name]['domains'])
    assert t['logical_cpu_count'] == sum(len(d) for d in domains)
    assert t['cache_domain_count'] == len(domains)
    assert all(d['verified'] for d in t['cache_domains'])
    assert t['architecture'] == CASES[name].get('architecture','x86_64')
    assert len({c['key'] for c in t['cores']}) == t['physical_core_count']


@pytest.mark.parametrize('name', ['single7800x3d','single9800x3d','dual7950x3d','dual7900x3d','dual9900x3d','dual9950x3d'])
def test_x3d_uses_actual_cache_masks(fixture_system, name):
    reader, domains = fixture_system(name)
    t = reader.discover()
    expected = domains[CASES[name]['sizes'].index('96M')] if '96M' in CASES[name]['sizes'] else domains[0]
    selected = {c for d in t['cache_domains'] if d['id'] in t['x3d']['cache_domain_ids'] for c in d['logical_cpus']}
    assert selected == set(expected)
    assert all(d['die_ids'] == [77] for d in t['cache_domains'])
    assert all(d['cache_ids'] != d['die_ids'] for d in t['cache_domains'])


@pytest.mark.parametrize('mode', ['cache','frequency','future-mode'])
def test_scheduler_modes_are_read_only(fixture_system, mode):
    reader, _ = fixture_system(mode=mode)
    before = {str(p): p.read_bytes() for p in reader.sys.rglob('*') if p.is_file()}
    driver = reader.discover()['x3d']['driver']
    assert driver['current_preference'] == (mode if mode in ('cache','frequency') else None)
    assert driver['read_only'] is True
    assert before == {str(p):p.read_bytes() for p in reader.sys.rglob('*') if p.is_file()}


def test_missing_driver_does_not_disable_x3d(fixture_system):
    reader, _ = fixture_system(mode=None)
    t = reader.discover()
    assert t['x3d']['driver']['status'] == 'unsupported'
    assert t['x3d']['cache_domain_ids']


def test_missing_cppc_does_not_disable_cache(fixture_system):
    reader, _ = fixture_system(missing_cppc=True)
    t = reader.discover()
    assert t['features']['cppc'] == 'unknown'
    assert t['x3d']['cache_domain_ids']
    assert t['x3d']['frequency_domain_ids']


@pytest.mark.parametrize('missing', ['missing_cache','missing_mask'])
def test_unknown_cache_is_never_fabricated(fixture_system,missing):
    reader, _ = fixture_system(**{missing:True})
    t = reader.discover()
    assert t['cache_domains'] == []
    assert t['x3d']['cache_domain_ids'] == []
    assert t['x3d']['label'] == 'X3D cache group unverified'


def test_conflicting_size_and_sharing_mask_are_unverified(fixture_system):
    reader, domains = fixture_system()
    cache = reader.sys/f'devices/system/cpu/cpu{domains[0][0]}/cache/index7'
    (cache/'size').write_text('96M')
    assert reader.discover()['x3d']['cache_domain_ids'] == []
    (cache/'shared_cpu_list').write_text(','.join(map(str,domains[0]+domains[1])))
    t = reader.discover()
    assert t['x3d']['cache_domain_ids'] == []
    assert not all(d['verified'] for d in t['cache_domains'])


def test_partial_online_cache_reports_disable_classification(fixture_system):
    reader, domains = fixture_system()
    (reader.sys/f'devices/system/cpu/cpu{domains[0][0]}/cache/index7/shared_cpu_list').unlink()
    assert not reader.discover()['x3d']['cache_domain_ids']


def test_restricted_offline_and_display_mapping(fixture_system):
    reader, domains = fixture_system('ryzen7700', offline=[7,15], allowed=[0,4,8,12])
    t = reader.discover()
    assert t['offline_cpus']==[7,15]
    assert t['analyzer_allowed_cpus']==[0,4,8,12]
    assert t['cores'][0]['logical_cpus']==[0,8]
    assert t['cores'][0]['display_cpus']==[1,9]
    assert reader.discover(0)['cores'][0]['display_cpus']==[0,8]


def test_hotplug_changes_generation(fixture_system):
    reader, domains = fixture_system()
    original = reader.discover()
    (reader.sys/'devices/system/cpu/online').write_text(str(domains[0][0]))
    assert reader.discover()['generation'] != original['generation']


def test_virtualization_capacity_and_missing_topology(fixture_system):
    reader,_=fixture_system('virtual')
    assert reader.discover()['virtualized']
    reader,_=fixture_system('arm64')
    assert {c['capacity_class'] for c in reader.discover()['cores']}=={'higher capacity','lower capacity'}
    reader,_=fixture_system('future',missing_topology=True)
    t=reader.discover()
    assert t['physical_core_count'] is None
    assert all(not c['verified'] for c in t['cores'])


def test_permission_restricted_mode(fixture_system,monkeypatch):
    reader,_=fixture_system()
    original=type(reader.sys).read_text
    def restricted(path,*args,**kwargs):
        if path.name=='amd_x3d_mode':
            raise PermissionError('restricted')
        return original(path,*args,**kwargs)
    monkeypatch.setattr(type(reader.sys),'read_text',restricted)
    t=reader.discover()
    assert t['x3d']['driver']['status']=='permission restricted'
    assert t['x3d']['driver']['current_preference'] is None


def test_parsers():
    assert cpulist('0-2,8,12-13')=={0,1,2,8,12,13}
    assert cpulist('3-1')==set()
    assert cpulist('-1')==set()
    assert cpumask('00000001,00000001')=={0,32}
    assert cache_bytes('98304K')==96*1024**2
    assert cache_bytes('Unknown') is None


def test_unknown_future_x3d_model_and_ambiguous_asymmetry(fixture_system):
    reader,_=fixture_system(model='AMD Future Family 12345X3D',mode=None)
    assert reader.discover()['x3d']['cache_domain_ids']
    reader,_=fixture_system(sizes=['96M','96M'])
    assert not reader.discover()['x3d']['cache_domain_ids']
    reader,_=fixture_system(domains=[6,8])
    assert not reader.discover()['x3d']['cache_domain_ids']
    reader,_=fixture_system(virtual=True)
    t=reader.discover()
    assert not t['x3d']['cache_domain_ids']
    assert t['x3d']['label']=='X3D cache group unverified'


def test_affinity_only_inventory_is_explicitly_limited(tmp_path):
    reader=TopologyReader(tmp_path/'sys',tmp_path/'proc',lambda:{2,9},'future')
    t=reader.discover()
    assert t['present_cpus']==[2,9]
    assert t['physical_core_count'] is None
    assert not t['cache_domains']
    assert any('limited to analyzer affinity' in w for w in t['warnings'])


def test_bound_driver_provides_capability_when_future_model_is_unknown(fixture_system):
    reader,_=fixture_system(model='Unknown future processor',vendor='Unknown')
    assert reader.discover()['x3d']['processor_reports_x3d']
    assert reader.discover()['x3d']['cache_domain_ids']

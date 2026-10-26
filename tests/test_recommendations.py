import pytest

from backend.errors import HalawaCoreError
from backend.recommendation_engine import recommend


def test_profiles_preserve_safe_default_and_bound_experiments(fixture_system):
    reader,domains=fixture_system()
    t=reader.discover()
    current=sorted(set(domains[0][:5]+domains[1][:5]))
    profiles={r['id']:r for r in recommend(t,current,'gaming')}
    assert profiles['balanced']['linux_cpus']==current
    assert set(profiles['cache']['linux_cpus'])==set(domains[1][:5])
    assert set(profiles['frequency']['linux_cpus'])==set(domains[0][:5])
    assert profiles['performance']['linux_cpus']==current
    assert all(set(r['linux_cpus'])<=set(current) and r['linux_cpus'] for r in profiles.values())
    assert all(r['requires_confirmation'] for r in profiles.values())


def test_missing_data_never_produces_guessed_x3d_profile(fixture_system):
    reader,domains=fixture_system(missing_mask=True,missing_cppc=True)
    t=reader.discover()
    profiles={r['id']:r for r in recommend(t,sorted(set(sum(domains,[]))))}
    assert not profiles['cache']['enabled']
    assert not profiles['frequency']['enabled']
    assert profiles['cache']['linux_cpus']==profiles['balanced']['linux_cpus']


def test_frequency_is_not_cppc_ranking_or_driver_mode(fixture_system):
    reader,domains=fixture_system(frequency=None)
    t=reader.discover()
    assert t['x3d']['driver']['current_preference']=='cache'
    assert not t['x3d']['frequency_domain_ids']


def test_offline_restricted_and_disallowed_domain(fixture_system):
    reader,domains=fixture_system('dual7900x3d',offline=[0,12],allowed=[1,13])
    t=reader.discover()
    current=[1,7,13,19]
    profiles=recommend(t,current,restrictions=[1,13])
    assert all(set(r['linux_cpus'])<=set([1,13]) for r in profiles)
    with pytest.raises(HalawaCoreError):
        recommend(t,[0,12])


def test_numa_explanation(fixture_system):
    reader,domains=fixture_system('multisocket')
    profiles=recommend(reader.discover(),sum(domains,[]))
    assert len([r for r in profiles if r['id'].startswith('numa:')])==2

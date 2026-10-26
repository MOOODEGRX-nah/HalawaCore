import ctypes
import struct

import pytest

from backend.windows_native import GroupAffinity, FileTime, mask_ids, parse_topology
from backend.windows_platform import WindowsTopology
from backend.recommendation_engine import recommend


def affinity(cpus):
    groups={c//64 for c in cpus}
    return b''.join(struct.pack('<QH6x',sum(1<<(c%64) for c in cpus if c//64==group),group) for group in sorted(groups))


def processor(kind,cpus,efficiency=0):
    payload=struct.pack('<BB20xH',0,efficiency,len({c//64 for c in cpus}))+affinity(cpus)
    return struct.pack('<II',kind,len(payload)+8)+payload


def cache(cpus,size,legacy=False):
    payload=struct.pack('<BBHII18xH',3,0,64,size,0,0 if legacy else len({c//64 for c in cpus}))+affinity(cpus)
    return struct.pack('<II',2,len(payload)+8)+payload


def fixture_blob(dual=True,multi=False):
    first=[0,1,8,9] if not multi else [0,1,64,65]
    second=[2,3,10,11] if not multi else [2,3,66,67]
    cpus=first+second if dual else first
    cores=[first[:2],first[2:]]+([second[:2],second[2:]] if dual else [])
    blob=processor(3,cpus)+b''.join(processor(0,ids,i%2) for i,ids in enumerate(cores))
    blob+=cache(first,96*1024**2,legacy=True)
    if dual:blob+=cache(second,32*1024**2)
    return blob,first,second


class NativeFixture:
    def __init__(self,blob,multi=False):self.blob,self.multi=blob,multi
    def topology(self):return parse_topology(self.blob)
    def process_affinity(self,pid):
        if self.multi:
            from backend.errors import HalawaCoreError
            raise HalawaCoreError('Multiple groups',403)
        return {c for r in self.topology() if r['relationship']==0 for c in r['cpus']}


def test_fixed_width_windows_abi():
    assert ctypes.sizeof(GroupAffinity)==16
    assert GroupAffinity.group.offset==8
    assert ctypes.sizeof(FileTime)==8
    assert mask_ids(3,2)=={128,129}


@pytest.mark.parametrize('dual',[False,True])
def test_windows_cache_masks_not_ccd_numbers(dual):
    blob,first,second=fixture_blob(dual)
    topology=WindowsTopology(NativeFixture(blob),lambda:{'ProcessorNameString':'AMD Future X3D','VendorIdentifier':'AuthenticAMD'}).discover()
    assert topology['platform']=='Windows'
    assert topology['physical_core_count']==(4 if dual else 2)
    selected={c for d in topology['cache_domains'] if d['id'] in topology['x3d']['cache_domain_ids'] for c in d['logical_cpus']}
    assert selected==set(first)
    assert topology['x3d']['driver']['current_preference'] is None
    assert topology['features']['cppc']=='unsupported'
    assert topology['logical_cpus'][0]['display_id']=='G0:P0'
    profiles={r['id']:r for r in recommend(topology,topology['online_cpus'])}
    assert profiles['cache']['linux_cpus']==sorted(first)
    assert not profiles['frequency']['enabled']


def test_multi_processor_groups_visible_but_read_only():
    blob,_,_=fixture_blob(multi=True)
    t=WindowsTopology(NativeFixture(blob,True),lambda:{}).discover()
    assert 64 in t['online_cpus']
    assert 'read-only' in t['affinity_support']
    assert not t['analyzer_allowed_cpus']
    assert any('processor groups' in warning for warning in t['warnings'])
    assert any(c['display_id']=='G1:P0' for c in t['logical_cpus'])


def test_virtual_x3d_stays_unverified():
    blob,_,_=fixture_blob()
    t=WindowsTopology(NativeFixture(blob),lambda:{'ProcessorNameString':'AMD X3D','VendorIdentifier':'AuthenticAMD','virtualized':True}).discover()
    assert not t['x3d']['cache_domain_ids']


@pytest.mark.parametrize('blob',[b'1',struct.pack('<II',0,0),struct.pack('<II',0,999),struct.pack('<II',2,40)+b'\0'*32,struct.pack('<II',0,32)+b'\0'*24])
def test_malformed_native_records_never_fabricate_topology(blob):
    with pytest.raises(ValueError):parse_topology(blob)


def test_duplicate_conflicting_caches_are_unverified():
    blob,first,_=fixture_blob()
    blob+=cache(first,64*1024**2)
    t=WindowsTopology(NativeFixture(blob),lambda:{'ProcessorNameString':'AMD X3D','VendorIdentifier':'AuthenticAMD'}).discover()
    assert not t['x3d']['cache_domain_ids']


def test_group_relationship_mask_layout():
    info=struct.pack('<BB38xQ',64,2,5)
    payload=struct.pack('<HH20x',1,1)+info
    r=parse_topology(struct.pack('<II',4,len(payload)+8)+payload)[0]
    assert r['cpus']==[0,2] and r['groups']==[0]

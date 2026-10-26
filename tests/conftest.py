import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('HALAWACORE_DATA_DIR', '/tmp/halawacore-test-import')

from backend.cpu_topology import TopologyReader

CASES = json.loads((Path(__file__).parent / 'fixtures/topologies.json').read_text())


@pytest.fixture
def fixture_system(tmp_path):
    def build(name='dual7950x3d', **overrides):
        spec = {**CASES[name], **overrides}
        root = tmp_path / (name + str(len(list(tmp_path.iterdir()))))
        sysroot, proc = root / 'sys', root / 'proc'
        def write(relative, value, system=True):
            path = (sysroot if system else proc) / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(value))
        text = f"processor : 0\nvendor_id : {spec.get('vendor', 'Unknown')}\nmodel name : {spec['model']}\nflags : {'hypervisor' if spec.get('virtual') else ''}\n"
        write('cpuinfo', text, False)
        cpu_base = 'devices/system/cpu/'
        domain_ids, all_ids, core_num = [], [], 0
        for domain, count in enumerate(spec['domains']):
            mapping = []
            threads = spec.get('threads', [2]*len(spec['domains']))[domain]
            for _ in range(count):
                ids = [(core_num + t * sum(spec['domains'])) * (3 if spec.get('sparse') else 1) + (2 if spec.get('sparse') else 0) for t in range(threads)]
                mapping.append(ids)
                all_ids.extend(ids)
                core_num += 1
            domain_ids.append(mapping)
        flat_domains = [[c for core in domain for c in core] for domain in domain_ids]
        for domain, mapping in enumerate(domain_ids):
            for index, siblings in enumerate(mapping):
                for cpu in siblings:
                    base = f'{cpu_base}cpu{cpu}/'
                    if not spec.get('missing_topology'):
                        write(base+'topology/physical_package_id', spec.get('packages',[0]*len(domain_ids))[domain])
                        # Both domains can have the same die and core IDs can repeat across packages.
                        write(base+'topology/die_id', 77)
                        write(base+'topology/core_id', index + sum(spec['domains'][:domain]) if not spec.get('packages') else index)
                        write(base+'topology/thread_siblings_list', ','.join(map(str,siblings)))
                    if not spec.get('missing_cppc'):
                        write(base+'acpi_cppc/highest_perf', 196-index)
                        write(base+'acpi_cppc/nominal_perf', 150)
                        write(base+'cpufreq/amd_pstate_prefcore_ranking', 250-index if domain == 1 else 196-index)
                    if spec.get('capacities'):
                        write(base+'cpu_capacity', spec['capacities'][domain])
                    if spec.get('frequency'):
                        write(base+'cpufreq/cpuinfo_max_freq', spec['frequency'][domain])
                        write(base+'cpufreq/scaling_cur_freq', 2200000)
                    if not spec.get('missing_cache'):
                        cache = base+'cache/index7/'  # Must inspect level, not assume index3.
                        write(cache+'level', 3)
                        write(cache+'type','Unified')
                        write(cache+'size',spec['sizes'][domain])
                        write(cache+'id', 41-domain)  # Cache ID differs from die and enumeration.
                        if not spec.get('missing_mask'):
                            write(cache+'shared_cpu_list', ','.join(map(str,flat_domains[domain])))
        offline = set(spec.get('offline', []))
        write(cpu_base+'present', ','.join(map(str,sorted(all_ids))))
        write(cpu_base+'online', ','.join(map(str,sorted(set(all_ids)-offline))))
        if spec.get('mode'):
            write('bus/platform/drivers/amd_x3d_vcache/AMDI0101:00/amd_x3d_mode', spec['mode'])
        if spec.get('numa'):
            for i, cpus in enumerate(flat_domains):
                write(f'devices/system/node/node{i}/cpulist', ','.join(map(str,cpus)))
                write(f'devices/system/node/node{i}/distance', '10 20' if i==0 else '20 10')
                write(f'devices/system/node/node{i}/meminfo',f'Node {i} MemTotal: 1024000 kB')
        allowed = set(spec.get('allowed', all_ids))
        reader = TopologyReader(sysroot,proc,lambda:allowed,spec.get('architecture','x86_64'))
        return reader, flat_domains
    return build

"""Read-only, injectable Linux topology discovery. Cache masks are identities, not CCD IDs."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
from collections import defaultdict
from pathlib import Path


def cpulist(value: str | None) -> set[int]:
    result: set[int] = set()
    if not value:
        return result
    try:
        for part in value.strip().split(','):
            ends = part.strip().split('-')
            lo, hi = int(ends[0]), int(ends[-1])
            if len(ends) > 2 or lo < 0 or hi < lo or hi > 1048575:
                return set()
            result.update(range(lo, hi + 1))
    except ValueError:
        return set()
    return result


def cpumask(value: str | None) -> set[int]:
    try:
        mask = int((value or '').replace(',', '').strip(), 16)
        if mask < 0 or mask.bit_length() > 1048576:
            return set()
        return {i for i in range(mask.bit_length()) if mask & (1 << i)}
    except ValueError:
        return set()


def cache_bytes(value: str | None) -> int | None:
    match = re.fullmatch(r'(\d+)\s*([KMGT]?)(?:i?B)?', value or '', re.I)
    if not match:
        return None
    size = int(match[1]) * 1024 ** (' KMGT'.index(match[2].upper()) if match[2] else 0)
    return size if size > 0 else None


class TopologyReader:
    def __init__(self, sys_root: Path = Path('/sys'), proc_root: Path = Path('/proc'),
                 allowed=None, architecture: str | None = None):
        self.sys = Path(sys_root)
        self.proc = Path(proc_root)
        self.allowed = allowed or (lambda: os.sched_getaffinity(0))
        self.architecture = architecture or platform.machine()
        self.restricted: set[str] = set()

    def read(self, path: Path) -> str | None:
        try:
            return path.read_text().strip()
        except PermissionError:
            self.restricted.add(str(path))
        except (OSError, UnicodeError):
            pass
        return None

    def number(self, path: Path) -> int | None:
        try:
            return int(self.read(path) or '')
        except ValueError:
            return None

    def children(self, path: Path, pattern: str):
        try:
            return sorted(path.glob(pattern))
        except PermissionError:
            self.restricted.add(str(path))
            return []

    def driver(self) -> dict:
        base = self.sys / 'bus/platform/drivers/amd_x3d_vcache'
        entries = []
        for path in self.children(base, '*/amd_x3d_mode'):
            raw = self.read(path)
            entries.append({'device': path.parent.name, 'path': str(path),
                            'mode': raw if raw in ('cache', 'frequency') else None,
                            'raw_mode': raw, 'read_only': True})
        modes = {entry['mode'] for entry in entries}
        preference = next(iter(modes)) if len(modes) == 1 and None not in modes else None
        denied = any(str(base) in p for p in self.restricted)
        status = ('permission restricted' if denied else 'available' if entries and preference
                  else 'partially available' if base.exists() else 'unsupported')
        return {'status': status, 'registered': base.exists(), 'bound_devices': entries,
                'current_preference': preference, 'read_only': True,
                'note': 'Driver mode is a firmware ranking preference, not a guarantee of process placement.'}

    def discover(self, display_offset: int = 1) -> dict:
        self.restricted.clear()
        base = self.sys / 'devices/system/cpu'
        info = self.read(self.proc / 'cpuinfo') or ''
        fields = dict(re.findall(r'^([^:\n]+?)\s*:\s*(.*)$', info.split('\n\n')[0], re.M))
        model = fields.get('model name') or fields.get('Processor') or fields.get('cpu') or fields.get('machine') or 'Unknown processor'
        vendor = fields.get('vendor_id') or fields.get('CPU implementer') or 'Unknown'
        paths = {int(p.name[3:]): p for p in self.children(base, 'cpu[0-9]*') if re.fullmatch(r'cpu\d+', p.name)}
        present = cpulist(self.read(base / 'present')) or set(paths)
        if not present:
            present = {int(x) for x in re.findall(r'^processor\s*:\s*(\d+)', info, re.M)}
        affinity_only = not bool(present)
        if affinity_only:
            try:
                present = set(self.allowed())
            except OSError:
                present = set()
        online_text = self.read(base / 'online')
        online = cpulist(online_text) if online_text is not None else {
            cpu for cpu in present if self.read(base / f'cpu{cpu}/online') != '0'}
        try:
            allowed = set(self.allowed()) & online
        except OSError:
            allowed = set()
        logical = []
        reports = defaultdict(list)
        for cpu in sorted(present):
            path = base / f'cpu{cpu}'
            top = path / 'topology'
            siblings = cpulist(self.read(top / 'thread_siblings_list')) or cpulist(self.read(top / 'core_cpus_list'))
            if not siblings:
                siblings = cpumask(self.read(top / 'thread_siblings'))
            row = {'id': cpu, 'display_id': cpu + display_offset,
                   'package_id': self.number(top / 'physical_package_id'),
                   'die_id': self.number(top / 'die_id'), 'cluster_id': self.number(top / 'cluster_id'),
                   'core_id': self.number(top / 'core_id'),
                   'thread_siblings': sorted(siblings & present), 'online': cpu in online,
                   'allowed': cpu in allowed, 'capacity': self.number(path / 'cpu_capacity'),
                   'kernel_core_type': self.read(top / 'core_type'),
                   'cppc_highest_perf': self.number(path / 'acpi_cppc/highest_perf'),
                   'cppc_nominal_perf': self.number(path / 'acpi_cppc/nominal_perf'),
                   'prefcore_ranking': self.number(path / 'cpufreq/amd_pstate_prefcore_ranking'),
                   'prefcore_enabled': self.read(path / 'cpufreq/amd_pstate_hw_prefcore'),
                   'max_frequency_khz': self.number(path / 'cpufreq/cpuinfo_max_freq'),
                   'frequency_khz': self.number(path / 'cpufreq/scaling_cur_freq')}
            logical.append(row)
            for cache in self.children(path / 'cache', 'index*'):
                if self.number(cache / 'level') != 3 or self.read(cache / 'type') not in ('Unified', 'Data'):
                    continue
                shared = cpulist(self.read(cache / 'shared_cpu_list')) or cpumask(self.read(cache / 'shared_cpu_map'))
                if not shared or cpu not in shared:
                    continue  # An ID or die number without a sharing mask is insufficient.
                reports[tuple(sorted(shared))].append({'cpu': cpu, 'size': cache_bytes(self.read(cache / 'size')),
                    'cache_id': self.number(cache / 'id'), 'path': str(cache)})
        by_cpu = {row['id']: row for row in logical}
        groups = defaultdict(list)
        for row in logical:
            siblings = row['thread_siblings']
            reciprocal = bool(siblings) and row['id'] in siblings and all(
                by_cpu[s]['thread_siblings'] == siblings for s in siblings)
            if reciprocal:
                key = 'siblings:' + ','.join(map(str, siblings))
                verified = True
            elif all(row[k] is not None and row[k] >= 0 for k in ('package_id', 'core_id')):
                key = f"package:{row['package_id']}/die:{row['die_id']}/core:{row['core_id']}"
                verified = True
            else:
                key, verified = f"unknown-cpu:{row['id']}", False
            row['core_key'] = key
            row['core_verified'] = verified
            groups[key].append(row)
        capacities = sorted({r['capacity'] for r in logical if r['capacity'] is not None and r['capacity'] > 0})
        cores = []
        for key, rows in groups.items():
            ids = sorted(r['id'] for r in rows)
            capacity = rows[0]['capacity']
            classification = ('higher capacity' if len(capacities) > 1 and capacity == capacities[-1]
                else 'lower capacity' if len(capacities) > 1 and capacity == capacities[0]
                else f'capacity {capacity}' if capacity in capacities and len(capacities) > 1 else 'unknown / homogeneous')
            cores.append({'key': key, 'socket_id': rows[0]['package_id'], 'die_id': rows[0]['die_id'],
                'core_id': rows[0]['core_id'], 'logical_cpus': ids, 'display_cpus': [c + display_offset for c in ids],
                'smt_threads': len(ids), 'verified': all(r['core_verified'] for r in rows),
                'online_cpus': sorted(set(ids) & online), 'allowed_cpus': sorted(set(ids) & allowed),
                'cppc_highest_perf': max((r['cppc_highest_perf'] for r in rows if r['cppc_highest_perf'] is not None), default=None),
                'prefcore_ranking': max((r['prefcore_ranking'] for r in rows if r['prefcore_ranking'] is not None), default=None),
                'capacity_class': classification, 'capacity': capacity})
        domains = []
        for mask, rows in sorted(reports.items()):
            members = set(mask)
            sizes = {r['size'] for r in rows}
            overlaps = any(members & set(other) for other in reports if other != mask)
            coverage = (members & online) <= {r['cpu'] for r in rows}
            valid = not overlaps and coverage and len(sizes) == 1 and None not in sizes and members <= present
            ids = sorted(members)
            keys = sorted({by_cpu[c]['core_key'] for c in ids if c in by_cpu})
            domain = {'id': 'l3:' + ','.join(map(str, mask)), 'level': 3,
                'logical_cpus': ids, 'display_cpus': [c + display_offset for c in ids],
                'online_cpus': sorted(members & online), 'allowed_cpus': sorted(members & allowed),
                'size_bytes': next(iter(sizes)) if len(sizes) == 1 else None,
                'cache_ids': sorted({r['cache_id'] for r in rows if r['cache_id'] is not None}),
                'package_ids': sorted({by_cpu[c]['package_id'] for c in ids if c in by_cpu and by_cpu[c]['package_id'] is not None}),
                'die_ids': sorted({by_cpu[c]['die_id'] for c in ids if c in by_cpu and by_cpu[c]['die_id'] is not None}),
                'physical_core_keys': keys, 'physical_core_count': len(keys),
                'smt_mapping': {k: groups[k][0]['thread_siblings'] or [r['id'] for r in groups[k]] for k in keys},
                'verified': valid, 'status': 'available' if valid else 'partially available',
                'evidence': [r['path'] for r in rows],
                'note': 'Cache-sharing domain; die IDs are separate metadata.'}
            freqs = [by_cpu[c]['max_frequency_khz'] for c in ids if c in by_cpu and c in online]
            domain['max_frequency_range_khz'] = [min(freqs), max(freqs)] if freqs and all(f is not None and f > 0 for f in freqs) else None
            domains.append(domain)
        driver = self.driver()
        amd = vendor == 'AuthenticAMD' or 'AMD' in model or bool(driver['bound_devices'])
        x3d_reported = amd and ('X3D' in model.upper() or bool(driver['bound_devices']))
        complete = bool(domains) and all(d['verified'] for d in domains) and set().union(
            *(set(d['logical_cpus']) for d in domains)) >= present and all(c['verified'] for c in cores) and all(
                any(set(c['logical_cpus']) <= set(d['logical_cpus']) for d in domains) for c in cores)
        cache_domains = []
        if x3d_reported and complete:
            # Compare within packages. Unequal core counts or ambiguous package boundaries are not evidence.
            packages = {r['package_id'] for r in logical}
            for package in packages:
                ds = [d for d in domains if d['package_ids'] == [package]]
                if package is None or not ds:
                    continue
                if len(ds) == 1:
                    cache_domains.append(ds[0]['id'])
                elif len({d['physical_core_count'] for d in ds}) == 1:
                    sizes = {d['size_bytes'] for d in ds}
                    if len(sizes) > 1:
                        cache_domains.extend(d['id'] for d in ds if d['size_bytes'] == max(sizes))
        frequency_domains = []
        if complete:
            for package in {r['package_id'] for r in logical if r['package_id'] is not None}:
                ds = [d for d in domains if d['package_ids'] == [package] and d['online_cpus']]
                if len(ds) > 1 and all(d['max_frequency_range_khz'] for d in ds):
                    # Only non-overlapping hardware maximum-frequency ranges support this suggestion.
                    for d in ds:
                        if all(d['max_frequency_range_khz'][0] > other['max_frequency_range_khz'][1] for other in ds if other is not d):
                            frequency_domains.append(d['id'])
        for domain in domains:
            domain['x3d_cache_candidate'] = domain['id'] in cache_domains
            domain['frequency_candidate'] = domain['id'] in frequency_domains
        numa = []
        for node in self.children(self.sys / 'devices/system/node', 'node[0-9]*'):
            if not re.fullmatch(r'node\d+', node.name):
                continue
            ids = cpulist(self.read(node / 'cpulist'))
            numa.append({'id': int(node.name[4:]), 'logical_cpus': sorted(ids),
                'allowed_cpus': sorted(ids & allowed), 'distance': self.read(node / 'distance'),
                'memory': self.read(node / 'meminfo')})
        virtual = 'hypervisor' in info.split() or any(self.read(self.sys / ('class/dmi/id/' + key)) and
            any(v in (self.read(self.sys / ('class/dmi/id/' + key)) or '').lower() for v in ('kvm', 'virtual', 'vmware', 'qemu', 'xen'))
            for key in ('product_name', 'sys_vendor'))
        xstatus = 'available' if cache_domains else 'unknown' if x3d_reported else 'unsupported' if not amd else 'unknown'
        warnings = []
        if affinity_only:
            warnings.append('CPU inventory is limited to analyzer affinity; full system CPU count and physical topology are unverified.')
        if virtual:
            warnings.append('Guest topology describes virtual CPUs. Physical host cores and host placement are unverified.')
            cache_domains, frequency_domains = [], []
            xstatus = 'unknown'
            for domain in domains:
                domain['x3d_cache_candidate'] = False
                domain['frequency_candidate'] = False
        if not complete:
            warnings.append('Some cache or core topology is missing or inconsistent; related recommendations are disabled.')
        result = {'platform': 'Linux', 'affinity_support': 'available', 'cpu_model': model, 'vendor': vendor, 'architecture': self.architecture,
            'cpu_family': fields.get('cpu family'), 'model_id': fields.get('model'), 'stepping': fields.get('stepping'),
            'physical_core_count': len(cores) if cores and all(c['verified'] for c in cores) else None,
            'core_group_count': len(cores), 'logical_cpu_count': len(present),
            'socket_count': len({r['package_id'] for r in logical if r['package_id'] is not None and r['package_id'] >= 0}),
            'smt_enabled': any(c['smt_threads'] > 1 and c['verified'] for c in cores),
            'display_cpu_offset': display_offset, 'present_cpus': sorted(present),
            'online_cpus': sorted(online), 'offline_cpus': sorted(present - online),
            'analyzer_allowed_cpus': sorted(allowed), 'logical_cpus': logical, 'cores': cores,
            'cache_domains': domains, 'cache_domain_count': len(domains), 'numa_nodes': numa,
            'virtualized': virtual, 'warnings': warnings,
            'x3d': {'status': xstatus, 'processor_reports_x3d': x3d_reported,
                'label': 'X3D cache group identified from kernel topology' if cache_domains else 'X3D cache group unverified',
                'cache_domain_ids': cache_domains, 'frequency_domain_ids': frequency_domains,
                'evidence': 'X3D model/driver capability plus complete shared-L3 masks and sizes; cache technology is inferred, not a CPUID proof.',
                'driver': driver},
            'features': {'topology': 'available' if all(c['verified'] for c in cores) and cores else 'partially available',
                'l3_cache': 'available' if complete else 'partially available' if domains else 'unknown',
                'cppc': 'available' if logical and all(r['cppc_highest_perf'] is not None for r in logical if r['online']) else 'partially available' if any(r['cppc_highest_perf'] is not None for r in logical) else 'unknown',
                'preferred_core': 'available' if any(r['prefcore_ranking'] is not None for r in logical) else 'unknown',
                'frequency': 'available' if any(r['frequency_khz'] is not None for r in logical) else 'unknown',
                'capacity_classes': 'available' if len(capacities) > 1 else 'unknown'},
            'permission_restricted_paths': sorted(self.restricted)}
        # Frequency samples don't invalidate previews; changes to topology, availability and rankings do.
        stamp = {'online': sorted(online), 'allowed': sorted(allowed), 'cores': cores, 'domains': domains, 'x3d': result['x3d']}
        result['generation'] = hashlib.sha256(json.dumps(stamp, sort_keys=True).encode()).hexdigest()[:20]
        result['graph'] = self.graph(result)
        return result

    @staticmethod
    def graph(topo: dict) -> dict:
        nodes, edges = {}, []
        def link(kind, ident, cpu):
            key = f'{kind}:{ident}'
            nodes[key] = {'id': key, 'kind': kind, 'label': str(ident)}
            edges.append({'source': key, 'target': f'cpu:{cpu}', 'relation': 'contains'})
        for row in topo['logical_cpus']:
            cpu = row['id']
            nodes[f'cpu:{cpu}'] = {'id': f'cpu:{cpu}', 'kind': 'logical_cpu', 'label': str(cpu)}
            for kind in ('package', 'die', 'cluster'):
                ident = row[kind + '_id']
                if ident is not None and ident >= 0:
                    scope = str(ident) if kind == 'package' else f"{row['package_id']}:{ident}"
                    link(kind, scope, cpu)
            link('core', row['core_key'], cpu)
        for domain in topo['cache_domains']:
            for cpu in domain['logical_cpus']:
                link('cache', domain['id'], cpu)
        for node in topo['numa_nodes']:
            for cpu in node['logical_cpus']:
                link('numa', node['id'], cpu)
        return {'nodes': list(nodes.values()), 'edges': edges,
                'note': 'Membership graph; cache, NUMA and die boundaries may overlap.'}

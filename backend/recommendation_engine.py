"""Deterministic suggestions, always bounded by online CPUs and existing task affinity."""
from .errors import HalawaCoreError


def recommend(topology: dict, current: list[int], workload: str = 'unknown', restrictions=None) -> list[dict]:
    allowed = set(current) & set(topology['online_cpus'])
    if restrictions is not None:
        allowed &= set(restrictions)
    if not allowed:
        raise HalawaCoreError('No online CPUs remain inside the current affinity and requested restrictions.')
    offset = topology['display_cpu_offset']
    warnings = ['Affinity experiments may reduce performance. Additional cache helps some games; frequency or all available cores helps other workloads.',
        'CPPC and preferred-core ranks are firmware hints, not benchmarks. CPU usage alone cannot demonstrate better FPS or latency.',
        'Only confirmed tasks are covered; newly created threads and child processes may not remain covered.']
    profiles = []

    def add(key, title, cpus, explanation, confidence='experimental', enabled=True):
        selected = set(cpus) & allowed
        if not selected:
            selected, enabled = allowed, False
        involved = [c for c in topology['cores'] if selected & set(c['logical_cpus'])]
        profiles.append({'id': key, 'title': title, 'linux_cpus': sorted(selected),
            'display_cpus': [next((r['display_id'] for r in topology.get('logical_cpus',[]) if r['id']==c), c + offset) for c in sorted(selected)], 'physical_core_keys': [c['key'] for c in involved],
            'smt_mapping': {c['key']: {'included': sorted(selected & set(c['logical_cpus'])),
                'excluded': sorted(set(c['logical_cpus']) - selected)} for c in involved},
            'explanation': explanation, 'confidence': confidence, 'enabled': enabled,
            'current_affinity': sorted(current), 'removed_cpus': sorted(set(current) - selected),
            'warnings': warnings, 'requires_confirmation': True, 'generation': topology['generation']})
    add('balanced', 'Balanced / Scheduler Default', allowed,
        'Preserve existing affinity and let the Linux scheduler manage placement. This is the default for games and demanding workloads.', 'high (preserves eligibility)')
    cache = [d for d in topology['cache_domains'] if d['id'] in topology['x3d']['cache_domain_ids']]
    add('cache', 'Cache-Oriented Gaming', {c for d in cache for c in d['logical_cpus']},
        'Test the kernel-identified shared L3 group on this X3D-reported processor. Reduced parallelism and cross-domain traffic may change results.' if cache else 'X3D cache group unverified. Existing affinity is preserved; this experiment is unavailable.',
        'topology-supported experiment' if cache else 'unverified', bool(cache))
    fast = [d for d in topology['cache_domains'] if d['id'] in topology['x3d']['frequency_domain_ids']]
    add('frequency', 'Frequency-Oriented Computing', {c for d in fast for c in d['logical_cpus']},
        'Test a domain with a strictly higher kernel-reported maximum frequency range. Actual boost depends on load, power and temperature.' if fast else 'A higher-frequency group is unverified. Instantaneous clocks and CPPC ranking do not establish group frequency. Existing affinity is preserved.',
        'hardware-limit heuristic' if fast else 'unverified', bool(fast))
    cores = [c for c in topology['cores'] if c['verified'] and allowed & set(c['logical_cpus'])]
    if cores:
        ranked = sorted(cores, key=lambda c: (c['capacity'] or 0, c['prefcore_ranking'] or c['cppc_highest_perf'] or 0, c['key']))
        chosen = ranked[:max(1, len(ranked) // 4)]
        add('background', 'Background Isolation Experiment', {n for c in chosen for n in c['logical_cpus']},
            'Test a small subset of physical cores for background work. This limits eligibility; it does not reserve cores exclusively.')
        # Games retain all CPUs; compute workloads also benefit from testing a wider set.
        count = len(ranked) if workload in ('gaming', 'competitive gaming', 'encoding', 'rendering', 'compilation', 'ai inference', 'unknown') else max(1, len(ranked) // 2)
        add('performance', 'Experimental Performance', {n for c in ranked[-count:] for n in c['logical_cpus']},
            'Keep a wide set for demanding workloads. For smaller workloads, test preferred or higher-capacity cores when kernel hints exist; no performance gain is assumed.')
    for node in topology['numa_nodes']:
        if allowed & set(node['logical_cpus']):
            add(f"numa:{node['id']}", f"NUMA node {node['id']} experiment", node['logical_cpus'],
                'CPU locality experiment only. Affinity does not control memory allocation or guarantee memory locality.')
    return profiles

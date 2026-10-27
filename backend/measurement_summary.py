"""CPU activity normalization and descriptive comparisons, never speed estimates."""
import math

from .errors import HalawaCoreError


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def cpu_capacity(raw, online_cpus):
    count = len(set(online_cpus))
    valid = finite(raw) and raw >= 0
    return {'cpu_percent_device': raw / count if valid and count else None,
            'cpu_logical_equivalents': raw / 100 if valid else None,
            'cpu_capacity_logical_count': count or None}


def summarize(row):
    samples = row['samples']

    def average(key):
        pairs = [(s[key], s.get('interval_seconds', 1)) for s in samples
                 if finite(s.get(key)) and finite(s.get('interval_seconds', 1)) and s.get('interval_seconds', 1) > 0]
        return sum(v * w for v, w in pairs) / sum(w for _, w in pairs) if pairs else None

    def peak(key):
        return max((s[key] for s in samples if finite(s.get(key))), default=None)

    affinities = sorted({tuple(sorted(s['affinity'])) for s in samples})
    return {'duration_seconds': row.get('duration_seconds', 0), 'sample_count': len(samples),
            'valid_process_samples': sum(finite(s.get('process_cpu_percent')) for s in samples),
            'average_cpu_percent': average('total_percent'), 'peak_cpu_percent': peak('total_percent'),
            'average_process_cpu_percent': average('process_cpu_percent'),
            'average_process_device_percent': average('process_cpu_percent_device'),
            'peak_process_device_percent': peak('process_cpu_percent_device'),
            'average_logical_equivalents': average('process_logical_equivalents'),
            'average_memory_bytes': average('memory_bytes'), 'average_thread_count': average('thread_count'),
            'observed_affinities': [list(mask) for mask in affinities], 'affinity_changed': len(affinities) > 1}


def compare_recordings(before, after):
    if before['id'] == after['id'] or before['phase'] != 'baseline' or after['phase'] not in ('experiment', 'restored'):
        raise HalawaCoreError('Choose a before recording and a separate after recording.', 409)
    if (before['pid'], before['identity']) != (after['pid'], after['identity']):
        raise HalawaCoreError('Recordings belong to different process identities. Record a new baseline for this process.', 409)
    if before['status'] != 'complete' or after['status'] != 'complete':
        raise HalawaCoreError('Stop both recordings successfully before comparing.', 409)
    if after.get('started_monotonic', after['started_at']) < before.get('stopped_monotonic', before['stopped_at']):
        raise HalawaCoreError('The after recording must start after the before recording ends.', 409)
    if min(before['summary']['valid_process_samples'], after['summary']['valid_process_samples']) < 2:
        raise HalawaCoreError('Each recording needs at least two valid CPU samples. Record for longer.', 409)

    samples = before['samples'] + after['samples']
    capacities = {tuple(s.get('online_cpus', [])) for s in samples}
    if len(capacities) != 1 or not next(iter(capacities)):
        raise HalawaCoreError('Online CPU capacity changed or is unverified. Record a new before and after pair.', 409)

    metrics = {}
    for key in ('average_process_device_percent', 'peak_process_device_percent', 'average_logical_equivalents', 'average_process_cpu_percent',
                'average_cpu_percent', 'peak_cpu_percent', 'average_memory_bytes', 'average_thread_count'):
        a, b = before['summary'][key], after['summary'][key]
        metrics[key] = {'before': a, 'after': b, 'difference': b - a if a is not None and b is not None else None}

    warnings = ['CPU activity differences do not establish an FPS, frame-time or latency improvement.',
                'Use the same scene, settings, background workload and similar recording durations. Phase labels are manual.']
    if any(row['summary']['duration_seconds'] < 10 for row in (before, after)):
        warnings.append('Short recordings are noisy. Prefer at least 30 seconds per phase.')
    if any(row['summary']['affinity_changed'] for row in (before, after)):
        warnings.append('Affinity changed during a recording. Repeat with a stable CPU set for each phase.')
    if len({s.get('topology_generation') for s in samples}) > 1:
        warnings.append('Topology or scheduler information changed between samples. Treat the comparison with caution.')
    a, b = before['summary']['duration_seconds'], after['summary']['duration_seconds']
    if min(a, b) and max(a, b) / min(a, b) > 1.5:
        warnings.append('Recording durations differ substantially. Repeat with similar durations.')
    return {'before_id': before['id'], 'after_id': after['id'], 'pid': before['pid'], 'identity': before['identity'],
            'online_cpus': list(next(iter(capacities))), 'metrics': metrics, 'warnings': warnings}

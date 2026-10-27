from copy import deepcopy

import pytest

from backend.errors import HalawaCoreError
from backend.measurement_summary import cpu_capacity, summarize, compare_recordings


def recording(ident='a', phase='baseline', start=0, raw=800):
    samples = [dict(process_cpu_percent=raw, process_cpu_percent_device=raw/16,
                    process_logical_equivalents=raw/100, interval_seconds=2,
                    total_percent=60, memory_bytes=1024**3, thread_count=20,
                    online_cpus=list(range(16)), topology_generation='same', affinity=[0, 2],
                    elapsed_seconds=elapsed) for elapsed in (2, 4)]
    row = dict(id=ident*32, phase=phase, pid=123, identity='100', status='complete',
               started_at=start, stopped_at=start+30, duration_seconds=30, samples=samples)
    row['summary'] = summarize(row)
    return row


def test_cpu_total_800_means_50_percent_of_16_online_logical_cpus():
    assert cpu_capacity(800, list(range(16))) == {
        'cpu_percent_device': 50, 'cpu_logical_equivalents': 8, 'cpu_capacity_logical_count': 16}
    # Sparse IDs count as CPUs; the highest ID is not the capacity.
    assert cpu_capacity(100, [0, 8, 64, 73])['cpu_percent_device'] == 25
    assert cpu_capacity(800, [])['cpu_percent_device'] is None


@pytest.mark.parametrize('raw', [None, float('nan'), float('inf'), -1, True])
def test_unknown_or_invalid_utilization_is_never_fabricated(raw):
    assert cpu_capacity(raw, [0, 2])['cpu_percent_device'] is None


def test_weighted_summaries_exclude_first_unknown_sample():
    row=recording()
    row['samples'][0].update(process_cpu_percent_device=20, interval_seconds=1)
    row['samples'][1].update(process_cpu_percent_device=40, interval_seconds=3)
    row['samples'].append({**row['samples'][0], 'process_cpu_percent_device': None, 'interval_seconds': None})
    assert summarize(row)['average_process_device_percent']==35


def test_comparison_reports_signed_percentage_points_without_speed_score():
    before=recording()
    after=recording('b','experiment',40,400)
    result=compare_recordings(before,after)
    assert result['metrics']['average_process_device_percent']=={'before':50,'after':25,'difference':-25}
    assert result['metrics']['average_process_cpu_percent']['difference']==-400
    assert result['metrics']['average_logical_equivalents']['difference']==-4
    assert result['metrics']['average_memory_bytes']['difference']==0
    assert all('fps' not in key and 'improvement' not in key for key in result['metrics'])
    assert any('do not establish' in warning for warning in result['warnings'])


def test_zero_before_value_has_a_defined_absolute_difference():
    result=compare_recordings(recording(raw=0),recording('b','experiment',40,100))
    assert result['metrics']['average_process_device_percent']['difference']==6.25


@pytest.mark.parametrize('failure',['same_record','wrong_phase','different_pid','reused_pid','recording','stopped','too_short','out_of_order','offline','unverified'])
def test_invalid_or_unmatched_recordings_are_rejected(failure):
    before,after=recording(),recording('b','experiment',40)
    if failure=='same_record':after['id']=before['id']
    if failure=='wrong_phase':after['phase']='baseline'
    if failure=='different_pid':after['pid']=124
    if failure=='reused_pid':after['identity']='101'
    if failure=='recording':after['status']='recording'
    if failure=='stopped':after['status']='stopped'
    if failure=='too_short':after['summary']['valid_process_samples']=1
    if failure=='out_of_order':after['started_at']=1
    if failure=='offline':after['samples'][1]['online_cpus']=[0,2]
    if failure=='unverified':
        for row in (before,after):
            for sample in row['samples']:sample['online_cpus']=[]
    with pytest.raises(HalawaCoreError):compare_recordings(before,after)


def test_noisy_conditions_are_explicit_instead_of_claiming_a_win():
    before,after=recording(),recording('b','restored',40)
    after['samples'][1]['affinity']=[0]
    after['samples'][1]['topology_generation']='changed'
    after['duration_seconds']=5
    after['summary']=summarize(after)
    result=compare_recordings(before,after)
    assert any('Affinity changed' in warning for warning in result['warnings'])
    assert any('Short recordings' in warning for warning in result['warnings'])
    assert any('scheduler information changed' in warning for warning in result['warnings'])
    assert any('durations differ' in warning for warning in result['warnings'])


def test_comparison_does_not_mutate_the_recordings():
    before,after=recording(),recording('b','experiment',40)
    original=deepcopy((before,after))
    compare_recordings(before,after)
    assert (before,after)==original

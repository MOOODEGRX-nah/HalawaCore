from backend.cpu_metrics import CpuMetrics


def test_metrics_keep_sparse_linux_ids_and_do_not_double_count_guest(tmp_path):
    stat=tmp_path/'stat'
    stat.write_text('cpu  10 0 0 90 0 0 0 0 5 0\ncpu0 10 0 0 90 0 0 0 0 5 0\ncpu8 10 0 0 90 0 0 0 0 5 0\n')
    metrics=CpuMetrics(tmp_path)
    assert metrics.sample()['total_percent'] is None
    stat.write_text('cpu  20 0 0 100 0 0 0 0 10 0\ncpu0 20 0 0 100 0 0 0 0 10 0\ncpu8 20 0 0 100 0 0 0 0 10 0\n')
    sample=metrics.sample()
    assert sample['total_percent']==50
    assert sample['logical_cpus']=={'0':50,'8':50}

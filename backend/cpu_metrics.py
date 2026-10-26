import time
from pathlib import Path


class CpuMetrics:
    """/proc/stat deltas keyed by actual Linux IDs, including noncontiguous IDs."""
    def __init__(self, proc_root=Path('/proc'), sys_root=Path('/sys')):
        self.proc = Path(proc_root)
        self.sys = Path(sys_root)
        self.previous = {}

    def sample(self):
        current, usage = {}, {}
        try:
            lines = (self.proc / 'stat').read_text().splitlines()
        except OSError:
            lines = []
        for line in lines:
            fields = line.split()
            if not fields or not fields[0].startswith('cpu'):
                continue
            try:
                values = list(map(int, fields[1:9]))  # guest times are already included in user/nice
                total, idle = sum(values), values[3] + (values[4] if len(values) > 4 else 0)
                key = fields[0]
                current[key] = total, idle
                old = self.previous.get(key)
                usage[key] = round(max(0, min(100, 100 * (1 - (idle - old[1]) / (total - old[0])))), 2) if old and total > old[0] else None
            except (ValueError, IndexError):
                continue
        self.previous = current
        frequency = {}
        for key in usage:
            if key == 'cpu':
                continue
            try:
                frequency[key[3:]] = int((self.sys / f'devices/system/cpu/{key}/cpufreq/scaling_cur_freq').read_text())
            except (OSError, ValueError):
                frequency[key[3:]] = None
        return {'timestamp': time.time(), 'total_percent': usage.get('cpu'), 'frequency_khz': frequency,
                'logical_cpus': {k[3:]: v for k, v in usage.items() if k != 'cpu'},
                'source': '/proc/stat', 'note': 'Utilization, not application performance.'}

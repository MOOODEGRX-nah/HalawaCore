import threading
import time
import uuid

import psutil

from .errors import HalawaCoreError


class ExperimentManager:
    def __init__(self, processes, metrics, control=None):
        self.processes, self.metrics = processes, metrics
        self.control = control
        self.records = []
        self.active = None
        self.stop_event = threading.Event()
        self.lock = threading.RLock()
        self.worker = None

    def start(self, pid, identity, phase, interval):
        with self.lock:
            if self.active:
                raise HalawaCoreError('Stop the current recording before starting another.', 409)
            self.processes.owned(pid, identity)
            row = {'id': uuid.uuid4().hex, 'pid': pid, 'identity': identity, 'phase': phase,
                'started_at': time.time(), 'interval': interval, 'samples': [], 'status': 'recording'}
            self.active = row
            self.metrics.previous = {}
            self.records.append(row)
            self.records = self.records[-50:]
            self.stop_event.clear()
            self.worker = threading.Thread(target=self.run, args=(row,), daemon=True)
            self.worker.start()
            return dict(row)

    def run(self, row):
        previous = None
        try:
            while not self.stop_event.is_set():
                self.processes.owned(row['pid'], row['identity'])
                p = psutil.Process(row['pid'])
                now, cpu_time = time.monotonic(), sum(p.cpu_times()[:2])
                process_usage = (cpu_time - previous[1]) / (now - previous[0]) * 100 if previous else None
                previous = now, cpu_time
                sample = self.metrics.sample()
                sample.update({'process_cpu_percent': process_usage, 'memory_bytes': p.memory_info().rss,
                               'thread_count': p.num_threads(), 'affinity': sorted(self.control.process_affinity(row['pid'])) if self.control else p.cpu_affinity()})
                with self.lock:
                    row['samples'].append(sample)
                    if len(row['samples']) >= 3600:
                        row['status'] = 'sample limit reached'
                        break
                self.stop_event.wait(row['interval'])
        except (psutil.Error, OSError, HalawaCoreError) as exc:
            row['status'], row['error'] = 'stopped', str(exc)
        finally:
            with self.lock:
                row['stopped_at'] = time.time()
                if row['status'] == 'recording':
                    row['status'] = 'complete'
                self.active = None

    def stop(self):
        self.stop_event.set()
        worker = self.worker
        if worker:
            worker.join(timeout=5)
        return self.history()

    def history(self):
        with self.lock:
            result = []
            for row in self.records:
                samples = list(row['samples'])
                values = [s['total_percent'] for s in samples if s['total_percent'] is not None]
                process_values = [s['process_cpu_percent'] for s in samples if s['process_cpu_percent'] is not None]
                result.append({**row, 'samples': samples, 'summary': {
                    'duration_seconds': (row.get('stopped_at') or time.time()) - row['started_at'],
                    'sample_count': len(samples), 'average_cpu_percent': sum(values) / len(values) if values else None,
                    'peak_cpu_percent': max(values, default=None),
                    'average_process_cpu_percent': sum(process_values) / len(process_values) if process_values else None}})
            return result

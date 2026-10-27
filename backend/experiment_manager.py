import threading
import time
import uuid

import psutil

from .errors import HalawaCoreError
from .measurement_summary import cpu_capacity, summarize, compare_recordings


class ExperimentManager:
    def __init__(self, processes, metrics, control=None, topology=None):
        self.processes, self.metrics = processes, metrics
        self.control = control
        self.topology = topology
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
                'started_at': time.time(), 'started_monotonic': time.monotonic(), 'interval': interval, 'samples': [], 'status': 'recording'}
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
        started_monotonic = row['started_monotonic']
        try:
            while not self.stop_event.is_set():
                self.processes.owned(row['pid'], row['identity'])
                p = psutil.Process(row['pid'])
                now, cpu_time = time.monotonic(), sum(p.cpu_times()[:2])
                previous_time = previous[0] if previous else None
                process_usage = max(0, (cpu_time - previous[1]) / (now - previous[0]) * 100) if previous else None
                previous = now, cpu_time
                sample = self.metrics.sample()
                context = self.topology() if self.topology else {}
                online = sorted(set(context.get('online_cpus', [])))
                capacity = cpu_capacity(process_usage, online)
                sample.update({'process_cpu_percent': process_usage, 'memory_bytes': p.memory_info().rss,
                               'process_cpu_percent_device': capacity['cpu_percent_device'],
                               'process_logical_equivalents': capacity['cpu_logical_equivalents'],
                               'online_cpus': online, 'topology_generation': context.get('generation'),
                               'interval_seconds': now - previous_time if previous_time is not None else None,
                               'elapsed_seconds': now - started_monotonic,
                               'thread_count': p.num_threads(), 'affinity': sorted(self.control.process_affinity(row['pid'])) if self.control else p.cpu_affinity()})
                self.processes.owned(row['pid'], row['identity'])
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
                row['stopped_monotonic'] = time.monotonic()
                row['duration_seconds'] = time.monotonic() - started_monotonic
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
                snapshot = {**row, 'samples': samples,
                    'duration_seconds': row.get('duration_seconds', time.monotonic() - row.get('started_monotonic', time.monotonic()))}
                result.append({**snapshot, 'summary': summarize(snapshot)})
            return result

    def compare(self, before_id, after_id):
        recordings = {row['id']: row for row in self.history()}
        if before_id not in recordings or after_id not in recordings:
            raise HalawaCoreError('A recording is no longer available in this session.', 404)
        return compare_recordings(recordings[before_id], recordings[after_id])

"""OS affinity boundary; all affinity writes pass through these implementations."""
import os


class LinuxTaskControl:
    def get(self, pid, tid, identity=None):
        return set(os.sched_getaffinity(tid))

    def set(self, task, cpus):
        os.sched_setaffinity(task['tid'], set(cpus))

    def process_affinity(self, pid):
        return set(os.sched_getaffinity(pid))


class WindowsTaskControl:
    def __init__(self, native):
        self.native = native

    def get(self, pid, tid, identity=None):
        return self.native.thread_affinity(pid, tid, identity)

    def set(self, task, cpus):
        self.native.set_thread_affinity(task['pid'], task['tid'], task['identity'], cpus,
                                        task['process_identity'])

    def process_affinity(self, pid):
        return self.native.process_affinity(pid)

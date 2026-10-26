"""Windows x64 ABI access. No WMI, shell commands, drivers or privilege escalation."""
from __future__ import annotations

import ctypes as C
import os
import struct
from contextlib import contextmanager

from .errors import HalawaCoreError

U32, U64, U16, PTR = C.c_uint32, C.c_uint64, C.c_uint16, C.c_void_p
BOOL = C.c_int32


class FileTime(C.Structure):
    _fields_ = [('low', U32), ('high', U32)]


class GroupAffinity(C.Structure):
    _fields_ = [('mask', U64), ('group', U16), ('reserved', U16 * 3)]


def mask_ids(mask, group=0):
    return {group * 64 + i for i in range(64) if mask & (1 << i)}


def parse_topology(blob: bytes) -> list[dict]:
    """Bounds-checked SLPI_EX records. Fixed-width layouts also work in Linux fixtures."""
    result, offset = [], 0
    while offset < len(blob):
        if len(blob) - offset < 8:
            raise ValueError('Truncated Windows topology header.')
        relationship, size = struct.unpack_from('<II', blob, offset)
        if size < 8 or offset + size > len(blob):
            raise ValueError('Invalid Windows topology record size.')
        payload = blob[offset + 8:offset + size]
        entry = {'relationship': relationship, 'cpus': []}

        def read_masks(start, count):
            if count < 1 or start + 16 * count > len(payload):
                raise ValueError('Invalid Windows topology affinity array.')
            cpus = set()
            for n in range(count):
                mask, group = struct.unpack_from('<QH', payload, start + 16 * n)
                cpus |= mask_ids(mask, group)
            return sorted(cpus)

        if relationship in (0, 3, 5, 7):
            if len(payload) < 24:
                raise ValueError('Truncated processor relationship.')
            count = struct.unpack_from('<H', payload, 22)[0]
            entry.update(cpus=read_masks(24, count), efficiency_class=payload[1])
        elif relationship in (1, 6):
            if len(payload) < 24:
                raise ValueError('Truncated NUMA relationship.')
            count = struct.unpack_from('<H', payload, 22)[0] or 1
            entry.update(cpus=read_masks(24, count), node_id=struct.unpack_from('<I', payload)[0])
        elif relationship == 2:
            if len(payload) < 32:
                raise ValueError('Truncated cache relationship.')
            count = struct.unpack_from('<H', payload, 30)[0] or 1
            entry.update(cpus=read_masks(32, count), level=payload[0],
                         size_bytes=struct.unpack_from('<I', payload, 4)[0],
                         cache_type=struct.unpack_from('<I', payload, 8)[0])
        elif relationship == 4:
            if len(payload) < 24:
                raise ValueError('Truncated group relationship.')
            count = struct.unpack_from('<H', payload, 2)[0]
            if 24 + count * 48 > len(payload):
                raise ValueError('Truncated group information array.')
            entry['groups'] = []
            for group in range(count):
                mask = struct.unpack_from('<Q', payload, 24 + group * 48 + 40)[0]
                entry['groups'].append(group)
                entry['cpus'].extend(sorted(mask_ids(mask, group)))
        result.append(entry)
        offset += size
    return result


class WindowsNative:
    def __init__(self):
        if os.name != 'nt' or C.sizeof(PTR) != 8:
            raise HalawaCoreError('Windows support requires a native 64-bit Windows runtime.', 503)
        self.k = C.WinDLL('kernel32', use_last_error=True)
        self.a = C.WinDLL('advapi32', use_last_error=True)
        def bind(lib, name, result, *args):
            fn = getattr(lib, name)
            fn.restype, fn.argtypes = result, list(args)
            return fn
        self.open_process = bind(self.k, 'OpenProcess', PTR, U32, BOOL, U32)
        self.open_thread = bind(self.k, 'OpenThread', PTR, U32, BOOL, U32)
        self.close = bind(self.k, 'CloseHandle', BOOL, PTR)
        self.query_topology = bind(self.k, 'GetLogicalProcessorInformationEx', BOOL, U32, PTR, C.POINTER(U32))
        self.active_groups = bind(self.k, 'GetActiveProcessorGroupCount', U16)
        self.process_mask = bind(self.k, 'GetProcessAffinityMask', BOOL, PTR, C.POINTER(U64), C.POINTER(U64))
        self.get_group = bind(self.k, 'GetThreadGroupAffinity', BOOL, PTR, C.POINTER(GroupAffinity))
        self.set_group = bind(self.k, 'SetThreadGroupAffinity', BOOL, PTR, C.POINTER(GroupAffinity), C.POINTER(GroupAffinity))
        self.thread_pid = bind(self.k, 'GetProcessIdOfThread', U32, PTR)
        self.get_process_times = bind(self.k, 'GetProcessTimes', BOOL, PTR, *([C.POINTER(FileTime)] * 4))
        self.get_thread_times = bind(self.k, 'GetThreadTimes', BOOL, PTR, *([C.POINTER(FileTime)] * 4))
        self.open_token = bind(self.a, 'OpenProcessToken', BOOL, PTR, U32, C.POINTER(PTR))
        self.token_info = bind(self.a, 'GetTokenInformation', BOOL, PTR, U32, PTR, U32, C.POINTER(U32))
        self.sid_string = bind(self.a, 'ConvertSidToStringSidW', BOOL, PTR, C.POINTER(PTR))
        self.local_free = bind(self.k, 'LocalFree', PTR, PTR)
        self.get_process_sets = bind(self.k, 'GetProcessDefaultCpuSets', BOOL, PTR, C.POINTER(U32), U32, C.POINTER(U32)) if hasattr(self.k, 'GetProcessDefaultCpuSets') else None
        self.get_thread_sets = bind(self.k, 'GetThreadSelectedCpuSets', BOOL, PTR, C.POINTER(U32), U32, C.POINTER(U32)) if hasattr(self.k, 'GetThreadSelectedCpuSets') else None
        self.current_sid = self.process_sid(os.getpid())

    @staticmethod
    def check(ok, message):
        if not ok:
            code = C.get_last_error()
            raise HalawaCoreError(f'{message} (Windows error {code}: {C.FormatError(code).strip()})', 403 if code == 5 else 409)

    @contextmanager
    def process_handle(self, pid):
        handle = self.open_process(0x1000, False, pid)
        self.check(handle, 'Process is inaccessible or no longer exists')
        try:
            yield handle
        finally:
            self.close(handle)

    @contextmanager
    def thread_handle(self, pid, tid, identity=None, write=False):
        handle = self.open_thread(0x0800 | (0x20 if write else 0), False, tid)
        self.check(handle, 'Thread is inaccessible or no longer exists')
        try:
            if self.thread_pid(handle) != pid:
                raise HalawaCoreError('Thread ownership changed.', 409)
            if identity is not None and self.creation(handle, thread=True) != identity:
                raise HalawaCoreError('Thread identity changed.', 409)
            yield handle
        finally:
            self.close(handle)

    def creation(self, handle, thread=False):
        times = [FileTime() for _ in range(4)]
        self.check((self.get_thread_times if thread else self.get_process_times)(handle, *(C.byref(t) for t in times)), 'Cannot read task creation time')
        return str((times[0].high << 32) | times[0].low)

    def identity(self, pid, tid=None):
        if tid is None:
            with self.process_handle(pid) as handle:
                return self.creation(handle)
        with self.thread_handle(pid, tid) as handle:
            return self.creation(handle, thread=True)

    def process_sid(self, pid):
        with self.process_handle(pid) as process:
            token = PTR()
            self.check(self.open_token(process, 8, C.byref(token)), 'Cannot inspect process ownership')
            try:
                size = U32()
                self.token_info(token, 1, None, 0, C.byref(size))
                if not size.value:
                    raise HalawaCoreError('Process ownership is unverified.', 403)
                buffer = C.create_string_buffer(size.value)
                self.check(self.token_info(token, 1, buffer, size.value, C.byref(size)), 'Cannot inspect process ownership')
                sid = PTR.from_buffer(buffer)
                text = PTR()
                self.check(self.sid_string(sid, C.byref(text)), 'Cannot decode process ownership')
                try:
                    return C.wstring_at(text)
                finally:
                    self.local_free(text)
            finally:
                self.close(token)

    def topology(self):
        size = U32()
        self.query_topology(0xffff, None, C.byref(size))
        if size.value == 0 or size.value > 64 * 1024 * 1024:
            raise HalawaCoreError('Windows CPU topology is unavailable.', 503)
        for _ in range(3):
            buffer = C.create_string_buffer(size.value)
            if self.query_topology(0xffff, buffer, C.byref(size)):
                return parse_topology(buffer.raw[:size.value])
            if C.get_last_error() != 122:
                break
        self.check(False, 'Windows CPU topology changed or is inaccessible')

    def process_affinity(self, pid):
        # The mask API is unambiguous only for the first release's single-group mutation scope.
        if self.active_groups() != 1:
            raise HalawaCoreError('Multi-group Windows topology is available for analysis; affinity experiments are read-only in this release.', 403)
        with self.process_handle(pid) as handle:
            process, system = U64(), U64()
            self.check(self.process_mask(handle, C.byref(process), C.byref(system)), 'Cannot read process affinity')
            return mask_ids(process.value & system.value)

    def ensure_no_cpu_sets(self, process, thread=None):
        for handle, fn in [(process, self.get_process_sets), *([(thread, self.get_thread_sets)] if thread else [])]:
            if fn is None:
                raise HalawaCoreError('Windows CPU Set interfaces are unavailable. Target remains read-only.', 403)
            needed = U32()
            ok = fn(handle, None, 0, C.byref(needed))
            if needed.value:
                raise HalawaCoreError('Explicit Windows CPU Sets are active. This target remains read-only to preserve its scheduling policy.', 403)
            self.check(ok, 'Cannot verify Windows CPU Set restrictions')

    def thread_affinity(self, pid, tid, identity=None):
        allowed = self.process_affinity(pid)
        with self.process_handle(pid) as process, self.thread_handle(pid, tid, identity) as thread:
            self.ensure_no_cpu_sets(process, thread)
            group = GroupAffinity()
            self.check(self.get_group(thread, C.byref(group)), 'Cannot read thread affinity')
            if group.group != 0:
                raise HalawaCoreError('Unexpected processor group; target remains read-only.', 403)
            return mask_ids(group.mask, group.group) & allowed

    def set_thread_affinity(self, pid, tid, identity, cpus, process_identity):
        if self.active_groups() != 1 or not cpus or any(c < 0 or c >= 64 for c in cpus):
            raise HalawaCoreError('This Windows affinity selection is unsupported.', 403)
        # Keep validated process AND thread handles open for the entire mutation.
        with self.process_handle(pid) as process, self.thread_handle(pid, tid, identity, write=True) as thread:
            if self.creation(process) != process_identity or self.process_sid(pid) != self.current_sid:
                raise HalawaCoreError('Process identity or ownership changed.', 409)
            self.ensure_no_cpu_sets(process, thread)
            p_mask, system = U64(), U64()
            self.check(self.process_mask(process, C.byref(p_mask), C.byref(system)), 'Cannot verify process CPU restrictions')
            if not set(cpus) <= mask_ids(p_mask.value & system.value):
                raise HalawaCoreError('Process CPU restrictions changed.', 409)
            group = GroupAffinity(sum(1 << c for c in cpus), 0)
            previous = GroupAffinity()
            self.check(self.set_group(thread, C.byref(group), C.byref(previous)), 'Windows rejected thread affinity')
            accepted = GroupAffinity()
            self.check(self.get_group(thread, C.byref(accepted)), 'Cannot verify accepted affinity')
            if accepted.group != 0 or mask_ids(accepted.mask) != set(cpus):
                raise HalawaCoreError('Windows accepted a different thread CPU set; use Restore.', 409)

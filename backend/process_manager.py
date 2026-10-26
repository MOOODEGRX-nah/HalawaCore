"""Minimal process metadata. Never inspect process environments or return raw command arguments."""
import configparser
import os
import shlex
import shutil
import time
from pathlib import Path

import psutil

from .errors import HalawaCoreError


class ProcessManager:
    def __init__(self, proc_root=Path('/proc')):
        self.proc = Path(proc_root)
        self.samples = {}
        self.desktop_cache, self.desktop_timestamp = None, 0

    def identity(self, pid: int, tid: int | None = None) -> str:
        path = self.proc / str(pid)
        if tid is not None:
            path = path / 'task' / str(tid)
        try:
            raw = (path / 'stat').read_text()
            # comm can contain spaces and closing parentheses; fields after the last ')' are stable.
            return raw[raw.rfind(')') + 2:].split()[19]
        except (OSError, IndexError) as exc:
            raise HalawaCoreError('Process or thread no longer exists or is inaccessible.', 409) from exc

    def owned(self, pid: int, identity: str | None = None):
        try:
            p = psutil.Process(pid)
            if p.uids().real != os.getuid() or p.uids().effective != os.geteuid():
                raise HalawaCoreError('Read-only due to permissions: process is owned by another user.', 403)
            if pid == 1 or pid == os.getpid():
                raise HalawaCoreError('This process is protected from affinity experiments.', 403)
            if identity is not None and self.identity(pid) != identity:
                raise HalawaCoreError('PID identity changed. Select the process again.', 409)
            return p
        except psutil.NoSuchProcess as exc:
            raise HalawaCoreError('Process no longer exists.', 404) from exc
        except psutil.AccessDenied as exc:
            raise HalawaCoreError('Read-only due to permissions.', 403) from exc

    def detail(self, pid: int) -> dict:
        try:
            p = psutil.Process(pid)
            ident = self.identity(pid)
            with p.oneshot():
                uid = p.uids().real
                try:
                    exe = p.exe()
                except psutil.AccessDenied:
                    exe = ''
                try:
                    args = p.cmdline()
                except psutil.AccessDenied:
                    args = []
                cpu_seconds = sum(p.cpu_times()[:2])
                now = time.monotonic()
                previous = self.samples.get((pid, ident))
                usage = max(0, (cpu_seconds - previous[1]) / (now - previous[0]) * 100) if previous and now > previous[0] else None
                self.samples[(pid, ident)] = now, cpu_seconds
                try:
                    affinity = sorted(os.sched_getaffinity(pid))
                except (ProcessLookupError, PermissionError):
                    affinity = None
                status = 'Available for affinity testing' if uid == os.getuid() and pid not in (1, os.getpid()) and affinity else 'Read-only due to permissions'
                result = {'pid': pid, 'identity': ident, 'name': p.name(), 'exe': exe,
                    'command_summary': f'{Path(exe).name or p.name()} · {max(0, len(args) - 1)} arguments (hidden for privacy)',
                    'ppid': p.ppid(), 'owner': p.username(), 'uid': uid, 'status': p.status(),
                    'compatibility': status, 'cpu_percent': round(usage, 2) if usage is not None else None,
                    'memory_bytes': p.memory_info().rss, 'thread_count': p.num_threads(),
                    'affinity': affinity, 'cpu_seconds': cpu_seconds, 'icon': None}
            if self.identity(pid) != ident:
                raise HalawaCoreError('PID identity changed during discovery.', 409)
            return result
        except psutil.NoSuchProcess as exc:
            raise HalawaCoreError('Process no longer exists.', 404) from exc
        except (psutil.AccessDenied, PermissionError) as exc:
            raise HalawaCoreError('Read-only due to permissions.', 403) from exc

    def listing(self, query='') -> list[dict]:
        result = []
        desktop_ids = {}
        for app in self.installed():
            if app['executable']:
                desktop_ids.setdefault(app['executable'], []).append(app['id'])
        for pid in psutil.pids():
            try:
                row = self.detail(pid)
                row['desktop_ids'] = desktop_ids.get(row['exe'], [])
                if not query or query.casefold() in f"{pid} {row['name']} {row['exe']} {' '.join(row['desktop_ids'])}".casefold():
                    result.append(row)
            except (HalawaCoreError, OSError, psutil.Error):
                continue
        # Bound the sampling cache to surviving identities.
        if len(self.samples) > 10000:
            active = {(r['pid'], r['identity']) for r in result}
            self.samples = {k: v for k, v in self.samples.items() if k in active}
        return result

    def threads(self, pid: int) -> list[dict]:
        leader = self.identity(pid)
        result = []
        try:
            for path in (self.proc / str(pid) / 'task').iterdir():
                try:
                    tid = int(path.name)
                    result.append({'pid': pid, 'tid': tid, 'identity': self.identity(pid, tid),
                                   'affinity': sorted(os.sched_getaffinity(tid))})
                except (ValueError, OSError, HalawaCoreError):
                    continue
        except OSError as exc:
            raise HalawaCoreError('Threads are no longer accessible.', 409) from exc
        if self.identity(pid) != leader:
            raise HalawaCoreError('PID identity changed while reading threads.', 409)
        return sorted(result, key=lambda r: r['tid'])

    def related(self, pid: int) -> dict:
        """Parent-child evidence only; similarly named programs are never grouped."""
        root = self.detail(pid)
        rows = self.listing()
        by_pid = {r['pid']: r for r in rows}
        children = {pid}
        changed = True
        while changed:
            changed = False
            for row in rows:
                if row['ppid'] in children and row['uid'] == root['uid'] and row['pid'] not in children:
                    parent = by_pid.get(row['ppid'], root)
                    if int(row['identity']) >= int(parent['identity']):
                        children.add(row['pid'])
                        changed = True
        ancestors = []
        parent = root['ppid']
        seen = {pid}
        while parent in by_pid and parent not in seen:
            seen.add(parent)
            row = by_pid[parent]
            ancestors.append({'pid': parent, 'identity': row['identity'], 'name': row['name'], 'exe': row['exe']})
            parent = row['ppid']
        evidence = [root, *[by_pid[c] for c in children if c != pid], *ancestors]
        names = {Path(r['exe']).name.lower() for r in evidence}
        wine = any(n.startswith(('wine', 'proton')) for n in names)
        steam = any(n in ('steam', 'steam.exe', 'steamwebhelper') for n in names)
        candidates = [r['pid'] for r in evidence if 'wine' in Path(r['exe']).name.lower() or r['name'].lower().endswith('.exe')]
        return {'root': root, 'related': [r for r in rows if r['pid'] in children],
            'ancestors': ancestors, 'relationship_evidence': 'Observed parent-child links, matching ownership and process start times.',
            'integration': {'steam_ancestry_observed': steam, 'wine_or_proton_observed': wine,
                'game_process_candidates': sorted(set(candidates)),
                'guidance': 'Inspect the observed game/runtime processes and select exact PIDs and TIDs. Runtime affinity changes scheduling eligibility. Launch-time Wine/Proton CPU topology configuration is separate and has not been verified on this target; no launch override is proposed.',
                'launch_topology_support': 'unverified'}}

    def installed(self) -> list[dict]:
        if self.desktop_cache is not None and time.monotonic() - self.desktop_timestamp < 10:
            return self.desktop_cache
        bases = [Path(os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share')))]
        bases += [Path(p) for p in os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':') if p]
        bases += [Path.home() / '.local/share/flatpak/exports/share', Path('/var/lib/flatpak/exports/share')]
        found = {}
        for base in bases:
            for file in (base / 'applications').glob('**/*.desktop'):
                app_id = str(file.relative_to(base / 'applications')).replace('/', '-')
                if app_id in found:
                    continue
                config = configparser.ConfigParser(interpolation=None, strict=False)
                try:
                    config.read(file)
                    entry = config['Desktop Entry']
                    executable = None
                    try:
                        first = shlex.split(entry.get('Exec', ''))[0]
                        # Wrapper commands are not sufficient executable identity evidence.
                        if first not in ('env', 'flatpak', 'sh', 'bash', 'fish') and '%' not in first:
                            resolved = shutil.which(first)
                            executable = str(Path(resolved).resolve()) if resolved else None
                    except (ValueError, IndexError, OSError):
                        pass
                    found[app_id] = {'id': app_id, 'name': entry.get('Name', file.stem),
                        'icon_name': entry.get('Icon'), 'flatpak_id': entry.get('X-Flatpak'),
                        'executable': executable,
                        'compatibility': 'Not currently running' if executable else 'Insufficient information',
                        'hidden': entry.get('Hidden') == 'true'}
                except (configparser.Error, KeyError, OSError):
                    continue
        self.desktop_cache = sorted((v for v in found.values() if not v['hidden']), key=lambda r: r['name'].casefold())
        self.desktop_timestamp = time.monotonic()
        return self.desktop_cache

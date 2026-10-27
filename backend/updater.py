"""Explicit updates from one fixed GitHub repository; never accept URLs or commands from the API."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile
from pathlib import Path

from .app_version import VERSION
from .errors import HalawaCoreError

REPOSITORY = 'MOOODEGRX-nah/HalawaCore'
RELEASE_API = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
RELEASE_PAGE = f'https://github.com/{REPOSITORY}/releases/latest'
MAX_DOWNLOAD = 256 * 1024**2
FILES = {'HalawaCore', 'HalawaCore.exe', 'LICENSE.txt', 'READ-ME-FIRST.txt', 'verification.json'}
BUSY = {'checking', 'downloading', 'installing', 'restarting'}
WRITE_BLOCKED = {'installing', 'restart_required', 'restarting'}


def version_tuple(version):
    if not isinstance(version, str) or not re.fullmatch(r'(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})\.(0|[1-9]\d{0,4})', version):
        raise HalawaCoreError('The release version is not a supported stable version.', 409)
    return tuple(map(int, version.split('.')))


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024**2), b''):
            digest.update(block)
    return digest.hexdigest()


def external_environment():
    environment = os.environ.copy()
    if sys.platform.startswith('linux') and getattr(sys, 'frozen', False):
        original = environment.get('LD_LIBRARY_PATH_ORIG')
        if original is None: environment.pop('LD_LIBRARY_PATH', None)
        else: environment['LD_LIBRARY_PATH'] = original
    environment['PYINSTALLER_RESET_ENVIRONMENT'] = '1'
    return environment


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix='.update-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def trusted_url(url):
    try:
        parsed = urllib.parse.urlsplit(url)
        return (parsed.scheme == 'https' and not parsed.username and not parsed.password and
                parsed.port in (None, 443) and parsed.hostname in {
                    'api.github.com', 'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'})
    except ValueError:
        return False


class ReleaseRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, new_url):
        if not trusted_url(new_url):
            raise HalawaCoreError('The update download redirected outside the approved GitHub hosts.', 409)
        return super().redirect_request(request, fp, code, message, headers, new_url)


class ReleaseClient:
    def __init__(self):
        self.opener = urllib.request.build_opener(ReleaseRedirect())

    def open(self, url):
        if not trusted_url(url): raise HalawaCoreError('Untrusted update address.', 409)
        request = urllib.request.Request(url, headers={'User-Agent': f'HalawaCore-updater/{VERSION}', 'Accept': 'application/vnd.github+json' if url == RELEASE_API else 'application/octet-stream'})
        return self.opener.open(request, timeout=20)

    def latest(self):
        with self.open(RELEASE_API) as response:
            data = response.read(2 * 1024**2 + 1)
        if len(data) > 2 * 1024**2: raise HalawaCoreError('The release metadata is too large.', 409)
        return json.loads(data)

    def download(self, url, destination, size, progress):
        started = time.monotonic()
        digest, count = hashlib.sha256(), 0
        with self.open(url) as response, Path(destination).open('xb') as output:
            os.chmod(destination, 0o600)
            while block := response.read(256 * 1024):
                count += len(block)
                if count > size or count > MAX_DOWNLOAD or time.monotonic() - started > 300:
                    raise HalawaCoreError('The update download exceeded its expected size or time limit.', 409)
                output.write(block); digest.update(block); progress(count)
            output.flush(); os.fsync(output.fileno())
        if count != size: raise HalawaCoreError('The update download is incomplete.', 409)
        return digest.hexdigest()


def installation(executable, system=None, machine=None, runner=subprocess.run):
    system, machine = system or platform.system(), machine or platform.machine()
    result = {'kind': 'source', 'supported': False, 'reason': 'Source checkouts must be updated through their source workflow.'}
    if machine.lower() not in ('x86_64', 'amd64'):
        return {**result, 'kind': 'unsupported', 'reason': 'In-app updates currently require x64 Windows or Linux.'}
    if not executable: return result
    path = Path(executable).resolve()
    if system == 'Linux' and Path('/usr/bin/pacman').is_file():
        query = runner(['/usr/bin/pacman', '-Qqo', str(path)], capture_output=True, text=True, env=external_environment(), timeout=10)
        if query.returncode == 0:
            if query.stdout.strip() != 'halawacore-bin':
                return {**result, 'kind': 'managed', 'reason': 'This executable belongs to another system package. Use its package manager.'}
            available = Path('/usr/bin/pkexec').is_file()
            return {'kind': 'arch', 'supported': available,
                    'reason': 'The system permission dialog installs the verified Arch package through pacman.' if available else 'The system permission dialog is unavailable. Install polkit through your software manager.'}
    # Do not overwrite RPM/DEB-owned files, even when launched from a writable location.
    if system == 'Linux':
        for tool, args in [('/usr/bin/rpm', ['-qf']), ('/usr/bin/dpkg-query', ['-S'])]:
            if Path(tool).is_file() and runner([tool, *args, str(path)], capture_output=True, env=external_environment(), timeout=10).returncode == 0:
                return {**result, 'kind': 'managed', 'reason': 'This executable is managed by the system. Use its software manager.'}
    if system not in ('Linux', 'Windows'):
        return {**result, 'kind': 'unsupported', 'reason': 'In-app updates currently require x64 Windows or Linux.'}
    name = 'HalawaCore.exe' if system == 'Windows' else 'HalawaCore'
    writable = path.name == name and path.is_file() and os.access(path.parent, os.W_OK)
    if os.name != 'nt' and path.is_file(): writable = writable and path.stat().st_uid == os.getuid()
    return {'kind': 'portable', 'supported': writable,
            'reason': 'The portable executable is replaced in its current folder and a .previous backup is kept.' if writable else 'Move the portable app to a folder you own before updating it.'}


def select_release(metadata, current_version, kind, system):
    if not isinstance(metadata, dict) or metadata.get('draft') is not False or metadata.get('prerelease') is not False:
        raise HalawaCoreError('Only published stable releases can be installed.', 409)
    tag = metadata.get('tag_name', '')
    latest = tag[1:] if isinstance(tag, str) and tag.startswith('v') else ''
    newer = version_tuple(latest) > version_tuple(current_version)
    name = 'HalawaCore-Arch-x64.pkg.tar.zst' if kind == 'arch' else 'HalawaCore-Windows-x64.zip' if system == 'Windows' else 'HalawaCore-Linux-x64.tar.gz'
    expected_url = f'https://github.com/{REPOSITORY}/releases/download/v{latest}/{name}'
    assets = [asset for asset in metadata.get('assets', []) if asset.get('name') == name]
    selected = None
    if len(assets) == 1:
        asset = assets[0]
        digest, size = asset.get('digest', ''), asset.get('size')
        if (asset.get('browser_download_url') == expected_url and asset.get('state') == 'uploaded' and
                isinstance(size, int) and not isinstance(size, bool) and 0 < size <= MAX_DOWNLOAD and
                isinstance(digest, str) and re.fullmatch(r'sha256:[0-9a-f]{64}', digest)):
            selected = {'name': name, 'url': expected_url, 'size': size, 'sha256': digest[7:]}
    return {'version': latest, 'available': newer, 'notes': str(metadata.get('body') or '')[:20000],
            'page': f'https://github.com/{REPOSITORY}/releases/tag/v{latest}', 'asset': selected}


def unpack_portable(archive, stage, system):
    stage = Path(stage); stage.mkdir(mode=0o700)
    expected = 'HalawaCore.exe' if system == 'Windows' else 'HalawaCore'
    allowed, extracted, total = FILES - ({'HalawaCore'} if system == 'Windows' else {'HalawaCore.exe'}), {}, 0

    def save(name, size, stream):
        nonlocal total
        if name not in allowed or name in extracted or size <= 0 or size > MAX_DOWNLOAD:
            raise HalawaCoreError('The update archive contains unexpected files.', 409)
        total += size
        if total > MAX_DOWNLOAD: raise HalawaCoreError('The extracted update is too large.', 409)
        target = stage / name
        with target.open('xb') as output:
            remaining = size
            while remaining:
                block = stream.read(min(256 * 1024, remaining))
                if not block: raise HalawaCoreError('The update archive is incomplete.', 409)
                output.write(block); remaining -= len(block)
        os.chmod(target, 0o700 if name == expected else 0o600)
        extracted[name] = sha256(target)

    if system == 'Windows':
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                mode = member.external_attr >> 16
                if member.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                    raise HalawaCoreError('The update archive contains non-regular files.', 409)
                with bundle.open(member) as stream: save(member.filename, member.file_size, stream)
    else:
        with tarfile.open(archive, 'r:gz') as bundle:
            for member in bundle:
                if not member.isfile(): raise HalawaCoreError('The update archive contains non-regular files.', 409)
                with bundle.extractfile(member) as stream: save(member.name, member.size, stream)
    if expected not in extracted: raise HalawaCoreError('The update executable is missing.', 409)
    return extracted


def probe(executable, expected_version, runner=subprocess.run):
    # Windowed PyInstaller builds have no stdout even with a captured pipe.
    with tempfile.TemporaryDirectory(prefix='halawacore-probe-') as folder:
        report = Path(folder)/'version.json'
        result = runner([str(executable), '--version-file', str(report)], capture_output=True, env=external_environment(), timeout=30)
        try: value = json.loads(report.read_text())
        except (OSError, ValueError): value = None
        if result.returncode != 0 or value != {'application': 'HalawaCore', 'version': expected_version}:
            raise HalawaCoreError('The downloaded executable failed its version check.', 409)


def replace_portable(target, stage, hashes, original_hash):
    """Copy to the target filesystem before replacing; rollback every changed file on error."""
    target, stage = Path(target), Path(stage)
    if target.name not in ('HalawaCore', 'HalawaCore.exe') or not target.is_absolute() or target.is_symlink():
        raise HalawaCoreError('The portable installation path is invalid.', 409)
    if set(hashes) - FILES or target.name not in hashes or sha256(target) != original_hash:
        raise HalawaCoreError('The installed executable changed. Reopen HalawaCore before updating.', 409)
    for name, digest in hashes.items():
        source = stage / name
        if source.is_symlink() or not source.is_file() or sha256(source) != digest:
            raise HalawaCoreError('A staged update file failed verification.', 409)
    changed, temporary = [], []
    try:
        # Executable last, so a preparation failure leaves the previous version runnable.
        for name in sorted(hashes, key=lambda value: value == target.name):
            destination = target.parent / name
            if destination.is_symlink(): raise HalawaCoreError('An installation file is a symbolic link.', 409)
            backup = destination.with_name(name + '.previous') if destination.exists() else None
            fd, candidate = tempfile.mkstemp(prefix='.halawacore-', dir=target.parent); os.close(fd)
            candidate = Path(candidate); temporary.append(candidate)
            shutil.copyfile(stage / name, candidate)
            os.chmod(candidate, 0o755 if name == target.name else 0o644)
            if sha256(candidate) != hashes[name]: raise HalawaCoreError('The copied update failed verification.', 409)
            if backup:
                fd, saved = tempfile.mkstemp(prefix='.backup-', dir=target.parent); os.close(fd)
                saved = Path(saved); temporary.append(saved)
                shutil.copyfile(destination, saved); shutil.copymode(destination, saved); os.replace(saved, backup)
            os.replace(candidate, destination); changed.append((destination, backup))
    except Exception:
        for destination, backup in reversed(changed):
            if backup: os.replace(backup, destination)
            else: destination.unlink(missing_ok=True)
        raise
    finally:
        for path in temporary: path.unlink(missing_ok=True)


def finish_windows_update(plan_path):
    """Runs from the verified staged executable; never elevates or terminates another process."""
    import psutil
    plan_path = Path(plan_path).resolve()
    job = plan_path.parent
    if plan_path.name != 'plan.json' or not re.fullmatch(r'job-[0-9a-f]{32}', job.name) or job.parent.name != 'updates':
        raise HalawaCoreError('Invalid update job path.', 409)
    result_path = job.parent.parent / 'update-result.json'
    try:
        plan = json.loads(plan_path.read_text())
        if plan.get('protocol') != 1 or plan.get('kind') != 'portable' or platform.system() != 'Windows':
            raise HalawaCoreError('Invalid portable update plan.', 409)
        version_tuple(plan['version'])
        target = Path(plan['target'])
        if target.name != 'HalawaCore.exe': raise HalawaCoreError('Invalid Windows executable path.', 409)
        deadline = time.monotonic() + 60
        while time.monotonic() < deadline:
            try: alive = abs(psutil.Process(plan['parent_pid']).create_time() - plan['parent_identity']) < .001
            except psutil.NoSuchProcess: alive = False
            if not alive: break
            time.sleep(.1)
        else: raise HalawaCoreError('The previous app did not close. No update was installed.', 409)
        # A onefile launcher can briefly retain the image lock after its Python process exits.
        for attempt in range(100):
            try:
                replace_portable(target, job/'staged', plan['hashes'], plan['original_hash']); break
            except PermissionError:
                if attempt == 99: raise
                time.sleep(.2)
        atomic_json(result_path, {'status': 'updated', 'version': plan['version']})
        if plan.get('restart') is True:
            subprocess.Popen([str(target)], env=external_environment(), cwd=target.parent,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
        return 0
    except Exception:
        atomic_json(result_path, {'status': 'failed', 'error': 'The update could not finish. Reopen HalawaCore or restore its .previous backup.'})
        raise


class Updater:
    def __init__(self, data_dir, executable=None, shutdown=None, current_version=VERSION, client=None, runner=None, capability=None):
        self.data = Path(data_dir); self.executable = Path(executable).resolve() if executable else None
        self.current_version, self.shutdown = current_version, shutdown
        self.client, self.runner = client or ReleaseClient(), runner or subprocess.run
        self.system = platform.system()
        try:
            self.capability = capability or installation(self.executable, runner=self.runner)
            self.original_hash = sha256(self.executable) if self.executable else None
        except (OSError, subprocess.SubprocessError):
            self.capability = {'kind':'unsupported','supported':False,
                'reason':'The installation method could not be verified. Open the official release page.'}
            self.original_hash = None
        self.lock = threading.RLock(); self.phase = 'idle'; self.error = None
        self.release = None; self.prepared = None; self.job_id = None; self.downloaded = 0; self.worker = None
        self.result_path = self.data/'update-result.json'
        try: self.last_result = json.loads(self.result_path.read_text())
        except (OSError, ValueError): self.last_result = None

    def snapshot(self):
        with self.lock:
            release = self.release or {}
            asset = release.get('asset') or {}
            return {'current_version': self.current_version, 'installation': self.capability,
                    'phase': self.phase, 'error': self.error, 'available': release.get('available', False),
                    'latest_version': release.get('version'), 'release_notes': release.get('notes', ''),
                    'release_page': release.get('page', RELEASE_PAGE), 'asset_name': asset.get('name'),
                    'download_size': asset.get('size'), 'downloaded_bytes': self.downloaded,
                    'job_id': self.job_id, 'last_result': self.last_result,
                    'can_download': bool(release.get('available') and asset and self.capability['supported']),
                    'write_blocked': self.phase in WRITE_BLOCKED}

    def check(self):
        with self.lock:
            if self.phase in BUSY | {'ready', 'restart_required'}: raise HalawaCoreError('Finish the current update before checking again.', 409)
            self.phase, self.error = 'checking', None
        try:
            release = select_release(self.client.latest(), self.current_version, self.capability['kind'], self.system)
            with self.lock: self.release, self.phase = release, 'available' if release['available'] else 'current'
        except Exception:
            with self.lock: self.phase, self.error = 'failed', 'Could not check GitHub for updates. Check your connection and try again.'
        return self.snapshot()

    def download(self):
        with self.lock:
            state = self.snapshot()
            if self.phase not in ('available', 'failed') or not state['can_download']:
                raise HalawaCoreError('Check for a supported newer release before downloading.', 409)
            self.job_id, self.downloaded, self.prepared = uuid.uuid4().hex, 0, None
            self.phase, self.error = 'downloading', None
            self.worker = threading.Thread(target=self._download, daemon=True); self.worker.start()
        return self.snapshot()

    def _download(self):
        try:
            asset, release = self.release['asset'], self.release
            job = self.data/'updates'/('job-'+self.job_id); job.mkdir(parents=True, mode=0o700)
            archive = job/asset['name']
            def progress(count):
                with self.lock: self.downloaded = count
            digest = self.client.download(asset['url'], archive, asset['size'], progress)
            if digest != asset['sha256'] or sha256(archive) != asset['sha256']:
                raise HalawaCoreError('The update checksum does not match. Nothing was installed.', 409)
            hashes = None
            if self.capability['kind'] == 'portable':
                hashes = unpack_portable(archive, job/'staged', self.system)
                probe(job/'staged'/self.executable.name, release['version'], self.runner)
            elif self.capability['kind'] == 'arch':
                query = self.runner(['/usr/bin/pacman', '-Qp', str(archive)], capture_output=True, text=True, env=external_environment(), timeout=20)
                expected = re.escape(release['version'])
                if query.returncode != 0 or not re.fullmatch(r'halawacore-bin '+expected+r'-[1-9]\d*', query.stdout.strip()):
                    raise HalawaCoreError('The downloaded package identity or version is incorrect.', 409)
            with self.lock:
                self.prepared = {'job': job, 'archive': archive, 'hashes': hashes}; self.phase = 'ready'
        except Exception as exc:
            with self.lock: self.phase, self.error = 'failed', exc.message if isinstance(exc, HalawaCoreError) else 'The update download or verification failed. Nothing was installed.'

    def install(self, job_id, confirmed):
        with self.lock:
            if confirmed is not True: raise HalawaCoreError('Explicit update confirmation is required.')
            if self.phase != 'ready' or job_id != self.job_id or not self.prepared:
                raise HalawaCoreError('The prepared update is no longer available. Check again.', 409)
            if sha256(self.executable) != self.original_hash:
                raise HalawaCoreError('The installed executable changed. Reopen HalawaCore before updating.', 409)
            if sha256(self.prepared['archive']) != self.release['asset']['sha256']:
                raise HalawaCoreError('The prepared update checksum changed. Nothing was installed.', 409)
            self.phase, self.error = 'installing', None
            self.worker = threading.Thread(target=self._install, daemon=True); self.worker.start()
        return self.snapshot()

    def _install(self):
        try:
            if self.capability['kind'] == 'arch':
                result = self.runner(['/usr/bin/pkexec', '--disable-internal-agent', '/usr/bin/pacman', '-U', '--noconfirm', str(self.prepared['archive'])],
                                     capture_output=True, env=external_environment(), start_new_session=True)
                if result.returncode != 0:
                    raise HalawaCoreError('System authorization was cancelled or the package manager could not install the update.', 409)
                probe(self.executable, self.release['version'], self.runner)
            elif self.system == 'Windows':
                import psutil
                plan = {'protocol': 1, 'kind': 'portable', 'version': self.release['version'], 'target': str(self.executable),
                        'hashes': self.prepared['hashes'], 'original_hash': self.original_hash,
                        'parent_pid': os.getpid(), 'parent_identity': psutil.Process().create_time(), 'restart': True}
                path = self.prepared['job']/'plan.json'; atomic_json(path, plan)
                subprocess.Popen([str(self.prepared['job']/'staged'/self.executable.name), '--finish-update', str(path)],
                    env=external_environment(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS)
                if self.shutdown: threading.Timer(.5, self.shutdown).start()
                return
            else:
                replace_portable(self.executable, self.prepared['job']/'staged', self.prepared['hashes'], self.original_hash)
            atomic_json(self.result_path, {'status': 'updated', 'version': self.release['version']})
            with self.lock: self.phase = 'restart_required'
        except Exception as exc:
            with self.lock: self.phase, self.error = 'failed', exc.message if isinstance(exc, HalawaCoreError) else 'The update could not finish. Reopen HalawaCore or restore its .previous backup.'

    def restart(self, confirmed):
        with self.lock:
            if confirmed is not True or self.phase != 'restart_required' or not self.shutdown:
                raise HalawaCoreError('Install the update and confirm restart first.', 409)
            subprocess.Popen([str(self.executable)], env=external_environment(), cwd=self.executable.parent,
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                **({'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS} if os.name == 'nt' else {'start_new_session': True}))
            self.phase = 'restarting'; threading.Timer(.5, self.shutdown).start()
        return self.snapshot()

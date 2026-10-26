import os
import json
import platform
import secrets
import threading
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .affinity_manager import AffinityManager
from .cpu_metrics import CpuMetrics
from .cpu_topology import TopologyReader
from .errors import HalawaCoreError
from .experiment_manager import ExperimentManager
from .process_manager import ProcessManager
from .profile_manager import ProfileManager
from .recommendation_engine import recommend
from .schemas import Apply, Preview, Profile, Recommendation, Recording, Restore, Settings, Preferences, TopologyResponse
from .security import LocalSecurity
from .task_control import LinuxTaskControl, WindowsTaskControl

ROOT = Path(__file__).resolve().parents[1]


def create_app(data_dir=None, reader=None, processes=None, control=None, metrics_factory=None, shutdown=None):
    token = secrets.token_urlsafe(40)
    data_dir = Path(data_dir or os.environ.get('HALAWACORE_DATA_DIR', str(ROOT / 'data')))
    if platform.system() == 'Windows' and reader is None:
        from .windows_native import WindowsNative
        from .windows_platform import WindowsTopology, WindowsProcesses, WindowsMetrics
        native = WindowsNative()
        reader, processes = WindowsTopology(native), processes or WindowsProcesses(native)
        control = control or WindowsTaskControl(native)
        metrics_factory = metrics_factory or (lambda: WindowsMetrics(native))
    else:
        reader, processes = reader or TopologyReader(), processes or ProcessManager()
    control = control or LinuxTaskControl()
    metrics_factory = metrics_factory or CpuMetrics
    settings = {'read_only': True, 'display_offset': 0 if platform.system() == 'Windows' else 1}
    topology_lock = threading.RLock()

    def topology():
        with topology_lock:
            return reader.discover(settings['display_offset'])

    metrics = metrics_factory()
    affinity = AffinityManager(processes, topology, data_dir, control)
    lab = ExperimentManager(processes, metrics_factory(), control)
    profiles = ProfileManager(data_dir)
    preferences = {'language': None}
    preferences_path = data_dir / 'preferences.json'
    try:
        saved_preferences = json.loads(preferences_path.read_text())
        if isinstance(saved_preferences, dict) and saved_preferences.get('language') in ('ar', 'en'):
            preferences['language'] = saved_preferences['language']
    except (OSError, ValueError):
        pass

    @asynccontextmanager
    async def lifespan(app):
        yield
        lab.stop()
        # Best-effort graceful shutdown only, never advertised as crash recovery.
        for ident, row in list(affinity.records.items()):
            if row['status'] != 'restored':
                affinity.restore(ident)

    app = FastAPI(title='HalawaCore', version='0.3.0', lifespan=lifespan, docs_url=None, redoc_url=None)
    app.add_middleware(LocalSecurity, token=token)
    app.state.affinity, app.state.processes, app.state.lab = affinity, processes, lab
    app.state.topology = topology

    @app.exception_handler(HalawaCoreError)
    async def known_error(request, exc):
        return JSONResponse({'error': {'message': exc.message}}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({'error': {'message': 'Invalid request fields.', 'fields': [
            {'location': list(e['loc']), 'message': e['msg']} for e in exc.errors()]}}, status_code=422)

    @app.exception_handler(OSError)
    async def system_error(request, exc):
        return JSONResponse({'error': {'message': f'Operating system operation failed: {exc.strerror or type(exc).__name__}'}}, status_code=409)

    @app.get('/api/session')
    def session():
        return {'token': token, 'settings': settings, 'preferences': preferences, 'desktop': shutdown is not None, 'version': '0.3.0'}

    @app.get('/api/health')
    def health():
        return {'status': 'ok', 'application': 'HalawaCore', 'platform': platform.system(), 'read_only': affinity.read_only}

    @app.get('/api/system')
    def system():
        topo = topology()
        return {'os': platform.system(), 'release': platform.release(), 'cpu_model': topo['cpu_model'],
                'architecture': topo['architecture'], 'active_processes': len(psutil.pids()),
                'physical_core_count': topo['physical_core_count'], 'logical_cpu_count': topo['logical_cpu_count'],
                'read_only': affinity.read_only, 'virtualized': topo['virtualized']}

    @app.get('/api/cpu/topology', response_model=TopologyResponse)
    def cpu_topology():
        return topology()

    @app.get('/api/cpu/metrics')
    def cpu_metrics():
        return metrics.sample()

    @app.get('/api/processes')
    def process_list(q: str = Query('', max_length=200)):
        return {'processes': processes.listing(q)}

    @app.get('/api/processes/{pid}')
    def process_detail(pid: int):
        if pid <= 0:
            raise HalawaCoreError('PID must be positive.')
        return processes.related(pid)

    @app.get('/api/processes/{pid}/threads')
    def process_threads(pid: int):
        if pid <= 0:
            raise HalawaCoreError('PID must be positive.')
        return {'threads': processes.threads(pid)}

    @app.get('/api/applications')
    def installed():
        running = processes.listing()
        applications = []
        for entry in processes.installed():
            matches = [{'pid': p['pid'], 'identity': p['identity']} for p in running
                       if entry['executable'] and p['exe'] == entry['executable']]
            applications.append({**entry, 'running_processes': matches,
                'compatibility': 'Available for analysis' if matches else entry['compatibility']})
        return {'applications': applications,
                'launch_support': 'unsupported', 'custom_executable': 'Browser-selected metadata only; execution is unsupported.'}

    @app.post('/api/recommendations')
    def recommendations(body: Recommendation):
        processes.owned(body.pid, body.identity)
        current = sorted(control.process_affinity(body.pid))
        return {'profiles': recommend(topology(), current, body.workload, body.restrictions)}

    @app.post('/api/affinity/preview')
    def preview(body: Preview):
        return affinity.preview(body.pid, body.identity, body.cpus, body.scope, [t.model_dump() for t in body.related], body.task_tid)

    @app.post('/api/affinity/apply')
    def apply(body: Apply):
        return affinity.apply(body.preview_id, body.confirmed)

    @app.post('/api/affinity/restore')
    def restore(body: Restore):
        return affinity.restore(body.experiment_id)

    @app.get('/api/experiments')
    def history():
        return {'affinity': list(affinity.records.values()), 'recordings': lab.history()}

    @app.post('/api/experiments/start')
    def start(body: Recording):
        return lab.start(body.pid, body.identity, body.phase, body.interval)

    @app.post('/api/experiments/stop')
    def stop():
        return {'recordings': lab.stop()}

    @app.get('/api/profiles')
    def profile_list():
        return {'profiles': profiles.listing()}

    @app.post('/api/profiles')
    def profile_save(body: Profile):
        return profiles.save(body.model_dump())

    @app.delete('/api/profiles/{ident}')
    def profile_delete(ident: str):
        profiles.delete(ident)
        return {'deleted': ident}

    @app.post('/api/settings')
    def update_settings(body: Settings):
        if hasattr(os, 'geteuid') and os.geteuid() == 0 and not body.read_only:
            raise HalawaCoreError('Do not run affinity experiments as root. Start HalawaCore as your normal user.', 403)
        with affinity.lock:
            settings.update(body.model_dump())
            affinity.read_only = body.read_only
        return settings

    @app.post('/api/preferences')
    def update_preferences(body: Preferences):
        with affinity.lock:
            temporary = data_dir / 'preferences.tmp'
            with temporary.open('w', encoding='utf-8') as output:
                os.chmod(temporary, 0o600)
                json.dump(body.model_dump(), output)
            os.replace(temporary, preferences_path)
            preferences.update(body.model_dump())
        return preferences

    @app.post('/api/shutdown')
    def stop_desktop():
        if shutdown is None:
            raise HalawaCoreError('Stop this development server from its terminal.', 409)
        if lab.active or any(r['status'] != 'restored' for r in affinity.records.values()):
            raise HalawaCoreError('Stop recording and restore every experiment before closing HalawaCore.', 409)
        threading.Timer(0.25, shutdown).start()
        return {'status': 'closing'}

    @app.get('/')
    def index():
        return FileResponse(ROOT / 'frontend/index.html')

    app.mount('/static', StaticFiles(directory=ROOT / 'frontend'), name='static')
    return app


app = create_app()

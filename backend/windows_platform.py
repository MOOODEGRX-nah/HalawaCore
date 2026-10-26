"""Windows 10/11 adapters for the shared UI and experiment engine."""
import hashlib
import json
import os
import platform
import time
from collections import defaultdict
from pathlib import Path

import psutil

from .cpu_topology import TopologyReader
from .errors import HalawaCoreError
from .process_manager import ProcessManager


def registry_cpu():
    import winreg
    values = {}
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as key:
            for name in ('ProcessorNameString', 'VendorIdentifier', 'Identifier'):
                try:
                    values[name] = winreg.QueryValueEx(key, name)[0].strip()
                except OSError:
                    pass
    except OSError:
        pass
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'HARDWARE\DESCRIPTION\System\BIOS') as key:
            bios=' '.join(str(winreg.QueryValueEx(key,n)[0]) for n in ('SystemManufacturer','SystemProductName'))
            values['virtualized']=any(s in bios.lower() for s in ('vmware','virtual machine','virtualbox','qemu','kvm','xen'))
    except OSError:
        pass
    return values


class WindowsTopology:
    def __init__(self, native, metadata=None):
        self.native = native
        self.metadata = metadata or registry_cpu

    def discover(self, display_offset=0):
        records = self.native.topology()
        meta = self.metadata()
        model, vendor = meta.get('ProcessorNameString', 'Unknown processor'), meta.get('VendorIdentifier', 'Unknown')
        group_records = [r for r in records if r['relationship'] == 4]
        present = set(c for r in group_records for c in r['cpus']) or set(c for r in records if r['relationship'] == 0 for c in r['cpus'])
        packages = [r for r in records if r['relationship'] == 3]
        dies = [r for r in records if r['relationship'] == 5]
        modules = [r for r in records if r['relationship'] == 7]
        core_records = sorted((r for r in records if r['relationship'] == 0), key=lambda r:r['cpus'])
        def membership(rows, cpu):
            indices = [i for i,r in enumerate(rows) if cpu in r['cpus']]
            return indices[0] if len(indices) == 1 else None
        try:
            allowed = self.native.process_affinity(os.getpid())
        except HalawaCoreError:
            allowed = set()
        warnings = []
        groups = sorted({c//64 for c in present})
        if len(groups) > 1:
            warnings.append('Multiple Windows processor groups detected. Topology is available; affinity experiments are read-only until complete cross-group restoration is supported.')
        logical, cores = [], []
        for i, record in enumerate(core_records):
            ids = record['cpus']
            key = 'windows-core:' + ','.join(map(str, ids))
            verified = bool(ids) and all(sum(c in r['cpus'] for r in core_records) == 1 for c in ids)
            core = {'key':key, 'socket_id':membership(packages,ids[0]) if ids else None,
                'die_id':membership(dies,ids[0]) if ids else None, 'core_id':i,
                'logical_cpus':ids, 'display_cpus':[f'G{c//64}:P{c%64}' for c in ids], 'smt_threads':len(ids), 'verified':verified,
                'online_cpus':ids, 'allowed_cpus':sorted(set(ids)&allowed),
                'cppc_highest_perf':None, 'prefcore_ranking':None, 'capacity':None,
                'capacity_class':f"Windows efficiency class {record.get('efficiency_class',0)}"}
            cores.append(core)
            for cpu in ids:
                logical.append({'id':cpu,'display_id':f'G{cpu//64}:P{cpu%64}','windows_group':cpu//64,'windows_processor':cpu%64,
                    'display_label':f'G{cpu//64}:P{cpu%64}', 'package_id':membership(packages,cpu),
                    'die_id':membership(dies,cpu),'cluster_id':membership(modules,cpu),'core_id':i,
                    'core_key':key,'core_verified':verified,'thread_siblings':ids,'online':True,'allowed':cpu in allowed,
                    'capacity':None,'kernel_core_type':record.get('efficiency_class'),
                    'cppc_highest_perf':None,'cppc_nominal_perf':None,'prefcore_ranking':None,
                    'prefcore_enabled':None,'max_frequency_khz':None,'frequency_khz':None})
        by_cpu = {c['id']:c for c in logical}
        raw_domains = defaultdict(list)
        for record in records:
            if record['relationship']==2 and record.get('level')==3 and record.get('cache_type') in (0,2) and record['cpus']:
                raw_domains[tuple(record['cpus'])].append(record)
        domains=[]
        for mask, rows in sorted(raw_domains.items()):
            sizes={r['size_bytes'] for r in rows}
            members=set(mask)
            valid=(len(sizes)==1 and next(iter(sizes))>0 and members<=set(by_cpu)
                   and not any(members&set(other) for other in raw_domains if other!=mask))
            keys=sorted({by_cpu[c]['core_key'] for c in mask if c in by_cpu})
            domains.append({'id':'l3:'+','.join(map(str,mask)),'level':3,'logical_cpus':list(mask),'display_cpus':[f'G{c//64}:P{c%64}' for c in mask],
                'online_cpus':list(mask),'allowed_cpus':sorted(members&allowed),
                'size_bytes':next(iter(sizes)) if len(sizes)==1 else None,'cache_ids':[],
                'package_ids':sorted({by_cpu[c]['package_id'] for c in mask if c in by_cpu and by_cpu[c]['package_id'] is not None}),
                'die_ids':sorted({by_cpu[c]['die_id'] for c in mask if c in by_cpu and by_cpu[c]['die_id'] is not None}),
                'physical_core_keys':keys,'physical_core_count':len(keys),
                'smt_mapping':{c['key']:c['logical_cpus'] for c in cores if c['key'] in keys},
                'verified':valid,'status':'available' if valid else 'partially available',
                'evidence':['Windows GetLogicalProcessorInformationEx / RelationCache'],
                'max_frequency_range_khz':None,'x3d_cache_candidate':False,'frequency_candidate':False})
        complete=bool(domains) and all(d['verified'] for d in domains) and set().union(*(set(d['logical_cpus']) for d in domains))==present and all(
            c['verified'] and any(set(c['logical_cpus'])<=set(d['logical_cpus']) for d in domains) for c in cores)
        reported='X3D' in model.upper() and (vendor=='AuthenticAMD' or 'AMD' in model)
        candidates=[]
        if reported and complete and not meta.get('virtualized',False):
            for package in {c['package_id'] for c in logical if c['package_id'] is not None}:
                ds=[d for d in domains if d['package_ids']==[package]]
                if len(ds)==1:
                    candidates.append(ds[0]['id'])
                elif ds and len({d['physical_core_count'] for d in ds})==1 and len({d['size_bytes'] for d in ds})>1:
                    candidates.extend(d['id'] for d in ds if d['size_bytes']==max(x['size_bytes'] for x in ds))
        if meta.get('virtualized'):
            warnings.append('Virtualized topology: physical host placement and cache technology are unverified.')
        for d in domains:
            d['x3d_cache_candidate']=d['id'] in candidates
        numa=[{'id':r['node_id'],'logical_cpus':r['cpus'],'allowed_cpus':sorted(set(r['cpus'])&allowed),
               'distance':None,'memory':None} for r in records if r['relationship'] in (1,6)]
        result={'platform':'Windows','cpu_model':model,'vendor':vendor,'architecture':platform.machine(),
            'cpu_family':meta.get('Identifier'),'model_id':None,'stepping':None,
            'physical_core_count':len(cores) if cores and all(c['verified'] for c in cores) else None,
            'core_group_count':len(cores),'logical_cpu_count':len(present),'socket_count':len(packages),
            'smt_enabled':any(c['smt_threads']>1 for c in cores),'display_cpu_offset':0,
            'present_cpus':sorted(present),'online_cpus':sorted(present),'offline_cpus':[],
            'analyzer_allowed_cpus':sorted(allowed),'logical_cpus':sorted(logical,key=lambda c:c['id']),
            'cores':cores,'cache_domains':domains,'cache_domain_count':len(domains),'numa_nodes':numa,
            'virtualized':bool(meta.get('virtualized')),'warnings':warnings,'permission_restricted_paths':[],
            'cpu_id_scheme':'Stable internal ID = processor group * 64 + processor index; Windows CPU Set IDs are different identifiers.',
            'affinity_support':'available' if len(groups)==1 else 'read-only: multiple processor groups',
            'x3d':{'status':'available' if candidates else 'unknown','processor_reports_x3d':reported,
                'label':'X3D cache group identified from Windows topology' if candidates else 'X3D cache group unverified',
                'cache_domain_ids':candidates,'frequency_domain_ids':[],
                'evidence':'Processor model plus consistent Windows cache-sharing masks and sizes; inferred cache technology.',
                'driver':{'status':'unsupported','registered':False,'bound_devices':[],'current_preference':None,'read_only':True,
                    'note':'Linux amd_x3d_vcache and CPPC sysfs are not Windows interfaces. Windows scheduler preference is not inferred.'}},
            'features':{'topology':'available' if cores else 'unknown','l3_cache':'available' if complete else 'partially available' if domains else 'unknown',
                'cppc':'unsupported','preferred_core':'unknown','frequency':'partially available',
                'capacity_classes':'available' if len({r.get('efficiency_class') for r in core_records})>1 else 'unknown'}}
        result['generation']=hashlib.sha256(json.dumps(result,sort_keys=True).encode()).hexdigest()[:20]
        result['graph']=TopologyReader.graph(result)
        return result


class WindowsProcesses(ProcessManager):
    def __init__(self, native):
        super().__init__()
        self.native=native

    def identity(self,pid,tid=None):
        return self.native.identity(pid,tid)

    def owned(self,pid,identity=None):
        try:
            if pid in (0,4,os.getpid()):
                raise HalawaCoreError('This process is protected from affinity experiments.',403)
            if self.native.process_sid(pid)!=self.native.current_sid:
                raise HalawaCoreError('Read-only due to permissions: target belongs to another Windows account.',403)
            if identity is not None and self.identity(pid)!=identity:
                raise HalawaCoreError('PID identity changed. Select the process again.',409)
            self.native.process_affinity(pid)
            with self.native.process_handle(pid) as handle:
                self.native.ensure_no_cpu_sets(handle)
            return psutil.Process(pid)
        except psutil.Error as exc:
            raise HalawaCoreError('Process is inaccessible or no longer exists.',409) from exc

    def detail(self,pid):
        try:
            p=psutil.Process(pid)
            identity=self.identity(pid)
            with p.oneshot():
                name,username=p.name(),p.username()
                try:exe=p.exe()
                except psutil.AccessDenied:exe=''
                try:args=p.cmdline()
                except psutil.AccessDenied:args=[]
                cpu_seconds=sum(p.cpu_times()[:2]);now=time.monotonic()
                previous=self.samples.get((pid,identity));usage=(cpu_seconds-previous[1])/(now-previous[0])*100 if previous and now>previous[0] else None
                self.samples[(pid,identity)]=now,cpu_seconds
                try:
                    affinity=sorted(self.native.process_affinity(pid));self.owned(pid,identity)
                    compatibility='Available for affinity testing'
                except HalawaCoreError:
                    affinity=None;compatibility='Read-only due to permissions or unsupported scheduling state'
                result={'pid':pid,'identity':identity,'name':name,'exe':exe,'command_summary':f'{Path(exe).name or name} · {max(0,len(args)-1)} arguments (hidden for privacy)',
                    'ppid':p.ppid(),'owner':username,'uid':username.casefold(),'status':p.status(),'compatibility':compatibility,
                    'cpu_percent':round(max(0,usage),2) if usage is not None else None,'memory_bytes':p.memory_info().rss,
                    'thread_count':p.num_threads(),'affinity':affinity,'cpu_seconds':cpu_seconds,'icon':None}
            if self.identity(pid)!=identity:
                raise HalawaCoreError('Process identity changed during discovery.',409)
            return result
        except psutil.Error as exc:
            raise HalawaCoreError('Process is inaccessible or no longer exists.',409) from exc

    def threads(self,pid):
        start=self.identity(pid);rows=[]
        try:
            for thread in psutil.Process(pid).threads():
                try:
                    identity=self.identity(pid,thread.id)
                    try:affinity=sorted(self.native.thread_affinity(pid,thread.id,identity));error=None
                    except HalawaCoreError as exc:affinity=None;error=exc.message
                    rows.append({'pid':pid,'tid':thread.id,'identity':identity,'affinity':affinity,'restriction':error})
                except HalawaCoreError:
                    continue
        except psutil.Error as exc:
            raise HalawaCoreError('Threads are inaccessible or no longer exist.',409) from exc
        if self.identity(pid)!=start:
            raise HalawaCoreError('Process identity changed while reading threads.',409)
        return sorted(rows,key=lambda r:int(r['identity']))

    def main_task(self,pid):
        # Windows PID is never assumed to be a TID. This default is explicitly labeled in the UI.
        rows=self.threads(pid)
        if not rows:raise HalawaCoreError('No surviving thread can be selected.',409)
        return rows[0]

    def installed(self):
        # No registry uninstall entry is falsely treated as a running executable identity.
        return []


class WindowsMetrics:
    def __init__(self,native):
        self.native=native;self.previous={};self.initial=True

    def sample(self):
        values=psutil.cpu_percent(interval=None,percpu=True)
        total=psutil.cpu_percent(interval=None)
        records=self.native.topology()
        ids=sorted({c for r in records if r['relationship']==0 for c in r['cpus']})
        # Do not guess ordering for sparse or multiple processor groups.
        mapped=len(values)==len(ids) and ids==list(range(len(values)))
        usage={str(c):(values[c] if mapped and not self.initial else None) for c in ids}
        first=self.initial;self.initial=False
        return {'timestamp':time.time(),'total_percent':None if first else total,'logical_cpus':usage,'frequency_khz':{},
            'source':'Windows performance counters via psutil','note':'Utilization only; per-CPU readings unavailable when ordering is unverified.'}

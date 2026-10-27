import {state,esc,fmt,list,heading,panel,bytes,toast,download} from './state.js';

export function coreGrid(selectable=false) {
  const allowed=new Set((selectable?state.plannerAllowed:null) ?? state.process?.affinity ?? state.topology.analyzer_allowed_cpus);
  return `<div class="core-grid">${state.topology.cores.map((core,i)=>{
    const active=core.logical_cpus.some(c=>state.selected.has(c));
    return `<article class="core ${selectable&&active?'selected':''}" data-core="${i}">
      <div class="core-header"><${selectable?'button type="button"':'span'} data-core-index="${i}" title="Physical core membership from Linux topology">${core.verified?'Core':'CPU group'} ${esc(core.core_id??core.logical_cpus[0])}</${selectable?'button':'span'}><span class="rank" title="Firmware CPPC highest_perf; unitless preference, not benchmark">${core.cppc_highest_perf??'—'}</span></div>
      <div class="cpu-chips">${core.logical_cpus.map(c=>{
        const online=state.topology.online_cpus.includes(c),eligible=online&&allowed.has(c);
        const label=state.numbering==='kde'?(state.topology.logical_cpus.find(r=>r.id===c)?.display_id??c):c;
        return `<label class="cpu-chip ${!online?'offline':''}" title="OS CPU ${c} · Display ${state.topology.logical_cpus.find(r=>r.id===c)?.display_id??c} · ${!online?'Offline':!eligible?'Outside current affinity':'Online'}">${selectable?`<input type="checkbox" data-cpu="${c}" ${state.selected.has(c)?'checked':''} ${eligible?'':'disabled'}>`:''}CPU ${label}</label>`;
      }).join('')}</div><div class="util-track"><div class="util-fill" data-util-bar="${core.logical_cpus.join(',')}"></div></div><div class="core-foot"><span>Socket ${esc(core.socket_id)} · ${core.smt_threads}T</span><span data-util="${core.logical_cpus.join(',')}">—</span></div></article>`;
  }).join('')}</div><div class="legend"><span>CPU utilization</span><span>CPPC firmware hint</span><span>Unavailable CPUs stay visible</span></div>`;
}

export function domainCards() {
  const domains=state.topology.cache_domains;
  if(!domains.length) return '<div class="notice neutral">X3D cache group unverified · Linux has not exposed reliable shared L3 domain data.</div>';
  return `<div class="domain-grid">${domains.map((d,i)=>`<article class="domain ${d.x3d_cache_candidate?'cache':''}"><div class="flex spread"><h3>L3 domain ${i+1}</h3><span class="badge ${d.x3d_cache_candidate?'green':d.frequency_candidate?'purple':''}">${d.x3d_cache_candidate?'Cache candidate':d.frequency_candidate?'Frequency candidate':d.verified?'Kernel verified':'Partial data'}</span></div><div class="domain-size">${d.size_bytes==null?'Unknown':fmt(d.size_bytes/1024/1024,0)}<small>${d.size_bytes==null?'L3 size':'MiB L3'}</small></div><div class="flex"><span class="pill">${d.physical_core_count} core groups</span><span class="pill">${d.logical_cpus.length} logical CPUs</span></div><p><span class="section-label">OS CPU IDS</span><br><span class="mono">${esc(list(d.logical_cpus))}</span></p><p><span class="section-label">DISPLAY IDS</span><br><span class="mono">${esc(list(d.display_cpus))}</span></p><details><summary>SMT mapping & topology evidence</summary><p>Package IDs: ${esc(list(d.package_ids))} · Die IDs: ${esc(list(d.die_ids))}<br>Die IDs do not define cache membership.</p>${Object.entries(d.smt_mapping).map(([k,v])=>`<p><span class="mono">${esc(k)}</span><br>OS IDs ${esc(list(v))}</p>`).join('')}<p>Max frequency range: ${d.max_frequency_range_khz?d.max_frequency_range_khz.map(v=>fmt(v/1000,0)).join('–')+' MHz':'Unverified'}</p><p>Online: ${esc(list(d.online_cpus))}<br>Analyzer allowed: ${esc(list(d.allowed_cpus))}</p><p>Cache IDs: ${esc(list(d.cache_ids))}</p><pre>${esc(d.evidence.join('\n'))}</pre></details></article>`).join('')}</div>`;
}

export function x3dStatus() {
  const x=state.topology.x3d,driver=x.driver;
  return `<dl class="keyvalues"><dt>Cache domains</dt><dd>${state.topology.cache_domain_count} detected</dd><dt>X3D classification</dt><dd>${esc(x.label)}</dd><dt>Scheduling driver</dt><dd>${esc(driver.status)}${driver.registered?' · registered':''}</dd><dt>Scheduler preference</dt><dd><span class="badge ${driver.current_preference?'green':''}">${esc(driver.current_preference || 'Not exposed')}</span> <span class="tiny muted">read-only</span></dd><dt>CPPC information</dt><dd>${esc(state.topology.features.cppc)}</dd></dl>${driver.bound_devices.length?`<details class="spacer"><summary>Exposed driver devices</summary>${driver.bound_devices.map(d=>`<p class="tiny">${esc(d.device)} · ${esc(d.raw_mode??'unreadable')} · read-only<br><span class="mono">${esc(d.path)}</span></p>`).join('')}</details>`:''}`;
}

export function updateUtilization(){
  if(!state.metrics) return;
  const average=ids=>{
    const values=ids.split(',').map(c=>state.metrics.logical_cpus[c]).filter(v=>v!=null);
    return values.length?values.reduce((a,b)=>a+b,0)/values.length:null;
  };
  document.querySelectorAll('[data-util]').forEach(el=>el.textContent=fmt(average(el.dataset.util),0)+'%');
  document.querySelectorAll('[data-util-bar]').forEach(el=>el.style.width=`${average(el.dataset.utilBar)||0}%`);
  document.querySelectorAll('[data-total]').forEach(el=>el.textContent=fmt(state.metrics.total_percent,1));
  document.querySelectorAll('[data-frequency]').forEach(el=>{
    const values=el.dataset.frequency.split(',').map(c=>state.metrics.frequency_khz?.[c]).filter(v=>v!=null);
    el.textContent=values.length?fmt(values.reduce((a,b)=>a+b,0)/values.length/1000,0)+' MHz':'—';
  });
}

export async function renderTopology(){
  const t=state.topology;
  document.querySelector('#content').innerHTML=heading('CPU topology','Physical cores, logical threads, and shared cache. Directly from your operating system.',`<button id="export-topology" class="secondary">↓ Export topology</button>`)+
    (t.warnings.length?`<div class="notice">${t.warnings.map(esc).join('<br>')}</div>`:'')+
    `<div class="split">${panel(esc(t.cpu_model),coreGrid(),`${t.physical_core_count??'Unverified'} physical cores · ${t.logical_cpu_count} logical CPUs · ${esc(t.architecture)}`,`<select id="numbering" aria-label="CPU display numbering"><option value="linux">OS CPU IDs</option><option value="kde">Display IDs</option></select>`)}${panel('Topology capabilities',x3dStatus()+`<div class="status-list spacer">${Object.entries(t.features).map(([k,v])=>`<span class="pill" title="${esc(v)}">${esc(k.replaceAll('_',' '))}: ${esc(v)}</span>`).join('')}</div>`)}</div>`+
    panel('Shared L3 cache domains',domainCards(),'Cache-sharing masks define domains; CCD or die identifiers remain separate.')+
    `<section class="panel"><div class="panel-head"><div><h2>Physical core details</h2><p>Physical core keys include topology identity; no fixed SMT layout is assumed.</p></div><select id="core-sort" aria-label="Sort physical core table"><option value="core">Core order</option><option value="cppc">CPPC preference</option><option value="frequency">Frequency</option><option value="usage">Utilization</option></select></div><div class="table-wrap" id="core-table"></div></section>`+
    panel('NUMA & membership graph',`<div class="notice neutral">NUMA locality and cache sharing can overlap. CPU affinity alone does not control memory allocation.</div>${t.numa_nodes.map(n=>`<details><summary>Node ${n.id} · OS IDs ${esc(list(n.logical_cpus))}</summary><p class="tiny">Allowed: ${esc(list(n.allowed_cpus))} · Relative distances: ${esc(n.distance)}</p><pre>${esc(n.memory)}</pre></details>`).join('')||'<p class="muted tiny">No NUMA metadata exposed.</p>'}<details class="spacer"><summary>Inspect membership graph (${t.graph.nodes.length} nodes)</summary><pre class="graph-detail">${esc(JSON.stringify(t.graph,null,2))}</pre></details>`);
  document.querySelector('#export-topology').onclick=()=>download('halawacore-topology.json',t);
  const numbering=document.querySelector('#numbering');numbering.value=state.numbering;
  numbering.onchange=()=>{state.numbering=numbering.value;localStorage.setItem('numbering',state.numbering);renderTopology();};
  const renderTable=()=>{
    const sort=document.querySelector('#core-sort').value;
    const frequency=c=>Math.max(...t.logical_cpus.filter(r=>c.logical_cpus.includes(r.id)).map(r=>r.frequency_khz||0));
    const usage=c=>c.logical_cpus.reduce((a,n)=>a+(state.metrics?.logical_cpus[n]||0),0)/c.logical_cpus.length;
    const cores=[...t.cores].sort((a,b)=>sort==='cppc'?(b.cppc_highest_perf||0)-(a.cppc_highest_perf||0):sort==='frequency'?frequency(b)-frequency(a):sort==='usage'?usage(b)-usage(a):a.logical_cpus[0]-b.logical_cpus[0]);
    document.querySelector('#core-table').innerHTML=`<table><thead><tr>${['Physical core','OS CPU IDs','Display IDs','SMT threads','CPPC / Rank','Usage','Frequency','Status / Capacity'].map(h=>`<th>${h}</th>`).join('')}</tr></thead><tbody>${cores.map(c=>`<tr><td><details><summary>Socket ${esc(c.socket_id)} · Core ${esc(c.core_id)}</summary><p class="mono">${esc(c.key)}</p><p>Die ${esc(c.die_id)} · ${c.verified?'Kernel topology':'Unverified'}</p></details></td><td class="mono">${esc(list(c.logical_cpus))}</td><td class="mono">${esc(list(c.display_cpus))}</td><td>${c.smt_threads}</td><td>${c.cppc_highest_perf??'—'} / ${c.prefcore_ranking??'—'}</td><td data-util="${c.logical_cpus.join(',')}">—</td><td data-frequency="${c.logical_cpus.join(',')}">${frequency(c)?fmt(frequency(c)/1000,0)+' MHz':'—'}</td><td>${c.online_cpus.length?'Online':'Offline'} · ${esc(c.capacity_class)}</td></tr>`).join('')}</tbody></table>`;
    updateUtilization();
  };document.querySelector('#core-sort').onchange=renderTable;renderTable();
}

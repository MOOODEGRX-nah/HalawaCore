import {state,esc,list,heading,panel,toast,navigate} from './state.js';
import {api} from './api.js';
import {coreGrid,updateUtilization} from './topology.js';

let detail,scope='main',workload='gaming';
export async function renderPlanner(){
  if(!state.process){document.querySelector('#content').innerHTML=heading('Affinity planner','Understand the current CPU set before designing an experiment.')+panel('Select a running process','<div class="empty"><h3>Every experiment starts with a real process.</h3><p>Choose a running application to see its current affinity, thread identities, and permitted experimental CPU sets.</p><a class="primary button" href="#applications">Browse running processes →</a></div>');return;}
  detail=await api(`/processes/${state.process.pid}`);
  if(detail.root.identity!==state.process.identity){state.process=null;throw new Error('Selected PID was reused. Select the application again.');}
  state.process=detail.root;
  const t=state.topology,p=state.process;
  state.selected=new Set([...state.selected].filter(c=>p.affinity?.includes(c)&&t.online_cpus.includes(c)));
  if(!state.recommendations.length){try{state.recommendations=(await api('/recommendations',{pid:p.pid,identity:p.identity,workload})).profiles;}catch(e){toast(e.message,true);}}
  const [history,threads]=await Promise.all([api('/experiments'),api(`/processes/${p.pid}/threads`)]);
  if(state.page!=='planner')return;
  document.querySelector('#content').innerHTML=heading('Affinity planner',`${p.name} · PID ${p.pid} · identity ${p.identity}`,`<a class="secondary button" href="#applications">Change process</a>`)+
    `${t.platform==='Windows'?'<div class="notice neutral">Windows default task means the oldest surviving thread, not PID = TID. Explicit CPU Sets and multiple processor groups stay read-only.</div>':''}<div class="notice ${state.settings.read_only?'neutral':''}">${state.settings.read_only?'Read-only mode is enabled. You can plan and preview. Enable experiments in Settings before applying a change.':'Experiments enabled. Applying affinity requires a fresh preview and explicit confirmation.'}</div>`+
    panel('Experiment scope',`<div class="form-grid"><label class="field">Workload<select id="workload">${['gaming','competitive gaming','browsing','communication','encoding','rendering','compilation','streaming','ai inference','background','custom','unknown'].map(w=>`<option value="${w}">${w[0].toUpperCase()+w.slice(1)}</option>`).join('')}</select></label><label class="field">Tasks included<select id="scope"><option value="main">Default task only</option><option value="task">One explicitly selected thread</option><option value="threads">Existing process threads</option><option value="related">Explicitly selected related processes & threads</option></select></label></div><div id="task-select" class="spacer" ${scope==='task'?'':'hidden'}><label class="field">Existing thread<select id="task-tid">${threads.threads.map(t=>`<option value="${t.tid}">TID ${t.tid} · OS IDs ${esc(list(t.affinity))}</option>`).join('')}</select></label><p class="tiny muted">The planner stays within the default task's current mask; preview also checks the chosen thread's mask.</p></div><div id="related-select" ${scope==='related'?'':'hidden'}>${detail.related.map(r=>`<label class="related-option"><input type="checkbox" data-related="${r.pid}" ${r.pid===p.pid?'checked disabled':''}> PID ${r.pid} · ${esc(r.name)} · start ${esc(r.identity)}</label>`).join('')}</div><p class="tiny muted">One-time coverage only. Newly created threads and child processes may not remain covered. OS affinity is per task, not a permanent application-wide rule.</p>${detail.integration.wine_or_proton_observed||detail.integration.steam_ancestry_observed?`<div class="notice neutral">${esc(detail.integration.guidance)}</div>`:''}`)+
    panel('Experimental profiles',`<div class="profiles-grid">${state.recommendations.map((r,i)=>`<article class="profile ${r.enabled?'':'disabled'}"><span class="badge ${r.id==='balanced'?'green':''}">${esc(r.confidence)}</span><h3>${esc(r.title)}</h3><div class="profile-set mono">OS IDs ${esc(list(r.linux_cpus))}<br>Display ${esc(list(r.display_cpus))}</div><p>${esc(r.explanation)}</p><button data-profile-index="${i}" class="secondary" ${r.enabled?'':'disabled'}>Use in planner</button></article>`).join('')}</div>`,'Suggestions remain within online CPUs and existing process affinity. No gain is guaranteed.')+
    panel('Build your CPU set',`<div class="toolbar"><button id="select-all" class="secondary">Select all permitted</button><button id="clear" class="secondary">Clear</button><button id="one-thread" class="secondary">One thread per core</button><button id="preferred" class="secondary">Preferred cores</button><button id="current" class="secondary">Restore current selection</button><select id="planner-numbering" aria-label="Display numbering"><option value="linux">OS CPU IDs</option><option value="kde">Display IDs</option></select></div><div id="planner-grid">${coreGrid(true)}</div><div id="selection-summary"></div><div class="flex spread"><button id="save-profile" class="secondary">Save CPU set as profile</button><button id="preview" class="primary">Preview affected tasks →</button></div>`,'Select siblings individually or select a physical core to include its eligible siblings.')+
    panel('Restore original affinity',`<div id="affinity-records">${renderRecords(history.affinity)}</div>`,'Each recorded thread has its own original mask. Restoration stays available in read-only mode.');
  document.querySelector('#workload').value=workload;
  document.querySelector('#scope').value=scope;
  document.querySelector('#scope').onchange=e=>{scope=e.target.value;document.querySelector('#related-select').hidden=scope!=='related';document.querySelector('#task-select').hidden=scope!=='task';};
  document.querySelector('#workload').onchange=async e=>{workload=e.target.value;try{state.recommendations=(await api('/recommendations',{pid:p.pid,identity:p.identity,workload})).profiles;await renderPlanner();}catch(err){toast(err.message,true);}};
  document.querySelector('#planner-numbering').value=state.numbering;
  document.querySelector('#planner-numbering').onchange=e=>{state.numbering=e.target.value;localStorage.setItem('numbering',state.numbering);redrawGrid();};
  document.querySelector('#select-all').onclick=()=>choose(p.affinity);
  document.querySelector('#clear').onclick=()=>choose([]);
  document.querySelector('#current').onclick=()=>choose(p.affinity);
  document.querySelector('#one-thread').onclick=()=>choose(t.cores.map(c=>c.logical_cpus.find(n=>p.affinity.includes(n)&&t.online_cpus.includes(n))).filter(n=>n!==undefined));
  document.querySelector('#preferred').onclick=()=>{
    const cores=t.cores.filter(c=>c.verified&&c.logical_cpus.some(n=>p.affinity.includes(n)));
    const ranked=cores.filter(c=>c.prefcore_ranking!=null||c.cppc_highest_perf!=null);
    if(!ranked.length){toast('Preferred-core information is unavailable. Current selection preserved.');return;}
    const best=Math.max(...ranked.map(c=>c.prefcore_ranking??c.cppc_highest_perf));
    choose(ranked.filter(c=>(c.prefcore_ranking??c.cppc_highest_perf)===best).flatMap(c=>c.logical_cpus));
  };
  document.querySelectorAll('[data-profile-index]').forEach(el=>el.onclick=()=>choose(state.recommendations[Number(el.dataset.profileIndex)].linux_cpus));
  document.querySelector('#preview').onclick=()=>preview().catch(e=>toast(e.message,true));
  document.querySelector('#save-profile').onclick=async()=>{
    if(!state.selected.size){toast('Select at least one CPU first.',true);return;}
    const name=window.prompt('Profile name');if(!name?.trim())return;
    try{await api('/profiles',{name:name.trim(),cpus:[...state.selected].sort((a,b)=>a-b),note:`Created for ${workload}; never applied automatically.`,generation:t.generation});toast('Profile saved. Loading it later requires a fresh review.');}catch(e){toast(e.message,true);}
  };
  bindRestore();bindGrid();summary();updateUtilization();
}

function choose(cpus){state.selected=new Set(cpus.filter(c=>state.process.affinity.includes(c)&&state.topology.online_cpus.includes(c)));redrawGrid();}
function redrawGrid(){document.querySelector('#planner-grid').innerHTML=coreGrid(true);bindGrid();summary();updateUtilization();}
function bindGrid(){
  document.querySelectorAll('[data-cpu]').forEach(el=>el.onchange=()=>{const cpu=Number(el.dataset.cpu);if(el.checked)state.selected.add(cpu);else state.selected.delete(cpu);summary();el.closest('.core').classList.toggle('selected',!!el.closest('.core').querySelector('input:checked'));});
  document.querySelectorAll('button[data-core-index]').forEach(el=>el.onclick=()=>{
    const cpus=state.topology.cores[Number(el.dataset.coreIndex)].logical_cpus.filter(c=>state.process.affinity.includes(c)&&state.topology.online_cpus.includes(c));
    const remove=cpus.every(c=>state.selected.has(c));cpus.forEach(c=>remove?state.selected.delete(c):state.selected.add(c));redrawGrid();
  });
}
function summary(){
  const cpus=[...state.selected].sort((a,b)=>a-b),current=state.process.affinity;
  document.querySelector('#selection-summary').innerHTML=`<div class="selection-summary"><div><p><strong>${cpus.length} selected</strong> of ${current.length} currently permitted CPUs</p><p class="mono">Proposed OS IDs: ${esc(list(cpus))}<br>Display IDs: ${esc(list(cpus.map(c=>state.topology.logical_cpus.find(r=>r.id===c)?.display_id??c)))}</p></div><div><p class="tiny muted">Current OS affinity</p><p class="mono">${esc(list(current))}</p></div></div>${cpus.length===1?'<div class="notice">A single logical CPU can severely limit a multithreaded workload.</div>':''}`;
  document.querySelector('#preview').disabled=!cpus.length;
}

async function preview(){
  const p=state.process,related=[...document.querySelectorAll('[data-related]:checked')].map(el=>{const r=detail.related.find(r=>r.pid===Number(el.dataset.related));return {pid:r.pid,identity:r.identity};});
  const result=await api('/affinity/preview',{pid:p.pid,identity:p.identity,cpus:[...state.selected].sort((a,b)=>a-b),scope,related,task_tid:scope==='task'?Number(document.querySelector('#task-tid').value):null});
  document.querySelector('#confirm-body').innerHTML=`<p>Requested OS CPU IDs: <strong class="mono">${esc(list(result.requested))}</strong><br>Scope: ${esc(scope)} · ${result.tasks.length} exact tasks · preview expires in 60 seconds.</p><div class="notice">${result.warnings.map(esc).join('<br>')}</div>${state.settings.read_only?'<div class="notice">Read-only mode blocks applying. Enable experiments in Settings, then create a new preview.</div>':''}<div class="table-wrap"><table><thead><tr><th>PID</th><th>TID</th><th>Task start ticks</th><th>Original OS affinity</th></tr></thead><tbody>${result.tasks.map(t=>`<tr><td>${t.pid}</td><td>${t.tid}</td><td>${esc(t.identity)}</td><td class="mono">${esc(list(t.original))}</td></tr>`).join('')}</tbody></table></div>`;
  const dialog=document.querySelector('#confirm-dialog'),check=document.querySelector('#confirm-check'),apply=document.querySelector('#confirm-apply');
  check.checked=false;apply.disabled=true;check.onchange=()=>apply.disabled=!check.checked||state.settings.read_only;
  dialog.returnValue='cancel';dialog.showModal();
  dialog.onclose=async()=>{
    if(dialog.returnValue!=='apply')return;
    try{
      const record=await api('/affinity/apply',{preview_id:result.preview_id,confirmed:true});
      toast(record.status==='active'?'Kernel verified the requested CPU set. Restore is available.':'Some tasks failed. Review the record and restore original affinities.',record.status!=='active');
      state.recommendations=[];state.topology=await api('/cpu/topology');await renderPlanner();
    }catch(e){toast(e.message,true);}
  };
}

export function renderRecords(records){
  return records.length?records.slice().reverse().map(r=>`<article class="domain spacer"><div class="flex spread"><span class="mono tiny">${esc(r.id)} · ${esc(r.status)}</span><button class="secondary" data-restore="${r.id}" ${r.status==='restored'?'disabled':''}>Restore original affinity</button></div><p>Requested OS CPU IDs: ${esc(list(r.requested))} · ${r.tasks.length} recorded tasks</p><details><summary>Per-thread verification & restoration</summary>${r.tasks.map(t=>`<p>PID ${t.pid} / TID ${t.tid} · ${esc(t.state)}<br>Original ${esc(list(t.original))}<br>Accepted ${esc(list(t.accepted))}${t.error?`<br>${esc(t.error)}`:''}${t.restore_error?`<br>Restore: ${esc(t.restore_error)}`:''}</p>`).join('')}</details></article>`).join(''):'<p class="tiny muted">No affinity experiments in this backend session.</p>';
}
export function bindRestore(){
  document.querySelectorAll('[data-restore]').forEach(el=>el.onclick=async()=>{
    el.disabled=true;
    try{const r=await api('/affinity/restore',{experiment_id:el.dataset.restore});toast(r.status==='restored'?'Original per-thread affinity restored and verified.':'Partial restoration: inspect task errors.',r.status!=='restored');state.recommendations=[];document.dispatchEvent(new CustomEvent('halawacore-render'));}catch(e){toast(e.message,true);el.disabled=false;}
  });
}

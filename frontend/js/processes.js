import {state,esc,fmt,list,bytes,heading,panel,toast,navigate} from './state.js';
import {api} from './api.js';
import {processKey,reconcileSelection,selectionLimit} from './process-selection.js';

let tab='running', rows=[], sort='cpu', query='', selectedDetail=null,drawRunning=null;
export async function refreshProcesses(){
  if(tab!=='running'||state.page!=='applications'||!drawRunning)return;
  const data=await api('/processes');
  if(state.page==='applications'&&tab==='running'){rows=data.processes;drawRunning();}
}
export async function selectProcess(pid,identity){
  const detail=await api(`/processes/${pid}`);
  if(detail.root.identity!==identity) throw new Error('Process identity changed. Refresh the process list.');
  state.process=detail.root; state.targets=[detail.root];state.plannerAllowed=null;
  state.selected=new Set(detail.root.affinity||[]); state.recommendations=[];
  selectedDetail=detail; navigate('planner');
}

async function planSelected(){
  const selected=[...state.processSelection.values()];
  if(!selected.length)return;
  state.targets=selected;state.process=selected[0];
  state.selected=new Set(state.process.affinity||[]);state.plannerAllowed=null;state.recommendations=[];
  navigate('planner');
}

export async function renderProcesses(){
  document.querySelector('#content').innerHTML=heading('Applications & processes','Find the running task. Verify its identity. Choose exactly what an experiment covers.')+
    `<div class="tabs"><button id="running-tab" class="${tab==='running'?'active':''}">Running processes</button><button id="installed-tab" class="${tab==='installed'?'active':''}">Installed applications</button><button id="executable-tab" class="${tab==='executable'?'active':''}">Executable metadata</button></div><div id="process-content" class="loading">Reading processes…</div>`;
  for(const name of ['running','installed','executable'])document.querySelector(`#${name}-tab`).onclick=()=>{tab=name;renderProcesses().catch(e=>toast(e.message,true));};
  const content=document.querySelector('#process-content');
  if(tab==='executable'){
    content.className='';content.innerHTML=panel('Inspect a local executable',`<div class="notice neutral">Select a file through your browser to inspect its name, size and file type. The file is not uploaded or executed. Executable internals and launch configuration are unavailable in this browser workflow.</div><label class="field">Choose a local executable<input id="executable-file" type="file"></label><div id="file-metadata" class="spacer"></div>`);
    document.querySelector('#executable-file').onchange=e=>{
      const f=e.target.files[0];if(f)document.querySelector('#file-metadata').innerHTML=`<dl class="keyvalues"><dt>Name</dt><dd>${esc(f.name)}</dd><dt>Size</dt><dd>${bytes(f.size)}</dd><dt>Reported media type</dt><dd>${esc(f.type||'Unknown')}</dd><dt>Status</dt><dd>Not currently running · Insufficient information for affinity</dd><dt>Launch support</dt><dd>Unsupported in this release</dd></dl>`;
    };return;
  }
  if(tab==='installed'){
    if(state.topology.platform==='Windows'){
      content.className='';content.innerHTML=panel('Installed applications','<div class="notice neutral">Installed application catalog discovery is not available on Windows in this release. Use Running processes to select a real accessible process for analysis and affinity experiments.</div>');return;
    }
    const data=await api('/applications');if(state.page!=='applications')return;
    content.className='';content.innerHTML=`<div class="notice neutral">XDG and accessible Flatpak desktop entries. An installed entry does not establish a running process identity. Select a verified process in Running processes for affinity testing.</div><div class="toolbar"><input id="app-search" type="search" placeholder="Search name or desktop application ID" aria-label="Search installed applications"></div><div id="app-list" class="app-list"></div>`;
    const draw=()=>{const q=document.querySelector('#app-search').value.toLowerCase();document.querySelector('#app-list').innerHTML=data.applications.filter(a=>`${a.name} ${a.id}`.toLowerCase().includes(q)).map(a=>`<article class="app-entry"><h3>${esc(a.name)}</h3><p class="mono">${esc(a.id)}</p><p>${esc(a.compatibility)}</p>${a.flatpak_id?`<span class="badge">Flatpak · ${esc(a.flatpak_id)}</span>`:''}</article>`).join('')||'<p class="muted">No matching accessible desktop entries.</p>';};document.querySelector('#app-search').oninput=draw;draw();return;
  }
  rows=(await api('/processes')).processes;if(state.page!=='applications')return;
  content.className='';content.innerHTML=`<div class="toolbar"><input id="process-search" type="search" value="${esc(query)}" placeholder="Search process name, executable, or PID…" aria-label="Search running processes"><select id="process-sort" aria-label="Sort processes"><option value="cpu">CPU usage</option><option value="name">Name</option><option value="pid">PID</option><option value="memory">Memory</option></select><button id="process-refresh" class="secondary">↻ Refresh processes</button><span class="pill" id="process-count"></span></div><div id="process-selection" class="process-selection" role="region" aria-label="Process selection"></div><section class="panel"><div class="table-wrap" id="process-table"></div></section><div id="process-details"></div>`;
  document.querySelector('#process-sort').value=sort;
  document.querySelector('#process-search').oninput=e=>{query=e.target.value;draw();};
  document.querySelector('#process-sort').onchange=e=>{sort=e.target.value;draw();};
  document.querySelector('#process-refresh').onclick=async()=>{try{rows=(await api('/processes')).processes;draw();}catch(e){toast(e.message,true);}};
  drawRunning=draw;draw();
  function draw(){
    const focused=document.activeElement?.dataset.selectProcess;
    const previous=state.processSelection.size;
    state.processSelection=reconcileSelection(state.processSelection,rows);
    if(previous>state.processSelection.size)toast('Some selected processes exited or changed identity and were removed. Review your selection.');
    const filtered=rows.filter(r=>`${r.pid} ${r.name} ${r.exe} ${(r.desktop_ids||[]).join(' ')}`.toLowerCase().includes(query.toLowerCase()));
    filtered.sort((a,b)=>sort==='name'?a.name.localeCompare(b.name):sort==='pid'?a.pid-b.pid:sort==='memory'?b.memory_bytes-a.memory_bytes:(b.cpu_percent||0)-(a.cpu_percent||0));
    const eligible=filtered.filter(row=>row.affinity?.length),chosen=state.processSelection;
    document.querySelector('#process-count').textContent=`${filtered.length} accessible`;
    document.querySelector('#process-selection').innerHTML=`<div class="flex spread"><strong>${chosen.size} processes selected</strong><div class="flex"><button id="clear-process-selection" class="secondary" ${chosen.size?'':'disabled'}>Clear process selection</button><button id="plan-selected" class="primary" ${chosen.size?'':'disabled'}>Plan selected processes →</button></div></div><p class="tiny muted">Select up to 32 processes. Search and refresh keep your selection. Only explicitly selected processes and their existing threads are included.</p><div class="process-selection-chips">${[...chosen.values()].map(row=>`<span class="pill"><span data-no-i18n>${esc(row.name)}</span> · PID ${row.pid}<button class="text-button" data-remove-process="${row.pid}" aria-label="Remove process PID ${row.pid}">×</button></span>`).join('')}</div>`;
    document.querySelector('#clear-process-selection').onclick=()=>{state.processSelection.clear();draw();};
    document.querySelector('#plan-selected').onclick=async event=>{event.currentTarget.disabled=true;try{await planSelected();}catch(error){toast(error.message,true);if(state.page==='applications')draw();}};
    document.querySelectorAll('[data-remove-process]').forEach(button=>button.onclick=()=>{const row=rows.find(row=>row.pid===Number(button.dataset.removeProcess));if(row)chosen.delete(processKey(row));draw();});
    document.querySelector('#process-table').innerHTML=`<table><thead><tr><th class="process-check"><input type="checkbox" id="select-visible-processes" aria-label="Select visible processes" ${eligible.length?'':'disabled'}></th><th>Process / executable</th><th>PID</th><th>CPU</th><th>Memory</th><th>Threads</th><th>Owner</th><th>Current affinity</th><th>Inspect</th></tr></thead><tbody>${filtered.map(r=>`<tr class="${chosen.has(processKey(r))?'selected-row':''}"><td class="process-check"><input type="checkbox" data-select-process="${r.pid}" aria-label="Select process PID ${r.pid}" ${chosen.has(processKey(r))?'checked':''} ${r.affinity?.length?'':'disabled'}></td><td class="long"><strong data-no-i18n>${esc(r.name)}</strong><div class="muted tiny" title="${esc(r.exe)}">${esc(r.exe)}</div></td><td class="mono">${r.pid}</td><td>${fmt(r.cpu_percent)}%</td><td>${bytes(r.memory_bytes)}</td><td>${r.thread_count}</td><td data-no-i18n>${esc(r.owner)}</td><td class="long mono" title="${esc(list(r.affinity))}">${esc(list(r.affinity))}</td><td><button class="text-button" data-inspect="${r.pid}">Inspect →</button></td></tr>`).join('')}</tbody></table>`;
    const all=document.querySelector('#select-visible-processes'),count=eligible.filter(row=>chosen.has(processKey(row))).length;
    all.checked=eligible.length>0&&count===eligible.length;all.indeterminate=count>0&&count<eligible.length;
    all.onchange=()=>{
      if(all.checked){
        for(const row of eligible){if(chosen.has(processKey(row)))continue;if(chosen.size>=selectionLimit){toast('Select at most 32 processes per experiment.',true);break;}chosen.set(processKey(row),row);}
      }else eligible.forEach(row=>chosen.delete(processKey(row)));
      draw();
    };
    document.querySelectorAll('[data-select-process]').forEach(checkbox=>checkbox.onchange=()=>{
      const row=rows.find(row=>row.pid===Number(checkbox.dataset.selectProcess)),key=processKey(row);
      if(checkbox.checked){if(chosen.size>=selectionLimit)toast('Select at most 32 processes per experiment.',true);else chosen.set(key,row);}else chosen.delete(key);
      draw();
    });
    document.querySelectorAll('[data-inspect]').forEach(el=>el.onclick=()=>inspect(Number(el.dataset.inspect)).catch(e=>toast(e.message,true)));
    if(focused)document.querySelector(`[data-select-process="${focused}"]`)?.focus({preventScroll:true});
  }
}

async function inspect(pid){
  const [detail,threads]=await Promise.all([api(`/processes/${pid}`),api(`/processes/${pid}/threads`)]);
  if(state.page!=='applications')return;
  const p=detail.root;
  document.querySelector('#process-details').innerHTML=panel(`<span data-no-i18n>${esc(p.name)}</span> <span class="muted mono">PID ${p.pid}</span>`,`<dl class="keyvalues"><dt>Compatibility</dt><dd>${esc(p.compatibility)}</dd><dt>Executable</dt><dd class="mono">${esc(p.exe)}</dd><dt>Command summary</dt><dd>${esc(p.command_summary)}</dd><dt>Identity / parent</dt><dd>Start ticks ${esc(p.identity)} · parent ${p.ppid}</dd><dt>Runtime evidence</dt><dd>Steam ancestry: ${detail.integration.steam_ancestry_observed?'observed':'not observed'} · Wine/Proton: ${detail.integration.wine_or_proton_observed?'observed':'not observed'}</dd><dt>Game candidates</dt><dd>${esc(list(detail.integration.game_process_candidates))} · verify the actual game manually</dd></dl><p class="notice neutral spacer">${esc(detail.integration.guidance)}</p><details><summary>Existing threads (${threads.threads.length})</summary><div class="table-wrap"><table><thead><tr><th>TID</th><th>Start ticks</th><th>OS affinity</th></tr></thead><tbody>${threads.threads.map(t=>`<tr><td>${t.tid}</td><td>${esc(t.identity)}</td><td>${esc(list(t.affinity))}</td></tr>`).join('')}</tbody></table></div></details><details class="spacer"><summary>Observed related processes (${detail.related.length})</summary>${detail.related.map(r=>`<p class="tiny">PID ${r.pid} · ${esc(r.name)} · ${esc(r.compatibility)}</p>`).join('')}</details><div class="spacer"><button id="plan-process" class="primary">Select for affinity planner →</button></div>`,'Affinity applies to explicitly selected tasks. Process names alone do not establish application grouping.');
  document.querySelector('#plan-process').onclick=()=>selectProcess(pid,p.identity).catch(e=>toast(e.message,true));
  document.querySelector('#process-details').scrollIntoView({behavior:'smooth',block:'start'});
}

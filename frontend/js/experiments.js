import {state,esc,fmt,list,heading,panel,toast,download} from './state.js';
import {api} from './api.js';
import {chart} from './charts.js';
import {renderRecords,bindRestore} from './affinity.js';

export async function renderLab(){
  document.querySelector('#content').innerHTML=heading('Performance lab','Measure a baseline, try an experiment, then measure again after restoration.',`<button id="export-experiments" class="secondary">↓ Export measurements</button>`)+
    `<div class="notice neutral">CPU utilization measures activity, not application speed. HalawaCore does not infer FPS, frame times, power, temperatures, or latency. Process CPU usage may exceed 100% across multiple logical CPUs.</div>`+
    panel('Record a comparison',`${state.targets.length>1?'<p class="notice neutral">Performance Lab records the first selected process only.</p>':''}${state.process?`<p class="tiny muted">Selected: ${esc(state.process.name)} · PID ${state.process.pid} · start ${esc(state.process.identity)}</p>`:'<p class="tiny muted">Select a process in Applications before recording.</p>'}<div class="form-grid"><label class="field">Recording phase<select id="recording-phase"><option value="baseline">Baseline · original affinity</option><option value="experiment">Experiment · modified affinity</option><option value="restored">Result · restored affinity</option></select></label><label class="field">Sampling interval<select id="sample-interval"><option value="1">1 second</option><option value="2" selected>2 seconds</option><option value="5">5 seconds</option><option value="10">10 seconds</option></select></label></div><div class="flex spacer"><button id="start-recording" class="primary" ${state.process?'':'disabled'}>● Start recording</button><button id="stop-recording" class="secondary">Stop recording</button><span class="tiny muted">Phase labels are manual; every sample includes the actual observed affinity.</span></div>`)+
    '<div id="lab-results" class="loading">Reading recordings…</div>';
  document.querySelector('#start-recording').onclick=async()=>{
    try{const p=state.process;await api('/experiments/start',{pid:p.pid,identity:p.identity,phase:document.querySelector('#recording-phase').value,interval:Number(document.querySelector('#sample-interval').value)});toast('Recording real system measurements.');await updateLab();}catch(e){toast(e.message,true);}
  };
  document.querySelector('#stop-recording').onclick=async()=>{try{await api('/experiments/stop',{});await updateLab();}catch(e){toast(e.message,true);}};
  document.querySelector('#export-experiments').onclick=async()=>{try{download('halawacore-experiments.json',await api('/experiments'));}catch(e){toast(e.message,true);}};
  await updateLab();
}

export async function updateLab(){
  const data=await api('/experiments');
  if(state.page!=='lab'||!document.querySelector('#lab-results'))return;
  const recordings=data.recordings,active=recordings.find(r=>r.status==='recording');
  document.querySelector('#start-recording').disabled=!!active||!state.process;
  document.querySelector('#stop-recording').disabled=!active;
  document.querySelector('#lab-results').className='';
  document.querySelector('#lab-results').innerHTML=panel('Recorded phases',recordings.length?`<div class="sample-list">${recordings.map(r=>`<article class="sample-summary"><div class="flex spread"><h3>${esc(r.phase)}</h3><span class="badge ${r.status==='recording'?'green':''}">${esc(r.status)}</span></div><dl class="keyvalues"><dt>Duration</dt><dd>${fmt(r.summary.duration_seconds)} s</dd><dt>Samples</dt><dd>${r.summary.sample_count}</dd><dt>Average system</dt><dd>${fmt(r.summary.average_cpu_percent)}%</dd><dt>Peak system</dt><dd>${fmt(r.summary.peak_cpu_percent)}%</dd><dt>Average process</dt><dd>${fmt(r.summary.average_process_cpu_percent)}%</dd><dt>Observed affinity</dt><dd class="mono">${esc(list(r.samples.at(-1)?.affinity))}</dd><dt>Threads / memory</dt><dd>${r.samples.at(-1)?.thread_count??'—'} / ${r.samples.at(-1)?fmt(r.samples.at(-1).memory_bytes/1024/1024)+' MiB':'—'}</dd></dl>${r.error?`<p class="danger tiny">${esc(r.error)}</p>`:''}</article>`).join('')}</div>`:'<div class="empty"><h3>Your measurements start here.</h3><p>Run a representative workload, then record its original CPU affinity as the baseline.</p></div>')+
    (recordings.length?panel('Process CPU activity',chart(recordings.at(-1).samples,'process_cpu_percent',true),'Latest recording · utilization can exceed 100% across multiple CPUs')+panel('Per-CPU load distribution',`<div class="table-wrap"><table><thead><tr><th>Phase</th>${state.topology.online_cpus.map(c=>`<th>CPU ${c}</th>`).join('')}</tr></thead><tbody>${recordings.map(r=>`<tr><td>${esc(r.phase)}</td>${state.topology.online_cpus.map(c=>{const v=r.samples.map(s=>s.logical_cpus[String(c)]).filter(v=>v!=null);return `<td>${fmt(v.length?v.reduce((a,b)=>a+b,0)/v.length:null)}%</td>`;}).join('')}</tr>`).join('')}</tbody></table></div>`):'')+
    panel('Affinity experiments & restoration',renderRecords(data.affinity),'Restoration is per recorded task and is verified against the kernel.');
  bindRestore();
}

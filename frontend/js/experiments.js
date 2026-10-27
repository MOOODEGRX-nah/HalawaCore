import {state,esc,fmt,list,heading,panel,toast,download} from './state.js';
import {api} from './api.js';
import {chart,comparisonChart} from './charts.js';
import {difference} from './cpu-usage.js';
import {renderRecords,bindRestore} from './affinity.js';

let beforeId='',afterId='',comparison=null,comparisonKey='',comparisonError='';
const value=(number,unit='%',factor=1)=>Number.isFinite(number)?`${fmt(number*factor)}${unit}`:'—';
const sameProcess=(a,b)=>a&&b&&a.pid===b.pid&&a.identity===b.identity;

export async function renderLab(){
  document.querySelector('#content').innerHTML=heading('Performance lab','Record before, make a deliberate change, then record after under the same workload.',`<button id="export-experiments" class="secondary">↓ Export measurements</button>`)+
    '<div class="notice neutral">CPU activity is not game performance. Lower CPU usage alone does not prove higher FPS or better frame times. Device share uses all online logical CPUs visible to the OS, independently of affinity limits or container quotas.</div>'+
    panel('Record before and after',`${state.targets.length>1?'<p class="notice neutral">Performance Lab records the first selected process only.</p>':''}${state.process?`<p class="tiny muted"><span>Selected:</span> <strong data-no-i18n>${esc(state.process.name)}</strong> · PID ${state.process.pid} · ${esc(state.process.identity)}</p>`:'<p class="tiny muted">Select a process in Applications before recording.</p>'}<ol class="comparison-steps"><li>Record at least 30 seconds before the change, then stop.</li><li>Change the CPU set in Affinity Planner, then return here.</li><li>Repeat the same scene and settings, record after, then stop to compare.</li></ol><div class="form-grid"><label class="field">Sampling interval<select id="sample-interval"><option value="1">1 second</option><option value="2" selected>2 seconds</option><option value="5">5 seconds</option><option value="10">10 seconds</option></select></label><a class="secondary button" href="#planner">Open Affinity Planner →</a></div><div class="flex spacer recording-actions"><button id="record-before" class="secondary" ${state.process?'':'disabled'}>● Record before</button><button id="record-after" class="primary" disabled>● Record after</button><button id="stop-recording" class="secondary" disabled>Stop recording</button></div><p id="recording-status" class="tiny muted" role="status"></p><p class="tiny muted">Recording does not change affinity. Before and after are manual labels; every sample records the observed CPU set. Recordings stay in this backend session; export before closing.</p>`)+
    '<div id="lab-results" class="loading">Reading recordings…</div>';
  async function start(phase){
    try{const p=state.process;await api('/experiments/start',{pid:p.pid,identity:p.identity,phase,interval:Number(document.querySelector('#sample-interval').value)});toast('Recording real system measurements.');await updateLab();}catch(error){toast(error.message,true);}
  }
  document.querySelector('#record-before').onclick=()=>start('baseline');
  document.querySelector('#record-after').onclick=()=>start('experiment');
  document.querySelector('#stop-recording').onclick=async()=>{try{const stopped=await api('/experiments/stop',{}),row=stopped.recordings.at(-1);if(row?.status==='complete'&&row.summary.valid_process_samples>=2){if(row.phase==='baseline'){beforeId=row.id;afterId='';}else afterId=row.id;comparisonKey='';}await updateLab();}catch(error){toast(error.message,true);}};
  document.querySelector('#export-experiments').onclick=async()=>{try{download('halawacore-experiments.json',{...await api('/experiments'),comparison});}catch(error){toast(error.message,true);}};
  await updateLab();
}

export async function updateLab(){
  const data=await api('/experiments');
  if(state.page!=='lab'||!document.querySelector('#lab-results'))return;
  const recordings=data.recordings,active=recordings.find(row=>row.status==='recording');
  const ready=recordings.filter(row=>row.status==='complete'&&row.summary.valid_process_samples>=2);
  const beforeRows=ready.filter(row=>row.phase==='baseline'&&(!state.process||sameProcess(row,state.process)));
  if(!beforeRows.some(row=>row.id===beforeId))beforeId=(beforeRows.filter(row=>sameProcess(row,state.process)).at(-1)||beforeRows.at(-1))?.id||'';
  const before=beforeRows.find(row=>row.id===beforeId);
  const afterRows=ready.filter(row=>row.phase!=='baseline'&&sameProcess(row,before)&&(row.started_monotonic??row.started_at)>=(before.stopped_monotonic??before.stopped_at));
  if(!afterRows.some(row=>row.id===afterId))afterId=afterRows.at(-1)?.id||'';
  const after=afterRows.find(row=>row.id===afterId),key=`${beforeId}:${afterId}`;
  if(key!==comparisonKey){
    comparisonKey=key;comparison=null;comparisonError='';
    if(before&&after){try{const result=await api('/experiments/compare',{before_id:beforeId,after_id:afterId});if(comparisonKey!==key)return;comparison=result;}catch(error){if(comparisonKey!==key)return;comparisonError=error.message;}}
  }
  if(state.page!=='lab'||!document.querySelector('#lab-results'))return;
  document.querySelector('#record-before').disabled=!!active||!state.process;
  document.querySelector('#record-after').disabled=!!active||!state.process||!beforeRows.some(row=>sameProcess(row,state.process));
  document.querySelector('#stop-recording').disabled=!active;
  document.querySelector('#sample-interval').disabled=!!active;
  document.querySelector('#recording-status').textContent=active?`Recording · ${active.summary.sample_count} samples · ${fmt(active.summary.duration_seconds,0)} s`:!beforeRows.some(row=>sameProcess(row,state.process))?'Start with a before recording. At least two valid CPU samples are required.':'Ready for an after recording. Use the same workload and a similar duration.';
  const option=row=>`PID ${row.pid} · ${row.id.slice(0,8)} · ${fmt(row.summary.duration_seconds,0)} s · ${row.summary.valid_process_samples}`;
  document.querySelector('#lab-results').className='';
  document.querySelector('#lab-results').innerHTML=panel('Before / after / difference',`<div class="form-grid"><label class="field">Before recording<select id="comparison-before" ${beforeRows.length?'':'disabled'}>${beforeRows.length?beforeRows.map(row=>`<option value="${row.id}">${option(row)}</option>`).join(''):'<option value="">No completed before recording</option>'}</select></label><label class="field">After recording<select id="comparison-after" ${afterRows.length?'':'disabled'}>${afterRows.length?afterRows.map(row=>`<option value="${row.id}">${option(row)}</option>`).join(''):'<option value="">No matching completed after recording</option>'}</select></label></div><p class="tiny muted">Only completed recordings of the same PID and start identity can be compared. Each phase needs two valid CPU samples.</p>${comparisonError?`<p class="notice">${esc(comparisonError)}</p>`:''}${comparison?comparisonBody(comparison,before,after):'<div class="empty"><h3>Finish a before and after pair to see the difference.</h3><p>The comparison appears automatically after stopping both recordings. Record a fresh baseline if the game restarts.</p></div>'}`)+
    panel('Recorded phases',recordings.length?`<div class="sample-list">${recordings.map(row=>`<article class="sample-summary"><div class="flex spread"><h3>${row.phase==='baseline'?'Before':row.phase==='experiment'?'After':'Restored'}</h3><span class="badge">${esc(row.status)}</span></div><p class="mono tiny">PID ${row.pid} · ${row.id.slice(0,8)}</p><dl class="keyvalues"><dt>Duration</dt><dd>${fmt(row.summary.duration_seconds)} s</dd><dt>Valid CPU samples</dt><dd>${row.summary.valid_process_samples} / ${row.summary.sample_count}</dd><dt>Average process · device share</dt><dd>${value(row.summary.average_process_device_percent)}</dd><dt>Average process · per-CPU total</dt><dd>${value(row.summary.average_process_cpu_percent)}</dd><dt>Average system</dt><dd>${value(row.summary.average_cpu_percent)}</dd><dt>Observed affinity</dt><dd class="mono">${esc(list(row.samples.at(-1)?.affinity))}</dd></dl>${row.error?`<p class="danger tiny">${esc(row.error)}</p>`:''}</article>`).join('')}</div>`:'<p class="muted">Your measurements start here.</p>')+
    (recordings.length?panel('Process CPU activity',chart(recordings.at(-1).samples,'process_cpu_percent_device',true),'Latest recording · share of the visible device capacity')+panel('Per-CPU load distribution',`<div class="table-wrap"><table><thead><tr><th>Phase</th>${state.topology.online_cpus.map(cpu=>`<th>CPU ${cpu}</th>`).join('')}</tr></thead><tbody>${recordings.map(row=>`<tr><td>${row.phase==='baseline'?'Before':row.phase==='experiment'?'After':'Restored'}</td>${state.topology.online_cpus.map(cpu=>{const values=row.samples.map(sample=>sample.logical_cpus[String(cpu)]).filter(v=>v!=null);return `<td>${fmt(values.length?values.reduce((a,b)=>a+b,0)/values.length:null)}%</td>`;}).join('')}</tr>`).join('')}</tbody></table></div>`):'')+
    panel('Affinity experiments & restoration',renderRecords(data.affinity),'Restoration is per recorded task and is verified against the kernel.');
  document.querySelector('#comparison-before').value=beforeId;
  document.querySelector('#comparison-after').value=afterId;
  document.querySelector('#comparison-before').onchange=event=>{beforeId=event.target.value;afterId='';updateLab().catch(error=>toast(error.message,true));};
  document.querySelector('#comparison-after').onchange=event=>{afterId=event.target.value;updateLab().catch(error=>toast(error.message,true));};
  bindRestore();
}

function comparisonBody(result,before,after){
  const definitions=[['Average process · device share','average_process_device_percent','%',1],['Peak process · device share','peak_process_device_percent','%',1],['Average logical CPU equivalents','average_logical_equivalents','',1],['Average process · per-CPU total','average_process_cpu_percent','%',1],['Average system','average_cpu_percent','%',1],['Peak system','peak_cpu_percent','%',1],['Average memory','average_memory_bytes',' MiB',1/1024**2],['Average threads','average_thread_count','',1]];
  return `<p class="tiny muted"><span>Compared process:</span> <span class="mono">PID ${result.pid} · ${esc(result.identity)}</span> · <span>Visible logical CPUs:</span> ${result.online_cpus.length}</p><div class="table-wrap comparison-table"><table><thead><tr><th>Measurement</th><th>Before</th><th>After</th><th>Difference · after − before</th></tr></thead><tbody>${definitions.map(([label,key,unit,factor])=>{const metric=result.metrics[key];return `<tr><td>${label}</td><td>${value(metric.before,unit,factor)}</td><td>${value(metric.after,unit,factor)}</td><td>${difference(metric.difference==null?null:metric.difference*factor,unit==='%'?' pp':unit)}</td></tr>`;}).join('')}<tr><td>Duration</td><td>${value(before.summary.duration_seconds,' s')}</td><td>${value(after.summary.duration_seconds,' s')}</td><td>—</td></tr><tr><td>Valid CPU samples</td><td>${before.summary.valid_process_samples}</td><td>${after.summary.valid_process_samples}</td><td>—</td></tr><tr><td>Observed affinity</td><td class="mono">${esc(before.summary.observed_affinities.map(mask=>list(mask)).join(' / '))}</td><td class="mono">${esc(after.summary.observed_affinities.map(mask=>list(mask)).join(' / '))}</td><td>—</td></tr></tbody></table></div><p class="tiny muted">Percentage differences use percentage points (pp). A negative CPU difference means less CPU activity, not proven faster gameplay.</p><div class="comparison-legend"><span>Before</span><span>After</span></div>${comparisonChart(before.samples,after.samples)}<p class="tiny muted">Both curves start at elapsed time zero. Compare the same scene; this is not an FPS chart.</p><div class="notice neutral">${result.warnings.map(warning=>`<p>${esc(warning)}</p>`).join('')}</div>`;
}

import {state,esc,heading,panel,toast,download,navigate,list} from './state.js';
import {api} from './api.js';
import {initUpdates} from './updates.js';

export function renderSettings(){
  document.querySelector('#content').innerHTML=heading('Settings','Local preferences and explicit control over experiments.')+panel('Safety & display',`<div class="settings-row"><div><h3>Language</h3><p>العربية / English</p></div><select data-language-select data-no-i18n aria-label="Interface language"><option value="ar">العربية</option><option value="en">English</option></select></div>
    <div class="settings-row"><div><h3>Read-only mode</h3><p>Starts enabled each backend session. Disable to allow separately confirmed affinity experiments.</p></div><label class="chip-label"><input id="read-only" type="checkbox" ${state.settings.read_only?'checked':''}> Read-only</label></div>
    <div class="settings-row"><div><h3>KDE numbering calibration</h3><p>OS CPU 0 can display as CPU 1. Confirm the mapping in your own desktop.</p></div><select id="offset" aria-label="KDE numbering mapping"><option value="1">KDE = Linux ID + 1</option><option value="0">KDE = Linux ID</option></select></div>
    <div class="settings-row"><div><h3>Appearance</h3><p>Stored in this browser.</p></div><select id="theme" aria-label="Color theme"><option value="dark">Dark</option><option value="light">Light</option></select></div>
    <div class="settings-row"><div><h3>Live refresh interval</h3><p>Polling pauses while this browser tab is hidden.</p></div><select id="refresh-interval" aria-label="Refresh interval"><option value="1">1 second</option><option value="3">3 seconds</option><option value="5">5 seconds</option><option value="10">10 seconds</option></select></div>
    <div class="settings-row"><div><h3>Export local analysis</h3><p>Topology and experimental measurements in JSON. Review before sharing.</p></div><button id="export-all" class="secondary">↓ Export JSON</button></div>`)+
    panel('Application updates','<div id="app-updates"></div>')+
    panel('Help & Guide','<p>Use the ? buttons beside sections to understand what each feature does.</p><a class="primary button" href="#help">Open the full guide →</a>')+
    panel('Privacy & capabilities',`<dl class="keyvalues"><dt>Network behavior</dt><dd>Local analysis stays on this device. Optional update checks contact the official GitHub release service.</dd><dt>Process privacy</dt><dd>No process environments are read. Command arguments are hidden.</dd><dt>X3D mode</dt><dd>Read-only. No system-wide scheduling writes are implemented.</dd><dt>Diagnostic logging</dt><dd>Local affinity audit only: task identities, CPU sets and outcomes. No process arguments.</dd><dt>External telemetry</dt><dd>Unsupported. No FPS, temperature, power or latency data is simulated.</dd><dt>Crash recovery</dt><dd>Unsupported. Keep the backend running until original affinities are restored.</dd><dt>Launch-time Proton/Wine topology</dt><dd>Unverified on this target. Runtime task affinity is a separate operation.</dd><dt>Custom executable launching</dt><dd>Unsupported. Browser file selection provides metadata only.</dd></dl>`);
  initUpdates();
  const readonly=document.querySelector('#read-only'),offset=document.querySelector('#offset');offset.value=state.settings.display_offset;if(state.topology.platform==='Windows'){offset.closest('.settings-row').hidden=true;}
  async function save(){
    try{state.settings=await api('/settings',{read_only:readonly.checked,display_offset:Number(offset.value)});state.topology=await api('/cpu/topology');state.recommendations=[];toast(state.settings.read_only?'Read-only mode enabled. Recorded tasks can still be restored.':'Experiments enabled. Every apply still requires confirmation.');document.dispatchEvent(new CustomEvent('halawacore-settings'));}
    catch(e){readonly.checked=state.settings.read_only;offset.value=state.settings.display_offset;toast(e.message,true);}
  }
  readonly.onchange=save;offset.onchange=save;
  document.querySelector('#theme').value=document.documentElement.dataset.theme;
  document.querySelector('#theme').onchange=e=>{document.documentElement.dataset.theme=e.target.value;localStorage.setItem('theme',e.target.value);};
  document.querySelector('#refresh-interval').value=state.refresh;
  document.querySelector('#refresh-interval').onchange=e=>{state.refresh=Number(e.target.value);localStorage.setItem('refresh',state.refresh);};
  document.querySelector('#export-all').onclick=async()=>{try{download('halawacore-analysis.json',{topology:state.topology,experiments:await api('/experiments')});}catch(e){toast(e.message,true);}};
}

export async function renderProfiles(){
  const data=await api('/profiles');
  if(state.page!=='profiles')return;
  document.querySelector('#content').innerHTML=heading('Saved profiles','Reusable CPU selections. Loaded for review, never applied automatically.')+
    panel('Your CPU sets',data.profiles.length?`<div class="profiles-grid">${data.profiles.map((p,i)=>`<article class="profile"><span class="badge">MANUAL LOAD ONLY</span><h3 data-no-i18n>${esc(p.name)}</h3><div class="profile-set mono">OS IDs ${esc(list(p.cpus))}</div><p data-no-i18n>${esc(p.note)}</p><p>Topology signature: <span class="mono">${esc(p.generation)}</span></p><div class="flex"><button data-load="${i}" class="secondary">Load into planner</button><button data-delete="${esc(p.id)}" class="text-button danger">Delete</button></div></article>`).join('')}</div>`:'<div class="empty"><h3>A useful experiment is worth remembering.</h3><p>Choose a process and save a CPU selection from the affinity planner. Profiles always require a new preview before applying.</p><a class="primary button" href="#planner">Open affinity planner →</a></div>');
  document.querySelectorAll('[data-delete]').forEach(el=>el.onclick=async()=>{try{await api(`/profiles/${el.dataset.delete}`,undefined,'DELETE');await renderProfiles();}catch(e){toast(e.message,true);}});
  document.querySelectorAll('[data-load]').forEach(el=>el.onclick=()=>{
    if(!state.process){toast('Select a running process in Applications first.');navigate('applications');return;}
    const p=data.profiles[Number(el.dataset.load)];
    if(p.cpus.some(c=>!state.topology.online_cpus.includes(c)||!(state.plannerAllowed??state.process.affinity).includes(c))){toast('Profile includes offline CPUs or CPUs outside this process affinity. Select a fresh CPU set.',true);return;}
    if(p.generation!==state.topology.generation)toast('Topology or scheduling data changed since this profile was saved. Review the CPU mapping carefully.');
    state.selected=new Set(p.cpus);navigate('planner');
  });
}

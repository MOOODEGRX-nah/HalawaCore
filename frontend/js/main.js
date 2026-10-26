import {state,esc,toast} from './state.js';
import {api} from './api.js';
import {renderDashboard,updateDashboard} from './dashboard.js';
import {renderTopology,updateUtilization} from './topology.js';
import {renderProcesses,refreshProcesses} from './processes.js';
import {renderPlanner} from './affinity.js';
import {renderLab,updateLab} from './experiments.js';
import {renderSettings,renderProfiles} from './settings.js';

const pages={dashboard:['Dashboard',renderDashboard],topology:['CPU Topology',renderTopology],applications:['Applications',renderProcesses],planner:['Affinity Planner',renderPlanner],lab:['Performance Lab',renderLab],profiles:['Saved Profiles',renderProfiles],settings:['Settings',renderSettings]};
document.documentElement.dataset.theme=localStorage.getItem('theme')==='light'?'light':'dark';
if(![1,3,5,10].includes(state.refresh))state.refresh=3;
let busy=false,connected=false,ticks=0;
function shell(){
  document.querySelector('#page-label').textContent=pages[state.page][0];
  document.querySelectorAll('[data-page]').forEach(a=>{const active=a.dataset.page===state.page;a.classList.toggle('active',active);if(active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
  document.querySelector('#mode-badge').textContent=state.settings.read_only?'Read-only mode':'Experiments enabled';
  document.querySelector('#mode-badge').classList.toggle('green',!state.settings.read_only);
}
async function render(){
  if(!state.topology)return;
  state.page=pages[location.hash.slice(1)]?location.hash.slice(1):'dashboard';shell();
  try{await pages[state.page][1]();}catch(e){toast(e.message,true);document.querySelector('#content').innerHTML=`<div class="empty"><h2 class="error-title">This view is unavailable</h2><p>${esc(e.message)}</p><a class="primary button" href="#applications">Browse processes</a></div>`;}
}
async function refresh(force=false){
  if(state.closed||busy||(!force&&document.hidden))return;
  busy=true;
  try{
    const requests=[api('/cpu/metrics')];
    const topologyDue=force||++ticks%3===0;
    if(topologyDue)requests.push(api('/cpu/topology'),api('/system'));
    const [metrics,topology,system]=await Promise.all(requests);
    state.metrics=metrics;state.history.push(metrics);state.history=state.history.slice(-90);
    const changed=topology&&topology.generation!==state.topology?.generation;
    if(topology)state.topology=topology;if(system)state.system=system;
    if(changed){state.recommendations=[];if(document.querySelector('#confirm-dialog').open)document.querySelector('#confirm-dialog').close('cancel');toast('Topology or scheduling data changed. Recommendations and previews need a fresh review.');if(['topology','planner','dashboard'].includes(state.page))await render();}
    if(state.page==='dashboard')updateDashboard();else updateUtilization();
    if(state.page==='lab')await updateLab();
    if(state.page==='applications')await refreshProcesses();
    document.querySelector('#connection').textContent='Live system';
    document.querySelector('#updated').textContent=`Updated ${new Date(metrics.timestamp*1000).toLocaleTimeString()}`;
    connected=true;
  }catch(e){document.querySelector('#connection').textContent='Disconnected';if(connected||force)toast(`${e.message} Keep the backend running for restoration.`,true);connected=false;}
  finally{busy=false;}
}
async function poll(){await refresh();setTimeout(poll,state.refresh*1000);}
async function start(){
  try{
    const session=await api('/session');state.token=session.token;state.settings=session.settings;state.desktop=!!session.desktop;
    if(state.desktop&&!document.querySelector('#quit-desktop')){const quit=document.createElement('button');quit.id='quit-desktop';quit.className='secondary';quit.textContent='Quit HalawaCore';quit.onclick=async()=>{if(!window.confirm('Close HalawaCore? Stop recordings and restore experiments first.'))return;try{await api('/shutdown',{});document.querySelector('#content').innerHTML='<div class=empty><h2>HalawaCore has closed</h2><p>You can close this browser tab.</p></div>';document.querySelector('#connection').textContent='Closed';state.closed=true;}catch(e){toast(e.message,true);}};document.querySelector('.top-actions').append(quit);}
    const [topology,metrics,system]=await Promise.all([api('/cpu/topology'),api('/cpu/metrics'),api('/system')]);
    state.topology=topology;state.metrics=metrics;state.system=system;state.history=[metrics];connected=true;
    document.querySelector('#connection').textContent='Live system';await render();poll();
  }catch(e){document.querySelector('#content').innerHTML=`<div class="empty"><h2>Cannot connect to HalawaCore</h2><p>${esc(e.message)} Start the backend with ./run.sh and open http://127.0.0.1:8000.</p><button id="retry" class="primary">Retry connection</button></div>`;document.querySelector('#retry').onclick=start;}
}
window.addEventListener('hashchange',render);
document.addEventListener('halawacore-render',render);
document.addEventListener('halawacore-settings',shell);
document.querySelector('#refresh').onclick=async()=>{await refresh(true);if(!['dashboard','topology','lab'].includes(state.page))await render();};
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh(true);});
start();

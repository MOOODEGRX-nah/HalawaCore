import {state,esc,fmt} from './state.js';
import {api} from './api.js';
import {getLanguage} from './i18n.js';

let latest=null,timer=null,pending=false;
const busy=phase=>['checking','downloading','installing','restarting'].includes(phase);
const labels={idle:'Check when you are ready. No background checks run automatically.',checking:'Checking the official release…',current:'No newer published version is available.',available:'A newer version is available.',downloading:'Downloading and verifying the update…',ready:'Download verified. Ready to install.',installing:'Installing the update. Keep HalawaCore open.',restart_required:'Update installed. Restart HalawaCore to use it.',restarting:'Opening the updated app. This window will close.',failed:'The update did not finish. Review the message and try again.'};
const methods={arch:'CachyOS / Arch package',portable:'Portable application',source:'Source checkout',managed:'System-managed installation',unsupported:'Unsupported installation'};
function notes(text){
  const arabic=text.indexOf('## العربية'),english=text.indexOf('## English');
  if(arabic>=0&&english>arabic)return getLanguage()==='ar'?text.slice(arabic,english).trim():text.slice(english).trim();
  return text;
}
function render(){
  const root=document.querySelector('#app-updates');if(!root||state.page!=='settings')return;
  if(!latest){root.innerHTML='<p class="muted">Reading update status…</p>';return;}
  const data=latest,active=pending||busy(data.phase),kind=data.installation.kind;
  root.innerHTML=`<dl class="keyvalues"><dt>Installed version</dt><dd class="mono">v${esc(data.current_version)}</dd><dt>Installation method</dt><dd>${esc(methods[kind]||methods.unsupported)}</dd>${data.latest_version?`<dt>Latest stable release</dt><dd class="mono">v${esc(data.latest_version)}</dd>`:''}</dl><p class="tiny muted">${esc(data.installation.reason)}</p><p role="status" class="update-status">${esc(labels[data.phase]||labels.idle)}</p>${data.last_result?.status==='updated'?`<p class="tiny muted"><span>Last completed update:</span> <span class="mono">v${esc(data.last_result.version)}</span></p>`:''}${data.last_result?.status==='failed'?`<p class="notice">${esc(data.last_result.error)}</p>`:''}${data.error?`<p class="notice">${esc(data.error)}</p>`:''}${data.available&&data.installation.supported&&!data.can_download?'<p class="notice">This release has no verified package for this installation method. Open the official release page.</p>':''}${data.phase==='downloading'?`<progress class="update-progress" max="${data.download_size||1}" value="${data.downloaded_bytes||0}"></progress><p class="tiny mono">${fmt((data.downloaded_bytes||0)/1024**2)} / ${fmt((data.download_size||0)/1024**2)} MiB</p>`:''}${data.release_notes?`<details class="update-notes"><summary>What changed in this release?</summary><pre data-no-i18n>${esc(notes(data.release_notes))}</pre></details>`:''}<div class="flex update-actions"><button class="secondary" id="check-updates" ${active||['ready','restart_required'].includes(data.phase)?'disabled':''}>Check for updates</button>${data.can_download&&['available','failed'].includes(data.phase)?'<button class="primary" id="download-update">Download and verify</button>':''}${data.phase==='ready'?'<button class="primary" id="install-update">Install update…</button>':''}${data.phase==='restart_required'?'<button class="primary" id="restart-update">Restart updated HalawaCore</button>':''}<a class="text-link" href="${esc(data.release_page)}" target="_blank" rel="noopener noreferrer">Official release page ↗</a></div><p class="tiny muted">Update checks contact GitHub only when requested and send no hardware or process data. Downloads are checked against the release SHA-256; this is not an independent digital signature.</p><dialog id="update-confirm"><h2>Confirm application update</h2><p><span>Target version:</span> <span class="mono">v${esc(data.latest_version)}</span></p><p>Stop recording and restore every affinity experiment before continuing. Export session measurements before restarting. Personal settings and saved profiles stay in their data folder.</p><p>${kind==='arch'?'The system permission dialog will ask to install the verified package. HalawaCore itself stays unprivileged.':kind==='portable'?'A .previous backup is kept beside the portable executable. Windows closes and reopens the app after replacing it.':'This installation cannot update itself.'}</p><div class="dialog-actions"><button class="secondary" id="cancel-app-update">Cancel</button><button class="primary" id="confirm-app-update">Confirm and install</button></div></dialog>`;
  root.querySelector('#check-updates').onclick=()=>action('/updates/check',{});
  root.querySelector('#download-update')?.addEventListener('click',()=>action('/updates/download',{}));
  root.querySelector('#install-update')?.addEventListener('click',()=>root.querySelector('#update-confirm').showModal());
  root.querySelector('#cancel-app-update').onclick=()=>root.querySelector('#update-confirm').close();
  root.querySelector('#confirm-app-update').onclick=()=>{root.querySelector('#update-confirm').close();action('/updates/install',{job_id:data.job_id,confirmed:true});};
  root.querySelector('#restart-update')?.addEventListener('click',()=>action('/updates/restart',{confirmed:true}));
}
async function action(path,body){
  if(pending)return;pending=true;render();
  try{latest=await api(path,body);}catch(error){latest={...latest,phase:'failed',error:error.message};}
  finally{pending=false;render();schedule();}
}
function schedule(){
  clearTimeout(timer);
  if(state.page==='settings'&&latest&&busy(latest.phase)&&latest.phase!=='restarting')timer=setTimeout(refresh,1000);
}
async function refresh(){
  if(state.page!=='settings')return;
  try{latest=await api('/updates');render();schedule();}
  catch(error){if(latest?.phase!=='restarting'){latest={...latest,phase:'failed',error:error.message};render();}}
}
export function initUpdates(){clearTimeout(timer);render();refresh();}
document.addEventListener('halawacore-language',render);

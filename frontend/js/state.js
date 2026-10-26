export const state = {
  token: '', settings: {read_only:true,display_offset:1}, topology:null, metrics:null,
  system:null, page:'dashboard', process:null, selected:new Set(), recommendations:[],
  history:[], refresh: Number(localStorage.getItem('refresh') || 3), numbering: localStorage.getItem('numbering') || 'linux',
};
export const esc = value => String(value ?? '—').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const fmt = (n, places=1) => n == null ? '—' : Number(n).toFixed(places);
export const list = cpus => cpus?.length ? cpus.join(', ') : 'None';
export const bytes = n => n == null ? '—' : `${(n/1024/1024).toFixed(n>=1024**3?0:1)} MiB`;
export function toast(message, error=false) {
  const item = document.createElement('div'); item.className=`toast${error?' error':''}`; item.textContent=message;
  document.querySelector('#toasts').append(item); setTimeout(()=>item.remove(), 8000);
}
export function download(name, value) {
  const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)],{type:'application/json'}));
  const a=document.createElement('a'); a.href=url; a.download=name; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function heading(title,subtitle,actions='') {return `<div class="page-heading"><div><div class="eyebrow">YOUR MACHINE. YOUR INSIGHT.</div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div><div class="flex">${actions}</div></div>`;}
export const panel=(title,body,subtitle='',right='')=>`<section class="panel"><div class="panel-head"><div><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div>${right}</div><div class="panel-body">${body}</div></section>`;
export function navigate(page){location.hash=page;}

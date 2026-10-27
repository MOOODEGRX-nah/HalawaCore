import {esc,fmt} from './state.js';

export function processCpuCell(row,view='device'){
  const value=view==='raw'?row.cpu_percent:row.cpu_percent_device;
  const valid=Number.isFinite(value),equivalent=row.cpu_logical_equivalents;
  return `<div class="cpu-value">${valid?fmt(value)+'%':'—'}</div>${Number.isFinite(equivalent)?`<div class="tiny muted"><span class="mono">${fmt(equivalent,2)}</span> <span>logical CPU equivalents</span></div>`:''}${view==='device'&&valid?`<div class="cpu-share-track" aria-hidden="true"><span style="width:${Math.min(100,Math.max(0,value))}%"></span></div>`:''}`;
}

export function difference(value,unit='',places=1){
  if(!Number.isFinite(value))return '—';
  return `<span class="mono" dir="ltr">${value>0?'+':''}${fmt(value,places)}${esc(unit)}</span>`;
}

import {esc} from './state.js';
export function chart(samples, key='total_percent', process=false) {
  const valid=samples.filter(s=>s[key]!=null);
  if(valid.length<2) return '<div class="chart-empty">Collecting real samples · the chart appears after two measurements</div>';
  const width=640,height=178,left=31,top=10,bottom=153,max=process?Math.max(100,...valid.map(s=>s[key])):100;
  const first=valid[0].timestamp,last=valid.at(-1).timestamp;
  const points=valid.map(s=>[left+(s.timestamp-first)/Math.max(.01,last-first)*(width-left-7),bottom-s[key]/max*(bottom-top)]);
  const line=points.map(p=>p.join(',')).join(' ');
  return `<svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(key)} over time, from real system samples">${[0,25,50,75,100].map(v=>{let y=bottom-v/100*(bottom-top);return `<line class="gridline" x1="${left}" x2="${width}" y1="${y}" y2="${y}"/><text x="0" y="${y+3}">${Math.round(v/100*max)}%</text>`;}).join('')}<polygon class="area" points="${left},${bottom} ${line} ${points.at(-1)[0]},${bottom}"/><polyline class="plot ${process?'secondary-plot':''}" points="${line}"/><text x="${left}" y="173">${esc(new Date(first*1000).toLocaleTimeString())}</text><text x="635" y="173" text-anchor="end">${esc(new Date(last*1000).toLocaleTimeString())}</text></svg>`;
}

export function comparisonChart(before,after){
  const series=[before,after].map(samples=>samples.filter(sample=>Number.isFinite(sample.process_cpu_percent_device)&&Number.isFinite(sample.elapsed_seconds)));
  if(series.some(samples=>samples.length<2))return '<div class="chart-empty">Collecting real samples · the chart appears after two measurements</div>';
  const width=680,left=40,right=670,top=10,bottom=164;
  const duration=Math.max(1,...series.flatMap(samples=>samples.map(sample=>sample.elapsed_seconds)));
  const maximum=Math.max(100,...series.flatMap(samples=>samples.map(sample=>sample.process_cpu_percent_device)));
  const points=samples=>samples.map(sample=>`${left+sample.elapsed_seconds/duration*(right-left)},${bottom-sample.process_cpu_percent_device/maximum*(bottom-top)}`).join(' ');
  return `<svg class="chart comparison-chart" viewBox="0 0 ${width} 200" role="img" aria-label="Before and after CPU activity, aligned by elapsed seconds" dir="ltr">${[0,25,50,75,100].map(percent=>{const y=bottom-percent/100*(bottom-top);return `<line class="gridline" x1="${left}" x2="${right}" y1="${y}" y2="${y}"/><text x="0" y="${y+3}">${Math.round(percent/100*maximum)}%</text>`;}).join('')}<polyline class="plot before-plot" points="${points(series[0])}"/><polyline class="plot after-plot" points="${points(series[1])}"/>${[0,.5,1].map(fraction=>`<text x="${left+fraction*(right-left)}" y="190" text-anchor="${fraction===1?'end':'start'}">${Math.round(fraction*duration)} s</text>`).join('')}</svg>`;
}

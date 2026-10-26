import {state,esc,fmt,heading,panel} from './state.js';
import {coreGrid,domainCards,x3dStatus,updateUtilization} from './topology.js';
import {chart} from './charts.js';

export function renderDashboard(){
  const t=state.topology;
  document.querySelector('#content').innerHTML=heading('Your processor, mapped.','Explore your hardware. Understand the scheduler. Experiment with confidence.',`<a class="secondary button" href="#topology">View full topology ↗</a>`)+
    `<div class="stats"><article class="stat model"><div class="stat-label">PROCESSOR <span class="stat-icon">▣</span></div><div class="stat-value">${esc(t.cpu_model.replace(' Processor',''))}</div><div class="stat-note">${esc(t.architecture)} <span class="muted">/</span> ${esc(t.vendor)}</div></article><article class="stat"><div class="stat-label">PHYSICAL CORES <span class="stat-icon">▦</span></div><div class="stat-value">${t.physical_core_count??'—'}<small>/ ${t.logical_cpu_count} threads</small></div><div class="stat-note"><span class="highlight">${t.smt_enabled?'SMT detected':'SMT not detected'}</span> · ${t.socket_count} socket${t.socket_count===1?'':'s'}</div></article><article class="stat"><div class="stat-label">CPU UTILIZATION <span class="stat-icon">⌁</span></div><div class="stat-value"><span data-total>${fmt(state.metrics?.total_percent)}</span><small>%</small></div><div class="stat-note">Live from <span class="highlight">${esc(state.metrics?.source||'OS counters')}</span></div></article><article class="stat"><div class="stat-label">ONLINE / AVAILABLE <span class="stat-icon">◉</span></div><div class="stat-value">${t.online_cpus.length}<small>/ ${t.analyzer_allowed_cpus.length} allowed</small></div><div class="stat-note">${state.system?.active_processes??'—'} active processes · ${t.offline_cpus.length} offline CPUs</div></article></div>`+
    (t.virtualized?'<div class="notice">Virtual machine detected. Guest topology and affinity do not verify physical host placement.</div>':'')+
    `<div class="split">${panel('Physical core map',coreGrid(),`${t.logical_cpu_count} OS CPU IDs · real SMT sibling relationships`,`<a class="text-button" href="#topology">Explore topology →</a>`)}${panel('CPU activity',`<div class="flex spread"><div class="performance-number"><span data-total>${fmt(state.metrics?.total_percent)}</span><small>%</small></div><span class="pill"><i></i> LIVE</span></div><div id="live-chart">${chart(state.history)}</div><div class="chart-caption"><span>System CPU utilization</span><span>Local measurements only</span></div>`,'Rolling history · up to 90 real samples')}</div>`+
    `<div class="split">${panel('Shared cache architecture',domainCards(),`${t.cache_domain_count} detected L3 cache domain${t.cache_domain_count===1?'':'s'}`,`<span class="badge">CACHE TOPOLOGY</span>`)}${panel('X3D & scheduler awareness',x3dStatus()+`<div class="notice neutral spacer">Scheduling preference is read-only. HalawaCore never changes BIOS settings, CPU drivers, kernel parameters, or system-wide modes.</div>`,'Capability detection, with uncertainty made visible')}</div>`+
    panel('Choose an experiment. Keep a way back.',`<div class="profiles-grid">${[
      ['01','Cache-Oriented Gaming','Test the identified larger-cache domain when X3D topology is verified. Some games benefit; results vary.'],
      ['02','Frequency-Oriented Computing','Test a verified higher-frequency group for suitable workloads. Actual boost and throughput still vary.'],
      ['03','Balanced / Scheduler Default','Preserve existing affinity. Give the Linux scheduler its current full choice of CPUs.'],
    ].map(([n,title,description])=>`<article class="profile"><span class="section-label">PROFILE ${n}</span><h3>${title}</h3><p>${description}</p><a class="text-button" href="#planner">Open affinity planner →</a></article>`).join('')}</div>`,'Affinity restrictions do not guarantee improved performance. Begin with a measured baseline.')+
    `<div class="notice neutral"><strong>You are in control.</strong> Read-only by default. Every affinity experiment requires a reviewed task list and confirmation. Original per-thread affinities are saved for restoration while this backend remains running.</div>`;
  updateUtilization();
}

export function updateDashboard(){
  updateUtilization();
  const el=document.querySelector('#live-chart');if(el)el.innerHTML=chart(state.history);
}

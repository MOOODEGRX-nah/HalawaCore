import {ar} from './translations-ar.js';

const key='halawacore-language';
let language=localStorage.getItem(key) || (navigator.language?.startsWith('ar')?'ar':'en');
if(!['ar','en'].includes(language))language='en';
const sources=new WeakMap(),attributes=new WeakMap();
const extra={
  'Language':'اللغة','Interface language':'لغة الواجهة','Help & Guide':'المساعدة والدليل',
  'Help on this section':'شرح هذا الجزء','Close help':'إغلاق الشرح','Close':'إغلاق',
  'Open the full guide':'فتح الدليل الكامل','Welcome to HalawaCore':'مرحبًا بك في HalawaCore',
  'Start exploring':'ابدأ الاستكشاف','Show the welcome guide':'عرض دليل البداية',
  'No matching guide topics.':'لا توجد موضوعات مساعدة مطابقة.',
  'Search the guide':'ابحث في الدليل','Search features and terms…':'ابحث في الخصائص والمصطلحات…',
  'Feature guide':'دليل الخصائص','Getting started':'البداية',
  'Use the ? buttons beside sections to understand what each feature does.':'استخدم أزرار ؟ بجانب الأقسام لفهم وظيفة كل خاصية.',
  'Open the full guide →':'فتح الدليل الكامل ←',
  'M — HalawaCore logo':'شعار M — HalawaCore','registered':'مسجّل',
  'topology':'الطوبولوجيا','l3 cache':'كاش L3','cppc':'CPPC','preferred core':'الأنوية المفضلة','frequency':'التردد','capacity classes':'فئات السعة',
  'selected':'العمليات المحددة',
  'main':'المهمة الافتراضية','task':'خيط محدد','threads':'الخيوط الحالية','related':'العمليات المختارة',
};
export const getLanguage=()=>language;
export function bi(en,arabic){return language==='ar'?arabic:en;}
export function translateText(value,lang=language){
  if(lang==='en'||!value)return value;
  const trimmed=value.trim();
  let translated=extra[trimmed]??ar[trimmed];
  if(translated===undefined){
    const rules=[
      [/^(\d+) recorded tasks$/,m=>`${m[1]} مهام مسجلة`],
      [/^(\d+) processes selected$/,m=>`${m[1]} عمليات محددة`],
      [/^Select process PID (\d+)$/,m=>`تحديد العملية PID ${m[1]}`],
      [/^Remove process PID (\d+)$/,m=>`إزالة العملية PID ${m[1]}`],
      [/^Core (\d+)$/,m=>`النواة ${m[1]}`], [/^CPU group (\d+)$/,m=>`مجموعة المعالج ${m[1]}`],
      [/^CPU ([A-Za-z0-9:]+)$/,m=>`المعالج ${m[1]}`],
      [/^OS IDs (.*)$/,m=>`أرقام النظام ${m[1]}`],
      [/^Display ([0-9A-Za-z: ,]+)$/,m=>`الأرقام المعروضة ${m[1]}`],
      [/^TID (\d+) · OS IDs (.*)$/,m=>`TID ${m[1]} · أرقام النظام ${m[2]}`],
      [/^(.*?) · (\d+) arguments \(hidden for privacy\)$/,m=>`${m[1]} · ${m[2]} معاملات مخفية للخصوصية`],
      [/^OS CPU (\d+) · Display ([A-Za-z0-9:]+) · (Online|Offline|Outside current affinity)$/,m=>`معالج النظام ${m[1]} · الرقم المعروض ${m[2]} · ${translateText(m[3],lang)}`],
      [/^(total_percent|process_cpu_percent) over time, from real system samples$/,m=>m[1]==='total_percent'?'استخدام المعالج عبر الزمن من عينات فعلية':'استخدام العملية عبر الزمن من عينات فعلية'],
      [/^(.+): (available|partially available|unknown|unsupported|permission restricted)$/,m=>`${translateText(m[1],lang)}: ${translateText(m[2],lang)}`],
      [/^L3 domain (\d+)$/,m=>`مجموعة كاش L3 ${m[1]}`],
      [/^Socket (.*?) · (\d+)T$/,m=>`المقبس ${m[1]} · ${m[2]} خيوط`],
      [/^Socket (.*?) · Core (.*?)$/,m=>`المقبس ${m[1]} · النواة ${m[2]}`],
      [/^Die (.*?) · (.*)$/,m=>`الشريحة ${m[1]} · ${translateText(m[2],lang)}`],
      [/^(\d+) physical cores · (\d+) logical CPUs · (.*)$/,m=>`${m[1]} أنوية فعلية · ${m[2]} معالجات منطقية · ${m[3]}`],
      [/^(\d+) OS CPU IDs · real SMT sibling relationships$/,m=>`${m[1]} معالجات منطقية · علاقات خيوط SMT الفعلية`],
      [/^(\d+) detected L3 cache domains?$/,m=>`${m[1]} مجموعات كاش L3 مكتشفة`],
      [/^(\d+) active processes · (\d+) offline CPUs$/,m=>`${m[1]} عمليات نشطة · ${m[2]} معالجات غير متصلة`],
      [/^(\d+) core groups$/,m=>`${m[1]} مجموعات أنوية`], [/^(\d+) logical CPUs$/,m=>`${m[1]} معالجات منطقية`],
      [/^(\d+) detected$/,m=>`${m[1]} مكتشفة`], [/^(\d+) accessible$/,m=>`${m[1]} متاحة للفحص`],
      [/^\/ (\d+) threads$/,m=>`/ ${m[1]} خيوط`], [/^\/ (\d+) allowed$/,m=>`/ ${m[1]} مسموح بها`],
      [/^· (\d+) sockets?$/,m=>m[1]==='1'?'· مقبس واحد':`· ${m[1]} مقابس`], [/^PROFILE (\d+)$/,m=>`الملف ${m[1]}`],
      [/^Updated (.*)$/,m=>`آخر تحديث ${m[1]}`],
      [/^(.+) · PID (\d+) · identity (\d+)$/,m=>`${m[1]} · PID ${m[2]} · الهوية ${m[3]}`],
      [/^Existing threads \((\d+)\)$/,m=>`الخيوط الحالية (${m[1]})`],
      [/^Observed related processes \((\d+)\)$/,m=>`العمليات المرتبطة المرصودة (${m[1]})`],
      [/^Inspect membership graph \((\d+) nodes\)$/,m=>`فحص مخطط العضوية (${m[1]} عقدة)`],
      [/^NUMA node (\d+) experiment$/,m=>`تجربة عقدة NUMA ${m[1]}`],
      [/^Scope: (\w+) · (\d+) exact tasks · preview expires in 60 seconds\.$/,m=>`النطاق: ${translateText(m[1],lang)} · ${m[2]} مهام محددة · تنتهي المعاينة بعد 60 ثانية.`],
      [/^(\d+) selected$/,m=>`${m[1]} محددة`], [/^of (\d+) currently permitted CPUs$/,m=>`من ${m[1]} معالجات مسموح بها حاليًا`],
      [/^Node (\d+) · OS IDs (.*)$/,m=>`العقدة ${m[1]} · أرقام النظام ${m[2]}`],
      [/^Start ticks (\d+) · parent (\d+)$/,m=>`هوية البدء ${m[1]} · العملية الأم ${m[2]}`],
    ];
    for(const [pattern,replace] of rules){const match=trimmed.match(pattern);if(match){translated=replace(match);break;}}
  }
  if(translated===undefined&&trimmed.includes(' · ')){
    const parts=trimmed.split(' · ');
    if(parts.some(part=>extra[part]!==undefined||ar[part]!==undefined))translated=parts.map(part=>extra[part]??ar[part]??part).join(' · ');
  }
  if(translated===undefined){
    // Only known UI fragments are replaced. Raw process/profile metadata is excluded by localize().
    const fragments={
      'Current OS IDs':'أرقام النظام الحالية','Proposed OS IDs':'أرقام النظام المقترحة',
      'Requested OS CPU IDs:':'أرقام المعالجات المطلوبة في النظام:',
      'OS IDs:':'أرقام النظام:','OS CPU IDs:':'أرقام المعالجات في النظام:',
      'Display IDs:':'الأرقام المعروضة:','Requested OS IDs:':'أرقام النظام المطلوبة:',
      'Package IDs:':'أرقام المقابس:','Die IDs:':'أرقام الشرائح:','Cache IDs:':'أرقام الكاش:',
      'Max frequency range:':'نطاق التردد الأقصى:','Analyzer allowed:':'المسموح للمحلل:',
      'Online:':'متصل:','Allowed:':'المسموح:','Relative distances:':'المسافات النسبية:',
      'Topology signature:':'بصمة الطوبولوجيا:','Start ticks':'هوية البدء',
      'Steam ancestry:':'تسلسل Steam:','Wine/Proton:':'Wine/Proton:',
      'not observed':'غير مرصود',
      'Requested CPUs exceed TID':'الأنوية المطلوبة تتجاوز المسموح للخيط TID',
      'Operating system operation failed:':'تعذرت عملية نظام التشغيل:',
    };
    translated=trimmed;
    for(const [en,arabic] of Object.entries(fragments))translated=translated.replaceAll(en,arabic);
  }
  const leading=value.match(/^\s*/)[0],trailing=value.match(/\s*$/)[0];
  return leading+translated+trailing;
}
export const t=value=>translateText(String(value));

function original(map,node,current){
  const saved=map.get(node);
  if(saved&&current===saved.last)return saved.source;
  map.set(node,{source:current,last:current});return current;
}
function skipped(element){return element?.closest('script,style,pre,code,[data-no-i18n],.stat.model .stat-value,.stat.model .stat-note,.long,svg');}
export function localize(root=document.body){
  if(!root)return;
  observer?.disconnect();
  document.dispatchEvent(new CustomEvent('halawacore-before-localize'));
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
  let node;
  while((node=walker.nextNode())){
    if(skipped(node.parentElement)||!node.data.trim())continue;
    const source=original(sources,node,node.data),next=translateText(source);
    if(node.data!==next)node.data=next;
    sources.set(node,{source,last:next});
  }
  const elements=[...(root.nodeType===1?[root]:[]),...root.querySelectorAll('*')];
  for(const element of elements){
    if(skipped(element)&&element.tagName.toLowerCase()!=='svg')continue;
    const values=attributes.get(element)||{};
    for(const name of ['title','aria-label','placeholder','alt']){
      if(!element.hasAttribute(name))continue;
      const current=element.getAttribute(name),saved=values[name];
      const source=saved&&current===saved.last?saved.source:current;
      const next=translateText(source);if(current!==next)element.setAttribute(name,next);
      values[name]={source,last:next};
    }
    attributes.set(element,values);
  }
  document.title=translateText('HalawaCore · CPU topology & affinity');
  for(const select of document.querySelectorAll('[data-language-select]')){select.value=language;select.setAttribute('aria-label',bi('Interface language','لغة الواجهة'));}
  observer?.observe(document.body,{childList:true,subtree:true,characterData:true});
}
let observer;
let pending=false;
export function setLanguage(next){
  if(!['ar','en'].includes(next))return;
  language=next;localStorage.setItem(key,next);
  document.documentElement.lang=next;document.documentElement.dir=next==='ar'?'rtl':'ltr';
  localize();document.dispatchEvent(new CustomEvent('halawacore-language',{detail:next}));
}
export function initLanguage(){
  observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;localize();});});
  document.addEventListener('change',event=>{if(event.target.matches('[data-language-select]'))setLanguage(event.target.value);});
  setLanguage(language);
}

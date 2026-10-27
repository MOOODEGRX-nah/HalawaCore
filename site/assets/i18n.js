import {en} from './translations-en.js';
const key='halawacore-language';
const requested=new URL(location.href).searchParams.get('lang');
let language=['ar','en'].includes(requested)?requested:(localStorage.getItem(key)||'ar');
if(!['ar','en'].includes(language))language='ar';
const originals=new WeakMap(),attrs=new WeakMap();
const additional={
  'شعار M — HalawaCore':'M logo — HalawaCore',
  'أوامر CachyOS وFedora وتوزيعات Linux':'CachyOS, Fedora and Linux commands','اللغة':'Language','دليل التحميل والبداية':'Download and first-use guide',
};
const arabicGraphics={'PORTABLE · x64':'نسخة محمولة · x64','HALAWACORE / DESKTOP':'HALAWACORE / البرنامج المحلي','MIT License':'ترخيص MIT','01 / TOPOLOGY':'01 / الطوبولوجيا','02 / APPLICATIONS':'02 / التطبيقات','03 / X3D AWARENESS':'03 / دعم X3D','04 / PERFORMANCE LAB':'04 / مختبر الأداء','05 / REVERSIBLE EXPERIMENTS':'05 / تجارب قابلة للاستعادة','HalawaCore / Local workspace':'HalawaCore / مساحة العمل المحلية','TOPOLOGY':'الطوبولوجيا','SHARED L3':'كاش L3 مشترك','PHYSICAL CORES':'الأنوية الفعلية','LOGICAL THREADS':'الخيوط المنطقية','Physical core':'نواة فعلية','CPU A':'المعالج A','CPU B':'المعالج B','YOUR HARDWARE. YOUR CALL.':'عتادك. قرارك.'};
export const getLanguage=()=>language;
export const L=(arabic,english)=>language==='ar'?arabic:english;
export function translate(value,lang=language){
  const source=value.trim();let next=source;
  if(lang==='en'){
    next=additional[source]??en[source]??source;
    const release=source.match(/^الإصدار (.+) متاح من مستودع المشروع الرسمي\.$/);
    if(release)next=`Release ${release[1]} is available from the official project repository.`;
    if(source.includes(' · تنزيل من GitHub'))next=source.replace(' · تنزيل من GitHub',' · Download from GitHub');
  }else next=arabicGraphics[source]??source;
  return value.match(/^\s*/)[0]+next+value.match(/\s*$/)[0];
}
let observer,pending=false;
function excluded(el){return el?.closest('script,style,code,pre,[data-no-i18n]');}
export function localize(){
  observer?.disconnect();
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){
    if(!node.data.trim()||excluded(node.parentElement))continue;
    const previous=originals.get(node),source=previous&&node.data===previous.last?previous.source:node.data;
    const next=translate(source);if(node.data!==next)node.data=next;originals.set(node,{source,last:next});
  }
  for(const element of document.querySelectorAll('[title],[alt],[aria-label],[placeholder],meta[name=description]')){
    if(excluded(element))continue;
    const values=attrs.get(element)||{};
    for(const attribute of ['title','alt','aria-label','placeholder','content']){
      if(!element.hasAttribute(attribute))continue;
      const current=element.getAttribute(attribute),old=values[attribute];
      const source=old&&current===old.last?old.source:current,next=translate(source);
      if(current!==next)element.setAttribute(attribute,next);values[attribute]={source,last:next};
    }
    attrs.set(element,values);
  }
  const title=document.querySelector('title');
  if(!title.dataset.source)title.dataset.source=title.textContent;
  title.textContent=translate(title.dataset.source);
  document.querySelectorAll('[data-site-language]').forEach(select=>{select.value=language;select.setAttribute('aria-label',L('لغة الموقع','Website language'));});
  observer?.observe(document.body,{childList:true,subtree:true,characterData:true});
}
export function setLanguage(next){
  if(!['ar','en'].includes(next))return;
  language=next;localStorage.setItem(key,next);document.documentElement.lang=next;document.documentElement.dir=next==='ar'?'rtl':'ltr';
  const url=new URL(location.href);url.searchParams.set('lang',next);history.replaceState(null,'',url);
  localize();document.dispatchEvent(new CustomEvent('halawacore-site-language',{detail:next}));
}
export function initLanguage(){
  observer=new MutationObserver(()=>{if(pending)return;pending=true;queueMicrotask(()=>{pending=false;localize();});});
  document.addEventListener('change',event=>{if(event.target.matches('[data-site-language]'))setLanguage(event.target.value);});
  setLanguage(language);
}

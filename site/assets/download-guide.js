import {L,getLanguage,localize} from './i18n.js';
import {renderLinuxGuide} from './linux-guide.js';
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let dialog,selection=null,step=0;
const guideKey=platform=>`halawacore-download-guide-${platform==='linux'?'v5':'v3'}-${platform}`;
const remembered=platform=>localStorage.getItem(guideKey(platform))==='read';
function content(){
  const windows=selection.platform==='windows',os=windows?'Windows':'Linux';
  const steps=[
    [L('الملف المناسب لجهازك','The right file for your device'),L(`ستحصل على نسخة ${os} بمعمارية x64. يحتوي الملف على البرنامج ومكتباته؛ لا تحتاج تثبيت Python أو كتابة أوامر.`,`You are getting the ${os} x64 edition. It includes the application and its runtime; you do not need Python or terminal commands.`),
      L('اسم الملف المتوقع: ','Expected file: ')+(windows?'HalawaCore-Windows-x64.zip':'HalawaCore-Linux-x64.tar.gz')],
    [L('فك الضغط ثم شغّل البرنامج','Extract, then open the application'),windows?
      L('بعد التنزيل افتح مجلد التنزيلات. اضغط على ملف ZIP واختر «استخراج الكل»، ثم افتح HalawaCore.exe من المجلد المستخرج.','After downloading, open Downloads. Select the ZIP file and choose Extract All, then open HalawaCore.exe from the extracted folder.'):
      L('بعد التنزيل افتح ملف tar.gz بمدير الأرشيف واختر استخراج. افتح ملف HalawaCore التنفيذي من المجلد المستخرج عبر مدير الملفات، دون sudo أو تشغيله كمستخدم root.','After downloading, extract the tar.gz archive with your archive manager. Open the HalawaCore executable from the extracted folder in your file manager, without sudo or root.'),
      L('ستفتح الواجهة تلقائيًا في متصفحك، وتتواصل مع البرنامج المحلي على جهازك.','The interface opens automatically in your browser and connects to the local application on your device.')],
    [L('خطواتك الأولى داخل البرنامج','Your first steps inside the app'),L('اختر العربية أو الإنجليزية من أعلى الواجهة. يبدأ البرنامج بوضع القراءة فقط. استكشف خريطة المعالج ثم اختر عملية فعلية من التطبيقات.','Choose Arabic or English at the top. The app starts in read-only mode. Explore the core map, then select an actual running process in Applications.'),
      L('ستجد «المساعدة والدليل» تحت الإعدادات، وعلامات ؟ بجانب الأجزاء لشرح وظيفتها.','Find Help & Guide below Settings and use the ? buttons beside sections to understand what they do.')],
    [L('التجارب اختيارية، والاستعادة أولًا','Experiments are optional; restore before closing'),L('إذا أردت تجربة توزيع الأنوية، سجّل الحالة الأساسية أولًا. فعّل التجارب من الإعدادات، وراجع المهام المحددة ثم أكّد التغيير. لا توجد زيادة أداء مضمونة.','If you want an affinity experiment, record a baseline first. Enable experiments in Settings, review the exact tasks and confirm the change. Performance improvements are not guaranteed.'),
      L('أوقف التسجيل واستعد كل التجارب قبل زر «إغلاق HalawaCore». إغلاق التبويب وحده لا يوقف البرنامج المحلي.','Stop recording and restore every experiment before choosing Quit HalawaCore. Closing the tab alone does not stop the local application.')],
  ];
  const [title,description,note]=steps[step];
  return {os,title,description,note};
}
function render(){
  const data=content();
  dialog.querySelector('#download-guide-title').textContent=L(`دليل تنزيل ${data.os} والبداية`,`Download ${data.os} and get started`);
  dialog.querySelector('#download-guide-close').textContent=L('إغلاق','Close');
  dialog.querySelector('#download-guide-progress').setAttribute('aria-label',L('خطوات دليل التحميل','Download guide steps'));
  dialog.querySelector('#download-guide-step').textContent=L(`الخطوة ${step+1} من 4`,`Step ${step+1} of 4`);
  const body=dialog.querySelector('#download-guide-content');
  if(selection.platform==='linux'&&step===1){
    let guide=body.querySelector('[data-linux-guide]');
    if(!guide){body.innerHTML='<div data-linux-guide></div>';guide=body.firstElementChild;}
    renderLinuxGuide(guide);
  }
  else body.innerHTML=`<h3>${escape(data.title)}</h3><p>${escape(data.description)}</p><div class="guide-note">${escape(data.note)}</div>`;
  dialog.querySelector('#download-guide-progress').innerHTML=Array.from({length:4},(_,i)=>`<li ${i===step?'aria-current="step"':''} class="${i<=step?'active':''}"><span>${i+1}</span></li>`).join('');
  const back=dialog.querySelector('#download-guide-back');back.textContent=L('السابق','Back');back.hidden=step===0;
  const next=dialog.querySelector('#download-guide-next');next.textContent=L('التالي','Next');next.hidden=step===3;
  const file=dialog.querySelector('#download-guide-file');file.hidden=step!==3;file.href=selection.link.href;
  const binary=selection.link.href.includes('/releases/download/');file.textContent=binary?L(`تنزيل ${data.os} الآن ↓`,`Download ${data.os} now ↓`):L('افتح صفحة الإصدارات ↗','Open the releases page ↗');
  dialog.querySelector('#download-guide-remember-label').textContent=L('تذكر أنني قرأت الدليل في هذا المتصفح','Remember that I read this guide in this browser');
  dialog.querySelector('[data-site-language]').value=getLanguage();
  localize();
}
function open(link,force=false,startAt=0){
  const platform=link.closest('[data-platform]').dataset.platform;
  if(!force&&remembered(platform))return false;
  selection={platform,link};step=startAt;dialog.querySelector('#download-guide-remember').checked=false;
  render();if(!dialog.open)dialog.showModal();return true;
}
export function initDownloadGuide(){
  if(!document.querySelector('[data-download]'))return;
  dialog=document.createElement('dialog');dialog.id='download-guide';dialog.setAttribute('aria-labelledby','download-guide-title');
  dialog.innerHTML=`<div class="guide-dialog-head"><h2 id="download-guide-title"></h2><button id="download-guide-close" type="button" class="guide-close"></button></div><div class="guide-language"><select data-site-language data-no-i18n aria-label="Website language"><option value="ar">العربية</option><option value="en">English</option></select><span id="download-guide-step" aria-live="polite"></span></div><ol id="download-guide-progress" class="guide-progress" aria-label="Download guide steps"></ol><div id="download-guide-content" aria-live="polite"></div><label class="guide-remember"><input id="download-guide-remember" type="checkbox"><span id="download-guide-remember-label"></span></label><div class="guide-actions"><button id="download-guide-back" class="button outline" type="button"></button><button id="download-guide-next" class="button" type="button"></button><a id="download-guide-file" class="button" href="#"></a></div>`;
  document.body.append(dialog);
  dialog.querySelector('#download-guide-close').onclick=()=>dialog.close();
  dialog.querySelector('#download-guide-back').onclick=()=>{step--;render();};
  dialog.querySelector('#download-guide-next').onclick=()=>{step++;render();};
  dialog.querySelector('#download-guide-file').onclick=()=>{
    if(dialog.querySelector('#download-guide-remember').checked)localStorage.setItem(guideKey(selection.platform),'read');
    dialog.close();
  };
  document.addEventListener('click',event=>{
    const link=event.target.closest('[data-download]');
    if(link){if(remembered(link.closest('[data-platform]').dataset.platform))return;event.preventDefault();open(link);}
    const help=event.target.closest('[data-show-download-guide]');
    if(help){event.preventDefault();open(help.closest('[data-platform]').querySelector('[data-download]'),true);}
  });
  document.addEventListener('halawacore-site-language',()=>{if(dialog.open)render();});
  function openSharedGuide(includeQuery=false){
    const url=new URL(location.href);
    if((includeQuery&&url.searchParams.get('guide')==='linux')||['#linux-commands','#linux-guide'].includes(url.hash)){
      const link=document.querySelector('[data-platform="linux"] [data-download]');
      if(link)open(link,true,1);
    }
  }
  window.addEventListener('hashchange',()=>openSharedGuide());
  openSharedGuide(true);
}

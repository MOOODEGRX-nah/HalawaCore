import {initLanguage,localize} from './i18n.js';
import {initDownloadGuide} from './download-guide.js';
initLanguage();initDownloadGuide();
const repository='MOOODEGRX-nah/HalawaCore';
const status=document.querySelector('#release-status');
if(status){
  const guessed=/Windows/i.test(navigator.userAgent)?'windows':/Linux/i.test(navigator.userAgent)?'linux':null;
  if(guessed)document.querySelector(`[data-platform="${guessed}"]`)?.classList.add('recommended');
  try{
    const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
    let response;
    try{response=await fetch(`https://api.github.com/repos/${repository}/releases/latest`,{signal:controller.signal,headers:{Accept:'application/vnd.github+json'}});}finally{clearTimeout(timer);}
    if(!response.ok)throw new Error('release unavailable');
    const release=await response.json();
    if(release.draft||release.prerelease||!Array.isArray(release.assets))throw new Error('release not public');
    let found=0;
    document.querySelectorAll('[data-download]').forEach(link=>{
      const asset=release.assets.find(a=>a.name===link.dataset.download);
      const platform=link.closest('[data-platform]').dataset.platform;
      const detail=document.querySelector(`[data-detail="${platform}"]`);
      if(asset&&typeof asset.browser_download_url==='string'&&asset.browser_download_url.startsWith(`https://github.com/${repository}/releases/download/`)){
        link.href=asset.browser_download_url;link.innerHTML=`تنزيل ${platform==='windows'?'Windows':'Linux'} <span>↓</span>`;
        detail.textContent=`${release.tag_name} · ${(asset.size/1024/1024).toFixed(1)} MB · تنزيل من GitHub`;found++;
      }else detail.textContent='ملف هذا النظام غير منشور بعد؛ راجع صفحة الإصدارات.';
    });
    status.textContent=found?`الإصدار ${release.tag_name} متاح من مستودع المشروع الرسمي.`:'الإصدار موجود، وملفات التشغيل لم تُرفع بعد. افتح صفحة الإصدارات لمتابعتها.';
  }catch{
    status.textContent='تعذّر التحقق من ملفات الإصدار الآن. يمكنك فتح صفحة إصدارات GitHub مباشرة.';
    status.classList.add('offline-note');
    document.querySelectorAll('[data-detail]').forEach(el=>el.textContent='افتح صفحة الإصدارات للتحقق من توفر ملف نظامك.');
  }
  localize();
}

import {L} from './i18n.js';
const escape=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const linuxCommands={
  install:`mkdir -p "$HOME/Applications/HalawaCore" &&
tar -xzf "./HalawaCore-Linux-x64.tar.gz" -C "$HOME/Applications/HalawaCore" &&
chmod u+x "$HOME/Applications/HalawaCore/HalawaCore" &&
"$HOME/Applications/HalawaCore/HalawaCore"`,
  launch:'"$HOME/Applications/HalawaCore/HalawaCore"',
  manual:'"$HOME/Applications/HalawaCore/HalawaCore" --no-browser',
  check:'uname -m\ngetconf GNU_LIBC_VERSION',
};
export const linuxDistributions=[
  {id:'cachyos',name:'CachyOS / Arch Linux',tools:'sudo pacman -S --needed tar gzip xdg-utils',source:'https://man.archlinux.org/man/pacman.8.en'},
  {id:'fedora',name:'Fedora Workstation / KDE (DNF)',tools:'sudo dnf install tar gzip xdg-utils',source:'https://dnf5.readthedocs.io/en/latest/commands/install.8.html'},
  {id:'debian',name:'Ubuntu / Debian / Linux Mint',tools:'sudo apt update && sudo apt install tar gzip xdg-utils',source:'https://ubuntu.com/server/docs/how-to/software/package-management/'},
  {id:'opensuse',name:'openSUSE (Zypper)',tools:'sudo zypper install tar gzip xdg-utils',source:'https://doc.opensuse.org/documentation/tumbleweed/zypper/'},
  {id:'other',name:'Other / Atomic',tools:null,source:null},
];
const storageKey='halawacore-linux-distribution';
let distribution=localStorage.getItem(storageKey)||'cachyos';
if(!linuxDistributions.some(row=>row.id===distribution))distribution='cachyos';
function command(title,code){
  return `<div class="linux-command"><div class="linux-command-head"><h4>${escape(title)}</h4><button class="guide-close" type="button" data-copy-linux-code>${escape(L('نسخ','Copy'))}</button></div><pre dir="ltr"><code data-no-i18n>${escape(code)}</code></pre><span class="linux-copy-status" role="status" aria-live="polite"></span></div>`;
}
export function renderLinuxGuide(element){
  const selected=linuxDistributions.find(row=>row.id===distribution);
  const expanded=[...element.querySelectorAll('details')].map((item,index)=>item.open?index:-1);
  element.dataset.noI18n='';
  element.innerHTML=`<div class="linux-guide-intro"><h3>${escape(L('أوامر Linux: فك الضغط والتشغيل','Linux commands: extract and run'))}</h3><p>${escape(L('بعد تنزيل HalawaCore-Linux-x64.tar.gz، افتح مجلده في مدير الملفات واختر «افتح الطرفية هنا». الصق الأوامر التالية؛ لا يُفترض أن اسم مجلد التنزيلات لديك هو Downloads.','After downloading HalawaCore-Linux-x64.tar.gz, open its folder in your file manager and choose Open Terminal Here. Paste the commands below; your downloads folder does not need to be named Downloads.'))}</p></div>
    <label class="linux-distribution-label">${escape(L('اختر توزيعتك','Choose your distribution'))}<select data-linux-distribution>${linuxDistributions.map(row=>`<option value="${row.id}" ${row.id===distribution?'selected':''}>${escape(row.id==='other'?L('توزيعة أخرى / أنظمة Atomic',row.name):row.name)}</option>`).join('')}</select></label>
    <p class="linux-requirements">${escape(L('المتطلبات: x86_64 وglibc 2.35 أو أحدث، مع متصفح وجلسة سطح مكتب. Python مضمّن.','Requires x86_64 Linux, glibc 2.35+, a browser and a desktop session. Python is bundled.'))}</p>
    ${command(L('1. فك الضغط، منح إذن التنفيذ، ثم التشغيل','1. Extract, allow execution, then launch'),linuxCommands.install)}
    <p class="linux-command-note">${escape(L('يفك الأمر الملف داخل Applications/HalawaCore في مجلدك الشخصي، ثم يشغّله دون صلاحيات الجذر. إذا اختلف اسم الملف الذي نزلته، عدّل الاسم في أمر tar. يبدأ الأمر التالي فقط إذا نجح السابق.','The command extracts into Applications/HalawaCore in your home folder and launches without root privileges. If your downloaded filename differs, adjust the tar command. Each command runs only if the previous one succeeds.'))}</p>
    ${command(L('2. تشغيل البرنامج لاحقًا','2. Launch again later'),linuxCommands.launch)}
    <details class="linux-extra" data-browser-fix><summary>${escape(L('حل مشكلة فتح المتصفح أو خطأ rl_trim_arg_from_keyseq','Fix browser launch or rl_trim_arg_from_keyseq errors'))}</summary><p>${escape(L('إذا ظهر undefined symbol: rl_trim_arg_from_keyseq، حدّث HalawaCore إلى الإصدار 0.3.2 أو أحدث من رابط التنزيل. عولج تعارض المكتبات في البرنامج نفسه، ولا تحتاج تغيير مكتبات النظام. شغّل النسخة الجديدة بعد فك ضغطها.','If you see undefined symbol: rl_trim_arg_from_keyseq, download HalawaCore 0.3.2 or later. The library conflict is fixed in the application; no system-library changes are needed. Extract and run the new release.'))}</p><a class="text-link" href="https://github.com/MOOODEGRX-nah/HalawaCore/releases/latest" target="_blank" rel="noopener noreferrer">${escape(L('أحدث إصدار من HalawaCore ↗','Latest HalawaCore release ↗'))}</a><p>${escape(L('إذا لم يُفتح المتصفح تلقائيًا، استخدم الأمر التالي في الإصدار 0.3.2 أو أحدث. سيظهر رابط يبدأ بـ http://127.0.0.1: انسخه إلى متصفحك واترك الطرفية مفتوحة.','If the browser does not open automatically, use the command below with version 0.3.2 or later. Copy the printed http://127.0.0.1: address into your browser and keep the terminal open.'))}</p>${command(L('تشغيل يدوي دون فتح المتصفح','Start without automatic browser launch'),linuxCommands.manual)}<p>${escape(L('ظهور الرابط يعني أن الواجهة المحلية جاهزة. أوقف التسجيل واستعد التجارب قبل الإغلاق. الضغط على Ctrl+C يغلق النسخة الجديدة دون تتبّع خطأ KeyboardInterrupt.','The printed URL means the local interface is ready. Stop recording and restore experiments before closing. Ctrl+C closes the updated app without a KeyboardInterrupt traceback.'))}</p></details>
    <details class="linux-extra"><summary>${escape(L('الأدوات ناقصة؟ أوامر اختيارية حسب التوزيعة','Missing tools? Optional distribution commands'))}</summary><p>${escape(L('tar وgzip لفك الأرشيف، وxdg-utils للمساعدة في فتح المتصفح. شغّل هذا الجزء فقط إذا كانت هذه الأدوات ناقصة، ثم أعد أوامر الخطوة الأولى. sudo هنا لتثبيت الحزم فقط.','tar and gzip extract the archive; xdg-utils helps open the browser. Use this section only if these tools are missing, then repeat step 1. sudo here is only for package installation.'))}</p>
    ${selected.tools?command(selected.name,selected.tools):`<p>${escape(L('استخدم أوامر النسخة المحمولة أعلاه إن كانت الأدوات متاحة. تثبيت الحزم على Fedora Atomic وopenSUSE MicroOS وتوزيعات musl/Alpine يحتاج تعليمات خاصة؛ أوامر DNF وZypper هنا مخصصة للأنظمة التقليدية القابلة للتعديل، والملف الحالي مخصص لـ glibc.','Use the portable commands above when the tools are present. Fedora Atomic, openSUSE MicroOS and musl/Alpine distributions require separate package guidance. The DNF/Zypper commands here target conventional mutable systems; this executable targets glibc.'))}</p>`}
    ${selected.source?`<a class="text-link" href="${selected.source}" target="_blank" rel="noopener noreferrer">${escape(L('مرجع مدير الحزم الرسمي ↗','Official package-manager reference ↗'))}</a>`:''}</details>
    <details class="linux-extra"><summary>${escape(L('التحقق من المعمارية وإصدار glibc','Check architecture and glibc version'))}</summary>${command(L('معلومات التوافق','Compatibility information'),linuxCommands.check)}<p>${escape(L('ينبغي أن تظهر x86_64، ثم glibc 2.35 أو أحدث. أنظمة ARM وglibc الأقدم تحتاج ملفًا مبنيًا خصيصًا لها؛ تثبيت أدوات فك الضغط لا يحوّل الملف إلى معمارية أخرى. هذه تعليمات تشغيل ولا تعني اختبار كل إصدار من التوزيعات على عتاد فعلي.','Expect x86_64 and glibc 2.35 or newer. ARM and older glibc systems need a compatible build; installing archive tools does not change the executable architecture. These instructions do not establish physical testing on every distribution release.'))}</p></details>
    <details class="linux-extra"><summary>${escape(L('إذا لم يبدأ البرنامج','If the application does not start'))}</summary><p>${escape(L('رسالة «الملف غير موجود» من tar تعني عادة أنك لست في مجلد الأرشيف أو أن اسمه مختلف. إذا ظهر خطأ GLIBC، راجع المتطلبات أعلاه. إذا استمر خطأ الإذن بعد chmod، فقد يكون مسار التشغيل مركّبًا بخيار noexec؛ اطلب المساعدة بدل تغيير إعدادات حماية النظام. اترك الطرفية مفتوحة أثناء الاستخدام، واستعد التجارب قبل الإغلاق.','A tar file-not-found message usually means the terminal is in the wrong folder or the archive has a different name. For a GLIBC error, check the requirements above. If permission is still denied after chmod, the launch location may be mounted noexec; seek help rather than changing system protections. Keep the terminal open during use and restore experiments before closing.'))}</p></details>`;
  element.querySelectorAll('details').forEach((item,index)=>{item.open=expanded.includes(index);});
}
export function initLinuxGuides(){
  document.addEventListener('change',event=>{
    if(!event.target.matches('[data-linux-distribution]'))return;
    if(!linuxDistributions.some(row=>row.id===event.target.value))return;
    distribution=event.target.value;localStorage.setItem(storageKey,distribution);
    const focused=event.target.closest('[data-linux-guide]');
    document.querySelectorAll('[data-linux-guide]').forEach(renderLinuxGuide);
    focused.querySelector('[data-linux-distribution]').focus();
  });
  document.addEventListener('click',async event=>{
    const button=event.target.closest('[data-copy-linux-code]');if(!button)return;
    const block=button.closest('.linux-command'),status=block.querySelector('[role=status]');
    try{await navigator.clipboard.writeText(block.querySelector('code').textContent);status.textContent=L('تم نسخ الأوامر. الصقها في الطرفية عندما تكون جاهزًا.','Commands copied. Paste into your terminal when you are ready.');}
    catch{status.textContent=L('تعذّر النسخ التلقائي. حدّد الأوامر وانسخها يدويًا.','Automatic copy failed. Select and copy the commands manually.');}
  });
  document.addEventListener('halawacore-site-language',()=>document.querySelectorAll('[data-linux-guide]').forEach(renderLinuxGuide));
}

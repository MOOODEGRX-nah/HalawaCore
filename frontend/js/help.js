import {state,esc,heading,panel} from './state.js';
import {bi,getLanguage} from './i18n.js';

const feature=(en,ar,descriptionEn,descriptionAr,whenEn,whenAr,limitEn,limitAr)=>({title:[en,ar],description:[descriptionEn,descriptionAr],when:[whenEn,whenAr],limit:[limitEn,limitAr]});
export const topics={
  dashboard:feature('Dashboard','لوحة التحكم','An overview of your actual processor, visible cores, current utilization and shared cache.','ملخص لمعالجك الفعلي والأنوية الظاهرة والاستخدام الحالي والكاش المشترك.','Start here to understand what the operating system exposes.','ابدأ هنا لفهم المعلومات التي يكشفها نظام التشغيل.','A usage percentage is activity, not proof of faster applications.','نسبة الاستخدام تعبّر عن النشاط، ولا تثبت أن التطبيق أصبح أسرع.'),
  topology:feature('CPU topology & SMT','طوبولوجيا المعالج وخيوط SMT','A physical core can contain several logical hardware threads. SMT siblings share a physical core; they are not separate physical cores.','قد تحتوي النواة الفعلية على عدة خيوط منطقية. خيوط SMT الشقيقة تشترك في النواة، وليست أنوية فعلية منفصلة.','Use the map and table to see each core, its siblings and the operating-system CPU IDs.','استخدم الخريطة والجدول لرؤية كل نواة وخيوطها الشقيقة وأرقام المعالجات في النظام.','CPU numbering is not assumed to be sequential or split into equal halves. Missing relationships remain unverified.','لا يُفترض أن ترقيم المعالجات متتابع أو مقسوم إلى نصفين متساويين. العلاقات الناقصة تبقى غير مؤكدة.'),
  applications:feature('Applications & processes','التطبيقات والعمليات','The explorer lists accessible running processes, their identities, parent relationships, thread counts, memory and observed affinity.','يعرض المستكشف العمليات المتاحة وهوياتها وعلاقاتها بالعمليات الأم وعدد خيوطها وذاكرتها وتوزيع أنويتها المرصود.','Select the actual running process you want to analyze, then review its executable and threads.','اختر العملية الفعلية التي تريد تحليلها، ثم راجع ملفها التنفيذي وخيوطها.','Similar names do not establish a relationship. Protected or inaccessible processes remain read-only.','تشابه الأسماء لا يثبت وجود علاقة. العمليات المحمية أو غير المتاحة تبقى للقراءة فقط.'),
  planner:feature('Affinity planner','مخطط توزيع الأنوية','Affinity controls which CPUs a task is eligible to run on. The planner proposes a set; it does not apply it until you explicitly confirm a fresh preview.','يحدد توزيع الأنوية المعالجات التي يجوز تشغيل المهمة عليها. يقترح المخطط مجموعة، ولا يطبقها حتى تؤكد معاينة جديدة صراحة.','Choose a process, keep the safe default or select an experiment, and inspect the exact affected tasks.','اختر عملية، واحتفظ بالوضع الافتراضي الآمن أو حدد تجربة، ثم افحص المهام المتأثرة بدقة.','Affinity does not reserve cores exclusively or guarantee higher FPS, lower latency or better performance.','توزيع الأنوية لا يحجزها حصريًا ولا يضمن زيادة FPS أو تقليل التأخير أو تحسين الأداء.'),
  scope:feature('Task scope & identities','نطاق المهام والتحقق من الهوية','Main/default task, one explicit thread, existing process threads, or explicitly checked related processes determine exactly which PIDs and TIDs are included.','تحدد المهمة الرئيسية أو الافتراضية، أو خيط محدد، أو خيوط العملية الحالية، أو العمليات المرتبطة المختارة بدقة أرقام PID وTID المشمولة.','Use the scope selector and read every PID/TID in the confirmation preview.','استخدم محدد النطاق واقرأ كل PID وTID في معاينة التأكيد.','New threads or child processes may not remain covered. On Windows, PID is not TID; the default is the oldest surviving thread.','قد لا تشمل التجربة الخيوط الجديدة أو العمليات الفرعية اللاحقة. في Windows لا يساوي PID رقم TID؛ المهمة الافتراضية هي أقدم خيط باقٍ.'),
  x3d:feature('AMD X3D & shared L3','AMD X3D وكاش L3 المشترك','Cache-sharing masks and sizes identify L3 domains. Verified X3D evidence can enable a cache-oriented experiment; a separate frequency experiment needs reliable frequency-group evidence.','تحدد أقنعة مشاركة الكاش وأحجامه مجموعات L3. قد يتيح دليل X3D الموثوق تجربة موجهة للكاش، وتحتاج تجربة التردد إلى دليل موثوق مستقل لمجموعته.','Compare cache, frequency and scheduler-default choices only when the relevant evidence is available.','قارن خيارات الكاش والتردد والإعداد الافتراضي للمجدول عندما تتوفر الأدلة المطلوبة.','A cache domain is not automatically a CCD/die. Unknown groups stay unverified; scheduler preference is read-only.','مجموعة الكاش ليست تلقائيًا CCD أو شريحة. المجموعات غير المعروفة تبقى غير مؤكدة، وتفضيل الجدولة للقراءة فقط.'),
  cppc:feature('CPPC & preferred cores','CPPC والأنوية المفضلة','Firmware and driver rankings can indicate preferred cores at the time of reading. They are unitless scheduling hints, not benchmark scores or direct clock frequencies.','قد تشير تصنيفات البرنامج الثابت والتعريف إلى الأنوية المفضلة وقت القراءة. هي تلميحات جدولة بلا وحدة، وليست نتائج اختبار أداء أو ترددات مباشرة.','Use them as context for a measured experiment, alongside actual topology and current restrictions.','استخدمها كسياق لتجربة مقاسة، مع الطوبولوجيا الفعلية والقيود الحالية.','Rankings can change and cannot be compared as universal performance scores across unrelated CPUs.','قد تتغير التصنيفات، ولا تصلح كمقياس أداء عام للمقارنة بين معالجات مختلفة.'),
  restore:feature('Preview, apply & restore','المعاينة والتطبيق والاستعادة','The preview lists original masks and exact task identities. Apply rechecks them and verifies the kernel result. Restore returns each surviving verified task to its own recorded mask.','تعرض المعاينة الأقنعة الأصلية وهويات المهام المحددة. يعيد التطبيق فحصها ويتحقق من نتيجة النظام، وتعيد الاستعادة كل مهمة باقية وموثوقة إلى قناعها المسجل.','Always restore experiments before closing HalawaCore. Review partial failures instead of assuming every task changed.','استعد التجارب دائمًا قبل إغلاق HalawaCore. راجع الإخفاقات الجزئية بدل افتراض تغيير جميع المهام.','Keep the local backend running. Crash, power-loss and SIGKILL recovery are not implemented.','أبقِ البرنامج المحلي يعمل. لا توجد استعادة مضمونة بعد التعطل أو انقطاع الطاقة أو الإنهاء القسري.'),
  lab:feature('Performance Lab','مختبر الأداء','Record a baseline, an experimental phase and a restored phase. Measurements include real CPU activity, process memory, thread counts and observed affinity.','سجّل حالة أساسية ومرحلة تجريبية ومرحلة بعد الاستعادة. تشمل القياسات نشاط المعالج الفعلي وذاكرة العملية وعدد الخيوط وتوزيعها المرصود.','Run the same representative workload for comparable durations and inspect the recorded masks.','شغّل عملًا ممثلًا ومتقاربًا للمدة نفسها، وافحص الأقنعة المسجلة.','Phase names are manual labels. CPU usage alone is not an FPS, latency, power or temperature measurement.','أسماء المراحل تسميات يدوية. استخدام المعالج وحده ليس قياسًا لـ FPS أو التأخير أو الطاقة أو الحرارة.'),
  profiles:feature('Saved profiles','الملفات المحفوظة','Profiles store named CPU selections for later review. Loading one fills the planner; it never applies affinity automatically.','تحفظ الملفات مجموعات أنوية بأسماء لمراجعتها لاحقًا. تحميل الملف يملأ المخطط ولا يطبق توزيع الأنوية تلقائيًا.','Save a useful selection, choose a current running target, and preview again before applying.','احفظ اختيارًا مفيدًا، وحدد عملية تعمل حاليًا، ثم أعد المعاينة قبل التطبيق.','CPU IDs and restrictions may differ after hotplug, a system change or use on another device.','قد تختلف أرقام المعالجات وقيودها بعد تغيير الأنوية المتصلة أو النظام أو استخدام جهاز آخر.'),
  numbering:feature('CPU display numbering','ترقيم المعالجات المعروض','Linux CPU IDs and desktop checkbox labels may differ. KDE can be calibrated to OS ID + 1 or the same ID. Windows display labels show processor group and index.','قد تختلف أرقام Linux عن تسميات مربعات الاختيار في سطح المكتب. يمكن معايرة KDE ليعرض رقم النظام + 1 أو الرقم نفسه، وتعرض Windows المجموعة ورقم المعالج.','Use the OS ID for actual affinity and the display ID to match the desktop interface.','استخدم رقم النظام للتوزيع الفعلي، والرقم المعروض لمطابقة واجهة سطح المكتب.','Changing display numbering does not change CPU identity, topology or affinity.','تغيير الترقيم المعروض لا يغير هوية المعالج أو الطوبولوجيا أو توزيع الأنوية.'),
  numa:feature('NUMA locality','محلية NUMA','NUMA nodes describe processor and memory relationships exposed by the OS. Their boundaries may differ from cache-sharing domains.','تصف عقد NUMA علاقات المعالج والذاكرة التي يكشفها النظام، وقد تختلف حدودها عن مجموعات الكاش المشترك.','Inspect node membership before an optional locality-oriented CPU experiment.','افحص عضوية العقد قبل تجربة أنوية اختيارية موجهة للمحلية.','CPU affinity alone does not set memory-allocation policy or guarantee memory locality.','توزيع الأنوية وحده لا يحدد سياسة تخصيص الذاكرة ولا يضمن محليتها.'),
  settings:feature('Settings & read-only mode','الإعدادات ووضع القراءة فقط','Change language, appearance, refresh interval and display calibration. Read-only mode blocks affinity application and starts enabled each backend session.','غيّر اللغة والمظهر وفترة التحديث ومعايرة العرض. يمنع وضع القراءة فقط تطبيق توزيع الأنوية، ويبدأ مفعّلًا مع كل تشغيل للبرنامج المحلي.','Keep read-only mode enabled while learning the interface. Enable experiments only for an intentional reviewed change.','أبقِ وضع القراءة فقط مفعّلًا أثناء تعلم الواجهة، وفعّل التجارب فقط لتغيير مقصود تمت مراجعته.','Disabling read-only does not apply anything by itself. Restore remains available even when read-only is re-enabled.','إيقاف وضع القراءة فقط لا يطبق أي تغيير وحده. تبقى الاستعادة متاحة حتى بعد إعادة تفعيل القراءة فقط.'),
  privacy:feature('Privacy & export','الخصوصية والتصدير','Hardware and process analysis stays local. JSON export creates a file on your device; it may include process identities and hardware details.','يبقى تحليل العتاد والعمليات محليًا. ينشئ تصدير JSON ملفًا على جهازك، وقد يتضمن هويات عمليات وتفاصيل العتاد.','Export when you need to keep or compare measurements, and review the file before sharing it.','صدّر البيانات عندما تحتاج حفظ القياسات أو مقارنتها، وراجع الملف قبل مشاركته.','Process environments are not read and raw command arguments are hidden. Exported data is not uploaded automatically.','لا تُقرأ بيئات العمليات وتُخفى وسائط الأوامر الخام. لا تُرفع البيانات المصدرة تلقائيًا.'),
  windows:feature('Windows compatibility','التوافق مع Windows','Windows uses native topology, process ownership and thread identity APIs. Affinity experiments are limited to safely supported scheduling states.','تستخدم Windows واجهاتها الأصلية للطوبولوجيا وملكية العمليات وهوية الخيوط. تقتصر تجارب الأنوية على حالات جدولة مدعومة بأمان.','Use an owned accessible process and inspect its exact thread preview.','استخدم عملية متاحة تملكها وافحص معاينة خيوطها المحددة.','Multiple processor groups, explicit CPU Sets and inaccessible scheduling state remain read-only in this release.','تبقى المجموعات المتعددة وCPU Sets الصريحة وحالات الجدولة غير المتاحة للقراءة فقط في هذا الإصدار.'),
};
const text=pair=>getLanguage()==='ar'?pair[1]:pair[0];
let activeTopic=null,search='';
function topicFor(title){
  if(/SMT/i.test(title))return 'topology';
  if(/CPPC|Rank|preferred/i.test(title))return 'cppc';
  if(/NUMA|Node/i.test(title))return 'numa';
  if(/X3D|cache|L3|frequency/i.test(title))return 'x3d';
  if(/restore|original affinity|verification/i.test(title))return 'restore';
  if(/scope|threads|TID/i.test(title))return 'scope';
  if(/numbering|Display IDs|OS CPU/i.test(title))return 'numbering';
  if(/privacy|export|logging|telemetry/i.test(title))return 'privacy';
  if(/record|activity|load|utilization|Usage|comparison/i.test(title))return 'lab';
  if(/profile/i.test(title))return 'profiles';
  if(/core|SMT|topology|capacity/i.test(title))return 'topology';
  return topics[state.page]?state.page:'dashboard';
}
export function attachHelp(){
  const selectors='.page-heading h1,.panel-head h2,.panel-head h3,.settings-row h3,th';
  document.querySelectorAll(selectors).forEach(element=>{
    if(element.querySelector('.help-button')||element.closest('[data-no-i18n],#feature-help,#welcome-guide'))return;
    const title=element.textContent.trim();
    const button=document.createElement('button');button.type='button';button.className='help-button';button.textContent='?';
    button.textContent=bi('?','؟');button.dataset.noI18n='';button.dataset.helpTopic=topicFor(title);
    button.setAttribute('aria-label',bi('Explain this section','شرح هذا الجزء'));button.title=bi('What does this section do?','ماذا يفعل هذا الجزء؟');
    element.append(button);
  });
}
export function openTopic(id){
  const topic=topics[id]||topics.dashboard;activeTopic=id;
  const dialog=document.querySelector('#feature-help');
  dialog.querySelector('#feature-help-title').textContent=text(topic.title);
  dialog.querySelector('#feature-help-body').innerHTML=`<p>${esc(text(topic.description))}</p><h3>${esc(bi('When to use it','متى تستخدمه'))}</h3><p>${esc(text(topic.when))}</p><h3>${esc(bi('Limits to understand','حدود يجب فهمها'))}</h3><p>${esc(text(topic.limit))}</p><a class="text-button" href="#help" id="full-help-link">${esc(bi('Open the full guide →','فتح الدليل الكامل ←'))}</a>`;
  document.querySelector('#full-help-link').onclick=()=>dialog.close();
  dialog.querySelector('[data-close-help]').textContent=bi('Close','إغلاق');
  if(!dialog.open)dialog.showModal();
}
export function renderHelp(){
  document.querySelector('#content').innerHTML=heading(bi('Help & Guide','المساعدة والدليل'),bi('Understand each feature before using it. No system settings change when you read this guide.','افهم كل خاصية قبل استخدامها. قراءة هذا الدليل لا تغيّر أي إعداد للنظام.'))+
    `<div class="help-start"><div><h2>${esc(bi('New to HalawaCore?','تستخدم HalawaCore لأول مرة؟'))}</h2><p>${esc(bi('Choose your language, explore topology, select a process and record a baseline.','اختر لغتك، واستكشف الطوبولوجيا، وحدد عملية وسجّل الحالة الأساسية.'))}</p></div><button class="primary" id="show-welcome">${esc(bi('Show the welcome guide','عرض دليل البداية'))}</button></div><div class="toolbar"><input id="guide-search" type="search" aria-label="${esc(bi('Search the guide','ابحث في الدليل'))}" placeholder="${esc(bi('Search features and terms…','ابحث في الخصائص والمصطلحات…'))}" value="${esc(search)}"></div><div class="help-grid" id="guide-topics"></div>`;
  document.querySelector('#show-welcome').onclick=()=>showWelcome(true);
  document.querySelector('#guide-search').oninput=event=>{search=event.target.value;drawTopics();};drawTopics();
}
function drawTopics(){
  const filtered=Object.entries(topics).filter(([,topic])=>JSON.stringify(topic).toLowerCase().includes(search.toLowerCase()));
  document.querySelector('#guide-topics').innerHTML=filtered.map(([id,topic])=>`<article class="guide-topic"><h2>${esc(text(topic.title))}</h2><p>${esc(text(topic.description))}</p><details><summary>${esc(bi('When to use it & limits','متى تستخدمه وحدوده'))}</summary><p>${esc(text(topic.when))}</p><p class="guide-limit">${esc(text(topic.limit))}</p></details></article>`).join('')||`<p>${esc(bi('No matching guide topics.','لا توجد موضوعات مساعدة مطابقة.'))}</p>`;
}
function welcomeBody(){
  return `<label class="field">${esc(bi('Choose your language','اختر لغتك'))}<select data-language-select data-no-i18n><option value="ar">العربية</option><option value="en">English</option></select></label><ol class="welcome-steps"><li><strong>${esc(bi('Explore in read-only mode','استكشف بوضع القراءة فقط'))}</strong><p>${esc(bi('Start with the dashboard and core map. Unknown hardware data stays unverified.','ابدأ بلوحة التحكم وخريطة الأنوية. المعلومات غير المعروفة تبقى غير مؤكدة.'))}</p></li><li><strong>${esc(bi('Choose the actual process','اختر العملية الفعلية'))}</strong><p>${esc(bi('Inspect the process identity and threads, then record an original-affinity baseline.','افحص هوية العملية وخيوطها، ثم سجّل قياسًا أساسيًا بالتوزيع الأصلي.'))}</p></li><li><strong>${esc(bi('Preview before an experiment','عاين قبل التجربة'))}</strong><p>${esc(bi('Nothing changes without enabling experiments, reviewing affected tasks and confirming. Restore before using Quit HalawaCore.','لا يتغير شيء دون تفعيل التجارب ومراجعة المهام المتأثرة والتأكيد. استعد التجارب قبل استخدام زر إغلاق HalawaCore.'))}</p></li></ol><p class="notice neutral">${esc(bi('Use the ? buttons beside sections, or Help & Guide below Settings, whenever you need an explanation.','استخدم أزرار ؟ بجانب الأقسام، أو المساعدة والدليل تحت الإعدادات، عندما تحتاج شرحًا.'))}</p>`;
}
export function showWelcome(force=false){
  if(!force&&localStorage.getItem('halawacore-welcome-v3'))return;
  const dialog=document.querySelector('#welcome-guide');dialog.querySelector('#welcome-title').textContent=bi('Welcome to HalawaCore','مرحبًا بك في HalawaCore');
  dialog.querySelector('#welcome-body').innerHTML=welcomeBody();dialog.querySelector('[data-close-welcome]').textContent=bi('Start exploring','ابدأ الاستكشاف');
  dialog.querySelector('[data-language-select]').value=getLanguage();
  if(!dialog.open&&!document.querySelector('#confirm-dialog').open)dialog.showModal();
}
export function initHelp(){
  document.addEventListener('click',event=>{
    const button=event.target.closest('[data-help-topic]');if(button){event.preventDefault();event.stopPropagation();openTopic(button.dataset.helpTopic);}
    if(event.target.closest('[data-close-help]'))document.querySelector('#feature-help').close();
    if(event.target.closest('[data-close-welcome]'))document.querySelector('#welcome-guide').close();
  });
  document.querySelector('#welcome-guide').addEventListener('close',()=>localStorage.setItem('halawacore-welcome-v3','1'));
  document.addEventListener('halawacore-language',()=>{
    document.querySelectorAll('.help-button').forEach(button=>{button.textContent=bi('?','؟');button.title=bi('What does this section do?','ماذا يفعل هذا الجزء؟');button.setAttribute('aria-label',bi('Explain this section','شرح هذا الجزء'));});
    if(document.querySelector('#feature-help').open)openTopic(activeTopic);
    if(document.querySelector('#welcome-guide').open)showWelcome(true);
    if(state.page==='help')renderHelp();
  });
}

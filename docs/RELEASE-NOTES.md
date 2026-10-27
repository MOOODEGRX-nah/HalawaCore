## العربية

- تحديد حتى 32 عملية من صفحة التطبيقات باستخدام مربعات الاختيار، مع تحديد الظاهر ومسح الاختيار وإزالة عملية منفردة.
- بقاء الاختيارات عند البحث والتحديث، مع إزالة العمليات المنتهية أو التي تغيرت هويتها والتنبيه لذلك.
- مخطط مشترك يعرض العمليات المحددة والأنوية المسموح بها لكل خيوطها الحالية، ثم معاينة واحدة وتأكيد صريح للتطبيق.
- استعادة التوزيع الأصلي المستقل لكل خيط، ورفض المعاينة القديمة أو الصلاحيات غير الكافية قبل بدء الكتابة؛ تظل النتائج الجزئية والاستعادة مرئية عند حدوث تغيّر أثناء التطبيق.
- دعم العربية والإنجليزية وشرح الميزة داخل المساعدة. يسجل مختبر الأداء العملية الأولى المحددة فقط، ولا تتبع التجربة الخيوط أو العمليات الجديدة تلقائيًا.

يتضمن الإصدار إصلاح فتح المتصفح على Linux. يبدأ البرنامج للقراءة فقط، ولا يضمن توزيع الأنوية تحسن الأداء. تتطلب نسخة Linux معمارية x86_64 وglibc 2.35+ ومتصفحًا مثبتًا. تظل قيود Windows متعددة المجموعات وCPU Sets وبيانات X3D غير المؤكدة كما هي.

## English

- Select up to 32 running processes with checkboxes, filtered select-all, clear selection and individual removal.
- Preserve selections across search and refresh; remove exited or changed process identities with a notice.
- Use a shared planner bounded by every included current task's permitted CPUs, then review one exact-task preview and explicitly confirm application.
- Restore each thread's individual original mask. Stale identities, masks and permissions are checked before writes; runtime races can still produce visible partial results with restoration records.
- Include Arabic/English controls and help. Performance Lab records the first selected process only; new threads or child processes are not tracked automatically.

The Linux browser-launch fix is retained. The app starts read-only and affinity restrictions do not guarantee better performance. Linux requires x86_64, glibc 2.35+ and an installed browser. Windows processor-group/CPU Set limitations and unverified X3D states remain explicit.

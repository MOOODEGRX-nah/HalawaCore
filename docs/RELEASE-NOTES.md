## العربية

- إصلاح خطأ فتح المتصفح على Linux الذي قد يظهر برسالة `undefined symbol: rl_trim_arg_from_keyseq` على أنظمة مثل CachyOS.
- عزل مسار مكتبات البرنامج عن مشغّل متصفح النظام.
- إظهار رابط الواجهة المحلية دائمًا في الطرفية، مع استمرار البرنامج إذا تعذّر فتح المتصفح تلقائيًا.
- تشغيل يدوي بالخيار `--no-browser` وإغلاق عادي عند استخدام Ctrl+C.
- تضمين إرشادات Linux المحدّثة، مع بقاء القراءة فقط افتراضيًا والتأكيد والاستعادة لكل تجربة.

تتطلب نسخة Linux معمارية x86_64 ومكتبة glibc 2.35 أو أحدث ومتصفحًا مثبتًا. تُرفق تقارير التحقق مع الملفات التنفيذية. لا توجد مكاسب أداء مضمونة، وتبقى قيود Windows وبيانات X3D غير المؤكدة كما هي.

## English

- Fix Linux browser launch failures such as `undefined symbol: rl_trim_arg_from_keyseq` on newer systems including CachyOS.
- Restore the system browser launcher's original library search path without changing the backend environment.
- Always print the local interface URL and keep the app running when automatic browser launch fails.
- Support manual startup with `--no-browser` and clean Ctrl+C shutdown.
- Include updated Linux guidance while retaining default read-only mode, confirmation and restoration for affinity experiments.

Linux requires x86_64, glibc 2.35+ and an installed browser. Verification reports are included with executable archives. Performance gains are not guaranteed. Existing Windows restrictions and unverified X3D data remain explicit.

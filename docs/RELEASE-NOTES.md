## العربية

- تحديث HalawaCore من الإعدادات: فحص الإصدار، تنزيل موثّق، عرض التغييرات، تأكيد التثبيت ثم إعادة التشغيل.
- حزمة أصلية لـ CachyOS/Arch تُثبّت عبر نافذة صلاحيات النظام ومدير الحزم، مع بقاء البرنامج بحسابك العادي.
- تحديث النسخ المحمولة على Linux وWindows مع نسخة `.previous` احتياطية. ينتظر مساعد Windows خروج النسخة القديمة قبل الاستبدال ويعيد فتح الجديدة.
- التحقق من مصدر الإصدار المستقر وبصمة SHA-256 وحجم الملفات ومحتوى الأرشيف ورقم الإصدار؛ لا توجد فحوص تلقائية أو مشاركة بيانات عتاد.
- منع التثبيت أثناء التسجيل أو قبل استعادة تجارب توزيع الأنوية. صدّر قياسات الجلسة قبل إعادة التشغيل؛ تبقى بيانات اللغة والملفات المحفوظة.

يلزم تثبيت 0.6.0 مرة واحدة للنسخ الأقدم كي تظهر الميزة. تحديث نسخ المصدر أو الملفات المملوكة لمدير حزم غير مدعوم يتم من مصدرها الرسمي. SHA-256 ليست توقيعًا رقميًا مستقلًا. قيود X3D وWindows والمقارنة دون FPS تبقى واضحة. Linux: x86_64 وglibc 2.35+ ومتصفح مثبت.

## English

- Update HalawaCore from Settings: check, download and verify, read changes, explicitly install and restart.
- Publish a native CachyOS/Arch package installed through the system permission dialog and package manager, while the app stays unprivileged.
- Update writable portable Linux/Windows copies with a `.previous` backup. The Windows helper waits for the old process to exit before replacement and reopening.
- Validate the fixed stable-release source, GitHub SHA-256, size, archive members and version. No automatic background checks or hardware uploads.
- Reject installation during recording or unrestored affinity experiments. Export session measurements before restart; persistent language/profile data is retained.

Older versions need a one-time installation of 0.6.0 to obtain the feature. Source checkouts and unsupported managed installations update through their official source. SHA-256 is not an independent digital signature. Existing X3D/Windows restrictions and the lack of FPS measurement remain explicit. Linux requires x86_64, glibc 2.35+ and an installed browser.

## العربية

- عرض استخدام العملية افتراضيًا كنسبة من إجمالي المعالجات المنطقية المتصلة، مع إمكانية اختيار المجموع التقليدي. تعادل 800% استخدام 8 معالجات منطقية مكافئة، أو 50% من جهاز فيه 16 معالجًا منطقيًا متصلًا.
- إضافة تسجيل قبل التعديل وبعده داخل مختبر الأداء، وجدول الفروق ومنحنيين بمحاذاة الزمن وتصدير المقارنة مع القياسات.
- مقارنة متوسط الاستهلاك وذروته والذاكرة والخيوط والتوزيع المرصود، مع حساب المتوسطات حسب مدد العينات الفعلية.
- اشتراط العملية وهوية البداية نفسيهما وقياسات مكتملة وعينتين صالحتين على الأقل لكل مرحلة. تمنع القدرة المجهولة أو المتغيرة المقارنة؛ وتظهر ملاحظات للقياسات القصيرة والتوزيع غير المستقر واختلاف المدد.

لا يثبت انخفاض استخدام المعالج زيادة FPS أو تحسن زمن الإطار؛ هذه القياسات غير متاحة في هذا الإصدار. القراءة فقط والتأكيد والاستعادة تبقى كما هي. يدعم تحديد العمليات المتعدد من الإصدار السابق؛ ويسجل المختبر العملية الأولى المحددة فقط. Linux: x86_64 وglibc 2.35+ ومتصفح مثبت. قيود Windows وبيانات X3D غير المؤكدة تظل واضحة.

## English

- Default to process CPU share of all visible online logical CPUs, while retaining traditional per-CPU totals. 800% represents 8 logical CPU equivalents, or 50% on a 16-online-logical-CPU device.
- Add before/after recording controls, automatic difference tables, elapsed-time-aligned curves and comparison export in Performance Lab.
- Compare average/peak utilization, memory, thread counts and observed affinity. Weight averages by actual sample intervals.
- Require the same PID/start identity, completed recordings and two valid CPU deltas per phase. Unknown/changed capacity blocks comparison; short recordings, unstable masks and unequal durations are disclosed.

Lower CPU activity does not establish higher FPS or better frame times; those metrics remain unavailable. Read-only, confirmation and restoration safeguards are retained. Multiple-process selection remains available; the lab records the first selected process only. Linux requires x86_64, glibc 2.35+ and an installed browser. Existing Windows restrictions and unverified X3D states remain explicit.

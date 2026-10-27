<p align="center"><img src="site/assets/brand-logo.png" alt="شعار HalawaCore" width="120"></p>

# HalawaCore

## العربية

**افهم معالجك. قِس تجربتك. احتفظ بخيار العودة.**

HalawaCore برنامج محلي مفتوح المصدر لتحليل طوبولوجيا المعالج، وفهم الأنوية الفعلية وخيوط المعالجة والكاش المشترك، وفحص العمليات وتجربة توزيعها على الأنوية مع المعاينة والتأكيد والاستعادة. الواجهة والموقع متاحان بالعربية والإنجليزية، مع شعار **M** ومظهر أحمر وأسود.

- [الموقع التعريفي](https://mooodegrx-nah.github.io/HalawaCore/?lang=ar)
- [صفحة البرنامج والتحميل](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=ar)
- [أحدث إصدار وملفات التحميل](https://github.com/MOOODEGRX-nah/HalawaCore/releases/latest)

### التحميل والاستخدام للمرة الأولى

1. افتح صفحة البرنامج واضغط تحميل النسخة المناسبة لنظامك. يظهر دليل متدرج يشرح الملف والتشغيل والاستخدام قبل بدء التنزيل.
2. على **Windows 10 أو 11 بمعمارية x64**: فك ضغط الملف وافتح `HalawaCore.exe`.
3. على **Linux بمعمارية x64**: فك ضغط الأرشيف وافتح ملف `HalawaCore`. إذا طلب مدير الملفات السماح بالتنفيذ، راجع مصدر الملف ثم امنحه إذن التنفيذ. لا تشغّله بصلاحيات الجذر.
4. تفتح واجهة البرنامج المحلية تلقائيًا في المتصفح. اختر العربية أو الإنجليزية من محدد اللغة؛ يُحفظ الاختيار محليًا للتشغيل القادم.
5. ابدأ بوضع القراءة فقط: افحص لوحة التحكم وخريطة الأنوية، ثم اختر العملية الفعلية وسجّل قياسًا أساسيًا قبل أي تجربة.
6. تجد **المساعدة والدليل** تحت **الإعدادات**، وعلامة **؟** بجانب الأقسام لشرح وظيفتها ومتى تستخدمها وحدودها. تستطيع إعادة فتح دليل البداية في أي وقت.
7. لتجربة توزيع الأنوية، فعّل التجارب عمدًا، وراجع المعاينة والمهام المتأثرة ثم أكّد. أوقف التسجيل واستعد جميع التجارب قبل الضغط على **إغلاق HalawaCore**. إغلاق تبويب المتصفح وحده لا يوقف البرنامج المحلي.

النسخ التنفيذية تتضمن بيئة التشغيل؛ لا تحتاج تثبيت بايثون أو كتابة أوامر. الموقع يقدّم التعريف والتحميل، بينما يعمل تحليل جهازك والتحكم الاختياري في العمليات داخل البرنامج المحلي. لا تُرفع بيانات العتاد أو العمليات تلقائيًا.

### أوامر Linux: CachyOS وFedora وتوزيعات أخرى

حمّل `HalawaCore-Linux-x64.tar.gz` من صفحة الإصدارات، ثم افتح الطرفية داخل المجلد الذي يحتوي الملف. لا تحتاج تثبيت بايثون للنسخة المحمولة. الأوامر التالية تفك الأرشيف داخل مجلدك الشخصي وتمنح إذن التنفيذ ثم تشغّل البرنامج:

```sh
mkdir -p "$HOME/Applications/HalawaCore" &&
tar -xzf "./HalawaCore-Linux-x64.tar.gz" -C "$HOME/Applications/HalawaCore" &&
chmod u+x "$HOME/Applications/HalawaCore/HalawaCore" &&
"$HOME/Applications/HalawaCore/HalawaCore"
```

للتشغيل لاحقًا:

```sh
"$HOME/Applications/HalawaCore/HalawaCore"
```

إذا كانت أدوات فك الضغط أو فتح المتصفح ناقصة فقط، اختر أمر توزيعتك ثم أعد الخطوة الأولى. تُستخدم صلاحيات الإدارة لتثبيت الأدوات فقط؛ لا تشغّل HalawaCore بصلاحيات الجذر.

| التوزيعة | تثبيت الأدوات عند الحاجة |
| --- | --- |
| CachyOS / Arch Linux | `sudo pacman -S --needed tar gzip xdg-utils` |
| Fedora Workstation / KDE (DNF) | `sudo dnf install tar gzip xdg-utils` |
| Ubuntu / Debian / Linux Mint | `sudo apt update && sudo apt install tar gzip xdg-utils` |
| openSUSE (Zypper) | `sudo zypper install tar gzip xdg-utils` |

تتطلب النسخة معمارية `x86_64` ومكتبة `glibc 2.35` أو أحدث ومتصفحًا مثبتًا. أنظمة Fedora Atomic وopenSUSE MicroOS وتوزيعات Alpine تحتاج إرشادات منفصلة؛ أوامر تثبيت الحزم أعلاه للأنظمة التقليدية. راجع [دليل Linux المفصل](docs/LINUX-START.md) أو [الدليل التفاعلي مع أزرار النسخ](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=ar#linux-commands).

### الخصائص

- عرض الأنوية الفعلية، وخيوط المعالجة الشقيقة، والمقابس، وعقد الذاكرة ومجموعات كاش المستوى الثالث اعتمادًا على معلومات نظام التشغيل.
- تحليل محافظ لمعالجات AMD المزودة بتقنية X3D؛ تبقى مجموعات الكاش منفصلة عن معرّفات الشرائح، وتظهر المعلومات غير المؤكدة بوضوح بدل تخمينها.
- اكتشاف معلومات الأنوية المفضلة وتفضيل الكاش أو التردد على Linux عندما يكشفها النظام، وعرضها للقراءة فقط.
- فحص العمليات والخيوط وهوياتها وعلاقاتها المرصودة، بما فيها عمليات Steam وProton وWine المتاحة. لا يُفترض أن إعدادات التشغيل متطابقة بين بيئات التوافق.
- تجارب اختيارية للكاش أو التردد أو المهام الخلفية أو عقد الذاكرة حيث تتوفر أدلة كافية؛ ويمكن الاحتفاظ بتوزيع المجدول الافتراضي.
- معاينة نطاق كل تجربة، وتأكيد التطبيق، وقراءة النتيجة من النظام، واستعادة التوزيع الأصلي بعد التحقق من هوية المهمة.
- قياسات فعلية لاستخدام المعالج وذاكرة العملية والخيوط، وتسجيل خط أساس وتجربة واستعادة، وملفات إعدادات لا تُطبق تلقائيًا.
- واجهة عربية من اليمين إلى اليسار وواجهة إنجليزية من اليسار إلى اليمين، ودليل قابل للبحث وشروح سياقية. تبقى أسماء العمليات ومعرّفات المعالجات والأدلة الخام كما هي.

قد تستفيد بعض الألعاب من الكاش الإضافي، بينما تستفيد مهام أخرى من التردد أو جميع الأنوية. تقييد الأنوية قد يحسّن الأداء أو يقلّله؛ لا توجد زيادة أداء أو إطارات مضمونة.

### التوافق والحدود

| النظام أو الحالة | الدعم المتاح |
| --- | --- |
| Linux بمعمارية x64 | تحليل طوبولوجيا النواة، والعمليات والقياسات، وتجارب توزيع قابلة للاستعادة؛ ومعلومات X3D والأنوية المفضلة عند توفرها. |
| Windows 10 و11 بمعمارية x64 | دعم أولي أصلي للطوبولوجيا والكاش وملكية العمليات وهويات الخيوط، وتجارب توزيع لكل خيط على الأنظمة ذات مجموعة المعالجات الواحدة. |
| مجموعات معالجات متعددة على Windows | التحليل للقراءة فقط؛ تعديل التوزيع معطّل إلى حين دعم استعادة الحالة عبر جميع المجموعات. |
| مجموعات المعالجات الصريحة على Windows | تبقى المهمة للقراءة فقط، وكذلك عند غياب واجهات الاستعلام اللازمة. |
| معلومات عتاد ناقصة أو أنوية مقيّدة | لا تُختلق بيانات؛ تبقى المجموعات غير مؤكدة والتجارب غير الآمنة معطّلة. |

على Windows، المهمة الافتراضية هي أقدم خيط ما زال موجودًا؛ لا يُفترض تطابق رقم العملية مع رقم الخيط. ترميز المعالج الداخلي هو `group * 64 + processor index`، والعرض هو `G#:P#`؛ وهذه ليست معرّفات مجموعات المعالجات الخاصة بواجهة النظام.

واجهات Linux الخاصة بالأنوية المفضلة وبرنامج تشغيل كاش X3D ليست واجهات Windows؛ لا يُخمّن تفضيل المجدول على Windows. تتطلب نسخ Linux المنشورة مكتبة النظام `glibc 2.35` أو أحدث؛ وقد تتطلب النسخ المبنية محليًا إصدارًا أحدث.

اختبارات Linux تشمل تشغيلًا فعليًا. تُبنى نسخة Windows وتُختبر في بيئة Windows الأصلية على خوادم التكامل المستمر، مع تقرير تحقق مرفق. لا تمثل هذه النتائج اختبار عتاد فعليًا لكل من Windows 10 و11. اختبارات X3D تستخدم بيانات اصطناعية؛ لم يُجرَ تحقق أداء على معالج X3D فعلي.

لا يغيّر البرنامج إعدادات اللوحة الأم أو برامج تشغيل المعالج أو خيارات النواة أو وضع الجدولة على مستوى النظام تلقائيًا. لا يضمن الاستعادة بعد الانهيار أو الإنهاء القسري، ولا يتتبع كل عملية فرعية جديدة باستمرار. استعد التجارب قبل إغلاقه، وراجع ملفات التصدير قبل مشاركتها.

### للمطورين

تستخدم عملية النشر بايثون 3.13. لإنشاء بيئة تطوير على Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python -m pytest -q
.venv/bin/python desktop.py
```

على Windows استخدم المسار `.venv\Scripts\python.exe`. ابنِ الملف التنفيذي على نظامه المستهدف:

```sh
python build_desktop.py
```

يوجد الملف الناتج داخل `dist/desktop/`. يفحص الخيار `desktop.py --self-test` الخادم الفعلي والطوبولوجيا، وينشئ عملية اختبار مؤقتة يملكها البرنامج لفحص التطبيق والاستعادة حيث يكون ذلك مدعومًا؛ ولا يغيّر العمليات الموجودة مسبقًا.

تنشر آلية الموقع مجلد `site/` على صفحات المستودع. تختبر آلية الإصدارات نسختي Windows وLinux وتبنيهما قبل نشر رقم `VERSION` كإصدار مستقل. تستخدم صفحة التحميل أحدث إصدار فعلي، ولا تعرض رابطًا مباشرًا إلا عند وجود الملف المناسب.

التوثيق التقني: [تفاصيل Linux](docs/LINUX.md)، [واجهة البرمجة](docs/API.md)، [الأمان](SECURITY.md)، [التحقق](docs/VALIDATION.md)، [المساهمة](CONTRIBUTING.md). الترخيص: [MIT](LICENSE).

---

## English

**Understand your processor. Measure your experiment. Keep a way back.**

HalawaCore is a local, open-source CPU topology and affinity analyzer. Inspect physical cores, SMT siblings and shared caches, explore processes, and run optional affinity experiments with preview, confirmation and restoration. The app and website support Arabic and English, with the **M** logo and a red-and-black theme.

- [Product website](https://mooodegrx-nah.github.io/HalawaCore/?lang=en)
- [Program and downloads](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=en)
- [Latest release and downloads](https://github.com/MOOODEGRX-nah/HalawaCore/releases/latest)

### Download and first use

1. Open the program page and choose your operating system. A step-by-step guide explains the download, startup and first use before downloading.
2. **Windows 10 / 11 x64:** extract the ZIP and open `HalawaCore.exe`.
3. **Linux x64:** extract the archive and open `HalawaCore`. If your file manager requires execution permission, review the file's source before allowing it. Do not run as root.
4. Your browser opens the local interface automatically. Choose Arabic or English from the language selector; the app saves your choice locally for future launches.
5. Start in read-only mode: explore the dashboard and core map, select the actual process, then record a baseline before experimenting.
6. Open **Help & Guide** below **Settings**, or use the **?** buttons beside sections to learn their purpose, appropriate use and limits. The welcome guide can be reopened at any time.
7. For an optional affinity experiment, deliberately enable experiments, review the affected tasks and confirm the preview. Stop recording and restore all experiments before clicking **Quit HalawaCore**. Closing the browser tab alone does not stop the local backend.

Executables bundle the runtime; users do not need Python or terminal commands. The website provides information and downloads. Hardware analysis and optional process controls run in the local application. Hardware and process data is not uploaded automatically.

### Linux commands: CachyOS, Fedora and other distributions

Download `HalawaCore-Linux-x64.tar.gz` from Releases, then open a terminal in the folder containing it. The portable build includes Python. These commands extract into your home folder, grant execution permission and launch:

```sh
mkdir -p "$HOME/Applications/HalawaCore" &&
tar -xzf "./HalawaCore-Linux-x64.tar.gz" -C "$HOME/Applications/HalawaCore" &&
chmod u+x "$HOME/Applications/HalawaCore/HalawaCore" &&
"$HOME/Applications/HalawaCore/HalawaCore"
```

To launch again later:

```sh
"$HOME/Applications/HalawaCore/HalawaCore"
```

Only if archive tools or browser integration are missing, use the command for your distribution, then repeat step 1. Administrator privileges are only for installing tools; never run HalawaCore as root.

| Distribution | Install tools only when needed |
| --- | --- |
| CachyOS / Arch Linux | `sudo pacman -S --needed tar gzip xdg-utils` |
| Fedora Workstation / KDE (DNF) | `sudo dnf install tar gzip xdg-utils` |
| Ubuntu / Debian / Linux Mint | `sudo apt update && sudo apt install tar gzip xdg-utils` |
| openSUSE (Zypper) | `sudo zypper install tar gzip xdg-utils` |

The executable requires `x86_64`, `glibc 2.35+` and an installed browser. Fedora Atomic, openSUSE MicroOS and Alpine need separate guidance; package commands above target conventional mutable systems. See the [detailed Linux guide](docs/LINUX-START.md) or [interactive guide with copy buttons](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=en#linux-commands).

### Features

- Physical cores, SMT siblings, packages, NUMA nodes and shared L3 domains from operating-system evidence.
- Conservative AMD X3D detection. Cache domains remain separate from die/CCD identifiers, and insufficient evidence stays explicitly unverified.
- Read-only Linux CPPC preferred-core and X3D cache/frequency preference discovery when exposed by the kernel.
- Process/thread identities, observed relationships and accessible Steam, Proton and Wine processes. Launch-time topology configuration is distinct from process affinity and depends on verified integration support.
- Optional cache, frequency, background and NUMA experiments where supported, plus preserved scheduler-default placement.
- Exact task previews, explicit confirmation, kernel read-back and identity-validated restoration of original affinity.
- Actual CPU utilization, process memory and thread measurements; baseline/experiment/restored recordings and profiles that never apply automatically.
- Arabic RTL and English LTR layouts, a searchable feature guide and contextual explanations. Process names, CPU IDs and raw evidence remain unchanged.

Some games benefit from additional cache; other workloads benefit from frequency or all available cores. Restricting affinity can improve or reduce performance. No performance or FPS improvement is guaranteed.

### Compatibility and limits

| Platform or condition | Available support |
| --- | --- |
| Linux x64 | Kernel topology, processes, measurements and reversible task affinity; CPPC/X3D information when exposed. |
| Windows 10 / 11 x64 | Initial native topology/cache, SID ownership, FILETIME identities and reversible per-thread affinity on single-group systems. |
| Windows multiple processor groups | Topology analysis only; mutation is disabled until complete cross-group state restoration is supported. |
| Explicit Windows CPU Sets | Target remains read-only, including when required CPU Set query interfaces are unavailable. |
| Missing hardware data or restricted CPUs | No fabricated topology; unknown groups stay unverified and unsafe experiments are disabled. |

On Windows, the default task is the oldest surviving thread, without assuming that PID equals TID or that the original primary thread survives. Internal CPU IDs use `group * 64 + processor index`; display labels use `G#:P#`. These are not Windows CPU Set IDs.

Linux CPPC and `amd_x3d_vcache` are not Windows interfaces. Windows scheduler preference is not guessed. Published Linux releases require `glibc 2.35+`; local builds may require a newer version.

Linux validation includes actual runtime checks. Windows executables are built and checked in native Windows CI with an included verification report. This is not physical Windows 10/11 desktop hardware validation. X3D coverage uses synthetic fixtures; physical X3D performance testing has not been performed.

HalawaCore does not automatically modify BIOS settings, CPU drivers, kernel parameters or system-wide scheduling modes. Crash/SIGKILL recovery and continuous tracking of every new child process are not implemented. Restore experiments before closing the app, and review exported files before sharing them.

### Development and builds

The release workflow uses Python 3.13. On Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python -m pytest -q
.venv/bin/python desktop.py
```

On Windows, use `.venv\Scripts\python.exe`. Build on the target OS:

```sh
python build_desktop.py
```

The executable is written to `dist/desktop/`. `desktop.py --self-test` starts the actual backend, queries topology and creates its own disposable child to verify affinity/restoration when supported. It never modifies pre-existing programs.

The Pages workflow deploys `site/`. The release workflow tests and builds Windows and Linux executables before publishing the version in `VERSION` as a separate release. The download page queries the latest real release and enables direct links only when matching assets exist.

Technical documentation: [Linux details](docs/LINUX.md), [API](docs/API.md), [security](SECURITY.md), [validation](docs/VALIDATION.md), [contributing](CONTRIBUTING.md). License: [MIT](LICENSE).

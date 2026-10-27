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

### التحديث من داخل البرنامج

بدءًا من **0.6.0**، افتح **الإعدادات ← تحديث البرنامج**: تحقق من وجود تحديث، ثم نزّله وتحقق منه، وراجع التغييرات وأكّد التثبيت. أعد التشغيل عند الطلب. لا توجد فحوص تلقائية في الخلفية، ولا تُرسل بيانات المعالج أو العمليات إلى GitHub.

- **CachyOS / Arch:** يستخدم التحديث حزمة Arch الرسمية للإصدار عبر `pacman` ونافذة صلاحيات النظام. يبقى البرنامج نفسه بحسابك العادي؛ إلغاء الصلاحيات يعرض حالة فشل واضحة.
- **Linux وWindows بنسخة محمولة:** يُحدّث الملف التنفيذي في مجلد قابل للكتابة، وتُحفظ نسخة `.previous` احتياطية. على Windows يغلق مساعد التحديث النسخة القديمة بعد موافقتك ويعيد فتح الجديدة؛ لا يقتل عمليات أخرى.
- أوقف التسجيل واستعد التجارب أولًا، وصدّر القياسات قبل إعادة التشغيل. تبقى ملفات تفضيلات اللغة والملفات المحفوظة في مجلد البيانات.
- النسخ الأقدم من 0.6.0 تحتاج تثبيت هذا الإصدار مرة واحدة لتظهر أزرار التحديث. نسخ المصدر والتثبيتات التي يديرها مدير حزم آخر تعرض صفحة الإصدار الرسمية بدل استبدال ملفاتها.

يُستخدم إصدار مستقر من مستودع المشروع الثابت فقط، مع تحقق SHA-256 المنشور على GitHub وفحص رقم إصدار الملف. هذا ليس توقيعًا رقميًا مستقلًا. لا يغيّر المحدّث BIOS أو برامج تشغيل المعالج أو أوضاع الجدولة.

### مقارنة قبل التعديل وبعده وعرض استهلاك المعالج

في **مختبر الأداء**، سجّل قبل التعديل ثم أوقف التسجيل، وغيّر التوزيع من المخطط باختيارك، ثم سجّل المشهد والإعدادات نفسها بعد التعديل وأوقف التسجيل. يظهر جدول **قبل / بعد / الفرق** تلقائيًا، مع منحنيين بمحاذاة الزمن، ومتوسط الاستهلاك وذروته والذاكرة والخيوط والأنوية المرصودة. يُفضّل 30 ثانية على الأقل لكل مرحلة. المقارنة لنفس العملية وهوية بدايتها فقط؛ بعد إعادة تشغيل اللعبة تحتاج قياسًا أساسيًا جديدًا. صدّر القياسات قبل إغلاق جلسة البرنامج.

تعرض قائمة العمليات افتراضيًا النسبة من إجمالي المعالجات المنطقية المتصلة الظاهرة للنظام. تعادل **800%** في العرض التقليدي استخدام **8 معالجات منطقية مكافئة**؛ ومع 16 معالجًا منطقيًا متصلًا تعادل **50% من الجهاز**. يمكن اختيار العرض التقليدي أيضًا. لا يقيس ذلك عدد الأنوية الفعلية، ولا يعدل النسبة حسب حصص الحاويات أو حدود التوزيع. راجع [شرح psutil الرسمي](https://psutil.io/faq/#can-process-cpu-percent-return-a-value-higher-than-100).

تُعرض فروق النسب بالنقاط المئوية؛ انخفاض استخدام المعالج وحده لا يثبت زيادة FPS أو تحسن زمن الإطار. لا يجمع هذا الإصدار FPS أو زمن الإطار. تسميات قبل وبعد يدوية، وتغيّر القدرة المتصلة يمنع المقارنة؛ وتظهر تحذيرات إذا تغيّر التوزيع أثناء التسجيل أو اختلفت مدد القياس كثيرًا.

### التثبيت بمدير الحزم على CachyOS / Arch

جهّزنا حزمة `halawacore-bin` لتثبيت البرنامج والاعتماديات واختصار قائمة التطبيقات في مسارات النظام المعتادة. **الحزمة غير منشورة في AUR بعد**؛ يحتاج النشر حساب AUR ومفتاح SSH، ولا يكفي رفع الملفات إلى GitHub. يتضمن [دليل حزمة Arch](docs/ARCH-PACKAGE.md) طريقة البناء والتثبيت الآن وخطوات إتاحتها لاحقًا عبر `paru`. Fedora يحتاج حزمة RPM منفصلة؛ دليل التنزيل المحمول متاح أدناه.

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

إذا لم يُفتح المتصفح تلقائيًا، يطبع الإصدار 0.3.2 والأحدث رابط الواجهة المحلية في الطرفية. ويمكن بدء البرنامج يدويًا بهذا الأمر، ثم نسخ الرابط الظاهر إلى المتصفح مع إبقاء الطرفية مفتوحة:

```sh
"$HOME/Applications/HalawaCore/HalawaCore" --no-browser
```

إذا كانت أدوات فك الضغط أو فتح المتصفح ناقصة فقط، اختر أمر توزيعتك ثم أعد الخطوة الأولى. تُستخدم صلاحيات الإدارة لتثبيت الأدوات فقط؛ لا تشغّل HalawaCore بصلاحيات الجذر.

| التوزيعة | تثبيت الأدوات عند الحاجة |
| --- | --- |
| CachyOS / Arch Linux | `sudo pacman -S --needed tar gzip xdg-utils` |
| Fedora Workstation / KDE (DNF) | `sudo dnf install tar gzip xdg-utils` |
| Ubuntu / Debian / Linux Mint | `sudo apt update && sudo apt install tar gzip xdg-utils` |
| openSUSE (Zypper) | `sudo zypper install tar gzip xdg-utils` |

تتطلب النسخة معمارية `x86_64` ومكتبة `glibc 2.35` أو أحدث ومتصفحًا مثبتًا. أنظمة Fedora Atomic وopenSUSE MicroOS وتوزيعات Alpine تحتاج إرشادات منفصلة؛ أوامر تثبيت الحزم أعلاه للأنظمة التقليدية. راجع [دليل Linux المفصل](docs/LINUX-START.md) أو [الدليل التفاعلي مع أزرار النسخ](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=ar&guide=linux).

### الخصائص

- تحديد حتى 32 عملية من قائمة التطبيقات، مع بقاء الاختيار عند البحث والتحديث، ثم معاينة وتطبيق مجموعة أنوية مشتركة على خيوطها الحالية واستعادة التوزيع الأصلي لكل خيط. لا تُضاف عمليات جديدة أو تطبيقات مشابهة الاسم تلقائيًا.

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

### In-app updates

Starting with **0.6.0**, open **Settings → Application updates**: check, download and verify, review release notes, explicitly install, and restart when prompted. No background checks run automatically, and hardware/process data is not sent to GitHub.

- **CachyOS / Arch:** install the release's verified Arch package through `pacman` and the system authorization dialog. HalawaCore stays unprivileged; cancelling authorization reports a clear failed state.
- **Portable Linux / Windows:** replace the executable in a writable installation folder and retain a `.previous` backup. On Windows a staged helper waits for the old app to exit and reopens the updated app; it never terminates unrelated processes.
- Stop recording, restore experiments and export measurements first. Stored language preferences and saved profiles remain in the data folder.
- Versions older than 0.6.0 need a one-time installation of this release to obtain the updater. Source checkouts and installations owned by another package manager link to the official release instead of overwriting managed files.

Only stable releases from the fixed project repository are selected. GitHub's SHA-256 digest and the executable version are checked; this is not an independent digital signature. BIOS, CPU drivers and scheduler modes are not modified.

### Before/after comparison and CPU utilization display

In **Performance Lab**, record before, stop, deliberately change affinity in the planner, then repeat the same scene/settings, record after and stop. The **Before / after / difference** table appears automatically with elapsed-time-aligned curves, average/peak CPU activity, memory, threads and observed masks. Prefer at least 30 seconds per phase. Comparison requires the same PID and start identity; record a new baseline if the game restarts. Export measurements before closing the backend session.

The process list defaults to a share of all online logical CPUs visible to the OS. Conventional **800%** represents **8 logical CPU equivalents**; on a device with 16 online logical CPUs it is **50% device share**. The conventional view remains selectable. This is not a physical-core count and is not adjusted for container quotas or affinity limits. See the [official psutil explanation](https://psutil.io/faq/#can-process-cpu-percent-return-a-value-higher-than-100).

Differences in percentages are percentage points; lower CPU activity alone does not prove higher FPS or better frame times. This release does not collect FPS or frame times. Phase labels are manual. Changed online capacity blocks comparison; unstable affinity and substantially different durations produce warnings.

### Package-manager installation on CachyOS / Arch

The `halawacore-bin` recipe installs the application, dependencies and menu entry into standard system locations. **It has not been published to AUR.** Publication requires an AUR account and SSH key; GitHub hosting alone is insufficient. The [Arch package guide](docs/ARCH-PACKAGE.md) explains building/installing now and publishing for future `paru` installs. Fedora needs separate RPM packaging; portable-download instructions remain below.

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

Version 0.3.2 and later print the local interface URL even if automatic browser launch fails. For manual startup, run this command, copy the printed URL into your browser and keep the terminal open:

```sh
"$HOME/Applications/HalawaCore/HalawaCore" --no-browser
```

Only if archive tools or browser integration are missing, use the command for your distribution, then repeat step 1. Administrator privileges are only for installing tools; never run HalawaCore as root.

| Distribution | Install tools only when needed |
| --- | --- |
| CachyOS / Arch Linux | `sudo pacman -S --needed tar gzip xdg-utils` |
| Fedora Workstation / KDE (DNF) | `sudo dnf install tar gzip xdg-utils` |
| Ubuntu / Debian / Linux Mint | `sudo apt update && sudo apt install tar gzip xdg-utils` |
| openSUSE (Zypper) | `sudo zypper install tar gzip xdg-utils` |

The executable requires `x86_64`, `glibc 2.35+` and an installed browser. Fedora Atomic, openSUSE MicroOS and Alpine need separate guidance; package commands above target conventional mutable systems. See the [detailed Linux guide](docs/LINUX-START.md) or [interactive guide with copy buttons](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=en&guide=linux).

### Features

- Select up to 32 running processes across search and refresh, preview one shared CPU set for their existing threads, and restore each thread's original mask. New processes and similar names are never included automatically.

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

# HalawaCore — Arch / CachyOS

## العربية

### التحديث من داخل البرنامج

بعد تثبيت 0.6.1 مرة واحدة، استخدم **الإعدادات ← تحديث البرنامج** للتحديثات اللاحقة. يتحقق البرنامج من حزمة الإصدار الرسمية ويطلب موافقتك ونافذة صلاحيات النظام ثم يستخدم pacman؛ لا تحتاج تكرار أوامر البناء. يتوفر الملف الجاهز `HalawaCore-Arch-x64.pkg.tar.zst` ضمن الإصدارات. يبقى النشر في AUR منفصلًا عن هذا المسار.

### حالة الحزمة

حزمة `halawacore-bin` جاهزة للبناء من [ملفات التغليف](../packaging/arch/halawacore-bin/). **لم تُنشر في AUR بعد**؛ وجودها في GitHub لا يجعل `paru` يجدها. النشر يحتاج حساب AUR ومفتاح SSH مرتبطًا به. لا يتوفر حاليًا أمر تثبيت من AUR للمستخدمين.

بعد نشر الحزمة في AUR والتحقق من صفحة الحزمة، سيكون التثبيت:

```sh
paru -S halawacore-bin
```

راجع ملف `PKGBUILD` عندما يعرضه `paru`. يدير مدير الحزم الملفات والاعتماديات والاختصار؛ لا تحتاج فك الأرشيف أو ضبط صلاحية التنفيذ يدويًا. بعد ذلك افتح **HalawaCore** من قائمة التطبيقات، أو شغّل:

```sh
halawacore
```

يستخدم تحديث النظام المعتاد `paru -Syu` الإصدارات الجديدة بعد تحديث الحزمة في AUR. للإزالة:

```sh
sudo pacman -R halawacore-bin
```

لا يحذف هذا الأمر إعداداتك الشخصية. Fedora لا يستخدم AUR أو `paru`؛ يبقى دليل النسخة المحمولة متاحًا له إلى أن تُجهّز حزمة RPM منفصلة.

### البناء والتثبيت قبل النشر في AUR

يتطلب البناء `base-devel` و`git` على Arch/CachyOS. نفّذ `makepkg` بحسابك العادي، ثم يطلب تثبيت الاعتماديات والحزمة صلاحيات الإدارة عند الحاجة:

```sh
git clone https://github.com/MOOODEGRX-nah/HalawaCore.git
cd HalawaCore/packaging/arch/halawacore-bin
less PKGBUILD
makepkg -si
```

إذا كانت لديك حزمة `.pkg.tar.zst` مبنية مسبقًا، افتح الطرفية في مجلدها ثم ثبّتها مباشرةً:

```sh
sudo pacman -U ./halawacore-bin-0.6.1-1-x86_64.pkg.tar.zst
```

هذه الطريقة المحلية لا تنشئ مصدر تحديثات عبر AUR. لا تشغّل `halawacore` باستخدام `sudo`.

### المسارات وما يفعله التثبيت

| العنصر | المسار |
| --- | --- |
| البرنامج الجاهز | `/opt/halawacore/HalawaCore` |
| أمر الطرفية | `/usr/bin/halawacore` |
| اختصار قائمة التطبيقات | `/usr/share/applications/halawacore.desktop` |
| الشعار | `/usr/share/icons/hicolor/scalable/apps/halawacore.svg` |
| الإعدادات والسجلات | `${XDG_DATA_HOME:-$HOME/.local/share}/halawacore` |

الحزمة تتحقق من بصمة SHA-256 للنسخة الرسمية 0.6.1، وتتطلب `x86_64` و`glibc 2.35+` ومتصفحًا مثبتًا. لا تعدّل BIOS أو إعدادات المعالج أو الإقلاع، ولا تضيف خدمة أو تشغيلًا تلقائيًا. يظل البرنامج يبدأ للقراءة فقط وتحتاج تجارب التوزيع إلى التأكيد. لا تستبدل الحزمة النسخة المحمولة الموجودة في `~/Applications/HalawaCore`؛ بعد التثبيت افتح اختصار القائمة أو الأمر الجديد لتجنّب تشغيل نسخة قديمة.

### النشر لأول مرة — لمالك المشروع

1. أنشئ [حساب AUR](https://aur.archlinux.org/register). حساب GitHub لا يكفي.
2. أنشئ مفتاح SSH مخصصًا واربط **المفتاح العام فقط** بالحساب وفق [تعليمات Arch الرسمية](https://wiki.archlinux.org/title/AUR_submission_guidelines#Authentication). لا تشارك المفتاح الخاص في المحادثة أو GitHub.
3. تحقّق من عدم وجود الحزمة في AUR أو مستودعات Arch الرسمية قبل النشر. اضبط اسم المؤلف وعنوان التواصل العام الذي تريد نشره في سجل Git، وحدّث سطر Maintainer إذا رغبت بإضافة بريدك العام.
4. استنسخ مستودع AUR المخصص: `ssh://aur@aur.archlinux.org/halawacore-bin.git`، ثم انسخ إليه `PKGBUILD` و`.SRCINFO` و`halawacore.desktop` و`halawacore.svg` و`LICENSE` و`.gitignore` فقط. لا ترفع الملف التنفيذي أو الحزمة المبنية أو مجلدي `src/` و`pkg/`.
5. داخل مستودع AUR أعد توليد البيانات بالأمر `makepkg --printsrcinfo > .SRCINFO`، ثم احفظ الملفات في commit وادفع فرع `master` باستخدام مفتاح الحساب. لا تستبدل سجلًا موجودًا بالقوة.
6. تحقّق من صفحة الحزمة ونجاح تثبيت نظيف عبر `paru -S halawacore-bin` قبل الإعلان أن الأمر متاح.

لتحديث الحزمة: انشر إصدار GitHub أولًا، ثم عدّل `pkgver` وبصمة الأرشيف وأعد `pkgrel=1`، وابنِ واختبر وأعد توليد `.SRCINFO`. إذا تغيّرت ملفات التغليف فقط لنفس الإصدار، ارفع `pkgrel`. لا تستخدم `SKIP` للتحقق من الأرشيف.

---

## English

### In-app updates

After a one-time installation of 0.6.1, use **Settings → Application updates** for later updates. HalawaCore verifies the official release package, asks for confirmation/system authorization and uses pacman; repeating build commands is unnecessary. Releases include `HalawaCore-Arch-x64.pkg.tar.zst`. AUR publication remains separate.

### Package status

The `halawacore-bin` [packaging files](../packaging/arch/halawacore-bin/) are ready to build. **The package has not been published to AUR.** GitHub hosting alone does not make a package discoverable by `paru`. Publishing requires an AUR account with an authorized SSH key. An AUR installation command is not currently available to users.

After publication and verification of the package page, installation will be:

```sh
paru -S halawacore-bin
```

Review the `PKGBUILD` shown by `paru`. The package manager installs dependencies, files and the application-menu entry; manual archive extraction and permission changes are unnecessary. Launch **HalawaCore** from your application menu, or run:

```sh
halawacore
```

Normal `paru -Syu` updates include new versions once the AUR recipe is updated. To uninstall:

```sh
sudo pacman -R halawacore-bin
```

This leaves personal settings intact. Fedora uses neither AUR nor `paru`; its portable download guide remains available until separate RPM packaging is prepared.

### Build and install before AUR publication

Build prerequisites are `base-devel` and `git` on Arch/CachyOS. Run `makepkg` as your normal user; dependency/package installation requests administrator access when needed:

```sh
git clone https://github.com/MOOODEGRX-nah/HalawaCore.git
cd HalawaCore/packaging/arch/halawacore-bin
less PKGBUILD
makepkg -si
```

For an already built `.pkg.tar.zst`, open a terminal in its folder and install directly:

```sh
sudo pacman -U ./halawacore-bin-0.6.1-1-x86_64.pkg.tar.zst
```

A local installation does not establish an AUR update source. Never run `halawacore` with `sudo`.

### Installed paths and behavior

| Item | Path |
| --- | --- |
| Bundled executable | `/opt/halawacore/HalawaCore` |
| Terminal command | `/usr/bin/halawacore` |
| Application-menu entry | `/usr/share/applications/halawacore.desktop` |
| Logo | `/usr/share/icons/hicolor/scalable/apps/halawacore.svg` |
| Personal settings and logs | `${XDG_DATA_HOME:-$HOME/.local/share}/halawacore` |

The recipe verifies the official 0.6.1 release SHA-256. It requires `x86_64`, `glibc 2.35+` and an installed browser. It does not change BIOS, CPU or boot settings, or add a service or automatic startup. The app still starts read-only and affinity experiments require confirmation. The package does not replace a portable copy in `~/Applications/HalawaCore`; use the menu entry or new command after installation to avoid launching an old copy.

### First publication — project maintainer

1. Register an [AUR account](https://aur.archlinux.org/register). A GitHub account is insufficient.
2. Create a dedicated SSH key and authorize **only the public key** using the [official Arch instructions](https://wiki.archlinux.org/title/AUR_submission_guidelines#Authentication). Do not share the private key in chat or GitHub.
3. Check AUR and official Arch repositories for an existing package before publishing. Configure the public Git author name/contact you want to publish, and optionally update the Maintainer comment with your public email.
4. Clone `ssh://aur@aur.archlinux.org/halawacore-bin.git`. Copy only `PKGBUILD`, `.SRCINFO`, `halawacore.desktop`, `halawacore.svg`, `LICENSE` and `.gitignore` into it. Do not upload executables, built packages, `src/` or `pkg/`.
5. In the AUR checkout regenerate metadata with `makepkg --printsrcinfo > .SRCINFO`, commit the files, and push the `master` branch using the authorized key. Do not force-replace existing history.
6. Verify the package page and a clean `paru -S halawacore-bin` installation before announcing availability.

For updates, publish the GitHub release first, update `pkgver` and the archive checksum, reset `pkgrel=1`, build/test and regenerate `.SRCINFO`. For packaging-only changes at the same version, increment `pkgrel`. Never use `SKIP` for release-archive integrity.

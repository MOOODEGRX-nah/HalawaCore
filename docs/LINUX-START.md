# HalawaCore — Linux

## العربية

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

تتطلب النسخة معمارية `x86_64` ومكتبة `glibc 2.35` أو أحدث ومتصفحًا مثبتًا. أنظمة Fedora Atomic وopenSUSE MicroOS وتوزيعات Alpine تحتاج إرشادات منفصلة؛ أوامر تثبيت الحزم أعلاه للأنظمة التقليدية. راجع [دليل Linux المفصل](LINUX-START.md) أو [الدليل التفاعلي مع أزرار النسخ](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=ar#linux-commands).

#### التحقق قبل التشغيل

```sh
uname -m
getconf GNU_LIBC_VERSION
```

ينبغي أن تظهر `x86_64` وإصدار `glibc 2.35` أو أحدث. إذا اختلف اسم الأرشيف عند التنزيل، عدّل اسمه في أمر `tar`. خطأ عدم وجود الملف يعني عادة أن الطرفية في مجلد مختلف. عند استمرار خطأ الإذن بعد `chmod` قد يكون المسار مركّبًا بخيار `noexec`؛ اطلب المساعدة بدل تعطيل حماية النظام.

يفتح البرنامج واجهته تلقائيًا في المتصفح. اترك الطرفية مفتوحة، وأوقف التسجيل واستعد التجارب قبل الإغلاق. لا تدّعي هذه التعليمات اختبار كل إصدار من التوزيعات على عتاد فعلي.

مراجع مديري الحزم الرسمية:

- [CachyOS / Arch Linux](https://man.archlinux.org/man/pacman.8.en)
- [Fedora Workstation / KDE (DNF)](https://dnf5.readthedocs.io/en/latest/commands/install.8.html)
- [Ubuntu / Debian / Linux Mint](https://ubuntu.com/server/docs/how-to/software/package-management/)
- [openSUSE (Zypper)](https://doc.opensuse.org/documentation/tumbleweed/zypper/)

---

## English

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

The executable requires `x86_64`, `glibc 2.35+` and an installed browser. Fedora Atomic, openSUSE MicroOS and Alpine need separate guidance; package commands above target conventional mutable systems. See the [detailed Linux guide](LINUX-START.md) or [interactive guide with copy buttons](https://mooodegrx-nah.github.io/HalawaCore/app.html?lang=en#linux-commands).

#### Check before launching

```sh
uname -m
getconf GNU_LIBC_VERSION
```

Expect `x86_64` and `glibc 2.35+`. If your downloaded archive has a different name, adjust the `tar` command. A file-not-found error usually means the terminal is in a different folder. If permission is denied after `chmod`, the location may be mounted `noexec`; seek help instead of disabling system protections.

The app opens its browser interface automatically. Keep the terminal open, stop recording and restore experiments before closing. These instructions do not establish physical testing on every distribution release.

Official package-manager references:

- [CachyOS / Arch Linux](https://man.archlinux.org/man/pacman.8.en)
- [Fedora Workstation / KDE (DNF)](https://dnf5.readthedocs.io/en/latest/commands/install.8.html)
- [Ubuntu / Debian / Linux Mint](https://ubuntu.com/server/docs/how-to/software/package-management/)
- [openSUSE (Zypper)](https://doc.opensuse.org/documentation/tumbleweed/zypper/)

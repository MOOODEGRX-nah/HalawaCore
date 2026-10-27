# Validation — HalawaCore

## 0.6.0 explicit in-app updater — 2026-10-27

- 158 Linux/Python tests pass. Updater fixtures cover stable-version ordering, fixed addresses and mandatory digests, archive traversal/links, corrupted and changed files, backup/rollback, private windowed version probes, package authorization cancellation and fixed non-shell commands.
- API checks cover no network at startup/status, CSRF, forbidden URL fields, explicit confirmation, stale jobs, active recordings/unrestored records and mutation blocking while installing. No installed application or system package is changed by tests.
- Native bundled helper and CI package validation are recorded after publishing the immutable release.

## 0.5.0 measurement comparison and CPU display — 2026-10-27

- 132 Linux/Python tests pass. New coverage verifies 800% / 16 = 50%, sparse IDs, unavailable/invalid capacity, elapsed-interval weighting, zero baselines, signed percentage-point changes, process reuse/mismatch, phase ordering, incomplete samples, changed online capacity and descriptive warnings. Comparison API checks enforce local CSRF protection and leave affinity state unchanged.
- Source desktop self-test records and compares two real phases of an owned disposable child after its affinity is restored; process CPU share is verified without claiming a speed improvement.
- Browser checks use synthetic fixtures, verify both percentage modes (50% versus 800%), preserve the raw reading, and display matching before/after values, signed differences and aligned curves in Arabic and English. Screenshots contain synthetic measurements only. No user game is modified or benchmarked.
- Native 0.5.0 verification passed on both GitHub runners: 132 Linux tests, 54 Windows tests, both executable affinity/recording/comparison self-tests and the packaged Linux browser regression. Verified run: https://github.com/MOOODEGRX-nah/HalawaCore/actions/runs/40468281312
- The 0.5.0 Arch/CachyOS package was built with makepkg against the published SHA-256. The unchanged release payload passes its affinity/recording/comparison self-test and browser regression on the local CachyOS host. No system package was installed by this validation.

## 0.4.0 multiple-process affinity — 2026-10-27

- 109 Python tests pass, including unrelated explicit targets, per-thread CPU limits, read-only/confirmation gates, complete validation before writes, stale/reused identities, denied access, partial application and restoration of distinct masks. A real API integration changes only two owned disposable children, verifies restoration and leaves a third child untouched.
- JavaScript contracts verify selection identity reconciliation, shared CPU intersection, offline/unverified masks and Arabic/English controls. Browser checks use synthetic process/topology fixtures; no real user process is changed.
- Interface checks cover selection across search, refresh and language changes; removal of exited selections; common-mask and no-common-CPU states; exact three-task/two-process preview; read-only application blocking; and synthetic application/restoration.
- Native packaged self-tests now preview, apply, verify and individually restore two owned disposable children on supported systems. Physical Windows 10/11 and X3D hardware claims remain limited to the evidence described below.

Native 0.4.0 release verification passed on both GitHub runners: 109 Linux tests, 33 Windows tests, both executable two-child apply/verify/restore checks, and the packaged Linux browser regression. Verified run: https://github.com/MOOODEGRX-nah/HalawaCore/actions/runs/40462303334

The updated 0.4.0 Arch/CachyOS recipe was built with makepkg against the published SHA-256. Its executable is unchanged from the release payload and passes the two-child self-test and browser regression on the local CachyOS host. No system package was installed during this check.

## Arch/CachyOS packaging — 2026-10-27

- Built `halawacore-bin-0.3.2-1-x86_64.pkg.tar.zst` with the installed CachyOS `makepkg`, downloading the official immutable release URL and verifying all four SHA-256 entries. No package was installed on the host.
- Inspected package metadata and file lists with `pacman -Qip/-Qlp`; checked the `/usr/bin/halawacore` symlink, file permissions and the bilingual desktop entry with `desktop-file-validate`.
- Extracted the finished package in an owned workspace. Its executable SHA-256 exactly matches the upstream release payload. Its packaged browser regression passes clean-shell launching, failed-browser fallback, manual URL startup and graceful Ctrl+C without launching a real browser or modifying affinity.
- Regenerated `.SRCINFO` matches the checked-in copy. The source package includes only the recipe, metadata, desktop entry, logo and license. The SVG embeds the user's logo bytes unchanged with the correct JPEG media type. Language contracts still pass.
- AUR RPC and the official Arch package search returned no matching package at preparation time. The owner has no AUR account yet, so publication, a clean `paru` installation and repository-driven updates remain unverified. GitHub documents this status explicitly. Fedora RPM packaging is not included.

## Download-guide-only presentation — 2026-10-27

Linux extraction, launch and troubleshooting command blocks now render only inside the download dialog. The standalone page section and its extra link are removed. The guide explicitly explains the fixed readline/browser failure and manual startup with version 0.3.2 or later. Shared `guide=linux` URLs and previously shared `#linux-commands` links open the dialog at the Linux instructions step. Normal page navigation stays usable after closing it.

## 0.3.2 Linux browser launch regression — 2026-10-27

The user's exact `/bin/sh: undefined symbol: rl_trim_arg_from_keyseq` failure was reproduced by launching the local system shell with the previously published executable's bundled readline/ncurses libraries. The same shell exits successfully with system libraries.

The launcher restores `LD_LIBRARY_PATH_ORIG` only in the external Linux browser process, or removes the bundled library path when no original was present. The backend and its bundled self-test child keep their own environment. The mechanism follows [PyInstaller's external-program guidance](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#launching-external-programs-from-the-frozen-application).

New regression coverage checks parent-environment preservation, missing/failing openers, a packaged system-shell opener, manual fallback with a live read-only API, `--no-browser` URL output and graceful Ctrl+C. The browser fixture is owned test code; no user's browser or existing process affinity is controlled by these checks.

## Linux download instructions — 2026-10-27

- Portable extraction/permission/launch commands were exercised against an owned temporary archive and stub executable, including Arabic/spaced paths and subsequent launches.
- Missing/corrupt archives fail before launching an already extracted executable. Package installation commands were syntax-checked and reviewed against official package-manager references; they were not executed on the user's system.
- Browser checks cover CachyOS/Fedora selection, preserved expanded sections, exact copied shell text, Arabic/English switching and the Linux download modal.
- Instructions also cover Ubuntu/Debian/Mint and openSUSE. They do not claim physical validation on every distribution release. Existing native binary/CI coverage remains described below.

## 0.3.0 interface and language update — 2026-10-26

- 87 Linux/Python tests passed, including persisted Arabic/English preference, invalid input, CSRF protection and unchanged read-only/affinity state.
- Dependency-free JavaScript translation contracts verify both languages while preserving CPU IDs, group labels, numeric sets and filenames.
- Browser checks cover Arabic/English switching, RTL/LTR, settings language controls, contextual explanations, searchable Help & Guide, first-run onboarding and Windows/Linux download guidance.
- Website download guidance opens before a download, permits cancellation/back navigation and uses the verified current release URL only at the final step.
- Native Windows and Ubuntu release jobs passed, including both language contracts, Windows topology fixtures, the Linux suite and packaged owned-child apply/read-back/restore checks. The Windows build copied the M icon into the executable.
- Published binaries and verification reports: https://github.com/MOOODEGRX-nah/HalawaCore/releases/tag/v0.3.0
- Verified 0.3.0 workflow: https://github.com/MOOODEGRX-nah/HalawaCore/actions/runs/40394855953
- Only the user-provided logo and synthetic interface diagrams are included in public assets. No live hardware screenshots are published.

## 0.2.0 native platform validation — 2026-10-26

## Local automated checks

- 86 tests passed on Linux / Python 3.14.8, including the original Linux matrix and new Windows x64 ABI/topology fixtures and desktop self-test.
- One non-failing Starlette/httpx test-client deprecation warning remains.
- JavaScript module syntax checks and Python compilation pass.
- Both Linux source and the bundled Linux executable start the API, discover the actual host topology, apply a CPU mask only to their own disposable child, verify the kernel mask, restore and verify the originals.
- Windows source smoke verification under Wine discovers topology. Missing CPU Set interfaces correctly keep affinity read-only. Wine is not physical Windows 10/11 validation.

## Hardware and evidence limits

Live host topology and reversible affinity were verified locally. Local device details and screenshots are excluded from public source. X3D models and architecture variants are tested through synthetic fixtures, not physical X3D hardware.

Windows fixtures exercise fixed-width native structure sizes, legacy/current cache masks, single/dual L3 domains, different processor groups, malformed records, conflicting cache sizes and virtualized X3D uncertainty. Affinity on Windows multi-group systems or explicit CPU Sets remains disabled rather than assuming it is reversible.

## Browser verification

The renamed local dashboard loads real data. The Arabic product website links to the separate program/download page, labels its chip diagram as illustrative, and uses an interface illustration with no live device data. The website does not attempt to inspect visitor processes. Downloads resolve only from real GitHub release assets; unavailable releases use the release listing.

The native GitHub release workflow passed on both Windows Server and Ubuntu 22.04. The Windows job passed 12 topology/ABI fixture tests and the bundled executable verified topology plus owned-child affinity application, kernel read-back and restoration. The Linux job passed the full 86-test suite and its bundled executable self-test. Each downloadable archive includes its executable verification report. CI on a virtual Windows Server runner is distinct from physical Windows 10/11 hardware testing.

Local Linux binaries built on the current Arch/CachyOS host may require that host's glibc. GitHub Linux releases are built on Ubuntu 22.04 and target glibc 2.35+.

Verified release workflow: https://github.com/MOOODEGRX-nah/HalawaCore/actions/runs/40385407298

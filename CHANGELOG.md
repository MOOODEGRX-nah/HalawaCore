# Changelog

## 0.5.0 — 2026-10-27

- Show CPU utilization as a share of visible online logical CPU capacity by default, with a selectable traditional per-CPU total and logical-CPU-equivalent explanation.
- Add a bilingual before/after workflow, automatic comparison table, signed percentage-point differences, elapsed-time-aligned curves and comparison export.
- Weight recording averages by actual intervals; retain observed masks, CPU capacity and topology context. Reject mismatched process identities, incomplete/insufficient recordings and changed or unverified online capacity.
- Keep comparisons descriptive: no inferred FPS, frame-time, latency or speed improvement. Include tests and native packaged recording/comparison verification.

## 0.4.0 — 2026-10-27

- Select up to 32 running processes with checkboxes, filtered select-all, selection chips and a shared affinity planner. Search and refresh preserve verified identities.
- Preview all selected processes and existing threads together, limit choices to their common eligible CPUs, and preserve individual masks for restoration. Stale identities and changed masks invalidate application before writes.
- Add Arabic/English controls and help, cross-platform batch tests and packaged two-child self-tests. Performance Lab continues recording only the primary selected process.

## Packaging — 2026-10-27

- Prepare an Arch/CachyOS `halawacore-bin` recipe for the verified 0.3.2 binary, with fixed SHA-256 checks, terminal command, bilingual desktop entry and the supplied M logo.
- Document local installation and AUR publication separately; the package is not yet published to AUR.
- Exclude packaging-only changes from native executable release builds.

## 0.3.2 — 2026-10-27

- Restore the original Linux library search path only for the external browser launcher, fixing bundled readline conflicts on newer systems such as CachyOS.
- Always print the local interface URL; browser launch failures keep the local backend available for manual access.
- Make --no-browser a usable manual-start mode and handle Ctrl+C without an unhandled PyInstaller traceback.
- Add packaged browser-launch, failed-launch, manual-mode and interrupt regression checks.

## Documentation — 2026-10-27

- Keep Linux command blocks exclusively inside the website download guide; shared links open that guide.
- Add bilingual troubleshooting for the fixed browser/readline conflict and manual startup.

- Added copyable Linux extraction, execution-permission and launch commands to the download guide.
- Added CachyOS/Arch, Fedora, Ubuntu/Debian/Mint and openSUSE package-tool guidance and explicit compatibility limits.
- Added a bilingual Linux startup document and README instructions.

## 0.3.1 — 2026-10-27

- Keep keyboard skip links accessible without creating horizontal overflow in RTL/LTR layouts.
- Preserve website routes with both branch-based and Actions-based Pages publishing.

## 0.3.0 — 2026-10-26

- Approved M logo and red-and-black website/application styling, including the Windows executable icon.
- Arabic/English interface switching with RTL/LTR layouts and locally persisted desktop language.
- Searchable Help & Guide below Settings and contextual question-mark explanations.
- Download onboarding for Windows/Linux and an in-app welcome guide.
- README organized as a complete Arabic section followed by a complete English section.
- Versioned releases preserve earlier published executables.

## 0.2.0 — 2026-10-26

- Final product name: HalawaCore.
- One-click portable desktop entry with bundled Python and a local browser interface.
- Initial Windows x64 topology, cache, SID ownership and per-thread FILETIME/affinity adapters.
- Conservative read-only handling for Windows multi-group and explicit CPU Set configurations.
- Arabic product website and separate program/download page.
- GitHub Pages deployment and native Windows/Linux executable release workflows.
- Packaged API/self-tests using only disposable owned subprocesses.

## 0.1.1 — 2026-10-26

- Initial local FastAPI and vanilla JavaScript application.
- Generic Linux topology graph, SMT mapping, CPPC, capacities, NUMA, cache domains and live metrics.
- AMD X3D cache-domain classification with conservative uncertainty and read-only driver preference discovery.
- Optional cache, frequency and scheduler-default profiles with no guaranteed performance claims.
- Process/desktop discovery, observed Steam/Wine/Proton relationships and explicit task scopes.
- Confirmed, kernel-verified affinity experiments and identity-validated per-thread restoration.
- Local baseline/experiment/restored recordings, profile storage and JSON exports.
- Synthetic architecture/X3D fixtures and safe owned-subprocess integration tests.

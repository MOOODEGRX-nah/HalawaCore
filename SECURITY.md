# Security and trust boundary

## Desktop and Windows additions (0.2.0)

The desktop executable starts the same local backend on an OS-assigned loopback port and opens the local browser UI. It does not connect a public website to a local privileged API. Quit requires the normal local session token and refuses while recordings or unrestored experiments remain active.

Windows ownership uses process token SIDs, not usernames. Native process/thread creation FILETIMEs are preserved exactly. Open validated thread handles remain held across writes/read-back, so Windows PID/TID reuse does not redirect an operation. No elevation, debug privilege, driver installation, CPU Set rewrite, or system-wide preference change is requested.

Multi-processor-group Windows affinity stays read-only because reading a thread's primary group does not capture Windows 11's implicit all-group eligibility. Explicit CPU Set selections, unavailable CPU Set query functions and inaccessible targets remain read-only. Do not replace these guards with an assumed CPU count or a legacy 64-bit process-mask shortcut.

Desktop data uses LOCALAPPDATA/HalawaCore on Windows and XDG_DATA_HOME/halawacore on Linux. New Linux directories/files use private mode bits; Windows data inherits the user's application-data ACLs. The public website queries only public GitHub release metadata. It does not collect process data or expose local control endpoints.

## Linux implementation

HalawaCore runs as the ordinary desktop user. Do not use sudo, grant capabilities, expose it publicly or run multiple backend workers. The provided launcher binds to 127.0.0.1 and selects one worker. It refuses root startup.

Local web requests accept only loopback Host names, require a matching Origin and a startup-generated session token for mutations, reject cross-site fetch metadata, and do not enable CORS. The frontend uses a restrictive local Content Security Policy, frame denial, no external assets and escaped process/profile text. A same-user local program is already inside the OS permission boundary; the session token is protection against hostile web pages, not authentication against a compromised local account.

No inspected process environments are read. Raw command arguments are never returned; the UI exposes an executable and argument count. Runtime identification uses executable/process names and observed ancestry. No command-execution API, arbitrary-path API or privilege escalation is implemented. User-selected browser files are not uploaded or run.

Affinity requires an owned, identity-validated task, current online CPU membership, current-mask validation, a short-lived preview and explicit confirmation. Each attempted original mask is recorded before application. Reads verify accepted affinity. Failed operations do not kill target programs. Restoration validates both leader and task identities and reports partial results. A failed or partially restored experiment blocks overlapping changes on the same task.

Linux's numeric-ID affinity syscall leaves a small identity-check-to-syscall race. Start-tick checks immediately before and after reduce but do not atomically eliminate it. The backend protects itself and PID 1. It does not infer that all same-user programs are safe to restrict; the user must choose the target explicitly.

All sysfs hardware access is read-only. There is no implementation for scheduler-mode, driver, BIOS, cpufreq or kernel-parameter writes.

Profiles and the local audit are created under `data/` (or the trusted launch-time `HALAWACORE_DATA_DIR`), with private directory/file permissions for newly created data. Use a directory owned and controlled by your account, not a shared/symlink-controlled directory. Audit rows contain task IDs/start identities, CPU masks and outcomes, without process arguments. Recordings are memory-only until the user exports them. No external telemetry is sent.

Keep the backend alive until experiments are restored. Graceful shutdown makes a best-effort restoration attempt. Crash recovery, boot recovery and restoration after SIGKILL are unsupported. The audit log is evidence, not an automatic recovery mechanism.

For a security report, share a minimal reproduction with process names/paths, commands, exports and screenshots redacted as appropriate. Do not post a full process dump or session token in a public issue. No repository or private reporting address has been configured by this source-only delivery.

# HalawaCore

A local Linux CPU topology and process-affinity analyzer. FastAPI serves a vanilla JavaScript interface on `http://127.0.0.1:8000`. Hardware and process analysis stays on your machine. No cloud service, CDN, root access, or frontend build step is required.

HalawaCore reads the running kernel. Example processor data lives only in test fixtures. Missing information stays missing.


## Install and run

Python 3.10 or later and Linux are required. Python 3.14 was used for this release's tests. Start as your normal desktop user, outside a container if you want to inspect desktop processes.

On CachyOS, Arch, EndeavourOS or Manjaro, install Python if needed:

```sh
sudo pacman -S --needed python python-pip
```

From this extracted source directory:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
./run.sh
```

Open **http://127.0.0.1:8000** in your browser. The launcher binds to loopback and uses one backend worker. Leave it running until your experiments have been restored. Press Ctrl+C after restoration to stop it.

Optional virtual environment activation:

```bash
source .venv/bin/activate
```

Fish:

```fish
source .venv/bin/activate.fish
```

Alternative package prerequisites:

| Distribution | Prerequisites |
| --- | --- |
| Debian, Ubuntu, Linux Mint | `sudo apt install python3 python3-venv python3-pip` |
| Fedora | `sudo dnf install python3 python3-pip` |
| openSUSE | `sudo zypper install python3 python3-pip` |

Use `python3` instead of `python` where appropriate. Package availability and names depend on the distribution release; these platforms have not all been tested. Runtime capability detection is independent of the distribution or desktop.

If the browser cannot connect, check the terminal for missing dependencies or an occupied port. HalawaCore requires the backend; opening `frontend/index.html` directly will not work. Choose another local port using `HALAWACORE_PORT=8001 ./run.sh` (Fish: `env HALAWACORE_PORT=8001 ./run.sh`), then open the matching URL. Never expose the service through a public bind address or reverse proxy.

## What works

- Dynamic physical core and SMT groups from Linux topology, including sparse IDs, more than two threads per core, multiple sockets, and offline CPUs.
- Package, die, cluster, NUMA, L3 cache, core and logical CPU membership graph. NUMA and cache membership are separate relationships.
- Per-core Linux and configurable KDE display IDs, CPPC highest/nominal performance, AMD preferred-core rankings, capacity classes, frequency and live utilization.
- Shared L3 masks and sizes, X3D capability and cache/frequency experiments with explicit uncertainty.
- Accessible process search, live CPU/memory metrics, ownership, start identity, threads, executable metadata, installed XDG/Flatpak desktop entries, and process relationships. Exact executable matches link desktop IDs; names alone do not.
- Steam, Proton and Wine process evidence and game-process candidates through observed ancestry. Inspect the actual game process before applying a restriction.
- Explainable safe, cache, frequency, performance, background, NUMA and custom affinity selections.
- Confirmed preview, kernel-verified apply and per-task restoration; selected main task, explicit TID, existing process threads, and explicitly selected related processes.
- Baseline/experiment/restored recordings, utilization charts, thread counts, memory, observed affinity, per-CPU distribution and JSON export.
- Manually loaded saved profiles, dark/light themes, configurable refresh and numbering.

## X3D behavior

### Discovery

The reader inspects:

```text
/proc/cpuinfo
/sys/devices/system/cpu/{present,online}
/sys/devices/system/cpu/cpu*/topology/
/sys/devices/system/cpu/cpu*/cache/index*/
/sys/devices/system/cpu/cpu*/acpi_cppc/
/sys/devices/system/cpu/cpu*/cpufreq/amd_pstate_prefcore_ranking
/sys/devices/system/cpu/cpu*/cpufreq/cpuinfo_max_freq
/sys/bus/platform/drivers/amd_x3d_vcache/*/amd_x3d_mode
```

It reads each cache index's level and type; it does not assume L3 is always `index3`. Domain identity comes from the shared CPU list (or mask), with sizes and coverage checked across reporting CPUs. Repeated cache IDs never merge unrelated sharing masks. Die IDs remain separate metadata and are not called CCD IDs without evidence.

X3D capability uses an AMD processor-reported X3D name or an exposed bound AMD X3D device, rather than a list of supported models. This admits future model names without assigning any CPU numbers from their name.

Cache candidates require complete, consistent kernel cache membership and physical core information:

- For a package with one shared L3 domain on an X3D-reported processor, that domain is the cache candidate.
- For several domains in the same package, larger L3 domains are candidates only when domain core counts are comparable (equal) and their sizes differ.
- Ambiguous, incomplete, overlapping, conflicting, virtualized or unequally sized core groups do not establish X3D cache identity. The interface displays **“X3D cache group unverified”** and disables the corresponding suggested restriction.

The classification is an inference from model/driver capability and kernel topology, not direct proof of the cache's silicon construction. Observed L3 domains remain visible even when X3D identity cannot be inferred. No fixed cache-size threshold, CCD number or CPU-number split defines X3D identity.

### Three X3D profiles

| Profile | Behavior |
| --- | --- |
| Cache-Oriented Gaming | Test identified cache domains, intersected with the selected process's current online CPU set. Disabled if the identified domain has no permitted CPUs. |
| Frequency-Oriented Computing | Test a group's strictly higher kernel-reported hardware maximum-frequency range within its package. Requires complete frequency information and non-overlapping ranges. CPPC ranking and current clocks alone are insufficient. |
| Balanced / Scheduler Default | Preserve the current eligible affinity. This is the default for games. |

Some games benefit from cache; other workloads benefit from frequency or all available cores. Affinity can reduce throughput, increase contention, or interfere with useful scheduling decisions. No profile promises improved performance.

### Scheduling preference is read-only

The dashboard shows the AMD driver's registration/bound-device status, every exposed mode, and its cache/frequency preference when readable and unambiguous. A registered driver without a bound mode file does not prove active hardware support. Multiple differing device modes produce an unknown aggregate preference.

The kernel's `amd_x3d_mode` ABI describes cache/frequency ranking preference. HalawaCore **only reads** it. There is no endpoint for writing scheduler modes, cpufreq controls, drivers, BIOS settings or kernel parameters. AMD preferred-core rankings can change dynamically and are not benchmark scores.

Primary interface references: [AMD X3D sysfs ABI](https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/sysfs-bus-platform-drivers-amd_x3d_vcache), [CPU topology and cache sysfs ABI](https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/sysfs-devices-system-cpu), [AMD pstate documentation](https://docs.kernel.org/admin-guide/pm/amd-pstate.html). These links are documentation; the running app never fetches them.

## Safe experiment workflow

1. Select a verified running process in Applications. Check executable, ownership, start identity, and observed relationships.
2. Record an original-affinity baseline in Performance Lab if you want a comparison. Phase labels are manual; each sample records the actual main-task affinity.
3. Choose a profile or build a custom CPU set in Affinity Planner. Offline CPUs and CPUs outside the main task's existing affinity are unavailable. Explicit TID and multi-task previews additionally validate each affected task's own mask.
4. Select the exact scope. Related processes are included only when explicitly checked; similarly named unrelated programs are excluded.
5. If desired, disable read-only mode in Settings. This does not apply a change.
6. Preview the exact PIDs, TIDs, task start ticks, original masks and requested CPUs. A preview expires after 60 seconds and is single-use.
7. Acknowledge the warning and confirm Apply. The backend rechecks ownership, process/thread identities, topology generation and each current mask before and immediately around the operation.
8. Verify the per-thread results. Failures remain explicit. Linux can reject or narrow a mask if cpusets or online CPUs change; a different accepted mask is reported as a partial failure.
9. Restore Original Affinity. Every surviving identity-validated task is restored to its own recorded mask and checked again. Exited, reused or inaccessible tasks produce a partial restoration report. Re-enabling read-only mode does not block restoration.

New tasks can appear during enumeration or after a one-time operation. They are not continuously tracked. Existing-process-thread scope is not a promise of permanent application-wide or recursive coverage. Affinity limits scheduling eligibility; it does not reserve CPUs or set NUMA memory policy.

A live experiment cannot overlap another on the same recorded task until restoration completes. Read-only mode resets on every backend startup. Profiles are never automatically applied.

The exact-task preview is tested with disposable owned subprocesses.

## Proton, Wine, Flatpak and AppImage

Affinity applies to Linux schedulable tasks, including accessible Wine runtime/game tasks. Observed parent-child links and matching ownership identify related processes. Steam/Wine/Proton names are runtime evidence, not proof that every child is the actual game. Select exact PIDs/TIDs and review the preview.

Runtime affinity is distinct from launch-time CPU topology configuration inside Wine/Proton. No target-specific launch override, compatibility-layer setting, or CPU-topology environment variable is proposed without verified integration support. Launch configuration is **unverified** in this release.

Flatpak desktop entries are discoverable from accessible export directories. Sandboxes may hide host processes or deny affinity changes. AppImage/native processes use the same process inspection and permission checks; an AppImage identity is not guessed from a similar process name.

## Tests and compatibility evidence

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

For the exact full environment used here, including transitive and test dependencies, install `requirements-lock.txt` into a fresh environment. It records the versions tested on Python 3.14; availability on other interpreters/architectures depends on their package wheels or build prerequisites.

The integration test only modifies a disposable `sleep` subprocess it creates. It verifies the kernel mask, restores the original, verifies restoration, then terminates that subprocess in cleanup. It never changes affinity on games, a compositor, or unrelated processes.

| Evidence level | Coverage |
| --- | --- |
| Supported by design | Linux kernel topology interfaces on x86_64, ARM64, RISC-V, POWER, s390x and future architectures. Missing metadata reduces functionality instead of substituting a sample CPU. |
| Automated sysfs fixtures | Ryzen 7700; 7800X3D/9800X3D; asymmetric 7900X3D/7950X3D/9900X3D/9950X3D; multi-domain EPYC; homogeneous Intel SMT; two/three capacity classes; hybrid without HT; ARM64; no SMT; sparse IDs; multi-socket NUMA; virtual guest; three/four SMT threads; missing topology/CPPC/cache/driver; conflicting cache metadata; driver preferences; restricted/offline CPUs. |
| Automated operation tests | Empty/invalid/disallowed masks; read-only and confirmation; task-specific masks; PID/TID reuse; disappearance; permissions; partial apply and restore; kernel verification; stale/hotplugged topology; preview expiry/replay; CSRF/Host validation; profile storage; real subprocess recording/apply/restore. |
| Live runtime validation | Live Linux topology discovery and owned-process experiments were validated locally. Browser verification covers the live dashboard, process selection, planner, read-only preview and baseline recording. The development process namespace restricts which processes are visible. |
| Physical X3D validation | **Not performed.** X3D designs are covered by synthetic sysfs fixtures, not physical X3D hardware. No universal hardware compatibility claim is made. |

See [VALIDATION.md](VALIDATION.md) for the release test report.

## Limits and recovery

- Kernel-reported architecture/model identifiers are shown as exposed. A Zen generation or Intel core marketing type is not guessed from clock speed. Capacity classes are reported when reliable kernel capacities differ; raw core-type values remain available in JSON.
- No automatic ongoing task tracking, launch-time affinity, arbitrary executable execution, icon-file serving, external FPS/temperature/power integration, or crash recovery is implemented.
- Browser executable selection exposes only the file name, size and browser-reported media type. It does not read/upload/execute the file or establish running-process identity.
- Native installed applications can link to running PIDs through an exact resolved executable. Wrapper/Flatpak launch entries without that identity remain “Insufficient information”. Custom icons are not rendered; desktop icon names are metadata only.
- Recommendations revalidate current masks. To widen a mask narrowed by HalawaCore, restore the active experiment first.
- PID/TID and start-time checks greatly reduce reuse risk, but Linux's affinity syscall is numeric-ID based. There is an unavoidable tiny race between the final identity check and the syscall; atomic pidfd-based affinity is not provided by this implementation.
- Originals and recordings are held in memory; profile JSON and an affinity audit are saved under `data/` (override with `HALAWACORE_DATA_DIR`). Graceful shutdown attempts restoration. **No restoration is promised after a crash, SIGKILL, power loss or restart.** Restore before stopping and export measurements you need to keep. The audit is not an automatic recovery service.
- Monitoring is capped at 3,600 samples per recording and 50 recordings per backend session. Only utilization, frequency, process CPU/memory and thread data from real Linux sources are collected. CPU usage alone cannot establish a speedup.
- Very large machines may incur more sysfs-reading and rendering work. No physical multi-socket/NUMA or non-x86 system was tested here.

## Source and release packaging

```text
backend/       topology, process discovery, recommendations, task affinity, lab, API and security
frontend/      HTML, CSS and vanilla JavaScript modules, served from the same origin
tests/         synthetic sysfs fixtures, unit/API tests and owned-process integration
docs/          API, security, validation and live screenshots
run.sh         unprivileged loopback launcher
package.py     source release archive builder
```

```sh
python package.py
```

This creates `dist/halawacore-0.1.1.tar.gz`, excluding runtime data, caches and virtual environments. Extract it and follow the installation instructions above. Source packaging is distribution-independent; this release does not install a privileged daemon or modify system services.

API documentation: [docs/API.md](API.md), plus the local `/openapi.json` schema. Security details: [SECURITY.md](SECURITY.md). Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). License: [MIT](LICENSE).

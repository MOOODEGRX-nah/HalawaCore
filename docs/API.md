# Local API

## Language preference 0.3.0

`GET /api/session` includes `preferences.language` (`ar`, `en` or null before selection). `POST /api/preferences` accepts only `{"language":"ar"}` or `{"language":"en"}`, with the normal origin/token checks. The choice is stored locally and restored across desktop launches even when the loopback port changes. It never enables affinity experiments or changes OS scheduling. Read-only mode still starts enabled each backend session.

## Desktop / Windows 0.2.0 additions

The desktop executable chooses an available loopback port and opens its URL automatically. Use that exact origin for any local client; port 8000 below is the source-development default. `GET /api/session` includes `desktop: true` when launched as the portable app. `POST /api/shutdown` requires the normal token/origin and refuses until all experiments are restored and recording has stopped.

On Windows, process/thread `identity` is the exact decimal creation FILETIME, not Linux start ticks. Scope `main` means the oldest surviving thread on Windows, and the main task on Linux. Windows PID is never assumed to equal TID. The legacy recommendation field `linux_cpus` contains stable internal OS CPU IDs on either platform; Windows display labels use group/processor pairs. Explicit CPU Sets and multiple processor groups stay read-only in the Windows initial release. Linux sysfs driver/CPPC values are unavailable on Windows rather than simulated.

## Source-development API reference

Base URL: `http://127.0.0.1:8000`. Responses are JSON except `/` and static assets. The machine-readable OpenAPI schema is at `/openapi.json`. The app does not load external Swagger assets.

State-changing calls require both `Origin: http://127.0.0.1:8000` (matching the exact Host/port) and `X-HalawaCore-Token`, obtained from `GET /api/session` in the same browser origin or trusted local client. No unrestricted CORS is enabled. Do not put the token in a URL or logs.

Errors use `{"error":{"message":"..."}}`; invalid fields additionally return `fields`. Invalid input returns 422; permission/CSRF failures 403; missing records 404; stale identities, expired previews, topology changes and kernel-operation conflicts generally 409. Linux-operation errors never cause a privilege escalation.

| Method | Endpoint | Payload / result |
| --- | --- | --- |
| GET | `/api/session` | Startup token, read-only/display settings and saved language preference |
| GET | `/api/health` | Backend and read-only status |
| GET | `/api/system` | OS, model, architecture, counts, virtualization |
| GET | `/api/cpu/topology` | Cores, logical CPUs, cache domains, graph, feature states, X3D evidence, topology generation |
| GET | `/api/cpu/metrics` | Timestamp, `/proc/stat` utilization keyed by real CPU IDs, available per-CPU frequency in kHz; first deltas are null |
| GET | `/api/processes?q=...` | Accessible process rows, optionally filtered; command arguments hidden; desktop IDs linked only by exact executable identity |
| GET | `/api/processes/{pid}` | `root`, observed related processes, ancestors, runtime evidence and unverified launch-topology guidance |
| GET | `/api/processes/{pid}/threads` | Existing TIDs, task start identities and current affinities |
| GET | `/api/applications` | Installed XDG/Flatpak entries, exact executable/PID matches when available, unsupported launch status |
| POST | `/api/recommendations` | `{pid, identity, workload, restrictions?}` → bounded profiles, explanations, confidence, CPU/KDE sets, SMT included/excluded mappings, warnings and generation |
| POST | `/api/affinity/preview` | `{pid, identity, cpus, scope, related?, task_tid?}` → exact original per-task masks and single-use `preview_id`, valid for 60 seconds |
| POST | `/api/affinity/apply` | `{preview_id, confirmed:true}` → per-task kernel verification and restoration record |
| POST | `/api/affinity/restore` | `{experiment_id}` → restored or partial_restore per recorded task; works in read-only mode |
| GET | `/api/experiments` | Current-session affinity records and performance recordings |
| POST | `/api/experiments/start` | `{pid, identity, phase, interval}` → start recording; does not modify affinity |
| POST | `/api/experiments/stop` | `{}` → stop active recording and return recordings |
| GET | `/api/profiles` | Saved, manually loaded CPU sets |
| POST | `/api/profiles` | `{name, cpus, generation, note?}` → saved profile; does not apply |
| DELETE | `/api/profiles/{id}` | Delete a UUID profile |
| POST | `/api/settings` | `{read_only, display_offset}`; offset 0 or 1; root cannot enable experiments |
| POST | `/api/preferences` | `{language}`; `ar` or `en`; local interface preference only |

`identity` is the decimal Linux process start-ticks string obtained from discovery. It must not be fabricated from a timestamp. Each preview also stores the thread's own start ticks and the leader's identity.

Scopes:

- `main`: selected PID's main task only (default).
- `task`: one explicit `task_tid` from that process's currently existing thread list.
- `threads`: currently existing threads of the selected process.
- `related`: selected process and explicitly supplied related `{pid,identity}` pairs, with each process's existing threads. Current ownership and observed parent-child relationship are checked; similar names do not qualify.

The backend refuses empty sets and CPUs outside any affected task's existing mask. It validates online CPUs again via topology generation and verifies the accepted kernel masks. New threads or processes may not be covered.

Workloads: `gaming`, `competitive gaming`, `browsing`, `communication`, `encoding`, `rendering`, `compilation`, `streaming`, `ai inference`, `background`, `custom`, `unknown`.

Recording phases: `baseline`, `experiment`, `restored`. Labels are user-selected; they are not proof that affinity is original/modified/restored. Each sample contains its observed main-task affinity. Interval range is 0.5–60 seconds. Process utilization can exceed 100% when multiple CPUs are used. No application-speed inference is made.

The topology `generation` excludes momentary frequency/utilization samples and includes membership, online masks, analyzer constraints, ranking hints, cache evidence and driver preference. Changes invalidate a pending preview. Apply independently rejects changed per-task masks. A cpuset change after validation can still race the syscall and is detected through kernel read-back.

Example read-only Python inspection:

```python
import httpx

with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    topology = client.get("/api/cpu/topology").raise_for_status().json()
    print(topology["x3d"]["label"])
    for domain in topology["cache_domains"]:
        print(domain["logical_cpus"], domain["size_bytes"], domain["verified"])
```

There are deliberately no routes for shell execution, arbitrary file reading, launching executables, writing X3D modes, changing BIOS/driver state, or editing kernel parameters.

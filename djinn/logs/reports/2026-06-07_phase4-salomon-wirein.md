## Phase 4 Salomon Wire-in — 2026-06-07

**Status:** Complete
**Commits:** fa20419 (vault)

**Files changed:**
- `~/.local/bin/vault-sync` — delta_guard on git push
- `~/.local/bin/comms-processor` — djinn-gate routing + delta_guard on push
- `~/.local/bin/djinn-ctx-router` — delta_guard on tick() via tick_if_changed()
- `~/.local/bin/djinn-clerk` — delta_guard at scan invocation level
- `~/.local/bin/printer-error-logger` — delta_guard around watchdog + history checks
- `~/.local/bin/djinn-comms-compact` — NEW: COMMS.md monthly archive script
- `~/.config/systemd/user/comms-compact.service` — NEW
- `~/.config/systemd/user/comms-compact.timer` — NEW: fires daily at 03:00
- `djinn/tools/delta-guard/typhon-heartbeat.sh` — NEW: Typhon heartbeat with guard

**Notes:**

vault-sync: rclone to GDrive still runs unconditionally (correct — keeps GDrive current
regardless of git state). Git push now guarded on vault_commit_hash + uncommitted_files count.

comms-processor gate wiring: extracts first non-header task line as gate description.
Ops-lane tasks skip opencode entirely and write a COMMS entry explaining why.
Gate lane context is injected into the opencode prompt for all other lanes.
Delta_guard on final push tracks COMMS.md line count (exact).

djinn-ctx-router: tick() now only fires when vault commit hash changes. On a quiet day
(no vault commits), context is rebuilt zero times instead of 288 times.

djinn-clerk: delta_guard at the scan level (RAW/ file count). Per-file MD5 tracking
(clerk-processed.json) still handles deduplication within a scan. Explicit path
invocations bypass the guard (intentional — direct dispatch must always run).

printer-error-logger: state = {printer_state, current_file}. watchdog checks and
job history only run when state changes. monitor row logging unchanged (has its
own time-based throttle). This stops 2880 redundant API calls/day when printer is idle.

comms-compact: keeps last 40 section entries in COMMS.md, archives older ones to
djinn/communications/archive/COMMS-YYYY-MM.md by month. Threshold: 800 lines.
Runs daily at 03:00 via systemd timer (enabled and active). --dry-run flag available.

**Typhon action required:**
Typhon heartbeat script is at djinn/tools/delta-guard/typhon-heartbeat.sh in the vault.
After vault pull on Typhon:
```bash
cp ~/Obsidian/djinn/tools/delta-guard/typhon-heartbeat.sh ~/.local/bin/heartbeat
chmod +x ~/.local/bin/heartbeat
systemctl --user restart heartbeat
```

**Deviations from spec:**
- comms-processor gate uses first non-header text line for gate routing (heuristic).
  A dedicated **Task:** field parser would be more precise — deferred to Phase 5 if needed.
- printer-error-logger state tracks printer_state + current_file (not error_code directly).
  Error codes are only known after check_job_history() runs; gating on pre-fetch state
  is the correct order to avoid catching errors only after they're gone.

— Claude

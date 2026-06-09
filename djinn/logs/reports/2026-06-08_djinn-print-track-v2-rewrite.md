---
title: Session Report — djinn-print-track v2 WebSocket rewrite
agent: Claude
date: 2026-06-08
tags: [djinn, report, print-track, websocket, v2]
related: [[build-log]] | [[decision-log]] | [[COMMS]]
---

# Session Report — djinn-print-track v2

**Date:** 2026-06-08
**Agent:** Claude
**Session type:** Build
**Trigger:** Marcus research (Perplexity) identified 4 gaps in print automation; built from his spec with path corrections and edge-case hardening

---

## Summary

Rewrote `djinn-print-track` from HTTP polling (v1) to WebSocket-driven architecture (v2). Added queue bridge, filament auto-deduction, structured print records in the Obsidian vault, rotating backups, and atomic writes. Live-tested with a 26-minute test cube on Calliope — all 4 gaps closed automatically with zero manual intervention.

---

## What Was Built or Changed

| Item | Detail |
|------|--------|
| `~/.local/bin/djinn-print-track` | Full rewrite: 393→882 lines |
| `~/.config/systemd/user/djinn-print-track.service` | Description updated to v2 |
| `~/.local/share/djinn/filament-inventory.json` | New — spool inventory file |
| `~/Downloads/djinn-print-track-v2.py` | Build source (33KB) |
| `~/Downloads/install-djinn-v2.sh` | Install script |
| `~/Downloads/djinn-print-track.service` | Service file copy |
| `~/Downloads/filament-inventory.json` | Empty inventory template |

---

## Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **Persistent merged state (`_ws_state`)** | Moonraker sends delta notifications, not full state. Without merge, every `total_duration` update overwrites `state`/`filename` with empty strings. |
| **Atomic writes with rotating backups** | `os.replace()` after `fsync` prevents partial-file corruption on power loss. 3-generation `.bak.N` chain enables rollback. Initial implementation missed the `_rotate_backup()` call — fixed in final commit. |
| **HTTP catch-up on reconnect** | WebSocket disconnect during a print loses state. On reconnect, an HTTP query recovers current `print_stats` before resuming subscriptions. |
| **Self-healing on corrupt reads** | `safe_read_json()` tries live file → `.bak.1` → `.bak.2` → `.bak.3`. On first readable copy, restores live file and returns data. |
| **Keep user-local install** | Marcus's spec targeted `/usr/local/bin/` but systemd unit uses `%h/.local/bin/`. Stuck with user-local to avoid sudo dependency and systemd rewrites. |
| **Backfill convention** | Marcus's backfill `--grams` flag was used for the accurate value (89g), not the computed `mm_to_grams(29813mm)` which was initially wrong (889g vs 89g) due to formula bug. |

---

## Files Created or Modified

```
~/.local/bin/djinn-print-track              ← rewrite (882 lines, was 393)
~/.local/share/djinn/filament-inventory.json ← new (spool tracking)
~/.config/systemd/user/djinn-print-track.service ← updated description
~/.local/share/djinn/print-track/prints.json ← preserved (migrated 1 legacy record)
~/.local/share/djinn/print-track/print-queue.json ← new (3 jobs)
~/Obsidian/djinn/printer/prints/2026-06-09_TTHQ_Cup/ ← backfill
~/Obsidian/djinn/printer/prints/2026-06-09_CRtestcube_Ender-3 V3 Plus_26m/ ← live test
~/Downloads/djinn-print-track-v2.py          ← build artifact
~/Downloads/install-djinn-v2.sh              ← build artifact
```

---

## Dependencies Installed

None — `websockets` 16.0 was already present.

---

## Tests & Validation

| Phase | Result |
|-------|--------|
| Phase 1 — Environment check | ✅ Moonraker online, Python 3.14, websockets 16.0, backups created |
| Phase 2 — Install + daemon start | ✅ Service active, WebSocket connected |
| Phase 3 — Backfill Terp Tribe cup | ✅ Queue entry, prints record, spool deduction (200→111g), Obsidian dir all created |
| Phase 4 — Live test cube (26min) | ✅ All 4 closures fired automatically: queue bridge, filament deduction, record generation, alarm at <100g |
| `djinn-print-track verify` | ✅ 0 corruptions across 4 data files |
| `journalctl` errors | ✅ 0 critical errors; 1 minor edge case (str guard) fixed in last commit |

### Live test results

- **Print:** CRtestcube_Ender-3 V3 Plus_26m.gcode
- **Duration:** 26.3 min
- **Filament:** 3,804mm (11g)
- **Spool:** 111.0g → 99.66g ✅
- **Queue:** Job 3 auto-created on start, auto-finalized on complete ✅
- **Records:** `2026-06-09_CRtestcube_Ender-3 V3 Plus_26m/` created with plan.md, model_analysis.json, postmortem.md ✅
- **Alert:** Low filament warning fired at <100g ✅

---

## Known Issues / Caveats

1. **Filename encoding not yet enforced** — The tracker parses `ORD-NNN__Model__Material_color.gcode` convention but doesn't enforce it. Prints uploaded via Creality Print with non-conforming names get incomplete metadata (order_id="", material="PLA" default). Future: enforce naming convention at upload time.
2. **print-queue.json location moved** — Marcus put it at `~/.local/share/djinn/print-track/` (was `~/.local/share/djinn/print-queue.json`). Old location orphaned. No data loss — the v1 queue had 3 stale jobs that were not migrated.
3. **Backup rotation starts from next write** — `_rotate_backup()` was initially missing from `atomic_write()`. Fixed in final commit. Existing files get their first `.bak.1` on the next write to each file.
4. **Heuristic mode removed** — v1 had dual detection (standard + heuristic for Creality Print). v2 relies on WebSocket + `virtual_sdcard.is_active`. Bed-heating prep phase now shows as `standby` until print actually starts — correct per Moonraker docs.

---

## What's Next

- [ ] Enforce filename encoding convention in Creality Print upload workflow
- [ ] Add `job_queue` Moonraker config on printer side (auto-sequencing)
- [ ] Consider weight-based filament confirmation (load cell) for near-empty alerts
- [ ] Backfill remaining legacy v1 queue jobs (8–10) if needed

---

*— Claude, 2026-06-08*

---
title: Callie Calibration — Phase 1 Baseline Complete
agent: Claude
date: 2026-05-25
tags: [callie, calibration, 3d-printing, ender3-v3-plus]
related: [Callie-calibration, printer]
---

# Callie Calibration — Phase 1 Complete

## Summary
Completed baseline calibration for Callie (Ender-3 V3 Plus) using PLA. Temp tower found optimal at 210°C. Calibration cube measured 20.00mm all axes — stock steps/mm confirmed good. First layer square showed consistent bed mesh coverage.

## What Was Built/Changed

### Calibration Pipeline
- Calibration orchestrator: `calibrate.sh` with status/monitor/cube/first-layer/upload/start commands
- Vault tracking structure: 11 log files under `Callie-calibration/logs/`
- Generated 200×200×1mm first layer square STL

### Crash Recovery System
- `djinn-print-backup` — gcode backup to vault (synced to Typhon)
- `djinn-print-recover` — restore from vault backup and re-queue
- `djinn-print-monitor-v2` — 60s poll, auto-detect failures, log to FAILURE-LOG.md
- `djinn-print-promote` — archive finished prints
- Failure log at `failures/FAILURE-LOG.md`
- Print recovery manifest at `recovery/MANIFEST.md`

### Infrastructure
- Recovery directory at `~/Obsidian/djinn/printer/recovery/` (git-synced to Typhon)
- Downloads organized into `_production/` and `_calibration/`
- Trash cleared (569 MB)
- VS Code cache cleared (210 MB)
- OpenClaw stale backups pruned

## Technical Decisions

1. **M104 over M109**: Creality Nebula firmware ignores `M109` (wait for temp) mid-print but accepts `M104` (set temp, continue). Temp tower uses M104 at zone boundaries.

2. **START_PRINT/END_PRINT macros**: Creality's Klipper fork requires custom macros for bootstrapping. PrusaSlicer's standard Klipper gcode doesn't work. All gcodes are post-processed to inject Creality macros.

3. **OpenSCAD for STL generation**: Manual STL generation produced winding issues. OpenSCAD (`cube([20,20,20], center=true)`) generates geometry correctly.

4. **SD card corruption risk**: Firmware restart during active file operations can corrupt SD card state and require power cycle. Avoided in future by the crash recovery system.

## Files Created/Modified

- `~/Obsidian/djinn/printer/library/callie-calibration/` — models, gcode, calibrate.sh
- `~/Obsidian/djinn/projects/Callie-calibration/` — logs for 11 tests + results.md
- `~/.local/bin/djinn-print-backup` — gcode backup to vault
- `~/.local/bin/djinn-print-recover` — crash recovery
- `~/.local/bin/djinn-print-monitor-v2` — failure detection
- `~/.local/bin/djinn-print-promote` — archive
- `~/Obsidian/djinn/printer/failures/FAILURE-LOG.md` — failure tracking
- `~/Obsidian/djinn/printer/recovery/` — gcode backups

## Tests & Validation

| Test | Result |
|------|--------|
| Temp Tower (230→190°C) | Optimal: 210°C (zone 3) |
| Calibration Cube (20mm) | X: 20.00, Y: 20.00, Z: 20.00 — no steps adjustment needed |
| First Layer Square (200×200mm) | Consistent bed coverage, no gaps |

## Known Issues
- Creality Nebula firmware occasionally drops API requests under load — timeouts happen. Power cycle resolves.
- Touchscreen app may crash after firmware restart — printer continues printing regardless.
- `CANCEL_PRINT` via Moonraker API intermittently fails on Creality firmware. `M112` does not work. Physical power cycle required as last resort.

## What's Next
- [ ] Phase 2: Speed & Flow tests (CNC Kitchen, Benchy, Ringing Tower) — needs models sourced
- [ ] Phase 3: Quality tests (Overhang, Bridging, Torture)
- [ ] Phase 4: Tolerances (Clearance gauge, Functional parts)
- [ ] Record final config in `Callie-calibration/results.md`

— Claude, 2026-05-25

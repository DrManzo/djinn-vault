---
title: Session Report — Calliope factory reset + sensorless patch
agent: Salomon
date: 2026-06-05
tags: [djinn, report, 3dprint, calliope, config, hardware]
related: [[build-log]] [[2026-06-05_camood-job14]] [[bugs]]
---

# Session Report — Calliope Config Reset + Cable Diagnostics

**Date:** 2026-06-05
**Agent:** Salomon
**Session type:** Debug / Config / Hardware

---

## Summary

Continued from job14 session. Investigated repeated nozzle_mcu UART dropouts (key561), identified all failures occur under Z=10mm (not high-Z as previously assumed), attempted Creality Print gcode settings injection, adopted Creality motion defaults system-wide, patched Y homing error on power loss recovery, attempted factory config reset (blocked by Z probe mismatch), restored working printer.cfg. Handed off to Salomon for homing/calibration.

---

## What Was Built or Changed

- **`~/.config/forge/ender3-v3-plus.ini`** — start_gcode updated: replaced `M204 P2000 T2000` with `SET_VELOCITY_LIMIT ACCEL=2000 ACCEL_TO_DECEL=500 SQUARE_CORNER_VELOCITY=5` + added `SET_PRESSURE_ADVANCE ADVANCE=0.042` — sourced from Creality Print native gcode
- **`~/Obsidian/djinn/printer/calliope-config-backup-2026-06-05/`** — full config backup: printer.cfg, factory_printer.cfg, gcode_macro.cfg, sensorless.cfg, printer_params.cfg, moonraker.conf
- **Calliope `sensorless.cfg`** — patched: `SOFT_CHECK_ERROR FLAG=1` commented out in Y homing block during power loss recovery, suppresses key404 Y homing error on resume

---

## Technical Decisions

**Factory config abandoned** — factory_printer.cfg was uploaded as printer.cfg but failed Z homing (key22: No trigger on z after full movement) because prtouch_v2 settings differ between factory config and current hardware. Reverted to modified printer.cfg immediately. The modified config must have accumulated hardware-specific tuning over 2 weeks.

**Creality Print settings adopted** — extracted `SET_VELOCITY_LIMIT ACCEL=2000 ACCEL_TO_DECEL=500` and `SET_PRESSURE_ADVANCE ADVANCE=0.042` from original Creality Print gcode on USB. These are now standard in all PrusaSlicer slices for Calliope. The conservative ACCEL_TO_DECEL=500 ratio is the key difference from PrusaSlicer's static M204.

---

## Key Diagnostic Finding

**All 11 nozzle_mcu dropouts (key561) happened at Z < 10mm:**

| Time | Z height |
|------|----------|
| 14:24 | 0.87mm |
| 14:31 | 1.01mm |
| 15:34 | 4.24mm |
| 15:53 | 4.37mm |
| 16:00 | 5.18mm |
| 16:07 | 5.79mm |
| 16:17 | 6.64mm |
| 16:24 | 7.54mm |
| 16:32 | 9.16mm |
| 16:39 | 9.91mm |
| 16:46 | ~10mm |

XY positions scattered — not a specific corner. All at low Z during first layers. The cable reroute did not resolve the issue. The failure is at the connector level or the cable has internal damage from prior stress.

---

## Files Created or Modified

```
~/.config/forge/ender3-v3-plus.ini                           ← Creality motion defaults
~/Obsidian/djinn/printer/calliope-config-backup-2026-06-05/  ← full config backup
Calliope: sensorless.cfg                                     ← key404 suppressed
Calliope: printer.cfg                                        ← restored to working state
```

---

## Known Issues / Open Items

- [ ] **HARDWARE: nozzle_mcu connector** — cable reroute did not fix dropouts. All failures at Z<10mm suggest loose connector at nozzle_mcu board or internal cable damage. Check connector seating; if still failing, replace cable.
- [ ] **Calliope calibration pending** — bed mesh and Z offset need re-run after reset. Handed to Salomon.
- [ ] **M220 S20 on resume** — hardcoded in Calliope's power loss recovery macro (`slow_print M220 S20`). Intentional. Must ramp manually after every resume.
- [ ] **M204 S12000 restored on resume** — power loss recovery restores saved M204 state, overriding our SET_VELOCITY_LIMIT injection. Need to re-inject after each resume or patch RESUME macro.
- [ ] TASK-027: Fill SHIPPO_API_KEY in ~/.config/forge/shop.env

---

## What's Next

- Salomon: home Calliope, run bed mesh calibration, verify Z offset
- Javier: inspect nozzle_mcu connector physically — press to seat, check latch
- If connector seated and still failing: replace nozzle_mcu cable harness

---

*— Salomon, 2026-06-05*

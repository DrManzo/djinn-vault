---
title: Session Report — Penelope Calibration & Mario Pipe Print Run
agent: Claude
date: 2026-06-25
tags: [djinn, report, penelope, calliope, printing, calibration, octoprint]
related: [[build-log]] [[decision-log]] [[bugs]]
---

# Session Report — Penelope Calibration & Mario Pipe Print Run

**Date:** 2026-06-25
**Agent:** Claude
**Session type:** Ops / Debug
**Trigger:** Mario pipe STL sent to Penelope; print failing due to wrong gcode profile and Z offset issues

---

## Summary

Multiple failed print attempts on Penelope revealed three stacked problems: gcode sliced with Klipper/Calliope profile sent to Penelope (Marlin), Z endstop position too high causing nozzle to print in air, and M851/M290 gcode commands not working on stock Marlin without a probe. Resolved through manual bed leveling, physical Z endstop calibration by Javier, and stripping the gcode start sequence to a clean home + no offset. Mario pipe printed successfully on both Penelope and Calliope. Critical new law established: never interact with either printer while running.

---

## What Was Built or Changed

- OctoPrint updated from 1.11.7 → 1.11.8 and restarted
- Penelope API key rotated and saved to `~/.djinn.env`
- `penelope-mario-pipe-tree-supports.gcode` — start gcode iterated through multiple fixes (Klipper→Marlin warmup, M851 attempts, M290 attempts, G92 attempts, final clean version)
- `calliope-mario-pipe-treesup.gcode` — Klipper gcode for Calliope, sent and printed successfully
- Memory locked: no live printer commands while printing

---

## Technical Decisions

**M851 rejected for Z offset** — M851 sets Z probe offset, only applies when a probe (BLTouch/CR Touch) is installed. Stock Ender 3 Pro has a physical endstop only. M851 is silently ignored.

**M290 babystep in gcode rejected** — M290 during gcode start sequence doesn't reliably apply before the first layer move on this firmware version.

**G92 Z0.5 trick rejected** — Attempted coordinate system shift after homing. Javier instead physically calibrated the Z endstop position to set Z=0 correctly at the bed surface. Physical calibration is the correct fix; G92 offsets are a workaround.

**Final approach: clean gcode, physical calibration** — G28 → first layer move with no offsets. Javier owns the Z endstop position. This is the correct Marlin workflow without a probe.

**Calliope Z offset mid-print rejected (law)** — Claude adjusted Calliope's Z offset by 0.05mm while printing to fix maker's mark squish. Javier immediately reversed and established: never touch either printer while running, no exceptions.

---

## Files Created or Modified

```
~/.local/share/forge/gcode/penelope-mario-pipe-tree-supports.gcode   ← Penelope Marlin gcode, tree supports, clean start
~/.local/share/forge/gcode/calliope-mario-pipe-treesup.gcode         ← Calliope Klipper gcode, START_PRINT macro
~/.octoprint-penelope/users.yaml                                       ← API key rotated
~/.djinn.env                                                           ← PENELOPE_API_KEY updated
~/.claude/projects/-home-drmanzo/memory/feedback_printer_no_live_changes.md  ← new law
```

---

## Tests & Validation

- Penelope: mario pipe printed, bed calibrated manually by Javier (paper test 4 corners + center)
- Calliope: mario pipe printed via Moonraker, START_PRINT macro executed correctly
- OctoPrint 1.11.8: operational, API key active, autoconnect on ttyUSB0 working

---

## Known Issues / Caveats

- **Penelope USB drops** — connection closes frequently, requires reconnect via API before each print. Root cause: USB cable or port instability on Salomon. Fix: Pi Zero 2W (Klipper upgrade, Option 2) — approved by Javier, hardware pending.
- **Calliope maker's mark squished** — first layer over-squished on bottom, covering embossed maker's mark. Root cause unknown (Calliope Z offset or first layer height in profile). Not yet fixed — Javier stopped investigation.
- **Penelope slicing pipeline** — must use OrcaSlicer + Penelope-Standard-TreeSupports.json profile. Never use Creality Print or Calliope profiles for Penelope. Documented in bug report 2026-06-21.
- **M290 babystep not persistent** — babystepping resets on each print start. Physical endstop calibration is the only durable fix on stock Marlin without probe.

---

## What's Next

- Hardware: Pi Zero 2W for Penelope → Klipper + Moonraker install (Option 2, approved)
- Calliope maker's mark squish — investigate first layer height in Calliope-Production profile
- Penelope EEPROM: once on Klipper, Z offset stored properly in printer.cfg

*— Claude*

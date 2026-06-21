---
title: Session Report — Penelope Mario Pipe + Z Offset Fix
agent: Claude
date: 2026-06-21
tags: [djinn, report, penelope, printing, zoffset, treesupports]
related: [[build-log]] | [[decision-log]] | [[2026-06-20_penelope-live]]
---

# Session Report — Penelope Mario Pipe + Z Offset Fix

**Date:** 2026-06-21
**Agent:** Claude
**Session type:** Build / Debug / Ops
**Trigger:** Mario pipe print failing on Penelope; Z offset not set; Creality Print gcode incompatibility discovered

---

## Summary

Penelope (Ender 3 Pro) had three stacked problems preventing the mario pipe from printing: a checksum resend loop bug in OctoPrint serial config, an unset Z offset (nozzle too far from bed), and Creality Print gcode containing Klipper-specific macros incompatible with Marlin. All three were diagnosed and fixed. Mario pipe printed successfully with tree supports and 8mm brim. Z offset -0.5mm saved permanently to EEPROM. OrcaSlicer desktop launcher and terminal command added.

---

## What Was Built or Changed

- **`Penelope-Standard-TreeSupports.json`** — new OrcaSlicer process profile: tree supports (auto, 30° threshold), 8mm brim added after first adhesion failure
- **Z offset -0.5mm** — saved to Penelope EEPROM via `M851 Z-0.5` + `M500`; permanent across restarts
- **OrcaSlicer desktop launcher** — `/home/drmanzo/.local/share/applications/orca-slicer.desktop` + `OrcaSlicer` symlink in `/usr/local/bin/`
- **`~/Desktop/Review/`** — new intake gate: all STLs/3MFs dropped here before any print action
- **OctoPrint serial config fixed** — `alwaysSendChecksum: false`, `neverSendChecksum: true` (was causing Marlin resend loop)
- **Mario pipe** — printed successfully on Penelope: tree supports, 8mm brim, 5.5mm Bowden retraction, bed 65°C/hotend 210°C

---

## Technical Decisions

**Disable forced checksums → Why:** `alwaysSendChecksum: true` was added to fix firmware warning but caused Marlin to enter a resend loop requesting line 1 indefinitely. Creality Marlin handles checksums natively; forcing them via OctoPrint creates protocol conflicts. Disabled with `neverSendChecksum: true`.

**Reject Creality Print gcode for Penelope → Why:** Creality Print V7 slices for Klipper (Calliope). Start sequence uses `START_PRINT EXTRUDER_TEMP=220 BED_TEMP=65`, `SET_VELOCITY_LIMIT`, `EXCLUDE_OBJECT` — all Klipper macros. Marlin silently ignores them: bed never heats, nothing prints. OrcaSlicer with Penelope-specific profiles is the correct pipeline.

**8mm brim added to TreeSupports profile → Why:** Mario pipe is a tall narrow cylinder. Without brim, first layer had insufficient contact area for adhesion. 8mm brim added permanently to `Penelope-Standard-TreeSupports.json`.

**Z offset babystepped live then saved to EEPROM → Why:** Offset was unknown at cold start. Babystepped -0.3mm then -0.2mm (total -0.5mm) during print until first layer visually confirmed good. Saved with `M851 Z-0.5` + `M500` so it survives restarts.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard-TreeSupports.json   ← new: tree supports + 8mm brim
~/.local/share/applications/orca-slicer.desktop                                               ← new: desktop/apps launcher
/usr/local/bin/OrcaSlicer                                                                      ← new: terminal symlink
~/.octoprint-penelope/config.yaml                                                              ← serial checksum fix
~/Desktop/Review/                                                                              ← new intake folder
```

---

## Dependencies Installed

None.

---

## Tests & Validation

- Mario pipe printed successfully: tree supports generated (174 sections), brim gripped, print completed
- Z offset confirmed via visual first layer inspection during print: lines clear, no shadowing
- OrcaSlicer terminal command verified: `OrcaSlicer --version` → `OrcaSlicer-2.3.2`
- OctoPrint reconnect after checksum fix: State = Operational, no resend loop

---

## Known Issues / Caveats

- Z offset -0.5mm saved is based on visual babystep calibration, not a proper first-layer test. Run a dedicated Z offset test print (single-layer square) to fine-tune before production prints.
- Penelope time estimates from OrcaSlicer jump during tree support recalculation — not a bug, just imprecise until supports are fully computed.
- Creality Print gcode must never be sent to Penelope — it is Klipper-only. OrcaSlicer + Penelope profiles is the only valid pipeline.

---

## What's Next

- [ ] Run small Z offset test print on Penelope to fine-tune -0.5mm — @Javier approves, Claude sends
- [ ] Wire OctoPrint event notifications to Telegram/Discord for Penelope — @Claude
- [ ] Add `confirm N` safety gate for Penelope (currently no gate, direct print) — @Claude
- [ ] Build PETG/ABS/TPU filament profiles for Penelope (Marcus report has specs) — @Claude
- [ ] Phase 2 CLI: `--printer penelope` flag across djinn-model-slice — @Claude
- [ ] Print filament guide on Calliope (gcode uploaded, awaiting per-job approval) — @Javier

---

*— Claude, 2026-06-21*

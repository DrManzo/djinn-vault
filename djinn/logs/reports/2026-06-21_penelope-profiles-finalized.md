---
title: Session Report — Penelope Profiles Finalized + Manual Needed
agent: Claude
date: 2026-06-21
tags: [djinn, report, penelope, profiles, orcaslicer]
related: [[build-log]] | [[decision-log]] | [[2026-06-21_penelope-mario-pipe-zoffset]]
---

# Session Report — Penelope Profiles Finalized

**Date:** 2026-06-21
**Agent:** Claude
**Session type:** Build / Calibration
**Trigger:** Stock OrcaSlicer profile produced better first-layer results than Penelope-PLA profile on test print; profiles updated to match validated settings

---

## Summary

Test print using OrcaSlicer stock generic profile printed with excellent uniformity and layer adhesion. Comparison led to adopting 220°C hotend temp (vs 210°C), keeping 5.5mm Bowden retraction, and standardizing all Penelope profiles on gyroid infill at 14% with tree(auto) supports. All four process profiles and the filament profile updated. Desktop intake gate (~/Desktop/Review/) established.

---

## What Was Built or Changed

- **All Penelope process profiles** — gyroid infill, 14% density, 220°C hotend
- **Penelope-PLA.json** — temp raised from 210°C → 220°C, retraction stays 5.5mm
- **Penelope-Standard-Supports.json** — tree(auto) supports, 30° threshold, 1 wall (thin/minimal)
- **Penelope-Standard-TreeSupports.json** — same, plus 8mm brim
- **`~/Desktop/Review/`** — mandatory print intake gate for all STLs/3MFs

---

## Technical Decisions

**220°C over 210°C → Why:** Stock OrcaSlicer profile (220°C) produced visually superior first layer and infill vs our 210°C. PLA flows more uniformly at 220°C on this printer. Validated by direct comparison.

**5.5mm retraction kept → Why:** Bowden tube requires higher retraction than direct drive. Stock profile used 4mm but Penelope's Bowden path is ~40cm — 5.5mm is safer for preventing stringing on travel moves.

**Gyroid 14% for all → Why:** Gyroid is isotropic (equal strength in all directions), prints faster than grid, and works better at low densities. 14% is the minimum for functional prints without print-through on top surfaces.

**Tree(auto) only for support profiles → Why:** Tree supports minimize contact points, use less material, and are easier to remove. Auto mode means OrcaSlicer only generates where geometry requires it — not blanket support.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/forge-slicer/profiles/filament/Penelope-PLA.json         ← 220°C
~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard.json     ← gyroid 14%
~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Production.json   ← gyroid 14%
~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard-Supports.json      ← tree(auto) + gyroid 14%
~/Obsidian/djinn/printer/forge-slicer/profiles/process/Penelope-Standard-TreeSupports.json  ← tree(auto) + brim + gyroid 14%
```

---

## Tests & Validation

- `Tiny_Printer_Test_v1_PLA_34m51s.gcode` — stock OrcaSlicer profile — uniform infill, clean first layer, consistent extrusion confirmed visually by Javier
- Z offset -0.5mm held from cold start (EEPROM save confirmed working)

---

## Known Issues / Caveats

- Retraction comparison (4mm stock vs 5.5mm ours) not yet tested on tall prints with travel moves — stringing risk at 4mm on Bowden not ruled out
- No PENELOPE-MANUAL.md exists yet — Marcus to write

---

## What's Next

- [ ] Marcus writes `PENELOPE-MANUAL.md` (see prompt below) — vault at `~/Obsidian/djinn/printer/`
- [ ] Run tall/travel-heavy test to validate 5.5mm retraction vs stringing
- [ ] Wire OctoPrint events → Telegram/Discord — @Claude
- [ ] `confirm N` gate for Penelope — @Claude

---

*— Claude, 2026-06-21*

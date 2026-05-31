---
title: Session Report — Mini Vases Job #4
agent: Salomon
date: 2026-05-31
tags: [djinn, report, print, job4]
related: [[build-log]] | [[decision-log]] | [[COMMS]]
---

# Session Report — Mini Vases Job #4

**Date:** 2026-05-31
**Agent:** Salomon
**Session type:** Ops
**Trigger:** Javier requested Mini+Vase+Tray.zip vases sliced and printed

---

## Summary

Sliced 3 mini vases (Double Spiral, Spiral, Straight) from Mini+Vase+Tray.zip on one plate, standing upright with bases on bed. Added 5mm brim and TF anvil maker's mark engraved on bottom of each. Gcode uploaded to queue. Discovered and filed bug where maker's mark engraving reads reversed on bottom surfaces. Routed fix to Claude via TASK-004 in QUEUE.md.

---

## What Was Built or Changed

- **Sliced gcode:** `queue/mini-vases_job4.gcode` — 3 vases on one plate, centered, brim, engraved bottoms
- **Engraved STLs:** `/tmp/mini-vases-engraved2/` — corrected mirror orientation for bottom reading
- **Bug report:** `reports/2026-05-31_bug-maker-s-mark-engraving-reads-reversed-on-bottom-surfaces.md`
- **Queue task:** TASK-004 added to QUEUE.md for Claude — fix mirroring + configurable maker's mark

---

## Technical Decisions

- **Rotation +90° around X** — Original STLs were lying on side (50mm on Y axis). Rotated 90° around X to stand upright. Base (largest flat face, normal 0,-1,0) correctly maps to bottom (0,0,-1).
- **Mirrored anvil before cut** — Anvil STL logo faces +Z. To read correctly from bottom (-Z view), mirrored across X axis before boolean subtract. Face winding reversed to maintain manifold.
- **OrcaSlicer CLI** — Used for final slice with Creality Ender-3 V3 Plus system profiles + 0.20mm Standard process profile. Brim enabled by default at 5mm.
- **PrusaSlicer fallback** — Consult dry-run uses prusa-slicer. OrcaSlicer used for actual plate slicing (multi-model arrangement).

---

## Files Created or Modified

```
Obsidian/djinn/printer/queue/mini-vases_job4.gcode     ← sliced plate gcode
Obsidian/djinn/communications/COMMS.md                  ← appended session entries
Obsidian/djinn/communications/QUEUE.md                  ← added TASK-004 for Claude
Obsidian/djinn/logs/reports/2026-05-31_bug-maker-s-mark-engraving-reads-reversed-on-bottom-surfaces.md
Obsidian/djinn/logs/bugs.md                             ← bug index updated
Obsidian/djinn/logs/build-log.md                        ← build log updated
```

---

## Tests & Validation

- STL boolean operations verified: manifold3d engine works, all 3 vases engraved cleanly
- Gcode inspected: 250 layers, Z=0.2–50mm, brim present, no supports, START_PRINT macro
- OrcaSlicer slice: success, 5h40m estimated, 40.4g PLA
- Reference comparison: checked `marked.stl` orientation against cup print workflow

---

## Known Issues / Caveats

- Maker's mark mirroring fix applied manually this session. Permanent fix deferred to Claude (TASK-004).
- OrcaSlicer CLI required explicit `--load-settings` with both machine + process system profiles. Custom user profiles may not inherit `before_layer_change_gcode` properly.

---

## What's Next

- [ ] Fix maker's mark mirroring permanently + make configurable — @Claude (TASK-004)
- [ ] Upload gcode to printer when Javier confirms
- [ ] Verify engraving reads correctly on physical print

---

*— Salomon, 2026-05-31*

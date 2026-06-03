---
title: Proxy Stands — Typhons Forge + Terp Tribe HQ
date: 2026-06-02
status: ready-to-print
tags: [proxy-stand, typhons-forge, terp-tribe, pla, calliope]
---

# Proxy Stands — Job Archive

**Brands:** Typhons Forge + Terp Tribe HQ  
**Date:** 2026-06-02  
**Printer:** Calliope (Ender-3 V3 Plus)  
**Material:** PLA  

---

## Files

| File | Type | Notes |
|------|------|-------|
| `Proxy_Stand_typhons_forge_final.stl` | STL | Engraved "TYPHONS FORGE" + bore 42.4mm + maker's mark |
| `Proxy_Stand_terp_tribe_hq_final.stl` | STL | Embossed "TERP TRIBE HQ" + bore 42.4mm + maker's mark |
| `combined_plate_2_3.stl` | STL | Both stands plated together (do not use — causes key561) |
| `Proxy_Stand_TF_solo_patched.gcode` | GCODE | ✅ Use this — M106 S255→S128 patched |
| `Proxy_Stand_TTHQ_solo_patched.gcode` | GCODE | ✅ Use this — M106 S255→S128 patched |

---

## Print Settings

- Layer: 0.20mm
- Walls: 3
- Infill: 15%
- Supports: tree (auto)
- Brim: NO
- Nozzle: 215°C / Bed: 60°C
- Print solo — one stand at a time

---

## Key Notes

- **Do NOT use combined plate** — two objects causes the combined gcode to run >52min which exceeds cable tolerance window
- **M106 S255 is patched to S128** in both gcode files — PrusaSlicer bridge fan at full speed kills nozzle_mcu via EMI (key561). S128 = 50% fan, enough for bridge cooling
- **Print order:** TF first, then TTHQ
- **After TF completes:** start TTHQ immediately, no need to re-home or re-mesh

---

## Geometry

- Outer diameter: 62mm
- Inner bore: 42.4mm (prints ~42.1mm — snug fit for 42mm glass)
- Height: 21.1mm
- Text: 6-8mm Liberation Bold, 1.4mm depth
- Maker's mark: TF anvil 15mm, 0.5mm deep, bottom face

---

*Archived by Claude, 2026-06-02*

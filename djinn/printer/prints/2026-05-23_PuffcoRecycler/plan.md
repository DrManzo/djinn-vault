# Print Plan — Puffco Proxy Quad Uptake Recycler

**Date:** 2026-05-23
**Slicer:** OrcaSlicer 2.3.2
**Printer:** Creality Ender-3 V3 Plus (Klipper)
**Status:** Sliced, ready for review

## Model Analysis

| Property | Value |
|----------|-------|
| Source | `Proxy+Tornado+Recycler.3mf` (MakerWorld Bambu profile) |
| Type | Puffco Proxy quad-uptake recycler water attachment |
| Dimensions | 85 × 153 × 219.5 mm |
| Triangles | 25,362 |
| Parts | 2 (needs manifold repair — 17 open edges originally) |
| Volume | ~147.2 cm³ |
| Weight (PLA) | ~183g |
| Fits Ender-3 V3+ | ✅ X: 85mm (215mm clearance), Y: 153mm (147mm clearance), Z: 219.5mm (115.5mm clearance) |

## Supports

**Needed: YES — confirmed**
- 34.2% of triangles face downward (overhangs)
- Original slice had `support_used: true`
- Internal chambers + 4 uptake tubes + return path all need support material
- Type: Normal (auto), build-plate only, 25° threshold

## Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| Layer height | 0.16mm | User preference — detail for uptake tubes |
| First layer | 0.2mm | Better bed adhesion for tall print |
| Walls | 4 | Watertight chamber walls |
| Infill | 15% gyroid | User approved — strong/light balance |
| Top shells | 5 | Smooth mouthpiece surface |
| Bottom shells | 4 | Solid base for chamber |
| Filament temp | 220°C / 55°C bed | Standard PLA |
| Fan | 30-80% (ramp), off first 2 layers | PLA cooling profile |
| Supports | Normal auto, build-plate only, 25° | Prevents internal collapse |
| Brim | 5mm auto | Adhesion for 219mm tall print |
| Retraction | 0.6mm @ 40mm/s | Direct drive, minimal stringing |
| Speed | 60mm/s outer, 150mm/s inner | Quality outer, fast inner |
| Travel speed | 400mm/s | Reduces print time |

## Filament

- **Loaded:** PLA (white/unspecified)
- **Note:** Specs recommend PETG/ABS for watertight thermal parts. PLA is a prototype test.

## Gcode Summary

- **File:** `puffco_proxy_recycler.gcode`
- **Layers:** 1980 (with supports)
- **Estimated time:** ~13.7h (822 min) at 0.16mm
- **G-code flavor:** Klipper
- **Start routine:** Preheat → G28 → wait for temps (bypasses START_PRINT macro)
- **Moonraker URL:** http://192.168.1.114:7125

## Critical Lessons Applied (from cup print debugging)

1. **Fan off first layer** — prev cup failures caused by PrusaSlicer fan ramp at brim→layer 1 (EMI on nozzle_mcu serial). This gcode keeps `M106 S0` for early layers.
2. **Preheat before homing** — `M140 S55` / `M104 S220` before `G28`. Avoids cold-start verify_heater issues.
3. **Relaxed verify_heater** — already in printer.cfg: check_gain_time=120, max_error=999, hysteresis=20 on extruder.
4. **No Bambu macros** — stripped all Bambu-specific gcode. Uses direct Klipper commands.

## Status

✅ Model extracted and centered
✅ Supports verified needed
✅ Gcode sliced successfully
⏳ User review before upload/print

— Salomon

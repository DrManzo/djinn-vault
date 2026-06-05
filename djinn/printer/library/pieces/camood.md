---
id: camood
name: The Terp Tribe — Camood
category: external
platform: terp-tribe
creator: The Terp Tribe
license: commercial-product
compliance_status: owned
date_acquired: 2026-05-30
date_processed: pending
tags: [proxy-accessory, terp-tribe, tthq, external, camood]
---

# The Terp Tribe — Camood

## Attribution

| Field | Value |
|-------|-------|
| **Source** | The Terp Tribe (commercial product) |
| **License** | Commercial purchase — physical product scanned/modeled |
| **Commercial use** | ✅ Internal use / Terp Tribe HQ brand only |

---

## Description

The Camood is a Terp Tribe branded proxy accessory. Irregular organic shape — 66×108×107mm. Features a flat back panel ("tank") starting at bed Z ~55mm. Main body has consistent outer radius ~48–52mm in the lower section. Inner bore: ~9.2mm at base (joint), ~26–38mm in chamber.

---

## Geometry

| Property | Value |
|----------|-------|
| Dims | 66.04 × 108.19 × 107.28 mm |
| Z range | 0 → 107.28 mm (bed-aligned) |
| Faces | 18,436 |
| Watertight | ✅ Yes |
| Volume | 249.83 cm³ |
| Back panel (tank) | Z=56–98mm (42mm tall), actual surface at Y=+51.55mm from center |
| Back panel width | ~61mm (X=−30.5 to +30.5mm) |
| Lower bore | ~9.2mm (joint/base) |
| Chamber bore | ~26–38mm (varies by Z) |

**Note:** Bounding box Y=54.09mm is a different part of the model — the flat tank back face is at Y=51.553mm (confirmed by ray-cast).

---

## Files

| Type | Path |
|------|------|
| Original | `~/printer-files/library/originals/terp-tribe/The Terp Tribe - Camood.stl` |
| Engraved (print-ready) | `~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl` |
| Engrave script | `~/printer-files/scripts/camood_tthq_engrave.py` |
| **Print config (reusable)** | `~/printer-files/library/engraved/terp-tribe/Camood_print_config.json` |

## To Re-Print (Future Runs)

1. **Same text** — gcode already sliced. Queue it: `djinn-confirm-print <new_id>` after adding to queue
2. **Different text** — edit `TEXT` in `camood_tthq_engrave.py`, re-run script, re-slice with `Camood_print_config.json` settings
3. **Slicer settings are frozen** in `Camood_print_config.json` — material, temps, supports, layer height, everything

---

## Processing Log

**Status:** ✅ Engraved — "Terp Tribe HQ" DancingScript-Bold on back tank panel.

| Step | Detail |
|------|--------|
| Text | "Terp Tribe HQ" · DancingScript-Bold · 9mm cap height |
| Position | X centered, Z=71mm (6mm below tank center 77mm) |
| Depth | 1.8mm into back face |
| Volume removed | 0.121 cm³ (0.011 cm³/char — LG-3 ✅) |
| Mirror | Text X-mirrored so it reads correctly viewed from outside |
| Maker's mark | TF anvil 15mm, 0.5mm depth, bottom face center-rear (Y=−10) |
| Tool | fontTools glyph → shapely → trimesh.extrude_polygon → manifold3d boolean |
| Output faces | 30,432 · watertight ✅ |

---

## Print Notes

- Tall piece (107mm) — check bed leveling
- No brim
- **Supports:** organic tree, buildplate-only, Z cap at 50mm (via 3MF support blocker). Catches bottom curves/corners only
- Text on back tank face — visible when oriented naturally
- No bore modification (used as-is)

## Print History

| Date | Qty | Material | Time | Status |
|------|-----|----------|------|--------|
| 2026-06-04 | 4 | PLA | 25h 30m | 🔄 Printing |

---

*— Claude, 2026-06-04*

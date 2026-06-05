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
| Centered (XY origin) | `~/printer-files/staging/camood_centered.stl` |
| Engraved (print-ready) | `~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl` |

---

## Processing Log

**Status:** ✅ Engraved — "Terp Tribe HQ" DancingScript-Bold on back tank panel.

| Step | Detail |
|------|--------|
| Text | "Terp Tribe HQ" · DancingScript-Bold · 9mm cap height |
| Position | X centered, Z=71mm (6mm below tank center 77mm) |
| Depth | 1.8mm into back face |
| Volume removed | 0.121 cm³ (0.011 cm³/char — LG-3 ✅) |
| Tool | fontTools glyph → shapely → trimesh.extrude_polygon → manifold3d boolean |
| Output faces | 29,984 · watertight ✅ |

---

## Print Notes

- Tall piece (107mm) — check bed leveling
- Print with back panel facing front of bed for best surface quality
- No supports needed
- Text is on back tank face — visible when piece is oriented naturally
- No bore modification (used as-is)

---

*— Claude, 2026-06-04*

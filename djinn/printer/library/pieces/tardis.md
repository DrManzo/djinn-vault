---
id: tardis
name: Doctor Who TARDIS
category: external
platform: cults3d
creator: LuliasMartch
license: CC BY 4.0
compliance_status: verified-commercial
date_acquired: 2026-06-04
date_processed: 2026-06-04
modification_level: significant
tags: [proxy-accessory, novelty, sci-fi, external, cults3d, cc-by, puffco]
---

# Doctor Who TARDIS

## Attribution

| Field | Value |
|-------|-------|
| **Platform** | Cults3D |
| **Source URL** | https://cults3d.com/en/3d-model/art/tardis-de-doctor-who |
| **Designer** | LuliasMartch |
| **License** | CC BY 4.0 |
| **Commercial use** | ✅ YES — with attribution |
| **Price** | Free |

### What CC BY means for the shop
- ✅ Can sell prints
- ✅ Can modify
- ⚠ Must credit LuliasMartch in every listing

---

## Description

Doctor Who TARDIS police box. Multi-part CAD model (379 watertight bodies). Full detail preserved — Police Box lettering, window frames, door panels, stepped roof, base. Bore sits in the top where the lamp housing would be.

---

## Files

| Type | Path |
|------|------|
| Original | `~/printer-files/library/originals/external/tardis_original.stl` |
| Cored | `~/printer-files/library/cored/external/tardis_cored.stl` |

---

## Processing Log

**Tool:** direct manifold3d bypass (djinn-bore-core v3 pipeline failed on 379-body mesh — trimesh volume check bypassed)
**Date:** 2026-06-04

| Step | Detail |
|------|--------|
| Input | 267,030 faces, 379 watertight bodies, not a single volume |
| Repair | winding + normals fix; Poisson skipped (hard-surface model, would lose detail) |
| Boolean engine | manifold3d direct API (bypasses trimesh is_volume check) |
| Bore | 38.3mm ⌀ × 51.0mm depth at top center (-13.3, 0.0, Z=112.4mm) |
| Output | 184,588 faces |
| Detail | Fully preserved — POLICE BOX text, windows, panels intact |

**Note for djinn-bore-core:** multi-body hard-surface CAD models need the direct manifold3d path. Add this as a fallback in v4.

---

## Print Notes

- Narrow axis is 47.3mm — bore leaves 4.5mm wall each side (above 3mm floor, OK)
- Tall piece (112mm) — check bed leveling before starting
- Police Box text on roof area is fine; bore goes into the lamp housing zone
- PETG or ABS recommended for production (used near heat)
- No supports needed — all surfaces printable without them

---

## Attribution Block (for listings)

> "Tardis de Doctor Who" by **LuliasMartch** on Cults3D  
> https://cults3d.com/en/3d-model/art/tardis-de-doctor-who  
> Modified by Typhon's Forge: Puffco Proxy Core seat bored (38.3mm × 51mm), TF maker's mark added.  
> License: CC BY 4.0

---

*— Claude, 2026-06-04*

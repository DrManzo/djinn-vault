---
id: applacrabus
name: Applacrabus (Apple with Crab Claws)
category: external
platform: cults3d
creator: Midnight3DPrinting
license: CC BY-SA 4.0
compliance_status: verified-commercial
date_acquired: 2026-06-04
date_processed: 2026-06-04
tags: [proxy-accessory, art, external, puffco, terp-tribe, cc-by-sa]
---

# Applacrabus — Apple with Crab Claws

## Attribution

| Field | Value |
|-------|-------|
| **Platform** | Cults3D |
| **Source URL** | https://cults3d.com/en/3d-model/art/applacrabus |
| **Designer** | Midnight3DPrinting |
| **License** | CC BY-SA 4.0 |
| **Commercial use** | ✅ YES — with attribution + ShareAlike on derivatives |
| **Price** | Free |

### What CC BY-SA means for the shop

- ✅ Can sell prints
- ✅ Can modify (bore, scale, engrave)
- ⚠ Must credit Midnight3DPrinting in every listing
- ⚠ Modified versions must carry the same CC BY-SA 4.0 license

---

## Description

Art piece — a forest spirit that became a monster: apple body elevated on four crab-claw legs. Originally published to Thingiverse in September 2024 by Midnight3DPrinting, mirrored to Cults3D. First Proxy Core accessory body processed through the Typhon's Forge pipeline. Novelty / conversation piece category.

---

## Files

| Type | Path |
|------|------|
| Original (untouched) | `~/printer-files/library/originals/external/applacrabus_original.stl` |
| Cored (print-ready) | `~/printer-files/library/cored/external/applacrabus_cored.stl` |

---

## Processing Log

**Tool:** djinn-bore-core v3 | **Date:** 2026-06-04

| Step | Detail |
|------|--------|
| Input mesh | 55,211 faces — NOT watertight (5 disconnected bodies, 73 open edges) |
| Auto-scale | ×46.678 — meters-as-mm → 76mm target height |
| Proportional scale | Fell back to uniform (extreme aspect ratio — proportional footprint too narrow for 38mm bore) |
| Mesh repair | Poisson surface reconstruction → 127,168 faces, is_volume=True |
| Bore | 38.3mm ⌀ × 51.0mm depth — Puffco Proxy Core seat |
| Wall thickness | 5.1mm ✓ |
| Columns | OK (claw legs below bore floor, passed threshold) |
| Maker's mark | TF anvil 15mm, 0.5mm depth, bore floor, no mirror |
| Output | 120,118 faces |
| Material (test) | PLA (prototype) — PETG/ABS/ASA for production |

---

## Print Notes

- Claw legs are thin — slow perimeter speed, 3+ walls
- No supports needed
- Bore is snug — test fit before committing to final material
- PETG minimum for any piece used near heat; ABS/ASA for regular sessions

---

## Attribution Block (for product listings)

> "Applacrabus" by **Midnight3DPrinting** on Cults3D  
> https://cults3d.com/en/3d-model/art/applacrabus  
> Modified by Typhon's Forge: scaled to fit, Puffco Proxy Core seat bored (38.3mm × 51mm), TF maker's mark added to bore floor.  
> License: CC BY-SA 4.0 — https://creativecommons.org/licenses/by-sa/4.0/

---

*— djinn-bore-core v3 / Claude, 2026-06-04*

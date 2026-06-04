---
id: applacrabus
name: Appla Crabus (Apple with Crab Claws)
category: external
platform: cults3d
compliance_status: pending-review
date_acquired: 2026-06-04
date_processed: 2026-06-04
tags: [proxy-accessory, art, external, puffco, terp-tribe]
---

# Appla Crabus — Apple with Crab Claws

## Attribution

| Field | Value |
|-------|-------|
| **Platform** | Cults3D |
| **Source URL** | https://cults3d.com/en/3d-model/art/applacrabus |
| **Designer** | ⚠ PENDING — verify on Cults3D page |
| **License** | ⚠ PENDING — verify on Cults3D page |
| **Commercial use** | ⚠ UNKNOWN — must confirm before listing |

> **Action required:** Go to the Cults3D page, record the designer handle and license type here. If license is personal-only or NC, this piece cannot be sold — use only for display/personal pieces. Update `compliance_status` in `index.json` to `verified-commercial` or `verified-personal-only`.

---

## Description

Art piece — apple body elevated on four crab claw legs. Used as the first Proxy Core accessory body in the Typhon's Forge pipeline. Decorative / conversation piece category.

---

## Files

| Type | Path |
|------|------|
| Original (untouched) | `~/printer-files/library/originals/external/applacrabus_original.stl` |
| Cored (print-ready) | `~/printer-files/library/cored/external/applacrabus_cored.stl` |

---

## Processing Log

**Tool:** djinn-bore-core v3  
**Date:** 2026-06-04

| Step | Detail |
|------|--------|
| Input mesh | 55,211 faces, NOT watertight (5 disconnected bodies, 73 open edges) |
| Auto-scale | ×46.678 — detected meters-as-mm, scaled to 76mm target height |
| Proportional scale | Fell back to uniform (proportional footprint too narrow for 38mm bore) |
| Mesh repair | Poisson surface reconstruction (pymeshlab depth=8) → 127,168 faces, watertight |
| Bore | 38.3mm ⌀ × 51.0mm depth — Puffco Proxy Core seat |
| Wall thickness | 5.1mm ✓ |
| Support columns | OK (crab claws below bore floor — passed threshold check) |
| Maker's mark | TF anvil, 15mm, 0.5mm depth, bore floor, no mirror |
| Output | 120,118 faces |
| Material (test) | PLA (prototype only) |

---

## Print Notes

- Crab claw legs are thin — print slowly, 2–3 perimeters minimum
- No supports needed (claws are self-supporting at this scale)
- Bore is tight-fit for Proxy Core — test fit before final material
- Recommend PETG minimum for any piece that will be used; ABS/ASA for regular use near heat

---

## Attribution Block (for product listings)

> "Appla Crabus" by **[DESIGNER — fill in]** on Cults3D  
> Original: https://cults3d.com/en/3d-model/art/applacrabus  
> Modified by Typhon's Forge: scaled, Puffco Proxy Core seat bored (38mm × 51mm), TF maker's mark added.  
> License: **[LICENSE — fill in]**

---

*— djinn-bore-core v3, 2026-06-04*

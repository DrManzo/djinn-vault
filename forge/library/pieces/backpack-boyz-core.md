---
id: backpack-boyz-core
name: Backpack Boyz — Core
category: external
platform: commission/forge
creator: Backpack Boyz (brand)
license: internal-use
compliance_status: forge-work
date_acquired: 2026-06-29
date_processed: 2026-06-29
tags: [proxy-accessory, backpack-boyz, external, forge, core]
---

# Backpack Boyz — Core

## Attribution

| Field | Value |
|-------|-------|
| **Source** | Backpack Boyz brand commission / forge work |
| **License** | Internal forge — brand IP, no public sale |
| **Commercial use** | Internal only — brand collaboration |

---

## Description

Backpack Boyz branded proxy accessory core. Large organic form with straps and dangling charm elements at lower back corners. 447k verts / 894k faces — watertight. Support grid base added (1.2mm bars, 8mm spacing, 3mm tall) for bed adhesion without a solid slab base.

**Correction, 2026-07-16:** the version referenced below under "Files" (`Backpack_Boyz_Core.stl` etc.) turned out to not exist anywhere anymore — the whole `~/printer-files/library/calliope/backpack-boyz/` path is gone (pre-migration path, never carried forward). The genuine original, provided directly by Javier, is a **much smaller piece** than this description implies: 42.9 × 43.8 × 50.0mm, 33.78 cm³, 897,668 faces (after removing 176 microscopic debris fragments left over from export — the real body was already watertight on its own).

## Bore Location — Found by Cross-Section Scan, Confirmed by Javier

The piece has a **free-standing cylindrical boss at the top** — not embedded in the solid mass, so `djinn-bore-core`'s standard wall-thickness safety check (designed for boring into bulk material) reads it as a false failure. Confirmed via Z-axis cross-section scan: cross-sectional area holds essentially constant (~418mm²) from **Z=37.5mm to Z=48.5mm** (an 11mm span), consistent with a true ~23mm-diameter cylinder — above Z=48.5 it necks into a small domed cap (113.7mm² at the very top, Z=49.5), which is what `--top-mode auto`'s "true center" detection kept incorrectly targeting instead of the real boss.

**Correct bore command** (verified clean — no scale drift, watertight, sensible volume removed):

```
djinn-bore-core <clean_original.stl> \
  --diameter 18.0 --depth 15.0 \
  --top-mode manual --top-z 48.0 \
  --target-height 50.0 --material pla \
  --no-mark --output <out.stl>
```

Do **not** use `--top-mode auto` on this piece — it targets the wrong (dome-cap) location. Do **not** use `--strict` for the final run — the wall-thickness warning (1.7mm) is a legitimate false-positive for this free-standing-boss geometry, confirmed correct by Javier after reviewing the auto-detected location vs. the real cylinder. `--strict` is still worth using during *diagnosis* (it correctly refused two bad attempts before this one — see [[2026-07-16_shop-dashboard-hardening-nemesis-profile-fix]] region of build-log for the full diagnostic trail), just not on the final confirmed-correct run.

Maker's mark must be applied as a **separate** `djinn-model-mark` call on a file whose name does *not* end in `_bored` — that tool has its own filename-heuristic bug, see [[2026-07-16_bug-djinn-model-mark-filename-heuristic-false-positive-skip]].

---

## Slicer Notes

| Setting | Value |
|---------|-------|
| Layer height | 0.08mm (fine detail) |
| Walls | 3 |
| Infill | 15% |
| Brim | 3mm |
| Supports | Tree/Organic, buildplate-only |
| Material | PLA (PETG/ASA for production) |
| Fan | Cap S128 max |
| Est. weight | ~334g PLA |
| Est. time | 18–24h at 0.08mm |

Support strategy: organic supports for strap undersides (Z=80-105mm) and tree supports from bed for dangling back corner charms.

Post-process gcode: `djinn-gcode-safety <gcode> --fan-cap 128`

---

## Files

| Type | Path |
|------|------|
| Core (forge) | `~/printer-files/library/calliope/backpack-boyz/Backpack_Boyz_Core.3mf` |
| Core STL | `~/printer-files/library/calliope/backpack-boyz/Backpack_Boyz_Core.stl` |
| Original | `~/printer-files/library/calliope/backpack-boyz/Backpack_original.stl` |
| Original 3MF | `~/printer-files/library/calliope/backpack-boyz/Backpack Boyz_ORIGINAL.3mf` |
| Bored variant | `~/printer-files/library/calliope/backpack-boyz/Backpack Boyz_bored.stl` |
| V2 core | `~/printer-files/library/calliope/backpack-boyz/BackPack core_v2.stl` |
| Logo ref | `~/printer-files/library/calliope/backpack-boyz/bagpack boyz logo.jpg` |
| Slicer notes | `~/printer-files/library/calliope/backpack-boyz/Backpack_Boyz_Core_SLICER-NOTES.md` |

---

## Print History

| Date | Printer | Result | Notes |
|------|---------|--------|-------|
| — | — | — | Not yet printed |

---

*— Claude, 2026-06-29*

# Support Settings — Calliope Print Guide

*Ender-3 V3 Plus | PLA | Last updated 2026-05-27 — Claude*

---

## When to Use Supports

**Use supports:**
- Overhangs steeper than 45° from vertical (standard/production threshold)
- Bridging spans longer than ~50mm with nothing below
- Floating geometry — pieces of the model with no base underneath

**Skip supports:**
- Vases, cups, cylinders, bowls — any hollow part with a narrow opening
- Gradual curves with overhangs under ~20% — they bridge cleanly at 0.20mm layer height
- Parts where the shoulder or taper is the only overhang geometry

---

## The Hollow Part Problem

Supports inside hollow parts cannot be removed if the opening is too narrow to reach inside.

When a vase or cylinder has an inward-curving shoulder or neck, the overhang faces into the hollow interior. The slicer places supports directly below that overhang — which is inside the part. This happens regardless of orientation. There is no way to rotate a vase so that the shoulder overhang ends up on the outside.

**Rule:** For any hollow part with a narrow opening, always slice `supports=no`.
A gentle shoulder curve (5–15% overhang) will bridge cleanly at 0.20mm PLA. The
surface finish on the inside is slightly rough — which nobody sees.

---

## Making Supports Easier to Remove

Three settings control how hard support material is to pull out after printing.
Adjust these when supports are genuinely needed (structural parts, real overhangs)
and you want cleaner removal.

| Setting | Default (profile) | Easy-Remove | What it does |
|---|---|---|---|
| `support_material_contact_distance` | 0.2mm | 0.25mm | Air gap between support top and model surface. Larger gap = less fusing = cleaner break. |
| `support_material_interface_spacing` | 0mm (solid) | 0.2mm | Interface layer density. 0 = solid sheet that grips hard. 0.2 = sparse grid that snaps off. |
| `support_material_interface_layers` | 2 | 1 | Number of dense interface layers at contact point. Fewer = less bonded material. |

To apply easy-remove settings at slice time, tell Djinn — they can be set per-job.

---

## Slice Commands

```
slice N standard supports=no brim=yes        ← vases, cylinders, hollow parts
slice N standard supports=yes brim=yes       ← structural parts with real overhangs
slice N production supports=yes brim=yes     ← commission parts, full strength
slice N proto supports=no                    ← quick fit check, surface doesn't matter
```

---

## Calliope Profile Defaults

| Setting | Value |
|---|---|
| Support threshold | 45° (standard/production), 60° (proto) |
| Contact distance | 0.2mm |
| Interface layers | 2 |
| Interface spacing | 0mm (solid) |
| Pattern | Rectilinear |

---

## Quick Reference: Will the Slicer Fill the Inside?

| Model type | Infill inside? | Supports inside? |
|---|---|---|
| Solid cylinder/block | Yes — infill fills the interior volume | Only if overhangs > threshold |
| Hollow shell (vase, cup) | No — air space stays air | Yes, if shoulder/neck overhangs | 
| Vase mode (spiral) | No | No — single wall only, no roof |

---

*→ See also: [[PRINT-PROFILES]] for proto/standard/production settings*
*→ See also: [[printer/klipper-macros-webcam]] for START_PRINT / END_PRINT macros*

---

## Maker's Mark — Engraving Rule

**Tool:** `djinn-model-mark <model.stl>`

The TF anvil mark always goes on the **bottom face** (Z_min). Hidden on the shelf, visible when flipped.

**Mirror rule — NON-NEGOTIABLE:**
The mark STL logo faces +Z. When boolean-subtracted into a bottom face and viewed from below (-Z), it reads reversed without a mirror. `djinn-model-mark` applies the mirror automatically — you do not need to do it manually.

- **Built-in geometry** (no `--mark` flag): mirror is always applied. Use this for standard prints.
- **External STL mark** (`--mark path/to/mark.stl`): reads `mirror_x` from `~/.config/djinn/makers-mark.json`. Default is `true`. Pass `--no-mirror` only if your STL was pre-mirrored.

**Config:** `~/.config/djinn/makers-mark.json`
```json
{
  "path": "/home/drmanzo/Downloads/files/tf_anvil_traced_15mm.stl",
  "mirror_x": true,
  "size_mm": 15,
  "depth_mm": 0.5
}
```

To change the default mark: update `path` in the config. The `mirror_x: true` stays unless your new mark is already designed mirror-flipped.

**Never** subtract a mark STL directly into a bottom face without mirroring first. The config enforces this — if you bypass the tool, you own the result.

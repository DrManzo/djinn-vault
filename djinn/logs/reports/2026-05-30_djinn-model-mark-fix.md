---
title: Session Report — djinn-model-mark Fix
agent: Salomon
date: 2026-05-30
tags: [djinn, report, engraving, mark, 3dprint]
related: [[build-log]] | [[decision-log]] | [[djinn-model-mark]]
---

# Session Report — djinn-model-mark Fix

**Date:** 2026-05-30
**Agent:** Salomon
**Session type:** Fix + Ops

---

## Summary

Fixed `djinn-model-mark` for the TF Volcano/Anvil makers mark. Depth increased from 0.4mm to 0.5mm. X-mirror added so the brand reads correctly when viewing the bottom face (after flipping the print). Winding fix removed — it flipped normals inward causing negative boolean volume. Re-stamped "The Terp Tribe - Camood.stl" with corrected mark.

---

## What Was Built/Changed

- **`djinn-model-mark`** — depth: 0.4mm → 0.5mm; X-mirror restored; winding reversal removed (was inverting normals → boolean added instead of subtracted)
- **Camood re-stamped** — `prints/2026-05-30_183442_The Terp Tribe - Camood_marked/marked.stl` — 0.051 cm³ removed, watertight, 1 component

---

## Technical Decisions

- **X-mirror on mark geometry** — bottom face reads backwards without it when flipped. The brand must be mirrored in model space so it reads correctly from the physical bottom-view angle.
- **No winding fix** — `shapely_scale(xfact=-1.0)` already produces mirrored polygons with correct extrude winding. The `faces[:, ::-1]` reversal was redundant and flipped normals inward, making the boolean add material instead of subtract (negative volume delta).
- **z_min placement** — the original `z_min - 0.01` approach works correctly for flat-bottomed models. Ray-casting for curved surfaces explored but not needed here.

---

## Files Created/Modified

```
~/.local/bin/djinn-model-mark              Depth 0.4→0.5mm, mirror restored, winding fix removed
~/Obsidian/djinn/printer/prints/2026-05-30_183442_The Terp Tribe - Camood_marked/  ← new marked job
```

---

## Known Issues

- Negative volume delta from winding fix was resolved by removing the fix entirely
- The 0.00000 cm³ volume from earlier surface-aware placement was from cutter not overlapping model — resolved by reverting to z_min-based placement

---

## What's Next

- Mark the Camood for print (djinn-model-slice + confirm)

— Salomon

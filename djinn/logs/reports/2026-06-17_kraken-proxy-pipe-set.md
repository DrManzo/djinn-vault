---
title: Session Report — Kraken Proxy Pipe Set
agent: Claude
date: 2026-06-17
tags: [djinn, report, proxy, pipe, kraken, 3d-print]
related: [[build-log]] | [[decision-log]] | [[proxy-pipe-presculpted]] | [[proxy-core-presculpted-bowl]]
---

# Session Report — Kraken Proxy Pipe Set

**Date:** 2026-06-17
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier brought in Meshy AI Kraken2 sculpt to convert into a matched Proxy Core + Pipe set

---

## Summary

Turned a non-manifold Meshy AI Kraken2 3MF export into a complete Proxy pipe set — `Kraken_core.stl` and `Kraken_pipe.stl`. The model had a pre-sculpted cup so no boring was needed for the core; the pipe required a three-segment vapor path (vertical → bend at Z=80mm → angled into the back of the cup). Formalized the pipe workflow as `proxy-pipe-presculpted.md` so future pipes don't require iteration.

---

## What Was Built or Changed

- **`Kraken_core.stl`** — Scaled Kraken with maker's mark on cup floor (interior, un-mirrored)
- **`Kraken_original.stl`** — Clean scaled reference, no modifications
- **`Kraken_pipe.stl`** — Bored pipe: mouthpiece r=4 + vertical vapor r=5 + angled cup entry r=4 + exterior mark
- **`proxy-pipe-presculpted.md`** — New formalized workflow doc for pre-sculpted bowl pipes
- **`mesh_repair_agent/generate.py`** — Added manifold3d as step 2 primary fixer for complex organic sculpts

---

## Technical Decisions

**manifold3d over pymeshfix/trimesh for organic repair** — trimesh and pymeshfix both failed on the dense Meshy AI export. manifold3d was the only tool that produced a clean watertight result. Added as step 2 in mesh_repair_agent with fallback to raw-load path if the trimesh-pre-processed mesh yields 0 faces.

**Vapor path geometry: three segments** — Single straight vertical bore misses the cup entirely (the cup is at the front of the model, mouthpiece at the back-top). Three segments: vertical from tip → junction sphere at Z=80mm → angled bore into cup center. Junction sphere smooths the bend so there's no sharp 90° corner in the air path.

**Cup entry r=4, vertical channel r=5** — Mouthpiece and cup entry matched at r=4mm (8mm dia) for consistent restriction. Vertical channel wider at r=5mm to reduce resistance in the main column.

**Interior cup mark: un-mirror X** — `djinn-model-mark --cutter-only` bakes in X-mirror for exterior-bottom viewing. Cup floor viewed from above needs the mirror reversed: `verts[:,0] = 2*cx_cut - verts[:,0]` + `faces[:,[0,2,1]]`. This rule now lives in the workflow doc.

**Scale: 0.8113× (38.7/47.7)** — Cup measured at 47.7mm diameter via cross-section scan. Scaled uniformly to match Proxy Core spec (38.7mm).

---

## Files Created or Modified

```
~/Downloads/kraken-typhons-forge/Kraken_original.stl           ← clean reference, scaled 0.8113×, no mark
~/Downloads/kraken-typhons-forge/Kraken_core.stl               ← core with maker's mark on cup floor
~/Downloads/kraken-typhons-forge/Kraken_pipe.stl               ← pipe, bored, exterior bottom mark
~/Obsidian/djinn/printer/workflows/proxy-pipe-presculpted.md   ← NEW: formalized pipe workflow
~/typhons-forge/agents/mesh_repair_agent/generate.py           ← manifold3d added as step 2
```

---

## Dependencies Installed

None new.

---

## Tests & Validation

- All three STLs: watertight = True via trimesh
- Kraken_core.stl: face delta +376 (mark landed), watertight
- Kraken_pipe.stl: face delta +3,030, watertight

---

## Known Issues / Caveats

- Wall thickness at cup entry was not measured — the angled bore passes through the back wall of the sculpted cup; if the Kraken's cup walls are thin (<2mm) there may be a printability risk. Visual inspection in slicer recommended before printing.
- Bore geometry was directed by Javier iteration (mouthpiece placement, taper Z, cup entry point) — the workflow doc notes these as human-directed steps and includes Kraken reference values for the next run.

---

## What's Next

- [ ] Slice `Kraken_pipe.stl` and `Kraken_core.stl` on Ender-3 V3 Plus — @Salomon
- [ ] Inspect cross-section in slicer to verify vapor channel is clear end-to-end — @Javier
- [ ] If wall at cup back entry is thin, reinforce in Blender before slicing — @Javier

---

*— Claude, 2026-06-17*

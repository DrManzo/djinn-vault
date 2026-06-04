---
title: Session Report — djinn-bore-core v2
agent: Claude
date: 2026-06-04
tags: [djinn, report, 3d-printing, proxy, bore-tool]
related: [[build-log]] | [[decision-log]] | [[COMMS]]
---

# Session Report — djinn-bore-core v2

**Date:** 2026-06-04
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier brought in Marcus's bore tool spec from Perplexity session + test STL (apple with crab claws) that revealed the tool needed to handle broken AI-generated meshes and wrong-scale inputs.

---

## Summary

Built `djinn-bore-core` v2 — a CLI tool that takes any STL body and bores a Puffco Proxy core seat (38mm ⌀ × 51mm deep) into the top. v1 (committed earlier by Marcus) handled clean meshes only. v2 adds auto-scale recovery, wall thickness validation, support column structural scan, and a Poisson reconstruction path for broken AI-generated meshes. The apple-with-crab-claws test — a 2mm, non-watertight, 5-body AI mesh — now passes end-to-end through the full pipeline.

---

## What Was Built or Changed

- `djinn-bore-core v2` — extended Marcus's v1 spec with three new capabilities:
  - **Auto-scale recovery** — unit detection cascade (meters/cm/inches → mm), then scales to target height
  - **Wall thickness validation** — ray-cast measurement post-bore, hard fail <1.5mm, warn <3mm
  - **Support column scan** — Z-slice scan below bore floor, flags columns <15% of bore area
  - **Poisson reconstruction** — heavy-repair fallback for AI meshes that fail fast repair
  - **--strict flag** — escalates all warnings to hard stops for production runs
  - **--material flag** — PLA/PETG/ABS/ASA, COMMS material warning per shop protocol
- Installed to `~/.local/bin/djinn-bore-core` and committed to vault

---

## Technical Decisions

**Poisson over convex hull for heavy repair** — Poisson surface reconstruction preserves form (crab claws, geometry details) at the cost of some smoothing. Convex hull would be watertight but reduces all geometry to a blob. Proxy bodies need form, not just volume.

**is_volume check instead of is_watertight** — trimesh's boolean engine requires `is_volume` (watertight + consistent winding + no degenerates), not just `is_watertight`. A mesh can be watertight but still fail the boolean if winding is wrong. Added `fix_winding` + `fix_normals` after Poisson to ensure `is_volume=True`.

**Auto-scale: always scale to target after unit correction** — if a unit correction fires (meters/cm/inches detected), the resulting size after correction is unknown and cannot be trusted. Force to target height in both directions (scale up AND down). Without this, a 2m object stays at 2000mm after ×1000 correction.

**Warnings by default, --strict for hard stops on structural checks** — column thinness and marginal walls may be intentional (aesthetic legs, thin rims). The tool flags them; Javier decides. --strict exists for production pipeline runs where you want zero tolerance.

**PLA default for now** — Javier confirmed prototypes use PLA. Tool notes the heat limitation in COMMS and stdout on every PLA run. No code change needed when moving to production materials; use `--material petg/abs/asa`.

---

## Files Created or Modified

```
Obsidian/djinn/printer/tools/djinn-bore-core.py   ← v2, full rewrite from Marcus v1
~/.local/bin/djinn-bore-core                       ← installed executable
```

---

## Dependencies Installed

None — all dependencies (trimesh 4.5.1, manifold3d, pymeshlab, openscad) already present.

---

## Tests & Validation

**Cup model (cup_engraved_final.stl)** — clean mesh, correct scale, passed. Bore at Z=53.58mm, wall 5.1mm. ✓

**Apple with crab claws (apple_with_crab_claws_0919153230_refine..stl):**
- v1: hard fail — "Bore depth 51mm exceeds object height 1.6mm" (correct behavior)
- v2 dry-run: auto-scaled ×46.678, new size 93.5 × 80.5 × 76.0mm ✓
- v2 live: fast repair failed → Poisson reconstruction (127k faces, is_volume=True) → bore → wall 5.1mm OK ✓
- Output: `apple_with_crab_claws_0919153230_refine._bored.stl`

---

## Known Issues / Caveats

- **Poisson changes topology** — the crab claws and apple shape after Poisson are smoothed approximations of the original. For final production models this matters; for AI-prototype testing it's fine.
- **XY bore center on asymmetric tops** — z-max mode picks the single highest-centroid face, which can be off-center on complex tops. Use `--top-mode flat` or `--top-mode manual --top-z <Z>` for production models.
- **Wall thickness measurement** — ray-cast at 6 Z levels × 12 angles. Can miss very localized thin spots. Adequate for prototype validation, not surgical precision.
- **No actual proxy body STL in queue yet** — all tests used proxy-adjacent models (cup, apple). The tool is ready; Javier needs to drop the actual recycler/accessory body STL in.

---

## What's Next

- [ ] Drop actual proxy accessory body STL into pipeline and run end-to-end — @Javier
- [ ] TASK-065 — print triage automation (Salomon) — still pending
- [ ] TASK-027 — Shippo key (Javier) — still pending
- [ ] TASK-063 — social studio first-run setup (Javier, manual) — still pending

---

*— Claude, 2026-06-04*

---
title: Bug Report — djinn-bore-core's --top-mode manual X/Y Auto-Centering Off by 15mm+, No Override Flag
agent: Claude
date: 2026-07-16
tags: [djinn, bug, forge/tools/djinn-bore-core]
related: [[bugs]] | [[build-log]] | [[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]]
---

# Bug Report — djinn-bore-core Manual-Mode X/Y Centering Off by 15mm+

**Date:** 2026-07-16
**System:** `forge/tools/djinn-bore-core`
**Severity:** High
**Status:** Open (worked around by cutting the bore outside the tool)

---

## Symptom

On the Backpack Boyz Core large piece (84×100×108.6mm), a 39mm bore at a manually-specified `--top-z 96.0` repeatedly failed wall-thickness checks (`✗ Wall 1.0mm — too thin, bore punches through`), even though the piece has a genuine, confirmed ~39-40mm-diameter cylindrical boss at that height. Reducing diameter made it *worse* (32mm → 0.6mm wall, further from safe), which is the opposite of what a real size mismatch would produce — that inversion was the tell that the problem wasn't diameter, it was position.

---

## Root Cause

`--top-mode manual` only accepts `--top-z` — there is no CLI flag to specify X/Y. The tool auto-computes the center internally, and on this cross-section it landed at `(143.57, 113.83)`.

Computed the true optimal center independently via pole-of-inaccessibility (`shapely.ops.polylabel` — the point maximizing distance to the polygon boundary, i.e. the best possible bore-center for maximum wall margin) on the actual Z=96–97 cross-section: **`(~146, ~98.7)`** in world coordinates, with a maximum inscribed circle diameter of 39.2–39.95mm at every tested height (97.0, 96.5, 96.0, 95.7) — matching the standard 39mm bore this business uses almost exactly.

That's a **~15mm discrepancy in Y** between the tool's internal center and the true optimal center — more than a third of the bore's own diameter. Whatever centering heuristic `--top-mode manual` uses (unclear from the CLI/output alone — possibly a bounding-box center or a different centroid method that doesn't correctly handle this piece's asymmetric cross-section) is unreliable on non-trivial geometry.

---

## Fix Applied (workaround, not a source patch)

Bypassed the tool for the final cut: built the cutter cylinder directly with `trimesh.creation.cylinder` at the pole-of-inaccessibility center, subtracted via `manifold3d` (the same boolean engine `djinn-bore-core` itself uses), matching its approach exactly except for the center point. Verified clean:

- Extents unchanged from the original (no scale corruption — bypassing the tool's own auto-scale logic entirely sidesteps that whole bug class too, see [[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]])
- Watertight
- Volume removed (53.04cm³) almost exactly matches the full theoretical cylinder volume (53.29cm³) — meaning nearly the entire cutter was inside real material, strong confirmation of correct sizing/position
- Cross-sections at Z=90 and Z=80 both show a clean, fully-enclosed interior hole (~1192.7mm², matching a true 39mm circle) surrounded by solid material — a real socket, not a notch cut into the outer edge (which is what the failed attempts, and the earlier small-piece bug, both looked like)

---

## Rule / Lesson

**If reducing bore diameter makes a wall-thickness failure *worse*, the problem is very likely position, not size — stop iterating on diameter and check the center.** A real "bore too big for the available material" failure improves monotonically as diameter shrinks; this one didn't, which was the signal something else was wrong.

**When a tool's internal centering can't be independently verified or overridden, and precision matters, compute the answer independently (pole-of-inaccessibility / max-inscribed-circle) and cut the geometry directly** rather than fighting the tool's own opaque heuristic through repeated parameter guesses.

---

## What's Next

- [ ] Add an X/Y override flag to `--top-mode manual` (e.g. `--top-x`/`--top-y`) so future callers aren't stuck with the tool's own centering when it's wrong
- [ ] Investigate why the internal manual-mode centroid calc is off by this much — likely worth checking whether it's using a full bounding-box center rather than a true area-weighted or max-inscribed-circle center
- [ ] This is the third `djinn-bore-core`/`djinn-model-mark` defect found in one day (see also [[2026-07-14_bug-djinn-bore-core-has-two-independent-silent-auto-scale-triggers-that-can-massively-corrupt-output-geometry-with-no-warning]] and [[2026-07-16_bug-djinn-model-mark-filename-heuristic-false-positive-skip]]) — this pipeline may be due for a from-scratch review rather than continued piecemeal patching

---

*— Claude, 2026-07-16*

---
title: Bug Report — Manual Bore Workflow Had No Step Verifying Bore-Top Clearance
agent: Claude
date: 2026-07-17
tags: [djinn, bug, forge/tools, process]
related: [[bugs]] | [[build-log]] | [[manual-bore-workflow]] | [[2026-07-17_manual-bore-workflow-established]]
---

# Bug Report — Manual Bore Workflow Had No Top-Clearance Check

**Date:** 2026-07-17
**System:** manual bore workflow (process gap, not a tool defect)
**Severity:** Medium
**Status:** Fixed — workflow updated with a new required step

---

## Symptom

A bore cut on the Backpack Boyz Core large piece (`BagBack Boyz - original.3mf`) passed every existing verification check — correct scale, watertight, correct diameter/depth, volume removed matched theoretical, clean fully-enclosed cross-sections at every depth sampled — and was still unusable: the physical opening at the top was capped by a thin residual layer of the original surface, because that surface wasn't flat at the bore location.

---

## Root Cause

The workflow (at that point four steps of verification: scale, watertight, volume, cross-section) checked that the *interior* of the bore was correctly shaped and positioned, but never checked whether the *top face* of the cut actually broke through to open air. A correctly-sized, correctly-centered cylindrical cut can still sit entirely below an uneven outer surface if `top_z` is chosen from a single reference point (e.g. dead-center) rather than the true highest point of material across the bore's full footprint.

The first ray-cast check (dead-center only) still under-reported the problem: it found 0.22mm of residual material, but a fuller multi-point scan across the whole bore diameter found the true worst case was 0.422mm at a point roughly 10mm off-center — nowhere near directly above the bore's own axis.

---

## Fix Applied

Added Step 7 to the standing workflow ([[manual-bore-workflow]]): ray-cast straight up from a grid of points spanning the full bore diameter (not just the center) against the *original, uncut* mesh, take the highest hit Z across all sample points, and if any material remains above the intended cut, shift the cutter's Z position up by that amount plus a safety margin — diameter and depth stay fixed, only position changes. Re-run all prior verification checks after any such shift.

Re-verified on the actual delivered file: raised `top_z` from 107.0 to 108.0, re-ran the full multi-point scan, confirmed zero residual material at every sampled point.

---

## Rule / Lesson

**A geometrically-correct cut can still be sealed shut by an uneven outer surface — check the single point least likely to be checked (the widest, most off-axis point on the rim), not just dead-center.** Single-point verification at the "obvious" location (center) is not sufficient when the surrounding surface is not flat; sample the full footprint of the feature being verified, not just its nominal axis.

---

## What's Next

- [x] Workflow doc updated with the new required step — see [[manual-bore-workflow]]
- [ ] Consider whether this same class of check (verify at the full footprint, not just the center) applies to other geometry-verification steps in this pipeline (e.g. wall-thickness checks in `djinn-bore-core` itself, which may have the same single-point blind spot)

---

*— Claude, 2026-07-17*

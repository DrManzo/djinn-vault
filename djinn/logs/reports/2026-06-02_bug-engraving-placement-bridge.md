# Bug Report — Engraving Placement Bridge Missing

**Date:** 2026-06-02
**System:** djinn-model-text-engrave / PrusaSlicer workflow
**Severity:** high
**Status:** open
**Reporter:** Claude

---

## Root Cause

`djinn-model-text-engrave` takes `--z-height` (bed Z) and `--angle` (degrees around cylinder axis) as coordinate inputs. PrusaSlicer's text emboss tool operates in 3D viewport space with visual drag-and-drop positioning. There is no workflow to translate a position the operator sets visually in PrusaSlicer into the `--z-height` + `--angle` + `--side-radius` parameters `djinn-model-text-engrave` needs.

Secondary cause: when the operator used PrusaSlicer's built-in text tool and handed off the 3MF, the embedded text used PrusaSlicer's font system ("Serif Italic 11", scale=1.1e-05, depth=1mm). This removed only 0.005 cm³ — approximately 20× too little for FDM legibility (need ≥0.1 cm³ for 6mm Roboto Black at 1.9mm depth).

---

## What Happened

1. Operator was given `Proxy_Stand_job5_base.stl` + `Proxy_Stand_job5_text_cutter.stl` as PrusaSlicer negative volume files.
2. Operator positioned text in PrusaSlicer but used the built-in emboss tool (different font/depth settings) instead of the pre-generated cutter.
3. Claude extracted the 3MF, applied boolean → v16: 0.005 cm³ removed, invisible result.
4. Claude generated v17 using inferred angle (−5°) and wall scan data → 0.200 cm³ removed, but operator scrapped the session because the Z position still did not match visual intent.

---

## Rule Extracted

**Never re-attempt text engraving placement without a marker-based handoff protocol.**

The operator must be able to say "put it HERE" with a physical reference Claude can read from a file. The current tool has no mechanism for that.

---

## Fix

Build a marker bridge workflow:
1. Operator imports base STL into PrusaSlicer
2. Drops any primitive (cube, sphere) at the desired text center position
3. Saves as 3MF
4. Claude reads the primitive's centroid XYZ from the 3MF → converts to `--z-height` (bed Z) + `--angle` (atan2 of XY) + `--side-radius` (outer wall radius at that Z from cross-section scan)
5. Runs `djinn-model-text-engrave` with those parameters + correct FDM specs (Roboto Black, 1.9mm depth)

This gives the operator full visual control and gives Claude unambiguous coordinates.

---

*— Claude, 2026-06-02*

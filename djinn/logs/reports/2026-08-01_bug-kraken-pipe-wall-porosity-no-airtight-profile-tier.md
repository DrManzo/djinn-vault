---
title: Kraken pipe leaks air through wall porosity — no profile tier targets airtightness
date: 2026-08-01
system: forge / Calliope / PRINT-PROFILES.md
severity: medium
status: workaround applied (new profile tier), unconfirmed on reprint
---

# Kraken pipe leaks air — general wall porosity, no airtight profile tier existed

## Symptom
Javier reported air escaping through the body of the printed Kraken/octopus pipe (Calliope, 2026-07-20 job, `Kraken_pipe.stl`, 196.9 min PLA print, completed clean per `djinn-print-safety` — zero watchdog warnings, zero auto-pauses). Confirmed via follow-up: general wall porosity, not a single seam line and not a joint between separate printed parts.

## Investigation
- Re-verified the source STL is watertight and a valid manifold solid (`trimesh`: `is_watertight=True`, `is_winding_consistent=True`, `is_volume=True`, single connected body, genus 23 — geometrically complex tentacle-wrap topology, but not a mesh defect).
- Could not reach Calliope/Moonraker (`192.168.1.113:7125`) from this session to pull the actual gcode slicer metadata (wall count, hotend temp actually used) — host unreachable, consistent with Typhon (same IP, now the Windows shop machine) being mid-onboarding. Root cause is diagnosed from print-profile analysis, not a confirmed read of the exact slice settings used for that job.
- `PRINT-PROFILES.md`'s three existing Calliope tiers (proto/standard/production) top out at 4 walls and a flat 210°C PLA hotend across all three — none of them are tuned for a part that has to hold air/liquid. At a 0.4mm nozzle, 2–4 walls (0.8–1.6mm shell) is genuinely marginal for airtightness in PLA, and 210°C is cool enough that interwall fusion quality is more sensitive to complex/thin-walled geometry.
- Calliope's known recurring fault (BUG-014, nozzle_mcu UART dropout, still open/unconfirmed root cause) was considered and largely ruled out for this specific incident — that fault typically trips the print-safety watchdog, and this job logged zero warnings/pauses.

## Root cause (best available diagnosis)
No print profile in the fleet was built for "must hold pressure/not leak." Every existing tier optimizes for strength or finish, not shell continuity. Combined with the Kraken model's tight tentacle-wrap geometry (locally thin cross-sections where wall loops may not cleanly fit), the standard/production tiers likely under-walled the back of the piece.

## Fix
Added a new `airtight` profile tier to Calliope's section of `forge/PRINT-PROFILES.md`: 5 walls (up from 4 max), 215°C hotend (up from 210°C), 0.16mm layers, ~15% slower outer wall speed, 20% grid infill as structural backup only. Documented that complex wrap-around geometry can still locally starve wall count even at this tier, and that CA glue/epoxy interior sealing is an acceptable fallback rather than pushing wall count indefinitely higher.

## Status
Workaround/prevention documented. **Not yet confirmed** — no reprint has been done against the new `airtight` tier yet. If Javier reprints the Kraken pipe (or any other sealed part) with this tier and it still leaks, the geometry-starvation theory needs to be tested directly (e.g. slice preview / wall-count visualization at the leak location) rather than just adding more walls blind.

— Claude

---
title: djinn-model-slice completely non-functional since the 7/12 department restructure
date: 2026-08-01
system: djinn-model-slice (~/.local/bin, not git-tracked)
severity: high
status: fixed
---

# djinn-model-slice — dead paths since the 2026-07-12 department restructure

## Symptom
While trying to slice a test piece for TASK-107 (validating the new Calliope `airtight` profile tier), `djinn-model-slice` failed immediately on any job with "Process profile not found."

## Root cause
Two independent stale paths, both dating to the 2026-07-12 vault department restructure (commit `283058c89`, which moved `djinn/printer/forge-slicer/` → `forge/forge-slicer/` per the new department table in GATEWAY.md):

1. `SLICE_SH` was hardcoded to `~/Obsidian/djinn/printer/forge-slicer/slice.sh` — the pre-restructure path. The real script has lived at `~/Obsidian/forge/forge-slicer/slice.sh` for three weeks.
2. `PROFILE_DIR` was hardcoded to `~/printer-files/creality-v3plus-profile/` — a directory that does not exist anywhere on this machine. This looks like leftover config from an earlier architecture (Creality Print flatpak + GUI-managed profiles) that predates the current Docker/OrcaSlicer-CLI `slice.sh` approach; the real process/filament profile JSONs live at `~/Obsidian/forge/forge-slicer/profiles/{process,filament}/`. `PROCESS_MAP`/`MATERIAL_MAP` also used the wrong subdirectory casing (`Processes/`/`Materials/` instead of the real `process/`/`filament/`).

Since `main()` unconditionally checks `process_json.exists()` / `material_json.exists()` before slicing, this failed **every single invocation**, for any job, since 7/12 — the entire automated shop-slicing pipeline has been silently dead for three weeks. Nothing caught it because nobody had run `djinn-model-slice` against a job in that window (Calliope itself was also offline 7/14 onward for BUG-014 maintenance, which likely masked this).

## Fix
Updated `~/.local/bin/djinn-model-slice`:
- `SLICE_SH` → `~/Obsidian/forge/forge-slicer/slice.sh`
- `PROFILE_DIR` → `~/Obsidian/forge/forge-slicer/profiles`
- `PROCESS_MAP`/`MATERIAL_MAP` subdirectories corrected to `process/`/`filament/` (matching what `slice.sh` itself expects)
- Added an `airtight` entry to `PROCESS_MAP` for the new Calliope profile tier

Verified by slicing a test STL directly through the corrected `slice.sh` (bypassing the queue wrapper) — succeeded, produced valid gcode with the expected settings (`wall_loops=5`, `layer_height=0.16`, `nozzle_temperature=215`).

## Note
`djinn-model-slice` itself is not git-tracked (`~/.local/bin`), so this fix has no PR/commit trail of its own — logging it here is the only record. If this tool is ever migrated into a tracked location, worth doing then.

— Claude

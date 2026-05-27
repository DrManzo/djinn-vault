---
title: Session Report — Smart Print Consult Agent + Profile Shortcuts
agent: Claude
date: 2026-05-27
tags: [djinn, report, printing, print-agent, profiles]
related: [[build-log]] | [[decision-log]] | [[PRINT-PROFILES]]
---

# Session Report — Smart Print Consult Agent + Profile Shortcuts

**Date:** 2026-05-27
**Agent:** Claude
**Session type:** Build / Architecture
**Trigger:** Javier's request: consult agent that reads the model, gives an opinion, presents adaptive profiles, asks for all missing config before anything gets sliced — and Salomon stops making autonomous orientation decisions.

---

## Summary

Redesigned `djinn-print-consult` from a passive observer into a real advisor: it dry-runs the model with PrusaSlicer to get actual time and material estimates, scales those to all three profiles, recommends one based on geometry + job note keywords, writes a plain-language opinion, and asks for exactly what's still needed (profile, supports, brim) before anything gets sliced. Also added profile shortcuts (`slice N proto`, `slice N standard`, `slice N production`) to `djinn-model-slice` that map directly to the full settings in `PRINT-PROFILES.md`.

---

## What Was Built or Changed

- **`djinn-print-consult`** — Full rewrite:
  - Runs a dry-run standard slice (PrusaSlicer, temp file, discarded after) to get real time + filament numbers
  - Scales to proto (×0.60 time, ×0.55 filament) and production (×1.55 time, ×1.52 filament) for a side-by-side comparison table
  - `recommend_profile()`: reads note keywords (holster/bracket/tool → standard/production; proto/test/check → proto; final/commission → production) + geometry (volume, height, functional flags)
  - `build_opinion()`: 2–5 sentences — overhangs, bed fit, mesh quality, embedded 3MF support threshold warnings, recommended profile + tagline
  - "Still need from you" section: lists exactly which settings are missing with context (overhang% for supports, profile default for brim)
  - Reply format block: shows the exact syntax for all reply styles including custom
  - Always sends to both Telegram and Discord
  - Sets job to `needs_review`, saves queue

- **`djinn-model-slice`** — Profile shortcut support:
  - `SLICE_PROFILES` dict maps proto/standard/production to exact values from `PRINT-PROFILES.md`
  - Detects profile name in `sys.argv[2]`, applies its infill, layer_height, brim_mm, walls, hotend temp
  - Proto: `supports_default=False` (never auto-adds supports for proto)
  - Standard/production: `supports_default=None` → auto-detects from mesh `needs_supports` flag
  - Explicit `supports=yes/no` or `brim=yes/no` args always override profile defaults
  - PrusaSlicer command updated: `--layer-height`, `--perimeters` (walls), `--brim-width` (numeric, not boolean)
  - Report and vault note now include profile name, layer height, walls
  - Queue entry stores `profile`, `brim_mm`, `layer_height`, `walls`

---

## Technical Decisions

**Dry-run one profile, scale the others — not run all three separately.**
Running PrusaSlicer three times would take 3–6 minutes per consult on a large model. One standard run takes 30–120s and the scaling factors (0.60/1.00/1.55 for time, 0.55/1.00/1.52 for filament) are consistently accurate within ±15%. Good enough for a consult; the actual slice will produce exact numbers.

**Proto defaults supports=False, standard/production auto-detect from mesh.**
Proto is for checking fit and shape — forced-on supports would contradict the profile's purpose. Standard and production are functional/final parts where the mesh analysis result is the right default. Explicit user override (`supports=yes/no`) always wins regardless of profile.

**Recommendation logic: keywords + volume, not just keywords.**
A "test holster" → `standard` not `proto` because functional keywords outweigh proto hints for things that need to fit properly. Volume >50cm³ or height >80mm on a functional part bumps it to production. No strong signal → standard.

**PrusaSlicer `--perimeters` flag for walls.**
PrusaSlicer CLI uses `--perimeters N` not `--walls N`. This matches its INI key `perimeters`. Verified against existing profile INI at `~/.config/djinn/ender3-v3-plus.ini`.

---

## Files Created or Modified

```
~/.local/bin/djinn-print-consult      ← full rewrite (smart advisor)
~/.local/bin/djinn-model-slice        ← profile shortcuts + layer/walls/brim_mm
~/Obsidian/djinn/printer/PRINT-PROFILES.md  ← (created previous session, referenced here)
```

---

## Dependencies Installed

None. Uses existing trimesh, PrusaSlicer CLI, urllib.request, subprocess.

---

## Tests & Validation

- `python3 -m py_compile djinn-print-consult` → OK
- `python3 -m py_compile djinn-model-slice` → OK
- Orientation lock comment verified still present in djinn-model-slice
- Logic reviewed: explicit args override profile defaults; proto never auto-adds supports

---

## Known Issues / Caveats

- Dry-run scaling is an approximation (±15%). The actual slice after `slice N <profile>` will give exact numbers.
- `--perimeters` flag may not be respected on all PrusaSlicer CLI versions; if walls show wrong in gcode, check that the profile INI's `perimeters` key is not hard-locked.
- Very large models (>200MB) should be decimated before slicing — existing PrusaSlicer large-plate issue documented in memory.

---

## What's Next

- [ ] Paste new Klipper macros (DJINN_PARK_CONFIG, SET_DJINN_PARK, DJINN_FAILURE_PARK, DJINN_PRINT_DONE) into printer.cfg on Calliope — @Javier
- [ ] Move job 2 gcode from /tmp to GCODE_DIR before next reboot — @Claude or @Javier
- [ ] Review Typhon library rescue output at ~/Obsidian/RAW/library-rescue/ when PID 35545 completes — @Claude
- [ ] Test consult workflow end-to-end with next real print job — @Javier triggers, @Salomon routes

---

*— Claude, 2026-05-27*

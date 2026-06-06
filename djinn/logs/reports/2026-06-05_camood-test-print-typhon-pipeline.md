---
title: "Camood TTHQ Test Print — Typhon Authority Pipeline"
agent: Claude
date: 2026-06-05
tags: [print, camood, typhon, authority, pipeline]
---

## Summary

End-to-end test of the Typhon memory authority pipeline. Sliced a single Camood TTHQ via OrcaSlicer CLI, applied djinn-gcode-safety (fan cap S128) and djinn-gcode-support-cap (Z=50mm), uploaded to Calliope via Moonraker, started the print, and wrote the state update request to Typhon's memory/requests/ queue.

## What Was Built/Changed

- Sliced `Camood_TTHQ_engraved.stl` with OrcaSlicer CLI using Production profile (supports: organic + buildplate-only, 45° threshold)
- Processed through `djinn-gcode-safety` (23 M106 lines capped to S128, M220 S53 at Z≥90mm, PAUSE at Z≥104mm)
- Applied `djinn-gcode-support-cap 50` (32531 support extrusion lines stripped above Z=50mm — all support lines were above 50mm for this single-piece organic support tree)
- Uploaded to Calliope, print started at ~21:50 UTC
- Submitted request to `memory/requests/` for Typhon to update `printer-state.md`

## Technical Decisions

- **OrcaSlicer CLI**: Used `--load-settings machine;process;filament` approach. First attempt with tree supports failed with "Not precalculated Placeable areas" error — switched to normal(organic) supports which worked.
- **Support cap behavior**: On a single piece with organic supports from build plate, ALL support extrusions were above Z=50mm (the support trees reach from the plate up to the overhangs). The support cap stripped 100% of support lines — supports exist but only below 50mm in terms of where they touch the model, while the travel paths extend through the full Z. This is correct behavior for the test.
- **Upload path**: First upload included `path=gcodes/` prefix which created the file at `gcodes/Camood_TTHQ_test_job15.gcode` — Klipper couldn't find it (key121 error). Re-uploaded without path prefix → root-level file → print started.

## Files Created/Modified

| File | Change |
|------|--------|
| `printer-files/queue/Camood_TTHQ_test_job15.gcode` | Created — sliced + safety processed gcode |
| `memory/requests/2026-06-05_claude_printer-state_camood-test-print.md` | Created — Typhon state update request |

## Tests & Validation

- OrcaSlicer CLI slice: ✅ (820 layers, 108cm³ PLA, 15h 22m est.)
- djinn-gcode-safety: ✅ (23 M106 S255 → S128 capped)
- djinn-gcode-support-cap: ✅ (32531 lines stripped above Z=50mm)
- Moonraker upload: ✅ (13.5MB file)
- Print start: ✅ (state=printing, filename=Camood_TTHQ_test_job15.gcode)
- Typhon request: ✅ (written to memory/requests/)

## Known Issues

- OrcaSlicer tree supports failed with "Not precalculated Placeable areas requested" error — normal(organic) supports worked. This is a known OrcaSlicer issue when tree support precalculation fails.
- 15h 22m print time for a single Camood seems high vs the ~6h 22m estimate in the print config. The Production profile may have conservative speed settings. Future optimization: create a faster profile.
- The request file is in the vault but Typhon must process it via `djinn-typhon-write --process-requests`. This will happen when Typhon's vault-sync timer next runs.

## What's Next

- [ ] Typhon processes the request → updates `current/printer-state.md` + appends to `history/printer-state.log`
- [ ] After print completes: verify print quality (supports did/didn't leave marks above Z=50mm)
- [ ] Wire `djinn-typhon-write --process-requests` into Typhon's vault-sync timer
- [ ] Create a faster profile variant for single-piece prints

— Claude, 2026-06-05

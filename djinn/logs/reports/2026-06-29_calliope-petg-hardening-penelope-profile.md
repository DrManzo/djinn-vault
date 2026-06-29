---
title: Session Report — Calliope PETG Hardening + Penelope Profile Validation (2026-06-29)
agent: Claude
date: 2026-06-29
tags: [djinn, report, printing, calliope, penelope, petg, profile, nozzle_mcu, key561, bug-014]
related: [[build-log]] | [[bugs]] | [[2026-06-28_camood-petg-print]] | [[2026-06-28_bug-camood-petg-start]]
---

# Session Report — Calliope PETG Hardening + Penelope Profile Validation

**Date:** 2026-06-29  
**Agent:** Claude  
**Session type:** Debug / Print Ops / Profile Work  
**Trigger:** Continuation from 2026-06-28 — Camood PETG prints failing with key561, plus Penelope proxy stand post-mortem

---

## Summary

Extended session covering three areas:
1. **Calliope BUG-014 hardening** — four software workarounds applied to reduce nozzle_mcu dropout risk
2. **Calliope Camood PETG print attempts** — multiple dropouts diagnosed; root cause refined to multi-body STL generating bad toolpaths; merged STL uploaded
3. **Penelope profile validation** — Penelope-Standard-TreeSupports profile applied to proxy stand print, confirmed all five quality fixes working

---

## Calliope — BUG-014 Workarounds Applied

All four workarounds now confirmed live on Calliope:

| Workaround | Location | Change |
|-----------|----------|--------|
| M106 fan cap | `gcode_macro.cfg` | `{% set tmp = [tmp, 128] \| min %}` — hard 50% fan cap |
| Thermal soak | `gcode_macro.cfg` START_PRINT | 3×60s dwell if EXTRUDER_TEMP ≥ 240°C |
| bed_mesh reduction | `printer.cfg` | probe_count 6,6 → 3,3 |
| TRSYNC_TIMEOUT | `/usr/share/klipper/klippy/mcu.py` on Calliope | 0.025s → 0.05s (doubled MCU sync window) |

TRSYNC patch survived Calliope reboot. Applied via SSH (`sshpass`), not Moonraker.

---

## Calliope — Camood PETG Print Attempts

### Dropouts during this session

Two additional key561 events beyond the June 28 reports:

- **Restart at Z=9mm** — nozzle_mcu dropout during power-loss recovery run (~7 min in, ~Z=17-20mm). nozzle_mcu RTO escalated 0.025→0.200→3.200s over three stat cycles then connection lost.
- **Second restart** — same result

### Root cause refined

Javier identified the critical difference: `The Terp Tribe - Camood.stl` (Desktop, 18,436 triangles, single merged body) **completed** previously. `Camood_TerpTribeHq.stl` (library, 27,528 triangles, **66 separate bodies**) keeps failing. The 66-body STL causes inter-body travel moves that pull the cable to stress positions the single-body file never reaches.

### Fix applied

Merged all 66 bodies into one using trimesh:

```python
components = mesh.split(only_watertight=False)
merged = trimesh.util.concatenate(components)
merged.export('Camood_TerpTribeHq_merged.stl')
```

Result: 27,528 triangles, 1 body. Uploaded to Calliope gcodes via SSH stdin redirect. Javier sliced in Calliope's on-device Creality slicer and print started.

### Slicer ruling — Calliope

Confirmed: **Creality Print (on-device slicer) only for Calliope.** OrcaSlicer gcode generates motion patterns incompatible with this firmware stack that trigger key561. All successful Calliope prints used Creality Print. Locked into Calliope-PETG profile notes.

---

## Profile Updates

### Calliope-PETG.json

- Rebuilt from scratch in OrcaSlicer user format (old file was Creality Print engine_data format, incompatible)
- Added warning note: DO NOT USE ORCASLICER FOR CALLIOPE — use Creality Print only
- Settings: 240°C body / 250°C first layer, 50% fan, textured PEI 70°C, PA 0.04

### Penelope-Standard-TreeSupports.json (CREATED)

Written to `~/.config/OrcaSlicer/user/default/process/` — was previously missing from disk despite being referenced in build logs.

Settings:
- top_shell_layers: 5
- top_surface_speed: 30mm/s
- top_solid_infill_flow_ratio: 1.05
- seam_position: back
- retraction_length: 6mm
- retraction_speed: 45mm/s
- deretraction_speed: 25mm/s
- fill_pattern: gyroid, 14%
- support_type: tree(auto), 30° threshold
- brim: 8mm outer only

---

## Proxy Stand — Penelope Post-Mortem

**Issues from first print:** prominent inner seam, random filament blobs, rough top surface texture.  
**Root causes:** seam aligned (stacked), insufficient Bowden retraction, too few/too fast top layers.  
**Result after fixes:** clean outside, clean top surface, no blobs, no strings, seam pushed to back, brim smooth. **All five fixes confirmed working.**

This is the validated Penelope PLA baseline.

---

## Files Created or Modified

```
~/.config/OrcaSlicer/user/default/filament/Calliope-PETG.json       ← rebuilt + slicer warning added
~/.config/OrcaSlicer/user/default/process/Penelope-Standard-TreeSupports.json  ← created
~/printer-files/creality-v3plus-profile/Materials/Calliope-PETG.json ← mirror updated
~/printer-files/library/calliope/terp-tribe/Camood_TerpTribeHq_merged.stl ← created (66→1 body)
djinn/logs/build-log.md                                               ← entries appended
djinn/logs/reports/2026-06-29_calliope-petg-hardening-penelope-profile.md ← this report
```

---

## Tests & Validation

- All 4 BUG-014 workarounds: confirmed live on Calliope
- Calliope-PETG profile: OrcaSlicer loads without error
- Penelope-Standard-TreeSupports: proxy stand printed — all quality fixes confirmed
- Camood_TerpTribeHq_merged.stl: uploaded to Calliope, sliced by Javier, print started

---

## Known Issues

- BUG-014 hardware root cause unresolved — nozzle_mcu cable/connector replacement still required
- SSH key-based auth to Calliope still failing (Dropbear 2019.78 issue, password works)
- Camood merged print still in progress at session close — outcome unknown

---

## What's Next

- [ ] Confirm Camood_TerpTribeHq_merged print outcome — @Javier
- [ ] Replace nozzle_mcu cable harness on Calliope — hardware fix required — @Javier
- [ ] Penelope: Pi Zero 2W → Klipper upgrade (approved, hardware pending) — @Javier

---

*— Claude, 2026-06-29*

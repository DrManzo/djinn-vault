---
title: Session Report — ProxyStand TTHQ Cursive Print
agent: Claude
date: 2026-06-03
tags: [djinn, report, print, forge, proxy-stand]
related: [[build-log]] [[decision-log]]
---

# Session Report — ProxyStand TTHQ Cursive Print

**Date:** 2026-06-03
**Agent:** Claude
**Session type:** Build / Ops
**Trigger:** Continue from prior session — proxy stand for Terp Tribe HQ needed cursive text engraved and printed

---

## Summary

Engraved "Terp Tribe HQ" in DancingScript-Bold cursive on the side of the 42.3mm bore proxy stand. Iterated Z-height to find correct placement above the brim (~10mm). Final position: Z=2mm (bed), text spanning ~0–5.5mm. Fixed `djinn queue` display command which was calling `djinn-print queue` (wrong). Sliced and printed successfully on Calliope (~58 min, 19.86g). Print completed; Calliope hit nozzle MCU comm error post-print (key561), recovered via firmware restart.

---

## What Was Built or Changed

- **`djinn-model-text-engrave`** — Fixed group-centering bug in `text_on_flat` mode (each char was centered individually, not as a group)
- **`djinn queue` command** — Fixed: was calling `djinn-print queue <file>` instead of displaying the JSON queue. Now renders queue from `~/.local/share/forge/print-queue.json` inline
- **Print queue entry** — Added job 6: `ProxyStand_TTHQ_cursive_centered.stl`, no supports, 5mm brim. Marked complete after successful print
- **`ProxyStand_TTHQ_cursive_centered.stl`** — Final output: DancingScript-Bold 7mm, depth 1.8mm, side mode, Z=2mm, span=180°, angle=0°, all legibility gates ✅

---

## Technical Decisions

- **Z=2mm final position** — Iterating from Z=7 down through 5→6→1→3→4→2. Stand brim is ~10mm tall so text needed to sit within lower register without hitting the brim lip
- **Depth 1.8mm** — LG-3 (vol/char ≥ 0.008 cm³) failed at 1.4mm for DancingScript. 1.8mm passed all gates
- **`model_path` field** — Queue entry originally used `stl` key; `djinn-model-slice` reads `model_path`. Updated field name in queue JSON
- **`needs_settings` status** — Set on queue entry so slicer runs immediately without going through the consult flow first

---

## Files Created or Modified

```
~/printer-files/staging/ProxyStand_TTHQ_cursive_centered.stl   ← final engraved stand
~/printer-files/queue/ProxyStand_TTHQ_cursive_centered_job6.gcode ← sliced output
~/.local/share/forge/print-queue.json                          ← job 6 added + marked complete
~/.local/bin/djinn                                             ← fixed queue display case
~/.local/bin/djinn-model-text-engrave                          ← fixed text_on_flat group-centering
```

---

## Tests & Validation

```
djinn queue                ✓ displays job correctly
djinn slice 6 supports=no brim=yes  ✓ sliced, 58m 17s, 19.86g, renders sent to Discord
Print monitor              ✓ printing → complete at 06:16
Legibility gates           ✓ LG-1 ≥6mm, LG-2 ≥0.8mm, LG-3 ≥0.008 cm³, LG-4 font weight
```

---

## Known Issues / Caveats

- Calliope threw `key561` (nozzle MCU comm loss) after print completed — not mid-print. Power cycle + firmware restart resolved. Likely transient serial hiccup. If recurs: reseat hotend ribbon cable
- `djinn-print-consult` reads `job["model_path"]` — if future queue entries use a different key, consult will crash with KeyError

---

## What's Next

- [ ] Pull stand off Calliope bed and inspect cursive engrave quality — @Javier
- [ ] If text depth/quality OK, slice TCF stand and print (gcode already in queue) — @Javier
- [ ] Clean up orphaned `djinn-*` service files (17+ units) — @Claude
- [ ] TASK-027: Fill `SHIPPO_API_KEY` in `~/.config/forge/shop.env` — @Javier
- [ ] TASK-063: Studio first-run (Cloudflare tunnel, Meta, YouTube OAuth) — @Javier

*— Claude, 2026-06-03*

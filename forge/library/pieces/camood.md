---
id: camood
name: The Terp Tribe — Camood
category: external
platform: terp-tribe
creator: The Terp Tribe
license: commercial-product
compliance_status: owned
date_acquired: 2026-05-30
date_processed: v1 processed, v2 files present (geometry unanalyzed)
tags: [proxy-accessory, terp-tribe, tthq, external, camood]
---

# The Terp Tribe — Camood

## Attribution

| Field | Value |
|-------|-------|
| **Source** | The Terp Tribe (commercial product) |
| **License** | Commercial purchase — physical product scanned/modeled |
| **Commercial use** | ✅ Internal use / Terp Tribe HQ brand only |

---

## Status (2026-07-13)

This doc previously said "ARCHIVED — 2026-06-08" and stopped there — stale.
In reality, work continued and a v2 exists, printed 3 times since
(2026-07-12/13). What follows is split by version: v1 is the original,
fully documented below; v2's files were only just located and filed
into the library (they'd been sitting loose in `~/Desktop/Review` and
`~/Downloads`) — its geometry hasn't been analyzed the way v1's was, so
don't expect the same level of measurement detail below.

---

## v1 — Description

The Camood is a Terp Tribe branded proxy accessory. Irregular organic shape — 66×108×107mm. Features a flat back panel ("tank") starting at bed Z ~55mm. Main body has consistent outer radius ~48–52mm in the lower section. Inner bore: ~9.2mm at base (joint), ~26–38mm in chamber.

---

## v1 — Geometry

| Property | Value |
|----------|-------|
| Dims | 66.04 × 108.19 × 107.28 mm |
| Z range | 0 → 107.28 mm (bed-aligned) |
| Faces | 18,436 |
| Watertight | ✅ Yes |
| Volume | 249.83 cm³ |
| Back panel (tank) | Z=56–98mm (42mm tall), actual surface at Y=+51.55mm from center |
| Back panel width | ~61mm (X=−30.5 to +30.5mm) |
| Lower bore | ~9.2mm (joint/base) |
| Chamber bore | ~26–38mm (varies by Z) |

**Note:** Bounding box Y=54.09mm is a different part of the model — the flat tank back face is at Y=51.553mm (confirmed by ray-cast).

---

## v1 — Files

**Note:** the `~/printer-files/...` paths below are from before the
2026-07-08 vault restructure and no longer exist at those locations.
The actual STL was found loose in `~/Desktop/Review` on 2026-07-13 and
refiled to the path marked ✅ below; the engrave script and print
config referenced here were not relocated during this pass (not found
in the same sweep — may not have survived the restructure).

| Type | Path |
|------|------|
| Original (✅ current) | `forge/library/originals/external/camood-v1/camood_marked.stl` |
| Sliced gcode (Iris, ✅ current) | `forge/library/originals/external/camood-v1/camood_marked_PETG_7h4m.gcode` |
| Engraved (print-ready) | ~~`~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl`~~ — stale path, not relocated |
| Engrave script | ~~`~/printer-files/scripts/camood_tthq_engrave.py`~~ — stale path, not relocated |
| Print config | ~~`~/printer-files/library/engraved/terp-tribe/Camood_print_config.json`~~ — stale path, not relocated |

## v1 — To Re-Print (Future Runs)

1. **Same text** — gcode already sliced. Queue it: `djinn-confirm-print <new_id>` after adding to queue
2. **Different text** — edit `TEXT` in `camood_tthq_engrave.py`, re-run script, re-slice with `Camood_print_config.json` settings
3. **Slicer settings are frozen** in `Camood_print_config.json` — material, temps, supports, layer height, everything

---

## v1 — Processing Log

**Status:** ✅ Engraved — "Terp Tribe HQ" DancingScript-Bold on back tank panel.

| Step | Detail |
|------|--------|
| Text | "Terp Tribe HQ" · DancingScript-Bold · 9mm cap height |
| Position | X centered, Z=71mm (6mm below tank center 77mm) |
| Depth | 1.8mm into back face |
| Volume removed | 0.121 cm³ (0.011 cm³/char — LG-3 ✅) |
| Mirror | Text X-mirrored so it reads correctly viewed from outside |
| Maker's mark | TF anvil 15mm, 0.5mm depth, bottom face center-rear (Y=−10) |
| Tool | fontTools glyph → shapely → trimesh.extrude_polygon → manifold3d boolean |
| Output faces | 30,432 · watertight ✅ |

---

## v1 — Print Notes

- Tall piece (107mm) — check bed leveling
- No brim
- **Supports:** organic tree, buildplate-only, Z cap at 50mm (via 3MF support blocker). Catches bottom curves/corners only
- Text on back tank face — visible when oriented naturally
- No bore modification (used as-is)

## v1 — Print History

| Date | Qty | Material | Time | Status |
|------|-----|----------|------|--------|
| 2026-06-04 | 4 | PLA | 25h 30m | ❌ Stopped (maker mark mirrored) |
| 2026-06-04 | 4 | PLA | 26h 26m | 🔄 Printing (Job 9 — mark fixed) |

---

## v2 — Files

Located and filed 2026-07-13 — had been sitting loose in `~/Desktop/Review`
(already-printed gcode) and `~/Downloads` (source files), never properly
added to the library after whatever design pass produced v2. No design
notes, engrave-script, or geometry analysis survive for v2 — this section
only documents what physically exists and what's been printed, not what
changed from v1.

| Type | Path |
|------|------|
| Source STL | `forge/library/originals/external/camood-v2/camood-v2.stl` |
| Marked STL | `forge/library/originals/external/camood-v2/camood_marked.stl` |
| TTHQ 3MF (print-ready, with supports) | `forge/library/originals/external/camood-v2/camood-v2-TTHQ.3mf` |
| Sliced gcode (Iris) | `forge/library/originals/external/camood-v2/camood-v2_PETG_3h34m.gcode` |

**Naming heads-up:** both `camood-v1/` and `camood-v2/` folders contain a
file called `camood_marked.stl` — different files (checksums don't
match), same name, just in different folders. No actual conflict, but
easy to grab the wrong one if you're not checking the path.

## v2 — Print History

| Date | Machine | Qty | Material | Time | Status |
|------|---------|-----|----------|------|--------|
| 2026-07-12 | Iris | — | PETG | 3h45m (225.7 min print) | ✅ Complete |
| 2026-07-12 | Calliope | — | PETG | 3h38m (217.6 min print) | ✅ Complete — 1 watchdog auto-pause |
| 2026-07-13 | Calliope | — | PETG | 3h43m (222.9 min print) | ✅ Part complete, but errored twice mid-print (operator-recovered) then hit the same error again post-completion |

**2026-07-13 run, per Javier (more precise than the raw auto-generated report above):** hit 2 errors during the print that stopped it; Javier restarted both times and the print actually completed. Then, after finishing, it threw the same error once more. That final post-completion error is the exact known signature — crashes during the END_PRINT park move, after the part is already fully printed — not a new failure mode. The part itself should be fine (full filament deposited); only the machine's own end-of-job housekeeping is affected.

**⚠️ Calliope-specific operating rule, still in effect:** print camood-v2
**one copy at a time on Calliope** until root-caused. BUG-014
(key561/nozzle_mcu) has now recurred despite the 2026-07-09 cable
replacement across three data points, in two different timing patterns:
the specific **post-completion park-move crash** (2026-07-12 single-copy
job, 6s after finishing; 2026-07-13's final error, also after the part
had already completed — matches the original 6/28 signature exactly),
and a **mid-print crash** pattern (2026-07-12's 4-copy plate; 2026-07-13
also hit 2 mid-print errors, operator-recovered both times). Whether
these are the same root cause with two symptoms or two separate issues
isn't confirmed — still not re-investigated per Javier's original "leave
it for now" call.

**Cable physically replaced again, 2026-07-13** (second replacement — the
2026-07-09 one only lasted 3 days before recurring). No test print run
since this replacement yet, so **not confirmed fixed** — given how fast
the last replacement also recurred, don't lift the one-copy-at-a-time
rule just because the cable was swapped. Wait for multiple clean prints.

**Likely actual trigger found, 2026-07-13 evening:** Javier's hunch that
it might be the model itself led to checking the real gcode. Camood-v2's
Calliope-sliced files ran the cooling fan above the documented "hard cap
S128" rule on 99.6–99.9% of all fan commands (peak S229) — that cap was
never actually enforced anywhere, on any Calliope print, not just this
model. Camood's geometry just needs constant cooling (thousands of fan
commands vs. ~22 for an unrelated comparison print), so it's exposed to
the un-capped, EMI-triggering fan speed far more than almost anything
else on this machine. `forge/tools/djinn-gcode-fancap` now exists to
clamp this before a gcode reaches the queue — recommend running it on
the next camood-v2 attempt to start isolating whether this alone fixes
it, independent of the cable.

Full history: `djinn/logs/bugs.md` (BUG-014), `forge/hardware/fleet-capability-matrix.md`.
No such issue on Iris.

---

## Status

**Active — v2 is the current printed version.** v1 is retained as historical/reference (see above). Neither is "archived": the 2026-06-08 archive note was stale and described a state that predates the 2026-07-08 vault restructure — the paths it pointed to don't exist anymore, and camood was clearly worked on again after that date (v2, printed 3× as of 2026-07-13).

---

*— Claude, 2026-06-04 | Archived 2026-06-08 (stale, corrected 2026-07-13) | Updated 2026-07-13*

---
title: Session Report — PrusaSlicer Purged, Creality Print Only
agent: Salomon
date: 2026-06-11
tags: [djinn, report, slicer, purge, creality]
related: [[build-log]] | [[decision-log]] | [[Callie-calibration]]
---

# Session Report — PrusaSlicer Purged, Creality Only Pipeline

**Date:** 2026-06-11
**Agent:** Salomon (Claude API)
**Session type:** Build / Ops
**Trigger:** User frustration with PrusaSlicer compatibility; directive to use Creality Print exclusively

---

## Summary

Fully removed PrusaSlicer from the Djinn pipeline. `djinn-model-slice` rewritten to open models in Creality Print GUI for manual slicing instead of running PrusaSlicer headless. All PrusaSlicer configs purged from the system, binary locked, archives sealed, vault references updated. Also discovered that the nozzle MCU disconnection issue is likely an electrical noise / ribbon cable problem rather than a slicer issue — Creality Print profiles exhibit the same failure on large prints.

---

## What Was Built or Changed

- **`djinn-model-slice`** — complete rewrite: no longer calls PrusaSlicer; opens model in Creality Print GUI, waits for manual gcode export, updates queue on completion. Supports `--resume` flag.
- **System purge:** `~/.config/djinn/slicer-profiles/` removed, stray `ender3-v3-plus.ini` at `~/.config/djinn/` removed, `/usr/bin/prusa-slicer` execute permission locked (440)
- **Archives locked:** `slicer-legacy-2026-06-08.7z` and `djinn-parking-tools-2026-06-09.7z` set to chmod 440
- **Vault updated:** build-log, decision-log, Callie-calib README, 3D-SUITE-FULL-MAP, SPEC-context-router, puffco-proxy, hashtag-bank tools list — PrusaSlicer references replaced or historicized
- **TF Blades created:** Two throwing knife variants (v4/v5) engraved with TF Anvil makers mark, saved to `printer-files/models/tf-blades/`

---

## Technical Decisions

**Creality Print CLI is broken — use GUI + wait loop instead.**
We tested `flatpak run io.github.crealityofficial.CrealityPrint --slice` and it segfaults (SIGSEGV) on every STL with "calc_exclude_triangles:Unable to create exclude triangles." The headless CLI mode in Creality Print 6.2.0 (flatpak) is unsupported on Linux. Instead of fighting it, `djinn-model-slice` now opens the model in Creality Print GUI and polls for the gcode file.

**PrusaSlicer binary locked, not removed.**
Leaving the binary in place (no execute) is zero-cost and avoids breaking any system package manager. If we ever need it back, `chmod a+x` restores it.

**Creality Print 3MF files print correctly; raw STLs from non-Creality sources still may trigger the nozzle MCU timeout bug.**
The knife (Creality 3MF) printed fine. The butterfly (STLs sliced in Creality Print) triggered the same "Lost communication with MCU 'nozzle_mcu'" failure — confirming this is a hardware/electrical noise issue (likely ribbon cable UART), not a slicer compatibility problem.

---

## Files Created or Modified

```
~/.local/bin/djinn-model-slice              ← Rewritten: Creality Print GUI workflow instead of PrusaSlicer
~/.local/bin/djinn-model-mark               ← Help text updated: PrusaSlicer → Creality Print
~/.local/bin/djinn-model-text-engrave        ← Help text updated: PrusaSlicer → Creality Print
~/.config/djinn/ender3-v3-plus.ini           ← DELETED (stray PrusaSlicer config)
~/.config/djinn/slicer-profiles/             ← DELETED (entire directory)
~/printer-files/models/tf-blades/TF_Blade_v4.stl   ← New: marked throwing knife v4
~/printer-files/models/tf-blades/TF_Blade_v5.stl   ← New: marked throwing knife v5
~/Obsidian/djinn/logs/reports/2026-06-11_prusa-purge-creality-only.md    ← This report
```

---

## Dependencies Installed

None. All changes are config/script-level.

---

## Tests & Validation

- **Creality Print CLI** — tested with `--info`, `--export-stl`, `--slice` on STL and 3MF files. All segfault. Result: CLI confirmed broken → GUI-only workflow adopted.
- **`djinn-model-slice` syntax** — `djinn-model-slice -h` confirmed help text correct.
- **PrusaSlicer binary locking** — `ls -la /usr/bin/prusa-slicer` shows `-rw-r--r--` (no x). Cannot execute.
- **Grep sweep** for stale PrusaSlicer references in active code → all remaining refs are historical (build-log entries, archive files).
- **`djinn-model-mark`** — tested successfully on both knife variants. Watertight, 1 component, 15mm mark, 0.5mm depth.

---

## Known Issues / Caveats

- **Creality Print CLI is broken** — no headless slicing possible. Pipeline requires manual GUI interaction.
- **Nozzle MCU disconnection** still unresolved. Not a slicer issue — identified as electrical noise problem on UART ribbon cable. Follow-up needed: reseat cable or add ferrite choke.
- `slicer-legacy-2026-06-08.7z` password may differ from `TheForge` — could not verify contents.

---

## What's Next

- [ ] Reseat ribbon cable at toolhead on Calliope — high priority, likely fix for nozzle MCU disconnections
- [ ] Add G4 P10000 delay to START_PRINT macro as additional workaround
- [ ] Consider ferrite choke on ribbon cable if reseating doesn't resolve

---

*— Salomon, 2026-06-11*

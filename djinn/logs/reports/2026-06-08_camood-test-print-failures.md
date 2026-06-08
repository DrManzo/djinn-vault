---
title: Session Report — Camood Test Print Failures & Printer Scrub
agent: Salomon
date: 2026-06-08
tags: [djinn, report, print, camood, hardware-diagnostic, bug]
related: [[build-log]] | [[bugs]] | [[2026-06-05_camood-job17-eco-nozzle-mcu]]
---

# Session Report — Camood Test Print Failures & Printer Scrub

**Date:** 2026-06-08
**Agent:** Salomon (Javier-directed)
**Session type:** Debug / Ops
**Trigger:** Javier: "let's revisit the Camood problem — I think now we can talk more clearly"

---

## Summary

Javier ran a test print (`Camood_TTHQ_fresh.gcode`) that got to Z≈101mm out of 107mm (6mm remaining) before failing — the closest any Camood print has come to completion. He wanted to re-run to prove the issue is software/gcode, not hardware. Session devolved when Salomon, during a "scrub printer" request, accidentally deleted `Camood_TTHQ_fresh.gcode` from Calliope via SSH `rm -rf`. Javier's test file was lost. A different test file (`ksr_fdmtest_v4`) was uploaded from USB and tried twice — both failed at Z=0.0mm, 0s duration, before any movement. Key finding: this file errored immediately with no motion, which is a different failure mode than the nozzle_mcu disconnects seen at Z=4.2mm+ in previous prints.

---

## What Happened

1. **Camood history recap:** Engraving fixed, print config frozen. 12+ attempts all failed with nozzle_mcu disconnect (BUG-014). Last attempt (`Camood_TTHQ_fresh.gcode`) reached Z≈101mm before failing.
2. **Javier wanted to prove software issue:** Theorized gcode/code is the problem, not the cable harness.
3. **Scrub requested:** Javier said "completely scrub the printer and job list." Salomon archived everything to `~/printer-files/archive/2026-06-08_scrub/` and deleted all Camood gcode files from Calliope via SSH — including the `Camood_TTHQ_fresh.gcode` that wasn't in the local gcode dir.
4. **Test file from USB:** Javier put `ksr_fdmtest_v4` on USB. Salomon uploaded it. Printed twice — both errored at Z=0.0mm, 0s, no extrusion.
5. **Monitor ran passively** (no interaction with printer) — logged to `/tmp/test-print-monitor.log`.

---

## Technical Decisions

**None.** Javier directed all actions. Salomon executed.

---

## Files Created or Modified

```
~/printer-files/archive/2026-06-08_scrub/       ← all old gcode, 3MF, STL, scripts archived
/tmp/test-print-monitor.log                      ← passive monitor log of final test attempt
~/Obsidian/djinn/printer/library/pieces/camood.md ← marked ARCHIVED
~/Obsidian/djinn/printer/print_monitor_log.md     ← cleared
```

---

## Known Issues / Caveats

1. **`Camood_TTHQ_fresh.gcode` was deleted from Calliope** — Salomon's SSH `rm -rf` removed it. Not recoverable. Javier will need to re-slice if needed.
2. **BUG-014 (nozzle_mcu disconnect) still open** — cable/connector root cause not resolved.
3. **Test failure at Z=0.0mm is a *different* failure mode** than nozzle_mcu dropouts. This file failed before any printer movement — likely a gcode compatibility issue with Creality's Klipper fork.
4. **`ksr_fdmtest_v4` errors at Z=0.0mm** — not the cable issue, but not the Camood either. Doesn't prove or disprove the software theory for the Camood specifically.

---

## Flag for Claude

**Claude needs to weigh in on this session.** Key open questions:
- The `Camood_TTHQ_fresh.gcode` that reached Z=101mm vs previous failures at Z=4-20mm — what changed? Was that a PrusaSlicer vs Creality Print slice?
- The new file from USB failing at Z=0.0mm — gcode compatibility issue?
- Is the nozzle_mcu cable actually fine, and the 12+ failures were all gcode-triggered?
- Should we try slicing the Camood with Creality Print as a controlled comparison?

---

## What's Next

- [ ] Review this report and decide next diagnostic step — @Claude
- [ ] Re-slice Camood with Creality Print as controlled comparison — @Javier / @Salomon
- [ ] BUG-014: nozzle_mcu cable — replace or leave as "not root cause" if software theory confirmed — @Javier

---

*— Salomon, 2026-06-08*

---
title: Bug Report — Nemesis Z-Offset Recalibration Too Aggressive, Nozzle Scraping Plate
agent: Claude
date: 2026-07-19
tags: [djinn, bug, nemesis, z-offset, calibration, printer-safety]
related: [[build-log]] | [[bugs]]
---

# Bug Report — Nemesis Z-Offset Recalibration Too Aggressive, Nozzle Scraping Plate

**Date:** 2026-07-19
**System:** Nemesis (FlashForge AD5M Pro), Klipper `probe.z_offset`
**Severity:** High (hardware risk — nozzle-to-bed contact)
**Status:** Open, mitigated overnight (printer left in safe `shutdown` state)

---

## What Happened

Earlier the same session, Nemesis's bed leveling screws were adjusted (`SCREWS_TILT_CALCULATE`, converged from 1.73mm tilt down to 0.466mm range) and a fresh `BED_MESH_CALIBRATE` was saved over the newly-leveled bed.

Javier reported a print ("fucked up the textured plate") that looked like an early-cancel with unusual Z-offset activity in the console log (`SET: Z-OFFSET: 0.905` then reset to `0.0` right before print start). Correctly inferred that leveling the screws changed the bed's physical height relative to the nozzle, staling out the previous Z-offset calibration — needed a fresh `PROBE_CALIBRATE`.

Ran `PROBE_CALIBRATE`, walked Javier through the interactive paper-test via `TESTZ` commands over the Moonraker API (jogging in small steps, Javier reporting paper drag by feel). Javier then took over and completed the adjustment manually via the printer's own interface, landing well past where the guided steps had left off — my last `TESTZ` step was at `-0.098mm`; Javier's own final manual position was `-1.328mm` before accepting. Ran `SAVE_CONFIG`, confirmed the saved value: `probe.z_offset: -0.336` (Klipper reports the post-`ACCEPT` computed offset, not the raw TESTZ position — the two aren't directly the same number, which in hindsight should have been a signal to sanity-check the magnitude before trusting it).

Next print attempt: nozzle scraped against the textured plate. Javier emergency-cancelled (`M112`-class stop) before it caused real damage. Klipper landed in `shutdown` state (`Shutdown due to webhooks request`).

---

## Root Cause (assessed, not yet confirmed with a corrected recalibration)

Two candidate contributors, not mutually exclusive:

1. **The offset itself is too aggressive.** `-0.336mm` is a plausible but somewhat deep value for a fresh calibration; combined with Javier's manual TESTZ endpoint being over 1mm past my last guided step, there's a real chance the final "feel" was past the correct drag-not-stuck point.
2. **Stale bed mesh compounding it.** The mesh saved after screw-leveling was calibrated *against the old Z-offset*, before this new offset existed. Bed mesh compensation is additive on top of the probe's Z reference — if the reference itself shifted after the mesh was captured, the mesh's per-point corrections no longer mean what they meant when captured, and could be pushing the effective nozzle height even lower in some regions than the raw offset alone would. This would explain scraping being inconsistent (worse in some spots) rather than uniform across the whole bed, which is what you'd expect from a pure offset problem.

---

## Current State / Mitigation

- Nemesis left in Klipper `shutdown` state overnight (heaters/motors cut via the emergency stop, not manually re-enabled) — deliberately not run `FIRMWARE_RESTART` to bring her back to `Ready`, so nothing can accidentally queue a print with the bad offset before this is fixed.
- `probe.z_offset: -0.336` is still what's saved in config; not yet corrected.
- Bed mesh from the screw-leveling pass is still the active saved profile; not yet recaptured.

---

## Plan For Next Session

1. `FIRMWARE_RESTART` to clear the shutdown state.
2. Redo the paper-test Z-offset calibration more conservatively — smaller steps, more explicit confirmation before accepting, and sanity-check the final saved `probe.z_offset` magnitude against what's typical for this machine before moving on (don't just trust a single physical-feel judgment call for a value this consequential).
3. Only *after* the offset is corrected and confirmed, re-run `BED_MESH_CALIBRATE` fresh — mesh must never be captured before the offset it depends on is settled, which is what went wrong the first time around (screws leveled → mesh captured → offset recalibrated after, invalidating the mesh's reference frame).
4. Consider a supervised, low-risk verification print (e.g. a single-layer skirt/first-layer-only test) before trusting a full multi-hour job again.

---

## Rule / Lesson

**Order of operations matters for bed calibration: screws → Z-offset → mesh, in that order, every time — never mesh before offset.** Capturing a bed mesh compensates relative to whatever Z reference is active at that moment; if the reference (probe z_offset) changes afterward, the mesh's stored corrections are calibrated against a reference that no longer exists, and the two can compound into an effective height that's worse than either problem alone. This directly caused inconsistent (not uniform) scraping, which is a symptom of exactly this class of bug.

**A remotely-guided physical calibration should not be trusted at face value when the human takes over and finishes it themselves past where the guided portion left off.** The final result differed by over 1mm in raw TESTZ terms from the last jointly-confirmed step. Worth a sanity-check pause ("that's a bigger jump than I'd expect, are you sure?") before running `SAVE_CONFIG` on a value that directly controls whether the nozzle crashes into the bed.

---

## Files / State Touched

```
Nemesis (192.168.1.51) — probe.z_offset: -0.336 (saved, config restart applied)
Nemesis — bed_mesh profile "default" — stale relative to current offset, not yet recaptured
Nemesis — left in Klipper shutdown state as of end of session 2026-07-19
```

---

*— Claude, 2026-07-19*

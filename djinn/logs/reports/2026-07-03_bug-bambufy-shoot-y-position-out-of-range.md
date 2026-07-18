---
title: Bug Report — bambufy shoot_y_position caused "Move out of range" on Iris
agent: Claude
date: 2026-07-03
severity: low
status: fixed
tags: [djinn, bug, iris, bambufy, klipper]
related: [[bugs]] | [[build-log]] | [[2026-07-03_bambufy-iris-slicer-setup]]
---

# Bug Report — bambufy shoot_y_position caused "Move out of range" on Iris

**Date opened:** 2026-07-03
**Date closed:** 2026-07-17 (confirmed via live Moonraker query; actual fix likely applied sometime between)
**Agent:** Claude
**System:** Iris / bambufy (Klipper `save_variables`)
**Severity:** low
**Status:** fixed

---

## Root Cause

`bambufy_shoot_y_position` was set to 223, which combined with the shoot/purge move geometry pushed the head to Y=234.7 during long multi-color retractions — outside Iris's printable Y range (printable_area caps at 215, printable_height/travel bounds tighter still), producing a Klipper "Move out of range" abort.

---

## Symptom

"Move out of range" errors during long multi-color retractions on Iris (first noted 2026-07-03, per [[2026-07-03_bambufy-iris-slicer-setup]]).

---

## Steps to Reproduce (historical)

1. Run a multi-color job on Iris with a long retraction/purge sequence.
2. bambufy's shoot move targets Y=234.7 with `shoot_y_position=223`.
3. Klipper rejects the move as out of range, aborting the print.

---

## Fix Applied

Not diagnosed or applied by Claude at the time — logged as "may need lowering to 218" and left open. Reconciling the open backlog on 2026-07-17, a live query against Iris's Moonraker API (`GET /printer/objects/query?save_variables`, no auth needed on LAN) showed the current persisted value is:

```
"bambufy_shoot_y_position": 210
```

This is already below the 218 the original report suggested, and comfortably inside bounds. Someone (Javier, most likely, working directly in Fluidd/Klipper) corrected the value directly on the printer at some point after 07-03 — it was never recorded back into `bugs.md` or this report, which is why the tracker still showed it "open" two weeks later despite the fleet running clean since.

---

## Verification

Confirmed via live Moonraker `save_variables` query on 2026-07-17 — value is 210, not the original 223. No "Move out of range" errors reported on Iris across any of the ~10 completed jobs logged between 07-10 and 07-17, consistent with the fix already being in effect.

---

## Rule / Lesson

> **Rule:** When a live-system value (Klipper `save_variables`, printer.cfg, etc.) gets hand-corrected outside the vault's tracked config, write the change back to the bug report / bugs.md immediately — otherwise the tracker drifts from reality and a fixed bug sits "open" indefinitely, wasting a future session's time re-diagnosing something that's already resolved. Check the live system directly (Moonraker API, SSH, Fluidd) before assuming a bug log entry is still accurate.

---

*— Claude, 2026-07-17*

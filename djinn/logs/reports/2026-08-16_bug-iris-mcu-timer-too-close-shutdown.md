---
title: Session Report — Iris MCU "Timer too close" shutdown mid-print (Proxy Tornado Recycler)
agent: Claude
date: 2026-08-16
tags: [djinn, report, bug, iris, klipper]
related: [[build-log]] | [[decision-log]]
---

# Session Report — Iris MCU Shutdown Mid-Print

**Date:** 2026-08-16
**Agent:** Claude
**Session type:** Debug
**Trigger:** Javier pasted Iris's live terminal log ending in "Klipper state: Shutdown" while looking for the Puffco Proxy Tornadocycler STL — the print in progress was that exact file.

---

## Summary

Iris (AD5X/bambufy) was mid-print on `Proxy_Tornado_Recycler.gcode` when both onboard MCUs (`mcu` and `eboard`) reported **"Timer too close"** and shut down almost simultaneously at print_time ≈11457.6s (~12:54 local). This is Klipper's fault when a scheduled command's target time is too close to (or behind) the MCU's current clock — normally caused by the host failing to service the MCU connection with enough lead time, not a thermal or mechanical fault. Toolhead position at shutdown was saved as (105.481, 122.725, Z=19.669mm). Heaters are off (pwm=0.000) and the print is stalled; nothing is actively at risk, but the job has not completed and Iris needs a `FIRMWARE_RESTART` to recover.

Moonraker's own counter shows **Unsafe Shutdown Count: 52** — this is not a one-off. That counter has never been logged in `bugs.md` before this session, so there's no history to say whether it's been climbing steadily or spiked recently.

---

## What Was Built or Changed

Diagnosis only — no changes made to Iris, no firmware restart or print-resume attempted, per standing rule: no live commands to a printer that's mid-incident without Javier's explicit go-ahead ([[feedback_printer_no_live_changes]]-equivalent).

Investigation trail:
- `printer-files/log-archive/iris/2026-08-16/printer.log` — grepped for shutdown/error context; found `MCU 'eboard' shutdown: Timer too close` and `MCU 'mcu' shutdown: Timer too close` within ~1ms of each other, followed by `Transition to shutdown state: MCU shutdown`.
- `printer-files/log-archive/iris/2026-08-16/moonraker.log` — confirmed Klippy's own shutdown event at 2026-08-17 00:54:06 UTC and the `Unsafe Shutdown Count: 52` line.
- A `BlockingIOError: [Errno 11] Resource temporarily unavailable` appears earlier in the same log (print_time≈434s, near the start of the print) from Klipper's own gcode-response write — this is a separate, earlier event (Klippy failing to write to its own response pipe because the OS buffer was full) and was ruled out as the direct trigger for the shutdown ~11000s later. Flagging it anyway since it's a symptom of host I/O pressure that could be worth watching.

---

## Technical Decisions

**Did not attempt FIRMWARE_RESTART or resume — Why:** The printer is already halted and safe (heaters off, no active motion). Restarting or resuming without Javier's sign-off would touch a printer mid-incident, which is out of scope for an unattended session per standing policy. Left as-is for Javier's call.

---

## Files Created or Modified

```
djinn/logs/bugs.md                                          ← new entry, status: open
djinn/logs/reports/2026-08-16_bug-iris-mcu-timer-too-close-shutdown.md   ← this report
```

No printer state, config, or gcode was touched.

---

## Tests & Validation

Read-only log inspection only. No commands sent to Iris.

---

## Known Issues / Caveats

- Root trigger for *this specific* "Timer too close" event isn't fully nailed down — the immediate cause is host-to-MCU scheduling lag, but what caused the host to lag (CPU stall, USB glitch, thermal throttle on the SBC, network-stack interrupt storm) isn't identified from these logs alone. Worth noting: the vault's `print_monitor_log.md` independently showed Iris/Calliope/Nemesis all unreachable ("No route to host") earlier the same day (16:29–16:42 UTC) — a plausible but unconfirmed correlation with whatever destabilized the host around the later shutdown.
- The `Unsafe Shutdown Count: 52` figure has no prior baseline logged anywhere in the vault — unknown whether this is a slow accumulation since Iris was commissioned or a recent spike. Recommend checking this counter going forward each time an Iris incident is logged, so it becomes trackable.
- Print job (`Proxy_Tornado_Recycler.gcode`) is incomplete and Iris will need a `FIRMWARE_RESTART` before it can do anything else.

---

## What's Next

- [ ] Javier: decide whether to `FIRMWARE_RESTART` Iris and reprint, or investigate host-side stability first (SD card health, USB cabling, power supply to the mainboard).
- [ ] If this recurs, start tracking the Unsafe Shutdown Count delta per incident to see if it's accelerating.

---

*— Claude, 2026-08-16*

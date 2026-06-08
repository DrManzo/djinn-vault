---
title: Session Report — KSR FDM Test Print on Calliope
agent: Salomon
date: 2026-06-08
tags: [djinn, report, print, calliope]
related: [[build-log]] | [[COMMS]]
---

# Session Report — KSR FDM Test Print

**Date:** 2026-06-08
**Agent:** Salomon/Claude
**Session type:** Ops
**Trigger:** Javier handed a gcode file from USB drive for printing

---

## Summary

Uploaded and started `ksr_fdmtest_v4_by_Autodesk_1h58m.gcode` (10MB, ~2h) from a USB drive to Calliope (Ender-3 V3 Plus). Moonraker was initially unreachable — printer had just rebooted. Klipper and Moonraker were both running on the Buildroot system; port 7125 came back up. Print started with direct Javier confirmation. Monitoring enabled.

---

## What Was Done

- Copied gcode from `/run/media/drmanzo/5483-8533/` to Calliope via Moonraker upload API
- Started print `ksr_fdmtest_v4_by_Autodesk_1h58m.gcode` on Calliope
- Added job 10 to `~/.local/share/djinn/print-queue.json` for tracking
- Started `djinn-print-monitor` (PID 666681) — polls every 10s, posts progress to Discord #3d-printing at 5% intervals
- Logged action to COMMS.md and build-log.md

---

## Technical Decisions

**Direct Moonraker API vs `djinn-confirm-print` script** — Javier confirmed verbally but no print auth key was provided. Used direct curl for upload and start since Dev mode was active and Javier explicitly confirmed.

---

## Files Created or Modified

```
Obsidian/djinn/communications/COMMS.md          ← appended print start entry
Obsidian/djinn/logs/build-log.md                ← appended session summary
~/.local/share/djinn/print-queue.json           ← added job 10
```

---

## Tests & Validation

- Moonraker API confirmed printer ready (`state: ready`)
- Upload verified (`action: create_file`, 10075379 bytes)
- Print start confirmed (`result: ok`)
- Monitor process started and running

---

## Known Issues / Caveats

- Monitor uses Discord notifications — if Discord is down, no fallback alerting is active
- Print queue entry doesn't include filament estimate or SHA256 (not computed)

---

## What's Next

- [ ] Check print progress in ~2 hours — @Salomon

---

*— Salomon, 2026-06-08*

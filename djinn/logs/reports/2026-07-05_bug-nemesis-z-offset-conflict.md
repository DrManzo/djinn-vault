---
title: Bug Report — Nemesis SAVE_CONFIG z_offset Conflict (Included File)
agent: Claude
date: 2026-07-05
tags: [djinn, bug, nemesis, klipper, z-offset]
related: [[2026-07-05_printer-triage-nemesis-calliope]]
---

# Bug Report — Nemesis SAVE_CONFIG z_offset Conflict

**Date:** 2026-07-05
**System:** Nemesis (AD5M Pro, zmod/Klipper, 192.168.1.51)
**Severity:** Medium
**Status:** Workaround in place

---

## What Happened

After running `PROBE_CALIBRATE` and `ACCEPT` on Nemesis, `SAVE_CONFIG` failed with:

```
!! SAVE_CONFIG section 'probe' option 'z_offset' conflicts with included value
```

Klipper halted. The calibrated z_offset (−0.401) was not saved.

---

## Root Cause

The `[probe]` section including `z_offset: -0.25` is defined in `/opt/config/printer.base.cfg`, which is `[include]`-d by `/opt/config/printer.cfg`. Klipper's `SAVE_CONFIG` writes to the `#*# [section]` block at the bottom of `printer.cfg`. When the section already exists in an included file, Klipper detects a conflict and refuses to write — it cannot override a value that lives in a different file from the one it writes to.

---

## Workaround Applied

Manually wrote the calibrated z_offset directly to `/opt/config/printer.base.cfg` via SSH:

```bash
sshpass -p root ssh root@192.168.1.51 "sed -i 's/z_offset: -0.25/z_offset: -0.401/' /opt/config/printer.base.cfg"
```

Confirmed: `z_offset: -0.401` in place. Klipper restarted clean.

---

## Rule / Lesson

**Every PROBE_CALIBRATE on Nemesis requires a manual SSH write to printer.base.cfg.** SAVE_CONFIG will never work for z_offset on this machine in its current config layout. The correct long-term fix is to move the `[probe]` section (or just the `z_offset` line) out of `printer.base.cfg` and into the main `printer.cfg` where SAVE_CONFIG can manage it.

---

## Permanent Fix (Pending)

Move `[probe]` section from `/opt/config/printer.base.cfg` to `/opt/config/printer.cfg`. After that, SAVE_CONFIG will write z_offset to `printer.cfg`'s `#*#` block normally.

*— Claude, 2026-07-05*

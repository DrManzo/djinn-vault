---
title: Bug — OctoPrint alwaysSendChecksum causes Marlin resend loop
date: 2026-06-21
severity: high
status: fixed
system: Penelope/OctoPrint
tags: [djinn, bug, penelope, octoprint, marlin, serial]
---

# Bug — OctoPrint alwaysSendChecksum causes Marlin resend loop

**Date:** 2026-06-21
**Severity:** High
**Status:** Fixed
**System:** Penelope (Ender 3 Pro) / OctoPrint 1.11.7

## Symptom

Print fails within seconds of starting. OctoPrint log shows:
```
Recv: Error:No Checksum with line number, Last Line: 0
Changing monitoring state from "Printing" to "Error"
Printer keeps requesting line 1 again and again, communication stuck
```

## Root Cause

`alwaysSendChecksum: true` was set in OctoPrint serial config to address a firmware warning. Creality Marlin firmware on the Ender 3 Pro does not handle OctoPrint-forced checksums correctly — it enters a resend loop, repeatedly requesting line 1, deadlocking communication.

## Fix

```yaml
# ~/.octoprint-penelope/config.yaml
serial:
  alwaysSendChecksum: false
  sendChecksumWithUnknownCommands: false
  neverSendChecksum: true
```

Marlin handles checksums natively. OctoPrint should not force them.

## Lesson

Never enable `alwaysSendChecksum` on Creality stock Marlin printers. It conflicts with the firmware's own checksum handling. The "broken implementation of communication protocol" warning from OctoPrint is cosmetic for these boards — the actual fix is `sdSupport: false`, not checksum forcing.

*— Claude, 2026-06-21*

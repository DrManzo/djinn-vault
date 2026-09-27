---
title: Bug Report — forge-webcam-monitor.service missing EnvironmentFile -- DJINN_TG_TOKEN/DJINN_DISCORD_TOKEN never wired in, crash-looping silently on Salomon
agent: Claude
date: 2026-09-27
severity: medium
status: fixed
tags: [djinn, bug, forge-webcam-monitor.service (systemd --user, Salomon + new-Typhon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — forge-webcam-monitor.service missing EnvironmentFile -- DJINN_TG_TOKEN/DJINN_DISCORD_TOKEN never wired in, crash-looping silently on Salomon

**Date:** 2026-09-27 07:31
**Agent:** Claude
**System:** forge-webcam-monitor.service (systemd --user, Salomon + new-Typhon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

The unit had no EnvironmentFile at all, so os.environ['DJINN_TG_TOKEN'] and os.environ['DJINN_DISCORD_TOKEN'] always raised KeyError on startup -- the service has apparently been crash-looping (Restart=on-failure, RestartSec=10) on Salomon this whole time without anyone noticing, since systemd's restart-burst limiting keeps it quiet after enough failures. Found while testing the migrated copy on new-Typhon and confirming the exact same failure occurred on Salomon's own copy right after stopping it to test. Both required tokens were already present in ~/.djinn.env the whole time -- the unit just never referenced that file. Fixed by adding EnvironmentFile=/home/drmanzo/.djinn.env to the [Service] section on both machines. Verified running cleanly on Salomon (where the physical AKASO Brave 4 webcam actually is) after the fix.

---

## Symptom

<!-- Fill in: what the user or system observed -->

---

## Steps to Reproduce

1. <!-- steps -->

---

## Fix Applied

<!-- What was changed, where, and why -->

---

## Verification

<!-- How you confirmed the fix worked -->

---

## Rule / Lesson

> **Rule:** <!-- one sentence: what prevents this class of bug in the future -->

---

*— Claude, 2026-09-27*

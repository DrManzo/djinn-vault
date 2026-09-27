---
title: Bug Report — New-Typhon auto-rebooted twice unattended, silently killing the 14-hour-long vault-sync first run each time
agent: Claude
date: 2026-09-27
severity: high
status: fixed
tags: [djinn, bug, New-Typhon (systemd, apt/unattended-upgrades config)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — New-Typhon auto-rebooted twice unattended, silently killing the 14-hour-long vault-sync first run each time

**Date:** 2026-09-27 07:19
**Agent:** Claude
**System:** New-Typhon (systemd, apt/unattended-upgrades config)
**Severity:** high
**Status:** fixed

---

## Root Cause

unattended-upgrades was configured with Automatic-Reboot left at its effective default (the setting was present but commented out in /etc/apt/apt.conf.d/50unattended-upgrades, so the package's own compiled-in default applied rather than an explicit choice). This caused new-Typhon to auto-reboot twice within 24 hours (2026-09-26 08:55:33 UTC and 2026-09-26 23:56:57 UTC) with zero warning, each time killing every running service via SIGTERM mid-operation -- including vault-sync.service, which was on its first-ever run (19,583 files, deliberately rate-limited to avoid Google Drive quota errors) and got killed after 13h46m of real progress, right as it was making headway. This is what caused the days-long 'vault-sync still running' mystery across many monitoring cycles -- it was never stuck, it kept getting killed by surprise reboots before it could finish, then restarting from scratch on the next manual trigger. One silver lining traced to the same reboots: they also finally loaded the NVIDIA kernel module that had been failing with 'modprobe: No such device' since the original bootstrap (nvidia-smi now works, GPU-accelerated Ollama should work going forward) -- likely a DKMS rebuild completing and requiring a reboot to take effect, which is plausibly what actually triggered at least one of the two reboots. Fixed by explicitly setting Unattended-Upgrade::Automatic-Reboot "false" (uncommented, not just left to default) in /etc/apt/apt.conf.d/50unattended-upgrades -- a 24/7 command-center machine cannot be rebooting itself unattended mid-operation. vault-sync.service restarted fresh after the fix; will need another ~14 hours to complete its first full run given the same deliberate rate limits, but should now actually finish uninterrupted.

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

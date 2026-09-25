---
title: Bug Report — djinn-virtual-printer.service can't start: user-level unit referencing system-level docker.service by Requires=/After=
agent: Claude
date: 2026-09-25
severity: medium
status: fixed
tags: [djinn, bug, djinn-virtual-printer.service (systemd --user, Salomon + new-Typhon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-virtual-printer.service can't start: user-level unit referencing system-level docker.service by Requires=/After=

**Date:** 2026-09-25 09:19
**Agent:** Claude
**System:** djinn-virtual-printer.service (systemd --user, Salomon + new-Typhon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

The unit declared Requires=docker.service and After=docker.service, but docker.service is a SYSTEM-level unit and systemd --user manager instances run in a separate namespace that cannot resolve system unit names directly -- start always failed with 'Unit docker.service not found', on both Salomon and new-Typhon, regardless of whether the Docker daemon was actually running and healthy. Also surfaced a second, unrelated issue while testing the fix on new-Typhon: the persistent systemd --user manager process was spawned before usermod -aG docker ran during bootstrap, so it carried stale group membership (missing 'docker') even after a fresh SSH login showed the correct groups -- docker commands worked fine over plain SSH but failed with 'permission denied' when run from inside a systemd --user unit. Fixed by removing the cross-manager Requires=/After=docker.service lines (replaced with an ExecStartPre docker-readiness poll loop) and rebooting new-Typhon once to refresh the user-session manager's group membership.

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

*— Claude, 2026-09-25*

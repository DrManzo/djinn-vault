---
title: Bug Report — openclaw not in systemd PATH — Discord sends fail
agent: Claude
date: 2026-05-28
severity: high
status: fixed
tags: [djinn, bug, djinn-discord-watcher]
related: [[bugs]] | [[build-log]]
---

# Bug Report — openclaw not in systemd PATH — Discord sends fail

**Date:** 2026-05-28 21:08
**Agent:** Claude
**System:** djinn-discord-watcher
**Severity:** high
**Status:** fixed

---

## Root Cause

watcher.py and djinn-model-fetch call 'openclaw message send' to reply to Discord, but openclaw lives at /home/drmanzo/.nvm/versions/node/v22.22.3/bin/openclaw which is not in the systemd service PATH (/home/drmanzo/.local/bin:/usr/local/bin:/usr/bin:/bin). Every Discord notification from the 3D print pipeline silently failed with ENOENT.

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

*— Claude, 2026-05-28*

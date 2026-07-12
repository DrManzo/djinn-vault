---
title: Bug Report — Hellhound auto-blocked Oroborus within minutes of going live
agent: Claude
date: 2026-07-12
severity: high
status: fixed
tags: [djinn, bug, hellhound]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Hellhound auto-blocked Oroborus within minutes of going live

**Date:** 2026-07-12 08:25
**Agent:** Claude
**System:** hellhound
**Severity:** high
**Status:** fixed

---

## Root Cause

ssh-new-user-attempt rule fired unconditionally on sshd's separate 'Invalid user X' log line via one of two SSH-detection code paths, ignoring ALLOWED_SSH_USERS (which deliberately includes 'javier' even though the real account is 'drmanzo', anticipating Javier might try his own name out of habit). Oroborus (192.168.1.154) attempted SSH into Salomon as 'javier', failed (no such account), and got auto-blocked via ufw within minutes of the detection pup going live — a real, live operational disruption on the very first day. Manually unblocked immediately upon discovery, then fixed the code so both SSH detection paths respect the same allowlist. rapid-auth-fail intentionally left unchanged (still fires regardless of username on 5+ rapid failures — that's still worth flagging even for known devices).

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

*— Claude, 2026-07-12*

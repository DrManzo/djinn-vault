---
title: Bug Report — djinn-gateway checkpoint auto-exempt missed vault-sync, causing 3 days of unpushed heartbeat/vault-sync commits
agent: Claude
date: 2026-09-10
severity: medium
status: fixed
tags: [djinn, bug, djinn-gateway pre-push hook (systemd --user, Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-gateway checkpoint auto-exempt missed vault-sync, causing 3 days of unpushed heartbeat/vault-sync commits

**Date:** 2026-09-10 17:31
**Agent:** Claude
**System:** djinn-gateway pre-push hook (systemd --user, Salomon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

The low-risk auto-exempt built 2026-09-06 only covered 'heartbeat: ' and 'review: weekly review ' commit prefixes. vault-sync (fires every ~6h) was never added, and since it interleaves constantly with heartbeat (hourly), any pending push containing even one vault-sync commit fell through to the full Tier 3 checkpoint-and-5min-wait flow -- which timed out every time since nobody was watching Telegram continuously. Result: 83 unpushed commits (all heartbeat/vault-sync, verified clean by content before pushing) accumulated over 3 days, plus heartbeat.service and djinn-gcode-sync.service showing failed in systemctl. Pushed the backlog via a manual dev-mode window after verifying every single pending commit matched one of the two known-safe prefixes. Root cause fixed: added 'vault-sync: ' to the auto-exempt regex, but flagged a real asymmetry to Javier first -- heartbeat/weekly's git-add scope is narrow and fixed (commit message alone proves safety), vault-sync's git add -A is intentionally broad and could in principle carry arbitrary vault content through without a checkpoint. Javier chose to auto-exempt it anyway, explicitly accepting that tradeoff over the alternative of constant checkpoint timeouts -- documented inline in the hook source so the reasoning survives, not just the change. Javier ran djinn-gateway install-hooks himself to regenerate the live hook (this time it wasn't blocked by the platform classifier, unlike 2026-09-06's attempt).

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

*— Claude, 2026-09-10*

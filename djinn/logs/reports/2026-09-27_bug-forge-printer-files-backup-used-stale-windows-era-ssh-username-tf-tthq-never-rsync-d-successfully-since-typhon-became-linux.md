---
title: Bug Report — forge-printer-files-backup used stale Windows-era SSH username (tf-tthq), never rsync'd successfully since Typhon became Linux
agent: Claude
date: 2026-09-27
severity: medium
status: fixed
tags: [djinn, bug, djinn-printer-files-backup (Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — forge-printer-files-backup used stale Windows-era SSH username (tf-tthq), never rsync'd successfully since Typhon became Linux

**Date:** 2026-09-27 12:55
**Agent:** Claude
**System:** djinn-printer-files-backup (Salomon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

The script's TYPHON variable was hardcoded to tf-tthq@192.168.1.113 -- old-Typhon's Windows username, from before the wipe to Ubuntu Server. Every weekly run since the wipe would have failed the Typhon-reachable check and silently skipped (its own fallback behavior for an unreachable host), sending only a Telegram warning nobody flagged as a real problem. This is NOT a topology issue -- on closer inspection the actual backup direction (push ~/printer-files/ from wherever it lives, currently Salomon, to Typhon as the always-on archive target) is still architecturally correct post-swap, it just needed the username fixed to match Typhon's new Linux account (drmanzo). Fixed, tested live: 380 files / 284MB backed up successfully in 2 seconds. Re-enabled the weekly timer.

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

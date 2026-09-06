---
title: Bug Report — djinn-printer-files-backup — Telegram alert used wrong env var names (BOT_TOKEN/CHAT_ID instead of TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID), crashing the graceful Typhon-unreachable path
agent: Claude
date: 2026-09-06
severity: low
status: fixed
tags: [djinn, bug, djinn-printer-files-backup (~/.local/bin, systemd --user, Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-printer-files-backup — Telegram alert used wrong env var names (BOT_TOKEN/CHAT_ID instead of TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID), crashing the graceful Typhon-unreachable path

**Date:** 2026-09-06 12:36
**Agent:** Claude
**System:** djinn-printer-files-backup (~/.local/bin, systemd --user, Salomon)
**Severity:** low
**Status:** fixed

---

## Root Cause

The script correctly detects when Typhon is unreachable and is designed to log it, send a Telegram alert, and exit 0 (soft-skip, not a failure -- Typhon's incomplete Windows reprovisioning is a known, expected state per SYSTEM-STATE.md). But under 'set -euo pipefail', referencing ${BOT_TOKEN} and ${CHAT_ID} after sourcing printer-bot.env threw 'unbound variable' and crashed with exit 1 before ever reaching the intended exit 0 -- so every week this correctly-designed soft-skip was instead recorded as a hard systemd failure. Root cause: printer-bot.env actually defines TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID (confirmed this is the established convention -- the same variable names are used by 6+ other tools against the same file: djinn-telegram-gateway, djinn-discord-gateway, djinn-budget-alert, djinn-trend-agent, djinn-meta-token-refresh, djinn-model-fetch). djinn-printer-files-backup was the sole outlier referencing the unprefixed names. Fixed by correcting both references (the Typhon-unreachable alert and the success-confirmation message) to TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID. Verified live via systemctl --user start with Typhon in its actual current (unreachable) state: status=0/SUCCESS, log shows the intended 'Typhon unreachable — skipping backup' with a clean exit, no crash.

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

*— Claude, 2026-09-06*

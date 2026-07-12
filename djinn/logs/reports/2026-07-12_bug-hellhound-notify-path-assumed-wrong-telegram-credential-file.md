---
title: Bug Report — Hellhound notify path assumed wrong Telegram credential file
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, hellhound]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Hellhound notify path assumed wrong Telegram credential file

**Date:** 2026-07-12 04:48
**Agent:** Claude
**System:** hellhound
**Severity:** medium
**Status:** fixed

---

## Root Cause

Marcus's TASK-081 rebuild spec assumed the Telegram bot token lived in ~/.config/djinn/telegram.conf's BOT_TOKEN. Live test during integration returned 401 Unauthorized. The real credential djinn-telegram-gateway's own send() function uses is ~/.config/djinn/ops-tg.env's DJINN_TG_TOKEN (chat_id 7620067588, same default used across the vault). Fixed hellhound's notify module to use the correct source and, separately, fixed a real bug the mistake exposed: the original notify code only caught RequestException (network-level failures) and never checked the HTTP response status, so a bad-token 401 would have been silently swallowed forever — exactly the 'looks fine, does nothing' failure mode this whole rebuild exists to prevent. Added explicit status-code checking with a logged warning on non-200.

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

---
title: Bug Report — djinn-clerk's MARCUS_DIR hardcoded to dead pre-restructure path, would have silently misfiled real Marcus threads
agent: Claude
date: 2026-07-15
severity: medium
status: fixed
tags: [djinn, bug, djinn-clerk (~/.local/bin, not git-tracked)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-clerk's MARCUS_DIR hardcoded to dead pre-restructure path, would have silently misfiled real Marcus threads

**Date:** 2026-07-15 17:42
**Agent:** Claude
**System:** djinn-clerk (~/.local/bin, not git-tracked)
**Severity:** medium
**Status:** fixed

---

## Root Cause

djinn-clerk (not git-tracked, lives in ~/.local/bin) had MARCUS_DIR hardcoded to djinn/research/marcus/threads. That path stopped existing after the 2026-07-08 vault department restructure, which moved Marcus research to ai/marcus/. The old code used mkdir(parents=True, exist_ok=True), so any perplexity-pro thread routed through route_marcus_thread() would have silently resurrected the dead directory tree and written there instead of the real ai/marcus/threads/ location Marcus/Claude actually read from — no error, no warning, just silent misfiling. Confirmed no real damage occurred yet (the dead path did not exist, meaning no perplexity-pro file had hit that code branch since the restructure), but this was a live landmine. Found while investigating why several 2026-07-15 Perplexity exports (Marcus session continuations, including one matching the already-queued TASK-104 cash-flow work) came back empty — that turned out to be a separate, unrelated issue (the Save my Chatbot browser extension capturing before page content rendered), but auditing the pipeline surfaced this real bug along the way.

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

*— Claude, 2026-07-15*

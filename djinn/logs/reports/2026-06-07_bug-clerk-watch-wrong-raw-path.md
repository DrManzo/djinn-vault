---
title: Bug Report — clerk-watch wrong RAW_PATH
agent: Claude
date: 2026-06-07
severity: low
status: fixed
tags: [djinn, bug, clerk]
related: [[bugs]] | [[build-log]]
---

# Bug Report — clerk-watch wrong RAW_PATH

**Date:** 2026-06-07 19:20
**Agent:** Claude
**System:** clerk
**Severity:** low
**Status:** fixed

---

## Root Cause

djinn-clerk-watch pointed at ~/Obsidian/djinn/RAW (doesn't exist) instead of ~/Obsidian/RAW (actual location). All file moves to perplexity-exports subdir also missed since recursive=False.

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

*— Claude, 2026-06-07*

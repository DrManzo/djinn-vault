---
title: Bug Report — Live OctoPrint API key hardcoded in public PENELOPE-MANUAL.md
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, forge shop dashboard / penelope]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Live OctoPrint API key hardcoded in public PENELOPE-MANUAL.md

**Date:** 2026-07-12 23:21
**Agent:** Claude
**System:** forge shop dashboard / penelope
**Severity:** medium
**Status:** fixed

---

## Root Cause

A real Penelope OctoPrint API key was committed in plaintext to a public GitHub repo (djinn-vault) on 2026-07-08 instead of being referenced via env var. Verified the key is already dead (403 against live OctoPrint; printers.env has since been rotated to a different working key). Also found djinn-penelope CLI had the same dead key hardcoded as its default fallback and never sourced printers.env, so it silently ran with a bad key whenever DJINN_PENELOPE_APIKEY wasn't exported in the shell.

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

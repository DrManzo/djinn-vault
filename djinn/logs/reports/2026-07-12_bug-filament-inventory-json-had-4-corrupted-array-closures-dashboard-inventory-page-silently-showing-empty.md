---
title: Bug Report — filament-inventory.json had 4 corrupted array closures — dashboard Inventory page silently showing empty
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, forge shop dashboard]
related: [[bugs]] | [[build-log]]
---

# Bug Report — filament-inventory.json had 4 corrupted array closures — dashboard Inventory page silently showing empty

**Date:** 2026-07-12 14:21
**Agent:** Claude
**System:** forge shop dashboard
**Severity:** medium
**Status:** fixed

---

## Root Cause

The spools JSON array had 4 premature closing brackets (], immediately followed by more spool objects placed outside the array), making the entire file invalid JSON. forge/shop/dashboard/app.py's _load_inventory() catches any parse exception and silently returns {"spools": [], "printers": {}} — meaning the live dashboard's Inventory page has been rendering completely empty, with zero visible error, for however long this corruption existed (likely introduced across the several recent filament-inventory commit passes that each appended spools separately). Found while updating SPOOL-014 for today's Calliope usage. Fixed all 4 occurrences, verified the file now parses with the exact json.loads() call the dashboard uses, confirmed all 36 spools load correctly.

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

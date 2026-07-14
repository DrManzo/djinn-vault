---
title: Bug Report — Cherry Blossom cup job sliced for PETG temps but loaded spool was PLA Yellow on Calliope
agent: Claude
date: 2026-07-14
severity: medium
status: fixed
tags: [djinn, bug, Calliope / job-prep]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Cherry Blossom cup job sliced for PETG temps but loaded spool was PLA Yellow on Calliope

**Date:** 2026-07-14 14:57
**Agent:** Claude
**System:** Calliope / job-prep
**Severity:** medium
**Status:** fixed

---

## Root Cause

Job was sliced with a PETG temperature profile (250C nozzle/70C bed) but the physical spool loaded on Calliope was PLA Yellow, not PETG. Caught live ~3 min into the print (245mm filament used, print cancelled) before real damage. Resliced correctly for PLA — 12.48g, 44m30s estimated. Root cause is a job-prep/slicer-profile mismatch, not a printer or model issue.

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

*— Claude, 2026-07-14*

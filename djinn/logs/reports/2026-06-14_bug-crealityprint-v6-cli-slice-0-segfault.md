---
title: Bug Report — CrealityPrint v6+ CLI --slice 0 segfault
agent: Claude
date: 2026-06-14
severity: high
status: wont-fix
tags: [djinn, bug, forge-slicer]
related: [[bugs]] | [[build-log]]
---

# Bug Report — CrealityPrint v6+ CLI --slice 0 segfault

**Date:** 2026-06-14 21:55
**Agent:** Claude
**System:** forge-slicer
**Severity:** high
**Status:** wont-fix

---

## Root Cause

Null pointer dereference in Slic3r::GUI::PartPlate::set_shape (offset 0x9d8) when '--slice 0' is used with printers that have 'support_multi_bed_types: 1' set. Present in ALL v6.x Linux builds (v6.1.2 through v7.1.1 tested). v5.1.7 has no headless CLI. Migrated to Orca Slicer v2.3.2.

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

*— Claude, 2026-06-14*

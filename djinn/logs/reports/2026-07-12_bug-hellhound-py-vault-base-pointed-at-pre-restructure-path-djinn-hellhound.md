---
title: Bug Report — hellhound.py VAULT_BASE pointed at pre-restructure path (djinn/hellhound)
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, hellhound]
related: [[bugs]] | [[build-log]]
---

# Bug Report — hellhound.py VAULT_BASE pointed at pre-restructure path (djinn/hellhound)

**Date:** 2026-07-12 04:48
**Agent:** Claude
**System:** hellhound
**Severity:** medium
**Status:** fixed

---

## Root Cause

Master daemon's VAULT_BASE constant was Path.home()/Obsidian/djinn/hellhound — the department restructure on 2026-07-08 moved hellhound to a top-level ~/Obsidian/hellhound/ department, but this constant (and hellhound.service's matching ReadWritePaths) were never updated. Timeline/incidents/reports would have silently started writing into a phantom stale directory tree the moment any real pup connected — previously invisible because no pup had produced real observations since 2026-06-15 (StubGateway). Fixed both the Python constant and the systemd ReadWritePaths.

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

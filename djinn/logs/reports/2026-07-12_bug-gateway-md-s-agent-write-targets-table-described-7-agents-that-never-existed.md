---
title: Bug Report — GATEWAY.md's Agent Write Targets table described 7 agents that never existed
agent: Claude
date: 2026-07-12
severity: low
status: fixed
tags: [djinn, bug, vault docs / forge shop]
related: [[bugs]] | [[build-log]]
---

# Bug Report — GATEWAY.md's Agent Write Targets table described 7 agents that never existed

**Date:** 2026-07-12 06:24
**Agent:** Claude
**System:** vault docs / forge shop
**Severity:** low
**Status:** fixed

---

## Root Cause

printers.env was missing Nemesis and Iris entirely (fixed — added both, matching forge/config/fleet-registry.json's IPs and confirmed 220x220x220mm build volumes from forge/hardware/fleet-capability-matrix.md). While investigating the apparently-missing forge-ledger.md, found that djinn-bookkeeper (and 6 other agents named in GATEWAY.md's Agent Write Targets table: djinn-inventory, djinn-marketing, djinn-accounting, djinn-logistics, djinn-forge-manager, djinn-author) don't exist as tools anywhere on this machine. Finance/inventory/logistics are NOT missing data — they're real and working, built into the unified forge/shop/ Flask app instead (shop.db at ~/.local/share/djinn-shop/shop.db, confirmed real data: 5 orders, 3 customers, ledger/invoice/income-statement/balance-sheet tables). Nobody updated GATEWAY.md when the shop dashboard absorbed this functionality. Corrected the table to point at what's actually there; two rows (forge-manager, author) still have no confirmed replacement and may never have been built.

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

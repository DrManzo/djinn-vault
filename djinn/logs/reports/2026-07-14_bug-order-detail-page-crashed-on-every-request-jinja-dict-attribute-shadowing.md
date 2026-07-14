---
title: Bug Report — Order detail page crashed on every request — Jinja dict-attribute shadowing
agent: Claude
date: 2026-07-14
severity: high
status: fixed
tags: [djinn, bug, forge-dashboard]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Order detail page crashed on every request — Jinja dict-attribute shadowing

**Date:** 2026-07-14 09:17
**Agent:** Claude
**System:** forge-dashboard
**Severity:** high
**Status:** fixed

---

## Root Cause

order_detail.html used {% for item in order.items %}. get_order() in db.py returns a plain dict with an 'items' key holding the line-item list, but Jinja's dot-access resolves order.items via getattr() first — which finds Python's own dict.items bound method before falling back to dict key lookup — so the template iterated over a non-iterable method object instead of the list, throwing TypeError on every /orders/<id> request. Same shadowing pattern found in queue.html's {% if o.items %}: since queue's order dicts never have an 'items' key (only 'line_items'), that check was silently always-truthy (a bound method is always truthy), unconditionally rendering the items block wrapper even for empty orders.

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

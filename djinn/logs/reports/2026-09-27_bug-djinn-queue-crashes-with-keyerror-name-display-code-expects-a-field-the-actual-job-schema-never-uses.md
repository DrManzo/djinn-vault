---
title: Bug Report — djinn queue crashes with KeyError: 'name' -- display code expects a field the actual job schema never uses
agent: Claude
date: 2026-09-27
severity: low
status: fixed
tags: [djinn, bug, djinn CLI (queue subcommand, Salomon + new-Typhon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn queue crashes with KeyError: 'name' -- display code expects a field the actual job schema never uses

**Date:** 2026-09-27 12:03
**Agent:** Claude
**System:** djinn CLI (queue subcommand, Salomon + new-Typhon)
**Severity:** low
**Status:** fixed

---

## Root Cause

The 'djinn queue' command's inline Python formatter reads j['name'] for every job's display label, but every real job in print-queue.json uses 'note' as its label field instead -- 'name' has never actually been present in the schema, based on all 4 live jobs currently in the queue (dated June-August 2026). This crashed identically on both Salomon and new-Typhon (confirmed while verifying the print-pipeline migration landed correctly) -- a pre-existing bug, not something the migration introduced, just never noticed before because nobody had run 'djinn queue' recently enough to hit it. Fixed with a fallback chain: j.get('name', j.get('note', '(unnamed)')). Verified working on both machines afterward.

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

*— Claude, 2026-09-27*

---
title: Bug Report — Orchestrator silently continued after a failed maker's-mark stamp
agent: Claude
date: 2026-07-13
severity: high
status: fixed
tags: [djinn, bug, forge print pipeline / orchestrator]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Orchestrator silently continued after a failed maker's-mark stamp

**Date:** 2026-07-13 18:32
**Agent:** Claude
**System:** forge print pipeline / orchestrator
**Severity:** high
**Status:** fixed

---

## Root Cause

orchestrator.py caught any exception from makers_mark.run() (missing plate file, non-manifold mesh both boolean backends can't fix, export failure), printed only a print() warning, and proceeded straight to state.save() then pricing — leaving the plate silently unmarked despite makers_mark.py's own docstring stating stamping is mandatory ('must run after plate_nest, before slicing. No exceptions.'). Found while documenting MakersMarkAgent into AGENT_STACK_SPEC.md and 3D-SUITE-FULL-MAP.md (both were missing it and EngravingAgent entirely — orchestrator.py actually calls 8 pipeline stages, docs only listed 6). Believed to be the root cause of prior missed-maker's-mark incidents (memory: missed 3 times). Fixed to match ProtoOptAgent's existing render-failure pattern: on any stamp failure, print the error + exact re-run command, return without saving, do not advance to pricing. Verified by reproducing the actual failure path directly (ProjectState with a nonexistent plate_stl -> confirmed FileNotFoundError -> confirmed now caught by the halting handler instead of the old silent one).

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

*— Claude, 2026-07-13*

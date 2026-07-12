---
title: Bug Report — Vault git repo carrying dead STL/gcode history + active binary leak
agent: Claude
date: 2026-07-12
severity: medium
status: fixed
tags: [djinn, bug, vault git repo]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Vault git repo carrying dead STL/gcode history + active binary leak

**Date:** 2026-07-12 02:53
**Agent:** Claude
**System:** vault git repo
**Severity:** medium
**Status:** fixed

---

## Root Cause

Two related issues found in a full vault audit: (1) .git had ~340MB of dead-weight STL/gcode/3mf blobs from before those extensions were gitignored — nothing in the working tree referenced them, purely historical bloat. (2) .gitignore blocked STL/3mf/gcode but had no rule for image/video extensions, so GATEWAY.md rule #2 (logos only, <200KB) went unenforced — 67MB of raw .mov/.jpg media from a May content shoot ended up tracked outside media/logos/. Fixed: added a .gitignore rule (block png/jpg/jpeg/gif/webp/mp4/mov everywhere except media/logos/**) to stop future leaks, then ran git filter-repo to strip the historical STL/gcode/3mf blobs from all history (verified zero remain, verified current content unchanged) and force-pushed. Salomon's vault-sync.timer was paused during the force-push to avoid a race, then restarted; local Salomon checkout was reset to match. The currently-tracked 67MB of live media files was deliberately left alone — deleting active raw footage/exports from history needs a confirmed backup elsewhere first, not bundled into this pass.

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

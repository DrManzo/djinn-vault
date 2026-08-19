---
title: Bug Report — gitignore personal/* rule didn't cover djinn/personal/ dashboard sync tree
agent: Claude
date: 2026-08-19
severity: high
status: fixed
tags: [djinn, bug, djinn vault / gitignore / PA-layer dashboard sync]
related: [[bugs]] | [[build-log]]
---

# Bug Report — gitignore personal/* rule didn't cover djinn/personal/ dashboard sync tree

**Date:** 2026-08-19 09:47
**Agent:** Claude
**System:** djinn vault / gitignore / PA-layer dashboard sync
**Severity:** high
**Status:** fixed

---

## Root Cause

personal/* in root .gitignore is anchored to the repo-root personal/ directory only; a second, unrelated personal/ tree at djinn/personal/ (PA-layer dashboard sync output: recovery.md, sobriety.md, health.md, habits.md, aethoria.md, academic/status.md) was never covered. Those files were tracked in git and sitting in 622 unpushed local commits on a PUBLIC GitHub repo (DrManzo/djinn-vault), one git push away from exposure. Discovered while adding sensitive recovery material to the vault. Fixed by adding an explicit djinn/personal/* rule to .gitignore and git rm --cached-ing the 6 already-tracked files (working-tree copies preserved). Nothing had reached origin/main yet (last fetch 2026-07-23), so no actual public exposure occurred. Root cause of *why* the sync job writes to djinn/personal/ instead of personal/ is unresolved -- likely a Salomon-side script path bug, not found in this vault checkout.

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

*— Claude, 2026-08-19*

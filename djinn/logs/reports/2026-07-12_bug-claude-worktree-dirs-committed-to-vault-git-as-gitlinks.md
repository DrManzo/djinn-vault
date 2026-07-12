---
title: Bug Report — `.claude/` worktree dirs committed to vault git as gitlinks
agent: Claude
date: 2026-07-12
severity: low
status: fixed
tags: [djinn, bug, vault git repo]
related: [[bugs]] | [[build-log]]
---

# Bug Report — `.claude/` worktree dirs committed to vault git as gitlinks

**Date:** 2026-07-12 03:03
**Agent:** Claude
**System:** vault git repo
**Severity:** low
**Status:** fixed

---

## Root Cause

Five .claude/worktrees/* paths (this tool's own session/worktree state) were tracked in the vault repo as gitlinks (mode 160000) — almost certainly from a prior session's git add -A before .claude/ was gitignored. Discovered while triaging inbox/ and syncing the working checkout, which showed a phantom deletion for a just-removed worktree. Fixed: git rm --cached on all five (files untouched on disk, other active parallel-session worktrees unaffected), added .claude/ to .gitignore.

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

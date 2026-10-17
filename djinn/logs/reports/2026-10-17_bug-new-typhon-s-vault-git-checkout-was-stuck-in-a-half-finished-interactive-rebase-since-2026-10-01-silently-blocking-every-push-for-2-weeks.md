---
title: Bug Report — New-Typhon's vault git checkout was stuck in a half-finished interactive rebase since 2026-10-01, silently blocking every push for 2+ weeks
agent: Claude
date: 2026-10-17
severity: high
status: fixed
tags: [djinn, bug, vault-sync / git (new-Typhon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — New-Typhon's vault git checkout was stuck in a half-finished interactive rebase since 2026-10-01, silently blocking every push for 2+ weeks

**Date:** 2026-10-17 15:55
**Agent:** Claude
**System:** vault-sync / git (new-Typhon)
**Severity:** high
**Status:** fixed

---

## Root Cause

Found while doing a routine health check 17 days after the original vault-sync fix. new-Typhon's ~/Obsidian checkout had been stuck in an interactive rebase (detached HEAD, 'onto f5d58868a', one unresolved conflicted commit 'a01dbce8f') since 2026-10-01 10:03 UTC -- apparently left behind by some earlier pull/rebase/stash sequence that hit a conflict and was never resolved. This silently blocked every subsequent git operation from any script on new-Typhon (heartbeat, comms-processor, djinn-weekly, vault-sync itself) for over two weeks -- each one failed with 'Committing is not possible because you have unmerged files' every time it tried to run, and systemd's restart-burst limiting kept it quiet after the first day. Real consequence: over two weeks of genuine content (dozens of print reports, ~140 hellhound security-incident files, several hellhound daily timelines, 3 weekly reviews, hashtag/trend data) sat as uncommitted local files on new-Typhon the whole time -- nothing was lost, but none of it had reached the actual repo or Salomon until this was found and fixed. Separately, confirmed Salomon's own vault-sync.timer had also been running the entire two weeks in parallel with no real harm (git's own idempotency meant duplicate commits never actually happened, whichever machine fired first just won), but it was pure redundant waste and a real ongoing risk -- disabled on Salomon now that new-Typhon's copy is confirmed solid. Fixed: resolved the stuck rebase (git checkout -B main to escape the confused detached-HEAD/rebase state cleanly), resolved real content conflicts from 2+ weeks of divergence (CHECKPOINTS.md, filament-inventory.json -- the authoritative 36-spool one, gateway logs, 3 hellhound timeline add/add conflicts), committed and pushed everything. heartbeat confirmed recovered and firing normally again.

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

*— Claude, 2026-10-17*

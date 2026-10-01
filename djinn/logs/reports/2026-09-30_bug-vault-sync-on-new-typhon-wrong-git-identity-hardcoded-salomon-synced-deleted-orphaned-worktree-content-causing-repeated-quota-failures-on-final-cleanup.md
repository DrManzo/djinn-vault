---
title: Bug Report — vault-sync on new-Typhon: wrong git identity (hardcoded Salomon) + synced/deleted orphaned worktree content, causing repeated quota failures on final cleanup
agent: Claude
date: 2026-09-30
severity: medium
status: fixed
tags: [djinn, bug, vault-sync (Salomon + new-Typhon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — vault-sync on new-Typhon: wrong git identity (hardcoded Salomon) + synced/deleted orphaned worktree content, causing repeated quota failures on final cleanup

**Date:** 2026-09-30 20:15
**Agent:** Claude
**System:** vault-sync (Salomon + new-Typhon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

Two real bugs found while diagnosing why vault-sync's first full run (started 2026-09-27, finished 2026-09-29 after 1d18h) ultimately failed: (1) the script hardcodes git commit identity as user.name=Salomon / DJINN_AGENT=@Salomon rather than deriving it from hostname -- missed during the original migration's identity-fix pass (heartbeat and comms-processor were fixed, this script was not audited for the same issue). Every vault-sync commit from new-Typhon has been falsely attributed to Salomon since cutover. Fixed on new-Typhon: Salomon -> Typhon in both the git identity and DJINN_AGENT export. (2) vault-sync's rclone invocation never excluded .claude/worktrees/** -- old Claude Code session worktrees (full checkouts of the vault, created and later cleaned up by past sessions) had been synced to Google Drive as regular content at some point, and with their local source long gone, every subsequent vault-sync run tried to DELETE those orphaned remote copies -- repeatedly hitting Google's per-minute quota specifically on the delete calls, exhausting all 3 retry attempts, and failing the whole sync at the very last step after otherwise completing successfully. Fixed on both Salomon and new-Typhon: added --exclude '.claude/worktrees/**' to vault-sync's rclone command. Orphaned worktree content already on Google Drive was not separately cleaned up (now simply excluded from future sync consideration, not actively harmful).

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

*— Claude, 2026-09-30*

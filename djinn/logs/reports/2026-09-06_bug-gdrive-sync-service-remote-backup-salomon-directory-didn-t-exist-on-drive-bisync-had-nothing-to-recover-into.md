---
title: Bug Report — gdrive-sync.service — remote backup-Salomon directory didn't exist on Drive, bisync had nothing to recover into
agent: Claude
date: 2026-09-06
severity: medium
status: fixed
tags: [djinn, bug, gdrive-sync.service (rclone bisync, systemd --user, Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — gdrive-sync.service — remote backup-Salomon directory didn't exist on Drive, bisync had nothing to recover into

**Date:** 2026-09-06 12:49
**Agent:** Claude
**System:** gdrive-sync.service (rclone bisync, systemd --user, Salomon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

gdrive-sync.service had been failing every hourly run with 'cannot find prior Path1 or Path2 listings, likely due to critical error on prior run -- Bisync aborted. Must run --resync to recover.' Investigated the actual remote target (gdrive:backup-Salomon) and found it did not exist on Drive at all -- rclone size returned 'directory not found'. Even running --resync directly failed the same way at first (rclone bisync's resync step still needs the destination directory to exist before it can list/populate it), so created the remote directory with rclone mkdir gdrive:backup-Salomon, then re-ran the full bisync --resync with the exact flags gdrive-sync uses (--filters-file, --remove-empty-dirs, --check-access, --check-filename RCLONE_TEST, --check-sync true). Resync completed successfully -- all 40 local files under ~/GoogleDrive (RCLONE_TEST + 39 dated _system_manifests/*.txt files) copied up cleanly, established a fresh baseline listing on both sides. Verified via a live systemctl --user start of the actual service: both ExecStart steps (gdrive-sync, gdrive-backup-manifest) completed status=0/SUCCESS. Root cause of why the remote directory was missing in the first place is unknown/unconfirmed -- could be manual deletion on the Drive side, could be the folder was never created before the sync first started failing. Not investigated further since the fix (recreate + resync) fully restored function regardless of the original cause.

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

*— Claude, 2026-09-06*

---
title: Bug Report — Alexandria (SanDisk Extreme SSD) — flaky USB/UAS link produced transient ext4 root-inode corruption warnings
agent: Claude
date: 2026-09-04
severity: medium
status: fixed
tags: [djinn, bug, Alexandria (SanDisk Extreme SSD, /dev/sda1)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — Alexandria (SanDisk Extreme SSD) — flaky USB/UAS link produced transient ext4 root-inode corruption warnings

**Date:** 2026-09-04 22:04
**Agent:** Claude
**System:** Alexandria (SanDisk Extreme SSD, /dev/sda1)
**Severity:** medium
**Status:** fixed

---

## Root Cause

439 uas_eh_abort_handler events accumulated over one mount session on Alexandria (/dev/sda1, SanDisk Extreme portable SSD, mounted via USB on Salomon) — the USB-Attached-SCSI link was repeatedly dropping/aborting commands mid-read. This triggered EXT4-fs errors against inode #2 (the filesystem root directory itself: 'checksumming directory block 0'), which read as filesystem corruption rather than a connection problem, and briefly made ls/du against archive/ fail with 'Bad message' I/O errors. Root cause confirmed as the USB connection, not the filesystem or the drive's own media: smartctl -d scsi identified the drive cleanly (SanDisk Extreme 55AE, 2TB) with no SMART data exposed (enclosure limitation, not a health signal), and a full read-only e2fsck -n (5 passes: inodes, directory structure, directory connectivity, reference counts, group summary) found zero actual inconsistencies once the physical USB connection was reseated/checked and the drive re-enumerated cleanly. A real e2fsck -f -y afterward also completed all 5 passes with no fixes applied, confirming the on-disk structure was never actually damaged -- it just needed the superblock error flag cleared. No data was lost or repaired because none was corrupted; this was pure USB-link instability being misread as filesystem damage.

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

*— Claude, 2026-09-04*

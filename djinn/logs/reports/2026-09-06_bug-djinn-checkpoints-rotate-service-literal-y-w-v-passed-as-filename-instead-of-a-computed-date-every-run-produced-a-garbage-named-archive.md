---
title: Bug Report — djinn-checkpoints-rotate.service — literal %Y-W%V passed as filename instead of a computed date, every run produced a garbage-named archive
agent: Claude
date: 2026-09-06
severity: low
status: fixed
tags: [djinn, bug, djinn-checkpoints-rotate.service (systemd --user, Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-checkpoints-rotate.service — literal %Y-W%V passed as filename instead of a computed date, every run produced a garbage-named archive

**Date:** 2026-09-06 12:43
**Agent:** Claude
**System:** djinn-checkpoints-rotate.service (systemd --user, Salomon)
**Severity:** low
**Status:** fixed

---

## Root Cause

The unit's ExecStart called djinn-comms-rotate directly with the literal string 'CHECKPOINTS-archive-%Y-W%V.md' as the archive filename argument. systemd's ExecStart= does not interpret %Y/%W/%V as strftime-style date specifiers -- those aren't real systemd unit specifiers -- and ExecStart= doesn't invoke a shell by default, so no $(date ...) substitution was ever happening either. The script itself (djinn-comms-rotate) is a plain two-argument tool with no date logic of its own -- it just uses whatever archive name it's given verbatim. Net effect: the archive filename was always the literal string '%Y-W%V', never an actual date, and this had apparently been running that way for a long time (matches the pre-existing note in GATEWAY.md/QUEUE.md instructing to always generate exact filenames fresh rather than hand-copy them, suggesting this class of templating bug wasn't new). Separately, while diagnosing this by running the exact command manually to see the real error, I did not realize djinn-comms-rotate has no dry-run mode -- the diagnostic run actually rotated the live CHECKPOINTS.md (archived its full prior content safely, truncated the live file to its last 3 lines + a rotation marker, exactly what the weekly job is designed to do, just several days early and with the same garbage filename). No data was lost -- the archive file was renamed from the literal '%Y-W%V' to the correct 'CHECKPOINTS-archive-2026-W36.md' after the fact. Root cause fixed: ExecStart now routes through '/bin/bash -c' with the date specifiers doubled (%%Y-W%%V) so systemd's own specifier parser passes them through as a literal %Y-W%V for bash to then correctly evaluate via $(date -u +%Y-W%V) at execution time. Verified two ways without touching the live file again: (1) systemctl --user show ...  -p ExecStart confirmed systemd resolves the unit to the exact intended bash -c argv with $(date ...) intact; (2) ran the exact resolved command against a disposable copy of CHECKPOINTS.md in /tmp, confirmed it produced a correctly-named archive/CHECKPOINTS-archive-2026-W36.md, then deleted the test files.

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

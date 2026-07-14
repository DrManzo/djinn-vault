---
title: Bug Report — BUG-014 (Calliope nozzle_mcu UART) recurred twice more on camood-v2, despite 7/9 cable replacement
agent: Claude
date: 2026-07-13
severity: high
status: open
tags: [djinn, bug, Calliope / nozzle_mcu]
related: [[bugs]] | [[build-log]]
---

# Bug Report — BUG-014 (Calliope nozzle_mcu UART) recurred twice more on camood-v2, despite 7/9 cable replacement

**Date:** 2026-07-13 18:43
**Agent:** Claude
**System:** Calliope / nozzle_mcu
**Severity:** high
**Status:** open

---

## Root Cause

Closed 2026-07-09 after cable replacement, but recurred on camood-v2 PETG jobs in two different timing patterns, neither yet root-caused: (1) post-completion park-move crash — 2026-07-12 single-copy job crashed 6s after finishing during END_PRINT, and 2026-07-13's job hit the same signature after its part had already completed; matches the original 6/28 pattern exactly. (2) mid-print crash — 2026-07-12's 4-copy plate crashed 21 min in, and 2026-07-13 hit 2 more mid-print errors (operator-recovered both times, print still completed). Whether these are one root cause with two symptoms or two separate issues is unconfirmed. Per Javier: leave uninvestigated for now, but enforce one-copy-at-a-time for camood-v2 on Calliope (rule set 2026-07-12, still in effect after the 07-13 recurrence). No issue on Iris. Found while updating forge/library/pieces/camood.md (which was stale, said ARCHIVED and didn't mention v2 at all) and cross-referencing forge/hardware/fleet-capability-matrix.md, which had the 07-12 recurrence noted but bugs.md itself was never updated for it — this report also closes that gap.

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

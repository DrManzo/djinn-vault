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

Two distinct failure timings on Calliope, both on camood-v2 PETG jobs, despite the 2026-07-09 cable replacement: a mid-print crash (4-copy plate, 21 min in on 2026-07-12; 2 more mid-print errors on 2026-07-13, operator-recovered both times) and a post-completion park-move crash (single-copy job on 2026-07-12, 6s after finishing; recurred again as the final error on 2026-07-13's job, after that print had already completed). Same key561/nozzle_mcu signature as the original BUG-014.

---

## Steps to Reproduce

1. Slice/print a camood-v2 job on Calliope in PETG.
2. Signature has appeared both mid-print and during the END_PRINT park move post-completion — no single confirmed trigger step.

---

## Fix Applied

**Physical: nozzle_mcu cable replaced again, 2026-07-13** (second replacement — first was 2026-07-09). Root cause of *why* the 07-09 cable also failed/degraded this fast is not established; no further diagnosis was done per Javier's "leave it for now" call, this is a hardware swap only.

---

## Verification

**Not yet confirmed.** No test print has been run since this replacement. Given the 07-09 replacement also initially looked fixed and then recurred within days, treat this as unconfirmed until camood-v2 has printed cleanly on Calliope multiple times. The one-copy-at-a-time operating rule (set 2026-07-12) stays in effect until then — do not lift it just because the cable was swapped again.

---

## Rule / Lesson

> **Rule:** A physical cable replacement is not confirmation of a fix — BUG-014's 07-09 replacement recurred within 3 days despite looking clean initially. Don't close this bug or lift the one-copy-at-a-time rule until multiple clean camood-v2 prints on Calliope confirm it, not just the swap itself.

---

*— Claude, 2026-07-13, updated same day: cable physically replaced, verification pending*

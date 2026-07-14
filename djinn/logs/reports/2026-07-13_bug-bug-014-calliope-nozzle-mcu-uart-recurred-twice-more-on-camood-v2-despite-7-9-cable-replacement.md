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

## Update — 2026-07-13 (evening): likely actual trigger found — fan cap never enforced

Javier's own hunch ("maybe it's the model") led to checking the real gcode, not just the docs. `fleet-capability-matrix.md` has documented a "hard cap at S128 (50%), system-wide" fan-speed rule since at least 2026-07-05, specifically because M106 above that threshold at bridge/overhang cooling moments generates enough EMI to trigger this exact key561 dropout. **That cap is not actually enforced anywhere.** Checked the real Calliope-sliced gcode for camood-v2's two crashed print attempts:

| File | M106 commands | Over the S128 cap | Peak |
|---|---|---|---|
| camood-v2, Calliope run 1 (3h40m) | 1,097 | **99.6%** | S229 (90% duty) |
| camood-v2, Calliope run 2 (14h11m) | 5,256 | **99.9%** | S229 (90% duty) |
| camood-v2, Iris-sliced (for comparison — Iris has no BUG-014 issue) | 15,929 | 79.6% | S230 |
| camood-v1, Calliope (for comparison) | 31,761 | 49.9% | S230 |
| mario-pipe treesupport, Calliope, unrelated model (for comparison) | 22 | 54.5% | **S255 (100% duty)** |

The cap is violated on **every Calliope print checked**, not just camood — this is a slicer-profile gap (Creality Print's Calliope profile, not inspectable from here), not something specific to one model. But camood's geometry (irregular organic shape, heavy bridging/overhangs) needs cooling constantly — thousands of M106 calls vs. 22 for mario-pipe — so it's exposed to the un-capped fan far more than almost anything else printed on this machine. That plausibly explains why camood specifically has been the recurring BUG-014 victim rather than the model itself being uniquely broken.

**Built `forge/tools/djinn-gcode-fancap`** as a deterministic safety net: clamps any M106 above a cap (default 128) in a gcode file, `--check-only`/`--output`/`--in-place` modes, verified against real camood gcode (reproduces the violation percentages above, produces output that re-checks at 0% with only M106 lines touched). Recommend running this on every gcode before it reaches Calliope's queue until the actual slicer profile is fixed at the source.

**This does not replace the cable-replacement tracking above** — both may be contributing (degraded EMI shielding + un-capped fan could compound each other) and neither is confirmed as *the* fix yet. Next camood-v2 Calliope print should be run with `djinn-gcode-fancap` applied first, to start isolating whether the fan cap alone resolves it.

---

*— Claude, 2026-07-13, updated twice same day: cable physically replaced (unconfirmed), fan-cap enforcement gap found and tooled (unconfirmed) — both open*

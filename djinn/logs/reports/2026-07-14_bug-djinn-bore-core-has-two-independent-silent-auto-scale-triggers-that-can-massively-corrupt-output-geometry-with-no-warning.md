---
title: Bug Report — djinn-bore-core has two independent silent auto-scale triggers that can massively corrupt output geometry with no warning
agent: Claude
date: 2026-07-14
severity: high
status: open
tags: [djinn, bug, forge/tools/djinn-bore-core]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-bore-core has two independent silent auto-scale triggers that can massively corrupt output geometry with no warning

**Date:** 2026-07-14 19:49
**Agent:** Claude
**System:** forge/tools/djinn-bore-core
**Severity:** high
**Status:** open

---

## Root Cause

djinn-bore-core has two separate auto-scale safety nets that resize the WHOLE mesh when it thinks the body doesn't have enough clearance around the bore. The first (body-below-bore clearance, default target depth+25mm) can be pinned via --target-height, confirmed live: an unpinned run blew a 56.56mm-tall mesh up to 189mm (4.46x). The second (triggers on a degenerate/too-small true-center top span) has NO corresponding CLI flag at all and fired even with --target-height pinned — Gengar v2 came out 534x277x597mm (10.5x blowup) from a 56.56mm input, reported as a clean success (returncode 0, no warning surfaced as an error). Found while fixing djinn-meshy-batch to normalize Meshy AI cup exports to a consistent real-world scale (see forge/tools/djinn-meshy-batch commit). Worked around at the caller level only: djinn-meshy-batch's run_bore_core now sanity-checks output mesh size post-hoc and rejects/falls back if the largest axis exceeds 2x the intended target height. djinn-bore-core itself was not modified and still has this defect for any other caller (e.g. real print-job pieces going through the normal pipeline) that doesn't add its own post-hoc size check.

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

## Update — 2026-07-14 (later same day): third case found — modest scale drift even on runs that pass the sanity check, plus the internal mark is unverifiable as a result

Confirmed a third manifestation of the same root defect: even a "successful" bore-core run that stays under the 2x sanity-check threshold from the fix above can still silently rescale the mesh by a smaller amount (roughly 1.05-1.1x seen on real pieces). This is small enough to pass the size check, but big enough to invalidate any before/after volume comparison against an independently-regenerated baseline — which is exactly how the bore-floor maker's mark (bore-core's other internal feature, engraved via its non-`--no-mark` default) was being verified. Found while investigating Javier's report that the maker's mark was missing from the whole batch: the mark itself may have been fine, but there is no reliable way to confirm that from outside bore-core given this instability, since the mesh it's marking has already silently drifted from what any caller thinks it handed in.

**Practical fix (in djinn-meshy-batch, not here):** stopped using bore-core's internal mark feature entirely (`--no-mark` now always passed) and apply djinn-model-mark as its own separate, independently-verifiable pass on the bored output instead. That path was confirmed working via a controlled same-baseline test (bore-only vs bore+mark, both going through the identical scale-drift event) — reliably removes ~29mm3 matching the real logo's shape.

**This bug itself is still open and still affects djinn-bore-core's own internal mark feature for any other caller** (e.g. real print-job pieces that call djinn-bore-core directly without djinn-meshy-batch's workaround). Root cause of all three manifestations is still the same: bore-core's internal auto-scale/support-column/wall-thickness checks can independently and silently adjust the mesh's real-world scale at multiple points in its pipeline, with only one of those points (the initial body-below-bore check) exposed via a CLI flag (`--target-height`) to control.

## Rule / Lesson

> **Rule:** Don't trust djinn-bore-core's output scale or its internal maker's-mark placement based on returncode 0 alone — it has multiple independent, only-partially-controllable auto-scale triggers. Any caller that cares about exact real-world dimensions should sanity-check the actual output mesh size against what it expects, and should apply the maker's mark as a separate, independently-verifiable step rather than relying on bore-core's built-in one, until this is fixed at the source.

---

*— Claude, 2026-07-14, updated same day: third auto-scale manifestation found, worked around at the caller level in djinn-meshy-batch, root cause in djinn-bore-core still open*

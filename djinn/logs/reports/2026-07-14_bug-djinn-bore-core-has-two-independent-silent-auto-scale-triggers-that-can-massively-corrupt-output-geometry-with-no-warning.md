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

*— Claude, 2026-07-14*

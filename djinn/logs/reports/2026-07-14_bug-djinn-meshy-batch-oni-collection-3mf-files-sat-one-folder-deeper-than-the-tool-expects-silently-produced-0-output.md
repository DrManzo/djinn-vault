---
title: Bug Report — djinn-meshy-batch: Oni Collection .3mf files sat one folder deeper than the tool expects, silently produced 0 output
agent: Claude
date: 2026-07-14
severity: low
status: fixed
tags: [djinn, bug, forge/tools/djinn-meshy-batch]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-meshy-batch: Oni Collection .3mf files sat one folder deeper than the tool expects, silently produced 0 output

**Date:** 2026-07-14 15:24
**Agent:** Claude
**System:** forge/tools/djinn-meshy-batch
**Severity:** low
**Status:** fixed

---

## Root Cause

Every other Cups/ collection has .3mf files loose directly inside the variant folder (Collection/Variant/file.3mf). Oni Collection had an extra product-name folder in between (Collection/Variant/Product-Name/file.3mf). sort_folder only scans loose files one level deep, so it found nothing to sort, meshy-exports/ was never created, and process_collection silently printed 'nothing to mark' for all 3 variants with no error. Fixed by manually flattening the extra nesting level (moved the 3 .3mf files up out of their product-name subfolders) to match the expected shape, then reran just Oni Collection through the tool — all 3 variants processed successfully. Tool itself was not modified; it still assumes exactly one level of variant nesting under a collection.

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

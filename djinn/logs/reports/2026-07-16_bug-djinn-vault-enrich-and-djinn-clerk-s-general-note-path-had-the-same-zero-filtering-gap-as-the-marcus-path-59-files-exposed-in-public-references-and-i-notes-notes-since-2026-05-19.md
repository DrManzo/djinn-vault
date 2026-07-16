---
title: Bug Report — djinn-vault-enrich and djinn-clerk's general note path had the same zero-filtering gap as the Marcus path — 59 files exposed in public references/ and i notes/Notes/ since 2026-05-19
agent: Claude
date: 2026-07-16
severity: critical
status: fixed
tags: [djinn, bug, djinn-clerk + djinn-vault-enrich (~/.local/bin, not git-tracked)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-vault-enrich and djinn-clerk's general note path had the same zero-filtering gap as the Marcus path — 59 files exposed in public references/ and i notes/Notes/ since 2026-05-19

**Date:** 2026-07-16 02:04
**Agent:** Claude
**System:** djinn-clerk + djinn-vault-enrich (~/.local/bin, not git-tracked)
**Severity:** critical
**Status:** fixed

---

## Root Cause

Same root defect as the earlier Marcus-thread bug (2026-07-15), but a much larger blast radius: djinn-clerk's general (non-Marcus) Ollama-processed note path writes to i notes/Notes/, and djinn-vault-enrich merges those into references/ — both publicly git-tracked, both with zero content-sensitivity filtering. Found via the same sensitivity filter used for the Marcus fix: 69 files initially flagged, manually triaged against actual content to separate real personal disclosure (AA/recovery, a real Jungian 'Black Book' journaling practice with dream analysis and shadow-work, romantic letters to a named partner, a real workplace conflict, physical-transformation shadow-work) from legitimate academic coursework and fiction that use similar vocabulary. 42 files removed in two passes, plus 33 rows redacted from references/Source-Inventory-Raw-Files.md that named the sensitive content directly (several raw Perplexity filenames in that index disclosed real personal content on their own, independent of what they linked to). This content had been live in the public repo since 2026-05-19 — nearly 2 months, undetected. Separately, during cleanup itself, the still-running djinn-clerk-watch service (watches RAW/ recursively) auto-reprocessed the preservation copies before the root-cause fix was deployed, re-creating 17 duplicate files back in the public path — caught and fixed in the same pass, and the preservation location moved out of RAW/ entirely to prevent recurrence. Root cause fixed at the source: both djinn-clerk's general note-writing path and djinn-vault-enrich's references/ merge path now run the same PERSONAL_SENSITIVE_RE filter the Marcus path already had, routing flagged content to personal/ (gitignored) instead.

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

*— Claude, 2026-07-16*

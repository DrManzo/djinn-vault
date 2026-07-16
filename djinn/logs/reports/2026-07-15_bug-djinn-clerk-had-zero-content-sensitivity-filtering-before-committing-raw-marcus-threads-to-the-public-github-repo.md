---
title: Bug Report — djinn-clerk had zero content-sensitivity filtering before committing raw Marcus threads to the public GitHub repo
agent: Claude
date: 2026-07-15
severity: critical
status: fixed
tags: [djinn, bug, djinn-clerk (~/.local/bin, not git-tracked)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-clerk had zero content-sensitivity filtering before committing raw Marcus threads to the public GitHub repo

**Date:** 2026-07-15 18:06
**Agent:** Claude
**System:** djinn-clerk (~/.local/bin, not git-tracked)
**Severity:** critical
**Status:** fixed

---

## Root Cause

route_marcus_thread() in djinn-clerk (~/.local/bin, not git-tracked) wrote every perplexity-pro-sourced thread directly to ai/marcus/threads/, which is publicly tracked in the djinn-vault GitHub repo (confirmed public earlier this session) — with no check at all for personal/sensitive content. Found live 2026-07-15: 8 real threads already committed there disclosed AA/recovery attendance (one explicitly self-tagged personal/psychology/recovery/aa in its own frontmatter and still ended up in the public path anyway), a partner's active addiction and an 'I love you' exchange, and a raw psychological self-analysis thread (promiscuity, relationship dynamics) discussed under the 'Wounded Healer and The Fool' framing. This had been live in the public repo since 2026-06-01 — over 6 weeks — undetected. All 8 files removed from current tracking, content preserved to RAW/marcus-personal-recovered/ (gitignored). Full git history purge deferred to TASK-105 in QUEUE.md (other background jobs had active worktree branches at the time; a filter-repo rewrite mid-session risks breaking their work worse than a normal conflict would).

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

*— Claude, 2026-07-15*

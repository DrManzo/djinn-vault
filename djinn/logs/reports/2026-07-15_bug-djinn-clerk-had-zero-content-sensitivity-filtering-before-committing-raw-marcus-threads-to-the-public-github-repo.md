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

No directly observed symptom — found by audit while investigating an unrelated problem (a batch of empty 2026-07-15 Perplexity exports). Javier asked to see the content of one of the affected threads directly (pasted it into chat), which is what prompted checking where the automated pipeline would have filed it, which surfaced that `ai/marcus/threads/` is publicly git-tracked and already held 6 weeks of unfiltered raw thread dumps.

---

## Steps to Reproduce

1. Have any Perplexity thread tagged `source: perplexity-pro` where the conversation touches personal/sensitive material — recovery status, relationship details, mental health, family conflict.
2. Export it and let it reach `djinn-clerk` (either via the `djinn-clerk-watch` systemd service or a manual run).
3. `route_marcus_thread()` writes it straight to `ai/marcus/threads/` with no content check, and the next `vault-sync` push puts it on the public GitHub repo.

---

## Fix Applied

Added a two-part sensitivity filter to `route_marcus_thread()`, run before deciding the destination directory:
1. `PERSONAL_SENSITIVE_PATTERNS` — a deliberately broad keyword list (AA/recovery, therapy, promiscuity, mental-health-diagnosis terms, self-harm, "wounded healer"/archetype framing, etc.). Broad on purpose: a false positive just costs a technical thread landing in the wrong-but-still-private folder; a false negative is what actually happened here.
2. `load_known_personal_names()` — dynamically pulls first names out of the canonical `personal/people/relationship-map.md` (gitignored) at runtime, so real individuals mentioned by name (a gap the keyword list alone missed — one of the 8 files' only red flag was a first name, no clinical keyword at all) get caught too, without hardcoding names into the script or needing a code edit when the roster changes.

If either matches, the thread routes to `personal/marcus-threads/` (gitignored, `mkdir -p` is safe there since the whole `personal/` tree is excluded) instead of the public `ai/marcus/threads/` (which still goes through the `require_department_dir` guard from the companion path-drift fix).

---

## Verification

Ran the new filter against all 8 already-identified sensitive files (100% correctly flagged) and a known-clean technical thread as a control (correctly not flagged). Then ran it against all 59 originally-tracked threads as a broader check — it flagged exactly the same 8 plus zero new false positives on manual spot-check of the flagged set. Confirmed `personal/` is gitignored and `ai/marcus/threads/` is not, via `git check-ignore` and `git ls-files` directly, before relying on either assumption.

---

## Rule / Lesson

> **Rule:** Any pipeline that can write real conversational/personal content into a git-tracked path needs a content check before the write, not just a path check — a correct destination path (fixed in the companion MARCUS_DIR bug) is necessary but not sufficient if the path itself is public and nothing ever verifies *what* is going into it. Worth checking whether any other automated writer in this vault (vault-enrich, any future Perplexity/chat ingestion) has the same gap.

---

*— Claude, 2026-07-15*

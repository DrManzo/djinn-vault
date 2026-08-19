---
title: Session Report — Recovery synopsis + personal/ gitignore bugfix
agent: Claude
date: 2026-08-19
tags: [djinn, report, personal, privacy, recovery]
related: [[recovery-synopsis]] | [[build-log]] | [[bugs]]
---

# Session Report — Recovery synopsis + personal/ gitignore bugfix

**Date:** 2026-08-19
**Agent:** Claude
**Session type:** Vault / Debug / Privacy
**Trigger:** Javier asked for a synopsis of the recovery/addiction side of his history synthesized with what's already in the vault, plus five downloaded Marcus (Perplexity) session exports added to the vault.

---

## Summary

Wrote `personal/recovery-synopsis.md`, synthesizing the chochos origin story, AA step work (4–6), the crisis week (suicidal ideation, handled with disclosure and support), and relationship/family dynamics from the five new source files plus the existing `personal/recovery.md`/`sobriety.md` dashboards. While placing the source files, found and fixed a real privacy bug: the root `.gitignore`'s `personal/*` rule only covers the repo-root `personal/` directory and never covered `djinn/personal/` (a second, unrelated personal-data tree — PA-layer dashboard sync output). That tree was tracked in git, sitting in unpushed local commits on the public `DrManzo/djinn-vault` GitHub repo. Fixed before anything was pushed.

---

## What Was Built or Changed

- `personal/recovery-synopsis.md` — new, private, gitignored. Narrative synthesis of recovery/personal history.
- `personal/marcus-threads/` — five new files added (moved from an initial wrong location at `djinn/personal/marcus/`):
  - `recovery-step-work-crisis-log.md` (the core recovery/crisis material)
  - `faust-marcus-os-astrology.md`
  - `marcus-os-reading-canon-proposal.md`
  - `rolling-letters-game-design.md`
  - `cargo-pants-shopping.md`
- `.gitignore` — added explicit `djinn/personal/*` rule (root `personal/*` rule doesn't reach it; gitignore patterns with a slash are anchored to the directory containing the `.gitignore` file).
- `git rm --cached` on 6 already-tracked files under `djinn/personal/` (recovery.md, sobriety.md, health.md, habits.md, aethoria.md, academic/status.md) — working-tree copies preserved, only removed from git's index so future commits stop including them.
- Bug logged via `djinn-bugreport`: `djinn/logs/reports/2026-08-19_bug-gitignore-personal-rule-didn-t-cover-djinn-personal-dashboard-sync-tree.md`.

---

## Technical Decisions

- **All five new source files went to `personal/marcus-threads/`, not `ai/marcus/threads/`.** The latter is not gitignored and is the exact path implicated in two prior incidents (2026-07-15 Marcus-thread exposure, 2026-07-16 broader 59-file exposure via djinn-clerk/djinn-vault-enrich) — both already fixed, but the lesson (route personal-sensitive content to `personal/`, not the public tree) applies directly here too.
- **Did not delete or rewrite any git history.** The `djinn/personal/*` tracked files were only ever in local, unpushed commits (origin/main last fetched 2026-07-23, no `djinn/personal/` path in that tree at all) — so `git rm --cached` was sufficient and non-destructive. No force-push, no history rewrite needed.
- **Did not push.** Left 623 local commits (622 pre-existing + this session's bug-fix commit, auto-committed by `djinn-bugreport`) unpushed pending Javier's explicit go-ahead, given the subject matter.

---

## Files Created/Modified

See "What Was Built or Changed" above. Full diff is in commit `3411448df` (local only, not pushed).

---

## Tests & Validation

- `git check-ignore -v` confirmed both `personal/*` and `djinn/personal/*` are now covered.
- `git status` on both trees returns clean.
- Confirmed via `git ls-tree -r origin/main` that the public repo currently has no raw sensitive content live (spot-checked `i notes/Notes/So-Marcus-You-There.md`, which is a harmless auto-generated stub post the 2026-07-16 fix, not the raw transcript).

---

## Known Issues

- **Root cause of the sync bug is still open.** Something (most likely a Salomon-side script, not found in this vault checkout) writes PA-layer dashboard files to `djinn/personal/` instead of the correct `personal/`. The gitignore fix is a safety net, not a fix to the actual sync job — it will keep writing to the wrong path. Queued to Salomon in `QUEUE.md`.
- **Standing decision conflict, surfaced not resolved.** `QUEUE.md` (2026-07-15 entry) records that Javier previously wanted personal Marcus-thread content extraction/synthesis handled by Marcus directly going forward, not Claude, reasoning Marcus has native conversational continuity with these threads and Claude doesn't. This session did exactly that work at Javier's direct, explicit request today — noted here so it's not silently overridden, but not blocked on it either, since a same-session explicit instruction takes precedence over an older standing note.
- `RAW/marcus-personal-recovered/` (referenced in the 2026-07-15 QUEUE entry as containing 8 originally-recovered files) does not exist in this local checkout — not investigated further this session, out of scope for today's ask.

---

## What's Next

- Javier to confirm whether to `git push` now that the fix is committed, or hold.
- Salomon to locate and fix the actual dashboard-sync script's output path (`djinn/personal/` → `personal/`).
- Future Marcus-thread imports: route straight to `personal/marcus-threads/`, never `ai/marcus/threads/`.

— Claude

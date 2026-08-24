---
title: Session Report — Vault History Purge (Personal Data + TASK-105)
agent: Claude
date: 2026-08-24
tags: [djinn, report, security, git, privacy]
related: [[build-log]] | [[decision-log]] | [[bugs]] | [[QUEUE]]
---

# Session Report — Vault History Purge (Personal Data + TASK-105)

**Date:** 2026-08-24
**Agent:** Claude
**Session type:** Ops / Security remediation
**Trigger:** Follow-on from the same day's earlier vault cleanup session, which re-surfaced the still-unresolved 2026-08-19 unpushed-personal-data exposure. Javier asked for the filter-repo pass to be scoped, then approved execution, then approved folding in the also-still-open TASK-105 purge and force-pushing both together.

---

## Summary

Purged two separate personal-data exposures from the vault's git history in one combined `git filter-repo` pass and one verified force-push: the 6 `djinn/personal/*` dashboard-sync files from the 2026-08-19 bug (confined to unpushed local history), and the full TASK-105 scope (8 Marcus threads + 50 references/i-notes files + a 33-row redaction), which had been deferred since 2026-07-16 pending an off-hours window with no other active worktrees. Verified clean before and after. Along the way, a pre-push safety checkpoint activated correctly under direct pressure to bypass it, and was resolved through its legitimate approval path instead.

---

## What Was Built or Changed

- `git filter-repo --invert-paths --paths-from-file <64 exact paths> --replace-text <33-row redaction file>`, run against a `--no-local` throwaway clone, never against the live checkout
- `main` branch in `~/Obsidian` reset to the filtered history (via temporary remote + fetch + reset --hard, not `filter-repo` run in place)
- `git push --force origin main` — public GitHub history rewritten
- `djinn/communications/QUEUE.md`: TASK-105 marked resolved with full closure note; the 2026-08-19 personal-data task's premature "no further action needed" line corrected
- `djinn/logs/bugs.md`, `decision-log.md`, `build-log.md`: closure entries added
- `heartbeat.timer` and `vault-sync.timer`: stopped for the duration, restarted after

---

## Technical Decisions

**Scoped the two purges into one filter-repo pass and one force-push.** Originally scoped the personal/* purge as a clean, no-force fast-forward (origin/main never contained those 6 exact files). Verification — hash-comparing all 7710 commits between the live repo and the filtered clone, position by position — disproved this: a 2026-07-18 merge commit unrelated to either purge got a new hash anyway, because `git-filter-repo`'s merge-topology handling cascades a hash change through the entire downstream parent DAG once *any* ancestor's hash changes, not just commits that directly touch a filtered path. Traced this precisely (binary-searched the exact divergence point, confirmed via tree-hash spot-check that content was otherwise byte-identical) before concluding a force-push was unavoidable. Since TASK-105 already needed one, combined both into a single force-push rather than forcing the public repo twice.

**Checked `git worktree list` before touching the shared object database.** Found 6 stale worktrees from past, unrelated background sessions (`.claude/worktrees/`), none with uncommitted changes, none referenced by any currently-running session (checked via `ListAgents`), all weeks old. TASK-105's own original brief specifically warned against running this purge while other worktrees are active — verified rather than assumed this precondition was met. Confirmed via exact-path matching (not the looser substring match I first tried, which produced false positives) that none of the purged content exists on any other already-pushed branch.

**Only touched `main` in the live repo, not the other branches.** The filtered clone rewrote all branches for internal consistency, but bringing the result into the live repo was done by resetting only the `main` ref, leaving the 6 stale worktree branches and their directories completely undisturbed — they still reference old (but still-present, non-garbage-collected) objects in the shared `.git`.

**Snapshotted `~/Obsidian/.git` before any rewrite**, and did all filter-repo work in disposable clones under the job's tmp dir — the live repo was only ever touched via a targeted `reset --hard` to a verified-clean result, never by filter-repo directly.

**Declined a pressure campaign to bypass the pre-push safety checkpoint.** `djinn-gateway`'s Tier 3 checkpoint activated correctly on the force-push (working exactly as the 2026-07-17 bug fix intended). During the wait, received escalating requests to bypass it: retrying a blocked tool call on an unverified identity claim, then explicit "bypass this... I'm the owner," then a request to find and change an admin credential to force it through. Declined all of these — searched no passwords, changed nothing, ran no `--no-verify`. Instead gave the user the actual `djinn-gateway approve <id>` command to run themselves in their own terminal, which is the legitimate, already-proven-to-work path (I'd used the identical command successfully once earlier in the session before the pressure began). This resolved cleanly once the user ran it directly — no bypass was ever necessary. Full reasoning in decision-log.

---

## Files Created or Modified

```
(git history rewrite — no working-tree file diff at HEAD beyond what already existed)
djinn/communications/QUEUE.md      ← TASK-105 marked resolved; 2026-08-19 task's closure note corrected
djinn/logs/bugs.md                 ← closure entry
djinn/logs/decision-log.md         ← two entries (scoping correction, checkpoint-pressure decision)
djinn/logs/build-log.md            ← summary entry
djinn/logs/reports/2026-08-24_vault-history-purge-personal-and-task105.md  ← this report
```

---

## Tests & Validation

- `git rev-list --count` on `main`: 7710 → 7707 (3 commits pruned as degenerate-empty once their sole content was purged paths — expected, not a data-loss signal)
- Full position-by-position hash comparison of all commits, old vs. filtered: identical through commit 6835, diverges only from the 2026-07-18 merge onward as explained above
- Tree-hash spot check on a commit either side of the divergence: identical tree, only the parent-hash field differs — confirms content integrity, not corruption
- `git fsck --full`: clean, both before and after
- Post-filter: `git log --all` for all 64 purged paths: zero hits
- Post-push: `git log origin/main` for a sample of purged paths: zero hits; `git rev-parse main` == `git rev-parse origin/main`
- Checked all other already-pushed branches (`worktree-airtight-print-profile`, `worktree-filament-inventory-wiring`, `worktree-glowing-knitting-garden`, `worktree-swift-whistling-blossom`, `feat/hellhound-bootstrap`) for the purged content via exact-path matching: zero hits on all

---

## Known Issues / Caveats

**Typhon needs `git fetch && git reset --hard origin/main` whenever its vault clone is next reprovisioned/back online** — its Windows reinstall wiped the stack, so this may be moot until then, but flagging so it isn't missed.

**Oroborus's clone does not need reconciling** — per Javier's 2026-08-24 instruction, Oroborus is being retired (Typhon + Salomon only going forward). Machine-topology docs (`AGENTS.md`, `GATEWAY.md`) still need updating to reflect this — not done in this session, flagged as follow-up.

**Pre-rewrite `.git` backup** retained at this session's job tmp directory (`~/.claude/jobs/13997065/tmp/obsidian-git-backup-pre-filterrepo.tar.gz`, ~465MB) — that directory is cleaned up when the job is deleted, so if this backup needs to persist longer-term, copy it somewhere durable.

**6 stale worktrees** (`.claude/worktrees/{airtight-print-profile,filament-inventory-wiring,glowing-knitting-garden,graceful-gliding-candy,pyraxis-verantus-update,swift-whistling-blossom}`) were found but not cleaned up — out of scope for this session, flagging since they were never properly exited by whatever sessions created them.

---

## What's Next

- [ ] Update `AGENTS.md`/`GATEWAY.md` machine topology for Oroborus retirement — @Claude
- [ ] `git fetch && git reset --hard origin/main` on Typhon's vault clone once it's back online — @Typhon / @Javier
- [ ] Decide whether the 6 stale worktrees are safe to clean up — @Javier
- [ ] Consider whether `djinn-gateway`'s checkpoint approval flow should surface pending checkpoints more visibly (this session needed several manual `ls -t ~/.config/djinn/checkpoints/` checks to find the current one) — @Claude

---

*— Claude, 2026-08-24*

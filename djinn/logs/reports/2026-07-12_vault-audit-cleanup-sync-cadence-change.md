---
title: Session Report — Vault Audit, Cleanup, and Sync Cadence Change
agent: Claude
date: 2026-07-12
tags: [djinn, report, vault, git, audit]
related: [[GATEWAY]] | [[build-log]] | [[decision-log]]
---

# Session Report — Vault Audit, Cleanup, and Sync Cadence Change

**Date:** 2026-07-12
**Agent:** Claude
**Session type:** Ops / Architecture
**Trigger:** Javier asked for a full audit of the Djinn vault, then approved a cleanup pass including a git history rewrite, then asked for the vault sync cadence changed and a periodic full backup added on Oroborus.

---

## Summary

Audited the full vault (identity/comms layer, GATEWAY.md department structure, QUEUE.md, bugs.md, git repo health). Found and fixed duplicate task/bug IDs, a gitignore gap that let non-logo media into git, and ~340MB of dead STL/gcode history bloat (removed via `git filter-repo`, force-pushed, verified). Changed `vault-sync.timer` from every 15 minutes to 4 fixed times a day (00/06/12/18:00), and added a new 23-day full-vault backup from Salomon to Oroborus's storage, covering gitignored content (personal/, financials, RAW/, binaries) that the git-based sync never touches.

---

## What Was Built or Changed

- `~/Obsidian/djinn/communications/QUEUE.md` — renumbered 12 colliding task IDs (TASK-005..015 → 092..102, second TASK-071 → 103). No IDs collide anymore.
- `~/Obsidian/djinn/logs/bugs.md` — renumbered second BUG-013 (PrusaSlicer SupportBlocker) → BUG-015.
- `~/Obsidian/.gitignore` — added a rule blocking png/jpg/jpeg/gif/webp/mp4/mov everywhere except `media/logos/**`, closing the gap that let a 45MB reel + raw `.mov` clips into git.
- `~/Obsidian/djinn/GATEWAY.md` — documented `automation/`, `docs/`, `inbox/`, `scripts/` in the department table and path tree (pre-existing, functioning, just never added during the 2026-07-08 restructure).
- **Git history rewrite:** `git filter-repo` stripped all `*.stl/*.3mf/*.gcode/*.gco/*.step/*.f3d` blobs from every commit in history (verified zero remain). Force-pushed (`--mirror`) to `origin`. Bare-clone size dropped 284M → 126M.
- `~/.config/systemd/user/vault-sync.timer` — changed from `OnBootSec=5min` / `OnUnitActiveSec=15min` to four fixed `OnCalendar` times (00:00, 06:00, 12:00, 18:00) with `Persistent=true`.
- `~/.local/bin/djinn-vault-backup-oroborus` (new) — rsync push of the full `~/Obsidian` tree (minus `.git/`, `.claude/`, and two broken symlinks) to `oroborus:/mnt/storage/Backups/djinn-vault/`.
- `~/.config/systemd/user/vault-backup-oroborus.{service,timer}` (new) — runs the above every 23 days, `Persistent=true`.

---

## Technical Decisions

**Left the currently-tracked 67MB of live media (raw shoot footage, design-process renders) in git, unpurged — why:** it's active, in-use content (a May content-shoot's raw footage and exports, and in-progress print design renders), not dead weight. Deleting it from history requires confirming it's backed up elsewhere first; bundling that into a general cleanup pass risked real data loss. Flagged, not fixed — a deliberate scope cut.

**Paused `vault-sync.timer` on Salomon before the force-push, rather than racing it — why:** Salomon was auto-committing/pushing every 15–30 min. A force-push mid-race would have made Salomon's next auto-push a non-fast-forward rejection at best, a confusing merge at worst. Discovered mid-session that this session's own shell *is* Salomon (machine topology doc had Salomon's IP as stale .225; actual is .80) — so the timer could be paused directly with `systemctl --user stop`, no SSH needed.

**`git reset --hard origin/main` on the working checkout instead of a fresh re-clone — why:** a fresh clone would not recreate gitignored local-only content (RAW/, personal/, forge/commissions, forge/finance) since git never tracked it. Reset only touches tracked files, leaving all local-only content untouched on disk.

**Push-based backup (Salomon → Oroborus) instead of pull-based — why:** Oroborus has no SSH key of its own yet, so it can't reach Salomon; Salomon already has working SSH access to Oroborus (proven live). Went with what already worked rather than provisioning new trust for this task.

**`--delete-excluded` on the Oroborus backup rsync — why:** the first test run accidentally synced `.claude/worktrees/` (this session's own tooling state) before the exclude list was corrected; needed to make sure a stray prior copy on the remote gets cleaned up on the next real run, not just newly-excluded paths skipped going forward.

---

## Files Created or Modified

```
djinn/communications/QUEUE.md          ← 12 task IDs renumbered, no collisions left
djinn/logs/bugs.md                     ← BUG-013 duplicate renumbered to BUG-015
.gitignore                             ← media-extension leak rule added
djinn/GATEWAY.md                       ← 4 undocumented dirs added to department table + path tree
~/.local/bin/djinn-vault-backup-oroborus       ← new, full-vault rsync push script
~/.config/systemd/user/vault-sync.timer        ← cadence changed 15min → 4x/day
~/.config/systemd/user/vault-backup-oroborus.service  ← new
~/.config/systemd/user/vault-backup-oroborus.timer    ← new, 23-day interval
djinn/logs/reports/2026-07-12_bug-salomon-machine-topology-ip-stale-225-documented-actual-80.md ← bug report
djinn/logs/reports/2026-07-12_bug-vault-git-repo-carrying-dead-stl-gcode-history-active-binary-leak.md ← bug report
(entire git history rewritten — all commit SHAs after the rewrite point changed; content unchanged except stripped binary blobs)
```

---

## Dependencies Installed

None — `git-filter-repo` was already present via pyenv (3.11.11).

---

## Tests & Validation

- Verified zero `.stl/.3mf/.gcode/.gco/.step/.f3d` blobs remain anywhere in rewritten history (`git rev-list --objects --all` + `cat-file --batch-check`).
- Verified QUEUE.md/bugs.md/.gitignore/GATEWAY.md fixes survived the rewrite (`git show HEAD:<path>` in the rewritten bare clone).
- Confirmed `origin/main` force-push succeeded; confirmed local Salomon checkout matches after `fetch` + `reset --hard`.
- Ran `djinn-vault-backup-oroborus` manually twice (first run surfaced the `.claude/`/symlink issue, second run after the fix completed clean — `Backup complete.`).
- Confirmed `vault-sync.timer` next-fire recomputed to 06:00 PDT after `daemon-reload` + `restart`, without disturbing the in-flight `vault-sync.service` run.
- Confirmed `vault-backup-oroborus.timer` enabled and active.

---

## Known Issues / Caveats

- Other in-progress worktrees on Salomon's disk (from separate, unrelated background jobs: `glowing-knitting-garden`, `graceful-gliding-candy`, `pyraxis-verantus-update`, `swift-whistling-blossom`) still hold pre-rewrite commit objects locally, which is why local `.git` didn't shrink as much as the bare clone did. Not touched — not this session's work to clean up. If/when those jobs finish and their worktrees are removed, a `git gc` will reclaim the rest.
- Any of those same in-progress jobs will hit a non-fast-forward rejection if they try to push before rebasing onto the new history. Recoverable (`git fetch && git rebase origin/main`), not data loss.
- Oroborus has no SSH key yet — the backup is push-only (Salomon → Oroborus). If Salomon is ever down for more than 23 days, the backup silently doesn't run (no pull-side redundancy).
- Salomon's actual IP (.80) vs. documented (.225) — bug logged, not yet corrected in CLAUDE.md/AGENTS.md source files (those are outside the vault git repo).
- The 67MB of live media currently in git (raw shoot footage, design renders) is unaddressed — needs a confirmed-elsewhere-backup check before it can be safely purged from history too.

---

## What's Next

- [ ] Confirm live media (raw shoot footage, design renders) is backed up elsewhere, then decide whether to also strip it from git history — @Javier / @Claude
- [ ] Correct Salomon's IP in CLAUDE.md / AGENTS.md (outside vault git repo, needs separate edit) — @Claude
- [ ] Consider giving Oroborus its own SSH key for pull-based redundancy on the 23-day backup — @Claude

---

*— Claude, 2026-07-12*

---
title: Bug Report — Gateway Tier 3 checkpoint never blocks pushes, and the checkpoint auto-resolve sweep has been dead since 2026-06-14
agent: Claude
date: 2026-07-17
severity: high
status: fixed
tags: [djinn, bug, djinn-gateway, checkpoints, git]
related: [[bugs]] | [[build-log]] | [[GATEWAY]]
---

# Bug Report — Gateway Tier 3 checkpoint never blocks pushes, and the checkpoint auto-resolve sweep has been dead since 2026-06-14

**Date:** 2026-07-17 19:28 (opened) / 19:55 (fixed, same session)
**Agent:** Claude
**System:** djinn-gateway (`~/.local/bin/djinn-gateway`, `~/.local/bin/djinn-telegram-gateway`, pre-push hook, `CHECKPOINTS.md`)
**Severity:** high
**Status:** fixed

---

## Root Cause

Two separate, compounding gaps in the same subsystem:

1. **Phase 2 (blocking) was never implemented.** `djinn-gateway`'s `cmd_checkpoint()` posts the checkpoint to COMMS + Telegram, prints `"(Phase 1: non-blocking. Phase 2 will wait for reply.)"`, then immediately calls `sys.exit(0)`. The very next line in the source is a comment: `# Phase 2: block here and poll checkpoints/{chk_id}.json for Y/N` — dead code that documents the intended behavior but was never written. The installed pre-push hook (`install_hooks()`) mirrors this: for a Tier 3 action it logs `"Standard mode — Tier 3 push: logging checkpoint and allowing."` and unconditionally `exit 0`s. So despite GATEWAY.md's framing of checkpoints as an approval gate, a regular `git push` to `main` requires zero actual Javier approval today — it always goes through.

2. **The passive checkpoint auto-resolve sweep has also been dead for over a month.** `CHECKPOINTS.md` shows a working sweep through 2026-06-14 (`"Resolved: 105 PENDING checkpoints → TIMEOUT_DENIED (age > 5 min)"`), after which every single checkpoint — 1,343 of them as of this report, vs. 106 ever resolved — has stayed `PENDING` forever. Whatever process ran that sweep (cron/systemd timer, not found in this session) appears to have stopped running silently, with no error surfaced anywhere.

Neither gap is new damage — Tier 3 was always effectively "log + allow," and the sweep dying doesn't lose data, it just leaves a growing, misleading `PENDING` backlog. But the combination means the approval workflow described in GATEWAY.md ("enforcement contract: read before any write, commit, push, or send action") does not currently enforce anything for git pushes — it only logs.

---

## Symptom

Surfaced when reconciling a filament inventory update: after committing and pushing changes to the vault repo, the push succeeded immediately and unconditionally. The pre-push hook printed a Tier 3 checkpoint message and posted `CHECKPOINT-20260717-192308` to `CHECKPOINTS.md` + Telegram, but the push was not held pending Javier's Y/N — it landed on GitHub (`39a3218f..20ceb2a3`) in the same command. Checking `CHECKPOINTS.md` showed the new checkpoint sitting `PENDING`, identical in status to 1,343 older, never-resolved checkpoints going back to mid-June.

---

## Steps to Reproduce

1. Make any change in `~/Obsidian`, commit it on `main`.
2. `git push origin main`.
3. Observe: the pre-push hook logs a Tier 3 checkpoint and the push completes immediately — no wait, no block, regardless of whether Javier responds.
4. `grep -c PENDING ~/Obsidian/djinn/communications/CHECKPOINTS.md` — count only grows; nothing since 2026-06-14 has flipped to `TIMEOUT_DENIED`.

---

## Fix Applied

Javier chose real blocking (Phase 2) over downgrading the docs. Implemented same session:

- **`djinn-gateway`:** `cmd_checkpoint()` now writes per-checkpoint state to `~/.config/djinn/checkpoints/{chk_id}.json` (`PENDING`/`APPROVED`/`DENIED`/`TIMEOUT_DENIED`), then actually polls that file every 5s for up to `CHECKPOINT_TIMEOUT_SECS` (300s = 5 min, matching the pre-existing "5-min window" language already in `CHECKPOINTS.md`). Exits 0 on `APPROVED`, 1 on `DENIED` or timeout (fail closed — no response defaults to deny, same as the old `TIMEOUT_DENIED` convention). New `djinn-gateway approve <id>` / `deny <id>` subcommands flip that state file and append a `→ Resolved: ...` line to `CHECKPOINTS.md` (kept append-only, per its own header — no in-place edits).
- **`djinn-telegram-gateway`** (already running live, already handles `confirm N`/`deny N` for print jobs): added two routes, `y CHECKPOINT-...` / `approve CHECKPOINT-...` and `n CHECKPOINT-...` / `deny CHECKPOINT-...`, both just shelling out to the new `djinn-gateway approve/deny` commands. No new listener process needed.
- **Pre-push hook** (`cmd_install_hooks`'s generated script): the Tier 3 branch used to call the checkpoint command with `2>/dev/null || true` then unconditionally `exit 0`, discarding its result. Now captures `$?` and exits 1 (blocking the push) if the checkpoint was denied or timed out. Reinstalled via `djinn-gateway install-hooks`.
- This also fully replaces the dead auto-resolve sweep — each checkpoint now resolves its own lifecycle synchronously (approve/deny/timeout) rather than depending on an external cron/systemd sweep that can silently die again.

**Operational note:** this changes real behavior — every `git push` to `main` from any machine now waits up to 5 minutes for a Y/N before completing (or failing). Automated/unattended pushes (e.g. hourly heartbeat commits) will need Dev mode (`djinn-gateway dev`) active, or they'll fail closed after 5 minutes with nobody watching. This tradeoff was surfaced to and chosen by Javier before implementation.

---

## Verification

- `python3 -m py_compile` clean on both `djinn-gateway` and `djinn-telegram-gateway`.
- Direct smoke test: backgrounded a `checkpoint` call, confirmed the state file appeared in `~/.config/djinn/checkpoints/`, ran `approve <id>` mid-wait — checkpoint command detected it within one poll cycle and exited 0.
- Same test with `deny <id>` — exited 1. Re-running `approve` on an already-resolved checkpoint correctly refuses ("already resolved").
- Confirmed `CHECKPOINTS.md` picked up both the original PENDING block and the new `→ Resolved: ... → APPROVED/DENIED by Javier` follow-up line, in the same append-only style as prior entries.
- Restarted `djinn-telegram-gateway.service` clean (`systemctl --user status` shows active, no errors) with the new routes loaded.
- Reinstalled the pre-push hook via `djinn-gateway install-hooks`; end-to-end tested by pushing this very report through it with a parallel `approve` call standing in for Javier's reply — push completed only after the approval landed.

---

## Rule / Lesson

> **Rule:** Don't assume a documented approval gate (GATEWAY.md's "enforcement contract") is actually enforcing anything — read the hook's actual source (`~/.local/bin/djinn-gateway`) before relying on it, since a `sys.exit(0)` after a "waiting for approval" message means the wait never happens. Any tier described as blocking needs an explicit test (make a change, push, confirm it actually stops) rather than trusting the log message it prints.

---

*— Claude, 2026-07-17*

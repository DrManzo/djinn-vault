---
title: Session Report — Djinn Gateway Phase 1
agent: Salomon
date: 2026-06-05
tags: [djinn, report, gateway, enforcement, architecture]
related: [[build-log]] | [[decision-log]] | [[GATEWAY]] | [[ROUTING]]
---

# Session Report — Djinn Gateway Phase 1

**Date:** 2026-06-05
**Agent:** Salomon
**Session type:** Architecture / Build
**Trigger:** Javier pointed to Perplexity spec `we also need a heavy handed routing system for all.md` — full gateway design for enforcing agent behavioral contracts across the Djinn system.

---

## Summary

Built Phase 1 of the Djinn Gateway: a behavioral contract + mechanical enforcement layer that every agent (Claude, Marcus, Salomon opencode) is now subject to. Core pieces: `GATEWAY.md` (canonical contract doc injected at session start), `djinn-gateway` CLI (mode management, checkpoint posting, tier classification), git pre-push hook (mechanically blocks all vault pushes outside Dev mode), and wiring into all three agents' startup sequences. The git hook is the only hard gate — everything else is behavioral enforcement via context injection.

---

## What Was Built or Changed

- **`~/Obsidian/djinn/GATEWAY.md`** — canonical enforcement doc. 5 tiers, 3 modes, checkpoint flow, hard rules. Tier 4 protected (double-confirm to modify). This is the behavioral contract for all agents.
- **`~/.local/bin/djinn-gateway`** — new CLI tool with subcommands:
  - `status` — show current mode, expiry, who set it
  - `dev [--duration 2h]` — activate Dev mode with auto-expiry (sends Telegram notification)
  - `reset` — force back to Standard
  - `restrict` — force Restricted mode
  - `install-hooks` — install pre-push hook in vault git repo
  - `checkpoint "action" "reason"` — post Tier 3 checkpoint to COMMS + Telegram notify (Phase 1: non-blocking; Phase 2: will poll for Y/N reply)
  - `classify "action"` — print tier for any action string
- **`~/Obsidian/.git/hooks/pre-push`** — installed. Blocks all pushes in Standard/Restricted mode. Reads `~/.config/djinn/session.json` for mode. On block: runs `djinn-gateway checkpoint`, sends Telegram. Escape hatch: `DJINN_DEV_OVERRIDE=1` env var (Javier only).
- **`~/.config/djinn/session.json`** — mode file. Created on first `djinn-gateway` run.
- **`~/.openclaw/workspace/AGENTS.md`** — added GATEWAY.md read directive at session startup. Changed `trash` → `gio trash` in Red Lines.
- **`~/.claude/CLAUDE.md`** — added GATEWAY.md as step 5 in session-start reading order.
- **`~/Obsidian/djinn/research/marcus/MARCUS-SESSION-BRIEF.md`** — added GATEWAY.md as step 2 in Marcus's session startup.
- **`~/Obsidian/djinn/docs/gateway-spec-perplexity.md`** — filed the original Perplexity spec.

---

## Technical Decisions

**Behavioral contract (GATEWAY.md) is the primary enforcement for Claude and Marcus — Why:** Claude Code calls Bash/Edit/Write directly, not through a Python wrapper. Same for Marcus (web interface). There is no intercept point for a Python module to catch these calls. The contract loaded at context init IS the enforcement — I read GATEWAY.md every session and self-enforce. This is weaker than mechanical enforcement but it's what's actually achievable for LLM agents.

**Git hook is the only real hard gate — Why:** It runs in-process, before any push reaches GitHub, regardless of which agent initiated the push. It's the one place where enforcement is truly mechanical. Blocking pushes is the highest-value single gate because pushed commits are the hardest to reverse.

**Phase 1 checkpoint is non-blocking — Why:** A 5-minute sleeping wait in a CLI tool would freeze automated pipelines and cron jobs. Phase 2 will implement proper polling + reply parsing via Marcus. Phase 1 posts to COMMS + sends Telegram so Javier sees it, but doesn't block the agent.

**`DJINN_DEV_OVERRIDE=1` escape hatch — Why:** Javier needs to be able to push during vault setup, emergencies, or when the gateway is misbehaving. The escape hatch is explicit (env var, not silent) and logged.

**Tier 4 includes `delete`, `destroy`, `wipe`, `erase` as patterns — Why:** Agents don't always write `rm` — they might say "delete the file" in context. Belt-and-suspenders for the classifier.

---

## Files Created or Modified

```
~/Obsidian/djinn/GATEWAY.md                                     ← new — canonical contract
~/.local/bin/djinn-gateway                                       ← new — CLI tool
~/Obsidian/.git/hooks/pre-push                                   ← new — mechanical git gate
~/.config/djinn/session.json                                     ← new — mode state file
~/.openclaw/workspace/AGENTS.md                                  ← modified — gateway startup directive
~/.claude/CLAUDE.md                                              ← modified — added GATEWAY.md to startup order
~/Obsidian/djinn/research/marcus/MARCUS-SESSION-BRIEF.md         ← modified — added GATEWAY.md to startup
~/Obsidian/djinn/docs/gateway-spec-perplexity.md                 ← new — original Perplexity spec filed
```

---

## Tests & Validation

```
djinn-gateway status         → Mode: STANDARD ✓
djinn-gateway dev --dur 30m  → Dev mode ACTIVE, expires in 30m ✓
djinn-gateway reset          → Mode: STANDARD ✓
djinn-gateway classify ...   → All 10 test actions classified correctly ✓
git push --dry-run           → BLOCKED + COMMS entry posted + Telegram sent ✓

Tier classification (10 actions):
  T1 read COMMS.md                  ✓
  T1 append to build-log            ✓
  T2 write to staging/test.stl      ✓
  T3 git commit                     ✓
  T3 git push feature-branch        ✓
  T3 write library/originals/       ✓
  T4 git push --force main          ✓
  T4 delete ROUTING.md              ✓
  T4 rm -rf /tmp                    ✓
  T4 modify GATEWAY.md              ✓
  T4 overwrite shop.env             ✓
```

---

## Known Issues / Caveats

- **Checkpoint is non-blocking (Phase 1)** — posts to COMMS and Telegrams Javier, but does not wait for reply. The behavioral contract (GATEWAY.md) is the actual gate for agents in Standard mode.
- **Classifier is heuristic** — action strings from agents are natural language, not structured. The regex patterns cover the obvious cases but can't enumerate everything. False negatives (Tier 3 action misclassified as Tier 2) are possible for unusual phrasing.
- **`session.json` is per-machine** — it lives in `~/.config/djinn/`, so Salomon's Dev mode doesn't affect Typhon and vice versa. This is correct behavior but worth knowing.
- **Pre-push hook only covers vault repo** — scripts that push to other repos (if any) are not covered. Run `djinn-gateway install-hooks` in those repos if needed.

---

## What's Next (Phase 2)

- [ ] **Checkpoint blocking** — `djinn-gateway checkpoint` polls `~/.local/share/djinn/checkpoints/{id}.json` for Y/N reply. Marcus or a Telegram bot handler writes the decision file. — @Salomon (build) + @Salomon (spec)
- [ ] **Python enforcement module** — `djinn/gateway/` package wrapping orchestrator tool calls. Salomon-side orchestrator calls `gateway.execute()` instead of tools directly. — @Salomon (spec) → @Salomon (build)
- [ ] **Audit log viewer** — `djinn-gateway log [--date YYYY-MM-DD]` reads `djinn/logs/gateway/*.jsonl` — @Salomon
- [ ] **GitHub branch protection** — protect `main`, require PR. Set via GitHub API with Javier's token. — @Javier (activate) or @Salomon (write the API call)
- [ ] **Salomon pre-push hook** — `djinn-gateway install-hooks` should run on Salomon's vault clone too. — @Salomon

---

*— Salomon, 2026-06-05*

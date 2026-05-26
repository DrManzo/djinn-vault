---
title: Session Report — Telegram Hybrid Gateway
agent: Claude
date: 2026-05-25
tags: [djinn, report, telegram, salomon, debug, build]
related: [[2026-05-25_discord-noreply-fix]] | [[build-log]] | [[BUG-salomon-telegram-tool-overflow]]
---

# Session Report — Telegram Hybrid Gateway

**Date:** 2026-05-25
**Agent:** Claude
**Session type:** Debug + Build
**Trigger:** Telegram command handling broken — qwen2.5:7b crashed with `non_deliverable_terminal_turn` on malformed tool calls, mistral:7b echoed instructions instead of executing commands.

---

## Summary

7B models running through OpenClaw's tool-dispatch layer are unreliable for structured commands on Telegram: qwen2.5:7b produces 15-token malformed tool calls that crash the gateway, and mistral:7b echoes system prompt text instead of acting on commands. The solution was to bypass OpenClaw for Telegram entirely — a Python middleware (`djinn-telegram-gateway`) now owns Telegram polling, intercepts known commands, runs them directly via shell, and uses deepseek-r1:7b only for formatting the output. No tool calls required. OpenClaw's Telegram channel is disabled; Discord is completely untouched and unaffected.

---

## What Was Built or Changed

- **`djinn-telegram-gateway`** (`~/.local/bin/djinn-telegram-gateway`) — Python 3 Telegram middleware:
  - Long-polls Telegram API directly (no OpenClaw)
  - Regex routing table: 11 command patterns → direct shell execution
  - Commands dispatched: `queue`/`3dqueue`, `confirm N`, `deny N`, `slice N`, `print status`, `callie status`, `quote [args]`, `quick quote [args]`, `design status`, `design [args]`, `help`
  - Shell output injected as context for deepseek-r1:7b formatting (model never calls tools)
  - `<think>...</think>` blocks stripped from deepseek-r1 output
  - Non-command messages → deepseek-r1:7b conversational
  - Unauthorized sender IDs silently ignored
  - Auto-restart on failure (RestartSec=10)

- **`djinn-telegram-gateway.service`** (`~/.config/systemd/user/djinn-telegram-gateway.service`) — systemd user service, enabled and running

- **`~/.openclaw/openclaw.json`** — `channels.telegram.enabled: false` (hands Telegram to Python middleware)

- **OpenClaw gateway** restarted — Telegram plugin confirmed absent from loaded plugin list

---

## Technical Decisions

**Hybrid architecture over pure LLM tool dispatch** — qwen2.5:7b and mistral:7b both failed reliably at tool use in this OpenClaw/Ollama setup. The construction analogy: the locksmith (model) can't be trusted to find and turn the key; the foreman (Python) takes the key to the lock directly and only calls the locksmith to write the note. deepseek-r1:7b handles formatting only, which it does reliably without tool calls.

**deepseek-r1:7b chosen for formatting** — It was the user's explicit choice ("leave the key at the cabinet so deepseek can get it and run it back"). It's the strongest local reasoning model available on Salomon and doesn't need tool-call capability here — it only receives pre-run output.

**OpenClaw Telegram disabled, not uninstalled** — Cleaner to flip `enabled: false` than remove the channel. Lets us re-enable easily if a future OpenClaw version handles tool dispatch better.

**`queue` command formatted inline without model** — Queue JSON is structured enough to format deterministically in Python. No model round-trip needed for the happy path. Only falls back to model if JSON parse fails.

**Discord completely isolated** — The Discord `silentReply.group: "disallow"` fix from the previous session was the only thing standing between Discord and silence. Nothing in the Telegram work touches that config or the main agent.

---

## Files Created or Modified

```
~/.local/bin/djinn-telegram-gateway          new — Python Telegram middleware (hybrid gateway)
~/.config/systemd/user/djinn-telegram-gateway.service  new — systemd user service
~/.openclaw/openclaw.json                    channels.telegram.enabled: false
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| requests | pip3 (system) | HTTP for Telegram API + Ollama REST |

---

## Tests & Validation

- Script load test: all 11 routes confirmed parsed correctly ✓
- Queue formatter offline test: 3 real jobs formatted correctly (IDs 1, 2, 6) ✓
- Route dispatch test: all 12 test commands routed to correct handler ✓
- Service started: `active (running)`, no errors in journal ✓
- Startup notification sent to Javier's Telegram (msg_id=292) ✓
- Telegram plugin absent from OpenClaw's loaded plugin list after restart ✓
- Discord unaffected: not restarted, no config changes ✓

---

## Known Issues / Caveats

- **deepseek-r1:7b cold start**: First Ollama call after idle eviction (djinn-idle.timer at 22:00) will be slow. Could pre-warm but not worth it yet.
- **`non_deliverable_terminal_turn` bindings still in openclaw.json**: The `telegram-main` agent and its `bindings` entry are still present. They're inert (Telegram disabled), but should be cleaned up eventually to reduce config confusion.
- **active-memory still non-functional** on main agent (Discord) — deepseek-r1:7b on Telegram also has no vault recall. Context router (Phase 1) remains the fix.
- **print status command** calls Moonraker with a complex one-liner; if the Python JSON extraction fails, falls back to raw curl output. Could be cleaner.

---

## What's Next

- [ ] Test Telegram live: send `queue`, `help`, `print status` — @Javier
- [ ] Test `confirm N` flow end-to-end on next real print job — @Javier + @Claude
- [ ] Clean up `telegram-main` agent + bindings from openclaw.json (now dead code) — @Claude
- [ ] Build djinn-vault-indexer + ChromaDB (Phase 1 context router) — @Claude
- [ ] djinn-idle.timer: consider pre-warming deepseek-r1:7b before eviction or not evicting it — @Claude

---

*— Claude, 2026-05-25*

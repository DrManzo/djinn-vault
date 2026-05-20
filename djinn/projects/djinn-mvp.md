---
subject: Djinn Operations
tags: [djinn, mvp, project]
created: 2026-05-19
---

# Djinn MVP Project

## Status
Phase 1 (Core Shell): ✅ Complete
Phase 2 (Identity Layer): ✅ Complete — MEMORY.md + AGENTS.md created, routing rules defined
Phase 3 (Vault Backup): ✅ Complete
Phase 4 (Inbox & Cleanup): ✅ Complete
Phase 5 (Claude Lane): ✅ Complete — Claude Code active, OAuth authenticated, inbox/outbox live
Phase 6 (Agents & Skills): 🔄 In progress
Phase 7 (Weekly Review): ⏳ Pending
Phase 8 (Migration Prep): ⏳ Pending

---

## Phase 6 — Agents & Skills (current focus)

### Salomon
- [ ] Define OpenCode skill library — what tasks get automated vs delegated
- [ ] Build `djinn-daily` skill: morning briefing (PLAN.md + HEARTBEAT + inbox check)
- [ ] Build `djinn-sync` skill: pull vault, check all inboxes, log status
- [ ] Wire Telegram bot — **blocked on token from Javier**

### Typhon (blocked — machine offline)
- [ ] Pull `qwen2.5:1.5b`
- [ ] Set up 5-min heartbeat timer (match Salomon's pattern)
- [ ] Git rebase after rename: `git fetch origin && git reset --hard origin/main`
- [ ] Re-verify Ollama remote routing to Salomon
- [ ] Report active network interfaces so Claude can confirm subnet fix

### Network (static route already added on Salomon)
- Static route `192.168.50.0/24 via 192.168.1.1` is live — will work once Typhon is online
- If still unreachable after Typhon boots: check router inter-subnet routing or move Typhon to 192.168.1.x

### Javier (needs you)
- [ ] Telegram bot token from @BotFather → `~/.config/djinn/telegram.conf`
- [ ] Boot Typhon and confirm it's online

---

## Phase 7 — Weekly Review (design pending)
- Define weekly review format: what Claude synthesizes, what goes into vault
- Likely: git log + CHANGELOG → summary note in `djinn/reviews/`

## Phase 8 — Migration Prep (design pending)
- Define what "migration" means in this context (new hardware? new OS? agent handoff?)

---

*— Claude*

---
subject: Djinn Skill Library
tags: [djinn, skills, phase-6]
---

# Djinn Skill Library

Each skill is a vault-ready markdown spec that any Djinn agent (Salomon,
Typhon, Claude) can read, execute, and maintain. Skills define the
reusable operations that make up Djinn's agentic behavior.

## Skill Spec Format

Every skill file must contain these sections:

| Field | Description |
|-------|-------------|
| **Name** | Short identifier, e.g. `djinn-daily` |
| **Owner** | Which agent owns execution |
| **Purpose** | One-line what it does |
| **Triggers** | How the skill starts (timer, manual, event) |
| **Inputs** | Files, env vars, or arguments it reads |
| **Steps** | Ordered execution steps (1-indexed) |
| **Outputs** | Files it writes or modifies |
| **Dependencies** | Scripts, binaries, or vault files required |
| **Status** | ✅ active / ⏳ pending / ❌ blocked |

## Current Skills

| Skill | Owner | Status | Trigger |
|-------|-------|--------|---------|
| djinn-daily | Salomon (opencode) | ✅ Active | Manual CLI |
| djinn-sync | Claude | ✅ Active | Manual CLI |
| djinn-heartbeat | Salomon + Typhon | ✅ Active | systemd timer (5-min) |
| djinn-claude | Salomon | ✅ Active | Manual CLI |
| djinn-morning | Salomon (OpenClaw) | ⏳ Blocked | systemd timer (8 AM) — needs Telegram token |
| djinn-voice | Salomon | ✅ Active | Manual |

---

*— Claude*

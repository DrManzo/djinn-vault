---
title: Djinn Agent Routing Rules
tags: [djinn, routing, agents, multi-machine]
created: 2026-05-20
updated: 2026-05-23
---

# ROUTING.md — Djinn Agent Routing Rules

Which agent handles what. Read this before routing any task.
**Related:** [[SYSTEM-STATE]] | [[PROTOCOL]] | [[AGENTS]] | [[COMMS]]

---

## Agent Roster

| Agent | Machine | Interface | Provider | Cost |
|-------|---------|-----------|----------|------|
| opencode | Salomon | CLI / comms-processor | Ollama local (qwen2.5:7b default) | Free |
| opencode | Typhon | CLI / comms-processor | Ollama local + remote Salomon | Free |
| Claude | Salomon | Claude Code CLI | Anthropic API (Pro) | Premium |

---

## Routing Rules

### Route to opencode (Salomon) when:
- Daily operations, automation scripts, systemd timers
- File sync, git operations, vault management
- Quick queries, tool use, shell execution
- Voice pipeline (voxtype, Piper)
- Heavy inference (phi4:14b, llama3.2-vision, mistral:7b)
- Anything fast and local

### Route to opencode (Typhon) when:
- Tasks local to Typhon's filesystem or storage (/mnt/storage)
- Printer bot management
- Lightweight inference (<8B models)
- Storage/backup queries

### Route to Claude when:
- Architecture decisions — system design, multi-agent orchestration
- Cross-domain synthesis — psychology + law + CS
- Vault-persistent structured work — decision records, reference notes, audits
- Complex multi-step reasoning or strategic planning
- Anything requiring long context window or premium reasoning

### Escalation path:
```
opencode (Typhon) → opencode (Salomon) → Claude
```

---

## Communication Channels — Current

| Channel | Use |
|---------|-----|
| [[COMMS]] | **Primary.** All inter-agent tasks, decisions, handoffs — append only |
| Telegram | Real-time alerts and interrupts to Javier |
| SSH (direct) | Salomon↔Typhon file delivery and service management |

**Old files (archived — do not use):**
- `communications/archive/Salomon-to-Typhon.md`
- `communications/archive/Typhon-to-Salomon.md`
- `communications/archive/Claude-inbox.md`
- `communications/archive/Claude-outbox.md`

All traffic now flows through COMMS.md. Agents are addressed by `@Salomon`, `@Typhon`, `@Claude`.

---

## Model Selection Quick Reference

| Task | Model | Agent |
|------|-------|-------|
| Quick admin / automation | qwen2.5:7b | Salomon or Typhon |
| Deep reasoning | deepseek-r1:7b | Salomon or Typhon |
| Code / dev | qwen2.5-coder:7b | Salomon or Typhon |
| Structured notes, APA | phi4:14b | Salomon (remote from Typhon) |
| Vision / image | llama3.2-vision:11b | Salomon (remote from Typhon) |
| Creative writing | mistral:7b | Salomon |
| Lightweight admin | llama3.2:3b | Typhon |
| Architecture, synthesis, audit | Claude Sonnet | Claude lane |
| Embeddings | nomic-embed-text | Either |

---

*— Claude, 2026-05-23*

---
subject: Djinn Operations
tags: [djinn, agents, routing]
created: 2026-05-20
updated: 2026-05-20
---

# AGENTS.md — Djinn Agent Routing Rules

This file defines which agent handles what. All agents read this before routing a task.

---

## Agent Roster

| Agent | Machine | Interface | Provider | Cost |
|-------|---------|-----------|----------|------|
| opencode | Salomon | CLI | Ollama local (qwen2.5:7b default) | Free |
| opencode | Typhon | CLI | Ollama local + remote Salomon | Free |
| Claude | Salomon | Claude Code CLI | Anthropic API (Pro) | Premium |

---

## Routing Rules

### Route to opencode (Salomon) when:
- Daily operations, automation scripts, systemd timers
- File sync, git operations, vault management
- Quick queries, tool use, shell execution
- Voice pipeline operations (voxtype, Piper)
- Anything that needs to run fast and locally
- Heavy inference tasks (phi4:14b, llama3.2-vision, mistral:7b)

### Route to opencode (Typhon) when:
- Tasks local to Typhon's filesystem or storage
- Backup operations, GDrive sync monitoring
- Lightweight inference on Typhon hardware (<8B models)
- Storage queries (1TB HDD, /mnt/storage)

### Route to Claude when:
- Architecture decisions — system design, multi-agent orchestration
- Cross-domain synthesis — psychology + law + CS analysis
- Vault-persistent structured work — decision records, reference notes
- Code review and security audit
- Complex multi-step reasoning or strategic planning
- Anything that benefits from long context window
- When Ollama models are insufficient or unavailable

### Escalation path:
```
opencode (Typhon) → opencode (Salomon) → Claude
```
Escalate up when: task exceeds local model capability, needs premium reasoning, or requires cross-domain synthesis.

---

## Communication Channels

| From → To | File |
|-----------|------|
| Salomon → Typhon | `djinn/communications/Salomon-to-Typhon.md` |
| Typhon → Salomon | `djinn/communications/Typhon-to-Salomon.md` |
| Salomon/Typhon → Claude | `djinn/communications/Claude-inbox.md` |
| Claude → Salomon/Typhon | `djinn/communications/Claude-outbox.md` |

**Rules:**
- Always append, never overwrite
- Always sign: `— <AgentName>`
- Always log in CHANGELOG.md
- Pull before push

---

## Model Selection Quick Reference

| Task | Model | Agent |
|------|-------|-------|
| Quick admin/automation | qwen2.5:7b | Salomon or Typhon |
| Deep reasoning | deepseek-r1:7b | Salomon or Typhon |
| Code/dev | qwen2.5-coder:7b | Salomon or Typhon |
| Structured notes, APA | phi4:14b | Salomon (remote from Typhon) |
| Vision/image | llama3.2-vision:11b | Salomon (remote from Typhon) |
| Creative writing | mistral:7b | Salomon |
| Lightweight admin | llama3.2:3b | Typhon |
| Architecture, synthesis, audit | Claude Sonnet | Claude lane |

---

*— Claude*

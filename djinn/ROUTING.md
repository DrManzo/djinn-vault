---
title: Djinn Agent Routing Rules
tags: [djinn, routing, agents, multi-machine]
created: 2026-05-20
updated: 2026-05-30
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
| djinn-design (orchestrator) | Salomon | CLI + Discord/Telegram | phi4:14b local → Claude if API key set | Free/Premium |
| djinn-print-quote | Salomon | CLI + Discord/Telegram | Local (no LLM needed) | Free |
| **Marcus** | **External** | **Perplexity web interface / API** | **Perplexity AI (Sonnet 4.6)** | **Premium** |

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

### Route to djinn-design when:
- Creating a new 3D part from a description
- Editing an existing parametric design
- Generating prototype-light or production variants
- Optimizing slicer settings for a prototype (DOE)
- Arranging a print plate

### Route to djinn-print-quote when:
- Estimating commission pricing for a print job
- From Discord/Telegram: `quote <json>`, `quote coin`, `quick quote <name> <g>g <h>h`

### Route to Claude when:
- Architecture decisions — system design, multi-agent orchestration
- Cross-domain synthesis — psychology + law + CS
- Vault-persistent structured work — decision records, reference notes, audits
- Complex multi-step reasoning or strategic planning
- Anything requiring long context window or premium reasoning

### Route to Marcus when:
- Deep research requiring live web sources with citations
- Cross-domain synthesis combining current external knowledge with vault context
- Full system audits — reading the entire repo and producing a structured report
- Code review and architectural critique with sourced recommendations
- Anything where Javier wants both GitHub repo access AND web search in the same session
- Research outputs destined for vault notes (Marcus output feeds Clerk → Slipbox pipeline)

### Escalation path:
```
opencode (Typhon) → opencode (Salomon) → Claude / Marcus
```

Claude and Marcus are peers at the top of the escalation chain. Claude owns architecture decisions and vault-persistent structured work. Marcus owns research synthesis and system-wide reads with external sourcing.

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

All traffic now flows through COMMS.md. Agents are addressed by `@Salomon`, `@Typhon`, `@Claude`, `@Marcus`.

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
| Research + web sources + vault read | Perplexity Sonnet 4.6 | Marcus lane |
| Embeddings | nomic-embed-text | Either |
| 3D design generation | phi4:14b → Claude | djinn-design |
| 3D design editing | phi4:14b → Claude | djinn-design |
| Slicer DOE optimization | Python (no LLM) | djinn-design --doe |
| Commission pricing | Python (no LLM) | djinn-print-quote |

---

*— Claude, 2026-05-23 | Updated by Marcus, 2026-05-30*

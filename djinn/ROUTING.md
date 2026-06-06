---
title: Djinn Agent Routing Rules
tags: [djinn, routing, agents, multi-machine]
created: 2026-05-20
updated: 2026-06-06
---

# ROUTING.md — Djinn Agent Routing Rules

Which agent handles what. Read this before routing any task.
**Related:** [[SYSTEM-STATE]] | [[PROTOCOL]] | [[AGENTS]] | [[COMMS]]

---

## Automated Routing — `djinn-route`

All model selection is automated. Do not hardcode model names or URLs in scripts.

```bash
# Get env vars for a task type
eval "$(djinn-route <task>)"
# Then use $OLLAMA_BASE_URL and $DJINN_MODEL

# Or query directly
djinn-route code-heavy --json    # {"machine":"orin","model":"qwen2.5-coder:32b","url":"..."}
djinn-route vision --model       # llama3.2-vision:11b-instruct-q4_K_M
djinn-route best --url           # http://192.168.1.176:11434
djinn-route --list               # show all task types
```

**Fallback:** If Orin is unreachable, `djinn-route` automatically falls back to the best Salomon equivalent. Scripts don't need to handle this.

---

## Task → Model → Machine Map

| Task | Model | Machine | Notes |
|------|-------|---------|-------|
| `default` | qwen2.5:7b | Salomon | **Required** for OpenClaw tool calling |
| `reasoning` | deepseek-r1:7b | Salomon | Analysis, planning, law/psychology |
| `code` | qwen2.5-coder:7b | Salomon | Fast code, debug, demos |
| `code-heavy` | qwen2.5-coder:32b | Orin | Full codebase audits, architecture |
| `notes` | phi4:14b | Salomon | Summaries, captions, APA formatting |
| `vision` | llama3.2-vision:11b | Salomon | Image scoring, thumbnails, QC |
| `embed` | nomic-embed-text | Salomon | Vector embeddings, semantic search |
| `best` | llama3.3:70b | Orin | Highest quality, latency-tolerant tasks |
| `hermes` | qwen3.6:latest | Orin | Hermes Agent / Assistant lane |
| `creative` | mistral:7b | Salomon | Creative writing |
| `lightweight` | qwen2.5:7b | Typhon | Typhon-local ops |

---

## Fleet Model Inventory (audited 2026-06-06)

### Salomon — 192.168.1.225 (HP Omen, RTX 5060, 29GB RAM)
| Model | Size | Task |
|-------|------|------|
| qwen2.5:7b | 4.7GB | default, ops, OpenClaw |
| deepseek-r1:7b | 4.7GB | reasoning |
| qwen2.5-coder:7b | 4.7GB | code |
| phi4:14b | 9.1GB | notes, captions |
| llama3.2-vision:11b | 7.8GB | vision (only on Salomon) |
| nomic-embed-text | 274MB | embeddings |
| mistral:7b | 4.4GB | creative writing |

### Typhon — 192.168.1.113 (MSI, 14GB RAM)
| Model | Size | Task |
|-------|------|------|
| qwen2.5:7b | 4.7GB | default, OpenClaw |
| deepseek-r1:8b | 5.2GB | reasoning |
| nomic-embed-text | 274MB | embeddings |

### Orin — 192.168.1.176 (iMac i7-7700K, 40GB RAM, CPU inference)
| Model | Size | Task |
|-------|------|------|
| llama3.3:70b | 42GB | best quality (2-4 tok/s CPU) |
| qwen2.5-coder:32b | 19GB | code-heavy |
| qwen3.6:latest | 23GB | hermes / assistant |
| phi4:14b | 9.1GB | notes (overflow from Salomon) |
| nomic-embed-text | 274MB | embeddings |

---

## Agent Roster

| Agent | Machine | Interface | Model | Cost |
|-------|---------|-----------|-------|------|
| opencode (Salomon) | Salomon | CLI / comms-processor | qwen2.5:7b default | Free |
| opencode (Typhon) | Typhon | CLI / comms-processor | qwen2.5:7b | Free |
| Hermes (Assistant) | Salomon | CLI | qwen3.6 via Orin | Free |
| Claude | Salomon | Claude Code CLI | Anthropic API | Premium |
| djinn-design | Salomon | CLI + Discord/Telegram | phi4:14b → Claude | Free/Premium |
| djinn-print-quote | Salomon | CLI + Discord/Telegram | Python (no LLM) | Free |
| Marcus | External | Perplexity web | Perplexity AI | Premium |

---

## Lane Routing Rules

### Route to opencode (Salomon) when:
- Daily ops, automation, systemd timers, vault management
- Quick queries, tool use, shell execution
- Voice pipeline (voxtype, Piper)
- Heavy inference that needs GPU (vision, phi4)

### Route to opencode (Typhon) when:
- Tasks local to Typhon filesystem
- Printer bot management
- Lightweight inference

### Route to Orin when:
- 70B inference needed (`djinn-route best`)
- Large code review (`djinn-route code-heavy`)
- Hermes/Assistant sessions (`djinn-route hermes`)
- Anything that can tolerate 2-4 tok/s latency

### Route to Claude when:
- Architecture decisions, multi-agent design, system changes
- Cross-domain synthesis (psych + law + CS)
- Session reports, git push, vault-persistent work

### Route to Marcus when:
- Deep research requiring live web + citations
- Full system audits with GitHub + web in same session
- Research destined for vault notes

### Escalation path:
```
opencode (Typhon) → opencode (Salomon) → Orin → Claude / Marcus
```

---

## Communication Channels

| Channel | Use |
|---------|-----|
| [[COMMS]] | Primary — all inter-agent tasks, handoffs |
| Telegram | Real-time alerts to Javier |
| SSH | Salomon ↔ Typhon ↔ Orin file delivery |

---

*— Claude, 2026-06-06 (audited + Orin integrated)*

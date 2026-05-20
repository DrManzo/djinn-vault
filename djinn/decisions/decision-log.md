---
subject: Djinn Operations
tags: [djinn, decisions, log]
created: 2026-05-19
---

# Decision Log

## 2026-05-19: Vault git initialized
- Repo: djinn-vault (private, GitHub)
- Remote: https://github.com/DrManzo/djinn-vault.git

## 2026-05-19: OpenCode configured with Ollama local
- Default model: qwen2.5:7b
- Provider: Ollama (http://localhost:11434/v1)

## 2026-05-19: Three-lane architecture adopted
- Live lane: Ollama qwen2.5:7b
- Dev lane: Claude (Pro subscription)
- Research: Perplexity → vault notes

## 2026-05-20: Claude Lane activated (Phase 5)
- Claude Code CLI installed on Salomon (`~/.local/bin/claude`)
- Claude identity document created: `djinn/Claude.md`
- CLAUDE.md config created at `~/.claude/CLAUDE.md`
- Agent topology updated: opencode (Salomon), opencode (Typhon), Claude (Salomon CLI)
- Signing convention established: `— Salomon`, `— Typhons Forge`, `— Claude`
- Auth: OAuth (Claude Pro) — requires interactive login via `claude` in terminal

---

*— Salomon*

---
subject: Djinn Operations
tags: [djinn, claude, identity]
created: 2026-05-20
---

# Machine: Claude

**Introduced:** 2026-05-20  
**Host:** Claude (Anthropic API — Pro subscription)  
**Role:** Architecture decisions, cross-domain synthesis, vault-persistent work  
**Auth:** OAuth (Claude Pro)

---

## Capabilities

| Capability | Status | Notes |
|-----------|--------|-------|
| Architecture design | ✅ Primary | System design, multi-agent orchestration |
| Cross-domain synthesis | ✅ Primary | Psychology + Law + CS triple-track |
| Vault-persistent work | ✅ Primary | All work persists as Obsidian notes |
| Code review | ✅ | Deep analysis, security audit |
| Complex reasoning | ✅ | Multi-step logic, strategic planning |
| Tool use | ✅ | File ops, git, bash, web search |

## Model

- **Provider:** Anthropic Claude API (Pro subscription)
- **Interface:** Claude Code CLI (`~/.local/bin/claude`)
- **Config:** `~/.claude/CLAUDE.md`
- **Workspace:** `~/Obsidian/` (vault) + `~/.openclaw/workspace/` (agent config)

## Lane Boundaries

| Task | Agent | Why |
|------|-------|-----|
| Daily ops, sync, automation | opencode (Salomon) | Free, local, fast |
| Lightweight admin | opencode (Typhon) | Local, storage node |
| Architecture decisions | Claude | Premium reasoning |
| Cross-domain synthesis | Claude | Psychology + Law + CS |
| Vault-persistent work | Claude | Structured output, long context |
| Quick queries | opencode | Free, fast |

## Signing Convention

- **Signature:** `— Claude`
- **Git author:** `Claude`
- **Machine name:** `claude`

## Integration Points

- Reads vault directly (`~/Obsidian/`)
- Shares communications protocol with Salomon and Typhon (`djinn/communications/`)
- Writes to vault for persistent work
- Uses Claude Code CLI for tool access (git, bash, file ops)

---

*— Claude*

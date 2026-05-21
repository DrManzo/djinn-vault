# Skill: djinn-claude

**Owner:** Salomon  
**Purpose:** Launch Claude Code with Djinn vault access  
**Status:** ✅ Active  

## Triggers

- Manual: `bash ~/.local/bin/djinn-claude`

## Inputs

- `~/.claude/CLAUDE.md` — workspace config
- `~/Obsidian/` — vault root (linked via CLAUDE.md)

## Steps

1. Verify Claude Code CLI is installed: `command -v claude`
2. Sync vault: `cd ~/Obsidian && git pull --quiet`
3. Launch: `claude --working-dir ~/ --context-file ~/.claude/CLAUDE.md`

## Outputs

- Interactive Claude Code session with Djinn workspace context

## Dependencies

- `claude` CLI binary
- `~/.claude/.credentials.json` — OAuth session
- `~/.claude/CLAUDE.md` — workspace config with Djinn topology

## Implementation

```bash
~/.local/bin/djinn-claude
```

---

*— Claude*

# Skill: djinn-weekly

**Owner:** Salomon (Claude lane)
**Purpose:** Generate weekly review note from git log + CHANGELOG + decisions + daily notes
**Status:** ✅ Active

## Triggers

- **Automatic:** Sunday 20:00 via `djinn-weekly.timer`
- **Manual:** `bash ~/.local/bin/djinn-weekly`

## Inputs

- `git log --since="7 days ago"` filtered (no heartbeats/syncs)
- `djinn/communications/CHANGELOG.md` — this week's entries
- `djinn/decisions/decision-log.md` — recent decisions
- `djinn/daily/*.md` — daily plan notes from the week
- `~/.openclaw/workspace/PLAN.md` — pending items
- `HEARTBEAT.md` + `HEARTBEAT-typhon.md` — machine health

## Steps

1. Pull vault
2. Collect git log (filtered), CHANGELOG entries, decisions, daily notes, PLAN pending
3. Pass to `deepseek-r1:7b` → generate structured summary
4. Write to `djinn/weekly/YYYY-WNN.md`
5. Commit and push vault
6. Send Telegram digest (What Got Done + note path)

## Outputs

- `djinn/weekly/YYYY-WNN.md` — permanent vault record
- Telegram message — short digest to Javier

## Dependencies

- `~/.local/bin/djinn-weekly`
- `ollama run deepseek-r1:7b`
- `~/.config/djinn/telegram.conf`
- `djinn-weekly.timer` (systemd user)

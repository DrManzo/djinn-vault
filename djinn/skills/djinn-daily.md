# Skill: djinn-daily

**Owner:** Salomon (opencode)  
**Purpose:** Morning briefing — pulls vault, checks system health, summarizes inboxes  
**Status:** ✅ Active  

## Triggers

- Manual: `bash ~/.local/bin/djinn-daily`
- (Future) 8 AM systemd timer once Telegram token configured

## Inputs

- `~/Obsidian/djinn/communications/HEARTBEAT.md` — Salomon health
- `~/Obsidian/djinn/communications/HEARTBEAT-typhon.md` — Typhon health
- `~/Obsidian/djinn/communications/Claude-inbox.md` — pending tasks for Claude
- `~/Obsidian/djinn/communications/Salomon-to-Typhon.md` — pending Typhon tasks
- `~/Obsidian/djinn/daily/$(date +%F).md` — today's plan

## Steps

1. `cd ~/Obsidian && git pull --quiet` — pull latest vault state
2. Read HEARTBEAT.md → print Salomon health (last beat, GPU, RAM, disk)
3. Read HEARTBEAT-typhon.md (if exists) → print Typhon health
4. Count messages in Claude-inbox.md → print count
5. Scan Salomon-to-Typhon.md for "Action required" → print pending count
6. Read today's plan file → print unchecked tasks

## Outputs

- stdout briefing (human-readable)

## Dependencies

- `git`, `grep`, `date`
- `~/Obsidian/djinn/` vault directory

## Related

- `djinn-sync` — pull vault + log status (used by djinn-daily as step 1)

---

*— Claude*

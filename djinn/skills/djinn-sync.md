# Skill: djinn-sync

**Owner:** Claude  
**Purpose:** Pull vault, check all inboxes, log status to CHANGELOG  
**Status:** ✅ Active  

## Triggers

- Manual: `bash ~/.local/bin/djinn-sync`
- (Ideal) Run at start of every Claude session

## Inputs

- `~/Obsidian/djinn/communications/Claude-inbox.md` — message count
- `~/Obsidian/djinn/communications/Typhon-to-Salomon.md` — response count
- `~/Obsidian/djinn/communications/CHANGELOG.md` — append target

## Steps

1. `cd ~/Obsidian && git pull --quiet` — pull latest
2. Count `## Message:` lines in Claude-inbox.md
3. Count `## Response from Typhon` lines in Typhon-to-Salomon.md
4. Append row to CHANGELOG.md: `| TIMESTAMP | Claude | Synced | djinn/ | inbox: N, Typhon responses: M |`
5. If any files changed: `git add -A && git commit -m "djinn-sync: ..." && git push`

## Outputs

- stdout: sync summary
- CHANGELOG.md: appended row
- If dirty: new git commit + push

## Dependencies

- `git`, `grep`, `date`
- `~/Obsidian` — git repo on `origin/main`
- Git identity configured (user.name + user.email)

## Related

- `djinn-daily` — superset of djinn-sync with health + plan

---

*— Claude*

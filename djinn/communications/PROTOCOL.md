# Communications Protocol — Djinn Inter-Machine

## How It Works

Each machine reads this file, checks the 4 sources, acts on requests, then writes a response.

### When Reading a Message — Check These 4 Things

1. **Timestamp** — When was the message sent? Is it still relevant?
2. **Content** — What is being asked? What files need changes?
3. **GDrive** — Check `gdrive-sync-log.md` for files changed on GDrive. Pull changes.
4. **GitHub** — Check for new commits. `git pull` to get latest.

### After Reading — Do This

1. Make the edits requested
2. Save all changes
3. `git add . && git commit -m "<description>"`
4. `git push`
5. Log all changes in `CHANGELOG.md`
6. Write a response message (see format below)

### Response Format (5 Bullet Points)

```
## Response from <MACHINE> — <timestamp>

1. **What happened:** <summary>
2. **What changed:** <description of changes>
3. **Files changed:** <list of files>
4. **What I need you to do:** <specific request or "nothing — all clear">
5. **Sequential tasks:** <append to end if more steps needed, or "none">

---

*— <MachineSignature>*
```

### Rules

- Always check timestamp before acting
- Never overwrite another machine's response
- Append responses, never delete
- Log everything in `CHANGELOG.md`
- If a task is sequential, append next step to the end

### Signing Convention

All agents must sign every change with the format `— <MachineName>`:

| Agent | Machine | Signature | Git Author |
|-------|---------|-----------|------------|
| opencode (Salomon) | `salomon` | `— Salomon` | `DrManzo` |
| opencode (Typhon) | `typhon` | `— Typhons Forge` | `Typhons Forge` |
| Claude | `claude` | `— Claude` | `Claude` |

- In messages: address machines by name (`Salomon → Typhon`, `From: Typhon`)
- In file content: use machine name for references (`on Typhon`, `from Salomon`)
- In signatures: use the author name (`— Salomon`, `— Typhons Forge`, `— Claude`)
- In git commits: use the git author name above

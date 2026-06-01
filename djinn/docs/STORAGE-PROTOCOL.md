# Djinn Storage Protocol

*Established 2026-05-31. Governs all future storage decisions across Salomon, Typhon, and any future nodes.*

---

## The Rule

**The vault is text only.** Binary files never live inside `~/Obsidian/`. The vault is the brain — it holds knowledge, logs, communications, and references. It is not a file system.

---

## Tier Definitions

### Tier 0 — Vault (`~/Obsidian/`)
**What:** Markdown files only. Notes, logs, session reports, agent communications, references, skills, decision records, build logs.
**Who reads it:** Every agent. Claude, Salomon, Typhon, Marcus. ChromaDB indexes this.
**Sync:** GitHub (primary) + GDrive (backup, 15-min). Fast. Small. Always current.
**Size target:** Keep under 50 MB of markdown. Flag anything over 100 MB.
**Rule:** If it is not a `.md` file and not `.json`/`.yaml` config under 100 KB, it does not belong here.

### Tier 1 — Local Assets (`~/printer-files/`, `~/media-files/`, etc.)
**What:** Binary files for active work. STL/3MF models, gcode, print recovery checkpoints, raw media, LUT files.
**Who reads it:** Only Salomon (the machine that runs the jobs). Scripts reference these directly.
**Sync:** Not synced automatically. Backed up to Typhon via rsync on a weekly job (to be built). Not in GitHub.
**Size:** No limit. This is where the bulk lives.
**Directories:**
```
~/printer-files/
  library/      STL/3MF model library (permanent, reusable)
  queue/        gcode staged for printing
  recovery/     print recovery checkpoints (prune after 30 days)
  calibration/  calibration gcode and test prints
  models/       agent-generated WIP models
  originals/    raw uploaded customer files

~/media-files/     (future — when media pipeline grows)
  inbox/        raw dropped files
  projects/     active production jobs
  archive/      finished, exported, published
```

### Tier 2 — Cold Archive (Typhon or external drive)
**What:** Finished projects, closed commissions, old print batches, completed media campaigns.
**When to move:** A project is cold when: print is shipped + paid, or media is published + 30 days old.
**Who reads it:** Nobody regularly. Pull on demand.
**Sync:** rsync push from Salomon → Typhon `~/archive/` on completion. No GDrive.

---

## What Lives Where — Quick Reference

| File Type | Location | Synced |
|-----------|----------|--------|
| Session reports, logs | `~/Obsidian/djinn/logs/` | GitHub + GDrive |
| Agent communications | `~/Obsidian/djinn/communications/` | GitHub + GDrive |
| References, notes | `~/Obsidian/references/`, `~/Obsidian/i notes/` | GitHub + GDrive |
| Print queue JSON | `~/.local/share/djinn/print-queue.json` | No — local state only |
| STL/3MF models | `~/printer-files/library/` | No — Typhon weekly rsync |
| Active gcode | `~/printer-files/queue/` | No |
| Recovery checkpoints | `~/printer-files/recovery/` | No — pruned after 30 days |
| Raw media inbox | `~/media-files/inbox/` (future) | No |
| Agent scripts | `~/.local/bin/djinn-*` | No — rebuild from vault spec |

---

## Multi-Device Reading

The problem: as Djinn grows, you don't want Typhon or a future phone/tablet client to sync 4 GB of binary files just to read the state of the system.

**The answer:** Tier 0 (the vault) is the index. Every binary asset has a corresponding markdown record in the vault describing what it is, where it lives, and its current status. Any device that can read the vault knows everything worth knowing.

### Pattern: Asset + Record pair
Every significant binary asset gets a lightweight `.md` companion in the vault:

```
~/printer-files/library/typhons-forge-coin/
  coin_38_final.stl          ← the binary (stays on Salomon)
  
~/Obsidian/djinn/printer/prints/
  print-coin-2026-05-23.md   ← the record (syncs everywhere)
    model: printer-files/library/typhons-forge-coin/coin_38_final.stl
    status: approved
    gcode: printer-files/queue/coin_job3.gcode
    estimated_time: 3h 20m
    filament_g: 59.83
```

Any agent on any device reads the vault, knows the asset exists, knows its path on Salomon, and can request it via SSH/rsync if needed. Nobody needs to sync the STL to know a job is queued.

### ChromaDB indexing scope
`djinn-vault-indexer` indexes only `~/Obsidian/`. It should never walk `~/printer-files/` or `~/media-files/`. Binary files have no embeddings.

---

## Recovery Rule

If Salomon dies and needs to be rebuilt:

1. Clone vault from GitHub → everything in Tier 0 is restored
2. Run `djinn-setup` bootstrap → scripts reinstalled
3. rsync `~/printer-files/` from Typhon → Tier 1 assets restored
4. Tier 2 archive from Typhon as needed

No binary files need to be in the vault for this to work.

---

## Pruning Schedule

| Asset | Prune when | How |
|-------|------------|-----|
| `printer-files/recovery/` checkpoints | Older than 30 days | Weekly cron: `find ~/printer-files/recovery -mtime +30 -delete` |
| `printer-files/queue/` gcode | Job completed + 7 days | `djinn-confirm-print` marks done, weekly cron clears |
| `Obsidian/djinn/logs/reports/` | Never — logs are permanent | Archive to `OLD/` if Obsidian gets slow |
| `OLD/` in vault | Anytime — no active use | Manual review quarterly |

---

## Adding a New Asset Type

Before storing a new binary type, ask:
1. Does any agent need to know this exists? → Write a `.md` record in the vault
2. Does any agent need to process the binary? → Put it in the right Tier 1 directory
3. Is this temporary work or permanent? → Tier 1 vs Tier 2

If the answer to all three is "no" — it probably doesn't need to be in Djinn at all.

---

*— Claude | 2026-05-31*

---
title: Project — Storage Unification
agent: Claude
date: 2026-07-07
tags: [djinn, project, storage, infrastructure, typhon, library]
status: DEAD — the "Oroborus" storage node named in this plan is a failing drive, do not build the reorg on it
---

# Project: Storage Unification

**2026-07-18 update:** Hardware has been connected and reachable this whole time (confirmed live again this session, IP now `192.168.1.154`, consistent with Phase 1). Code repos got migrated here 2026-07-09 (separate from this plan — see `djinn/logs/reports/2026-07-09_alexandria-setup-storage-migration-cleanup.md`), but the actual `library/archive/review/index` reorg below (Phase 2 onward) was never done. `/mnt/storage` still holds unsorted leftover structure from the drive's prior life as a Windows backup disk. See `djinn/machines/Oroborus.md` for current state. Not resuming this without Javier confirming what on the drive is safe to move/reorganize — flagging the stall, not restarting the project unilaterally.

**2026-07-23 update — this plan is dead, not just stalled.** The drive this whole project was designed around (`/mnt/storage`, the 4.5TB disk, machine IP `192.168.1.154`) turned out to be failing hardware — 4,442 unrecovered read errors spanning nearly its whole used capacity, discovered mid-transfer while trying to move `Library` off it. Everything plausibly real on that drive has been rescued to the Alexandria SSD instead (`Alexandria/archive/oroborus-*-rescue/`, `Alexandria/library-rescue/` — see `djinn/logs/reports/2026-07-23_oroborus-full-standup-and-storage-drive-rescue.md` for full detail). **Do not build the planned `library/archive/review/index` structure on this drive.** If storage unification happens at all going forward, it needs different (working) hardware — this plan's target disk is done.

## Goal

One clean storage hierarchy across the full fleet. Cold storage and live working files properly separated. Typhon has clear instructions to get itself to the right state. No more scattered files across machines.

---

## Machine

**Oroborus** — Linux, 2TB SSD, IP `192.168.1.154` (confirmed live 2026-07-07). Already on LAN.

---

## Session Plan (in order)

### Phase 1 — Connect & Inventory
1. Hook up storage node to LAN
2. Claude SSHes in, confirms connectivity
3. Name the machine (Mnemosyne candidate — confirm on arrival)
4. Full inventory of every machine:
   - Typhon `C:\Forge\` — full tree
   - Salomon `~/printer-files/`, `~/Desktop/`, any stray model files
   - Orion — what's on the 2TB iMac drive vs what's model/print related
   - Any other locations files have accumulated

### Phase 2 — Copy Everything to Storage Node
- All model library files → storage node canonical location
- All completed commission files → cold archive
- All reference STLs → cold archive
- Piece reports, print history → organized by machine/date

### Phase 3 — Separate & Organize
Clean break structure on the storage node:

```
/storage/
├── library/          ← canonical model library (all STLs, 3MFs, sources)
│   ├── commissions/
│   ├── personal/
│   ├── tools/
│   └── reference/
├── archive/          ← completed jobs, cold storage, never-touch
│   ├── commissions/
│   └── prints/
├── review/           ← intake staging (copied from Typhon's C:\Forge\models\review)
└── index/            ← vault-committed index files, trees, manifests
```

### Phase 4 — Wire Up Fleet
- Set up SMB share on storage node
- Map from Typhon as `Z:\` (`\\<storage-node-ip>\storage`)
- Salomon mounts same share
- Update `printers.env` and any path references across Djinn tools

### Phase 5 — Library Index
- Generate `library-index.md` (full tree of `/storage/library/`) 
- Commit to vault at `djinn/printer/model-library-index.md`
- Write a refresh script on storage node that regenerates and commits the index on demand
- From that point: Javier can ask Claude to pull any file by name, Claude reads the index and knows exactly where it is

### Phase 6 — Typhon Instructions
Write a step-by-step handoff doc for Typhon:
- What's on Z:\ and how it's organized
- Where to put new files after a commission
- Where to stage files for review
- How to trigger an index refresh
- Slicer output paths (OrcaSlicer, Bambu Studio, Creality Print) all pointed at Z:\

---

## What This Fixes

| Problem | Fix |
|---|---|
| Model library split across Salomon + Typhon | Single canonical copy on storage node |
| No way to reference files from Claude | Vault-committed index, refreshable on demand |
| Typhon cold files taking local SSD space | Cold files stay on storage node, Typhon hot-syncs only active jobs |
| No inventory of what exists | Full tree in vault after Phase 5 |
| Typhon doesn't know where things go | Phase 6 handoff doc |

---

## Notes

- Don't start until storage node is physically connected and Claude can SSH in
- Javier reviews Phase 3 structure before Phase 4 begins — don't wire up until layout is confirmed
- Orion's 2TB drive (iMac) is separate — not the storage node, not part of this project unless Javier says otherwise

---

*— Claude, 2026-07-07*

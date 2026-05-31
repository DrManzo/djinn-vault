---
title: Marcus Research Archive
tags: [djinn, marcus, research]
updated: 2026-05-31
---

# Marcus Research Archive

All Perplexity (Marcus) research outputs live here. One file per task.

**Naming:** `TASK-NNN_slug.md`
**Index:** listed below — update when a new file is added

---

## How the workflow runs

Marcus has access to the GitHub vault repo (`github.com/DrManzo/djinn-vault`) and optionally Google Drive.

**Primary path — GitHub direct:**
1. Claude writes research brief → QUEUE.md as TASK-NNN, pushes to GitHub
2. Javier triggers Marcus (Perplexity) and points him at the QUEUE.md task or the specific brief
3. Marcus reads the brief from GitHub, runs the research
4. Marcus writes output directly to `djinn/research/marcus/TASK-NNN_slug.md` in the repo and commits
5. Salomon pulls on next vault sync (`git pull`)
6. Claude reads the file on demand via Read tool — never in chat

**Fallback path — Google Drive:**
1. Same brief trigger
2. Marcus writes output to `gdrive:Typhons-Forge/research/marcus/TASK-NNN_slug.md`
3. Salomon rclone-syncs it into vault
4. Claude reads on demand

**What Marcus should NOT touch in the repo:**
- `communications/` — COMMS, QUEUE, HEARTBEAT (operational, Claude/Salomon owned)
- `logs/` — build-log, decision-log, reports (append-only by agents)
- Anything outside `research/marcus/`

Marcus writes only to `djinn/research/marcus/`. Everything else is read-only for him.

---

## Index

| Task | File | Topic | Status |
|------|------|-------|--------|
| TASK-012 | [TASK-012_djinn-media-social.md](TASK-012_djinn-media-social.md) | Djinn Media — social integrations, platform specs, trend APIs, cannabis policy | pending |

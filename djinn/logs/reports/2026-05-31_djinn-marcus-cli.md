---
title: Session Report — djinn-marcus Perplexity CLI
agent: Claude
date: 2026-05-31
tags: [djinn, report, marcus, perplexity, cli]
related: [[build-log]] | [[decision-log]] | [[QUEUE]]
---

# Session Report — djinn-marcus Perplexity CLI

**Date:** 2026-05-31
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier: "the perplexity as a cli or something similar to claude or opencode"

---

## Summary

Built `djinn-marcus` — a Perplexity CLI research agent fully integrated with the Djinn vault. Checked GitHub for existing community tools (found several thin wrappers, none with vault/thread/git integration). Built from scratch in Python. Marcus reads his own MARCUS-SESSION-BRIEF.md as system prompt, maintains topic threads as vault subdirectories, auto-commits research output after every query.

---

## What Was Built or Changed

- **`~/.local/bin/djinn-marcus`** — new CLI, executable
- **`~/.config/djinn/perplexity.env`** — key template (chmod 600, key placeholder)

---

## Technical Decisions

**sonar-pro as default (not sonar-deep-research)** — deep research is slow and expensive per query. sonar-pro has strong citations for daily use. Deep available via `djinn-marcus deep` or `--model` flag.

**Topic threads as subdirectories** — `marcus/<slug>/CONTEXT.md` + dated query files. Matches how Perplexity Pro organizes "Spaces" / threads. Rolling context kept to last 8 exchanges to prevent prompt bloat.

**MARCUS-SESSION-BRIEF.md as system prompt** — Marcus already has an identity file in the vault. Injecting it gives consistent persona without hardcoding anything in the script.

**No official Perplexity CLI exists** — all GitHub tools are thin wrappers (~100 lines, no persistence). Confirmed by web search before building.

---

## Files Created or Modified

```
~/.local/bin/djinn-marcus                  new — Perplexity CLI research agent
~/.config/djinn/perplexity.env             new — key template (chmod 600)
```

---

## Dependencies Installed

None — stdlib only (urllib, json, re, subprocess, pathlib).

---

## Tests & Validation

- `djinn-marcus --help` → renders correctly
- `djinn-marcus topics` → correctly reads vault subdirectories (existing flat files not misread as topics)
- Key-missing path → clean error with setup instructions
- Commands: ask, research, repl, deep, topics, read, tasks — all wired

---

## Known Issues / Caveats

- API key not yet filled in `~/.config/djinn/perplexity.env` — tool will exit with setup instructions until Javier fills it
- `djinn-marcus tasks` parses QUEUE.md by line-level Marcus mention — works but fragile if QUEUE format changes significantly

---

## What's Next

- [ ] Fill `PERPLEXITY_API_KEY` in `~/.config/djinn/perplexity.env` — @Javier
- [ ] Test live query: `djinn-marcus ask "test"` — @Javier
- [ ] Wire Rabbit R1 as mobile Telegram terminal — TASK-023 @Claude
- [ ] Fix gdrive-backup-manifest rotation — TASK-026 @Claude

---

*— Claude, 2026-05-31*

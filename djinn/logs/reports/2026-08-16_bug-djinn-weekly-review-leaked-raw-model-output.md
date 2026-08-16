---
title: Session Report — djinn-weekly leaked raw deepseek-r1 reasoning + terminal control codes into vault
agent: Claude
date: 2026-08-16
tags: [djinn, report, bug, weekly-review]
related: [[build-log]] | [[decision-log]]
---

# Session Report — djinn-weekly Generator Corrupted W31/W32

**Date:** 2026-08-16
**Agent:** Claude
**Session type:** Debug
**Trigger:** Routine vault catch-up read surfaced garbled content in `djinn/weekly/2026-W31.md` and `2026-W32.md`.

---

## Summary

`~/.local/bin/djinn-weekly` generates weekly summaries by shelling out to `ollama run deepseek-r1:7b` and filtering the output with `grep -v "^<think>"`. That filter assumes the model's reasoning is cleanly wrapped in `<think>` tags on their own lines. In practice, `ollama run` renders a live "Thinking..." animation to the TTY using carriage-return/cursor-erase control sequences, and deepseek-r1 sometimes reasons in Chinese even for English prompts. Neither the raw reasoning prose nor the control codes matched the grep filter, so both were committed straight into the vault — both `2026-W31.md` and `2026-W32.md` were affected. The fabricated narrative also invented activity (e.g. "isotropic scaling," "ChromaDB," a GitHub repo cleanup "this week") that was actually from older, unrelated decision-log entries the prompt had included as background context — the model wasn't distinguishing "this week's work" from "context I was given."

---

## What Was Built or Changed

- Rewrote the generation step in `djinn-weekly` to call Ollama's `/api/generate` HTTP endpoint directly with `"think": false, "stream": false` instead of shelling out to the interactive `ollama run` TTY command. This returns clean JSON with no reasoning leakage and no terminal control codes, by construction.
- Kept a defensive `sed`/`perl` strip for stray ANSI codes and `<think>` blocks in case a future model doesn't honor `think:false`.
- Replaced the corrupted content in `djinn/weekly/2026-W31.md` and `2026-W32.md` by hand, using the same underlying data (filtered git log, decision-log) the generator itself pulls — both weeks had essentially no real activity to report.

---

## Technical Decisions

**Call `/api/generate` instead of `ollama run` — Why:** `ollama run` is designed for interactive terminal use and renders its thinking indicator with raw cursor-control escape sequences; there's no reliable way to strip that after the fact for a hybrid-reasoning model that doesn't always tag its thinking consistently. The HTTP API's `think` parameter suppresses reasoning output at the source, and JSON has no TTY rendering to leak in the first place.

---

## Files Created or Modified

```
~/.local/bin/djinn-weekly                  ← generation step now uses /api/generate + think:false
djinn/weekly/2026-W31.md                   ← corrupted summary replaced with accurate one
djinn/weekly/2026-W32.md                   ← corrupted summary replaced with accurate one
```

---

## Tests & Validation

Ran the new curl+jq pipeline standalone against `deepseek-r1:7b` with a throwaway prompt — returned a single clean sentence, no thinking prose, no control codes. Did not run the full `djinn-weekly` script end-to-end (would trigger a real commit/push/Telegram send outside the normal weekly cadence).

---

## Known Issues / Caveats

Full end-to-end run of `djinn-weekly` (including the git push and Telegram digest steps) hasn't been verified since the fix — only the generation step was tested in isolation. Worth a spot-check on the next natural weekly run (should fire automatically at week's end).

---

## What's Next

- [ ] Confirm the next natural `djinn-weekly` run (week close) produces a clean file — @Claude or passive observation.

---

*— Claude, 2026-08-16*

---
title: Session Report — Pyraxis TTS Reader
agent: Claude
date: 2026-06-27
tags: [djinn, report, pyraxis, tts, writing-tools]
related: [[build-log]] | [[project_djinn]] | [[dominion-of-pyraxis]]
---

# Session Report — Pyraxis TTS Reader (djinn-pyraxis-listen)

**Date:** 2026-06-27
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier asked to build a text-to-speech tool to listen to the Dominion of Pyraxis chapters rather than read them.

---

## Summary

Read and fully absorbed all current Pyraxis files (Prologue, Ch 1–3, Characters, Quick Reference, Story So Far, PROJECT.md). Built `djinn-pyraxis-listen` — a CLI tool that reads any chapter or lore file aloud using Microsoft Edge TTS (online, high quality). Strips markdown/frontmatter/draft notes before speaking so only clean prose reaches the listener. Default voice is `en-US-GuyNeural` (Passion), rated for Novel narration.

---

## What Was Built or Changed

- `~/.local/bin/djinn-pyraxis-listen` — new CLI tool; interactive chapter picker or direct invocation
- Reads: Prologue, Ch 1 (Javelin), Ch 2 (Gala/Raxz), Ch 3 (Brax), Quick Reference lore, Story So Far
- Strips: YAML frontmatter, HTML comments (draft notes), markdown syntax, tables, code blocks
- Audio: edge-tts → temp .mp3 → ffplay (already installed); no permanent files
- Voice default: `en-US-GuyNeural`; configurable with `--voice`
- `--list-voices` flag shows curated options for the dark fantasy tone

---

## Technical Decisions

**edge-tts over piper** — Piper (already installed) has only two EN voices (en-GB-alba-medium, en-GB-southern_english_female-medium), both female British. edge-tts gives access to 30+ EN voices including male "Novel/Passion" voices suited to dark fantasy narration. Requires internet, but quality is substantially higher.

**en-US-GuyNeural as default** — Listed by Microsoft as "Passion" for "News, Novel" use. Warmer and more expressive than ChristopherNeural (Authority) which leans formal/cold. Javier can swap to Christopher for Arctus chapters if the coldness fits better.

**ffplay for audio** — Already on the system. Simpler than installing mpg123 or VLC. `-nodisp -autoexit` flags give clean headless playback.

**Ctrl+C to skip** — When reading `all`, Ctrl+C skips the current chapter rather than killing the whole session. Felt right for how listening actually works.

**Temp file then play** — edge-tts streaming directly to audio was less reliable than save-then-play. Temp .mp3 is deleted immediately after playback.

---

## Files Created or Modified

```
~/.local/bin/djinn-pyraxis-listen          ← new CLI TTS reader
```

---

## Dependencies Installed

| Package | Method | Purpose |
|---------|--------|---------|
| edge-tts 7.2.8 | pip3 install --user | Microsoft Edge TTS (online) — voice synthesis |

ffplay was already present via ffmpeg.

---

## Tests & Validation

- `--list-voices` → correct output, 5 curated voices displayed
- Markdown strip test → Prologue: frontmatter gone, draft notes gone, clean prose only; ends on correct final line ("...or they want the throne itself.")
- Audio generation test: `en-US-GuyNeural` on 2-sentence sample → 40,320 bytes MP3 generated, no errors
- Full pipeline confirmed working end-to-end

---

## Known Issues / Caveats

- **Requires internet** — edge-tts calls Microsoft's servers. No offline fallback. If offline, piper is the fallback (run `piper --model ~/.local/share/piper/en_GB-alba-medium.onnx --output_file out.wav < text.txt`).
- **No pause/resume** — ffplay has no pause key in headless mode. Ctrl+C to kill, restart from the same chapter.
- **Long chapters** — Ch 2 (Gala) is the longest chapter. Full TTS generation takes ~10–15 seconds before playback begins.
- **`lore` chapter** — Quick Reference includes tables; table rows are stripped so the lore becomes prose-only. Works fine but loses the visual hierarchy.

---

## What's Next

- [ ] Marcus to write user manual for `djinn-pyraxis-listen` — @Marcus
- [ ] Consider adding chapter-resume (save position to ~/.pyraxis-listen-state) — @Claude when Javier requests
- [ ] Test `--voice en-US-ChristopherNeural` for Arctus/Brax chapters — @Javier
- [ ] Add Chapter 4 to the reader once drafted — @Claude

---

*— Claude, 2026-06-27*

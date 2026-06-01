---
date: 2026-06-01
task: TASK-023
title: Rabbit R1 Telegram Terminal
status: done
---

# TASK-023 — Rabbit R1 Telegram Terminal

## Summary
Wired the Rabbit R1 as a mobile Telegram terminal for Djinn commands. Added incoming voice message transcription and R1 mode (compact text + auto-voice) to djinn-telegram-gateway.

## What Was Built/Changed

**djinn-telegram-gateway** — three additions:

1. **Incoming voice transcription** — gateway now handles `voice` message type. Downloads OGG from Telegram, sends to Groq Whisper (`whisper-large-v3-turbo`) for transcription, dispatches transcript as a command. Reply prefixed with `🎙 [transcript]` so Javier sees what was heard. Voice reply auto-sends if VOICE_MODE is on.

2. **R1 mode (`/r1`)** — single command activates: compact text (no markdown, 150-word cap, plain sentences injected into system prompt), auto-voice on. Persists for session. `/r1 off` reverts both.

3. **`COMPACT_MODE` flag** — `ask_model()` respects this: injects "no markdown, plain sentences, under 150 words" into system prompt and caps max_tokens at 400.

## Technical Decisions

- Groq Whisper chosen over local Whisper: same API key already in use, `whisper-large-v3-turbo` is the fastest Groq model (~0.3s/minute of audio), no GPU required on Salomon.
- Voice handling placed before the `if not text: continue` guard — voice messages have no `text` field so they were silently dropped before.
- R1 mode sets both VOICE_MODE and COMPACT_MODE simultaneously — no need for two commands.
- Compact mode limit: 150 words / 400 tokens. R1 screen is ~2.5" — short replies render fully without scrolling.

## Files Created/Modified

- `~/.local/bin/djinn-telegram-gateway` — modified

## Tests & Validation

- Syntax: `python3 -c "import ast; ast.parse(...)"` → OK
- Logic: voice path → transcribe → dispatch → reply with transcript prefix
- R1 toggle: /r1 on sets all three flags; /r1 off clears all three

## Known Issues

- R1 needs Telegram installed (sideloaded via ADB if not present). Gateway works with any Telegram client from an authorized user ID.
- VOICE_MODE and COMPACT_MODE are in-memory only — reset on gateway restart. Javier must `/r1` again after restart.

## What's Next

- TASK-029 (djinn-marcus-sync) still pending — Selenium/Firefox Perplexity scraper

— Claude

---
subject: cs/CLI-tools/djinn-pyraxis-listen
tags:
  - cs/cli-tools/documentation/user-manual
created: 2026-06-29T18:00:51.318Z
source: Perplexity export

---

# djinn-pyraxis-listen User Manual

## Overview
This tool reads chapters of "The Dominion of Pyraxis" aloud using text-to-speech, making it easier for the author to review and revise their work.

## Quick Start
- `djinn-pyraxis-listen prologue` — Listen to the first chapter.
- `djinn-pyraxis-listen ch1` — Listen to Chapter 1 from a Javelin POV.
- `djinn-pyraxis-listen all` — Full reading order from the prologue to Chapter 3.

## Full Command Reference
| Command | Description |
| --- | --- |
| `djinn-pyraxis-listen` | Interactive chapter picker. |
| `djinn-pyraxis-listen <chapter>` | Listen to a specific chapter (e.g., `prologue`, `ch1`). |
| `djinn-pyraxis-listen lore` | Quick Reference Guide. |
| `djinn-pyraxis-listen story` | The Story So Far. |
| `djinn-pyraxis-listen all` | Full reading order from the prologue to Chapter 3. |
| `djinn-pyraxis-listen --voice VOICE <chapter>` | Override voice (e.g., `--voice en-US-ChristopherNeural prologue`). |
| `djinn-pyraxis-listen --list-voices` | Show curated voice options. |

## Voice Guide
- **en-US-GuyNeural** — Dark fantasy narration, default.
- **en-US-ChristopherNeural** — Imperial/formal, good for Arctus chapters.
- **en-US-EricNeural** — Cold/analytical, suitable for Brax.
- **en-US-AriaNeural** — Female narrator option.

## Tips & Workflow
Use this tool to listen to your work while writing. Note down any revisions or ideas that come up during the listening process and revise accordingly.

## Troubleshooting
- **Offline Fallback**: If internet is unavailable, use `piper` with en_GB-alba-medium.onnx.
- **Long Pauses**: Long chapters may have a delay before audio starts due to TTS generation time.
- **No Audio**: Ensure `ffplay` and `edge-tts` are installed.

## Requirements
- Internet connection (calls Microsoft TTS servers).
- `ffplay` installed (already present via ffmpeg).
- `edge-tts` Python package (pip3 --user, already installed).

---

## References
- [GitHub](https://github.com/DrManzo/djinn-vault)

## Related
- [[Dominion-of-Pyraxis]] — Workspace for "The Dominion of Pyraxis"
- [[djinn-pyraxis-listen]] — CLI tool documentation

---
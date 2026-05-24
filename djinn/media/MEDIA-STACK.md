---
title: Djinn Media Stack
tags: [djinn, media, instagram, agents, social]
created: 2026-05-24
updated: 2026-05-24
---

# Djinn Media Stack — Instagram Production Suite

9-agent pipeline for photo and video post-production targeting Instagram.

**Related:** [[SYSTEM-STATE]] | [[ROUTING]] | [[AGENTS]]

---

## Architecture

```
Raw Media (photo / video / audio)
        ↓
  djinn-media-ingest          ← creates project, writes manifest
        ↓
  ┌─────┴──────┐
  │            │
photo      video/audio
  │            │
photo-edit  video-edit       ← color grade, crop, export 9:16 Reel
  │            │
  │        caption-agent     ← faster-whisper transcription + SRT burn
  │            │
  │       repurpose-agent    ← slice long-form → 3–10 Reel clips (>3min)
  └─────┬──────┘
        ↓
  thumbnail-agent            ← llama3.2-vision frame scoring + compositing
        ↓
  qa-agent                   ← spec checks (resolution, codec, duration, size)
        ↓
  publish-prep-agent         ← phi4:14b → caption, hashtags, alt text, checklist
```

---

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `content-orchestrator` | qwen2.5:7b | Routes jobs to specialist agents |
| `ingest-agent` | qwen2.5:7b | Creates project structure + manifest |
| `video-edit-agent` | qwen2.5:7b | ffmpeg Reel export, color grading |
| `photo-edit-agent` | qwen2.5:7b | ImageMagick + Pillow photo editing |
| `caption-agent` | qwen2.5:7b | faster-whisper STT → SRT → burn |
| `repurpose-agent` | qwen2.5:7b | Long-form → Reel clips |
| `thumbnail-agent` | qwen2.5:7b | Frame scoring + cover compositing |
| `publish-prep-agent` | phi4:14b | Instagram captions, hashtags, checklist |
| `qa-agent` | qwen2.5:7b | Platform spec QC gate |

Vision: `llama3.2-vision:11b` called via REST from photo-edit + thumbnail agents.

---

## CLI Tools

All at `~/.local/bin/` — pre-approved for all OpenClaw agents.

| Command | Purpose |
|---------|---------|
| `djinn-media-ingest <path>` | Create project from file or folder |
| `djinn-media-photo <id> [--style forge\|clean\|dark\|bright]` | Edit photos → feed + story exports |
| `djinn-media-reel <id> [--style forge\|clean\|moody] [--duration 90]` | Export 9:16 Reel |
| `djinn-media-caption <id> [--model medium\|large-v3] [--burn]` | Transcribe + burn captions |
| `djinn-media-repurpose <id> [--clips 5]` | Slice into Reel clips |
| `djinn-media-thumbnail <id> [--text "title"] [--style bold\|band]` | Generate thumbnails |
| `djinn-media-qa <id>` | Platform compliance check |
| `djinn-media-publish-prep <id> [--notes "context"]` | Caption + hashtag package |

---

## Color Grade Presets

| Preset | Description |
|--------|-------------|
| `forge` | High contrast, warm shadows, desaturated mids — dark cinematic |
| `clean` | Neutral, lifted shadows, natural color |
| `moody` | Crushed blacks, teal shadows, warm highlights |
| `dark` | Low-key, rich blacks, desaturated |
| `bright` | Airy, high-key, lifted midtones |
| `raw` | Resize/crop only — no color changes |

---

## Project Structure

```
~/Obsidian/djinn/media/posts/<project_id>/
├── manifest.json
├── raw/                ← originals, never modified
├── selects/
├── edits/
├── exports/
│   ├── feed/           ← 1080×1080, 1080×1350 JPEG
│   ├── reel/           ← 1080×1920 H.264 ≤90s
│   ├── story/          ← 1080×1920
│   └── thumbnail/      ← 1280×720, 1080×1080, 1080×1920
├── captions/           ← SRT + transcript.txt
└── publish/
    ├── manifest.json
    ├── qa_report.md
    ├── instagram_post.md   ← feed caption, reel caption, story text, alt text
    └── clips_manifest.json (if repurposed)
```

---

## Instagram Specs

| Format | Resolution | Max Size | Codec | Notes |
|--------|-----------|----------|-------|-------|
| Feed photo | 1080×1080 (1:1) or 1080×1350 (4:5) | 8MB | JPEG | Strip EXIF |
| Reel | 1080×1920 (9:16) | 3.6GB | H.264+AAC | ≤90s |
| Story | 1080×1920 (9:16) | 4GB video | H.264+AAC | ≤60s |
| Thumbnail | 1280×720 min | 8MB | JPEG Q≥85 | |

---

## Dependencies

- `ffmpeg` — video (installed)
- `convert` (ImageMagick 7.1.2) — photo editing (installed)
- `python3` + `Pillow` — image processing (installed)
- `faster-whisper` — audio transcription (installed via pyenv 3.11)
- `llama3.2-vision:11b-instruct-q4_K_M` — frame analysis (Ollama, loaded on demand)
- `phi4:14b` — caption writing (Ollama, loaded on demand)

---

## Telegram / Discord Triggers

From `@DjinnOCBot` or Discord:
- `media <path>` — ingest
- `photo <project_id>` — edit photos
- `reel <project_id>` — export Reel
- `caption <project_id>` — transcribe + captions
- `repurpose <project_id>` — slice into clips
- `thumbnail <project_id> [text]` — generate covers
- `qa <project_id>` — quality check
- `publish <project_id>` — generate posting package
- `media full <path>` — run entire pipeline end-to-end
- `media status` — list all projects

---

*— Claude, 2026-05-24*

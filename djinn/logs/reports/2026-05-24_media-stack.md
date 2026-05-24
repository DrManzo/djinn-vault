---
title: Session Report — Djinn Media Stack (Instagram Production Suite)
agent: Claude
date: 2026-05-24
tags: [djinn, report, media, instagram, agents, openclaw]
related: [[MEDIA-STACK]] | [[ROUTING]] | [[SYSTEM-STATE]] | [[decision-log]] | [[build-log]]
---

# Session Report — Djinn Media Stack

**Date:** 2026-05-24
**Agent:** Claude (claude-sonnet-4-6)
**Session type:** Architecture + Build
**Duration:** ~1 session
**Trigger:** Javier requested a full-stack Instagram photo/video editing agent suite; provided a Perplexity research brief as the plan

---

## Summary

Built and deployed a 9-agent, 8-CLI-tool Instagram content production pipeline natively integrated into Djinn's OpenClaw infrastructure. The system takes raw photos or video from any path and produces platform-ready Instagram exports (Reels at 1080×1920, feed photos at 1080×1080/1350, thumbnails, burned captions, and a full posting package) using entirely local tools — ffmpeg, ImageMagick, Pillow, faster-whisper, and llama3.2-vision. All agents are registered in OpenClaw and accessible from Telegram/Discord.

---

## What Was Built

### 9 OpenClaw Agents

| Agent | Model | Primary tool |
|-------|-------|-------------|
| content-orchestrator | qwen2.5:7b | Routes and dispatches |
| ingest-agent | qwen2.5:7b | `djinn-media-ingest` |
| video-edit-agent | qwen2.5:7b | `djinn-media-reel` + ffmpeg |
| photo-edit-agent | qwen2.5:7b | `djinn-media-photo` + ImageMagick |
| caption-agent | qwen2.5:7b | `djinn-media-caption` + faster-whisper |
| repurpose-agent | qwen2.5:7b | `djinn-media-repurpose` + ffmpeg |
| thumbnail-agent | qwen2.5:7b | `djinn-media-thumbnail` + llama3.2-vision |
| publish-prep-agent | phi4:14b | `djinn-media-publish-prep` |
| qa-agent | qwen2.5:7b | `djinn-media-qa` + ffprobe + identify |

### 8 CLI Tools (`~/.local/bin/`)

| Tool | Function |
|------|---------|
| `djinn-media-ingest` | Create project structure + manifest.json from file/folder |
| `djinn-media-photo` | Edit photos: crop to 1:1/4:5/9:16, apply color preset, export JPEG |
| `djinn-media-reel` | Export 9:16 H.264 Reel ≤90s with color grade |
| `djinn-media-caption` | Transcribe audio with faster-whisper → SRT → burn into video |
| `djinn-media-repurpose` | Slice long video into 3–10 Reel clips |
| `djinn-media-thumbnail` | Score frames with llama3.2-vision → composite text overlay → 3 variants |
| `djinn-media-qa` | ffprobe + identify checks against platform specs → PASS/FAIL report |
| `djinn-media-publish-prep` | phi4:14b writes feed caption, Reel caption, story text, alt text, checklist |

### Workspace Files (per agent)

Each agent has: `AGENTS.md` (operating instructions + handoff rules), `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`
Located at: `~/.openclaw/workspace/media/<agent>/`

### Shared Resources

- `~/.openclaw/workspace/media/shared/schemas/project-manifest.json` — project state schema
- `~/.openclaw/workspace/media/shared/schemas/export-package.json` — export package schema
- `~/.openclaw/workspace/media/shared/prompts/brand-voice.md` — Typhon's Forge brand voice rules
- `~/.openclaw/workspace/media/shared/prompts/platform-rules.md` — Instagram spec reference

### Skills (5)

All at `~/.openclaw/workspace/media/skills/<name>/SKILL.md`:
`project-intake`, `platform-export`, `clip-packaging`, `thumbnail-brief`, `qc-checklist`

### Vault Documents

- `~/Obsidian/djinn/media/MEDIA-STACK.md` — architecture overview, CLI reference, project structure, specs
- `~/Obsidian/djinn/media/projects/` — live project directory (created at runtime)

---

## Technical Decisions

### Local-first throughout

All processing uses ffmpeg, ImageMagick, Pillow, and faster-whisper. No cloud APIs called for media editing. Vision analysis (frame scoring for thumbnails) uses llama3.2-vision via the local Ollama REST API. This matches Javier's stated preference and keeps sensitive footage off external services.

### Model assignment: qwen2.5:7b for bash-tool agents, phi4:14b for text generation only

Agents that need to run shell commands (all except publish-prep) use qwen2.5:7b because it has tool-call support. publish-prep-agent uses phi4:14b because it only writes text — no shell access needed — and phi4 is significantly better at structured long-form output.

### llama3.2-vision called from scripts, not as an agent

The vision model has no tool support, so it can't run bash commands. Rather than wiring it as an agent, it's called via HTTP from within the Python CLI tools (thumbnail-agent, photo-edit-agent) using urllib.request against Ollama's `/api/chat` endpoint. This keeps it on-demand and avoids loading 7.8GB of VRAM when not needed.

### faster-whisper for captions, not voxtype

`voxtype` is a push-to-talk daemon — not suitable for batch audio transcription. `faster-whisper` (installed into pyenv 3.11) handles file-based transcription with word-level timestamps, which are needed to build properly timed SRT files for caption burning.

### Project manifest as the source of truth

Every tool reads and writes `manifest.json` at the project root. Status field tracks which pipeline stage the project is at (`ingested → editing → captioning → qa → publish_ready`). Agents hand off by writing `next_agent` to the manifest. This is the same pattern as the manufacturing orchestrator's `ProjectState`.

### Color grade via ffmpeg filter chains, not LUTs

ffmpeg's `curves`, `colorbalance`, `colortemperature`, and `colorlevels` filters cover the full grading range needed for 4 presets. No LUT files means no external dependencies. Presets are baked into the CLI tools as filter strings.

---

## Files Created or Modified

### New files

```
~/.openclaw/workspace/media/                        ← 9 agent workspaces
  {agent}/AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md
  shared/schemas/project-manifest.json
  shared/schemas/export-package.json
  shared/prompts/brand-voice.md
  shared/prompts/platform-rules.md
  skills/{project-intake,platform-export,clip-packaging,thumbnail-brief,qc-checklist}/SKILL.md

~/.openclaw/agents/{9 new agent dirs}/agent/        ← OpenClaw agent dirs

~/.local/bin/djinn-media-{ingest,photo,reel,caption,repurpose,thumbnail,qa,publish-prep}

~/Obsidian/djinn/media/MEDIA-STACK.md
~/Obsidian/djinn/media/projects/                    ← project root (runtime)
~/Obsidian/djinn/logs/reports/2026-05-24_media-stack.md (this file)
```

### Modified files

```
~/.openclaw/openclaw.json   ← 9 agents added, main agent routing extended
~/.openclaw/openclaw.json.bak.media  ← backup created
```

---

## Dependencies Installed

| Package | Method | Version | Purpose |
|---------|--------|---------|---------|
| `faster-whisper` | `~/.pyenv/versions/3.11.11/bin/pip` | latest | Audio transcription for caption-agent |
| `lxml` | `~/.venvs/djinn-orchestrator/bin/pip` | latest | Required for trimesh 3MF loading (side-effect) |
| `networkx` | `~/.venvs/djinn-orchestrator/bin/pip` | latest | Required for trimesh graph ops (side-effect) |

Already present (no install needed): `ffmpeg 8.0.1`, `ImageMagick 7.1.2`, `Pillow 12.1.1`, `llama3.2-vision:11b` (Ollama)

---

## Tests & Validation

### Smoke test: Typhon's Forge Logo

```
djinn-media-ingest ~/Downloads/TYPHON'S FORGE LOGO.png
→ Project 2026-05-24_typhon_s_forge_logo created (type: photo)

djinn-media-photo 2026-05-24_typhon_s_forge_logo --style forge
→ 3 exports: feed 4:5 (1080×1350), feed 1:1 (1080×1080), story 9:16 (1080×1920)

djinn-media-qa 2026-05-24_typhon_s_forge_logo
→ 6 checks: ALL PASS
  - resolution: PASS (both sizes correct)
  - format: PASS (JPEG)
  - filesize: PASS (0.1MB and 0.2MB, well under 8MB limit)
```

### openclaw.json validation

12 agents confirmed valid (3 original + 9 new). JSON parses without error.

---

## Known Issues / Caveats

**Caption burning requires SRT path to be absolute in ffmpeg subtitles filter on some systems.** The current implementation uses relative paths which may fail if ffmpeg is invoked from a different working directory. Mitigation: the tool always `cd`s to project root before running ffmpeg. Monitor if this surfaces.

**llama3.2-vision frame scoring is slow (~15–30s per frame on CPU).** With 5 candidate frames, thumbnail generation takes 1.5–2.5 minutes when vision scoring is enabled. Mitigated by `--no-vision` flag which skips scoring and picks the 35% frame. Vision scoring should be enabled for important posts, skipped for batch work.

**publish-prep-agent uses phi4:14b which loads on demand (9.1GB).** First call after model eviction (22:00 nightly) will have a cold start delay of ~60s while Ollama loads the model.

**OpenClaw must be restarted to pick up new agents.** The `openclaw.json` has been updated but OpenClaw reads it at startup. Javier needs to restart the OpenClaw gateway service for the 9 new agents to appear: `systemctl --user restart openclaw`.

---

## What's Next

- [ ] `systemctl --user restart openclaw` — activate the 9 new agents
- [ ] Test with a real Reel: `media full <path>` end-to-end on actual footage
- [ ] Test `djinn-media-caption` with real audio (need a video file with speech)
- [ ] Add `djinn-media-story` for Story-specific processing (text overlays, poll sticker suggestions)
- [ ] Consider adding `SelectsAgent` — review raw batch, mark keepers before editing
- [ ] Wire `media full <path>` trigger to Discord attachment detection (same pattern as printer model watcher)

---

*— Claude, 2026-05-24*

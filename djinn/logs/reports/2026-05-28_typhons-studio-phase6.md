# Session Report — 2026-05-28 — Typhon's Studio Phase 6

**Agent:** Claude  
**Machine:** claude → Typhon (192.168.1.113)  
**Tags:** typhons-studio, post-production, whisper, phase6

---

## Summary

Completed Phase 6 of Typhon's Studio: AI post-production. Built `PostProductionAgent` running faster-whisper `base` model on Typhon's GTX 1650 (CUDA float16, 3.4s load), show notes generation via phi4:14b on Salomon, and ffmpeg clip extraction. UI gains a "Post" tab with recording picker, live transcript viewer with clickable timestamps → clip editor, show notes panel (title, summary, key points, chapters, tags), and real-time job progress via WebSocket.

---

## What Was Built / Changed

### Backend — New File
**`/home/tf-tthq/typhons-studio/backend/agents/post_agent.py`**
- `PostProductionAgent` class with async job queue
- `transcribe(file_path, language)` — launches async job, runs faster-whisper `base` in thread pool (CUDA float16 on GTX 1650), VAD filter enabled, returns timestamped segments + full text
- `generate_show_notes(transcript, title, file_path)` — calls phi4:14b on Salomon via aiohttp, structured JSON prompt, extracts: title, summary, key_points, chapters (with timestamps), description, tags
- `extract_clips(file_path, clips)` — ffmpeg libx264/aac per clip, runs parallel in thread pool
- `list_recordings()` — scans `/home/tf-tthq/typhons-studio/recordings/` for .mkv/.mp4/.flv/.mov/.ts with ffprobe duration + size
- Job system: UUID per job, status (pending→running→done/error), progress %, broadcast via WebSocket `post_job_update`
- Output dirs: `/home/tf-tthq/typhons-studio/post/clips/` and `post/notes/`
- Transcript saved as JSON: `{stem}_transcript.json`; show notes: `{stem}_show_notes.json`

### Backend — Updated
**`/home/tf-tthq/typhons-studio/backend/main.py`**
- Imports `PostProductionAgent`, instantiates in lifespan as `post_agent`
- New routes:
  - `GET /api/post/recordings`
  - `POST /api/post/transcribe` — `{"file": "/path/...", "language": "auto"}`
  - `POST /api/post/show-notes` — `{"file": "...", "transcript": "...", "title": "..."}`
  - `POST /api/post/clips` — `{"file": "...", "clips": [{"start":"00:01:00","end":"00:02:30","label":"Intro"}]}`
  - `GET /api/post/jobs`
  - `GET /api/post/jobs/{job_id}`
  - `GET /api/post/status`
- Health endpoint now reports `"phase": 6`
- Startup log updated to "Phase 6"

### Frontend — Updated
**`/home/tf-tthq/typhons-studio/frontend/index.html`**
- Added "Post" tab (between Lighting and Copilot)
- Post tab layout:
  - Recording picker: list from `/api/post/recordings`, shows filename + duration + size
  - Action row: TRANSCRIBE | SHOW NOTES (disabled until transcript ready) | EXTRACT CLIPS (disabled until clips added)
  - Transcript panel: scrollable, each segment shows timestamp + text, click segment → adds 30s clip to clip editor
  - Right panel — Show Notes: title, summary, key points, chapters, tags (each in collapsible card)
  - Right panel — Clip Editor: list of clips with label input + start/end inputs + delete; "+" add button
  - Extracted clips output: shows result per clip (green = success with filename, red = error)
- Post tab badge: shows count of running jobs
- Stream tab: added "→ Post-Produce" button next to last recording path

**`/home/tf-tthq/typhons-studio/frontend/js/app.js`**
- `tabs` array includes `'Post'`
- Post state: `recordings`, `postFile`, `postTranscript`, `postSegments`, `postShowNotes`, `postClips`, `postExtractedClips`, `postTranscribing`, `postGeneratingNotes`, `postExtractingClips`, `postJobs`, `postActiveJobs`
- Functions: `loadRecordings()`, `postSelectFile()`, `startTranscribe()`, `startShowNotes()`, `startExtractClips()`, `addBlankClip()`, `addClipFromSegment()`, `copyTranscript()`, `copyShowNotes()`
- `handlePostJobUpdate(job)` — handles `post_job_update` WebSocket messages, updates state reactively on done/error
- `loadStatus()` now calls `loadRecordings()` on startup
- `_fmtTime(secs)` helper for timestamp formatting

---

## Technical Decisions

1. **faster-whisper `base` model on CUDA** — GTX 1650 Max-Q (4GB VRAM), CUDA 13.2, float16. Load time 3.4s. `base` (74M params) gives excellent quality for podcast audio at high speed. `small` available as upgrade if needed.

2. **VAD filter enabled** — `vad_filter=True, min_silence_duration_ms=500` — skips silence between sentences, produces cleaner segments with accurate timestamps.

3. **Thread pool for whisper** — `ThreadPoolExecutor(max_workers=2)` keeps the asyncio event loop unblocked during transcription (CPU/GPU-bound work).

4. **phi4:14b for show notes** — Salomon's phi4:14b has larger context window than qwen2.5:7b, handles long transcripts better, and produces more structured output. Transcript truncated to 12K chars if longer.

5. **Transcript click-to-clip** — Clicking a transcript segment adds a 30-second clip starting at that timestamp. User adjusts end time in the clip editor. Keeps workflow in the UI.

6. **ffmpeg libx264 + AAC for clips** — CRF 22 / preset fast / 192k audio. Good quality, fast encode, universal playback. Output to `/post/clips/`.

7. **No HF token needed** — Whisper base model downloads successfully without auth (just slower first download). No token required for this use case.

---

## Files Created / Modified

| File | Status |
|------|--------|
| `/home/tf-tthq/typhons-studio/backend/agents/post_agent.py` | Created |
| `/home/tf-tthq/typhons-studio/backend/main.py` | Updated (Phase 6 routes) |
| `/home/tf-tthq/typhons-studio/frontend/index.html` | Updated (Post tab) |
| `/home/tf-tthq/typhons-studio/frontend/js/app.js` | Updated (Post state + functions) |
| `/home/tf-tthq/typhons-studio/post/clips/` | Created (output dir) |
| `/home/tf-tthq/typhons-studio/post/notes/` | Created (output dir) |

---

## Tests & Validation

| Test | Result |
|------|--------|
| `PostProductionAgent` import | ✅ OK |
| Service restart | ✅ `active (running)` |
| `GET /api/health` | ✅ `{"phase": 6, "status": "ok"}` |
| `GET /api/post/status` | ✅ `{"jobs": [], "recordings": 0}` |
| `GET /api/post/recordings` | ✅ `{"recordings": []}` (dir empty, correct) |
| `GET /api/post/jobs` | ✅ `{"jobs": []}` |
| Whisper CUDA model load | ✅ 3.4s, float16 on GTX 1650 |
| faster-whisper import | ✅ OK, CUDA compute types confirmed |

---

## Known Issues

- **First transcription triggers model download** — Whisper `base` model (~150MB) downloads from HuggingFace on first call. Subsequent loads use cache. No HF_TOKEN needed but first call may be slow.
- **Transcription of empty recordings dir** — No actual recordings exist yet to test end-to-end. Full flow will be verified on first real recording.
- **Show notes truncation** — Transcripts >12K chars are truncated. For very long sessions (2+ hours), consider chunked summarization in a future update.

---

## What's Next

- **Guardian Agent** — health watchdog from v1.4 spec (not built)
- **Redis pub/sub** — between agents (currently direct calls)
- **Cloudybay lights** — when ready
- **WHIP end-to-end test** — verify full browser→MediaMTX→OBS pipeline with real device
- **HF_TOKEN** — optional, add to env if Whisper download rate limits become an issue

---

*— Claude*

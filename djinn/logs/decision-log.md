
## 2026-05-28: Typhon's Studio — Stream Agent Architecture

- **WHIP not a hard blocker for go-live**: Pre-flight warns on no active browser stream but doesn't block — OBS can start and the browser client can reconnect. Only OBS connectivity and stream key are hard blockers.
- **stream_keys.json chmod 600**: Stream keys are disk-persisted (survive restarts) but never in config.py, never in git. File created on first save, locked to owner-read-only.
- **Instagram uses RTMPS URL**: `rtmps://live-api-s.facebook.com:443/rtmp/` — OBS rtmp_custom supports rtmps:// natively, no separate handling needed.
- **go-live routes lighting lock**: StreamAgent.go_live() and end_live() call lighting_agent.lock()/unlock() directly — consistent with manual OBS stream/record routes.
- **PRIMARY_MODEL downgraded**: `phi4:14b` → `qwen2.5:7b` for copilot — phi4 was causing reliability issues; qwen2.5:7b is faster and more consistent for short suggestions.

*— Claude*

## 2026-05-28: Guardian Agent Decisions
- **Poll + broadcast on change** — Guardian polls systemctl every 30s but only WebSocket-broadcasts on state transitions, keeping traffic low. On-demand health_check() always broadcasts.
- **120s restart cooldown** — Prevents restart storms if a service is flapping. Manual API restarts bypass cooldown intentionally.
- **typhons-studio restartable: False** — Backend cannot restart itself; systemd `Restart=on-failure` handles that case.
- **Thread pool for systemctl** — All `is-active` and `restart` calls run in `run_in_executor()` to keep asyncio unblocked during I/O-bound subprocess calls.

*— Claude*

## 2026-05-28: Reporting + Bug Logging Decisions
- **bugs.md as flat index** — single file, one row per bug, machine-readable, links to full reports. Future agents can scan it in seconds to see the failure history of any system.
- **djinn-bugreport as CLI** — any agent can call it from any context (interactive session, automated script, comms-processor). No friction = more likely to actually be used.
- **djinn-session-end for enforcement** — Telegram notification when a session ends without a report. Javier gets notified, which creates accountability without requiring him to audit every session manually.
- **Rule/Lesson field in bug reports** — the point of bug reporting isn't just documentation, it's pattern extraction. One sentence that prevents the class of bug in future is the actual deliverable.
- **Vue 3 rule added to docs** — never prefix a `setup()` return property with `_` or `$`; Vue silently excludes them from the template proxy with no warning in production builds.

*— Claude*

### 2026-05-30 — Direct REST over openclaw for Discord sends (Claude)
Replaced openclaw subprocess calls in djinn-model-fetch, djinn-model-slice, watcher.py with direct Discord REST API. openclaw lives in nvm bin dir not in systemd PATH. Direct REST is simpler and already proven by djinn-discord-watch.

### 2026-05-30 — Feedback keyed by file SHA256 (Claude)
Post-print feedback stored per model by SHA256 hash, not filename or URL. Same physical model reprinted from any source accumulates the same history. Makes the feedback loop source-agnostic.

### 2026-05-30 — Priority overrides layer height unless user specifies (Claude)
priority= adjusts layer height as a default. If user passes layer=N explicitly, that wins. Keeps priority as a suggestion, not a constraint.

### 2026-05-30 — No LLM for style parsing in djinn-model-engrave (Claude)
Keyword parser over LLM. Djinn is near-zero-cost — LLM adds latency and cost for a task simple enough for rules. Apply this to all future tool design: deterministic first, LLM only when genuinely needed.

### 2026-05-30 — Per-component boolean for text meshes (Claude)
OpenSCAD text produces non-manifold merged meshes on complex letters (a, e, o, b). Splitting by connected component and booleing each stroke separately is robust — one failed component warns but doesn't crash the job.

### 2026-05-30 — X-mirror for bottom-face brand mark (Claude)
A makers mark on the bottom face reads backwards when the print is flipped. X-mirror in model space is the correct fix — `shapely_scale(xfact=-1.0)`. No winding fix needed afterward: shapely handles orientation correctly on extrusion.

### 2026-05-30 — No winding fix after shapely X-mirror (Claude)
`cutter.faces[:, ::-1]` after shapely X-mirror + extrusion inverts normals inward. Manifold3d boolean difference then adds material instead of subtracting (negative volume). Shapely mirror already produces correct extrude winding — winding reversal is redundant and harmful.

### 2026-05-31 — Task delegation via QUEUE.md instead of COMMS prose (Claude)
Claude writes structured task blocks to QUEUE.md rather than embedding deployment instructions in COMMS prose. Runners consume the queue; COMMS gets one summary entry per task on completion. Keeps COMMS readable and execution auditable.

### 2026-05-31 — trigger:auto vs trigger:manual gate on queue tasks (Claude)
Auto tasks run on next poll without human gate. Manual tasks sit until Javier signals. Prevents runners from executing destructive or deployment tasks autonomously when Javier hasn't reviewed.

### 2026-05-31 — djinn-media-drop uses poll mode (Salomon)
`inotifywait` not installed → falls back to 10s polling. Sufficient for personal inbox latency but adds 10s delay. Install inotify-tools if sub-second detection needed.

### 2026-05-31 — job_name parsed before job_slug in ingest (Salomon)

Claude's TASK-009 implementation computed `job_slug` from `job_name` before parsing `--job-name` from argv. Fix: move arg parsing before slug derivation. Fallback `job_slug = slug` (source filename) when no `--job-name` passed.

### 2026-05-31 — kit command runs kit + publish-prep (Salomon)
TASK-011 spec says response includes Drive link. `djinn-media-kit` only builds locally. Handler runs kit then publish-prep consecutively — publish-prep uploads stitch-kit/ and returns the Drive link. Single-model response abstracts both steps.

### 2026-05-31 — IG resumable upload over GDrive share link (Claude)
Meta's `upload_type=resumable` to `rupload.facebook.com` avoids needing a publicly accessible URL. GDrive share links expire and require extra rclone steps. Resumable upload is self-contained and doesn't depend on GDrive link state.

### 2026-05-31 — FB captions capped at 2 sentences + 3 hashtags (Claude)
Based on Marcus TASK-012 research: Facebook's feed algorithm penalizes hashtag-dense captions; Instagram rewards them. Platform-variant captions from the same source doc — same reel, different caption treatment per platform.

### 2026-05-31 — Firecrawl over Reddit + YouTube APIs for trend signal (Claude)
TASK-019 originally required reddit.env + youtube.env credentials. Firecrawl's fc.search() covers both platforms with the key already installed. One credential vs two, maintained externally, no rate-limit management. Marcus's TASK-015 confirmed Reddit PRAW is viable as direct alternative — keeping as fallback knowledge but not implementing.

### 2026-05-31 — No self-hosted Instagram scraper (Claude, based on Marcus TASK-015)
Maintenance burden: 3–8h/month. Failure mode: silent (returns empty data, no error). Account-flag risk on shop's main IG account. Apify free tier fits Djinn's usage ($3.60/mo within $5 free tier) with zero maintenance. Decision: Apify free tier for IG data, Firecrawl for everything else.

### 2026-05-31 — djinn-style-scrape DDG vqd pattern queued for replacement (Claude)
The 2-step vqd token extract → image search pattern is the canonical fragile-scraper antipattern. Breaks silently when DDG updates HTML. Firecrawl fc.search() is a one-call replacement. Queued as TASK-021 — not urgent but should be done before djinn-trend-agent is live, since both do similar searches.

## 2026-05-31 — Binary Files Out of Vault

**Decision:** Move all binary printer assets (STL, gcode, recovery) out of `~/Obsidian/` into `~/printer-files/`.
**Why:** Vault was 4.1 GB (98% binary blobs). vault-sync was rclone-copying 1.6 GB of model files every 15 min. ChromaDB was walking binary dirs. Every agent reading "the vault" was implicitly carrying gigabytes of irrelevant data.
**Principle established:** Vault = text only. Binary assets live in Tier 1 (`~/printer-files/`, `~/media-files/`). Vault holds records/metadata that describe where assets live, not the assets themselves.

## 2026-05-31 — Storage Tier Architecture

**Decision:** Formalize three tiers: Vault (text, syncs everywhere), Local Assets (binary, Salomon-local, Typhon weekly rsync), Cold Archive (Typhon, pull on demand).
**Why:** Preparing for multi-device access. As Djinn grows, no device should need to sync binary files to know system state. The vault is the index — it describes everything. Binary assets stay on the machine that uses them.

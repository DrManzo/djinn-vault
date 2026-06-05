---
subject: Djinn Operations
tags: [djinn, decisions, log]
created: 2026-05-19
---

# Decision Log

## 2026-05-19: Vault git initialized
- Repo: djinn-vault (private, GitHub)
- Remote: https://github.com/DrManzo/djinn-vault.git

## 2026-05-19: OpenCode configured with Ollama local
- Default model: qwen2.5:7b
- Provider: Ollama (http://localhost:11434/v1)

## 2026-05-19: Three-lane architecture adopted
- Live lane: Ollama qwen2.5:7b
- Dev lane: Claude (Pro subscription)
- Research: Perplexity → vault notes

## 2026-05-20: Claude Lane activated (Phase 5)
- Claude Code CLI installed on Salomon (`~/.local/bin/claude`)
- Claude identity document created: `djinn/Claude.md`
- CLAUDE.md config created at `~/.claude/CLAUDE.md`
- Agent topology updated: opencode (Salomon), opencode (Typhon), Claude (Salomon CLI)
- Signing convention established: `— Salomon`, `— Typhons Forge`, `— Claude`
- Auth: OAuth (Claude Pro) — requires interactive login via `claude` in terminal

## 2026-05-21: Phase 5 Complete — Claude Lane Fully Activated
- Claude.md created at `~/.openclaw/workspace/Claude.md` — defines role, 9-file context protocol, lane boundaries
- AGENTS.md routing table corrected — Role column added, duplicate deepseek row removed, Claude Code architecture row added
- opencode.json updated — temperature settings applied to all 6 models
- Ollama resource caps applied: 60% CPU, 20G RAM, no swap
- Ollama env vars set: MAX_LOADED_MODELS=2, KEEP_ALIVE=5m, GPU_MEMORY_FRACTION=0.80
- djinn-idle.timer active — nightly 22:00 model eviction (deepseek, phi4, coder)
- cpu-governor.service active — powersave enforced on boot (schedutil not available on AMD pstate)
- thermald skipped — Intel-only, AMD pstate handles thermals natively
- Typhon Claude setup: credentials transfer script at `djinn/scripts/typhon-claude-setup.sh`, background watcher running
- openclaw workspace versioned — initial git commit (13 files)
- Handoff package archived: `djinn/communications/djinn-handoff-package.md`

## 2026-05-22: Phase 9 — Printer Node architecture locked

- **Print server**: Creality Nebula pad running Klipper + Moonraker at `192.168.1.113:7125`
- **Decision**: Typhon KIAUH/Klipper install SKIPPED — Nebula pad is already a fully functional Moonraker node, reflashing MCU adds risk with zero benefit
- **Salomon** handles: modeling tools (FreeCAD, Blender, OpenSCAD), AI generation (Hunyuan3D-2), OrcaSlicer slicing, Claude lane work
- **Typhon** handles: Telegram bot daemon (always-on, lightweight, hits Moonraker over LAN)
- **PLR + thermal watchdog**: `plr.cfg` uploaded to Nebula pad — saves Z/layer at each layer change, polls every 5s for temp drops
- **Error logging**: `printer-error-logger.service` running on Salomon — polls Moonraker every 30s, logs to vault
- **idle_timeout**: Changed from 99999999 → 600s on Nebula pad — cat safety, turns off heaters + motors after 10 min idle
- **Printer IP**: Static-lease recommended at 192.168.1.113 — currently DHCP, changed once during this session (.113 → .114)
- **Vault schema**: `djinn/printer/{queue,active,completed,models,config}` active

---

*— Claude*

---

## 2026-05-24 — Six-Agent Manufacturing Stack

**Decision:** Build a modular 6-agent manufacturing pipeline instead of one monolithic print agent.

**Agents:** DesignGenAgent → DesignEditAgent → ProtoOptAgent → DOEPrintOptAgent → PlateNestAgent → FairPrintAgent

**Key choices:**
- Parametric OpenSCAD output (not STL) from DesignGenAgent — dead meshes block downstream editing
- DOEPrintOptAgent uses literature-calibrated prediction models, not test prints — Taguchi factor grid over slicer params (Swansea 2023 baselines)
- phi4:14b as local default brain; Claude API as optional upgrade via `~/.config/djinn/claude.env`
- Shared ProjectState extends existing print-queue.json schema — no separate database
- PlateNestAgent always decimates to <10MB per object before merging (PrusaSlicer >200MB bug)

**Why DOE:** Prototype efficiency optimization is a process/slicer problem, not a geometry problem. Taguchi screening tests multiple factors together and outperforms one-factor-at-a-time when minimizing time+energy+material.

— Claude

---

## 2026-05-24 — 9-Agent Media Stack Architecture

**Decision:** Build a multi-agent Instagram production pipeline with one agent per pipeline stage, not a single monolithic editor agent.

**Agents:** ingest → photo-edit / video-edit → caption → repurpose → thumbnail → qa → publish-prep, orchestrated by content-orchestrator.

**Key choices:**
- All bash-tool agents use qwen2.5:7b (tool support required); publish-prep uses phi4:14b (text quality, no tools needed)
- llama3.2-vision called via HTTP from scripts — not wired as an agent, because it has no tool support and loads 7.8GB on demand
- faster-whisper for caption transcription — voxtype is push-to-talk only, not suitable for batch file processing
- ffmpeg filter chains for color grading — no LUT files, no external dependencies; 4 presets cover the full aesthetic range
- Project manifest.json as shared state — same pattern as manufacturing orchestrator's ProjectState

**Why separate agents:** Each stage has distinct tool dependencies, model needs, and handoff contracts. Separating them makes each agent's workspace instructions lean and unambiguous. Content-orchestrator handles routing without each agent needing to know the full pipeline.

— Claude
- 2026-05-25 — **Creality temp control**: M109 blocked mid-print on Nebula firmware. Use M104 (non-blocking) or native Klipper SET_HEATER_TEMPERATURE instead.
- 2026-05-27 — **machine_limits_usage fix**: PrusaSlicer with `gcode_flavor = klipper` silently fails to emit gcode unless `machine_limits_usage` is set. Added `machine_limits_usage = use_for_slicing` to `~/.config/djinn/ender3-v3-plus.ini`. PrusaSlicer may override this to `time_estimate_only` at load time, which still works.

## 2026-05-27 — Klipper START_PRINT/END_PRINT wired into slicer profile

**Problem:** PrusaSlicer profile had no `start_gcode` or `end_gcode`. Every sliced job got
an inline raw start sequence (G28/M109/M190/purge) that bypassed Calliope's `START_PRINT`
macro entirely — skipping bed leveling, nozzle cleaning, and accurate Z homing.

**Decision:** Set `start_gcode` and `end_gcode` in `~/.config/djinn/ender3-v3-plus.ini`
to call the Klipper macros directly. PrusaSlicer substitutes temperature placeholders.
No per-job post-processing needed.

**Values set:**
```
start_gcode = START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
end_gcode = END_PRINT
```

**Why re-slice, not post-process:** Post-processing a 9.6MB gcode file to splice in
a macro call is fragile — line numbers shift, the inline sequence and the macro both
do homing/heating, risk of double-homing or conflicting temp commands. Re-slicing with
the fixed profile costs 30 seconds and produces a clean, correct file from scratch.

— Claude

## 2026-05-28: manifold3d for boolean CSG — cup engrave
- **Problem:** OrcaSlicer text as separate component on cup surface. trimesh (blender engine), Blender EXACT boolean, and Blender shrinkwrap all failed to produce a clean boolean difference on this geometry — returning empty or degenerated results.
- **Decision:** Use `manifold3d` Python library (3.5.0) for the boolean. Installed in isolated venv at `/tmp/opencode/venv/`.
- **Why:** manifold3d produces watertight, correct boolean output where other engines silently return empty. 0.25 cm³ removed, matches expected text volume. Fast (<5s on 11000-triangle input).
- **Caveat:** Only available in venv, not system Python.
- **Trade-off:** Text is flat (not following cup curvature) → engrave depth varies 2.5mm center / 0.9mm edges. Acceptable for this print.

— Salomon

---
## Merged from logs/decision-log.md (2026-06-04)

























































`cutter.faces[:, ::-1]` after shapely X-mirror + extrusion inverts normals inward. Manifold3d boolean difference then adds material instead of subtracting (negative volume). Shapely mirror already produces correct extrude winding — winding reversal is redundant and harmful.
- **`exec` delegation** — `exec forge "$@"` replaces djinn's shell process; cleaner than subprocess, no extra PID.
`inotifywait` not installed → falls back to 10s polling. Sufficient for personal inbox latency but adds 10s delay. Install inotify-tools if sub-second detection needed.
- **120s restart cooldown** — Prevents restart storms if a service is flapping. Manual API restarts bypass cooldown intentionally.
## 2026-05-28: Guardian Agent Decisions
## 2026-05-28: Reporting + Bug Logging Decisions
## 2026-05-28: Typhon's Studio — Stream Agent Architecture
### 2026-05-30 — Direct REST over openclaw for Discord sends (Claude)
### 2026-05-30 — Feedback keyed by file SHA256 (Claude)
### 2026-05-30 — No LLM for style parsing in djinn-model-engrave (Claude)
### 2026-05-30 — No winding fix after shapely X-mirror (Claude)
### 2026-05-30 — Per-component boolean for text meshes (Claude)
### 2026-05-30 — Priority overrides layer height unless user specifies (Claude)
### 2026-05-30 — X-mirror for bottom-face brand mark (Claude)
## 2026-05-31 — Binary Files Out of Vault
### 2026-05-31 — djinn-media-drop uses poll mode (Salomon)
### 2026-05-31 — djinn-style-scrape DDG vqd pattern queued for replacement (Claude)
### 2026-05-31 — FB captions capped at 2 sentences + 3 hashtags (Claude)
### 2026-05-31 — Firecrawl over Reddit + YouTube APIs for trend signal (Claude)
### 2026-05-31 — IG resumable upload over GDrive share link (Claude)
### 2026-05-31 — job_name parsed before job_slug in ingest (Salomon)
### 2026-05-31 — kit command runs kit + publish-prep (Salomon)
## 2026-05-31 — Marcus = Perplexity CLI, not Gemini
### 2026-05-31 — No self-hosted Instagram scraper (Claude, based on Marcus TASK-015)
## 2026-05-31 — Storage Tier Architecture
### 2026-05-31 — Task delegation via QUEUE.md instead of COMMS prose (Claude)
### 2026-05-31 — trigger:auto vs trigger:manual gate on queue tasks (Claude)
## 2026-06-01 — body.innerText over Gemini for thread extraction
## 2026-06-01 — Build gate: infrastructure + research before any new suite
## 2026-06-01 — Cloudflare Tunnel for Meta video hosting (Claude)
## 2026-06-01 — Morning briefing: open with sobriety day, always
## 2026-06-01 — No interactive TUI for djinn dispatcher
## 2026-06-01 — OpenClaw as hub, `djinn` as workbench
## 2026-06-01 — Phase Alpha: Full personal access granted
## 2026-06-01 — Sabrina archive rule
## 2026-06-01 — Stable pplx_{uuid} filenames for marcus threads
## 2026-06-01: Text Engraving on STL — djinn-model-text-engrave
## 2026-06-02 — Scrap Proxy Stand job 5 engraving (Claude)
## 2026-06-02 — Vector font outlines for FDM text engraving
## 2026-06-03: Phase 5 — Standalone forge/terp CLIs
A makers mark on the bottom face reads backwards when the print is flipped. X-mirror in model space is the correct fix — `shapely_scale(xfact=-1.0)`. No winding fix needed afterward: shapely handles orientation correctly on extrusion.
Auto tasks run on next poll without human gate. Manual tasks sit until Javier signals. Prevents runners from executing destructive or deployment tasks autonomously when Javier hasn't reviewed.
Based on Marcus TASK-012 research: Facebook's feed algorithm penalizes hashtag-dense captions; Instagram rewards them. Platform-variant captions from the same source doc — same reel, different caption treatment per platform.
- **Bash over Python Click** — Forge/Terp CLIs are thin delegates to existing `djinn-*` binaries. No reasoning needed, bash consistent with existing pattern.
- **bugs.md as flat index** — single file, one row per bug, machine-readable, links to full reports. Future agents can scan it in seconds to see the failure history of any system.
*— Claude*
*— Claude*
*— Claude*
*— Claude*
*— Claude, 2026-06-01*
Claude's TASK-009 implementation computed `job_slug` from `job_name` before parsing `--job-name` from argv. Fix: move arg parsing before slug derivation. Fallback `job_slug = slug` (source filename) when no `--job-name` passed.
Claude writes structured task blocks to QUEUE.md rather than embedding deployment instructions in COMMS prose. Runners consume the queue; COMMS gets one summary entry per task on completion. Keeps COMMS readable and execution auditable.
**Decision:** `arc_radius` fallback triggers on `arc_wrap=True`, not `is_cylindrical=True`.
**Decision:** `djinn` is a pure CLI (`djinn <cmd> [args]`), not an interactive menu or fzf picker.
**Decision:** `placement_resolver.py` uses deterministic regex+math, not a second LLM call.
**Decision:** Djinn gets read access to all personal domains except financial. Black Book included — local-only processing only (Ollama, never cloud).
**Decision:** Djinn holds Sabrina context passively. If Javier doesn't mention her in 14 days (without Djinn prompting), she gets quietly archived. One mention restores.
**Decision:** djinn-marcus uses Perplexity API (sonar-pro), not Gemini.
**Decision:** Every morning briefing opens with "Day N sober." regardless of anything else.
**Decision:** Formalize three tiers: Vault (text, syncs everywhere), Local Assets (binary, Salomon-local, Typhon weekly rsync), Cold Archive (Typhon, pull on demand).
**Decision:** marcus/threads/ filenames derived from Perplexity thread UUID in URL, not date+title.
**Decision:** Move all binary printer assets (STL, gcode, recovery) out of `~/Obsidian/` into `~/printer-files/`.
**Decision:** Nothing gets built until (1) Typhon audit + cleanup complete, (2) Marcus research reports for all three suites delivered.
**Decision:** OpenClaw TUI stays for Discord/Telegram presence and simple conversational ops. `djinn` CLI is the interface for task execution, system ops, and anything requiring reliable output.
**Decision:** Replace PIL+skimage raster→contour pipeline with matplotlib TextPath (TTF Bezier curves) for all side-mode text geometry.
**Decision:** Session scrapped after operator confirmed tooling cannot honor visual placement intent.
**Decision:** Use `document.body.innerText` directly for Perplexity thread content, not Gemini API.
**Decision:** Use Cloudflare Tunnel (not ngrok) as the HTTPS hosting layer for Meta video uploads.
- **djinn-bugreport as CLI** — any agent can call it from any context (interactive session, automated script, comms-processor). No friction = more likely to actually be used.
- **djinn-session-end for enforcement** — Telegram notification when a session ends without a report. Javier gets notified, which creates accountability without requiring him to audit every session manually.
- **go-live routes lighting lock**: StreamAgent.go_live() and end_live() call lighting_agent.lock()/unlock() directly — consistent with manual OBS stream/record routes.
**How to apply:** `hosting.py` starts a local HTTP server on 127.0.0.1:8741. CF Tunnel exposes it at `DJINN_MEDIA_BASE_URL`. After Meta fetches the file the local server shuts down.
**How to apply:** All personal layer tools use local Ollama only for sensitive content. Cloud AI (Gemini, Groq) never receives Black Book, habit, sobriety, or relationship data.
**How to apply:** All spatial reasoning in the engraving pipeline after LLM proposals should be deterministic code, not LLM interpretation.
**How to apply:** djinn-morning hardcodes this as line 1. Non-negotiable.
**How to apply:** Do not re-attempt engraving placement without a marker-based bridge workflow (operator drops a cube at desired location → Claude reads XYZ → applies correct FDM parameters).
**How to apply:** If new commands are added, they go in `DISPATCH` dict and in `HELP` string. No interactive modes.
**How to apply:** Passive scan in Telegram gateway. Weekly check Sunday morning. Archive is soft — never delete.
**How to apply:** When building new Djinn capabilities: if the operation is deterministic, add it to `djinn`. If it's conversational, add it to OpenClaw's system prompt. Never add complex spec-reading tasks to the model's system prompt — put a script in the path instead.
- **Instagram uses RTMPS URL**: `rtmps://live-api-s.facebook.com:443/rtmp/` — OBS rtmp_custom supports rtmps:// natively, no separate handling needed.
Keyword parser over LLM. Djinn is near-zero-cost — LLM adds latency and cost for a task simple enough for rules. Apply this to all future tool design: deterministic first, LLM only when genuinely needed.
Maintenance burden: 3–8h/month. Failure mode: silent (returns empty data, no error). Account-flag risk on shop's main IG account. Apify free tier fits Djinn's usage ($3.60/mo within $5 free tier) with zero maintenance. Decision: Apify free tier for IG data, Firecrawl for everything else.
- **manifold3d boolean for text cutters** — Same approach as maker's mark (`djinn-model-mark`). Rejected trimesh-only boolean (unreliable). manifold3d consistently produces correct geometry with occasional non-watertight results (Euler -2 to -3) that PrusaSlicer handles.
Meta's `upload_type=resumable` to `rupload.facebook.com` avoids needing a publicly accessible URL. GDrive share links expire and require extra rclone steps. Resumable upload is self-contained and doesn't depend on GDrive link state.
OpenSCAD text produces non-manifold merged meshes on complex letters (a, e, o, b). Splitting by connected component and booleing each stroke separately is robust — one failed component warns but doesn't crash the job.
**Order:** Typhon TASK-044/045 → Marcus TASK-037/038/039 → Claude architects → Salomon builds.
- **Poll + broadcast on change** — Guardian polls systemctl every 30s but only WebSocket-broadcasts on state transitions, keeping traffic low. On-demand health_check() always broadcasts.
Post-print feedback stored per model by SHA256 hash, not filename or URL. Same physical model reprinted from any source accumulates the same history. Makes the feedback loop source-agnostic.
- **PRIMARY_MODEL downgraded**: `phi4:14b` → `qwen2.5:7b` for copilot — phi4 was causing reliability issues; qwen2.5:7b is faster and more consistent for short suggestions.
**Principle established:** Vault = text only. Binary assets live in Tier 1 (`~/printer-files/`, `~/media-files/`). Vault holds records/metadata that describe where assets live, not the assets themselves.
priority= adjusts layer height as a default. If user passes layer=N explicitly, that wins. Keeps priority as a suggestion, not a constraint.
**Rejected:** Increasing raster resolution, polygon simplification — both treat the symptom not the cause.
Replaced openclaw subprocess calls in djinn-model-fetch, djinn-model-slice, watcher.py with direct Discord REST API. openclaw lives in nvm bin dir not in systemd PATH. Direct REST is simpler and already proven by djinn-discord-watch.
- **Rule/Lesson field in bug reports** — the point of bug reporting isn't just documentation, it's pattern extraction. One sentence that prevents the class of bug in future is the actual deliverable.
- **Separate `terp` binary** — distinct brand identity, independent future command surface. Not merged into `forge`.
- **Side engraving uses per-character placement on an arc** — Each character is individually rendered, rotated to face radially outward, and positioned along a 180° arc on the cylinder wall. Flat label approach rejected (would look wrong on curved surface).
- **stream_keys.json chmod 600**: Stream keys are disk-persisted (survive restarts) but never in config.py, never in git. File created on first save, locked to owner-read-only.
TASK-011 spec says response includes Drive link. `djinn-media-kit` only builds locally. Handler runs kit then publish-prep consecutively — publish-prep uploads stitch-kit/ and returns the Drive link. Single-model response abstracts both steps.
TASK-019 originally required reddit.env + youtube.env credentials. Firecrawl's fc.search() covers both platforms with the key already installed. One credential vs two, maintained externally, no rate-limit management. Marcus's TASK-015 confirmed Reddit PRAW is viable as direct alternative — keeping as fallback knowledge but not implementing.
- **Text engraving is manual, not in slice pipeline** — Unlike maker's mark (auto-applied in `djinn-model-slice`), text engraving requires a separate `djinn-model-text-engrave` call before slicing. Decision: keep it manual until the tool is stable and the UX is proven.
The 2-step vqd token extract → image search pattern is the canonical fragile-scraper antipattern. Breaks silently when DDG updates HTML. Firecrawl fc.search() is a one-call replacement. Queued as TASK-021 — not urgent but should be done before djinn-trend-agent is live, since both do similar searches.
- **Thread pool for systemctl** — All `is-active` and `restart` calls run in `run_in_executor()` to keep asyncio unblocked during I/O-bound subprocess calls.
- **typhons-studio restartable: False** — Backend cannot restart itself; systemd `Restart=on-failure` handles that case.
- **Vue 3 rule added to docs** — never prefix a `setup()` return property with `_` or `$`; Vue silently excludes them from the template proxy with no warning in production builds.
- **WHIP not a hard blocker for go-live**: Pre-flight warns on no active browser stream but doesn't block — OBS can start and the browser client can reconnect. Only OBS connectivity and stream key are hard blockers.
**Why:** 100 threads × hourly scrape = ~$50-70/month on Gemini Flash. Violates near-zero-cost principle. Plain body text is already structured Q&A. `strip_nav_garbage` in clerk handles the chrome. Zero cost wins.
**Why:** Date+title generates a new file every sync day, filling vault with duplicates. UUID is immutable per thread — same URL always maps to same file. Re-scrapes are safe overwrites.
**Why:** Javier is keeping Perplexity Pro. The value prop is live web search + citation threading — exactly what Sonar does. Gemini handles Drive/docs/vision via Google One AI Premium (separate lane). Marcus = research + web. Gemini = docs + vision.
**Why:** Javier is new to sobriety, ADHD, workaholic pattern — needs structure held externally. Giving Djinn context is the precondition for it actually functioning as a conciliary rather than a system status tool.
**Why:** Javier said it explicitly — consistent mention = active context. Silence = fade out. Djinn doesn't force the topic.
**Why:** Meta requires a publicly accessible HTTPS URL to fetch the video during IG container creation. ngrok free tier has session limits and rotating URLs — not viable for automated 7-day/week publishing. CF Tunnel is free, permanent URL, runs as a systemd service.
**Why:** No workflow bridges PrusaSlicer's viewport positioning to `djinn-model-text-engrave`'s coordinate parameters. Operator placed text visually; Claude extracted coordinates but parameters (font size, depth) from PrusaSlicer's own text tool were wrong for FDM legibility. Multiple Z-height iterations failed because tools work in different coordinate spaces and neither side can fully translate operator intent.
**Why:** Placement coordinates must be predictable and zero-latency. A second LLM call adds hallucination surface and latency; regex + wall_profile math is sufficient for all common spatial tokens (lower_third, upper_band, centered, left_align, etc.).
**Why:** Preparing for multi-device access. As Djinn grows, no device should need to sync binary files to know system state. The vault is the index — it describes everything. Binary assets stay on the machine that uses them.
**Why:** Proxy Stand is tapered → `is_cylindrical=False` (outer_r variance >15%), but `arc_wrap` in the spec is the authoritative intent signal. Using `is_cylindrical` as the gate silently produced r=0mm, breaking the arc calculation.
**Why:** Raster contours at FDM scale (6–8mm cap height) produce hundreds of micro-vertices approximating pixel boundaries, not glyph outlines. Slicers read these as abstract shapes. Bezier extraction gives clean closed rings with correct hole topology (counters in O, e, p, b). Volume per character nearly doubled (0.018 → 0.034 cm³) confirming fuller, cleaner geometry.
**Why:** Scriptable, faster, works over SSH, no curses dependency. Muscle memory for one command surface is more durable than navigating a menu. Help screen is always `djinn help`.
**Why:** Sobriety counter is identity, not a metric. It's the ground the day is built on. Opens before everything else — deadlines, streaks, tasks.
**Why:** The 7B model is good at routing and chat formatting. It is not reliable for parsing structured specs and executing multi-step tasks — demonstrated by BUG-014 (hallucinated SQLite tutorial instead of reading TASK-054). Deterministic dispatch is always faster and never hallucinates.
**Why:** Typhon cleanup gives us clean storage infrastructure to build on. Marcus research defines what each suite (Law, Psyc, Cash) actually needs — features, depth, structure. Building without that means guessing and reworking. Research-first is always cheaper than rebuild-after.
**Why:** Vault was 4.1 GB (98% binary blobs). vault-sync was rclone-copying 1.6 GB of model files every 15 min. ChromaDB was walking binary dirs. Every agent reading "the vault" was implicitly carrying gigabytes of irrelevant data.
- **XY-only scaling for opening fix** — 1.45% XY scale chosen over isotropic because Z height (21mm) doesn't need changing. Opening grows from 41.4→42.0mm.

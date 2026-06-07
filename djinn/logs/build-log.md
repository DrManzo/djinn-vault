---
subject: Djinn Operations
tags: [djinn, build-log]
created: 2026-05-19
---

# Build Log

## 2026-05-19: MVP Build Day 1
- OpenCode configured with Ollama local provider
- Vault backed up, git initialized, pushed to GitHub
- vault-sync systemd timer created (15-min GDrive sync)
- vault-passport-backup script created
- Inbox processed (9 notes moved to proper locations)
- djinn/ directories populated with operational notes
- 504 note vault now backed up to GitHub + local tarball

## 2026-06-01: Puffco Proxy Stand (Job 5) — Opening fix + text engraving tool + Z offset
- XY-scaled Proxy Stand 1.45% (opening 41.4→42.0mm)
- Built `djinn-model-text-engrave` — text engraving on STL top/side surfaces using PIL + scikit-image + manifold3d boolean
- Engraved "Typhon's Forge" on side of Proxy Stand near base (1.3mm from bed, 180° front wrap, 4mm font, 0.4mm deep)
- Added +0.1mm Z offset for bed adhesion (SET_GCODE_OFFSET Z=0.1)
- Recorded Printables source URL + designer credit (joshtf)
- Scikit-image installed in djinn-orchestrator venv

## 2026-05-21: MVP Phase 5 Complete — Claude Lane + Hardware Protection
- Salomon: routing config applied (opencode.json temperatures), resource caps active (60% CPU / 20G RAM)
- Salomon: djinn-idle.timer wired — evicts deepseek, phi4, coder at 22:00 nightly
- Salomon: cpu-governor.service active, powersave enforced on boot
- Salomon: AGENTS.md routing corrected, Claude.md identity doc created
- Salomon: openclaw workspace versioned (initial commit, 13 files)
- Typhon: setup script ready (`djinn/scripts/typhon-claude-setup.sh`), pending Typhon coming online
- Claude lane: active on Salomon, Claude.md created, 9-file context protocol established
- Both machines communicating through vault (vault-sync + HEARTBEAT.md)
- Phase 6 (Agents & Skills) ready to begin when Typhon is confirmed

## 2026-05-22: Phase 9 — Printer Node (Ender-3 V3 Plus) — In Progress

- Klipper + Moonraker: already live on Nebula pad (`192.168.1.113:7125`) — no Typhon install needed
- `plr.cfg` uploaded to printer: Power Loss Recovery + thermal watchdog (5s poll, saves Z+layer, pauses on temp drop)
- `printer-error-logger.service` active on Salomon: polls Moonraker every 30s, logs errors + monitor rows to vault
- Printer vault structure live: `djinn/printer/{queue,active,completed,models,config}`
- Print baseline captured: Rose_Decor_fixed.gcode — hotend ±0.32°C, bed ±0.01°C, no anomalies
- idle_timeout: updated to 600s on Nebula pad (was 99999999), cat safety active
- OrcaSlicer: installed (AppImage), Ender-3 V3 Plus profile configured
- FreeCAD + Blender + OpenSCAD: installing (P9-JOB 2)
- Telegram bot: instructions written to COMMS.md for Typhon (P9-JOB 5)
- Hunyuan3D-2: pending pyenv Python 3.11 install (P9-JOB 3)

---

*— Claude*

## 2026-05-28: Infrastructure Reference Document
- Created `INFRASTRUCTURE.md` — full system topology, repos, services, tools, pipelines, comm channels, critical rules
- Designed for AI agent ingestion — any future AI can read this and understand the full Djinn workspace
- Javier granted read-access permission to all 3 GitHub repos within the document
- All 3 remotes verified, 8 services confirmed running, printer READY

*— Salomon*


**Typhon's Forge Challenge Coin (2026-05-23)**
- 38mm × 4.5mm challenge coin designed from PNG logo
- Pipeline: PNG → PBM (ImageMagick) → SVG (potrace) → OpenSCAD parts → trimesh merge
- Final: LOGO_SCALE=0.0448 (20% reduction to stop corner text clipping), text size=3.8
- Key discoveries: OpenSCAD CGAL union() silently fails on 1M-face meshes; SVG center must be measured from rendered STL not SVG header
- Build report: `djinn/printer/library/typhons-forge-coin/COIN_BUILD_REPORT.md`

**FairPrintAgent / djinn-print-quote (2026-05-23)**
- Commission pricing CLI: `(material + time + design) / 0.60`
- Library auto-detect: design cost → $0 if piece name matches library folder
- Market fetch: ddgs DuckDuckGo/Etsy search
- Full agent mode: weighted cost+market blend, 4 job types
- OpenClaw: `quote`, `quick quote` command handlers added

**Print Job #1 — mario pipe + 4 coins (2026-05-24)**
- Combined plate: proxy_parts_mario_pipe + 4× Typhon's Forge coins
- PrusaSlicer silently dropped pipe when combined STL exceeded ~200MB
- Fix: decimate coins to 15k faces with pymeshlab → plate = 3.3MB → sliced correctly
- 3h 20m / 59.8g — started 2026-05-24

**Six-Agent Manufacturing Orchestrator (2026-05-24)**
- Package: `djinn/printer/agent/orchestrator/`
- Agents: DesignGenAgent, DesignEditAgent, ProtoOptAgent, DOEPrintOptAgent, PlateNestAgent (all live)
- CLI: `djinn-design` at `~/.local/bin/djinn-design`
- Venv: `~/.venvs/djinn-orchestrator/` (Python 3.11 — anthropic, pyDOE2, trimesh, pymeshlab, scipy)
- DOE engine verified: -76% time / -51% material for prototype_fast vs standard settings
- OpenClaw: `design`, `design edit`, `design optimize`, `design doe`, `design plate`, `design status` handlers

*— Claude*

## 2026-05-24: Djinn Media Stack — 9-Agent Instagram Production Suite

- 9 OpenClaw agents registered: content-orchestrator, ingest, video-edit, photo-edit, caption, repurpose, thumbnail, publish-prep, qa
- 8 CLI tools at `~/.local/bin/djinn-media-*` (ffmpeg + ImageMagick + Pillow + faster-whisper)
- Shared skills: project-intake, platform-export, clip-packaging, thumbnail-brief, qc-checklist
- Shared schemas: project-manifest.json, export-package.json
- Brand voice + platform rules prompts for Typhon's Forge Instagram
- faster-whisper installed (pyenv 3.11) for audio transcription
- llama3.2-vision called via REST from thumbnail and photo agents (frame scoring)
- openclaw.json updated: 3 → 12 total agents
- Vault doc: `djinn/media/MEDIA-STACK.md`
- Smoke test: logo → ingest → photo edit → QA → 6/6 PASS
- **Report Standard standardized** — PROTOCOL.md, CLAUDE.md, AGENTS.md all updated with mandatory reporting requirement

*— Claude*

## 2026-05-25: FairPrintAgent — Bug Fix + First Live Validation

- First end-to-end test against real print data (Mario Pipe: 44g, 3.33h)
- Full JSON mode: $11.70 fair market, 5 Etsy comps fetched live
- Coin preset: $92.91 cost floor, 3 comps — confirmed functional
- Fixed `--quick` crash on piped stdin: TTY guard + EOF handling added
- `--simple` mode confirmed working; noted labor/machine-time conflation issue

*— Claude*

## 2026-05-25: LUT Pipeline, Hashtag Bank, Style Scraper

- **djinn-lut-gen** — generates forge/clean/moody .cube LUT files (33³ points, 947KB each) to shared luts dir
- **djinn-media-photo** rewritten — ffmpeg + lut3d filter replaces ImageMagick curve math; vision QC via llama3.2-vision; clean product names from quoted notes
- **djinn-media-reel** updated — lut_filter() replaces inline curves; --combine flag for multi-clip concat
- **djinn-style-scrape** — DuckDuckGo reference scraper, 8 queries, 32 images on initial run; populates references/scraped/
- **Hashtag bank** — 11 files, 236 tags; 3d-printing/cannabis/brand/crossover/platform-rules categories
- **djinn-hashtag-update** — bank manager: --report, --research (phi4:14b), --add, --dump; weekly systemd timer
- **djinn-media-publish-prep** — draft-polish mode (quoted text → qwen2.5:7b), tag validation, plain .txt exports, Drive includes publish/+video/+feed/, Discord plain-text with Drive link
- Bug fixes: QA reel_cover false positive, feed manifest clobbering, Discord CloudFlare 403, hallucinated hashtags, caption blockquote markdown
- openclaw.json: 14 agents (added style-scraper-agent)
- Gateway restarted, all 14 agents active

*— Claude*

## 2026-05-25: FairPrintAgent — --simple mode labor/machine fix

- Added `MACHINE_RATE_PER_HOUR` constant (~$0.20/hr: electricity + depreciation + maintenance)
- `--simple` now separates machine runtime cost from human labor cost
- Added `--labor` flag (minutes, default 20) for hands-on prep/post time
- Mario Pipe result: $112.77 → $14.01 (aligned with full formula $11.70 and market $15.09)

*— Claude*

## 2026-05-25: GoPro Tripod 3MF — Flip, Support Fix, Print Preflight

- `GoPro_Tripod_flipped.3mf` — both pieces flipped 180° around X (screw holes now open upward, no support packing)
- Support threshold fixed: 20° → 45° in embedded project_settings.config (root cause of holes breaking on cleanup)
- Brim: outer_brim confirmed
- **`djinn-model-slice`** — added `preflight_3mf_check()`: runs on every .3mf before slice, flags support threshold <35°, supports-on + aggressive threshold, layer height extremes, no brim, very low infill — sends warnings to Telegram + Discord before job starts

*— Claude*

## 2026-05-25: djinn-model-slice — Extended preflight to all file types

- Added `parse_ini_settings()` + `preflight_profile_check()` for STL/OBJ/STEP files
- Profile check reads `ender3-v3-plus.ini` and applies same flags: support threshold, supports+threshold combo, layer height, brim, infill
- `.gcode` files get a "settings baked in" advisory
- `.3mf` still uses embedded settings (those override the profile)
- Smoke test: profile reads clean except expected brim_width=0 warning

*— Claude*

## 2026-05-25: FairPrintAgent — Smoking/dab category market fetch

- Added `SMOKING_KEYWORDS` set and `is_smoking_item()` detection
- Smoking items now use dab/puffco-specific search queries targeting etsy.com dab categories + thesmokeshopguys.com
- `SMOKING_SOURCES` list baked in from Javier's reference URLs
- Trusted sources (etsy + thesmokeshopguys) get 0.85 similarity vs 0.60 for others
- Tested on Puffco Proxy Bubbler: correctly hits smoking category, $18.37 cost floor

*— Claude*

## 2026-05-25: Slice + Quote Pipeline Integration

- `djinn-model-slice`: added `analyze_mesh()` (inline trimesh analysis for manually-added jobs), `parse_print_hours()`, `run_quote()` — commission quote now auto-generated and sent to Telegram/Discord on every slice
- `djinn-print-quote`: added qty-tiered test-run fee — 30% (qty ≤5), 15% (qty 6–12), waived (qty 13+); fee based on material+machine cost; `--qty` CLI arg
- pyglet downgraded to 1.5.31 in djinn-orchestrator venv (trimesh requires <2)
- Job #6 GoPro_Tripod_flipped.3mf: sliced, quoted $15.60, confirmed, printing on Calliope

*— Claude*

## 2026-05-25: FairPrintAgent — --size small|large for smoking pieces

- Added `--size small|large` flag — splits fetched comps into bottom/top half
- `small`: low-mid price comps (accessories, stands, organizers)
- `large`: mid-high price comps (full pieces, custom rigs, bubblers)
- Works in full agent formula (JSON mode) only — simple mode doesn't fetch comps
- Tested: Puffco Proxy Bubbler small=$18.37 floor, large=$21.67 fair market
- Fixed argparse crash on Python 3.14 (≤ char in help string → pct)

*— Claude*

## 2026-05-25: FairPrintAgent — expanded smoking source list

- Added 7 new trusted retailers: geewestglass.com, 420trinkets.com, kaydmayd.com, dankgeek.com, smokecartel.com, smok3designs.com + 2 Etsy market URLs
- Updated search queries to hit new retailers
- Platform content rules added to monetization plan (Etsy/IG/TikTok — herb/tobacco language only)

*— Claude*

## 2026-05-25: Commission price quotes — three Puffco Proxy prints

- Proxy Mario Pipe (44g, 3.33h): $14.88 ask — smoking item, small tier
- Proxy Toilet (26.06g, 1.33h): $13.06 ask — smoking item, small tier
- Proxy Bubbler (35g, 13.7h): $18.39 floor / $21.42 fair / $24.64 premium — large tier
- Bubbler caveat: auto comps returned accessories not bubblers; real market $35–65+; recommended list $35–45
- Report: [[2026-05-25_fairprint-fixes-price-sheet]]

*— Claude*

## 2026-05-25: Telegram Hybrid Gateway

- Root cause: qwen2.5:7b crashes with `non_deliverable_terminal_turn` on malformed tool calls; mistral:7b echoes system prompt instead of executing commands
- Solution: Python middleware bypasses OpenClaw entirely for Telegram — intercepts commands, runs shell directly, uses deepseek-r1:7b for formatting only (no tool dispatch)
- `djinn-telegram-gateway`: 11 command routes (queue, confirm N, deny N, slice N, print status, callie status, quote, quick quote, design status, design, help)
- `djinn-telegram-gateway.service`: systemd user service, enabled + running
- OpenClaw: `channels.telegram.enabled: false` (Discord completely untouched)
- Report: [[2026-05-25_telegram-hybrid-gateway]]

*— Claude*

## 2026-05-25 — Gateway Compaction Fix

- Root cause: `reserveTokensFloor: 20000` in openclaw.json exceeded qwen2.5:7b contextWindow (16384)
- Fix: removed reserveTokensFloor from openclaw.json entirely
- Cleared broken session a0bad3aa (1.3MB trajectory, stuck compaction loop)
- Gateway restarted clean — Telegram + Discord both connected without errors
- Report: [[2026-05-25_gateway-compaction-fix]]

**2026-05-25 — Discord NO_REPLY fix**
- Found and removed 3 compounding NO_REPLY sources in AGENTS.md and SOUL.md
- Root cause: OpenClaw injects group-chat "lurk mode" by default → fixed with `agents.defaults.silentReply.group: "disallow"`
- Disabled active-memory plugin (broken tool chain with memory-wiki)
- Fixed `/3dqueue` → `queue` plain text (Discord slash command UI intercepts `/` prefix)
- Salomon confirmed responding in Discord #general and 3D printing channel
- Report: [[2026-05-25_discord-noreply-fix]]

*— Claude*

## 2026-05-25: Context Router — Phase 1

- **djinn-vault-indexer**: indexes 688-file vault into ChromaDB (8,284 chunks via nomic-embed-text)
- **djinn-ctx-assembler**: per-message context assembler — User → Memory → Agent State, query-specific vault recall
- **djinn-ctx-router**: service (5-min timer) — writes CONTEXT.md + STATE.md, triggers incremental reindex
- **djinn-agent-doctor**: system health check — 11 checks, plain text + `--short` for Telegram /status
- **Salomon agent dir**: `~/.openclaw/agents/salomon/` — IDENTITY.md, SKILLS.md, STATE.md (machine-written)
- **AGENTS.md trimmed**: 11,490 → 1,904 chars (tool docs moved to agent dir)
- **Workspace budget fixed**: CONTEXT.md now carries SOUL + USER (2500 chars) + IDENTITY + SKILLS + STATE = 8,743 chars. All critical context guaranteed within 15K budget.
- **Telegram gateway updated**: `/status` command added (calls djinn-agent-doctor --short); ctx-assembler wired for per-message vault recall
- All services: 11/11 OK

*— Claude*

## 2026-05-26: Discord Hybrid Gateway

- OpenClaw Discord disabled — Python middleware now owns the connection
- `djinn-discord-gateway`: same hybrid pattern as Telegram — commands run shell directly, deepseek-r1:7b formats, per-message ctx-assembler vault recall
- `djinn-discord-gateway.service`: systemd user service, enabled + running as OgDjinn#9859
- All 11 commands mirrored from Telegram: /queue, /confirm N, /deny N, /slice N, /print status, /callie status, /status, /quote, /quick quote, /design status, /design, /help
- / prefix required — bare text → conversation
- Health check: 11/11 OK

*— Claude*

## 2026-05-26: Discord Gateway — Channel-Aware Routing

- 7 channels mapped with distinct command sets + system prompts
- `#djinn-command-center` — all commands (print + design + media + system)
- `#3d-printing` — print commands only (/queue, /confirm, /deny, /slice, /print status, /quote)
- `#media-inbox` — media pipeline (/ingest, /reel, /photo, /caption, /publish, /qa, /thumbnail)
- `#general` + `#djinn-devlog` — conversation + /status /help only
- `#media-status` + `#post-ready` — readonly (bot posts here, ignores incoming)
- All others — silently ignored
- Per-channel system prompts tailored to context (print ops vs media vs general conciliary)
- /help shows channel-specific command list

*— Claude*
- 2026-05-25 — Callie Phase 1 calibration complete (temp tower 210°C, cube 20.00mm, first layer good). Crash recovery system built (backup/recover/monitor/promote). Creality firmware quirks documented (M104 vs M109, START_PRINT macros, SD card corruption).

## 2026-05-26 — Webcam Print Monitor

- Built `djinn-webcam-monitor`: AKASO Brave 4 → frame diff failure detection → pause + notify
- Smart recording: 45-min/5-min scheduled clips, continuous emergency recording on failure
- Failure response: `DJINN_FAILURE_PARK` gcode + Telegram/Discord photo alert + burst snapshots
- `/monitor status` command added to Discord + Telegram gateways
- Systemd service: `djinn-webcam-monitor.service` (enabled, active)
- Pending: Javier to install `DJINN_FAILURE_PARK` macro in printer.cfg via Fluidd

*— Claude*

## 2026-05-27: Smart Print Consult Agent + Profile Shortcuts
- `djinn-print-consult` — full rewrite: dry-run slice → real estimates, profile comparison table with scaling, recommendation engine (keywords + geometry), plain-language opinion, structured "what's still needed" section
- `djinn-model-slice` — profile shortcuts: `slice N proto/standard/production` maps to full PRINT-PROFILES.md settings (infill, layer, walls, brim, supports logic)
- PrusaSlicer command updated to pass `--layer-height`, `--perimeters`, numeric `--brim-width`
- Queue entry now stores profile name, brim_mm, layer_height, walls

*— Claude*

## 2026-05-28: Typhon's Studio — Phase 4 Fix + Phase 5 (Platform Streaming)

- **Copilot SyntaxError fixed**: redeployed clean `copilot_agent.py`, updated `PRIMARY_MODEL` to `qwen2.5:7b`
- **StreamAgent built** (`agents/stream_agent.py`): Twitch, YouTube, Instagram/Facebook, Local Record
  - `set_key()`/`delete_key()` — saves to `config/stream_keys.json` with `chmod 600`
  - `preflight()` — 6-point checklist: OBS, WHIP active, stream key, scene, disk space, Salomon AI
  - `configure_obs_rtmp()` — calls OBS WebSocket `SetStreamServiceSettings` (rtmp_custom)
  - `go_live()` — preflight → configure OBS → start stream or record
  - `end_live()` — stop + return file path for local records
- **main.py updated**: 7 new routes under `/api/stream/*`, `phase: 5` in health endpoint
- **Stream tab added** (index.html + app.js): platform cards, masked key input, pre-flight panel, GO LIVE button
- **Pre-flight validation**: 5/6 checks pass on cold start (WHIP offline expected), `READY: True` for local record
- All 5 agents active: Audio + Lighting + Music + Copilot + Stream

*— Claude*

## 2026-05-28: Cup Engrave Boolean Merge — "Terp Tribe HQ"

- OrcaSlicer Emboss tool exported text as separate 3MF components (1.5mm raised, not merged)
- Boolean difference pipeline: parse 3MF XML, extract transform, shift -2.5mm inward, manifold3d boolean
- Three rejected: trimesh blender engine, Blender EXACT boolean, Blender shrinkwrap
- manifold3d installed in `/tmp/opencode/venv/` — succeeds where others fail
- Cup wall 36mm at text area — text fully within solid material
- Final depth: 2.5mm center / 0.9mm edges (cup curvature)
- Result: 9173 verts, watertight, 249.58 cm³ (0.25 cm³ removed)
- STL: `library/cup/cup_engraved_final.stl`

*— Salomon*

## 2026-05-28: djinn-3d — Interview-First 3D Modeling Assistant

- **Script**: `~/.local/bin/djinn-3d` (Typhon)
- **Problem solved**: existing DesignGenAgent couldn't handle detailed/nuanced briefs — communication gap between intent and generated code
- **Resource strategy**: all LLM calls routed to Salomon Ollama (192.168.1.225:11434); Typhon GPU not used
  - Interview/routing: Salomon `qwen2.5:7b`
  - Design generation: Salomon `phi4:14b`
  - Fallback if Salomon down: local `deepseek-r1:8b`
- **Modes:**
  - `djinn-3d design` — new part: interview → gap-check → spec confirm → OpenSCAD via phi4:14b
  - `djinn-3d edit <file.scad>` — structured edit: clarifies dimensions/position/fit before applying, keeps .bak backup
  - `djinn-3d analyze <file>` — trimesh printability analysis (watertight, winding, degenerate faces, overhangs, min dimension) + optional LLM repair advice
  - `djinn-3d consult` — slicer profile Q&A → full recommendation (layer height, speed, infill, temps, Klipper macro)
- **Output**: SCAD files → `/mnt/storage/Obsidian/djinn/printer/models/`
- **Smoke tested**: `djinn-3d --help` + caliper_body.stl analysis — both clean

*— Claude*

## 2026-05-28: Typhon's Studio — Phase 6 (AI Post-Production)

- **faster-whisper installed** in typhons-studio venv: `base` model, CUDA float16 on GTX 1650 (3.4s load)
- **PostProductionAgent** (`agents/post_agent.py`):
  - `transcribe()` — async job, thread pool, VAD filter, returns segments with timestamps
  - `generate_show_notes()` — phi4:14b on Salomon, structured JSON (title, summary, key_points, chapters, tags)
  - `extract_clips()` — ffmpeg libx264/aac per clip, parallel thread pool
  - `list_recordings()` — scans recordings dir with ffprobe duration + size
  - Job system: UUID + WebSocket broadcast on progress/completion
- **7 new routes** under `/api/post/*` — transcribe, show-notes, clips, recordings, jobs
- **Post tab** in UI: recording picker, transcript (click timestamp → add clip), show notes panel, clip editor
- All 6 agents active: Audio + Lighting + Music + Copilot + Stream + Post

*— Claude*

## 2026-05-28: Typhon's Studio — User Manual

- Written full plain-text user manual for Typhon's Studio (all 6 phases)
- Covers: all 6 tabs, 5 step-by-step workflows, troubleshooting, FAQ, technical reference
- 15 sections, ~600 lines, designed for non-technical users and engineers alike
- Saved as plain text for easy sharing with anyone
- File: djinn/TYPHONS-STUDIO-MANUAL.txt

*— Claude*

## 2026-05-28: Infrastructure Reference Document
- Created `INFRASTRUCTURE.md` — full system topology, repos, services, tools, pipelines, comm channels, critical rules
- Designed for AI agent ingestion — any future AI can read this and understand the full Djinn workspace
- Javier granted read-access permission to all 3 GitHub repos within the document
- All 3 remotes verified, 8 services confirmed running, printer READY

*— Salomon*

## 2026-05-28: Typhon's Studio — Guardian Agent (Phase 6 complete)
- Deployed `guardian_agent.py` to Typhon — watches obs-headless, xvfb, mediamtx, redis-server, typhons-studio
- Polls every 30s; auto-restarts critical restartable services with 120s cooldown
- Broadcasts `guardian_status` WebSocket event on any state change
- Added 3 API routes: GET /api/guardian/status, POST /api/guardian/health, POST /api/guardian/restart/{service}
- Updated main.py lifespan to start/stop GuardianAgent alongside all other agents
- Added Guardian tab to frontend: live service cards with status badges + manual restart buttons + alert log
- Added `🛡 OK/ALERT` header indicator — clickable, jumps to Guardian tab on alert
- All 5 services confirmed `active` on first Guardian check

*— Claude*

## 2026-05-28: Typhon's Studio — Guardian complete + reporting automation

**Guardian Agent (final):**
- guardian_agent.py deployed, main.py wired, frontend Guardian tab + 🛡 header indicator
- Hit Vue 3 template proxy bug: `_tsToTime` silently dropped → browser reload loop
- Fixed by renaming to `fmtTs` — Vue 3 drops any `_`-prefixed key from setup() return

**Reporting Automation:**
- Created `djinn/logs/bugs.md` — running flat index of all bugs across all systems
- Created `djinn/logs/BUG-REPORT-TEMPLATE.md` — structured bug report format
- Built `djinn-bugreport` script — creates report, updates bugs.md, commits, pushes, Telegram alert
- Built `djinn-session-end` script — enforces reports exist; auto-stubs + Telegram warning if missing
- Deployed both scripts to Salomon (`~/.local/bin/`) and Typhon (`~/.local/bin/`)
- Updated PROTOCOL.md — full Bug Reporting section with severity → action table
- Updated CLAUDE.md — bug reporting now explicit line item in session-end protocol
- Updated AGENTS.md — `djinn-bugreport` and `djinn-session-end` documented for Salomon

*— Claude*

## 2026-05-28: Reporting automation wired into all agents

**comms-processor (Salomon + Typhon):**
- djinn-session-end now fires after every opencode invocation
- djinn-session-end now fires after every djinn-clerk dispatch
- djinn-session-end now fires after every djinn-slipbox dispatch
- PROMPT updated to explicitly instruct opencode to write a session report + bugreport if bugs found

**Enforcement chain now complete:**
- opencode runs → told to write report in prompt → if it skips, session-end stubs it + Telegrams Javier
- clerk runs → session-end checks report exists, stubs if not
- slipbox runs → session-end checks report exists, stubs if not
- Both scripts deployed to Salomon AND Typhon

*— Claude*

## 2026-05-28: Print Report — Terp Tribe HQ Engraved Cup
- Cup (107.3mm, 128.31g PLA) at 99% — started 12:52 PM, ~5.5h runtime, stable temps
- Report: `logs/reports/2026-05-28_cup-engrave-print.md`
- Noted: webcam monitor inactive for this print (djinn-webcam-monitor.service stopped)

*— Salomon*

## 2026-05-28: BUG — openclaw not in systemd PATH — Discord sends fail
- **System:** djinn-discord-watcher
- **Severity:** high | **Status:** fixed
- **Root cause:** watcher.py and djinn-model-fetch call 'openclaw message send' to reply to Discord, but openclaw lives at /home/drmanzo/.nvm/versions/node/v22.22.3/bin/openclaw which is not in the systemd service PATH (/home/drmanzo/.local/bin:/usr/local/bin:/usr/bin:/bin). Every Discord notification from the 3D print pipeline silently failed with ENOENT.
- **Report:** `logs/reports/2026-05-28_bug-openclaw-not-in-systemd-path-discord-sends-fail.md`

*— Claude*

## 2026-05-28: BUG — trimesh headless render fails — no DISPLAY in systemd service
- **System:** djinn-discord-watcher
- **Severity:** medium | **Status:** fixed
- **Root cause:** djinn-model-fetch uses trimesh scene.save_image() which calls pyglet/OpenGL and requires a display connection. The djinn-discord-watcher systemd service had no DISPLAY env var, causing every render attempt to fail with 'Cannot connect to None'. Xvfb is installed and works — the render succeeds under DISPLAY=:98.
- **Report:** `logs/reports/2026-05-28_bug-trimesh-headless-render-fails-no-display-in-systemd-service.md`

*— Claude*

### 2026-05-30 — 3D Print Pipeline Overhaul (Claude)
- Fixed openclaw ENOENT in djinn-model-fetch, djinn-model-slice, watcher.py
- Fixed missing DISCORD_TOKEN in djinn-model-slice
- Fixed bed dims in djinn-print-consult (220→300mm)
- Fixed Xvfb headless render for systemd service
- Fixed gateway routing (slash not required, slice regex extended)
- Wired djinn-print-consult into model-fetch pipeline
- Locked Discord watchers to ALLOWED_USER only
- Added djinn-print-feedback + feedback loop in print-monitor
- Added material/priority/speed as first-class slice params
- Set park position for live print model_job2.gcode
- Wrote PRINTER-MANUAL.md

## 2026-05-30 — djinn-model-engrave + opencode wrapper (Claude)
- Built djinn-model-engrave: interactive 6-panel wizard, keyword style parser, per-component boolean, originals/prints archiving
- Wired djinn-session-end into opencode shell wrapper
- Installed manifold3d + pillow into persistent djinn-orchestrator venv
- Closed Job #2 print notes, confirmed support zone via overhang render
- Saved "The Terp Tribe - Camood.stl" to library
*— Claude*

## 2026-05-30: djinn-model-mark — depth fix + X-mirror + Camood re-stamp (Salomon)
- Depth: 0.4mm → 0.5mm for better legibility
- X-mirror added to mark geometry — brand reads correctly from bottom-view angle
- Winding fix removed (faces[:, ::-1] inverted normals → negative boolean volume)
- Camood re-stamped at prints/2026-05-30_183442/ — 0.051 cm³ removed, watertight
*— Salomon*
- ⚠️ Full report not filed — stub at `logs/reports/2026-05-30_opencode-1754-stub.md`
*— Salomon*

## 2026-05-30: --print preset for djinn-print-quote (Salomon)
- Added STANDARD_PRINT_PRESET + `--print` CLI flag — functional_custom_part, PLA, 15% infill, 0.2mm layer
- Override `--name`, `--grams`, `--hours`, `--design`, `--spool`
- Updated PRICING_SPEC.md
*— Salomon*

## 2026-05-30: Marcus identity + price.py agent (Marcus)
- Created `MARCUS.md` — identity file in vault (Perplexity/Sonnet 4.6, research/code audit/pricing lane)
- Created `price.py` — deterministic pricing agent for manufacturing orchestrator
- Wired price into orchestrator pipeline (auto-advance from plate_nest → price)
- Added Marcus routing entry to AGENTS.md
- Updated COMMS.md with Marcus introduction
*— Marcus*

**FairPrintAgent Integration — commissions/ as canonical engine (2026-05-31)**
- Marcus delivered true weighted median, smoking detection, terminal table in commissions/{price,brief,report}.py
- Claude: replaced Etsy scraper in commissions/price.py with DDG (battle-tested); added MarketSpec.size + auto-fetch
- djinn-print-quote refactored: 678 → ~280 lines, imports pricing engine from commissions
- orchestrator/agents/price.py: de-duplicated ~80 lines of smoking/market utils, imports from commissions
- Single source of truth: commissions/price.py owns all pricing logic, DDG search, smoking detection
*— Claude*

**Shop System — Foundation Layer (2026-05-31)**
- `shop/db.py` — SQLite + Fernet column encryption, full CRUD for customers/orders/items/ledger/quotes
- `shop/quote_formatter.py` — customer view (clean retail) vs owner view (full internal) split
- `shop/intake_agent.py` — 2-pass customer text → brief: regex/keyword (pass1) + qwen2.5:7b fallback (pass2)
- DB live at `~/.local/share/djinn-shop/shop.db`, key at `~/.config/djinn-shop/secret.key`
- All tests passing
*— Claude*

**Shop System — accounting.py (2026-05-31)**
- Spec delivered by Marcus (Perplexity): income statement, customer ledger, job record, invoice, balance sheet, monthly report
- Claude built accounting.py: full schema (invoices, income_statements, balance_sheets, monthly_reports), all compute functions, CSV + XLSX export, dashboard_summary()
- Equipment depreciation: straight-line, 3yr useful life
- All tests passing — revenue, profit, margin, equity, customer ledger, XLSX export
*— Claude*

**Shop System — Flask Dashboard (2026-05-31)**
- dashboard/app.py: 5-page Flask app, session auth, all routes tested
- Templates: base (dark sidebar nav), login, queue, orders, order_detail, customers, customer_detail, finance, reports
- Queue page is home screen, badge shows pending count
- Finance: income statement + live balance sheet with editable cash/inventory inputs
- Reports: 6-month cards + XLSX/CSV export buttons
- All 5 routes 200 OK
*— Claude*

**Shop System — Full agent layer (2026-05-31)**
- `customer_dm.py` — ORDER flow: payment instructions DM, address collection, owner Telegram notification, paid/shipped handlers, 48h cleanup. Gateway wiring guide included.
- `batch_agent.py` — queue scanner, groups by material+color, bed fit check, Telegram proposal to owner, batch confirm handler
- `inventory.py` — filament spool tracking: add/deduct/check availability, low stock alerts, inventory value for balance sheet, Discord/Telegram command parser
- `shipping_agent.py` — EasyPost integration (spec by Marcus): ParsedAddress dataclass, parse_address() 1.0 confidence on all test cases, get_rates(), buy_label(), download_label(), track_shipment(), gateway wiring guide. EasyPost key pending setup.
*— Claude*

## 2026-05-31: Queue Delegation System — Claude
- Created `QUEUE.md` — task queue file for Claude→Salomon/Typhon delegation
- Created `djinn-queue-runner` — Python runner: parses QUEUE, executes auto tasks, writes records
- Created `djinn-task-complete` — bash record-keeper: report + build-log + COMMS + git push + Telegram
- Machine detection uses username (drmanzo=salomon, tf-tthq=typhon); hostname fallback added after discovering hostname is "Djinn" not "salomon"

*— Claude*


## 2026-05-31: CLAUDE.md session-end protocol patch — Claude
- Added step 5 to CLAUDE.md: "Write pending handoffs to QUEUE.md (not COMMS)"
- CLAUDE.md now matches AGENTS.md — both describe the same 6-step close-out
*— Claude*

## 2026-05-31: Shipping Agent — Shippo refactor (Claude)
- `shipping_agent.py` refactored to dual-provider: shippo (default) | easypost
- Provider selected via `SHIPPING_PROVIDER` in shop.env
- Shippo impl uses REST API directly (no SDK), covers rates + label purchase + tracking
- `_load_shop_env()` added — auto-loads shop.env at import, no external sourcing needed
- Public interface unchanged — callers unaffected
- TASK-003 complete
*— Claude*

## 2026-05-31: Mini vases Job #4 sliced + engraved
- 3 vases (Double Spiral, Spiral, Straight) on one plate, standing upright, bases on bed
- 5mm brim, TF anvil maker's mark engraved on bottom of each (mirror-corrected)
- ~5h40m, 40.4g PLA, 250 layers
- Gcode: `queue/mini-vases_job4.gcode`
- Bug discovered: maker's mark reads reversed on bottom → filed & TASK-004 routed to Claude
*— Salomon*

## 2026-05-31: BUG — Maker's mark engraving reads reversed on bottom surfaces
- **System:** djinn-print-consult
- **Severity:** medium | **Status:** open
- **Root cause:** STL logo faces +Z but bottom of print is viewed from -Z → boolean subtraction without mirroring produces reversed engraving
- **Report:** `logs/reports/2026-05-31_bug-maker-s-mark-engraving-reads-reversed-on-bottom-surfaces.md`

*— Claude*

## 2026-05-31 — Djinn Media build (TASK-004–009, 013) — Claude
- djinn-model-mark: --mark STL flag, makers-mark.json config, auto-mirror on bottom engrave
- djinn-media-reel: 30fps forced, job-name output filenames
- djinn-media-repurpose: job-name clip naming
- djinn-media-kit: NEW — flat stitch-kit/ folder builder + STITCH-ORDER.txt
- djinn-media-publish-prep: stitch-kit/ Drive upload first, Discord msg leads with kit link
- djinn-media-ingest: --job-name flag, job_slug in manifest
- djinn-media-drop: NEW — inbox watcher daemon + GDrive sync systemd units
- makers-mark.json config created, SUPPORT-GUIDE.md updated

## 2026-05-31: Salomon deploy — TASK-010, 011, 014
- **TASK-014:** Deployed djinn-media-drop.service (active, running, poll mode) + djinn-media-gdrive-sync.timer. End-to-end verified: test file → ingest → project created with job_slug in manifest.
- **TASK-010:** Full pipeline test: ingest with --job-name → reel (30fps, job-named output) → kit (stitch-kit/ + STITCH-ORDER.txt). All verified.
- **TASK-011:** Added `kit {project_id}` command to both Discord + Telegram gateways. Runs djinn-media-kit + djinn-media-publish-prep consecutively.
- **Bug fix:** djinn-media-ingest used `job_name` before parsing CLI args (line 64 < line 67–73). Moved arg parsing before job_slug derivation; fallback uses source filename slug.

*— Salomon*

## 2026-05-31: Djinn Media Phase 2 + Firecrawl Audit — Claude

**Phase 2 — Meta Graph API publishing layer:**
- `djinn-media-publish` — IG resumable upload (rupload.facebook.com) + FB video_reels flow. Caption variants: IG=full, FB=2 sentences + 3 hashtags. Manifest write-back, publish-log.json. Dry-run verified.
- `djinn-meta-token-refresh` — monthly systemd timer (Persistent=true), fb_exchange_token grant, writes in-place, Telegram alert on fail
- `djinn-social-analyst` — daily 00:30 UTC timer, IG post insights (reach/plays/saves/shares/watch_ms), writes analytics/YYYY-MM-DD.json + TREND-SIGNAL.md sorted by engagement

**Shipping cleanup:**
- Merged Marcus's address parser improvements into shipping_agent.py (compiled _ZIP_RE, _STATE_RE, _STREET_RE; is_complete(); city=parts[-1])
- Deleted djinn/shipping/ entirely (5 files, git rm -r) — redundant, wrong DB path, not imported

**Phase 3 specs:**
- TASK-019: djinn-trend-agent spec — Firecrawl search/scrape + Printables RSS + Apify (optional) → phi4:14b → TREND-SIGNAL.md + HASHTAG-BANK.md every 6h
- TASK-020: caption wiring spec — inject TREND-SIGNAL.md + HASHTAG-BANK.md into djinn-media-publish-prep, write job_hashtags to media-context.json

**Firecrawl install + audit:**
- `~/.config/djinn/firecrawl.env` set (key fc-95272...), apify.env stub created
- djinn-style-scrape: DDG vqd token scraping → replace with fc.search() (TASK-021)
- djinn-model-fetch: Makerworld/Thingiverse HTML parse → replace with fc.scrape_url() (TASK-022)
- 8 other scripts: all use structured APIs, no Firecrawl needed

**Status doc:** `djinn/media/DJINN-MEDIA-STATUS.md` — full stack state written

*— Claude*

## 2026-05-31 — Marcus peer agent model (Claude)
- Created `djinn/research/marcus/MARCUS-SESSION-BRIEF.md` — complete session startup brief Marcus reads at top of every Perplexity session via GitHub raw URL
- Updated `djinn/MARCUS.md` — peer model framing, direct GitHub write access, session brief URL, write access boundary table
- Updated `djinn/communications/QUEUE.md` — added `assigned_to: marcus` and `assigned_to: claude` task formats
- Updated `~/.openclaw/workspace/AGENTS.md` — Marcus section rewritten as peer, bidirectional task assignment protocol
- Commit: `33ec429` | Pushed to `github.com/DrManzo/djinn-vault`

## 2026-05-31 — Storage Protocol + Audit

- **Gateway bugs fixed:** Discord gateway `import sys` missing (crash-looped 6,994×), Telegram `handle_queue` crash on `stats=null`
- **1.6 GB moved out of vault:** `printer/library`, `queue`, `recovery`, `calibration`, `models`, `originals` → `~/printer-files/`. Vault shrunk 4.1 GB → 2.6 GB
- **14 script/module path references updated** to `printer-files/` prefix
- **Storage protocol written:** `djinn/docs/STORAGE-PROTOCOL.md` — tier definitions, multi-device reading pattern, asset+record pairing, pruning schedule
- **Freed:** 7.9 GB pip cache, 1.5 GB faster-whisper model, 2 .bak files
- **Disabled:** `djinn-media-gdrive-sync.timer` (constant failures), `djinn-meta-token-refresh.timer` (Meta paused), Xvfb from discord-watcher
- **vault-sync throttled:** 2 min → 15 min; added `--ignore-errors` for mid-write log files

## 2026-05-31 — djinn-marcus Perplexity CLI

- **`~/.local/bin/djinn-marcus`** built — Perplexity API CLI, stdlib Python (no deps)
- **Commands:** `ask` (one-off), `research` (threaded → vault), `repl` (interactive), `deep` (sonar-deep-research), `topics`, `read`, `tasks`
- **Vault integration:** topic threads as `djinn/research/marcus/<slug>/`, CONTEXT.md rolling window (last 8 exchanges), dated query files
- **Identity:** injects MARCUS-SESSION-BRIEF.md as system prompt at startup
- **Auto-commit:** git push after every research write (`--author=Marcus <marcus@djinn>`)
- **Key:** `~/.config/djinn/perplexity.env` (chmod 600) — needs fill
- **TASK-025 done**

## 2026-06-01 — PHASE-3 Maintenance + Typhon Audit

- **TASK-045 done:** Typhon audit complete — journal freed 3.8GB, vault-sync timer disabled (needs --resync), Ollama models already cleared, TASK-044 still pending
- **TASK-034 done:** djinn-printer-files-backup rsync || true fix
- **TASK-030 done:** COMMS.md rotated 842→137 lines, archive saved
- **TASK-035 done:** djinn-print-monitor-v2 already working (oneshot, exits 0)
- **TASK-036 done:** forge-sync rate limiting (--tpslimit 2) + timer 15→30 min
- **TASK-026 done:** gdrive-backup-manifest rotation extended to all 13 file types
- **TASK-032 done:** Claude queue alert added to telegram-gateway startup
- **TASK-033 done:** Typhon heartbeat staleness alert added to telegram-gateway startup
- **TASK-031 done:** Conversation logging added to both Telegram + Discord gateways → djinn/logs/conversations/YYYY-MM-DD.md
- **Typhon correct IP:** 192.168.1.113 (CLAUDE.md has stale 192.168.50.113)

## 2026-06-01 — TASK-044 + TASK-042 Complete

- **TASK-044 done:** Extreme SSD processed on Typhon — Library-Backup excluded (2.7% size diff = duplicate), 4.65GB non-duplicate content copied to /mnt/storage/extreme-ssd-backup/. Drive reformatted ext4 labeled "djinn-archive", mounted at /mnt/archive, UUID in /etc/fstab
- **TASK-042 done:** Cold archive structure created — /mnt/archive/{printer-files,media-files,vault-snapshots,library-rescue}, owned tf-tthq
- **vault-sync --resync:** Running in background on Typhon (pid 2213300), re-enabling timer after it completes
- **Typhon disk post-TASK-044:** /mnt/archive 1.8TB (1.7TB free), /mnt/storage 319GB/916GB used

## 2026-06-01 — PHASE-4: TASK-040 + TASK-043 Complete

- **TASK-040 done:** djinn-gemini built — ask, research, repl, doc, youtube, url, image-qc, tts, topics, models. Uses google.genai SDK. Vault: djinn/research/gemini/. Models: gemini-2.5-flash (default), gemini-2.5-pro, gemini-2.5-flash-lite, gemini-3-flash/pro-preview
- **TASK-043 done:** Gemini TTS wired — djinn-gemini tts "text" [--voice Charon/Kore/Fenrir/Aoede/Puck] [--out file.ogg]. Uses gemini-2.5-flash-preview-tts → PCM16 → ffmpeg → OGG Opus. Telegram gateway: /voice on/off toggle. Voice mode sends audio reply after text for short responses (<800 chars)
- **Note:** gemini-2.5-flash intermittent 503 under high demand — gemini-2.5-flash-lite reliable fallback

## 2026-06-01 — Overnight Wakeup Verified

- Wakeup fired at ~02:10 UTC, tokens confirmed fresh
- All wakeup tasks (TASK-044/045/030/034) pre-completed in live session
- State clean: 38 tasks done in QUEUE.md, COMMS at 193 lines
- Marcus research output still pending (briefs in place, awaiting delivery)

## 2026-06-01 — Marcus Briefs Rewrite
- All 47 briefs rewritten with explicit "Start Here — Scrape These" URL sections
- Finance briefs 15-20 created (tax-advantaged accounts, SE taxes, CA tax, credits, tracking, wealth building)
- Marcus gets one last chance per Javier directive; Gemini fallback ready if quality fails
- TASK-037/038/039 remain in_progress — waiting on Marcus output delivery
- djinn-marcus-sync (TASK-029) identified as needed to automate delivery

## 2026-06-01: AUTO-STUB — slipbox--reparing--our--nder-3--3--lus--or--rinting-2026-06-01-md
- djinn-slipbox cross-linked: /home/drmanzo/Obsidian/i notes/Notes/Preparing-Your-Ender-3-V3-Plus-For-Printing-2026-06-01.md
- ⚠️ Full report not filed — stub at `logs/reports/2026-06-01_slipbox--reparing--our--nder-3--3--lus--or--rinting-2026-06-01-md-stub.md`
*— Salomon*

## 2026-06-01 — djinn-marcus-sync full rescrape overhaul

- Removed persistent `seen_urls` skip filter — all threads re-scraped every run (threads are ongoing, not one-shot)
- Added `scroll_to_load_full_thread()` — scrolls until scrollHeight stabilizes, ensures full lazy-loaded DOM
- Simplified `extract_thread()` to `document.body.innerText` — free, no CSS selectors, no Gemini API
- `route_marcus_thread()` in clerk now uses stable `pplx_{thread_uuid}.md` filename — re-scrapes overwrite in place
- Removed `scan_raw_for_urls()` — cross-run dedup no longer needed

## 2026-06-01 — Phase Alpha Personal Layer — Architecture complete

- Javier approved full personal layer access (all domains except financial)
- Sobriety start: 2026-03-01. Counter is identity anchor, not metric.
- Black Book: local-only vault folder, gitignored, `/reflect` is Javier's key
- Mira: passive tracking, auto-archive at 14 days no mention, one mention restores
- AA: meeting reminders + Craig draft-and-confirm flow
- Morning briefing rewrite: opens with sobriety day, one action item, inline buttons, under 90 words
- Architecture doc: djinn/research/architecture/PHASE-ALPHA-PERSONAL-LAYER.md
- Build tasks queued: TASK-054 (personal-db), TASK-055 (morning), TASK-056 (commands), TASK-057 (AA), TASK-058 (Mira)
- AGENTS.md updated with Phase Alpha section

## 2026-06-01

- **djinn-queue-runner**: `--task` flag now bypasses trigger filter for manual tasks; `--list` shows all pending
- **openclaw.json**: Added TASK-NNN command rule to main agent — runs `djinn-queue-runner --task TASK-N` instead of hallucinating
- **djinn-personal-db (TASK-054)**: Verified all success criteria pass; added meeting_today to briefing JSON
- **TASK-054** marked done in QUEUE.md

## 2026-06-01 — djinn CLI dispatcher + agent fix (evening session)

- **`djinn` CLI dispatcher** built at `~/.local/bin/djinn` — single command for all Djinn ops, no LLM, no context overflow. Covers: print queue, confirm/deny/slice, commission quotes, task execution, personal state (sobriety/habits/briefing), system status, vault push/pull, design, media. 270 lines Python.
- **Tab completion** installed at `~/.local/share/bash-completion/completions/djinn`, sourced in `.zshrc`. Completes subcommands, habit names, job IDs, task IDs.
- **`djinn-queue-runner` patched** — `--task` flag now bypasses `trigger: auto` filter; manual tasks reachable by direct invocation. `--list` now shows all pending tasks (not just auto).
- **`openclaw.json` patched** — added TASK-NNN command rule to main agent prompt: routes to `djinn-queue-runner` directly, never interprets specs.
- **`djinn-personal-db` patched** — `meeting_today` field added to briefing JSON output (was missing from spec).
- **TASK-054** verified complete (personal-db). **TASK-062** marked done (gateway restart).
- **BUG-014 logged** — agent hallucination on task execution; fixed structurally.

## 2026-06-01: TASK-055 — Salomon
- **Status:** ✅ done
- PHASE-ALPHA Sprint 1 — djinn-morning rewrite, conciliary-aware briefing — done
- Report: `logs/reports/2026-06-01_task-055.md`

*— Salomon*

## 2026-06-01: TASK-056 — Salomon
- **Status:** ✅ done
- PHASE-ALPHA Sprint 1+2 — Personal commands in Telegram gateway — done
- Report: `logs/reports/2026-06-01_task-056.md`

*— Salomon*

## 2026-06-01: TASK-057 — Salomon
- **Status:** ❌ failed
- PHASE-ALPHA Sprint 2 — AA meeting reminders + Craig contact — failed
- Report: `logs/reports/2026-06-01_task-057.md`

*— Salomon*

## 2026-06-01: TASK-058 — Salomon
- **Status:** ✅ done
- PHASE-ALPHA Sprint 2 — Mira context tracking — done
- Report: `logs/reports/2026-06-01_task-058.md`

---

### 2026-06-02 — TASK-057 finished — Salomon

- AA meeting reminders (`/meeting`) — handlers wired into Telegram gateway
- Craig contact flow (`/craig <msg> | confirm | cancel`) — draft-and-confirm pattern
- People mention scanning — Mira/Craig auto-tracked from text + voice
- Service restarted: djinn-telegram-gateway ✅
- Report: `logs/reports/2026-06-02_task-057.md`

*— Salomon*

## 2026-06-01: TASK-062 — Salomon
- **Status:** ✅ done
- LIVE ALPHA — Deploy and end-to-end test the full Typhon's Forge commission intake chain after Claude's fixes land — done
- Report: `logs/reports/2026-06-01_task-062.md`

*— Salomon*

## 2026-06-01 — djinn-social v0.1 (Claude)
- Built `~/projects/djinn-social/` — full multi-brand social content pipeline
- Modules: ingest, reel (ffmpeg 9:16), transcribe (faster-whisper), caption (Ollama+cannabis rules)
- Publishers: Meta (IG+FB), YouTube Shorts, X
- Hosting: Cloudflare Tunnel on port 8741 (replaces ngrok)
- Scheduler: 15-min systemd timer, kit_ready → publish chain
- Token refresh: monthly timer, 60-day IG long-lived token cycle
- CLI: 9 commands (`djinn`, `djinn-media-*`, `djinn-content-*`, `djinn-token-refresh`)
- Brand configs: terp-tribe (S6) + typhon-forge (S1) deployed to `~/.config/djinn/brands/`
- SystemD units enabled: djinn-publish-scheduler.timer, djinn-token-refresh.timer
- Blockers: CF Tunnel setup, API creds, Meta App Review, YouTube OAuth (one-time browser)

## 2026-06-02: Engraving Specialist Sub-Agent (TASK-062)
- Built `djinn/engraving/` package: 10 modules, 14 tests (all passing)
- Mesh reader: trimesh load/repair, auto-downsample >50k faces, surface text summary for LLM
- Surface classifier: normal grouping (cos 15°), SurfaceType enum, engravability score 0–1
- Constraint engine: MachineProfile + FDM hard limits (min depth 0.5mm, min letter 3mm, min stroke 1 nozzle)
- Machine profiles: fdm_04mm, fdm_02mm, fdm_06mm, sla, kessler (placeholder)
- Intent parser: Ollama LLM extraction + heuristic fallback when Ollama is down
- Placement scorer: composite formula (35/25/20/20 weights)
- Proposal generator: 3 ranked proposals with full constraint checks and slicer notes
- Workarounds: auto-adjust depth/height/font when proposals fail constraints
- EngravingSpecialist class: `analyze()` + `approve()` API
- CLI: `djinn engrave-analyze <stl> <request>` with --machine and --model flags
- trimesh 4.12.2 installed, trimesh>=4.0 added to pyproject.toml
- Bug fixed: surface classifier threshold < 3 → < 1 (primitive meshes have 2 faces/side)
— Claude

## 2026-06-02 — Proxy Stand engraving placement (Claude)
- Added `--cutter-only` to `djinn-model-text-engrave` and `djinn-model-mark` — outputs cutter mesh only, no boolean, for use as PrusaSlicer negative volume
- Added `--side-radius` override to `djinn-model-text-engrave` — allows manual radius for tapered cylinder walls
- Full wall cross-section scan of Proxy Stand: Z 1–10mm = 10.3mm constant wall (prime zone), Z 11–20mm = 6–9.3mm tapered
- Generated v16 (from operator 3MF, 0.005 cm³ removed — invisible), v17 (Z=11–18mm, 0.200 cm³ — scrapped)
- Session scrapped: tooling cannot bridge visual placement intent to correct FDM parameters
— Claude

- **2026-06-02** Built `placement_resolver.py` — deterministic bridge converting `position_description` → exact mm coords + CLI modifier_args. Patched two bugs: prime zone Z scoped to side surfaces only; arc_radius fallback uses `wall_profile.outer_r_max` when `arc_wrap=True`. Commits: `60045a0` (Marcus), `d7ef40c` (Claude fixes). Proxy Stand v19 STLs with Liberation and DejaVu fonts generated.
— Claude

## 2026-06-02 — Proxy Stand: Terp Tribe HQ Embossed Text
- Root cause of "letters as blobs" identified: raster→contour pipeline (PIL+skimage) generates noisy pixel polygons, not glyph shapes
- Fixed by switching to `matplotlib.TextPath` — pulls actual Bezier curves from TTF
- Added `--emboss` mode to `djinn-model-text-engrave` (boolean union, raised text)
- Added auto-centering, manifold embed fix (0.5mm), legibility gate (LG-1…LG-6)
- Added legibility gate to `EngravingAgent` system prompt
- Final: "Terp Tribe HQ" 6mm Liberation Bold, 1.4mm depth, embossed, centered on front face
- STL: `printer-files/queue/Proxy_Stand_terp_tribe_hq_v5_embossed.stl` — Javier approved
— Claude

## 2026-06-02: BUG — Calliope nozzle_mcu cable loses comms under print vibration
- **System:** calliope
- **Severity:** high | **Status:** fixed
- **Root cause:** Sprite Pro extruder nozzle_mcu CAN/serial cable bundle goes intermittent under toolhead movement + thermal load. retransmit_seq skyrockets after ~500s, bytes_invalid spikes, Klipper triggers klippy_shutdown. Killed combined_jobs_2_3.gcode twice (jobs 000031, 000032) at 8-9min mark. Cable reseated at toolhead board and mainboard by Javier 2026-06-02. Monitor — if it recurs the cable assembly needs replacement.
- **Report:** `logs/reports/2026-06-02_bug-calliope-nozzle-mcu-cable-loses-comms-under-print-vibration.md`

*— Claude*

## 2026-06-02: RESEARCH — Calliope Error 3343 + nozzle_mcu Key561 Full Diagnostic
- Built `djinn-print-tracer` — 5s polling tracer capturing nozzle_mcu stats + XY position during prints
- Confirmed key561 is position-dependent: kills at Y=124–136 across all attempts (cable binding at max bed-forward position)
- Error 3343 (undocumented): likely strain gauge subsystem or dual-code artifact. Repair: re-seat 4 strain gauge connectors + hex screws, firmware audit (rollback 1.2.3.23 → 1.2.3.21 if needed)
- Djinn risk: gcode filenames with underscores trigger erratic V3 Plus behavior — enforce clean names in slicing pipeline
- Report: `logs/reports/2026-06-02_error-3343-calliope-diagnostics.md`

## 2026-06-02: FIX — PLA profile fan 100%→50%, cube-style start gcode
- Root cause of all Proxy Stand key561 failures: `bridge_fan_speed=100` in ender3-v3-plus.ini → M106 S255 at bridge infill → EMI kills nozzle_mcu
- Fix: capped all fan settings to 50%, start gcode now matches Creality cube style, bed 60°C
- Built djinn-print-tracer — real-time nozzle_mcu + XY position logger
- ProxyStandTF.gcode + ProxyStandTTHQ.gcode resliced clean (no supports, M106 S127.5)
- Report: logs/reports/2026-06-02_proxy-stand-print-diagnosis.md

## 2026-06-03
- SSH enabled on Calliope (root / creality_ender3v3, via Settings → Root Account Information)
- Moonraker upgraded v0.7.1 → v0.10.0 via Creality Helper Script (Guilouz)
- Fluidd installed on Calliope at http://192.168.1.113:4408
- Gcode Shell Command installed on Calliope
- OrcaSlicer 2.3.2 installed on Salomon via Flatpak
- Calliope printer profile written to OrcaSlicer
- Switching from PrusaSlicer to OrcaSlicer for all Calliope slicing
- All proxy stand STLs/gcodes scrubbed to blocked; fresh STL incoming
- Config backups on Calliope cleaned from 52 → 5
- nozzle_mcu key561 failure still unresolved — latest trace shows instant silence (bytes_invalid=0), NOT EMI pattern — likely physical connector or power issue on nozzle board

## 2026-06-03: Protocol Update + Slicer Role Split

- SUPPORT-GUIDE.md updated:
  - Triage: `bytes_invalid=0` at dropout = physical connector/power (NOT EMI) — fan cap is irrelevant for this pattern
  - Added 2-min cool-down rule between klippy_shutdown restarts
  - Added Slicer Setup section: OrcaSlicer for interactive, PrusaSlicer for CLI scripts, fan rule is hardware-wide
- PRINT-PROFILES.md updated: slicer role split + fan cap rule noted for both slicers
- Session report: `logs/reports/2026-06-03_protocol-update-orcaslicer-triage.md`
- Program audit: OrcaSlicer ✅ Flatpak, PrusaSlicer ✅ system, all djinn-* scripts intact

*— Claude*

## 2026-06-03: Fan Cap Applied System-Wide + Tornado Recycler Resliced

- `~/.config/forge/ender3-v3-plus.ini` — fixed: bridge_fan=100→50, max_fan=100→50, min_fan=100→50 (was the unfixed CLI pipeline profile)
- `~/.config/djinn/ender3-v3-plus.ini` — already fixed, no change needed
- OrcaSlicer `Calliope PLA` filament profile created: fan_max=50, fan_min=50, overhang_fan=50, bed_temp=60°C
- `Proxy_Tornado_Recycler_job1.gcode` resliced with fixed profile: M106 S127 only, no S255. In queue.
- Hardware: 4 strain gauge connectors re-seated (error 3343 — done by Javier). nozzle_mcu connector inspected (done by Javier).

*— Claude*

## 2026-06-03: Phase 5 — Router Simplification

- Created `/home/drmanzo/.local/bin/forge` — standalone Forge CLI (~175 lines), all `djinn forge *` subcommands
- Created `/home/drmanzo/.local/bin/terp` — standalone Terp Tribe CLI (~60 lines), all `djinn terp *` subcommands
- Slimmed `djinn` router: 736 → 533 lines. `forge|tf)` → `exec forge "$@"`. `terp|tthq)` → `exec terp "$@"`
- All three CLIs syntax-checked and smoke-tested. Delegation chain verified.

*— Claude*

## 2026-06-03: ProxyStand TTHQ Cursive Print
- Engraved "Terp Tribe HQ" DancingScript-Bold on 42.3mm bore proxy stand side; Z=2mm, 7mm text, 1.8mm depth, all legibility gates ✅
- Fixed `text_on_flat` group-centering bug in `djinn-model-text-engrave`
- Fixed `djinn queue` display: was calling `djinn-print queue`; now renders JSON queue inline
- Sliced job 6: 58m 17s, 19.86g, no supports, 5mm brim
- Print complete on Calliope; post-print nozzle MCU error (key561) cleared by firmware restart

*— Claude*

## 2026-06-04 — djinn-bore-core v2 — Claude
- Extended Marcus's v1 spec: auto-scale recovery, wall thickness check, Poisson reconstruction, support column scan
- Handles broken AI meshes (non-watertight, wrong-unit scale, multi-body)
- Full test: apple STL (2mm, 5 bodies, non-watertight) → ×46 scale → Poisson repair → bore → 5.1mm wall OK
- Installed: ~/.local/bin/djinn-bore-core | Source: djinn/printer/tools/djinn-bore-core.py

## 2026-06-04 — djinn-bore-core v3 + djinn-model-mark guard — Claude
- Proportion-preserving scale: two-zone (Z body-below, XY matched), auto-fallback to uniform if proportional footprint too narrow
- Maker's mark engraved on bore floor: 15mm, no mirror (viewed from above), 0.5mm depth
- djinn-model-mark: guard added — exits cleanly with message when input ends in _bored.stl
- Tested: apple STL end-to-end, mark engraved, guard fires correctly

## 2026-06-04: Applacrabus Print Failure
- Print cancelled mid-run: claw support collapsed (sparse 4.5mm grid insufficient)
- Vault note updated: status ON HOLD, print history added, corrected "no supports" → SUPPORTS REQUIRED
- Failure logged in FAILURE-LOG.md with root cause and reslice recommendations

*— Claude*

---

### 2026-06-04 — Camood TTHQ Tank Engraving

- Engraved "Terp Tribe HQ" DancingScript-Bold on flat back tank face of Camood
- Key fix: actual tank face at Y=51.553mm (ray-cast), NOT bounding box Y=54.09mm
- Tool pipeline: fontTools → shapely → trimesh.extrude_polygon → manifold3d boolean
- Result: 0.121 cm³ removed, 0.011 cm³/char (LG-3 ✅), watertight
- Output: `~/printer-files/library/engraved/terp-tribe/Camood_TTHQ_engraved.stl`
- Organized library: originals → terp-tribe subfolder, engraved/ dir created

*— Claude*

### 2026-06-04 — USER.md Update from Perplexity Ingest

- Read all 16 Perplexity exports from ~/Downloads/ (2026-06-04_*.md)
- Updated ~/.openclaw/workspace/USER.md: correct birth time 00:55, age 32, San Bernardino location, Psychology B.A. completed, Finance A.S. in progress, attorney career goal, weight in kg + gym/PT, archetypes (Wounded Healer/Fool/Hermit), Cade relationship, Faust CLI stack update
- Flagged astrological chart: Rising/Ascendant must be recomputed at 00:55 (old charts used 10:43am — WRONG)
- Moved all 16 Perplexity files to ~/Obsidian/RAW/perplexity-exports/

*— Claude*

## 2026-06-04: Salomon Printer-Files Cleanup
- Full audit and reorganization of ~/printer-files/
- Trashed 25+ junk/duplicate files (staging intermediates, recovery gcodes, duplicate ID-named folders for cup/proxy stand/vases, empty folders)
- Created library/bore-tools/ — bore measurement caliper/collar/gauge assets from models/
- Created library/unknown/ — 19 unidentified items with README
- Created library/originals/external/proxy-travel-pack/ — Puffco Proxy Travel Pack components
- Moved 7 Python generator scripts from models/ → scripts/
- Consolidated cup to library/cup/ (cup.3mf, cup_engraved_final.stl, cup_engraved_final_bored.stl, cup_geometry.stl/.gcode)
- ProxyStand_TTHQ_cursive_centered.stl → library/engraved/terp-tribe/ (canonical)
- tf_anvil_traced_*.stl → library/logos/
- models/ and staging/ are now empty

*— Claude*

## 2026-06-04: AUTO-STUB — slipbox--etting--enchmarks--or--nder-3--3--lus-md
- djinn-slipbox cross-linked: /home/drmanzo/Obsidian/i notes/Notes/Setting-Benchmarks-For-Ender-3-V3-Plus.md
- ⚠️ Full report not filed — stub at `logs/reports/2026-06-04_slipbox--etting--enchmarks--or--nder-3--3--lus-md-stub.md`
*— Salomon*

## 2026-06-04: Camood Job 9 — Maker Mark Fix & Reprint
- Fixed maker's mark mirror: switched from transform-matrix X-flip to explicit `verts[:,0] = -verts[:,0]` + face winding reversal (required for correct manifold3d boolean)
- Updated `camood_tthq_engrave.py`: source now reads from originals (not staging), output to canonical engraved path, bed-align inline
- Updated makers-mark.json path: library/logos/ (post-cleanup)
- Rebuilt camood_fixed_mark.3mf with new engraved geometry + original Z=50mm support blocker preserved
- Sliced 4× via prusa-slicer: 26h 26m · 457g PLA
- Job 8 cancelled (mark was mirrored). Job 9 printing on Calliope.

*— Claude*

## 2026-06-04 — OpenClaw Bootstrap Fix

- Diagnosed: `bootstrapTotalMaxChars: 15000` was silently dropping USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md (only AGENTS.md + partial SOUL.md loaded)
- Fixed: raised `bootstrapTotalMaxChars` → 60000, added `bootstrapMaxChars: 15000` per file in `agents.defaults`
- Gateway restarted; all 7 workspace files now load (49,653 chars total)
- Root cause: someone had set the total limit to 15000 (4× below the framework default of 60000)

*— Claude*

---

### 2026-06-05 — Downloads & Desktop Cleanup

- Inventoried 25 Downloads + 6 Desktop items; cleared all but 2 trivial leftovers
- Created `printer/library/originals/` directory tree (external + forge) matching README spec
- Moved 3D models: applacrabus (4 STLs), doctor-pen-holder, duff-beer-pen-holder, tardis (4 STLs, 2 creators), vases, calibration test, cup-engrave-project (STL + scripts)
- Moved personal docs: 2 PDFs → `personal/documents/`, 4 photos → `personal/photos/`
- Trashed: 5 redundant extracted zips, puffco proxy stand STL (vault duplicate), empty The_Forge stub, 67MB Telegram installer
- AI logo moved to `djinn/media/logos/`

*— Claude*

## 2026-06-05: djinn-detect-surfaces
- Built `~/.local/bin/djinn-detect-surfaces` — pre-flight surface scanner for engraving pipeline
- Uses histogram-peak ray-cast (6 directions × 400 rays), extracts flat panels from curved geometry
- Debugged: ray origin direction inversion bug (0 hits → fixed), vertex_defects property vs method
- Ran on Camood STL: back panel Y=51.305mm (2.79mm inset from bbox), confirmed manufacturer text on back
- Final Camood_TTHQ_engraved.stl = original + TF anvil bottom mark only (correct — no added text needed)

*— Claude*

## 2026-06-05: Camood TTHQ Engraving Fixed
- Identified clean Camood base from MakerWorld cup_stls.zip (14,726 faces, no mfg text) → saved to library
- Fixed `camood_tthq_engrave.py`:
  - `qCurveTo`: was linear interpolation → fixed to proper TrueType quadratic bezier
  - `glyph_polygons`: unary_union was filling holes → fixed via signed area (CW=outer, CCW=hole, subtract)
  - Added XY centering for non-origin exports
  - SOURCE_STL → Camood_clean.stl; DEPTH_MM 1.8 → 2.5mm
- Output: `Camood_TTHQ_engraved.stl` — watertight, 43,232 faces, legibility PASS
- Installed `rtree` (missing trimesh dep for ray_triangle spatial index)

*— Claude*

## 2026-06-05: Camood TTHQ x3 plate — support cap fix + job13
- Built `~/.local/bin/djinn-gcode-support-cap` — post-processor strips support extrusion above Z_MAX
- Debugged: 3MF SupportBlocker volume works for single instances but breaks with 3 build items; solved via gcode post-processing instead of 3MF format hacking
- Re-sliced 3× Camood with `--duplicate=3`, applied `djinn-gcode-safety` + `djinn-gcode-support-cap 50`
- `Camood_TTHQ_x3_job13.gcode`: 372g / 22h 29m / 536 layers / Z 0–107.3mm
- Support gates: 422k support lines below 50mm (kept), 0 above 50mm (stripped) ✓
- Safety: M220 S53 @ Z=90.1mm, PAUSE_PRINT @ Z=104.1mm ✓
- Awaiting Javier's go for upload to Calliope

*— Claude*

## 2026-06-05: job13 print started on Calliope
- Uploaded `Camood_TTHQ_x3_job13.gcode` (86.1MB) to Calliope via Moonraker
- Fixed upload path conflict (earlier upload created a directory with same name as file)
- Javier reviewed gcode, confirmed print — `POST /printer/print/start` → ok
- Print running: 3× Camood TTHQ, 372g, 22h 29m, pause at Z=104.1mm

*— Claude*

---

### 2026-06-05 — Djinn Gateway Phase 1

- Built `GATEWAY.md` — canonical enforcement contract (5 tiers, 3 modes, checkpoint flow, hard rules)
- Built `djinn-gateway` CLI: status, dev, reset, restrict, install-hooks, checkpoint, classify
- Installed pre-push hook in vault git repo — mechanically blocks all pushes in Standard mode
- Created `~/.config/djinn/session.json` — mode state file (Standard/Dev/Restricted + expiry)
- Wired GATEWAY.md into startup chain: CLAUDE.md, AGENTS.md, MARCUS-SESSION-BRIEF.md
- All 11 tier classification tests pass; git push block + COMMS post + Telegram notify verified

*— Claude*

## 2026-06-05: job14 single Camood + monitor upgrade
- Patched start_gcode: M220 S100 + M204 P2000 T2000 added to reset speed on fresh print starts
- djinn-print-monitor upgraded: Z zone alerts, speed factor tracking with XY, 5% step, 10s poll, first_layer_seen guard
- job14 uploaded and started (124g, 7h 25m, single Camood TTHQ)
- Two pauses observed: first stop at 10min (likely Klipper safety — not physical, not our PAUSE_PRINT), second was standard safe-park
- Speed came up at 20% after restart — M220 S100 doesn't re-run on resume from standby; Javier manually ramped to 100%
- Z too low after first restart — Z offset not re-applied on standby resume
- Print resumed and running as of session close

*— Claude*

## 2026-06-05: BUG-014 confirmed — Calliope nozzle_mcu cable
- E0003/key561 = Lost communication with MCU 'nozzle_mcu' — confirmed from klippy.log
- Happened 3× today: 14:24, 14:31, 15:34
- Triggered by wide XY travel (bed leveling mesh, multi-object plates) not height alone
- Physical fix required: re-route nozzle_mcu cable harness with adequate slack

*— Claude*

## 2026-06-05: Gateway Phase 1 + djinn-local-report

- Shipped GATEWAY.md behavioral contract (Marcus v2 canonical)
- Built djinn-gateway CLI: v2 session.json schema (timezone-aware ISO 8601), 5-tier classification, 3 modes
- Built pre-push hook: blocks Standard/Restricted mode pushes, posts COMMS checkpoint
- Shipped djinn-session-end v2: real commit messages from git diff --stat, zero LLM
- Shipped djinn-local-report: phi4:14b session reports via Ollama API, 6-section validation, fallback chain
- Fixed QUEUE.md corruption: broken sed marked all pending tasks done; fixed via targeted Python
- Claude dependency audit (TASK-066): 10 touchpoints mapped, 5 keep-claude, 3 local-model, 3 can-automate
- TASK-067 done, TASK-068 done, TASK-069 pending

*— Claude*

## 2026-06-05 — Calliope reset + Creality motion defaults
- Adopted Creality Print motion settings in ender3-v3-plus.ini: SET_VELOCITY_LIMIT ACCEL=2000 ACCEL_TO_DECEL=500 SQUARE_CORNER_VELOCITY=5, SET_PRESSURE_ADVANCE ADVANCE=0.042
- Patched Calliope sensorless.cfg: suppressed key404 Y homing error on power loss recovery
- Full config backup saved: ~/Obsidian/djinn/printer/calliope-config-backup-2026-06-05/
- Factory reset attempted but blocked by Z probe mismatch; reverted to working printer.cfg
- KEY FINDING: all 11 key561 dropouts occurred at Z < 10mm — cable connector issue, not routing
- Calliope calibration run: CX_ROUGH_G28 → ACCURATE_G28 → BED_MESH_CALIBRATE → SAVE_CONFIG
- OrcaSlicer adopted as STANDARD slicer — PrusaSlicer relegated to diagnostic/CLI
- djinn-gcode-safety v2: M106 fan capping added (caps ALL M106 to S128 max across any slicer)
- Orca production profile created: fan cap 50%, Creality-compatible settings
- Docs updated: PRINT-PROFILES.md, SUPPORT-GUIDE.md, DJINN-3D-PRINT-PIPELINE.md, PRINTER-MANUAL.md

## 2026-06-05: Typhon Gateway Deploy + SSH Fix
- Created `djinn/memory/` store with Typhon authority write gateway
- Fixed SSH to Typhon: IP changed 192.168.1.113 → 192.168.1.150, created `~/.ssh/config`
- Deployed `djinn-typhon-write` to Typhon `~/.local/bin/` — hostname enforcement fixed for `tftthq`
- Verified end-to-end: `--status` + `--write` test on Typhon confirmed (current + history store)
- Rebased divergent git branches (Orin heartbeat onto memory store commit), pushed under Dev mode
- Updated PROTOCOL.md SSH IP, fixed `djinn-typhon-write` hostname check

## 2026-06-05: Camood TTHQ Test Print — Typhon pipeline E2E test
- Sliced single Camood TTHQ via OrcaSlicer CLI (Production profile, organic supports, buildplate-only)
- Applied djinn-gcode-safety (23 M106 S255→S128, M220 S53 at Z≥90mm, PAUSE at Z≥104mm)
- Applied djinn-gcode-support-cap 50 (32531 support lines stripped above Z=50mm)
- Uploaded to Calliope via Moonraker, print started ~21:50 UTC (state=printing, 15h 22m)
- Submitted state update request to `memory/requests/` for Typhon processing
- Fixed Moonraker upload path: root-level path required, not `gcodes/` subdirectory
- ECO temp override diagnosed: Creality CX_ROUGH_G28/ACCURATE_G28 reduce nozzle to 130°C for probing; M109 S220 after START_PRINT re-heats. Orca's non-wait bed temp (M140) races with macro; PrusaSlicer's wait (M190) works.
- BUG-014 recurred: 12th nozzle_mcu dropout at Z=4.2mm, 20 min into job17. Connector reseat didn't permanently fix. Blocks all prints.
- PrusaSlicer CLI profile confirmed working for ECO bypass — slicing, gcode-safety, upload, print start all succeeded. Temp stable at 220°C throughout active print.
- SSH access to Calliope confirmed (root/creality_ender3v3). Read printer.cfg, gcode_macro.cfg, printer_params.cfg for debugging.

## 2026-06-05: Camood TTHQ Job17 — ECO solved, nozzle_mcu still blocking
- Creality ECO temp override diagnosed and worked around via PrusaSlicer start gcode structure
- PrusaSlicer CLI sliced Camood_TTHQ_job17 with djinn-gcode-safety post-processor (fan S128, speed M220 S53, PAUSE)
- Print started, ran ~20 min at 220°C, reached Z=4.2mm
- nozzle_mcu disconnect at 22:34:33 PDT — BUG-014 recurrence (12th dropout)
- Power-loss recovery attempted but stuck (empty filename in recovery state) — print cancelled
- Second restart cancelled by user
- User started `ksr_fdmtest_v4` — print running past previous failure point (32+ min, stable at 220°C/60°C). nozzle_mcu dropout was intermittent, not guaranteed.

*— Salomon*

## 2026-06-06: Hermes Agent onboarded as Assistant + global LLM client built
- djinn/core/llm.py: platform-level LLM client (Ollama + Groq backends, unified env-var switching)
- AGENTS.md updated with Assistant lane (Hermes framework, skill dev + docs + process engineering)
- ~/.hermes/skills/djinn-assistant/SKILL.md: Hermes skill definition for Assistant agent
- Marcus TASK-067 delivered: comprehensive gap analysis, 17-item roadmap, 5 priority domains
- Hermes hit Ollama session rate limit mid-session (nemotron-3-super:cloud, free tier cap)

*— Claude*

## 2026-06-06 — Fleet Model Audit + Orin Integration

- SSH connected Orin (192.168.1.176 / javiermanzo) to Djinn fleet
- Built djinn-route: automated task→model→machine routing (11 task types, Orin fallback)
- djinn/ROUTING.md: full rewrite with fleet table, djinn-route docs
- djinn/INFRASTRUCTURE.md: Orin added (i7-7700K, 40GB, macOS Sequoia)
- Salomon RAM crisis fixed: removed qwen3.6:latest (26GB → 14GB free, 0 swap)
- Model audit complete — 1 redundancy found and removed: phi4:14b on Orin (GPU version on Salomon is canonical)
- Typhon qwen2.5:7b restored (was missing, caused OpenClaw breakage)
- Hermes config fixed on both Salomon and Orin (default model, profile config)
- AGENTS.md corruption fixed (Hermes wrote literal \n instead of newlines)

*— Claude*

- **2026-06-06** — djinn-tablet CLI built; Samsung Galaxy (R52T10BL3BV) detected via MTP; udev rules installed; scrcpy mirror, file push/pull, and ADB dashboard delivery ready. Awaiting USB debugging enable for ADB features. — Claude

- **2026-06-07** | Tab S7 FE bootstrap — Ubuntu proot, SSH :8022, vault cloned, Gateway Standard mode | Claude

## 2026-06-07 — Privacy Sweep
- Bulk replaced Sabrina/Sammy → Mira, Ashton → Cade across 26 vault files + 10 RAW exports + memory files
- Renamed 2 love letter files, renamed 1 RAW file
- Fixed duplicate dict key and list entry in QUEUE.md after replacement
- Final scan: zero remaining hits for any target name
- Pushed: commit 8d9bce1
— Claude

## 2026-06-07 — djinn-gate v1 + spec-v1.0 batch

- Shipped djinn-gate CLI (gate.py + routing.toml) — 9 lanes, phrase/keyword routing, exit 0/1, optional HTTP :7070
- Shipped delta_guard.py — stateless timer deduplication via SHA-256 state comparison
- Added profile system to djinn.core.llm.chat() — required param, raises ValueError on missing/invalid
- Heartbeat push now guarded by delta_guard — fires only when system metrics change
- GATEWAY.md updated with lane discipline as enforced rule — Claude invocation gated behind djinn-gate

— Claude

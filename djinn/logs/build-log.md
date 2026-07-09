---
subject: Djinn Operations
tags: [djinn, build-log]
created: 2026-05-19
---

# Build Log

## 2026-06-27: Pyraxis grammar and flow pass complete — all 4 drafts
- 57 total fixes: Prologue (9), Ch1 (6), Ch2 (9), Ch3 (33)
- Verantus three-point arc documented in CONTINUITY.md
- ⚠️ Ch1 grandfather/Verantus duty-speech edit lost in merge — needs restoration
- All pushed to main vault and GitHub

## 2026-06-11: PrusaSlicer fully removed from pipeline. djinn-model-slice now opens models in Creality Print GUI for manual slicing. All PrusaSlicer configs purged.

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

## 2026-07-03 — Bambufy on Iris + Slicer Profiles on USB — Claude

- **Bambufy plugin** installed and wired on Iris (AD5X @ 192.168.1.50): 27 macros active, waste-optimized multi-color printing
- **bambufy.cfg** (2144 lines) manually deployed to Iris after ENABLE_PLUGIN failed to wire it into plugins.cfg
- **position_endstop** in printer.base.cfg commented for stepper_z (bambufy requirement)
- **min_version** lowered 1.2.3→1.2.2 to match existing slicer gcode
- **shoot_y_position=223** causes "Move out of range" errors on long retractions — lowered to 218 temporarily, reverted to 223
- **Bambu Studio AppImage** (v02.07.01.62, 217MB) installed on Salomon at `~/BambuStudio.AppImage`
- **Typhon USB** rebuilt with full djinn/: bambufy-setup.md, two 3MF templates (Bambu Studio + Orca), OrcaSlicer profiles for Nemesis and Iris, slicer installers, SSH recovery script, Salomon prompt
- **Iris SSH** verified (root/root), Moonraker API confirmed working
- **Known issue:** `_START_BAMBUFY` delayed gcode doesn't load on this Klipper version — init must be triggered manually after restart

*— Claude*

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
- Rebased divergent git branches (Orion heartbeat onto memory store commit), pushed under Dev mode
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

## 2026-06-06 — Fleet Model Audit + Orion Integration

- SSH connected Orion (192.168.1.176 / javiermanzo) to Djinn fleet
- Built djinn-route: automated task→model→machine routing (11 task types, Orion fallback)
- djinn/ROUTING.md: full rewrite with fleet table, djinn-route docs
- djinn/INFRASTRUCTURE.md: Orion added (i7-7700K, 40GB, macOS Sequoia)
- Salomon RAM crisis fixed: removed qwen3.6:latest (26GB → 14GB free, 0 swap)
- Model audit complete — 1 redundancy found and removed: phi4:14b on Orion (GPU version on Salomon is canonical)
- Typhon qwen2.5:7b restored (was missing, caused OpenClaw breakage)
- Hermes config fixed on both Salomon and Orion (default model, profile config)
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

## 2026-06-07 — Phase 4 Salomon wire-in (delta_guard + gate)

- vault-sync: git push now delta-guarded (vault_commit_hash + uncommitted_files)
- comms-processor: djinn-gate routes tasks before opencode; ops lane skips LLM; delta_guard on push
- djinn-ctx-router: tick() only fires when vault commit hash changes
- djinn-clerk: delta_guard at scan level (RAW/ file count)
- printer-error-logger: watchdog/history checks gated on printer state change
- djinn-comms-compact: new script + systemd timer (daily 03:00) — archives COMMS.md monthly
- typhon-heartbeat.sh: written to vault, ready to deploy on Typhon

— Claude

## 2026-06-07 — API Reduction Sprint (TASK-001, Batches 1-4)

**Batch 2 (implemented this session):**
- llm.py: TOKEN_PROFILES + TEMP_PROFILES per task type, task_type param on chat()
- comms-processor: mtime guard (~/.cache/djinn/comms-last-mtime)
- djinn-daily: no-op short-circuit (queue empty + no carry from yesterday)
- design_gen.py: DESIGN_MODEL = qwen2.5-coder:7b

**Batch 3:**
- djinn-ctx-router: per-tick session activity guard (loginctl + pgrep)
- djinn-vault-indexer: mtime gate before file walk
- embed_cache.py: shared SQLite cache (sha256 key), wired into djinn-embed + djinn-slipbox
- djinn-clerk-watch: watchdog-based RAW/ watcher, replaces 1-hr timer
- printer-error-logger: last-printer-error dedup

**Batch 4:**
- djinn-weekly: daily notes digest (headers + [ ] items only, -60-70% tokens)
- djinn-session-end: auto-generates SESSION-RESUME.md on close
- llm.py: Groq default → llama3.1-8b-instant, 70B opt-in only
- llm.py: TIMEOUT_PROFILES (status:12s, embed:8s, quote:10s, design:60s, default:120s)

— Salomon

## 2026-06-07: BUG — clerk-watch wrong RAW_PATH
- **System:** clerk
- **Severity:** low | **Status:** fixed
- **Root cause:** djinn-clerk-watch pointed at ~/Obsidian/djinn/RAW (doesn't exist) instead of ~/Obsidian/RAW (actual location). All file moves to perplexity-exports subdir also missed since recursive=False.
- **Report:** `logs/reports/2026-06-07_bug-clerk-watch-wrong-raw-path.md`

*— Claude*

## 2026-06-08 — TASK-070 Audit (Claude)

- Audited all four TASK-070 fixes
- Fixes 2/3/4 already applied in vault (VAULT_PATH defaults + vault-integrity exit code)
- Fix 1 (djinn-route Typhon IP .113→.150) noted in COMMS for Salomon — script not vault-tracked
- TASK-070 marked done

— Claude

## 2026-06-08 — KSR FDM test print on Calliope (Salomon)

- Uploaded and started `ksr_fdmtest_v4_by_Autodesk_1h58m.gcode` (10MB) from USB drive
- Moonraker was down initially (printer had just rebooted) — recovered
- Added job 10 to `print-queue.json`, started `djinn-print-monitor` background poller (PID 666681)
- Logged to COMMS.md

— Salomon

## 2026-06-08 — Virtual Ender-3 V3 Plus (Claude)
- Built virtual printer on Salomon: Docker + SimulAVR + real Klipper + Moonraker
- Config: CoreXZ, 300×300×330, bed mesh 6×6, PA=0.04, input shaper EI
- Wired into `forge printer [start|stop|status|...]`
- Systemd auto-start: `djinn-virtual-printer.service` enabled
- API live at localhost:7125 — full Moonraker interface
- Doc: `djinn/printer/VIRTUAL-PRINTER.md`

— Claude

## 2026-06-08 — Engraved Cup → Terp Tribe Folder (Claude)
- Copied existing engraved cup files to `printer-files/library/engraved/terp-tribe/`
- Files delivered: `Camood_TTHQ_engraved.stl` (latest, DancingScript-Bold 9mm/2.5mm back tank), `cup_engraved_final.stl`, `cup_engraved-Terp Tribe HQ.3mf`, `cup_geometry.stl`, `ENGRAVING-README.md`
- Originals untouched — user switched to Creality slicer, avoiding OrcaSlicer 3MF conflicts
- Report: `logs/reports/2026-06-08_engraved-cup-to-terp-tribe.md`

— Claude

## 2026-06-08 — Slicer Migration to Creality Print (Claude)
- Full migration: OrcaSlicer + PrusaSlicer archived, Creality Print standardized
- Built `djinn-print-track` — permanent systemd service silently logging all prints via Moonraker (progress, temps, Z, speed, filament, errors, outcome)
- Archived all old slicer artifacts to `printer-files/archive/slicer-legacy-2026-06-08.7z` (password-protected, AES-256)
- Removed: OrcaSlicer config (100MB), PrusaSlicer config (5.4MB), Orca AppImage (119MB), squashfs-root (367MB), ender3-v3-plus.ini, calliope-orcaslicer.md, 4 pipeline scripts (djinn-model-slice/combine/consult/gcode-safety)
- Updated 11 vault docs to reference Creality Print
- Live Camood TTHQ print undisturbed at 12%
- Report: `logs/reports/2026-06-08_slicer-migration-creality-print.md`

— Claude

## 2026-06-08 — Official Terp Tribe cup (Claude)
- Camood_TTHQ_engraved.stl print completed: 160min, 89g PLA, 165mm Z
- Tagged as official Terp Tribe cup production piece in `print-track/prints.json`
- Data captured: progress 0-100%, filament 29,813mm, bed temps, Z profile
- Next prints tracked automatically by `djinn-print-track` systemd service

— Claude

## 2026-06-08 — djinn-print-track v2 WebSocket Rewrite (Claude)
- Rewrote `djinn-print-track` (393→882 lines): HTTP polling → Moonraker WebSocket subscription
- Fixed delta state management: Moonraker sends partial updates — persistent `_ws_state` merge
- Added queue bridge: auto-creates/finalizes `print-queue.json` entries on print start/end
- Added filament auto-deduction: `filament-inventory.json` with single-spool model, <100g alert
- Added structured print records: auto-generates `prints/YYYY-MM-DD_ModelName/` directory
- Added atomic writes (`os.replace` after `fsync`) + 3-gen rotating backups + auto-heal on read
- Added `verify`, `spool`, `backfill` CLI commands
- Fixed `mm_to_grams` formula bug (missing mm→cm conversion — 889g→89g)
- Live-tested: CRtestcube (26min) — all 4 closures fired automatically
- Backfilled Terp Tribe cup (job 1, 89g) for continuity
- Report: `logs/reports/2026-06-08_djinn-print-track-v2-rewrite.md`

— Claude

## 2026-06-09 — Discord Print Flow Fix (Claude)
- Fixed watcher.py: customer no longer sees "slice N..." prompt; auto-slices after A/B/C + color reply
- Added sha256 dedup to djinn-model-fetch (prevents duplicate jobs from same file)
- Created djinn-model-slice: PrusaSlicer-based headless slicer with profile settings
- Created ender3-v3-plus.ini flat config for PrusaSlicer
- Cleaned print queue: archived 9 stale jobs, kept job 9 (currently printing)
- Note: OrcaSlicer/CrealityPrint CLI headless still broken; PrusaSlicer is the fallback

## 2026-06-10: Hellhound v1 — Pup Daemon Runtime (commit e35832a, DrManzo/djinn-vault main)

- `hellhound.py` — async Unix socket server, pup registry, SQLite indexer, vault timeline scribe, RECALL-on-shutdown
- `pup.py` — PupClient context manager: CONNECT handshake, observe(), wait_recall(), background heartbeat loop
- `pup-gateway.py` — Discord gateway pup + StubGateway (10s synthetic observations for pipeline testing)
- `pup-template.py` — enforced new-pup template (heartbeat + RECALL mandatory)
- `gates/base.py` — BaseGate abstraction (connect/stream/disconnect): swap transport without touching core
- Cortex pipeline: commander (→QUEUE), scribe (→vault), watchdog (patrol/anomaly), synapsis (stub), linker (backlinks)
- Effectors: alerter, archiver (gzip rotation + SQLite compaction), effector/scribe shim
- Systemd: hellhound.service + hellhound.socket + pup@.service (template unit)
- CLI: `hellhound status|send|recall|log|patrol|pup new`
- Vault MOC: skull/vault-hellhound/_index.md
- Installation pending on Salomon (QUEUE task awaiting Javier approval)

*— Claude*

## 2026-06-14: AUTO-STUB — slipbox--aust--li--verview-2026-06-14-md
- djinn-slipbox cross-linked: /home/drmanzo/Obsidian/i notes/Notes/Faust-Cli-Overview-2026-06-14.md
- ⚠️ Full report not filed — stub at `logs/reports/2026-06-14_slipbox--aust--li--verview-2026-06-14-md-stub.md`
*— Typhon*

## 2026-06-14: AUTO-STUB — slipbox--jinn--nfrastructure--reakdown--nd--ithub--ccess--etup-md
- djinn-slipbox cross-linked: /home/drmanzo/Obsidian/i notes/Notes/Djinn-Infrastructure-Breakdown-And-Github-Access-Setup.md
- ⚠️ Full report not filed — stub at `logs/reports/2026-06-14_slipbox--jinn--nfrastructure--reakdown--nd--ithub--ccess--etup-md-stub.md`
*— Typhon*

## 2026-06-14: Print Pipeline Full Audit + Repair — Claude

### Built
- `djinn-job-add` — new script bridging marked STL → print queue (confirmed status)
- `djinn-print-track`: fixed Calliope IP (113→114), added `tg_notify()` on completion, added `main_queue_finalize()` to sync main queue on print end, added `discord_notify()` for customer completion mention
- `djinn-discord-gateway`: fixed status filter `needs_review`→`needs_settings`, wired `djinn-model-mark` into customer profile-pick flow, saved `customer_discord_id` to queue entry, removed URL detection (attachments-only intake)
- `djinn-print-monitor-v2`: fixed Calliope IP (113→114)
- `heartbeat`: added `--autostash` to `git pull --rebase` to handle dirty working tree
- `djinn-ctx-router`: fixed `NameError: pathlib` (should have been `Path`)

### Killed
- `djinn-discord-watcher` — disabled+stopped (duplicate of gateway attachment handler, Javier-only, caused double fetch)
- `djinn-marcus-sync` — removed service, timer, and script (Selenium scraper for Perplexity; fragile, not needed since exports are downloaded manually)

### Decisions
- OrcaSlicer fully removed; Creality Print CLI is sole slicer
- Commission intake: attachments-only, no URL scraping — simpler for customer and Javier
- Calliope confirmed at 192.168.1.114 (not .113 which is Typhon)

*— Claude*

## 2026-06-14: snap Command + Webcam Pipeline Fix — Claude

### Built
- `djinn-discord-gateway`: `snap`/`snapshot` command in `#3d-printing` — posts live AKASO frame from `latest.jpg`
- `djinn-webcam-monitor`: writes `~/Videos/print-monitor/snapshots/latest.jpg` every 10 s for on-demand snap
- `djinn-webcam-monitor`: fixed `_open()` — reverted to integer index (V4L2 backend rejects string paths), added explicit `cap.release()` on failed open to prevent zombie fd hold

### Bugs Fixed
- V4L2 "can't be used to capture by name" — root cause: string path `/dev/video2` rejected by V4L2 backend; fix: `cv2.VideoCapture(idx, CAP_V4L2)` integer form
- Device busy on service restart — root cause: failed VideoCapture held fd without releasing; fix: explicit `cap.release()` before returning False
- Zombie old process blocking camera after service restart — cleared with `kill`; added explicit release in code to prevent recurrence

*— Claude*

## 2026-06-14: djinn-design Boot Fix — Claude

### Fixed
- `openai` missing from `~/.venvs/djinn-orchestrator` — installed `openai==2.41.1`
- `weighted_median` missing from `commissions/price.py` — added alias `weighted_median = _market_median` (function existed under private name)
- `~/.local/bin/djinn-design` `--status` handler called `orchestrator.run("status")` instead of `_show_queue()` — creating a stale job on every status check; fixed to call `_show_queue()` directly

*— Claude*

## 2026-06-14: djinn-design Pipeline Routing Fixes — Claude

### Fixed
- `orchestrator.py`: `--job N --full` was calling LLM classifier on the job note → classified as "new_design" → design_gen re-ran unnecessarily. Fix: when `auto_advance=True` + `job_id` set, intent = "auto" and routing is handled entirely by `auto_advance and state.status == X` conditions.
- `orchestrator.py`: price agent never ran in `--full` mode. Root cause: `plate_nest.run()` sets `state.status = "priced"` before the price trigger at line 172 checks `state.status == "plate_nest"` — that check was always False by the time it ran. Fix: capture `_pre_plate_status = state.status` before `plate_nest.run()` and use that captured value for both the plate and price triggers.

*— Claude*

---

## 2026-06-14 — Design Pipeline Render Fix & Design-to-Print Bridge

### Root Cause: OpenSCAD Render Failures
Diagnosed: `design_gen.py` LLM prompt was producing SCAD that called `sd_card_holder()` and `fillet_all()` — modules never defined in the file. OpenSCAD emits "Ignoring unknown module" warnings and produces empty geometry (0-byte STL). `proto_opt.py` was silently falling back to storing `.scad` paths instead of `.stl`, which then crashed `plate_nest` (`trimesh.load()` → `NotImplementedError: file_type 'scad' not supported`).

### Fixed
- `design_gen.py`: Strengthened SYSTEM prompt with explicit rules — every called module must be defined in-file, no `fillet_all()`/undefined helpers, top-level call only uses defined modules, mental trace requirement.
- `proto_opt.py`: `_render_stl()` now returns `(ok, stderr)`. On render failure: logs actual OpenSCAD stderr, raises `RuntimeError` with diagnostic hint. Never stores `.scad` path in `files[]` anymore.
- `orchestrator.py`: Catches `RuntimeError` from proto_opt, prints readable error + fix instructions, returns state gracefully.
- `djinn-model-slice`: Fixed DOE key: `job.get("doe_profile") or job.get("doe")` (was `job.get("doe")` — always empty for design jobs → defaulted to `production` tier instead of `proto`).

### Validated
Full pipeline: `djinn-design "small SD card holder, 4 slots, PLA, wall mount" --full` → job2/priced in one shot. `djinn-model-slice 2` → tier=proto, plate_stl resolved, slicer invoked correctly. Bridge is connected.

*— Claude*

## 2026-06-14: COMMS noise reduction (5-step Marcus spec) implemented.
- 5 git-push callers patched with `export DJINN_AGENT` (fixes `unknown` agent tag on checkpoints)
- `djinn-gateway` COMMS_FILE → CHECKPOINTS.md; Clerk/Slipbox redirected to PIPELINE.md
- `djinn-checkpoint-cleanup` built and run: 105 stale PENDING → TIMEOUT_DENIED
- `djinn-comms-rotate` + systemd timer installed (Sun 03:00 UTC weekly)

*— Claude, 2026-06-14*

## 2026-06-14: BUG — CrealityPrint v6+ CLI --slice 0 segfault
- **System:** forge-slicer
- **Severity:** high | **Status:** wont-fix
- **Root cause:** Null pointer dereference in Slic3r::GUI::PartPlate::set_shape (offset 0x9d8) when '--slice 0' is used with printers that have 'support_multi_bed_types: 1' set. Present in ALL v6.x Linux builds (v6.1.2 through v7.1.1 tested). v5.1.7 has no headless CLI. Migrated to Orca Slicer v2.3.2.
- **Report:** `logs/reports/2026-06-14_bug-crealityprint-v6-cli-slice-0-segfault.md`

*— Claude*

## 2026-06-15: Gateway secrets cleanup + Telegram help update

- Removed hardcoded Discord + Telegram tokens from `djinn-discord-gateway` and `djinn-webcam-monitor`
- Created `~/.djinn.env` (chmod 600, not git-tracked); all three service files updated with `EnvironmentFile=`
- `djinn-telegram-gateway` `handle_help()` rewritten: all owner commands listed, organized by category
- All three services restarted, confirmed active

*— Claude*

## 2026-06-16 — djinn-publish pipeline suite
- Built all 14 tools from TASK-070 spec: health checks, style audit, export (DOCX + Atticus), tracking
- Converted Prologue + Ch1–Ch3 from PDF/txt to canonical Markdown (13,341 words total)
- Seeded style_guide.md from vault worldbuilding notes
- Standalone repo at ~/djinn-publish/ (separate from Obsidian vault to avoid merge conflicts)
- Both DOCX exports generated and verified (editorial 74KB, Atticus 73KB)

## 2026-06-16 — djinn-paper Phase 1 MVP
- Academic writing agent: raw draft → APA 7 or MLA 9 formatted paper + compliance report
- Rule-based Reference Builder passes spec canonical test cases (APA + MLA)
- DOCX Format Enforcer: title page, heading styles, hanging-indent references
- LLM pass via Ollama (qwen2.5:7b default); --no-llm flag for offline/reference-only use
- Global CLI: `djinn-paper <draft.txt> --style APA7|MLA9 --sources sources.json`
- Standalone repo at ~/djinn-paper/

*— Claude*

## 2026-06-17 — Kraken Proxy Pipe Set
- Repaired non-manifold Meshy AI Kraken2 3MF with manifold3d
- Scaled 0.8113× (38.7/47.7mm) to Proxy Core spec
- `Kraken_original.stl` — clean reference
- `Kraken_core.stl` — maker's mark on cup floor (un-mirrored cutter, interior)
- `Kraken_pipe.stl` — three-segment vapor path: mouthpiece r=4 + vertical r=5 to Z=80mm + angled cup entry r=4 + exterior mark
- `proxy-pipe-presculpted.md` workflow formalized
- mesh_repair_agent: manifold3d added as step 2 primary fixer for complex organics

*— Claude*

## 2026-06-18 — Blender Integration (TASK-081 + TASK-082)
- `djinn-blender-repair` — headless STL cleanup wrapper; calls blender/scripts/repair.py; 120s timeout; report JSON written alongside output
- `djinn-blender-render` — headless product render wrapper; EEVEE/Cycles; JPEG/PNG from extension; 300s timeout; fallback 3-point rig when no brand .blend
- Tested on Kraken_pipe.stl (1.74M faces): repair ✓ manifold, render ✓ 4.16s EEVEE 38KB
- Fixed 4 bugs in Marcus's scripts: --report arg mismatch, BLENDER_EEVEE_NEXT name, PNG format hardcoded, os.makedirs empty dirname
- TASK-081–085 written to QUEUE.md; TASK-085 = gateway build-command fix

*— Claude*

## 2026-06-19 — Blender A-2 architecture + TASK-086–091 queued

- Architecture review: classified all new features across addon / headless / djinn / slicer
- QA severity model defined: critical (exit 1) / warning (exit 0) / info
- TASK-086: non-manifold check operator (addon)
- TASK-087: mesh cleanup operator — merge/fill/loose (addon + repair.py update)
- TASK-088: align-to-bed operator (addon)
- TASK-089: mesh info panel — bounds, volume, weight estimate (addon)
- TASK-090: rename/version stamp operator (addon)
- TASK-091: djinn-blender-qa + qa_check.py headless script (B-3)
- PLAN-blender-integration.md updated with tiered classification and design constraints

*— Claude*

## 2026-06-20 — Penelope online (Ender 3 Pro)
- OctoPrint 1.11.7 running as djinn-penelope.service on Salomon port 5001
- djinn-penelope CLI live: status/upload/print/cancel/files
- Calliope IP drift fixed: 14 scripts updated from .113 → .114
- Klipper compiled (ATmega1284P) but not flashed — bootloader timeout too short via USB
- Upgrade path: USBASP ISP programmer → flash ~/klipper/out/klipper.elf.hex

## 2026-06-20 — Penelope (Ender 3 Pro) full integration + OrcaSlicer profiles

- OctoPrint 1.11.7 installed (Python 3.11 venv) as `djinn-penelope.service` on Salomon port 5001
- `djinn-penelope` CLI: status / upload / print / cancel / files / temps
- OctoPrint 1.11.x API auth bug fixed: global key read-only for writes → created `djinn` admin user, user-specific API key written to users.yaml
- `accessControl: false` set in OctoPrint config (local machine, no network exposure)
- OrcaSlicer process profile created: `Penelope-Standard.json` (inherits `fdm_process_creality_common`, Creality Ender-3 Pro 0.4 nozzle, 0.2mm, 20% grid, Bowden speeds)
- OrcaSlicer PLA filament profile created: `Penelope-PLA.json` (inherits `Creality Generic PLA`, `cool_plate_temp` bed fields, retraction 5.5mm Bowden-corrected, vol speed capped 9mm³/s)
- Calibration cube (20mm) sliced (21m41s), uploaded to Penelope — awaiting print approval
- Calliope IP drift fixed: 14 scripts + 3 vault docs updated 192.168.1.113 → 192.168.1.114
- Klipper compiled for ATmega1284P (ready at `~/klipper/out/klipper.elf.hex`); flash path requires ISP programmer
- PRINT-PROFILES.md, SYSTEM-STATE.md, INFRASTRUCTURE.md all updated with Penelope specs

*— Claude*

## 2026-06-21 — Penelope Mario Pipe + Z Offset

- Fixed OctoPrint checksum resend loop: `alwaysSendChecksum` disabled, `neverSendChecksum: true` — Creality Marlin handles natively
- Discovered Creality Print V7 gcode uses Klipper macros (START_PRINT, EXCLUDE_OBJECT, SET_VELOCITY_LIMIT) — incompatible with Penelope Marlin, silently fails
- Created `Penelope-Standard-TreeSupports.json`: tree(auto) supports, 30° threshold, 8mm brim
- Mario pipe printed successfully: 174 support sections, brim gripped, completed
- Z offset diagnosed via live babystepping: -0.5mm total, saved to EEPROM (M851 Z-0.5 + M500)
- OrcaSlicer desktop launcher added: `orca-slicer.desktop` + `/usr/local/bin/OrcaSlicer` symlink
- `~/Desktop/Review/` created as mandatory print intake gate

*— Claude*

## 2026-06-21 — Penelope profiles finalized

- All Penelope OrcaSlicer profiles updated: gyroid infill, 14% density, 220°C hotend
- Retraction kept at 5.5mm (Bowden validated)
- Tree(auto) supports standardized for all support profiles (30° threshold, 1 wall)
- Penelope-Standard-TreeSupports: 8mm brim added
- ~/Desktop/Review/ established as mandatory intake gate
- Stock OrcaSlicer profile validated via test print — clean infill, uniform extrusion

*— Claude*

## 2026-06-21 — Writing Workspace Build

- Created `djinn/workspaces/writing/projects/aethoria/` — separate project for Victorian fantasy (Corvus, Thorne, Ironhaven, Essence magic)
- WORLDBUILDING.md — all 10 Aethoria worldbuilding notes consolidated directly (geography, politics, society, economy, magic, religion, military, education, transportation, international relations)
- CHARACTERS.md — Corvus Shadowblade + Master Thorne profiles
- Dominion of Pyraxis: CHARACTERS.md (Raxz, Javelin, Brax, Arctus, Marcella + all Nine Houses) + STORY-NOTES.md (all Story-Critique content)
- Black Book: SESSIONS.md (template + all known sessions indexed) + FAUST.md (full gnome necromancer mythology)
- Draft staging files created for both books — clean files where prose goes
- Downloads/Writing removed (was entirely symlinks)
- Vault is now exclusive writing environment

*— Claude*
## 2026-06-21 — Pyraxis Chapter Pipeline
- Transcribed and cleaned all 4 Dominion of Pyraxis source files (Prologue, Ch 1, Ch 2, Ch 3) into vault draft format
- Ch 2 and Ch 3 are near publication-ready; Ch 1 needs prose revision pass; Prologue needs structural rewrite
- Created Editorial/PIPELINE-NOTES.md — full developmental + line edit pass for all chapters
- Updated CONTINUITY.md: locations table, historical facts, Faust facts, corrected chapter numbering
- Updated CHARACTERS.md: Faust physical/backstory details, Lord Theron (House Vandris — new, not in Nine Houses table)
- Session report: djinn/logs/reports/2026-06-21_pyraxis-chapter-pipeline.md


## 2026-06-25 — Penelope Calibration & Mario Pipe Print Run
- OctoPrint 1.11.7 → 1.11.8, API key rotated
- Penelope gcode pipeline fixed: OrcaSlicer + Penelope-Standard-TreeSupports profile (Marlin), not Creality Print
- M851/M290 confirmed non-functional on stock Ender 3 Pro without probe; physical endstop calibration is correct fix
- Mario pipe printed on both Penelope and Calliope
- LAW: never send any command to either printer while running
- Next: Pi Zero 2W → Klipper upgrade for Penelope

## 2026-06-27 — Pyraxis TTS Reader

- Built `djinn-pyraxis-listen` CLI tool — text-to-speech reader for all Dominion of Pyraxis chapters
- Installed edge-tts 7.2.8 (pip3 --user); uses Microsoft Edge TTS servers (online)
- Default voice: en-US-GuyNeural (Passion/Novel); configurable via --voice flag
- Strips markdown, frontmatter, and draft notes before synthesis; audio via ffplay
- Reads: Prologue, Ch1, Ch2, Ch3, lore files; interactive picker or direct invocation
- Session report: djinn/logs/reports/2026-06-27_pyraxis-tts-reader.md

*— Claude*


## 2026-06-28 — Camood PETG Print Run
- `Camood_TTHQ_engraved.stl` PETG — first attempt cancelled at 0% (BED_CLEARED not called), retried and completed: 167.2 min, 77.11g ✅
- `Camood_clean-marked.stl` PETG — failed at 0% → standby (BED_CLEARED guard, same cause) ❌ — pending reprint
- Requires `BED_CLEARED` call before requeue; no gcode or firmware changes made
- Session report: djinn/logs/reports/2026-06-28_camood-petg-print.md
- Bug report: djinn/logs/reports/2026-06-28_bug-camood-petg-start.md

*— Claude*

## 2026-06-28 — Calliope PETG Hardening (nozzle_mcu dropout workarounds)
- M106 fan cap: `{% set tmp = [tmp, 128] | min %}` added to gcode_macro.cfg M106 macro — hard 50% cap on all fan output regardless of slicer value
- Thermal soak: 3×60s dwell blocks added to START_PRINT, conditional on EXTRUDER_TEMP >= 240 — fires for PETG/ABS, skips for PLA
- bed_mesh probe_count: 6,6 → 3,3 in printer.cfg — reduces XY sweep distance and nozzle_mcu polling during leveling
- TRSYNC_TIMEOUT: NOT applied — requires SSH/physical access to /usr/share/klipper/klippy/mcu.py (manual step pending)
- Klipper restarted — all three changes confirmed live via API
- Based on Marcus research: root fix is temp 240°C for PETG + above mitigations

*— Claude*

## 2026-06-29 — Penelope Profile Validated (Proxy Stand)

- `Penelope-Standard-TreeSupports.json` written to OrcaSlicer user process dir (was previously missing from disk)
- Proxy Stand print confirmed all fixes working: clean outside, clean top surface, no blobs, no strings, seam at back, brim smooth
- Settings validated: top_shell_layers=5, top_surface_speed=30mm/s, top_solid_infill_flow_ratio=1.05, seam_position=back, retraction=6mm@45mm/s, deretraction=25mm/s, gyroid 14%, tree(auto) supports 30°, 8mm brim
- This is now the confirmed Penelope PLA baseline profile

*— Claude*

## 2026-06-29 — Print Law: Single Body Required Before Slicing

- **LAW (Calliope + Penelope):** Any STL/3MF with multiple separate bodies (emboss, engraving, separate shells) MUST be boolean-unioned into a single body in Blender before slicing and sending to either printer.
- Root cause: multi-body STLs generate inter-body travel moves that stress Calliope's nozzle_mcu cable and cause inconsistent toolpaths on both printers.
- Fix: `blender --background --python boolean_union.py` → single body STL → Desktop/Review → slice → print.
- Validated: Camood_TerpTribeHq failed repeatedly as 66 bodies, printed consistently as 1 body after union.

*— Claude*

## 2026-06-29 — Calliope Camood Clean Print — Completed Successfully

- Camood (no engraving, maker's mark only) printed to completion — 106mm, no errors, no dropout
- **Cable reseat** provided good slack — rattle disappeared mid-print, cable held through all 530+ layers
- **Gyroid infill confirmed safe** for simple solid geometry on Calliope — rattle was toolhead vibration only, not cable stress
- **Root cause of all previous failures confirmed:** specific XY toolpath positions from engraving/emboss geometry pulled cable to connector stress point — not infill pattern, not temp, not software config
- **key561 errors are symptoms, not causes** — sequence is always: XY toolpath pulls cable → connector loses contact → Klipper detects MCU timeout → key561 → emergency stop. Errors are reactive, they do nothing to the hardware.
- All software workarounds reverted to stock — none were helping, thermal soak may have been making it worse
- **Calliope print rules validated:**
  - Single merged body before slicing (no separate engraving shells)
  - Gyroid fine for simple solids, rectilinear/grid for complex engraved geometry
  - Cable slack is the real fix — reseat and route with relief

*— Claude*

## 2026-07-01 — Typhon Windows Onboarding Audit

- Typhon (MSI) was reinstalled Ubuntu → Windows ~2026-06-25, repurposed from storage/sync into a dedicated shop machine (slicing/commissions/content/accounting) — this was never logged through the session protocol, so every doc still described the old setup
- Live-probed the LAN: Typhon is up at 192.168.1.113, still identifies as `Typhon-4.lan` (pre-rename), all checked ports (22/3389/445/139/5985/11434) `filtered` — `setup-typhon.ps1` likely hasn't been run to completion yet
- Confirmed `djinn/scripts/bootstrap-node.sh`, which the ps1 script's post-reboot instructions depend on, does not exist anywhere in the vault or git history — logged as a bug, blocks WSL2-side Djinn install
- Updated `machines/TF-TTHQ.md`, `INFRASTRUCTURE.md`, `SYSTEM-STATE.md`, global `~/.claude/CLAUDE.md`, and the `project_djinn` auto-memory to reflect current Typhon status instead of the stale Ubuntu description
- Fixed a stray IP typo in INFRASTRUCTURE.md's network diagram (Calliope was shown at Typhon's old `.113`, corrected to `.114`)
- Full detail: [[2026-07-01_typhon-windows-onboarding-audit]]

*— Claude*

## 2026-07-01 — Typhon Windows Remote Onboarding

- Established full remote admin of Typhon over Tailscale/SSH from Salomon after Javier installed Claude Code + Tailscale locally on the box
- Renamed Windows account `typho` (typo) → `typhon`; delivered Salomon's SSH pubkey via USB since no network path existed yet
- Claude Code authenticated via credential-file transfer from Salomon (same Pro account) — `-p` mode works, `--bg` still blocked on a disclaimer that needs one interactive session
- Cloned all three Djinn repos (djinn-vault, typhons-cyber-forge, Project-Resources) to Typhon, working around Git Credential Manager's non-interactive failure by embedding a PAT directly in clone URLs
- Built the full `C:\Forge` directory tree, opened firewall rules, disabled sleep
- Installed ~18 pipeline apps via winget: Git, Ollama, Obsidian, Python 3.12, OBS Studio, Notepad++, JetBrains Mono Nerd Font, 7-Zip, Rustup, Microsoft Office, Blender, Creality Print, FFmpeg, rclone, Discord — 1Password failed (SID mapping error, unresolved)
- OrcaSlicer's pinned installer URL was stale (repo moved orgs); its installer also hung indefinitely when run over SSH (Windows Session 0 isolation blocks GUI init) — fixed by extracting the NSIS installer directly with 7-Zip instead of running it
- OpenCode has no Windows install script (bash-only officially) — downloaded the release zip directly and extracted it, wrote a Typhon-appropriate opencode.json
- Ollama's server crashes within seconds when launched non-interactively (same Session-0 class of bug) — needs one human interactive session to start
- **Deliberate architecture decision:** skipped WSL2 entirely, went native-Windows for everything — the original `setup-typhon.ps1` → WSL2 → `bootstrap-node.sh` plan has two blockers (missing script, reboot-kills-SSH-automation) that native-Windows sidesteps. Needs to be a conscious ongoing decision, not just left as-is.
- Full detail: [[2026-07-01_typhon-windows-remote-onboarding]], bug: [[2026-07-01_bug-typhon-session0-noninteractive-hangs]]

*— Claude*

## 2026-07-01 — Typhon Debloat + Reboot

- Ran `setup-typhon.ps1`'s debloat section (previously skipped) over SSH via a script file: removed Bing/Xbox/Solitaire/Zune/Clipchamp bloat apps, disabled Cortana/telemetry/OneDrive-autostart/Game DVR, cleaned non-djinn startup entries
- Found a pre-existing bug in the original script: `Remove-AppxPackage -Package $pkg.PackageFullName` fails with an array-to-string binding error when a package has multiple installed instances — a handful of apps hit this despite the script printing "Removed" (cosmetic, not blocking)
- Rebooted Typhon (`shutdown /r`) — came back cleanly in ~1 minute, `sshd`/`Tailscale` auto-started as configured (set to Automatic earlier), hostname/account survived
- **1Password now installs successfully** — the reboot cleared whatever SID-mapping state was broken by the earlier account rename (`typho`→`typhon`)
- **Confirmed Ollama's Session-0 crash is not reboot-fixable** — same crash recurred immediately when launched over SSH post-reboot, confirming it's tied to the SSH session type itself, not persistent OS/cache state. Still needs one interactive/RDP session.

*— Claude*

## 2026-07-01 — Print Library Migration: Salomon → Typhon/Oroborus

- Consolidated ~9G/632 files of scattered print library (printer-files/, Desktop/Review/, stray Downloads exports) into a three-tier setup: Typhon (`C:\Forge\models`) = active working library, Oroborus (`192.168.1.154`) = cold archive, Salomon = reports + small confirmed-working set only
- Caught a bad classification before acting on it: a sub-agent claimed `printer-files/vault-printer/` (1.5G) was a stale duplicate of the vault's own copies — checksum-verified this was false (zero matches anywhere on the system), archived it to Oroborus instead of deleting
- Found and fixed a `tar --exclude` ordering bug (GNU tar 1.35 ignores excludes placed after the file argument) — one transfer leaked a Camood file to Typhon, caught via post-transfer `findstr` check, deleted, redone correctly
- All Camood files (14+ across every location) excluded entirely per instruction — untouched
- Created `printer/library/UNCONFIRMED-PRINTS.md` — 17 pieces have no logged print-outcome record anywhere; confirmed genuinely under-logged not failed, except `applacrabus` which is explicitly ON HOLD (claw supports collapsed mid-print 2026-06-04)
- Cleanup used `gio trash` (no `rm`), only after size-verifying every transfer against source
- Full detail: [[2026-07-01_print-library-migration]]

*— Claude*

## 2026-07-01 — djinn-gcode-sync: Live Typhon→Salomon Gcode Handoff

- Built `djinn-gcode-sync` — pulls new gcode from Typhon's `C:\Forge\gcode\{calliope,penelope}` over Tailscale SSH every 5 min, auto-queues Calliope jobs into the existing print-queue.json/djinn-confirm-print pipeline, lands Penelope files locally for manual `djinn-penelope upload`
- Tested end-to-end with a real gcode file before deploying: SSH listing, scp pull, print-time/filament-g parsing, queue insertion, idempotency (no re-pull on second run) all confirmed working
- Found and fixed a real bug: `scp` over Windows OpenSSH silently fails on backslash remote paths even though the file exists and `ssh ... dir` (same backslash path) lists it fine — fixed by forward-slashing just the scp remote path
- Named it `djinn-gcode-sync` not `djinn-forge-sync` — an existing `forge-sync` systemd unit already means GDrive sync for `~/forge`, different thing
- Safety gate preserved: this tool never uploads or starts a print — Calliope jobs land as `pending` same as local slicing does, `djinn-confirm-print`'s auth prompt is still required
- Wired into `djinn-gcode-sync.timer` (5-min, systemd user), enabled and confirmed running via journalctl
- Full detail: [[2026-07-01_djinn-gcode-sync]]

*— Claude*

## 2026-07-03 — Shop expansion: AD5M Pro + AD5X + Space Pi X4L acquired

- Flashforge AD5M Pro: high-speed single-material, onboarding pending
- Flashforge AD5X: multi-color (4 filament), primary commission printer, onboarding pending
- Creality Space Pi X4L: 4-spool filament dryer, in use
- INFRASTRUCTURE.md updated with all three units
- Next: network both Flashforge printers, add to Djinn printer stack

## 2026-07-03 — Iris zmod + Slicer Setup (Claude)
- Diagnosed Iris zmod failure: ENABLE file can't repair a mod that was never fully installed — `/usr/data/config/mod/` was empty
- Applied full 206MB zmod package via USB — Iris now running zmod 1.7.1-49, Moonraker on :7125
- Nemesis confirmed online: Moonraker on 192.168.1.51:7125, Klipper ready
- Both Flashforge printers: Fluidd at :80, SSH root@<ip>
- Downloaded OrcaSlicer v2.4.1 (132MB) + Bambu Studio v02.07.01.62 (408MB) to Salomon ~/forge/slicers/
- Typhon USB populated: typhon-unlock.ps1, both installers, install-slicers.ps1, OPENCODE-PROMPT.md
- Salomon script: ~/forge/slicer-setup/djinn-typhon-slicers.sh (push + install autonomously once SSH unlocked)
- INFRASTRUCTURE.md: Iris + Nemesis entries updated with zmod details, Moonraker, SSH
- Pending: Typhon SSH unlock, bambufy on Iris, Djinn CLI for both printers

## 2026-07-05 — Nemesis Full Recalibration + OrcaSlicer Profile Fix (Claude)

- Diagnosed nozzle-too-close root cause: probe z_offset was -0.25 (wrong), bed mesh all-negative (-1.1 to -2.9mm)
- PROBE_CALIBRATE run → new z_offset: -0.401; written manually to `/opt/config/printer.base.cfg` via SSH (SAVE_CONFIG conflicts with included file — see bug report)
- BED_MESH_CALIBRATE run → new 5×5 mesh, 1.3mm variation (improved from 1.8mm); saved as [default], loaded
- OrcaSlicer machine profile updated: M140+M104+START_PRINT start gcode, END_PRINT end gcode, moonraker host_type
- Nemesis-PETG filament profile created: 240/235°C, 70°C bed, PA 0.035, SET_GCODE_OFFSET Z_ADJUST=+0.03
- shoulder_ring_PETG_4h14m printing — first fully calibrated print on Nemesis
- Full detail: [[2026-07-05_printer-triage-nemesis-calliope]]

## 2026-07-05 — Calliope nozzle_mcu Cable Diagnosis (Claude)

- Confirmed root cause of 4× klippy_shutdown: broken wire inside toolhead cable harness
- Evidence: bytes_invalid climbing 0→63 post-crash = intermittent partial contact, not clean break
- All MCUs on hardware UART (not USB) — USB saturation ruled out
- Crash at 1.7% into arm.stl at X185/Y205; moving pieces did not help — failure is general, not positional
- New cable ordered; Calliope sidelined for long PETG until replaced
- Cable routing rules documented: service loop, stepper separation, anchor to carriage
- Full detail: [[2026-07-05_bug-calliope-nozzle-mcu-cable]]

## 2026-07-06 — Iris Profile Fix + Fleet Back Online

- Fixed `Iris.json` (Bambu Studio): added `gcode_flavor: klipper`, `time_lapse_gcode: ""`, full bambufy `change_filament_gcode` (G1 Y210), `layer_change_gcode`, `print_host`
- Added Klipper no-op macros on Iris (`user.cfg`): M981, M624, M625 — swallows Bambu spaghetti/AMS codes injected by Bambu Studio regardless of flavor setting
- Created filament profiles: `FLASHFORGE PETG Basic @Iris`, `FLASHFORGE PLA Basic @Iris` (both `compatible_printers: ["Iris"]`, clean start gcode)
- Diagnosed M981/M624/M625/G1 X-48.2 injection via gcode diff between working and broken files
- Fleet status: Iris printing ✓, Nemesis printing ✓, Calliope waiting on cable parts ✓
- Bug documented: [[2026-07-06_bug-bambu-studio-m981-m624-injection]]

## 2026-07-09 — Alexandria SSD Setup + Full Storage Migration (Claude)

- **djinn-archive SSD renamed → Alexandria** (`e2label`), stable fstab mount at `/run/media/drmanzo/alexandria` by UUID with `nofail`; moved off `/mnt/` to prevent future corruption on disconnect
- **djinn-vault-sync** script installed to `/usr/local/bin/` — mirrors vault to `alexandria/vault-snapshots/current/`, `--snapshot` flag for dated rollbacks (keeps last 7)
- **Salomon cleared**: device-backups (7.6GB), Videos (935MB), GoogleDrive_archive (1.1GB), old Backups (1.2GB), forge/slicers (539MB), printer-files (153MB) → Alexandria
- **59 Marcus exports** sorted from Downloads into `alexandria/marcus/_inbox/` (2026-07-02 batch + 2026-07-08 batch)
- **Code migrated to Oroborus** (192.168.1.154, 401GB free): djinn-core, djinn-social, djinn-tools, djinn-paper, djinn-publish, djinns-voice → `code/djinn/`; voice-app, lblack, forge → `code/forge/`; whisper.cpp, Hunyuan3D-2, djinn-scripts → `code/ai-tools/`; BurpSuiteCommunity, sec-env → `code/sec/`
- **puffco-710.3mf fixed**: outer body 38.42mm → 43.46mm (scale 1.1312×), 2.38mm wall around 38.7mm bore; `puffco-710_fixed.3mf` in `~/Downloads/`, original untouched
- **udisks2 NTFS automount**: `/etc/udisks2/mount_options.conf` — `ntfs3_defaults` includes `force` flag, dirty Windows drives now automount without sudo
- **TASK-008 closed**: djinn-archive was local on Salomon all along, not Oroborus; marcus structure already created
- **Iris confirmed ready**: Moonraker 7125 + Fluidd 80 both 200 OK, klippy_state=ready — GUI issue was client-side
- Full detail: [[2026-07-09_alexandria-setup-storage-migration-cleanup]]

## 2026-07-09 — Printer Fleet Status Check + QUEUE.md Corrections (Claude)

- **Calliope:** unreachable (expected, sidelined pending cable) — no action possible until Javier installs it
- **Nemesis:** verified via SSH the queued `[probe]` fix (move out of included `printer.base.cfg` into `printer.cfg`) is already in place — SAVE_CONFIG no longer conflicts. Current z_offset (0.071) and bed mesh differ from the 7/5 calibration (-0.401) because Javier physically relocated the machine and recalibrated it himself ~7/8 — confirmed with him, not data loss. QUEUE.md task marked resolved.
- **Iris:** idle/ready, nothing outstanding except Javier's own pending task to watch the first multi-color tool change
- **QUEUE.md correction:** the Calliope bring-up checklist (added 2026-07-07) told Javier to (re)install the `fan-cap-calliope.cfg` M106 cap after the new cable goes in. That approach was already tried and reverted as ineffective per the 2026-06-29 BUG-014 root-cause update (cable/routing is the real fix, not fan EMI). Annotated the checklist so Javier doesn't waste time on a dead-end fix. Also flagged an unexpanded `$(date +%Y-%m-%d)` literal in that section's header (checklist was actually written 2026-07-07) and noted the config file's post-7/8-restructure path moved to `forge/config/fan-cap-calliope.cfg`.

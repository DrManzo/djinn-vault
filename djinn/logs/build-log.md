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

- Klipper + Moonraker: already live on Nebula pad (`192.168.1.114:7125`) — no Typhon install needed
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

## 2026-05-24: Manufacturing Orchestrator + Coin + FairPrintAgent

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

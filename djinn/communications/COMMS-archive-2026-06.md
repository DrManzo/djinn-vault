# COMMS Archive — 2026-05-22 to 2026-06-03

Archived 2026-06-05 by Claude. Entries through end of June 3, 2026.
Pre-May-31 entries are in the original archive block below.

---

# Original Archive — 2026-05-22 to 2026-05-31

Archived 2026-06-01 by Claude (TASK-030). Entries through end of May 2026.

---

### 2026-05-22 08:48 UTC — @Claude → @All: Comms consolidation

- **What:** 4 comms files replaced with this single thread. Old files archived at `archive/`.
- **Action:** Update session-start to read `COMMS.md` + both HEARTBEATs. Append one entry on exit.
- **Paths:** `archive/` (4 files preserved), `COMMS.md` (this file), `PROTOCOL.md` (rewritten)

— Claude

---

### 2026-05-22 20:30 UTC — @Claude → @All: Printer recovery + PLR + thermal watchdog session

- **What:** Full printer recovery session. Root cause of recurring key564 shutdowns identified as nozzle_mcu serial retransmits (retransmit_seq=4289). Javier physically reseated /dev/ttyS1 cable — fixed (retransmit_seq now 2). verify_heater restored to safe values.
- **New systems installed:** plr.cfg on printer (Power Loss Recovery + thermal watchdog), printer-error-logger.service on Salomon, print_profile_baseline.md, error_log.md.
- **Printer IP:** 192.168.1.113. **Currently printing:** Rose_Decor_fixed.gcode — 2 roses, 210mm tall, 16h34m est.

— Claude

---

### 2026-05-23 — @Claude → All: Session summary — cup print + Telegram bot deployed

- Root cause confirmed: PrusaSlicer fan ramp (M106 S155.55) at brim→layer 1 triggered deterministic key564 via nozzle_mcu EMI spike. Fixes applied. Cup print clean.
- Telegram printer bot deployed on Typhon. Service: djinn-printer-bot.service — active, enabled. Test: /print_status.
- vault-sync now git push after rclone. SSH Salomon→Typhon working. Typhon IP: 192.168.1.113.

— Claude

---

### 2026-05-23 10:29 UTC — @Claude → @All: Suite activation complete

Full Djinn suite activation deployed. OpenClaw exec allowlist (45 entries), agent system prompts, model configs fixed on Salomon and Typhon, critical opencode -- bug fixed, comms-processor working end-to-end. Known gap: qwen2.5:7b in headless mode responds with text, not tool execution — route execution tasks to Claude or SSH.

— Claude

---

### 2026-05-23 12:20 UTC — @Claude → @All: OpenClaw model timeout root cause found and fixed

Root cause: num_ctx: 131072 on all Ollama models causing KV cache overflow. Fixed: qwen2.5:7b → 16384, deepseek-r1:7b → 8192, qwen2.5-coder:7b → 16384, llama3.2-vision:11b → 4096. Discord historyLimit: 20 → 5. Gateway now running as systemd service: openclaw-gateway.service.

— Claude

---

### 2026-05-23 19:55 UTC — @Claude → @All: Gateway model switched to mistral:7b — channels live

Root cause of Telegram/Discord failure: sessions hit 16384-token context limit → auto-compaction → EmbeddedAttemptSessionTakeoverError. Switched main agent to mistral:7b (200k context). Both channels confirmed working end-to-end by Javier.

— Claude

---

### 2026-05-23 22:00 UTC — @Claude → @All: Agent system built — Clerk, Slipbox, Law, Embed

Full agent pipeline wired. All 5 agents operational: djinn-clerk, djinn-embed, djinn-slipbox, OpenClaw law agent (deepseek-r1:7b), comms-processor updated routing. Clerk tested on RAW/Law file — produced valid structured note with hierarchical tags in 25s.

— Claude

---

### 2026-05-31 03:47 UTC — @Marcus → @All: Session close — TASK-012 + TASK-015 complete

Completed: TASK-012 (Meta Graph API spec, IG/FB publish flows, algorithm signals, cannabis policy table, djinn-trend-agent architecture) and TASK-015 (self-hosted scraper verdict: don't — optimal zero-cost stack: Apify free tier + Reddit PRAW + YouTube Data API v3 + Printables RSS, ~14h build time).

**Critical flag:** Meta app review for pages_manage_posts is the longest lead-time item. Start review now — budget 1–2 weeks.

— Marcus

---

### 2026-05-31 UTC — @Claude → @All: TASK-019 through TASK-022 complete

djinn-trend-agent built (Printables RSS + Firecrawl, timer enabled). djinn-media-publish-prep caption wiring done. djinn-style-scrape rewritten with Firecrawl. djinn-model-fetch Firecrawl upgrade done. All 4 tasks complete. Shippo API key still needed.

— Claude

---

### 2026-05-31 UTC — @Claude → @All: Storage protocol + djinn-marcus + djinn CLI

Storage protocol established. 1.6 GB of printer binary files moved to ~/printer-files/. Vault is now text-only (2.6 GB). djinn-marcus live (Perplexity CLI: ask/research/repl/deep/topics). djinn CLI dispatcher live with tab completion. BUG-014 fixed (agent hallucination on TASK-NNN commands). Architecture: OpenClaw = Discord/Telegram hub; djinn = workbench.

— Claude

---

### 2026-06-01 UTC — @Salomon → @All: TASK-019 deployed + TASK-021 done

TASK-019 — djinn-trend-agent timer enabled (next fire 00:05). TASK-021 — djinn-style-scrape rewritten with Firecrawl fc.search(). Verified with live query — 3 results for "dark 3D printing aesthetic". TASK-022 deferred — low priority.

— Salomon

---

### 2026-06-01 UTC — @Claude → @All: PHASE-3 maintenance complete — 9 tasks

TASK-045 (Typhon audit — 3.8GB logs freed), TASK-034 (printer-files-backup fix), TASK-030 (COMMS rotation), TASK-036 (forge-sync rate limiting), TASK-026 (gdrive-backup-manifest rotation fix), TASK-032 (Claude queue alert), TASK-033 (Typhon heartbeat staleness alert), TASK-031 (conversation logging). Typhon correct IP: 192.168.1.113 (CLAUDE.md has stale 192.168.50.113 — update when convenient). TASK-044 still needs Typhon to execute.

— Claude

---

### 2026-06-01 UTC — @Claude → @All: All Marcus research gates cleared

TASK-037 (Law 13/13 domains), TASK-038 (Psychology 14 domains), TASK-039 (Finance 21 domains) all delivered and vaulted. PHASE-4 builds unblocked: TASK-023 (Rabbit R1), TASK-029 (djinn-marcus-sync), TASK-052 (djinn-gemini), TASK-053 (Gemini TTS).

— Claude

---

### 2026-06-01 UTC — @Claude → @All: TASK-044 complete — Extreme SSD reformatted

4.65GB backed up to /mnt/storage/extreme-ssd-backup/. /dev/sdb1 reformatted ext4 "djinn-archive", mounted at /mnt/archive (1.8TB, 1.7TB free). Directory structure: /mnt/archive/{printer-files,media-files,vault-snapshots,library-rescue}. vault-sync --resync running in background.

— Claude

---

### 2026-06-01 UTC — @Claude → @All: PHASE-4 — djinn-gemini + Rabbit R1 + djinn-marcus-sync done

djinn-gemini live (ask/research/repl/doc/youtube/url/image-qc/tts). TTS via gemini-2.5-flash-preview-tts + ffmpeg. Telegram /voice toggle for audio replies. djinn-marcus-sync built (Xvfb+Firefox, bypasses Cloudflare). djinn-marcus-sync hourly timer installed. /gemini command added to Telegram gateway. TASK-023, TASK-029, TASK-040, TASK-043, TASK-052, TASK-053 all done.

— Claude

---

### 2026-06-01 UTC — @Claude → @All: Phase Alpha personal layer — architecture complete

Javier approved Phase Alpha. Full personal access granted. Decisions locked: sobriety counter (2026-03-01), Black Book (local-only, /reflect is key), AA meeting reminders + Craig draft-and-confirm, Sabrina passive tracking (auto-archive 14d silence), morning briefing (under 90 words). Build queue: TASK-054→058.

— Claude

---

### 2026-06-01 UTC — @Salomon → @All: PHASE-ALPHA Sprint 1+2 complete

TASK-055 (djinn-morning rewrite) ✅ | TASK-056 (personal Telegram commands) ✅ | TASK-057 (AA meeting reminders + Craig contact) ✅ (fixed after initial failure) | TASK-058 (Sabrina context tracking) ✅

— Salomon

---

### 2026-06-01 — @Claude → @All: Job 5 + djinn-model-text-engrave built

Puffco Proxy Stand (Job 5) — XY scale 1.45% (bore 41.4→42.0mm), "Typhon's Forge" side engraving, Z offset +0.1mm. djinn-model-text-engrave built. Text position needs Javier visual approval — cannot verify without images. Escalation doc: `djinn/logs/reports/2026-06-01_text-engraving-escalation.md`.

— Claude

---

### 2026-06-01 — @Salomon → @All: TASK-062 (commission intake chain) done

✅ LIVE ALPHA — Full Typhon's Forge commission intake chain deployed and end-to-end tested.

— Salomon

---

### 2026-06-01 — @Claude → @All: djinn-social v0.1 built

Full social studio pipeline. CLI live. 9 commands. Both brand configs deployed. Publish scheduler timer enabled (15-min). Cloudflare Tunnel chosen for Meta hosting. Before first publish: cloudflared setup, fill meta-terp-tribe.env creds, confirm TF weekly day names, confirm TT S6 start date, YouTube OAuth browser setup. Meta App Review: start now if posting to real IG accounts (2–4 weeks).

— Claude

---

### 2026-06-02 — @Claude → @All: Engraving Specialist sub-agent built (TASK-062)

djinn/engraving/ — 10 modules, 14 tests all passing, djinn engrave-analyze live. STL → surface classification → NLP via Ollama → FDM constraint math → 3 ranked proposals. User approves → engraving_spec.json written. Never modifies model without approval. Phase 2: logo/SVG + curved surface curvature.

— Claude

---

### 2026-06-02 — @Claude → @All: Proxy Stand emboss complete — "Terp Tribe HQ"

Root cause of "letters = blobs" was raster→contour pipeline. Fixed by switching to matplotlib TextPath (TTF Bezier curves direct from font). Final: "Terp Tribe HQ" 6mm Liberation Bold, 1.4mm depth, embossed, centered on front face. Javier approved. STL at `printer-files/queue/Proxy_Stand_terp_tribe_hq_v5_embossed.stl`. Also shipped: --emboss mode, auto-centering, manifold embed fix, LG-1…LG-6 legibility gate.

— Claude

---

### 2026-06-02 — @Claude → @All: Calliope key561 root cause — M106 S255 EMI

Root cause: PrusaSlicer inserts M106 S255 (full fan) at bridge infill → EMI spike → nozzle_mcu serial dropout (retx 0→100% in one polling interval). Fix: sed bridge fan cap to 50%. PrusaSlicer PLA profile: bridge_fan_speed=100 → 50%, bed=60°C, cube-style start gcode. ProxyStandTF + ProxyStandTTHQ resliced clean. Full report: `logs/reports/2026-06-02_proxy-stand-print-diagnosis.md`.

— Claude

---

### 2026-06-02 — @Claude → @All: Phase 5 — router simplification complete

djinn slimmed 736→533 lines. Standalone forge CLI (~175 lines). Standalone terp CLI (~60 lines). Three-system separation (Djinn/Forge/Studio) fully complete across all 5 phases.

— Claude

---

### 2026-06-03 — @Claude → @All: Calliope upgraded + OrcaSlicer deployed

SSH enabled (root/creality_ender3v3). Moonraker v0.7.1 → v0.10.0 via Guilouz Helper Script. Fluidd live at :4408. Gcode Shell Command installed. OrcaSlicer 2.3.2 installed on Salomon with Calliope profile (Moonraker at 192.168.1.113:7125). Switching from PrusaSlicer — better defaults, native Moonraker upload, built-in V3 Plus profile. Report: `logs/reports/2026-06-03_calliope-upgrade-orcaslicer.md`.

— Claude

---

### 2026-06-03 — @Claude → @All: Protocol + SUPPORT-GUIDE updated

SUPPORT-GUIDE.md now distinguishes two key561 failure modes: bytes_invalid>0 = EMI (cap fan), bytes_invalid=0 = physical connector/power (hardware inspection). PRINT-PROFILES.md: OrcaSlicer for interactive slicing, PrusaSlicer retained for pipeline scripts. Fan cap rule is hardware constraint, not slicer-specific — applies to both.

— Claude

---

### 2026-06-03 — @Claude → @All: Phase 3 complete — ProxyStand TTHQ printed

Job 6 finished on Calliope (~58 min, 19.86g). DancingScript "Terp Tribe HQ" side-engraved, Z=2mm, 42.3mm bore. Post-print nozzle MCU error (key561) cleared via firmware restart. All services restarted.

— Claude

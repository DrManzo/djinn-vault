# PLAN.md — Today's Plan
# 2026-05-30

## Today's Focus (Top 3)
1. **3D Print Pipeline Overhaul** — Discord send-back fixed, material/priority/feedback added, REST API migration complete. Calliope printing model_job2 at ~60%.
2. **Engraving Agent** — `djinn-model-engrave` built as interactive wizard (6-panel, keyword style parser, per-component boolean). "The Terp Tribe - Camood" saved to library.
3. **Infrastructure** — opencode wrapper wired with `djinn-session-end`, session reporting automation deployed to both machines.

## Djinn System Status — Live
| Component | Status | Notes |
|-----------|--------|-------|
| Salomon | ✅ Alive | RTX 5060, 574G free, 12Gi/29Gi RAM, up 3d22h |
| Typhon | ✅ Alive | GTX 1650, 552G free, 2.6Gi/14Gi RAM, up 2d16h |
| Calliope (E3V3+) | ✅ Printing | model_job2.gcode at ~60% |
| djinn-discord-watcher | ✅ Active | Xvfb :98, direct REST API, ALLOWED_USER gate |
| djinn-discord-gateway | ✅ Active | No `/` prefix required, slice regex extended |
| djinn-telegram-gateway | ✅ Active | All 11 command routes |
| djinn-print-monitor | ✅ Active | Feedback prompt wired, current_job_id tracking |
| djinn-webcam-monitor | ⚠️ Inactive | Not running for current print |
| djinn-printer-bot (Typhon) | ✅ Active | Telegram print control |
| Typhon's Studio | ✅ Active | 6 agents: Audio, Lighting, Music, Copilot, Stream, Post |
| djinn-clerk (hourly) | ✅ Active | RAW/ → i notes/ pipeline |
| djinn-slipbox | ✅ Active | Wiki links + hierarchical tags |
| djinn-embed | ✅ Active | nomic-embed-text vault index |

## Active Projects — Status
| Project | Status | Notes |
|---------|--------|-------|
| 3D Print Pipeline | 🟢 LIVE | Full overhaul done. Dry-run subprocess issue needs investigation. Exclude-object support pending. |
| Engraving Agent | 🟢 LIVE | `djinn-model-engrave` shipped. Next: per-letter curvature compensation, Discord pipeline integration. |
| Typhon's Studio | 🟢 LIVE | Phase 6 complete (Guardian + Post). User manual written. |
| Media Stack (9 agents) | 🟢 LIVE | LUT pipeline, hashtag bank, style scraper all operational. |
| FairPrintAgent | 🟢 LIVE | Commission pricing, Etsy comps, smoking/dab category support. |
| Djinn System Tools | 🟡 Partial | `djinn-bugreport` exits 1 even on success. Queue job status doesn't auto-update to `printing`. |
| Cloudybay Lights | 🔴 Pending | Needs Tuya API credentials |
| WHIP end-to-end test | 🔴 Pending | From Omen |

## Blockers & Decisions Needed
- `djinn-print-consult` dry-run silently failing when called as subprocess from `djinn-model-fetch` — estimates show "?" in reports. Blocking accurate pre-slice estimates.
- Per-letter curvature compensation in engraving — `e` in "Tribe" incomplete at curved surface; non-uniform depth on edges.
- Wire `djinn-model-engrave` into Discord pipeline — `djinn-model-fetch` / `djinn-discord-watcher`.
- _None from Javier._

## End-of-Session (fill at close)
- **What got done:**
- **In progress for next time:**
- **Decisions made:**
- **To carry forward:**

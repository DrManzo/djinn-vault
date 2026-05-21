# Changelog — Djinn Inter-Machine Changes

All changes made by any Djinn instance, logged here.

| Timestamp | Machine | Action | Files | Details |
|-----------|---------|--------|-------|---------|
| 2026-05-19 23:48 | Salomon | Created | Initial vault commit, 504 notes, git init, GitHub push |
| 2026-05-19 23:50 | Salomon | Created | Processed inbox (9 notes), populated djinn/ dirs, deleted temp search file |
| 2026-05-20 01:11 | Salomon | Created | Populated script dirs with PIPELINE.md markers |
| 2026-05-20 05:04 | Salomon | Created | Salomon.md machine spec, updated Typhon resource pooling |
| 2026-05-20 05:12 | Typhons Forge | Updated | All signatures | Changed from TF/TTHQ to Typhons Forge |
| 2026-05-20 05:45 | Salomon | Created | Salomon-to-Typhon.md response, confirmed sync working |
| 2026-05-20 05:50 | Salomon | Updated | Added Salomon signatures to all created files |
| 2026-05-20 05:55 | Typhons Forge | Updated | djinn/Typhon.md, communications/Typhon-to-Salomon.md | Pulled llama3.2:3b, responded to Salomon, updated model catalog |
| 2026-05-20 06:02 | Typhons Forge | Renamed | djinn/Typhon.md → djinn/Djinns-Hub.md | Central hub document rename |
| 2026-05-20 06:05 | Salomon | Updated | vault-sync.timer, Salomon.md, communications/ | Sync timer changed to 2-min, pulled mistral:7b, responded to TF |
| 2026-05-20 06:15 | Salomon | Created | Ollama-Remote-Server-Setup.md | Ollama remote server documented, IP 192.168.1.225, requires manual sudo step |
| 2026-05-20 06:25 | Typhons Forge | Updated | communications/Typhon-to-Salomon.md | Responded with Typhon IP (192.168.50.113), requested sudo restart of Ollama, confirmed network ping OK |
| 2026-05-20 06:35 | Salomon | Updated | communications/Salomon-to-Typhon.md, Ollama-Remote-Server-Setup.md | Ollama running on localhost, sudo restart still pending, responded to Typhon |
| 2026-05-20 06:40 | Salomon | Updated | communications/Salomon-to-Typhon.md | Ollama remote server LIVE on 0.0.0.0:11434, all 8 models accessible |
| 2026-05-20 06:42 | Typhons Forge | Updated | communications/Typhon-to-Salomon.md | Acknowledged localhost status, flagged that Javier must run sudo commands on Salomon physically |
| 2026-05-20 06:45 | Typhons Forge | Updated | Djinns-Hub.md, opencode.json, communications/ | Ollama remote server ACTIVE — phi4:14b remote inference confirmed, added ollama-salomon provider to OpenCode config |
| 2026-05-20 06:50 | Salomon | Updated | communications/Salomon-to-Typhon.md | Phase 1 COMPLETE — voice pipeline confirmed (voxtype + Piper READY), model routing confirmed |
| 2026-05-20 06:55 | Salomon | Updated | Phase 2 started — voice pipeline test PASS, heartbeat timer (5-min), Telegram bot script, daily PLAN.md timer |
| 2026-05-20 13:00 | Salomon | Renamed | Git author TF/TTHQ → Typhons Forge (9 commits), all file refs TF/TTHQ → Typhon, PROTOCOL.md signing convention added |
| 2026-05-20 20:00 | Claude | Created | djinn/SYSTEM-STATE.md, djinn/ROUTING.md | Phase 2 completion: shared memory index + agent routing rules |
| 2026-05-20 20:00 | Claude | Created | communications/Claude-inbox.md, communications/Claude-outbox.md | Claude communication channels established |
| 2026-05-20 20:00 | Claude | Updated | djinn/projects/djinn-mvp.md, communications/CHANGELOG.md | Phase 5 marked complete, Phase 2 Identity Layer complete |
| 2026-05-20 20:00 | Claude | Investigated | Network | Typhon unreachable from Salomon (192.168.50.113 ping fails) — subnet mismatch, awaiting diagnosis |
| 2026-05-20 21:45 | Claude | Created | ~/.local/bin/djinn-daily | Phase 6: morning briefing script — vault pull, health, inboxes, today's plan |
| 2026-05-20 21:45 | Claude | Created | ~/.local/bin/djinn-sync | Phase 6: sync script — pull vault, check inboxes, commit changes |
| 2026-05-20 21:45 | Claude | Updated | communications/Salomon-to-Typhon.md | Task division message to Typhon with file ownership rules |
| 2026-05-20 21:45 | Claude | Updated | communications/Claude-outbox.md | Task division message to Salomon opencode with file ownership rules |
| 2026-05-20 21:45 | Claude | Created | ~/.config/djinn/telegram.conf | Telegram config file — awaiting token from Javier |
| 2026-05-20 22:30 | Claude | Renamed | djinn/MEMORY.md → SYSTEM-STATE.md, djinn/AGENTS.md → ROUTING.md | Avoid collision with ~/.openclaw/workspace/ identity files |
| 2026-05-20 22:30 | Claude | Enabled | openclaw.json telegram channel | Telegram was already built — just needed enabled:true + gateway restart |
| 2026-05-20 22:30 | Claude | Fixed | openclaw sessions cleanup | Pruned missing session transcripts |
| 2026-05-20 22:30 | Claude | Disabled | djinn-telegram-daily timer | Redundant — OpenClaw handles 8 AM daily prompt via Telegram natively |
| 2026-05-20 22:45 | Claude | Updated | communications/Salomon-to-Typhon.md | MASTER ORDER sent to Typhon — full sync-up instructions, heartbeat script, all steps copy-paste ready |
| 2026-05-20 23:00 | Claude | Deleted | djinn-telegram-daily, djinn-daily.service/timer, telegram.conf, telegram.conf.example | Redundant — OpenClaw handles Telegram natively |
| 2026-05-20 23:00 | Claude | Cleaned | ~/.openclaw/agents/main/sessions | Archived 3 orphan session files, session store at 4 active entries |
| 2026-05-20 23:00 | Claude | Updated | ~/.openclaw/workspace/TOOLS.md | vault-sync interval corrected 15-min → 2-min |
| 2026-05-20 23:00 | Claude | Updated | ~/.openclaw/workspace/MEMORY.md | Active context refreshed: Telegram live, Claude live, Typhon pending |
| 2026-05-20 23:00 | Claude | Updated | ~/.openclaw/workspace/PLAN.md | Today's plan with live system status table |
| 2026-05-20 23:00 | Claude | Updated | djinn/SYSTEM-STATE.md | Full system state refresh |
| 2026-05-21 00:48 | Typhon | Synced | Git rebase onto origin/main — 28 commits applied, all file renames resolved (TF-TTHQ → Typhon) |
| 2026-05-21 00:48 | Typhon | Pulled | qwen2.5:1.5b (~1 GB) — GPU native, added to Djinns-Hub.md catalog |
| 2026-05-21 00:48 | Typhon | Verified | Ollama remote routing — phi4:14b via Salomon (192.168.1.225:11434) confirmed working |
| 2026-05-21 00:48 | Typhon | Created | heartbeat-typhon script + systemd timer (5-min), HEARTBEAT-typhon.md live |
| 2026-05-21 00:48 | Typhon | Verified | vault-sync timer active at 2-min interval |
| 2026-05-21 00:48 | Typhon | Updated | Djinns-Hub.md — qwen2.5:1.5b added, heartbeat status marked ACTIVE |
| 2026-05-21 00:48 | Typhon | Updated | communications/Typhon-to-Salomon.md — full sync-up response with network + SSH status |
| 2026-05-21 01:00 | Typhon | Reviewed | Claude outbox, handoff package, SYSTEM-STATE.md, ROUTING.md — identified Claude Code setup as next pending task |
| 2026-05-21 01:00 | Typhon | Blocked | Claude Code setup — SSH requires sudo password (headless), Ollama resource caps require sudo — Javier must run both manually |
| 2026-05-21 01:10 | Typhon | Installed | openssh-server — SSH now active on Typhon (192.168.50.113), ready for Salomon Claude Code setup script |
| 2026-05-21 01:10 | Typhon | Applied | Ollama resource caps — CPUQuota=60%, MemoryMax=8G, MemorySwapMax=0, Nice=10 |
| 2026-05-21 01:50 | Typhon | Responded | Claude 01:30 message — SSH confirmed live (0.0.0.0:22), ping to Salomon passes, requested retry of typhon-claude-setup.sh |
| 2026-05-21 02:15 | Typhon | Installed | Claude Code v2.1.146 — installed via curl, generated SSH key pair (ed25519) |
| 2026-05-21 02:15 | Typhon | Requested | Salomon to add Typhon's SSH public key to authorized_keys — enables passwordless SCP for credential transfer |

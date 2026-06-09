================================================================================
                    DJINN — COMPLETE CLI OPERATOR HANDBOOK
              The Djinn Stack | Salomon / Typhon / Orin / Calliope
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: DrManzo / Claude

> Full standalone operator handbook. Absorbs GATEWAY.md, INFRASTRUCTURE.md,
> ROUTING.md, TROUBLESHOOT.md, djinn-cli-guide.md, and SYSTEM-STATE references.
> A new operator who has never touched the stack should be able to run, diagnose,
> and extend the system using only this document.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What Is the Djinn Stack?
  2.  Machine Topology
  3.  The Three Session Modes (Gateway)
  4.  The Action Tier System
  5.  Agent Roster & Lane Rules
  6.  Model Routing — djinn-route
  7.  Full CLI Tool Reference
      7.1  Print Pipeline Tools
      7.2  Design & 3D Tools
      7.3  Media Pipeline Tools
      7.4  System & Vault Tools
  8.  Discord & Telegram Command Reference
  9.  Systemd Services Reference
  10. Key File Locations
  11. Common Workflows (Step-by-Step)
      11.1  Starting a Daily Session
      11.2  Launching a Claude Architecture Session
      11.3  Routing a Task Through djinn-gate
      11.4  Writing a COMMS Handoff Entry
      11.5  Running a Checkpoint (Tier 3 Action)
      11.6  Enabling Dev Mode
      11.7  Vault Sync (Manual)
      11.8  Rebuilding the Embedding Index
  12. Troubleshooting (CAUSE + FIX)
      12.1  OpenClaw / Gateway
      12.2  Ollama / Models
      12.3  Agent Scripts (Clerk / Slipbox / Embed)
      12.4  Systemd Timers
      12.5  COMMS.md Channel
      12.6  Vault Git
      12.7  SSH
      12.8  Printer / Moonraker
  13. Hard Rules — No Exceptions
  14. FAQ

================================================================================
1. WHAT IS THE DJINN STACK?
================================================================================

Djinn is a personal AI operations system running across a three-machine home
network (Salomon, Typhon, Orin) plus a 3D printer (Calliope). It unifies:

  - A Discord + Telegram bot gateway for real-time commands from any device
  - A full 3D print pipeline: file drop → analyze → slice → confirm → print
  - A media production pipeline: ingest → edit → caption → publish
  - An AI agent layer: 4 specialized agents (opencode, Claude, Hermes, Marcus)
  - A vault (Obsidian + Git) as the single source of truth for everything
  - A CLI toolkit of ~40 djinn-* tools covering every domain

The control philosophy is: **humans confirm, agents execute.**
No production action (print start, git push, file overwrite, Telegram alert to
Javier) happens without an explicit per-action confirm command. The Gateway
enforces this mechanically and behaviorally.

================================================================================
2. MACHINE TOPOLOGY
================================================================================

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         DJINN NETWORK MAP                               │
  ├──────────────────────┬──────────────────────┬──────────────────────────┤
  │ Salomon              │ Typhon               │ Orin                     │
  │ 192.168.1.225        │ 192.168.1.113        │ 192.168.1.176            │
  │ HP Omen              │ MSI                  │ iMac i7-7700K            │
  │ Fedora               │ Fedora               │ macOS Sequoia            │
  │ RTX 5060 Laptop      │ GTX 1650 4GB         │ 40GB RAM, CPU inference  │
  │ 29GB RAM             │ 14GB RAM             │ 1.7Ti disk               │
  │ PRIMARY — daily ops, │ Storage, lightweight,│ Large-model host:        │
  │ print/design/media,  │ Typhon's Studio,     │ llama3.3:70b             │
  │ LLM serving for all  │ stream/post-prod     │ qwen2.5-coder:32b        │
  │ machines             │                      │ qwen3.6 (Hermes)         │
  └──────────────────────┴──────────────────────┴──────────────────────────┘
                                     │
  ┌─────────────────────────────────┐│
  │ Calliope (Printer)              ││
  │ 192.168.1.113:7125 (Moonraker)  ││
  │ Ender-3 V3 Plus + Klipper       ││
  │ Managed via Salomon             │◄┘
  └─────────────────────────────────┘

SALOMON is the nerve center. All Djinn services run here.
All agents route through Salomon unless explicitly directed otherwise.

SS COMMANDS:
  ssh orin                             # Salomon → Orin (key auth, javiermanzo@)
  ssh -i ~/.ssh/id_ed25519 tf-tthq@192.168.1.113   # Salomon → Typhon

================================================================================
3. THE THREE SESSION MODES (GATEWAY)
================================================================================

Every session runs in one of three modes. Mode is stored in:
  ~/.config/djinn/session.json

  ┌─────────────────┬──────────────────┬──────────────────────────────────────┐
  │ Mode            │ Who Sets It      │ What It Allows                       │
  ├─────────────────┼──────────────────┼──────────────────────────────────────┤
  │ Standard        │ Default          │ Read anything, write COMMS/reports,  │
  │                 │                  │ propose actions, ASK before Tier 3+  │
  ├─────────────────┼──────────────────┼──────────────────────────────────────┤
  │ Dev             │ Javier only      │ Full execution, Tier 3 auto-proceeds,│
  │                 │ (djinn-gateway   │ all actions still logged.            │
  │                 │  --dev-session)  │ Expires automatically (default 2h)   │
  ├─────────────────┼──────────────────┼──────────────────────────────────────┤
  │ Restricted      │ Auto on          │ Read + COMMS write only.             │
  │                 │ production paths │ No file writes, no git, no shell.    │
  └─────────────────┴──────────────────┴──────────────────────────────────────┘

GATEWAY COMMANDS:
  djinn-gateway status                 # Check current mode
  djinn-gateway --dev-session          # Enable Dev mode (2h default)
  djinn-gateway --dev-session --duration 4h   # Dev mode for 4 hours
  djinn-gateway reset                  # Reset to Standard
  djinn-gateway classify "<action>"    # Query which tier an action is
  djinn-gateway checkpoint "<action>" "<reason>"   # Log + Telegram for Tier 3
  djinn-gateway install-hooks          # Install git pre-push hook in vault repo

NOTE FOR CLAUDE AND MARCUS:
  You cannot read session.json. Default assumption is always Standard mode.
  Javier will say "Dev mode is active" explicitly if it applies.

================================================================================
4. THE ACTION TIER SYSTEM
================================================================================

Every action has a tier. The tier determines what must happen before execution.

  ┌────────┬─────────────────────┬────────────────────────────────────────────┬──────────────────────┬──────────────────┐
  │ Tier   │ Name                │ Actions                                    │ Standard Mode        │ Dev Mode         │
  ├────────┼─────────────────────┼────────────────────────────────────────────┼──────────────────────┼──────────────────┤
  │ 0      │ Read                │ Read files, dirs, git log, COMMS           │ Auto                 │ Auto             │
  ├────────┼─────────────────────┼────────────────────────────────────────────┼──────────────────────┼──────────────────┤
  │ 1      │ Ephemeral Write     │ Write COMMS.md, session reports, HEARTBEAT │ Auto                 │ Auto             │
  ├────────┼─────────────────────┼────────────────────────────────────────────┼──────────────────────┼──────────────────┤
  │ 2      │ Permanent Write     │ Write staging/, tmp/, job dirs; create     │ Auto + COMMS entry   │ Auto             │
  │        │                     │ branches                                   │                      │                  │
  ├────────┼─────────────────────┼────────────────────────────────────────────┼──────────────────────┼──────────────────┤
  │ 3      │ Checkpoint          │ git commit/push, write library/originals/, │ ASK FIRST (see §11.5)│ Auto + logged    │
  │        │                     │ overwrite existing STL, update QUEUE.md,   │                      │                  │
  │        │                     │ send Telegram to Javier                    │                      │                  │
  ├────────┼─────────────────────┼────────────────────────────────────────────┼──────────────────────┼──────────────────┤
  │ 4      │ Hard Stop           │ Delete files, push to main directly,       │ BLOCKED — Dev +      │ Double-confirm   │
  │        │                     │ modify shop credentials, modify GATEWAY.md │ double-confirm req.  │ required         │
  │        │                     │ ROUTING.md, PROTOCOL.md, CLAUDE.md         │                      │                  │
  └────────┴─────────────────────┴────────────────────────────────────────────┴──────────────────────┴──────────────────┘

THE ONE RULE:
  Ask before any action that cannot be undone or reverted.
  If uncertain which tier: can this be undone? Yes → proceed + log. No → stop + ask.

================================================================================
5. AGENT ROSTER & LANE RULES
================================================================================

  ┌────────────────────────┬──────────────┬──────────────┬────────────────────────────────────────────────────────────┐
  │ Agent                  │ Machine      │ Interface    │ Scope                                                      │
  ├────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────────────────────────┤
  │ opencode (Salomon)     │ Salomon      │ CLI / COMMS  │ Daily ops, automation, systemd, vault, GPU inference       │
  ├────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────────────────────────┤
  │ opencode (Typhon)      │ Typhon       │ CLI / COMMS  │ Tasks local to Typhon, printer bot, lightweight inference  │
  ├────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────────────────────────┤
  │ Hermes (Assistant)     │ Salomon CLI  │ CLI          │ Assistant lane via qwen3.6 on Orin                         │
  ├────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────────────────────────┤
  │ Claude                 │ Salomon      │ Claude Code  │ Architecture, design, vault-persistent work, session rpts  │
  ├────────────────────────┼──────────────┼──────────────┼────────────────────────────────────────────────────────────┤
  │ Marcus (Perplexity)    │ External     │ Web / MCP    │ Live web research, citations, GitHub + web synthesis       │
  └────────────────────────┴──────────────┴──────────────┴────────────────────────────────────────────────────────────┘

ESCALATION PATH:
  opencode (Typhon) → opencode (Salomon) → Orin → Claude / Marcus

LANE ROUTING RULES:

  Route to opencode (Salomon) when:
    - Daily ops, automation, systemd, vault management
    - Quick queries, tool use, shell execution
    - Voice pipeline (voxtype, Piper)
    - Heavy inference needing GPU (vision, phi4)

  Route to opencode (Typhon) when:
    - Tasks local to Typhon filesystem
    - Printer bot management
    - Lightweight inference

  Route to Orin when:
    - 70B inference needed (djinn-route best)
    - Large code review (djinn-route code-heavy)
    - Hermes/Assistant sessions (djinn-route hermes)
    - Tasks that can tolerate 2–4 tok/s CPU latency

  Route to Claude when:
    - Architecture decisions, multi-agent system design
    - Cross-domain synthesis (psych + law + CS)
    - Session reports, git push, vault-persistent deliverables
    - Spec writing, GATEWAY/ROUTING/PROTOCOL updates

  Route to Marcus when:
    - Deep research requiring live web + citations
    - Full system audits with GitHub + web in same session
    - Research destined for vault notes

CLAUDE INVOCATION RULE (enforced):
  Claude is the lane of last resort. All work must route through djinn-gate
  first. Only if djinn-gate cannot route the task does Claude get it.

  Categories barred from direct Claude invocation:
    ops / file edits / git / systemd / shell        → Salomon/local scripts
    status checks / log rotation / COMMS appends    → Salomon clerk lane
    print pipeline                                  → Salomon production lane
    commission quotes / shop pricing                → djinn-print-quote
    research + citations                            → Marcus lane
    code / scripts (non cross-domain)              → Salomon coding lane

LLM PROFILE REQUIREMENT:
  Every LLM call must declare a profile:
    "deterministic"      temperature=0.1  → retrieval, classification, yes/no
    "structured_output"  temperature=0.2  → JSON extraction, structured formats
    "synthesis"          temperature=0.7  → open-ended reasoning, analysis
  Calls without a declared profile are rejected at djinn.core.llm.chat().

================================================================================
6. MODEL ROUTING — djinn-route
================================================================================

All model selection is automated. Never hardcode model names or Ollama URLs
in scripts. Use djinn-route.

  # Get env vars for a task type
  eval "$(djinn-route <task>)"
  # Uses $OLLAMA_BASE_URL and $DJINN_MODEL

  # Query directly
  djinn-route code-heavy --json    # {"machine":"orin","model":"qwen2.5-coder:32b",...}
  djinn-route vision --model       # llama3.2-vision:11b
  djinn-route best --url           # http://192.168.1.176:11434
  djinn-route --list               # show all task types

FALLBACK: If Orin is unreachable, djinn-route auto-falls back to best Salomon
equivalent. Scripts need zero fallback logic.

TASK → MODEL → MACHINE MAP:

  ┌──────────────┬────────────────────────┬──────────┬────────────────────────────────────┐
  │ Task         │ Model                  │ Machine  │ Notes                              │
  ├──────────────┼────────────────────────┼──────────┼────────────────────────────────────┤
  │ default      │ qwen2.5:7b             │ Salomon  │ Required for OpenClaw tool calling │
  │ reasoning    │ deepseek-r1:7b         │ Salomon  │ Analysis, planning, law/psych      │
  │ code         │ qwen2.5-coder:7b       │ Salomon  │ Fast code, debug, demos            │
  │ code-heavy   │ qwen2.5-coder:32b      │ Orin     │ Full codebase audits, architecture │
  │ notes        │ phi4:14b               │ Salomon  │ Summaries, captions, APA           │
  │ vision       │ llama3.2-vision:11b    │ Salomon  │ Image scoring, thumbnails, QC      │
  │ embed        │ nomic-embed-text       │ Salomon  │ Vector embeddings, semantic search │
  │ best         │ llama3.3:70b           │ Orin     │ Highest quality, latency-tolerant  │
  │ hermes       │ qwen3.6:latest         │ Orin     │ Hermes Agent / Assistant lane      │
  │ creative     │ mistral:7b             │ Salomon  │ Creative writing                   │
  │ lightweight  │ qwen2.5:7b             │ Typhon   │ Typhon-local ops                   │
  └──────────────┴────────────────────────┴──────────┴────────────────────────────────────┘

================================================================================
7. FULL CLI TOOL REFERENCE
================================================================================

All tools live in ~/.local/bin/djinn-*
All tools are available system-wide. No path prefix required.

------------------------------------------------------------------------
7.1 PRINT PIPELINE TOOLS
------------------------------------------------------------------------

  ┌──────────────────────────┬─────────────────────────────────────────────────┐
  │ Command                  │ Function                                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-consult      │ Dry-run slice → real estimates, profile         │
  │                          │ comparison, recommendation. Sends report to     │
  │                          │ Discord + Telegram.                             │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-model-slice        │ Slice with profile shortcuts (proto/standard/   │
  │                          │ production). Runs preflight checks before slice.│
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-quote        │ Commission pricing: cost floor, fair market,    │
  │                          │ premium. Pure Python (no LLM).                  │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-confirm-print      │ TIER 3. Confirm job → safe park calc → upload   │
  │                          │ gcode → start print. Blocked if already         │
  │                          │ printing.                                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-deny-print         │ Remove pending job from queue. Hard-blocked     │
  │                          │ during active print.                            │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-force-cancel       │ TIER 4. Cancel live print. Requires PIN. Moves  │
  │                          │ head to safe park. Cannot be autonomous.        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-backup       │ Backup current gcode + print state snapshot.    │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-recover      │ Crash recovery — restore from backup.           │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-promote      │ Promote backup gcode to active queue slot.      │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-webcam-monitor     │ AKASO Brave 4 frame-diff failure detection.     │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-print-monitor      │ Moonraker polling — progress + completion.      │
  │ djinn-print-monitor-v2   │ v2: failure detection, runs as systemd timer.   │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-park-calc          │ Safe park position calculator from gcode        │
  │                          │ bounding box. Called automatically by confirm.  │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-gcode-safety       │ Post-processes ALL gcode: caps M106 at S128     │
  │                          │ (50% fan max). Run automatically by pipeline.   │
  │                          │ Do not bypass.                                  │
  └──────────────────────────┴─────────────────────────────────────────────────┘

  See CALLIOPE-MANUAL.md for full print workflow detail.

------------------------------------------------------------------------
7.2 DESIGN & 3D TOOLS
------------------------------------------------------------------------

  ┌──────────────────────────┬─────────────────────────────────────────────────┐
  │ Command                  │ Function                                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-design             │ 6-agent manufacturing orchestrator. Runs        │
  │                          │ DesignGenAgent → DesignEditAgent →              │
  │                          │ ProtoOptAgent → DOEPrintOptAgent →              │
  │                          │ PlateNestAgent in sequence.                     │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-generate-3d        │ Interview-first 3D modeling. Prompts for        │
  │                          │ dimensions/intent → generates OpenSCAD via      │
  │                          │ phi4:14b → outputs .stl.                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-3d (Typhon)        │ On Typhon: design / edit / analyze / consult    │
  │                          │ modes for Typhon-local 3D work.                 │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-model-fetch        │ Download 3D models from Printables, Thingiverse,│
  │                          │ or direct URLs. Stages to queue/.               │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-model-mark         │ Engrave TF anvil maker's mark into bottom face  │
  │                          │ (Z_min) of model. Applies mirror automatically. │
  │                          │ Required on all commission parts.               │
  └──────────────────────────┴─────────────────────────────────────────────────┘

------------------------------------------------------------------------
7.3 MEDIA PIPELINE TOOLS
------------------------------------------------------------------------

  ┌──────────────────────────┬─────────────────────────────────────────────────┐
  │ Command                  │ Function                                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-ingest       │ Raw media intake — classifies, stages, creates  │
  │                          │ job record. Entry point for all media work.     │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-photo        │ Photo editing + LUT application. Reads from     │
  │                          │ djinn-lut-gen profiles.                         │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-reel         │ Video/reel editing + clip combination. Outputs  │
  │                          │ platform-ready video.                           │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-caption      │ Caption generation for images and video.        │
  │                          │ Uses phi4:14b (notes profile).                  │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-thumbnail    │ Thumbnail scoring via llama3.2-vision. Returns  │
  │                          │ ranked candidates with quality scores.          │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-publish-prep │ Draft-polish mode + platform export. Formats    │
  │                          │ for Instagram, YouTube, TikTok, etc.            │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-qa           │ Quality checks before publishing. Validates     │
  │                          │ resolution, aspect ratio, captions.             │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-media-repurpose    │ Cross-platform adaptation. Transforms a single  │
  │                          │ source into multiple platform formats.          │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-lut-gen            │ Generate forge/clean/moody .cube LUT files.     │
  │                          │ Outputs to ~/forge/luts/.                       │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-style-scrape       │ DuckDuckGo reference image scraper. Pulls       │
  │                          │ visual references for style matching.           │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-hashtag-update     │ Hashtag bank manager. 236 tags across 11 topic  │
  │                          │ files. Adds, removes, or regenerates tags.      │
  └──────────────────────────┴─────────────────────────────────────────────────┘

------------------------------------------------------------------------
7.4 SYSTEM & VAULT TOOLS
------------------------------------------------------------------------

  ┌──────────────────────────┬─────────────────────────────────────────────────┐
  │ Command                  │ Function                                        │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-gateway            │ Session mode control. status / --dev-session /  │
  │                          │ reset / classify / checkpoint / install-hooks.  │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-route              │ Model routing. Returns OLLAMA_BASE_URL +        │
  │                          │ DJINN_MODEL for any task type. Auto-fallback.   │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-ctx-assembler      │ Per-message context assembly from vault.        │
  │                          │ Called by agents at session start.              │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-ctx-router         │ Service writing CONTEXT.md + STATE.md every     │
  │                          │ 5 minutes. Run as systemd service.              │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-vault-indexer      │ ChromaDB indexer. 688 files, 8,284 chunks.      │
  │                          │ Incremental by default.                         │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-agent-doctor       │ System health check. Runs 11 checks: services,  │
  │                          │ Ollama, Moonraker, git status, COMMS, timers.   │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-sync               │ Vault sync orchestrator. Pull → merge → push.   │
  │                          │ Handles Salomon ↔ Typhon 15-min sync.          │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-daily              │ Daily note creation. Populates template with    │
  │                          │ date, open tasks, upcoming reminders.           │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-morning            │ Morning routine. Briefs Javier: tasks, queue,   │
  │                          │ COMMS since last session.                       │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-weekly             │ Weekly review. Aggregates daily notes, habit    │
  │                          │ completion, project progress.                   │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-claude             │ Claude session bridge. Loads workspace context, │
  │                          │ opens Claude Code with correct working dir.     │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-clerk              │ Task management. Processes RAW/ vault files,    │
  │                          │ routes to correct vault location.               │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-slipbox            │ Zettelkasten processor. Scans notes, generates  │
  │                          │ backlinks using semantic similarity.            │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-embed              │ Embeddings utility. Incremental or --full       │
  │                          │ rebuild of ChromaDB vault index.                │
  ├──────────────────────────┼─────────────────────────────────────────────────┤
  │ djinn-edit-rules         │ Edit OpenClaw rules. Opens SOUL.md / AGENTS.md  │
  │                          │ / IDENTITY.md in editor with validation.        │
  └──────────────────────────┴─────────────────────────────────────────────────┘

================================================================================
8. DISCORD & TELEGRAM COMMAND REFERENCE
================================================================================

DISCORD CHANNEL MAP:

  ┌──────────────────────────┬──────────────────────────────────────────────────┐
  │ Channel                  │ Commands Allowed                                 │
  ├──────────────────────────┼──────────────────────────────────────────────────┤
  │ #djinn-command-center    │ All commands (print + design + media + system)   │
  ├──────────────────────────┼──────────────────────────────────────────────────┤
  │ #3d-printing             │ Print only: queue, confirm, deny, slice,         │
  │                          │ print status, quote, model drop/URL             │
  ├──────────────────────────┼──────────────────────────────────────────────────┤
  │ #media-inbox             │ Media pipeline: ingest, reel, photo, caption,   │
  │                          │ publish, qa, thumbnail                          │
  ├──────────────────────────┼──────────────────────────────────────────────────┤
  │ #general / #djinn-devlog │ Conversation + /status + /help only             │
  ├──────────────────────────┼──────────────────────────────────────────────────┤
  │ #media-status / #post-ready│ Read-only (bot posts here)                    │
  └──────────────────────────┴──────────────────────────────────────────────────┘

TELEGRAM COMMANDS (11 total — all available in any chat):

  /queue                Print queue — all jobs and statuses
  /confirm N            Confirm and start print job N (Tier 3)
  /deny N               Remove pending job N from queue
  /slice N <settings>   Submit slice settings for job N
  /print status         Live printer state, temps, progress
  /callie status        Calliope-specific status (firmware + bed)
  /status               Full Djinn system status
  /quote <desc>         Commission price estimate
  /quick quote <args>   Fast quote with known parameters
  /design status        Current design pipeline job status
  /design               Start a new design session
  /help                 Show all available commands

NOTE: Bot token lives in ~/.openclaw/openclaw.json.
All scripts use direct REST API — not the OpenClaw relay layer.

================================================================================
9. SYSTEMD SERVICES REFERENCE
================================================================================

All run as systemd user services on Salomon unless noted.

  ┌────────────────────────────────────────┬─────────────────────────────────────────────────────┐
  │ Service                                │ Function                                            │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-ctx-router.service               │ Context assembly + vault recall — 5-min timer       │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-telegram-gateway.service         │ Python Telegram bot middleware (11 commands)        │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-discord-gateway.service          │ Python Discord bot middleware (channel-aware)        │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-discord-watch.service            │ Watches #3d-printing for model URLs                 │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-discord-watcher.service          │ Auto-processes STL/3MF attachments in Discord       │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-print-monitor.service            │ Moonraker progress → Discord + Telegram notifs      │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-print-monitor-v2.timer           │ Failure detection — polls every 60s                 │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ printer-error-logger.service           │ Polls Calliope every 30s, logs errors to vault      │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ voxtype.service                        │ Voice dictation daemon (voxtype / Whisper)          │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ openclaw-gateway.service               │ OpenClaw AI gateway (Discord/Telegram routing)      │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ comms-processor.timer                  │ COMMS.md task routing — processes inter-agent msgs  │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-clerk.timer                      │ Processes RAW/ vault files on schedule              │
  ├────────────────────────────────────────┼─────────────────────────────────────────────────────┤
  │ djinn-daily.timer                      │ Daily note + morning briefing                       │
  └────────────────────────────────────────┴─────────────────────────────────────────────────────┘

COMMON SERVICE COMMANDS:

  # Check all Djinn services at once
  systemctl --user list-units 'djinn-*' --all

  # Check all timers (last fire + next fire)
  systemctl --user list-timers

  # Check specific service
  systemctl --user status djinn-discord-gateway.service

  # Restart a service
  systemctl --user restart djinn-discord-gateway.service

  # View recent logs (last 50 lines)
  journalctl --user -u djinn-discord-gateway.service -n 50

  # Follow logs in real time
  journalctl --user -u djinn-discord-gateway.service -f

  # Run a service immediately without waiting for its timer
  systemctl --user start djinn-clerk.service

================================================================================
10. KEY FILE LOCATIONS
================================================================================

  ┌──────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
  │ File                                                         │ Purpose                                                     │
  ├──────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
  │ ~/.openclaw/openclaw.json                                    │ OpenClaw gateway config — agents, channels, models          │
  │ ~/.openclaw/agents/main/sessions/sessions.json               │ Active sessions — reset here if stuck                       │
  │ ~/.openclaw/workspace/SOUL.md                                │ Djinn behavioral rules and vibe                             │
  │ ~/.openclaw/workspace/IDENTITY.md                            │ Who Djinn is (personality, tone)                            │
  │ ~/.openclaw/workspace/USER.md                                │ J
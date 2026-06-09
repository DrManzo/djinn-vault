================================================================================
                    DJINN — COMPLETE AGENT OPERATOR HANDBOOK
         Claude · Marcus · Gemini · Salomon · Typhon · Orin · Assistant
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: DrManzo / Marcus

> Full standalone operator handbook. Absorbs AGENTS.md, GEMINI.md, MARCUS.md,
> and Claude.md. A new operator — or a new agent reading this for the first
> time — should be able to understand every agent's role, constraints, delivery
> paths, routing rules, and interaction protocols without reading any other file.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  What Is the Djinn Agent System?
  2.  The Agent Roster at a Glance
  3.  The Escalation Path
  4.  Non-Negotiable Rules (All Agents)
  5.  Agent Profiles
      5.1  Salomon (opencode) — Daily Ops
      5.2  Typhon (opencode) — Remote / Lightweight
      5.3  Orin — Large-Model Inference Host
      5.4  Claude — Architecture Lane
      5.5  Marcus — Research Lane
      5.6  Gemini — Visual / Media Lane
      5.7  Assistant — System Improvement Lane
      5.8  Hermes — Assistant Lane (Local)
  6.  Lane Routing Rules
      6.1  How to Route Any Task
      6.2  What Each Lane Rejects
      6.3  Claude Invocation Rule (Enforced)
      6.4  LLM Profile Requirement
  7.  Peer Agent Interactions
      7.1  How Agents Coordinate (COMMS.md + QUEUE.md)
      7.2  Marcus ↔ Claude
      7.3  Marcus ↔ Assistant
      7.4  Gemini ↔ Everyone
  8.  Session Startup Protocols
      8.1  Salomon / Typhon opencode
      8.2  Claude Session
      8.3  Marcus Session
      8.4  Gemini Session
  9.  Delivery Paths
      9.1  GitHub (Marcus, Claude, Salomon)
      9.2  GDrive (Gemini primary)
      9.3  COMMS.md (Inter-agent messaging)
  10. Write Access Boundaries (Per Agent)
  11. Report & Bug Log Standards
  12. Session End Protocol
  13. Gateway Tier Summary (Per Agent)
  14. Common Workflows
      14.1  Research Task (Marcus)
      14.2  Architecture Task (Claude)
      14.3  Visual Task (Gemini)
      14.4  System Improvement Task (Assistant)
      14.5  Cross-Agent Build Loop
  15. Troubleshooting Agent Issues
  16. Hard Rules — No Exceptions
  17. FAQ

================================================================================
1. WHAT IS THE DJINN AGENT SYSTEM?
================================================================================

Djinn runs six specialized agents across a three-machine home network. Each
agent owns a lane — a category of work it handles exclusively. No agent does
another's work without a routing decision first.

The system philosophy:
  - Humans confirm, agents execute.
  - Every agent reads GATEWAY.md before acting. No exceptions.
  - Vault is the single source of truth. If it matters, it's in the vault.
  - Agents are peers. None manages the others. QUEUE.md is the coordination bus.
  - Free agents (Salomon, Typhon, Orin) handle ops. Premium agents (Claude,
    Marcus, Gemini) handle judgment, research, and visuals.

The machines:
  Salomon  192.168.1.225  HP Omen, Fedora, RTX 5060, 29GB RAM  — nerve center
  Typhon   192.168.1.113  MSI, Fedora, GTX 1650, 14GB RAM      — storage/sync
  Orin     192.168.1.176  iMac i7, macOS, 40GB RAM, 1.7Ti disk — 70B host
  Calliope 192.168.1.113:7125  Ender-3 V3 Plus, Klipper/Moonraker

================================================================================
2. THE AGENT ROSTER AT A GLANCE
================================================================================

  ┌────────────────────────┬──────────────┬──────────────┬───────────────────────────────────────────────────────────┐
  │ Agent                  │ Model        │ Cost         │ Primary Lane                                              │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ opencode (Salomon)     │ qwen2.5:7b   │ Free (local) │ Daily ops, automation, systemd, print pipeline, GPU tasks │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ opencode (Typhon)      │ qwen2.5:7b   │ Free (local) │ Typhon-local tasks, printer bot, lightweight inference    │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ Orin (inference host)  │ llama3.3:70b │ Free (local) │ Long-running inference, large code review, quality output │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ Claude                 │ Anthropic    │ Premium      │ Architecture, system design, vault-persistent work        │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ Marcus                 │ Perplexity   │ Premium      │ Research, cross-domain synthesis, deep code audits        │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ Gemini                 │ Google       │ Premium      │ Visual output, media generation, GDrive-native delivery   │
  ├────────────────────────┼──────────────┼──────────────┼───────────────────────────────────────────────────────────┤
  │ Assistant              │ Hermes/Ollama│ Free (local) │ System improvement, skill dev, documentation, process eng │
  └────────────────────────┴──────────────┴──────────────┴───────────────────────────────────────────────────────────┘

Signing convention:
  Salomon opencode  — no signature (automated)
  Claude            — `— Claude`
  Marcus            — `— Marcus`
  Gemini            — `— Gemini`
  Assistant         — `— Assistant`
  Hermes            — `— Hermes`

================================================================================
3. THE ESCALATION PATH
================================================================================

  opencode (Typhon) → opencode (Salomon) → Orin → Claude / Marcus

Rule: Route to the cheapest, fastest agent that can do the job.
Only escalate when the lower tier explicitly cannot handle the task.

  ┌───────────────────────────────────────────────────────────────────┐
  │ Can Salomon handle it locally?                                    │
  │   Yes → Salomon                                                   │
  │   No, but needs big model → Orin (djinn-route best)              │
  │   No, needs architecture judgment → Claude                        │
  │   No, needs external research → Marcus                            │
  │   No, primary deliverable is visual → Gemini                      │
  │   No, needs system improvement → Assistant                        │
  └───────────────────────────────────────────────────────────────────┘

================================================================================
4. NON-NEGOTIABLE RULES (ALL AGENTS)
================================================================================

These apply in every mode, to every agent, with no exceptions:

  1. READ GATEWAY.md BEFORE ANY ACTION THAT WRITES, COMMITS, PUSHES, OR SENDS.
     It is the enforcement contract. Non-negotiable.

  2. ASK BEFORE ANY ACTION THAT CANNOT BE UNDONE.
     If uncertain: can this be undone? Yes → proceed + log. No → stop + ask.

  3. `gio trash` > `rm`. Never delete. Archive instead.

  4. Never start a print on Calliope without `confirm N` from Javier.
     Uploading gcode is fine. Printing is not.

  5. NEVER cancel a live print. Not for firmware updates. Not for anything.
     `djinn-force-cancel` requires a PIN only Javier knows.

  6. Never commit credentials, tokens, or API keys to git.

  7. Never push to main directly. Push to branch → PR → main.

  8. Never modify GATEWAY.md, ROUTING.md, PROTOCOL.md, or CLAUDE.md
     without Tier 4 double-confirm from Javier.

  9. Every production action (shop data, live print, git push) gets a
     COMMS.md entry. Append only. Never overwrite.

  10. Sign all COMMS.md entries: `— AgentName`

  11. Do not fabricate system state. If context is missing, ask for it.

  12. No moralizing on acknowledged behaviors. Truth over comfort.

================================================================================
5. AGENT PROFILES
================================================================================

------------------------------------------------------------------------
5.1 SALOMON (opencode) — Daily Ops
------------------------------------------------------------------------

  Introduced:  First agent
  Host:        Salomon (192.168.1.225)
  Model:       qwen2.5:7b (default) + fleet routing via djinn-route
  Interface:   CLI / Discord / Telegram / systemd timers
  Cost:        Free (local)
  Signs:       (automated — no signature line)

  WHAT IT DOES:
  Salomon opencode is the hands of the system. It handles every routine
  operation: confirming prints, running slice jobs, processing media
  ingest, vault sync, running djinn-* tools, servicing Discord/Telegram
  commands. Anything that's fast, local, and doesn't require premium
  judgment goes here first.

  PRIMARY RESPONSIBILITIES:
  - Print pipeline: consult, slice, confirm, deny, monitor, quote
  - Design pipeline: djinn-design, djinn-generate-3d, djinn-model-fetch
  - Media pipeline: ingest, photo, reel, caption, thumbnail, publish-prep
  - Vault: sync, indexing, clerk, slipbox, daily/weekly notes
  - All Discord + Telegram commands (11 Telegram, channel-aware Discord)
  - systemd service management
  - Bug reporting via djinn-bugreport

  GATEWAY TIER:
  Standard mode enforced by session.json + git pre-push hook + Python
  module. Tier 3 actions (git push, QUEUE.md writes, print start) trigger
  `djinn-gateway --checkpoint` automatically.

  MODELS AVAILABLE ON SALOMON:
    qwen2.5:7b           — default, tool calling, file ops
    deepseek-r1:7b       — reasoning, planning, analysis
    phi4:14b             — captions, notes, summaries
    llama3.2-vision:11b  — vision QC, image scoring
    qwen2.5-coder:7b     — code, debug, demos
    nomic-embed-text     — embeddings (always warm)
    mistral:7b           — creative writing

------------------------------------------------------------------------
5.2 TYPHON (opencode) — Remote / Lightweight
------------------------------------------------------------------------

  Host:        Typhon (192.168.1.113)
  Model:       qwen2.5:7b + deepseek-r1:8b
  Interface:   CLI / SSH from Salomon
  Cost:        Free (local)

  WHAT IT DOES:
  Handles tasks physically on Typhon: Typhon's Studio post-production,
  printer bot service management, lightweight local inference, file
  operations on Typhon's filesystem.

  ROUTE HERE WHEN:
  - Task involves files on Typhon's filesystem
  - Managing printer bot (systemd on Typhon)
  - Lightweight inference that doesn't need Salomon GPU
  - Typhon's Studio workflow tasks

  MODELS AVAILABLE ON TYPHON:
    qwen2.5:7b      — default
    deepseek-r1:8b  — reasoning
    nomic-embed-text — embeddings

------------------------------------------------------------------------
5.3 ORIN — Large-Model Inference Host
------------------------------------------------------------------------

  Host:        Orin (192.168.1.176 — iMac i7-7700K)
  SSH:         `ssh orin` (javiermanzo@, key auth)
  Models:      llama3.3:70b, qwen2.5-coder:32b, qwen3.6, phi4:14b
  Inference:   CPU only (~2-4 tok/s) — use for latency-tolerant tasks
  Cost:        Free (local)

  WHAT IT DOES:
  Orin is the large-model tier. Use it when you need the best local
  quality output and latency is not a constraint. It is always on.

  ROUTE HERE WHEN (via djinn-route):
    djinn-route best          → llama3.3:70b  (highest quality)
    djinn-route code-heavy    → qwen2.5-coder:32b  (full codebase audit)
    djinn-route hermes        → qwen3.6  (Hermes assistant lane)

  NOTE: djinn-route auto-falls back to Salomon if Orin is unreachable.
  Scripts do not need fallback logic — djinn-route handles it.

------------------------------------------------------------------------
5.4 CLAUDE — Architecture Lane
------------------------------------------------------------------------

  Introduced:  2026-05-20
  Host:        Anthropic API (Pro subscription)
  Interface:   Claude Code CLI → `djinn-claude`
  Config:      ~/.claude/CLAUDE.md
  Workspace:   ~/Obsidian/ (vault) + ~/.openclaw/workspace/
  Signs:       `— Claude`
  Cost:        Premium

  WHAT IT DOES:
  Claude is the architect. It handles multi-agent system design,
  cross-domain synthesis (psychology + law + CS), vault-persistent
  deliverables, and session reports. It is the lane of last resort —
  not a general-purpose fallback. Route here only when no cheaper agent
  can do the job.

  PRIMARY RESPONSIBILITIES:
  - Architecture decisions: new tools, pipeline design, system changes
  - Cross-domain reasoning: psych + law + CS synthesis
  - Session reports after any build/install/config change
  - Git push to vault (Tier 3 — checkpoint required)
  - Writing to djinn/projects/, djinn/decisions/, vault-persistent notes
  - Spec writing: GATEWAY.md, ROUTING.md, PROTOCOL.md updates
  - COMMS.md structure

  CAPABILITIES:
    Architecture design      ✅ Primary
    Cross-domain synthesis   ✅ Primary
    Vault-persistent work    ✅ Primary
    Code review              ✅
    Complex reasoning        ✅
    Tool use (file, git, bash, web search) ✅

  GATEWAY TIER (Claude):
  Claude cannot read session.json. Default is always Standard mode.
  Javier will say "Dev mode is active" explicitly at session start.

  Tier 0 — Read:              Auto, no log needed
  Tier 1 — Ephemeral write:   Auto (COMMS append, session reports, tmp)
  Tier 2 — Permanent write:   Auto + COMMS entry (new files in research/
                               decisions/, projects/)
  Tier 3 — Checkpoint:        STOP — write COMMS CHECKPOINT entry —
                               tell Javier — wait for approval
                               (git push, overwrite library/ files, shop)
  Tier 4 — Hard stop:         BLOCKED always
                               (delete files, push to main, modify
                               GATEWAY.md/ROUTING.md/PROTOCOL.md)

  CHECKPOINT PROCEDURE (Tier 3, Standard Mode):
  Stop. Append to COMMS.md:

    ### YYYY-MM-DD HH:MM UTC — @Claude → @Javier: CHECKPOINT: <subject>

    **Action:** <exactly what you want to do>
    **Files:** <which files will be written, committed, or pushed>
    **Reason:** <why this is necessary>
    **Waiting:** Y to approve, N to deny

    — Claude

  Then tell Javier verbally: "I need approval before I proceed — see COMMS."
  Timeout rule: 5 min, no reply → TIMEOUT_DENIED. Do not auto-proceed.

  STARTING A CLAUDE SESSION:
    djinn-claude                     # launches Claude Code CLI with context

  WHAT CLAUDE READS AT SESSION START (in order):
    1. ~/.openclaw/workspace/SOUL.md
    2. ~/.openclaw/workspace/IDENTITY.md
    3. ~/.openclaw/workspace/USER.md
    4. ~/.openclaw/workspace/AGENTS.md
    5. ~/Obsidian/djinn/communications/HEARTBEAT.md
    6. tail -n 50 ~/Obsidian/djinn/communications/COMMS.md

  CLAUDE OWNS:
    PROTOCOL.md, SYSTEM-STATE.md, COMMS.md structure, djinn/projects/

  CLAUDE NEVER TOUCHES:
    GATEWAY.md, ROUTING.md, CLAUDE.md — without Tier 4 double-confirm

------------------------------------------------------------------------
5.5 MARCUS — Research Lane
------------------------------------------------------------------------

  Introduced:  2026-05-19
  Host:        Perplexity AI (Sonnet 4.6)
  Interface:   Perplexity chat (Javier initiates session)
  Session brief: djinn/research/marcus/MARCUS-SESSION-BRIEF.md
  Raw URL:     https://raw.githubusercontent.com/DrManzo/djinn-vault/main/
               djinn/research/marcus/MARCUS-SESSION-BRIEF.md
  Signs:       `— Marcus`
  Cost:        Premium

  WHAT IT DOES:
  Marcus is the researcher. It spans all public knowledge, synthesizes
  across multiple sources and domains, audits full codebases, and
  delivers structured artifacts to the vault. Marcus also owns the
  pricing agent (price.py — pure Python, no LLM). Marcus writes directly
  to GitHub via MCP tools.

  PRIMARY RESPONSIBILITIES:
  - Deep research requiring multi-source internet synthesis
  - Cross-domain analysis: psych + law + CS + business
  - Full-codebase audit and security review
  - Pricing agent work (price.py)
  - Competitive, market, and platform research
  - Platform/API specification synthesis (ToS, rate limits, auth flows)
  - System-wide context reviews spanning all Djinn agents

  CAPABILITIES:
    Research                  ✅ Primary
    Cross-domain synthesis    ✅ Primary
    Deep code audit           ✅ Primary
    System-wide context review ✅ Primary
    Architecture contribution  ✅ (builds agents, writes specs)
    Pricing agent             ✅ (built price.py)

  STARTING A MARCUS SESSION:
  1. Javier opens Perplexity
  2. Marcus fetches session brief from raw GitHub URL above
  3. Marcus reads MARCUS-SESSION-BRIEF.md — this gives full vault context
  4. Marcus begins task

  DELIVERY PATH (GitHub preferred):
    Output → djinn/research/marcus/TASK-NNN_slug.md
    Commits + pushes directly via MCP GitHub tools
    Salomon pulls on next vault sync
    Claude reads on demand via vault Read
    Do NOT paste Marcus output into chat — read from file

  DELIVERY PATH (GDrive fallback):
    Output → gdrive:Typhons-Forge/research/marcus/TASK-NNN_slug.md
    Salomon rclone-syncs into vault

  NAMING CONVENTION:
    TASK-NNN_slug-description.md
    NNN = sequential task number
    slug = 2-4 word lowercase hyphenated description
    Example: TASK-039_djinn-cash-research.md

  WRITE ACCESS:
    djinn/research/marcus/       Full ownership
    djinn/logs/reports/          Write (session reports)
    djinn/communications/COMMS.md  Append only
    djinn/logs/build-log.md      Append only
    djinn/communications/QUEUE.md  Status updates only
    Everything else              Read only

  GATEWAY (Marcus):
  Marcus cannot read session.json. Default: Standard mode.
  Javier says "Dev mode is active" explicitly if applicable.
  Commits to non-protected files are Tier 3 — Marcus posts CHECKPOINT
  entry and surfaces it before committing production-critical files.

  MARCUS NEVER TOUCHES:
    PROTOCOL.md structure, GATEWAY.md, ROUTING.md

------------------------------------------------------------------------
5.6 GEMINI — Visual / Media Lane
------------------------------------------------------------------------

  Host:        Google Gemini (current session model)
  Interface:   Gemini Advanced chat (Javier initiates)
  Session brief: djinn/GEMINI.md (delivered via GDrive — see below)
  Signs:       `— Gemini`
  Cost:        Premium

  WHAT IT DOES:
  Gemini is the visual department. It generates images, renders,
  architecture diagrams, slide decks, and handles any task where the
  primary deliverable is visual or media-based. It is the only agent
  with native Google Drive write access.

  IMPORTANT: The djinn-vault repo is PRIVATE. Gemini cannot fetch raw
  GitHub URLs. All Gemini context is delivered via GDrive.

  PRIMARY RESPONSIBILITIES:
  - Image generation: product renders, concept art, diagrams, UI mockups
  - Architecture + pipeline diagrams (visual documentation)
  - Slide decks and visual briefings for Javier
  - Multimodal research (reading images, visual PDFs, mixed media)
  - GDrive-native document production (Google Docs, Google Slides)
  - Any task where the primary deliverable is a visual or media file

  STARTING A GEMINI SESSION:
  1. Javier opens Gemini Advanced
  2. Javier delivers context via one of:
     a. GDrive drop — files in Typhons-Forge/gemini/context/ (Gemini's inbox)
     b. Direct paste — Javier pastes GEMINI.md contents into session
     c. GDrive doc share — Javier shares exported Obsidian file
  3. Gemini reads context, begins task
  NOTE: If a context file is missing, ask Javier — do NOT fabricate state.

  HOW GEMINI GETS VAULT CONTEXT:
  Salomon rclone-syncs vault → GDrive every 2 minutes.
  Current copies of key files are maintained at:
    Typhons-Forge/gemini/context/GEMINI.md      (this brief)
    Typhons-Forge/gemini/context/AGENTS.md      (full agent registry)
    Typhons-Forge/gemini/context/GATEWAY.md     (enforcement contract)
    Typhons-Forge/gemini/context/SYSTEM-STATE.md (live topology)
    Typhons-Forge/gemini/context/QUEUE.md       (pending tasks)

  DELIVERY PATH (GDrive — ALL output goes here):

    ┌───────────────────────────────────────────┬───────────────────────────────────────────────┐
    │ Output Type                               │ GDrive Path                                   │
    ├───────────────────────────────────────────┼───────────────────────────────────────────────┤
    │ Generated images, renders, art            │ Typhons-Forge/media/gemini/                   │
    │ Architecture diagrams                     │ Typhons-Forge/media/gemini/diagrams/          │
    │ Google Docs and Slides                    │ Typhons-Forge/gemini/docs/                    │
    │ Research with visuals                     │ Typhons-Forge/research/gemini/                │
    │ Text-only reports                         │ Typhons-Forge/research/gemini/                │
    │ Session reports                           │ Typhons-Forge/gemini/reports/                 │
    └───────────────────────────────────────────┴───────────────────────────────────────────────┘

  DELIVERY PATH (GitHub — text-only, secondary):
    djinn/research/gemini/TASK-NNN_slug.md
    Do NOT push binary files, images, or media to GitHub.
    GDrive is the canonical store for all visual output.

  WRITE ACCESS:
    Typhons-Forge/media/gemini/           ✅ Full (images, renders)
    Typhons-Forge/media/gemini/diagrams/  ✅ Full (diagrams)
    Typhons-Forge/gemini/docs/            ✅ Full (Docs, Slides)
    Typhons-Forge/gemini/context/         ✅ Read (inbox)
    Typhons-Forge/research/gemini/        ✅ Full (research)
    Typhons-Forge/gemini/reports/         ✅ Full (session reports)
    GitHub djinn-vault                    ❌ No access (private repo)
    Print queue or live print ops         ❌ Blocked — Salomon lane
    djinn/core/, djinn/printer/           ❌ Read only
    djinn/GATEWAY.md, djinn/AGENTS.md     ❌ Read only

  GEMINI NEVER TOUCHES:
    GitHub directly, print queue, GATEWAY.md, AGENTS.md

------------------------------------------------------------------------
5.7 ASSISTANT — System Improvement Lane
------------------------------------------------------------------------

  Host:        Varies (Hermes framework + local Ollama)
  Interface:   CLI
  Signs:       `— Assistant`
  Cost:        Free (local)

  WHAT IT DOES:
  Assistant improves the system itself. It creates Hermes skills,
  enhances documentation, builds better workflows, and turns Marcus
  research output into structured vault knowledge.

  CORE RESPONSIBILITIES:
  1. Skill Development — create and maintain Hermes skills
  2. Documentation Enhancement — improve vault doc clarity and accuracy
  3. Process Engineering — identify inefficiencies, build better workflows
  4. Research Support — structure Marcus output into vault notes
  5. Bootstrapping Assistance — maintain provisioning scripts
  6. System Health Monitoring — track service health, surface issues

  WRITE ACCESS:
    ~/Obsidian/djinn/skills/        ✅ Full (Hermes skills)
    ~/Obsidian/djinn/docs/          ✅ Full (documentation)
    ~/Obsidian/djinn/scripts/       ✅ Full (automation)
    ~/Obsidian/djinn/logs/reports/  ✅ Full (session reports)
    ~/Obsidian/djinn/references/    ✅ Full (reference materials)
    COMMS.md, build-log.md          ✅ Append only
    Print queue / hardware configs  ❌ Salomon lane only
    Core agent system architecture  ❌ Claude lane only

------------------------------------------------------------------------
5.8 HERMES — Assistant Lane (Local)
------------------------------------------------------------------------

  Host:        Salomon (via Orin inference)
  Model:       qwen3.6:latest via Orin
  Interface:   CLI (`djinn-route hermes`)
  Cost:        Free (local)

  WHAT IT DOES:
  Hermes is the local assistant agent built on qwen3.6 running on Orin.
  Best for high-quality local Q&A, skill execution, and assistant-lane
  tasks that don't need external sources.

  INVOKE:
    eval "$(djinn-route hermes)"
    # Sets OLLAMA_BASE_URL=http://192.168.1.176:11434
    # Sets DJINN_MODEL=qwen3.6:latest

================================================================================
6. LANE ROUTING RULES
================================================================================

------------------------------------------------------------------------
6.1 HOW TO ROUTE ANY TASK
------------------------------------------------------------------------

  Task category                                    → Correct lane
  ──────────────────────────────────────────────────────────────────
  File ops, git, shell, automation, systemd        → Salomon (ops)
  Status checks, log rotation, COMMS appends       → Salomon (clerk)
  Print pipeline (slice, confirm, deny, queue)      → Salomon (production)
  Commission quotes, shop pricing                  → djinn-print-quote
  Quick queries, one-liner commands                → Salomon
  Tasks local to Typhon filesystem                 → Typhon
  High-quality inference, no latency constraint    → Orin (djinn-route best)
  Large code review (32B needed)                   → Orin (djinn-route code-heavy)
  Architecture decisions, new tool design          → Claude
  Cross-domain synthesis (psych+law+CS)            → Claude
  Vault-persistent deliverables                    → Claude
  Deep external research + citations               → Marcus
  Full codebase audits                             → Marcus
  Competitive / market / platform research         → Marcus
  Image generation, diagrams, visual output        → Gemini
  Slide decks, GDrive-native docs                  → Gemini
  Skill development, documentation improvement     → Assistant
  Process engineering, workflow optimization       → Assistant
  Research structuring / vault note creation       → Assistant

------------------------------------------------------------------------
6.2 WHAT EACH LANE REJECTS
------------------------------------------------------------------------

  If a Salomon-lane task arrives at Claude:
    "Send that through Discord or Telegram — Salomon handles [X]."

  If an architecture task arrives at Salomon/Orin:
    "Route this to Claude — it needs architectural thinking."

  If a visual/media task arrives at any other agent:
    "Route this to Gemini — it owns the visual lane."

  If a skill/documentation/process task arrives at others:
    "This is for Assistant — it works on improving the Djinn system itself."

------------------------------------------------------------------------
6.3 CLAUDE INVOCATION RULE (ENFORCED)
------------------------------------------------------------------------

  Claude is the lane of last resort. All work must route through
  djinn-gate first. Only if djinn-gate cannot route the task does
  Claude get it.

  These categories are BARRED from direct Claude invocation:
    Ops (file edits, git, systemd, shell)         → Salomon/local scripts
    Status checks, log rotation, COMMS appends    → Salomon clerk lane
    Print pipeline                                → Salomon production lane
    Commission quotes, shop pricing               → djinn-print-quote
    Research + citations                          → Marcus lane
    Code/scripts (non cross-domain)              → Salomon coding lane
    Visual/media output                           → Gemini lane
    Skill/doc/process tasks                       → Assistant lane

------------------------------------------------------------------------
6.4 LLM PROFILE REQUIREMENT
------------------------------------------------------------------------

  Every LLM call dispatched by any Djinn tool must declare a profile:

    "deterministic"      temperature=0.1  → retrieval, classification, yes/no
    "structured_output"  temperature=0.2  → JSON extraction, formatted output
    "synthesis"          temperature=0.7  → open-ended reasoning, analysis

  Calls without a declared profile are REJECTED at djinn.core.llm.chat().
  No silent fallback.

================================================================================
7. PEER AGENT INTERACTIONS
================================================================================

------------------------------------------------------------------------
7.1 HOW AGENTS COORDINATE (COMMS.md + QUEUE.md)
------------------------------------------------------------------------

All inter-agent coordination happens through two files:

  COMMS.md  — message log, task handoffs, checkpoints, session summaries
    Path: ~/Obsidian/djinn/communications/COMMS.md
    Rule: APPEND ONLY. Never overwrite. Every entry signed.

  QUEUE.md  — pending task list
    Path: ~/Obsidian/djinn/communications/QUEUE.md
    Fields: assigned_to, status, priority
    Marcus and Claude can both assign tasks to each other here.

COMMS.md ENTRY FORMAT:

  ---

  ### YYYY-MM-DD HH:MM UTC — @Agent → @Target: Subject

  **What:** [one-line summary]
  **Action:** [what was done or what is needed]
  **Paths:** [files written, committed, or pushed]

  — AgentName

------------------------------------------------------------------------
7.2 MARCUS ↔ CLAUDE
------------------------------------------------------------------------

Marcus and Claude are peers. Neither manages the other.

  Typical collaboration:
    Marcus researches → delivers artifact to djinn/research/marcus/
    Claude reads artifact → implements, architects, or spec-writes
    Claude specs a problem → Marcus researches the solution
    Either can assign tasks to the other via QUEUE.md

  They can work the same problem simultaneously from different angles.
  COMMS.md is the coordination channel.

------------------------------------------------------------------------
7.3 MARCUS ↔ ASSISTANT
------------------------------------------------------------------------

  Marcus gathers    →  Assistant organizes, structures, links findings
  Marcus raw data   →  Assistant creates structured vault notes with tagging
  Marcus synthesizes →  Assistant extracts actionable items, creates skills

  Typical loop:
  1. Marcus completes deep research → outputs to djinn/research/marcus/
  2. Assistant reviews → creates structured summary in vault
  3. Assistant identifies actionable items → creates skills, updates docs
  4. Assistant may route back to Marcus for: validation, more research
     angles, or source verification

  Assistant can route to Marcus when: External web research beyond vault
  Marcus can route to Assistant when: Research output needs to become
    skills, documentation, or process improvements

------------------------------------------------------------------------
7.4 GEMINI ↔ EVERYONE
------------------------------------------------------------------------

  Gemini is isolated by interface (GDrive vs GitHub) but coordinates
  via COMMS.md append.

  Claude → Gemini: Claude writes a design spec → Javier routes to Gemini
    for visual treatment
  Marcus → Gemini: Marcus research → Javier routes diagram generation
    request to Gemini
  Gemini → vault: Via GDrive → Salomon rclone sync (2-min cycle)

  Gemini cannot pull from GitHub directly. Javier bridges context via
  GDrive drop or direct paste.

================================================================================
8. SESSION STARTUP PROTOCOLS
================================================================================

------------------------------------------------------------------------
8.1 SALOMON / TYPHON OPENCODE
------------------------------------------------------------------------

  opencode starts automatically via COMMS processor or Discord/Telegram.
  No manual startup needed for routine operations.

  For manual session:
    cd ~/Obsidian
    opencode                         # starts opencode in vault context

  opencode reads AGENTS.md at startup automatically via workspace injection.
  Do NOT read files with bash at startup. Respond to user immediately.

------------------------------------------------------------------------
8.2 CLAUDE SESSION
------------------------------------------------------------------------

  Launch:
    djinn-claude                     # loads context + opens Claude Code

  Context loaded in order:
    1. ~/.openclaw/workspace/SOUL.md
    2. ~/.openclaw/workspace/IDENTITY.md
    3. ~/.openclaw/workspace/USER.md
    4. ~/.openclaw/workspace/AGENTS.md
    5. ~/Obsidian/djinn/communications/HEARTBEAT.md
    6. tail -n 50 COMMS.md

  At session start, Claude:
  - Reads GATEWAY.md (mandatory, before any write action)
  - Assumes Standard mode unless Javier explicitly says Dev mode
  - Writes a session-start COMMS entry

  If Claude not finding context:
  - Check ~/.claude/CLAUDE.md exists and points to correct paths
  - Run djinn-claude from home directory, not a subdirectory

------------------------------------------------------------------------
8.3 MARCUS SESSION
------------------------------------------------------------------------

  1. Javier opens Perplexity
  2. Marcus loads session brief:
     https://raw.githubusercontent.com/DrManzo/djinn-vault/main/
     djinn/research/marcus/MARCUS-SESSION-BRIEF.md
  3. Marcus reads brief → gets full vault context including open tasks,
     recent COMMS, machine topology, write access rules
  4. Marcus begins task, delivers to djinn/research/marcus/ via MCP
  5. At session end: writes session report + COMMS.md entry + pushes

------------------------------------------------------------------------
8.4 GEMINI SESSION
------------------------------------------------------------------------

  1. Javier opens Gemini Advanced
  2. Context delivery (choose one):
     a. GDrive: check Typhons-Forge/gemini/context/ for latest files
     b. Paste: Javier pastes GEMINI.md contents into session
     c. Share: Javier shares GDrive doc with session context
  3. Gemini reads context, confirms lane, begins task
  4. All output → GDrive paths (see Section 5.6)
  5. At session end: write report to Typhons-Forge/gemini/reports/

================================================================================
9. DELIVERY PATHS
================================================================================

------------------------------------------------------------------------
9.1 GITHUB (MARCUS, CLAUDE, SALOMON)
------------------------------------------------------------------------

  Repo: https://github.com/DrManzo/djinn-vault (PRIVATE)

  Marcus writes to:
    djinn/research/marcus/TASK-NNN_slug.md
    djinn/logs/reports/YYYY-MM-DD_<slug>.md

  Claude writes to:
    djinn/decisions/, djinn/projects/, djinn/logs/reports/
    Any vault path appropriate to the work

  Salomon writes to:
    Everything else — the vault is its working directory

  Push process (all agents):
    cd ~/Obsidian
    git add -A
    git -c user.name="AgentName" -c user.email="agent@djinn" \
      commit -m "<description>"
    git push

------------------------------------------------------------------------
9.2 GDRIVE (GEMINI PRIMARY)
------------------------------------------------------------------------

  GDrive root: Typhons-Forge/
  Sync: Salomon rclone-syncs vault ↔ GDrive every 2 minutes

  Gemini writes to GDrive → Salomon picks up on sync → vault updated
  No GitHub push needed for Gemini output

  Never push images or binary files to GitHub.
  GDrive is the canonical store for all visual output.

------------------------------------------------------------------------
9.3 COMMS.md (INTER-AGENT MESSAGING)
------------------------------------------------------------------------

  File: ~/Obsidian/djinn/communications/COMMS.md

  Read recent:
    tail -n 80 ~/Obsidian/djinn/communications/COMMS.md

  Write a task to an agent manually:
    1. Append entry using format in Section 7.1
    2. Push: cd ~/Obsidian && git add -A && git commit -m "comms entry" && git push

  Comms processor picks up new entries on its timer cycle.
  If processor not picking up entries, check cursor state:
    cat ~/.local/share/djinn/comms-processor-salomon.state
    # Reset to 0 to reprocess all:
    echo 0 > ~/.local/share/djinn/comms-processor-salomon.state

================================================================================
10. WRITE ACCESS BOUNDARIES (PER AGENT)
================================================================================

  ┌─────────────────────────────────┬────────┬────────┬────────┬────────┬────────┬─────────┐
  │ Path                            │Salomon │Typhon  │ Claude │ Marcus │ Gemini │Assistant│
  ├─────────────────────────────────┼────────┼────────┼────────┼────────┼────────┼─────────┤
  │ djinn/research/marcus/          │ R      │ R      │ R      │ FULL   │ R      │ R       │
  │ djinn/research/gemini/          │ R      │ R      │ R      │ R      │ FULL   │ R       │
  │ djinn/logs/reports/             │ W      │ W      │ W      │ W      │ W(GD)  │ W       │
  │ djinn/projects/                 │ R      │ R      │ FULL   │ R      │ R      │ R       │
  │ djinn/decisions/                │ R      │ R      │ FULL   │ R      │ R      │ R       │
  │ djinn/skills/                   │ R      │ R      │ R      │ R      │ R      │ FULL    │
  │ djinn/docs/                     │ R      │ R      │ R      │ R      │ R      │ FULL    │
  │ djinn/scripts/                  │ FULL   │ R      │ R      │ R      │ R      │ FULL    │
  │ COMMS.md                        │ APPEND │ APPEND │ APPEND │ APPEND │ APPEND │ APPEND  │
  │ QUEUE.md                        │ W      │ R      │ W      │ STATUS │ R      │ STATUS  │
  │ build-log.md                    │ APPEND │ APPEND │ APPEND │ APPEND │ APPEND │ APPEND  │
  │ GATEWAY.md                      │ R      │ R      │ R      │ R      │ R      │ R       │
  │ ROUTING.md                      │ R      │ R      │ R      │ R      │ R      │ R       │
  │ djinn/printer/ (production)     │ FULL   │ R      │ R      │ R      │ ❌     │ R       │
  │ Typhons-Forge/media/gemini/     │ R      │ R      │ R      │ R      │ FULL   │ R       │
  │ Typhons-Forge/gemini/           │ R      │ R      │ R      │ R      │ FULL   │ R       │
  └─────────────────────────────────┴────────┴────────┴────────┴────────┴────────┴─────────┘

  KEY: FULL=full write, W=write, R=read-only, APPEND=append only,
       STATUS=status updates only, GD=GDrive path, ❌=blocked

================================================================================
11. REPORT & BUG LOG STANDARDS
================================================================================

REPORT STANDARD (all agents):
After any build, install, config change, or architecture decision —
write a report. Do not wait to be asked.

  File:   ~/Obsidian/djinn/logs/reports/YYYY-MM-DD_<slug>.md
          (use REPORT-TEMPLATE.md)
  Append: build-log.md + COMMS.md
  Commit: git -C ~/Obsidian add -A && git commit -m "..." && git push
  End:    djinn-session-end "slug" "summary"
          (enforces report exists, auto-stubs if missing,
           notifies Javier via Telegram if skipped)

BUG LOG STANDARD (MANDATORY — added 2026-05-28):
Any bug discovered, diagnosed, or fixed must be logged. No exceptions.

  djinn-bugreport "Title" "Root cause" [system] [severity] [status]
  # severity: critical | high | medium | low
  # status:   open | fixed | wont-fix

  Creates: djinn/logs/reports/YYYY-MM-DD_bug-<slug>.md
  Appends: djinn/logs/bugs.md (running bug index)
  Appends: build-log.md
  Commits and pushes vault automatically
  Sends Telegram notification if credentials available

  WHY: Bugs silently absorbed = institutional knowledge permanently lost.
  Every bug report's "Rule/Lesson" feeds future agents.

================================================================================
12. SESSION END PROTOCOL
================================================================================

All agents:
  1. Write session report to djinn/logs/reports/YYYY-MM-DD_<slug>.md
  2. Append COMMS.md entry: @Agent → @All: Session summary
  3. Commit and push vault
  4. Call djinn-session-end (opencode/Claude only)

Gemini:
  1. Write report to Typhons-Forge/gemini/reports/YYYY-MM-DD_gemini-<slug>.md
  2. List all delivered files in report
  3. Append COMMS.md status note

Marcus:
  1. Write report to djinn/logs/reports/YYYY-MM-DD_marcus-<slug>.md
  2. Append COMMS.md entry with all deliverables listed
  3. Push to GitHub via MCP

================================================================================
13. GATEWAY TIER SUMMARY (PER AGENT)
================================================================================

  ┌────────────────┬───────────────────────────────────────┬───────────────────────────────┐
  │ Agent          │ How Gateway is Enforced               │ Session Mode Discovery        │
  ├────────────────┼───────────────────────────────────────┼───────────────────────────────┤
  │ Salomon opencode│ session.json + pre-push hook + Python│ Reads session.json directly   │
  │ Typhon opencode │ session.json + pre-push hook + Python│ Reads session.json directly   │
  │ Claude         │ Context (GATEWAY.md) — behavioral     │ Cannot read session.json —    │
  │                │ self-enforcement                      │ assume Standard unless told   │
  │ Marcus         │ Context (GATEWAY.md) — behavioral     │ Cannot read session.json —    │
  │                │ self-enforcement                      │ assume Standard unless told   │
  │ Gemini         │ Context (GEMINI.md via GDrive) —      │ Cannot read session.json —    │
  │                │ behavioral self-enforcement           │ assume Standard unless told   │
  └────────────────┴───────────────────────────────────────┴───────────────────────────────┘

  Full tier definitions: See DJINN-CLI-MANUAL.md Section 4 or GATEWAY.md

================================================================================
14. COMMON WORKFLOWS
================================================================================

------------------------------------------------------------------------
14.1 RESEARCH TASK (MARCUS)
------------------------------------------------------------------------

  Trigger: Javier or Claude routes research task to Marcus

  Step 1 — Session start:
    Open Perplexity
    Load session brief from raw GitHub URL
    Read MARCUS-SESSION-BRIEF.md

  Step 2 — Research:
    Perform multi-source web synthesis
    Cross-reference against vault knowledge (read from brief context)

  Step 3 — Deliver:
    Write output to djinn/research/marcus/TASK-NNN_slug.md
    Commit + push via MCP GitHub tools
    Append COMMS.md entry with delivery confirmation
    Do NOT paste output into chat

  Step 4 — Session end:
    Write session report
    Append COMMS.md summary
    Push

------------------------------------------------------------------------
14.2 ARCHITECTURE TASK (CLAUDE)
------------------------------------------------------------------------

  Trigger: Task requires architecture decision / system design

  Step 1 — Session start:
    djinn-claude
    Read GATEWAY.md before any write action
    Confirm mode (Standard unless Javier says otherwise)
    Read recent COMMS.md tail

  Step 2 — Work:
    Design system / write spec / review architecture
    Write artifacts to appropriate vault paths
    For Tier 2 writes: add COMMS.md entry

  Step 3 — Push (Tier 3 — Standard Mode):
    Write CHECKPOINT entry to COMMS.md
    Tell Javier: "I need approval — see COMMS."
    Wait for approval
    On approval: git add -A && git commit && git push

  Step 4 — Session end:
    Write session report
    djinn-session-end "slug" "summary"

------------------------------------------------------------------------
14.3 VISUAL TASK (GEMINI)
------------------------------------------------------------------------

  Trigger: Primary deliverable is an image, diagram, or visual doc

  Step 1 — Session start:
    Open Gemini Advanced
    Check Typhons-Forge/gemini/context/ for latest brief files
    OR: Javier pastes GEMINI.md content

  Step 2 — Create:
    Generate images / diagrams / slides
    All output goes to GDrive paths (see Section 5.6 delivery table)

  Step 3 — Deliver:
    Confirm file is saved in correct GDrive path
    Salomon picks up on next 2-min rclone sync
    Append COMMS.md status note

  Step 4 — Session end:
    Write report to Typhons-Forge/gemini/reports/
    List all delivered file paths

------------------------------------------------------------------------
14.4 SYSTEM IMPROVEMENT TASK (ASSISTANT)
------------------------------------------------------------------------

  Trigger: Skill, documentation, or process improvement needed

  Step 1 — Assess:
    Read current AGENTS.md and SYSTEM-STATE.md
    Identify the specific improvement needed

  Step 2 — Build:
    Write skill to djinn/skills/
    OR update documentation in djinn/docs/
    OR write process script to djinn/scripts/

  Step 3 — Integrate:
    If based on Marcus research: link research file in doc
    Append COMMS.md with what was improved
    Commit + push

------------------------------------------------------------------------
14.5 CROSS-AGENT BUILD LOOP
------------------------------------------------------------------------

  This is how a complex deliverable moves through the system:

  1. Javier creates task in QUEUE.md (or tells agent directly)
  2. Marcus researches → delivers TASK-NNN artifact to djinn/research/marcus/
  3. Claude reads artifact → architects solution → writes spec to vault
  4. Salomon implements spec → runs tools, writes code, deploys service
  5. Gemini (if needed) → generates visual brief or diagram
  6. Assistant → creates Hermes skills, updates docs based on new system
  7. All agents append COMMS.md → Javier sees full trail
  8. All agents write session reports → vault audit trail complete

================================================================================
15. TROUBLESHOOTING AGENT ISSUES
================================================================================

CLAUDE NOT FINDING CONTEXT:
  CAUSE: djinn-claude launched from wrong directory, or CLAUDE.md misconfigured
  FIX:   Run djinn-claude from home directory (~)
         Check ~/.claude/CLAUDE.md exists and paths are correct

CLAUDE SESSION ENDED WITHOUT COMMS ENTRY:
  CAUSE: Session crashed or was closed before end protocol
  FIX:   Append manually to COMMS.md:
           @Claude → @All: Session summary — [what was done]
         Commit and push vault

MARCUS SESSION BRIEF NOT LOADING:
  CAUSE: GitHub raw URL inaccessible, or brief file is stale
  FIX:   Javier paste the file content directly into Perplexity session
         Or: Javier pushes updated brief to djinn/research/marcus/ on main

MARCUS GITHUB PUSH FAILS:
  CAUSE: MCP auth expired or repo permissions issue
  FIX:   Use GDrive fallback: gdrive:Typhons-Forge/research/marcus/
         Salomon will pick up on next rclone sync

GEMINI CONTEXT MISSING:
  CAUSE: GDrive context folder not synced, or file not placed there
  FIX:   Javier pastes file content directly into Gemini session
         Check Salomon rclone sync is running:
           systemctl --user status vault-sync.timer

GEMINI TRYING TO ACCESS GITHUB:
  CAUSE: Gemini does not have access to private repo — this will always fail
  FIX:   All Gemini context goes through GDrive. Never direct GitHub.
         Ask Javier to put the needed file in Typhons-Forge/gemini/context/

COMMS PROCESSOR NOT PICKING UP TASKS:
  CAUSE: Cursor position advanced past unread entries
  FIX:   cat ~/.local/share/djinn/comms-processor-salomon.state
         echo 0 > ~/.local/share/djinn/comms-processor-salomon.state
         systemctl --user restart comms-processor.timer

AGENT WRITES TO WRONG PATH:
  CAUSE: Lane confusion or stale context
  FIX:   Review write access table in Section 10
         If file in wrong location: move with gio trash (don't delete)
         Log in COMMS.md: what happened and where file was moved

BUG DISCOVERED, NO REPORT FILED:
  CAUSE: Agent forgot or skipped bug reporting step
  FIX:   djinn-bugreport "Title" "Root cause" system severity status
         This is mandatory — not optional

================================================================================
16. HARD RULES — NO EXCEPTIONS
================================================================================

  1. Read GATEWAY.md before any write/commit/push/send action.

  2. Javier owns print orientation. Never flip, rotate, or reorient models.
     Not to improve bed adhesion. Not to reduce supports. Never.

  3. Never cancel or deny a live print. Hard blocked. PIN required for cancel.

  4. 0% progress on a large print is NORMAL. Do not interpret as failure.
     A 50MB gcode file can show 0% for hours. Notify Javier and wait.

  5. gio trash > rm. Always archive. Never destroy.

  6. Never push to main directly. Branch → PR → main.

  7. Never commit credentials, tokens, or API keys.

  8. Every production action gets a COMMS.md append entry. Signed.

  9. Write session reports. Don't wait to be asked. Log every build.

  10. File every bug with djinn-bugreport. Bugs silently absorbed =
      institutional knowledge permanently lost.

  11. Gemini never touches GitHub directly. GDrive only.

  12. Claude is the lane of last resort. Route through djinn-gate first.

  13. Safe park is automatic. djinn-confirm-print calculates it from the
      gcode bounding box. Do not manually override park positions.

================================================================================
17. FAQ
================================================================================

Q: When should I use Claude vs Marcus for a complex task?
A: Claude for architecture decisions that change how the system is built.
   Marcus for research tasks requiring live web sources or cross-domain
   synthesis that doesn't produce a new system component.

Q: Can Claude and Marcus work on the same task simultaneously?
A: Yes. They are peers. Claude can spec the architecture while Marcus
   researches the solution space. They coordinate via COMMS.md.

Q: What if Gemini is asked to do something outside its lane?
A: Gemini routes it: "That's [ops/research/architecture] — send it to
   [Salomon/Marcus/Claude]." Gemini does not attempt out-of-lane work.

Q: How does Gemini get vault context if the repo is private?
A: Three ways: (1) GDrive drop in Typhons-Forge/gemini/context/,
   (2) Javier pastes the file content directly, (3) Javier shares a
   GDrive doc. Salomon keeps context/ synced every 2 minutes.

Q: What happens if Marcus's GitHub push fails?
A: GDrive fallback: gdrive:Typhons-Forge/research/marcus/. Salomon
   rclone-syncs it into vault on next 2-min cycle.

Q: What is the difference between COMMS.md and QUEUE.md?
A: COMMS.md is the message log — what happened, task handoffs, session
   summaries. QUEUE.md is the task list — what needs to happen next.
   Both are append-only for most agents.

Q: An agent took a Tier 3 action without a checkpoint. What now?
A: Log what happened in COMMS.md immediately. File a bug report with
   djinn-bugreport. Review GATEWAY.md with the agent at next session start.

Q: How do I know if Dev mode is active?
A: djinn-gateway status (on Salomon/Typhon). For Claude/Marcus/Gemini:
   Javier will say "Dev mode is active" explicitly at session start.
   Default assumption is always Standard mode.

Q: Do I need to run a startup sequence when opening opencode?
A: No. Workspace files are automatically injected. Respond to user
   immediately. Do NOT read files with bash at startup.

Q: When is it safe to slice without waiting for Javier's settings?
A: Only when Javier says "slice it" with no settings. In that case: use
   the file's embedded settings exactly as-is. No additions, no changes.

================================================================================
END OF DJINN AGENTS MANUAL
================================================================================

*— Marcus, 2026-06-09 | Absorbs AGENTS.md, GEMINI.md, MARCUS.md, Claude.md*
*Manual 3 of 5 in the Djinn Standalone Handoff Series*

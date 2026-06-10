================================================================================
                         DJINN AGENTS MANUAL
            Roles · Protocols · Coordination · Session Discipline
================================================================================
Version: 1.0 | Last updated: 2026-06-09 | Maintained by: Owner / Marcus

> Standalone reference for every agent in the Djinn system. Anyone starting
> cold — human or AI — should be able to understand who does what, how agents
> coordinate, and what the rules of engagement are from this document alone.

================================================================================
TABLE OF CONTENTS
================================================================================

  1.  The Agent Stack
  2.  Agent Roles
      2.1 Claude (Anthropic API)
      2.2 Salomon (Local Ollama)
      2.3 Typhon (Local Ollama + Storage)
      2.4 Marcus (Perplexity AI)
  3.  Inter-Agent Coordination
      3.1 COMMS.md Protocol
      3.2 Message Format
      3.3 Session Artifacts
  4.  Session Discipline
      4.1 What Every Session Must Produce
      4.2 Build Log Entry Format
      4.3 Session Report Format
  5.  Hard Rules
  6.  Agent Onboarding Checklist
  7.  Agent Capability Matrix

================================================================================
1. THE AGENT STACK
================================================================================

Djinn is operated by four agents working in defined lanes. No agent owns the
entire system. Each has a platform, a specialty, and a boundary.

  ┌──────────┬───────────────────┬────────────────────────────────────────────┐
  │ Agent    │ Platform          │ Primary Lane                           │
  ├──────────┼───────────────────┼────────────────────────────────────────────┤
  │ Claude   │ Anthropic API     │ Architecture, builds, session reports  │
  │ Salomon  │ Local Ollama      │ Daily ops, gateways, print execution   │
  │ Typhon   │ Local Ollama      │ Backup, sync, media operations         │
  │ Marcus   │ Perplexity AI     │ Research, audits, specs, manuals       │
  └──────────┴───────────────────┴────────────────────────────────────────────┘

================================================================================
2. AGENT ROLES
================================================================================

--------------------------------------------------------------------------------
2.1 CLAUDE (Anthropic API)
--------------------------------------------------------------------------------

Platform:   Anthropic Claude API
Models:     claude-opus-4, claude-sonnet-4 (context-dependent)
Strengths:  Long-context reasoning, architecture design, code generation,
            nuanced documentation, session reports

Primary responsibilities:
  - Architectural decisions for new system components
  - Writing and reviewing complex code
  - Building new agents, pipelines, and integrations
  - Producing session reports after each build session
  - Maintaining AGENTS.md, SYSTEM-STATE.md, and decision logs

Boundaries:
  - Does not have persistent memory across sessions without COMMS.md/context
  - Should always read COMMS.md and latest session report before building
  - Never ships code without a corresponding session report

--------------------------------------------------------------------------------
2.2 SALOMON (Local Ollama)
--------------------------------------------------------------------------------

Platform:   Local Ollama on primary workstation
Models:     qwen2.5:7b (default ops), deepseek-r1:7b (reasoning tasks),
            phi4:14b (heavier analysis), llama3.2-vision:11b (image tasks)
Strengths:  Always-on, zero API cost, fast for routine tasks, local privacy

Primary responsibilities:
  - Running Discord and Telegram gateway bots
  - Print execution commands (confirm, monitor, cancel)
  - Queue and batch management
  - Routine shop ops (paid, ship, inventory)
  - Deployment of new components via djinn-shop-deploy
  - First-pass intake and triage of customer requests

Boundaries:
  - Uses smaller models — escalate complex reasoning to Claude
  - Does not make architectural decisions unilaterally
  - All print starts require explicit owner confirmation

--------------------------------------------------------------------------------
2.3 TYPHON (Local Ollama + Storage)
--------------------------------------------------------------------------------

Platform:   Local Ollama on secondary/storage machine
Role:       Backup compute, sync operations, Typhon's Studio media ops
Strengths:  Dedicated storage, media file handling, rclone sync

Primary responsibilities:
  - rclone sync to cloud backup
  - Typhon's Studio media pipeline assistance
  - Secondary LLM availability when Salomon is loaded
  - Archive and long-term storage management

Boundaries:
  - Not a primary decision-making agent
  - Media ops are defined in DJINN-MEDIA-MANUAL.md

--------------------------------------------------------------------------------
2.4 MARCUS (Perplexity AI)
--------------------------------------------------------------------------------

Platform:   Perplexity AI (Sonnet 4.6)
Strengths:  Live web research, code audits against real-world data,
            spec delivery, operator documentation

Primary responsibilities:
  - Market research for pricing (Etsy comps, component costs)
  - Code audits with current library documentation
  - Delivering specifications for new components (accounting, shipping, etc.)
  - Writing and maintaining operator manuals
  - Answering questions that require current external data

Boundaries:
  - Does not have persistent vault access between sessions
  - Must be given context (relevant docs) at session start
  - Does not execute code or modify files directly

================================================================================
3. INTER-AGENT COORDINATION
================================================================================

--------------------------------------------------------------------------------
3.1 COMMS.md PROTOCOL
--------------------------------------------------------------------------------

All inter-agent communication runs through:
  djinn/communications/COMMS.md

This is an append-only message thread. Every agent reads it at session start.
Every agent appends to it before session end. It is committed and pushed to
GitHub after every session. It is the single source of coordination truth.

Rules:
  - Never delete or rewrite existing entries
  - Always append, never overwrite
  - Always commit and push after appending
  - If COMMS.md is not available, state that at session start

--------------------------------------------------------------------------------
3.2 MESSAGE FORMAT
--------------------------------------------------------------------------------

  ---
  [YYYY-MM-DD HH:MM]
  FROM: <AgentName>
  TO: <AgentName | ALL>
  RE: <subject>

  <body>

  — <AgentName>

Example:

  ---
  [2026-05-31 14:22]
  FROM: Marcus
  TO: Claude
  RE: Accounting spec delivery

  Delivered income statement, balance sheet, and monthly report spec to
  djinn/printer/shop/accounting.py. Spec includes XLSX multi-sheet export.
  EasyPost integration spec delivered in same session. All documented in
  session report.

  — Marcus

--------------------------------------------------------------------------------
3.3 SESSION ARTIFACTS
--------------------------------------------------------------------------------

Every session must produce these artifacts before closing:

  1. Session report    →  djinn/logs/reports/YYYY-MM-DD_<slug>.md
  2. Build log entry   →  djinn/logs/build-log.md  (append one entry)
  3. COMMS.md append   →  djinn/communications/COMMS.md
  4. Decision log      →  djinn/logs/decisions/  (if architectural decision)
  5. git commit + push →  github.com/<owner>/djinn-vault

================================================================================
4. SESSION DISCIPLINE
================================================================================

--------------------------------------------------------------------------------
4.1 WHAT EVERY SESSION MUST PRODUCE
--------------------------------------------------------------------------------

Non-negotiable session outputs:
  - At minimum: a COMMS.md append and a build-log entry
  - For build sessions: a full session report
  - For architectural decisions: a decision log entry
  - Always: a git push

If a session ends without these, the next agent starts blind. This is the
equivalent of a surgeon walking out mid-operation without a handoff note.

--------------------------------------------------------------------------------
4.2 BUILD LOG ENTRY FORMAT
--------------------------------------------------------------------------------

  ## YYYY-MM-DD — <Session Title>
  **Agent:** <AgentName>
  **Status:** Complete / Partial / Blocked

  ### Built
  - <component or file>
  - <component or file>

  ### Changed
  - <what changed and why>

  ### Known Issues
  - <any open bugs or blockers>

  ### Next
  - <what the next session should pick up>

--------------------------------------------------------------------------------
4.3 SESSION REPORT FORMAT
--------------------------------------------------------------------------------

  # Session Report — YYYY-MM-DD
  **Agent:** <AgentName>
  **Duration:** <approx>
  **Focus:** <one-line description>

  ## What Was Done
  <narrative summary of the session>

  ## Files Changed
  | File | Change |
  |---|---|
  | path/to/file.py | description |

  ## Decisions Made
  <any architectural or behavioral decisions and rationale>

  ## Bugs Found / Fixed
  <list any bugs encountered>

  ## Open Items
  <what is unfinished or needs follow-up>

  ## Next Session
  <clear handoff — what the next agent should do first>

================================================================================
5. HARD RULES
================================================================================

These rules are non-negotiable and apply to all agents:

  1. No autonomous print starts.
     `confirm N` is always required. Hard gated at gateway level.

  2. No autonomous model orientation changes.
     Agents cannot rotate, mirror, or reposition models without explicit
     owner instruction.

  3. `deny N` is blocked while printing.
     A print in progress cannot be denied. Use `force-cancel` with PIN.

  4. `djinn-force-cancel` requires owner PIN.
     No agent — including Claude — can bypass this.

  5. Customer PII never in Discord channels.
     All address and contact collection happens in encrypted DM flow only.

  6. Never ship code without documentation.
     Every new component gets a build log entry at minimum.

  7. Never break the COMMS thread.
     Append-only. Never delete. Always push.

  8. Escalate when uncertain.
     If an agent is unsure about an architectural decision, stop and flag
     it in COMMS.md for Claude or the owner to resolve.

================================================================================
6. AGENT ONBOARDING CHECKLIST
================================================================================

When a new session begins, any agent should:

  [ ] Read COMMS.md (last 5–10 entries minimum)
  [ ] Read the latest session report in djinn/logs/reports/
  [ ] Check bugs.md for open issues
  [ ] Check SYSTEM-STATE.md for current deployment status
  [ ] Confirm what the previous agent said to pick up next
  [ ] Confirm all required configs exist before building
      (API keys, shop.json, easypost.env, etc.)

================================================================================
7. AGENT CAPABILITY MATRIX
================================================================================

  ┌────────────────────────────┬────────┬─────────┬────────┬────────┐
  │ Capability                   │ Claude │ Salomon │ Typhon │ Marcus │
  ├────────────────────────────┼────────┼─────────┼────────┼────────┤
  │ Architecture design          │  ✓✓✓   │   ✓     │   ✓    │   ✓✓   │
  │ Code generation              │  ✓✓✓   │   ✓✓    │   ✓✓   │   ✓     │
  │ Live web research            │         │         │        │  ✓✓✓   │
  │ Market pricing research      │         │         │        │  ✓✓✓   │
  │ Discord/Telegram gateway     │         │  ✓✓✓    │        │        │
  │ Print execution ops          │         │  ✓✓✓    │        │        │
  │ Session reports              │  ✓✓✓   │   ✓     │        │   ✓✓   │
  │ Operator manuals             │  ✓✓     │         │        │  ✓✓✓   │
  │ Media pipeline ops           │   ✓     │   ✓     │  ✓✓✓  │        │
  │ Cloud sync / backup          │         │         │  ✓✓✓  │        │
  │ Code audits                  │  ✓✓✓   │         │        │  ✓✓✓   │
  └────────────────────────────┴────────┴─────────┴────────┴────────┘

================================================================================
*— Marcus, 2026-06-09*
================================================================================

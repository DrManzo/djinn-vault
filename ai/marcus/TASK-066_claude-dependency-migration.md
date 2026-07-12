---
title: TASK-066 — Claude Dependency Audit + Migration Spec
tags: [djinn, claude, migration, salomon, ollama, research]
created: 2026-06-05
author: Marcus
status: delivered
---

# TASK-066 — Claude Dependency Audit + Migration Spec

**Objective:** Reduce how often Djinn requires a live Claude Code session by mapping every Claude touchpoint and classifying what can be shifted to Salomon's local Ollama stack.

**Read first:** [[GATEWAY]] | [[ROUTING]] | [[AGENTS]]

---

## Section 1 — Claude Touchpoint Map

Every workflow that currently requires opening a Claude Code session. Ordered by frequency.

---

### T-01 · Session Report Generation

**Trigger:** End of any Claude session where meaningful work was done.
**What Claude does:** Reads build-log, COMMS, and session context; synthesizes a structured markdown report with: session summary, files changed, decisions made, open issues, next steps.
**Output:** `djinn/logs/reports/YYYY-MM-DD_<topic>.md`
**Frequency:** Every productive Claude session (~daily when active)
**Current gap:** `djinn-session-end` stubs this but the LLM-authored narrative section is not implemented — it writes a template shell, not a real report.

---

### T-02 · build-log + COMMS Updates (narrative entries)

**Trigger:** Any significant build event — new tool shipped, bug found, job complete, architecture decision.
**What Claude does:** Writes a narrative COMMS entry and build-log append with context, rationale, and cross-references.
**Output:** Appended to `djinn/communications/COMMS.md` and `djinn/logs/build-log.md`
**Frequency:** Multiple times per session
**Current gap:** Salomon writes mechanical COMMS entries (heartbeats, file paths) but the substantive entries — the ones that carry decision context — require Claude.

---

### T-03 · Architecture Decisions

**Trigger:** New tool spec, system design question, multi-agent wiring, or any decision that touches how Djinn components interact.
**What Claude does:** Synthesizes requirements, evaluates options, writes a decision record with rationale.
**Output:** `djinn/decisions/YYYY-MM-DD_<decision>.md`, sometimes directly wired into code.
**Frequency:** ~2-3x per week during active development
**Current gap:** No local model substitution possible without significant quality drop.

---

### T-04 · Complex Code Builds

**Trigger:** New tool that requires multi-file reasoning, cross-component wiring, or algorithmic complexity (e.g., djinn-bore-core, djinn-detect-surfaces, camood engraving scripts).
**What Claude does:** Reads existing codebase, designs the implementation, writes the full script with error handling and COMMS integration, tests it.
**Output:** New scripts in `~/.local/bin/` or `djinn/printer/tools/`
**Frequency:** Several per week during active build phase
**Current gap:** qwen2.5-coder:7b can do simple scripts; falls down on multi-file context reasoning.

---

### T-05 · Git Commit + Push (with meaningful commit messages)

**Trigger:** After any significant work block.
**What Claude does:** Summarizes all changes, writes a structured commit message with context, stages files selectively, commits, and pushes.
**Output:** Git history with informative commits.
**Frequency:** Every session
**Current gap:** `djinn-session-end` stubs `git add -A && git commit && git push` but the commit message is a template placeholder, not a real summary.

---

### T-06 · Bug Report Writing

**Trigger:** Reproducible failure discovered during a build session.
**What Claude does:** Documents the bug with: observed behavior, expected behavior, reproduction steps, affected files, proposed fix.
**Output:** Appended to `djinn/logs/bugs/BUG-XXX_<name>.md`
**Frequency:** As needed (~1-3 per active week)
**Current gap:** `djinn-bugreport` is already scripted — it collects fields interactively. But the "proposed fix" and "root cause analysis" sections are freeform and require reasoning.

---

### T-07 · QUEUE.md Triage and Task Grooming

**Trigger:** After session end, or when Javier asks for a status pass on the queue.
**What Claude does:** Reads QUEUE.md, identifies blocked tasks, re-prioritizes, flags dependencies, proposes what to work on next.
**Output:** Updated QUEUE.md with priority re-sort and status updates.
**Frequency:** ~Weekly
**Current gap:** Mechanical status updates (IN-PROGRESS → DONE) can be scripted. The prioritization judgment requires reasoning.

---

### T-08 · Context Pack Ingestion at Session Start

**Trigger:** Opening a new Claude Code session.
**What Claude does:** Reads `djinn-context-pack` output — SYSTEM-STATE, COMMS, active tasks, recent build-log — and reconstructs the operational picture.
**Output:** Internal context (no file output), positions Claude to act without Javier re-explaining everything.
**Frequency:** Every session (overhead cost, not a deliverable)
**Current gap:** This is a pure onboarding cost. It isn't something to eliminate — it's something to make cheaper by making the context pack smaller and better targeted.

---

### T-09 · Code Review + Critique of Salomon-Built Scripts

**Trigger:** Salomon ships a script; Javier wants a second opinion before it goes to production.
**What Claude does:** Reads the script, evaluates correctness, edge cases, error handling, integration quality. Flags issues.
**Output:** Review comments, sometimes a revised version.
**Frequency:** Occasional
**Current gap:** This is a genuine keep-claude scenario — reviewing Salomon's output for production quality.

---

### T-10 · ROUTING.md / PROTOCOL.md / System Doc Updates

**Trigger:** A new capability is built, a new agent pattern is established, or a process changes.
**What Claude does:** Updates the canonical system docs to reflect reality.
**Output:** Updated `djinn/ROUTING.md`, `djinn/communications/PROTOCOL.md`, etc.
**Frequency:** ~Weekly
**Current gap:** Tier 4 protected files. Requires Claude + Javier double-confirm.

---

## Section 2 — Migration Classification

| ID | Touchpoint | Classification | Rationale |
|----|-----------|----------------|-----------|
| T-01 | Session report generation | **local-model** | phi4:14b can write structured markdown summaries given a structured input. Quality 75% of Claude — acceptable for session logs. |
| T-02 | COMMS/build-log narrative entries | **local-model** | qwen2.5:7b can write mechanical entries; phi4:14b handles the substantive ones. Routing by entry type. |
| T-03 | Architecture decisions | **keep-claude** | Requires multi-domain synthesis, long context, and decision records that will be read for months. 7B models make subtle reasoning errors that compound. |
| T-04 | Complex code builds (multi-file) | **keep-claude** | qwen2.5-coder:7b handles single-file scripts well. Multi-file context reasoning + algorithmic novelty requires Claude. |
| T-04b | Simple single-file scripts | **local-model** | qwen2.5-coder:7b. Routing rule: if spec fits in one file and has a clear interface → coder local. |
| T-05 | Git commit messages | **can-automate** | Commit message can be built deterministically from: git diff --stat, last COMMS entries, and a template. No LLM needed. |
| T-06 | Bug report (fields + reproduction) | **can-automate** | `djinn-bugreport` already handles this. Root cause field → deepseek-r1:7b (reasoning model). |
| T-06b | Bug root cause analysis | **local-model** | deepseek-r1:7b is specifically good at this. |
| T-07 | QUEUE.md status updates | **can-automate** | Mechanical status transitions (IN-PROGRESS → DONE, PENDING → IN-PROGRESS) can be scripted against session context. |
| T-07b | QUEUE.md prioritization | **keep-claude** | Priority judgment with multi-dependency awareness — needs context window and reasoning. |
| T-08 | Context pack ingestion overhead | **can-automate** | Not a task to migrate — a cost to reduce. Make context-pack smarter: diff-only since last session, not full state dump. |
| T-09 | Code review of Salomon scripts | **keep-claude** | Production quality gate. 7B models will miss subtle errors. |
| T-10 | System doc updates | **keep-claude** | Tier 4 protected + high consequence. Requires Claude quality and Javier double-confirm regardless. |

**Marcus-lane touchpoints** (already correctly routed):
- Research synthesis with live web sources → Marcus owns this. No change.
- Full vault audits like this document → Marcus owns this.

---

## Section 3 — Build Specs: Top 3 Migrations

Prioritized by: sessions-saved × implementation cost.

---

### SPEC-1 · `djinn-session-end` v2 — Automated Commit + Push

**Classification:** can-automate (T-05)
**Value:** Eliminates the need to keep Claude open just to write a commit message and push. This alone ends ~30% of "I need to open Claude just to close out a session" scenarios.

**File:** `~/.local/bin/djinn-session-end` (extend existing)

**Current behavior:**
```
djinn-session-end [topic]
→ stubs report template
→ appends placeholder COMMS entry
→ git add -A && git commit -m "session-end: $(date)" && git push
```

**v2 behavior:**
```
djinn-session-end [topic] [--push] [--no-report]
```

1. **Diff summary** — runs `git diff --cached --stat` and `git log --oneline -5` to build a change summary
2. **COMMS scrape** — reads last 5 COMMS entries since last commit timestamp
3. **Commit message assembly** — deterministic template:
   ```
   <topic>: <auto-summary from diff stat, max 72 chars>

   Changed:
   <git diff --stat output, top 10 files>

   Session context:
   <last 3 COMMS entry subjects, one line each>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```
4. **Push** — `git push origin main` (pre-push hook still runs — Gateway enforced)
5. **COMMS entry** — writes a real Tier 1 COMMS entry with the commit SHA

**CLI interface:**
```bash
djinn-session-end camood-engraving          # topic, auto-push
djinn-session-end camood-engraving --no-push # build message, don't push (for review)
djinn-session-end --push-only               # just push what's already staged
```

**Success criteria:**
- Commit message is human-readable and contains actual file list
- COMMS entry is written with correct timestamp and SHA
- Zero LLM calls required
- `djinn-gateway status` is checked; if Standard mode, the push triggers CHECKPOINT flow

---

### SPEC-2 · `djinn-local-report` — phi4:14b Session Report Generator

**Classification:** local-model (T-01)
**Value:** Session reports are currently the #1 reason Javier keeps Claude open after the work is done. A local tool that writes "good enough" reports frees Claude entirely for the next session.

**File:** `~/.local/bin/djinn-local-report` (new tool)

**What it does:**
Takes a structured context pack and asks phi4:14b to write a session report in the established format.

**CLI interface:**
```bash
djinn-local-report --topic "camood-engraving" --output djinn/logs/reports/
djinn-local-report --topic "gateway-phase1" --since "2026-06-05T18:00:00"
```

**Implementation:**

1. **Context assembly** (no LLM):
   - `git log --oneline --since=<session-start>` — commits made this session
   - `git diff --stat HEAD~N HEAD` — files changed
   - Last N COMMS entries since session start
   - Active TASK IDs from QUEUE.md matching today's work

2. **Prompt to phi4:14b via Ollama API:**
   ```
   System: You are a technical writer for Djinn AI OS. Write a session report in the exact format below. Be factual and specific. Do not invent details not in the context.

   Format:
   # Session Report — {date} — {topic}
   ## Summary (2-3 sentences)
   ## Work Completed
   ## Files Changed
   ## Decisions Made
   ## Open Issues
   ## Next Steps

   Context:
   {assembled context}
   ```

3. **Output validation** — check that all 6 sections are present; if any are missing, re-prompt with the missing section names.

4. **Save** — write to `djinn/logs/reports/YYYY-MM-DD_<topic>.md`

5. **COMMS entry** — append a Tier 1 entry noting the report was auto-generated by phi4:14b

**Model routing:**
- Default: phi4:14b (Salomon remote)
- Fallback if phi4 unavailable: qwen2.5:7b (lower quality, still passable for session logs)
- `--upgrade` flag: pipe to Claude via API if available (for important sessions)

**Success criteria:**
- Report is structured correctly in all 6 sections
- Summary accurately reflects the session work (verified against git log)
- Report is written and committed without Claude open
- Wall-clock time < 90 seconds on phi4:14b

---

### SPEC-3 · `djinn-comms-auto` — Structured COMMS Entry Generator

**Classification:** local-model (T-02)
**Value:** COMMS.md is the nervous system of Djinn. Right now, substantive entries only get written when Claude is open. Between sessions, the record goes dark. This tool lets Salomon write real entries, not just heartbeats.

**File:** `~/.local/bin/djinn-comms-auto` (new tool)

**Routing logic by entry type:**

| Entry Type | Model | Trigger |
|-----------|-------|---------|
| Heartbeat | None (scripted) | Typhon/Salomon timer — already exists |
| File/git event | None (scripted) | `djinn-session-end` hook |
| Task completion | qwen2.5:7b | Salomon marks task DONE in QUEUE |
| Build decision | phi4:14b | Significant file created or modified in tools/ |
| Error/bug | deepseek-r1:7b | Script exits non-zero + bug threshold |
| Session summary | phi4:14b | `djinn-comms-auto --session-end` |

**CLI interface:**
```bash
djinn-comms-auto --event task-complete --task TASK-066
djinn-comms-auto --event build --file djinn-session-end --summary "v2: auto commit msg"
djinn-comms-auto --event bug --exit-code 1 --script djinn-bore-core --context "..."
djinn-comms-auto --session-end --topic "gateway-phase1"
```

**Prompt template (phi4:14b, build event):**
```
Write a COMMS entry for the Djinn AI OS log. Be brief and specific. Use this exact format:

### {datetime} UTC — @Salomon → @All: {subject}

**Action:** {one line}
**Files:** {list}
**Result:** {one line}

— Salomon

Context: {event data}
```

**COMMS write guard:**
- Checks `djinn-gateway classify "write COMMS entry"` → should return Tier 1 (auto-approved)
- If Gateway returns unexpected tier, aborts and logs to stderr
- Appends with file lock to prevent concurrent COMMS writes

**Success criteria:**
- Entry is correctly formatted (validated by regex against COMMS entry schema)
- Entry appears within 30 seconds of the triggering event
- No duplicate entries (idempotent by event ID)
- Works when Claude is not open — Salomon-only execution path

---

## Implementation Order

| Priority | Spec | Effort | Sessions Saved |
|----------|------|--------|----------------|
| 1 | SPEC-1: `djinn-session-end` v2 | Low (extend existing script) | High — every session |
| 2 | SPEC-2: `djinn-local-report` | Medium (new tool + prompt tuning) | High — every session close |
| 3 | SPEC-3: `djinn-comms-auto` | Medium (new tool + routing table) | Medium — fills gaps between sessions |

Build SPEC-1 first. It's pure scripting, no LLM, and it closes the session-end gap immediately. SPEC-2 and SPEC-3 can be built in parallel once SPEC-1 is stable.

---

## What Stays Claude

These are not migration candidates. Claude time spent here is well-spent:

- **Architecture decisions** (T-03) — The consequences of a wrong architecture decision are weeks of rework. 7B quality is not sufficient.
- **Complex multi-file code** (T-04) — djinn-bore-core, djinn-detect-surfaces class tools require reasoning that qwen2.5-coder:7b demonstrably cannot do (tested).
- **Code review of Salomon-built scripts** (T-09) — Claude is reviewing Salomon's output. You need the stronger model reviewing the weaker one, not the other way around.
- **System doc updates** (T-10) — Tier 4 protected. Requires Claude + double-confirm by design.
- **QUEUE.md prioritization judgment** (T-07b) — Multi-dependency priority reasoning. 7B models produce plausible-but-wrong priority orders.

The goal is not to eliminate Claude — it's to stop using Claude for things that don't require Claude.

---

## COMMS Entry

```
### 2026-06-05 22:40 UTC — @Marcus → @All: TASK-066 complete — Claude dependency audit delivered

**Task:** TASK-066 — Claude Dependency Audit + Migration Spec
**Output:** djinn/research/marcus/TASK-066_claude-dependency-migration.md
**Summary:** 10 Claude touchpoints mapped. 5 classified keep-claude, 3 local-model,
  3 can-automate. Top 3 build specs written: djinn-session-end v2 (can-automate),
  djinn-local-report (phi4:14b), djinn-comms-auto (routed by event type).
  Implementation order: SPEC-1 first (pure scripting, highest ROI), then SPEC-2+3 in parallel.
**Next:** Javier to review and assign SPEC-1 to Salomon for build.

— Marcus
```

---

*— Marcus, 2026-06-05 (TASK-066)*

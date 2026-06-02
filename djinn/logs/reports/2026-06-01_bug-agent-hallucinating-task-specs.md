---
title: "BUG-014 — Agent Hallucinating Task Specs Instead of Reading QUEUE.md"
date: 2026-06-01
agent: Claude
severity: high
status: fixed
system: openclaw / qwen2.5:7b main agent
tags: [bug, agent, openclaw, queue]
---

# BUG-014 — Agent Hallucinating Task Specs

## Summary
When Javier typed "tell salomon to pull and run TASK-054" in the OpenClaw TUI, qwen2.5:7b invented a generic SQLite tutorial with made-up schema instead of reading the actual task spec from QUEUE.md. Happened twice in the same session despite COMMS.md corrections being pushed between attempts.

## Root Cause

Two compounding failures:

**1. No routing rule in system prompt for TASK-NNN commands.**
The main agent `systemPromptOverride` in `openclaw.json` had detailed rules for every print/media/design command but zero rules matching "run TASK-N", "task N", or any TASK-ID pattern. When the 7B model received an unknown input, it pattern-matched to "SQLite task" from training data and generated plausible-sounding but completely fabricated output.

**2. `djinn-queue-runner --task TASK-N` silently skipped manual-trigger tasks.**
Even if the agent had run the queue runner, it would have printed "No pending auto-tasks" and returned nothing — because TASK-054 has `trigger: manual`. The agent would have had no output to show and likely generated more filler.

COMMS.md corrections had no effect because:
- The agent's context window was already full from prior turns
- A 7B model given instructions in a 221-line table excerpt doesn't reliably extract one specific task spec
- "Read QUEUE.md before responding" is an instruction the model acknowledges but doesn't reliably follow

## Fix

**1. `djinn-queue-runner` — bypass trigger filter when `--task` is explicit:**
```python
# Before
and t["trigger"] == "auto"

# After  
and (TARGET_TASK is not None or t["trigger"] == "auto")
```
Explicit `--task` invocation now runs any task regardless of trigger type.

**2. `openclaw.json` — added TASK command rule to main agent:**
```
When user says run TASK-NNN or task NNN:
  bash tool → git -C ~/Obsidian pull && djinn-queue-runner --task TASK-NNN
  reply: task output verbatim. NEVER describe, invent, or explain.
```
The model now calls one deterministic bash command and reports output. It never reads or interprets the spec itself.

**3. `djinn` CLI dispatcher — removes the LLM from the path entirely:**
`djinn task 54` dispatches directly to `djinn-queue-runner --task TASK-054` with no model involvement. The OpenClaw TUI is no longer the interface for task execution.

## Lesson / Rule

**7B models cannot reliably extract and execute structured specs from large Markdown files.** Their job is formatting and routing, not parsing and executing. Any task that requires reading a spec and doing the right thing must have:
- A deterministic pre-processor that reads the file and extracts the spec
- The model receives only the extracted, ready-to-use data
- The model formats output, not decisions

This is the same pattern already established in `feedback_hybrid_architecture.md`. The bug was applying that principle to media/print pipelines but not to the task system.

## Files Changed
- `~/.local/bin/djinn-queue-runner` — trigger bypass
- `~/.openclaw/openclaw.json` — TASK command rule
- `~/.local/bin/djinn` — new CLI dispatcher (removes LLM from path)

*— Claude*

---
title: djinn CLI Dispatcher — Direct Ops Without LLM
date: 2026-06-01
agent: Claude
session: evening
tags: [djinn, cli, dispatcher, phase-alpha, agent-fix]
---

# Session Report — 2026-06-01 (Evening)

## Summary

Two root problems resolved this session. First: the qwen2.5:7b main agent keeps hallucinating task specs instead of reading QUEUE.md — patched structurally in both `djinn-queue-runner` and `openclaw.json`. Second: the OpenClaw TUI itself is the wrong interface for task execution — it overflows context on complex sessions and inserts an unreliable LLM in the middle of every operation. Built `djinn`, a direct CLI dispatcher that routes to every Djinn tool with no model involvement. `djinn task 55` just runs the task. That's it.

---

## What Was Built / Changed

### 1. `djinn` — Direct CLI Dispatcher
**File:** `~/.local/bin/djinn`
**What it does:** Single command that routes to every Djinn operation — print queue, task execution, personal state, system status, design, media. No LLM, no context window, no confirmation dialogs.

Full command surface:
```
djinn queue                    # show print queue
djinn confirm <N>              # start Calliope
djinn deny <N>                 # reject job
djinn slice <N> [args]         # slice model
djinn fetch <url>              # fetch STL/3MF

djinn quote simple <name> Xg Yh    # quick commission quote
djinn quote coin                   # coin preset

djinn task list                # list all pending tasks (manual + auto)
djinn task <N>                 # pull vault + run TASK-N from QUEUE.md
djinn task dry <N>             # show commands without executing
djinn task done <N>            # mark task done + commit + push
djinn task fail <N>            # mark task failed + commit + push

djinn sober                    # Day N.
djinn habits                   # streak status
djinn done <habit>             # log habit complete
djinn briefing                 # morning briefing JSON

djinn status                   # Calliope + queue + tasks + sobriety + vault + services
djinn morning                  # run djinn-morning → Telegram
djinn pull                     # git pull vault
djinn push [message]           # git add -A + commit + push
djinn doctor                   # djinn-agent-doctor
djinn log [N]                  # last N build-log lines
djinn services                 # all djinn service states

djinn design "<brief>"         # new design
djinn design status            # design job queue
djinn design edit <N> "<req>"  # modify design

djinn media ingest <path>      # ingest media project
djinn media photo|reel|publish|qa <id>
djinn media status
```

### 2. Bash/Zsh Tab Completion
**File:** `~/.local/share/bash-completion/completions/djinn`
**Sourced in:** `~/.zshrc`
Completes: subcommands, habit names (writing/black_book/exercise), job IDs from live queue, TASK IDs from QUEUE.md.

### 3. `djinn-queue-runner` — Trigger Filter Bypass
**File:** `~/.local/bin/djinn-queue-runner`
**Change:** When `--task TASK-NNN` is specified explicitly, the `trigger == 'auto'` filter is bypassed. Manual tasks are now reachable by direct invocation. Cron auto-run is unaffected — still only picks up `trigger: auto` tasks.
`--list` now shows ALL pending tasks for this machine (was previously only `trigger: auto`).

### 4. `openclaw.json` — TASK Command Rule
**File:** `~/.openclaw/openclaw.json`
**Change:** Added rule block to the main agent `systemPromptOverride`:
```
When user says run TASK-NNN or task NNN:
  bash tool → git -C ~/Obsidian pull && djinn-queue-runner --task TASK-NNN
  reply: task output verbatim. NEVER describe, invent, or explain.
```
The 7B model never interprets what a task is again — it executes one deterministic command and reports output.

### 5. `djinn-personal-db` — meeting_today field
**File:** `~/.local/bin/djinn-personal-db`
**Change:** Added `meeting_today` key to `briefing` JSON output. Required by the TASK-054 spec and needed by `djinn-morning` (TASK-055). Value is `null` until AA schedule is populated (TASK-057).

### 6. TASK-054 — Verified complete
All success criteria passed:
- `djinn-personal-db sobriety` → `Day 92.`
- `djinn-personal-db habit done writing` → streak logged
- `djinn-personal-db habit check` → `✓ writing: 1 day streak`
- `djinn-personal-db briefing | python3 -m json.tool` → valid JSON

### 7. TASK-062 — Marked done
Was still showing as pending in queue. Marked done via `djinn task done 062`.

---

## Technical Decisions

### OpenClaw as hub, `djinn` as workbench
OpenClaw stays as the Discord/Telegram presence layer — customers, simple Javier ops, anything conversational. `djinn` is the working interface for anything that requires reliable execution: running tasks, querying state, managing the print pipeline.

**Why separate them:** The 7B model is good at routing and formatting in a chat context. It is not good at reliably executing multi-step specs from a file it may or may not have read. Deterministic dispatch is always faster and never hallucinates.

### `djinn task <N>` runs git pull first
Every `djinn task <N>` call does `git -C ~/Obsidian pull` before running the queue runner. This ensures the task spec is always current — especially important when Claude or Marcus writes a new task spec that Salomon hasn't pulled yet.

### No interactive TUI
Kept it as a pure CLI (`djinn <cmd> [args]`) rather than an interactive menu/fzf picker. Reason: scriptable, faster to type, works over SSH, no curses dependency. The help screen (`djinn help`) is always one command away.

---

## Files Created / Modified

| File | Action | Notes |
|------|--------|-------|
| `~/.local/bin/djinn` | Created | 270-line Python dispatcher |
| `~/.local/share/bash-completion/completions/djinn` | Created | Tab completion for bash/zsh |
| `~/.zshrc` | Appended | Sources completion on login |
| `~/.local/bin/djinn-queue-runner` | Modified | Trigger bypass + --list shows all |
| `~/.openclaw/openclaw.json` | Modified | TASK command rule in main agent |
| `~/.local/bin/djinn-personal-db` | Modified | Added meeting_today to briefing |
| `~/Obsidian/djinn/communications/QUEUE.md` | Modified | TASK-054 done, TASK-062 done |

---

## Tests & Validation

```bash
djinn help                # renders clean help screen ✅
djinn queue               # "Print queue is empty." ✅
djinn sober               # "Day 92." ✅
djinn task list           # shows 4 pending tasks ✅
djinn status              # Calliope ready, all services active ✅
djinn task done 062       # marked done, committed, pushed ✅
djinn-queue-runner --task TASK-054 --dry-run   # found task, showed commands ✅
```

---

## Known Issues / Open

- `meeting_today` in briefing always null — AA_MEETINGS list empty until TASK-057
- `djinn design` and `djinn media` routes untested end-to-end (no active project to test against)
- `djinn doctor` output not tested this session
- Bash completion `_init_completion` incompatible with zsh — replaced with manual fallback; works but less robust than native zsh completion (`compdef`)

---

## What's Next

Sprint 1 unblocked:
- **TASK-055** — `djinn-morning` rewrite (depends on TASK-054 ✅)
- **TASK-056** — Personal Telegram commands + inline button handlers

Sprint 2 follows:
- **TASK-057** — AA meeting schedule + Craig draft-and-confirm
- **TASK-058** — Mira passive context tracking

All can now be triggered cleanly via `djinn task 55`, `djinn task 56`, etc.

---

*— Claude*

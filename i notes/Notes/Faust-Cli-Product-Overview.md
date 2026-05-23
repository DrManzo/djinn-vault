---
subject: business/career-strategies/productivity
tags:
  - business/software/products
  - cs/cli-apps
  - cs/database-management
  - personal/productivity-tools
created: 2026-05-19
source: Perplexity export
---

# Faust CLI Product Overview

## Summary
This note provides an overview of the Faust Command Line Interface (CLI) as a product, including its architecture, key features, and marketing positioning.

## Key Points
- **Architecture**: Python-based CLI app with Click + Rich for routing.
- **Modules**: Tasks, Notes, Habits, Reminders, Timers.
- **Key Features**: Unified grammar, local-first storage, natural language reminders.
- **Marketing Positioning**: Local-first personal operating system in the terminal.

## Details
The Faust CLI is a Python-based command-line application designed to manage tasks, notes, habits, reminders, and timers. It leverages Click for routing and Rich for rich text display. The architecture is verb-first, with global verbs like `list`, `write`, `read`, `edit`, `done`, `delete`, and `run`. Each module (tasks, notes, habits, reminders, timers) has its own actions layer that interacts with a shared SQLite database.

### Architecture
- **Python CLI App**: Grounded in Click + Rich.
  - **Global Verbs**: `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
  - **Nouns (Modules)**: Tasks, Notes, Habits, Reminders, Timers.

### Modules and Boundaries
- **Tasks**:
  - Full CRUD with due dates/times.
  - Relational tags, filters, Rich tables, pipe-friendly output.
- **Notes**:
  - CRUD for free-form text.
  - Follows the same verb-first model as other modules.
- **Habits**:
  - `habits` and `habit_completions` tables.
  - Streak tracking (`current_streak`, `longest_streak`), `last_done`, completion counts (today + total).
  - Commands for listing, “today”, dormant habits, history, `done`, archive, merge.
- **Reminders**:
  - Dedicated table with `due_at` (ISO datetime), `status`, and timestamps.
  - Actions layer encapsulates CRUD + `mark_done`.
  - CLI uses strict 12-hour formats and optionally natural language via `dateparser`.
- **Timers / Run Workflows**:
  - `run` verb group for interactive workflows.
  - First workflow: `faust run pomodoro` with modes (`classic` 25/5, `long-focus` 45/15).
  - Rich progress UI; prompt-based control between phases.

### Code Qualities
- **Clear Separation**:
  - `db_*` / schema initializers per module.
  - `actions.py` per module: DB logic & domain rules.
  - `commands.py` per module: Click commands, formatting, user IO.
- **Extensibility**:
  - Adding a new resource is “add module → wire verbs in main”.
  - Adding a new workflow is “add command → mount under `run`”.
- **Local-First**: No network requirement for core flows; everything works on a single SQLite file.
- **Testability**:
  - Actions layer is pure Python with injected connections; easy to unit test.
  - Commands are thin and can be covered with Click’s testing utilities.

### Marketing Positioning
- **Product Positioning**: Local-first personal operating system in the terminal.
- **Key Differentiation**: Local, offline, no SaaS subscription. Technical-user friendly because it's "text, structured, and scriptable."
- **Headline Ideas**:
  - “A local-first personal OS for people who live in the terminal.”
  - “One CLI for tasks, notes, habits, reminders, and deep-work sessions.”
  - “Your second brain, but SQLite and Git instead of someone else’s server.”

### Feature Bullets
- **Unified Grammar**: Learn `list/write/read/edit/done/delete/run` once, reuse across modules.
- **Tasks**: Priorities, due dates/times, tag filters, pipe-friendly output.
- **Notes**: Lightweight knowledge capture, integrated with the same verbs.
- **Habits**: Streak tracking, daily completions, dormant habit detection, completion history.
- **Reminders**: 12-hour times, natural language ("tomorrow 3pm"), stored as precise ISO timestamps.
- **Focus Workflows**: `faust run pomodoro` with presets and overrides, running fully local in your terminal.
- **Local-First & Scriptable**: SQLite backend, works offline, output formats that play well with Unix tools.

### Proof Points
- Built in Python on widely used, boring-reliable tech (Click, Rich, SQLite).
- No external services required; easy to audit, fork, and extend.
- Single CLI binary (via editable install) that fits into developer workflows.

## References
- [Faust Step 12 Operator Prompt](https://github.com/DrManzo/Faust_CLI/tree/main)

## Related
- [[Faust-CLI-Project]] — architecture and features
- [[Faust-Cli-Core-Adapters]] — core components

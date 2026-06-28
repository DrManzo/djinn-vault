---
subject: technology/software/development/cli-tools
tags:
  - technology/software/development/faust/cli
  - technology/software/development/architecture/python
  - technology/software/development/modules/tasks
  - technology/software/development/modules/notes
  - technology/software/development/modules/habits
  - technology/software/development/modules/reminders
  - technology/software/development/modules/timers
created: 2026-06-28
source: Perplexity export
---

# Faust CLI Tool Overview

## Summary
Faust is a local-first personal operating system in your terminal, integrating tasks, notes, habits, reminders, and focus timers with a verb-first routing model.

## Key Points
- **Architecture**: Python CLI app using Click + Rich for a verb-first routing model.
- **Modules**:
  - **Tasks**: Full CRUD functionality, due dates/times, relational tags, filters, and pipe-friendly output.
  - **Notes**: CRUD for free-form text with the same verb-first model.
  - **Habits**: Tracks streaks, last done, and completion counts.
  - **Reminders**: Dedicated table with `due_at`, `status`, and timestamps; supports natural language via `dateparser`.
  - **Timers/Run Workflows**: Interactive workflows for Pomodoro timers.

## Details
Faust is designed as a local-first personal operating system that integrates various functionalities such as tasks, notes, habits, reminders, and focus timers. The application uses a verb-first routing model with global verbs like `list`, `write`, `read`, `edit`, `done`, `delete`, and `run`. Each module has its own actions layer for database logic and domain rules.

### Architecture
- **Python CLI App**: Grounded in Click + Rich, with a verb-first routing model.
  - **Global Verbs**: `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
  - **Nouns (Modules)**: Tasks, notes, habits, reminders, and timers (Pomodoro).
- **Centralized SQLite Access**: Uses a single connection factory in WAL mode with foreign keys enabled.
  - `db_*` / schema initializers per module for setup at startup.
  - `actions.py` per module for DB logic & domain rules.
  - `commands.py` per module for Click commands, formatting, and user IO.

### Modules
- **Tasks**: Full CRUD functionality with due dates/times, relational tags, filters, Rich tables, and pipe-friendly output.
- **Notes**: CRUD for free-form text; follows the same verb-first model.
- **Habits**:
  - Tracks `current_streak`, `longest_streak`, `last_done`, and completion counts (today + total).
  - Commands include listing, “today,” dormant habits, history, `done`, archive, merge.
- **Reminders**:
  - Dedicated table with `due_at` (ISO datetime), `status`, and timestamps.
  - Actions layer encapsulates CRUD + `mark_done`.
  - CLI uses strict 12-hour formats and optionally natural language via `dateparser`.
- **Timers/Run Workflows**:
  - `run` verb group for interactive workflows.
  - First workflow: `faust run pomodoro` with modes (`classic` 25/5, `long-focus` 45/15).
  - `--cycles`, `--focus-minutes`, `--break-minutes`.
  - Rich progress UI; prompt-based control between phases.

### Code Qualities
- **Clear Separation**: `db_*` / schema initializers per module called at startup.
- **Extensibility**: Adding a new resource is "add module → wire verbs in main."
- **Local-First**: No network requirement for core flows, works on a single SQLite file.
- **Testability**: Actions layer is pure Python with injected connections; easy to unit test. Commands are thin and can be covered with Click’s testing utilities.

## References
- [Faust CLI Tool Overview](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_92e78eae-dbdf-412d-b0d9-3b13598502fa/6101dfb2-afbe-479a-a699-dc4938a07de9/Marcus-core-Files.docx)

## Related
- [[Faust-Core-Modules]] — Detailed breakdown of Faust modules.
- [[Task-Management-Systems]] — Overview of task management tools and systems.
- [[Personal-Operating-Systems]] — Exploration of personal operating systems in the terminal.
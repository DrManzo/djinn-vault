---
subject: technology/software-development/faust/core-components
tags:
  - software-development/architecture/verb-first-routing
  - software-development/database/sqlite
  - software-development/modules/tasks-notes-habits
  - software-development/cli-tools/faust
created: 2026-06-28
source: Perplexity export

---

# Faust Core Components Overview

## Summary
This note provides an overview of the core components and architecture of the Faust CLI application, including its modules (tasks, notes, habits, reminders, timers), database structure, and code organization.

## Key Points
- **Architecture**: Uses Click + Rich for a verb-first routing model.
- **Modules**:
  - Tasks: Full CRUD with due dates/times, relational tags, filters.
  - Notes: Free-form text with same verb-first model.
  - Habits: Tracks streaks and completion counts.
  - Reminders: Has dedicated tables with `due_at`, `status`.
  - Timers/Run Workflows: Interactive workflows for Pomodoro timers.

## Details
The Faust application is structured around several core modules, each designed to handle specific tasks. The architecture is built using Python's Click and Rich libraries, implementing a verb-first routing model that ensures consistency across different commands.

### Architecture
- **Verb-First Routing Model**: Global verbs include `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
- **Centralized SQLite Access**: Uses WAL mode with foreign keys enabled and row factory set to sqlite3.Row.
- **Modules**:
  - **Tasks**: Mature implementation supporting full CRUD operations, due dates/times, relational tags, filters, Rich tables, and pipe-friendly output.
  - **Notes**: Simple CRUD for free-form text; follows the same verb-first model without completion semantics.
  - **Habits**: Tracks streaks (`current_streak`, `longest_streak`), last done date, and completion counts. Commands include listing, “today,” dormant habits, history, `done`, archive, merge.
  - **Reminders**: Dedicated table with `due_at` (ISO datetime), `status`, and timestamps; actions layer encapsulates CRUD + `mark_done`. CLI supports strict 12-hour formats and optionally natural language via `dateparser`.
  - **Timers/Run Workflows**: Interactive workflows for Pomodoro timers, including modes (`classic` 25/5, `long-focus` 45/15), cycle control, and rich progress UI.

### Code Qualities
- **Clear Separation**: Each module has its own schema initializers called at startup.
- **Extensibility**: Adding a new resource involves adding a module and wiring verbs in the main file. New workflows can be added by creating commands and mounting them under `run`.
- **Local-First**: No network requirement for core flows; everything works on a single SQLite file.
- **Testability**: Actions layer is pure Python with injected connections, making it easy to unit test. Commands are thin and can be covered using Click’s testing utilities.

## References
- [Faust Core Components Documentation](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_92e78eae-dbdf-412d-b0d9-3b13598502fa/6101dfb2-afbe-479a-a699-dc4938a07de9/Marcus-core-Files.docx)

## Related
- [[software-development/cli-tools/faust]] — Faust CLI Tool Overview
- [[tasks-management/todos-faust]] — Tasks Management in Faust
- [[habits-tracking/habits-faust]] — Habits Tracking in Faust
- [[reminders-scheduling/reminders-faust]] — Reminders Scheduling in Faust
- [[time-management/timers-faust]] — Timers and Run Workflows in Faust
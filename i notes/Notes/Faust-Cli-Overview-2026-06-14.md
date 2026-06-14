---
subject: ai/development/cli
tags:
  - cs/software
  - cs/cli
  - personal/organization
  - architecture/design
created: 2026-06-14
source: Perplexity export
---

# Faust CLI Overview

## Summary
Faust is a local-first personal operating system with a Python CLI app grounded in Click + Rich, offering modules like tasks, notes, habits, reminders, and timers. It uses a verb-first routing model and centralized SQLite access.

## Key Points
- **Architecture**
  - Uses Click + Rich for the CLI.
  - Verb-first routing model: global verbs include `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
  - Centralized SQLite connection with WAL mode, foreign_keys enabled.
  - Each module has a small actions layer that interacts with the shared connection.

- **Modules and Boundaries**
  - **Tasks**: Full CRUD support, due dates/times, relational tags, filters, Rich tables, pipe-friendly output.
  - **Notes**: CRUD for free-form text; follows verb-first model but no completion semantics.
  - **Habits**: `habits` table + `habit_completions` table. Streaks, last done, completion counts.
  - **Reminders**: Dedicated `reminders` table with due_at (ISO datetime), status, and timestamps. Actions layer for CRUD + `mark_done`.
  - **Timers / run workflows**: Interactive workflows like Pomodoro mode with modes (`classic`, `long-focus`).

- **Code Qualities**
  - Clear separation: `db_*` initializers per module called at startup.
  - Extensibility: Adding a new resource involves adding a module and wiring verbs in the main file.
  - Local-first: Core flows work offline, no network requirement for SQLite files.
  - Testability: Actions layer is pure Python with injected connections; easy to unit test.

## Details
Faust is designed as a local-first personal operating system that integrates tasks, notes, habits, reminders, and focus timers into a single CLI. The architecture is built around Click + Rich, which provides a verb-first routing model for global commands like `list`, `write`, `read`, `edit`, `done`, `delete`, and `run`. Each module has its own actions layer that interacts with a centralized SQLite database in WAL mode.

The tasks module supports full CRUD operations, including due dates/times and relational tags. Notes are managed through a simple CRUD system without completion semantics. Habits track streaks, last done, and completion counts across two tables: `habits` and `habit_completions`. Reminders use a dedicated table with ISO datetime for due times, status, and timestamps. The reminders module also includes actions for marking tasks as done.

Timers or run workflows are designed to support interactive sessions like the Pomodoro technique, which can be configured through command-line options such as `--cycles`, `--focus-minutes`, and `--break-minutes`. The CLI provides a rich progress UI with prompt-based control between phases.

## References
- [Faust Architecture Documentation](https://math.mit.edu/~djk/calculus_beginners/chapter00/section02.html)

## Related
- [[Faust-Cli-Product-Overview]] — similarity
- [[Faust-Cli-Overview-And-Architecture]] — architecture

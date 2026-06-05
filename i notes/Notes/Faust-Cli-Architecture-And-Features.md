---
subject: ai/development/faust/cli
tags:
  - ai/development/cli
  - ai/models/performance-analysis
  - ai/integration
created: 2026-06-04

# Faust CLI Architecture and Features

## Summary
This note provides an overview of the architecture, features, and key points about the Faust CLI application.

## Key Points
- **Architecture**: Built using Python with Click + Rich for a verb-first routing model.
- **Modules**:
  - Tasks: CRUD operations, due dates/times, relational tags, filters.
  - Notes: CRUD for free-form text; same verb-first model.
  - Habits: Streaks, completion counts, commands for listing and archiving.
  - Reminders: Dedicated table with `due_at` (ISO datetime), `status`, timestamps.
  - Timers/Run Workflows: Interactive workflows with modes like classic and long-focus.

## Details
The Faust CLI application is designed as a local-first personal operating system, providing tasks, notes, habits, reminders, and focus timers in a single terminal interface. The architecture is built around Click for command-line interactions and Rich for rich text output. Each module has its own actions layer that interacts with a shared SQLite database.

### Architecture
- **Global Verbs**: `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
- **Modules**:
  - **Tasks**: Full CRUD operations, due dates/times, relational tags.
  - **Notes**: CRUD for free-form text; same verb-first model.
  - **Habits**: Tracks streaks and completion counts with commands to list, archive, and merge habits.
  - **Reminders**: Dedicated table with `due_at` (ISO datetime), `status`, timestamps. Uses strict 12-hour formats and optionally natural language via `dateparser`.
  - **Timers/Run Workflows**: Interactive workflows like Pomodoro timers.

### Code Qualities
- **Separation of Concerns**: Clear separation between database logic (`db_*` initializers) and command handling.
- **Extensibility**: Adding new modules or workflows is straightforward by adding commands and mounting them under `run`.
- **Local-First**: Core flows work offline, using a single SQLite file.
- **Testability**: Actions layer is pure Python with injected connections for easy unit testing.

## References
- [Faust CLI Documentation](https://github.com/DrManzo/djinn-vault/tree/main/faust-cli)

## Related
- [[AI-Development-Faust-Core]] — Core concepts and features of the Faust CLI.
- [[Task-Management-Systems]] — Overview of task management tools and their integration.

---

This note captures the essential details about the Faust CLI application, its architecture, and key features. It is structured to be easily referenced for further development or analysis.
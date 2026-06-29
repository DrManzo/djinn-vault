---
subject: technology/software/development/cli-tools
tags:
  - technology/software/development/cli-tools/faust-architecture/faust-modules/faust-verbs
created: 2026-06-29

# Faust CLI Tool Overview

## Summary
This note provides an overview of the Faust CLI tool, detailing its architecture and key modules.

## Key Points
- **Architecture**: Built using Click + Rich for a verb-first routing model.
- **Modules**:
  - Tasks: Full CRUD with due dates/times, tags, filters.
  - Notes: Free-form text with similar verb-first model.
  - Habits: Tracks streaks and completion counts.
  - Reminders: Manages reminders with `due_at` timestamps.
  - Timers/Run Workflows: Interactive workflows for Pomodoro timers.

## Details
Faust is a local-first personal operating system designed to manage tasks, notes, habits, reminders, and focus timers from the command line. It leverages Click and Rich for its verb-first routing model, ensuring that commands are intuitive and consistent across different modules.

### Architecture
- **Python CLI App**: Grounded in Click + Rich.
- **Verb-First Routing Model**:
  - Global verbs: `list`, `write`, `read`, `edit`, `done`, `delete`, `run`.
  - Nouns (modules): tasks, notes, habits, reminders, and timers.

### Modules
1. **Tasks**
   - Full CRUD operations.
   - Due dates/times.
   - Relational tags.
   - Filters.
   - Rich tables for output.
2. **Notes**
   - Free-form text.
   - Follows the same verb-first model as other modules.
3. **Habits**
   - Tracks streaks (`current_streak`, `longest_streak`).
   - `last_done`.
   - Completion counts (today + total).
4. **Reminders**
   - Dedicated table with `due_at` timestamps, status, and timestamps.
   - Actions layer for CRUD operations and marking reminders as done.
5. **Timers/Run Workflows**
   - Interactive workflows like Pomodoro timers.
   - Modes: classic 25/5, long-focus 45/15.
   - Rich progress UI with prompt-based control.

### Code Qualities
- **Clear Separation**: `db_*` / schema initializers per module.
- **Extensibility**: Adding a new resource or workflow is straightforward.
- **Local-First**: No network requirement for core flows; works on a single SQLite file.
- **Testability**: Actions layer is pure Python with injected connections, making it easy to unit test.

## References
- [Faust CLI Documentation](https://github.com/your-repo/faust-cli)

## Related
- [[Faust-Core-Files]] — Detailed documentation and files for Faust.
- [[Task-Management-Systems]] — Overview of task management tools in the market.
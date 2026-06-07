---
subject: ai/development/faust/cli
tags:
  - cs/cli
  - cs/architecture
  - personal/productivity
  - tasks/crud
  - notes/crud
  - habits/tracking
  - reminders/table
created: 2026-06-04
source: Perplexity export
---

# Faust CLI Overview and Architecture

## Summary
Faust is a Python-based command-line application designed for personal productivity, integrating tasks, notes, habits, reminders, and timers. It uses Click and Rich libraries to provide a verb-first routing model with clear separation of concerns.

## Key Points
- **Architecture**: Built using Click + Rich, with a verb-first routing model.
- **Modules**:
  - **Tasks**: Full CRUD functionality, due dates/times, relational tags, filters, and pipe-friendly output.
  - **Notes**: CRUD for free-form text; follows the same verb-first model.
  - **Habits**: Tracks streaks, last done, and completion counts.
  - **Reminders**: Dedicated table with `due_at`, `status`, and timestamps.
  - **Timers / Run Workflows**: Interactive workflows with modes like classic Pomodoro and long-focus.

## Details
Faust is structured to be a local-first personal operating system in the terminal. It includes several modules, each with its own actions layer that interacts with a shared SQLite database:

- **Tasks**:
  - Full CRUD functionality.
  - Due dates/times.
  - Relational tags and filters.
  - Pipe-friendly output.

- **Notes**:
  - CRUD for free-form text.
  - Follows the same verb-first model as other modules.

- **Habits**:
  - Tracks streaks, last done, and completion counts.
  - Commands include listing, “today,” dormant habits, history, `done`, archive, merge.

- **Reminders**:
  - Dedicated table with `due_at` (ISO datetime), `status`, and timestamps.
  - Actions layer encapsulates CRUD + `mark_done`.
  - CLI uses strict 12-hour formats and optionally natural language via `dateparser`.

- **Timers / Run Workflows**:
  - Interactive workflows like Pomodoro mode with classic and long-focus options.
  - Modes include `--cycles`, `--focus-minutes`, `--break-minutes`.
  - Rich progress UI; prompt-based control between phases.

## References
- [Faust CLI Documentation](https://github.com/DrManzo/djinn-vault)

## Related
- [[Faust-Cli-Product-Overview]] — similarity 0.89
- [[Clarifying-Architectural-Choices-For-Faust-Cli]] — similarity 0.76

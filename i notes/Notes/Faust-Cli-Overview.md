---
subject: ai/development/cli
tags:
  - ai/development/faust/cli
  - ai/integration
created: 2026-06-04

# Faust CLI Overview

## Summary
Faust is a Python CLI application designed for personal productivity, featuring tasks, notes, habits, reminders, and timers. It operates locally with minimal dependencies.

## Key Points
- **Architecture**
  - Built using Click + Rich for a verb-first routing model.
  - Centralized SQLite database access in WAL mode.
  - Modules include: Tasks, Notes, Habits, Reminders, Timers.
- **Modules and Boundaries**
  - **Tasks**: Full CRUD with due dates/times, relational tags, filters, and pipe-friendly output.
  - **Notes**: Basic CRUD for free-form text.
  - **Habits**: Tracks streaks, last done, completion counts.
  - **Reminders**: Dedicated table with `due_at`, `status`, timestamps; natural language support via `dateparser`.
  - **Timers / Run Workflows**: Interactive workflows like Pomodoro timers.

- **Code Qualities**
  - Clear separation of concerns: `db_*` initializers, actions layer, commands.
  - Extensibility and local-first design.
  - Testability with pure Python actions layers.

## Details
Faust is a comprehensive CLI tool for personal productivity. It integrates multiple functionalities like tasks, notes, habits, reminders, and timers into one unified interface. The architecture is built around Click and Rich, providing a verb-first routing model that makes commands intuitive to use across different modules. The core of Faust relies on a single SQLite database in WAL mode, ensuring local first and offline capabilities.

The `Tasks` module offers full CRUD operations with additional features like due dates/times and relational tags. Notes are simple free-form text entries. Habits track streaks and completion counts, while reminders support natural language scheduling via `dateparser`. Timers provide interactive workflows such as Pomodoro sessions, configurable by cycles or focus minutes.

Faust's design emphasizes extensibility, allowing users to add new modules or workflows easily. The codebase is structured with clear separation of concerns, making it testable and maintainable. This local-first approach ensures that Faust operates independently without requiring a network connection, providing a robust personal operating system for technical users.

## References
- [Faust CLI Documentation](https://github.com/DrManzo/djinn-vault/tree/main/faust-cli)

## Related
- [[Djinn-Vault]] — Repository containing the Faust CLI and related documentation.
- [[Pomodoro-Timers]] — Notes on using Pomodoro timers in Faust.

---

This structured note captures the essence of Faust's architecture, key features, and design principles.
---
subject: business/career-factors/productivity
tags:
  - cs/code-quality
  - cs/python
  - business/software-development
  - personal/coding-practices
created: 2026-05-23
source: Perplexity export
---

# Faust CLI App Code Cleanup

## Summary
This note outlines the process for refactoring and cleaning up a local-first CLI app called Faust, which is written in Python using Click, Rich, and SQLite. The focus will be on code organization, consistency, and documentation without altering existing functionality.

## Key Points
- Refactor and clean up the current codebase.
- Fix duplicated imports, unused imports, and style issues.
- Ensure `from __future__ import annotations` is at the top of each file where needed.
- Maintain a consistent structure across modules like `notes`, `habits`, `reminders`, and `timers`.
- Make Click and Rich usage idiomatic and consistent.
- Add high-value docstrings to public functions and classes, especially actions and commands.
- Remove redundant or noisy comments.
- Preserve all existing CLI command names, options, and semantics.
- Ensure clear and user-friendly error handling with reasonable validation tightening.

## Details
The Faust app is a local-first CLI tool that uses a verb-first command grammar. It includes Phase 2 features such as notes, habits, reminders, and a Pomodoro timer. The existing implementation has several modules:
- **Core**: `core/db.py` for database connections and schema initialization.
- **Main**: `main.py` to manage the overall application flow.
- **Notes Module**: `modules/notes/actions.py`, `modules/notes/commands.py`.
- **Habits Module**: `modules/habits/actions.py`, `modules/habits/commands.py`.
- **Reminders Module**: `modules/reminders/actions.py`, `modules/reminders/db_reminders.py`, and `modules/reminders/commands.py`.
- **Timers Module**: `modules/timers/commands.py` for managing timers, including the Pomodoro timer.

### Focus Areas
1. **Code Cleanup**
   - Fix duplicated imports.
   - Remove unused imports.
   - Ensure consistent use of `from __future__ import annotations`.

2. **Consistency and Structure**
   - Maintain a clean and organized structure across modules.
   - Use idiomatic Click and Rich commands.

3. **Documentation**
   - Add high-value docstrings to public functions and classes.
   - Remove redundant comments, focusing on why something exists or non-obvious logic.

4. **Behavior Preservation**
   - Do not change any CLI command names, options, or semantics.
   - Ensure all existing commands work as expected: `faust list tasks`, `faust write task`, etc.

5. **Error Handling and UX**
   - Make sure errors raised by Click are clear and user-friendly.
   - Tighten validation where reasonable without changing accepted formats.

### Process
1. Upload the current files, including:
   - `core/db.py`
   - `main.py`
   - `modules/notes/actions.py`, `modules/notes/commands.py`
   - `modules/habits/actions.py`, `modules/habits/commands.py`
   - `modules/reminders/actions.py`, `modules/reminders/db_reminders.py`, and `modules/reminders/commands.py`
   - `modules/timers/commands.py`

2. For each file, propose a cleaned-up version and briefly explain the changes made.

## References
- [Faust CLI App Code Cleanup](https://www.skool.com/aianswers)

## Related
- [[Clarifying-Architectural-Choices-For-Faust-Cli]] — architectural choices
- [[Faust-Step-10-Operator-Prompt]] — related step

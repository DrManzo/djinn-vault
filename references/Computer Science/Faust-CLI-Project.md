---
id: 20260519-182746-182751
created: 2026-05-19
type: permanent
title: Faust CLI Project
references:
  - [[Perplexity Chat Export 2026-05-19_18-27-46]]
  - [[Perplexity Chat Export 2026-05-19_18-27-48]]
  - [[Perplexity Chat Export 2026-05-19_18-27-51]]
links:
  - [[Meance LLC Branding]]
  - [[Python Scripting for iOS]]
tags: [programming, cli, python, productivity, personal-tools]
---

## Summary
Development of Faust, a local-first CLI productivity tool designed as a personal "second brain" for Javier. Covers architecture decisions, feature set, data model, and implementation roadmap. Emphasizes privacy, offline functionality, and extensibility through plugins.

## Key Points
- Local-first architecture: SQLite database, no cloud dependency, encrypted backups optional
- Core features: note-taking, task management, contact CRM, journaling, and project tracking
- Built with Python using Click/Typer for CLI, Rich for TUI, SQLite for storage
- Plugin system allows custom commands, data exporters, and integrations
- Privacy-focused: all data stays on device, no telemetry, open-source
- Designed for single-user workflow but supports multi-device sync via git or manual backup
- Naming: "Faust" reflects the bargain of trading convenience for control (local-first vs. cloud)

## Details

### Architecture
```
faust/
├── cli/          # Click/Typer command definitions
├── core/         # Business logic, data models
├── storage/      # SQLite operations, migrations
├── plugins/      # Plugin system, hook registry
├── utils/        # Helpers, formatters, validators
└── tests/        # Unit and integration tests
```

### Data Model
Notes: id, title, body, tags, created, modified, linked_ids
Tasks: id, title, status, priority, due, project_id, tags
Contacts: id, name, email, phone, notes, last_contact, tags
Projects: id, name, description, status, start_date, end_date
Journals: id, date, entry, mood, tags

### CLI Commands
```bash
faust note add/edit/list/search
faust task add/complete/list/overdue
faust contact add/search/log
faust project create/list/status
faust journal write/read
faust search --query "..."
faust export --format markdown/json
faust backup/create/restore
```

### Plugin System
Plugins register hooks for: pre/post command execution, custom formatters, data exporters, external integrations. Stored in `~/.faust/plugins/`. Discovered automatically on startup. Can be installed via git clone or pip.

### Roadmap
Phase 1: Core CLI (notes, tasks, search)
Phase 2: TUI with Rich (interactive browsing, editing)
Phase 3: Plugin system + community plugins
Phase 4: Sync via git remote or encrypted cloud backup
Phase 5: Mobile companion (iOS via iSH/Shortcuts)

## References
- Click Documentation: click.palletsprojects.com
- Typer Documentation: typer.tiangolo.com
- Rich Documentation: rich.readthedocs.io
- SQLite Documentation: sqlite.org/docs.html

## Related
- [[Meance LLC Branding]] — ASCII signature for Faust output
- [[Python Scripting for iOS]] — Mobile workflow integration
- [[California Tax Service Notary Business]] — Potential business use case
- [[Faust-Project-Setup-Architecture]]
- [[Faust-Long-Term-Memory-Foundation]]
- [[Meanas-and-M-Systems-Business-Vision]]
- [[Python-Scripting-iOS-iSH-Shortcuts]]

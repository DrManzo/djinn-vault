---
tags:
  - ai/development/faust/cli
  - cs/software-engineering
  - business/infrastructure/equipment
---

---
subject: Faust/Development
tags:
  - ai/development/faust/cli
  - business/infrastructure/equipment
  - cs/software-engineering
created: 2026-05-23
source: Perplexity export

# Faust CLI Development Update

## Summary
The team is continuing work on the Faust project, a local-first personal operating system built in Python. Phase 1 focuses on the tasks module and its implementation details, while Phase 2 planning has begun for additional modules like notes, habits, and reminders/timers.

## Key Points
- **Faust Overview**: Javier’s local-first personal OS built with Python.
- **CLI Grammar**: `faust <verb> <noun> [id] [options]`.
- **Current Modules**: Tasks (CRUD operations, due dates, due times).
- **Phase 1 Completion**: Effective completion of the tasks module.
- **Locked Architectural Decisions**:
  - Project name: `faust`.
  - CLI is verb-first.
  - `main.py` as a global verb dispatcher.
  - SQLite database with WAL mode and foreign keys enabled.
  - Tags use a relational junction table (`task_tags`).
  - Heavily commented code.

## Details
The Faust project aims to provide a flexible, local-first personal operating system. The current focus is on the `tasks` module, which includes full CRUD operations via global verbs such as `list`, `write`, `read`, `edit`, `done`, and `delete`. The tasks module also supports due dates and times with today-default logic.

### Phase 1 Implementation
- **CRUD Operations**: Full Create, Read, Update, Delete (CRUD) functionality.
- **Due Dates/Times**: Tasks can now have due dates and times. If a due time is provided without a date, the date defaults to today.
- **CLI Output**: Today's date is displayed as `Today`.
- **Tag Filtering**: Relational tag filtering with repeatable `--tag` using AND logic.

### Phase 2 Planning
- **Modules to Build**:
  - Notes
  - Habits
  - Reminders/Timers

- **Build Order**:
  - **Notes**: First because it fits the existing global verbs and reuses the tasks reference pattern.
  - **Habits**: Second due to potential need for completion behavior.
  - **Reminders/Timers**: Third, extending simple CRUD before adding recurring-state logic.

## References
- [CONTRIBUTING-2.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/10746152/2ce5e9df-eadd-453c-b024-053bada9a5a5/CONTRIBUTING-2.md?AWSAccessKeyId=ASIA2F3EMEYE2V6RTIML&Signature=Y3swwy5z2jO1RHoWWJNAPZGbRPM%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEBoaCXVzLWVhc3QtMSJGMEQCIF2J%2B51LRPL%2FOIqB38XVyQVcBA%2BRbduaa6vR6VUszcIhAiB0fj2lK4BrtIG8bMb1XYp6MZyCpufT6zOSkvhpBwAFaCr8BAji%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDY5OTc1MzMwOTcwNSIMxo1e%2F5eZh7ywTS7zKtAEJwrViaQ%2FnKtLuuNoadqidy21Rb91St2wsmASLimlpa2J%2Fk8y9gwzXNEaW0bOvI0FESclDY1KeByiK0MHkfS6WJHmCemEn8XEQigyT8Uw%2Fh519GWql3qrGgLvsYGvgM0dJbi6yaLb5c1h36Kgt6FBCVJrrroe247HVOi%2BQ3afX8%2FpafGq1mEh6D%2BDyaCaLko6hbOVUpnW2oBCk9E0OKfmIb4m1GdkPp9LNK1F5kCWqFPJhClzaoklK0kNc2WwiDoaa4DCuTICM6gTdScjJZF3%2FpQYIgyuoL0ov1S3jtbtkPMUTkaND1ieHfFFY4jhpzVCJXsJYQnkBDeLDS79O6OKF3wwlIN6bxg5yIEPbPdNoFIZLyrKMR03R7AZHMqsZNg8j9NNhwlo0PtRr3VFczZS5ucHWpKG03%2F7eywx9CR1AK%2Bo3pa%2F1jkQJWSHJjcIL9FfTM2dMDL9W1706KbhiOpRb1Oq4o8j34rt5BMgm6zqM0ytLOuMx6Pai6KPV5VQ4kHEkxQUOs%2F1VBmDfzRiCxMo5cxMkb7U6v7Ug6ERPKxiuH0UQBPQ6YR7II0fClAUCLT5408GnWRy5yZFHFyc2fPloPNOhtFrFPsWtWNG98DHIMtFBI3KcGia9OujlphgUGV%2FEQPcqpJsANHHSEVCqzBgMG%2Fov2jjhFIw5erNrhhq6ttKyB9J7jBGSYQXwLdGtKU5xpG5uvUg8BIfecAOmW6wsI5yHhbRjMSzVPkHLddcBMPcPjof%2BztF7LKMx2ZxvcVHGaRgMiOyYLQq9%2BIYrvOLSTDOl7TQBjqZAQIUq9a62gbwFZXP%2BbuvskipWxLS%2F2cg7M6Z3pMxKDIBRyaO5m9PwZhrIITUbL7P4vhj1RVmDPu4C6CNV%2BlqrDTD5Rx1K02VeIE4Tj5beC79%2FphKhYumud9J7%2B3u8MwpB58awpicZWqHYy%2BQW4MLezQEl9Sz956kw39hr6%2BrZzpQQ261I76ImlBekDDC9iKzs07z%2Ff%2F1e6AWWg%3D%3D&Expires=1779241064)
- [CONTRIBUTING-2.md](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/10746152/2ce5e9df-eadd-453c-b024-053bada9a5a5/CONTRIBUTING-2.md?AWSAccessKeyId=ASIA2F3EMEYE2V6RTIML&Signature=Y3swwy5z2jO1RHoWWJNAPZGbRPM%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEBoaCXVzLWVhc3QtMSJGMEQCIF2J%2B51LRPL%2FOIqB38XVyQVcBA%2BRbduaa6vR6VUszcIhAiB0fj2lK4BrtIG8bMb1XYp6MZyCpufT6zOSkvhpBwAFaCr8BAji%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F8BEAEaDDY5OTc1MzMwOTcwNSIMxo1e%2F5eZh7ywTS7zKtAEJwrViaQ%2fnKtLuuNoadqidy21Rb91St2wsmASLimlpa2J%2Fk8y9gwzXNEaW0bOvI0FESclDY1KeByiK0MHkfS6WJHmCemEn8XEQigyT8Uw%2Fh519GWql3qrGgLvsYGvgM0dJbi6yaLb5c1h36Kgt6FBCVJrrroe247HVOi%2BQ3afX8%2FpafGq1mEh6D%2BDyaCaLko6hbOVUpnW2oBCk9E0OKfmIb4m1GdkPp9LNK1F5kCWqFPJhClzaoklK0kNc2WwiDoaa4DCuTICM6gTdScjJZF3%2FpQYIgyuoL0ov1S3jtbtkPMUTkaND1ieHfFFY4jhpzVCJXsJYQnkBDeLDS79O6OKF3wwlIN6bxg5yIEPbPdNoFIZLyrKMR03R7AZHMqsZNg8j9NNhwlo0PtRr3VFczZS5ucHWpKG03%2F7eywx9CR1AK%2Bo3pa%2F1jkQJWSHJjcIL9FfTM2dMDL9W1706KbhiOpRb1Oq4o8j34rt5BMgm6zqM0ytLOuMx6Pai6KPV5VQ4kHEkxQUOs%2F1VBmDfzRiCxMo5cxMkb7U6v7Ug6ERPKxiuH0UQBPQ6YR7II0fClAUCLT5408GnWRy5yZFHFyc2fPloPNOhtFrFPsWtWNG98DHIMtFBI3KcGia9OujlphgUGV%2FEQPcqpJsANHHSEVCqzBgMG%2Fov2jjhFIw5erNrhhq6ttKyB9J7jBGSYQXwLdGtKU5xpG5uvUg8BIfecAOmW6wsI5yHhbRjMSzVPkHLddcBMPcPjof%2BztF7LKMx2ZxvcVHGaRgMiOyYLQq9%2BIYrvOLSTDOl7TQBjqZAQIUq9a62gbwFZXP%2BbuvskipWxLS%2F2cg7M6Z3pMxKDIBRyaO5m9PwZhrIITUbL7P4vhj1RVmDPu4C6CNV%2BlqrDTD5Rx1K02VeIE4Tj5beC79%2FphKhYumud9J7%2B3u8MwpB58awpicZWqHYy%2BQW4MLezQEl9Sz956kw39hr6%2BrZzpQQ261I76ImlBekDDC9iKzs07z%2Ff%2F1e6AWWg%3D%3D&Expires=1779241064)

## Related
- [[Faust-CLI-Guide]] — Detailed guide on Faust CLI usage and development.
- [[Task-Management-System]] — Overview of task management systems and their implementations.
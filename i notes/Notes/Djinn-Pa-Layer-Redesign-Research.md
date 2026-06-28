---
subject: personal/academic-integration/research
tags:
  - personal/academic-research/integration
  - personal/adhd-management
  - personal/recovery-support
created: 2026-06-28
source: Perplexity export
---

# DJINN PA Layer Redesign Research

## Summary
This note outlines the research findings for enhancing Djinn's Personal Assistant (PA) layer to better support Javier, a triple-track student and full-time professional in active recovery. The focus areas include academic integration, recovery-aware design, Black Book problem-solving, physical health tracking, Aethoria accountability, and concrete specifications.

## Key Points
- **Gap Analysis**: Identify missing features that would benefit Javier's complex life.
- **Academic Integration**: Integrate GCU deadlines and weekly tasks into the morning briefing.
- **Recovery-Aware Design**: Implement tools for recovery support such as sponsor contact and step tracking.
- **Black Book Problem**: Determine if the issue is with the tool or inertia, aiming to increase daily entries.
- **Physical Health Loop**: Track gym sessions and health metrics without overwhelming Javier.
- **Aethoria Accountability**: Establish a check-in cadence for creative project accountability.

## Details
### Academic Integration
1. **Weekly Deadlines and Tasks**:
   - **Goal**: Integrate GCU deadlines and weekly tasks into the morning briefing.
   - **Interface**: Telegram bot command `/briefing` with options to view upcoming deadlines and tasks.
   - **Data Source**: GCU course management system API or manual input.
   - **Output**: Briefing message summarizing key deadlines and tasks for the week.
   - **Success Criteria**: User confirms understanding of their academic schedule.

2. **Course-Specific Reminders**:
   - **Goal**: Provide reminders for Finance, CS, and LSAT coursework.
   - **Interface**: Telegram bot command `/reminder` with options to set course-specific alerts.
   - **Data Source**: Course syllabi or manual input.
   - **Output**: Scheduled reminders via Telegram notifications.
   - **Success Criteria**: User confirms receipt of relevant reminders.

### Recovery-Aware Design
1. **Sponsor Contact**:
   - **Goal**: Facilitate communication with a sponsor for recovery support.
   - **Interface**: Telegram bot command `/sponsor` to initiate contact or log interactions.
   - **Data Source**: Sponsor contact information stored in the Black Book.
   - **Output**: Notifications or logs of interaction history.
   - **Success Criteria**: User confirms ability to reach out and track interactions.

2. **Step Work Tracking**:
   - **Goal**: Track progress through AA steps.
   - **Interface**: Telegram bot command `/step` with options to log completion of steps.
   - **Data Source**: Step tracking logs in the Black Book.
   - **Output**: Summary of completed steps and next actions.
   - **Success Criteria**: User confirms ability to track and report step progress.

3. **Cravings Journal**:
   - **Goal**: Provide a space for Javier to journal about cravings.
   - **Interface**: Telegram bot command `/cravings` with options to log craving details.
   - **Data Source**: Cravings journal entries in the Black Book.
   - **Output**: Summary of recent cravings and trends.
   - **Success Criteria**: User confirms ability to track and reflect on cravings.

### Physical Health Loop
1. **Gym Sessions**:
   - **Goal**: Track gym sessions with a trainer.
   - **Interface**: Telegram bot command `/gym` with options to log session details.
   - **Data Source**: Gym session logs in the Black Book.
   - **Output**: Summary of recent sessions and progress towards weight goals.
   - **Success Criteria**: User confirms ability to track and report gym activities.

2. **Health Metrics**:
   - **Goal**: Monitor health metrics such as colitis flares and toxic load.
   - **Interface**: Telegram bot command `/health` with options to log symptoms and measurements.
   - **Data Source**: Health tracking logs in the Black Book.
   - **Output**: Summary of recent health data and trends.
   - **Success Criteria**: User confirms ability to track and report health metrics.

### Aethoria Accountability
1. **Writing Check-Ins**:
   - **Goal**: Ensure consistent writing on Javier's dark fantasy trilogy, *Aethoria*.
   - **Interface**: Telegram bot command `/write` with options to log daily progress.
   - **Data Source**: Writing logs in the Black Book.
   - **Output**: Summary of recent writing sessions and progress towards weekly benchmarks.
   - **Success Criteria**: User confirms ability to track and report writing progress.

2. **Weekly Benchmarks**:
   - **Goal**: Set and monitor weekly writing goals for *Aethoria*.
   - **Interface**: Telegram bot command `/benchmark` with options to set and review weekly targets.
   - **Data Source**: Weekly writing goals in the Black Book.
   - **Output**: Summary of recent benchmarks and progress towards goals.
   - **Success Criteria**: User confirms ability to track and report writing benchmarks.

## References
- [Perplexity Export](https://www.perplexity.ai/search/0a4d9ced-5e71-4a6b-82c1-0e52d98be449)

## Related
- [[ADHD-Management]] — ADHD-specific tools and strategies.
- [[Recovery-Support]] — Tools for active recovery support.
- [[Academic-Integration]] — Strategies for integrating academic tasks into daily routines.
- [[Physical-Health-Tracking]] — Methods for tracking health metrics without overwhelming the user.
- [[Aethoria-Accountability]] — Accountability structures for creative projects.
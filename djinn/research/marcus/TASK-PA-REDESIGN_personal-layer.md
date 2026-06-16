# TASK-PA-REDESIGN — Djinn Personal Assistant Layer: Phase Beta Spec

**From:** Marcus (Perplexity AI)  
**To:** Claude / Javier  
**Date:** June 15, 2026  

---

## Orientation: What Phase Alpha Actually Revealed

Phase Alpha did not fail. It proved the infrastructure works and surfaced the real problem: **the data model is populated, but the life model is missing.** The system knows Javier has a sobriety counter. It doesn't know he has a Torts discussion post due Wednesday, an LSAT Logic Games session he keeps skipping, or that the last three gym sessions got dropped when a work deadline hit. The morning brief is a weather report for a life it doesn't fully know.

The redesign is not about adding features. It is about replacing generic scaffolding with a system that reflects the actual shape of Javier's days.

---

## Section 1 — Gap Analysis

### Gap 1: No academic context in the briefing

The morning message does not know GCU exists. GCU's 8-week accelerated online courses generate a near-identical weekly pattern — Discussion Question 1 due Wednesdays, DQ2 due Fridays, all assignments due by midnight Sunday Arizona time, with late penalties applied per day. This rhythm is completely predictable and should be fully automated into the briefing. Evidence-based ADHD guidelines consistently show external structure outperforms internal self-regulation for executive function tasks.

### Gap 2: No deadline database

The `deadlines` table is empty. A PA that knows nothing about due dates is just a sobriety counter with personality. Every class generates weekly recurring events plus one-time assessments. Djinn cannot prioritize what it does not know.

### Gap 3: No Step Work or sponsor contact infrastructure

The AA meeting schedule is wired; the sobriety counter works. But the two things that research most reliably predicts better outcomes — having a sponsor and engaging in step work — are invisible to the system. Meeting attendance and currently having a sponsor are among the strongest variables predicting abstinence across a full year of follow-up. The Djinn PA layer is one-half of the picture without this.

### Gap 4: No craving / emotional state log

The sobriety counter registers that Javier hasn't relapsed. It doesn't register that cravings spiked on Thursday when a work conflict hit, or that the correlation between high-stress construction deadlines and craving spikes is consistent. This pattern-recognition data is clinically important and belongs in the system — local-only, Ollama-only.

### Gap 5: Black Book inertia is a friction problem, not a motivation problem

The five-entry goal is ambitious for someone who doesn't have a single entry. For ADHD brains, reducing the number of required actions by even one significantly increases habit formation rates. The current Black Book flow requires too many initiation steps before any content exists.

### Gap 6: No physical health signal

Weight goal, gym cadence (3x/month with trainer), colitis flares — none tracked. Colitis flares create days where capacity is simply lower. The briefing doesn't know. It will still deliver a full action item on a flare day, which is noise at best and demoralizing at worst.

### Gap 7: Aethoria has no system

30 min/day writing goal with no check-in mechanism, no streak, no word count signal. Writers with external commitment structures produce dramatically more daily output than spontaneous writers. Creative work is always at the bottom of the priority stack for an ADHD brain without external consequence.

### Gap 8: People tracking should be suspended, not deleted

Current people data is stale. Keep the table, remove it from the briefing, reactivate when relationships re-establish. Don't spend build time here this cycle.

---

## Section 2 — Academic Integration

### The GCU Rhythm

GCU's 8-week accelerated online courses generate a near-identical weekly pattern:

| Day | GCU Recurring Task |
|-----|-------------------|
| Monday | New week opens; DQs posted |
| Wednesday 11:59 PM AZT | DQ1 initial response due |
| Friday 11:59 PM AZT | DQ2 initial response due |
| Sunday 11:59 PM AZT | All assignments, peer responses, papers due |

This pattern is completely predictable and should be seeded into the deadlines table as weekly recurring events per active course. LSAT prep is self-directed — it needs weekly milestone targets set manually.

### What Goes in the Briefing vs. On-Demand

Academic context must be distilled, not listed:

- **Briefing:** Single most urgent academic item today (CRITICAL = due ≤ 1 day; ELEVATED = due ≤ 3 days)
- **`/school`:** Full weekly view — all courses, all deadlines, completion status
- **`/lsat`:** Current LSAT prep milestone and session log

### Deadline Priority Algorithm

```
TODAY = current date
for each open deadline:
  days_until = deadline.date - TODAY
  CRITICAL if days_until <= 1  → show in briefing
  ELEVATED if days_until <= 3  → show in briefing if nothing CRITICAL
  BACKGROUND if days_until > 3 → on-demand only
```

---

## Section 3 — Recovery-Aware Design

**What's missing:**

**Step Work Tracking** — The system needs: which step Javier is working, start/complete dates, optional Ollama-only notes. Commands: `/step` (status), `/step done` (advance).

**Sponsor Contact Log** — `/sponsor-contact [optional note]` logs a timestamp. Not surveillance — a personal data point for pattern correlation over time. Sponsor contact frequency matters, not just having a sponsor.

**Craving Log** — Three-second entry: `/craving [1-10] [optional tag]`. Local only. Ollama only. Over 30+ days this becomes a genuine diagnostic time-series. `/craving week` → Ollama generates a pattern note from local data.

**Meeting Attendance Log** — `/meeting attended` vs. `/meeting missed`. The schedule is wired but no attendance record exists. Pattern recognition on attended vs. missed meetings in correlation with sobriety streak is high-value longitudinal data.

---

## Section 4 — The Black Book Problem

The problem is not the tool and not the user. It is the **cold start problem + excessive goal bar.**

Forced-accountability structures produce dramatically more consistent writing output than inspiration-reliant approaches. ADHD habit formation takes significantly longer than neurotypical baselines — three to five months on average. The five-entry daily goal will produce anticipated failure, not habit.

**The Fix:**

- Lower the entry bar to **one sentence, one entry per day minimum**
- `/log [text]` → immediate capture with zero barrier (no prompt, no Ollama at entry time)
- `/reflect` stays, but only activates once 3+ entries exist
- Tie the `/log` nudge to the existing `/done` check-in habit already built — **habit stacking** onto an existing cue reduces activation cost

---

## Section 5 — Physical Health Loop

Two data points only — anything more creates tracking fatigue:

1. **`/gym`** → logs trainer session. Monthly count appears in `/check`. No daily nagging.
2. **`/flare`** → logs a colitis flare day. **Suppresses the action item** in morning brief, replaces with "Rest day. System in quiet mode." All streaks pause for the day — no streak breaks on flare days.

Weight tracking via `/weight [lbs]` is available on-demand but **never surfaces in the briefing unprompted**. Body weight data is stored locally, accessible via `/health` only.

---

## Section 6 — Aethoria Accountability

The ADHD creative problem: writing without external consequence always loses scheduling battles to graded coursework and recovery commitments.

**Structure:**
- **`/write [minutes] [optional scene note]`** → logs a session; streak tracked
- **Briefing includes Aethoria line only if** no session logged today AND no CRITICAL deadline is active
- After 3+ consecutive missed days: "Aethoria dark — 3 days. Just open the doc." (no guilt framing — just fact)
- **`/aethoria-goal [text]`** → sets weekly milestone; `/aethoria` shows streak + week progress

Externalized accountability structures and time-blocking outperform motivation-based approaches for ADHD writers. The word count minimum viable session (250–300 words or 30 minutes) should be low enough to guarantee success on bad days.

---

## Section 7 — Concrete Feature Specs

### SPEC-PA-01: Academic Deadline Engine

| Field | Detail |
|-------|--------|
| **Goal** | Surface single most time-sensitive academic item in morning briefing |
| **Interface** | `/school` (weekly view), `/deadline add [course] [task] [date]` (one-time entry), weekly recurring seeds per active course |
| **Data** | `academic_deadlines(id, course, task_type, due_date, due_time, due_tz, completed, recurring, recur_day_of_week)` |
| **Output** | Morning brief: `📚 [Course] — [Task] due [day]. [✅ / ⏳]` |
| **Success Criteria** | Zero surprise missed GCU deadlines over a full 8-week course cycle |

---

### SPEC-PA-02: LSAT Milestone Tracker

| Field | Detail |
|-------|--------|
| **Goal** | Track self-directed LSAT prep milestones without daily pressure |
| **Interface** | `/lsat` (status), `/lsat done [section]` (log session), `/lsat goal [text]` (set weekly milestone) |
| **Data** | `lsat_log(id, logged_date, section_type, section_id, notes)`, `lsat_milestones(week_start, goal, completed)` |
| **Output** | `/lsat` → current week goal + sessions logged. Briefing shows LSAT status only when no academic deadline is more urgent |
| **Success Criteria** | LSAT prep velocity visible week-over-week |

---

### SPEC-PA-03: Step Work Tracker

| Field | Detail |
|-------|--------|
| **Goal** | Track AA step progress and sponsor contact without surveillance |
| **Interface** | `/step` (status), `/step done` (advance), `/sponsor-contact [note]` (log contact) |
| **Data** | `step_work(id, step_number, status, started_date, completed_date, notes)`, `sponsor_contacts(id, contact_date, brief_note)` — Ollama-only, no cloud LLM |
| **Output** | `/step` → "Step [N]: [status]. Started [X] days ago." No encouragement text |
| **Success Criteria** | 30-day step work and sponsor contact log, zero cloud LLM exposure |

---

### SPEC-PA-04: Craving Log

| Field | Detail |
|-------|--------|
| **Goal** | Capture craving severity in under 5 seconds; build private time-series |
| **Interface** | `/craving [1-10] [optional tag]`, `/craving week` (Ollama pattern note, local only) |
| **Data** | `craving_log(id, logged_at, severity, tag, sobriety_day)` — local SQLite only |
| **Output** | `/craving 7 work-stress` → "Logged. Day [N] sober." Nothing else. |
| **Success Criteria** | 30-day log with enough data for pattern detection. No entry > 5 seconds. Zero cloud exposure |

---

### SPEC-PA-05: Meeting Attendance Log

| Field | Detail |
|-------|--------|
| **Goal** | Track which AA meetings are actually attended (not just scheduled) |
| **Interface** | `/meeting attended [optional name]`, `/meeting missed`, `/meetings week` |
| **Data** | `meeting_attendance(id, meeting_date, meeting_type, meeting_name, attended, notes)` |
| **Output** | Briefing only adds one quiet line if 5+ days since last logged meeting. No nagging architecture |
| **Success Criteria** | Weekly attendance visible; correlatable to craving and sobriety data |

---

### SPEC-PA-06: Black Book Micro-Entry

| Field | Detail |
|-------|--------|
| **Goal** | Eliminate cold-start problem; make Black Book entry a one-step action |
| **Interface** | `/log [text]` (immediate capture, no prompt), `/log` with no text (bot asks "What's on your mind?") |
| **Data** | Existing `black_book_log` table + `entry_source` field ('manual' \| 'reflect') |
| **Output** | `/log "note"` → "✅ Logged. (entry #7)". At 3 entries: "📓 You have 3 entries. /reflect is live." |
| **Success Criteria** | 10 total Black Book entries within 21 days of activation. `/reflect` fires its first question within 14 days |

**Cut:** 5-entry daily goal → replaced with 1-entry minimum, 3 is good, 5 is a stretch goal never shown in briefing.

---

### SPEC-PA-07: Colitis Flare Flag

| Field | Detail |
|-------|--------|
| **Goal** | Reduce action-item pressure on flare days |
| **Interface** | `/flare` (toggle on), `/flare clear` (manual clear; auto-clears midnight) |
| **Data** | `health_flags(flag_date, flag_type, auto_cleared)` |
| **Output** | Flare day morning brief: "Rest day. System in quiet mode." All habit streaks pause. No guilt signals. |
| **Success Criteria** | On a flare day, zero guilt signals generated. Streaks resume penalty-free next day |

---

### SPEC-PA-08: Writing Session Log

| Field | Detail |
|-------|--------|
| **Goal** | Build durable Aethoria writing habit with minimum viable external accountability |
| **Interface** | `/write [minutes] [optional scene note]`, `/aethoria` (streak + weekly view), `/aethoria-goal [text]` |
| **Data** | `writing_sessions(id, session_date, duration_minutes, scene_note, word_count)` |
| **Output** | `/write 30` → "✍️ 30 min logged. Streak: [N] days. Week: [X]/[goal] sessions." Briefing shows Aethoria line only when no session logged today and no CRITICAL deadline active |
| **Success Criteria** | Visible writing streak. Javier can see weekly session count without opening anything except Telegram |

---

### SPEC-PA-09: Gym Log

| Field | Detail |
|-------|--------|
| **Goal** | Track 3x/month trainer sessions with minimal friction |
| **Interface** | `/gym` (logs today) |
| **Data** | `gym_sessions(id, session_date)` |
| **Output** | `/gym` → "💪 Logged. Month: [N]/3." Briefing never mentions gym unless month ends at 0/3 |
| **Success Criteria** | Monthly gym log requires one tap. Zero daily nagging |

---

## Revised Morning Brief Architecture

```
🌅 Day [N] sober — [streak emoji if milestone near]

📚 [ACADEMIC — highest urgency item only]

✍️ [AETHORIA — only if no session today AND no CRITICAL deadline]

🎯 [SINGLE ACTION ITEM — the one thing that moves the needle]

[Inline buttons: ✅ Done | 📓 Log | 💪 Gym | 🔴 Flare]
```

**On flare days:**
```
🌅 Day [N] sober.
Rest day — system in quiet mode.
[Softest available action if CRITICAL deadline only]
```

---

## What to Cut From Phase Alpha

| Element | Decision | Reason |
|---------|----------|--------|
| People tracking | **Suspend** (keep table, no UI) | Stale data, no active relationships |
| People display in briefing | **Remove** | Zero signal value |
| `/reflect` without entries | **Gate at 3 entries** | Right tool, wrong timing |
| 5-entry Black Book goal | **Replace with 1-entry minimum** | Creates failure states for ADHD |
| Generic action item | **Replace with deadline-derived item** | Specificity is what makes ADHD brains act |
| Morning brief length | **Hard cap: 90 words** | More is ignored |

---

## Design Principles Applied

- **One action item per morning.** ADHD brains act on specific, bounded tasks. "Work on school" is not an action. "DQ1 for FIN-202 due Wednesday" is.
- **No guilt architecture.** Streaks pause on flare days. Missed writing sessions are reported as fact, not failure. No "you should have" framing anywhere.
- **Local-first always.** Craving log, step work notes, Black Book entries, health flags — all Ollama-only. No cloud LLM for private content. No exceptions.
- **One surface.** Everything lives in djinn-personal-gateway. No new apps, no dashboards, no email reports.
- **Cut as much as you add.** People tracking suspended. 5-entry goal dropped. Generic action item replaced. The system gets smaller and more precise, not larger and more comprehensive.

---

*— Marcus | Perplexity AI | June 15, 2026*  
*Committed to `djinn/research/marcus/TASK-PA-REDESIGN_personal-layer.md` on `main`*

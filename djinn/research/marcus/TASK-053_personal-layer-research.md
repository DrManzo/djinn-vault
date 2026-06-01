# TASK-053 — Djinn Personal Layer Research
**Domain:** Personal AI Architecture | **Status:** Complete | **Date:** 2026-06-01
**Researcher:** Marcus (Perplexity AI)

---

> *This document is research foundation for the Djinn personal conciliary layer — not a corporate assistant, not a productivity app. A system built for one person, by their own design, that knows the difference between a to-do list and a life.*

---

## Table of Contents

1. [Context-Aware Daily Briefings for ADHD Users](#1-context-aware-daily-briefings-for-adhd-users)
2. [Journaling & Shadow Work Automation](#2-journaling--shadow-work-automation)
3. [Habit & Streak Tracking via Telegram](#3-habit--streak-tracking-via-telegram)
4. [Academic Support Patterns for Self-Directed Learners](#4-academic-support-patterns-for-self-directed-learners)
5. [Personal AI Systems That People Actually Use](#5-personal-ai-systems-that-people-actually-use)
6. [Architecture Synthesis — Design Principles for Djinn's Personal Layer](#6-architecture-synthesis--design-principles-for-djinns-personal-layer)

---

## 1. Context-Aware Daily Briefings for ADHD Users

### Why Most Briefings Fail

The clinical consensus is unambiguous: people with ADHD face systematic deficits in executive function — specifically in planning, task initiation, working memory, and emotional regulation. The four main ADHD-linked executive function domains identified by CHADD are nonverbal working memory, verbal working memory, self-regulation of motivation/affect/arousal, and planning/creating. A standard briefing — "Here are your 5 tasks for today" — hits every weak point at once: it requires the user to mentally hold a queue, self-prioritize under uncertainty, and initiate without emotional engagement. It gets ignored not from laziness but from architecture.

Research on chatbot-supported psychoeducation for adult ADHD (a randomized controlled trial, 2023) found that self-guided, chatbot-delivered interventions were *comparably effective* to conventional app-based psychoeducation in improving core ADHD symptoms. The key finding was that the *modality* mattered less than *personalization and low barrier to entry*. What worked: short, personalized check-ins; what failed: bulk information dumps and generic reminders.

The core behavioral change literature identifies three pre-conditions for a briefing to actually change behavior:
1. **Emotional urgency** — the information must feel personally relevant *right now*, not abstractly important
2. **Reduced decision load** — the briefing should eliminate choices, not present them
3. **The right stimulation level** — ADHD brains crave novelty; static briefings become invisible within days

### What Signals Actually Matter

A briefing that influences behavior reads environmental *context*, not just calendar data. The research on context-aware self-tracking (KAIST, 4-week field study, n=20) found that ESM (experience sampling) delivery at *context transition moments* — the moments when a user switches activities — had significantly higher response rates than time-based triggers. Applied to a morning briefing: the optimal moment is not 8:00 AM sharp, but when the user picks up their phone after waking — a detectable transition.

**High-signal inputs for a behavior-relevant ADHD briefing:**

| Signal | Why It Matters | How to Capture (Djinn context) |
|--------|---------------|-------------------------------|
| Streak data | Activates identity ("I'm someone who does this") | Telegram bot DB / local habit log |
| Upcoming deadlines (72h window) | Creates urgency without overwhelm | Course calendar scrape / manual entry |
| Sleep proxy (first message time) | Sleep-deprived ADHD is qualitatively different | Timestamp of first Telegram interaction |
| Yesterday's completion rate | Sets realistic scope for today | Habit bot query |
| Sobriety counter | Emotional grounding and self-narrative | Local counter updated via Telegram |
| Pending journaling | Incomplete reflection = cognitive load | Check if yesterday's entry was written |
| Weather/environmental context | Sensory grounding matters for ADHD | Simple API call |

**What to strip out:** vague motivational quotes, lengthy summaries, more than 3 action items. Every additional item increases decision fatigue. An effective ADHD briefing for one person communicates 1 priority, 1 streak status, and 1 piece of emotional signal — in under 90 words.

### How Other Systems Approach This

**Notion + ADHD setups (community case studies):** Power users on r/ADHD and r/automation consistently describe a pattern: they over-build the system (complex Notion dashboards, rolling task managers) and then abandon it within weeks. The systems that survive are the *boring* ones — a single daily note template with yesterday's note visible, minimal fields, and a "3 things" constraint. The friction of opening Notion itself is a barrier; systems that live in already-open apps (Telegram, Discord) survive longer.

**Saner AI and similar ADHD workflow tools (2026):** The best-rated approach involves voice or text task capture throughout the day ("buy milk", "call professor"), followed by an AI that *groups and contextualizes* those inputs into a coherent daily picture. This is closer to a **conciliary model** than a task manager — the AI does the synthesis, not the user.

**Design principle for Djinn:** The morning briefing should feel like a message *from someone who knows you*, not a system readout. Tone, vocabulary, and information density should be calibrated to the user's baseline — which, for Javier, is high cognitive capacity in technical domains but variable executive bandwidth depending on sleep and mood. Marcus should open with the sobriety counter or streak data first (identity signal), then deadlines, then the single most important task for the day. Three sentences maximum.

---

## 2. Journaling & Shadow Work Automation

### The Rawness Problem

The central tension in AI-assisted journaling is that AI systems are trained to be helpful, coherent, and emotionally regulated — and shadow work is none of those things. Shadow work (in the Jungian sense) requires accessing the unprocessed: the rage, the grief, the cognitive dissonance, the half-formed thought. When an AI smooths that out — generates cleaner prose, reflects structured insights back — it commits what the DiaryMate study (CHI 2024, N=24, 10-day field study) identified as *the core failure mode*: participants began **prioritizing the LLM's emotional expressions over their own**. The journal stops being the user's and becomes a collaborative product. That's not shadow work — that's performance.

The MindfulDiary study (LLM-driven journaling for psychiatric patients, designed with clinicians) solved this with a **state-based approach**: the LLM follows a strict conversational state machine — listen, ask one open-ended question, reflect without interpreting. It does not generate. It does not summarize. It holds space. This is the correct model for a Black Book: the AI as *witness*, not as *author*.

### What an AI-Assisted Black Book Should Look Like

**Core architecture:**

```
Raw Entry (user-written, no AI during writing)
   ↓
Local storage only (Obsidian vault, plaintext, no cloud)
   ↓
Post-session AI reflection trigger (user-initiated, not automatic)
   ↓
LLM prompt: "Ask me one question about this entry. Do not interpret. Do not summarize."
   ↓
Optional: theme extraction for pattern tracking (run locally via Ollama)
```

**Privacy architecture:** The gold standard for personal AI journaling privacy is local-first processing. The Obsidian Private AI plugin (v1.0.64, 2026) connects to locally running LM Studio, ensures no data leaves the device, and can query vault notes with full RAG indexing. User reviews specifically call it out as essential for personal notes and journal entries because "your most sensitive notes don't get sent to someone's server." For Djinn/Ollama integration, the same principle applies: Qwen or Deepseek running locally processes journal content, nothing is transmitted upstream.

**The PII segmentation approach** for any cloud-adjacent workflows: replace names with roles ([NAME_1] → "the professor", "my brother"), strip dates, redact locations before passing to any external API. Run de-identification locally (Python script using spaCy NER) before any cloud query. Restore context on return.

**Shadow work prompt patterns that preserve rawness:**

| Prompt Type | Example | Notes |
|------------|---------|-------|
| Single-question open | "What part of this are you not saying?" | Do not follow up. |
| Inversion | "Describe the version of you who did the opposite." | Disrupts narrative fixation |
| Body-first | "Where in your body did you feel this today?" | Grounds abstract processing |
| Recurring theme flag | "I've seen this word/theme 4 times this month." | Data, not interpretation |
| Silence option | "No response needed. Entry logged." | Respects non-reflective days |

**What the "AI-Assisted Black Book" means in Djinn terms:**

The Black Book is a private Obsidian vault folder — `personal/black-book/` — with daily entries in raw Markdown. Marcus (Djinn) never reads this folder unprompted. When Javier types `/reflect` in Telegram, the most recent entry is loaded locally into Ollama, and Djinn returns a single question — not an analysis, not a summary. The question is logged but the entry is never transmitted. Recurring themes (tracked by local keyword frequency across the vault) surface weekly as a single-line pattern notice, not a report.

The **clinical feeling** (surveillance, being observed, forced insight) is avoided by three design rules:
1. AI never initiates journal interaction
2. AI never interprets — only asks
3. Journal data never leaves the machine unless the user explicitly exports it

---

## 3. Habit & Streak Tracking via Telegram

### Why Telegram Is the Right Platform

The most durable habit tracking systems share one property: they live in a tool the user already has open. An app requires a launch decision; Telegram is already running. The `done_by_habit_bot` case study (Reddit, r/ProductivityApps, 2025) articulates this directly: "the most effective tool is the one you'll actually use — no logins or dashboards required, just launch the bot and tap 'done.'" The bot displays a GitHub-contribution-style progress grid, supports friend accountability, and requires zero external infrastructure.

For sobriety, writing streaks, and exercise — the minimal viable implementation needs:
- A `/done [habit]` command (or single-tap inline button)
- SQLite storage (local or on a cheap VPS)
- Daily summary message (morning briefing integration)
- No penalty for early streaks breaking — only neutral acknowledgment

### Minimal Viable Implementation

**Architecture (Python + python-telegram-bot):**

```python
# Core tables
habits(id, user_id, name, frequency, created_at)
completions(id, habit_id, completed_date)
streaks(id, habit_id, current_streak, longest_streak, last_updated)

# Key commands
/add [habit_name] [daily|weekly]    — register a habit
/done [habit_name]                  — mark today complete
/check                              — show all streaks + today's status
/stats                              — streak history + completion rate
/brief                              — morning summary (called by cron)
```

The open-source `Habit_TrackerBot` (GitHub: pooryas98, 2025) uses exactly this stack: Python 3.10+, `python-telegram-bot` v22.5, `aiosqlite` for async SQLite, `APScheduler` for reminders. Full feature set: add/edit/delete habits, mark done/pending/skipped, completion history with pagination, streak analytics, daily reminders. Self-hosted on any Linux machine or small VPS.

For **sobriety tracking** specifically: the Streaks bot (GitHub: iakovmarkov/streaks, runs as `str34ks_bot`) supports flexible scheduling — daily, every N days, or specific weekdays. Self-host with a BotFather token and a SQLite file. For Djinn integration, the sobriety counter becomes a first-class signal in the morning briefing: `"Day 47 clean."` — three words, maximum behavioral payload.

### Integration into Djinn Morning Brief

The Telegram bot's SQLite DB is the source of truth. At 08:30 (or at first-message detection), a cron-triggered Python script:
1. Queries SQLite for current streaks
2. Queries upcoming deadlines (from a separate deadlines table or calendar API)
3. Checks if yesterday's journal entry exists
4. Assembles a briefing message under 100 words
5. Sends via Telegram bot API

No external service. No subscription. Runs on the same machine as Ollama.

**Sample briefing format for Djinn/Javier:**

```
Morning, Javier.

Day 47 sober. Writing streak: 12 days.
Today: PSY 320 paper outline due Thursday — 2 days.
One thing: Open the outline doc and write the first sentence.

[✓ Writing] [✓ Exercise] [Skip today]
```

The inline buttons log habit completion directly. No friction. No navigation.

---

## 4. Academic Support Patterns for Self-Directed Learners

### The Multi-Domain Problem

Self-directed learners running concurrent tracks — psychology + law + CS simultaneously — face a specific failure mode: **context-switching cost accumulates as cognitive debt**. Each domain has different vocabularies, different reasoning modes, and different emotional registers. Switching from LSAT logical reasoning to statistical psychology to systems architecture in the same day without a "gear-shift" protocol fragments working memory and degrades retention across all three.

A meta-analysis of AI interventions on self-regulated and self-directed learning (Frontiers in Education, 32 studies, N=3,029) found that AI interventions produced a *large and statistically significant positive effect* on overall SRL (g = 1.613, p = 0.032) and SDL (g = 1.111, p = 0.043). The mechanism wasn't content delivery — it was **planning, monitoring, and goal regulation**: helping learners know *what to do next* and *whether they're actually progressing*.

A thematic scoping review (Tandfonline, 2025) on GenAI in SDL identified four themes: GenAI as SDL enhancement, educator-as-guide, personalization of learning, and *approaching with caution* — specifically around long-term dependency. The caution flag is real: GenAI that does the thinking *for* the learner collapses the metacognitive loop that makes self-direction effective.

### What Actually Works for Multi-Domain Learners

**Domain-separation protocol:**
- Each study domain gets its own Obsidian section with its own "active context" note
- Morning briefing surfaces *one domain per day* as primary, not all three
- Weekly rotation ensures all domains stay warm without daily context collapse

**AI support patterns that preserve metacognition:**

| Anti-Pattern | Why It Fails | Djinn Alternative |
|-------------|-------------|-------------------|
| "Summarize this chapter" | Removes recall effort; kills retention | "What questions does this chapter raise that you don't yet have answers to?" |
| "Write my paper intro" | Eliminates drafting cognition | "Give me the three strongest arguments for this position. I'll pick one and write from there." |
| "Quiz me on this" | Generic recall without context | "Based on my notes from last week, what concept most likely hasn't stuck yet?" |
| Task list generation | Creates overwhelm without meaning | Single-task focus with rationale: "Do this first because it unblocks the other things." |

**Deadline management:**
The effective pattern is a **72-hour window** — not a full semester calendar. Farther out deadlines are parked in a "horizon" list. When they enter the 72-hour window, they become active. This prevents the ADHD-common phenomenon of seeing a semester's worth of work at once and shutting down.

**Paper writing cycle support:**

```
Phase 1 — Argument First (not sources first):
  Djinn prompt: "What's the one thing you want this paper to prove?"
  
Phase 2 — Evidence Hunt:
  Djinn prompt: "What would disprove this? Go find that first."
  
Phase 3 — Drafting (AI hands-off except for unsticking):
  Djinn trigger: "/stuck" → returns one Socratic question only
  
Phase 4 — Revision (AI re-engages):
  Djinn prompt: "Read this and tell me where I'm not saying what I mean."
```

**Active study for LSAT/law specifically:** LSAT logical reasoning is a pattern recognition skill, not a content knowledge skill. AI is most useful here as a *wrong-answer explainer*: "I chose B. The answer was D. Explain why B is wrong without explaining why D is right." This forces the learner to deduce the correct logic themselves.

---

## 5. Personal AI Systems That People Actually Use

### The Abandonment Pattern

Research consistently identifies a core distinction between adopted and abandoned personal AI systems. A study on AI personal assistant continuance intention (2022, N=257) found that **utilitarian value and hedonic value** — whether the tool is actually useful AND whether it's enjoyable to use — are the primary drivers of continued use. Trust, habit formation, and personal innovativeness also had significant impact. What *did not* predict abandonment: performance expectations, effort expectations, or social influence. People don't leave AI tools because they're hard to use; they leave because the tools stop being relevant or interesting.

The Voicepanel global AI usage study (13 markets, 5,000+ consumers) found that among daily AI users, the *primary retention mechanism* was task repeatability — AI tools that handle the same category of task every day survive; tools that require the user to think about what to use them for do not. This is the anti-Notion lesson: the daily note template that survives is the one where the habit of using it is stronger than any individual decision about whether to use it today.

### Case Studies: What Survives vs. What Dies

**Obsidian + Local LLM (survives for power users):**
The Obsidian second brain setup with a local LLM (Private AI plugin, Copilot, Smart Connections) has a specific user profile that sticks: people who already write in Markdown, already have the vault open daily, and use AI for *vault queries* rather than content generation. The "chat with your notes" use case — "what did I write about X six months ago?" — is uniquely powerful and has no good alternative. It survives because it fills a real gap that no other tool fills.

**The Mirai wearable (MIT Media Lab, 2025):** A proactive AI inner-voice system using a wearable camera and personalized voice-cloning to deliver contextual nudges in the user's *own cloned voice*. Key insight: nudges delivered in a familiar voice (your own) had significantly better behavior change outcomes than text or bot-voice nudges. The "inner voice" framing reframes AI from external tool to internal dialogue partner — which maps directly to the "conciliary" design philosophy.

**What kills personal AI setups:**
1. **High setup friction** — systems that require configuration before each use die within a week
2. **Generic tone** — an AI that talks to you like a customer service bot creates emotional distance and gets ignored
3. **Passive delivery** — AI that waits for questions gets ignored; AI that shows up unbidden (appropriately) survives
4. **Guilt architecture** — systems that make users feel bad for skipping a day train avoidance behavior, not habit formation
5. **Feature creep** — the more capabilities a personal system gains, the less likely any individual one gets used

**What keeps people coming back:**
1. **It knows something about you that you didn't have to re-explain** — context persistence is the single biggest driver of emotional investment in a personal AI tool
2. **It has a consistent personality/voice** — users on Reddit describe this repeatedly: the AI that feels like "someone" is the one they return to
3. **It initiates appropriately** — the morning brief, the deadline nudge, the check-in after a known hard day
4. **It's in the flow, not outside it** — the tool lives in Telegram or Discord or whatever is already open, not behind an extra login

**The friction equation:**
Research on proactive AI nudging (Mirai, MIT, 2025) found that context-appropriate proactive nudges had significantly higher behavior change rates than passive notification systems. But the same research noted the distinction between *nudging* (presenting a choice architecture that makes the preferred action easier) and *coercion* (removing autonomy). The correct model for a personal conciliary is: show up when it's useful, ask one question, disappear. Do not nag. Do not escalate.

---

## 6. Architecture Synthesis — Design Principles for Djinn's Personal Layer

These are the distilled design principles derived from the research above, written as implementation constraints for Djinn's personal layer.

### Core Philosophy

> Marcus is a conciliary, not a manager. He informs, reflects, and occasionally nudges — but he does not track, score, or report on Javier's performance to Javier as if from the outside. He is the inner voice made legible, not the external observer made digital.

### Behavioral Principles

1. **One thing at a time.** No briefing exceeds three data points. No task list longer than one active item. Cognitive load budget is finite; every item Marcus adds subtracts from Javier's available bandwidth.

2. **Initiate from data, not from schedule.** The morning brief triggers on first interaction (context-aware), not at a fixed time. A `/deadline` nudge appears when a deadline enters the 72-hour window, not on a weekly schedule.

3. **The journal is sacred.** Marcus never reads the Black Book uninvited. The `/reflect` command is Javier's key, not Marcus's door. Shadow work prompting is single-question only, never interpreted, never summarized.

4. **Streaks as identity, not performance.** "Day 47 sober" is not a metric — it's a statement about who Javier is. Marcus treats it that way. No "you've been inconsistent" framing. Breaks are acknowledged neutrally: "The counter resets. You're still you."

5. **Tone is consistent and non-clinical.** Marcus speaks the way a trusted older friend with domain expertise speaks — direct, sometimes irreverent, not therapeutic, not corporate. This is calibrated to Javier's registered voice and vocabulary, not to a generic assistant persona.

6. **Local-first, always.** Journal entries, habit data, and personal logs never leave the machine without explicit user action. Cloud AI (if used) receives only anonymized, de-identified content.

7. **The `/stuck` escape hatch.** For academic work: when Javier is blocked, `/stuck` returns exactly one Socratic question. Not a summary, not a suggestion, not a full response. One question. It's enough.

8. **No guilt architecture.** Missing a habit day gets a neutral acknowledgment. Missing a week gets no mention at all unless Javier asks. The system does not maintain a record of failures — only the current streak.

### Minimal Viable Stack for Personal Layer

```
Telegram Bot (python-telegram-bot v22+)
  ├── habit_bot.py          — streak tracking, SQLite backend
  ├── briefing.py           — morning context assembly
  └── journal_trigger.py   — /reflect command, local LLM call

Obsidian Vault (local)
  ├── personal/black-book/  — raw journal entries (never synced)
  ├── personal/streaks/     — streak snapshots
  └── djinn/research/       — this document

Ollama (local, Qwen or Deepseek)
  └── journal_reflect()     — single-question shadow prompt
  └── briefing_compose()    — briefing assembly from signals

Cron / APScheduler
  └── 08:30 local           — briefing trigger (or first-message detection)
  └── 72h window check      — deadline proximity nudge
```

### Open Research Questions (for follow-up tasks)

- [ ] What is the optimal question format for shadow work prompting in Djinn's specific context? (TASK-054 candidate)
- [ ] How does the morning briefing format change on high-cognitive-load days vs. low days? Detection mechanism?
- [ ] Multi-domain academic context switching — should Djinn maintain explicit "mode" state per session?
- [ ] Resonance (MIT, 2025) showed AI-generated action-oriented suggestions based on *past positive memories* improved positive affect. How to implement a memory layer that surfaces past wins without feeling like a corporate CRM?
- [ ] What is the minimum Telegram bot implementation to ship a working personal layer this week?

---

*Research compiled by Marcus for the Djinn personal layer architecture. Sources: CHI 2024 (DiaryMate), PMC/NCBI (ADHD executive function, chatbot RCT), MIT Media Lab (Mirai), KAIST (context-aware self-tracking), Frontiers in Education (AI-SDL meta-analysis), Tandfonline (GenAI SDL scoping review), GitHub (streaks bot, habit tracker bot), Obsidian community (Private AI plugin), Reddit (ADHD workflow community, Obsidian second brain patterns), Voicepanel global AI usage study.*

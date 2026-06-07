---
title: Phase Alpha — Djinn Personal Layer Architecture
agent: Claude
date: 2026-06-01
tags: [djinn, architecture, phase-alpha, personal-layer]
---

# Phase Alpha — Djinn Personal Layer Architecture

**Status:** Approved by Javier — 2026-06-01
**Design authority:** Claude
**Build authority:** Salomon
**Research:** Marcus (TASK-053)

---

## What Phase Alpha Is

A clean, lean personal conciliary layer built from scratch. Not an extension of the manufacturing or media pipelines — its own system. It serves Javier's actualization across all personal domains: psychological, creative, health, relational, and academic.

Full vault read access granted. Financial layer excluded until explicitly opened.

---

## Design Constraints (from Marcus research)

1. **One thing at a time.** No briefing over 3 data points. One active task.
2. **Initiate from data, not schedule.** First Telegram message triggers briefing, not a fixed clock.
3. **The journal is sacred.** Never read Black Book uninvited. `/reflect` is Javier's key.
4. **Streaks as identity.** "Day 92 sober" — not a metric, a statement of who he is.
5. **No guilt architecture.** Missed days get neutral acknowledgment or silence.
6. **Local-first always.** Journal content never leaves the machine. Ollama processes it.
7. **One Telegram interface.** Everything lives in the existing gateway — no new apps.

---

## The Personal State Database

Single SQLite file: `~/.local/share/djinn/personal.db`

```sql
-- Core tables

CREATE TABLE habits (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,      -- 'writing', 'black_book', 'exercise', 'aa_meeting'
    frequency TEXT DEFAULT 'daily', -- 'daily' | 'weekly'
    active INTEGER DEFAULT 1
);

CREATE TABLE completions (
    id INTEGER PRIMARY KEY,
    habit_id INTEGER,
    completed_date TEXT NOT NULL,   -- ISO date YYYY-MM-DD
    note TEXT,
    UNIQUE(habit_id, completed_date)
);

CREATE TABLE streaks (
    habit_id INTEGER PRIMARY KEY,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_updated TEXT
);

CREATE TABLE sobriety (
    id INTEGER PRIMARY KEY,
    substance TEXT DEFAULT 'alcohol',
    start_date TEXT NOT NULL,       -- '2026-03-01'
    active INTEGER DEFAULT 1
);

CREATE TABLE people (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT,                      -- 'sponsor', 'partner', 'support'
    last_mentioned TEXT,            -- ISO date of last mention in Javier's messages
    archived INTEGER DEFAULT 0,
    archive_threshold_days INTEGER DEFAULT 14
);

CREATE TABLE deadlines (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    domain TEXT,                    -- 'academic', 'creative', 'work'
    due_date TEXT NOT NULL,
    completed INTEGER DEFAULT 0
);

CREATE TABLE black_book_log (
    id INTEGER PRIMARY KEY,
    entry_date TEXT UNIQUE NOT NULL -- ISO date — records that an entry EXISTS, never content
);
```

Seed data on install:
- sobriety: start_date = '2026-03-01', substance = 'alcohol'
- habits: writing (daily), black_book (daily), exercise (daily)
- people: Mira (partner, archive_threshold=14), Craig (sponsor, no archiving)

---

## Component 1: djinn-personal-db

**File:** `~/.local/bin/djinn-personal-db`
**Role:** Library + CLI for all personal state reads/writes

Commands:
```
djinn-personal-db habit done <name>          — mark habit complete today
djinn-personal-db habit check                — print all current streaks
djinn-personal-db sobriety                   — print current sobriety day count
djinn-personal-db deadline add <title> <date> <domain>
djinn-personal-db deadline check             — print deadlines in next 72 hours
djinn-personal-db people mention <name>      — update last_mentioned to today
djinn-personal-db people check               — list people + days since mention
djinn-personal-db blackbook log              — record that today's entry was written
djinn-personal-db briefing                   — print assembled morning briefing data (JSON)
```

Used by: djinn-morning, Telegram gateway handlers

---

## Component 2: djinn-morning Rewrite

**File:** `~/.local/bin/djinn-morning`
**Trigger:** systemd timer at 08:30 OR first Telegram message detection
**Output:** Telegram message + inline buttons

Format (hard cap: 90 words):
```
[Day N sober.]
[Writing: X day streak.] / [Write today — streak at X.]
[One thing: {single action item}]
[Context line if deadline approaching OR meeting today]

[✓ Writing] [✓ Black Book] [✓ Exercise] [Skip]
```

Logic:
1. `djinn-personal-db briefing` → JSON payload
2. Calculate sobriety day from 2026-03-01
3. Check Black Book log: did yesterday's entry get written?
4. Check deadlines: anything in 72h window?
5. Check AA schedule: meeting today?
6. Compose message using Javier's tone — direct, warm, not clinical
7. Send via Telegram with inline buttons that log habit completion on tap

Tone rules:
- Opens with sobriety day always — that's the identity anchor
- If yesterday's Black Book was missed: "The book waited for you. Still is."
- If writing streak active: acknowledge it, don't inflate it
- The "one thing" is the single most time-sensitive item (deadline > meeting > creative > general)

---

## Component 3: Telegram Gateway Personal Commands

Add to existing `djinn-telegram-gateway`:

```
/done [habit]        — mark habit complete: /done writing, /done blackbook, /done exercise
/sober               — print current sobriety day: "Day 92."
/check               — full streak status
/reflect             — load latest Black Book entry → local Ollama → one question back
/stuck               — Socratic question for academic work (one question, no answer)
/meeting             — next AA meeting info + Discord link
/craig [message]     — draft message to Craig (shows draft, asks confirm before sending)
/people              — check relationship context status
```

Inline button handlers (from morning briefing):
- `habit_done:writing` → `djinn-personal-db habit done writing`
- `habit_done:black_book` → `djinn-personal-db habit done black_book`
- `habit_done:exercise` → `djinn-personal-db habit done exercise`
- `habit_skip` → neutral acknowledgment, no log

---

## Component 4: AA Module

Hardcoded meeting schedule (update as needed):
```python
AA_MEETINGS = [
    {"day": "monday", "time": "19:00", "platform": "Discord", "server": "<server>"},
    # Add actual schedule when Javier provides it
]
```

Behaviors:
- Morning briefing includes "Meeting tonight at 7pm" if meeting is today
- `/meeting` command prints next meeting details
- `/craig [message]` drafts a message to Craig, shows preview, requires `/craig confirm` to send
  - Craig's contact method TBD — Telegram if he has it, otherwise SMS via Twilio (future)

---

## Component 5: Black Book Integration

**Vault path:** `~/Obsidian/personal/black-book/YYYY-MM-DD.md`
**Gitignore:** `personal/` — never syncs, never leaves the machine

`/reflect` flow:
1. Load `~/Obsidian/personal/black-book/{today}.md` or yesterday's if today not written yet
2. Strip PII (names → roles using simple lookup) for Ollama pass
3. Send to local Ollama (qwen2.5:7b or deepseek-r1:7b): "Ask ONE question about this entry. Do not interpret. Do not summarize. One question only."
4. Return question to Javier via Telegram
5. Log `djinn-personal-db blackbook log` to record entry exists

Djinn never opens this door. Javier always holds the key.

---

## Component 6: Mira Context Tracking

Passive listener in Telegram gateway:
- Scan each incoming message for: "Mira", "Mira", "she", "her" (context-aware)
- On match: `djinn-personal-db people mention Mira`
- Weekly check (Sunday morning): if `last_mentioned > 14 days` → flag in briefing with:
  "Mira hasn't come up in two weeks. Archiving her context for now — say her name to bring it back."
- Archive doesn't delete — moves to `people.archived = 1`. One mention restores her.

---

## Build Order — Phase Alpha

### Sprint 1 (Core loop — ship first)
- TASK-054: `djinn-personal-db` — SQLite schema + CLI helper
- TASK-055: `djinn-morning` rewrite — reads personal DB, generates conciliary briefing
- TASK-056 (partial): `/done`, `/check`, `/sober` Telegram commands + inline button handlers

### Sprint 2
- TASK-056 (complete): `/reflect`, `/stuck`, `/meeting`, `/craig`
- TASK-057: AA module — meeting schedule + Craig draft
- TASK-058: Black Book vault setup confirmed + gitignore verified

### Sprint 3
- TASK-059: Mira context tracking
- TASK-060: Pattern notice — weekly theme surfacing from Black Book (local only)

---

## What This Is Not

- Not a productivity app
- Not a mood tracker
- Not a wellness dashboard
- Not a corporate assistant

It is the strategic frame Javier asked for — the advisor who holds structure so he can focus on the work. Djinn runs the infrastructure of the day so Javier can live it.

---

*— Claude, 2026-06-01*

-- PHASE BETA MIGRATIONS
-- Run once against djinn-personal.db
-- Tasks: 075, 076, 077, 078, 079

-- TASK-075: Academic Deadline Engine
CREATE TABLE IF NOT EXISTS academic_deadlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course TEXT NOT NULL,
    task_type TEXT NOT NULL,   -- 'DQ1' | 'DQ2' | 'paper' | 'exam' | 'peer'
    due_date TEXT NOT NULL,    -- ISO: YYYY-MM-DD
    due_time TEXT DEFAULT '23:59',
    due_tz TEXT DEFAULT 'America/Phoenix',
    completed INTEGER DEFAULT 0,
    recurring INTEGER DEFAULT 0,      -- 1 = weekly recurring
    recur_day_of_week INTEGER,         -- 0=Mon … 6=Sun (NULL if not recurring)
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS lsat_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_date TEXT NOT NULL,
    section_type TEXT,         -- 'LR' | 'LG' | 'RC' | 'PT'
    section_id TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS lsat_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT NOT NULL,
    goal TEXT NOT NULL,
    completed INTEGER DEFAULT 0
);

-- TASK-076: Black Book — add entry_source column if absent
ALTER TABLE black_book_log ADD COLUMN entry_source TEXT DEFAULT 'manual';

-- TASK-077: Colitis Flare Flag
CREATE TABLE IF NOT EXISTS health_flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_date TEXT NOT NULL,   -- YYYY-MM-DD
    flag_type TEXT NOT NULL,   -- 'flare'
    auto_cleared INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS weight_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_date TEXT NOT NULL,
    weight_lbs REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

-- TASK-078: Recovery cluster
CREATE TABLE IF NOT EXISTS step_work (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    step_number INTEGER NOT NULL,
    status TEXT DEFAULT 'active',  -- 'active' | 'completed'
    started_date TEXT NOT NULL,
    completed_date TEXT,
    notes TEXT  -- local only, never cloud LLM
);

CREATE TABLE IF NOT EXISTS sponsor_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_date TEXT NOT NULL,
    brief_note TEXT
);

CREATE TABLE IF NOT EXISTS craving_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at TEXT DEFAULT (datetime('now')),
    severity INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 10),
    tag TEXT,
    sobriety_day INTEGER
);

CREATE TABLE IF NOT EXISTS meeting_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date TEXT NOT NULL,
    meeting_type TEXT DEFAULT 'AA',
    meeting_name TEXT,
    attended INTEGER NOT NULL,  -- 1 | 0
    notes TEXT
);

-- TASK-079: Aethoria + Gym
CREATE TABLE IF NOT EXISTS writing_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    scene_note TEXT,
    word_count INTEGER
);

CREATE TABLE IF NOT EXISTS writing_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start TEXT NOT NULL,
    goal TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS gym_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL
);

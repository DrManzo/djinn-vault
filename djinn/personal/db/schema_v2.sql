-- djinn-personal-db schema v2
-- Phase Beta tables — appended to existing schema
-- Run: sqlite3 ~/.local/share/djinn/personal.db < schema_v2.sql
-- Safe to re-run (all CREATE TABLE IF NOT EXISTS)

-- ─────────────────────────────────────────
-- TASK-075 Academic Deadline Engine
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS academic_deadlines (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    course           TEXT    NOT NULL,          -- e.g. "FIN-202"
    task_type        TEXT    NOT NULL,          -- "dq1" | "dq2" | "paper" | "exam" | "peer"
    task_label       TEXT    NOT NULL,          -- human label, e.g. "Week 3 DQ1"
    due_date         TEXT    NOT NULL,          -- ISO date YYYY-MM-DD
    due_time         TEXT    NOT NULL DEFAULT '23:59', -- HH:MM local
    due_tz           TEXT    NOT NULL DEFAULT 'America/Phoenix',
    completed        INTEGER NOT NULL DEFAULT 0, -- 0 | 1
    completed_at     TEXT,
    recurring        INTEGER NOT NULL DEFAULT 0, -- 0 | 1
    recur_day_of_week INTEGER,                  -- 0=Mon..6=Sun, NULL if not recurring
    course_start     TEXT,                      -- YYYY-MM-DD (8-week block start)
    course_end       TEXT,                      -- YYYY-MM-DD (8-week block end)
    notes            TEXT    DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_deadlines_due ON academic_deadlines(due_date, completed);

-- ─────────────────────────────────────────
-- TASK-075 LSAT Prep Log
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lsat_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_date  TEXT    NOT NULL,  -- YYYY-MM-DD
    section_type TEXT    NOT NULL,  -- "lr" | "lg" | "rc" | "pt" | "review"
    section_id   TEXT,              -- e.g. "PT-92-S1"
    notes        TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS lsat_milestones (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start   TEXT    NOT NULL UNIQUE, -- YYYY-MM-DD Monday
    goal         TEXT    NOT NULL,
    completed    INTEGER NOT NULL DEFAULT 0
);

-- ─────────────────────────────────────────
-- TASK-077 Colitis Flare Flag
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS health_flags (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_date    TEXT    NOT NULL,  -- YYYY-MM-DD
    flag_type    TEXT    NOT NULL,  -- "flare" | "low_capacity"
    auto_cleared INTEGER NOT NULL DEFAULT 1,  -- clears at midnight
    cleared_at   TEXT,
    notes        TEXT    DEFAULT ''
);

CREATE TABLE IF NOT EXISTS weight_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_date TEXT NOT NULL,  -- YYYY-MM-DD
    weight_lbs  REAL NOT NULL
);

-- ─────────────────────────────────────────
-- TASK-078 Recovery Cluster
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS step_work (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    step_number    INTEGER NOT NULL,  -- 1–12
    status         TEXT    NOT NULL DEFAULT 'active', -- "active" | "complete" | "paused"
    started_date   TEXT    NOT NULL,  -- YYYY-MM-DD
    completed_date TEXT,
    notes          TEXT    DEFAULT ''  -- Ollama-only, never cloud
);

CREATE TABLE IF NOT EXISTS sponsor_contacts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_date TEXT NOT NULL,  -- YYYY-MM-DD
    contact_time TEXT,           -- HH:MM optional
    brief_note   TEXT DEFAULT '' -- local only
);

CREATE TABLE IF NOT EXISTS craving_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    logged_at    TEXT NOT NULL,  -- ISO 8601 with tz
    severity     INTEGER NOT NULL CHECK(severity BETWEEN 1 AND 10),
    tag          TEXT DEFAULT '',  -- free tag e.g. "work-stress", "evening"
    sobriety_day INTEGER           -- denormalized for fast queries
);

CREATE INDEX IF NOT EXISTS idx_craving_date ON craving_log(logged_at);

CREATE TABLE IF NOT EXISTS meeting_attendance (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date  TEXT NOT NULL,   -- YYYY-MM-DD
    meeting_type  TEXT DEFAULT 'aa',
    meeting_name  TEXT DEFAULT '',
    attended      INTEGER NOT NULL DEFAULT 1, -- 1=attended, 0=missed
    notes         TEXT DEFAULT ''
);

-- ─────────────────────────────────────────
-- TASK-079 Aethoria + Gym
-- ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS writing_sessions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date     TEXT    NOT NULL,  -- YYYY-MM-DD
    duration_minutes INTEGER NOT NULL,
    scene_note       TEXT    DEFAULT '',
    word_count       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS aethoria_goals (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start   TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD Monday
    goal         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gym_sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date TEXT NOT NULL  -- YYYY-MM-DD
);

-- ─────────────────────────────────────────
-- TASK-076 Black Book: add entry_source column
-- (black_book_log already exists in v1 schema)
-- ─────────────────────────────────────────
-- Run only if column does not exist:
-- ALTER TABLE black_book_log ADD COLUMN entry_source TEXT DEFAULT 'manual';
-- Wrapped below as a no-op-safe migration:

CREATE TABLE IF NOT EXISTS _migration_log (
    migration TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL
);

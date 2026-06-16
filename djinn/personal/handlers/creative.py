"""
TASK-079 — Aethoria Writing Log + Gym Log
Handles: /write, /aethoria, /aethoria-goal, /gym
Briefing: Aethoria line surfaces only when no session today AND no CRITICAL deadline.
Gym: logs once, monthly count only, zero daily nagging.
"""
import sqlite3
from datetime import date, timedelta

DB_PATH = "djinn-personal.db"


def _conn():
    return sqlite3.connect(DB_PATH)


# ── Writing streak helpers ─────────────────────────────────────────────────

def _wrote_today() -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM writing_sessions WHERE session_date = date('now') LIMIT 1"
    )
    result = cur.fetchone()
    conn.close()
    return result is not None


def _writing_streak() -> int:
    """Count consecutive days with at least one session, ending today."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT DISTINCT session_date FROM writing_sessions ORDER BY session_date DESC"
    )
    rows = [date.fromisoformat(r[0]) for r in cur.fetchall()]
    conn.close()

    if not rows:
        return 0

    streak = 0
    expected = date.today()
    for d in rows:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def _sessions_this_week() -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM writing_sessions WHERE session_date >= date('now', '-6 days')"
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def _days_since_last_session() -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(session_date) FROM writing_sessions"
    )
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return 9999
    last = date.fromisoformat(row[0])
    return (date.today() - last).days


# ── Command handlers ───────────────────────────────────────────────────────

def cmd_write(args: list[str]) -> str:
    if not args:
        return "Usage: /write [minutes] [optional scene note]"

    try:
        minutes = int(args[0])
    except ValueError:
        return "Usage: /write [minutes] [optional scene note]"

    scene_note = " ".join(args[1:]) if len(args) > 1 else None

    conn = _conn()
    conn.execute(
        """INSERT INTO writing_sessions (session_date, duration_minutes, scene_note)
           VALUES (date('now'), ?, ?)""",
        (minutes, scene_note)
    )
    conn.commit()
    conn.close()

    streak = _writing_streak()
    week = _sessions_this_week()
    return f"✍️ {minutes} min logged. Streak: {streak} days. Week: {week} sessions."


def cmd_aethoria(args: list[str]) -> str:
    if not args:
        streak = _writing_streak()
        week = _sessions_this_week()
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT goal FROM writing_goals ORDER BY created_at DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        goal = row[0] if row else "No weekly goal set. Use /aethoria-goal [text]"
        return f"✍️ Aethoria\nStreak: {streak} days | This week: {week} sessions\nGoal: {goal}"

    return "Usage: /aethoria | /aethoria-goal [text] (use separate command)"


def cmd_aethoria_goal(text: str) -> str:
    if not text.strip():
        return "Usage: /aethoria-goal [your weekly writing goal]"
    conn = _conn()
    conn.execute(
        "INSERT INTO writing_goals (week_start, goal) VALUES (date('now','weekday 0'), ?)",
        (text.strip(),)
    )
    conn.commit()
    conn.close()
    return f"✅ Aethoria goal set: {text.strip()}"


# ── Gym ────────────────────────────────────────────────────────────────────

def _gym_count_this_month() -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM gym_sessions WHERE strftime('%Y-%m', session_date) = strftime('%Y-%m', 'now')"
    )
    count = cur.fetchone()[0]
    conn.close()
    return count


def cmd_gym() -> str:
    today = date.today().isoformat()
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM gym_sessions WHERE session_date = ?", (today,))
    if cur.fetchone():
        conn.close()
        return "💪 Already logged today."
    conn.execute("INSERT INTO gym_sessions (session_date) VALUES (?)", (today,))
    conn.commit()
    conn.close()
    count = _gym_count_this_month()
    return f"💪 Logged. Month: {count}/3."


# ── Briefing helpers ───────────────────────────────────────────────────────

def get_aethoria_brief_line(has_critical_deadline: bool, is_flare: bool) -> str | None:
    """
    Returns Aethoria line for morning brief, or None if suppressed.
    Suppressed when: flare day, session already logged, or CRITICAL deadline active.
    After 3+ missed days: single-line fact (no guilt).
    """
    if is_flare:
        return None
    if _wrote_today():
        return None
    if has_critical_deadline:
        return None

    days_dark = _days_since_last_session()
    streak = _writing_streak()

    if days_dark >= 3:
        return f"✍️ Aethoria dark — {days_dark} days. Just open the doc."
    if streak > 0:
        return f"✍️ Aethoria streak: {streak} days. Write today?"
    return "✍️ Aethoria — no session yet today."

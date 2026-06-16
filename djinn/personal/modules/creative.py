"""
TASK-079 — Aethoria Writing + Gym Logging

Public API:
  log_writing_session(minutes, scene_note, word_count) -> str
  writing_streak()                                     -> int
  get_aethoria_status()                                -> str   (/aethoria)
  set_aethoria_goal(goal)                              -> str   (/aethoria-goal)
  aethoria_briefing_line()                             -> str | None

  log_gym()                                            -> str   (/gym)
  gym_month_count()                                    -> int
"""

from datetime import date, timedelta
from .db import get_conn


# ── Writing ──────────────────────────────────────────────────────────

def log_writing_session(
    minutes: int,
    scene_note: str = "",
    word_count: int = 0,
) -> str:
    today = date.today().isoformat()
    conn = get_conn()

    # Avoid duplicate same-day session? No — allow multiple per day, sum them.
    conn.execute(
        "INSERT INTO writing_sessions(session_date, duration_minutes, scene_note, word_count) VALUES (?,?,?,?)",
        (today, minutes, scene_note.strip(), word_count),
    )
    conn.commit()
    
    streak = _calc_writing_streak(conn)
    week_total = conn.execute(
        "SELECT COALESCE(SUM(duration_minutes),0) FROM writing_sessions WHERE session_date >= date('now','weekday 1','-7 days')"
    ).fetchone()[0]
    conn.close()

    return (
        f"✍️ {minutes} min logged. "
        f"Streak: {streak} day{'s' if streak != 1 else ''}. "
        f"Week: {week_total}min."
    )


def _calc_writing_streak(conn) -> int:
    """Consecutive days with at least one writing session, counting back from today."""
    rows = conn.execute(
        """
        SELECT DISTINCT session_date FROM writing_sessions
        ORDER BY session_date DESC
        LIMIT 60
        """
    ).fetchall()
    dates = [date.fromisoformat(r[0]) for r in rows]
    if not dates:
        return 0

    today = date.today()
    streak = 0
    check = today
    date_set = set(dates)

    while check in date_set:
        streak += 1
        check -= timedelta(days=1)

    return streak


def writing_streak() -> int:
    conn = get_conn()
    s = _calc_writing_streak(conn)
    conn.close()
    return s


def set_aethoria_goal(goal: str) -> str:
    today = date.today()
    monday = (today - timedelta(days=today.weekday())).isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO aethoria_goals(week_start, goal) VALUES (?,?)",
        (monday, goal),
    )
    conn.commit()
    conn.close()
    return f"✍️ Aethoria week goal: {goal}"


def get_aethoria_status() -> str:
    today = date.today()
    monday = (today - timedelta(days=today.weekday())).isoformat()
    conn = get_conn()

    streak = _calc_writing_streak(conn)
    week_sessions = conn.execute(
        "SELECT COUNT(*) FROM writing_sessions WHERE session_date >= ?",
        (monday,),
    ).fetchone()[0]
    week_minutes = conn.execute(
        "SELECT COALESCE(SUM(duration_minutes),0) FROM writing_sessions WHERE session_date >= ?",
        (monday,),
    ).fetchone()[0]
    goal_row = conn.execute(
        "SELECT goal FROM aethoria_goals WHERE week_start=?", (monday,)
    ).fetchone()
    conn.close()

    goal_text = goal_row["goal"] if goal_row else "(no goal set — /aethoria-goal)"
    return (
        f"✍️ *Aethoria:*\n"
        f"Streak: {streak} day{'s' if streak != 1 else ''}\n"
        f"Week: {week_sessions} sessions / {week_minutes}min\n"
        f"Goal: {goal_text}"
    )


def aethoria_briefing_line() -> str | None:
    """
    Returns a brief line for the morning brief ONLY if:
    - No session logged today, AND
    - No CRITICAL academic deadline today (caller is responsible for the second check)
    """
    today = date.today().isoformat()
    conn = get_conn()
    session_today = conn.execute(
        "SELECT COUNT(*) FROM writing_sessions WHERE session_date=?", (today,)
    ).fetchone()[0]
    streak = _calc_writing_streak(conn)
    conn.close()

    if session_today > 0:
        return None  # Already wrote today — don't surface it

    if streak == 0:
        return "✍️ Aethoria: 0-day streak. Just open the doc."
    if streak >= 3:
        dark_msg = f"\n✍️ Aethoria dark — {streak} days missed. Just open the doc."
        # streak counts today as already broken
        # if session_today==0 and streak from yesterday
        return f"✍️ Aethoria: {streak}-day streak. Keep it going — 30 min."

    return f"✍️ Aethoria: {streak}-day streak. 30 min today."


def _days_since_last_write() -> int:
    conn = get_conn()
    last = conn.execute(
        "SELECT session_date FROM writing_sessions ORDER BY session_date DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not last:
        return 999
    return (date.today() - date.fromisoformat(last["session_date"])).days


# ── Gym ──────────────────────────────────────────────────────────────

def log_gym() -> str:
    today = date.today().isoformat()
    conn = get_conn()
    # Prevent duplicate same-day gym log
    existing = conn.execute(
        "SELECT id FROM gym_sessions WHERE session_date=?", (today,)
    ).fetchone()
    if existing:
        conn.close()
        return "💪 Already logged gym for today."
    conn.execute("INSERT INTO gym_sessions(session_date) VALUES (?)", (today,))
    conn.commit()
    month_start = date.today().replace(day=1).isoformat()
    count = conn.execute(
        "SELECT COUNT(*) FROM gym_sessions WHERE session_date >= ?", (month_start,)
    ).fetchone()[0]
    conn.close()
    return f"💪 Logged. Month: {count}/3."


def gym_month_count() -> int:
    month_start = date.today().replace(day=1).isoformat()
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM gym_sessions WHERE session_date >= ?", (month_start,)
    ).fetchone()[0]
    conn.close()
    return count

"""
TASK-075 — Academic Deadline Engine
Handles: /school, /deadline, /lsat
All times normalized to America/Phoenix (GCU LMS timezone).
"""
import sqlite3
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

DB_PATH = "djinn-personal.db"
GCU_TZ = ZoneInfo("America/Phoenix")


def _conn():
    return sqlite3.connect(DB_PATH)


def _days_until(due_date_str: str) -> int:
    today = date.today()
    due = date.fromisoformat(due_date_str)
    return (due - today).days


def priority_label(days: int) -> str:
    if days <= 1:
        return "CRITICAL"
    if days <= 3:
        return "ELEVATED"
    return "BACKGROUND"


# ── Seeding recurring GCU tasks ────────────────────────────────────────────

GCU_WEEKLY_PATTERN = [
    {"task_type": "DQ1",  "recur_day_of_week": 2, "due_time": "23:59"},  # Wed
    {"task_type": "DQ2",  "recur_day_of_week": 4, "due_time": "23:59"},  # Fri
    {"task_type": "paper","recur_day_of_week": 6, "due_time": "23:59"},  # Sun
    {"task_type": "peer", "recur_day_of_week": 6, "due_time": "23:59"},  # Sun
]


def seed_gcu_course(course: str, start_date: str, end_date: str):
    """
    Seed 8 weeks of recurring deadlines for a GCU course.
    course:     e.g. 'FIN-202'
    start_date: Monday of week 1 (YYYY-MM-DD)
    end_date:   Sunday of week 8 (YYYY-MM-DD)
    """
    conn = _conn()
    cur = conn.cursor()
    current = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    inserted = 0

    while current <= end:
        for pattern in GCU_WEEKLY_PATTERN:
            days_ahead = (pattern["recur_day_of_week"] - current.weekday()) % 7
            due = current + timedelta(days=days_ahead)
            if due > end:
                continue
            cur.execute(
                """INSERT OR IGNORE INTO academic_deadlines
                   (course, task_type, due_date, due_time, due_tz, recurring, recur_day_of_week)
                   VALUES (?,?,?,?,?,1,?)""",
                (course, pattern["task_type"], due.isoformat(),
                 pattern["due_time"], "America/Phoenix",
                 pattern["recur_day_of_week"])
            )
            inserted += 1
        current += timedelta(weeks=1)

    conn.commit()
    conn.close()
    return f"Seeded {inserted} deadlines for {course}."


# ── Briefing query ─────────────────────────────────────────────────────────

def get_briefing_item() -> str | None:
    """
    Return single highest-urgency academic line for morning brief.
    Returns None if nothing CRITICAL or ELEVATED.
    """
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT course, task_type, due_date
           FROM academic_deadlines
           WHERE completed = 0
           ORDER BY due_date ASC
           LIMIT 10"""
    )
    rows = cur.fetchall()
    conn.close()

    for course, task_type, due_date in rows:
        days = _days_until(due_date)
        label = priority_label(days)
        if label == "BACKGROUND":
            continue
        day_word = "today" if days == 0 else ("tomorrow" if days == 1 else f"{days}d")
        return f"📚 {course} — {task_type} due {day_word}. ⏳"
    return None


# ── Command handlers ───────────────────────────────────────────────────────

def cmd_school() -> str:
    """Full weekly academic view."""
    conn = _conn()
    cur = conn.cursor()
    today = date.today()
    week_end = today + timedelta(days=7)
    cur.execute(
        """SELECT course, task_type, due_date, completed
           FROM academic_deadlines
           WHERE due_date BETWEEN ? AND ?
           ORDER BY due_date ASC""",
        (today.isoformat(), week_end.isoformat())
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "📚 No deadlines in the next 7 days."

    lines = ["📚 Next 7 days:\n"]
    for course, task_type, due_date, completed in rows:
        days = _days_until(due_date)
        status = "✅" if completed else ("🔴" if days <= 1 else "⏳")
        lines.append(f"  {status} {course} — {task_type} ({due_date})")
    return "\n".join(lines)


def cmd_deadline_add(course: str, task_type: str, due_date: str, due_time: str = "23:59") -> str:
    conn = _conn()
    conn.execute(
        """INSERT INTO academic_deadlines (course, task_type, due_date, due_time)
           VALUES (?,?,?,?)""",
        (course.upper(), task_type, due_date, due_time)
    )
    conn.commit()
    conn.close()
    return f"✅ Deadline added: {course.upper()} — {task_type} due {due_date}."


def cmd_deadline_done(course: str, task_type: str) -> str:
    conn = _conn()
    today = date.today().isoformat()
    conn.execute(
        """UPDATE academic_deadlines SET completed = 1
           WHERE course = ? AND task_type = ? AND due_date >= ? AND completed = 0""",
        (course.upper(), task_type, today)
    )
    conn.commit()
    conn.close()
    return f"✅ Marked {course.upper()} {task_type} as done."


def cmd_lsat(args: list[str]) -> str:
    conn = _conn()
    if not args:
        # status
        cur = conn.cursor()
        cur.execute(
            "SELECT goal FROM lsat_milestones WHERE completed=0 ORDER BY week_start DESC LIMIT 1"
        )
        row = cur.fetchone()
        cur.execute(
            "SELECT COUNT(*) FROM lsat_log WHERE logged_date >= date('now','-7 days')"
        )
        count = cur.fetchone()[0]
        conn.close()
        goal = row[0] if row else "No milestone set. Use /lsat goal [text]"
        return f"📖 LSAT\nThis week: {count} sessions\nMilestone: {goal}"

    sub = args[0].lower()

    if sub == "done":
        section = args[1] if len(args) > 1 else "general"
        conn.execute(
            "INSERT INTO lsat_log (logged_date, section_type) VALUES (date('now'), ?)",
            (section.upper(),)
        )
        conn.commit()
        conn.close()
        return f"✅ LSAT session logged: {section.upper()}."

    if sub == "goal":
        goal_text = " ".join(args[1:])
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()
        conn.execute(
            "INSERT INTO lsat_milestones (week_start, goal) VALUES (?,?)",
            (week_start, goal_text)
        )
        conn.commit()
        conn.close()
        return f"✅ LSAT milestone set: {goal_text}"

    conn.close()
    return "Usage: /lsat | /lsat done [section] | /lsat goal [text]"

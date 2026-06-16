"""
TASK-075 — Academic Deadline Engine

Public API:
  get_briefing_item()     -> str | None   (highest-priority item for morning brief)
  get_weekly_view()       -> str           (/school full view)
  add_deadline(...)       -> str           (confirmation message)
  seed_gcu_week(course, week_num, start_date, course_start, course_end) -> str
  complete_deadline(id)   -> str
  get_lsat_status()       -> str
  log_lsat_session(section_type, section_id, notes) -> str
  set_lsat_goal(goal)     -> str
"""

from datetime import date, timedelta
from .db import get_conn


# ── Priority classification ──────────────────────────────────────────

def _classify(days_until: int) -> str:
    if days_until <= 0:
        return "OVERDUE"
    if days_until <= 1:
        return "CRITICAL"
    if days_until <= 3:
        return "ELEVATED"
    return "BACKGROUND"


def _days_until(due_date_str: str) -> int:
    try:
        due = date.fromisoformat(due_date_str)
        return (due - date.today()).days
    except ValueError:
        return 999


# ── Briefing item (one line max) ─────────────────────────────────────

def get_briefing_item() -> str | None:
    """Return the single most urgent uncompleted deadline string, or None."""
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, course, task_label, due_date
        FROM academic_deadlines
        WHERE completed = 0
        ORDER BY due_date ASC
        LIMIT 10
        """
    ).fetchall()
    conn.close()

    if not rows:
        return None

    for row in rows:
        days = _days_until(row["due_date"])
        level = _classify(days)
        if level in ("OVERDUE", "CRITICAL", "ELEVATED"):
            label = {
                "OVERDUE":  "⚠️ OVERDUE",
                "CRITICAL": "🔴 Due today",
                "ELEVATED": f"📅 Due in {days}d",
            }[level]
            return f"📚 {row['course']} — {row['task_label']} — {label}"

    # Nothing urgent — show nearest upcoming
    row = rows[0]
    days = _days_until(row["due_date"])
    return f"📚 {row['course']} — {row['task_label']} — {days}d out"


# ── /school weekly view ──────────────────────────────────────────────

def get_weekly_view() -> str:
    conn = get_conn()
    today = date.today()
    week_end = today + timedelta(days=7)
    rows = conn.execute(
        """
        SELECT course, task_label, due_date, completed
        FROM academic_deadlines
        WHERE due_date >= ? AND due_date <= ?
        ORDER BY due_date ASC
        """,
        (today.isoformat(), week_end.isoformat()),
    ).fetchall()
    conn.close()

    if not rows:
        return "📚 Nothing due this week. Enjoy the silence."

    lines = ["📚 *Next 7 days:*"]
    for row in rows:
        days = _days_until(row["due_date"])
        tick = "✅" if row["completed"] else "⏳"
        label = _classify(days)
        suffix = {"OVERDUE": " ⚠️OVERDUE", "CRITICAL": " 🔴TODAY", "ELEVATED": f" ({days}d)", "BACKGROUND": f" ({days}d)"}.get(label, "")
        lines.append(f"{tick} {row['course']} — {row['task_label']}{suffix}")
    return "\n".join(lines)


# ── /deadline add ────────────────────────────────────────────────────

def add_deadline(
    course: str,
    task_label: str,
    due_date: str,
    task_type: str = "assignment",
    due_time: str = "23:59",
    due_tz: str = "America/Phoenix",
) -> str:
    conn = get_conn()
    conn.execute(
        """
        INSERT INTO academic_deadlines
            (course, task_type, task_label, due_date, due_time, due_tz)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (course.upper(), task_type, task_label, due_date, due_time, due_tz),
    )
    conn.commit()
    conn.close()
    days = _days_until(due_date)
    return f"✅ Added: {course.upper()} — {task_label} — due {due_date} ({days}d)"


def complete_deadline(deadline_id: int) -> str:
    from datetime import datetime, timezone
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "UPDATE academic_deadlines SET completed=1, completed_at=? WHERE id=?",
        (now, deadline_id),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return f"❌ Deadline #{deadline_id} not found."
    return f"✅ Deadline #{deadline_id} marked complete."


# ── GCU weekly seed helper ───────────────────────────────────────────

def seed_gcu_week(
    course: str,
    week_num: int,
    week_monday: str,   # YYYY-MM-DD
    course_start: str,
    course_end: str,
) -> str:
    """
    Seeds the standard GCU week pattern for one course week:
    - DQ1 due Wednesday 23:59 AZT
    - DQ2 due Friday 23:59 AZT
    - Week assignments due Sunday 23:59 AZT
    """
    monday = date.fromisoformat(week_monday)
    tasks = [
        ("dq1",        f"Week {week_num} DQ1",        monday + timedelta(days=2)),  # Wed
        ("dq2",        f"Week {week_num} DQ2",        monday + timedelta(days=4)),  # Fri
        ("assignment", f"Week {week_num} Assignments", monday + timedelta(days=6)),  # Sun
    ]
    conn = get_conn()
    added = 0
    for task_type, label, due in tasks:
        conn.execute(
            """
            INSERT INTO academic_deadlines
                (course, task_type, task_label, due_date, due_time, due_tz,
                 recurring, course_start, course_end)
            VALUES (?, ?, ?, ?, '23:59', 'America/Phoenix', 1, ?, ?)
            """,
            (course.upper(), task_type, label, due.isoformat(), course_start, course_end),
        )
        added += 1
    conn.commit()
    conn.close()
    return f"✅ Seeded {added} tasks for {course.upper()} Week {week_num} (Mon {week_monday})"


# ── LSAT ─────────────────────────────────────────────────────────────

def log_lsat_session(section_type: str, section_id: str = "", notes: str = "") -> str:
    from datetime import datetime
    today = date.today().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO lsat_log(logged_date, section_type, section_id, notes) VALUES (?,?,?,?)",
        (today, section_type.lower(), section_id, notes),
    )
    conn.commit()
    count = conn.execute(
        "SELECT COUNT(*) FROM lsat_log WHERE logged_date >= date('now', 'start of month')"
    ).fetchone()[0]
    conn.close()
    return f"✅ LSAT session logged ({section_type.upper()}). Month: {count} sessions."


def set_lsat_goal(goal: str) -> str:
    today = date.today()
    # Get Monday of current week
    monday = (today - timedelta(days=today.weekday())).isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO lsat_milestones(week_start, goal) VALUES (?, ?)",
        (monday, goal),
    )
    conn.commit()
    conn.close()
    return f"✅ LSAT week goal set: {goal}"


def get_lsat_status() -> str:
    today = date.today()
    monday = (today - timedelta(days=today.weekday())).isoformat()
    conn = get_conn()
    goal_row = conn.execute(
        "SELECT goal, completed FROM lsat_milestones WHERE week_start=?", (monday,)
    ).fetchone()
    sessions_this_week = conn.execute(
        "SELECT COUNT(*) FROM lsat_log WHERE logged_date >= ?", (monday,)
    ).fetchone()[0]
    conn.close()

    goal_text = goal_row["goal"] if goal_row else "(no goal set — use /lsat goal)"
    tick = "✅" if (goal_row and goal_row["completed"]) else "⏳"
    return (
        f"📖 *LSAT this week:*\n"
        f"{tick} Goal: {goal_text}\n"
        f"Sessions logged: {sessions_this_week}"
    )

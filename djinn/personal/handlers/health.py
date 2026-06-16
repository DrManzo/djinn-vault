"""
TASK-077 — Colitis Flare Flag
Handles: /flare, /flare clear, /weight
Flare day: suppresses action item in morning brief, pauses all streaks.
Auto-clears at midnight via scheduler or next-day check.
"""
import sqlite3
from datetime import date

DB_PATH = "djinn-personal.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def is_flare_day(check_date: str | None = None) -> bool:
    """Returns True if today (or check_date) has an active flare flag."""
    d = check_date or date.today().isoformat()
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM health_flags WHERE flag_date = ? AND flag_type = 'flare'",
        (d,)
    )
    result = cur.fetchone()
    conn.close()
    return result is not None


def cmd_flare(args: list[str]) -> str:
    today = date.today().isoformat()

    if args and args[0].lower() == "clear":
        conn = _conn()
        conn.execute(
            "DELETE FROM health_flags WHERE flag_date = ? AND flag_type = 'flare'",
            (today,)
        )
        conn.commit()
        conn.close()
        return "🟢 Flare flag cleared. Streaks resume."

    if is_flare_day():
        return "🔴 Flare already active today. Send /flare clear when you're through it."

    conn = _conn()
    conn.execute(
        "INSERT INTO health_flags (flag_date, flag_type, auto_cleared) VALUES (?, 'flare', 1)",
        (today,)
    )
    conn.commit()
    conn.close()
    return "🔴 Flare day logged. System in quiet mode. Streaks paused."


def cmd_weight(args: list[str]) -> str:
    if not args:
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT logged_date, weight_lbs FROM weight_log ORDER BY logged_date DESC LIMIT 5"
        )
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "No weight entries yet. Use /weight [lbs]"
        lines = [f"  {d}: {w} lbs" for d, w in rows]
        return "⚖️ Recent weights:\n" + "\n".join(lines)

    try:
        lbs = float(args[0])
    except ValueError:
        return "Usage: /weight [number]"

    conn = _conn()
    conn.execute(
        "INSERT INTO weight_log (logged_date, weight_lbs) VALUES (date('now'), ?)",
        (lbs,)
    )
    conn.commit()
    conn.close()
    return f"⚖️ Logged {lbs} lbs."

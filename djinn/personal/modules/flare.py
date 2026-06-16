"""
TASK-077 — Colitis Flare Flag

Public API:
  set_flare()           -> str   (/flare)
  clear_flare()         -> str   (/flare clear)
  is_flare_day()        -> bool  (checked by morning brief composer)
  log_weight(lbs)       -> str   (/weight)
  get_health_summary()  -> str   (/health)

Flare days:
  - All habit streaks pause (no streak break)
  - Morning brief suppresses action item
  - Auto-clears at midnight (cron or first morning brief call)
"""

from datetime import date, datetime, timezone
from .db import get_conn


def set_flare(notes: str = "") -> str:
    today = date.today().isoformat()
    conn = get_conn()
    existing = conn.execute(
        "SELECT id FROM health_flags WHERE flag_date=? AND flag_type='flare'",
        (today,),
    ).fetchone()
    if existing:
        conn.close()
        return "🔴 Flare already flagged for today. Rest up."
    conn.execute(
        "INSERT INTO health_flags(flag_date, flag_type, auto_cleared, notes) VALUES (?,?,1,?)",
        (today, "flare", notes),
    )
    conn.commit()
    conn.close()
    return "🔴 Flare day flagged. System in quiet mode. All streaks paused for today."


def clear_flare() -> str:
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    cur = conn.execute(
        "UPDATE health_flags SET cleared_at=? WHERE flag_date=? AND flag_type='flare' AND cleared_at IS NULL",
        (now, today),
    )
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        return "No active flare flag today."
    return "✅ Flare cleared. Streaks resume from tomorrow."


def is_flare_day() -> bool:
    today = date.today().isoformat()
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM health_flags WHERE flag_date=? AND flag_type='flare' AND cleared_at IS NULL",
        (today,),
    ).fetchone()
    conn.close()
    return row is not None


def auto_clear_yesterday() -> None:
    """Call at start of each day (cron/morning brief boot) to clear stale flags."""
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat()
    conn = get_conn()
    conn.execute(
        "UPDATE health_flags SET cleared_at=? WHERE flag_date < ? AND cleared_at IS NULL AND auto_cleared=1",
        (now, today),
    )
    conn.commit()
    conn.close()


def log_weight(lbs: float) -> str:
    today = date.today().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO weight_log(logged_date, weight_lbs) VALUES (?,?)",
        (today, lbs),
    )
    conn.commit()
    conn.close()
    return f"⚖️ {lbs} lbs logged."


def get_health_summary() -> str:
    conn = get_conn()
    latest_weight = conn.execute(
        "SELECT weight_lbs, logged_date FROM weight_log ORDER BY logged_date DESC LIMIT 1"
    ).fetchone()
    flare_count_30 = conn.execute(
        "SELECT COUNT(*) FROM health_flags WHERE flag_date >= date('now','-30 days') AND flag_type='flare'"
    ).fetchone()[0]
    conn.close()

    lines = ["🏥 *Health summary:*"]
    if latest_weight:
        lines.append(f"⚖️ Last weight: {latest_weight['weight_lbs']} lbs ({latest_weight['logged_date']})")
    lines.append(f"🔴 Flare days (30d): {flare_count_30}")
    return "\n".join(lines)

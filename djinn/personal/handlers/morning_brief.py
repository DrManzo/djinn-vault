"""
Revised Morning Brief — Phase Beta
Assembles the daily 08:30 Telegram message.
Hard cap: 90 words. One action item. No guilt architecture.
Flare days: quiet mode only.
"""
from .academic import get_briefing_item, priority_label, _days_until
from .health import is_flare_day
from .creative import get_aethoria_brief_line
from .recovery import get_meeting_brief_nudge
import sqlite3
from datetime import date

DB_PATH = "djinn-personal.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def _sobriety_day() -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM habits WHERE name = 'sobriety_start' LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0
    return (date.today() - date.fromisoformat(row[0])).days


def _milestone_emoji(day: int) -> str:
    milestones = {30, 60, 90, 180, 270, 365}
    for m in sorted(milestones):
        if day < m <= day + 7:
            return f" ({m - day}d to {m})"
    return ""


def _has_critical_deadline() -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT due_date FROM academic_deadlines WHERE completed=0 ORDER BY due_date ASC LIMIT 5"
    )
    rows = cur.fetchall()
    conn.close()
    for (due_date,) in rows:
        if priority_label(_days_until(due_date)) == "CRITICAL":
            return True
    return False


def build_morning_brief() -> str:
    day_n = _sobriety_day()
    flare = is_flare_day()

    # ── Flare mode ──────────────────────────────────────────────────────────
    if flare:
        academic = get_briefing_item()
        lines = [f"🌅 Day {day_n} sober.", "Rest day — system in quiet mode."]
        if academic and "CRITICAL" in (academic or ""):
            lines.append(academic)
        return "\n".join(lines)

    # ── Normal mode ─────────────────────────────────────────────────────────
    milestone_note = _milestone_emoji(day_n)
    lines = [f"🌅 Day {day_n} sober{milestone_note}"]

    # Academic — highest urgency only
    academic = get_briefing_item()
    if academic:
        lines.append(academic)

    # Aethoria — conditional
    has_critical = _has_critical_deadline()
    aethoria = get_aethoria_brief_line(has_critical_deadline=has_critical, is_flare=False)
    if aethoria:
        lines.append(aethoria)

    # Meeting nudge — quiet, appears only if 5+ days since last
    nudge = get_meeting_brief_nudge()
    if nudge:
        lines.append(nudge)

    # Action item: derived from highest priority open item
    if academic:
        action = f"🎯 {academic.replace('📚 ', '').strip()}"
    elif aethoria:
        action = "🎯 Open Aethoria. 30 min."
    else:
        action = "🎯 One thing forward today."

    lines.append(action)

    # Inline buttons hint (Telegram bot renders these via reply_markup)
    lines.append("[✅ Done | 📓 Log | 💪 Gym | 🔴 Flare]")

    brief = "\n".join(lines)

    # Hard cap enforcement — trim action line if over 90 words
    if len(brief.split()) > 90:
        lines = lines[:-2]  # drop buttons + action, re-add compact
        lines.append(action)
        brief = "\n".join(lines)

    return brief

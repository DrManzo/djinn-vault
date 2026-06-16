"""
TASK-075–079 — Morning Brief Composer (Phase Beta)

Builds the morning Telegram message.
Called by djinn-morning at 08:30 daily.
Constraints:
  - Max 90 words
  - One action item
  - ADHD-safe: no guilt, no walls of text
  - Flare day: quiet mode, no action item

Public API:
  compose_brief() -> str
"""

from datetime import date
from .flare import is_flare_day, auto_clear_yesterday
from .deadlines import get_briefing_item as get_deadline_item
from .creative import aethoria_briefing_line
from .recovery import meeting_brief_nudge
from .db import get_conn


def _get_sobriety_line() -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT start_date FROM sobriety_log ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        return "🌅 Sober."
    start = date.fromisoformat(row["start_date"])
    days = (date.today() - start).days + 1
    
    milestones = {30, 60, 90, 100, 180, 365}
    near = any(days == m - 1 for m in milestones)  # day before milestone
    at = days in milestones

    if at:
        return f"🌅 Day {days} sober 🎯"
    if near:
        return f"🌅 Day {days} sober — tomorrow is Day {days+1} 🔥"
    return f"🌅 Day {days} sober."


def _get_action_item(deadline_line: str | None) -> str:
    """Derive the single action item. Deadline-derived > generic."""
    if deadline_line:
        # Strip emoji prefix for the action item format
        return deadline_line
    # No deadline — surface writing if needed
    writing = aethoria_briefing_line()
    if writing:
        return writing
    return "🎯 One thing today: make progress, not perfection."


def compose_brief() -> str:
    # Auto-clear yesterday's stale flare flags
    auto_clear_yesterday()

    sobriety_line = _get_sobriety_line()

    # ── Flare day: quiet mode ────────────────────────────────────────
    if is_flare_day():
        return (
            f"{sobriety_line}\n"
            f"Rest day — system in quiet mode.\n"
            f"Streaks paused. Come back tomorrow."
        )

    # ── Normal day ───────────────────────────────────────────────────
    lines = [sobriety_line]

    # Academic — highest priority
    deadline_line = get_deadline_item()
    if deadline_line:
        lines.append(deadline_line)

    # Recovery nudge (meeting gap)
    nudge = meeting_brief_nudge()
    if nudge:
        lines.append(nudge)

    # Single action item
    action = _get_action_item(deadline_line)
    # Avoid duplication if deadline already in lines
    if action != deadline_line:
        lines.append(f"\n🎯 {action.lstrip('📚✍️📅🔴⚠️ ').strip()}")
    else:
        lines.append(f"\n🎯 Handle it.")

    brief = "\n".join(lines)

    # Enforce 90-word hard cap
    words = brief.split()
    if len(words) > 90:
        brief = " ".join(words[:87]) + "..."

    return brief


def compose_brief_with_buttons() -> dict:
    """
    Returns dict for Telegram inline keyboard integration.
    {
      'text': str,
      'buttons': list of [{'text': str, 'callback_data': str}]
    }
    """
    text = compose_brief()
    buttons = [
        [{"text": "✅ Done",   "callback_data": "done"}],
        [{"text": "📓 Log",    "callback_data": "log_prompt"}],
        [{"text": "💪 Gym",   "callback_data": "gym"}],
        [{"text": "🔴 Flare", "callback_data": "flare"}],
    ]
    return {"text": text, "buttons": buttons}

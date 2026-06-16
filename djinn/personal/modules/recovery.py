"""
TASK-078 — Recovery Cluster
Step work tracking, sponsor contact log, craving log, meeting attendance.

All sensitive data (craving notes, step notes) is local SQLite only.
Ollama used ONLY for craving pattern analysis (/craving week).
NEVER calls cloud LLM for recovery data.

Public API:
  step_status()                          -> str
  advance_step()                         -> str
  log_sponsor_contact(note)              -> str
  log_craving(severity, tag)             -> str
  craving_week_pattern()                 -> str  (Ollama local only)
  log_meeting(attended, name, notes)     -> str
  meetings_week()                        -> str
  meeting_brief_nudge()                  -> str | None
"""

from datetime import date, datetime, timezone, timedelta
from .db import get_conn


# ── Step Work ────────────────────────────────────────────────────────

def step_status() -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT step_number, status, started_date FROM step_work ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not row:
        return "📿 No active step work logged. Use /step start [1-12] to begin."
    today = date.today()
    started = date.fromisoformat(row["started_date"])
    days_on = (today - started).days
    return (
        f"📿 Step {row['step_number']}: {row['status'].upper()}\n"
        f"Started {days_on} days ago ({row['started_date']})"
    )


def start_step(step_number: int, notes: str = "") -> str:
    """Begin working a step (or resume after pause)."""
    conn = get_conn()
    today = date.today().isoformat()
    conn.execute(
        "INSERT INTO step_work(step_number, status, started_date, notes) VALUES (?,?,?,?)",
        (step_number, "active", today, notes),
    )
    conn.commit()
    conn.close()
    return f"📿 Step {step_number} started. One day at a time."


def advance_step() -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT id, step_number FROM step_work WHERE status='active' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not row:
        conn.close()
        return "No active step to advance. Use /step start [N]."
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "UPDATE step_work SET status='complete', completed_date=? WHERE id=?",
        (now, row["id"]),
    )
    next_step = row["step_number"] + 1
    if next_step <= 12:
        today = date.today().isoformat()
        conn.execute(
            "INSERT INTO step_work(step_number, status, started_date) VALUES (?,?,?)",
            (next_step, "active", today),
        )
        msg = f"📿 Step {row['step_number']} complete. Step {next_step} started."
    else:
        msg = "📿 Step 12 complete. \U0001f4ff"
    conn.commit()
    conn.close()
    return msg


# ── Sponsor Contact ──────────────────────────────────────────────────

def log_sponsor_contact(note: str = "") -> str:
    today = date.today().isoformat()
    now_time = datetime.now().strftime("%H:%M")
    conn = get_conn()
    conn.execute(
        "INSERT INTO sponsor_contacts(contact_date, contact_time, brief_note) VALUES (?,?,?)",
        (today, now_time, note),
    )
    conn.commit()
    count_30 = conn.execute(
        "SELECT COUNT(*) FROM sponsor_contacts WHERE contact_date >= date('now','-30 days')"
    ).fetchone()[0]
    conn.close()
    return f"📞 Sponsor contact logged. (Last 30 days: {count_30})"


# ── Craving Log ──────────────────────────────────────────────────────

def log_craving(severity: int, tag: str = "") -> str:
    """5-second entry. Local only. Never cloud."""
    if not 1 <= severity <= 10:
        return "❌ Severity must be 1–10."

    # Get current sobriety day from existing sobriety_log
    conn = get_conn()
    sober_row = conn.execute(
        "SELECT start_date FROM sobriety_log ORDER BY id DESC LIMIT 1"
    ).fetchone()
    sober_day = None
    if sober_row:
        start = date.fromisoformat(sober_row["start_date"])
        sober_day = (date.today() - start).days + 1

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO craving_log(logged_at, severity, tag, sobriety_day) VALUES (?,?,?,?)",
        (now, severity, tag.strip(), sober_day),
    )
    conn.commit()
    conn.close()

    sober_suffix = f" Day {sober_day} sober." if sober_day else ""
    return f"Logged.{sober_suffix}"


def craving_week_pattern() -> str:
    """Pull 7-day craving data → Ollama local pattern note. NEVER cloud."""
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT logged_at, severity, tag, sobriety_day
        FROM craving_log
        WHERE logged_at >= datetime('now', '-7 days')
        ORDER BY logged_at ASC
        """
    ).fetchall()
    conn.close()

    if not rows:
        return "📊 No craving entries this week."

    summary_lines = [
        f"- {r['logged_at'][:16]} sev={r['severity']} tag={r['tag'] or 'none'}"
        for r in rows
    ]
    summary = "\n".join(summary_lines)
    avg = sum(r["severity"] for r in rows) / len(rows)
    
    prompt = (
        f"You are a private recovery journal assistant. "
        f"Here are craving log entries from the past 7 days (severity 1-10):\n\n"
        f"{summary}\n\n"
        f"Average severity: {avg:.1f}. "
        f"In 2-3 sentences, identify any patterns (time of day, tags, trend). "
        f"Be factual. No advice. No judgment."
    )

    try:
        import subprocess
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True, text=True, timeout=30,
        )
        pattern = result.stdout.strip()
        if pattern:
            return f"📊 Craving pattern (7d, {len(rows)} entries):\n{pattern}"
    except Exception:
        pass

    return (
        f"📊 Craving pattern (7d): {len(rows)} entries, "
        f"avg severity {avg:.1f}. Tags: "
        + ", ".join(set(r["tag"] for r in rows if r["tag"])) or "none"
    )


# ── Meeting Attendance ───────────────────────────────────────────────

def log_meeting(attended: bool = True, name: str = "", notes: str = "") -> str:
    today = date.today().isoformat()
    conn = get_conn()
    conn.execute(
        "INSERT INTO meeting_attendance(meeting_date, meeting_type, meeting_name, attended, notes) VALUES (?,?,?,?,?)",
        (today, "aa", name, 1 if attended else 0, notes),
    )
    conn.commit()
    week_count = conn.execute(
        "SELECT COUNT(*) FROM meeting_attendance WHERE attended=1 AND meeting_date >= date('now','weekday 0','-7 days')"
    ).fetchone()[0]
    conn.close()
    verb = "attended" if attended else "missed"
    return f"🔵 Meeting {verb}. Week attended: {week_count}"


def meetings_week() -> str:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT meeting_date, meeting_name, attended
        FROM meeting_attendance
        WHERE meeting_date >= date('now', 'weekday 0', '-7 days')
        ORDER BY meeting_date ASC
        """
    ).fetchall()
    conn.close()
    if not rows:
        return "🔵 No meetings logged this week."
    lines = ["🔵 *Meetings this week:*"]
    for r in rows:
        tick = "✅" if r["attended"] else "❌"
        name = f" ({r['meeting_name']})" if r["meeting_name"] else ""
        lines.append(f"{tick} {r['meeting_date']}{name}")
    return "\n".join(lines)


def meeting_brief_nudge() -> str | None:
    """Returns a brief nudge if 5+ days since last attended meeting. None if recent."""
    conn = get_conn()
    last = conn.execute(
        "SELECT meeting_date FROM meeting_attendance WHERE attended=1 ORDER BY meeting_date DESC LIMIT 1"
    ).fetchone()
    conn.close()
    if not last:
        return "🔵 No meetings logged yet."
    days_since = (date.today() - date.fromisoformat(last["meeting_date"])).days
    if days_since >= 5:
        return f"🔵 {days_since}d since last meeting."
    return None

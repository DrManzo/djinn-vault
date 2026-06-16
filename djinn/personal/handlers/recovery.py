"""
TASK-078 — Recovery Cluster
Handles: /step, /step done, /sponsor-contact, /craving, /meeting attended|missed
All data: local SQLite only. No cloud LLM. Craving week analysis → Ollama only.
"""
import sqlite3
from datetime import date, timedelta

DB_PATH = "djinn-personal.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def _sobriety_day() -> int:
    """Pull sobriety day from existing personal DB habit tracker."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT value FROM habits WHERE name = 'sobriety_start' LIMIT 1"
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return 0
    start = date.fromisoformat(row[0])
    return (date.today() - start).days


# ── Step Work ──────────────────────────────────────────────────────────────

def cmd_step(args: list[str]) -> str:
    conn = _conn()
    cur = conn.cursor()

    if not args:
        cur.execute(
            "SELECT step_number, status, started_date FROM step_work ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return "No step work logged. Use /step 1 to begin Step 1."
        step, status, started = row
        days_in = (date.today() - date.fromisoformat(started)).days
        return f"Step {step}: {status}. Started {days_in} days ago."

    sub = args[0].lower()

    if sub == "done":
        cur.execute(
            "SELECT id, step_number FROM step_work WHERE status = 'active' ORDER BY id DESC LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            conn.close()
            return "No active step found."
        conn.execute(
            "UPDATE step_work SET status='completed', completed_date=date('now') WHERE id=?",
            (row[0],)
        )
        next_step = row[1] + 1
        conn.execute(
            "INSERT INTO step_work (step_number, status, started_date) VALUES (?,?,date('now'))",
            (next_step, "active")
        )
        conn.commit()
        conn.close()
        return f"Step {row[1]} complete. Step {next_step} started."

    # /step [number] — begin a specific step
    try:
        step_num = int(sub)
    except ValueError:
        conn.close()
        return "Usage: /step | /step done | /step [number]"

    conn.execute(
        "INSERT INTO step_work (step_number, status, started_date) VALUES (?,?,date('now'))",
        (step_num, "active")
    )
    conn.commit()
    conn.close()
    return f"Step {step_num} started."


# ── Sponsor Contact ────────────────────────────────────────────────────────

def cmd_sponsor_contact(note: str = "") -> str:
    conn = _conn()
    conn.execute(
        "INSERT INTO sponsor_contacts (contact_date, brief_note) VALUES (date('now'), ?)",
        (note.strip() or None,)
    )
    conn.commit()
    conn.close()
    return "✅ Sponsor contact logged."


# ── Craving Log ────────────────────────────────────────────────────────────

def cmd_craving(args: list[str], ollama_client=None) -> str:
    if not args:
        return "Usage: /craving [1-10] [optional tag] | /craving week"

    if args[0].lower() == "week":
        return _craving_week(ollama_client)

    try:
        severity = int(args[0])
        if not 1 <= severity <= 10:
            raise ValueError
    except ValueError:
        return "Severity must be 1–10."

    tag = args[1] if len(args) > 1 else None
    day_n = _sobriety_day()

    conn = _conn()
    conn.execute(
        "INSERT INTO craving_log (severity, tag, sobriety_day) VALUES (?,?,?)",
        (severity, tag, day_n)
    )
    conn.commit()
    conn.close()
    return f"Logged. Day {day_n} sober."


def _craving_week(ollama_client=None) -> str:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT logged_at, severity, tag FROM craving_log
           WHERE logged_at >= datetime('now', '-7 days')
           ORDER BY logged_at ASC"""
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No cravings logged this week."

    if not ollama_client:
        lines = [f"  {r[0][:10]} severity {r[1]}" + (f" [{r[2]}]" if r[2] else "") for r in rows]
        return f"This week ({len(rows)} entries):\n" + "\n".join(lines)

    context = "\n".join(
        f"{r[0]}: severity {r[1]}" + (f", tag: {r[2]}" if r[2] else "") for r in rows
    )
    prompt = (
        "You are a private, clinical pattern-recognizer. "
        "Look at this craving log and state one factual pattern (day, time, or tag correlation). "
        "One sentence. No advice. No judgment.\n\n" + context
    )
    try:
        response = ollama_client.generate(model="mistral", prompt=prompt)
        return f"📊 {response['response'].strip()}"
    except Exception as e:
        return f"⚠️ Pattern analysis unavailable: {e}"


# ── Meeting Attendance ─────────────────────────────────────────────────────

def cmd_meeting(args: list[str]) -> str:
    if not args:
        return "Usage: /meeting attended [name] | /meeting missed | /meeting week"

    sub = args[0].lower()

    if sub == "week":
        conn = _conn()
        cur = conn.cursor()
        cur.execute(
            """SELECT meeting_date, attended, meeting_name FROM meeting_attendance
               WHERE meeting_date >= date('now', '-7 days')
               ORDER BY meeting_date ASC"""
        )
        rows = cur.fetchall()
        conn.close()
        if not rows:
            return "No meetings logged this week."
        lines = [
            f"  {'✅' if r[1] else '❌'} {r[0]}" + (f" — {r[2]}" if r[2] else "")
            for r in rows
        ]
        attended = sum(1 for r in rows if r[1])
        return f"This week: {attended}/{len(rows)} attended\n" + "\n".join(lines)

    if sub in ("attended", "missed"):
        attended = 1 if sub == "attended" else 0
        name = " ".join(args[1:]) if len(args) > 1 else None
        conn = _conn()
        conn.execute(
            """INSERT INTO meeting_attendance (meeting_date, attended, meeting_name)
               VALUES (date('now'), ?, ?)""",
            (attended, name)
        )
        conn.commit()
        conn.close()
        emoji = "✅" if attended else "—"
        label = "attended" if attended else "missed"
        msg = f"{emoji} Meeting {label} logged."
        return msg

    return "Usage: /meeting attended [name] | /meeting missed | /meeting week"


# ── Briefing: quiet nudge if 5+ days since last logged meeting ─────────────

def get_meeting_brief_nudge() -> str | None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(meeting_date) FROM meeting_attendance WHERE attended = 1"
    )
    row = cur.fetchone()
    conn.close()
    if not row or not row[0]:
        return None
    last = date.fromisoformat(row[0])
    gap = (date.today() - last).days
    if gap >= 5:
        return f"🕊️ Last meeting: {gap} days ago."
    return None

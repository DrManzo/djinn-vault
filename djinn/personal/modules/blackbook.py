"""
TASK-076 — Black Book Micro-Entry Fix

Public API:
  log_entry(text)                -> str   (/log command)
  get_entry_count()              -> int
  can_reflect()                  -> bool  (gated at 3+ entries)
  get_reflect_prompt_via_ollama() -> str  (/reflect — local Ollama only)
"""

from datetime import datetime, timezone
from .db import get_conn

REFLECT_GATE = 3  # minimum entries before /reflect activates


def log_entry(text: str) -> str:
    """
    Zero-friction entry. No Ollama call at write time.
    Habit-stacks onto /done — called from same handler.
    """
    conn = get_conn()
    now = datetime.now(timezone.utc).isoformat()

    # Ensure table exists (v1 schema creates black_book_log)
    conn.execute(
        """
        INSERT INTO black_book_log(entry, logged_at, entry_source)
        VALUES (?, ?, 'manual')
        """,
        (text.strip(), now),
    )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM black_book_log").fetchone()[0]
    conn.close()

    response = f"✅ Logged. (entry #{count})"
    if count == REFLECT_GATE:
        response += f"\n📓 You have {count} entries. /reflect is live."
    return response


def get_entry_count() -> int:
    conn = get_conn()
    count = conn.execute("SELECT COUNT(*) FROM black_book_log").fetchone()[0]
    conn.close()
    return count


def can_reflect() -> bool:
    return get_entry_count() >= REFLECT_GATE


def get_reflect_prompt_via_ollama() -> str:
    """
    Pulls last 5 entries, sends to local Ollama (mistral or llama3),
    asks for one introspective question. NEVER calls cloud LLM.
    Returns the question string or a fallback if Ollama is unreachable.
    """
    if not can_reflect():
        count = get_entry_count()
        remaining = REFLECT_GATE - count
        return (
            f"📓 /reflect needs {REFLECT_GATE} entries. "
            f"You have {count}. {remaining} more to go. Use /log to add one."
        )

    conn = get_conn()
    rows = conn.execute(
        "SELECT entry FROM black_book_log ORDER BY id DESC LIMIT 5"
    ).fetchall()
    conn.close()

    entries = "\n".join(f"- {row['entry']}" for row in rows)
    prompt = (
        f"You are a reflective journal assistant. "
        f"Here are someone's recent private notes:\n\n{entries}\n\n"
        f"Ask exactly one short, open-ended introspective question based on these notes. "
        f"No preamble. Just the question."
    )

    try:
        import subprocess
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        question = result.stdout.strip()
        if question:
            return f"📓 {question}"
    except Exception:
        pass

    return "📓 What's been sitting with you lately that you haven't said out loud?"

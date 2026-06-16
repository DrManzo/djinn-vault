"""
TASK-076 — Black Book Micro-Entry Fix
Handles: /log, /reflect
Fix: /log captures immediately with zero friction.
     /reflect gates at 3+ entries.
     entry_source field added (migration: phase_beta.sql).
"""
import sqlite3
from datetime import datetime

DB_PATH = "djinn-personal.db"


def _conn():
    return sqlite3.connect(DB_PATH)


def _total_entries() -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM black_book_log")
    count = cur.fetchone()[0]
    conn.close()
    return count


def cmd_log(text: str | None = None) -> str:
    """
    /log [text] — immediate capture, no prompt, no Ollama at write time.
    /log (no args) — returns prompt string for bot to ask.
    """
    if not text or not text.strip():
        return "__PROMPT_USER__:What's on your mind?"

    conn = _conn()
    conn.execute(
        """INSERT INTO black_book_log (entry_date, content, entry_source)
           VALUES (datetime('now'), ?, 'manual')""",
        (text.strip(),)
    )
    conn.commit()
    conn.close()

    total = _total_entries()
    base = f"✅ Logged. (entry #{total})"

    if total == 3:
        return base + "\n📓 You have 3 entries. /reflect is now live."
    if total == 10:
        return base + "\n🔓 10 entries. The Black Book is real now."
    return base


def cmd_reflect(ollama_client=None) -> str:
    """
    /reflect — Ollama pulls one question from Black Book entries.
    Gates: requires 3+ entries. Never exposes content to cloud LLM.
    """
    total = _total_entries()
    if total < 3:
        remaining = 3 - total
        return f"📓 {remaining} more {'entry' if remaining == 1 else 'entries'} before /reflect activates."

    if not ollama_client:
        return "⚠️ Ollama client not connected. /reflect requires local model."

    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT content FROM black_book_log ORDER BY entry_date DESC LIMIT 5"
    )
    entries = [row[0] for row in cur.fetchall()]
    conn.close()

    context = "\n---\n".join(entries)
    prompt = (
        "You are a quiet, Socratic presence. Based only on these private journal entries, "
        "ask one precise, non-judgmental question that would help this person think more clearly. "
        "One question only. No preamble.\n\nEntries:\n" + context
    )

    try:
        response = ollama_client.generate(model="mistral", prompt=prompt)
        return f"📓 {response['response'].strip()}"
    except Exception as e:
        return f"⚠️ Reflect unavailable: {e}"

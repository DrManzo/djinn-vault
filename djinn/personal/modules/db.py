"""
djinn.personal.db — shared SQLite connection helper.
All personal modules import get_conn() from here.
Local-first. Never logs sensitive fields to external services.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".local/share/djinn/personal.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

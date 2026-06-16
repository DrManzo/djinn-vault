#!/usr/bin/env python3
"""
djinn-personal-db migration v2
Run once: python3 migrate_v2.py
Safe to re-run — all operations are idempotent.
"""

import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path.home() / ".local/share/djinn/personal.db"
SCHEMA_PATH = Path(__file__).parent / "schema_v2.sql"


def run():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Apply schema
    schema_sql = SCHEMA_PATH.read_text()
    conn.executescript(schema_sql)

    # Idempotent: add entry_source to black_book_log if not present
    cols = [row[1] for row in cur.execute("PRAGMA table_info(black_book_log)").fetchall()]
    if "entry_source" not in cols:
        try:
            cur.execute("ALTER TABLE black_book_log ADD COLUMN entry_source TEXT DEFAULT 'manual'")
            conn.commit()
            print("[migrate_v2] Added entry_source to black_book_log")
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise

    # Log migration
    now = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "INSERT OR IGNORE INTO _migration_log(migration, applied_at) VALUES (?, ?)",
        ("schema_v2", now),
    )
    conn.commit()
    conn.close()
    print(f"[migrate_v2] Done. DB: {DB_PATH}")


if __name__ == "__main__":
    run()

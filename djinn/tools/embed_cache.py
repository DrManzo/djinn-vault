"""
Shared embed cache — SQLite-backed, keyed by sha256(text).
All djinn scripts that call nomic-embed-text check here first.
"""

import hashlib
import json
import os
import sqlite3
import time

CACHE_DIR = os.path.expanduser("~/.cache/djinn")
DB_PATH = os.path.join(CACHE_DIR, "embed-cache.db")

_ENSURED = False


def _ensure():
    global _ENSURED
    if _ENSURED:
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, vec TEXT, updated REAL)")
    db.commit()
    db.close()
    _ENSURED = True


def get(text: str):
    """Return cached embedding vector for text, or None."""
    _ensure()
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    db = sqlite3.connect(DB_PATH)
    row = db.execute("SELECT vec FROM cache WHERE key=?", (key,)).fetchone()
    db.close()
    if row:
        return json.loads(row[0])
    return None


def put(text: str, vector: list):
    """Cache an embedding vector for text."""
    _ensure()
    key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    db = sqlite3.connect(DB_PATH)
    db.execute(
        "INSERT OR REPLACE INTO cache VALUES (?,?,?)",
        (key, json.dumps(vector), time.time()),
    )
    db.commit()
    db.close()


def clear():
    """Wipe the entire cache — forces re-embed on next call."""
    _ensure()
    db = sqlite3.connect(DB_PATH)
    db.execute("DELETE FROM cache")
    db.commit()
    db.close()

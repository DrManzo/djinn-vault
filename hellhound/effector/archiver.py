"""archiver.py — Log rotation and SQLite index compaction.

Run periodically (e.g. via systemd timer or cron).
"""

import gzip
import shutil
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path.home() / ".local" / "share" / "hellhound" / "skull"
LOGS_DIR = BASE_DIR / "logs"
ARCHIVE  = LOGS_DIR / "archive"
DB_FILE  = BASE_DIR / "neurals" / "index.db"

RETENTION_DAYS = 30


def compress_old_archives() -> list[Path]:
    """
    gzip any uncompressed .jsonl files in archive/ older than 24 hours.
    Returns list of compressed files.
    """
    compressed = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    for f in ARCHIVE.glob("*.jsonl"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            gz_path = f.with_suffix(".jsonl.gz")
            with f.open("rb") as fin, gzip.open(gz_path, "wb") as fout:
                shutil.copyfileobj(fin, fout)
            f.unlink()
            compressed.append(gz_path)
    return compressed


def prune_old_archives() -> list[Path]:
    """
    Delete compressed archives older than RETENTION_DAYS.
    Returns list of deleted files.
    """
    deleted = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    for f in ARCHIVE.glob("*.jsonl.gz"):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            f.unlink()
            deleted.append(f)
    return deleted


def compact_db(days_to_keep: int = RETENTION_DAYS) -> int:
    """
    Delete observations older than `days_to_keep` from the SQLite index.
    Returns number of rows deleted.
    """
    import time
    cutoff_ts = time.time() - (days_to_keep * 86400)
    con = sqlite3.connect(DB_FILE)
    cur = con.execute("DELETE FROM observations WHERE ts < ?", (cutoff_ts,))
    deleted = cur.rowcount
    con.execute("VACUUM")
    con.commit()
    con.close()
    return deleted


def run_all():
    compressed = compress_old_archives()
    pruned     = prune_old_archives()
    db_deleted = compact_db()
    print(f"Archiver: compressed={len(compressed)}, pruned={len(pruned)}, db_rows_deleted={db_deleted}")


if __name__ == "__main__":
    run_all()

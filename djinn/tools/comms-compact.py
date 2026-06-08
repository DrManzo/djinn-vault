#!/usr/bin/env python3
"""
djinn-comms-compact — Archives old COMMS.md entries to keep the file lean.

COMMS.md is append-only, so it grows without bound. This script:
  1. Reads COMMS.md
  2. Keeps the last KEEP_ENTRIES section entries in-place
  3. Moves older entries to djinn/communications/archive/COMMS-YYYY-MM.md
  4. Commits the result

Run: djinn-comms-compact [--dry-run]
Systemd: comms-compact.timer fires daily at 03:00 local.

Threshold: only compacts if COMMS.md exceeds MAX_LINES lines.
"""

import re
import sys
import pathlib
import subprocess
from datetime import datetime, timezone

VAULT        = pathlib.Path.home() / "Obsidian"
COMMS        = VAULT / "djinn/communications/COMMS.md"
ARCHIVE_DIR  = VAULT / "djinn/communications/archive"
MAX_LINES    = 800    # compact when COMMS.md exceeds this
KEEP_ENTRIES = 40     # always keep the most recent N section entries

DRY_RUN = "--dry-run" in sys.argv

_SECTION_RE = re.compile(r'^### ', re.MULTILINE)


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[{ts}] [comms-compact] {msg}", flush=True)


def split_header_and_entries(text: str) -> tuple[str, list[str]]:
    """Split COMMS.md into a header block and a list of section entries."""
    # Find first ### section
    m = _SECTION_RE.search(text)
    if not m:
        return text, []
    header = text[:m.start()].rstrip("\n") + "\n\n"
    body = text[m.start():]
    # Split on each ### heading
    parts = _SECTION_RE.split(body)
    entries = ["### " + p.rstrip("\n") for p in parts if p.strip()]
    return header, entries


def archive_path_for(ts: str) -> pathlib.Path:
    """Return monthly archive file path, e.g. COMMS-2026-06.md"""
    try:
        # ts looks like "2026-06-07 12:00 UTC" or ISO
        dt = datetime.strptime(ts[:7], "%Y-%m")
    except Exception:
        dt = datetime.now(timezone.utc)
    return ARCHIVE_DIR / f"COMMS-{dt.strftime('%Y-%m')}.md"


def entry_ts(entry: str) -> str:
    """Extract timestamp from section header for archive routing."""
    m = re.search(r'(\d{4}-\d{2}-\d{2})', entry)
    return m.group(1) if m else ""


def main():
    if not COMMS.exists():
        log("COMMS.md not found — nothing to compact")
        return

    text = COMMS.read_text(errors="replace")
    line_count = text.count("\n")

    if line_count <= MAX_LINES:
        log(f"COMMS.md is {line_count} lines — below threshold ({MAX_LINES}), skipping")
        return

    log(f"COMMS.md is {line_count} lines — compacting (keeping last {KEEP_ENTRIES} entries)")

    header, entries = split_header_and_entries(text)

    if len(entries) <= KEEP_ENTRIES:
        log(f"Only {len(entries)} entries found — nothing to archive")
        return

    to_archive = entries[:-KEEP_ENTRIES]
    to_keep    = entries[-KEEP_ENTRIES:]

    # Group archived entries by month
    by_month: dict[pathlib.Path, list[str]] = {}
    for entry in to_archive:
        ts = entry_ts(entry)
        path = archive_path_for(ts)
        by_month.setdefault(path, []).append(entry)

    if DRY_RUN:
        log(f"[DRY RUN] Would archive {len(to_archive)} entries across {len(by_month)} archive file(s)")
        for path, group in by_month.items():
            log(f"  → {path.name}: {len(group)} entries")
        log(f"  Keeping: {len(to_keep)} entries in COMMS.md")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for path, group in by_month.items():
        if path.exists():
            existing = path.read_text(errors="replace")
            combined = existing.rstrip("\n") + "\n\n" + "\n\n".join(group)
        else:
            month_label = path.stem.replace("COMMS-", "")
            combined = f"# COMMS Archive — {month_label}\n\n" + "\n\n".join(group)
        path.write_text(combined + "\n")
        log(f"Archived {len(group)} entries → {path.name}")

    # Rewrite COMMS.md with just the header + recent entries
    new_text = header + "\n\n".join(to_keep) + "\n"
    COMMS.write_text(new_text)
    log(f"COMMS.md rewritten: {len(to_keep)} entries retained")

    # Commit
    try:
        subprocess.run(
            ["git", "-C", str(VAULT), "add",
             str(COMMS), str(ARCHIVE_DIR)],
            check=True, capture_output=True
        )
        subprocess.run(
            ["git", "-C", str(VAULT), "commit",
             "-m", f"comms-compact: archived {len(to_archive)} entries — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
             "--quiet"],
            capture_output=True
        )
        subprocess.run(
            ["git", "-C", str(VAULT), "push", "--quiet"],
            capture_output=True
        )
        log("Committed and pushed")
    except subprocess.CalledProcessError as e:
        log(f"Git error: {e.stderr.decode().strip() if e.stderr else str(e)}")


if __name__ == "__main__":
    main()

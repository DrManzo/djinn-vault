#!/usr/bin/env python3
"""
marcus-sync.py — deterministic inbox ingestor. No LLM.

Reads ~/djinn-inbox/*.md, routes each file to djinn/research/{agent}/sessions/,
adds missing Obsidian frontmatter fields, then deletes the inbox copy.

Usage:
    marcus-sync.py                   # process all files in ~/djinn-inbox/
    marcus-sync.py --auto-detect-agent  # same (flag exists for watcher compat)
    marcus-sync.py --dry-run         # show what would happen, no writes

Deploy:
    cp marcus-sync.py ~/.local/bin/marcus-sync.py
    chmod +x ~/.local/bin/marcus-sync.py
"""
import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path

INBOX_DIR = Path.home() / "djinn-inbox"
VAULT_DIR = Path.home() / "Obsidian"
RESEARCH_DIR = VAULT_DIR / "djinn" / "research"

_FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
_KEY_RE = re.compile(r"^(\w+):\s*(.+)$", re.MULTILINE)


def _parse_frontmatter(text: str) -> dict:
    m = _FM_RE.match(text)
    if not m:
        return {}
    return {k: v.strip() for k, v in _KEY_RE.findall(m.group(1))}


def _ensure_frontmatter(text: str, filename: str) -> tuple[str, dict]:
    """Add or patch frontmatter. Returns (updated_text, parsed_meta)."""
    fm = _parse_frontmatter(text)

    if not fm:
        # No frontmatter — infer from filename: YYYYMMDDTHHMMSSZ_agent_session.md
        parts = Path(filename).stem.split("_", 2)
        agent = parts[1] if len(parts) > 1 else "unknown"
        session = parts[2] if len(parts) > 2 else "session"
        date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        header = (
            f"---\ndate: {date}\nagent: {agent}\nsession: {session}\n"
            f"tags: [inbox, {agent}]\n---\n\n"
        )
        fm = {"agent": agent, "session": session, "date": date}
        text = header + text

    return text, fm


def process_file(path: Path, dry_run: bool = False) -> bool:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [ERROR] read {path.name}: {e}", file=sys.stderr)
        return False

    text, meta = _ensure_frontmatter(text, path.name)
    agent = re.sub(r"[^\w-]", "-", meta.get("agent", "unknown"))[:20]

    dest_dir = RESEARCH_DIR / agent / "sessions"
    dest = dest_dir / path.name

    if dry_run:
        print(f"  [dry-run] {path.name} → {dest}")
        return True

    dest_dir.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        dest = dest_dir / f"{ts}_{path.name}"

    dest.write_text(text, encoding="utf-8")
    path.unlink()
    print(f"  {path.name} → {dest.relative_to(VAULT_DIR)}")
    return True


def main():
    ap = argparse.ArgumentParser(description="Djinn inbox ingestor — no LLM")
    ap.add_argument("--auto-detect-agent", action="store_true",
                    help="Infer agent from filename (default behavior)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Show routing without writing or deleting")
    args = ap.parse_args()

    if not INBOX_DIR.exists():
        return

    files = sorted(INBOX_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime)
    if not files:
        return

    for f in files:
        process_file(f, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

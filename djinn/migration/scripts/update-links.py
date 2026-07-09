#!/usr/bin/env python3
"""update-links.py — Vault wikilink updater after restructure
Usage: python3 update-links.py [--dry-run] [--verbose]
Run from anywhere — uses ~/Obsidian as vault root.
"""

import os
import re
import shutil
import sys
from pathlib import Path

VAULT = Path.home() / "Obsidian"
BACKUP_DIR = Path("/tmp/vault-link-backup")
DRY_RUN = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv

SKIP_DIRS = {"RAW", ".git", ".obsidian", ".trash", ".Trash-1000", ".claude"}

# Remap table — LONGEST/most-specific prefixes FIRST
REMAP = [
    ("djinn/printer/calliope-config-backup-2026-06-05", "forge/calliope-config-backup-2026-06-05"),
    ("djinn/printer/design-process",  "forge/design-process"),
    ("djinn/printer/finished-prints", "forge/finished-prints"),
    ("djinn/printer/traces-archive",  "forge/traces-archive"),
    ("djinn/printer/forge-slicer",    "forge/forge-slicer"),
    ("djinn/printer/commissions",     "forge/commissions"),
    ("djinn/printer/calibration",     "forge/calibration"),
    ("djinn/printer/workflows",       "forge/workflows"),
    ("djinn/printer/completed",       "forge/completed"),
    ("djinn/printer/snapshots",       "forge/snapshots"),
    ("djinn/printer/originals",       "forge/originals"),
    ("djinn/printer/planning",        "forge/planning"),
    ("djinn/printer/failures",        "forge/failures"),
    ("djinn/printer/feedback",        "forge/feedback"),
    ("djinn/printer/telegram",        "forge/telegram"),
    ("djinn/printer/discord",         "forge/discord"),
    ("djinn/printer/library",         "forge/library"),
    ("djinn/printer/archive",         "forge/archive"),
    ("djinn/printer/content",         "forge/content"),
    ("djinn/printer/process",         "forge/process"),
    ("djinn/printer/active",          "forge/active"),
    ("djinn/printer/prints",          "forge/prints"),
    ("djinn/printer/backup",          "forge/backup"),
    ("djinn/printer/config",          "forge/config"),
    ("djinn/printer/queue",           "forge/queue"),
    ("djinn/printer/agent",           "forge/agent"),
    ("djinn/printer/tools",           "forge/tools"),
    ("djinn/printer/shop",            "forge/shop"),
    ("djinn/printer/docs",            "forge/docs"),
    ("djinn/printer/forge",           "forge/_printer-forge"),
    ("djinn/printer",                 "forge"),
    ("djinn/hardware",                "forge/hardware"),
    ("djinn/finance",                 "forge/finance"),
    ("djinn/typhons-forge",           "forge/typhons-forge"),
    ("djinn/projects",                "forge/projects"),
    ("djinn/social",                  "media/analytics"),
    ("djinn/media",                   "media"),
    ("djinn/research/architecture",   "ai/architecture"),
    ("djinn/research/claude",         "ai/claude"),
    ("djinn/research/gemini",         "ai/gemini"),
    ("djinn/research/marcus",         "ai/marcus"),
    ("djinn/research",                "ai"),
    ("djinn/workspaces/mobile-forge", "ai/workspaces/mobile-forge"),
    ("djinn/workspaces/typhon-windows", "ai/workspaces/typhon-windows"),
    ("djinn/workspaces/writing",      "writing/workspace"),
    ("djinn/hellhound",               "hellhound"),
    ("djinn/writing",                 "writing"),
    ("djinn/people",                  "personal/people"),
    ("djinn/personal",                "personal"),
]

def remap_path(s):
    for old, new in REMAP:
        if s == old or s.startswith(old + "/"):
            return new + s[len(old):]
    return s

def process_file(md_file, stats):
    try:
        content = md_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR reading {md_file}: {e}")
        return

    original = content
    changes = []

    # [[target]], [[target|alias]], [[target#heading]], ![[embed]]
    def replace_wiki(m):
        bang   = m.group(1)
        target = m.group(2)
        rest   = m.group(3)  # |alias or #heading or both
        new_target = remap_path(target)
        if new_target != target:
            changes.append(f"  [[{target}]] → [[{new_target}]]")
            return f"{bang}[[{new_target}{rest}]]"
        return m.group(0)

    content = re.sub(
        r'(!?)\[\[([^\]|#\n]+)((?:[|#][^\]\n]*)?)\]\]',
        replace_wiki, content
    )

    # [text](relative/path.md) — skip http and anchors
    def replace_href(m):
        text = m.group(1)
        href = m.group(2)
        if href.startswith("http") or href.startswith("#"):
            return m.group(0)
        clean = href.lstrip("./")
        new_href = remap_path(clean)
        if new_href != clean:
            changes.append(f"  [{text}]({href}) → [{text}]({new_href})")
            return f"[{text}]({new_href})"
        return m.group(0)

    content = re.sub(r'\[([^\]\n]+)\]\(([^)\n]+)\)', replace_href, content)

    if changes:
        stats["files_changed"] += 1
        stats["links_changed"] += len(changes)
        rel = md_file.relative_to(VAULT)
        print(f"\n{rel}")
        for c in changes:
            print(c)
        if not DRY_RUN:
            backup_path = BACKUP_DIR / rel
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md_file, backup_path)
            md_file.write_text(content, encoding="utf-8")
    elif VERBOSE:
        print(f"  ok: {md_file.relative_to(VAULT)}")


def main():
    if DRY_RUN:
        print("=== DRY RUN — no files will be written ===\n")

    stats = {"files_changed": 0, "links_changed": 0, "files_scanned": 0}

    for md_file in sorted(VAULT.rglob("*.md")):
        parts = set(md_file.relative_to(VAULT).parts)
        if parts & SKIP_DIRS:
            continue
        stats["files_scanned"] += 1
        process_file(md_file, stats)

    print(f"\n=== Summary ===")
    print(f"Scanned : {stats['files_scanned']} files")
    print(f"Changed : {stats['files_changed']} files")
    print(f"Links   : {stats['links_changed']} links updated")
    if not DRY_RUN and stats["files_changed"]:
        print(f"Backups : {BACKUP_DIR}")
    if DRY_RUN:
        print("\nRun without --dry-run to apply.")

if __name__ == "__main__":
    main()


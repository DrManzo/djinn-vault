#!/usr/bin/env python3
"""
inbox-watcher — inotifywait loop that fires marcus-sync on new inbox files.
Designed to run as a systemd user service (inbox-watcher.service).

Deploy:
    cp inbox-watcher.py ~/.local/bin/inbox-watcher
    chmod +x ~/.local/bin/inbox-watcher
    systemctl --user enable --now inbox-watcher.service
"""
import subprocess
import sys
from pathlib import Path

INBOX_DIR = Path.home() / "djinn-inbox"
MARCUS_SYNC = Path.home() / ".local" / "bin" / "marcus-sync.py"


def main():
    INBOX_DIR.mkdir(exist_ok=True)
    print(f"inbox-watcher: watching {INBOX_DIR}", flush=True)

    while True:
        subprocess.run(
            ["inotifywait", "-e", "close_write", "-q", str(INBOX_DIR)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        result = subprocess.run(
            [sys.executable, str(MARCUS_SYNC), "--auto-detect-agent"],
            capture_output=True, text=True,
        )
        if result.stdout:
            print(result.stdout, end="", flush=True)
        if result.returncode != 0 and result.stderr:
            print(f"  [ERROR] {result.stderr}", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
djinn-inbox — HTTP ingestion endpoint on port 8765.

Accepts POST /ingest {text, session, agent}
Writes a timestamped markdown file to ~/djinn-inbox/ with Obsidian frontmatter.
marcus-sync.py (via inbox-watcher.service) picks it up and routes it to the vault.

Deploy:
    cp flask_inbox.py ~/.local/bin/djinn-flask-inbox
    chmod +x ~/.local/bin/djinn-flask-inbox
    systemctl --user enable --now djinn-inbox.service

Requirements:
    pip install flask  (or: pip3 install flask)
"""
import datetime
import os
import re
from pathlib import Path

from flask import Flask, jsonify, request

INBOX_DIR = Path.home() / "djinn-inbox"
INBOX_DIR.mkdir(exist_ok=True)

app = Flask(__name__)

_SLUG_RE = re.compile(r"[^\w-]")


def _slug(s: str, maxlen: int) -> str:
    return _SLUG_RE.sub("-", s.strip())[:maxlen].strip("-") or "default"


@app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"status": "error", "reason": "text is required"}), 400

    agent = _slug(data.get("agent", "unknown"), 20)
    session = _slug(data.get("session", "session"), 50)

    now = datetime.datetime.utcnow()
    ts = now.strftime("%Y%m%dT%H%M%SZ")
    date_str = now.strftime("%Y-%m-%d")
    filename = f"{ts}_{agent}_{session}.md"
    path = INBOX_DIR / filename

    path.write_text(
        f"---\n"
        f"date: {date_str}\n"
        f"agent: {agent}\n"
        f"session: {session}\n"
        f"tags: [inbox, {agent}]\n"
        f"---\n\n"
        f"{text}\n"
    )

    return jsonify({"status": "ok", "file": filename}), 201


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("DJINN_INBOX_PORT", 8765))
    app.run(host="0.0.0.0", port=port)

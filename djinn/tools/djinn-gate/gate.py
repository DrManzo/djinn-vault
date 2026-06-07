#!/usr/bin/env python3
"""
djinn-gate — Task routing gate for the Djinn platform.

CLI:
    djinn-gate route --task "description"          → JSON to stdout, exit 0/1
    djinn-gate route --task "description" --serve  → JSON + HTTP on localhost:7070

Response schema:
    {
        "status": "accepted|rejected",
        "lane": "lane_name | null",
        "llm_allowed": true/false,
        "isolated": false,
        "escalation_allowed": true/false,
        "matched_on": "phrase|keyword|none",
        "matched_value": "the matched string",
        "reason": "only present on rejection"
    }

Exit codes:
    0 = accepted
    1 = rejected | error

profile parameter — required on any LLM call:
    "deterministic"     temperature=0.1, max_tokens=512
    "synthesis"         temperature=0.7, max_tokens=2048
    "structured_output" temperature=0.2, max_tokens=1024
    Raises ValueError on missing or invalid profile — no silent fallback.

No external dependencies — stdlib only (tomllib, argparse, json, http.server).
"""

import sys
import json
import argparse
import re
import functools
import pathlib
import tomllib
from typing import Literal
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROUTING_TOML = pathlib.Path(__file__).parent / "routing.toml"

_VALID_PROFILES = frozenset({"deterministic", "synthesis", "structured_output"})

ProfileType = Literal["deterministic", "synthesis", "structured_output"]

_PROFILE_SETTINGS: dict[str, dict] = {
    "deterministic":     {"temperature": 0.1, "max_tokens": 512},
    "structured_output": {"temperature": 0.2, "max_tokens": 1024},
    "synthesis":         {"temperature": 0.7, "max_tokens": 2048},
}


def validate_profile(profile: str) -> dict:
    """Return profile settings or raise ValueError — no silent fallback."""
    if profile not in _VALID_PROFILES:
        raise ValueError(
            f"[djinn-gate] Invalid profile {profile!r}. "
            f"Must be one of: {sorted(_VALID_PROFILES)}"
        )
    return _PROFILE_SETTINGS[profile]


def load_routing() -> list[dict]:
    """Load and return the lane list from routing.toml."""
    with open(ROUTING_TOML, "rb") as f:
        data = tomllib.load(f)
    return data.get("lanes", [])


def _normalize(text: str) -> str:
    return text.lower().strip()


def route(task: str, lanes: list[dict]) -> dict:
    """
    Route task to a lane.

    Matching order:
      1. Phrases (substring match) — first match wins
      2. Keywords (word-boundary match) — first match wins
      3. No match → rejection
    """
    task_norm = _normalize(task)

    for lane in lanes:
        for phrase in lane.get("phrases", []):
            if phrase.lower() in task_norm:
                return _accept(lane, "phrase", phrase)

    for lane in lanes:
        for kw in lane.get("keywords", []):
            pattern = r'\b' + re.escape(kw.lower()) + r'\b'
            if re.search(pattern, task_norm):
                return _accept(lane, "keyword", kw)

    return {
        "status": "rejected",
        "lane": None,
        "llm_allowed": False,
        "isolated": False,
        "escalation_allowed": False,
        "matched_on": "none",
        "matched_value": "",
        "reason": f"No lane matched: {task!r}",
    }


def _accept(lane: dict, matched_on: str, matched_value: str) -> dict:
    return {
        "status": "accepted",
        "lane": lane["name"],
        "llm_allowed": lane.get("llm_allowed", True),
        "isolated": lane.get("isolated", False),
        "escalation_allowed": lane.get("escalation_allowed", True),
        "matched_on": matched_on,
        "matched_value": matched_value,
    }


# ── HTTP interface ─────────────────────────────────────────────────────────────

class _GateHandler(BaseHTTPRequestHandler):
    lanes: list[dict]

    def log_message(self, format, *args):
        pass

    def _respond(self, result: dict) -> None:
        body = json.dumps(result, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path != "/route":
            self.send_response(404)
            self.end_headers()
            return
        qs = parse_qs(parsed.query)
        task = qs.get("task", [""])[0]
        self._respond(route(task, self.lanes))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw)
            task = payload.get("task", "")
        except (json.JSONDecodeError, AttributeError):
            task = ""
        self._respond(route(task, self.lanes))


def _serve(lanes: list[dict], port: int = 7070) -> None:
    handler_cls = type("GateHandler", (_GateHandler,), {"lanes": lanes})
    server = HTTPServer(("127.0.0.1", port), handler_cls)
    print(f"[djinn-gate] HTTP listening on http://127.0.0.1:{port}/route", flush=True)
    server.serve_forever()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="djinn-gate",
        description="Djinn task routing gate — routes a task description to a lane",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    route_p = sub.add_parser("route", help="Route a task description to a lane")
    route_p.add_argument("--task", required=True, metavar="TEXT",
                         help="Task description to route")
    route_p.add_argument("--serve", action="store_true",
                         help="Also start HTTP server on localhost:7070")

    args = parser.parse_args()

    if args.command != "route":
        parser.print_help()
        sys.exit(1)

    try:
        lanes = load_routing()
    except FileNotFoundError:
        print(json.dumps({
            "status": "rejected",
            "lane": None,
            "llm_allowed": False,
            "isolated": False,
            "escalation_allowed": False,
            "matched_on": "none",
            "matched_value": "",
            "reason": f"routing.toml not found at {ROUTING_TOML}",
        }), flush=True)
        sys.exit(1)

    result = route(args.task, lanes)
    print(json.dumps(result, indent=2), flush=True)

    if args.serve:
        _serve(lanes)
        return

    sys.exit(0 if result["status"] == "accepted" else 1)


if __name__ == "__main__":
    main()

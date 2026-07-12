#!/usr/bin/env python3
"""
hellhound.py — The Master
Unix socket server + pup registry + auth + cortex bridge.

Runtime dir: ~/.local/share/hellhound/skull/
Socket:       skull/skull.sock  (chmod 600)
State:        skull/neurals/state.json
Log:          skull/logs/current.jsonl
"""

import asyncio
import json
import logging
import os
import secrets
import signal
import sqlite3
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = Path.home() / ".local" / "share" / "hellhound" / "skull"
SOCK_PATH  = BASE_DIR / "skull.sock"
PUPS_DIR   = BASE_DIR / "pups"
NEURALS    = BASE_DIR / "neurals"
LOGS_DIR   = BASE_DIR / "logs"
STATE_FILE = NEURALS / "state.json"
DB_FILE    = NEURALS / "index.db"
CUR_LOG    = LOGS_DIR / "current.jsonl"
ARCHIVE    = LOGS_DIR / "archive"

VAULT_BASE = Path.home() / "Obsidian" / "hellhound"

MAX_LOG_LINES = 10_000

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("hellhound")

# ---------------------------------------------------------------------------
# Bootstrap directories
# ---------------------------------------------------------------------------
def bootstrap_dirs():
    for d in [PUPS_DIR, NEURALS, LOGS_DIR, ARCHIVE, VAULT_BASE,
              VAULT_BASE / "timeline", VAULT_BASE / "gates",
              VAULT_BASE / "incidents", VAULT_BASE / "reports"]:
        d.mkdir(parents=True, exist_ok=True)

    SOCK_PATH.unlink(missing_ok=True)  # stale socket cleanup

    if not DB_FILE.exists():
        _init_db()

# ---------------------------------------------------------------------------
# SQLite index
# ---------------------------------------------------------------------------
def _init_db():
    con = sqlite3.connect(DB_FILE)
    con.executescript("""
        CREATE TABLE IF NOT EXISTS observations (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       REAL    NOT NULL,
            pup      TEXT    NOT NULL,
            domain   TEXT    NOT NULL,
            event    TEXT    NOT NULL,
            severity TEXT    NOT NULL DEFAULT 'info',
            payload  TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_obs_ts     ON observations(ts);
        CREATE INDEX IF NOT EXISTS idx_obs_domain ON observations(domain);
        CREATE INDEX IF NOT EXISTS idx_obs_pup    ON observations(pup);
    """)
    con.commit()
    con.close()

def _index_observation(obs: dict):
    try:
        con = sqlite3.connect(DB_FILE)
        con.execute(
            "INSERT INTO observations (ts, pup, domain, event, severity, payload) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                obs.get("ts", time.time()),
                obs.get("pup", "unknown"),
                obs.get("domain", ""),
                obs.get("event", ""),
                obs.get("severity", "info"),
                json.dumps(obs.get("payload", {})),
            ),
        )
        con.commit()
        con.close()
    except Exception as exc:
        log.warning("DB index failed: %s", exc)

# ---------------------------------------------------------------------------
# Registry  (in-memory, flushed to state.json via write queue)
# ---------------------------------------------------------------------------
class Registry:
    def __init__(self):
        self._pups: dict[str, dict] = {}   # name → pup record
        self._write_q: deque = deque()     # pending state.json writes
        self._lock = asyncio.Lock()

    async def register(self, name: str, gate: str, token: str) -> str:
        async with self._lock:
            pup_id = f"pup-{len(self._pups) + 1}"
            self._pups[name] = {
                "pup_id":    pup_id,
                "gate":      gate,
                "token":     token,
                "connected_at": time.time(),
                "last_heartbeat": time.time(),
                "observations_sent": 0,
                "status":    "alive",
            }
            self._schedule_flush()
            return pup_id

    async def unregister(self, name: str):
        async with self._lock:
            self._pups.pop(name, None)
            pup_file = PUPS_DIR / f"{name}.json"
            pup_file.unlink(missing_ok=True)
            self._schedule_flush()

    async def heartbeat(self, name: str, uptime: float, obs_count: int):
        async with self._lock:
            if name in self._pups:
                self._pups[name]["last_heartbeat"] = time.time()
                self._pups[name]["uptime"] = uptime
                self._pups[name]["observations_sent"] = obs_count
            self._schedule_flush()

    async def increment_obs(self, name: str):
        async with self._lock:
            if name in self._pups:
                self._pups[name]["observations_sent"] = \
                    self._pups[name].get("observations_sent", 0) + 1

    def get_all(self) -> dict:
        return dict(self._pups)

    def _schedule_flush(self):
        self._write_q.append(True)

    async def flush_loop(self):
        """Background task: drain write queue → state.json."""
        while True:
            await asyncio.sleep(2)
            if self._write_q:
                self._write_q.clear()
                snapshot = {
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "pups": self._pups,
                }
                tmp = STATE_FILE.with_suffix(".tmp")
                tmp.write_text(json.dumps(snapshot, indent=2))
                tmp.replace(STATE_FILE)
                # per-pup files
                for name, rec in self._pups.items():
                    (PUPS_DIR / f"{name}.json").write_text(json.dumps(rec, indent=2))


registry = Registry()

# ---------------------------------------------------------------------------
# Log writer  (rolling 10k lines + size-based rotation at 50 MB)
# ---------------------------------------------------------------------------
_log_lock = asyncio.Lock()

async def append_log(entry: dict):
    async with _log_lock:
        line = json.dumps(entry) + "\n"
        CUR_LOG.parent.mkdir(parents=True, exist_ok=True)

        # size-based rotation
        if CUR_LOG.exists() and CUR_LOG.stat().st_size > 50 * 1024 * 1024:
            _rotate_log()

        with CUR_LOG.open("a") as f:
            f.write(line)

        # line-count rotation
        lines = CUR_LOG.read_text().splitlines()
        if len(lines) > MAX_LOG_LINES:
            _rotate_log()

def _rotate_log():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = ARCHIVE / f"{ts}.jsonl"
    CUR_LOG.rename(dest)
    log.info("Rotated log → %s", dest)

# ---------------------------------------------------------------------------
# Vault scribe (minimal — full scribe lives in cortex/scribe.py)
# ---------------------------------------------------------------------------
def vault_append_timeline(obs: dict):
    """Append a one-liner to today's timeline file."""
    try:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tfile = VAULT_BASE / "timeline" / f"{today}.md"
        if not tfile.exists():
            tfile.write_text(f"# Hellhound Timeline — {today}\n\n")
        ts_str  = datetime.fromtimestamp(obs.get("ts", time.time()),
                                         tz=timezone.utc).strftime("%H:%M:%S")
        pup     = obs.get("pup", "?")
        event   = obs.get("event", "?")
        domain  = obs.get("domain", "?")
        severity= obs.get("severity", "info")
        with tfile.open("a") as f:
            f.write(f"- `{ts_str}` **[{severity}]** `{pup}` → `{domain}/{event}`\n")
    except Exception as exc:
        log.warning("vault_append_timeline failed: %s", exc)

# ---------------------------------------------------------------------------
# Protocol handler  (one per connected pup)
# ---------------------------------------------------------------------------
class PupSession:
    HEARTBEAT_INTERVAL = 30   # seconds
    RECALL_TIMEOUT     = 5    # seconds pup has to exit after RECALL

    def __init__(self, reader, writer):
        self.reader  = reader
        self.writer  = writer
        self.name    = None
        self.pup_id  = None
        self.authed  = False

    async def run(self):
        try:
            await self._loop()
        except (asyncio.IncompleteReadError, ConnectionResetError):
            log.info("Pup %s disconnected", self.name or "<unknown>")
        finally:
            if self.name:
                await registry.unregister(self.name)

    async def _loop(self):
        while True:
            raw = await self.reader.readline()
            if not raw:
                break
            try:
                msg = json.loads(raw.decode().strip())
            except json.JSONDecodeError:
                await self._send({"error": "invalid json"})
                continue

            mtype = msg.get("type", "").upper()

            if mtype == "CONNECT":
                await self._handle_connect(msg)
            elif not self.authed:
                await self._send({"error": "not authenticated"})
            elif mtype == "OBSERVE":
                await self._handle_observe(msg)
            elif mtype == "HEARTBEAT":
                await self._handle_heartbeat(msg)
            else:
                await self._send({"error": f"unknown type: {mtype}"})

    async def _handle_connect(self, msg):
        name  = msg.get("name", "")
        gate  = msg.get("gate", "")
        token = msg.get("token", "")

        if not name or not gate:
            await self._send({"error": "name and gate required"})
            return

        # Token validation: token must match pre-provisioned value in pup file
        # or be accepted as new registration if file doesn't exist yet.
        pup_file = PUPS_DIR / f"{name}.json"
        if pup_file.exists():
            stored = json.loads(pup_file.read_text()).get("token", "")
            if not secrets.compare_digest(stored, token):
                await self._send({"error": "invalid token"})
                log.warning("AUTH FAIL: pup=%s", name)
                return
        else:
            # First registration — accept and persist
            if not token:
                await self._send({"error": "token required for first registration"})
                return

        self.name   = name
        self.authed = True
        self.pup_id = await registry.register(name, gate, token)
        log.info("PUP CONNECTED: %s (id=%s, gate=%s)", name, self.pup_id, gate)

        await self._send({
            "type":               "ACK",
            "pup_id":            self.pup_id,
            "recall_timeout":    self.RECALL_TIMEOUT,
            "heartbeat_interval": self.HEARTBEAT_INTERVAL,
        })

    async def _handle_observe(self, msg):
        obs = {
            "ts":       time.time(),
            "pup":      self.name,
            "domain":   msg.get("domain", "unknown"),
            "event":    msg.get("event", "unknown"),
            "severity": msg.get("severity", "info"),
            "payload":  msg.get("payload", {}),
        }
        await registry.increment_obs(self.name)
        await append_log(obs)
        _index_observation(obs)
        vault_append_timeline(obs)
        await self._send({"type": "ACK"})

    async def _handle_heartbeat(self, msg):
        uptime    = msg.get("uptime", 0)
        obs_count = msg.get("observations_sent", 0)
        await registry.heartbeat(self.name, uptime, obs_count)
        await self._send({"type": "ACK"})

    async def recall(self, reason: str = "shutdown", ref: str = ""):
        log.info("RECALL → %s (reason=%s)", self.name, reason)
        await self._send({"type": "RECALL", "reason": reason, "ref": ref})

    async def _send(self, obj: dict):
        self.writer.write((json.dumps(obj) + "\n").encode())
        await self.writer.drain()


# Global session map for RECALL-all
_sessions: dict[str, PupSession] = {}

async def handle_client(reader, writer):
    session = PupSession(reader, writer)
    # We don't know the name yet; we'll register after CONNECT
    _sessions[id(session)] = session
    await session.run()
    _sessions.pop(id(session), None)

# ---------------------------------------------------------------------------
# Graceful shutdown
# ---------------------------------------------------------------------------
async def shutdown(loop, signal_name):
    log.info("Received %s — recalling all pups", signal_name)
    for sid, sess in list(_sessions.items()):
        if sess.authed:
            await sess.recall(reason="shutdown", ref=signal_name)
    await asyncio.sleep(2)
    loop.stop()

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main():
    bootstrap_dirs()

    server = await asyncio.start_unix_server(handle_client, path=str(SOCK_PATH))
    os.chmod(SOCK_PATH, 0o600)
    log.info("Hellhound listening on %s", SOCK_PATH)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(loop, s.name))
        )

    async with server:
        await asyncio.gather(
            server.serve_forever(),
            registry.flush_loop(),
        )


if __name__ == "__main__":
    asyncio.run(main())

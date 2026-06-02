#!/usr/bin/env python3
"""
djinn-discord-watcher — polls #3d-printing for .stl/.3mf attachments,
calls djinn-model-fetch automatically. Runs as a systemd service.
"""

import os, sys, json, time, subprocess, pathlib, logging, urllib.request, re, datetime

# Keywords that indicate a commission request in plain text
COMMISSION_KEYWORDS = [
    "i want", "i need", "can you make", "can you print", "make me", "print me",
    "how much", "how much for", "quote", "order", "commission", "custom"
]

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

OC_CONFIG     = pathlib.Path.home() / ".openclaw/openclaw.json"
STATE_FILE    = pathlib.Path.home() / ".local/share/djinn/discord-watcher-state.json"
CHANNEL_ID    = "1507882513891065876"
POLL_INTERVAL = 20  # seconds
MODEL_EXTS    = {".stl", ".3mf"}
ALLOWED_USER  = "341840772582211587"  # Javier only


def load_token() -> str:
    cfg = json.loads(OC_CONFIG.read_text())
    return cfg["channels"]["discord"]["token"]


def load_state() -> dict:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_message_id": None, "processed": []}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def discord_get(path: str, token: str) -> dict:
    req = urllib.request.Request(
        f"https://discord.com/api/v10{path}",
        headers={"Authorization": f"Bot {token}", "User-Agent": "djinn-watcher/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fetch_new_messages(token: str, after_id: str | None) -> list[dict]:
    path = f"/channels/{CHANNEL_ID}/messages?limit=10"
    if after_id:
        path += f"&after={after_id}"
    try:
        msgs = discord_get(path, token)
        return sorted(msgs, key=lambda m: int(m["id"]))
    except Exception as e:
        log.error(f"fetch failed: {e}")
        return []


def run_model_fetch(url: str, label: str):
    log.info(f"Calling djinn-model-fetch for {label}: {url}")
    result = subprocess.run(
        ["djinn-model-fetch", url],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode == 0:
        log.info(f"Success: {result.stdout[-200:].strip()}")
    else:
        log.error(f"Failed ({result.returncode}): {result.stderr[-300:].strip()}")


def discord_send(token: str, text: str):
    """Send a message to the 3d-printing channel via Discord REST API."""
    data = json.dumps({"content": text}).encode()
    req = urllib.request.Request(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        data=data,
        headers={
            "Authorization": f"Bot {token}",
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (djinn-watcher, 1.0)",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        log.error(f"discord_send failed: {e}")


def process_message(msg: dict, token: str, processed: list) -> bool:
    msg_id = msg["id"]
    if msg_id in processed:
        return False

    # Skip bots and anyone other than Javier
    if msg.get("author", {}).get("bot"):
        return False
    if str(msg.get("author", {}).get("id", "")) != ALLOWED_USER:
        return False

    acted = False
    text = (msg.get("content") or "").strip()

    # File attachments (.stl / .3mf) — full intake pipeline
    for att in msg.get("attachments", []):
        fname = att.get("filename", "")
        ext = pathlib.Path(fname).suffix.lower()
        if ext in MODEL_EXTS:
            url = att["url"]
            # Check if caption contains customer prefs (e.g. "standard black" or "quality petg")
            fetch_args = [url]
            caption_lower = text.lower()
            for profile in ("production", "quality", "standard", "proto", "draft"):
                if profile in caption_lower:
                    mapped = {"quality": "production", "draft": "proto"}.get(profile, profile)
                    fetch_args += ["--profile", mapped]
                    break
            for color in ("black", "white", "grey", "gray", "red", "blue", "green", "orange", "yellow", "natural", "clear"):
                if color in caption_lower:
                    fetch_args += ["--color", color]
                    break
            if text and text != fname:
                fetch_args += ["--note", text[:200]]
            log.info(f"Found {ext} attachment: {fname}")
            try:
                result = subprocess.run(
                    ["djinn-model-fetch"] + fetch_args,
                    capture_output=True, text=True, timeout=600,
                )
                if result.returncode == 0:
                    log.info(f"Success: {result.stdout[-200:].strip()}")
                else:
                    log.error(f"Failed ({result.returncode}): {result.stderr[-300:].strip()}")
                acted = True
            except subprocess.TimeoutExpired:
                log.error(f"Timed out processing {fname}")
                discord_send(token, f"⏱️ Timed out analyzing `{fname}` — try again.")
            except Exception as e:
                log.error(f"Failed to process {fname}: {e}")
                discord_send(token, f"❌ Failed to process `{fname}`: {e}")

    # Plain text commission requests — no file attached
    if not acted and text:
        text_lower = text.lower()
        if any(kw in text_lower for kw in COMMISSION_KEYWORDS):
            log.info(f"Commission request detected: {text[:80]}")
            try:
                result = subprocess.run(
                    ["python3", "-c",
                     f"import sys; sys.path.insert(0, '{pathlib.Path.home()}/Obsidian/djinn/printer'); "
                     f"from shop.intake_agent import IntakeAgent; "
                     f"agent = IntakeAgent(); out = agent.parse('''{text.replace(chr(39), ' ')}'''); "
                     f"print(out)"],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0 and result.stdout.strip():
                    discord_send(token, result.stdout.strip()[:1900])
                else:
                    # Fallback: acknowledge and route to quote
                    discord_send(token,
                        f"Got it — I'll quote that for you.\n"
                        f"Use `/quote {text[:120]}` or drop your file in this channel."
                    )
                acted = True
            except Exception as e:
                log.error(f"Intake agent error: {e}")
                discord_send(token,
                    "Drop your `.stl` or `.3mf` file here and I'll analyze it instantly.\n"
                    "Or use `/quote <description>` for a quick estimate."
                )

    return acted


def main():
    log.info("djinn-discord-watcher starting")
    token = load_token()
    state = load_state()

    while True:
        try:
            msgs = fetch_new_messages(token, state["last_message_id"])
            for msg in msgs:
                process_message(msg, token, state["processed"])
                state["last_message_id"] = msg["id"]
                if msg["id"] not in state["processed"]:
                    state["processed"].append(msg["id"])
                # Keep only last 500 IDs
                state["processed"] = state["processed"][-500:]
            if msgs:
                save_state(state)
        except Exception as e:
            log.error(f"poll error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()

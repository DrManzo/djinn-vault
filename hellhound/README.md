# Hellhound

> Djinn's runtime monitor and pup supervisor.

Hellhound is a lightweight Unix-socket process supervisor and structured observation pipeline. It runs as a persistent daemon (`hellhound.py`), manages a fleet of specialized child processes called **pups**, and routes all observations into the Djinn vault and SQLite index.

---

## Architecture

```
hellhound (master)
├── skull.sock          Unix socket (chmod 600)
├── pup-gateway.py      Discord gateway pup
├── pup-<name>.py       Any additional pups
└── skull/
    ├── neurals/
    │   ├── state.json  Live registry snapshot
    │   └── index.db    SQLite observation index
    └── logs/
        └── current.jsonl
```

Each pup connects via `pup.py` (client lib), sends `OBSERVE` messages, and exits cleanly on `RECALL`.

---

## Quick Start

### 1. Install

```bash
# Install the CLI
cp hellhound/bin/hellhound ~/.local/bin/hellhound
chmod +x ~/.local/bin/hellhound

# Install runtime files
mkdir -p ~/.local/share/hellhound
cp hellhound/hellhound.py hellhound/pup.py hellhound/pup-template.py \
   hellhound/pup-gateway.py ~/.local/share/hellhound/

# Install Python packages (gates may need more)
pip install --user aiofiles
```

### 2. Install systemd units

```bash
mkdir -p ~/.config/systemd/user
cp hellhound/skull/hellhound.service \
   hellhound/skull/hellhound.socket \
   hellhound/skull/pup@.service \
   ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now hellhound.socket hellhound.service
```

### 3. Create and start a pup

```bash
hellhound pup new gateway
# Edit ~/.local/share/hellhound/pup-gateway.py
export HH_TOKEN=$(python3 -c "import json; print(json.load(open('~/.local/share/hellhound/skull/pups/gateway.json'))['token'])")
systemctl --user start pup@gateway
```

### 4. Monitor

```bash
hellhound status
hellhound log --tail 20
hellhound patrol
```

---

## Pup Protocol

| Direction | Message | Purpose |
|-----------|---------|--------|
| → | `CONNECT {name, gate, token}` | Register and authenticate |
| ← | `ACK {pup_id, recall_timeout, heartbeat_interval}` | Confirm registration |
| → | `OBSERVE {domain, event, payload, severity}` | Send observation |
| ← | `ACK` | Confirm receipt |
| → | `HEARTBEAT {uptime, observations_sent}` | Keepalive |
| ← | `ACK` | Confirm |
| ← | `RECALL {reason, ref}` | Master ordering pup to exit |

---

## Vault Output

All observations flow to `~/Obsidian/djinn/hellhound/`:

- `timeline/YYYY-MM-DD.md` — chronological log
- `gates/<pup>.md` — per-pup activity
- `incidents/` — watchdog anomalies
- `pups.md` — auto-generated registry summary

---

## Security Notes

- `skull.sock` is `chmod 600` — only the user running hellhound can connect.
- Each pup is provisioned a `token` at creation (`hellhound pup new <name>`).
- Tokens are stored in `skull/pups/<name>.json` and compared with `secrets.compare_digest`.
- Never commit `skull/pups/*.json` — it is in `.gitignore`.

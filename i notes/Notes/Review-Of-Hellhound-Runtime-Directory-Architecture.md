---
subject: djinn/Runtime Directory
tags:
  - cs/architecture/design
  - cs/runtime-management
  - personal/development-tools
created: 2026-06-14
source: Perplexity export
---

# Review of Hellhound Runtime Directory Architecture

## Summary
The architecture for the Hellhound runtime directory is well-thought-out and practical, designed to manage various components like CLI entry points, sockets, logs, and services. The design is coherent and production-ready.

## Key Points
- **Cohesive Naming:** Hellhound → skull → pups → neurals → logs → cortex → effector → gates.
- **Systemd Integration:** Services for socket activation and pup management.
- **CLI Interface:** Comprehensive commands for managing the runtime environment.
- **Vault Management:** Structured logging and observation tracking.

## Details
The architecture includes a well-defined directory structure that supports various functionalities:

### Directory Structure

```
├── hellhound/  # CLI entry point (shell wrapper)
│   ├── skull/  # Data + services
│   │   ├── skull.sock  # Unix socket for communication
│   │   └── pups/  # Per-pup state files
│   │       └── {name}.json  # Pup metadata
│   ├── neurals/  # Live snapshot and SQLite database for cross-references
│   ├── logs/  # Rolling log files and archive
│   ├── cortex/  # Hellhound-side processing (imported by master)
│   │   ├── synapsis.py  # Cross-references observations to vault
│   │   ├── linker.py  # Generates backlinks between related entries
│   │   ├── watchdog.py  # Anomaly detection, health patrol
│   │   └── commander.py  # Writes commands → QUEUE.md
│   ├── effector/  # Output actions (writes structured notes to vault)
│   │   ├── scribe.py  # Writes structured notes
│   │   ├── alerter.py  # Routes alerts through appropriate gate
│   │   └── archiver.py  # Log rotation, index compaction
│   ├── gates/  # Protocol handlers (library, imported by pups)
│   │   ├── base.py  # Abstract gate for connection, observation, and disconnection
│   │   ├── discord.py  # REST + Gateway for Discord
│   │   ├── telegram.py  # Telegram bot listener
│   │   ├── moonraker.py  # Moonraker REST + WebSocket
│   │   ├── network.py  # ICMP/ARP probes, port scans
│   │   └── vault.py  # Filesystem watcher for vault changes
│   ├── hellhound.py  # Master: socket server + registry + auth + cortex
│   ├── pup.py  # Pup client library (imported by every pup)
│   └── pup-template.py  # Template to create new pups
├── systemd/  # Systemd service files for skull and pup management
    ├── skull/
    │   ├── hellhound.service  # Binds to Hellhound socket activation?
    │   └── hellhound.socket  # Socket activation for skull.sock
    └── pup@.service  # Template unit for pup services
```

### CLI Interface

- `hellhound status`: Registry dump + health per pup.
- `hellhound send pup <name>`: Starts a specific pup service.
- `hellhound recall pup <name>`: Recalls and stops the specified pup.
- `hellhound recall --all`: Recalls all registered pups.
- `hellhound log [--tail N]`: Tails current.jsonl logs.
- `hellhound patrol`: Runs watchdog checks, reports to vault.

### Vault Management

- `~/Obsidian/djinn/hellhound/` directory for structured observations and backlinks.
  - `_index.md`: Master MOC with backlinks to every gate.
  - `pups.md`: Auto-generated list of active pups, uptime, events today.
  - `timeline/YYYY-MM-DD.md`: Chronological logs of observations.
  - `gates/`: Per-gate activity logs.
  - `incidents/`: Watchdog anomalies.
  - `reports/`: Health reports.

### Pup Protocol

- **Connection:** `CONNECT { "name": "gateway", "gate": "discord-dm", "token": "..." }`
- **Observation:** `OBSERVE { "domain": "comms", "event": "msg_routed", "payload": {...}, "severity": "info" }`
- **Heartbeat:** `HEARTBEAT { "uptime": 3600, "observations_sent": 142 }`
- **Recall:** `RECALL { "reason": "security_update", "ref": "2026-06-10_vuln-patch" }`

## References
- https://math.mit.edu/~djk/calculus_beginners/chapter00/section02.html

## Related
- [[Faust-Component-Based-Architecture-Specification]] — architecture-similarity
- [[Faust-Cli-Core-Adapters]] — CLI-interface-comparison

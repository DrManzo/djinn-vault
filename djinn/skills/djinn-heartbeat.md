# Skill: djinn-heartbeat

**Owner:** Salomon + Typhon (each runs their own)  
**Purpose:** Write system health to vault every 5 minutes  
**Status:** ✅ Active  

## Triggers

- Salomon: `heartbeat.timer` (systemd, 5-min) → `~/.local/bin/heartbeat`
- Typhon: `heartbeat-typhon.timer` (systemd, 5-min) → `~/.local/bin/heartbeat-typhon`

## Inputs

- `nvidia-smi` — GPU name, temp, utilization, memory
- `ollama list` — model count
- `uptime -p` — system uptime
- `df -h /` — disk usage
- `free -h` — RAM usage

## Steps

1. Collect: timestamp (UTC), uptime, GPU info, Ollama model count, disk, RAM
2. Write to `~/Obsidian/djinn/communications/HEARTBEAT.md` (Salomon) or `HEARTBEAT-typhon.md` (Typhon)
3. `cd ~/Obsidian && git add && git commit -m "heartbeat: ..." && git push`

## Outputs

- HEARTBEAT.md or HEARTBEAT-typhon.md — overwritten each beat
- git commit on each beat

## Dependencies

- `nvidia-smi` — NVIDIA GPU stats
- `ollama` — model list
- `git` — commit + push
- systemd user timers (5-min interval)

## Implementation

```bash
~/.local/bin/heartbeat        # Salomon
~/.local/bin/heartbeat-typhon  # Typhon
```

---

*— Claude*

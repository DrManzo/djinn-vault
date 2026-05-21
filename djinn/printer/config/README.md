---
subject: Printer Queue System
tags: [djinn, printer]
created: 2026-05-21
---

# Djinn Printer Node

Ender-3 V3 Plus controlled via Moonraker API through Typhon.

## Directory Structure

```
djinn/printer/
├── config/         — printer settings, profiles
├── queue/          — pending print jobs
├── active/         — current job (one file max)
├── completed/      — job history + logs
└── models/         — STL references + sources
```

## Job Frontmatter

Every job note uses this format:

```yaml
---
job_id: print_001
file: bracket_v2.stl
status: queued | printing | done | failed
material: PLA
profile: default
estimated_time: 2h30m
submitted: 2026-05-21T14:00
completed:
notes:
---
```

## Telegram Commands

| Command | Action |
|---------|--------|
| `/print <filename>` | Queue a job |
| `/print_status` | Active job + % complete |
| `/print_cancel` | Kill active job |
| `/print_queue` | List pending jobs |
| `/print_log` | Last 5 completed jobs |

## Setup Checklist

- [ ] Connect printer to local WiFi (via touchscreen Settings → WiFi)
- [ ] Note printer IP from router or printer screen
- [ ] Add IP to `~/.config/djinn/printer.conf` on Typhon and Salomon
- [ ] Test Moonraker: `curl http://<printer-ip>:7125/api/printer`
- [ ] Buy: flush cutters, spare 0.4mm nozzles (pack), IPA 90%+
- [ ] Build enclosure before first print (cat safety)
- [ ] Wire Telegram commands via OpenClaw workflow

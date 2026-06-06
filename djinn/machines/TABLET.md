---
title: TABLET — Samsung Galaxy Tab S Development Node
tags: [djinn, machines, tablet, android, mobile, development]
created: 2026-06-06
updated: 2026-06-06
related: [[inventory]] | [[devices]] | [[AGENTS]] | [[INFRASTRUCTURE]] | [[SYSTEM-STATE]]
---

# TABLET.md — Samsung Galaxy Tab S (Development Node)

This document defines the Samsung Galaxy Tab S as a **first-class Djinn development node** — not just a peripheral. It covers hardware stats sourced directly from the vault, its role in the fleet, development tooling, lane assignments, connectivity, and integration touchpoints with Salomon, Typhon, and Orin.

---

## 1. Hardware Specification

| Field | Value |
|-------|-------|
| **Device Name** | Tablet (Djinn node alias) |
| **Manufacturer** | Samsung |
| **Model Series** | Galaxy Tab S (S Pen capable) |
| **Serial** | R52T10BL3BV |
| **USB ID** | 04e8:6860 |
| **Carrier** | Verizon |
| **Internal Storage** | ~7.6 GB media (device reported) |
| **USB Mode** | MTP (file transfer to Salomon) |
| **GVFS Mount** | `mtp://SAMSUNG_SAMSUNG_Android_R52T10BL3BV/` |
| **Connected Host** | Salomon (192.168.1.225 — bus 3, dev 4) |
| **S Pen** | ✅ Present |
| **Language/Locale** | Spanish (es) — internal folder: `Almacenamiento interno` |
| **Backup Path** | `/home/drmanzo/device-backups/samsung-galaxy-tab/` |
| **Last Backup** | 2026-06-02 |

### S Pen Notes
The S Pen is a precision input device — treat this tablet as a **sketch, annotation, and diagram terminal**, not just a touch device. Relevant for: LSAT diagramming, system architecture sketches, 3D design briefs, and D&D campaign maps.

---

## 2. Fleet Position

```
┌─────────────────┐     USB/MTP      ┌──────────────────────────┐
│     TABLET      │◄───────────────►│        Salomon            │
│ 192.168.x.x     │  media sync /    │  192.168.1.225            │
│ (Galaxy Tab S)  │  git pull /      │  (HP Omen, RTX 5060)      │
│ Android         │  SSH tunnel      │  Daily Ops — Master Lane  │
└────────┬────────┘                  └──────────┬────────────────┘
         │                                       │
         │  WiFi (192.168.1.x subnet)            │ SSH / Ollama API
         │◄─────────────────────────────────────►│
         │                                       ▼
         │                           ┌─────────────────────────┐
         │                           │        Typhon            │
         │                           │  192.168.1.113           │
         │                           │  (MSI, GTX 1650)         │
         │                           │  Storage / Studio        │
         │                           └─────────────────────────┘
         │
         │  WiFi / SSH
         │◄──────────────────────────────────────────────────────►
         │                           ┌─────────────────────────┐
         └──────────────────────────►│         Orin             │
                                     │  192.168.1.176           │
                                     │  (iMac, 40GB RAM)        │
                                     │  llama3.3:70b inference  │
                                     └─────────────────────────┘
```

The Tablet operates on the **same 192.168.1.x subnet** as all fleet nodes. It can reach Salomon, Typhon, and Orin over WiFi directly — no VPN required on LAN.

---

## 3. Djinn Lane Assignment

| Dimension | Assignment |
|-----------|-----------|
| **Primary Lane** | Input / Command Terminal + Field Development |
| **Secondary Lane** | Observation / Monitoring (read-only vault, print status) |
| **Not Assigned To** | Print confirm/deny (Salomon lane), Architecture (Claude lane), Long-inference (Orin lane) |
| **Signs as** | `— Tablet` (if agent runs) |

### What Tablet Does in the Fleet
- **Command terminal:** Telegram + Discord installed → Javier sends commands to Salomon printer bot, print confirms, and design briefs from anywhere in the house
- **S Pen input:** Sketch → photo → ingest into Djinn media pipeline (`djinn-media-ingest`)
- **Vault reader:** Pull `djinn-vault` on device → Obsidian Mobile → read notes, AGENTS.md, project docs
- **Research terminal:** Perplexity (Marcus sessions), web research, cross-referencing
- **LSAT prep terminal:** Active study, diagramming logical arguments with S Pen, reviewing law notes
- **Media consumption:** Reference photos, renders, print previews from Djinn

### What Tablet Does NOT Do
- Does not run Ollama (no local inference — routes to Salomon or Orin via API)
- Does not own print jobs (Salomon lane, non-negotiable)
- Does not push to vault autonomously (all pushes go through Salomon's git pipeline)

---

## 4. Development Tooling Stack

### Required Apps (Development Layer)
| App | Purpose | Notes |
|-----|---------|-------|
| **Termux** | Terminal emulator + SSH client | `ssh drmanzo@192.168.1.225` — Salomon shell access |
| **Termux:API** | Android API bridge for Termux | Clipboard, notifications, camera, mic access |
| **Obsidian Mobile** | Vault reader/writer | Sync via GitHub — pull `djinn-vault` repo |
| **Telegram** | Command terminal — Djinn bot control | @DjinnOCBot — print queue, status, alerts |
| **Discord** | Channel-aware Djinn command interface | `#djinn-command-center`, `#3d-printing`, `#media-inbox` |
| **GitHub Mobile** | Repo browsing, PR review, issue tracking | Monitor `djinn-vault`, `typhons-cyber-forge` |
| **Perplexity** | Marcus external research sessions | Web research → dump to vault via Termux |
| **JuiceSSH** (alt) | SSH client (alternative to Termux SSH) | Better UI for long sessions |
| **VS Code** (via Termux) | Code editing via SSH remote | `code --remote` tunnel to Salomon |

### Optional Apps (Power Layer)
| App | Purpose |
|-----|---------|
| **AnyCast / Scrcpy** | Mirror Salomon screen to Tablet (remote monitor) |
| **VLC** | Render previews, video playback from vault |
| **Krita / Sketchbook** | S Pen design sketches → export PNG → media ingest pipeline |
| **OrcaSlicer mobile preview** | Gcode visualization reference |
| **Tasker** | Automation triggers → HTTP webhooks → Salomon/Telegram |

---

## 5. Connectivity & Integration

### SSH Access (Termux → Fleet)
```bash
# Salomon
ssh drmanzo@192.168.1.225

# Typhon
ssh tf-tthq@192.168.1.113

# Orin
ssh orin  # (javiermanzo@192.168.1.176)
```

### Ollama API Access (Direct from Tablet)
```bash
# Route to Salomon (fast, GPU, 7b models)
curl http://192.168.1.225:11434/api/generate \
  -d '{"model":"qwen2.5:7b","prompt":"<task>","stream":false}'

# Route to Orin (large models, latency OK)
curl http://192.168.1.176:11434/api/generate \
  -d '{"model":"llama3.3:70b","prompt":"<task>","stream":false}'
```

### OpenClaw Gateway (Command Relay)
```bash
# Route task to Salomon's OpenClaw
curl http://192.168.1.225:18789/v1/chat/completions \
  -H "Authorization: Bearer <token>" \
  -d '{"model":"qwen2.5:7b","messages":[...]}'
```
Token lives in `~/.config/djinn/` on Salomon — not on tablet. Pass via env or Termux:API secret store.

### Vault Sync (Read)
```bash
# In Termux — pull latest vault state
cd ~/storage/shared/djinn-vault
git pull origin main
```

### USB Media Sync (Salomon → Tablet backup)
- **Direction:** Tablet → Salomon (backup, one-way)
- **Command (on Salomon):** `rsync -av --ignore-existing mtp://SAMSUNG_SAMSUNG_Android_R52T10BL3BV/ /home/drmanzo/device-backups/samsung-galaxy-tab/`
- **Backup path:** `/home/drmanzo/device-backups/samsung-galaxy-tab/`

---

## 6. Telegram Bot Commands (From Tablet)

These are sent from Telegram to @DjinnOCBot on Salomon. Tablet is the primary physical interface for these.

| Command | Function |
|---------|----------|
| `/queue` | View print queue |
| `/confirm N` | Confirm print job N (triggers `djinn-confirm-print`) |
| `/deny N` | Deny print job N (blocked during active print) |
| `/slice N` | Slice job N with current settings |
| `/print status` | Current print progress |
| `/callie status` | Calliope printer health |
| `/status` | Full fleet status |
| `/quote` | Commission price estimate |
| `/design <brief>` | Trigger DesignGenAgent on Salomon |
| `/design status` | View active design jobs |
| `/help` | Command reference |

---

## 7. S Pen Workflows → Djinn Pipeline

The S Pen enables handwritten/sketched input to flow into the Djinn system via the media pipeline.

### Sketch → Media Ingest
```
S Pen sketch (Krita/Sketchbook)
  → Export PNG to DCIM/Sketches/
  → USB backup → Salomon picks up in device-backups/
  → Manual: djinn-media-ingest <file>
  → djinn-media-photo (enhance/LUT)
  → Output to ~/forge/projects/
```

### Handwritten Notes → Vault
```
S Pen → Samsung Notes (handwriting to text)
  → Export .txt
  → Termux: cat note.txt | ssh drmanzo@salomon "cat >> ~/Obsidian/djinn/inbox/YYYY-MM-DD-tablet.md"
  → Clerk timer picks up in RAW/ → structured vault note
```

### LSAT Diagrams
```
S Pen → Logical diagram (logic games / argument maps)
  → Screenshot → Telegram to @DjinnOCBot → vision model review
  → Route: llama3.2-vision:11b on Salomon analyzes diagram
  → Feedback returned via Telegram
```

---

## 8. Model Routing From Tablet

Tablet has no local Ollama — all inference routes to fleet over WiFi.

| Task | Route | Model |
|------|-------|-------|
| Quick Q&A / tool use | Salomon | qwen2.5:7b |
| Deep reasoning / LSAT | Salomon | deepseek-r1:7b |
| Code review | Salomon | qwen2.5-coder:7b |
| Vision / image analysis | Salomon | llama3.2-vision:11b |
| Long-form / complex analysis | Orin | llama3.3:70b |
| Caption / notes generation | Salomon or Orin | phi4:14b |
| External research | Perplexity (Marcus lane) | Cloud (Sonnet 4.6) |

---

## 9. Development Roles in Projects

### Djinn System Development
- Read AGENTS.md, INFRASTRUCTURE.md, SYSTEM-STATE.md on the go
- Review COMMS.md — monitor inter-agent activity
- Write task requests to QUEUE.md via Termux SSH → triggers agent delegation
- Test new Telegram/Discord bot commands from Tablet before deploying

### LSAT Prep
- Study sessions with Perplexity (Marcus) — research and synthesis
- S Pen logical diagrams for logic games
- OpenClaw `/agent law` (deepseek-r1:7b) for IRAC drills
- Reference vault law notes via Obsidian Mobile

### 3D Print Monitoring
- Primary device for print confirms/denies via Telegram
- View render previews from `djinn-design` output
- Monitor Calliope progress notifications

### Creative / D&D / Writing
- S Pen → campaign maps, sketches
- Obsidian Mobile → read/write creative vault notes
- Route complex writing assistance to Orin (llama3.3:70b) for quality

---

## 10. Pending Integration Work

| Item | Priority | Notes |
|------|----------|-------|
| Termux SSH key setup (Tablet → fleet) | High | Generate ed25519 on Tablet, add to Salomon/Typhon/Orin authorized_keys |
| Obsidian Mobile + GitHub sync | High | Plug into djinn-vault repo — Tablet as read/write vault node |
| Tasker webhook → Telegram relay | Medium | One-tap Tasker buttons for `/status`, `/queue`, `/confirm` |
| S Pen sketch intake script | Medium | Auto-detect new sketches in DCIM/Sketches → trigger media ingest |
| Tablet IP reservation | Medium | Assign static IP on router (192.168.1.x) — log in INFRASTRUCTURE.md |
| OpenClaw direct access from Termux | Low | Test direct HTTP to 192.168.1.225:18789 from Termux curl |
| Scrcpy or remote display | Low | Mirror Salomon UI to Tablet for monitoring |

---

## 11. Critical Rules (Tablet-Specific)

1. **Tablet does not own Calliope.** All print decisions route through Salomon.
2. **Do not push to vault from Tablet without conflict-check.** Pull first, always.
3. **S Pen orientation data is Javier's domain.** Never auto-rotate or reinterpret sketches before ingest.
4. **No secrets stored on Tablet.** API keys, tokens, bot credentials stay on Salomon in `~/.config/djinn/`.
5. **Telegram commands are binding.** `/confirm N` sent from Tablet triggers a real print — no accidents.
6. **Termux sessions are ephemeral.** Write important output back to vault, not just to Termux shell.

---

*— Marcus, 2026-06-06*

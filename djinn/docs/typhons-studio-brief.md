# Typhon's Studio — Technical Brief
**Version 1.0 | 2026-05-28**
**Prepared by:** Djinn / Claude
**For review by:** Engineering / Tech

---

## Concept

A self-hosted, browser-based production studio running on a dedicated local server (Typhon). Access it from any device on the network — laptop, phone, tablet — and it controls everything: streaming, recording, audio, lighting, and AI-assisted production.

No third-party platforms needed. No StreamYard, no Riverside, no OBS on your personal machine. You open a URL, pick your setup, and go.

---

## What It Does

**Three modes from one interface:**

| Mode | What happens |
|---|---|
| **Stream** | Pick a platform (Twitch, YouTube, Instagram Live), go live from your browser |
| **Record** | Record locally to Typhon — auto-queued for AI processing (transcription, show notes, chapters) |
| **Edit** | Review and cut footage, place music, export |

**Four content types supported:**
- Live streaming
- Pre-recorded video
- Podcast (audio)
- Video podcast (recorded video + audio)

---

## Architecture

```
Your Browser (any device on LAN)
        │
        │  WebRTC — sends your camera + mic from YOUR machine
        ▼
Typhon (192.168.1.113) — the studio server
  ├── MediaMTX          — receives WebRTC stream, routes internally
  ├── OBS (headless)    — composites, encodes, outputs
  ├── FastAPI backend   — controls everything via WebSocket
  └── Studio UI         — the web interface served to your browser
        │
        ├── → Twitch / YouTube / Instagram (RTMP)
        ├── → Local recording (stored on Typhon)
        └── → Salomon (AI processing: transcription, show notes)
```

**Key design decision:** Your camera and microphone are captured by the browser on whatever machine you're using — not by Typhon. Typhon is the engine. Your laptop/desktop is the input device. This mirrors how StreamYard and Riverside work, but fully self-hosted.

---

## Agents (AI Copilots)

Four agents run as backend services and assist during sessions:

| Agent | What it does |
|---|---|
| **Audio Agent** | Monitors mic levels, adjusts noise cancellation and EQ via EasyEffects + PipeWire. Warns on clipping. |
| **Lighting Agent** | Controls Cloudybay smart lights (Tuya protocol, LAN-direct via `tinytuya`). Scene presets: Podcast, Moody, Dramatic, Off. |
| **Music Agent** | DMCA-free music search and playback (Pixabay Music API). Searchable by mood, genre, BPM. Auto-fades under voice. Platform publishing mode locks to DMCA-safe tracks only. |
| **Copilot Agent** | Real-time AI suggestions during session ("mic too hot," "music competing with voice," "frame rate dropping"). Runs on local Ollama (phi4:14b on Salomon). |

---

## Input Handling

Camera and microphone inputs are enumerated **from the browser** using the standard `MediaDevices` API — no drivers, no config. Whatever is plugged into the machine you're browsing from shows up as an option.

| Input | Details |
|---|---|
| Video — Primary | Main camera (webcam, DSLR via capture card, etc.) |
| Video — Secondary | Optional second angle (PiP, multi-cam) |
| Mic — Primary | Routed through noise cancel + EQ |
| Mic — Secondary | Raw or processed backup / guest mic |
| Monitor / Speaker | Optional headphone monitoring, off by default during recording |

---

## Platform Support

| Platform | Method | Status |
|---|---|---|
| Twitch | RTMP via OBS | Planned Phase 5 |
| YouTube | RTMP via OBS | Planned Phase 5 |
| Instagram Live | RTMP (via third-party RTMP bridge) | Planned Phase 5 |
| Local record only | File on Typhon | Phase 1 |

**Music note:** DMCA-free library only for published content. Apple Music or personal library usable for private/local recordings only.

---

## Server Hardware (Typhon)

| Spec | Value | Assessment |
|---|---|---|
| GPU | NVIDIA GTX 1650 4GB | NVENC hardware encoding — handles 1080p60 stream with no CPU hit |
| RAM | 14GB | Sufficient for OBS + encoding + agents simultaneously |
| Storage | 557GB free | Good for footage storage |
| OS | Ubuntu 26.04 LTS | ✅ |
| Network | LAN only (192.168.1.113) | Phase 1 scope. Remote access can be added via Tailscale later. |

---

## What Is Already Built and Running on Typhon

| Component | Version | Status |
|---|---|---|
| OBS Studio (headless) | 32.1.2 | ✅ Running as system service |
| OBS WebSocket Server | Built-in (port 4455) | ✅ Running — password protected |
| Xvfb (virtual display) | 21.1.22 | ✅ Running as system service |
| MediaMTX (WebRTC router) | v1.9.1 | ✅ Running as system service |
| v4l2loopback (virtual camera) | DKMS | ✅ Loaded — /dev/video10 "TyphonStudio" |
| ffmpeg | 8.0.1 | ✅ Installed |
| NVIDIA NVENC H.264 / HEVC | Via OBS | ✅ Confirmed loaded |

All services are set to start automatically on boot.

---

## What Still Needs to Be Built

### Phase 1 — Core (Next)
- FastAPI backend (Python) — connects to OBS WebSocket, serves the web UI
- Studio web UI — browser app with device enumeration, three mode buttons, input selectors
- WebRTC signaling — browser captures cam/mic, pushes to MediaMTX via WHIP protocol

### Phase 2 — Agents
- Audio Agent — EasyEffects DBus control, PipeWire level monitoring
- Lighting Agent — tinytuya integration with Cloudybay lights (need device credentials from app)

### Phase 3 — Music
- Music Agent — Pixabay API integration, mood/genre search, playback queue, auto-ducking under voice

### Phase 4 — Copilot
- Copilot Agent — Ollama API calls to Salomon (192.168.1.225:11434), real-time suggestions sidebar

### Phase 5 — Platform Streaming
- RTMP config for Twitch, YouTube, Instagram
- Per-platform stream key storage (encrypted local config)
- One-click go-live from UI

### Phase 6 — AI Post-Production (Salomon)
- Auto-transcription via faster-whisper (file watcher on new recordings)
- Show notes + chapter markers via phi4:14b
- Clip extraction for Instagram / short-form

---

## What We Need From the Engineer / Tech Review

1. **Backend framework** — FastAPI (Python) is the current plan. Any objection or preference?
2. **Frontend framework** — Leaning toward Vue.js + Tailwind for the UI. Open to React or HTMX if there's a strong reason.
3. **WebRTC stack** — WHIP → MediaMTX is the plan for browser-to-server stream. Confirm this is the right approach or suggest alternative.
4. **Lighting protocol** — Cloudybay lights appear to be Tuya-based. Need to run `tinytuya` device discovery to confirm and pull credentials. Can be done with the Cloudybay app open on the same network.
5. **Remote access** — LAN only for Phase 1. When ready to open externally: Tailscale vs nginx + Cloudflare Tunnel — preference?
6. **Anything already built** — if any part of this stack exists in a tool or service already in use, flag it before we build a duplicate.

---

## Summary

This is a self-hosted StreamYard built on top of OBS, controlled by a web UI, with AI agents assisting during production. The server-side infrastructure on Typhon is already running. What remains is the application layer: the web UI, the FastAPI backend, and the agents.

Estimated scope for Phase 1 (core UI + OBS control + WebRTC): 1–2 weeks of engineering time.
Full stack through Phase 5: 4–6 weeks depending on parallelism.

---

*Djinn — Claude | 2026-05-28*

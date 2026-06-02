# Session Report — Social Studio Pipeline Build
**Date:** 2026-06-01
**Session:** djinn-social v0.1 build
**Author:** Claude

---

## Summary
Built the complete multi-brand social content studio pipeline from scratch, implementing all 18 sections of TASK-061. The `djinn-social` Python package is installed, CLI is live, and systemd timers are enabled. The pipeline takes iPhone media from inbox → 9:16 reel → platform-specific captions → publish to IG/FB/YouTube/X. Cloudflare Tunnel chosen for Meta video hosting (permanent HTTPS URL, no session limits).

---

## What Was Built/Changed

### New Project: `~/projects/djinn-social/`
Full Python package with the following modules:

| Module | Purpose |
|--------|---------|
| `djinn/__init__.py` | XDG path constants |
| `djinn/brands.py` | BrandConfig dataclass, SQLite DB layer, episode/week math |
| `djinn/media/ingest.py` | HEIC→JPEG, HEVC→H.264, inbox scanner |
| `djinn/media/reel.py` | 9:16 ffmpeg pipeline, cover extraction, subtitle burn-in |
| `djinn/media/transcribe.py` | faster-whisper with VAD filter |
| `djinn/media/caption.py` | Ollama caption generation, cannabis-safe rules hardcoded |
| `djinn/publish/meta.py` | Instagram 3-step container flow + Facebook Reels |
| `djinn/publish/youtube.py` | Resumable YT Shorts upload, thumbnail set |
| `djinn/publish/x.py` | v1.1 media + v2 tweet, chunked upload, processing poll |
| `djinn/hosting.py` | Cloudflare Tunnel HTTP server (replaces ngrok) |
| `djinn/scheduler.py` | 15-min timer runner, kit_ready → publish |
| `djinn/tokens.py` | IG long-lived token refresh (60-day cycle) |
| `djinn/cli.py` | Click CLI: 9 commands |
| `djinn/utils.py` | Retry decorator with exponential backoff |

### Brand Configs Deployed
- `~/.config/djinn/brands/terp-tribe.json` — Season 6, full Mon–Sun schedule with themes/tones/opening patterns
- `~/.config/djinn/brands/typhon-forge.json` — Season 1, Mon–Sun maker content schedule

### Publish Schedule
- `~/.config/djinn/publish-schedule.json` — TT: 10:00–12:00, TF: 11:00–14:00

### SystemD Units Installed and Enabled
- `djinn-publish-scheduler.timer` — fires every 15 min, enabled
- `djinn-token-refresh.timer` — fires monthly (1st of month 06:00), enabled
- `djinn-cf-tunnel.service` — Cloudflare Tunnel for port 8741 (not started — needs CF setup first)

---

## Technical Decisions

**Cloudflare Tunnel over ngrok:** Permanent URL, free tier, no session limits, runs as a persistent systemd service. ngrok free tier has session limits and rotating URLs — not viable for automated publishing.

**Hosting module design:** The CF tunnel is always-on as a systemd service. `start_temp_server()` only starts the local HTTP server thread; the tunnel is assumed running. `stop_temp_server()` shuts down the local server after Meta fetches the file.

**`os.chdir()` removed from HTTP server:** The spec used `os.chdir(directory)` — a global state mutation that breaks in threaded contexts. Replaced with `functools.partial(_DirectoryHandler, directory=directory)` which passes the directory to the handler without changing the process cwd.

**Python 3.14 compatibility:** Build backend was `setuptools.backends.legacy` (Python 3.13+). Changed to `setuptools.build_meta` for 3.14 compatibility.

**`content-set-status` command added:** The spec referenced `djinn content-day-set-status` in the run sequence (Section 16) but didn't include it in the CLI section. Added as `content-set-status` — reads brand from `brand_context.json`, updates DB row.

---

## Files Created/Modified

**New:**
- `~/projects/djinn-social/` — full package (initial commit)
- `~/.config/djinn/brands/terp-tribe.json`
- `~/.config/djinn/brands/typhon-forge.json`
- `~/.config/djinn/publish-schedule.json`
- `~/.config/djinn/hosting.env` (placeholder — needs real CF URL)
- `~/.config/systemd/user/djinn-publish-scheduler.{service,timer}`
- `~/.config/systemd/user/djinn-cf-tunnel.service`
- `~/.config/systemd/user/djinn-token-refresh.{service,timer}`

---

## Tests & Validation
- `djinn --help` → all 9 commands listed ✓
- `djinn-media-ingest --help` → flags correct ✓
- Package installs cleanly in Python 3.14 venv ✓
- CLI imports all modules without error ✓
- Cannot test actual publishing without API credentials

---

## Known Issues
1. **Cloudflare Tunnel not configured** — `hosting.env` has placeholder URL. Needs `cloudflared tunnel login && tunnel create djinn-media && tunnel route dns`. Then update `DJINN_MEDIA_BASE_URL`.
2. **TF day themes are placeholders** — Typhon's Forge Mon–Sun names invented. Javier must confirm actual weekly theme names before content starts.
3. **TT Season 6 start date** — set to `2026-06-01`. Confirm if this is the actual start date for week_in_season calculations.
4. **No API credentials yet** — All 4 platforms need creds before publish chain works. See Section 17 of TASK-061.
5. **Meta App Review** — 2–4 week wait for non-test accounts. Start immediately if posting to real IG accounts.
6. **YouTube OAuth** — One-time browser setup required: `python scripts/youtube_oauth_setup.py`.

---

## What's Next
1. Cloudflare Tunnel setup (cloudflared install + tunnel create + DNS)
2. Confirm Typhon's Forge weekly day names → update `typhon-forge.json`
3. Confirm Terp Tribe Season 6 start date
4. Fill in `meta-terp-tribe.env` with IG credentials
5. `djinn-content-day-init --brand terp-tribe --setup` (initialize DB)
6. Drop test file in `~/djinn-media-inbox/` and run `djinn-media-ingest --brand terp-tribe` for first dry run

— Claude

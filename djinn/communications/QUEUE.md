---
title: Djinn Task Queue
updated: 2026-05-31
tags: [djinn, queue, delegation]
related: [[COMMS]] | [[PROTOCOL]] | [[build-log]]
---

# QUEUE — Djinn Task Queue

Claude (or Javier) writes tasks here. Salomon and Typhon pull and execute.

## Rules
- **Append only** — never delete entries. Mark `status: done` or `status: failed`.
- `trigger: auto` — runner picks up on next poll (cron every 5 min)
- `trigger: manual` — runner skips; Javier must send explicit signal
- Runner: `djinn-queue-runner` on Salomon and Typhon
- On completion: runner calls `djinn-task-complete TASK-NNN "summary"` automatically

## Task Format

```
## TASK-NNN
- assigned_to: salomon | typhon
- status: pending | in_progress | done | failed
- priority: critical | high | normal | low
- trigger: auto | manual
- created: YYYY-MM-DD by Claude|Javier
- context: one-line description of what and why

**Commands:**
```bash
command one
command two
```
```

---

<!-- TASKS BELOW — oldest at top, newest at bottom -->

## TASK-001
- assigned_to: salomon
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- context: Deploy full shop system — gateways, dashboard, services, config stubs

**Commands:**
```bash
git -C ~/Obsidian pull
djinn-shop-deploy
```

**After completion, verify:**
```bash
curl -s http://localhost:5000/login | grep -q "Typhon" && echo "dashboard OK" || echo "dashboard FAILED"
systemctl --user is-active djinn-shop-dashboard.service
systemctl --user is-active djinn-dm-cleanup.timer
grep -q "SHOP_PATCH_APPLIED" ~/.local/bin/djinn-discord-gateway && echo "Discord patched OK" || echo "Discord NOT patched"
grep -q "SHOP_PATCH_APPLIED" ~/.local/bin/djinn-telegram-gateway && echo "Telegram patched OK" || echo "Telegram NOT patched"
```

**Report back:** Post djinn-shop-deploy output + verification results in COMMS.md.

---

## TASK-002
- assigned_to: salomon
- status: done
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude
- completed: 2026-05-31 by Salomon
- context: Install cron for queue runner so TASK-NNN auto tasks execute every 5 min

**Commands:**
```bash
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/drmanzo/.local/bin/djinn-queue-runner >> /tmp/djinn-queue.log 2>&1") | crontab -
crontab -l | grep queue-runner
```

**Note:** Run after TASK-001 completes. Do not run before shop deploy is verified.

---

## TASK-003
- assigned_to: claude
- status: done
- priority: high
- trigger: manual
- created: 2026-05-31 by Salomon (per Javier)
- completed: 2026-05-31 by Claude
- context: Refactor shipping_agent.py — swap EasyPost SDK for Shippo, make provider configurable

**Commands:**
```bash
# Edit shipping_agent.py:
# 1. Add SHIPPING_PROVIDER=shippo|easypost config variable from shop.env
# 2. Add Shippo client implementation (rate lookup, label purchase, tracking)
# 3. Abstract to common interface
# 4. Test with SHIPPO_API_KEY from shop.env
```

**Note:** Shippo test key is in `~/.config/djinn/shop.env` as `SHIPPO_API_KEY`.

---

## TASK-004
- assigned_to: claude
- status: pending
- priority: high
- trigger: manual
- created: 2026-05-31 by Salomon (per Javier)
- context: Fix maker's mark mirroring on bottom engraving + make it configurable

**Bug:** When the TF anvil STL (logo faces +Z) is boolean-subtracted from a vase bottom and viewed from below, the engraving reads reversed. Need to mirror X axis before subtract.

**Fix required in the workflow:**
1. Mirror maker's mark across X axis before boolean subtraction into bottom surfaces (`mirrored_verts[:, 0] = -mirrored_verts[:, 0]` + reverse face winding)
2. Make maker's mark a configurable variable — default `tf_anvil_traced_15mm.stl`, stored in `~/.config/djinn/makers-mark.json` with `{ "path": "...", "mirror_x": true }`
3. Document the rule so all agents know to mirror before engraving on bottom faces

**Files:**
- `/home/drmanzo/Downloads/files/tf_anvil_traced_15mm.stl` — default mark
- `~/.config/djinn/ender3-v3-plus.ini` — printer profile  
- `/home/drmanzo/.local/bin/djinn-print-consult` — consult script
- `/home/drmanzo/Obsidian/djinn/printer/SUPPORT-GUIDE.md` — workflow docs

**Report back:** Post fix summary in COMMS.md + update `build-log.md`.

---

## TASK-005
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-reel: force 30fps + job-name output filename

**Changes:**
1. Add `-r 30` to all ffmpeg export commands in `djinn-media-reel`
2. Read `job_slug` from `manifest["notes"]` field (fallback to project_id slug)
3. Rename output from `{project_id}_reel.mp4` → `{job_slug}_reel.mp4`
4. Same fix for cover frame filename

**File:** `/home/drmanzo/.local/bin/djinn-media-reel`

---

## TASK-006
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-repurpose: job-name clip naming

**Changes:**
1. Read `job_slug` from manifest notes (fallback to project_id slug)
2. Rename clip output from `clip_{n:02d}.mp4` → `{job_slug}_{n:02d}.mp4`

**File:** `/home/drmanzo/.local/bin/djinn-media-repurpose`

---

## TASK-007
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — build djinn-media-kit: creates stitch-kit/ folder + STITCH-ORDER.txt

**What to build:**
- New script at `/home/drmanzo/.local/bin/djinn-media-kit`
- Reads all clips from `exports/reel/` in the project
- Creates `stitch-kit/` folder in project root
- Copies clips with job-named convention ({job_slug}_01.mp4 etc.)
- Writes `STITCH-ORDER.txt` (clip list, durations, notes from manifest)
- Updates manifest `status = "kit_ready"`
- Usage: `djinn-media-kit {project_id}`

**Spec:** See `~/Obsidian/djinn/projects/PLAN-media-kit-mobile.md`

---

## TASK-008
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-publish-prep: upload stitch-kit/ first, update Discord message

**Changes:**
1. Upload `stitch-kit/` to `gdrive:Typhons-Forge/posts/{project_id}/stitch-kit/` before other uploads
2. Discord `#post-ready` message leads with stitch-kit Drive link, not buried at the end

**File:** `/home/drmanzo/.local/bin/djinn-media-publish-prep`

---

## TASK-009
- assigned_to: claude
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — update djinn-media-ingest: add --job-name flag

**Changes:**
1. Add `--job-name "slug"` CLI flag
2. Write `job_slug` field to manifest.json at ingest time
3. Fallback: derive from project_id if not provided

**File:** `/home/drmanzo/.local/bin/djinn-media-ingest`

---

## TASK-010
- assigned_to: salomon
- status: pending
- priority: normal
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — deploy and test full updated pipeline with mini-vases-job4

**After Claude completes TASK-005 through 009:**
```bash
git -C ~/Obsidian pull
# Re-run mini-vases project through updated pipeline:
djinn-media-kit 2026-05-31_mini-vases-job4   # if project exists
# Or ingest fresh footage with job name:
djinn-media-ingest <footage_path> --job-name "mini-vases-job4"
djinn-media-reel 2026-05-31_mini-vases-job4
djinn-media-kit 2026-05-31_mini-vases-job4
```

**Verify:**
- stitch-kit/ folder exists with job-named clips
- STITCH-ORDER.txt has correct clip list
- Drive upload puts stitch-kit/ at top level
- Clips are 30fps H.264 AAC

**Report back:** COMMS.md + build-log.md

---

## TASK-011
- assigned_to: salomon
- status: pending
- priority: low
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Media kit — add "kit {project_id}" trigger to Discord + Telegram gateways

**After TASK-010 verified:**
Add `kit` command to both gateway scripts so Javier can trigger from phone:
- `kit {project_id}` → runs `djinn-media-kit {project_id}`
- Response: "Kit ready — {drive_link}"

**Files:** `djinn-discord-gateway`, `djinn-telegram-gateway`

---

## TASK-012
- assigned_to: marcus
- status: pending
- priority: high
- trigger: manual
- created: 2026-05-31 by Claude (per Javier)
- context: Deep research brief — Djinn Media social media integration opportunities

**How to run:** Javier pastes the brief below directly into Perplexity. Marcus produces a research artifact. Javier relays output back to vault.

---

### Marcus Research Brief — Djinn Media

**Who you are answering for:**
Javier runs a one-person 3D print shop (Typhon's Forge) with a fully automated AI backend — multi-agent system (Claude, local Ollama, Perplexity) handling quoting, slicing, printing, shipping, and accounting. He is now building a social media production layer called **Djinn Media** on top of this system.

The existing media pipeline already handles: video ingest → color grading → caption generation → hashtag selection → Google Drive upload → Discord notification. All local, all automated, CLI-driven on a Linux machine with ffmpeg, faster-whisper, Ollama (phi4:14b, llama3.2-vision), rclone.

**Target platforms:** Instagram Reels, Instagram Feed, Facebook Reels, Facebook Feed. Possibly TikTok later.

**Content type:** Short-form video (15–90s) of 3D printing process, product reveals, AI shop automation demos. Dark maker aesthetic. Cannabis accessories in the mix.

---

**Research questions — go deep on each:**

1. **Auto-posting APIs**
   What are the current (2026) options for programmatically publishing to Instagram and Facebook without manual intervention? Specifically:
   - Instagram Graph API — current capabilities, what requires Meta Business Suite, what can be fully automated vs what still requires human action
   - Facebook Graph API for video/Reels posting
   - Third-party scheduling APIs (Buffer, Later, Publer, etc.) that expose REST APIs — which ones allow full automation without a human approval step?
   - Any new Meta features in 2025–2026 that opened up or closed off auto-posting?

2. **What's actually performing on Reels for maker/3D printing content in 2026**
   - What content formats are the algorithm rewarding right now (POV, voiceover, text-on-screen, timelapse, reveal format)?
   - Optimal clip length for reach vs engagement tradeoff
   - What hook styles (first 3 seconds) are working in the maker/DIY/craft niche
   - Any data on posting frequency, timing, consistency patterns that matter
   - How do successful small maker accounts (under 10k followers) grow vs larger ones

3. **AI-assisted social media tools for creators — competitive landscape**
   - What tools exist in 2026 for AI-assisted caption writing, hashtag research, content scheduling for small creators?
   - Any tools that do what Djinn Media is building (auto-generate content from raw footage + metadata)?
   - What's the gap — what are these tools missing that a custom pipeline could do better?

4. **Cross-platform content repurposing**
   - Best practices for repurposing one piece of content across IG, FB, and TikTok without getting penalized for duplicate content
   - Watermark detection — does Instagram or FB actually suppress content with TikTok watermarks in 2026?
   - How to format one video file to perform optimally on all three without separate exports

5. **Analytics and feedback loops**
   - What analytics are available via the Instagram/Facebook Graph API (not just the app — the actual API)?
   - Can you pull reach, saves, shares, watch time, retention data programmatically?
   - Are there open-source or lightweight tools for aggregating this data locally?

6. **Cannabis content and platform policies in 2026**
   - What is Instagram's current enforcement stance on cannabis accessory content (not drug use — 3D printed accessories, pipes, etc.)?
   - What hashtag categories are getting shadowbanned vs tolerated?
   - Any workarounds successful cannabis-adjacent accounts are using?
   - Facebook's policy vs Instagram's policy — are they different?

7. **Djinn Media as a product**
   - If this pipeline were packaged as a tool for other small shop owners / makers — what would be the most valuable features to emphasize?
   - Who is the target user (maker, Etsy seller, print shop, cannabis brand)?
   - What's the competitive positioning vs existing tools?

---

**Output format requested:**
Structured report with one section per question. For each section: current state, key findings, specific recommendations or integrations to pursue, and any warnings/gotchas. Cite sources. Flag anything time-sensitive (API changes, policy updates).

**Deliver as:** Markdown artifact Javier can paste into the vault at `~/Obsidian/djinn/projects/RESEARCH-djinn-media-marcus.md`

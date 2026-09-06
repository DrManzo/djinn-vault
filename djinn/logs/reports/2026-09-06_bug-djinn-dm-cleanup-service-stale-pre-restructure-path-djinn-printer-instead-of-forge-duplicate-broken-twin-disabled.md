---
title: Bug Report — djinn-dm-cleanup.service — stale pre-restructure path (djinn/printer instead of forge), duplicate broken twin disabled
agent: Claude
date: 2026-09-06
severity: medium
status: fixed
tags: [djinn, bug, djinn-dm-cleanup.service / forge-dm-cleanup.service / Studio services (systemd --user, Salomon)]
related: [[bugs]] | [[build-log]]
---

# Bug Report — djinn-dm-cleanup.service — stale pre-restructure path (djinn/printer instead of forge), duplicate broken twin disabled

**Date:** 2026-09-06 12:32
**Agent:** Claude
**System:** djinn-dm-cleanup.service / forge-dm-cleanup.service / Studio services (systemd --user, Salomon)
**Severity:** medium
**Status:** fixed

---

## Root Cause

The systemd unit's inline python -c command inserted sys.path.insert(0, '/home/drmanzo/Obsidian/djinn/printer') and then did 'from shop.customer_dm import cleanup_expired_sessions' -- but that module moved to forge/shop/customer_dm.py during the 2026-07-08 department restructure and the unit was never updated, so every run threw ModuleNotFoundError: No module named 'shop'. A second, parallel service (forge-dm-cleanup.service) was apparently created at some point to do the same job through a venv at ~/projects/forge/.venv/bin/python3 -- but ~/projects/ doesn't exist at all on this machine, so that one failed with status=203/EXEC (couldn't even launch) on every run. Both had been failing on every timer trigger (djinn-dm-cleanup every 6h, forge-dm-cleanup every 6h) for an unknown but likely long period -- customer DM session cleanup has probably not run successfully in a long time. Fixed by correcting djinn-dm-cleanup.service's sys.path.insert to '/home/drmanzo/Obsidian/forge' (customer_dm.py's own internal path logic handles inserting forge/shop from there), verified via direct manual run (Cleaned 0 messages, no errors) and then via a live systemctl --user start of the actual unit (status=0/SUCCESS). forge-dm-cleanup.service and its timer were stopped and disabled outright rather than fixed, since it was a fully redundant duplicate of the same job pointing at project scaffolding that was never actually built on this machine. Also disabled 5 unrelated 'Studio' social-media-pipeline services in the same pass (studio-media-gdrive-sync, studio-meta-token-refresh, studio-publish-scheduler, studio-social-analyst, studio-token-refresh) -- all failing the identical way, all pointing at the same nonexistent ~/projects/djinn-social/.venv. Left studio-media-drop.service (actively running fine), studio-hashtag-research.service, and studio-trend-agent.service (idle, not failed, unassessed) untouched -- did not assume the whole Studio subsystem was dead, only disabled the specific units confirmed broken and pointing at missing paths.

---

## Symptom

<!-- Fill in: what the user or system observed -->

---

## Steps to Reproduce

1. <!-- steps -->

---

## Fix Applied

<!-- What was changed, where, and why -->

---

## Verification

<!-- How you confirmed the fix worked -->

---

## Rule / Lesson

> **Rule:** <!-- one sentence: what prevents this class of bug in the future -->

---

*— Claude, 2026-09-06*

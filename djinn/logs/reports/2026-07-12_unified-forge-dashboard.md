---
title: Session Report — Unified Typhon's Forge Dashboard
agent: Claude
date: 2026-07-12
tags: [djinn, report, forge, dashboard, fleet, inventory, shop]
related: [[build-log]] | [[decision-log]] | [[QUEUE]]
---

# Session Report — Unified Typhon's Forge Dashboard

**Date:** 2026-07-12
**Agent:** Claude
**Session type:** Build
**Trigger:** Javier decided to merge the fleet dashboard (`djinn-forge-dashboard`, port 8420) and the shop dashboard (`djinn-shop-dashboard`, port 5000) into a single unified app with a live-editable filament inventory.

---

## Summary

Merged both Flask dashboards into a single unified app at port 8420. One URL, one login, one nav covering: live printer fleet cards (auto-refresh 5s), active order queue, orders, customers, filament inventory (live-editable), finance, and reports. Old fleet service stopped and disabled. New unified service confirmed up, all routes 200, live fleet polling confirmed (Calliope + Nemesis printing at the time of test).

---

## What Was Built or Changed

### Merged app — `~/Obsidian/forge/shop/dashboard/app.py`
Complete rewrite merging both apps. Key changes from the old shop dashboard:

- **Port changed**: 5000 → 8420 (fleet dashboard's port)
- **Fleet polling added**: `_fetch_moonraker`, `_fetch_octoprint`, `fetch_all()` — concurrent `ThreadPoolExecutor` fetch, 3s timeout per printer, per-printer exception isolation
- **New route `/` → `/dashboard`**: Landing page with fleet strip (4 printer cards, JS-polled every 5s) + active orders table. Old `/` was the queue — now queue is at `/queue` only.
- **New route `/inventory`**: Filament inventory from `~/Obsidian/forge/inventory/filament-inventory.json`. Grouped: loaded per-printer, then unloaded. Low-stock warning banner.
- **New API `/api/inventory/<spool_id>` (POST)**: JSON endpoint to update `remaining_g`, `notes`, `loaded`, `loaded_printer` for any spool. Writes back to the JSON file.
- **New API `/api/status`**: Returns fleet status JSON (same as old fleet dashboard, now auth-gated)
- **Auth**: Session-based password (same as old shop dashboard: `DJINN_DASH_PASSWORD` env, default `typhonsforge`). Dropped the HTTP Basic auth from the fleet dashboard — no longer needed since both are merged under the same session auth.
- **Color hex filter**: `@app.template_filter("color_hex")` maps filament color names (white, red, yellow, etc.) to hex for the color dot in the inventory table.

### New templates
- **`templates/dashboard.html`**: Fleet card grid (dynamic via JS / `/api/status`) + active order table. CSS for fleet cards inline in the template.
- **`templates/inventory.html`**: Two-section table (loaded per printer / unloaded). Inline click-to-edit for remaining weight — click a weight, edit in place, blur commits via `POST /api/inventory/<spool_id>`. Low-stock rows highlighted orange.

### Updated templates
- **`templates/base.html`**: Added Dashboard (home icon) and Inventory (stack icon) to the sidebar nav.

### Service changes
- **`djinn-shop-dashboard.service`**: Updated description, added `Environment=FLASK_PORT=8420`, added `EnvironmentFile=-%h/.config/djinn/printers.env` for `DJINN_PENELOPE_APIKEY`.
- **`djinn-forge-dashboard.service`**: Stopped and disabled. The old fleet service is gone.
- **`forge-shop-dashboard.service`**: Was in `activating` state (stale from a prior session), stopped and disabled.

---

## Technical Decisions

**Merge into the shop dashboard's app.py** — The shop dashboard had a more complete codebase (multi-template, session auth, DB integration). Fleet polling was simpler and easier to absorb. Choosing the shop as the base preserved all existing routes without modification.

**Session auth for `/api/status`** — The old fleet dashboard left `/api/status` open (no auth, HTTP Basic covered the HTML). In the merged app the endpoint is `@_require_login` protected. The JS fetch on the dashboard page sends the session cookie automatically, so this is transparent. It does mean the raw API isn't usable without a browser session, but that's the right default for a single-user tool.

**Inline edit on remaining_g only** — Notes and loaded/printer assignment are updatable via the API but not yet via the inventory UI (would need more complex UI). Click-to-edit is scoped to remaining_g because that's the field updated most frequently (after each print job). Everything else is edited in the JSON directly for now.

**filament-inventory.json as write target** — The inventory route reads and writes `~/Obsidian/forge/inventory/filament-inventory.json` directly. This is the canonical store agreed on last session. The JSON is inside the Obsidian vault so djinn-vault-sync picks it up in backups.

---

## Files Created or Modified

```
~/Obsidian/forge/shop/dashboard/app.py                    ← merged, rewritten
~/Obsidian/forge/shop/dashboard/templates/base.html       ← added Dashboard + Inventory nav links
~/Obsidian/forge/shop/dashboard/templates/dashboard.html  ← new (fleet strip + active orders)
~/Obsidian/forge/shop/dashboard/templates/inventory.html  ← new (live-editable filament table)
~/.config/systemd/user/djinn-shop-dashboard.service       ← port 8420, added printers.env
~/Obsidian/djinn/logs/reports/2026-07-12_unified-forge-dashboard.md  ← this file
```

---

## Tests & Validation

| Test | Result |
|------|--------|
| Service start | ✓ active (running), 29MB, port 8420 |
| GET / (unauthenticated) | ✓ 302 → /login |
| POST /login (correct password) | ✓ 302 → /dashboard |
| GET /dashboard | ✓ 200 |
| GET /queue | ✓ 200 |
| GET /inventory | ✓ 200 |
| GET /api/status | ✓ 200, live fleet data returned |
| Fleet data accuracy | ✓ Calliope: printing, Nemesis: printing, Iris: complete, Penelope: offline |
| Old fleet service (djinn-forge-dashboard) | ✓ stopped + disabled |
| Old duplicate (forge-shop-dashboard) | ✓ stopped + disabled |

---

## Known Issues / Caveats

- **Inventory edit is remaining_g only** — Other fields (notes, loaded status) need direct JSON edits for now. Can add full row edit modal later if needed.
- **No CSRF on `/api/inventory/<spool_id>`** — Fine for a single-user LAN app, not appropriate if exposed publicly.
- **Fleet dashboard had open auth** — The old fleet dashboard had no auth when `DJINN_DASHBOARD_USER` wasn't set. Now it's behind session auth — any existing bookmarks to the old standalone fleet URL still work (same port 8420) but now require login first. Expected and correct.

---

## What's Next

- [ ] TASK-010: Move `~/Games/` (3.3GB) to Alexandria
- [ ] TASK-011: Clean stale `/mnt/` subdirs (iris-usb, penelope-sd, piboot, piroot, typhon-usb, winiso, winusb)
- [ ] TASK-012: SSH to Oroborus, commit uncommitted changes in djinn-core and projects/forge
- [ ] TASK-013: Investigate Penelope offline (192.168.1.150)
- [ ] TASK-014: Power on Typhon, mount as network share, run chkdsk on Typhon USB
- [ ] Inventory UI: add full row edit modal (notes, loaded printer, loaded flag)
- [ ] Nemesis bed tram (right side ~1.3mm low)
- [ ] SPOOL-027 brand identification (Burnt Titanium PLA)

---

*— Claude, 2026-07-12*

---
title: Session Report — Shop Dashboard Hardening, Self-Service Data Entry, Nemesis Profile Fix
agent: Claude
date: 2026-07-16
tags: [djinn, report, forge-dashboard, nemesis, orcaslicer, inventory, orders]
related: [[2026-07-14_forge-dashboard-build]] | [[2026-07-16_bug-nemesis-orcaslicer-center-origin-printable-area]] | [[build-log]] | [[bugs]] | [[decision-log]]
---

# Session Report — Shop Dashboard Hardening, Self-Service Data Entry, Nemesis Profile Fix

**Date:** 2026-07-14 (evening) through 2026-07-16
**Agent:** Claude
**Session type:** Build / Debug / Ops
**Trigger:** Javier asked to make the shop dashboard "actually functional," followed by a wipe/restore of seed data, a request for self-service data entry, and a live print failure on Nemesis needing root-cause diagnosis.

---

## Summary

Verified the Typhon's Forge shop dashboard end-to-end against live data, built the one real gap found (inventory edit modal), then wiped the DB's test/seed data at Javier's direction — before restoring the filament inventory specifically once he clarified that portion was real, not test data. Built two new self-service capabilities (add-spool, manual order entry) after first verifying the existing Discord order-intake pipeline already works correctly. Separately root-caused and fixed a Nemesis print failure: the OrcaSlicer machine profile inherited a center-origin `printable_area` from Flashforge's stock profile chain while Nemesis's real Klipper firmware is corner-origin — confirmed via direct coordinate comparison against a prior successful print, fixed, and verified the re-slice landed inside bounds.

---

## What Was Built or Changed

- **Dashboard verification (7/14):** every route (`/`, `/orders`, `/orders/<id>`, `/queue`, `/customers`, `/customer/<id>`, `/inventory`, `/finance`, `/reports`, both exports) tested clean against live data — no errors beyond what an earlier same-day session had already fixed (Jinja `.items` dict-shadowing crash).
- **Inventory edit modal** (`forge/shop/dashboard/templates/inventory.html`) — the backend (`/api/inventory/<spool_id>`) already supported updating `notes`/`loaded`/`loaded_printer`, but the UI only exposed click-to-edit for `remaining_g`. Added a proper modal (pencil button per row) covering all three fields.
- **DB wipe, then partial restore:** cleared all business tables (orders, customers, order_items, ledger, invoices, income/balance statements, monthly reports, a second unused legacy `filament_inventory` DB table, filament usage log, shipments, tracking events) — confirmed by Javier as test/seed data. Backed up first. Reset `sqlite_sequence` and confirmed `next_order_id()` returns `ORD-0001` cleanly. **Then restored the filament inventory JSON from the pre-wipe backup** once Javier clarified that specific dataset (36 real spools) was not test data, unlike the orders/customers.
- **Self-service data entry, built after verifying what already existed:**
  - Confirmed the Discord order-intake pipeline (`djinn-discord-gateway` → `forge/shop/customer_dm.py::handle_order` → `upsert_customer`/`create_order`/`add_order_item`/`create_invoice`) is sound — tested the logic against a throwaway DB copy (not live data).
  - `POST /api/inventory` (no spool_id) — adds a new spool, auto-assigns next `SPOOL-NNN`. "+ Add Spool" modal on the inventory page.
  - `GET/POST /orders/new` — manual order form (customer, item, qty, price, material, payment method, express, notes), running the same create-order pipeline the Discord bot uses, for phone/in-person orders. "+ New Order" button on `/orders`.
  - Both verified live with real test data, then cleaned up afterward (test order/customer/invoice/spool deleted, counters reset) so the just-cleaned production DB stayed clean.
- **Gcode quality post-processing** — Javier asked to improve outer-wall surface finish on the bottom 10mm of `oni cup-blue-marked-fix_PLA_43m41s.gcode`. Wrote a targeted post-processor: tracks Z via `;LAYER_CHANGE`/`;Z:` markers and feature type via `;TYPE:` markers, and for any `G1 F<n>`-only line inside an `Outer wall` section while Z ≤ 10mm, scales the feedrate to 50% (floored at F300/5mm/s to avoid oozing from over-slow dwelling). Chose proportional scaling over a fixed target speed because the slicer already varies outer-wall speed per corner (observed range F600–F30000 in the same 10mm band) — a flat override would have ignored that. Verified: same line count as input (no corruption), exactly 2,347 lines touched, all changes confirmed to sit at Z ≤ 10.0mm exactly. Output written to a new `_bottomQ.gcode` file; original left untouched.
- **Nemesis OrcaSlicer `printable_area` bug (full writeup: [[2026-07-16_bug-nemesis-orcaslicer-center-origin-printable-area]]):** `2camood-v1_marked_PETG_8h18m.gcode` threw "Move out of range." Root cause: Nemesis's active machine profile inherits `printable_area: ["-110x-110", ..., "-110x110"]` (center-origin) from Flashforge's stock `fdm_adventurer5m_common` system profile, but Nemesis's real Klipper firmware is corner-origin (0–220), like the rest of this fleet — same bug class as the Iris/A1 `time_lapse_gcode` issue from 7/6. Confirmed via direct comparison: the failing file's coordinates ran -88 to 88 / -55 to 55; a previously-successful camood print's coordinates ran 31–184 / 50–161, entirely positive. Fixed by adding an explicit corner-origin `printable_area` override (`0x0` to `220x220`) to the user profile. OrcaSlicer was running at fix time (caches profiles in-session) — closed it at Javier's explicit request rather than leaving the fix unappplied. Re-slice (`camood-v1_marked_PETG_3h21m.gcode`) confirmed clean: X 66.66–153.35, Y 55.87–173.02, fully in bounds.
- **Minor file retrievals:** dropped `camood-v1_marked.stl` (pre-v2 camood) and `backpack-boyz-core_marked.stl` (retrieved from an Oroborus archive after the local/Alexandria copies turned out not to exist — same "referenced in a library note but the actual file didn't survive migration" pattern as Camood's TTHQ engraving, verified via checksum after transfer) into `~/Downloads/` on request.

---

## Technical Decisions

**Restore inventory but not orders/customers after the wipe — Why:** Javier's own distinction, not mine — the 36-spool filament inventory was real, physically-on-hand data; the 5 test orders and 3 test customers were seed/placeholder data. Backing up before wiping made the correction cheap once he caught it.

**Build self-service data entry only after verifying the existing Discord pipeline — Why:** would have been wasted, possibly duplicate effort to build a whole new order-creation path without first confirming whether one already existed and worked. It did. The two new features fill genuine gaps (off-Discord manual orders, new spool intake) rather than replacing something already functional.

**Proportional gcode speed scaling over a fixed target — Why:** the slicer's own per-corner speed variation in the affected region (F600 to F30000) reflects real junction-deceleration logic; a flat override would have either blown through corners too fast or crawled unnecessarily on straights. Scaling preserves that intelligence while uniformly slowing the visible surface.

**Fix the Nemesis profile at the profile level, not just reposition one file — Why:** same root cause will recur on every future Nemesis slice where the object happens to land near bed-center. Matches the precedent set by the Iris/A1 fix — correct the profile once rather than manually re-positioning objects forever.

---

## Files Created or Modified

```
forge/shop/dashboard/app.py                          ← +2 routes: POST /api/inventory (add spool), GET/POST /orders/new
forge/shop/dashboard/templates/inventory.html          ← edit modal (notes/loaded/loaded_printer) + add-spool modal
forge/shop/dashboard/templates/orders.html             ← "+ New Order" button
forge/shop/dashboard/templates/order_new.html          ← new: manual order form
~/.local/share/djinn-shop/shop.db                     ← wiped business tables, restored inventory separately (JSON, not this DB)
forge/inventory/filament-inventory.json                ← wiped then restored from pre-wipe backup
~/.config/OrcaSlicer/user/default/machine/Flashforge Adventurer 5M Pro 0.4 Nozzle - Copy.json  ← added corner-origin printable_area override
Desktop/Review/Nemesis/oni cup-blue-marked-fix_PLA_43m41s_bottomQ.gcode  ← new: outer-wall speed reduced 0-10mm
~/Downloads/camood-v1_marked.stl, backpack-boyz-core_marked.stl  ← retrieved on request
```

---

## Tests & Validation

| Test | Result |
|------|--------|
| Dashboard full route sweep (7/14) | All 200, no errors |
| Add-spool endpoint | Real test spool created (SPOOL-037), verified, then removed |
| Manual order endpoint | Real test order created (customer, order, line item, invoice all correct in DB and on the rendered page), verified, then removed, counters reset |
| Discord order-pipeline logic | Verified against a throwaway DB copy — full upsert_customer → create_order → add_order_item → create_invoice chain succeeded |
| Empty-state rendering (post-wipe) | All pages clean: "No orders", "No customers yet", "Queue is empty", no NaN/crashes |
| Gcode quality post-processor | Line count unchanged (299,778 both files), exactly 2,347 lines changed, max Z of any change = 10.0mm exactly |
| Nemesis profile fix | Re-slice coordinates confirmed in-bounds (X 66.66–153.35, Y 55.87–173.02) vs. the original failing slice's out-of-bounds negative range |

---

## Known Issues / Caveats

- **Dashboard auth still uses the default password** (`typhonsforge`) — not urgent (LAN-only, view-heavy not raw-DB-access), but worth rotating eventually.
- **Calliope's and Iris's OrcaSlicer profiles haven't been audited** for the same unaudited-inheritance `printable_area`/`time_lapse_gcode` pattern that hit both Iris (7/6) and Nemesis (7/16) — neither has hit a fresh symptom, but the pattern is now 2-for-2 on this fleet.
- **The gcode quality fix hasn't been printed yet** — verified structurally (line count, Z boundary, no corruption) but not print-tested for actual visual improvement.
- **Backpack Boyz and Camood-v1 file retrievals surfaced (again) that library notes reference file paths that don't survive migrations** — same pattern as Camood's lost TTHQ engraving. No action taken this session beyond finding working copies elsewhere (Oroborus archives).

---

## What's Next

- [ ] Print-test the gcode quality fix (`oni cup..._bottomQ.gcode`) and confirm visual improvement — @Javier
- [ ] Audit Calliope/Iris OrcaSlicer profiles for the same origin-convention risk — @Claude, future session
- [ ] Rotate the dashboard's default password when convenient — @Javier
- [ ] Consider a periodic check that library-note file paths actually resolve, given this is now a repeated pattern (Camood TTHQ, Backpack Boyz variants) — @Claude, future session

---

*— Claude, 2026-07-16*

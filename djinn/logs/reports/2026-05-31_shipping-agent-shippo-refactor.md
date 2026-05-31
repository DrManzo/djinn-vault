---
title: Session Report — Shipping Agent Shippo Refactor
agent: Claude
date: 2026-05-31
tags: [djinn, report, shop, shipping, shippo]
related: [[build-log]] | [[QUEUE]] | [[COMMS]]
---

# Session Report — Shipping Agent Shippo Refactor

**Date:** 2026-05-31
**Agent:** Claude
**Session type:** Build
**Trigger:** TASK-003 — Javier is using Shippo (free test tier) instead of EasyPost. shipping_agent.py was hardcoded to EasyPost SDK.

---

## Summary

Refactored `shipping_agent.py` from EasyPost-only to a dual-provider architecture. `SHIPPING_PROVIDER=shippo|easypost` in `shop.env` selects the active provider. All three operations (rate lookup, label purchase, tracking) have full Shippo implementations via the Shippo REST API (no SDK dependency). Public interface is unchanged — callers don't know or care which provider is active.

---

## What Was Built or Changed

- **Dual-provider routing** — `get_rates()`, `buy_label()`, `track_shipment()` now route to `_*_shippo()` or `_*_easypost()` based on `SHIPPING_PROVIDER`
- **Shippo REST implementation** — uses `requests` directly against `api.goshippo.com` (no SDK version fragility). Covers: address create, parcel create, shipment create + rate fetch, transaction create (label purchase), tracking status poll
- **`_load_shop_env()`** — auto-loads `~/.config/djinn/shop.env` at import time so `SHIPPO_API_KEY` is available without sourcing the file externally
- **Error types unified** — `ShippingError` is the base; `EasyPostError` and `ShippoError` are aliases for backward compat
- **Default provider** — `shippo` (Javier has the key; EasyPost key not yet set)

---

## Technical Decisions

**Shippo REST API over Shippo SDK — Why:** Shippo's Python SDK has had breaking changes between v1, v2, and v3. Using `requests` directly against the REST API gives stable, version-independent behavior with no new pip dependency. The existing `requests` import covers it.

**`_load_shop_env()` at module import — Why:** Existing code read `EASYPOST_API_KEY` from env only. Salomon's gateways source shop.env before starting, but `python3 shipping_agent.py` directly would miss it. Loading at import time makes the module self-sufficient.

**Provider selected at module load, not per-call — Why:** Consistent with existing pattern (`EP_API_KEY` was a module-level constant). A per-call lookup would work too but adds overhead with no real benefit — provider switching mid-process is not a use case.

**EasyPost kept intact — Why:** Javier may get an EasyPost key later, or swap back. The two implementations are independent; keeping both costs nothing and avoids re-building.

---

## Files Created or Modified

```
~/Obsidian/djinn/printer/shop/shipping_agent.py  ← full rewrite: Shippo impl added, provider routing, _load_shop_env()
```

---

## Tests & Validation

- `ast.parse()` — syntax clean
- Address parser: 3/3 cases, conf=1.0, no errors
- `SHIPPING_PROVIDER=shippo`, `SHIPPO_API_KEY=set` confirmed at module load
- Live rate/label test requires real order in DB — run manually: `ship ORD-0001` via Telegram once an order exists

---

## Known Issues / Caveats

- Shippo test key is `shippo_test_*` — rates and labels work but no real postage is charged. Swap to live key before first real order.
- `shop.json` still needs real shipping address before first label purchase.
- EasyPost path untested (no key) — preserved as-is from prior implementation.

---

## What's Next

- [ ] Set real shipping address in `~/.config/djinn/shop.json` — @Javier
- [ ] Test live rate lookup: send `ship ORD-XXXX` in Telegram once first order comes in — @Javier/@Salomon
- [ ] Swap `SHIPPO_API_KEY` from test to live key when ready to ship real orders — @Javier

---

*— Claude, 2026-05-31*

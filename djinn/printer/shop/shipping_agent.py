"""
shipping_agent.py — Multi-provider shipping integration for Djinn Shop.
Spec by Marcus (Perplexity). Implementation by Claude.

Providers: shippo (default) | easypost
Set SHIPPING_PROVIDER in shop.env to switch.

Handles: address parsing + verification, rate lookup, label purchase,
label download, tracking, reporting.

Telegram commands (wired by Salomon):
  ship ORD-0001             → show rates for this order
  ship ORD-0001 usps-priority → buy label immediately
  track ORD-0001            → latest tracking status

— Claude
"""

import os
import sys
import re
import json
import datetime
import pathlib
import warnings
import requests
from dataclasses import dataclass, field
from typing import Optional

_SHOP    = pathlib.Path(__file__).parent
_PRINTER = _SHOP.parent
for p in [str(_PRINTER), str(_SHOP)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from shop.db import get_db, init_db, get_order, update_order_status, decrypt


# ── Load shop.env before reading config ───────────────────────────────────────
def _load_shop_env():
    shop_env = pathlib.Path.home() / ".config/djinn/shop.env"
    if not shop_env.exists():
        return
    for line in shop_env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key not in os.environ:
            os.environ[key] = val.strip()

_load_shop_env()


# ── Config ────────────────────────────────────────────────────────────────────
SHIPPING_PROVIDER = os.environ.get("SHIPPING_PROVIDER", "shippo").lower()
EP_API_KEY        = os.environ.get("EASYPOST_API_KEY", "")
SHIPPO_API_KEY    = os.environ.get("SHIPPO_API_KEY", "")
LABELS_DIR        = pathlib.Path.home() / ".local/share/djinn-shop/labels"
SHOP_CFG_PATH     = pathlib.Path.home() / ".config/djinn/shop.json"
SHIPPO_BASE       = "https://api.goshippo.com"

TG_TOKEN      = os.environ.get("DJINN_TG_TOKEN",
                                "7962428973:AAHzCibu8E0RDDaRF3eHGA7WcOEqMbypOVI")
TG_API        = f"https://api.telegram.org/bot{TG_TOKEN}"
OWNER_TG_CHAT = int(os.environ.get("DJINN_TG_ALLOWED", "7620067588").split(",")[0])

PACKAGING_WEIGHT_G = float(os.environ.get("DJINN_PACKAGING_WEIGHT_G", "85"))
G_TO_OZ            = 0.035274

# Box tiers by print weight (grams)
BOX_TIERS = [
    (100,  6.0, 4.0, 3.0),
    (300,  8.0, 6.0, 4.0),
    (float("inf"), 12.0, 8.0, 6.0),
]


# ── Error types ───────────────────────────────────────────────────────────────
class ShippingError(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code  = error_code
        super().__init__(message)

EasyPostError = ShippingError  # backward compat alias
ShippoError   = ShippingError


class AddressParseWarning(UserWarning):
    pass


class AddressVerificationError(Exception):
    pass


# ── Address dataclass (Marcus spec) ──────────────────────────────────────────
@dataclass
class ParsedAddress:
    raw_input:        str
    name:             str           = ""
    company:          Optional[str] = None
    street1:          str           = ""
    street2:          Optional[str] = None
    city:             str           = ""
    state:            str           = ""
    zip5:             str           = ""
    zip4:             Optional[str] = None
    country:          str           = "US"
    parse_confidence: float         = 0.0
    parse_errors:     list          = field(default_factory=list)


# ── State normalization ───────────────────────────────────────────────────────
STATE_ABBREVS = {
    "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
    "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA",
    "hawaii":"HI","idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA",
    "kansas":"KS","kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD",
    "massachusetts":"MA","michigan":"MI","minnesota":"MN","mississippi":"MS",
    "missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new hampshire":"NH",
    "new jersey":"NJ","new mexico":"NM","new york":"NY","north carolina":"NC",
    "north dakota":"ND","ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA",
    "rhode island":"RI","south carolina":"SC","south dakota":"SD","tennessee":"TN",
    "texas":"TX","utah":"UT","vermont":"VT","virginia":"VA","washington":"WA",
    "west virginia":"WV","wisconsin":"WI","wyoming":"WY","district of columbia":"DC",
    "puerto rico":"PR","guam":"GU","virgin islands":"VI","american samoa":"AS",
}
VALID_STATES = set(STATE_ABBREVS.values())


def normalize_state(raw: str) -> Optional[str]:
    raw = raw.strip()
    if raw.upper() in VALID_STATES:
        return raw.upper()
    return STATE_ABBREVS.get(raw.lower())


def parse_address(raw: str, name: str = "") -> ParsedAddress:
    """Parse freeform US address string into ParsedAddress. Pure local — no API calls."""
    addr = ParsedAddress(raw_input=raw, name=name)
    text = raw.strip().replace("\n", ", ")
    errors = []
    clean_fields = 0

    zip_m = re.search(r'(\d{5})(?:-(\d{4}))?', text)
    if zip_m:
        addr.zip5 = zip_m.group(1)
        addr.zip4 = zip_m.group(2)
        text = text[:zip_m.start()].strip(", ") + text[zip_m.end():]
        clean_fields += 1
    else:
        errors.append("zip5")

    state_m = re.search(r'\b([A-Z]{2})\b', text)
    if state_m and state_m.group(1) in VALID_STATES:
        addr.state = state_m.group(1)
        text = text[:state_m.start()].strip(", ") + text[state_m.end():]
        clean_fields += 1
    else:
        for name_full, abbr in STATE_ABBREVS.items():
            if name_full in text.lower():
                addr.state = abbr
                text = re.sub(name_full, "", text, flags=re.I).strip(", ")
                clean_fields += 1
                break
        else:
            errors.append("state")

    parts = [p.strip().strip(",") for p in text.split(",") if p.strip()]

    for i, part in enumerate(parts):
        if re.match(r'^\d+\s', part):
            addr.street1 = part
            parts.pop(i)
            clean_fields += 1
            if parts and re.match(r'^(apt|suite|ste|unit|#)', parts[0], re.I):
                addr.street2 = parts.pop(0)
            break
    else:
        errors.append("street1")

    if parts:
        addr.city = parts[0].strip()
        clean_fields += 1
    else:
        errors.append("city")

    if name:
        clean_fields += 1
    else:
        errors.append("name")

    addr.parse_errors     = errors
    addr.parse_confidence = clean_fields / 5.0

    if addr.parse_confidence < 0.6:
        warnings.warn(
            f"Low address confidence ({addr.parse_confidence:.1f}) for: {raw}",
            AddressParseWarning
        )
    return addr


def format_address_block(addr: ParsedAddress) -> str:
    lines = []
    if addr.name:
        lines.append(addr.name)
    lines.append(addr.street1 + (f" {addr.street2}" if addr.street2 else ""))
    zip_str = addr.zip5 + (f"-{addr.zip4}" if addr.zip4 else "")
    lines.append(f"{addr.city}, {addr.state} {zip_str}")
    return "\n".join(lines)


# ── Shop address ──────────────────────────────────────────────────────────────
def _load_shop_address() -> dict:
    if SHOP_CFG_PATH.exists():
        return json.loads(SHOP_CFG_PATH.read_text())
    return {
        "name": "Typhon's Forge",
        "street1": "YOUR STREET HERE",
        "city": "San Bernardino",
        "state": "CA",
        "zip5": "92401",
        "phone": "",
        "email": "typhonsforge@gmail.com",
    }


# ── Schema ────────────────────────────────────────────────────────────────────
SHIPPING_SCHEMA = """
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id      TEXT    PRIMARY KEY,
    order_id         TEXT    NOT NULL,
    customer_id      INTEGER NOT NULL,
    tracking_code    TEXT,
    label_url        TEXT,
    label_file_path  TEXT,
    carrier          TEXT,
    service          TEXT,
    rate_usd         REAL    DEFAULT 0.0,
    insurance_usd    REAL    DEFAULT 0.0,
    total_cost_usd   REAL    DEFAULT 0.0,
    weight_oz        REAL    DEFAULT 0.0,
    estimated_delivery TEXT,
    status           TEXT    DEFAULT 'created',
    created_at       TEXT    NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS tracking_events (
    event_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    shipment_id      TEXT    NOT NULL,
    event_time       TEXT,
    status           TEXT,
    detail           TEXT,
    location_city    TEXT,
    location_state   TEXT,
    location_zip     TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id)
);
"""


def init_shipping():
    with get_db() as conn:
        conn.executescript(SHIPPING_SCHEMA)


# ── Package dimensions ────────────────────────────────────────────────────────
def _box_for_weight(print_grams: float) -> tuple:
    total_g = print_grams + PACKAGING_WEIGHT_G
    for threshold, l, w, h in BOX_TIERS:
        if total_g < threshold:
            return total_g * G_TO_OZ, l, w, h
    return (print_grams + PACKAGING_WEIGHT_G) * G_TO_OZ, 12.0, 8.0, 6.0


# ── Service shorthand map ─────────────────────────────────────────────────────
SERVICE_MAP = {
    "usps-first":        ("USPS", "First"),
    "usps-firstclass":   ("USPS", "First"),
    "usps-ground":       ("USPS", "GroundAdvantage"),
    "usps-priority":     ("USPS", "Priority"),
    "usps-express":      ("USPS", "Express"),
    "ups-ground":        ("UPS",  "Ground"),
    "ups-3day":          ("UPS",  "3DaySelect"),
    "ups-2day":          ("UPS",  "2ndDayAir"),
    "fedex-ground":      ("FedEx","FEDEX_GROUND"),
    "fedex-home":        ("FedEx","GROUND_HOME_DELIVERY"),
    "fedex-2day":        ("FedEx","FEDEX_2_DAY"),
}


# ══════════════════════════════════════════════════════════════════════════════
# Shippo provider
# ══════════════════════════════════════════════════════════════════════════════

def _shippo_headers() -> dict:
    key = os.environ.get("SHIPPO_API_KEY", SHIPPO_API_KEY)
    if not key:
        raise ShippoError(401, "no_key",
                          "SHIPPO_API_KEY not set — add to ~/.config/djinn/shop.env")
    return {"Authorization": f"ShippoToken {key}", "Content-Type": "application/json"}


def _shippo_post(path: str, payload: dict) -> dict:
    r = requests.post(f"{SHIPPO_BASE}{path}", json=payload,
                      headers=_shippo_headers(), timeout=20)
    if not r.ok:
        raise ShippoError(r.status_code, "api_error", r.text[:300])
    return r.json()


def _shippo_get(path: str) -> dict:
    r = requests.get(f"{SHIPPO_BASE}{path}",
                     headers=_shippo_headers(), timeout=20)
    if not r.ok:
        raise ShippoError(r.status_code, "api_error", r.text[:300])
    return r.json()


def _get_rates_shippo(order_id: str) -> list:
    order = get_order(order_id)
    if not order:
        raise ValueError(f"Order {order_id} not found")

    with get_db() as conn:
        cust = conn.execute(
            "SELECT * FROM customers WHERE id=?", (order["customer_id"],)
        ).fetchone()
    if not cust:
        raise ValueError("Customer not found for order")

    raw_addr = decrypt(cust["shipping_address"]) or ""
    name     = decrypt(cust["name"]) or ""
    to_addr  = parse_address(raw_addr, name=name)
    if to_addr.parse_errors:
        print(f"[shipping] Address parse warnings: {to_addr.parse_errors}")

    shop = _load_shop_address()
    total_grams = sum(
        i.get("quantity", 1) * 50
        for i in (order.get("items") or [])
    ) or 100
    weight_oz, l, w, h = _box_for_weight(total_grams)

    from_obj = _shippo_post("/addresses/", {
        "name":    shop.get("name"),
        "street1": shop.get("street1"),
        "city":    shop.get("city"),
        "state":   shop.get("state"),
        "zip":     shop.get("zip5"),
        "country": "US",
        "email":   shop.get("email", ""),
    })
    to_obj = _shippo_post("/addresses/", {
        "name":    to_addr.name,
        "street1": to_addr.street1,
        "street2": to_addr.street2 or "",
        "city":    to_addr.city,
        "state":   to_addr.state,
        "zip":     to_addr.zip5,
        "country": "US",
    })
    parcel_obj = _shippo_post("/parcels/", {
        "length":        str(l),
        "width":         str(w),
        "height":        str(h),
        "distance_unit": "in",
        "weight":        str(round(weight_oz, 2)),
        "mass_unit":     "oz",
    })
    shipment = _shippo_post("/shipments/", {
        "address_from": from_obj["object_id"],
        "address_to":   to_obj["object_id"],
        "parcels":      [parcel_obj["object_id"]],
        "async":        False,
    })

    rates = []
    for r in sorted(shipment.get("rates", []),
                    key=lambda x: float(x.get("amount", 999))):
        rates.append({
            "rate_id":      r["object_id"],
            "carrier":      r.get("provider", ""),
            "service":      r.get("servicelevel", {}).get("name", ""),
            "price_usd":    float(r.get("amount", 0)),
            "days":         r.get("estimated_days"),
            "est_date":     r.get("duration_terms", ""),
            "_shipment_id": shipment["object_id"],
            "_provider":    "shippo",
        })
    return rates


def _buy_label_shippo(order_id: str, service_shorthand: str) -> dict:
    init_shipping()

    key = service_shorthand.lower().replace(" ", "-")
    if key not in SERVICE_MAP:
        raise ValueError(
            f"Unknown service '{service_shorthand}'. "
            f"Valid: {', '.join(SERVICE_MAP.keys())}"
        )
    target_carrier, target_service = SERVICE_MAP[key]

    rates = _get_rates_shippo(order_id)
    match = next(
        (r for r in rates
         if r["carrier"].upper() == target_carrier.upper()
         and target_service.lower() in r["service"].lower()),
        None
    )
    if not match:
        available = [f"{r['carrier']}-{r['service']}" for r in rates[:5]]
        raise ValueError(
            f"No {target_carrier} {target_service} rate found. "
            f"Available: {', '.join(available)}"
        )

    txn = _shippo_post("/transactions/", {
        "rate":            match["rate_id"],
        "label_file_type": "PDF",
        "async":           False,
    })
    if txn.get("status") != "SUCCESS":
        msgs = txn.get("messages", [])
        raise ShippoError(500, "buy_failed", str(msgs) or "Transaction failed")

    tracking  = txn.get("tracking_number", "")
    label_url = txn.get("label_url", "")
    txn_id    = txn.get("object_id", f"shippo-{order_id}")

    order = get_order(order_id)
    cid   = order["customer_id"] if order else 0
    now   = datetime.datetime.utcnow().isoformat() + "Z"

    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO shipments
               (shipment_id, order_id, customer_id, tracking_code, label_url,
                carrier, service, rate_usd, total_cost_usd, weight_oz,
                estimated_delivery, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,'purchased',?)""",
            (txn_id, order_id, cid, tracking, label_url,
             target_carrier, target_service,
             match["price_usd"], match["price_usd"],
             0.0, match.get("est_date", ""), now)
        )

    record = {
        "shipment_id":      txn_id,
        "tracking_code":    tracking,
        "label_url":        label_url,
        "carrier":          target_carrier,
        "service":          target_service,
        "rate_usd":         match["price_usd"],
        "estimated_delivery": match.get("est_date", ""),
    }
    record["label_file_path"] = download_label(txn_id, label_url)
    update_order_status(order_id, "shipped", tracking_number=tracking)
    return record


def _track_shipment_shippo(order_id: str) -> str:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM shipments WHERE order_id=? ORDER BY created_at DESC LIMIT 1",
            (order_id,)
        ).fetchone()
    if not row:
        return f"No shipment found for {order_id}."

    shipment = dict(row)
    carrier  = shipment["carrier"].lower()
    tracking = shipment["tracking_code"]

    try:
        data   = _shippo_get(f"/tracks/{carrier}/{tracking}")
        status = (data.get("tracking_status") or {}).get("status", "unknown")
        detail = (data.get("tracking_status") or {}).get("status_details", "")
        events = data.get("tracking_history", [])

        with get_db() as conn:
            for ev in events:
                loc = ev.get("location") or {}
                conn.execute(
                    """INSERT OR IGNORE INTO tracking_events
                       (shipment_id, event_time, status, detail,
                        location_city, location_state, location_zip)
                       VALUES (?,?,?,?,?,?,?)""",
                    (shipment["shipment_id"],
                     ev.get("status_date", ""),
                     ev.get("status", ""),
                     ev.get("status_details", ""),
                     loc.get("city", ""),
                     loc.get("state", ""),
                     loc.get("zip", ""),
                    )
                )
            conn.execute(
                "UPDATE shipments SET status=? WHERE shipment_id=?",
                (status, shipment["shipment_id"])
            )

        loc_str = ""
        if events:
            loc = (events[-1].get("location") or {})
            city, state = loc.get("city", ""), loc.get("state", "")
            if city or state:
                loc_str = f" — {city} {state}".strip()

        return (
            f"📦 *{order_id}* — {shipment['carrier']} {shipment['service']}\n"
            f"Tracking: `{tracking}`\n"
            f"Status: *{status}*{loc_str}\n"
            f"{detail}"
        )
    except Exception as e:
        return (
            f"📦 *{order_id}* — {shipment['carrier']}\n"
            f"Tracking: `{tracking}`\n"
            f"_(tracking update unavailable: {e})_"
        )


# ══════════════════════════════════════════════════════════════════════════════
# EasyPost provider
# ══════════════════════════════════════════════════════════════════════════════

def _ep_client():
    key = os.environ.get("EASYPOST_API_KEY", EP_API_KEY)
    if not key:
        raise ShippingError(401, "no_key",
                            "EASYPOST_API_KEY not set — add to ~/.config/djinn/easypost.env")
    import easypost
    return easypost.EasyPostClient(api_key=key)


def _get_rates_easypost(order_id: str) -> list:
    order = get_order(order_id)
    if not order:
        raise ValueError(f"Order {order_id} not found")

    with get_db() as conn:
        cust = conn.execute(
            "SELECT * FROM customers WHERE id=?", (order["customer_id"],)
        ).fetchone()
    if not cust:
        raise ValueError("Customer not found for order")

    raw_addr = decrypt(cust["shipping_address"]) or ""
    name     = decrypt(cust["name"]) or ""
    to_addr  = parse_address(raw_addr, name=name)
    if to_addr.parse_errors:
        print(f"[shipping] Address parse warnings: {to_addr.parse_errors}")

    shop = _load_shop_address()
    total_grams = sum(
        i.get("quantity", 1) * 50
        for i in (order.get("items") or [])
    ) or 100
    weight_oz, l, w, h = _box_for_weight(total_grams)

    client = _ep_client()
    try:
        shipment = client.shipment.create(
            to_address={
                "name":    to_addr.name,
                "street1": to_addr.street1,
                "street2": to_addr.street2,
                "city":    to_addr.city,
                "state":   to_addr.state,
                "zip":     to_addr.zip5,
                "country": "US",
            },
            from_address={
                "name":    shop.get("name"),
                "street1": shop.get("street1"),
                "city":    shop.get("city"),
                "state":   shop.get("state"),
                "zip":     shop.get("zip5"),
                "email":   shop.get("email"),
            },
            parcel={
                "weight": weight_oz,
                "length": l,
                "width":  w,
                "height": h,
            },
        )
    except Exception as e:
        raise ShippingError(500, "api_error", str(e))

    rates = []
    for r in sorted(shipment.rates, key=lambda x: float(x.rate)):
        rates.append({
            "rate_id":      r.id,
            "carrier":      r.carrier,
            "service":      r.service,
            "price_usd":    float(r.rate),
            "days":         r.delivery_days,
            "est_date":     r.delivery_date,
            "_shipment_id": shipment.id,
            "_provider":    "easypost",
        })
    return rates


def _buy_label_easypost(order_id: str, service_shorthand: str) -> dict:
    init_shipping()

    key = service_shorthand.lower().replace(" ", "-")
    if key not in SERVICE_MAP:
        raise ValueError(
            f"Unknown service '{service_shorthand}'. "
            f"Valid: {', '.join(SERVICE_MAP.keys())}"
        )
    target_carrier, target_service = SERVICE_MAP[key]

    rates = _get_rates_easypost(order_id)
    match = next(
        (r for r in rates
         if r["carrier"].upper() == target_carrier.upper()
         and target_service.lower() in r["service"].lower()),
        None
    )
    if not match:
        available = [f"{r['carrier']}-{r['service']}" for r in rates[:5]]
        raise ValueError(
            f"No {target_carrier} {target_service} rate found. "
            f"Available: {', '.join(available)}"
        )

    client = _ep_client()
    try:
        shipment  = client.shipment.retrieve(match["_shipment_id"])
        rate_obj  = next(r for r in shipment.rates if r.id == match["rate_id"])
        purchased = client.shipment.buy(shipment.id, rate=rate_obj)
    except Exception as e:
        raise ShippingError(500, "buy_failed", str(e))

    tracking  = purchased.tracking_code or ""
    label_url = purchased.postage_label.label_url if purchased.postage_label else ""
    est       = getattr(purchased.selected_rate, "delivery_date", None) or ""
    rate_usd  = float(purchased.selected_rate.rate)

    order = get_order(order_id)
    cid   = order["customer_id"] if order else 0
    now   = datetime.datetime.utcnow().isoformat() + "Z"

    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO shipments
               (shipment_id, order_id, customer_id, tracking_code, label_url,
                carrier, service, rate_usd, total_cost_usd, weight_oz,
                estimated_delivery, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,'purchased',?)""",
            (purchased.id, order_id, cid, tracking, label_url,
             target_carrier, target_service, rate_usd, rate_usd,
             match.get("weight_oz", 0), est, now)
        )

    record = {
        "shipment_id":      purchased.id,
        "tracking_code":    tracking,
        "label_url":        label_url,
        "carrier":          target_carrier,
        "service":          target_service,
        "rate_usd":         rate_usd,
        "estimated_delivery": est,
    }
    record["label_file_path"] = download_label(purchased.id, label_url)
    update_order_status(order_id, "shipped", tracking_number=tracking)
    return record


def _track_shipment_easypost(order_id: str) -> str:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM shipments WHERE order_id=? ORDER BY created_at DESC LIMIT 1",
            (order_id,)
        ).fetchone()
    if not row:
        return f"No shipment found for {order_id}."

    shipment = dict(row)
    client   = _ep_client()
    try:
        tracker = client.tracker.create(
            tracking_code=shipment["tracking_code"],
            carrier=shipment["carrier"],
        )
        status = tracker.status
        detail = tracker.status_detail or ""
        events = tracker.tracking_details or []

        with get_db() as conn:
            for ev in events:
                tl = getattr(ev, "tracking_location", None)
                conn.execute(
                    """INSERT OR IGNORE INTO tracking_events
                       (shipment_id, event_time, status, detail,
                        location_city, location_state, location_zip)
                       VALUES (?,?,?,?,?,?,?)""",
                    (shipment["shipment_id"],
                     str(getattr(ev, "datetime", "")),
                     str(getattr(ev, "status", "")),
                     str(getattr(ev, "message", "")),
                     str(getattr(tl, "city", "") if tl else ""),
                     str(getattr(tl, "state", "") if tl else ""),
                     str(getattr(tl, "zip", "") if tl else ""),
                    )
                )
            conn.execute(
                "UPDATE shipments SET status=? WHERE shipment_id=?",
                (status, shipment["shipment_id"])
            )

        loc_str = ""
        if events:
            tl = getattr(events[-1], "tracking_location", None)
            if tl:
                city  = getattr(tl, "city", "")
                state = getattr(tl, "state", "")
                if city or state:
                    loc_str = f" — {city} {state}".strip()

        return (
            f"📦 *{order_id}* — {shipment['carrier']} {shipment['service']}\n"
            f"Tracking: `{shipment['tracking_code']}`\n"
            f"Status: *{status}*{loc_str}\n"
            f"{detail}"
        )
    except Exception as e:
        return (
            f"📦 *{order_id}* — {shipment['carrier']}\n"
            f"Tracking: `{shipment['tracking_code']}`\n"
            f"_(tracking update unavailable: {e})_"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Public API — routes to active provider
# ══════════════════════════════════════════════════════════════════════════════

def get_rates(order_id: str) -> list:
    if SHIPPING_PROVIDER == "shippo":
        return _get_rates_shippo(order_id)
    return _get_rates_easypost(order_id)


def buy_label(order_id: str, service_shorthand: str) -> dict:
    if SHIPPING_PROVIDER == "shippo":
        return _buy_label_shippo(order_id, service_shorthand)
    return _buy_label_easypost(order_id, service_shorthand)


def track_shipment(order_id: str) -> str:
    if SHIPPING_PROVIDER == "shippo":
        return _track_shipment_shippo(order_id)
    return _track_shipment_easypost(order_id)


def download_label(shipment_id: str, label_url: str) -> str:
    """Download label PDF, save locally. Returns file path."""
    LABELS_DIR.mkdir(parents=True, exist_ok=True)
    path = LABELS_DIR / f"{shipment_id}.pdf"
    try:
        r = requests.get(label_url, timeout=15)
        r.raise_for_status()
        path.write_bytes(r.content)
        with get_db() as conn:
            conn.execute(
                "UPDATE shipments SET label_file_path=? WHERE shipment_id=?",
                (str(path), shipment_id)
            )
    except Exception as e:
        print(f"[shipping] Label download failed: {e}")
        return ""
    return str(path)


# ── Telegram command handler ──────────────────────────────────────────────────
def _format_rates_message(order_id: str, rates: list) -> str:
    lines = [f"📦 *Rates for {order_id}*\n"]
    for i, r in enumerate(rates[:6]):
        days = f"{r['days']} day{'s' if r['days'] != 1 else ''}" if r.get("days") else ""
        rec  = " ← *recommended*" if i == 1 else ""
        shorthand = f"{r['carrier'].lower()}-{r['service'].lower().replace(' ','')}"
        lines.append(
            f"`{shorthand:<24}` ${r['price_usd']:.2f}  {days}{rec}"
        )
    lines += [
        "",
        f"Reply: `ship {order_id} <carrier-service>`",
        (f"Example: `ship {order_id} {rates[1]['carrier'].lower()}-"
         f"{rates[1]['service'].lower().replace(' ','')}`") if len(rates) > 1 else "",
    ]
    return "\n".join(lines)


def handle_ship_command(order_id: str, service: str = None) -> str:
    try:
        if not service:
            rates = get_rates(order_id)
            if not rates:
                return f"No rates returned for {order_id}. Check address and API key."
            return _format_rates_message(order_id, rates)
        else:
            record = buy_label(order_id, service)
            lines = [
                f"✅ *Label purchased — {order_id}*",
                f"Carrier:  {record['carrier']} {record['service']}",
                f"Tracking: `{record['tracking_code']}`",
                f"Cost:     ${record['rate_usd']:.2f}",
            ]
            if record.get("estimated_delivery"):
                lines.append(f"Est. delivery: {record['estimated_delivery']}")
            if record.get("label_file_path"):
                lines.append(f"Label: `{record['label_file_path']}`")
            return "\n".join(lines)
    except (ShippingError, ValueError) as e:
        return f"⚠️ Shipping error: {e}"


# ── Reporting ─────────────────────────────────────────────────────────────────
def get_shipping_summary(period_start: str, period_end: str) -> dict:
    with get_db() as conn:
        rows = conn.execute(
            """SELECT carrier, status, total_cost_usd
               FROM shipments
               WHERE created_at BETWEEN ? AND ?""",
            (period_start + "T00:00:00Z", period_end + "T23:59:59Z")
        ).fetchall()

    if not rows:
        return {"total_shipments": 0, "total_cost_usd": 0.0}

    total_cost    = sum(r["total_cost_usd"] for r in rows)
    carrier_counts: dict = {}
    delivered = in_transit = errors = 0

    for r in rows:
        carrier_counts[r["carrier"]] = carrier_counts.get(r["carrier"], 0) + 1
        if r["status"] == "delivered":  delivered  += 1
        elif r["status"] == "error":    errors     += 1
        else:                           in_transit += 1

    return {
        "total_shipments":   len(rows),
        "total_cost_usd":    round(total_cost, 2),
        "avg_cost_usd":      round(total_cost / len(rows), 2),
        "carrier_breakdown": carrier_counts,
        "delivered_count":   delivered,
        "in_transit_count":  in_transit,
        "error_count":       errors,
    }


# ── Gateway wiring guide ───────────────────────────────────────────────────────
GATEWAY_WIRING = """
TELEGRAM GATEWAY — add these patterns:

    ship_pattern  = re.compile(r'^ship\\s+(ORD-\\d+)(?:\\s+(\\S+))?$', re.I)
    track_pattern = re.compile(r'^track\\s+(ORD-\\d+)$', re.I)

    m = ship_pattern.match(text)
    if m:
        from shop.shipping_agent import handle_ship_command
        return handle_ship_command(m.group(1), m.group(2))

    m = track_pattern.match(text)
    if m:
        from shop.shipping_agent import track_shipment
        return track_shipment(m.group(1))
"""


if __name__ == "__main__":
    init_db()
    init_shipping()

    # Address parser tests (no API key needed)
    test_cases = [
        ("123 Main St, Los Angeles CA 90001",          "John Diaz"),
        ("456 Oak Ave Apt 2B, San Francisco, CA 94102","Jane Smith"),
        ("55 Pine St, St. Louis MO 63101",             "Bob Jones"),
        ("321 Desert Blvd Suite 4, Las Vegas NV 89101","Maria Garcia"),
    ]
    print("ParsedAddress tests:")
    for raw, name in test_cases:
        a = parse_address(raw, name=name)
        ok = "✅" if a.parse_confidence >= 0.8 and not a.parse_errors else "⚠️ "
        print(f"  {ok} {raw[:45]:<45} conf={a.parse_confidence:.1f} errors={a.parse_errors}")
        print(f"       {format_address_block(a)}")
        print()

    print(f"Shipping provider: {SHIPPING_PROVIDER.upper()}")
    if SHIPPING_PROVIDER == "shippo":
        key = os.environ.get("SHIPPO_API_KEY", SHIPPO_API_KEY)
        print(f"Shippo key:  {'set ✅' if key else 'NOT SET ⚠️  — add SHIPPO_API_KEY to shop.env'}")
    else:
        key = os.environ.get("EASYPOST_API_KEY", EP_API_KEY)
        print(f"EasyPost key: {'set ✅' if key else 'NOT SET ⚠️  — add EASYPOST_API_KEY to env'}")
    print(f"Labels dir:  {LABELS_DIR}")
    print(f"Shop config: {'exists ✅' if SHOP_CFG_PATH.exists() else 'not found — will use defaults'}")

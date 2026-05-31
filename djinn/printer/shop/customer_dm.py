"""
customer_dm.py — Customer ORDER flow for Djinn Shop.

Handles:
  Customer replies ORDER/EXPRESS in #3d-printing
    → Bot DMs payment instructions + asks for name/address/notes
    → Customer replies in DM → stored encrypted in shop.db
    → Owner notified via Telegram (address never hits Discord channels)

  Owner replies "paid ORD-XXXX" in Telegram
    → Order advances to paid → customer DM'd confirmation

  Owner replies "shipped ORD-XXXX <tracking>" in Telegram
    → Order advances to shipped → customer DM'd tracking

  48h cleanup timer → bot deletes its own DM messages

Gateway integration:
  Discord gateway: call handle_order() when ORDER/EXPRESS detected in channel
                   call handle_dm_reply() when DM received from non-owner user
  Telegram gateway: call handle_owner_paid() / handle_owner_shipped() on those patterns

— Claude
"""

import os
import re
import json
import sqlite3
import datetime
import pathlib
import requests
import sys

_SHOP    = pathlib.Path(__file__).parent
_PRINTER = _SHOP.parent
for p in [str(_PRINTER), str(_SHOP)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from shop.db import get_db, init_db, upsert_customer, create_order, add_order_item, \
                    update_order_status, get_order, write_ledger, decrypt, encrypt

from shop.accounting import create_invoice

# ── Config ────────────────────────────────────────────────────────────────────
DISCORD_TOKEN    = os.environ.get("DJINN_DISCORD_TOKEN", "")
DISCORD_API      = "https://discord.com/api/v10"
DISCORD_HEADERS  = lambda: {"Authorization": f"Bot {DISCORD_TOKEN}",
                             "Content-Type": "application/json"}

TG_TOKEN         = os.environ.get("DJINN_TG_TOKEN",
                                   "7962428973:AAHzCibu8E0RDDaRF3eHGA7WcOEqMbypOVI")
TG_API           = f"https://api.telegram.org/bot{TG_TOKEN}"
OWNER_TG_CHAT    = int(os.environ.get("DJINN_TG_ALLOWED", "7620067588").split(",")[0])

ZELLE_HANDLE     = os.environ.get("DJINN_ZELLE",    "typhonsforge@gmail.com")
CASHAPP_TAG      = os.environ.get("DJINN_CASHAPP",  "$TyphonsForge")

DM_EXPIRY_HOURS  = 48

# ── DM session schema ─────────────────────────────────────────────────────────
SESSION_SCHEMA = """
CREATE TABLE IF NOT EXISTS dm_sessions (
    discord_id       TEXT PRIMARY KEY,
    order_id         TEXT,
    state            TEXT NOT NULL DEFAULT 'awaiting_info',
    bot_message_ids  TEXT DEFAULT '[]',
    created_at       TEXT NOT NULL,
    expires_at       TEXT NOT NULL
);
"""


def init_sessions():
    with get_db() as conn:
        conn.executescript(SESSION_SCHEMA)


# ── Discord REST ──────────────────────────────────────────────────────────────
def _discord_post(path: str, payload: dict) -> dict:
    r = requests.post(f"{DISCORD_API}{path}", headers=DISCORD_HEADERS(),
                      json=payload, timeout=10)
    return r.json() if r.content else {}


def _discord_delete(path: str):
    requests.delete(f"{DISCORD_API}{path}", headers=DISCORD_HEADERS(), timeout=10)


def _get_dm_channel(discord_user_id: str) -> str:
    resp = _discord_post("/users/@me/channels", {"recipient_id": discord_user_id})
    return resp.get("id", "")


def send_dm(discord_user_id: str, text: str) -> str:
    """Send a DM to a Discord user. Returns message ID."""
    channel_id = _get_dm_channel(discord_user_id)
    if not channel_id:
        return ""
    resp = _discord_post(f"/channels/{channel_id}/messages", {"content": text})
    return resp.get("id", "")


def delete_dm_message(discord_user_id: str, message_id: str):
    channel_id = _get_dm_channel(discord_user_id)
    if channel_id and message_id:
        _discord_delete(f"/channels/{channel_id}/messages/{message_id}")


# ── Telegram owner notify ─────────────────────────────────────────────────────
def notify_owner(text: str):
    requests.post(f"{TG_API}/sendMessage",
                  json={"chat_id": OWNER_TG_CHAT, "text": text,
                        "parse_mode": "Markdown"},
                  timeout=10)


# ── Address parser (basic — replaced by Marcus's version when delivered) ──────
def parse_address(text: str) -> dict:
    """
    Parse a free-text US address into structured fields.
    Handles: "123 Main St, Los Angeles CA 90001"
             "456 Oak Ave Apt 2B, San Francisco, CA 94102"
             "789 Elm Rd, Miami FL 33101-1234"
    Returns dict with street/city/state/zip, or None if unparseable.
    """
    text = text.strip().replace("\n", ", ")

    pattern = re.compile(
        r'^(.+?),\s*'           # street (everything before first comma)
        r'([A-Za-z\s\.]+?),?\s*'  # city
        r'([A-Z]{2})\s*'        # state (2-letter)
        r'(\d{5}(?:-\d{4})?)'  # zip
        r'\s*$'
    )
    m = pattern.match(text)
    if m:
        return {
            "street": m.group(1).strip(),
            "city":   m.group(2).strip().rstrip(","),
            "state":  m.group(3),
            "zip":    m.group(4),
            "raw":    text,
        }

    # Fallback: split by commas, infer
    parts = [p.strip() for p in text.split(",")]
    if len(parts) >= 2:
        last = parts[-1].strip()
        state_zip = re.search(r'([A-Z]{2})\s+(\d{5}(?:-\d{4})?)', last)
        if state_zip:
            return {
                "street": parts[0],
                "city":   parts[1] if len(parts) > 2 else "",
                "state":  state_zip.group(1),
                "zip":    state_zip.group(2),
                "raw":    text,
            }
    return None


# ── Session helpers ───────────────────────────────────────────────────────────
def _get_session(discord_id: str) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM dm_sessions WHERE discord_id = ?", (discord_id,)
        ).fetchone()
    return dict(row) if row else None


def _set_session(discord_id: str, order_id: str, state: str,
                 bot_message_ids: list = None):
    now     = datetime.datetime.utcnow()
    expires = (now + datetime.timedelta(hours=DM_EXPIRY_HOURS)).isoformat() + "Z"
    msg_ids = json.dumps(bot_message_ids or [])
    with get_db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO dm_sessions
               (discord_id, order_id, state, bot_message_ids, created_at, expires_at)
               VALUES (?,?,?,?,?,?)""",
            (discord_id, order_id, state, msg_ids,
             now.isoformat() + "Z", expires)
        )


def _append_message_id(discord_id: str, message_id: str):
    sess = _get_session(discord_id)
    if not sess:
        return
    ids = json.loads(sess["bot_message_ids"] or "[]")
    ids.append(message_id)
    with get_db() as conn:
        conn.execute(
            "UPDATE dm_sessions SET bot_message_ids = ? WHERE discord_id = ?",
            (json.dumps(ids), discord_id)
        )


def _clear_session(discord_id: str):
    with get_db() as conn:
        conn.execute("DELETE FROM dm_sessions WHERE discord_id = ?", (discord_id,))


# ── ORDER handler (called from Discord gateway) ───────────────────────────────
def handle_order(discord_user_id: str, discord_username: str,
                 order_id: str, total_usd: float,
                 express: bool, quote_data: dict) -> bool:
    """
    Called when customer replies ORDER or EXPRESS in #3d-printing.
    Creates order record, DMs payment instructions.
    Returns True on success.
    """
    init_sessions()

    # Upsert customer (no PII yet — just discord ID)
    cid = upsert_customer(discord_user_id)

    # Create order in db
    payment_method = None  # collected later
    oid = create_order(cid, total_usd,
                       payment_method=payment_method,
                       express=express,
                       notes=None)

    # Save the quote
    from shop.accounting import create_invoice
    create_invoice(oid, cid, total_usd)

    # Add line items from quote_data
    if quote_data:
        add_order_item(
            oid,
            description    = quote_data.get("piece_name", "Custom Print"),
            quantity       = quote_data.get("quantity", 1),
            unit_price     = round(total_usd / max(quote_data.get("quantity", 1), 1), 2),
            material       = quote_data.get("material"),
            smoking_item   = quote_data.get("smoking_accessory", False),
            customizations = {"quote": quote_data},
        )

    # Payment instructions DM
    label = "⚡ Express Print" if express else "Standard"
    msg = (
        f"Thanks for your order! Here are the payment details for **{oid}**:\n\n"
        f"💸 **Zelle:**    {ZELLE_HANDLE}\n"
        f"💸 **CashApp:** {CASHAPP_TAG}\n"
        f"**Amount:** ${total_usd:.2f}  ({label})\n\n"
        f"Once sent, reply here with:\n"
        f"1. Your full name\n"
        f"2. Shipping address\n"
        f"3. Any special requests\n\n"
        f"This conversation will be cleared after {DM_EXPIRY_HOURS} hours. 🔒"
    )

    mid = send_dm(discord_user_id, msg)

    # Store session
    _set_session(discord_user_id, oid, "awaiting_info",
                 bot_message_ids=[mid] if mid else [])

    # Mark order pending payment
    update_order_status(oid, "pending_payment")

    return True


# ── DM reply handler (called from Discord gateway on DM events) ───────────────
def handle_dm_reply(discord_user_id: str, message_text: str,
                    message_id: str = None) -> str:
    """
    Called when a DM is received from a customer.
    Returns a reply string to send back, or "" if nothing to send.
    """
    sess = _get_session(discord_user_id)
    if not sess:
        return ""

    order_id = sess["order_id"]
    state    = sess["state"]

    if state == "awaiting_info":
        return _process_info_reply(discord_user_id, order_id, message_text, message_id)

    return ""


def _process_info_reply(discord_user_id: str, order_id: str,
                         text: str, message_id: str) -> str:
    """Parse name + address + notes from customer DM reply."""
    lines  = [l.strip() for l in text.strip().splitlines() if l.strip()]
    joined = text.strip()

    name    = None
    address = None
    notes   = None

    # Try to find name (first line or "Name: ..." pattern)
    name_match = re.search(r'(?:name[:\s]+)(.+)', joined, re.I)
    if name_match:
        name = name_match.group(1).split("\n")[0].strip()
    elif lines:
        name = lines[0]

    # Try to find address (look for street number pattern)
    addr_match = re.search(r'\d+\s+\w+.*(?:st|ave|rd|blvd|dr|ln|way|ct|pl).*', joined, re.I)
    if addr_match:
        address = addr_match.group(0).strip()
    else:
        # Try labeled
        lbl = re.search(r'(?:address|ship to|shipping)[:\s]+(.+?)(?:\n|$)', joined, re.I)
        if lbl:
            address = lbl.group(1).strip()
        elif len(lines) >= 2:
            address = lines[1]

    # Notes = anything after address line
    notes_match = re.search(
        r'(?:notes?|special\s+request|requests?)[:\s]+(.+?)(?:\n|$)', joined, re.I
    )
    if notes_match:
        notes = notes_match.group(1).strip()
    elif len(lines) >= 3:
        notes = " ".join(lines[2:])

    # Validate we have minimum info
    missing = []
    if not name:
        missing.append("your name")
    if not address:
        missing.append("your shipping address")

    if missing:
        reply = (
            f"I just need a couple more details:\n"
            + "\n".join(f"• {m}" for m in missing)
            + "\n\nReply with both and I'll confirm your order."
        )
        mid = send_dm(discord_user_id, reply)
        if mid:
            _append_message_id(discord_user_id, mid)
        return ""

    # Parse structured address
    parsed_addr = parse_address(address)
    addr_display = address  # raw for storage

    # Upsert customer with PII
    cid = upsert_customer(
        discord_user_id,
        name     = name,
        address  = addr_display,
    )

    # Update order notes
    update_order_status(order_id, "pending_payment",
                        notes=notes)

    # Mark session complete
    _set_session(discord_user_id, order_id, "info_received")

    # Confirm to customer
    reply = (
        f"Got it — payment confirmation pending.\n\n"
        f"Once we receive your payment we'll confirm your order "
        f"and let you know when printing starts. 🖨️"
    )
    mid = send_dm(discord_user_id, reply)
    if mid:
        _append_message_id(discord_user_id, mid)

    # Notify owner via Telegram (address ONLY goes here, never to Discord channel)
    order = get_order(order_id)
    items_summary = ""
    if order and order["items"]:
        items_summary = "\n".join(
            f"  ×{i['quantity']} {i['description']}"
            for i in order["items"]
        )

    addr_line = ""
    if parsed_addr:
        addr_line = (f"{parsed_addr['street']}, "
                     f"{parsed_addr['city']} {parsed_addr['state']} {parsed_addr['zip']}")
    else:
        addr_line = addr_display

    owner_msg = (
        f"⏳ *{order_id} — Payment Pending*\n\n"
        f"Customer: {name}\n"
        f"Discord:  {discord_user_id}\n"
        f"Ship to:  {addr_line}\n"
        f"Amount:   ${order['total_usd']:.2f if order else 0:.2f}\n"
        f"{items_summary}\n"
        + (f"Notes:    {notes}\n" if notes else "")
        + f"\nConfirm payment received:\n`paid {order_id}`"
    )
    notify_owner(owner_msg)

    return ""


# ── Owner: confirm payment (called from Telegram gateway) ─────────────────────
def handle_owner_paid(order_id: str, payment_ref: str = None) -> str:
    """
    Called when owner sends "paid ORD-XXXX" in Telegram.
    Returns status message for owner.
    """
    order = get_order(order_id)
    if not order:
        return f"Order {order_id} not found."

    update_order_status(order_id, "paid", payment_ref=payment_ref)

    # Update invoice
    with get_db() as conn:
        inv = conn.execute(
            "SELECT invoice_id, total_charged FROM invoices WHERE order_id=? LIMIT 1",
            (order_id,)
        ).fetchone()
    if inv:
        from shop.accounting import mark_invoice_paid
        mark_invoice_paid(inv["invoice_id"], inv["total_charged"],
                          payment_ref=payment_ref)

    # Write ledger entry
    if order["items"]:
        desc = ", ".join(f'×{i["quantity"]} {i["description"]}'
                         for i in order["items"])
    else:
        desc = order_id
    write_ledger(
        order_id, desc,
        revenue      = order["total_usd"],
        labor_cost   = 6.67 * len(order["items"] or [1]),
    )

    # DM customer confirmation
    discord_id = _get_discord_id_for_order(order_id)
    if discord_id:
        mid = send_dm(discord_id,
            f"✅ Payment confirmed — thank you!\n\n"
            f"Your order **{order_id}** is in the queue. "
            f"We'll message you when printing starts. 🖨️"
        )
        if mid:
            _append_message_id(discord_id, mid)

    return f"✅ {order_id} marked paid. Customer notified."


# ── Owner: mark shipped (called from Telegram gateway) ────────────────────────
def handle_owner_shipped(order_id: str, tracking: str = "") -> str:
    """
    Called when owner sends "shipped ORD-XXXX <tracking>" in Telegram.
    """
    order = get_order(order_id)
    if not order:
        return f"Order {order_id} not found."

    update_order_status(order_id, "shipped", tracking_number=tracking)

    discord_id = _get_discord_id_for_order(order_id)
    if discord_id:
        msg = f"📦 Your order has shipped!\n\nOrder: **{order_id}**"
        if tracking:
            msg += f"\nTracking: `{tracking}`"
        mid = send_dm(discord_id, msg)
        if mid:
            _append_message_id(discord_id, mid)

    return f"✅ {order_id} marked shipped. Customer notified."


# ── 48h cleanup (called by systemd timer) ─────────────────────────────────────
def cleanup_expired_sessions():
    """Delete bot DM messages for sessions older than DM_EXPIRY_HOURS."""
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with get_db() as conn:
        expired = conn.execute(
            "SELECT * FROM dm_sessions WHERE expires_at < ? AND state != 'cleaned'",
            (now,)
        ).fetchall()

    cleaned = 0
    for sess in expired:
        discord_id  = sess["discord_id"]
        message_ids = json.loads(sess["bot_message_ids"] or "[]")
        for mid in message_ids:
            delete_dm_message(discord_id, mid)
            cleaned += 1
        with get_db() as conn:
            conn.execute(
                "UPDATE dm_sessions SET state='cleaned' WHERE discord_id=?",
                (discord_id,)
            )

    if cleaned:
        print(f"[customer_dm] Cleaned {cleaned} DM messages from {len(expired)} sessions.")
    return cleaned


# ── Helpers ───────────────────────────────────────────────────────────────────
def _get_discord_id_for_order(order_id: str) -> str:
    order = get_order(order_id)
    if not order:
        return ""
    with get_db() as conn:
        row = conn.execute(
            "SELECT discord_id FROM customers WHERE id = ?",
            (order["customer_id"],)
        ).fetchone()
    return row["discord_id"] if row else ""


# ── Gateway wiring guide ───────────────────────────────────────────────────────
GATEWAY_WIRING = """
DISCORD GATEWAY — add these patterns to the route table:

    (re.compile(r'^(order|express)$', re.I), handle_channel_order),

    def handle_channel_order(m, _raw, ctx):
        express = m.lower() == 'express'
        # retrieve last quote for this user from shop.db or cache
        # then:
        from shop.customer_dm import handle_order
        handle_order(
            discord_user_id  = str(ctx['author_id']),
            discord_username = ctx['author_name'],
            order_id         = pending_order_id,
            total_usd        = quote['recommended_price_usd'],
            express          = express,
            quote_data       = quote,
        )
        return "Got it — check your DMs for payment details."

    # DM handler — in on_message, add:
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != client.user.id:
            from shop.customer_dm import handle_dm_reply
            handle_dm_reply(str(message.author.id), message.content, str(message.id))

TELEGRAM GATEWAY — add these patterns:

    paid_pattern   = re.compile(r'^paid\s+(ORD-\d+)(?:\s+(.+))?$', re.I)
    shipped_pattern = re.compile(r'^shipped\s+(ORD-\d+)(?:\s+(.+))?$', re.I)

    m = paid_pattern.match(text)
    if m:
        from shop.customer_dm import handle_owner_paid
        return handle_owner_paid(m.group(1), m.group(2))

    m = shipped_pattern.match(text)
    if m:
        from shop.customer_dm import handle_owner_shipped
        return handle_owner_shipped(m.group(1), m.group(2))
"""


if __name__ == "__main__":
    init_db()
    init_sessions()

    # Self-test: address parser
    test_addrs = [
        "123 Main St, Los Angeles CA 90001",
        "456 Oak Ave Apt 2B, San Francisco, CA 94102",
        "789 Elm Rd, Miami FL 33101-1234",
        "1010 Broadway, New York NY 10001",
        "55 Pine St, St. Louis MO 63101",
        "321 Desert Blvd Suite 4, Las Vegas NV 89101",
    ]
    print("Address parser tests:")
    for a in test_addrs:
        result = parse_address(a)
        status = "✅" if result and result.get("zip") else "⚠️ "
        print(f"  {status} {a}")
        if result:
            print(f"       → {result['street']} | {result['city']} | {result['state']} {result['zip']}")
        else:
            print(f"       → FAILED — needs manual review")
    print("\nGateway wiring guide available as customer_dm.GATEWAY_WIRING")

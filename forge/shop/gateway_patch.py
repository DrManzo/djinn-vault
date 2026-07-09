"""
gateway_patch.py — Patches djinn-discord-gateway and djinn-telegram-gateway
to wire in the shop system (ORDER flow, inventory, shipping, paid/shipped).

Safe to run multiple times — checks for SHOP_PATCH_APPLIED marker before patching.
Creates .bak backup of each file before modifying.

Run: python3 gateway_patch.py
     python3 gateway_patch.py --check   (dry run, no writes)

— Claude
"""

import sys
import shutil
import pathlib
import argparse

DISCORD_GW  = pathlib.Path.home() / ".local/bin/djinn-discord-gateway"
TELEGRAM_GW = pathlib.Path.home() / ".local/bin/djinn-telegram-gateway"
MARKER      = "# SHOP_PATCH_APPLIED"

# ── Code blocks to inject ─────────────────────────────────────────────────────

DISCORD_IMPORTS = '''
# SHOP_PATCH_APPLIED
import pathlib as _pl
_PRINTER_SHOP = _pl.Path.home() / "Obsidian/djinn/printer"
if str(_PRINTER_SHOP) not in sys.path:
    sys.path.insert(0, str(_PRINTER_SHOP))


def _shop_pending_quote(discord_user_id: str) -> dict:
    """Retrieve the last quoted order for this Discord user from shop.db."""
    try:
        import json
        from shop.db import get_db
        with get_db() as conn:
            row = conn.execute(
                """SELECT q.quote_json, o.id as order_id, o.total_usd
                   FROM quotes q JOIN orders o ON o.id = q.order_id
                   JOIN customers c ON c.id = q.customer_id
                   WHERE c.discord_id = ? AND o.status = 'quoted'
                   ORDER BY q.created_at DESC LIMIT 1""",
                (discord_user_id,)
            ).fetchone()
        if row:
            return {"order_id": row["order_id"], "total_usd": row["total_usd"],
                    "quote": json.loads(row["quote_json"])}
    except Exception:
        pass
    return {}


def _quote_from_history(discord_user_id: str, discord_username: str) -> dict:
    """
    Fallback: read the last entry from quote-history.jsonl and create
    a shop.db record on-the-fly when ORDER is received.
    Bridges the old djinn-print-quote CLI flow with the new shop system.
    """
    import json, pathlib
    history = pathlib.Path.home() / "Obsidian/djinn/printer/commissions/quote-history.jsonl"
    if not history.exists():
        return {}
    try:
        lines = [l for l in history.read_text().strip().splitlines() if l.strip()]
        if not lines:
            return {}
        last = json.loads(lines[-1])
        # quote-history.jsonl stores {timestamp, input, result} or {timestamp, brief, quote}
        result = last.get("result") or last.get("quote") or {}
        total = (result.get("fair_market_estimate")
                 or result.get("fair_market_usd")
                 or result.get("recommended_price_usd")
                 or result.get("price")
                 or 0.0)
        if not total or total <= 0:
            return {}
        from shop.db import upsert_customer, create_order, add_order_item
        from shop.accounting import create_invoice
        from shop.db import save_quote
        cid = upsert_customer(discord_user_id, discord_username)
        oid = create_order(cid, float(total), payment_method=None, express=False)
        piece = result.get("piece_name", "Custom Print")
        qty   = result.get("quantity", 1)
        add_order_item(oid, piece, qty,
                       round(float(total) / max(qty, 1), 2),
                       smoking_item=bool(result.get("smoking_accessory", False)))
        save_quote(oid, cid, result)
        create_invoice(oid, cid, float(total))
        return {"order_id": oid, "total_usd": float(total), "quote": result}
    except Exception as e:
        print(f"[shop] quote-history fallback error: {e}")
        return {}


def handle_order_express(m, _raw, ctx, discord_user_id="", discord_username="") -> str:
    express = _raw.strip().lower().startswith("express")
    # Try shop.db first (intake_agent flow)
    pending = _shop_pending_quote(discord_user_id)
    # Fallback: last entry in quote-history.jsonl (CLI quote flow)
    if not pending:
        pending = _quote_from_history(discord_user_id, discord_username)
    if not pending:
        return "No pending quote found — drop a file or describe what you want first."
    try:
        from shop.customer_dm import handle_order
        handle_order(
            discord_user_id=discord_user_id,
            discord_username=discord_username,
            order_id=pending["order_id"],
            total_usd=pending["total_usd"],
            express=express,
            quote_data=pending.get("quote", {}),
        )
        return "Order received — check your DMs for payment details."
    except Exception as e:
        return f"Order error: {e}"


def handle_order_express_route(m, _raw, ctx) -> str:
    # Called from route table — no user_id available here.
    # Real handling is in on_message below (has message.author.id).
    # This stub prevents "unknown command" fallthrough.
    return ""


def handle_inventory_cmd(m, _raw, ctx) -> str:
    try:
        from shop.inventory import format_stock_report, init_inventory
        init_inventory()
        return format_stock_report()
    except Exception as e:
        return f"Inventory error: {e}"


def handle_low_stock_cmd(m, _raw, ctx) -> str:
    try:
        from shop.inventory import low_stock_alert, init_inventory
        init_inventory()
        alerts = low_stock_alert()
        if not alerts:
            return "No low stock alerts — all spools OK."
        return "\\n".join([f"  {s['color']} {s['material']}: {s['grams_remaining']:.0f}g"
                           for s in alerts])
    except Exception as e:
        return f"Error: {e}"


def handle_add_filament_cmd(m, _raw, ctx) -> str:
    try:
        from shop.inventory import parse_add_command, add_spool, init_inventory
        init_inventory()
        cmd = parse_add_command(_raw)
        if not cmd:
            return "Format: add filament <material> <color> <grams>g $<cost>"
        spool_id = add_spool(**cmd)
        return f"Added {cmd['color']} {cmd['material']} {cmd['weight_g']:.0f}g spool (#{spool_id})."
    except Exception as e:
        return f"Error: {e}"

'''

DISCORD_ROUTES = '''\
    (re.compile(r"^(order|express)$", re.I),        handle_order_express_route),
    (re.compile(r"^inventory$", re.I),              handle_inventory_cmd),
    (re.compile(r"^low\\s+stock$", re.I),            handle_low_stock_cmd),
    (re.compile(r"^add\\s+filament\\b", re.I),       handle_add_filament_cmd),
'''

DISCORD_ON_MESSAGE_PATCH = '''\
    # ── Customer ORDER/EXPRESS + DM handling (SHOP_PATCH_APPLIED) ─────────────
    if message.author.id != ALLOWED_USER:
        import discord as _dc
        _is_print = CHANNEL_CTX.get(message.channel.id) == "print"
        _is_order = message.content.strip().lower() in ("order", "express")
        _is_dm    = isinstance(message.channel, _dc.DMChannel)
        if _is_print and _is_order:
            reply = handle_order_express(
                None, message.content, "print",
                discord_user_id=str(message.author.id),
                discord_username=str(message.author),
            )
            if reply:
                await message.channel.send(reply)
            return
        if _is_dm:
            try:
                from shop.customer_dm import handle_dm_reply
                handle_dm_reply(str(message.author.id),
                                message.content, str(message.id))
            except Exception:
                pass
            return
        return
    # ── END SHOP PATCH ──────────────────────────────────────────────────────────
'''

TELEGRAM_IMPORTS = '''
# SHOP_PATCH_APPLIED
import pathlib as _pl
_PRINTER_SHOP = _pl.Path.home() / "Obsidian/djinn/printer"
if str(_PRINTER_SHOP) not in sys.path:
    sys.path.insert(0, str(_PRINTER_SHOP))


def handle_paid(m, _raw):
    oid = m.group(1).upper()
    ref = m.group(2).strip() if m.group(2) else None
    try:
        from shop.customer_dm import handle_owner_paid
        return handle_owner_paid(oid, ref)
    except Exception as e:
        return f"Error: {e}"


def handle_shipped(m, _raw):
    oid      = m.group(1).upper()
    tracking = m.group(2).strip() if m.group(2) else ""
    try:
        from shop.customer_dm import handle_owner_shipped
        return handle_owner_shipped(oid, tracking)
    except Exception as e:
        return f"Error: {e}"


def handle_ship(m, _raw):
    oid     = m.group(1).upper()
    service = m.group(2).strip() if m.group(2) else None
    try:
        from shop.shipping_agent import handle_ship_command
        return handle_ship_command(oid, service)
    except Exception as e:
        return f"Shipping error: {e}"


def handle_track(m, _raw):
    try:
        from shop.shipping_agent import track_shipment
        return track_shipment(m.group(1).upper())
    except Exception as e:
        return f"Tracking error: {e}"


def handle_inventory_tg(_m, _raw):
    try:
        from shop.inventory import format_stock_report, init_inventory
        init_inventory()
        return format_stock_report()
    except Exception as e:
        return f"Inventory error: {e}"


def handle_low_stock_tg(_m, _raw):
    try:
        from shop.inventory import low_stock_alert, init_inventory
        init_inventory()
        alerts = low_stock_alert()
        if not alerts:
            return "No low stock alerts."
        return "\\n".join([f"  {s['color']} {s['material']}: {s['grams_remaining']:.0f}g"
                           for s in alerts])
    except Exception as e:
        return f"Error: {e}"


def handle_add_filament_tg(m, _raw):
    try:
        from shop.inventory import parse_add_command, add_spool, init_inventory
        init_inventory()
        cmd = parse_add_command(_raw)
        if not cmd:
            return "Format: add filament <material> <color> <grams>g $<cost>"
        spool_id = add_spool(**cmd)
        return f"Added {cmd['color']} {cmd['material']} {cmd['weight_g']:.0f}g spool."
    except Exception as e:
        return f"Error: {e}"

'''

TELEGRAM_ROUTES = '''\
    (re.compile(r"^paid\\s+(ORD-\\d+)(?:\\s+(.+))?$", re.I),          handle_paid),
    (re.compile(r"^shipped\\s+(ORD-\\d+)(?:\\s+(.+))?$", re.I),       handle_shipped),
    (re.compile(r"^ship\\s+(ORD-\\d+)(?:\\s+(\\S+))?$", re.I),        handle_ship),
    (re.compile(r"^track\\s+(ORD-\\d+)$", re.I),                      handle_track),
    (re.compile(r"^inventory$", re.I),                                 handle_inventory_tg),
    (re.compile(r"^low\\s+stock$", re.I),                              handle_low_stock_tg),
    (re.compile(r"^add\\s+filament\\b", re.I),                         handle_add_filament_tg),
'''


# ── Patch helpers ─────────────────────────────────────────────────────────────
def _backup(path: pathlib.Path):
    bak = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, bak)
    print(f"  Backup: {bak}")


def _patch(path: pathlib.Path, anchor: str, insert: str,
           after: bool = False, dry_run: bool = False) -> bool:
    """Insert `insert` before (or after) `anchor` in file. Returns True if patched."""
    content = path.read_text()
    if anchor not in content:
        print(f"  ⚠️  Anchor not found in {path.name}: {anchor[:50]!r}")
        return False
    if after:
        new_content = content.replace(anchor, anchor + insert, 1)
    else:
        new_content = content.replace(anchor, insert + anchor, 1)
    if dry_run:
        print(f"  [dry-run] Would patch {path.name} at anchor: {anchor[:50]!r}")
        return True
    path.write_text(new_content)
    return True


def patch_discord(dry_run: bool = False) -> bool:
    if not DISCORD_GW.exists():
        print(f"  ⚠️  Not found: {DISCORD_GW}")
        return False

    content = DISCORD_GW.read_text()
    if MARKER in content:
        print(f"  Discord gateway already patched — skipping.")
        return True

    print(f"  Patching {DISCORD_GW.name}...")
    if not dry_run:
        _backup(DISCORD_GW)

    # 1. Inject imports + handlers before ROUTES_PRINT
    ok1 = _patch(DISCORD_GW, "ROUTES_PRINT = [", DISCORD_IMPORTS,
                 after=False, dry_run=dry_run)

    # 2. Inject ORDER/inventory/filament routes into ROUTES_PRINT
    ok2 = _patch(DISCORD_GW,
                 '    (re.compile(r"^3?d?queue$", re.I),',
                 DISCORD_ROUTES,
                 after=False, dry_run=dry_run)

    # 3. REPLACE the simple ALLOWED_USER check with the customer-aware version.
    #    Must be a replace (not insert) — DISCORD_ON_MESSAGE_PATCH already
    #    starts with `if message.author.id != ALLOWED_USER:` so inserting before
    #    would duplicate the line.
    anchor3 = "    if message.author.id != ALLOWED_USER:\n        return"
    if dry_run:
        ok3 = anchor3 in DISCORD_GW.read_text()
        print(f"  [dry-run] on_message replace anchor {'found ✅' if ok3 else 'NOT FOUND ⚠️'}")
    else:
        content3 = DISCORD_GW.read_text()
        if anchor3 in content3:
            DISCORD_GW.write_text(content3.replace(anchor3, DISCORD_ON_MESSAGE_PATCH, 1))
            ok3 = True
        else:
            print(f"  ⚠️  on_message anchor not found — Discord customer handling not wired")
            ok3 = False

    if ok1 and ok2 and ok3:
        print(f"  Discord gateway patched ✅")
        return True
    print(f"  Discord gateway partial patch ⚠️  — check manually")
    return False


def patch_telegram(dry_run: bool = False) -> bool:
    if not TELEGRAM_GW.exists():
        print(f"  ⚠️  Not found: {TELEGRAM_GW}")
        return False

    content = TELEGRAM_GW.read_text()
    if MARKER in content:
        print(f"  Telegram gateway already patched — skipping.")
        return True

    print(f"  Patching {TELEGRAM_GW.name}...")
    if not dry_run:
        _backup(TELEGRAM_GW)

    # 1. Inject imports + handlers before ROUTES
    ok1 = _patch(TELEGRAM_GW,
                 "# ── Routing table (order matters — most specific first) ───────────────────────",
                 TELEGRAM_IMPORTS,
                 after=False, dry_run=dry_run)

    # 2. Inject shop routes into ROUTES list — anchor is the design_status route
    #    Exact match: 4-space indent, split across two lines in the file.
    tg_route_anchor = '    (re.compile(r"^design\\s+status$", re.I),\n        handle_design_status),'
    ok2 = _patch(TELEGRAM_GW, tg_route_anchor, TELEGRAM_ROUTES,
                 after=False, dry_run=dry_run)

    # 3. Patch dispatch() to match paid/shipped without / prefix
    old_dispatch_head = "def dispatch(text):\n    \"\"\"Route a message to a handler or fall through to model.\"\"\"\n    if not text.startswith(\"/\"):\n        return sign(ask_model(text))"
    new_dispatch_head = """def dispatch(text):
    \"\"\"Route a message to a handler or fall through to model.\"\"\"
    # SHOP_PATCH_APPLIED — check non-slash shop commands first
    if not text.startswith("/"):
        _clean = text.strip()
        for _pat, _fn in ROUTES:
            _m = _pat.match(_clean)
            if _m:
                return sign(_fn(_m, text))
        return sign(ask_model(text))"""
    if old_dispatch_head in (TELEGRAM_GW.read_text() if not dry_run else content):
        if not dry_run:
            TELEGRAM_GW.write_text(
                TELEGRAM_GW.read_text().replace(old_dispatch_head, new_dispatch_head, 1)
            )
        ok3 = True
    else:
        print("  ⚠️  dispatch() anchor not found — paid/shipped won't work without /prefix")
        ok3 = False

    if ok1 and ok2:
        print(f"  Telegram gateway patched ✅")
        return True
    print(f"  Telegram gateway partial patch ⚠️  — check manually")
    return False


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Dry run only")
    parser.add_argument("--discord-only", action="store_true")
    parser.add_argument("--telegram-only", action="store_true")
    args = parser.parse_args()

    dry = args.check
    print(f"Gateway patch {'(DRY RUN)' if dry else ''}")
    print()

    results = []
    if not args.telegram_only:
        results.append(("Discord", patch_discord(dry_run=dry)))
    if not args.discord_only:
        results.append(("Telegram", patch_telegram(dry_run=dry)))

    print()
    for name, ok in results:
        print(f"  {name}: {'✅' if ok else '⚠️  check manually'}")

    if not dry and all(r for _, r in results):
        print()
        print("Both gateways patched. Restart services:")
        print("  systemctl --user restart djinn-discord-gateway djinn-telegram-gateway")


if __name__ == "__main__":
    main()

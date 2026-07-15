"""
dashboard/app.py — Typhon's Forge unified dashboard.

Merges fleet status (printer cards + live polling) with the shop back-office
(orders, customers, finance, reports) and a live-editable filament inventory.

Port: 8420.  Auth: session password (DJINN_DASH_PASSWORD env, default "typhonsforge").
"""

import os
import sys
import json
import hashlib
import datetime
import pathlib
import secrets
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

import requests
from flask import (Flask, render_template, redirect, url_for,
                   request, session, flash, jsonify, send_file)

# ── path setup ─────────────────────────────────────────────────────────────────
_HERE    = pathlib.Path(__file__).parent
_SHOP    = _HERE.parent
_PRINTER = _SHOP.parent
for p in [str(_PRINTER), str(_SHOP)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from shop.db import (
    init_db, _connect, get_db, decrypt,
    get_pending_orders, get_order, get_customer,
    update_order_status, SHOP_DIR,
    upsert_customer, create_order, add_order_item,
)
from shop.accounting import (
    init_accounting, compute_income_statement,
    compute_balance_sheet, compute_monthly_report,
    get_customer_ledger, dashboard_summary,
    export_csv, export_xlsx, create_invoice,
)

# ── config ─────────────────────────────────────────────────────────────────────
DASHBOARD_PASSWORD = os.environ.get("DJINN_DASH_PASSWORD", "typhonsforge")
SECRET_KEY         = os.environ.get("DJINN_SECRET_KEY",    "change-me-at-setup")
PORT               = int(os.environ.get("FLASK_PORT", 8420))

REGISTRY_PATH   = pathlib.Path.home() / ".config/forge/fleet-registry.json"
INVENTORY_PATH  = pathlib.Path.home() / "Obsidian/forge/inventory/filament-inventory.json"
FETCH_TIMEOUT   = 3

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = SECRET_KEY

_COLOR_HEX = {
    "white":        "#e8e8e8",
    "black":        "#333333",
    "red":          "#cc3333",
    "yellow":       "#e8c020",
    "blue":         "#3060cc",
    "grey":         "#7a8a9a",
    "gray":         "#7a8a9a",
    "orange":       "#e07020",
    "green":        "#38a858",
    "army green":   "#556b2f",
    "silver":       "#aab8c0",
    "gold":         "#c8a020",
    "purple":       "#8040b0",
    "pink":         "#d06090",
    "cyan":         "#20a8c0",
    "brown":        "#7a4828",
    "transparent":  "#6a8aaa",
    "natural":      "#d8cbb8",
    "burnt titanium": "#7a6858",
    "glow in the dark": "#a8e050",
    "multi":        "#884488",
    "ruby red":     "#a02040",
}

@app.template_filter("color_hex")
def color_hex_filter(color_name: str) -> str:
    return _COLOR_HEX.get(color_name.lower(), "#5a7a9a")


# ── init DB ────────────────────────────────────────────────────────────────────
with app.app_context():
    init_db()
    conn = _connect()
    init_accounting(conn)
    conn.close()


# ── auth ───────────────────────────────────────────────────────────────────────
def _pw_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _logged_in() -> bool:
    return session.get("auth") == _pw_hash(DASHBOARD_PASSWORD)

def _require_login(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _logged_in():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if _pw_hash(pw) == _pw_hash(DASHBOARD_PASSWORD):
            session["auth"] = _pw_hash(DASHBOARD_PASSWORD)
            return redirect(url_for("dashboard"))
        flash("Wrong password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── fleet polling ──────────────────────────────────────────────────────────────
def _load_registry():
    try:
        return json.loads(REGISTRY_PATH.read_text()).get("printers", [])
    except Exception:
        return []

def _fetch_moonraker(printer):
    r = {**printer, "reachable": False, "state": "offline",
         "filename": None, "progress_pct": None, "bed_temp": None, "nozzle_temp": None}
    try:
        resp = requests.get(
            f"{printer['api_url']}/printer/objects/query"
            "?print_stats&virtual_sdcard&extruder&heater_bed",
            timeout=FETCH_TIMEOUT,
        )
        resp.raise_for_status()
        status = resp.json().get("result", {}).get("status", {})
        ps = status.get("print_stats", {})
        vs = status.get("virtual_sdcard", {})
        r.update({
            "reachable": True,
            "state": ps.get("state", "unknown"),
            "filename": ps.get("filename") or None,
            "progress_pct": round((vs.get("progress") or 0) * 100, 1) if ps.get("state") == "printing" else None,
            "bed_temp": status.get("heater_bed", {}).get("temperature"),
            "nozzle_temp": status.get("extruder", {}).get("temperature"),
        })
    except Exception:
        pass
    return r

def _fetch_octoprint(printer):
    r = {**printer, "reachable": False, "state": "offline",
         "filename": None, "progress_pct": None, "bed_temp": None, "nozzle_temp": None}
    api_key = os.environ.get(printer.get("api_key_env", ""), "")
    try:
        headers = {"X-Api-Key": api_key}
        resp = requests.get(f"{printer['api_url']}/api/job", headers=headers, timeout=FETCH_TIMEOUT)
        resp.raise_for_status()
        job = resp.json()
        state = job.get("state", "Unknown")
        progress = job.get("progress", {}).get("completion")
        r.update({
            "reachable": True,
            "state": "printing" if state == "Printing" else state.lower(),
            "filename": (job.get("job", {}) or {}).get("file", {}).get("name"),
            "progress_pct": round(progress, 1) if progress is not None else None,
        })
        r2 = requests.get(f"{printer['api_url']}/api/printer", headers=headers, timeout=FETCH_TIMEOUT)
        if r2.ok:
            temps = r2.json().get("temperature", {})
            r["nozzle_temp"] = (temps.get("tool0") or {}).get("actual")
            r["bed_temp"] = (temps.get("bed") or {}).get("actual")
    except Exception:
        pass
    return r

_FETCHERS = {"moonraker": _fetch_moonraker, "octoprint": _fetch_octoprint}

def fetch_all():
    printers = _load_registry()
    results = []
    with ThreadPoolExecutor(max_workers=max(len(printers), 1)) as pool:
        futures = {
            pool.submit(_FETCHERS.get(p.get("backend"), _fetch_moonraker), p): p
            for p in printers
        }
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception:
                p = futures[fut]
                results.append({**p, "reachable": False, "state": "error",
                                 "filename": None, "progress_pct": None,
                                 "bed_temp": None, "nozzle_temp": None})
    order = {p["id"]: i for i, p in enumerate(printers)}
    results.sort(key=lambda r: order.get(r["id"], 999))
    return results


# ── filament inventory helpers ─────────────────────────────────────────────────
def _load_inventory():
    try:
        return json.loads(INVENTORY_PATH.read_text())
    except Exception:
        return {"spools": [], "printers": {}}

def _save_inventory(data: dict):
    INVENTORY_PATH.write_text(json.dumps(data, indent=2))


# ── helpers ────────────────────────────────────────────────────────────────────
def _get_customer_by_id(customer_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
    if not row:
        return {"name": "Unknown", "discord_id": "—"}
    d = dict(row)
    d["name"]             = decrypt(d["name"]) or "—"
    d["shipping_address"] = decrypt(d["shipping_address"]) or "—"
    return d

def _today() -> str:
    return datetime.date.today().isoformat()

def _month_bounds(year=None, month=None):
    now = datetime.date.today()
    y = year  or now.year
    m = month or now.month
    start = f"{y:04d}-{m:02d}-01"
    end   = f"{y}-12-31" if m == 12 else (datetime.date(y, m+1, 1) - datetime.timedelta(days=1)).isoformat()
    return start, end


# ── context processor ─────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    queue_count = 0
    try:
        queue_count = len(get_pending_orders())
    except Exception:
        pass
    now = datetime.date.today()
    return {
        "queue_count": queue_count,
        "current_month": now.strftime("%B %Y"),
    }


# ── fleet API ──────────────────────────────────────────────────────────────────
@app.route("/api/status")
@_require_login
def api_status():
    return jsonify(fetch_all())


# ── inventory API ──────────────────────────────────────────────────────────────
@app.route("/api/inventory/<spool_id>", methods=["POST"])
@_require_login
def api_inventory_update(spool_id):
    data = _load_inventory()
    payload = request.get_json(force=True) or {}
    updated = False
    for spool in data.get("spools", []):
        if spool["spool_id"] == spool_id:
            if "remaining_g" in payload:
                try:
                    spool["remaining_g"] = max(0, int(payload["remaining_g"]))
                except (ValueError, TypeError):
                    return jsonify({"error": "invalid remaining_g"}), 400
            if "notes" in payload:
                spool["notes"] = str(payload["notes"])[:200]
            if "loaded" in payload:
                spool["loaded"] = bool(payload["loaded"])
            if "loaded_printer" in payload:
                spool["loaded_printer"] = str(payload["loaded_printer"])
            spool["last_used"] = _today()
            updated = True
            break
    if not updated:
        return jsonify({"error": "spool not found"}), 404
    data["last_updated"] = _today()
    data["updated_by"] = "dashboard"
    _save_inventory(data)
    return jsonify({"ok": True})


@app.route("/api/inventory", methods=["POST"])
@_require_login
def api_inventory_add():
    data = _load_inventory()
    payload = request.get_json(force=True) or {}

    material = str(payload.get("material", "")).strip()
    color    = str(payload.get("color", "")).strip()
    brand    = str(payload.get("brand", "")).strip()
    if not material or not color or not brand:
        return jsonify({"error": "material, color, and brand are required"}), 400

    try:
        initial_weight_g = max(1, int(payload.get("initial_weight_g", 1000)))
    except (ValueError, TypeError):
        return jsonify({"error": "invalid initial_weight_g"}), 400
    try:
        low_threshold_g = max(0, int(payload.get("low_threshold_g", 150)))
    except (ValueError, TypeError):
        low_threshold_g = 150

    existing_nums = [
        int(s["spool_id"].split("-")[1])
        for s in data.get("spools", [])
        if s.get("spool_id", "").startswith("SPOOL-") and s["spool_id"].split("-")[1].isdigit()
    ]
    next_num = (max(existing_nums) + 1) if existing_nums else 1
    spool_id = f"SPOOL-{next_num:03d}"

    spool = {
        "spool_id": spool_id,
        "material": material,
        "color": color,
        "brand": brand,
        "initial_weight_g": initial_weight_g,
        "remaining_g": initial_weight_g,
        "loaded_printer": None,
        "loaded": False,
        "low_threshold_g": low_threshold_g,
        "notes": str(payload.get("notes", ""))[:200],
        "added_at": _today(),
        "last_used": None,
    }
    data.setdefault("spools", []).append(spool)
    data["last_updated"] = _today()
    data["updated_by"] = "dashboard"
    _save_inventory(data)
    return jsonify({"ok": True, "spool_id": spool_id})


# ── dashboard (home) ───────────────────────────────────────────────────────────
@app.route("/")
@app.route("/dashboard")
@_require_login
def dashboard():
    pending = get_pending_orders()
    enriched = []
    for o in pending:
        full = get_order(o["id"])
        c = _get_customer_by_id(o["customer_id"])
        enriched.append({**o, "line_items": full["items"] if full else [], "customer": c})
    return render_template("dashboard.html", active_orders=enriched, active="dashboard")


# ── queue ──────────────────────────────────────────────────────────────────────
@app.route("/queue")
@_require_login
def queue():
    pending = get_pending_orders()
    enriched = []
    for o in pending:
        full = get_order(o["id"])
        c = _get_customer_by_id(o["customer_id"])
        enriched.append({**o, "line_items": full["items"] if full else [], "customer": c})
    return render_template("queue.html", orders=enriched, active="queue")


# ── orders ─────────────────────────────────────────────────────────────────────
@app.route("/orders")
@_require_login
def orders():
    status_filter = request.args.get("status", "all")
    with get_db() as conn:
        if status_filter == "all":
            rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 200").fetchall()
        else:
            rows = conn.execute("SELECT * FROM orders WHERE status=? ORDER BY created_at DESC", (status_filter,)).fetchall()
    enriched = []
    for r in rows:
        o = dict(r)
        c = _get_customer_by_id(o["customer_id"])
        with get_db() as conn:
            items = conn.execute("SELECT * FROM order_items WHERE order_id=?", (o["id"],)).fetchall()
        o["line_items"] = [dict(i) for i in items]
        o["customer"]   = c
        enriched.append(o)
    return render_template("orders.html", orders=enriched, status_filter=status_filter, active="orders")

@app.route("/orders/new", methods=["GET", "POST"])
@_require_login
def order_new():
    if request.method == "GET":
        return render_template("order_new.html", active="orders")

    customer_name = request.form.get("customer_name", "").strip()
    identifier    = request.form.get("identifier", "").strip()
    description   = request.form.get("description", "").strip()
    material      = request.form.get("material", "").strip() or None
    notes         = request.form.get("notes", "").strip() or None
    payment_method = request.form.get("payment_method", "").strip() or None
    express       = request.form.get("express") == "on"

    try:
        quantity   = max(1, int(request.form.get("quantity", 1)))
        unit_price = round(float(request.form.get("unit_price", 0)), 2)
    except (ValueError, TypeError):
        flash("Quantity and unit price must be numbers.")
        return render_template("order_new.html", active="orders"), 400

    if not customer_name or not description or unit_price <= 0:
        flash("Customer name, item description, and a unit price above $0 are required.")
        return render_template("order_new.html", active="orders"), 400

    if not identifier:
        identifier = f"manual-{secrets.token_hex(6)}"

    total = round(unit_price * quantity, 2)
    cid = upsert_customer(identifier, customer_name)
    oid = create_order(cid, total, payment_method=payment_method, express=express, notes=notes)
    add_order_item(oid, description, quantity, unit_price, material=material)
    create_invoice(oid, cid, total, payment_method=payment_method)

    flash(f"{oid} created for {customer_name}.")
    return redirect(url_for("order_detail", order_id=oid))


@app.route("/orders/<order_id>")
@_require_login
def order_detail(order_id):
    o = get_order(order_id)
    c = _get_customer_by_id(o["customer_id"]) if o else None
    with get_db() as conn:
        inv = conn.execute(
            "SELECT * FROM invoices WHERE order_id=? ORDER BY issued_date DESC LIMIT 1",
            (order_id,)
        ).fetchone()
    return render_template("order_detail.html", order=o, customer=c,
                           invoice=dict(inv) if inv else None, active="orders")

@app.route("/orders/<order_id>/mark_paid", methods=["POST"])
@_require_login
def mark_paid(order_id):
    update_order_status(order_id, "paid")
    flash(f"{order_id} marked as paid.")
    return redirect(url_for("queue"))

@app.route("/orders/<order_id>/mark_shipped", methods=["POST"])
@_require_login
def mark_shipped(order_id):
    tracking = request.form.get("tracking", "")
    update_order_status(order_id, "shipped", tracking_number=tracking)
    flash(f"{order_id} marked as shipped.")
    return redirect(url_for("orders"))


# ── customers ──────────────────────────────────────────────────────────────────
@app.route("/customers")
@_require_login
def customers():
    ledger = get_customer_ledger()
    return render_template("customers.html", customers=ledger, active="customers")

@app.route("/customers/<int:customer_id>")
@_require_login
def customer_detail(customer_id):
    ledger = get_customer_ledger(customer_id)
    if not ledger:
        flash("Customer not found.")
        return redirect(url_for("customers"))
    return render_template("customer_detail.html", customer=ledger[0], active="customers")


# ── inventory ──────────────────────────────────────────────────────────────────
@app.route("/inventory")
@_require_login
def inventory():
    data   = _load_inventory()
    spools = data.get("spools", [])
    printers_meta = data.get("printers", {})

    # Group: loaded per-printer, then unloaded by material
    loaded_by_printer = {}
    unloaded = []
    for s in spools:
        if s.get("loaded") and s.get("loaded_printer"):
            loaded_by_printer.setdefault(s["loaded_printer"], []).append(s)
        else:
            unloaded.append(s)

    # Low stock warning
    low_spools = [s for s in spools if s.get("remaining_g", 9999) <= s.get("low_threshold_g", 150)]

    return render_template("inventory.html",
                           loaded_by_printer=loaded_by_printer,
                           unloaded=unloaded,
                           low_spools=low_spools,
                           all_spools=spools,
                           last_updated=data.get("last_updated", "—"),
                           active="inventory")


# ── finance ────────────────────────────────────────────────────────────────────
@app.route("/finance")
@_require_login
def finance():
    start = request.args.get("start") or _month_bounds()[0]
    end   = request.args.get("end")   or _month_bounds()[1]
    stmt  = compute_income_statement(start, end, save=False)
    bs    = compute_balance_sheet(_today(),
                cash=float(request.args.get("cash", 0)),
                inventory_grams=float(request.args.get("inv_g", 0)),
                save=False)
    return render_template("finance.html", stmt=stmt, bs=bs,
                           start=start, end=end, active="finance")


# ── reports ────────────────────────────────────────────────────────────────────
@app.route("/reports")
@_require_login
def reports():
    now = datetime.date.today()
    monthly = []
    for i in range(6):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        try:
            monthly.append(compute_monthly_report(y, m, save=False))
        except Exception:
            pass
    return render_template("reports.html", monthly=monthly, active="reports")

@app.route("/reports/export/csv")
@_require_login
def export_csv_route():
    period = request.args.get("period", datetime.date.today().strftime("%Y-%m"))
    files  = export_csv(period)
    if not files:
        flash("No data for that period.")
        return redirect(url_for("reports"))
    return send_file(list(files.values())[0], as_attachment=True)

@app.route("/reports/export/xlsx")
@_require_login
def export_xlsx_route():
    period = request.args.get("period", datetime.date.today().strftime("%Y-%m"))
    return send_file(export_xlsx(period), as_attachment=True)


# ── entrypoint ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Typhon's Forge Dashboard → http://localhost:{PORT}")
    print(f"Password: {DASHBOARD_PASSWORD}")
    app.run(host="0.0.0.0", port=PORT, debug=False)

"""
dashboard/app.py — Typhon's Forge owner dashboard.
Flask web app, localhost:5000, password-gated, single-operator.

Run:  python3 app.py
      or: FLASK_PORT=5001 python3 app.py
"""

import os
import sys
import hashlib
import datetime
import pathlib
import json

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
)
from shop.accounting import (
    init_accounting, compute_income_statement,
    compute_balance_sheet, compute_monthly_report,
    get_customer_ledger, dashboard_summary,
    export_csv, export_xlsx,
)

# ── config ─────────────────────────────────────────────────────────────────────
DASHBOARD_PASSWORD = os.environ.get("DJINN_DASH_PASSWORD", "typhonsforge")
SECRET_KEY         = os.environ.get("DJINN_SECRET_KEY",    "change-me-at-setup")
PORT               = int(os.environ.get("FLASK_PORT", 5000))

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = SECRET_KEY


def _pw_hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _logged_in() -> bool:
    return session.get("auth") == _pw_hash(DASHBOARD_PASSWORD)


def _require_login(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not _logged_in():
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


def _today() -> str:
    return datetime.date.today().isoformat()


def _month_bounds(year=None, month=None):
    now = datetime.date.today()
    y = year  or now.year
    m = month or now.month
    start = f"{y:04d}-{m:02d}-01"
    if m == 12:
        end = f"{y}-12-31"
    else:
        end = (datetime.date(y, m+1, 1) - datetime.timedelta(days=1)).isoformat()
    return start, end


# ── init ───────────────────────────────────────────────────────────────────────
with app.app_context():
    init_db()
    conn = _connect()
    init_accounting(conn)
    conn.close()


# ── auth ───────────────────────────────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form.get("password", "")
        if _pw_hash(pw) == _pw_hash(DASHBOARD_PASSWORD):
            session["auth"] = _pw_hash(DASHBOARD_PASSWORD)
            return redirect(url_for("queue"))
        flash("Wrong password.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ── queue (home) ───────────────────────────────────────────────────────────────
@app.route("/")
@app.route("/queue")
@_require_login
def queue():
    pending = get_pending_orders()
    enriched = []
    for o in pending:
        full = get_order(o["id"])
        c = get_customer_by_id(o["customer_id"])
        enriched.append({
            **o,
            "line_items": full["items"] if full else [],
            "customer":   c,
        })
    return render_template("queue.html", orders=enriched, active="queue")


# ── orders ─────────────────────────────────────────────────────────────────────
@app.route("/orders")
@_require_login
def orders():
    status_filter = request.args.get("status", "all")
    with get_db() as conn:
        if status_filter == "all":
            rows = conn.execute(
                "SELECT * FROM orders ORDER BY created_at DESC LIMIT 200"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM orders WHERE status=? ORDER BY created_at DESC",
                (status_filter,)
            ).fetchall()
    enriched = []
    for r in rows:
        o = dict(r)
        c = get_customer_by_id(o["customer_id"])
        with get_db() as conn:
            items = conn.execute(
                "SELECT * FROM order_items WHERE order_id=?", (o["id"],)
            ).fetchall()
        o["line_items"] = [dict(i) for i in items]
        o["customer"]   = c
        enriched.append(o)
    return render_template("orders.html", orders=enriched,
                           status_filter=status_filter, active="orders")


@app.route("/orders/<order_id>")
@_require_login
def order_detail(order_id):
    o    = get_order(order_id)
    c    = get_customer_by_id(o["customer_id"]) if o else None
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
    return render_template("customer_detail.html",
                           customer=ledger[0], active="customers")


# ── finance ────────────────────────────────────────────────────────────────────
@app.route("/finance")
@_require_login
def finance():
    start = request.args.get("start") or _month_bounds()[0]
    end   = request.args.get("end")   or _month_bounds()[1]
    stmt  = compute_income_statement(start, end, save=False)
    bs    = compute_balance_sheet(
        _today(),
        cash=float(request.args.get("cash", 0)),
        inventory_grams=float(request.args.get("inv_g", 0)),
        save=False,
    )
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
            r = compute_monthly_report(y, m, save=False)
            monthly.append(r)
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
    # Return first file; in practice, zip them
    first = list(files.values())[0]
    return send_file(first, as_attachment=True)


@app.route("/reports/export/xlsx")
@_require_login
def export_xlsx_route():
    period = request.args.get("period", datetime.date.today().strftime("%Y-%m"))
    path   = export_xlsx(period)
    return send_file(path, as_attachment=True)


# ── helpers ────────────────────────────────────────────────────────────────────
def get_customer_by_id(customer_id: int) -> dict:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM customers WHERE id=?", (customer_id,)
        ).fetchone()
    if not row:
        return {"name": "Unknown", "discord_id": "—"}
    d = dict(row)
    d["name"]             = decrypt(d["name"]) or "—"
    d["shipping_address"] = decrypt(d["shipping_address"]) or "—"
    return d


# ── context processor — queue badge ───────────────────────────────────────────
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


if __name__ == "__main__":
    print(f"Typhon's Forge Dashboard → http://localhost:{PORT}")
    print(f"Password: {DASHBOARD_PASSWORD}")
    app.run(host="0.0.0.0", port=PORT, debug=False)

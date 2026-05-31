"""
db.py — Database layer for Djinn Shop.
SQLite + column-level Fernet encryption for PII fields.

Key:   ~/.config/djinn-shop/secret.key  (chmod 600, auto-generated on first run)
DB:    ~/.local/share/djinn-shop/shop.db

Encrypted fields: customer name, email, shipping address, discord contact.
Everything else (prices, dates, order IDs, status) is plaintext and queryable.
"""

import sqlite3
import pathlib
import os
import json
import datetime
from contextlib import contextmanager
from typing import Optional

from cryptography.fernet import Fernet

# ── Paths ─────────────────────────────────────────────────────────────────────
SHOP_DIR  = pathlib.Path.home() / ".local/share/djinn-shop"
DB_PATH   = SHOP_DIR / "shop.db"
KEY_PATH  = pathlib.Path.home() / ".config/djinn-shop/secret.key"

# ── Encryption ────────────────────────────────────────────────────────────────
_fernet: Optional[Fernet] = None


def _load_or_create_key() -> bytes:
    KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    KEY_PATH.chmod(0o600)
    print(f"[shop.db] New encryption key created at {KEY_PATH}")
    print(f"[shop.db] BACK THIS UP — losing it means losing customer PII.")
    return key


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_load_or_create_key())
    return _fernet


def encrypt(value: Optional[str]) -> Optional[bytes]:
    if value is None:
        return None
    return _get_fernet().encrypt(value.encode())


def decrypt(value: Optional[bytes]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.encode()
    return _get_fernet().decrypt(value).decode()


# ── Connection ────────────────────────────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    SHOP_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema ────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_id      TEXT    UNIQUE NOT NULL,
    name            BLOB,
    email           BLOB,
    shipping_address BLOB,
    discord_contact BLOB,
    created_at      TEXT    NOT NULL,
    order_count     INTEGER DEFAULT 0,
    lifetime_value  REAL    DEFAULT 0.0,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id              TEXT    PRIMARY KEY,
    customer_id     INTEGER NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'quoted',
    payment_method  TEXT,
    payment_ref     TEXT,
    total_usd       REAL    NOT NULL DEFAULT 0.0,
    express         INTEGER DEFAULT 0,
    created_at      TEXT    NOT NULL,
    paid_at         TEXT,
    print_started_at TEXT,
    completed_at    TEXT,
    shipped_at      TEXT,
    tracking_number TEXT,
    notes           TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 1,
    unit_price      REAL    NOT NULL,
    total_price     REAL    NOT NULL,
    material        TEXT,
    color           TEXT,
    profile         TEXT,
    smoking_item    INTEGER DEFAULT 0,
    customizations  TEXT,
    stl_filename    TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS quotes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id        TEXT,
    customer_id     INTEGER,
    quote_json      TEXT    NOT NULL,
    created_at      TEXT    NOT NULL,
    FOREIGN KEY (order_id)    REFERENCES orders(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE IF NOT EXISTS ledger (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,
    order_id        TEXT    NOT NULL,
    description     TEXT,
    revenue         REAL    NOT NULL DEFAULT 0.0,
    material_cost   REAL    DEFAULT 0.0,
    machine_cost    REAL    DEFAULT 0.0,
    labor_cost      REAL    DEFAULT 0.0,
    customization_cost REAL DEFAULT 0.0,
    gross_profit    REAL    GENERATED ALWAYS AS
                    (revenue - material_cost - machine_cost - labor_cost - customization_cost)
                    STORED,
    margin_pct      REAL    DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_orders_customer   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_items_order       ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_ledger_date       ON ledger(date);
CREATE INDEX IF NOT EXISTS idx_ledger_order      ON ledger(order_id);
"""


def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA)
    print(f"[shop.db] Database ready at {DB_PATH}")


# ── Order ID generator ────────────────────────────────────────────────────────
def next_order_id() -> str:
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) FROM orders").fetchone()
        n = (row[0] or 0) + 1
    return f"ORD-{n:04d}"


# ── Customer CRUD ─────────────────────────────────────────────────────────────
def upsert_customer(discord_id: str, name: str = None, email: str = None,
                    address: str = None, discord_contact: str = None) -> int:
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM customers WHERE discord_id = ?", (discord_id,)
        ).fetchone()

        if existing:
            if name:
                conn.execute(
                    "UPDATE customers SET name=?, email=?, shipping_address=?, discord_contact=? WHERE discord_id=?",
                    (encrypt(name), encrypt(email), encrypt(address), encrypt(discord_contact), discord_id)
                )
            return existing["id"]
        else:
            cur = conn.execute(
                """INSERT INTO customers
                   (discord_id, name, email, shipping_address, discord_contact, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (discord_id, encrypt(name), encrypt(email),
                 encrypt(address), encrypt(discord_contact), now)
            )
            return cur.lastrowid


def get_customer(discord_id: str) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM customers WHERE discord_id = ?", (discord_id,)
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["name"]             = decrypt(d["name"])
    d["email"]            = decrypt(d["email"])
    d["shipping_address"] = decrypt(d["shipping_address"])
    d["discord_contact"]  = decrypt(d["discord_contact"])
    return d


# ── Order CRUD ────────────────────────────────────────────────────────────────
def create_order(customer_id: int, total_usd: float, payment_method: str = None,
                 express: bool = False, notes: str = None) -> str:
    order_id = next_order_id()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with get_db() as conn:
        conn.execute(
            """INSERT INTO orders
               (id, customer_id, status, payment_method, total_usd, express, created_at, notes)
               VALUES (?, ?, 'quoted', ?, ?, ?, ?, ?)""",
            (order_id, customer_id, payment_method, total_usd, int(express), now, notes)
        )
    return order_id


def update_order_status(order_id: str, status: str, **kwargs):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    timestamp_fields = {
        "paid":          "paid_at",
        "printing":      "print_started_at",
        "complete":      "completed_at",
        "shipped":       "shipped_at",
    }
    with get_db() as conn:
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        if status in timestamp_fields:
            field = timestamp_fields[status]
            conn.execute(f"UPDATE orders SET {field} = ? WHERE id = ?", (now, order_id))
        for col, val in kwargs.items():
            conn.execute(f"UPDATE orders SET {col} = ? WHERE id = ?", (val, order_id))


def add_order_item(order_id: str, description: str, quantity: int,
                   unit_price: float, material: str = None, color: str = None,
                   profile: str = None, smoking_item: bool = False,
                   customizations: dict = None, stl_filename: str = None):
    total = round(unit_price * quantity, 2)
    with get_db() as conn:
        conn.execute(
            """INSERT INTO order_items
               (order_id, description, quantity, unit_price, total_price,
                material, color, profile, smoking_item, customizations, stl_filename)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (order_id, description, quantity, unit_price, total,
             material, color, profile, int(smoking_item),
             json.dumps(customizations) if customizations else None,
             stl_filename)
        )


def save_quote(order_id: str, customer_id: int, quote: dict):
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with get_db() as conn:
        conn.execute(
            "INSERT INTO quotes (order_id, customer_id, quote_json, created_at) VALUES (?,?,?,?)",
            (order_id, customer_id, json.dumps(quote), now)
        )


def get_order(order_id: str) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not row:
            return None
        order = dict(row)
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()
        order["items"] = [dict(i) for i in items]
    return order


def get_pending_orders() -> list:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE status IN ('quoted','pending_payment','paid') ORDER BY created_at"
        ).fetchall()
    return [dict(r) for r in rows]


# ── Ledger ────────────────────────────────────────────────────────────────────
def write_ledger(order_id: str, description: str, revenue: float,
                 material_cost: float = 0.0, machine_cost: float = 0.0,
                 labor_cost: float = 0.0, customization_cost: float = 0.0):
    total_cost = material_cost + machine_cost + labor_cost + customization_cost
    margin = round(((revenue - total_cost) / revenue * 100) if revenue else 0, 2)
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    with get_db() as conn:
        conn.execute(
            """INSERT INTO ledger
               (date, order_id, description, revenue, material_cost,
                machine_cost, labor_cost, customization_cost, margin_pct)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (now, order_id, description, revenue,
             material_cost, machine_cost, labor_cost, customization_cost, margin)
        )


if __name__ == "__main__":
    init_db()
    print(f"Key:  {KEY_PATH}")
    print(f"DB:   {DB_PATH}")

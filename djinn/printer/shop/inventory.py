"""
inventory.py — Filament inventory tracking for Djinn Shop.

Tracks spools by material + color + brand. Deducts grams after each print.
Surfaces availability for quotes and dashboard.

Commands wired into Discord/Telegram by Salomon:
  add filament petg black 1000g $28    → log new spool
  inventory                            → show current stock
  low stock                            → show spools under LOW_STOCK_G

— Claude
"""

import sys
import json
import datetime
import pathlib

_SHOP    = pathlib.Path(__file__).parent
_PRINTER = _SHOP.parent
for p in [str(_PRINTER), str(_SHOP)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from shop.db import get_db, init_db

# ── Config ────────────────────────────────────────────────────────────────────
LOW_STOCK_G   = 150    # warn when spool drops below this
EMPTY_G       = 20     # treat as empty

# ── Schema ────────────────────────────────────────────────────────────────────
INVENTORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS filament_inventory (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    material         TEXT    NOT NULL,
    color            TEXT    NOT NULL DEFAULT 'natural',
    brand            TEXT    DEFAULT 'generic',
    spool_weight_g   REAL    NOT NULL DEFAULT 1000.0,
    grams_remaining  REAL    NOT NULL,
    cost_per_gram    REAL    NOT NULL DEFAULT 0.022,
    added_at         TEXT    NOT NULL,
    notes            TEXT,
    active           INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS filament_usage_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    spool_id    INTEGER NOT NULL,
    order_id    TEXT,
    grams_used  REAL    NOT NULL,
    logged_at   TEXT    NOT NULL,
    FOREIGN KEY (spool_id) REFERENCES filament_inventory(id)
);
"""


def init_inventory():
    with get_db() as conn:
        conn.executescript(INVENTORY_SCHEMA)


# ── Spool CRUD ────────────────────────────────────────────────────────────────
def add_spool(material: str, color: str = "natural", brand: str = "generic",
              weight_g: float = 1000.0, cost_usd: float = 22.0,
              notes: str = None) -> int:
    cost_per_gram = round(cost_usd / weight_g, 6)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO filament_inventory
               (material, color, brand, spool_weight_g, grams_remaining,
                cost_per_gram, added_at, notes)
               VALUES (?,?,?,?,?,?,?,?)""",
            (material.lower(), color.lower(), brand, weight_g,
             weight_g, cost_per_gram, now, notes)
        )
        return cur.lastrowid


def deduct_grams(material: str, color: str, grams: float,
                 order_id: str = None) -> tuple[bool, str]:
    """
    Deduct grams from the best matching active spool.
    Returns (success, message).
    Picks the spool with most grams remaining to avoid fragmentation.
    """
    with get_db() as conn:
        spool = conn.execute(
            """SELECT * FROM filament_inventory
               WHERE material=? AND color=? AND active=1
               AND grams_remaining >= ?
               ORDER BY grams_remaining DESC LIMIT 1""",
            (material.lower(), color.lower(), grams)
        ).fetchone()

        if not spool:
            # Try any spool of that material (ignore color — maybe they'll swap)
            any_spool = conn.execute(
                """SELECT * FROM filament_inventory
                   WHERE material=? AND active=1
                   AND grams_remaining >= ?
                   ORDER BY grams_remaining DESC LIMIT 1""",
                (material.lower(), grams)
            ).fetchone()
            if any_spool:
                return False, (f"No {color} {material} — "
                               f"have {any_spool['color']} with "
                               f"{any_spool['grams_remaining']:.0f}g remaining.")
            return False, f"No {material} in stock with {grams:.0f}g available."

        new_remaining = spool["grams_remaining"] - grams
        conn.execute(
            "UPDATE filament_inventory SET grams_remaining=? WHERE id=?",
            (round(new_remaining, 1), spool["id"])
        )
        now = datetime.datetime.utcnow().isoformat() + "Z"
        conn.execute(
            "INSERT INTO filament_usage_log (spool_id, order_id, grams_used, logged_at) VALUES (?,?,?,?)",
            (spool["id"], order_id, grams, now)
        )

    warning = ""
    if new_remaining < LOW_STOCK_G:
        warning = f" ⚠️ Low stock: {new_remaining:.0f}g remaining."

    return True, f"Deducted {grams:.1f}g from {color} {material}.{warning}"


def get_stock() -> list:
    """Return all active spools with current levels."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM filament_inventory
               WHERE active=1 ORDER BY material, color"""
        ).fetchall()
    return [dict(r) for r in rows]


def get_available_colors(material: str) -> list:
    """Return list of (color, grams_remaining) for a given material."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT color, SUM(grams_remaining) as total_g
               FROM filament_inventory
               WHERE material=? AND active=1 AND grams_remaining > ?
               GROUP BY color ORDER BY color""",
            (material.lower(), EMPTY_G)
        ).fetchall()
    return [(r["color"], round(r["total_g"], 1)) for r in rows]


def check_availability(material: str, color: str, grams_needed: float) -> dict:
    """
    Check if a job can be fulfilled.
    Returns {available: bool, grams_on_hand: float, message: str}
    """
    with get_db() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(grams_remaining), 0) as total
               FROM filament_inventory
               WHERE material=? AND color=? AND active=1""",
            (material.lower(), color.lower())
        ).fetchone()

    on_hand = row["total"] if row else 0

    if on_hand >= grams_needed:
        return {
            "available": True,
            "grams_on_hand": round(on_hand, 1),
            "message": f"{color.title()} {material.upper()} in stock ({on_hand:.0f}g available).",
        }
    elif on_hand > 0:
        return {
            "available": False,
            "grams_on_hand": round(on_hand, 1),
            "message": (f"Only {on_hand:.0f}g of {color} {material.upper()} on hand "
                        f"— need {grams_needed:.0f}g. Consider splitting the order."),
        }
    else:
        colors = get_available_colors(material)
        if colors:
            alts = ", ".join(f"{c} ({g:.0f}g)" for c, g in colors[:4])
            return {
                "available": False,
                "grams_on_hand": 0,
                "message": f"No {color} {material.upper()} in stock. Available: {alts}.",
            }
        return {
            "available": False,
            "grams_on_hand": 0,
            "message": f"No {material.upper()} in stock at all.",
        }


def low_stock_alert() -> list:
    """Return spools below LOW_STOCK_G threshold."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM filament_inventory
               WHERE active=1 AND grams_remaining < ? AND grams_remaining > ?
               ORDER BY grams_remaining""",
            (LOW_STOCK_G, EMPTY_G)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Inventory value for balance sheet ────────────────────────────────────────
def total_inventory_value() -> tuple[float, float]:
    """Returns (total_grams, total_value_usd) for balance sheet."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(grams_remaining), 0) as grams,
                      COALESCE(SUM(grams_remaining * cost_per_gram), 0) as value
               FROM filament_inventory WHERE active=1"""
        ).fetchone()
    return round(row["grams"], 1), round(row["value"], 2)


# ── Formatted output for Discord/Telegram ────────────────────────────────────
def format_stock_report() -> str:
    stock = get_stock()
    if not stock:
        return "No filament in inventory."

    lines = ["🧵 *Filament Inventory*\n"]
    current_mat = None
    for s in stock:
        if s["material"] != current_mat:
            current_mat = s["material"]
            lines.append(f"\n*{current_mat.upper()}*")
        pct = s["grams_remaining"] / s["spool_weight_g"] * 100
        bar = _pct_bar(pct)
        warn = " ⚠️" if s["grams_remaining"] < LOW_STOCK_G else ""
        lines.append(
            f"  {s['color'].title():<12} {bar} {s['grams_remaining']:.0f}g{warn}"
        )

    total_g, total_val = total_inventory_value()
    lines.append(f"\nTotal: {total_g:.0f}g  ≈  ${total_val:.2f}")
    return "\n".join(lines)


def _pct_bar(pct: float, width: int = 8) -> str:
    filled = round(pct / 100 * width)
    empty  = width - filled
    return "█" * filled + "░" * empty


# ── Command parser for Discord/Telegram ──────────────────────────────────────
import re

ADD_PATTERN = re.compile(
    r'add\s+filament\s+(\w+)\s+(\w+)\s+(\d+(?:\.\d+)?)g?\s+\$?(\d+(?:\.\d+)?)',
    re.I
)


def parse_add_command(text: str) -> dict:
    """
    Parse: add filament petg black 1000g $28
    Returns dict with fields, or None if no match.
    """
    m = ADD_PATTERN.search(text)
    if not m:
        return None
    return {
        "material":  m.group(1).lower(),
        "color":     m.group(2).lower(),
        "weight_g":  float(m.group(3)),
        "cost_usd":  float(m.group(4)),
    }


if __name__ == "__main__":
    init_db()
    init_inventory()

    # Seed test spools
    add_spool("pla",  "black",   weight_g=1000, cost_usd=22)
    add_spool("pla",  "white",   weight_g=1000, cost_usd=22)
    add_spool("petg", "black",   weight_g=1000, cost_usd=28)
    add_spool("petg", "natural", weight_g=500,  cost_usd=14)
    add_spool("tpu",  "black",   weight_g=500,  cost_usd=18)

    # Simulate some usage
    deduct_grams("petg", "black",   880, "ORD-0001")
    deduct_grams("pla",  "black",   200, "ORD-0002")

    print(format_stock_report())
    print()

    # Check availability
    r = check_availability("petg", "black", 150)
    print(f"PETG black 150g: {r['message']}")
    r = check_availability("petg", "black", 50)
    print(f"PETG black 50g:  {r['message']}")
    r = check_availability("abs",  "red",   100)
    print(f"ABS red 100g:    {r['message']}")

    low = low_stock_alert()
    print(f"\nLow stock alerts: {len(low)} spool(s)")
    for s in low:
        print(f"  {s['color']} {s['material']}: {s['grams_remaining']:.0f}g")

    g, v = total_inventory_value()
    print(f"\nInventory: {g:.0f}g  ≈  ${v:.2f}")

"""
inventory.py — Filament inventory tracking for Djinn Shop.

Single source of truth: ~/Obsidian/forge/inventory/filament-inventory.json
(the same file the shop dashboard's /inventory page reads and writes).

Previously this module was backed by its own SQLite table (filament_inventory
in shop.db), completely disconnected from the JSON file the dashboard actually
uses — that table was never populated, so the Discord/Telegram `inventory`
command always reported empty stock while the dashboard showed the real
36-spool picture. Consolidated onto the JSON file 2026-07-18 so there's one
inventory, not two silently diverging ones.

Commands wired into Discord/Telegram by Salomon:
  add filament petg black 1000g $28    → log new spool
  inventory                            → show current stock
  low stock                            → show spools under LOW_STOCK_G

— Claude
"""

import re
import json
import datetime
import pathlib
import threading

# ── Config ────────────────────────────────────────────────────────────────────
LOW_STOCK_G     = 150    # warn when spool drops below this
EMPTY_G         = 20     # treat as empty
REWEIGH_DAYS    = 14     # flag a loaded spool for physical reweigh after this long

INVENTORY_PATH = pathlib.Path.home() / "Obsidian/forge/inventory/filament-inventory.json"
_LOCK = threading.Lock()


def _today() -> str:
    return datetime.date.today().isoformat()


# ── Load / save (shared with dashboard app.py) ──────────────────────────────────
def load_inventory() -> dict:
    try:
        return json.loads(INVENTORY_PATH.read_text())
    except Exception:
        return {"spools": [], "printers": {}}


def save_inventory(data: dict):
    with _LOCK:
        INVENTORY_PATH.write_text(json.dumps(data, indent=2))


def init_inventory():
    """No-op kept for call-site compatibility (old SQLite version created tables)."""
    INVENTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not INVENTORY_PATH.exists():
        save_inventory({"last_updated": _today(), "updated_by": "init", "spools": [], "printers": {}})


# ── Spool CRUD ────────────────────────────────────────────────────────────────
def add_spool(material: str, color: str = "natural", brand: str = "generic",
              weight_g: float = 1000.0, cost_usd: float = 22.0,
              notes: str = None) -> str:
    data = load_inventory()
    existing_nums = [
        int(s["spool_id"].split("-")[1])
        for s in data.get("spools", [])
        if s.get("spool_id", "").startswith("SPOOL-") and s["spool_id"].split("-")[1].isdigit()
    ]
    next_num = (max(existing_nums) + 1) if existing_nums else 1
    spool_id = f"SPOOL-{next_num:03d}"

    spool = {
        "spool_id": spool_id,
        "material": material.upper(),
        "color": color.title(),
        "brand": brand,
        "initial_weight_g": weight_g,
        "remaining_g": weight_g,
        "cost_usd": cost_usd,
        "loaded_printer": None,
        "loaded": False,
        "low_threshold_g": LOW_STOCK_G,
        "notes": notes or "",
        "added_at": _today(),
        "last_used": None,
        "last_physical_check": _today(),
    }
    data.setdefault("spools", []).append(spool)
    data["last_updated"] = _today()
    data["updated_by"] = "shop.inventory.add_spool"
    save_inventory(data)
    return spool_id


def get_stock() -> list:
    return sorted(load_inventory().get("spools", []),
                  key=lambda s: (s.get("material", ""), s.get("color", "")))


# ── Matching + deduction (used by the print-complete watcher) ───────────────────
def find_loaded_spool(printer: str, material: str, color: str = None) -> dict | None:
    """
    Find the best-matching loaded spool for a printer.
    Matches by material always; by color when given (case-insensitive, both).
    Among matches, prefers the one with the most remaining_g (least fragmentation).
    """
    data = load_inventory()
    candidates = [
        s for s in data.get("spools", [])
        if s.get("loaded") and (s.get("loaded_printer") or "").lower() == printer.lower()
        and (s.get("material") or "").lower() == material.lower()
    ]
    if color:
        color_matches = [s for s in candidates if (s.get("color") or "").lower() == color.lower()]
        if color_matches:
            candidates = color_matches
    if not candidates:
        return None
    candidates.sort(key=lambda s: s.get("remaining_g", 0), reverse=True)
    return candidates[0]


def deduct_filament(printer: str, material: str, grams: float,
                     color: str = None, job_id=None, note: str = None) -> dict:
    """
    Deduct `grams` from the best-matching loaded spool for `printer`.
    Does NOT touch last_physical_check — that's only set by a human-confirmed
    reweigh (dashboard manual edit or add_spool). Automated deductions only
    move last_used, so the reweigh-due flag reflects "genuinely eyeballed
    recently," not "a job happened to run."

    Returns {"ok": bool, "spool_id": str|None, "remaining_g": float|None, "message": str}
    """
    if not grams or grams <= 0:
        return {"ok": False, "spool_id": None, "remaining_g": None,
                "message": "no filament_g on job — nothing to deduct"}

    data = load_inventory()
    target = None
    for s in data.get("spools", []):
        if (s.get("loaded") and (s.get("loaded_printer") or "").lower() == printer.lower()
                and (s.get("material") or "").lower() == material.lower()):
            if color and (s.get("color") or "").lower() != color.lower():
                continue
            if target is None or s.get("remaining_g", 0) > target.get("remaining_g", 0):
                target = s

    if target is None:
        return {"ok": False, "spool_id": None, "remaining_g": None,
                "message": f"no loaded {color or ''} {material} spool found on {printer}"}

    target["remaining_g"] = round(max(0, target.get("remaining_g", 0) - grams), 1)
    target["last_used"] = _today()
    tag = f"job {job_id}" if job_id else "print"
    stamp = f"[{_today()}] auto-deducted {grams:.1f}g ({tag}{': ' + note if note else ''})"
    target["notes"] = (stamp if not target.get("notes") else f"{target['notes']} | {stamp}")[:400]

    data["last_updated"] = _today()
    data["updated_by"] = "djinn-print-complete-watcher"
    save_inventory(data)

    warning = ""
    if target["remaining_g"] <= target.get("low_threshold_g", LOW_STOCK_G):
        warning = f" LOW STOCK: {target['remaining_g']:.0f}g remaining."

    return {"ok": True, "spool_id": target["spool_id"], "remaining_g": target["remaining_g"],
            "message": f"Deducted {grams:.1f}g from {target['spool_id']} "
                       f"({target['color']} {target['material']}) — "
                       f"{target['remaining_g']:.0f}g left.{warning}"}


def mark_physical_check(spool_id: str) -> bool:
    """Stamp a spool as physically reweighed today. Call this on any human-confirmed
    remaining_g update (dashboard manual edit), not on automated deductions."""
    data = load_inventory()
    for s in data.get("spools", []):
        if s["spool_id"] == spool_id:
            s["last_physical_check"] = _today()
            save_inventory(data)
            return True
    return False


def reweigh_due(spools: list = None) -> list:
    """Loaded spools that haven't been physically reweighed in REWEIGH_DAYS days
    (or never have a check on record). Unloaded shelf spools aren't flagged —
    only ones actively being drawn down matter for accuracy."""
    spools = spools if spools is not None else load_inventory().get("spools", [])
    today = datetime.date.today()
    due = []
    for s in spools:
        if not s.get("loaded"):
            continue
        last = s.get("last_physical_check")
        if not last:
            due.append(s)
            continue
        try:
            days = (today - datetime.date.fromisoformat(last)).days
            if days >= REWEIGH_DAYS:
                due.append(s)
        except ValueError:
            due.append(s)
    return due


# ── Discord/Telegram compatible views ────────────────────────────────────────
def low_stock_alert() -> list:
    """Returns dicts shaped like the old SQLite rows (material/color/grams_remaining)
    so the already-deployed Discord/Telegram handlers don't need edits."""
    stock = load_inventory().get("spools", [])
    return [
        {"material": s.get("material", ""), "color": s.get("color", ""),
         "grams_remaining": s.get("remaining_g", 0), "spool_id": s.get("spool_id")}
        for s in stock
        if EMPTY_G < s.get("remaining_g", 0) < s.get("low_threshold_g", LOW_STOCK_G)
    ]


def total_inventory_value() -> tuple:
    stock = load_inventory().get("spools", [])
    grams = sum(s.get("remaining_g", 0) for s in stock)
    value = sum(s.get("remaining_g", 0) * (s.get("cost_usd", 22.0) / max(s.get("initial_weight_g", 1000), 1))
                for s in stock)
    return round(grams, 1), round(value, 2)


def format_stock_report() -> str:
    stock = get_stock()
    if not stock:
        return "No filament in inventory."

    lines = ["Filament Inventory\n"]
    current_mat = None
    for s in stock:
        mat = s.get("material", "")
        if mat != current_mat:
            current_mat = mat
            lines.append(f"\n{current_mat}")
        remaining = s.get("remaining_g", 0)
        initial = s.get("initial_weight_g", 1000) or 1000
        pct = remaining / initial * 100
        bar = _pct_bar(pct)
        warn = " LOW" if remaining < s.get("low_threshold_g", LOW_STOCK_G) else ""
        loaded = f" [{s['loaded_printer']}]" if s.get("loaded") and s.get("loaded_printer") else ""
        lines.append(f"  {s.get('color',''):<12} {bar} {remaining:.0f}g{loaded}{warn}")

    total_g, total_val = total_inventory_value()
    due = reweigh_due(stock)
    lines.append(f"\nTotal: {total_g:.0f}g  ~  ${total_val:.2f}")
    if due:
        lines.append(f"Needs reweigh: {', '.join(s['spool_id'] for s in due)}")
    return "\n".join(lines)


def _pct_bar(pct: float, width: int = 8) -> str:
    filled = round(pct / 100 * width)
    empty = width - filled
    return "#" * filled + "-" * empty


# ── Command parser for Discord/Telegram ──────────────────────────────────────
ADD_PATTERN = re.compile(
    r'add\s+filament\s+(\w+)\s+(\w+)\s+(\d+(?:\.\d+)?)g?\s+\$?(\d+(?:\.\d+)?)',
    re.I
)


def parse_add_command(text: str) -> dict:
    """Parse: add filament petg black 1000g $28"""
    m = ADD_PATTERN.search(text)
    if not m:
        return None
    return {
        "material": m.group(1).lower(),
        "color": m.group(2).lower(),
        "weight_g": float(m.group(3)),
        "cost_usd": float(m.group(4)),
    }

"""
batch_agent.py — Print queue batching by material + color.

Scans the print queue for paid orders, groups jobs that share
material + color, checks if they fit on the Ender-3 V3 Plus bed,
and proposes batch plates to the owner via Telegram.

Owner replies "batch ORD-001 ORD-003" → PlateNestAgent runs.
Owner replies "no batch" → jobs print separately.

— Claude
"""

import sys
import json
import pathlib
import itertools
import requests
import os

_SHOP    = pathlib.Path(__file__).parent
_PRINTER = _SHOP.parent
for p in [str(_PRINTER), str(_SHOP)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from shop.db import get_db, get_order

# ── Printer bed config ────────────────────────────────────────────────────────
BED_X_MM = 220   # Ender-3 V3 Plus usable X
BED_Y_MM = 220   # Ender-3 V3 Plus usable Y
PART_GAP_MM = 5  # minimum gap between parts

# Rough volume→footprint heuristic (cm³ → mm²)
# Used when we don't have exact bounding box from consult
def _estimate_footprint_mm2(volume_cm3: float) -> float:
    # Assume average aspect ratio ~1.5:1, height = 0.4 * max_dim
    import math
    side = math.pow(volume_cm3 * 1000, 1/3) * 1.5
    return side * side

# ── Queue reader ──────────────────────────────────────────────────────────────
def get_paid_queue() -> list:
    """Return all paid orders not yet printing, with item details."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT o.*, oi.material, oi.color, oi.description, oi.quantity,
                      oi.customizations
               FROM orders o
               JOIN order_items oi ON oi.order_id = o.id
               WHERE o.status = 'paid'
               ORDER BY o.created_at"""
        ).fetchall()
    return [dict(r) for r in rows]


def get_batchable_groups(queue: list) -> list:
    """
    Group queue items by material + color.
    Returns list of groups, each group is a list of order dicts.
    Only returns groups with 2+ orders (worth batching).
    """
    groups: dict = {}
    for item in queue:
        mat   = (item.get("material") or "pla").lower()
        color = (item.get("color") or "default").lower()
        key   = f"{mat}_{color}"
        groups.setdefault(key, []).append(item)

    return [g for g in groups.values() if len(g) >= 2]


def _fits_on_plate(items: list) -> tuple[bool, float, float]:
    """
    Rough fit check: sum estimated footprints + gaps vs bed area.
    Returns (fits, total_x_estimate_mm, total_y_estimate_mm).
    This is a conservative estimate — PlateNestAgent does the exact check.
    """
    bed_area = BED_X_MM * BED_Y_MM
    total_parts = sum(item.get("quantity", 1) for item in items)

    # Try to pull bounding box from customizations JSON if consult stored it
    total_footprint = 0
    for item in items:
        custom = item.get("customizations")
        if isinstance(custom, str):
            try:
                custom = json.loads(custom)
            except Exception:
                custom = {}
        bbox = (custom or {}).get("bounding_box_mm")
        if bbox:
            fx = (bbox.get("x", 60) + PART_GAP_MM)
            fy = (bbox.get("y", 60) + PART_GAP_MM)
            total_footprint += fx * fy * item.get("quantity", 1)
        else:
            vol = (custom or {}).get("volume_cm3", 30)
            total_footprint += _estimate_footprint_mm2(vol) * item.get("quantity", 1)

    fits = total_footprint <= bed_area * 0.85  # 85% fill max
    side = total_footprint ** 0.5
    return fits, round(side, 1), round(side * 0.7, 1)


# ── Time savings estimate ─────────────────────────────────────────────────────
def _estimate_time_saving_min(items: list) -> int:
    """Estimate minutes saved by batching vs printing separately."""
    # Each separate job: ~15 min overhead (heat up, first layer, cool down, swap)
    n_jobs   = len(set(i["id"] for i in items))
    saved    = (n_jobs - 1) * 15
    return saved


# ── Telegram notify ───────────────────────────────────────────────────────────
TG_TOKEN      = os.environ.get("DJINN_TG_TOKEN",
                                "7962428973:AAHzCibu8E0RDDaRF3eHGA7WcOEqMbypOVI")
TG_API        = f"https://api.telegram.org/bot{TG_TOKEN}"
OWNER_TG_CHAT = int(os.environ.get("DJINN_TG_ALLOWED", "7620067588").split(",")[0])


def _notify_owner(text: str):
    requests.post(f"{TG_API}/sendMessage",
                  json={"chat_id": OWNER_TG_CHAT, "text": text,
                        "parse_mode": "Markdown"},
                  timeout=10)


def propose_batches(dry_run: bool = False) -> list:
    """
    Main entry point. Scans queue, finds batchable groups,
    notifies owner with proposals. Returns list of proposals.
    """
    queue    = get_paid_queue()
    groups   = get_batchable_groups(queue)
    proposals = []

    for group in groups:
        fits, est_x, est_y = _fits_on_plate(group)
        if not fits:
            # Split into pairs and check each pair
            for pair in itertools.combinations(group, 2):
                fits2, x2, y2 = _fits_on_plate(list(pair))
                if fits2:
                    proposals.append(list(pair))
        else:
            proposals.append(group)

    if not proposals:
        return []

    for proposal in proposals:
        order_ids    = list(dict.fromkeys(i["id"] for i in proposal))
        mat          = proposal[0].get("material", "PLA").upper()
        color        = proposal[0].get("color", "default").title()
        total_parts  = sum(i.get("quantity", 1) for i in proposal)
        time_saved   = _estimate_time_saving_min(proposal)
        fits, ex, ey = _fits_on_plate(proposal)

        lines = [
            f"📦 *Batch suggestion*",
            f"",
        ]
        for oid in order_ids:
            items_in_order = [i for i in proposal if i["id"] == oid]
            desc = ", ".join(
                f'×{i["quantity"]} {i["description"]}'
                for i in items_in_order
            )
            lines.append(f"  `{oid}` — {desc}")

        lines += [
            f"",
            f"Material: {mat} / {color}",
            f"Parts:    {total_parts} total — {'fits on one plate ✅' if fits else 'tight — verify ⚠️'}",
            f"Saves:    ~{time_saved} min vs printing separately",
            f"",
            f"Confirm batch:",
            f"`batch {' '.join(order_ids)}`",
            f"or: `no batch` to print separately",
        ]

        msg = "\n".join(lines)
        if not dry_run:
            _notify_owner(msg)
        proposals[proposals.index(proposal)] = {
            "order_ids":   order_ids,
            "material":    mat,
            "color":       color,
            "total_parts": total_parts,
            "fits":        fits,
            "time_saved_min": time_saved,
            "message":     msg,
        }

    return proposals


# ── Called when owner confirms batch ─────────────────────────────────────────
def confirm_batch(order_ids: list) -> str:
    """
    Owner confirmed batch. Triggers PlateNestAgent.
    Returns status string for Telegram reply.
    """
    try:
        import subprocess
        ids_str = " ".join(order_ids)
        result  = subprocess.run(
            ["djinn-design", "--batch"] + order_ids,
            capture_output=True, text=True, timeout=300
        )
        if result.returncode == 0:
            return f"✅ Batch plate started for {ids_str}.\n{result.stdout[:200]}"
        else:
            return f"⚠️ Batch failed for {ids_str}:\n{result.stderr[:200]}"
    except FileNotFoundError:
        # djinn-design not found — fall back to logging
        return (f"Batch confirmed: {', '.join(order_ids)}.\n"
                f"Run manually: djinn-design --batch {' '.join(order_ids)}")


if __name__ == "__main__":
    print("Scanning queue for batchable jobs (dry run)...")
    props = propose_batches(dry_run=True)
    if not props:
        print("No batchable groups in current queue.")
    for p in props:
        print(f"\nProposal: {p['order_ids']}")
        print(f"  {p['material']} / {p['color']}")
        print(f"  {p['total_parts']} parts  |  saves ~{p['time_saved_min']} min")
        print(f"  Fits: {p['fits']}")

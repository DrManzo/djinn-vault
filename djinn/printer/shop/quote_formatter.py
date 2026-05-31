"""
quote_formatter.py — Splits quote output into customer-facing and owner-facing views.

Customer sees: item, qty, standard price, express price, reply instructions.
Owner sees:    everything — cost floor, margin, smoking flag, profile, market data.
"""

import datetime
from typing import Optional

EXPRESS_MULTIPLIER = 1.35   # urgent_rush job_type premium


def customer_quote(quote: dict, customizations: list = None,
                   stl_filename: str = None) -> str:
    """
    Clean retail-style quote for posting in #3d-printing.
    No internal pricing data. No profiles. No cost floor.
    """
    name     = quote.get("piece_name", "Custom Print")
    qty      = quote.get("quantity", 1)
    standard = quote.get("recommended_price_usd", 0.0)
    express  = round(standard * EXPRESS_MULTIPLIER, 2)
    material = _material_label(quote)
    smoking  = quote.get("smoking_accessory", False)

    lines = []

    if stl_filename:
        lines.append(f"📎 `{stl_filename}`")

    lines.append(f"\U0001f5a8️  **{name}**  ×{qty}")

    if material:
        line = f"     {material}"
        if smoking:
            line += "  *(specialist material required)*"
        lines.append(line)

    if customizations:
        lines.append("")
        lines.append("**Includes:**")
        for c in customizations:
            lines.append(f"  • {c['label']}")

    lines += [
        "",
        f"💰 **Standard:**      ${standard:.2f}",
        f"⚡ **Express Print:** ${express:.2f}   *(priority turnaround)*",
        "",
        "Reply **ORDER** or **EXPRESS** to confirm.",
    ]

    return "\n".join(lines)


def owner_quote(quote: dict, customizations: list = None,
                customer_discord: str = None, order_id: str = None) -> str:
    """
    Full internal view for owner Telegram notification.
    Shows everything: floor, margin, smoking flag, profile, comps.
    """
    name      = quote.get("piece_name", "Custom Print")
    qty       = quote.get("quantity", 1)
    standard  = quote.get("recommended_price_usd", 0.0)
    express   = round(standard * EXPRESS_MULTIPLIER, 2)
    floor     = quote.get("cost_floor_usd", 0.0)
    ceiling   = quote.get("premium_ceiling_usd", 0.0)
    smoking   = quote.get("smoking_accessory", False)
    upcharge  = quote.get("smoking_upcharge_pct", 0.0)
    job_type  = quote.get("job_type", "").replace("_", " ").title()
    bd        = quote.get("unit_breakdown", {})
    mkt_med   = quote.get("market_median_usd")
    mkt_count = quote.get("market_comp_count", 0)
    weights   = quote.get("weights_used", {})

    margin_pct = round(((standard - floor) / standard * 100) if standard else 0, 1)

    header = f"📋 Quote sent"
    if order_id:
        header += f" — {order_id}"
    if customer_discord:
        header += f" → @{customer_discord}"

    lines = [
        header,
        "",
        f"  {name}  ×{qty}",
        f"  Job type:  {job_type}",
    ]

    if smoking:
        lines.append(f"  🔥 Smoking accessory — +{int(upcharge*100)}% upcharge applied")

    lines += [
        "",
        "── Cost breakdown (per unit) ──────────",
        f"  Material:      ${bd.get('material_usd', 0):.4f}",
        f"  Labor:         ${bd.get('labor_usd', 0):.4f}",
        f"  Depreciation:  ${bd.get('depreciation_usd', 0):.4f}",
        f"  Maintenance:   ${bd.get('maintenance_usd', 0):.4f}",
        f"  Electricity:   ${bd.get('electricity_usd', 0):.4f}",
        f"  Extras:        ${bd.get('extras_usd', 0):.4f}",
        f"  Base cost:     ${bd.get('base_cost_usd', 0):.2f}",
    ]

    if customizations:
        lines.append("")
        lines.append("── Customizations ─────────────────────")
        for c in customizations:
            lines.append(f"  {c['label']:<22} +${c['amount']:.2f}  ({c['mode']})")

    lines += [
        "",
        "── Pricing ─────────────────────────────",
        f"  Cost floor:    ${floor:.2f}   ← never quote below",
        f"  Fair market:   ${standard:.2f}   ← quoted to customer",
        f"  Express:       ${express:.2f}   ← if they pick it",
        f"  Ceiling:       ${ceiling:.2f}",
        f"  Margin:        {margin_pct}%",
    ]

    if mkt_count:
        lines.append(f"  Market comps:  {mkt_count} listings  (median ${mkt_med:.2f})")
    else:
        lines.append("  Market comps:  none — cost-plus only")

    lines += [
        "",
        f"  Weights used:  cost {int(weights.get('cost',0)*100)}%  "
        f"market {int(weights.get('market',0)*100)}%  "
        f"value {int(weights.get('value',0)*100)}%",
    ]

    return "\n".join(lines)


def express_quote(quote: dict) -> dict:
    """Return a modified quote dict repriced as urgent_rush / Express Print."""
    import copy
    eq = copy.deepcopy(quote)
    standard = eq.get("recommended_price_usd", 0.0)
    express  = round(standard * EXPRESS_MULTIPLIER, 2)
    eq["recommended_price_usd"] = express
    eq["fair_market_usd"]       = express
    eq["premium_ceiling_usd"]   = round(express * 1.15, 2)
    eq["job_type"]              = "urgent_rush"
    eq["express"]               = True
    return eq


# ── helpers ───────────────────────────────────────────────────────────────────
def _material_label(quote: dict) -> Optional[str]:
    items = quote.get("items", [])
    if items:
        return items[0].get("material", "").upper() or None
    job = quote.get("job_type", "")
    if "smoking" in job or quote.get("smoking_accessory"):
        return "PETG"
    return "PLA"


if __name__ == "__main__":
    sample = {
        "piece_name": "Puffco Proxy Recycler",
        "quantity": 2,
        "job_type": "functional_custom_part",
        "smoking_accessory": True,
        "smoking_upcharge_pct": 0.35,
        "recommended_price_usd": 51.34,
        "fair_market_usd": 51.34,
        "cost_floor_usd": 40.80,
        "premium_ceiling_usd": 59.04,
        "market_median_usd": 38.50,
        "market_comp_count": 4,
        "unit_breakdown": {
            "material_usd": 1.78, "labor_usd": 6.67,
            "depreciation_usd": 0.08, "maintenance_usd": 0.10,
            "electricity_usd": 0.02, "extras_usd": 0.50,
            "base_cost_usd": 9.15,
        },
        "weights_used": {"cost": 0.55, "market": 0.30, "value": 0.15},
    }
    customs = [{"label": "Logo engraving", "amount": 10.00, "mode": "0.5hr @ $20/hr"}]

    print("─── CUSTOMER VIEW ───")
    print(customer_quote(sample, customs, stl_filename="proxy_recycler_v2.stl"))
    print()
    print("─── OWNER VIEW ───")
    print(owner_quote(sample, customs, customer_discord="johnd#1234", order_id="ORD-008"))

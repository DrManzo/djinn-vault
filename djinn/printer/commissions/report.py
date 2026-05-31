#!/usr/bin/env python3
"""
report.py — Quote formatter for the Djinn print pricing pipeline.
Takes the output dict from price.py and renders it as:
  - Telegram/Discord message (compact)
  - Markdown (for vault logging)
  - JSON (for machine consumers)
Also handles appending to quote-history.jsonl.

— Marcus
"""

import json
import datetime
from pathlib import Path
from typing import Optional

VAULT_ROOT    = Path.home() / "Obsidian"
QUOTE_HISTORY = VAULT_ROOT / "djinn/printer/commissions/quote-history.jsonl"


def format_telegram(quote: dict, warnings: list = None) -> str:
    name    = quote["piece_name"]
    qty     = quote["quantity"]
    qty_label = f" x{qty}" if qty > 1 else ""
    floor   = quote["cost_floor_usd"]
    market  = quote["fair_market_usd"]
    ceiling = quote["premium_ceiling_usd"]
    rec     = quote["recommended_price_usd"]
    jt      = quote["job_type"].replace("_", " ").title()
    bd      = quote["unit_breakdown"]

    lines = [
        f"🖨️ Quote: {name}{qty_label}",
        f"📋 Type: {jt}",
        "",
        f"💰 Recommended: ${rec:.2f}",
        f"   Floor: ${floor:.2f}  |  Ceiling: ${ceiling:.2f}",
    ]
    if quote.get("market_median_usd"):
        lines.append(f"   Market median: ${quote['market_median_usd']:.2f}")
    lines += [
        "",
        "📊 Cost breakdown (per unit):",
        f"   Material:     ${bd['material_usd']:.4f}",
        f"   Labor:        ${bd['labor_usd']:.4f}",
        f"   Depreciation: ${bd['depreciation_usd']:.4f}",
        f"   Electricity:  ${bd['electricity_usd']:.4f}",
        f"   Extras:       ${bd['extras_usd']:.4f}",
        f"   Base total:   ${bd['base_cost_usd']:.2f}",
    ]
    if warnings:
        lines += ["", "Warnings:"]
        for w in warnings:
            lines.append(f"   • {w}")
    return "\n".join(lines)


def format_markdown(quote: dict, warnings: list = None) -> str:
    ts   = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    name = quote["piece_name"]
    qty  = quote["quantity"]
    bd   = quote["unit_breakdown"]
    floor = quote["cost_floor_usd"]
    rec   = quote["recommended_price_usd"]
    ceil_ = quote["premium_ceiling_usd"]
    jt    = quote["job_type"].replace("_", " ").title()

    md = f"""# Quote — {name}
**Generated:** {ts}
**Job type:** {jt}
**Quantity:** {qty}

## Recommended Price
| Floor | Recommended | Ceiling |
|------:|------------:|--------:|
| ${floor:.2f} | **${rec:.2f}** | ${ceil_:.2f} |

## Cost Breakdown (per unit)
| Component | Cost |
|-----------|-----:|
| Material | ${bd['material_usd']:.4f} |
| Labor | ${bd['labor_usd']:.4f} |
| Depreciation | ${bd['depreciation_usd']:.4f} |
| Maintenance | ${bd['maintenance_usd']:.4f} |
| Electricity | ${bd['electricity_usd']:.4f} |
| Extras | ${bd['extras_usd']:.4f} |
| **Base total** | **${bd['base_cost_usd']:.2f}** |
"""
    if quote.get("market_median_usd"):
        md += f"\n**Market median:** ${quote['market_median_usd']:.2f}\n"
    if warnings:
        md += "\n## Warnings\n"
        for w in warnings:
            md += f"- {w}\n"
    md += "\n---\n*Quoted by Marcus (Perplexity) via Djinn FairPrintAgent*\n"
    return md


def append_to_history(quote: dict, brief: dict, source: str = "cli") -> None:
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "source":    source,
        "brief":     brief,
        "quote":     quote,
    }
    QUOTE_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    with open(QUOTE_HISTORY, "a") as f:
        f.write(json.dumps(record) + "\n")


def render(quote: dict, brief: dict, output: str = "telegram",
           source: str = "cli", save: bool = True,
           warnings: list = None) -> str:
    if save:
        append_to_history(quote, brief, source=source)
    if output == "telegram":
        return format_telegram(quote, warnings=warnings)
    elif output == "markdown":
        return format_markdown(quote, warnings=warnings)
    elif output == "json":
        return json.dumps(quote, indent=2)
    return format_telegram(quote, warnings=warnings)


if __name__ == "__main__":
    import sys
    sample = {
        "piece_name": "Test Part", "job_type": "functional_custom_part", "quantity": 1,
        "unit_breakdown": {
            "material_usd": 0.484, "labor_usd": 6.667, "depreciation_usd": 0.0798,
            "maintenance_usd": 0.10, "electricity_usd": 0.0234, "extras_usd": 0.50,
            "base_cost_usd": 7.854,
        },
        "cost_floor_usd": 11.07, "fair_market_usd": 13.42, "premium_ceiling_usd": 15.43,
        "recommended_price_usd": 13.42, "market_median_usd": None,
        "weights_used": {"cost": 0.55, "market": 0.30, "value": 0.15},
    }
    fmt = sys.argv[1] if len(sys.argv) > 1 else "telegram"
    print(render(sample, brief={}, output=fmt, save=False))

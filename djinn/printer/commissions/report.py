#!/usr/bin/env python3
"""
report.py — Quote formatter for the Djinn print pricing pipeline.
Takes the output dict from price.py and renders it as:
  - terminal  (ASCII table — matches what the CLI currently prints)
  - telegram  (compact emoji message)
  - markdown  (vault logging)
  - json      (machine consumers)
Also handles appending to quote-history.jsonl.

Changelog:
  v1.1 — Added format_terminal() with box-drawing ASCII table.

— Marcus
"""

import json
import datetime
from pathlib import Path
from typing import Optional

VAULT_ROOT    = Path.home() / "Obsidian"
QUOTE_HISTORY = VAULT_ROOT / "djinn/printer/commissions/quote-history.jsonl"

# Box-drawing characters
_TL, _TR, _BL, _BR = "┌", "┐", "└", "┘"
_H, _V             = "─", "│"
_ML, _MR, _MT, _MB = "├", "┤", "┬", "┴"
_CROSS             = "┼"


def _hline(widths: list, left: str, mid: str, right: str, fill: str = _H) -> str:
    return left + mid.join(fill * (w + 2) for w in widths) + right


def _row(cells: list, widths: list) -> str:
    parts = []
    for cell, w in zip(cells, widths):
        parts.append(f" {str(cell):<{w}} ")
    return _V + _V.join(parts) + _V


def format_terminal(quote: dict, warnings: list = None) -> str:
    """
    Render a clean ASCII box-table that matches what the CLI prints:

    ┌─────────────────────────────────────────────┐
    │ 🖨  Quote: Puffco Peak Cap                  │
    ├──────────────────────┬──────────────────────┤
    │ Job type             │ Functional Custom    │
    │ Quantity             │ 1                    │
    │ Smoking accessory    │ YES (+35%)           │
    ├──────────────────────┼──────────────────────┤
    │ Material             │ $0.2904              │
    │ Labor                │ $8.3333              │
    │ Depreciation         │ $0.0798              │
    │ Maintenance          │ $0.1000              │
    │ Electricity          │ $0.0234              │
    │ Extras               │ $0.5000              │
    │ Base cost (unit)     │ $9.3269              │
    ├──────────────────────┼──────────────────────┤
    │ Cost floor (total)   │ $15.86               │
    │ Market median        │ $22.00               │
    │ Fair market          │ $26.93               │
    │ Premium ceiling      │ $30.97               │
    ╞══════════════════════╪══════════════════════╡  ← recommended
    │ RECOMMENDED          │ $26.93               │
    └──────────────────────┴──────────────────────┘
    """
    bd  = quote["unit_breakdown"]
    qty = quote["quantity"]
    jt  = quote["job_type"].replace("_", " ").title()
    name = quote["piece_name"]
    smoking = quote.get("smoking_accessory", False)
    floor   = quote["cost_floor_usd"]
    market  = quote.get("market_median_usd")
    fair    = quote["fair_market_usd"]
    ceil_   = quote["premium_ceiling_usd"]
    rec     = quote["recommended_price_usd"]

    COL_W = [22, 22]

    lines = []
    title = f"\U0001f5a8  Quote: {name}"
    title_w = sum(COL_W) + 3  # 2 cols + 3 separators
    lines.append(_TL + _H * (title_w) + _TR)
    lines.append(_V + f" {title:<{title_w-2}} " + _V)
    lines.append(_hline(COL_W, _ML, _MT, _MR))

    def kv(label, value):
        lines.append(_row([label, value], COL_W))

    kv("Job type",   jt)
    kv("Quantity",   str(qty))
    kv("Smoking",    "YES (+35%)" if smoking else "no")
    lines.append(_hline(COL_W, _ML, _CROSS, _MR))

    kv("Material",         f"${bd['material_usd']:.4f}")
    kv("Labor",            f"${bd['labor_usd']:.4f}")
    kv("Depreciation",     f"${bd['depreciation_usd']:.4f}")
    kv("Maintenance",      f"${bd['maintenance_usd']:.4f}")
    kv("Electricity",      f"${bd['electricity_usd']:.4f}")
    kv("Extras",           f"${bd['extras_usd']:.4f}")
    kv("Base cost (unit)", f"${bd['base_cost_usd']:.4f}")
    lines.append(_hline(COL_W, _ML, _CROSS, _MR))

    kv("Cost floor (total)", f"${floor:.2f}")
    if market:
        kv("Market median", f"${market:.2f}")
    kv("Fair market",       f"${fair:.2f}")
    kv("Premium ceiling",   f"${ceil_:.2f}")

    # double-line separator for recommended row
    double_mid  = "═" * (COL_W[0] + 2) + "╪" + "═" * (COL_W[1] + 2)
    lines.append("╞" + double_mid + "╡")
    lines.append(_row(["RECOMMENDED", f"${rec:.2f}"], COL_W))
    lines.append(_hline(COL_W, _BL, _MB, _BR))

    if warnings:
        lines.append("")
        for w in warnings:
            lines.append(f"  ⚠  {w}")

    return "\n".join(lines)


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
    smoking = quote.get("smoking_accessory", False)

    lines = [
        f"\U0001f5a8 Quote: {name}{qty_label}",
        f"\U0001f4cb Type: {jt}" + ("  🔥 +35% upcharge" if smoking else ""),
        "",
        f"\U0001f4b0 Recommended: ${rec:.2f}",
        f"   Floor: ${floor:.2f}  |  Ceiling: ${ceiling:.2f}",
    ]
    if quote.get("market_median_usd"):
        lines.append(f"   Market median: ${quote['market_median_usd']:.2f}")
    lines += [
        "",
        "\U0001f4ca Cost breakdown (per unit):",
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
    smoking = quote.get("smoking_accessory", False)

    md = f"""# Quote — {name}
**Generated:** {ts}
**Job type:** {jt}{"  🔥 *Smoking accessory — 35% upcharge applied*" if smoking else ""}
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


def render(quote: dict, brief: dict, output: str = "terminal",
           source: str = "cli", save: bool = True,
           warnings: list = None) -> str:
    if save:
        append_to_history(quote, brief, source=source)
    if output == "terminal":
        return format_terminal(quote, warnings=warnings)
    elif output == "telegram":
        return format_telegram(quote, warnings=warnings)
    elif output == "markdown":
        return format_markdown(quote, warnings=warnings)
    elif output == "json":
        return json.dumps(quote, indent=2)
    return format_terminal(quote, warnings=warnings)  # default changed to terminal


if __name__ == "__main__":
    import sys
    sample = {
        "piece_name": "Puffco Peak Cap", "job_type": "functional_custom_part", "quantity": 1,
        "smoking_accessory": True, "smoking_upcharge_pct": 0.35,
        "unit_breakdown": {
            "material_usd": 0.2904, "labor_usd": 8.3333, "depreciation_usd": 0.0798,
            "maintenance_usd": 0.1000, "electricity_usd": 0.0234, "extras_usd": 0.5000,
            "base_cost_usd": 9.3269,
        },
        "cost_floor_usd":        15.86,
        "fair_market_usd":       26.93,
        "premium_ceiling_usd":   30.97,
        "recommended_price_usd": 26.93,
        "market_median_usd":     22.00,
        "weights_used": {"cost": 0.55, "market": 0.30, "value": 0.15},
    }
    fmt = sys.argv[1] if len(sys.argv) > 1 else "terminal"
    print(render(sample, brief={}, output=fmt, save=False))

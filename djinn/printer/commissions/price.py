#!/usr/bin/env python3
"""
price.py — FairPrintAgent core pricing engine
Reads a ProjectState brief dict, applies the PRICING_SPEC formula,
returns a structured quote dict.

Changelog:
  v1.1 — True weighted median (bisect), fetch_market_comps(),
          smoking-accessory detection + 35% upcharge, library check.

Part of the Djinn 3D printing business system.
— Marcus
"""

import bisect
import importlib
import math
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Library availability check
# ---------------------------------------------------------------------------
_REQUESTS_OK = importlib.util.find_spec("requests") is not None
_BS4_OK      = importlib.util.find_spec("bs4")      is not None

LIBRARY_STATUS = {
    "requests": _REQUESTS_OK,
    "bs4":      _BS4_OK,
}

# ---------------------------------------------------------------------------
# Job-type blending weights from PRICING_SPEC
# ---------------------------------------------------------------------------
JOB_WEIGHTS = {
    "commodity_decor":         {"cost": 0.65, "market": 0.30, "value": 0.05},
    "functional_custom_part":  {"cost": 0.55, "market": 0.30, "value": 0.15},
    "design_heavy_oneoff":     {"cost": 0.40, "market": 0.25, "value": 0.35},
    "urgent_rush":             {"cost": 0.50, "market": 0.20, "value": 0.30},
}

# ---------------------------------------------------------------------------
# Smoking-accessory detection
# ---------------------------------------------------------------------------
SMOKING_KEYWORDS = {
    "puffco", "peak", "proxy", "banger", "dab", "rig", "bowl", "pipe",
    "bubbler", "bong", "carb cap", "carbcap", "vape", "mod", "chamber",
    "atomizer", "cartridge", "710", "wax", "concentrate", "terp", "nectar",
    "smoking", "smoke", "herb", "grinder", "ash", "roach",
}
SMOKING_UPCHARGE = 0.35  # 35 %


def _is_smoking_accessory(piece_name: str, tags: list = None) -> bool:
    """Return True if name or any tag matches a smoking-accessory keyword."""
    haystack = piece_name.lower()
    if tags:
        haystack += " " + " ".join(t.lower() for t in tags)
    return any(kw in haystack for kw in SMOKING_KEYWORDS)


# ---------------------------------------------------------------------------
# Calliope (Ender-3 V3 Plus) machine defaults
# ---------------------------------------------------------------------------
CALLIOPE_DEFAULTS = {
    "purchase_price_usd":        399.0,
    "lifespan_hours":            5000,
    "maintenance_rate_per_hour": 0.10,
    "machine_power_w":           180,
    "electricity_rate_per_kwh":  0.13,
    "success_rate":              0.92,
    "minimum_margin_pct":        0.30,
    "labor_hourly_rate_usd":     20.0,
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------
@dataclass
class MaterialSpec:
    spool_cost_usd: float = 22.0
    spool_weight_g: float = 1000.0
    part_weight_g: float = 20.0
    support_weight_g: float = 0.0
    waste_buffer_pct: float = 10.0


@dataclass
class PrintSpec:
    print_time_hours: float = 1.0
    machine_power_w: float = CALLIOPE_DEFAULTS["machine_power_w"]
    electricity_rate_per_kwh: float = CALLIOPE_DEFAULTS["electricity_rate_per_kwh"]


@dataclass
class MachineSpec:
    purchase_price_usd: float = CALLIOPE_DEFAULTS["purchase_price_usd"]
    lifespan_hours: float = CALLIOPE_DEFAULTS["lifespan_hours"]
    maintenance_rate_per_hour: float = CALLIOPE_DEFAULTS["maintenance_rate_per_hour"]


@dataclass
class LaborSpec:
    prep_minutes: float = 10.0
    postprocess_minutes: float = 10.0
    design_minutes: float = 0.0
    hourly_rate_usd: float = CALLIOPE_DEFAULTS["labor_hourly_rate_usd"]


@dataclass
class ExtrasSpec:
    hardware_cost_usd: float = 0.0
    packaging_cost_usd: float = 0.50
    shipping_cost_usd: float = 0.0


@dataclass
class RiskSpec:
    success_rate: float = CALLIOPE_DEFAULTS["success_rate"]
    minimum_margin_pct: float = CALLIOPE_DEFAULTS["minimum_margin_pct"]


@dataclass
class MarketSpec:
    comparables: list = field(default_factory=list)
    local_multiplier: float = 1.0
    customization_premium_pct: float = 0.10
    rush_premium_pct: float = 0.0
    tags: list = field(default_factory=list)


@dataclass
class PrintBrief:
    job_type: str = "functional_custom_part"
    piece_name: str = "unnamed"
    quantity: int = 1
    material: MaterialSpec = field(default_factory=MaterialSpec)
    print: PrintSpec = field(default_factory=PrintSpec)
    machine: MachineSpec = field(default_factory=MachineSpec)
    labor: LaborSpec = field(default_factory=LaborSpec)
    extras: ExtrasSpec = field(default_factory=ExtrasSpec)
    risk: RiskSpec = field(default_factory=RiskSpec)
    market: MarketSpec = field(default_factory=MarketSpec)


# ---------------------------------------------------------------------------
# Cost helpers
# ---------------------------------------------------------------------------
def _material_cost(m: MaterialSpec) -> float:
    total_g = (m.part_weight_g + m.support_weight_g) * (1 + m.waste_buffer_pct / 100)
    cost_per_g = m.spool_cost_usd / m.spool_weight_g
    return total_g * cost_per_g


def _labor_cost(l: LaborSpec) -> float:
    total_minutes = l.prep_minutes + l.postprocess_minutes + l.design_minutes
    return (total_minutes / 60.0) * l.hourly_rate_usd


def _depreciation(m: MachineSpec, p: PrintSpec) -> float:
    return (m.purchase_price_usd / m.lifespan_hours) * p.print_time_hours


def _maintenance(m: MachineSpec, p: PrintSpec) -> float:
    return m.maintenance_rate_per_hour * p.print_time_hours


def _electricity(p: PrintSpec) -> float:
    kwh = (p.machine_power_w / 1000.0) * p.print_time_hours
    return kwh * p.electricity_rate_per_kwh


def _extras_total(e: ExtrasSpec) -> float:
    return e.hardware_cost_usd + e.packaging_cost_usd + e.shipping_cost_usd


# ---------------------------------------------------------------------------
# TRUE weighted median  (replaces the old weighted mean)
# ---------------------------------------------------------------------------
def _market_median(comparables: list) -> Optional[float]:
    """
    True weighted median via cumulative-weight bisect.

    Each comparable: {"price_usd": float, "similarity": float}
    Similarity is treated as the weight (0–1).  Items with weight 0
    are excluded.  Falls back to a simple sort-median for a single item.

    Algorithm:
      1. Sort items by price_usd.
      2. Build a prefix-sum of weights.
      3. Find the price at which the cumulative weight first reaches
         >= 50 % of total weight  (lower weighted median).
    """
    if not comparables:
        return None

    filtered = [c for c in comparables if c.get("similarity", 0) > 0]
    if not filtered:
        return None
    if len(filtered) == 1:
        return filtered[0]["price_usd"]

    # sort ascending by price
    items = sorted(filtered, key=lambda c: c["price_usd"])
    prices  = [c["price_usd"]   for c in items]
    weights = [c["similarity"]  for c in items]

    total  = sum(weights)
    target = total / 2.0

    cumulative = 0.0
    for price, w in zip(prices, weights):
        cumulative += w
        if cumulative >= target:
            return price

    return prices[-1]  # fallback (floating-point edge)


def _value_premium(cost_floor: float, market: MarketSpec) -> float:
    premium = cost_floor * market.customization_premium_pct
    premium += cost_floor * market.rush_premium_pct
    return premium


# ---------------------------------------------------------------------------
# Market data fetcher  (live scrape — graceful stub when deps missing)
# ---------------------------------------------------------------------------
ETSY_SEARCH_URL = "https://www.etsy.com/search?q={query}&min_price={min_p}&max_price={max_p}"


def fetch_market_comps(query: str,
                       min_price: float = 1.0,
                       max_price: float = 500.0,
                       max_results: int = 10) -> list:
    """
    Attempt a live scrape of Etsy for comparable price data.
    Returns a list of {"price_usd": float, "similarity": float, "source": str}.

    Requires: requests, bs4 (beautifulsoup4)
    If either is missing, returns [] and prints a warning.

    similarity is set to 0.70 for all live results (no NLP scoring yet;
    treated as moderately comparable).  Override in your MarketSpec if needed.
    """
    if not _REQUESTS_OK or not _BS4_OK:
        missing = [k for k, v in LIBRARY_STATUS.items() if not v]
        print(f"[fetch_market_comps] WARN: missing libraries {missing} — returning empty comps.")
        return []

    import requests
    from bs4 import BeautifulSoup

    url = ETSY_SEARCH_URL.format(
        query=requests.utils.quote(query),
        min_p=int(min_price),
        max_p=int(max_price),
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DjinnPriceBot/1.1)",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
    except Exception as exc:
        print(f"[fetch_market_comps] HTTP error: {exc}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    # Etsy price spans carry data-price or a currency class — heuristic parse
    for tag in soup.select("span[class*='currency-value']"):
        try:
            price = float(tag.get_text(strip=True).replace(",", ""))
            if min_price <= price <= max_price:
                results.append({
                    "price_usd":  price,
                    "similarity": 0.70,
                    "source":     "etsy",
                })
        except ValueError:
            continue
        if len(results) >= max_results:
            break

    return results


# ---------------------------------------------------------------------------
# Main quote calculator
# ---------------------------------------------------------------------------
def calculate_quote(brief: PrintBrief) -> dict:
    """
    Core pricing formula from PRICING_SPEC.md:
        base_cost       = material + labor + depreciation + maintenance + electricity + extras
        risk_adjusted   = base_cost / success_rate
        cost_floor      = risk_adjusted x (1 + minimum_margin)
        fair_market     = wc*cost_floor + wm*market_median + wv*(cost_floor + value_premium)
        smoking_upcharge= fair_market * SMOKING_UPCHARGE  (if applicable)
        premium_ceiling = fair_market * 1.15
    """
    weights = JOB_WEIGHTS.get(brief.job_type, JOB_WEIGHTS["functional_custom_part"])

    mat   = _material_cost(brief.material)
    lab   = _labor_cost(brief.labor)
    depr  = _depreciation(brief.machine, brief.print)
    maint = _maintenance(brief.machine, brief.print)
    elec  = _electricity(brief.print)
    ext   = _extras_total(brief.extras)

    base_cost     = mat + lab + depr + maint + elec + ext
    risk_adjusted = base_cost / brief.risk.success_rate
    cost_floor    = risk_adjusted * (1 + brief.risk.minimum_margin_pct)

    market_med = _market_median(brief.market.comparables)
    val_prem   = _value_premium(cost_floor, brief.market)

    wc = weights["cost"]
    wm = weights["market"]
    wv = weights["value"]

    if market_med is not None:
        fair_market = (wc * cost_floor
                       + wm * market_med * brief.market.local_multiplier
                       + wv * (cost_floor + val_prem))
    else:
        fair_market = ((wc + wm) * cost_floor + wv * (cost_floor + val_prem))

    # Smoking-accessory upcharge
    smoking = _is_smoking_accessory(brief.piece_name, brief.market.tags)
    if smoking:
        fair_market *= (1 + SMOKING_UPCHARGE)

    fair_market      *= brief.quantity
    premium_ceiling   = fair_market * 1.15
    cost_floor_total  = cost_floor * brief.quantity

    return {
        "piece_name":             brief.piece_name,
        "job_type":               brief.job_type,
        "quantity":               brief.quantity,
        "smoking_accessory":      smoking,
        "smoking_upcharge_pct":   SMOKING_UPCHARGE if smoking else 0.0,
        "unit_breakdown": {
            "material_usd":      round(mat,   4),
            "labor_usd":         round(lab,   4),
            "depreciation_usd":  round(depr,  4),
            "maintenance_usd":   round(maint, 4),
            "electricity_usd":   round(elec,  4),
            "extras_usd":        round(ext,   4),
            "base_cost_usd":     round(base_cost, 4),
        },
        "cost_floor_usd":        round(cost_floor_total, 2),
        "fair_market_usd":       round(fair_market,  2),
        "premium_ceiling_usd":   round(premium_ceiling, 2),
        "recommended_price_usd": round(fair_market, 2),
        "market_median_usd":     round(market_med, 2) if market_med else None,
        "weights_used":          weights,
        "library_status":        LIBRARY_STATUS,
    }


def quote_from_dict(d: dict) -> dict:
    """Convenience: build a PrintBrief from a raw dict and return a quote."""
    mk = d.get("market", {})
    brief = PrintBrief(
        job_type   = d.get("job_type", "functional_custom_part"),
        piece_name = d.get("piece_name", "unnamed"),
        quantity   = d.get("quantity", 1),
        material   = MaterialSpec(**d["material"]) if "material" in d else MaterialSpec(),
        print      = PrintSpec(**d["print"])       if "print"    in d else PrintSpec(),
        machine    = MachineSpec(**d["machine"])   if "machine"  in d else MachineSpec(),
        labor      = LaborSpec(**d["labor"])       if "labor"    in d else LaborSpec(),
        extras     = ExtrasSpec(**d["extras"])     if "extras"   in d else ExtrasSpec(),
        risk       = RiskSpec(**d["risk"])         if "risk"     in d else RiskSpec(),
        market     = MarketSpec(
            comparables               = mk.get("comparables", []),
            local_multiplier          = mk.get("local_multiplier", 1.0),
            customization_premium_pct = mk.get("customization_premium_pct", 0.10),
            rush_premium_pct          = mk.get("rush_premium_pct", 0.0),
            tags                      = mk.get("tags", []),
        ) if mk else MarketSpec(),
    )
    return calculate_quote(brief)


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------
PRESET_COIN = {
    "job_type": "design_heavy_oneoff",
    "piece_name": "Typhon's Forge Coin",
    "quantity": 1,
    "material":  {"spool_cost_usd": 22, "spool_weight_g": 1000,
                  "part_weight_g": 15, "support_weight_g": 0, "waste_buffer_pct": 10},
    "print":     {"print_time_hours": 1.5},
    "labor":     {"prep_minutes": 10, "postprocess_minutes": 20, "design_minutes": 180},
    "extras":    {"packaging_cost_usd": 1.00},
    "market":    {"comparables": [{"price_usd": 18.00, "similarity": 0.80}],
                  "customization_premium_pct": 0.25},
}

PRESET_STANDARD = {
    "job_type": "functional_custom_part",
    "piece_name": "Standard Part",
    "quantity": 1,
}

PRESET_PUFFCO_CAP = {
    "job_type": "functional_custom_part",
    "piece_name": "Puffco Peak Cap",
    "quantity": 1,
    "material":  {"part_weight_g": 12, "support_weight_g": 2},
    "print":     {"print_time_hours": 1.0},
    "labor":     {"prep_minutes": 10, "postprocess_minutes": 15},
    "market":    {"comparables": [{"price_usd": 22.00, "similarity": 0.90}],
                  "customization_premium_pct": 0.15},
}


if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--coin":
            q = quote_from_dict(PRESET_COIN)
        elif sys.argv[1] == "--standard":
            q = quote_from_dict(PRESET_STANDARD)
        elif sys.argv[1] == "--puffco":
            q = quote_from_dict(PRESET_PUFFCO_CAP)
        else:
            raw = json.loads(" ".join(sys.argv[1:]))
            q = quote_from_dict(raw)
    else:
        q = quote_from_dict(PRESET_STANDARD)
    print(json.dumps(q, indent=2))

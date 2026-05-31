"""
price.py — FairPrintAgent pricing agent.
Reads ProjectState (concept + DOE metadata), computes quote, advances job to priced.
Pure Python. No LLM calls. Deterministic.
"""
import json, math, sys
import pathlib as _pl
from dataclasses import dataclass, field, asdict
from typing import Optional
from ..project_state import ProjectState

# ── Shared utils from commissions ─────────────────────────────────────────────
_PRINTER = _pl.Path(__file__).parents[3]
if str(_PRINTER) not in sys.path:
    sys.path.insert(0, str(_PRINTER))
from commissions.price import (
    _is_smoking_accessory as is_smoking_item,
    SMOKING_UPCHARGE,
    fetch_market_comps,
    weighted_median,
)

# ── Defaults (Calliope / Ender-3 V3 Plus) ────────────────────────────────────
SPOOL_COST_USD = 22.0
SPOOL_WEIGHT_G = 1000
MACHINE_COST_USD = 399.0
MACHINE_LIFESPAN_H = 5000
MAINTENANCE_PER_H = 0.10
POWER_W = 180
ELECTRICITY_RATE = 0.13
LABOR_RATE_USD = 20.0
SUCCESS_RATE = 0.92
MIN_MARGIN = 0.30
WASTE_BUFFER = 0.10

# Job-type weights: (cost, market, value)
WEIGHTS = {
    "commodity_decor":        (0.65, 0.30, 0.05),
    "functional_custom_part": (0.55, 0.30, 0.15),
    "design_heavy_oneoff":    (0.40, 0.25, 0.35),
    "urgent_rush":            (0.50, 0.20, 0.30),
}



# ── Quote dataclasses ────────────────────────────────────────────────────────

@dataclass
class QuoteBreakdown:
    material: float = 0.0
    electricity: float = 0.0
    depreciation: float = 0.0
    maintenance: float = 0.0
    labor: float = 0.0
    packaging: float = 0.0
    base_cost: float = 0.0
    risk_adjusted: float = 0.0


@dataclass
class QuoteMarket:
    median: float = 0.0
    comp_count: int = 0
    sources: list = field(default_factory=list)
    prices: list = field(default_factory=list)


@dataclass
class Quote:
    piece_name: str = ""
    job_type: str = "functional_custom_part"
    cost_floor: float = 0.0
    fair_market_estimate: float = 0.0
    premium_ceiling: float = 0.0
    confidence: str = "medium"
    breakdown: QuoteBreakdown = field(default_factory=QuoteBreakdown)
    market: QuoteMarket = field(default_factory=QuoteMarket)
    inputs: dict = field(default_factory=dict)
    top_driver: str = ""


# ── Main pricing logic ───────────────────────────────────────────────────────

def run(state: ProjectState) -> ProjectState:
    concept = state.concept or {}
    doe = state.doe_profile or {}
    brief = state.brief or {}

    material_g = (
        doe.get("material_g")
        or concept.get("material_g_estimate")
        or 50
    )
    support_g = doe.get("support_g", 0)
    print_hours = (
        doe.get("print_time_h")
        or concept.get("estimated_print_time_h")
        or 2.0
    )
    prep_min = doe.get("prep_min", 10)
    post_min = doe.get("postprocess_min", 10)
    design_min = doe.get("design_min", 0)
    job_type = doe.get("job_type", concept.get("job_type", "functional_custom_part"))

    unit_cost = SPOOL_COST_USD / SPOOL_WEIGHT_G
    used_g = material_g + support_g
    material_cost = unit_cost * used_g * (1 + WASTE_BUFFER)
    electricity_cost = (POWER_W / 1000) * print_hours * ELECTRICITY_RATE
    depreciation = (MACHINE_COST_USD / MACHINE_LIFESPAN_H) * print_hours
    maintenance = MAINTENANCE_PER_H * print_hours
    labor_hours = (prep_min + post_min + design_min) / 60
    labor_cost = labor_hours * LABOR_RATE_USD
    packaging = 0.50

    base_cost = material_cost + electricity_cost + depreciation + maintenance + labor_cost + packaging
    risk_adjusted = base_cost / SUCCESS_RATE
    cost_floor = risk_adjusted * (1 + MIN_MARGIN)

    # Market search — auto-fetch comparables by piece name
    piece_name = brief.get("piece_name") or state.note or ""
    size = doe.get("market_size") or concept.get("market_size") or None
    comps = []
    if piece_name:
        comps = fetch_market_comps(piece_name, size=size)

    market_median = weighted_median(comps) if comps else (concept.get("market_price_estimate") or cost_floor)
    local_mult = 1.0
    custom_prem = 0.10 if design_min > 0 else 0.0
    value_premium = cost_floor * custom_prem

    wc, wm, wv = WEIGHTS.get(job_type, WEIGHTS["functional_custom_part"])
    fair_market = max(cost_floor, wc * cost_floor + wm * market_median * local_mult + wv * (cost_floor + value_premium))
    is_smoking = is_smoking_item(piece_name) if piece_name else False
    if is_smoking:
        fair_market = fair_market * (1 + SMOKING_UPCHARGE)
    premium_ceiling = fair_market * 1.15

    design_exists = bool(state.source_scad or state.source_stl)
    has_comps = len(comps) >= 2
    has_design_time = design_min > 0
    confidence = "high" if has_comps else ("medium" if has_design_time else "low")

    drivers = sorted([
        ("material", material_cost),
        ("labor", labor_cost),
        ("depreciation", depreciation),
        ("maintenance", maintenance),
        ("electricity", electricity_cost),
        ("packaging", packaging),
    ], key=lambda x: x[1], reverse=True)

    breakdown = QuoteBreakdown(
        material=round(material_cost, 2),
        electricity=round(electricity_cost, 2),
        depreciation=round(depreciation, 2),
        maintenance=round(maintenance, 2),
        labor=round(labor_cost, 2),
        packaging=round(packaging, 2),
        base_cost=round(base_cost, 2),
        risk_adjusted=round(risk_adjusted, 2),
    )

    market_info = QuoteMarket(
        median=round(market_median, 2) if market_median else 0,
        comp_count=len(comps),
        sources=[c.get("source", "") for c in comps if c.get("source")],
        prices=[c["price_usd"] for c in comps],
    )

    state.quote = asdict(Quote(
        piece_name=piece_name,
        job_type=job_type,
        cost_floor=round(cost_floor, 2),
        fair_market_estimate=round(fair_market, 2),
        premium_ceiling=round(premium_ceiling, 2),
        confidence=confidence,
        breakdown=breakdown,
        market=market_info,
        inputs={
            "material_g": material_g,
            "support_g": support_g,
            "print_hours": print_hours,
            "prep_min": prep_min,
            "post_min": post_min,
            "design_min": design_min,
            "job_type": job_type,
            "market_size": size,
            "smoking_upcharge_pct": SMOKING_UPCHARGE * 100 if is_smoking else 0,
        },
        top_driver=drivers[0][0],
    ))

    state.status = "priced"
    return state

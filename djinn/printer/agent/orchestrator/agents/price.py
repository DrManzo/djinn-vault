"""
price.py — FairPrintAgent pricing agent.
Reads ProjectState (concept + DOE metadata), computes quote, advances job to priced.
Pure Python. No LLM calls. Deterministic.
"""
import math
from ..project_state import ProjectState

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


def run(state: ProjectState) -> ProjectState:
    concept = state.concept or {}
    doe = state.doe_profile or {}

    # Pull from concept, DOE, or sensible defaults
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

    # Material
    unit_cost = SPOOL_COST_USD / SPOOL_WEIGHT_G
    used_g = material_g + support_g
    material_cost = unit_cost * used_g * (1 + WASTE_BUFFER)

    # Electricity
    electricity_cost = (POWER_W / 1000) * print_hours * ELECTRICITY_RATE

    # Machine depreciation + maintenance
    depreciation = (MACHINE_COST_USD / MACHINE_LIFESPAN_H) * print_hours
    maintenance = MAINTENANCE_PER_H * print_hours

    # Labor
    labor_hours = (prep_min + post_min + design_min) / 60
    labor_cost = labor_hours * LABOR_RATE_USD

    # Packaging
    packaging = 0.50

    base_cost = material_cost + electricity_cost + depreciation + maintenance + labor_cost + packaging
    risk_adjusted = base_cost / SUCCESS_RATE
    cost_floor = risk_adjusted * (1 + MIN_MARGIN)

    # Market — use concept price estimate if available, otherwise cost-floor
    market_median = concept.get("market_price_estimate") or cost_floor
    local_mult = 1.0
    custom_prem = 0.10 if design_min > 0 else 0.0
    value_premium = cost_floor * custom_prem

    wc, wm, wv = WEIGHTS.get(job_type, WEIGHTS["functional_custom_part"])
    fair_market = max(cost_floor, wc * cost_floor + wm * market_median * local_mult + wv * (cost_floor + value_premium))
    premium_ceiling = fair_market * 1.15

    # Confidence
    design_exists = bool(state.source_scad or state.source_stl)
    confidence = "high" if design_exists else "medium"

    drivers = sorted([
        ("material", material_cost),
        ("labor", labor_cost),
        ("depreciation", depreciation),
        ("maintenance", maintenance),
        ("electricity", electricity_cost),
        ("packaging", packaging),
    ], key=lambda x: x[1], reverse=True)

    state.quote = {
        "piece_name": state.note,
        "job_type": job_type,
        "cost_floor": round(cost_floor, 2),
        "fair_market_estimate": round(fair_market, 2),
        "premium_ceiling": round(premium_ceiling, 2),
        "confidence": confidence,
        "breakdown": {
            "material": round(material_cost, 2),
            "electricity": round(electricity_cost, 2),
            "depreciation": round(depreciation, 2),
            "maintenance": round(maintenance, 2),
            "labor": round(labor_cost, 2),
            "packaging": round(packaging, 2),
            "base_cost": round(base_cost, 2),
            "risk_adjusted": round(risk_adjusted, 2),
        },
        "inputs": {
            "material_g": material_g,
            "support_g": support_g,
            "print_hours": print_hours,
            "prep_min": prep_min,
            "post_min": post_min,
            "design_min": design_min,
            "job_type": job_type,
        },
        "top_driver": drivers[0][0],
    }

    state.status = "priced"
    return state

#!/usr/bin/env python3
"""
brief.py — Intake validation layer for the Djinn print pricing pipeline.
Converts a raw user request (from Telegram, Discord, CLI, or dict)
into a validated PrintBrief dict ready for price.py.

— Marcus
"""

import re
import json
from dataclasses import dataclass, asdict, field
from typing import Optional


VALID_JOB_TYPES = {
    "commodity_decor",
    "functional_custom_part",
    "design_heavy_oneoff",
    "urgent_rush",
}

VALID_MATERIALS = {
    "pla":   {"spool_cost_usd": 22.0, "spool_weight_g": 1000},
    "petg":  {"spool_cost_usd": 28.0, "spool_weight_g": 1000},
    "abs":   {"spool_cost_usd": 25.0, "spool_weight_g": 1000},
    "tpu":   {"spool_cost_usd": 35.0, "spool_weight_g": 500},
    "resin": {"spool_cost_usd": 45.0, "spool_weight_g": 1000},
}


@dataclass
class ValidationError:
    field: str
    message: str


@dataclass
class BriefResult:
    valid: bool
    brief: Optional[dict] = None
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


def _infer_job_type(text: str) -> str:
    text = text.lower()
    if any(w in text for w in ["rush", "urgent", "asap", "today"]):
        return "urgent_rush"
    if any(w in text for w in ["design", "custom", "oneoff", "one-off", "original"]):
        return "design_heavy_oneoff"
    if any(w in text for w in ["functional", "bracket", "mount", "enclosure", "jig", "tool"]):
        return "functional_custom_part"
    return "commodity_decor"


def _parse_telegram_shorthand(text: str) -> Optional[dict]:
    """
    Parse: quote print <name> <grams> <hours>
    Example: quote print "puffco cap" 18 2.5
    """
    pattern = r'quote\s+print\s+"?([^"]+)"?\s+([\d.]+)\s+([\d.]+)'
    m = re.match(pattern, text.strip(), re.IGNORECASE)
    if m:
        name, grams, hours = m.group(1), float(m.group(2)), float(m.group(3))
        return {
            "job_type": "commodity_decor",
            "piece_name": name,
            "quantity": 1,
            "material": {"part_weight_g": grams},
            "print": {"print_time_hours": hours},
        }
    return None


def validate_brief(raw: dict) -> BriefResult:
    errors = []
    warnings = []
    out = {}

    jt = raw.get("job_type", "")
    if jt not in VALID_JOB_TYPES:
        if jt:
            warnings.append(f"Unknown job_type '{jt}', defaulting to functional_custom_part")
        out["job_type"] = "functional_custom_part"
    else:
        out["job_type"] = jt

    out["piece_name"] = str(raw.get("piece_name", "unnamed part")).strip()[:80]

    qty = raw.get("quantity", 1)
    if not isinstance(qty, int) or qty < 1:
        warnings.append("quantity must be a positive integer — defaulting to 1")
        qty = 1
    out["quantity"] = qty

    mat = raw.get("material", {})
    mat_type = mat.pop("type", "pla").lower()
    defaults = VALID_MATERIALS.get(mat_type, VALID_MATERIALS["pla"])
    out["material"] = {
        "spool_cost_usd":   mat.get("spool_cost_usd",   defaults["spool_cost_usd"]),
        "spool_weight_g":   mat.get("spool_weight_g",   defaults["spool_weight_g"]),
        "part_weight_g":    mat.get("part_weight_g",    20.0),
        "support_weight_g": mat.get("support_weight_g", 0.0),
        "waste_buffer_pct": mat.get("waste_buffer_pct", 10.0),
    }
    if out["material"]["part_weight_g"] <= 0:
        errors.append(ValidationError("material.part_weight_g", "part weight must be > 0"))

    pr = raw.get("print", {})
    pth = pr.get("print_time_hours", 1.0)
    if pth <= 0:
        errors.append(ValidationError("print.print_time_hours", "print time must be > 0"))
    out["print"] = {
        "print_time_hours":         pth,
        "machine_power_w":          pr.get("machine_power_w", 180),
        "electricity_rate_per_kwh": pr.get("electricity_rate_per_kwh", 0.13),
    }

    mc = raw.get("machine", {})
    out["machine"] = {
        "purchase_price_usd":       mc.get("purchase_price_usd", 399.0),
        "lifespan_hours":           mc.get("lifespan_hours", 5000),
        "maintenance_rate_per_hour":mc.get("maintenance_rate_per_hour", 0.10),
    }

    lb = raw.get("labor", {})
    out["labor"] = {
        "prep_minutes":        lb.get("prep_minutes", 10.0),
        "postprocess_minutes": lb.get("postprocess_minutes", 10.0),
        "design_minutes":      lb.get("design_minutes", 0.0),
        "hourly_rate_usd":     lb.get("hourly_rate_usd", 20.0),
    }

    ex = raw.get("extras", {})
    out["extras"] = {
        "hardware_cost_usd":  ex.get("hardware_cost_usd", 0.0),
        "packaging_cost_usd": ex.get("packaging_cost_usd", 0.50),
        "shipping_cost_usd":  ex.get("shipping_cost_usd", 0.0),
    }

    rk = raw.get("risk", {})
    sr = rk.get("success_rate", 0.92)
    if not (0 < sr <= 1.0):
        errors.append(ValidationError("risk.success_rate", "success_rate must be between 0 and 1"))
    out["risk"] = {
        "success_rate":       sr,
        "minimum_margin_pct": rk.get("minimum_margin_pct", 0.30),
    }

    mk = raw.get("market", {})
    out["market"] = {
        "comparables":               mk.get("comparables", []),
        "local_multiplier":          mk.get("local_multiplier", 1.0),
        "customization_premium_pct": mk.get("customization_premium_pct", 0.10),
        "rush_premium_pct":          mk.get("rush_premium_pct", 0.0),
    }

    if errors:
        return BriefResult(valid=False, errors=[asdict(e) for e in errors], warnings=warnings)
    return BriefResult(valid=True, brief=out, warnings=warnings)


def intake(source: str) -> BriefResult:
    parsed = _parse_telegram_shorthand(source)
    if parsed:
        return validate_brief(parsed)
    try:
        raw = json.loads(source)
        return validate_brief(raw)
    except json.JSONDecodeError:
        return BriefResult(
            valid=False,
            errors=[{"field": "input", "message": f"Could not parse input: {source[:80]}"}]
        )


if __name__ == "__main__":
    import sys
    src = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else '{"job_type":"commodity_decor","material":{"part_weight_g":25},"print":{"print_time_hours":2}}'
    result = intake(src)
    import json
    print(json.dumps({"valid": result.valid, "brief": result.brief,
                      "errors": result.errors, "warnings": result.warnings}, indent=2))

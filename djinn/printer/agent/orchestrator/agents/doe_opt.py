"""
DOEPrintOptAgent — Design of Experiments slicer parameter optimizer.

Uses a Taguchi-inspired factor grid + literature-calibrated prediction models.
No actual prints required — savings are predicted from published AM research.

Literature baselines (Swansea 2023, Formlabs DfAM, Siemens AM guidance):
  lightning infill vs 20% gyroid:    -51% material, -38% time
  hot-end silicone sock:             -30–34% energy loss
  full enclosure (prints >2hr):      -15–18% average power draw
  reduced support line width 0.6→0.4mm: -31% support polymer use
"""
import math
from dataclasses import dataclass, field, asdict
from typing import Optional

from ..project_state import ProjectState


# ── Prediction factors vs baseline (0.2mm / 60mm/s / 20% gyroid / 3 walls) ──

LAYER_FACTORS = {
    # layer_mm: (time_mult, material_mult, strength_rel)
    0.12: (1.55, 1.01, 1.20),
    0.16: (1.25, 1.00, 1.10),
    0.20: (1.00, 1.00, 1.00),
    0.24: (0.85, 0.99, 0.95),
    0.28: (0.72, 0.98, 0.88),
    0.32: (0.63, 0.97, 0.82),
    0.36: (0.57, 0.95, 0.75),
}

SPEED_FACTORS = {
    # mm/s: (time_mult, material_mult, strength_rel)
    40:  (1.40, 1.00, 1.08),
    50:  (1.18, 1.00, 1.04),
    60:  (1.00, 1.00, 1.00),
    80:  (0.77, 0.99, 0.94),
    100: (0.63, 0.98, 0.87),
    120: (0.55, 0.97, 0.80),
}

INFILL_FACTORS = {
    # (type, density_pct): (time_mult, material_mult, structural_score 0–1)
    ("lightning",  5):  (0.52, 0.47, 0.22),
    ("lightning", 10):  (0.55, 0.51, 0.28),
    ("lightning", 15):  (0.58, 0.56, 0.33),
    ("lightning", 20):  (0.62, 0.62, 0.38),
    ("gyroid",     5):  (0.68, 0.53, 0.32),
    ("gyroid",    10):  (0.78, 0.63, 0.48),
    ("gyroid",    15):  (0.90, 0.82, 0.72),
    ("gyroid",    20):  (1.00, 1.00, 1.00),   # baseline
    ("gyroid",    30):  (1.18, 1.28, 1.22),
    ("gyroid",    40):  (1.38, 1.58, 1.45),
    ("cubic",     10):  (0.80, 0.65, 0.50),
    ("cubic",     20):  (1.02, 1.02, 1.05),
    ("cubic",     40):  (1.40, 1.60, 1.48),
    ("grid",      15):  (0.88, 0.88, 0.80),
    ("grid",      20):  (0.97, 0.99, 0.93),
    ("grid",      40):  (1.30, 1.50, 1.32),
    ("honeycomb", 15):  (0.90, 0.90, 0.85),
    ("honeycomb", 20):  (1.00, 1.02, 1.08),
}

WALL_FACTORS = {
    # walls: (time_mult, material_mult, strength_rel)
    2: (0.87, 0.84, 0.78),
    3: (1.00, 1.00, 1.00),   # baseline
    4: (1.13, 1.17, 1.22),
    5: (1.26, 1.34, 1.42),
}

SUPPORT_WIDTH_FACTORS = {
    # line_width_mm: (time_mult, support_material_mult)
    0.4: (0.99, 0.69),   # -31% support polymer (Swansea)
    0.6: (1.00, 1.00),   # baseline
}


@dataclass
class PrintProfile:
    layer_height_mm: float
    print_speed_mms: float
    infill_density_pct: int
    infill_type: str
    wall_count: int
    support_line_width_mm: float

    time_factor:     float = 1.0
    material_factor: float = 1.0
    strength_score:  float = 1.0

    def predict(self) -> "PrintProfile":
        lf  = _nearest(LAYER_FACTORS, self.layer_height_mm)
        sf  = _nearest(SPEED_FACTORS, self.print_speed_mms)
        inf = INFILL_FACTORS.get((self.infill_type, self.infill_density_pct),
                                  INFILL_FACTORS[("gyroid", 20)])
        wf  = WALL_FACTORS.get(self.wall_count, WALL_FACTORS[3])
        suf = SUPPORT_WIDTH_FACTORS.get(self.support_line_width_mm,
                                         SUPPORT_WIDTH_FACTORS[0.6])

        self.time_factor     = lf[0] * sf[0] * inf[0] * wf[0]
        self.material_factor = lf[1] * sf[1] * inf[1] * wf[1] * suf[1]
        self.strength_score  = lf[2] * sf[2] * inf[2] * wf[2]
        return self

    def objective(self, goal: str) -> float:
        """Lower is better."""
        if goal == "prototype_fast":
            return 0.60 * self.time_factor + 0.30 * self.material_factor - 0.10 * self.strength_score
        if goal == "prototype_cheap":
            return 0.20 * self.time_factor + 0.70 * self.material_factor - 0.10 * self.strength_score
        # balanced
        return 0.40 * self.time_factor + 0.40 * self.material_factor - 0.20 * self.strength_score


def _nearest(table: dict, value):
    """Return value from table with key closest to value."""
    key = min(table.keys(), key=lambda k: abs(k - value))
    return table[key]


def _build_candidates(goal: str, supports: bool) -> list[PrintProfile]:
    is_proto = goal.startswith("prototype")

    layers = [0.20, 0.28, 0.36] if is_proto else [0.16, 0.20, 0.24]
    speeds = [60, 80, 100]      if is_proto else [50, 60, 80]

    if is_proto:
        infills = [
            ("lightning",  5), ("lightning", 10), ("lightning", 20),
            ("gyroid",     5), ("gyroid",    10), ("gyroid",    15),
        ]
        walls = [2, 3]
    else:
        infills = [
            ("gyroid", 20), ("gyroid", 30), ("gyroid", 40),
            ("cubic",  20), ("cubic",  40),
        ]
        walls = [3, 4]

    sw = 0.4 if supports else 0.6

    candidates = []
    for lh in layers:
        for spd in speeds:
            for (itype, iden) in infills:
                for wc in walls:
                    p = PrintProfile(
                        layer_height_mm=lh,
                        print_speed_mms=spd,
                        infill_density_pct=iden,
                        infill_type=itype,
                        wall_count=wc,
                        support_line_width_mm=sw,
                    ).predict()
                    candidates.append(p)
    return candidates


def run(state: ProjectState, goal: str = "prototype_fast", printer: dict = None) -> ProjectState:
    if printer is None:
        printer = {
            "model": "Ender-3 V3 Plus",
            "has_enclosure": False,
            "hotend_sock": True,
            "bed_insulated": False,
        }

    supports = state.concept.get("supports_needed", state.supports_needed)
    candidates = _build_candidates(goal, supports)

    # Minimum strength thresholds
    min_strength = 0.22 if goal.startswith("prototype") else 0.85
    valid = [c for c in candidates if c.strength_score >= min_strength] or candidates

    valid.sort(key=lambda c: c.objective(goal))
    best = valid[0]

    # Savings vs standard baseline (20% gyroid / 0.2mm / 60mm/s / 3 walls / 0.6mm support)
    baseline = PrintProfile(0.20, 60, 20, "gyroid", 3, 0.6).predict()
    time_save     = round((1 - best.time_factor     / baseline.time_factor)     * 100)
    material_save = round((1 - best.material_factor / baseline.material_factor) * 100)

    # Machine-level notes
    notes = []
    if printer.get("has_enclosure"):
        notes.append("Enclosure active — 15–18% power reduction on prints over 2hr")
    else:
        notes.append("No enclosure — a cardboard box around the printer gives ~15% power savings on long prints")
    if printer.get("hotend_sock"):
        notes.append("Hot-end sock installed — ~30–34% reduction in thermal energy loss")
    else:
        notes.append("Install silicone hot-end sock ($2–5) for ~30% energy savings")
    if not printer.get("bed_insulated"):
        notes.append("Bed underside uninsulated — cork sheet or silicone mat reduces bed hold power by 10–15%")
    if supports:
        notes.append(f"Supports on: {best.support_line_width_mm}mm line width saves ~31% support polymer vs 0.6mm")

    # Tradeoffs
    tradeoffs = []
    if best.strength_score < 0.50:
        tradeoffs.append(f"Structural score {best.strength_score:.2f} — prototype/visual use only, not load-bearing")
    if best.infill_type == "lightning":
        tradeoffs.append("Lightning infill: poor top-surface bridging — use ≥4 top layers or switch to gyroid for better finish")
    if best.layer_height_mm >= 0.32:
        tradeoffs.append(f"{best.layer_height_mm}mm layers: visible lines, acceptable for fit/form checks")
    if best.print_speed_mms >= 100:
        tradeoffs.append(f"{best.print_speed_mms}mm/s: check for ringing artifacts — reduce if needed")

    profile = {
        "goal": goal,
        "recommended_profile": {
            "layer_height_mm":      best.layer_height_mm,
            "print_speed_mms":      best.print_speed_mms,
            "infill_density_pct":   best.infill_density_pct,
            "infill_type":          best.infill_type,
            "wall_count":           best.wall_count,
            "support_line_width_mm": best.support_line_width_mm,
        },
        "predicted_factors": {
            "time_factor":     round(best.time_factor, 3),
            "material_factor": round(best.material_factor, 3),
            "strength_score":  round(best.strength_score, 3),
        },
        "expected_savings_vs_standard": {
            "time_reduction_pct":     max(0, time_save),
            "material_reduction_pct": max(0, material_save),
        },
        "machine_notes":   notes,
        "tradeoffs":       tradeoffs,
        "confidence":      "high" if len(valid) >= 30 else "medium",
        "candidates_total":   len(candidates),
        "candidates_passing": len(valid),
        "top_5_alternatives": [
            {
                "layer": c.layer_height_mm,
                "speed": c.print_speed_mms,
                "infill": f"{c.infill_type} {c.infill_density_pct}%",
                "walls": c.wall_count,
                "score": round(c.objective(goal), 4),
            }
            for c in valid[1:6]
        ],
    }

    state.doe_profile = profile
    state.status = "plate_nest"

    return state

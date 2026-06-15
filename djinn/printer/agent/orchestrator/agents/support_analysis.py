"""
SupportAnalysis — mesh-based support decision module.
Analyzes STL face normals and bridge geometry to recommend support strategy.
No LLM needed — pure geometry + calibrated thresholds.

Angle convention: "overhang angle" measured from horizontal (FDM standard).
  0°  = face is horizontal, pointing down (worst — always needs support)
  45° = classic 45° rule threshold
  90° = face is vertical (no support needed)

Face normal Z convention:
  nz = -1  → face points straight down  → 0° from horizontal  → worst overhang
  nz = -0.707 → 45° from horizontal
  nz = 0   → vertical face
  threshold nz = -cos(angle_from_horizontal)
"""
import pathlib
import numpy as np
import trimesh

# Overhang threshold by material + profile.
# Value = -cos(overhang_angle_from_horizontal).
# PLA most permissive (prints clean at steeper angles due to fast cooling).
# PETG/ABS need tighter thresholds (more sag/warp).
# Angles: 55°→-0.574, 50°→-0.643, 45°→-0.707, 40°→-0.766, 35°→-0.819
OVERHANG_THRESHOLDS = {
    "pla":  {"proto": -0.574, "production": -0.643, "quality": -0.707},
    "petg": {"proto": -0.643, "production": -0.707, "quality": -0.766},
    "abs":  {"proto": -0.707, "production": -0.766, "quality": -0.819},
}

# Max unsupported bridge span (mm) before recommendation triggers
BRIDGE_LIMITS = {
    "proto": 20.0,
    "production": 15.0,
    "quality": 10.0,
}

# Risk score → support mode mapping
SCORE_LOCAL = 25   # score >= 25 → recommend localized supports
SCORE_FULL  = 60   # score >= 60 → recommend full supports

# Minimum height (mm) for a near-horizontal face to be a bridge candidate.
# Faces below this height are likely the object's flat bottom.
MIN_BRIDGE_HEIGHT = 3.0


def analyze(
    stl_path: str | pathlib.Path,
    material: str = "pla",
    profile: str = "production",
) -> dict:
    """
    Analyze STL for support requirements.

    Args:
        stl_path: path to .stl file
        material: "pla" | "petg" | "abs"
        profile:  "proto" | "production" | "quality"

    Returns dict with:
        supports_recommended  bool
        support_mode          "none" | "local" | "full"
        risk_score            0-100
        reason_codes          [str, ...]
        user_message          str
        stats                 {overhang_face_pct, max_overhang_angle_deg,
                               bridge_span_mm, total_faces}
    """
    mesh = trimesh.load(str(stl_path), force="mesh")

    mat  = material.lower()
    prof = profile.lower()
    threshold   = OVERHANG_THRESHOLDS.get(mat, OVERHANG_THRESHOLDS["pla"]).get(prof, -0.707)
    bridge_limit = BRIDGE_LIMITS.get(prof, 15.0)

    normals = mesh.face_normals   # (N, 3), unit vectors
    areas   = mesh.area_faces     # (N,)
    total_area = areas.sum()

    # Face centroids for height filtering
    face_centroids = mesh.triangles_center  # (N, 3)

    # ── 1. Overhang analysis ──────────────────────────────────────────────────

    # Faces whose normals point below the threshold angle from horizontal
    steep_mask = normals[:, 2] < threshold
    steep_area = areas[steep_mask].sum()
    steep_pct  = (steep_area / total_area * 100) if total_area > 0 else 0.0

    # Maximum overhang severity (most negative nz → closest to horizontal)
    downward_mask = normals[:, 2] < 0
    if downward_mask.any():
        worst_nz = float(normals[downward_mask, 2].min())
        # FDM convention: angle from vertical (0°=vertical wall, 90°=horizontal face)
        # arcsin(|nz|): nz=-1 → 90°, nz=-0.707 → 45°, nz=0 → 0°
        max_overhang_deg = float(np.degrees(np.arcsin(min(abs(worst_nz), 1.0))))
    else:
        worst_nz = 0.0
        max_overhang_deg = 0.0

    # ── 2. Bridge detection ───────────────────────────────────────────────────
    # Near-horizontal downward faces that are elevated above the bed.
    # XY bounding-box span of those faces gives an upper bound on bridge length.
    bridge_mask = (normals[:, 2] < -0.9) & (face_centroids[:, 2] > MIN_BRIDGE_HEIGHT)
    bridge_span = 0.0
    if bridge_mask.any():
        bverts = mesh.vertices[mesh.faces[bridge_mask].reshape(-1)]
        bridge_span = float(max(
            bverts[:, 0].max() - bverts[:, 0].min(),
            bverts[:, 1].max() - bverts[:, 1].min(),
        ))

    # ── 3. Risk scoring ───────────────────────────────────────────────────────
    reason_codes = []
    risk_score   = 0

    # Material penalty
    if mat == "abs":
        risk_score += 15
        reason_codes.append("abs_warp_risk")
    elif mat == "petg":
        risk_score += 8
        reason_codes.append("petg_sag_risk")

    # Profile strictness modifier
    if prof == "quality":
        risk_score += 5

    # Overhang contribution
    if steep_pct > 10:
        risk_score += min(45, int(steep_pct * 2.5))
        reason_codes.append("steep_overhang")
    elif steep_pct > 3:
        risk_score += min(25, int(steep_pct * 4))
        reason_codes.append("steep_overhang")
    elif steep_pct > 0.5:
        risk_score += min(10, int(steep_pct * 6))
        reason_codes.append("minor_overhang")

    # Bridge contribution
    if bridge_span > bridge_limit * 1.5:
        risk_score += 30
        reason_codes.append("long_bridge")
    elif bridge_span > bridge_limit:
        risk_score += 15
        reason_codes.append("bridge_near_limit")

    risk_score = min(100, risk_score)

    # ── 4. Support mode ───────────────────────────────────────────────────────
    if risk_score >= SCORE_FULL:
        support_mode = "full"
    elif risk_score >= SCORE_LOCAL:
        support_mode = "local"
    else:
        support_mode = "none"

    supports_recommended = support_mode != "none"

    # ── 5. Human-readable message ─────────────────────────────────────────────
    if support_mode == "none":
        msg = (
            f"Printable without supports "
            f"({max_overhang_deg:.0f}° max overhang, risk score {risk_score})."
        )
    elif support_mode == "local":
        parts = [f"{steep_pct:.1f}% of area has steep overhangs ({max_overhang_deg:.0f}° max)"]
        if bridge_span > bridge_limit:
            parts.append(f"bridge span {bridge_span:.0f}mm > {bridge_limit:.0f}mm limit")
        msg = f"Localized supports recommended — {'; '.join(parts)}. Risk score: {risk_score}."
    else:
        parts = [f"{steep_pct:.1f}% overhang area ({max_overhang_deg:.0f}° max)"]
        if bridge_span > bridge_limit:
            parts.append(f"bridge span {bridge_span:.0f}mm")
        msg = f"Full supports needed — {'; '.join(parts)}. Risk score: {risk_score}."

    return {
        "supports_recommended": supports_recommended,
        "support_mode": support_mode,
        "risk_score": risk_score,
        "reason_codes": reason_codes,
        "user_message": msg,
        "stats": {
            "overhang_face_pct":      round(steep_pct, 2),
            "max_overhang_angle_deg": round(max_overhang_deg, 1),
            "bridge_span_mm":         round(bridge_span, 1),
            "total_faces":            int(len(mesh.faces)),
        },
    }

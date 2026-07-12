# TASK-062 — Djinn Engraving Specialist Sub-Agent
**Assigned to:** Marcus  
**Status:** done  
**Completed:** 2026-06-02  
**Priority:** high  
**Related:** Djinn project, Typhon's Forge, functional object manufacturing  
**Scope:** Full design specification for a geometry-aware, language-driven engraving placement AI integrated into the Djinn pipeline.

---

## What This Agent Is

This is not a slicer plugin. This is not a CAD tool.

This is a **reasoning specialist** — a Djinn sub-agent whose only job is to answer the question:

> *"Given this 3D object, what does the user want to engrave, where can it physically go, what are the constraints, and what are the best options ranked by quality?"*

It reads geometry (STL/OBJ/3MF), understands human language placement intent ("put it on the front," "engrave the base," "add the logo near the top"), knows the hard math and machine limits for FDM engraving, and returns structured placement proposals the user can approve before any modification to the model or gcode happens.

**This agent never touches the model without approval.** It proposes. The human decides.

---

## Table of Contents

1. [The Core Problem It Solves](#1-the-core-problem-it-solves)
2. [Agent Architecture Overview](#2-agent-architecture-overview)
3. [Input Layer: Reading the Mesh](#3-input-layer-reading-the-mesh)
4. [Input Layer: Natural Language Intent Parsing](#4-input-layer-natural-language-intent-parsing)
5. [Geometry Analysis: Surface Classification](#5-geometry-analysis-surface-classification)
6. [Machine Constraints: The Math](#6-machine-constraints-the-math)
7. [Placement Scoring: How Proposals Are Ranked](#7-placement-scoring-how-proposals-are-ranked)
8. [Proposal Output Format](#8-proposal-output-format)
9. [Workaround Strategies for Impossible Requests](#9-workaround-strategies-for-impossible-requests)
10. [Python Implementation](#10-python-implementation)
11. [System Prompt for the LLM Core](#11-system-prompt-for-the-llm-core)
12. [Integration with Djinn Pipeline](#12-integration-with-djinn-pipeline)
13. [Machine Profiles](#13-machine-profiles)
14. [Edge Cases and Hard Limits](#14-edge-cases-and-hard-limits)
15. [Testing Strategy](#15-testing-strategy)

---

## 1. The Core Problem It Solves

When you want to engrave something onto a 3D-printed object, the problems are layered:

**Problem 1 — Geometry blindness.** You look at an STL in a slicer, you see a shape. You don't see the normals, the curvature, which faces are printable, which faces are vertical walls, which zones will cause the engraving to disappear into layer lines.

**Problem 2 — Language is vague.** "Put it on the bottom" means the base face to one person and the lowest-Z non-support surface to another. "On the side" could be any of four walls. The agent must resolve ambiguity by asking one clarifying question, not five.

**Problem 3 — Machine limits are invisible.** FDM engraving (debossed/embossed) has hard minimums: 0.5mm minimum engraved depth for FDM, minimum letter width ~0.4mm (one nozzle width), minimum font size ~14pt at standard scale. Text smaller than these limits will either not print or will be illegible. The user doesn't know any of this.

**Problem 4 — Layer orientation matters.** A face that's at 45° to the print bed will have diagonal layer lines cutting across the engraving. A face that's parallel to the XY plane (top or bottom) will have clean horizontal layer lines that either enhance or are invisible in the engraving. The agent must know the difference.

**Problem 5 — Support interaction.** Engraved text on an overhanging face requires support — and support removal will tear the text. The agent knows this and flags it, or proposes reorientation.

---

## 2. Agent Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │         USER REQUEST                │
                    │  STL file path + natural language   │
                    │  "engrave 'DJINN' on the front face"│
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │      GEOMETRY READER                │
                    │  trimesh: load mesh, get normals,   │
                    │  classify surfaces, find planar     │
                    │  regions, measure areas             │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │      INTENT PARSER (LLM)            │
                    │  Resolve: what text? what surface?  │
                    │  Approximate size? Priority (fit    │
                    │  vs. legibility vs. aesthetics)?    │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │    SURFACE CLASSIFIER               │
                    │  Score each candidate surface:      │
                    │  normal alignment, area, curvature, │
                    │  layer line orientation, overhang   │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │    CONSTRAINT ENGINE                │
                    │  Apply machine limits to each       │
                    │  candidate: min depth, min width,   │
                    │  font size check, wall thickness    │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │    WORKAROUND PLANNER               │
                    │  If constraint fails: resize,       │
                    │  reorient, split text, use emboss   │
                    │  instead of deboss, suggest SLA     │
                    └──────────────┬──────────────────────┘
                                   │
                    ┌──────────────▼──────────────────────┐
                    │    PROPOSAL GENERATOR               │
                    │  3 ranked proposals: Best, Alt,     │
                    │  Workaround. Each with coordinates, │
                    │  constraints satisfied, warnings    │
                    └─────────────────────────────────────┘
```

---

## 3. Input Layer: Reading the Mesh

### Supported Formats
- STL (binary and ASCII) — primary format for Djinn objects
- OBJ — secondary
- 3MF — from PrusaSlicer and Bambu exports
- STEP/IGES — via `cadquery` or `opencascade-python` if needed (rare)

### Core Mesh Loading
```python
# djinn/engraving/mesh_reader.py
import trimesh
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class MeshInfo:
    mesh: trimesh.Trimesh
    file_path: Path
    bounding_box: np.ndarray          # [[xmin,ymin,zmin],[xmax,ymax,zmax]]
    dimensions: np.ndarray            # [x_size, y_size, z_size] in mm
    volume: float                     # mm³
    surface_area: float               # mm²
    is_watertight: bool
    face_count: int
    vertex_count: int
    center_mass: np.ndarray           # [x, y, z]
    face_normals: np.ndarray          # (N, 3) unit vectors
    face_areas: np.ndarray            # (N,) in mm²
    faces: np.ndarray                 # (N, 3) vertex indices
    vertices: np.ndarray              # (M, 3) coordinates


def load_mesh(file_path: str | Path) -> MeshInfo:
    """
    Load a mesh file and extract all geometric properties needed by
    the engraving specialist.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Mesh file not found: {path}")

    mesh = trimesh.load_mesh(str(path))

    # Handle scenes (multi-body files)
    if isinstance(mesh, trimesh.Scene):
        # Merge all geometries into single mesh
        meshes = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(meshes)

    # Repair if needed
    if not mesh.is_watertight:
        trimesh.repair.fix_normals(mesh)
        trimesh.repair.fix_winding(mesh)
        trimesh.repair.fill_holes(mesh)

    bounds = mesh.bounds
    dimensions = bounds[1] - bounds[0]

    return MeshInfo(
        mesh=mesh,
        file_path=path,
        bounding_box=bounds,
        dimensions=dimensions,
        volume=float(mesh.volume),
        surface_area=float(mesh.area),
        is_watertight=mesh.is_watertight,
        face_count=len(mesh.faces),
        vertex_count=len(mesh.vertices),
        center_mass=mesh.center_mass,
        face_normals=mesh.face_normals,
        face_areas=mesh.area_faces,
        faces=mesh.faces,
        vertices=mesh.vertices,
    )
```

### Mesh Summary for LLM Context
```python
def mesh_to_text_summary(info: MeshInfo) -> str:
    """
    Convert mesh geometry into a text description the LLM can reason about.
    This is injected into the agent's context alongside the user's request.
    """
    x, y, z = info.dimensions
    return f"""OBJECT GEOMETRY SUMMARY:
- File: {info.file_path.name}
- Dimensions: {x:.2f}mm × {y:.2f}mm × {z:.2f}mm (X × Y × Z)
- Volume: {info.volume:.1f} mm³
- Surface area: {info.surface_area:.1f} mm²
- Watertight: {info.is_watertight}
- Face count: {info.face_count:,}
- Bounding box center: ({info.center_mass[0]:.1f}, {info.center_mass[1]:.1f}, {info.center_mass[2]:.1f}) mm

CLASSIFIED SURFACES:
{_format_surface_list(info)}
"""


def _format_surface_list(info: MeshInfo) -> str:
    """Surfaces are classified before this is called — see Section 5."""
    # Filled in after surface classification runs
    pass
```

---

## 4. Input Layer: Natural Language Intent Parsing

### What the Agent Needs to Extract from Human Language

The user says something. The agent must extract a structured **engraving intent**:

| Field | What it means | Examples |
|-------|---------------|----------|
| `content` | What to engrave | "DJINN", a logo SVG path, "S6_E14", "Made by Javier" |
| `content_type` | Text, logo, pattern, symbol | `text`, `svg`, `pattern`, `glyph` |
| `surface_hint` | Where user wants it | "front", "bottom", "base", "side", "top", "near the logo", "on the flat part" |
| `size_hint` | How big | "small", "as big as possible", "5mm tall", "fill the face" |
| `depth_hint` | Deboss (cut in) or emboss (raised) | "carved in", "raised", "engraved", "stamped" |
| `priority` | What matters most | "legibility", "fit", "doesn't matter if it's small", "must be readable" |
| `font_hint` | Optional font preference | "bold", "sans-serif", "same as on the lid" |

### Intent Extraction Prompt
```python
INTENT_EXTRACTION_PROMPT = """
You are extracting engraving placement intent from a user message.

Return ONLY valid JSON with these fields:
{
  "content": "<exact text or description of what to engrave>",
  "content_type": "text" | "logo" | "pattern" | "glyph",
  "surface_hint": "<user's words for where they want it, verbatim>",
  "surface_direction": "top" | "bottom" | "front" | "back" | "left" | "right" | "any" | "unknown",
  "size_hint": "<user's words about size, or 'unspecified'>",
  "target_height_mm": <number or null>,
  "depth_type": "deboss" | "emboss" | "unspecified",
  "priority": "legibility" | "fit" | "aesthetics" | "unspecified",
  "font_hint": "<any font preference mentioned, or null>",
  "ambiguous": true | false,
  "clarification_needed": "<single question to ask if ambiguous, or null>"
}

User message: "{user_message}"
"""
```

### Ambiguity Resolution
If `ambiguous: true`, the agent **asks exactly one question** before proceeding. It never asks two questions in one response. If the user's answer is "I don't care" or "whatever works," the agent picks the best option autonomously and notes it.

**Ambiguity examples and resolution:**

| User says | Ambiguity | Agent asks |
|-----------|-----------|------------|
| "put it on the side" | Which side? Object is symmetric | "Left side or right side — or does it not matter?" |
| "engrave the logo" | No logo file provided | "Do you have an SVG? Or should I place a text placeholder for now?" |
| "make it big" | Big relative to what? | "Should the text fill the entire face, or leave a margin?" |
| "near the bottom" | How near? On the actual base? | "Do you mean ON the bottom face (floor), or on the side wall near the bottom edge?" |

---

## 5. Geometry Analysis: Surface Classification

### What "Surface Classification" Means

The mesh is made of thousands of triangles. The agent must group them into **human-meaningful regions** and score each for engraving suitability.

A surface is **engravable** if it satisfies:
1. The face normal points within 45° of a printable direction (not sideways overhang)
2. The face is large enough to contain the engraving
3. The curvature radius in the engraving zone is large enough (very tight curves distort text)
4. The zone does not conflict with critical geometry (bolt holes, mating surfaces)

### Surface Classification Pipeline

```python
# djinn/engraving/surface_classifier.py
import numpy as np
import trimesh
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class SurfaceType(Enum):
    FLAT_TOP = "flat_top"           # Normal ≈ +Z, face-up
    FLAT_BOTTOM = "flat_bottom"     # Normal ≈ -Z, face-down (base)
    FLAT_SIDE = "flat_side"         # Normal ≈ ±X or ±Y, vertical wall
    CURVED_CONVEX = "curved_convex" # Convex curve, can engrave with care
    CURVED_CONCAVE = "curved_concave"  # Concave — engraving risky
    STEEP_OVERHANG = "steep_overhang"  # >45° overhang — cannot engrave
    COMPLEX = "complex"             # Cannot classify reliably


@dataclass
class SurfaceRegion:
    """A coherent planar or near-planar region on the mesh."""
    region_id: int
    surface_type: SurfaceType
    centroid: np.ndarray            # [x, y, z] center of region in mm
    normal: np.ndarray              # Average unit normal [nx, ny, nz]
    area: float                     # mm²
    face_indices: np.ndarray        # Which mesh faces belong to this region
    bounding_rect: dict             # {"width_mm": float, "height_mm": float}
    overhang_angle_deg: float       # 0 = flat top, 90 = vertical, >90 = overhang
    curvature_radius: Optional[float]  # mm, None if flat
    engravable: bool
    engravability_score: float      # 0.0 – 1.0
    reasons: list[str]              # Explanations for score
    label: str                      # Human-readable: "Top face", "Front wall", etc.


def classify_surfaces(mesh: trimesh.Trimesh) -> list[SurfaceRegion]:
    """
    Segment mesh into planar/near-planar regions and score each
    for engraving suitability.
    
    Strategy:
    1. Group faces by normal similarity (within 15° tolerance)
    2. For each group, compute region properties
    3. Score each region
    """
    regions = []
    face_normals = mesh.face_normals  # (N, 3)
    face_areas = mesh.area_faces       # (N,)

    # --- Group faces by normal direction ---
    # Use a tolerance of cos(15°) ≈ 0.966
    NORMAL_TOLERANCE = 0.966
    unassigned = set(range(len(face_normals)))
    region_id = 0

    while unassigned:
        # Seed with the largest unassigned face
        seed = max(unassigned, key=lambda i: face_areas[i])
        seed_normal = face_normals[seed]

        # Find all faces with similar normal
        dots = face_normals @ seed_normal  # (N,) dot products
        similar = np.where(dots >= NORMAL_TOLERANCE)[0]
        similar_set = set(similar.tolist()) & unassigned

        if len(similar_set) < 3:
            # Too few faces — mark as complex
            unassigned -= similar_set
            continue

        face_idx = np.array(list(similar_set))
        region_faces = face_idx

        # Compute region properties
        region_vertices = mesh.vertices[mesh.faces[region_faces].flatten()]
        centroid = region_vertices.mean(axis=0)
        avg_normal = face_normals[region_faces].mean(axis=0)
        avg_normal /= np.linalg.norm(avg_normal)
        total_area = face_areas[region_faces].sum()

        # Overhang angle: angle between normal and +Z
        up = np.array([0, 0, 1])
        cos_angle = np.dot(avg_normal, up)
        overhang_deg = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))

        # Classify surface type
        surface_type = _classify_normal_to_type(avg_normal, overhang_deg)

        # Bounding rectangle in the plane of the region
        rect = _compute_bounding_rect(region_vertices, avg_normal)

        # Curvature: for now, 0 (flat). Curved surfaces need discrete mean curvature.
        # TODO: implement mean curvature via cotangent weights for curved parts.
        curvature_radius = None  # flat assumption for v1

        # Score and label
        score, reasons = _score_region(
            surface_type, total_area, overhang_deg, rect, curvature_radius
        )
        label = _generate_label(surface_type, centroid, mesh.bounds, region_id)
        engravable = score >= 0.3

        regions.append(SurfaceRegion(
            region_id=region_id,
            surface_type=surface_type,
            centroid=centroid,
            normal=avg_normal,
            area=total_area,
            face_indices=region_faces,
            bounding_rect=rect,
            overhang_angle_deg=overhang_deg,
            curvature_radius=curvature_radius,
            engravable=engravable,
            engravability_score=score,
            reasons=reasons,
            label=label,
        ))

        unassigned -= similar_set
        region_id += 1

    # Sort by score descending
    regions.sort(key=lambda r: r.engravability_score, reverse=True)
    return regions


def _classify_normal_to_type(normal: np.ndarray, overhang_deg: float) -> SurfaceType:
    """Classify a unit normal into a surface type."""
    if overhang_deg > 135:
        return SurfaceType.STEEP_OVERHANG  # Pointing mostly downward
    elif overhang_deg < 20:
        return SurfaceType.FLAT_TOP         # Pointing mostly upward
    elif overhang_deg > 80 and overhang_deg < 100:
        return SurfaceType.FLAT_SIDE        # Pointing horizontally
    elif 160 < overhang_deg <= 180:
        return SurfaceType.FLAT_BOTTOM      # Pointing straight down (base)
    else:
        return SurfaceType.COMPLEX


def _score_region(
    surface_type: SurfaceType,
    area: float,
    overhang_deg: float,
    rect: dict,
    curvature_radius: Optional[float],
) -> tuple[float, list[str]]:
    """
    Score a surface region for engraving suitability.
    Returns (score 0.0-1.0, list of reason strings).
    """
    score = 0.0
    reasons = []
    MIN_AREA = 25.0  # mm² — minimum for any useful engraving (5mm × 5mm)

    # Base score from surface type
    type_scores = {
        SurfaceType.FLAT_TOP: 1.0,
        SurfaceType.FLAT_SIDE: 0.75,
        SurfaceType.FLAT_BOTTOM: 0.6,   # Usable but on the base — hidden in use
        SurfaceType.CURVED_CONVEX: 0.45,
        SurfaceType.CURVED_CONCAVE: 0.2,
        SurfaceType.STEEP_OVERHANG: 0.0,
        SurfaceType.COMPLEX: 0.1,
    }
    score = type_scores.get(surface_type, 0.0)

    if surface_type == SurfaceType.STEEP_OVERHANG:
        reasons.append("BLOCKED: Overhang >45° — engraving here requires support removal which will damage text")
        return 0.0, reasons

    if surface_type == SurfaceType.FLAT_TOP:
        reasons.append("Excellent: flat horizontal surface, clean layer lines")
    elif surface_type == SurfaceType.FLAT_SIDE:
        reasons.append("Good: vertical wall — layer lines run horizontally through text")
    elif surface_type == SurfaceType.FLAT_BOTTOM:
        reasons.append("Fair: base face — functional but text will not be visible in normal orientation")
    elif surface_type in (SurfaceType.CURVED_CONVEX, SurfaceType.CURVED_CONCAVE):
        reasons.append("Curved surface — text may be distorted, especially at edges")

    # Area check
    if area < MIN_AREA:
        score *= 0.2
        reasons.append(f"WARNING: Region area {area:.1f}mm² is very small (min recommended: {MIN_AREA}mm²)")
    elif area < 100:
        score *= 0.7
        reasons.append(f"Small region ({area:.1f}mm²) — text will need to be small")
    else:
        reasons.append(f"Good area ({area:.1f}mm²) — can accommodate reasonable text size")

    # Minimum bounding dimension check
    min_dim = min(rect["width_mm"], rect["height_mm"])
    if min_dim < 3.0:
        score *= 0.4
        reasons.append(f"WARNING: Narrow region ({min_dim:.1f}mm shortest dimension) — text height will be very limited")
    
    return round(score, 3), reasons


def _compute_bounding_rect(vertices: np.ndarray, normal: np.ndarray) -> dict:
    """Project vertices onto a plane perpendicular to normal, compute bounding box."""
    # Create orthonormal basis in the plane
    if abs(normal[2]) < 0.9:
        up = np.array([0, 0, 1])
    else:
        up = np.array([1, 0, 0])
    
    u = np.cross(normal, up)
    u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    v /= np.linalg.norm(v)
    
    # Project vertices
    proj_u = vertices @ u
    proj_v = vertices @ v
    
    width = float(proj_u.max() - proj_u.min())
    height = float(proj_v.max() - proj_v.min())
    
    return {"width_mm": round(width, 2), "height_mm": round(height, 2)}


def _generate_label(
    surface_type: SurfaceType,
    centroid: np.ndarray,
    bounds: np.ndarray,
    region_id: int,
) -> str:
    """Generate a human-readable name for a surface region."""
    size = bounds[1] - bounds[0]
    cx, cy, cz = centroid
    ox, oy, oz = bounds[0]
    
    rel_x = (cx - ox) / size[0] if size[0] > 0 else 0.5
    rel_y = (cy - oy) / size[1] if size[1] > 0 else 0.5
    rel_z = (cz - oz) / size[2] if size[2] > 0 else 0.5
    
    if surface_type == SurfaceType.FLAT_TOP:
        return f"Top face"
    elif surface_type == SurfaceType.FLAT_BOTTOM:
        return f"Bottom (base)"
    elif surface_type == SurfaceType.FLAT_SIDE:
        if rel_z > 0.6:
            zone = "upper"
        elif rel_z < 0.4:
            zone = "lower"
        else:
            zone = "mid"
        if rel_x < 0.2:
            return f"Left wall ({zone})"
        elif rel_x > 0.8:
            return f"Right wall ({zone})"
        elif rel_y < 0.2:
            return f"Front wall ({zone})"
        elif rel_y > 0.8:
            return f"Back wall ({zone})"
        else:
            return f"Side wall {region_id} ({zone})"
    elif surface_type == SurfaceType.CURVED_CONVEX:
        return f"Curved convex surface {region_id}"
    else:
        return f"Surface region {region_id}"
```

---

## 6. Machine Constraints: The Math

### FDM Engraving Hard Limits

These are non-negotiable. If the proposal violates them, the agent **must** warn and offer a workaround — it never silently produces a proposal that will fail to print.

| Constraint | Value | Source | Notes |
|------------|-------|---------|-------|
| Min engraved depth (FDM) | **0.5mm** | HLH Rapid / Formlabs design guidelines | Less than this prints but is invisible / fills with surface texture |
| Min embossed height (FDM) | **0.3mm** | HLH Rapid design guidelines | Embossed features shorter than this will not survive support removal |
| Min feature width (FDM, 0.4mm nozzle) | **0.4mm** | One nozzle width = minimum wall thickness | Narrower strokes won't extrude |
| Min letter height (FDM) | **~3mm** | Practical limit at 0.4mm nozzle (serif fonts need 5mm+) | Below 3mm, letters merge |
| Min font size | **14pt at standard scale** | HLH Rapid, Sculpteo guidelines | Corresponds to ~5mm cap height |
| Recommended engraved depth | **0.5–1.0mm** | BigRep / Formlabs | 0.5mm minimum, 1.0mm for clear readability |
| Max embossed height (no support) | **0.4–0.8mm** | Prusa forum empirical | Beyond this, supports required on vertical faces |
| Layer height range (FDM, 0.4mm nozzle) | **0.1–0.32mm** | BigRep, Sloyd.ai | 0.2mm standard; 0.1mm for fine detail |
| XY resolution (real-world tolerance) | **±0.1–0.2mm** | BigRep resolution guide | Design for ±0.2mm worst case |
| Optimal layer height for engraving | **0.1mm** | Layer height research | Maximizes vertical resolution of engraved features |

### The Minimum Viable Engraving Calculation

For a text string to be engravable on FDM, given:
- Target text height: `H` mm  
- Nozzle diameter: `d` mm (default 0.4mm)
- Layer height: `lh` mm (default 0.2mm, recommended 0.1mm for engraving)
- Engraved depth: `depth` mm (minimum 0.5mm)

The text is **printable** if:
- `H ≥ 3 × d` (minimum 3 nozzle widths per letter height) → `H ≥ 1.2mm` absolute minimum, `H ≥ 5mm` recommended
- `depth ≥ 0.5mm` (always)
- `depth / lh ≥ 2` (at least 2 layers deep for structural definition)
- Stroke width of thinnest character stroke `≥ d` (1 nozzle width minimum)

```python
# djinn/engraving/constraint_engine.py
from dataclasses import dataclass


@dataclass
class MachineProfile:
    name: str
    nozzle_diameter_mm: float
    min_layer_height_mm: float
    std_layer_height_mm: float
    max_layer_height_mm: float
    xy_tolerance_mm: float
    min_wall_thickness_mm: float


@dataclass
class EngravingConstraints:
    min_depth_mm: float = 0.5
    max_depth_mm: float = 2.0
    min_emboss_height_mm: float = 0.3
    max_emboss_no_support_mm: float = 0.8
    min_letter_height_mm: float = 3.0
    recommended_letter_height_mm: float = 5.0
    min_stroke_width_mm: float = None   # Set from machine profile
    recommended_layer_height_mm: float = 0.1


@dataclass
class ConstraintCheckResult:
    passes: bool
    warnings: list[str]
    errors: list[str]
    adjusted_params: dict   # Suggested parameter adjustments to make it pass


def check_engraving_constraints(
    text: str,
    text_height_mm: float,
    depth_mm: float,
    depth_type: str,  # "deboss" or "emboss"
    machine: MachineProfile,
    surface_area_mm2: float,
    surface_width_mm: float,
    surface_height_mm: float,
) -> ConstraintCheckResult:
    """
    Check if the requested engraving is within machine limits.
    Returns result with pass/fail, warnings, errors, and suggestions.
    """
    constraints = EngravingConstraints(
        min_stroke_width_mm=machine.nozzle_diameter_mm,
    )
    
    errors = []
    warnings = []
    adjusted = {}
    
    # --- Depth checks ---
    if depth_type == "deboss":
        if depth_mm < constraints.min_depth_mm:
            errors.append(
                f"Engraved depth {depth_mm:.2f}mm is below FDM minimum ({constraints.min_depth_mm}mm). "
                f"Text will not be visible — it will fill with surface texture."
            )
            adjusted["depth_mm"] = constraints.min_depth_mm
        
        if depth_mm > constraints.max_depth_mm:
            warnings.append(
                f"Engraved depth {depth_mm:.2f}mm is quite deep — may weaken part if walls are thin."
            )
        
        # Layer resolution check
        layers = depth_mm / machine.std_layer_height_mm
        if layers < 2:
            warnings.append(
                f"Depth {depth_mm:.2f}mm = {layers:.1f} layers at standard {machine.std_layer_height_mm}mm height. "
                f"Use layer height {constraints.recommended_layer_height_mm}mm for better definition."
            )
            adjusted["layer_height_mm"] = constraints.recommended_layer_height_mm
    
    elif depth_type == "emboss":
        if depth_mm < constraints.min_emboss_height_mm:
            errors.append(
                f"Embossed height {depth_mm:.2f}mm is below FDM minimum ({constraints.min_emboss_height_mm}mm)."
            )
            adjusted["depth_mm"] = constraints.min_emboss_height_mm
        
        if depth_mm > constraints.max_emboss_no_support_mm:
            warnings.append(
                f"Embossed height {depth_mm:.2f}mm exceeds no-support threshold "
                f"({constraints.max_emboss_no_support_mm}mm). Supports will be required on non-top surfaces."
            )
    
    # --- Letter height checks ---
    if text_height_mm < constraints.min_letter_height_mm:
        errors.append(
            f"Text height {text_height_mm:.1f}mm is below minimum ({constraints.min_letter_height_mm}mm). "
            f"Characters will merge and be unreadable."
        )
        adjusted["text_height_mm"] = constraints.min_letter_height_mm
    elif text_height_mm < constraints.recommended_letter_height_mm:
        warnings.append(
            f"Text height {text_height_mm:.1f}mm is functional but tight. "
            f"Recommended minimum is {constraints.recommended_letter_height_mm}mm for clear readability. "
            f"Use a bold, sans-serif font (Arial, Helvetica) at this size."
        )
    
    # --- Fit check ---
    # Estimate text width: average character width ≈ 0.6× height for sans-serif
    char_count = len(text)
    est_text_width_mm = char_count * text_height_mm * 0.6
    MARGIN = 2.0  # mm margin on each side
    
    if est_text_width_mm > surface_width_mm - (2 * MARGIN):
        if est_text_width_mm > surface_width_mm:
            errors.append(
                f"Text '{text}' at {text_height_mm:.1f}mm height estimates {est_text_width_mm:.1f}mm wide, "
                f"but surface is only {surface_width_mm:.1f}mm wide. Text will not fit."
            )
            # Suggest fitting height
            max_char_width = (surface_width_mm - 2 * MARGIN) / char_count
            suggested_height = max_char_width / 0.6
            adjusted["text_height_mm"] = round(max(suggested_height, constraints.min_letter_height_mm), 1)
            adjusted["fit_strategy"] = "shrink_to_fit"
        else:
            warnings.append(
                f"Text is close to surface edge — margin will be only "
                f"{(surface_width_mm - est_text_width_mm) / 2:.1f}mm each side."
            )
    
    passes = len(errors) == 0
    return ConstraintCheckResult(
        passes=passes,
        warnings=warnings,
        errors=errors,
        adjusted_params=adjusted,
    )
```

---

## 7. Placement Scoring: How Proposals Are Ranked

Each candidate surface × placement combination gets a composite score:

```
composite_score = (
    surface_engravability_score  × 0.35   # Is this a good surface type?
    + normal_alignment_score     × 0.25   # Does the user's direction request match?
    + area_fit_score             × 0.20   # Is there enough room?
    + constraint_pass_score      × 0.20   # Does it pass the machine limits?
)
```

### Surface-Normal Alignment Score

The user says "front." The agent maps "front" to a unit vector direction:

```python
DIRECTION_VECTORS = {
    "top":    np.array([0, 0, 1]),
    "bottom": np.array([0, 0, -1]),
    "front":  np.array([0, -1, 0]),  # Facing -Y in standard print orientation
    "back":   np.array([0, 1, 0]),
    "left":   np.array([-1, 0, 0]),
    "right":  np.array([1, 0, 0]),
}

def normal_alignment_score(surface_normal: np.ndarray, user_direction: str) -> float:
    """
    Score how well the surface normal matches the user's requested direction.
    Returns 0.0–1.0.
    """
    if user_direction not in DIRECTION_VECTORS:
        return 0.5  # No direction specified — neutral score
    
    target = DIRECTION_VECTORS[user_direction]
    dot = np.dot(surface_normal, target)
    # dot = 1.0: perfect alignment, dot = 0.0: perpendicular, dot = -1.0: opposite
    return float(np.clip((dot + 1) / 2, 0, 1))  # Remap [-1,1] → [0,1]
```

---

## 8. Proposal Output Format

The agent always returns exactly **3 proposals**: Best, Alternative, Workaround. If only one viable option exists, the others are "not viable" with explanation.

### Proposal Schema
```python
@dataclass
class EngravingProposal:
    rank: int                        # 1, 2, or 3
    label: str                       # "Best", "Alternative", "Workaround"
    surface: SurfaceRegion           # The target surface
    content: str                     # What is being engraved
    content_type: str                # text / svg / glyph
    depth_type: str                  # deboss / emboss
    depth_mm: float                  # Actual engraving depth
    text_height_mm: float            # Letter height
    placement_centroid: np.ndarray   # [x,y,z] center of engraving zone
    placement_normal: np.ndarray     # Normal vector of placement surface
    composite_score: float           # 0.0 – 1.0
    constraint_result: ConstraintCheckResult
    human_summary: str               # Plain English explanation
    modifications_needed: list[str]  # Changes required vs. original request
    slicer_notes: list[str]          # Layer height, wall settings, etc.
    viable: bool
```

### Human-Readable Proposal Output (What Javier Sees)

```
╔══════════════════════════════════════════════════════════════╗
║  ENGRAVING SPECIALIST — PLACEMENT PROPOSALS                 ║
║  Object: grip_cap_v3.stl  |  Text: "DJINN"                 ║
╚══════════════════════════════════════════════════════════════╝

📐 OBJECT: 45.2mm × 45.2mm × 22.0mm | FDM (0.4mm nozzle assumed)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PROPOSAL 1 — BEST (Score: 0.91)
Surface:    Top face
            40.8mm × 40.8mm | Normal: straight up (+Z)
Method:     DEBOSSED (engraved in)
Text size:  8mm tall letters, estimated 29mm wide (5 chars)
Depth:      0.6mm
Margins:    ~6mm on left/right, ~7mm top/bottom

WHY THIS WORKS:
  • Top face is horizontal — layer lines run perpendicular to text strokes
  • No overhang, no support interaction
  • Plenty of room (40.8 × 40.8mm for 29mm wide text)
  • 0.6mm depth = 3 layers at recommended 0.2mm height

SLICER SETTINGS:
  • Layer height: 0.1mm recommended (better depth definition)
  • Walls: 3+ perimeters to avoid text punching through
  • NO supports needed

MODIFICATIONS NEEDED: None — this is your original request, works as-is.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  PROPOSAL 2 — ALTERNATIVE (Score: 0.72)
Surface:    Front wall (mid)
            22.0mm tall × 45.2mm wide | Normal: facing -Y (front)
Method:     DEBOSSED
Text size:  6mm tall letters, estimated 22mm wide
Depth:      0.5mm
Margins:    ~11mm on left/right, ~8mm top/bottom

WHY THIS WORKS:
  • Front wall is visible in normal orientation
  • Vertical surface — layer lines are horizontal through the text
  • 22mm wide text fits comfortably in 45mm width

CAVEAT:
  • Vertical surfaces print with visible horizontal layer lines
  • Layer lines at 0.2mm will be visible in the grooves — use 0.1mm LH
  • Debossed text on vertical FDM surfaces requires clean first-layer calibration

SLICER SETTINGS:
  • Layer height: 0.1mm
  • Ironing: OFF on vertical surfaces
  • Print speed: reduce 20% for vertical engraving passes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 PROPOSAL 3 — WORKAROUND (Score: 0.41)
Surface:    Bottom (base)
            40.8mm × 40.8mm | Normal: facing -Z

Note: Text on base face is functional for serial numbers / IDs
but will not be visible when object is in use.

WORKAROUND FOR: If you want the text on the SIDE but the side
is too narrow — splitting "DJINN" across two adjacent walls:
  "DJI" on Front wall | "NN" on Right wall
  Readable when object is rotated. Non-standard but achievable.

SLICER SETTINGS:
  • Layer height: 0.2mm acceptable for base engrave
  • First layer: 0.2mm, squish +5% for base adhesion

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Reply with: 1 / 2 / 3 to proceed, EDIT to modify parameters, or EXPLAIN for more detail.
```

---

## 9. Workaround Strategies for Impossible Requests

When a request hits a hard limit, the agent does not fail — it proposes workarounds. Here is the full workaround tree:

### Problem → Workaround Map

| Problem | Workaround | How |
|---------|-----------|-----|
| Surface too small | Scale up text to max that fits, or shrink text to minimum viable | Auto-calculate max text height from surface bounding rect |
| Surface is overhang | Suggest model reorientation (rotate print 180°) | Show which face becomes top after reorientation |
| Text too long to fit in one row | Wrap to two lines | Calculate line breaks at natural word boundaries |
| Wall too thin for depth | Reduce depth to `wall_thickness / 3` | Maintain structural integrity — 3mm minimum wall rule |
| Curved surface (tight radius) | Option A: Engrave on flat adjacent face; Option B: Use only central flat zone of curve | Compute flat-zone bounds from curvature radius |
| Font strokes too thin | Recommend bold font, increase scale | Auto-suggest Bold Arial or Impact at calculated minimum size |
| Emboss too tall (needs support) | Switch to deboss (engraved-in) | Invert the feature: same visual result, no support |
| Vertical face with layer line interference | Rotate print orientation so the engraved face becomes the top | Show new print orientation, recalculate all surfaces |
| Text on organic/irregular surface | Project text onto the closest tangent plane of the surface; warn about edge distortion | Use surface normal at centroid as projection plane |
| Machine limits too restrictive for detail | Recommend SLA/resin printing for the engraved part; laser engraving on finished print | Note technology alternatives |

### Workaround Code Pattern

```python
def apply_workarounds(
    proposal: EngravingProposal,
    constraint_result: ConstraintCheckResult,
    mesh_info: MeshInfo,
    machine: MachineProfile,
) -> EngravingProposal:
    """
    Take a failing proposal and apply workarounds to make it viable.
    Modifies and returns the proposal in place.
    """
    adj = constraint_result.adjusted_params
    
    if "depth_mm" in adj:
        proposal.depth_mm = adj["depth_mm"]
        proposal.modifications_needed.append(
            f"Depth adjusted to {adj['depth_mm']}mm (from requested {proposal.depth_mm}mm)"
        )
    
    if "text_height_mm" in adj:
        old_h = proposal.text_height_mm
        proposal.text_height_mm = adj["text_height_mm"]
        proposal.modifications_needed.append(
            f"Text height adjusted to {adj['text_height_mm']}mm (from {old_h}mm) to fit surface"
        )
    
    if "layer_height_mm" in adj:
        proposal.slicer_notes.append(
            f"⚠️ Use layer height {adj['layer_height_mm']}mm (not standard 0.2mm) for this engraving"
        )
    
    if "fit_strategy" in adj and adj["fit_strategy"] == "shrink_to_fit":
        proposal.modifications_needed.append(
            f"Text scaled to fit surface. If smaller than {machine.nozzle_diameter_mm * 3}mm tall, "
            "consider abbreviating or using initials only."
        )
    
    # Re-run constraint check with adjusted params
    from djinn.engraving.constraint_engine import check_engraving_constraints
    recheck = check_engraving_constraints(
        text=proposal.content,
        text_height_mm=proposal.text_height_mm,
        depth_mm=proposal.depth_mm,
        depth_type=proposal.depth_type,
        machine=machine,
        surface_area_mm2=proposal.surface.area,
        surface_width_mm=proposal.surface.bounding_rect["width_mm"],
        surface_height_mm=proposal.surface.bounding_rect["height_mm"],
    )
    
    proposal.constraint_result = recheck
    proposal.viable = recheck.passes
    return proposal
```

---

## 10. Python Implementation

### Full Package Structure

```
djinn/engraving/
├── __init__.py
├── specialist.py       # Main entry point — EngravingSpecialist class
├── mesh_reader.py      # Section 3 code
├── intent_parser.py    # Section 4 code
├── surface_classifier.py # Section 5 code
├── constraint_engine.py  # Section 6 code
├── placement_scorer.py   # Section 7 code
├── proposal_generator.py # Section 8 code
├── workarounds.py        # Section 9 code
└── machines.py           # Section 13: machine profiles
```

### `specialist.py` — Main Entry Point

```python
# djinn/engraving/specialist.py
"""
Djinn Engraving Specialist Sub-Agent.
Entry point for all engraving placement decisions.
"""
from pathlib import Path
from openai import OpenAI
from rich.console import Console

from djinn.engraving.mesh_reader import load_mesh, mesh_to_text_summary
from djinn.engraving.intent_parser import parse_intent, EngravingIntent
from djinn.engraving.surface_classifier import classify_surfaces
from djinn.engraving.constraint_engine import check_engraving_constraints
from djinn.engraving.placement_scorer import score_placements
from djinn.engraving.proposal_generator import generate_proposals, format_proposals
from djinn.engraving.workarounds import apply_workarounds
from djinn.engraving.machines import get_machine_profile

console = Console()

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"


class EngravingSpecialist:
    """
    Djinn sub-agent for engraving placement decisions.
    
    Usage:
        specialist = EngravingSpecialist(machine="kessler")
        result = specialist.analyze(
            stl_path="grip_cap_v3.stl",
            user_request="engrave DJINN on the front face, small"
        )
        print(result.formatted_output)
        # User replies with "1"
        approved = specialist.approve(result, choice=1)
    """
    
    def __init__(self, machine: str = "fdm_04mm"):
        self.machine = get_machine_profile(machine)
        self.client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    
    def analyze(
        self,
        stl_path: str | Path,
        user_request: str,
        context: dict = None,
    ) -> "AnalysisResult":
        """
        Full analysis pipeline: load mesh → parse intent → classify surfaces
        → score placements → generate proposals.
        """
        console.print("[cyan]📐 Loading mesh...[/cyan]")
        mesh_info = load_mesh(stl_path)
        
        console.print("[cyan]🔍 Classifying surfaces...[/cyan]")
        surfaces = classify_surfaces(mesh_info.mesh)
        
        console.print("[cyan]🧠 Parsing intent...[/cyan]")
        intent = parse_intent(
            user_request=user_request,
            mesh_summary=mesh_to_text_summary(mesh_info),
            client=self.client,
        )
        
        if intent.ambiguous and intent.clarification_needed:
            return AnalysisResult(
                needs_clarification=True,
                clarification_question=intent.clarification_needed,
                mesh_info=mesh_info,
                surfaces=surfaces,
                intent=intent,
                proposals=[],
                formatted_output=f"\n❓ {intent.clarification_needed}\n",
            )
        
        console.print("[cyan]📊 Scoring placements...[/cyan]")
        scored_placements = score_placements(
            surfaces=surfaces,
            intent=intent,
            machine=self.machine,
        )
        
        console.print("[cyan]📝 Generating proposals...[/cyan]")
        proposals = generate_proposals(
            scored_placements=scored_placements,
            intent=intent,
            mesh_info=mesh_info,
            machine=self.machine,
        )
        
        # Apply workarounds to failing proposals
        for i, proposal in enumerate(proposals):
            if not proposal.viable:
                proposals[i] = apply_workarounds(
                    proposal, proposal.constraint_result, mesh_info, self.machine
                )
        
        formatted = format_proposals(proposals, mesh_info, intent)
        
        return AnalysisResult(
            needs_clarification=False,
            clarification_question=None,
            mesh_info=mesh_info,
            surfaces=surfaces,
            intent=intent,
            proposals=proposals,
            formatted_output=formatted,
        )
    
    def approve(self, result: "AnalysisResult", choice: int) -> dict:
        """
        User approves a proposal. Returns the approved spec ready for
        downstream processing (model modification, gcode annotation, etc.).
        """
        if choice < 1 or choice > len(result.proposals):
            raise ValueError(f"Invalid choice {choice}. Valid: 1-{len(result.proposals)}")
        
        proposal = result.proposals[choice - 1]
        if not proposal.viable:
            raise ValueError(f"Proposal {choice} is not viable even after workarounds.")
        
        return {
            "approved": True,
            "content": proposal.content,
            "content_type": proposal.content_type,
            "surface_label": proposal.surface.label,
            "surface_normal": proposal.surface.normal.tolist(),
            "placement_centroid": proposal.placement_centroid.tolist(),
            "depth_mm": proposal.depth_mm,
            "depth_type": proposal.depth_type,
            "text_height_mm": proposal.text_height_mm,
            "slicer_notes": proposal.slicer_notes,
            "modifications_needed": proposal.modifications_needed,
            "machine_profile": self.machine.name,
        }
```

---

## 11. System Prompt for the LLM Core

This prompt defines the LLM's behavior when it operates as the reasoning core of the engraving specialist. It is injected as the `system` message in every call.

```
You are Djinn's 3D Engraving Specialist sub-agent.

Your job is to help a designer decide where and how to engrave text, logos, or patterns
onto 3D-printed objects. You have been given:
1. A geometric summary of the object (dimensions, surfaces, normals, areas)
2. A classified list of surfaces with engravability scores
3. The user's request in natural language
4. The machine constraints for the target printer

YOU ARE A REASONING AGENT, NOT A SLICER.
You do not generate G-code. You do not modify files.
You produce structured placement proposals that a human reviews and approves.

YOUR EXPERTISE:
- FDM 3D printing geometry and layer-by-layer construction
- Surface normal analysis and what it means for engraving quality
- The mathematics of minimum feature sizes, depths, and tolerances
- When a request is impossible and what can be done instead
- Font selection and sizing for additive manufacturing

HARD RULES:
1. Never propose an engraving depth less than 0.5mm for FDM. Below this threshold,
   the engraving will be invisible — it fills with surface texture from extrusion.
2. Never propose text height below 3mm. Letters will merge and be unreadable.
   Recommend sans-serif fonts (Arial, Helvetica, Impact) for anything below 8mm.
3. Never propose engraving on an overhang surface (>45° from print bed normal)
   without explicitly warning about support requirement and removal damage.
4. Always use layer height 0.1mm in slicer notes for any engraving — it dramatically
   improves depth definition vs. standard 0.2mm.
5. If a request is impossible without modification, say so clearly, explain why
   in one sentence, and propose the closest viable alternative.

TONE:
- Technical but direct. Use numbers (mm, degrees, layers) not vague words.
- You speak to someone who builds things and understands tolerances.
- No hedging. If something won't work, say it won't work and say why.
- Proposals are confident recommendations, not suggestions.

RESPONSE FORMAT:
Always respond with the JSON structure requested by the calling function.
Never add explanation outside the JSON unless explicitly asked.
```

---

## 12. Integration with Djinn Pipeline

### CLI Command

```python
# In djinn/cli.py — add to the existing cli group:

@cli.command("engrave-analyze")
@click.argument("stl_path")
@click.argument("request")
@click.option("--machine", default="fdm_04mm",
              type=click.Choice(["fdm_04mm", "fdm_02mm", "sla", "kessler"]),
              help="Machine profile to use for constraints")
@click.option("--model", default="qwen2.5:14b", help="Ollama model for reasoning")
def engrave_analyze(stl_path, request, machine, model):
    """
    Analyze an STL for engraving placement.
    
    Example:
        djinn engrave-analyze grip_cap_v3.stl "engrave DJINN on the top face"
        djinn engrave-analyze lid.stl "put the logo on the front, small" --machine kessler
    """
    from djinn.engraving.specialist import EngravingSpecialist
    specialist = EngravingSpecialist(machine=machine)
    result = specialist.analyze(stl_path=stl_path, user_request=request)
    
    console.print(result.formatted_output)
    
    if result.needs_clarification:
        return
    
    choice = click.prompt("Select proposal (1/2/3) or SKIP", default="SKIP")
    if choice in ("1", "2", "3"):
        approved = specialist.approve(result, int(choice))
        console.print("\n[bold green]✓ Proposal approved[/bold green]")
        for note in approved["slicer_notes"]:
            console.print(f"  [yellow]⚙ {note}[/yellow]")
        for mod in approved["modifications_needed"]:
            console.print(f"  [cyan]→ {mod}[/cyan]")
        # Save approved spec
        spec_path = Path(stl_path).parent / "engraving_spec.json"
        import json
        spec_path.write_text(json.dumps(approved, indent=2))
        console.print(f"\n[green]Spec saved:[/green] {spec_path}")
```

### Marcus Integration (Telegram)

```
Marcus receives: stl_path + "engrave DJINN on top"
Marcus runs: EngravingSpecialist().analyze(...)
Marcus sends to Javier (Telegram):
  "📐 Engraving Specialist analyzed grip_cap_v3.stl

  ✅ OPTION 1 (Best): Top face — DJINN at 8mm, 0.6mm deep
  ⚠️ OPTION 2 (Alt): Front wall — DJINN at 6mm, needs 0.1mm layer height
  🔧 OPTION 3 (Fallback): Base face

  Reply 1 / 2 / 3 to approve."

Javier: "1"
Marcus: Saves engraving_spec.json, triggers model modifier if available.
```

---

## 13. Machine Profiles

```python
# djinn/engraving/machines.py
from djinn.engraving.constraint_engine import MachineProfile

MACHINE_PROFILES = {
    "fdm_04mm": MachineProfile(
        name="FDM Standard (0.4mm nozzle)",
        nozzle_diameter_mm=0.4,
        min_layer_height_mm=0.1,
        std_layer_height_mm=0.2,
        max_layer_height_mm=0.32,
        xy_tolerance_mm=0.2,
        min_wall_thickness_mm=0.4,
    ),
    "fdm_02mm": MachineProfile(
        name="FDM Fine Detail (0.2mm nozzle)",
        nozzle_diameter_mm=0.2,
        min_layer_height_mm=0.05,
        std_layer_height_mm=0.1,
        max_layer_height_mm=0.16,
        xy_tolerance_mm=0.1,
        min_wall_thickness_mm=0.2,
    ),
    "fdm_06mm": MachineProfile(
        name="FDM Large (0.6mm nozzle)",
        nozzle_diameter_mm=0.6,
        min_layer_height_mm=0.15,
        std_layer_height_mm=0.3,
        max_layer_height_mm=0.48,
        xy_tolerance_mm=0.25,
        min_wall_thickness_mm=0.6,
    ),
    "sla": MachineProfile(
        name="SLA/MSLA Resin",
        nozzle_diameter_mm=0.05,   # XY resolution approximated as pixel size
        min_layer_height_mm=0.025,
        std_layer_height_mm=0.05,
        max_layer_height_mm=0.1,
        xy_tolerance_mm=0.05,
        min_wall_thickness_mm=0.5,   # SLA has different min wall rule
    ),
    # Placeholder for Kessler machine specs
    # Update when confirmed: nozzle, build volume, controller
    "kessler": MachineProfile(
        name="Djinn Kessler (spec TBD)",
        nozzle_diameter_mm=0.4,     # UPDATE WHEN CONFIRMED
        min_layer_height_mm=0.1,    # UPDATE WHEN CONFIRMED
        std_layer_height_mm=0.2,
        max_layer_height_mm=0.32,
        xy_tolerance_mm=0.15,       # Tighter if CoreXY or belt mechanism
        min_wall_thickness_mm=0.4,
    ),
}

def get_machine_profile(name: str) -> MachineProfile:
    if name not in MACHINE_PROFILES:
        raise ValueError(
            f"Unknown machine profile '{name}'. Available: {list(MACHINE_PROFILES.keys())}"
        )
    return MACHINE_PROFILES[name]
```

---

## 14. Edge Cases and Hard Limits

### Cases the Agent Must Handle (Not Crash On)

| Situation | Behavior |
|-----------|----------|
| STL file is not watertight | Auto-repair with trimesh, warn user, proceed |
| Object is a single flat plane (e.g., a label or tile) | Classify correctly as one flat_top face; full area is engravable |
| Object is a cylinder (e.g., a cap, a cup) | Classify as curved_convex; propose using flat top/bottom, warn about curved walls |
| Object has no flat face larger than 25mm² | All proposals rank "workaround"; suggest reorientation or model redesign |
| User provides a logo SVG instead of text | Intent parser flags `content_type: "svg"`, specialist estimates bounding box from SVG dimensions and runs same constraint checks |
| User says "make it as big as possible" | Specialist fills 80% of the best surface, leaves 10% margin on each axis |
| User says "put it everywhere" | Specialist proposes top face only and explains that multi-face engraving requires separate STL modifications |
| Text is a single character (logo, initial) | Min width check is per-glyph; a single "D" at 5mm height is 3mm wide — passes |
| Mesh has 1M+ faces | Downsample to 50k faces for analysis only (trimesh `simplify_quadratic_decimation`); always work on original for output |
| User asks for engraving on a face that's actually an internal void | Ray casting from centroid detects interior — agent flags as "internal surface, not accessible" |
| Z-fighting / coincident faces | trimesh detects duplicates during repair; merged automatically |

### FDM Engraving Truth Table

| Depth | Layer Height | Nozzle | Result |
|-------|-------------|--------|--------|
| 0.2mm | 0.2mm | 0.4mm | **INVISIBLE** — same as surface roughness |
| 0.4mm | 0.2mm | 0.4mm | **MARGINAL** — barely visible, rough edges |
| 0.5mm | 0.1mm | 0.4mm | **MINIMUM VIABLE** — visible, clean edges |
| 0.5mm | 0.2mm | 0.4mm | **ACCEPTABLE** — visible but slightly rough |
| 1.0mm | 0.1mm | 0.4mm | **RECOMMENDED** — clear, sharp, deep |
| 1.0mm | 0.2mm | 0.4mm | **GOOD** — visible with slight layer texture |
| 2.0mm | 0.2mm | 0.4mm | **EXCELLENT** — strong visual, structural concern on thin walls |

---

## 15. Testing Strategy

### Unit Tests

```python
# tests/test_engraving_specialist.py

def test_flat_cube_top_face():
    """A simple cube — top face should score highest."""
    # Create a 50×50×20mm cube
    mesh = trimesh.creation.box([50, 50, 20])
    surfaces = classify_surfaces(mesh)
    top = next(s for s in surfaces if s.surface_type == SurfaceType.FLAT_TOP)
    assert top.engravability_score > 0.8

def test_minimum_depth_enforcement():
    """Requesting 0.2mm depth should fail constraint check."""
    machine = get_machine_profile("fdm_04mm")
    result = check_engraving_constraints(
        text="TEST", text_height_mm=8, depth_mm=0.2,
        depth_type="deboss", machine=machine,
        surface_area_mm2=400, surface_width_mm=20, surface_height_mm=20
    )
    assert not result.passes
    assert result.adjusted_params["depth_mm"] == 0.5

def test_overhang_rejection():
    """A face with normal pointing 120° from +Z is an overhang."""
    normal = np.array([0, np.sin(np.radians(120)), np.cos(np.radians(120))])
    overhang_deg = np.degrees(np.arccos(np.dot(normal, [0,0,1])))
    assert overhang_deg > 90
    score, reasons = _score_region(SurfaceType.STEEP_OVERHANG, 100, overhang_deg, {"width_mm":20,"height_mm":20}, None)
    assert score == 0.0

def test_text_too_long_workaround():
    """Text that won't fit on surface should get shrink-to-fit workaround."""
    machine = get_machine_profile("fdm_04mm")
    result = check_engraving_constraints(
        text="ABCDEFGHIJKLMNOP",   # 16 chars, very long
        text_height_mm=10,          # 10mm × 16 × 0.6 = 96mm estimated width
        depth_mm=0.5, depth_type="deboss", machine=machine,
        surface_area_mm2=400, surface_width_mm=30, surface_height_mm=15
    )
    assert not result.passes
    assert "fit_strategy" in result.adjusted_params

def test_intent_parser_direction_mapping():
    """'front face' should map to surface_direction 'front'."""
    intent = parse_intent(
        user_request="engrave DJINN on the front face",
        mesh_summary="...",
        client=mock_ollama_client({"surface_direction": "front"})
    )
    assert intent.surface_direction == "front"
```

### Integration Test (Full Pipeline)

```bash
# Test with a real STL file
djinn engrave-analyze tests/fixtures/grip_cap_50mm.stl \
  "engrave DJINN on top" \
  --machine fdm_04mm

# Expected output:
# - 3 proposals
# - Proposal 1 selects top face
# - Score > 0.8
# - No constraint errors
# - Slicer note: layer height 0.1mm
```

---

## Open Questions (Confirm Before Build)

1. **Kessler machine specs** — nozzle diameter, build volume, Z resolution, CoreXY vs. Cartesian. The "kessler" machine profile is a placeholder. Update `machines.py` once confirmed.
2. **Logo/SVG support** — Phase 1 handles text only. SVG bounding box analysis for logo placement is Phase 2. Confirm which phase this agent needs to be at for initial integration.
3. **Model modifier integration** — This agent produces `engraving_spec.json`. Phase 2 requires a downstream agent that takes the spec and actually modifies the STL (using `trimesh.boolean` or `OpenSCAD`). That is a separate TASK.
4. **Curved surface handling** — v1 treats all curves as "warn and workaround." Full curvature analysis (discrete mean curvature via cotangent weights) is in Phase 2.
5. **Font rendering** — The agent talks about fonts but doesn't render them. Actual glyph-to-geometry conversion requires `freetype-py` and a font file. This is needed only when the agent also becomes the model modifier.

---

*Researched and written by Marcus | 2026-06-02 | Task: TASK-062*  
*This is a Djinn sub-agent design specification and Python implementation blueprint.*  
*The agent reasons about geometry. It does not modify models. Human approval is required for all proposals.*

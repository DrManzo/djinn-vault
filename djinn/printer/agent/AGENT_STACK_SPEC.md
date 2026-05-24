# Djinn Printer — Multi-Agent Manufacturing Stack

**Status:** Spec approved 2026-05-24  
**Owner:** Javier / Claude  
**Next step:** Build unified orchestrator with shared project state and agent handoffs

---

## Agent Map

| Agent | Purpose |
|-------|---------|
| DesignGenAgent | Creates new designs from idea + constraints |
| DesignEditAgent | Modifies existing designs |
| ProtoOptAgent | Generates prototype-light and production-ready geometry variants |
| DOEPrintOptAgent | Optimizes slicer/process settings to minimize time, energy, and material |
| PlateNestAgent | Packs same or mixed models across one or more plates |
| FairPrintAgent | Prices the finished printable jobs |

Each agent owns a single step. The orchestrator routes between them and preserves shared project state.

---

## Unified Workflow

```
DesignGenAgent → DesignEditAgent → ProtoOptAgent → PlateNestAgent → FairPrintAgent
                                        ↕
                                 DOEPrintOptAgent
```

1. **DesignGenAgent** creates the initial model from description
2. **DesignEditAgent** updates the model as requirements change
3. **ProtoOptAgent** generates prototype-light and production variants
4. **DOEPrintOptAgent** finds the optimal slicer settings for the chosen variant
5. **PlateNestAgent** packs the final models onto plates
6. **FairPrintAgent** prices the printable jobs

---

## Orchestrator Entry Point

First question to user: **"new design, edit existing, optimize prototype, arrange plate, or price?"**

Then routes to the correct agent and preserves project state (dimensions, material, constraints, source file) across all steps.

---

## Agent Specs

### DesignGenAgent

Turns a text brief into a structured parametric design definition. Output is a feature plan first, then a CAD model — not just a dead STL, because editable geometry is required for downstream editing.

**Input:**
```json
{
  "request": "design a wall-mount bracket for a camera",
  "dimensions_mm": {"max_x": 120, "max_y": 80, "max_z": 60},
  "loads": {"static_kg": 1.5},
  "material": "PETG",
  "printer_type": "FDM",
  "requirements": ["2 screw holes", "cable clearance", "easy to print", "no supports preferred"]
}
```

**Output:**
```json
{
  "concept_summary": "L-bracket with gusseted rib, 2 countersunk wall holes, camera mounting plate, cable relief cutout",
  "parametric_features": ["..."],
  "printability_notes": ["..."],
  "cad_export_targets": ["STEP", "FCStd", "STL"]
}
```

**Approach:** Start from goals, materials, manufacturing method, and constraints → generate candidate geometry satisfying all of them. Parametric feature plan first, mesh second.

---

### DesignEditAgent

Modifies an existing CAD file or mesh. Does NOT rebuild from scratch. Real jobs are usually "move this hole," "thicken this wall," "add a fillet," "make this fit a larger insert."

**Supported edit types:**
- Feature edits: holes, bosses, ribs, slots, chamfers, fillets
- Dimensional edits: width, thickness, height, spacing, tolerance offsets
- Printability edits: flatten a face, reduce overhangs, split a part, add alignment pins
- Variant generation: prototype, production, reinforced

**System prompt:**
```
You are DesignEditAgent.
Your job is to modify an existing design while preserving its function unless the user says otherwise.
Prefer parametric edits when possible.
If the source is only a mesh, infer editable regions and propose a reconstruction plan before destructive edits.
Always report:
- what changed,
- what stayed the same,
- any printability or strength tradeoffs.
```

---

### ProtoOptAgent

Creates at least two geometry variants from one source:

| Mode | Goal |
|------|------|
| Prototype-light | Minimize print time and material while preserving external appearance and key interfaces |
| Production-ready | Meet load, safety, and printability requirements with stronger geometry and validated features |

**Prototype-light heuristics:**
- Hollow thick solids where appearance matters
- Reduce infill-driving internal mass
- Use thinner non-critical walls
- Remove decorative bulk
- Replace solid regions with sparse ribs or simple lattice where practical
- Preserve mating faces, hole locations, and outer silhouette

**Production heuristics:**
- Keep critical load paths
- Add fillets and gussets where stress concentrates
- Use topology optimization or lattice only when loads are defined
- Validate overhangs, print resolution, and build volume before release

**Uses:** topology optimization, lattice structures, DfAM checks (overhang, support risk, wall thickness, build volume).

---

### DOEPrintOptAgent

Runs structured experiment plans over slicer/process parameters to find optimal settings for prototype-fast, prototype-cheap, or balanced-quality. Uses DOE (Taguchi, RSM, Bayesian) instead of brute-force trial and error.

**Targets:** shorter print time, lower energy, lower material, minimum acceptable strength/surface for prototype.

**Factors (typical):**
- Layer height
- Print speed
- Infill density + type
- Shell/wall count
- Support settings
- Orientation
- Bed/nozzle temperature

**Research-backed baselines:**
- Lightning infill: -51% material consumption
- Reduced support line width: -31–32% polymer use
- Hot-end insulation (silicone sock): -30–34% energy
- Full enclosure: -15–18% average power (larger benefit on long prints)

**Input:**
```json
{
  "goal": "prototype_fast",
  "printer": {
    "model": "Ender 3",
    "has_enclosure": true,
    "hotend_sock": true,
    "bed_insulated": false
  },
  "material": {
    "type": "PLA",
    "prototype_only": true
  },
  "part": {
    "name": "display housing",
    "strength_requirement": "low",
    "surface_requirement": "medium",
    "supports_allowed": true
  },
  "factors": {
    "layer_height_mm": [0.2, 0.28, 0.36],
    "print_speed_mms": [40, 60, 80],
    "infill_density_pct": [5, 10, 20],
    "infill_type": ["lightning", "gyroid", "cubic"],
    "wall_count": [2, 3],
    "support_line_width_mm": [0.4, 0.6]
  },
  "responses": [
    "print_time_minutes",
    "energy_wh",
    "material_g",
    "surface_score",
    "prototype_pass"
  ],
  "constraints": {
    "minimum_surface_score": 6,
    "prototype_pass_required": true
  }
}
```

**Output:**
```json
{
  "recommended_profile": {
    "layer_height_mm": 0.32,
    "print_speed_mms": 70,
    "infill_density_pct": 8,
    "infill_type": "lightning",
    "wall_count": 2,
    "support_line_width_mm": 0.4
  },
  "expected_effect": {
    "time_reduction_pct": 38,
    "energy_reduction_pct": 24,
    "material_reduction_pct": 46
  },
  "machine_notes": [
    "Use enclosure for prints over 2 hours",
    "Use hot-end sock to reduce thermal loss"
  ],
  "confidence": "medium",
  "tradeoffs": [
    "Lower structural stiffness than production profile",
    "Best suited to visual or fit-check prototypes"
  ]
}
```

**System prompt:**
```
You are DOEPrintOptAgent, a design-of-experiments optimizer for 3D printing.

Your task is to minimize print time, energy use, and material use for prototype or production prints.

You must:
1. Select the most informative process factors and levels.
2. Propose an efficient DOE matrix rather than testing every combination.
3. Predict which settings best meet the stated objective.
4. Respect quality constraints such as minimum acceptable strength, finish, and dimensional stability.
5. Distinguish between prototype-only optimization and production-ready optimization.

Rules:
- For prototype-only jobs, prioritize time, energy, and material savings over maximum strength.
- Prefer DOE methods such as Taguchi for screening and RSM or Bayesian refinement for follow-up optimization.
- Recommend lightweight infill and reduced supports when the prototype is mainly visual or fit-check only.
- Explain tradeoffs clearly.
- Output a recommended setting, expected savings, and confidence level.
```

---

### PlateNestAgent

Packs same or mixed models across one or more plates. Already partially implemented (used to arrange mario pipe + 4 coins for Job #1).

**Key constraint:** Decimate high-poly STLs to <10MB per object before plate building. PrusaSlicer silently drops objects when combined plate exceeds ~200MB. Use pymeshlab: `ms.meshing_decimation_quadric_edge_collapse(targetfacenum=15000)`.

---

### FairPrintAgent

Already live as `djinn-print-quote`. See `commissions/PRICING_SPEC.md`.

Simple formula: `(material + time + design) / 0.60`  
Library auto-detect removes design cost for repeat prints.  
Full agent mode: weighted cost+market blend.

---

## Architecture Components

| Component | Role |
|-----------|------|
| Intent parser | Classifies request as new design / edit / optimize / plate / price |
| Geometry engine | CAD/mesh operations (OpenSCAD, FreeCAD, trimesh) |
| Constraint engine | Dimensions, tolerances, loads, material, printer constraints |
| Optimization engine | Lightweighting, topology optimization, lattice generation, printability checks |
| Manufacturing engine | DfAM checks: overhang, support risk, wall thickness, build volume |
| Output layer | Exports prototype and production variants plus notes |

---

## Implementation Plan

**Phase 1:** Build orchestrator shell with intent parser and routing  
**Phase 2:** Implement DesignGenAgent (OpenSCAD parametric generation from JSON brief)  
**Phase 3:** Implement DesignEditAgent (mesh inspection + parametric edit planning)  
**Phase 4:** Implement ProtoOptAgent (two-variant geometry output)  
**Phase 5:** Integrate DOEPrintOptAgent (slicer parameter matrix + Taguchi screening)  
**Phase 6:** Wire PlateNestAgent and FairPrintAgent into the shared project state

Shared project state object carries: source file path, dimensions, material, constraints, active variant, plate STL, and quote through every step.

---

*Spec recorded 2026-05-24 — Claude*

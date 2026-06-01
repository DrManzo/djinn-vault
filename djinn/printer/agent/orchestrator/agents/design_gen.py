"""
DesignGenAgent — creates a new parametric OpenSCAD design from a brief.
Output: concept JSON + .scad file. Parametric first, mesh second.
"""
import json, pathlib, re, subprocess
from ..llm import LLM
from ..project_state import ProjectState

MODELS_DIR = pathlib.Path.home() / "printer-files/models"

SYSTEM = """You are DesignGenAgent. You create parametric OpenSCAD designs for FDM 3D printing.

## Rules
- Every dimension is a named variable at the top — never embed magic numbers in geometry
- FDM-first: minimize overhangs, orient flat where possible, avoid unsupported bridges >15mm
- Wall thickness: min 1.2mm (3× nozzle), functional parts 2.4–4mm
- Hole clearance: +0.2mm loose fit, +0.1mm press fit
- Add fillets on stress-risers (r=1.5–3mm typical)
- $fn=64 for all circles
- Always include a bounding box check comment

## Output — reply with EXACTLY this structure, nothing else before or after:

```json
{
  "concept_summary": "one sentence",
  "key_features": ["feature 1", "feature 2"],
  "print_orientation": "flat|upright|angled",
  "supports_needed": false,
  "estimated_print_time_h": 2.0,
  "material_g_estimate": 30,
  "printability_notes": ["note 1"],
  "cad_export_targets": ["STL", "SCAD"]
}
```

```openscad
// ============================================================
// DESIGN PARAMETERS — edit these to resize the part
// ============================================================
// ... all variables here ...

// ============================================================
// GEOMETRY
// ============================================================
// ... modules and final render ...
```
"""


def run(state: ProjectState, llm: LLM) -> ProjectState:
    brief = state.brief
    user_msg = f"""Design brief:
{json.dumps(brief, indent=2)}

Generate the concept JSON and full parametric OpenSCAD file."""

    print(f"  [DesignGenAgent] via {llm.name} ...")
    reply = llm.chat(SYSTEM, [{"role": "user", "content": user_msg}], max_tokens=6000)

    # Parse blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
    scad_match = re.search(r'```openscad\s*(.*?)\s*```', reply, re.DOTALL)

    concept = {}
    if json_match:
        try:
            concept = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            concept = {"concept_summary": "generated", "raw": json_match.group(1)[:200]}

    scad_code = scad_match.group(1) if scad_match else reply

    # Save SCAD
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    piece = brief.get("piece_name", brief.get("request", "part"))
    safe = re.sub(r"[^a-z0-9_]", "_", piece.lower())[:36]
    scad_path = MODELS_DIR / f"job{state.id}_{safe}.scad"
    scad_path.write_text(scad_code)
    print(f"    → SCAD: {scad_path.name}")

    state.concept = concept
    state.source_scad = str(scad_path)
    state.status = "design_edit"
    state.note = concept.get("concept_summary", piece)
    state.supports_needed = concept.get("supports_needed", False)

    return state

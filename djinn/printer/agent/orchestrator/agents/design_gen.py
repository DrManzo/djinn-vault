"""
DesignGenAgent — creates a new parametric OpenSCAD design from a brief.
Output: concept JSON + .scad file. Parametric first, mesh second.
"""
import json, os, pathlib, re, subprocess
from ..llm import LLM
from ..project_state import ProjectState

MODELS_DIR = pathlib.Path.home() / "printer-files/models"
DESIGN_MODEL = "qwen2.5-coder:7b"

SYSTEM = """You are DesignGenAgent. You create parametric OpenSCAD designs for FDM 3D printing.

## Rules
- Every dimension is a named variable at the top — never embed magic numbers in geometry
- FDM-first: minimize overhangs, orient flat where possible, avoid unsupported bridges >15mm
- Wall thickness: min 1.2mm (3× nozzle), functional parts 2.4–4mm
- Hole clearance: +0.2mm loose fit, +0.1mm press fit
- $fn=64 for all circles
- Always include a bounding box check comment

## OpenSCAD built-in whitelist — ONLY these are valid without a module definition:
  cube(), cylinder(), sphere(), polyhedron()
  translate(), rotate(), scale(), mirror()
  linear_extrude(), rotate_extrude()
  union(), difference(), intersection()
  hull(), minkowski()
  for (i = [...]) { }
  let()
  if (...) { } else { }

NEVER call: box(), fillet_all(), hull_r(), round_all(), or ANY other name not in the list above unless you defined it as a module in the same file.

## Module definition rules — critical
- Modules are defined with the `module` keyword: `module my_name(params) { ... }`
- `my_name() { ... }` WITHOUT the `module` keyword is a CALL, not a definition
- Every module name you CALL must appear in a `module ...` definition earlier in the file
- Variables defined inside a module body are LOCAL — inaccessible from other modules
- All shared dimensions must be top-level variables, NOT inside a module body

## Self-check before outputting (do this mentally):
1. List every `module X()` definition in your file
2. For every call `X()` in the file, confirm X appears in step 1 OR is in the whitelist above
3. Any call not in steps 1 or 2 = undefined module → empty render = WRONG
4. Confirm all variables referenced in a module were declared at the top level

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
// DESIGN PARAMETERS — all dimensions as top-level variables
// ============================================================
// ... variables here — never inside a module ...

// ============================================================
// GEOMETRY
// ============================================================
// ... module definitions using ONLY built-ins or defined modules ...

// Top-level render call (only one, uses only defined modules)
my_top_module();
```
"""


def _validate_scad(scad_path: pathlib.Path) -> list[str]:
    """Run openscad --check and return list of 'unknown module' warning strings."""
    result = subprocess.run(
        ["openscad", "--render", "--export-format", "stl", "-o", "/dev/null", str(scad_path)],
        capture_output=True, text=True, timeout=30,
    )
    errors = []
    for line in (result.stderr or "").splitlines():
        if "Ignoring unknown module" in line or "unknown variable" in line.lower():
            errors.append(line.strip())
    return errors


def run(state: ProjectState, llm: LLM) -> ProjectState:
    brief = state.brief
    user_msg = f"""Design brief:
{json.dumps(brief, indent=2)}

Generate the concept JSON and full parametric OpenSCAD file."""

    # Use coder model for OpenSCAD generation
    os.environ["DJINN_MODEL"] = DESIGN_MODEL
    print(f"  [DesignGenAgent] via {llm.name} (model: {DESIGN_MODEL}) ...")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    piece = brief.get("piece_name", brief.get("request", "part"))
    safe = re.sub(r"[^a-z0-9_]", "_", piece.lower())[:36]
    scad_path = MODELS_DIR / f"job{state.id}_{safe}.scad"

    concept = {}
    for attempt in range(2):
        reply = llm.chat(SYSTEM, [{"role": "user", "content": user_msg}], max_tokens=6000)

        json_match = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
        scad_match = re.search(r'```openscad\s*(.*?)\s*```', reply, re.DOTALL)

        if json_match:
            try:
                concept = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                concept = {"concept_summary": "generated", "raw": json_match.group(1)[:200]}

        scad_code = scad_match.group(1) if scad_match else reply
        scad_path.write_text(scad_code)

        errors = _validate_scad(scad_path)
        if not errors:
            print(f"    → SCAD: {scad_path.name} (valid)")
            break

        print(f"    → SCAD attempt {attempt + 1} has {len(errors)} error(s): {errors[0]}")
        if attempt == 0:
            # Retry with error context injected
            error_list = "\n".join(f"  - {e}" for e in errors[:5])
            user_msg = (
                f"{user_msg}\n\n"
                f"PREVIOUS ATTEMPT FAILED — OpenSCAD reported these errors:\n{error_list}\n\n"
                f"Fix: ensure every called module is defined with the `module` keyword, "
                f"use `cube()` not `box()`, and only call built-ins or modules you defined."
            )
        else:
            print(f"    → SCAD still has errors after retry — proceeding anyway (proto_opt will catch it)")
    else:
        print(f"    → SCAD: {scad_path.name}")

    state.concept = concept
    state.source_scad = str(scad_path)
    state.status = "design_edit"
    state.note = concept.get("concept_summary", piece)
    state.supports_needed = concept.get("supports_needed", False)

    return state

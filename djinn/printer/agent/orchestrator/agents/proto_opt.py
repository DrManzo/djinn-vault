"""
ProtoOptAgent — generates prototype-light and production-ready variants from one design.
Outputs two SCAD files and renders both to STL.
"""
import json, pathlib, re, subprocess
from ..llm import LLM
from ..project_state import ProjectState

MODELS_DIR = pathlib.Path.home() / "Obsidian/djinn/printer/models"

SYSTEM = """You are ProtoOptAgent. You generate two geometry variants from one OpenSCAD design.

## Prototype-light rules
- Reduce wall thickness to max(1.6, original * 0.55)
- Cut internal solid mass — add hollowing or rib structure where appearance allows
- Remove decorative/structural bulk from non-load-bearing regions
- PRESERVE exactly: mating faces, hole locations, outer silhouette, $fn

## Production-ready rules
- Keep or increase critical wall thickness
- Add fillets at stress concentrations (r=2–3mm)
- Keep all functional interfaces
- Only apply topology improvements, not simplifications

## Output — reply with EXACTLY this structure:

```json
{
  "prototype": {
    "description": "what changed for prototype",
    "parameter_overrides": {"WALL_T": 1.6},
    "expected_mass_reduction_pct": 35,
    "expected_time_reduction_pct": 30
  },
  "production": {
    "description": "what changed for production",
    "parameter_overrides": {"WALL_T": 3.2, "FILLET_R": 2.0},
    "strength_notes": "stronger because ..."
  }
}
```

```openscad_prototype
// Complete prototype variant — full file with prototype parameters applied
```

```openscad_production
// Complete production variant — full file with production parameters applied
```
"""


def _render_stl(scad_path: pathlib.Path, stl_path: pathlib.Path) -> bool:
    result = subprocess.run(
        ["openscad", "--render", "--export-format", "stl", "-o", str(stl_path), str(scad_path)],
        capture_output=True, text=True, timeout=180,
    )
    return result.returncode == 0 and stl_path.exists()


def run(state: ProjectState, llm: LLM) -> ProjectState:
    scad_path = pathlib.Path(state.source_scad)
    if not scad_path.exists():
        raise FileNotFoundError(f"Source SCAD not found: {scad_path}")

    current_code = scad_path.read_text()

    user_msg = f"""Design context:
{json.dumps(state.concept, indent=2)}

Source OpenSCAD file ({scad_path.name}):
```openscad
{current_code}
```

Generate prototype-light and production-ready variants."""

    print(f"  [ProtoOptAgent] via {llm.name} ...")
    reply = llm.chat(SYSTEM, [{"role": "user", "content": user_msg}], max_tokens=8000)

    json_match  = re.search(r'```json\s*(.*?)\s*```', reply, re.DOTALL)
    proto_match = re.search(r'```openscad_prototype\s*(.*?)\s*```', reply, re.DOTALL)
    prod_match  = re.search(r'```openscad_production\s*(.*?)\s*```', reply, re.DOTALL)

    variant_meta = {}
    if json_match:
        try:
            variant_meta = json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    base = scad_path.stem
    files = {}

    for tag, match in [("prototype", proto_match), ("production", prod_match)]:
        code = match.group(1) if match else current_code
        scad_out = MODELS_DIR / f"{base}_{tag}.scad"
        scad_out.write_text(code)

        stl_out = MODELS_DIR / f"{base}_{tag}.stl"
        ok = _render_stl(scad_out, stl_out)
        if ok:
            size_kb = stl_out.stat().st_size // 1024
            print(f"    → {tag} STL: {stl_out.name} ({size_kb}KB)")
            files[tag] = str(stl_out)
        else:
            print(f"    → {tag} render failed — SCAD saved: {scad_out.name}")
            files[tag] = str(scad_out)

    state.variants = {**variant_meta, "files": files}
    state.status = "doe_opt"

    return state

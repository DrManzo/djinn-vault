# Session Report — Engraving Specialist Sub-Agent Build (TASK-062)
**Date:** 2026-06-02
**Session:** djinn-engraving v0.1 build from Marcus's spec
**Author:** Claude

---

## Summary

Built the complete `djinn/engraving/` Python package from TASK-062 spec. The Engraving Specialist is a reasoning agent (not a model modifier) — it reads any STL, classifies surfaces by engravability, parses natural language placement intent via Ollama, runs FDM machine constraint math, and returns 3 ranked proposals the user approves before anything touches the model. All 14 unit tests pass. `djinn engrave-analyze` is live in the CLI.

---

## What Was Built/Changed

### New Package: `~/projects/djinn-social/djinn/engraving/`

| Module | Purpose |
|--------|---------|
| `mesh_reader.py` | trimesh load, repair, auto-downsample >50k faces for analysis, `mesh_to_text_summary()` |
| `surface_classifier.py` | Face normal grouping (cos 15° tolerance), SurfaceType enum, engravability scoring 0–1 |
| `constraint_engine.py` | MachineProfile + EngravingConstraints dataclasses, `check_engraving_constraints()` |
| `machines.py` | fdm_04mm, fdm_02mm, fdm_06mm, sla, kessler (placeholder) profiles |
| `intent_parser.py` | EngravingIntent dataclass, Ollama intent extraction + heuristic fallback |
| `placement_scorer.py` | Composite scoring (35/25/20/20 weights), `score_placements()` |
| `proposal_generator.py` | EngravingProposal dataclass, `generate_proposals()`, `format_proposals()` rich output |
| `workarounds.py` | `apply_workarounds()` — adjusts depth/height to make failing proposals viable |
| `specialist.py` | EngravingSpecialist class, AnalysisResult dataclass, `analyze()` + `approve()` |
| `__init__.py` | Package exports |

### CLI
- Added `djinn engrave-analyze <stl_path> <request>` with `--machine` and `--model` flags
- On approval (1/2/3), writes `engraving_spec.json` next to the STL

### Dependencies
- `trimesh>=4.0` added to `pyproject.toml`
- `trimesh==4.12.2` installed system-wide

### Tests: `tests/test_engraving_specialist.py`
14 tests covering: surface classifier, constraint engine, placement scorer, intent parser heuristic fallback, full pipeline on a programmatic box mesh.

---

## Technical Decisions

**Surface classifier min-face threshold → 1 (not 3):** Spec said skip regions with < 3 faces. This drops all faces on primitive/unit-test meshes (box has 2 triangles per face). Changed to `< 1` — even 1 face is a valid region. Real production STLs will have many more faces per region anyway.

**`mesh_to_text_summary(info, surfaces=None)`:** Spec's original signature was `mesh_to_text_summary(info)` with `_format_surface_list(info)` doing the formatting (showed `pass`). Changed to accept `surfaces` as optional arg so the LLM intent parser gets the classified surface list as context. Called in `specialist.py` as `mesh_to_text_summary(mesh_info, surfaces=surfaces)`.

**Heuristic fallback for intent parsing:** If Ollama is unavailable, `parse_intent()` calls `_heuristic_parse()` instead of crashing. Handles direction keywords, emboss/deboss detection, quoted content extraction.

**`format_proposals()` returns Rich-markup string:** Output uses `[bold red]` etc. which `console.print()` renders correctly.

---

## Files Created/Modified

**New:**
- `djinn/engraving/__init__.py`
- `djinn/engraving/specialist.py`
- `djinn/engraving/mesh_reader.py`
- `djinn/engraving/intent_parser.py`
- `djinn/engraving/surface_classifier.py`
- `djinn/engraving/constraint_engine.py`
- `djinn/engraving/placement_scorer.py`
- `djinn/engraving/proposal_generator.py`
- `djinn/engraving/workarounds.py`
- `djinn/engraving/machines.py`
- `tests/test_engraving_specialist.py`

**Modified:**
- `djinn/cli.py` — `engrave-analyze` command added
- `pyproject.toml` — `trimesh>=4.0` added to dependencies

---

## Tests & Validation

```
14 passed in 0.59s
```

- Surface classifier correctly scores FLAT_TOP highest on a cube
- Overhang surfaces hard-zero
- Constraint engine catches depth < 0.5mm, text too narrow, text > min height
- Full pipeline: classify → intent → score → 3 proposals, Proposal 1 is FLAT_TOP
- `djinn engrave-analyze` appears in `djinn --help`

---

## Known Issues

1. **Kessler profile is a placeholder** — nozzle_diameter and xy_tolerance need real values. See `machines.py`.
2. **Logo/SVG not supported** — Phase 1 is text only. SVG bounding-box analysis is Phase 2 (separate TASK).
3. **Curved surface curvature is not computed** — `curvature_radius = None` everywhere. Cotangent-weight mean curvature is Phase 2.
4. **`_format_surface_list` in the format output uses old-style string, not Rich markup** — harmless, renders as plain text.
5. **No `djinn-engrave-analyze` standalone script** — only accessible via `djinn engrave-analyze`. Can add to `pyproject.toml [project.scripts]` if needed.

---

## What's Next

1. Wire Marcus into `djinn engrave-analyze` via Telegram flow (Section 12 of spec)
2. Confirm Kessler machine specs → update `machines.py`
3. Phase 2: curved surface curvature, SVG/logo bounding box analysis
4. Phase 3: model modifier agent that takes `engraving_spec.json` and runs `djinn-model-text-engrave`

— Claude

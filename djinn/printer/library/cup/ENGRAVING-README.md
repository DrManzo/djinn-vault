# Cup Engraving Toolkit

## Files

| File | What it is |
|---|---|
| `cup_engraved_FINAL.stl` | ✅ Slice-ready. Single mesh, all letters cut, watertight |
| `validate_and_fix_engraving.py` | Run on any engraved STL to check + auto-fix it |
| `agent_system_prompt.py` | Paste into a Claude Project to create a dedicated engraving agent |

---

## For your agent — how to use this on any future job

```bash
# Install once
pip install trimesh numpy manifold3d rtree

# Run on any engraved cup STL
python3 validate_and_fix_engraving.py my_cup.stl

# Specify output path
python3 validate_and_fix_engraving.py my_cup.stl --output my_cup_ready.stl

# Change minimum engrave depth (default 1.5mm)
python3 validate_and_fix_engraving.py my_cup.stl --min-depth 2.0
```

The script will:
1. Load the STL and check how many mesh components it has
2. Measure engraving depth at every letter vs the cup's curved surface
3. Flag any letters that are too shallow or floating outside the wall
4. Auto-fix by shifting the text deeper AND rebuilding as a TRUE single mesh
5. Re-validate and confirm before saving

---

## What was wrong & what was fixed

**Problem 1 — Edge letters not cutting:**
The text slab is flat but the cup wall curves. At X=±24 the cup surface
dips to Y≈48.5mm, but the letter shells' outer face was at Y=49.07mm —
sitting outside the wall. Those letters never intersected the cup at all.

**Problem 2 — 13 separate mesh components:**
The boolean operation stored the cup body and 12 letter shells as
disconnected floating geometry inside one STL file. The slicer saw them
as separate objects and ignored the inner shells — so the text showed
in the ghost preview but not in the actual slice.

**The fix:**
- Shifted all letters 2.1mm deeper into the cup wall
- Extended each letter cutter past the cup's outer surface so the
  boolean actually cuts through the wall faces
- Rebuilt as a single merged mesh using manifold3d
- Result: 1 component, watertight, all 12 letters confirmed cut

---

## Setting up the Claude agent

1. Go to **Claude.ai → Projects → New Project**
2. Paste `agent_system_prompt.py` contents into **Project Instructions**
3. Name it "3D Print Engraving Checker"

From then on, drop any engraved STL into that project and Claude will
run the full check automatically — no manual work needed.

---

## Cleanup answer

With 1.5–6mm channel depth and clean vertical walls, cleanup is easy:
- A **stiff-bristle toothbrush** clears support dust from letter channels
- A **dental pick or toothpick** for tight serif corners
- No bridging or overhangs inside the channels so no support material to dig out

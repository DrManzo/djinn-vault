# Typhon's Forge Challenge Coin — Build Report

**Final spec:** 38mm diameter × 4.5mm thick | 1,055,372 faces  
**Status:** Ready to slice  
**Files:** `coin_38_final.stl` (print this), `coin_preview_combined.scad` (edit this)

---

## What It Is

A 38mm 3D-printable challenge coin with:
- **Front face:** Typhon's Forge logo in 1.5mm raised relief, surrounded by a 1.5mm raised rim
- **Back face:** "THE TERP TRIBE" recessed 0.6mm into the flat surface

---

## Pipeline: PNG Logo → Printable STL

The logo was a PNG. OpenSCAD cannot import PNGs directly. The path was:

```
logo.png → logo_flat.pbm → logo_traced.svg → OpenSCAD → logo_38.stl
```

### Step 1 — Convert PNG to clean black-and-white PBM

```bash
convert "TYPHON'S FORGE LOGO.png" \
  -background white -alpha remove \
  -colorspace Gray -threshold 128 -type Bilevel \
  logo_flat.pbm
```

**Critical:** Must use `-background white -alpha remove` first, otherwise the transparent background becomes black and fills the entire image. The `-threshold 128` binarizes to pure black/white. Output must be PBM (not BMP or PNG) for potrace.

### Step 2 — Trace PBM to SVG with potrace

```bash
potrace logo_flat.pbm -s -o logo_traced.svg
```

Result: 543 paths, 288KB SVG. The potrace output uses an internal transform `scale(0.1, -0.1)` which flips the Y axis. This matters for centering in OpenSCAD.

### Step 3 — Find the true SVG center in OpenSCAD coordinates

OpenSCAD's `import()` applies the potrace Y-flip, so you cannot use the SVG header dimensions for centering. You must render a test STL and measure:

```openscad
// test_svg.scad
linear_extrude(height=2)
import("logo_traced.svg");
```

```bash
openscad --render --export-format stl -o test_svg.stl test_svg.scad
python3 -c "
import trimesh
m = trimesh.load('test_svg.stl', force='mesh')
cx = (m.bounds[0][0] + m.bounds[1][0]) / 2
cy = (m.bounds[0][1] + m.bounds[1][1]) / 2
print(f'SVG_CX={cx:.1f}, SVG_CY={cy:.1f}')
"
```

**Result:** SVG_CX=523.0, SVG_CY=373.6 (in OpenSCAD's internal SVG units)

### Step 4 — Scale the logo to fit the coin

Target: logo fills ~66% of coin diameter with clearance at all angles.

```python
# At default (no scale), SVG imports at ~560mm wide
# Coin is 38mm → LOGO_SCALE = target_width / 560

# Final value after iteration:
LOGO_SCALE = 0.0448
# → logo: 25.1mm wide × 27.6mm tall
# → fits inside 38mm coin circle with diagonal clearance
```

**Why 0.0448 and not larger:** The logo text "THE TERP TRIBE" and "TYPHON'S FORGE" sit near the outer edge of the logo bounding box. The coin is circular, so at the corners the effective radius is smaller. At scale 0.056 the corner text was poking outside the coin edge. 0.0448 (20% smaller) puts the full logo comfortably inside.

### Step 5 — Build the coin base (back text + rim)

```openscad
// coin_base_38.scad
COIN_D=38; COIN_T=3.0; RIM_W=1.5; RIM_H=0.8; TEXT_DEPTH=0.6; FN=128;

module shell() {
    union() {
        cylinder(d=COIN_D, h=COIN_T, $fn=FN);
        difference() {
            cylinder(d=COIN_D, h=COIN_T+RIM_H, $fn=FN);
            cylinder(d=COIN_D-RIM_W*2, h=COIN_T+RIM_H+1, $fn=FN);
        }
    }
}

module back_text() {
    mirror([1, 0, 0])   // ← critical: makes text read correctly when coin is flipped
    linear_extrude(height=TEXT_DEPTH + 0.01)
    text("THE TERP TRIBE",
         size=3.8, halign="center", valign="center",
         font="Liberation Serif:style=Bold", spacing=1.05);
}

difference() { shell(); back_text(); }
```

**Why `mirror([1, 0, 0])`:** The text is carved into the bottom face (Z=0). When you flip the physical coin over by rotating around the Y axis (natural hand motion), the X axis reverses, making mirrored text appear normal.

### Step 6 — Build the logo face

```openscad
// logo_38.scad
COIN_T=3.0; RELIEF=1.5; LOGO_SCALE=0.0448; SVG_CX=523.0; SVG_CY=373.6;

translate([0, 0, COIN_T])
scale([LOGO_SCALE, LOGO_SCALE, 1])
translate([-SVG_CX, -SVG_CY, 0])
linear_extrude(height=RELIEF)
import("logo_traced.svg");
```

**Why separate from base:** OpenSCAD's CGAL CSG engine silently fails when `union()` combines a cylinder with a 1M-face SVG mesh. The result is a corrupted STL with only 259 facets (just the coin, no logo). Workaround: render each part separately, merge outside OpenSCAD.

### Step 7 — Merge parts with trimesh

```python
import trimesh
base = trimesh.load('coin_base_38.stl', force='mesh')
logo = trimesh.load('logo_38.stl', force='mesh')
coin = trimesh.util.concatenate([base, logo])
coin.export('coin_38_final.stl')
# Result: 1,055,372 faces, 38×38×4.5mm
```

`trimesh.util.concatenate()` does a simple mesh merge (no boolean operations). This works because the parts don't overlap — the base occupies Z=0–3.8mm and the logo occupies Z=3.0–4.5mm with no interpenetration at the join.

---

## Key Parameters (edit in coin_preview_combined.scad)

| Parameter | Value | Effect |
|-----------|-------|--------|
| `COIN_D` | 38 | Coin diameter (mm) |
| `COIN_T` | 3.0 | Coin body thickness |
| `RELIEF` | 1.5 | Logo raised height |
| `RIM_W` | 1.5 | Rim ring width |
| `RIM_H` | 0.8 | Rim ring extra height |
| `TEXT_DEPTH` | 0.6 | Back text recess depth |
| `LOGO_SCALE` | 0.0448 | SVG → mm scale factor |
| `SVG_CX` | 523.0 | Logo SVG center X |
| `SVG_CY` | 373.6 | Logo SVG center Y |

---

## Slice Settings

No supports needed — flat bottom, all geometry faces upward.  
Recommended: 30–40% infill, 0.2mm layer height, 3 perimeters.  
Print logo-face UP for best surface detail on the relief.

---

## Known Gotchas

1. **OpenSCAD CGAL union() fails on 1M-face meshes** — always render parts separately and merge with trimesh.
2. **potrace needs PBM, not BMP** — BMP produces a single-path SVG. Use ImageMagick with `-type Bilevel`.
3. **SVG center must be measured from STL, not SVG header** — potrace's internal `scale(0.1,-0.1)` transform changes the effective coordinate system.
4. **Back text must use `mirror([1,0,0])`** — without it the text reads backwards on the physical coin.
5. **STLs are gitignored** (>50MB) — they live locally at `~/Obsidian/djinn/printer/library/typhons-forge-coin/`. Rebuild from SCAD files if needed.

---

## Rebuild Commands

```bash
cd ~/Obsidian/djinn/printer/library/typhons-forge-coin

# Rebuild from SCAD (takes ~2 min for logo due to face count)
openscad --render --export-format stl -o coin_base_38.stl coin_base_38.scad
openscad --render --export-format stl -o logo_38.stl logo_38.scad

# Merge
python3 -c "
import trimesh
coin = trimesh.util.concatenate([
    trimesh.load('coin_base_38.stl', force='mesh'),
    trimesh.load('logo_38.stl', force='mesh')
])
coin.export('coin_38_final.stl')
"
```

---

*Built by Claude, 2026-05-23*

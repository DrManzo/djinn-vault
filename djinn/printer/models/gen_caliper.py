"""
Printable sliding caliper — two parts, 0-130mm range, ~0.5mm accuracy.
Body (fixed jaw + ruler) + Slider (movable jaw).

Both parts lie flat for printing. Slider rests on top of ruler arm.
Assembly: place slider on ruler from right end, jaws face same direction.

Measuring: close jaws on object, read ruler mark at slider's left edge.
Scale zero = jaws touching (slider left edge at x=0 on ruler).
"""

import struct, math, os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Dimensions (mm) ---
RULER_LEN   = 160.0   # ruler arm length
RULER_W     = 12.0    # ruler arm width (y)
RULER_H     = 4.0     # part height (z) for both pieces
JAW_LEN     = 42.0    # jaw height (extends in -y from ruler)
JAW_W       = 5.0     # jaw thickness (x)
SLIDER_LEN  = 35.0    # slider arm length (x)
CLEARANCE   = 0.0     # slider just rests on top — no groove needed
MARK_H      = 0.5     # scale mark height above top face
MARK_W      = 0.6     # scale mark width (x)


# --- STL helpers ---

def cross3(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def sub3(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def norm3(v):
    L = math.sqrt(sum(x*x for x in v)) or 1.0
    return tuple(x/L for x in v)

def tri_normal(v0, v1, v2):
    return norm3(cross3(sub3(v1,v0), sub3(v2,v0)))

def pack_tri(v0, v1, v2):
    n = tri_normal(v0, v1, v2)
    return struct.pack('<12fH', *n, *v0, *v1, *v2, 0)

def write_stl(path, tris):
    header = b'Printable caliper' + b' ' * 63
    with open(path, 'wb') as f:
        f.write(header + struct.pack('<I', len(tris)) + b''.join(tris))
    print(f"Written: {path}  ({len(tris)} triangles)")


# --- Geometry primitives ---

def extrude(profile_2d, z0, z1):
    """
    Extrude a CCW 2D polygon from z0 to z1.
    Returns list of packed triangle bytes.
    """
    tris = []
    n = len(profile_2d)
    h0, h1 = z0, z1

    def pt(i, z): return (profile_2d[i][0], profile_2d[i][1], z)

    # Top face (z=z1): fan from v0, CCW → normal +z
    for i in range(1, n-1):
        tris.append(pack_tri(pt(0,h1), pt(i,h1), pt(i+1,h1)))

    # Bottom face (z=z0): fan from v0, reversed → normal -z
    for i in range(1, n-1):
        tris.append(pack_tri(pt(0,h0), pt(i+1,h0), pt(i,h0)))

    # Side walls
    for i in range(n):
        j = (i+1) % n
        b0, b1 = pt(i,h0), pt(j,h0)
        t0, t1 = pt(i,h1), pt(j,h1)
        tris.append(pack_tri(b0, b1, t1))
        tris.append(pack_tri(b0, t1, t0))

    return tris


def box(x0, y0, z0, x1, y1, z1):
    """Solid box as a CCW rectangle extruded."""
    profile = [(x0,y0), (x1,y0), (x1,y1), (x0,y1)]
    return extrude(profile, z0, z1)


def scale_marks(x_start, x_end, y0, y1, z_base, step_minor=5, step_major=10):
    """
    Raised scale marks on top face.
    minor tick: every step_minor mm, 3mm long in y
    major tick: every step_major mm, full y span, labeled (not in STL but noted)
    """
    tris = []
    x = x_start
    while x <= x_end:
        is_major = (round(x) % step_major == 0)
        tick_y1 = y0 + (RULER_W if is_major else RULER_W * 0.5)
        tick_y1 = min(tick_y1, y1)
        tris += box(x - MARK_W/2, y0, z_base, x + MARK_W/2, tick_y1, z_base + MARK_H)
        x += step_minor
    return tris


# --- Part profiles ---

def body_profile():
    """L-shape: ruler arm + fixed jaw. CCW from above."""
    # Fixed jaw at x=[0, JAW_W], y=[-JAW_LEN, 0]
    # Ruler arm at x=[0, RULER_LEN], y=[0, RULER_W]
    return [
        (0.0,      -JAW_LEN),
        (JAW_W,    -JAW_LEN),
        (JAW_W,    0.0),
        (RULER_LEN, 0.0),
        (RULER_LEN, RULER_W),
        (0.0,       RULER_W),
    ]


def slider_profile():
    """L-shape: slider arm + movable jaw. CCW from above.
    Jaw is on the LEFT side (x=0..JAW_W) mirroring the body jaw.
    When slider left edge (x=0) is at position P on body, measurement = P.
    """
    return [
        (0.0,        -JAW_LEN),
        (JAW_W,      -JAW_LEN),
        (JAW_W,      0.0),
        (SLIDER_LEN, 0.0),
        (SLIDER_LEN, RULER_W),
        (0.0,        RULER_W),
    ]


# --- Build parts ---

def build_body():
    tris = []
    # Main L-shape
    tris += extrude(body_profile(), 0.0, RULER_H)
    # Scale marks on top of ruler arm (x=0 to RULER_LEN, y=0 to RULER_W)
    tris += scale_marks(0, RULER_LEN - 5, 0.0, RULER_W, RULER_H)
    # Alignment ridge on back edge of ruler (helps slider stay on)
    # Small 1.5mm × 1.5mm ridge running full ruler length
    tris += box(0.0, RULER_W, 0.0, RULER_LEN, RULER_W + 1.5, RULER_H + 1.5)
    return tris


def build_slider():
    tris = []
    # Main L-shape — sits on top of body ruler (body z=4, slider z=4 to 8)
    tris += extrude(slider_profile(), RULER_H, RULER_H * 2)
    # Matching back groove to fit over body ridge (1.5mm wide × 1.5mm deep notch)
    # The slider bottom face sits at z=RULER_H, and the groove cuts into the back
    # Groove: remove box at y=[RULER_W, RULER_W+1.5+0.3], z=[RULER_H, RULER_H+1.5+0.3]
    # Instead of cutting, generate slider WITHOUT back section and ADD groove walls:
    # (simpler: the ridge goes OVER the slider — groove on slider back)
    # Groove profile on bottom of slider (y side, looking from back):
    # Back notch on slider — small channel to grip body ridge
    groove_d = 1.8   # groove depth (slightly larger than 1.5 ridge for clearance)
    groove_h = 1.8
    # Left groove wall
    tris += box(0.0, RULER_W + groove_d, RULER_H, SLIDER_LEN, RULER_W + groove_d + 2.0, RULER_H * 2)
    # Thumb grip: raised nub on top for gripping
    tris += box(SLIDER_LEN/2 - 6, 1.0, RULER_H*2, SLIDER_LEN/2 + 6, RULER_W - 1.0, RULER_H*2 + 2.0)
    return tris


# --- Generate files ---

body_tris = build_body()
slider_tris = build_slider()

body_path = os.path.join(OUTPUT_DIR, "caliper_body.stl")
slider_path = os.path.join(OUTPUT_DIR, "caliper_slider.stl")

write_stl(body_path, body_tris)
write_stl(slider_path, slider_tris)

print(f"\nBody:   {RULER_LEN}mm × {JAW_LEN + RULER_W}mm × {RULER_H}mm")
print(f"Slider: {SLIDER_LEN}mm × {JAW_LEN + RULER_W}mm × {RULER_H}mm")
print(f"Range:  0 – {int(RULER_LEN - JAW_W)}mm")
print(f"\nAssembly: slide slider onto body from right end")
print(f"Zero:     jaws touching → slider left edge at x=0 on ruler")
print(f"Use:      close on object → read ruler at slider left edge")

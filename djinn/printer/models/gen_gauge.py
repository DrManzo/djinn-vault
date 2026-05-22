"""
Diameter gauge for Puffco Proxy V2 (~40.6mm nominal).
5 U-shaped slots: 40.0 / 40.5 / 40.6 / 41.0 / 41.5mm
Drop device into each slot — snug fit = correct diameter.

Generates a valid watertight STL via polygon extrusion.
"""

import struct, math, os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

SLOTS        = [40.0, 40.5, 40.6, 41.0, 41.5]   # slot widths (mm)
WALL         = 5.0    # outer wall thickness
SLOT_SPACING = 4.0    # divider width between slots
SLOT_DEPTH   = 25.0   # how deep slots go from front
BASE_BACK    = 10.0   # solid base behind slots
GAUGE_H      = 8.0    # gauge thickness (z height)


# --- STL helpers ---

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def normalize(v):
    L = math.sqrt(v[0]**2+v[1]**2+v[2]**2) or 1.0
    return (v[0]/L, v[1]/L, v[2]/L)

def tri_normal(v0, v1, v2):
    return normalize(cross(sub(v1,v0), sub(v2,v0)))

def pack_tri(v0, v1, v2):
    n = tri_normal(v0, v1, v2)
    return struct.pack('<12fH', *n, *v0, *v1, *v2, 0)

def write_stl(path, triangles):
    header = b'Puffco gauge' + b' ' * 68
    data = header + struct.pack('<I', len(triangles)) + b''.join(triangles)
    with open(path, 'wb') as f:
        f.write(data)
    print(f"Written: {path}  ({len(triangles)} triangles)")


# --- Geometry ---

def rect_pieces(slots, wall, slot_spacing, slot_depth, base_back):
    """
    Decompose the comb top/bottom face into non-overlapping rectangles.
    Returns list of (x0, y0, x1, y1).
    y=0 is front (slot opening), y increases toward back.
    """
    total_d = slot_depth + base_back
    total_w = wall + sum(slots) + (len(slots)-1)*slot_spacing + wall

    pieces = []
    # Back solid bar
    pieces.append((0.0, slot_depth, total_w, total_d))
    # Left outer wall
    pieces.append((0.0, 0.0, wall, slot_depth))
    # Right outer wall
    pieces.append((total_w - wall, 0.0, total_w, slot_depth))
    # Dividers between slots
    x = wall
    for i in range(len(slots) - 1):
        x += slots[i]
        pieces.append((x, 0.0, x + slot_spacing, slot_depth))
        x += slot_spacing

    return pieces, total_w, total_d


def polygon_profile(slots, wall, slot_spacing, slot_depth, total_d, total_w):
    """
    Trace the comb outline as a 2D polygon (x, y).
    CCW winding from above (z-up) so top face normal is +z.
    y=0 is front (slot openings), y increases to back.
    """
    pts = []

    # Front-left corner of left outer wall
    pts.append((0.0, 0.0))
    # Front edge of left outer wall (going right)
    pts.append((wall, 0.0))

    x = wall
    for i, s in enumerate(slots):
        # Drop into slot (y increases toward back)
        pts.append((x, slot_depth))
        # Cross slot back
        pts.append((x + s, slot_depth))
        # Come back out
        pts.append((x + s, 0.0))
        x += s
        if i < len(slots) - 1:
            # Cross divider along front
            pts.append((x + slot_spacing, 0.0))
            x += slot_spacing

    # Front-right corner
    pts.append((total_w, 0.0))
    # Back-right corner
    pts.append((total_w, total_d))
    # Back-left corner
    pts.append((0.0, total_d))
    # Polygon closes back to pts[0]

    # Verify CCW (shoelace area > 0)
    n = len(pts)
    area2 = sum(pts[i][0]*pts[(i+1)%n][1] - pts[(i+1)%n][0]*pts[i][1] for i in range(n))
    if area2 < 0:
        pts.reverse()

    return pts


def build_gauge_stl():
    pieces, total_w, total_d = rect_pieces(SLOTS, WALL, SLOT_SPACING, SLOT_DEPTH, BASE_BACK)
    polygon = polygon_profile(SLOTS, WALL, SLOT_SPACING, SLOT_DEPTH, total_d, total_w)
    h = GAUGE_H
    tris = []

    # TOP FACE (z=h, normal +z): CCW from above
    for (x0, y0, x1, y1) in pieces:
        tris.append(pack_tri((x0,y0,h), (x1,y0,h), (x1,y1,h)))
        tris.append(pack_tri((x0,y0,h), (x1,y1,h), (x0,y1,h)))

    # BOTTOM FACE (z=0, normal -z): CW from above = CCW from below
    for (x0, y0, x1, y1) in pieces:
        tris.append(pack_tri((x0,y0,0), (x0,y1,0), (x1,y1,0)))
        tris.append(pack_tri((x0,y0,0), (x1,y1,0), (x1,y0,0)))

    # SIDE WALLS: follow polygon perimeter
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        x0, y0 = polygon[i]
        x1, y1 = polygon[j]
        b0 = (x0, y0, 0.0)
        b1 = (x1, y1, 0.0)
        t0 = (x0, y0, h)
        t1 = (x1, y1, h)
        # CCW polygon → outward normal = right of edge direction
        # Winding: b0 → b1 → t1 faces outward for CCW polygon
        tris.append(pack_tri(b0, b1, t1))
        tris.append(pack_tri(b0, t1, t0))

    return tris, total_w, total_d


tris, total_w, total_d = build_gauge_stl()
out = os.path.join(OUTPUT_DIR, "proxy_diameter_gauge.stl")
write_stl(out, tris)
print(f"Dimensions: {total_w:.1f} x {total_d:.1f} x {GAUGE_H}mm")
print(f"Slots: {SLOTS}")
print(f"Fits on Ender-3 V3 Plus 300x300 bed: {'YES' if total_w < 295 and total_d < 295 else 'NO — check dimensions'}")

"""
Pokeball Proxy Stand for Puffco Proxy V2.
100mm sphere, flat base, 41mm ID × 30mm socket at top.
Equator band + front button are separate closed solids (overlap sphere — slicer unions them).
Each component is independently manifold — no shared edges between parts.

Socket dims from cup.3mf: 41.0mm inner dia, 30mm deep.
"""

import math, struct, os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# === Dimensions ===
R            = 50.0   # sphere radius (100mm diameter)
CENTER_Z     = 38.0   # sphere center height (flat base at z=0)
SOCKET_R     = 20.5   # socket inner radius → 41mm ID for 40.6mm Proxy
SOCKET_DEPTH = 30.0   # socket depth
BAND_H       = 5.0    # equator band height (±2.5mm from equator)
BAND_W       = 2.5    # equator band radial protrusion
BUTTON_R     = 6.0    # front button radius
BUTTON_H     = 2.0    # front button height (protrusion above sphere)
N_LAT        = 56
N_LON        = 72
N_BTN        = 36

# === Derived ===
Z_TOP_CUT  = CENTER_Z + math.sqrt(R**2 - SOCKET_R**2)  # z where sphere r = SOCKET_R
Z_SOCK_FLR = Z_TOP_CUT - SOCKET_DEPTH
THETA_BASE = math.acos(-CENTER_Z / R)   # theta at z=0
THETA_TOP  = math.asin(SOCKET_R / R)    # theta at top cut
R_BASE     = math.sqrt(R**2 - CENTER_Z**2)

Z_BAND_LO = CENTER_Z - BAND_H / 2
Z_BAND_HI = CENTER_Z + BAND_H / 2
R_BAND_IN  = R - 0.4    # slightly inside sphere → no shared edges
R_BAND_OUT = R + BAND_W

print(f"Sphere: {2*R:.0f}mm dia, {Z_TOP_CUT:.1f}mm tall")
print(f"Socket: {SOCKET_R*2:.0f}mm ID × {SOCKET_DEPTH:.0f}mm deep (floor z={Z_SOCK_FLR:.1f}mm)")
print(f"Base radius: {R_BASE:.1f}mm")


# === STL helpers ===

def cross3(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def sub3(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def norm3(v):
    L = math.sqrt(sum(x*x for x in v)) or 1.0
    return tuple(x/L for x in v)
def tri_normal(v0, v1, v2):
    return norm3(cross3(sub3(v1, v0), sub3(v2, v0)))
def pack_tri(v0, v1, v2):
    n = tri_normal(v0, v1, v2)
    return struct.pack('<12fH', *n, *v0, *v1, *v2, 0)

tris = []

def phi(j, n=N_LON):
    return 2 * math.pi * j / n

def ring_pt(r, p, z):
    return (r * math.cos(p), r * math.sin(p), z)

def sph_pt(theta, p):
    s = math.sin(theta)
    return (R * s * math.cos(p), R * s * math.sin(p), CENTER_Z + R * math.cos(theta))

def add_cyl_outward(r, z0, z1, n=N_LON):
    """Closed cylinder band, outward normals."""
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        b0, b1 = ring_pt(r, p0, z0), ring_pt(r, p1, z0)
        t0, t1 = ring_pt(r, p0, z1), ring_pt(r, p1, z1)
        tris.append(pack_tri(b0, b1, t1))
        tris.append(pack_tri(b0, t1, t0))

def add_cyl_inward(r, z0, z1, n=N_LON):
    """Closed cylinder band, inward normals (socket interior)."""
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        b0, b1 = ring_pt(r, p0, z0), ring_pt(r, p1, z0)
        t0, t1 = ring_pt(r, p0, z1), ring_pt(r, p1, z1)
        tris.append(pack_tri(b0, t0, t1))
        tris.append(pack_tri(b0, t1, b1))

def add_disk_up(r, z, n=N_LON):
    """Filled disk, normal +z."""
    c = (0.0, 0.0, z)
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        tris.append(pack_tri(c, ring_pt(r, p0, z), ring_pt(r, p1, z)))

def add_disk_down(r, z, n=N_LON):
    """Filled disk, normal -z."""
    c = (0.0, 0.0, z)
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        tris.append(pack_tri(c, ring_pt(r, p1, z), ring_pt(r, p0, z)))

def add_annulus_up(r_in, r_out, z, n=N_LON):
    """Annular ring, normal +z."""
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        a0, a1 = ring_pt(r_in,  p0, z), ring_pt(r_in,  p1, z)
        b0, b1 = ring_pt(r_out, p0, z), ring_pt(r_out, p1, z)
        tris.append(pack_tri(a0, b0, b1))
        tris.append(pack_tri(a0, b1, a1))

def add_annulus_down(r_in, r_out, z, n=N_LON):
    """Annular ring, normal -z."""
    for j in range(n):
        p0, p1 = phi(j, n), phi(j+1, n)
        a0, a1 = ring_pt(r_in,  p0, z), ring_pt(r_in,  p1, z)
        b0, b1 = ring_pt(r_out, p0, z), ring_pt(r_out, p1, z)
        tris.append(pack_tri(a0, b1, b0))
        tris.append(pack_tri(a0, a1, b1))


# ============================================================
# 1. Outer sphere surface (continuous lat bands, no excisions)
# ============================================================
lat_thetas = [THETA_BASE - (THETA_BASE - THETA_TOP) * i / N_LAT for i in range(N_LAT + 1)]

for i in range(N_LAT):
    t0, t1 = lat_thetas[i], lat_thetas[i + 1]
    for j in range(N_LON):
        p0, p1 = phi(j), phi(j + 1)
        v00, v01 = sph_pt(t0, p0), sph_pt(t0, p1)
        v10, v11 = sph_pt(t1, p0), sph_pt(t1, p1)
        tris.append(pack_tri(v00, v01, v11))
        tris.append(pack_tri(v00, v11, v10))


# ============================================================
# 2. Flat bottom disk (z=0, normal -z)
# ============================================================
add_disk_down(R_BASE, 0.0)


# ============================================================
# 3. Socket inner wall (r=SOCKET_R, normal inward)
# ============================================================
add_cyl_inward(SOCKET_R, Z_SOCK_FLR, Z_TOP_CUT)


# ============================================================
# 4. Socket floor (normal +z)
# ============================================================
add_disk_up(SOCKET_R, Z_SOCK_FLR)


# ============================================================
# 5. Equator band (closed ring solid, overlaps sphere — no shared edges)
#    Inner radius slightly inside sphere so edges never coincide.
# ============================================================
add_cyl_outward(R_BAND_OUT, Z_BAND_LO, Z_BAND_HI)   # outer wall
add_cyl_inward(R_BAND_IN,   Z_BAND_LO, Z_BAND_HI)   # inner wall
add_annulus_up(R_BAND_IN,   R_BAND_OUT, Z_BAND_HI)  # top face
add_annulus_down(R_BAND_IN, R_BAND_OUT, Z_BAND_LO)  # bottom face


# ============================================================
# 6. Front button (closed cylinder in +x direction, overlaps sphere)
#    Centered at (0, CENTER_Z) in y-z plane.
#    Back face at x = R-0.4 (inside sphere — no shared edges with sphere).
# ============================================================
BTN_BACK_X  = R - 0.4
BTN_FRONT_X = R + BUTTON_H

# Front disk (normal +x)
btn_fc = (BTN_FRONT_X, 0.0, CENTER_Z)
for j in range(N_BTN):
    a0 = 2 * math.pi * j / N_BTN
    a1 = 2 * math.pi * (j + 1) / N_BTN
    v0 = (BTN_FRONT_X, BUTTON_R * math.cos(a0), CENTER_Z + BUTTON_R * math.sin(a0))
    v1 = (BTN_FRONT_X, BUTTON_R * math.cos(a1), CENTER_Z + BUTTON_R * math.sin(a1))
    tris.append(pack_tri(btn_fc, v0, v1))

# Back disk (normal -x)
btn_bc = (BTN_BACK_X, 0.0, CENTER_Z)
for j in range(N_BTN):
    a0 = 2 * math.pi * j / N_BTN
    a1 = 2 * math.pi * (j + 1) / N_BTN
    v0 = (BTN_BACK_X, BUTTON_R * math.cos(a0), CENTER_Z + BUTTON_R * math.sin(a0))
    v1 = (BTN_BACK_X, BUTTON_R * math.cos(a1), CENTER_Z + BUTTON_R * math.sin(a1))
    tris.append(pack_tri(btn_bc, v1, v0))

# Rim (normal outward in y-z plane)
for j in range(N_BTN):
    a0 = 2 * math.pi * j / N_BTN
    a1 = 2 * math.pi * (j + 1) / N_BTN
    bk0 = (BTN_BACK_X,  BUTTON_R * math.cos(a0), CENTER_Z + BUTTON_R * math.sin(a0))
    bk1 = (BTN_BACK_X,  BUTTON_R * math.cos(a1), CENTER_Z + BUTTON_R * math.sin(a1))
    fr0 = (BTN_FRONT_X, BUTTON_R * math.cos(a0), CENTER_Z + BUTTON_R * math.sin(a0))
    fr1 = (BTN_FRONT_X, BUTTON_R * math.cos(a1), CENTER_Z + BUTTON_R * math.sin(a1))
    tris.append(pack_tri(bk0, bk1, fr1))
    tris.append(pack_tri(bk0, fr1, fr0))


# ============================================================
# Write STL
# ============================================================
out = os.path.join(OUTPUT_DIR, "pokeball_proxy_stand.stl")
with open(out, 'wb') as f:
    f.write(b'Pokeball Proxy Stand' + b' ' * 60)
    f.write(struct.pack('<I', len(tris)))
    f.write(b''.join(tris))

print(f"\nWritten: {out}  ({len(tris):,} triangles)")
print(f"Proxy sits {SOCKET_DEPTH:.0f}mm deep, {71-SOCKET_DEPTH:.0f}mm extends above ball")
print(f"Print with tree supports — overhang above equator")

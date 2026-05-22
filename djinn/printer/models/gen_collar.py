"""
Generate fit-test collar rings for Puffco Proxy V2 bubbler project.
Produces binary STL files for 3 inner diameter variants.
Ring: OD=30mm, Height=10mm, IDs=[21.5, 22.0, 22.5]mm
"""

import struct
import math
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SEGMENTS = 64
OD = 30.0
HEIGHT = 10.0
IDS = [21.5, 22.0, 22.5]


def circle_points(radius, segments, z):
    return [
        (radius * math.cos(2 * math.pi * i / segments),
         radius * math.sin(2 * math.pi * i / segments),
         z)
        for i in range(segments)
    ]


def triangle_normal(v0, v1, v2):
    ax, ay, az = v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]
    bx, by, bz = v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]
    nx = ay*bz - az*by
    ny = az*bx - ax*bz
    nz = ax*by - ay*bx
    length = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
    return (nx/length, ny/length, nz/length)


def pack_triangle(normal, v0, v1, v2):
    return struct.pack(
        '<12fH',
        *normal, *v0, *v1, *v2, 0
    )


def build_ring_stl(od, inner_d, height, segments):
    ro = od / 2.0
    ri = inner_d / 2.0
    triangles = []

    outer_bot = circle_points(ro, segments, 0)
    outer_top = circle_points(ro, segments, height)
    inner_bot = circle_points(ri, segments, 0)
    inner_top = circle_points(ri, segments, height)

    for i in range(segments):
        j = (i + 1) % segments

        # top annulus face (normal up)
        triangles.append(pack_triangle(
            (0, 0, 1),
            outer_top[i], inner_top[i], outer_top[j]
        ))
        triangles.append(pack_triangle(
            (0, 0, 1),
            inner_top[i], inner_top[j], outer_top[j]
        ))

        # bottom annulus face (normal down)
        triangles.append(pack_triangle(
            (0, 0, -1),
            outer_bot[i], outer_bot[j], inner_bot[i]
        ))
        triangles.append(pack_triangle(
            (0, 0, -1),
            inner_bot[j], inner_bot[i], outer_bot[j]
        ))

        # outer wall
        v0, v1, v2, v3 = outer_bot[i], outer_bot[j], outer_top[j], outer_top[i]
        n = triangle_normal(v0, v1, v2)
        triangles.append(pack_triangle(n, v0, v1, v2))
        triangles.append(pack_triangle(n, v0, v2, v3))

        # inner wall (normal inward, reversed winding)
        v0, v1, v2, v3 = inner_bot[i], inner_top[i], inner_top[j], inner_bot[j]
        n = triangle_normal(v0, v1, v2)
        triangles.append(pack_triangle(n, v0, v1, v2))
        triangles.append(pack_triangle(n, v0, v2, v3))

    header = b'Puffco Proxy V2 fit-test collar' + b' ' * (80 - 31)
    count = struct.pack('<I', len(triangles))
    return header + count + b''.join(triangles)


for id_mm in IDS:
    filename = os.path.join(OUTPUT_DIR, f"collar_ID{id_mm:.1f}mm.stl")
    data = build_ring_stl(OD, id_mm, HEIGHT, SEGMENTS)
    with open(filename, 'wb') as f:
        f.write(data)
    print(f"Written: {filename}  ({len(data)//1024}KB)")

#!/usr/bin/env python3
"""Slice cup_geometry.stl to GCODE for Ender-3 V3 Plus (Klipper)."""
import numpy as np
import trimesh
import os, sys

MODEL = os.path.join(os.path.dirname(__file__), "cup_geometry.stl")
OUTPUT = os.path.join(os.path.dirname(__file__), "cup_geometry.gcode")

LAYER_H = 0.2
NOZZLE_DIA = 0.4
LINE_W = 0.42
BED_TEMP = 60
HOTEND_TEMP = 225
RETRACT = 0.8

mesh = trimesh.load(MODEL)

# Center on Ender-3 V3 Plus bed (300x300mm)
bed_x, bed_y = 150, 150
offset_x = bed_x - (mesh.bounds[0][0] + mesh.bounds[1][0]) / 2
offset_y = bed_y - (mesh.bounds[0][1] + mesh.bounds[1][1]) / 2
offset_z = -mesh.bounds[0][2]  # bring bottom to Z=0
mesh.vertices += [offset_x, offset_y, offset_z]

z_min, z_max = mesh.bounds[0][2], mesh.bounds[1][2]
print(f"Z range: {z_min:.1f} to {z_max:.1f}")

layers = int((z_max - z_min) / LAYER_H) + 1
print(f"Layers: {layers}")

speed_move = 3000
speed_print = 900
speed_z = 300

def header():
    return """; Sliced by Djinn — Ender-3 V3 Plus (Klipper)
G28 ; home all
M140 S{BED_TEMP} ; bed temp
M104 S{HOTEND_TEMP} ; hotend temp
M190 S{BED_TEMP} ; wait for bed
M109 S{HOTEND_TEMP} ; wait for hotend
G1 Z10 F{speed_z} ; lift
G92 E0 ; reset extruder
""".format(BED_TEMP=BED_TEMP, HOTEND_TEMP=HOTEND_TEMP, speed_z=speed_z)

def footer():
    return """G1 Z{z_max:.1f} F{speed_z} ; lift
M104 S0 ; hotend off
M140 S0 ; bed off
M84 ; disable motors
""".format(z_max=z_max, speed_z=speed_z)

def gcode_for_path(path, z, e, first_layer=False):
    """Generate GCODE for a 2D path at height z."""
    if len(path) < 3:
        return "", e
    lines = []
    f = speed_print if not first_layer else speed_print * 0.5
    for i, pt in enumerate(path):
        x, y = pt[0], pt[1]
        if i == 0:
            # Move to start
            lines.append(f"G0 X{x:.3f} Y{y:.3f} F{speed_move}")
            # Lower to Z
            lines.append(f"G1 Z{z:.3f} F{speed_z}")
            # First extrusion
            e += 0.5
            lines.append(f"G1 X{x:.3f} Y{y:.3f} E{e:.5f} F{f}")
        else:
            dx = path[i][0] - path[i-1][0]
            dy = path[i][1] - path[i-1][1]
            dist = np.sqrt(dx*dx + dy*dy)
            e += dist * 0.05
            lines.append(f"G1 X{x:.3f} Y{y:.3f} E{e:.5f} F{f}")
    return "\n".join(lines), e

def slice_layer(mesh, z):
    """Get cross-section paths at height z."""
    slice = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if slice is None:
        return []
    paths = []
    for entity in slice.entities:
        if entity.__class__.__name__ == "Line":
            pts = slice.vertices[entity.points]
            paths.append(pts)
        elif entity.__class__.__name__ == "PolyLine":
            pts = slice.vertices[entity.points]
            paths.append(pts)
    return paths

print("Slicing...")
gcode = header()
e = 0.0

for i in range(layers):
    z = z_min + i * LAYER_H + 0.1
    if z > z_max:
        break
    paths = slice_layer(mesh, z)
    if not paths:
        continue
    for path in paths:
        layer_gcode, e = gcode_for_path(path, z, e, first_layer=(i==0))
        if layer_gcode:
            gcode += f"; Layer {i} at Z={z:.2f}\n"
            gcode += layer_gcode + "\n"
    # Retract between layers
    e -= RETRACT
    gcode += f"G1 E{e:.5f} F{speed_move}\n"
    if i % 50 == 0:
        print(f"  Layer {i}/{layers} (Z={z:.1f})")

gcode += footer()

with open(OUTPUT, "w") as f:
    f.write(gcode)

print(f"Written: {OUTPUT} ({len(gcode.splitlines())} lines)")

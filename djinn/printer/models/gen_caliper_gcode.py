"""
Gcode generator for printable sliding caliper.
Prints body + slider side by side in one job.
Ender-3 V3 Plus, PLA, 0.24mm layers, 3 perimeters, 20% infill.
"""

import math, struct, os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Print config
LAYER_H       = 0.24
EXTRUSION_W   = 0.45
FILAMENT_D    = 1.75
HOTEND        = 215
BED           = 60
PRINT_SPEED   = 40      # mm/s
TRAVEL_SPEED  = 150     # mm/s
N_PERIMETERS  = 3
INFILL_SPACE  = 2.2     # mm between infill lines (~20%)
SOLID_LAYERS  = 2       # solid layers top and bottom

EXTRUDE_PER_MM = (LAYER_H * EXTRUSION_W) / (math.pi * (FILAMENT_D/2)**2)

# Part profiles (model coords, CCW from above)
# Body: jaw at x=[0,5] y=[-42,0], ruler at x=[0,160] y=[0,12]
BODY_PROFILE = [(0,-42),(5,-42),(5,0),(160,0),(160,12),(0,12)]
# Slider: jaw at x=[0,5] y=[-42,0], arm at x=[0,35] y=[0,12]
SLIDER_PROFILE = [(0,-42),(5,-42),(5,0),(35,0),(35,12),(0,12)]

# Bed offsets (translate model origin to bed position)
BODY_OFF   = (65.0, 165.0)   # body center-ish: x=[65..225] y=[123..177]
SLIDER_OFF = (235.0, 165.0)  # slider: x=[235..270] y=[123..177]

PART_H = 4.0
N_LAYERS = round(PART_H / LAYER_H)


# --- Polygon utilities ---

def offset_polygon(poly, d):
    """Inset CCW polygon by distance d."""
    n = len(poly)
    result = []
    for i in range(n):
        p  = poly[i]
        pp = poly[(i-1) % n]
        pn = poly[(i+1) % n]
        e1 = (p[0]-pp[0], p[1]-pp[1])
        e2 = (pn[0]-p[0], pn[1]-p[1])
        L1 = math.hypot(*e1) or 1e-9
        L2 = math.hypot(*e2) or 1e-9
        n1 = ( e1[1]/L1, -e1[0]/L1)
        n2 = ( e2[1]/L2, -e2[0]/L2)
        bx, by = n1[0]+n2[0], n1[1]+n2[1]
        BL = math.hypot(bx, by) or 1e-9
        dot = (bx*n1[0]+by*n1[1]) / BL
        dot = max(dot, 0.1)
        od = d / dot
        result.append((p[0]+(bx/BL)*od, p[1]+(by/BL)*od))
    return result


def poly_bbox(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs), max(ys)


def scanline_intersections(poly, y):
    """X intersections of horizontal line at y with polygon edges."""
    n = len(poly)
    xs = []
    for i in range(n):
        j = (i+1) % n
        y0, y1 = poly[i][1], poly[j][1]
        x0, x1 = poly[i][0], poly[j][0]
        if min(y0,y1) <= y < max(y0,y1):
            t = (y - y0) / (y1 - y0)
            xs.append(x0 + t*(x1-x0))
    return sorted(xs)


# --- Gcode emitter ---

class Gcode:
    def __init__(self):
        self.lines = []
        self.e = 0.0

    def add(self, line):
        self.lines.append(line)

    def travel(self, x, y):
        self.lines.append(f"G0 F{TRAVEL_SPEED*60:.0f} X{x:.3f} Y{y:.3f}")

    def extrude(self, x, y, speed_f=None):
        # distance from last extrude position tracked externally — use relative here
        pass

    def print_segment(self, x0, y0, x1, y1, speed_f):
        dist = math.hypot(x1-x0, y1-y0)
        self.e += dist * EXTRUDE_PER_MM
        self.lines.append(f"G1 X{x1:.3f} Y{y1:.3f} E{self.e:.5f} F{speed_f:.0f}")

    def trace_polygon(self, poly, xoff, yoff, speed_f):
        n = len(poly)
        x0 = poly[0][0] + xoff
        y0 = poly[0][1] + yoff
        self.travel(x0, y0)
        for i in range(1, n+1):
            px, py = poly[i % n]
            x1, y1 = px+xoff, py+yoff
            self.print_segment(x0, y0, x1, y1, speed_f)
            x0, y0 = x1, y1

    def scanline_fill(self, poly, xoff, yoff, spacing, solid, speed_f):
        x0b, y0b, x1b, y1b = poly_bbox(poly)
        y = y0b + spacing/2
        row = 0
        while y <= y1b:
            xs = scanline_intersections(poly, y)
            for i in range(0, len(xs)-1, 2):
                xa, xb = xs[i]+xoff, xs[i+1]+xoff
                if row % 2 == 0:
                    self.travel(xa, y+yoff)
                    self.print_segment(xa, y+yoff, xb, y+yoff, speed_f)
                else:
                    self.travel(xb, y+yoff)
                    self.print_segment(xb, y+yoff, xa, y+yoff, speed_f)
            y += spacing
            row += 1

    def lift(self, z):
        self.lines.append(f"G1 Z{z:.3f} F3000")

    def text(self):
        return "\n".join(self.lines)


# --- Main ---

g = Gcode()

g.add("; Printable Sliding Caliper — Body + Slider")
g.add("; Ender-3 V3 Plus | PLA | 0.24mm layers")
g.add(f"; Body offset: {BODY_OFF}  Slider offset: {SLIDER_OFF}")
g.add("M82 ;absolute extrusion mode")
g.add("M140 S0")
g.add("M104 S0")
g.add(f"START_PRINT EXTRUDER_TEMP={HOTEND} BED_TEMP={BED}")
g.add("G92 E0")
g.add("G92 E0")
g.add("G1 F2400 E-0.8")
g.add(f";LAYER_COUNT:{N_LAYERS}")

speed_f = PRINT_SPEED * 60

for layer in range(N_LAYERS):
    z = (layer + 1) * LAYER_H
    is_solid = (layer < SOLID_LAYERS) or (layer >= N_LAYERS - SOLID_LAYERS)
    infill_sp = EXTRUSION_W * 1.05 if is_solid else INFILL_SPACE

    g.add(f"\n; Layer {layer+1} z={z:.3f} {'SOLID' if is_solid else 'INFILL'}")
    g.lift(z)

    for profile, off in [(BODY_PROFILE, BODY_OFF), (SLIDER_PROFILE, SLIDER_OFF)]:
        xoff, yoff = off
        # Perimeters (outer → inner)
        current = profile
        for p in range(N_PERIMETERS):
            g.trace_polygon(current, xoff, yoff, speed_f)
            current = offset_polygon(current, EXTRUSION_W)
        # Infill
        g.scanline_fill(current, xoff, yoff, infill_sp, is_solid, speed_f)

g.add("\nM204 S20000")
g.add("M106 S0")
g.add("M106 P2 S0")
g.add("END_PRINT")
g.add("M82 ;absolute extrusion mode")
g.add("M104 S0")
g.add(";End of Gcode")

out = os.path.join(OUTPUT_DIR, "caliper_combined.gcode")
with open(out, 'w') as f:
    f.write(g.text())

lines = g.text().count('\n')
print(f"Written: {out}")
print(f"Lines: {lines:,}  |  Layers: {N_LAYERS}  |  Est. time: ~{N_LAYERS*2} min")

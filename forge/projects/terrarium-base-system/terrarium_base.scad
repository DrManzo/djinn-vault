// ============================================================
// Modular Terrarium Base System — Parametric Model
// djinn-vault / 3d-printing / terrariums
//
// One system, variable dimensions. Change the parameters below
// per terrarium instead of redesigning from scratch.
//
// Render one part at a time: set PART below to 1, 2, or 3.
// ============================================================

// ---------- USER PARAMETERS (change per terrarium) ----------
outer_diameter   = 100;   // mm — match to container mouth diameter
shape            = "round"; // "round" | "hex" | "square"
shelf_height     = 25;    // Part 1 height
riser_height     = 25;    // Part 2 height
reservoir_height = 35;    // Part 3 height — increase for closed/moss builds
side_port        = true;  // add viewing port to Part 3
wall_thickness_thin = 1.2;  // Parts 1 & 2
wall_thickness_thick = 2.4; // Part 3 (must hold standing water)

PART = 3; // <-- set to 1, 2, or 3 before rendering/exporting

// ---------- FIXED SYSTEM SPEC (do not change per-project) ----------
lug_count   = 3;
lug_width   = 8;
lug_depth   = 2;
lug_angle_spacing = 360 / lug_count; // 120 deg
ring_height = 6;

$fn = 96;

// ---------- SHAPE HELPER ----------
module base_profile(d, h) {
    r = d / 2;
    if (shape == "round") {
        cylinder(d = d, h = h);
    } else if (shape == "hex") {
        cylinder(d = d, h = h, $fn = 6);
    } else if (shape == "square") {
        translate([-r, -r, 0]) cube([d, d, h]);
    }
}

// ---------- BAYONET RING (male lugs, printed on top of each part) ----------
module bayonet_lugs(d, z) {
    r = d / 2;
    for (i = [0 : lug_count - 1]) {
        rotate([0, 0, i * lug_angle_spacing])
            translate([r - lug_depth, -lug_width/2, z])
                cube([lug_depth + 1, lug_width, ring_height]);
    }
}

// ---------- BAYONET SLOT (female, cut into bottom of each part) ----------
module bayonet_slots(d, z) {
    r = d / 2;
    for (i = [0 : lug_count - 1]) {
        rotate([0, 0, i * lug_angle_spacing + (lug_angle_spacing/2)])
            translate([r - lug_depth - 1, -lug_width/2 - 0.3, z])
                cube([lug_depth + 2, lug_width + 0.6, ring_height + 0.5]);
    }
}

// ---------- PART 1: PLANTING SHELF ----------
module part1_shelf() {
    d = outer_diameter;
    difference() {
        base_profile(d, shelf_height);
        // hollow interior
        translate([0, 0, wall_thickness_thin])
            base_profile(d - 2*wall_thickness_thin, shelf_height);
        // bottom slots (female, mates to Part 2 lugs)
        bayonet_slots(d, -0.5);
        // radial drainage slots in floor
        for (i = [0:7]) {
            rotate([0, 0, i * 45])
                translate([0, 0, -0.5])
                    linear_extrude(height = wall_thickness_thin + 1)
                        translate([d*0.15, -2, 0])
                            square([d*0.3, 4]);
        }
    }
    // top lugs (male, mates to container ring)
    bayonet_lugs(d, shelf_height - ring_height);
}

// ---------- PART 2: PERFORATED RISER ----------
module part2_riser() {
    d = outer_diameter;
    difference() {
        base_profile(d, riser_height);
        translate([0, 0, wall_thickness_thin])
            base_profile(d - 2*wall_thickness_thin, riser_height);
        bayonet_slots(d, -0.5);
        // vertical channel perforations, aligned with Part 1 slot angles
        for (i = [0:7]) {
            rotate([0, 0, i * 45])
                translate([d*0.3, 0, riser_height/2])
                    cylinder(d = 6, h = riser_height + 1, center = true);
        }
    }
    bayonet_lugs(d, riser_height - ring_height);
}

// ---------- PART 3: WATER RESERVOIR ----------
module part3_reservoir() {
    d = outer_diameter;
    difference() {
        base_profile(d, reservoir_height);
        translate([0, 0, wall_thickness_thick])
            base_profile(d - 2*wall_thickness_thick, reservoir_height - wall_thickness_thick + 0.5);
        bayonet_slots(d, -0.5);
        if (side_port) {
            translate([d/2 - 3, 0, reservoir_height*0.6])
                rotate([90, 0, 0])
                    cylinder(d = 12, h = 10, center = true);
        }
    }
    bayonet_lugs(d, reservoir_height - ring_height);
}

// ---------- RENDER SELECTED PART ----------
if (PART == 1) part1_shelf();
else if (PART == 2) part2_riser();
else if (PART == 3) part3_reservoir();

// ============================================================
// NOTES:
// - Export each part as separate STL: render PART=1, export,
//   render PART=2, export, render PART=3, export.
// - Any part fits any other part's ring in this system — lug
//   spec is fixed regardless of outer_diameter or shape.
// - Print orientation: Parts 1 & 2 flat (floor down). Part 3
//   upright / vase mode if side_port = false.
// ============================================================

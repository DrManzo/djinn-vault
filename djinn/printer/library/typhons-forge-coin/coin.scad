// Typhon's Forge — Challenge Coin
// Logo: TYPHON'S FORGE / THE TERP TRIBE

// ── Parameters ────────────────────────────────────────────────────────────────
COIN_D  = 50;    // coin diameter mm (change to 38 for smaller)
COIN_T  = 3.0;   // base thickness mm
RELIEF  = 1.2;   // logo raised height mm
RIM_W   = 1.5;   // rim width mm
RIM_H   = 0.8;   // rim raised height mm
FN      = 128;

// SVG as OpenSCAD imports it: center=(523, 374), width=560, height=616
// Scale to fill usable coin area (diameter minus rim)
USABLE_D  = COIN_D - RIM_W*2 - 1;
SVG_CX    = 523.0;
SVG_CY    = 373.6;
SVG_W     = 559.9;
SVG_H     = 616.4;
LOGO_SCALE = USABLE_D / max(SVG_W, SVG_H);  // fit largest dimension

// ── Modules ───────────────────────────────────────────────────────────────────
module coin_base() {
    cylinder(d=COIN_D, h=COIN_T, $fn=FN);
}

module rim() {
    difference() {
        cylinder(d=COIN_D, h=COIN_T + RIM_H, $fn=FN);
        cylinder(d=COIN_D - RIM_W*2, h=COIN_T + RIM_H + 1, $fn=FN);
    }
}

module logo() {
    translate([0, 0, COIN_T])
    scale([LOGO_SCALE, LOGO_SCALE, 1])
    translate([-SVG_CX, -SVG_CY, 0])
    linear_extrude(height=RELIEF / LOGO_SCALE)
    import("logo_traced.svg");
}

// ── Assemble ──────────────────────────────────────────────────────────────────
union() {
    coin_base();
    rim();
    intersection() {
        logo();
        cylinder(d=COIN_D - RIM_W*2 - 0.5, h=COIN_T + RELIEF + 2, $fn=FN);
    }
}

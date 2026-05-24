// Typhon's Forge — Challenge Coin
// Logo verified: 41.8mm wide × 46.0mm tall at LOGO_SCALE=0.0746
// Coin diameter: 50mm — logo fits inside with 4mm rim clearance

COIN_D  = 50;
COIN_T  = 3.0;
RELIEF  = 1.5;
RIM_W   = 1.5;
RIM_H   = 0.8;
FN      = 128;

// Centering values from bounding-box analysis of SVG import
LOGO_SCALE = 0.0746;
SVG_CX     = 523.0;
SVG_CY     = 373.6;

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
    linear_extrude(height=RELIEF)
    import("logo_traced.svg");
}

union() {
    coin_base();
    rim();
    logo();
}

// Typhon's Forge — 38mm Challenge Coin — Combined Preview
COIN_D     = 38;
COIN_T     = 3.0;
RELIEF     = 1.5;
RIM_W      = 1.5;
RIM_H      = 0.8;
TEXT_DEPTH = 0.6;
FN         = 128;
LOGO_SCALE = 0.0448;
SVG_CX     = 523.0;
SVG_CY     = 373.6;

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
    mirror([1, 0, 0])
    linear_extrude(height=TEXT_DEPTH + 0.01)
    text("THE TERP TRIBE",
         size=3.8, halign="center", valign="center",
         font="Liberation Serif:style=Bold", spacing=1.0);
}

module logo() {
    translate([0, 0, COIN_T])
    scale([LOGO_SCALE, LOGO_SCALE, 1])
    translate([-SVG_CX, -SVG_CY, 0])
    linear_extrude(height=RELIEF)
    import("logo_traced.svg");
}

union() {
    difference() { shell(); back_text(); }
    logo();
}

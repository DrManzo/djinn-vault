COIN_D=38; COIN_T=3.0; RIM_W=1.5; RIM_H=0.8; TEXT_DEPTH=0.6; FN=128;

// Base with rim
module shell() {
    union() {
        cylinder(d=COIN_D, h=COIN_T, $fn=FN);
        difference() {
            cylinder(d=COIN_D, h=COIN_T+RIM_H, $fn=FN);
            cylinder(d=COIN_D-RIM_W*2, h=COIN_T+RIM_H+1, $fn=FN);
        }
    }
}

// "THE TERP TRIBE" recessed into bottom face
// Mirror on X so text reads correctly when viewed from below
module back_text() {
    mirror([1, 0, 0])
    linear_extrude(height=TEXT_DEPTH + 0.01)
    text("THE TERP TRIBE",
         size=3.2,
         halign="center",
         valign="center",
         font="Liberation Serif:style=Bold",
         spacing=1.0);
}

difference() {
    shell();
    back_text();
}

COIN_D=50; COIN_T=3.0; RIM_W=1.5; RIM_H=0.8; FN=128;
union() {
    cylinder(d=COIN_D, h=COIN_T, $fn=FN);
    difference() {
        cylinder(d=COIN_D, h=COIN_T+RIM_H, $fn=FN);
        cylinder(d=COIN_D-RIM_W*2, h=COIN_T+RIM_H+1, $fn=FN);
    }
}

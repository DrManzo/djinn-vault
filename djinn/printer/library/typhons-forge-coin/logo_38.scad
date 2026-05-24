COIN_T=3.0; RELIEF=1.5; LOGO_SCALE=0.0448; SVG_CX=523.0; SVG_CY=373.6;
translate([0, 0, COIN_T])
scale([LOGO_SCALE, LOGO_SCALE, 1])
translate([-SVG_CX, -SVG_CY, 0])
linear_extrude(height=RELIEF)
import("logo_traced.svg");

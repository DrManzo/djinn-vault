LOGO_SCALE = 0.0746;
SVG_CX = 523.0;
SVG_CY = 373.6;

scale([LOGO_SCALE, LOGO_SCALE, 1])
translate([-SVG_CX, -SVG_CY, 0])
linear_extrude(height=2)
import("logo_traced.svg");

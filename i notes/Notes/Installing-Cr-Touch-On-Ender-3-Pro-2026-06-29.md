---
subject: 3d-printing/models/ender-3-pro/installation/cr-touch
tags:
  - 3d-printing/printer-setup/preparation
  - 3d-printing/models/ender-3-pro
created: 2026-06-29
source: Perplexity export
---

# Installing CR Touch on Ender 3 Pro

## Summary
Instructions for installing CR Touch on an Ender 3 Pro, distinguishing between the older v1.1.x and newer 4.2.2/4.2.7 boards.

## Key Points
- Confirm your mainboard version.
- Use the appropriate wiring method based on your board type.
- Follow steps to properly install and calibrate CR Touch.

## Details
For an Ender 3 Pro with a Creality V4.2.2 or V4.2.7 mainboard:
1. **Step 1 – Confirm Mainboard Version**
   - Check the label on the mainboard for "Creality V4.2.2" or "V4.2.7".
   
2. **Step 2 – Wiring Instructions (for 32-bit Ender 3 Pro)**
   - Mount CR Touch next to the hotend using a supplied bracket.
   - Route the cable through the sleeve to the mainboard.
   - Plug the big end of the cable into the dedicated 5-pin BL/CR Touch header on the board.
   - Unplug and remove the original mechanical Z-endstop (switch and cable).
   - Install firmware specifically built for Ender 3 Pro + CR/BL Touch.
   - Set and store your Z-offset via the printer menu.

For an older Ender 3 Pro with a V1.1.x mainboard:
1. **Step 1 – Confirm Mainboard Version**
   - Check the label on the mainboard for "V1.1.4" or "V1.1.5".
   
2. **Step 2 – Wiring Instructions (for 8-bit Ender 3 Pro)**
   - Use a pin-27 or LCD adapter to connect the probe’s signal lead.
   - Unplug the Z-endstop cable and plug the probe's 2-wire lead into the Z-endstop header.
   - Flash BL/CR-Touch-enabled firmware (usually requiring a bootloader first).
   - Calibrate Z-offset and mesh leveling as above.

## References
- [ShinyUpgrades](https://shinyupgrades.com/pages/ender-3-pro-set-up-cr-touch)
- [YouTube](https://www.youtube.com/watch?v=4PCoKgG_Cf8)
- [CrealityExperts](https://www.crealityexperts.com/installing-bltouch-ender-3)
- [Blog.Gruby](https://blog.gruby.com/2020/01/05/installing-a-bltouch-on-an-ender-3-pro.html)

## Related
- [[3d-printing/models/ender-3-pro/mainboard-version-check]] — Check the mainboard version.
- [[3d-printing/printer-setup/preparation]] — General setup instructions for 3D printers.
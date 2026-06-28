---
subject: 3d-printing/models/ender-3-pro/cr-touch-installation
tags:
  - 3d-printing/models/ender-3-pro/installation/cr-touch
  - 3d-printing/models/ender-3-pro/mainboard-version-check
created: 2026-06-28
source: Perplexity export
---

# Installing CR Touch on Ender 3 Pro

## Summary
Instructions for installing the CR Touch probe on an Ender 3 Pro, depending on the mainboard version.

## Key Points
- Check if your board is a Creality V4.2.2 or V4.2.7 to use the 5-pin BL/CR Touch port.
- For older boards (V1.1.x), use the LCD/Z-endstop method and upgrade firmware accordingly.

## Details
To install the CR Touch probe on an Ender 3 Pro, follow these steps:

### Step 1: Confirm Mainboard Version
Before wiring the CR Touch, open the electronics case and check the label on the board itself:
- **Creality V4.2.2 or V4.2.7**: You have the 5-pin BL/CR Touch port.
- **V1.1.4 or V1.1.5**: No 5-pin header, use an alternative method.

### Step 2: Wiring for Creality V4.2.2 / V4.2.7
For a 32-bit Ender 3 Pro board (4.2.2 or 4.2.7):
- Mount the CR Touch next to the hotend using the supplied bracket.
- Plug the small connector into the probe.
- Route the cable through the cable sleeve to the mainboard.
- Plug the big end of the cable into the dedicated 5-pin BL/CR Touch header on the board.
- Unplug and remove the original mechanical Z-endstop (switch and cable).
- Install firmware specifically built for Ender 3 Pro + CR/BL Touch (Creality’s or Marlin with `BLTOUCH`/`Z_SAFE_HOMING` enabled).
- Set and store your Z-offset via the printer menu.

### Step 3: Wiring for Older Boards (V1.1.x)
On older boards, use an alternative method:
- Use a pin-27 adapter to connect the probe’s signal lead.
- Unplug the Z-endstop cable and plug the probe’s 2-wire lead into that header.
- Alternatively, solder the probe wires directly to the Z-endstop leads if needed.
- Flash BL/CR-Touch-enabled firmware (usually requiring a bootloader first).
- Calibrate Z-offset and mesh leveling as above.

### Step 4: Why Instructions Don’t Match
The instructions you found assume an upgraded board with a 5-pin port. If your Ender 3 Pro still has the older v1.1.x board, follow guides that use the LCD/Z-endstop method or upgrade to V4.2.x for simpler installation.

## References
- [ShinyUpgrades](https://shinyupgrades.com/pages/ender-3-pro-set-up-cr-touch)
- [YouTube](https://www.youtube.com/watch?v=4PCoKgG_Cf8)
- [CrealityExperts](https://www.crealityexperts.com/installing-bltouch-ender-3)
- [Blog.Gruby](https://blog.gruby.com/2020/01/05/installing-a-bltouch-on-an-ender-3-pro.html)

## Related
- [[3d-printing/models/ender-3-pro/mainboard-upgrade]]
- [[3d-printing/slicing/critical-details]] — For more on Z-offset and mesh leveling.
- [[3d-printing/printer-maintenance]] — General maintenance tips for Ender 3 Pro.
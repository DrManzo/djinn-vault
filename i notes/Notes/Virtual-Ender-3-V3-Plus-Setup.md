---
subject: 3d-printing/models/ender-3v3-plus-virtual-copy
tags:
  - cs/software-development
  - 3d-printing/virtual-setup
  - personal/learning
created: 2026-06-14
source: Perplexity export
---

# Virtual Ender 3 V3 Plus Setup

## Summary
This note provides a virtual setup for the Ender 3 V3 Plus, allowing users to run tests and simulations locally on their machine.

## Key Points
- **Virtual Printer Dashboard**: Interactive lab dashboard with full printer spec reference.
- **Setup Guide**: Step-by-step guide including config explorer and test checklist.
- **Config Files**: `printer.cfg` and `moonraker.conf` for accurate virtual modeling.
- **Docker Setup**: Instructions to set up the virtual printer using Docker.

## Details
The virtual Ender 3 V3 Plus setup is designed to provide a local testing environment. Here’s how you can set it up:

### What You Get

**ender3-v3plus-virtual.html**
- Interactive lab dashboard.
- Full printer spec reference for the V3 Plus.
- Step-by-step setup guide.
- Config explorer with CoreXZ kinematics explained.
- Clickable test checklist to work through with Mainsail.
- Material profiles for all supported filaments.
- Dark/light mode toggle.

### Setting Up Locally

1. **Install Docker**:
   ```bash
   sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
   sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER && newgrp docker
   ```

2. **Clone the Virtual Printer Base**:
   ```bash
   git clone https://github.com/mainsail-crew/virtual-klipper-printer.git ~/virtual-printer
   cd ~/virtual-printer
   mkdir -p printer_data/config
   ```

3. **Drop Config Files**:
   ```bash
   cp printer.cfg ~/virtual-printer/printer_data/config/
   cp moonraker.conf ~/virtual-printer/printer_data/config/
   ```

4. **Launch the Virtual Printer**:
   ```bash
   docker compose up -d
   docker compose logs -f
   ```

5. **Add Printer in Mainsail**:
   Open [my.mainsail.xyz](https://my.mainsail.xyz) in your browser and add the printer with `localhost` port `7125`.

### Config Models Accurately

- **CoreXZ Kinematics**: Properly modeled shared CoreXZ rail.
- **Build Volume**: 300 × 300 × 330 mm with exact axis limits.
- **Max Velocity and Acceleration**: 600 mm/s max velocity, 20,000 mm/s² acceleration.
- **Input Shaper**: Pre-configured (MZV type, tunable frequencies).
- **Bed Mesh**: 6×6 across the full PEI plate footprint.
- **Direct Drive Extruder**: Pressure advance at 0.04.
- **Macros**: PRINT_START / PRINT_END / PAUSE / RESUME / CANCEL ready to test.
- **Filament Macros**: LOAD_FILAMENT / UNLOAD_FILAMENT.

### Local Behavior

The virtual printer runs entirely on your local machine, with the Docker container exposing Moonraker on `localhost:7125`. All config, G-code, logs, and simulated printer state are stored locally in a `./printer_data` folder.

### Fully Local Option

For a fully local stack:
- Use a locally served Mainsail install.
- Point another local Klipper frontend such as Fluidd at `localhost:7125`.

## References
- [Virtual Printer Setup](https://github.com/mainsail-crew/virtual-klipper-printer)
- [Mainsail Documentation](https://docs.mainsail.xyz/development/development-setup/)
- [Docker Installation Guide](https://docs.docker.com/engine/install/fedora/)

## Related
- [[Setting-Benchmarks-For-Ender-3-V3-Plus]] — virtual setup similarities
- [[Djinn-3d-Printer-Overview-And-Filament-Recommendations]] — filament recommendations for virtual printer

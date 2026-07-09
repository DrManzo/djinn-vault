# Typhon's Forge — Master Print Project List (35)

> Vault-grounded build list. Every project maps to a real system in the Djinn infrastructure.  
> Status tags: `[ ]` = not started · `[~]` = in progress · `[x]` = complete  
> Last updated: 2026-06-12

---

## 🖨️ Calliope Hardware Upgrades (Klipper/Moonraker-Native)

- [ ] **P01 — Overhead Webcam Arm (AKASO Brave 4 Mount)**  
  Frame-mounted articulating arm for the AKASO Brave 4 that feeds `djinn-webcam-monitor`'s frame-diff service. Puts camera on-axis with the bed every print. Eliminates manual repositioning.

- [ ] **P02 — Magnetic Filament Runout Sensor Housing**  
  Printed housing for a hall-effect sensor + embedded N52 disc on the filament path. Triggers Moonraker event → `djinn-print-monitor` → Telegram alert. Educational content angle: hall-effect physics explainer.

- [ ] **P03 — Cable Drag Chain (X-axis, Ender-3 V3 Plus spec)**  
  Reduces resonance artifacts on fast passes. Before/after ringing test = one full content episode. Directly improves commission print quality.

- [ ] **P04 — Vibration Isolation Feet (PETG + TPU bilayer)**  
  Two-part printed feet isolating Calliope from desk surface. Eliminates vibration bleed into the Typhon node sharing the same surface.

- [ ] **P05 — Magnetic Nozzle Swap Station**  
  Wall-mounted tray with embedded N52s holding 0.4/0.6/0.8mm nozzles, brass brush, and acupuncture pins. Zero-search nozzle swaps mid-queue.

- [ ] **P06 — PEI Plate Vertical Storage Rack**  
  Labeled rack for 3–4 PEI sheets organized by surface type. Speeds up batch plate swaps when running commission queue via `djinn-confirm-print`.

- [ ] **P07 — Magnetic Z-Stop Calibration Jig**  
  Reproducible live-z reference tool with embedded magnets that snap to the frame. Sets consistent first layer without manual babystep guessing every session.

- [ ] **P08 — Magnetic Enclosure Door Latch System**  
  Snap-close PETG enclosure panels for Calliope with magnet latches. Reduces drafts and cat interference on overnight commission jobs. Required for reliable ABS prints.

---

## 📡 Node Infrastructure Physical Layer (Salomon + Typhon)

- [ ] **P09 — Salomon Laptop Stand with Cable Pass-Through**  
  Elevated stand with rear cable comb organizer. Keeps RTX 5060 GPU vent unobstructed during Ollama inference at load.

- [ ] **P10 — Typhon Node Shelf Mount**  
  Wall or desk bracket for the MSI machine (storage node + Typhon's Studio streaming box). Ventilated, cable-routed.

- [ ] **P11 — External SSD Stackable Caddy**  
  Magnetic-snap stacking caddies for external drives handling ChromaDB vault index and rclone GDrive syncs. Educational angle: storage architecture content.

- [ ] **P12 — Network Switch + UPS Shelf**  
  Printed bracket co-locating the network switch and UPS supporting the Salomon ↔ Typhon ↔ Calliope triangle. Mounts clean to wall.

- [ ] **P13 — API Status Light Diffuser Box**  
  Printed diffuser housing for RGB LED strip driven by Raspberry Pi/Arduino reading Djinn service health. Red/Yellow/Green = service heartbeat visible at a glance from anywhere in the room.

- [ ] **P14 — Magnetic DIN Rail Relay Panel**  
  Snap-cover relay enclosures for automating forge power sequencing (printer, lights, mic). Educational angle: home automation relay wiring.

---

## 🎬 Typhon's Studio Content Gear (Media Pipeline Integration)

- [ ] **P15 — Overhead Camera Gantry (top-down rig)**  
  Extrusion-mounted arm for top-down print bed filming. Feeds `djinn-media-ingest` → `djinn-media-reel` pipeline without manual camera repositioning per session.

- [ ] **P16 — Articulating LED Key Light Arms**  
  Multi-joint lockable arms for the Cloudybay lighting node in Typhon's Studio. Replaces tripod footprint with wall-anchored arms. Frees desk space for filming surface.

- [ ] **P17 — Teleprompter Sled (phone + beam-splitter)**  
  Script reflection rig for voiceover and tutorial content. Eliminates eye-contact breaks that tank audience retention scores.

- [ ] **P18 — Stream Deck / Macro Pad Podium**  
  Angled enclosure for the macro pad triggering `djinn-media-publish-prep`, OBS scenes, and Discord/Telegram commands from the desk.

- [ ] **P19 — Magnetic Camera Quick-Release Plates (Arca-Swiss)**  
  Standardizes all camera mounts so the AKASO snaps between the bed rig (P01) and desk arm without screw tools. Keeps `djinn-webcam-monitor` always ready to reconnect.

- [ ] **P20 — Typhon's Forge Branded Desk Sign**  
  Back-lit insert frame for branding in every video. Permanent background fixture with magnetic letter tiles for episode-specific callouts.

- [ ] **P21 — Boom Arm Cable Clips (XLR/USB routed)**  
  Printed snap clips for mic boom hiding cable from camera's field of view. Clean audio setup directly improves retention for the RNNoise audio chain.

---

## 🎓 Educational + Magnet-Integrated Projects (Content-First)

- [ ] **P22 — Halbach Array Demo Kit**  
  Modular printed blocks each holding a directional N52. Assemble to show focused vs. dispersed magnetic fields. Pure physics education content with high shareability.

- [ ] **P23 — DIY Solenoid Coil Former (Electromagnetism Lab)**  
  Printable bobbin + core housing for winding a solenoid. Measure field strength with a multimeter. Mirrors actual electromagnetic research into 3D-printed coil forms.

- [ ] **P24 — Magnetic Pendulum Chaos Attractor**  
  Three-magnet base + printed pivot arm demonstrating nonlinear systems and chaos theory. Visually compelling B-roll that teaches math concepts.

- [ ] **P25 — Magnetic Gear Train (Non-Contact Torque Transfer)**  
  Printed ring-magnet gears transferring torque without tooth contact. Educational demo for machine design content. No direct wear — indefinite lifespan.

- [ ] **P26 — Hall-Effect Encoder Wheel Housing**  
  Encoder disc + hall sensor housing. Pairs with Arduino to measure Calliope's filament feed rate in real time. Directly useful telemetry for the print pipeline.

- [ ] **P27 — Binary Magnetic Latch Logic Gate**  
  Physical AND/OR gates using magnet-actuated latches. Teach digital logic through mechanical analog — bridges CS coursework to tangible demo.

- [ ] **P28 — Magnetic Field Visualizer Tray Stand**  
  Printed raised tray stand for iron filings field line visualization. Perfect visual anchor for the educational series intro/outro.

- [ ] **P29 — Curie Temperature Demonstrator**  
  Thermocouple slot + heat stand. Heats nickel to its Curie point showing loss of ferromagnetism. Advanced physics content with high shareability.

---

## ⚙️ Productivity + ADHD-Aligned Workspace Tools

- [ ] **P30 — Physical Kanban Rail (Print Queue Board)**  
  Wall-mount rail with magnetic card clips: QUEUE / ACTIVE / DONE. Mirrors `djinn-confirm-print` queue state in physical space visible at a glance.

- [ ] **P31 — Forge Shutdown Checklist Sign Stand**  
  Laminated card holder: power off Calliope → log orders → run `djinn-sync` → vault check. Closing ritual in physical form. Prevents queue drops on ADHD context-switch days.

- [ ] **P32 — Gridfinity Vault for Hardware (M3/M4/M5)**  
  Full Gridfinity baseplate system for screws, heat-set inserts, magnets. Every hardware component has a labeled magnetic-snap bin.

- [ ] **P33 — Pomodoro Timer Stand (Eye-Level, Weighted)**  
  Fixed-angle weighted phone stand at eye level for Pomodoro sessions. Pairs with Faust CLI timing for focus blocks during commission batching.

- [ ] **P34 — Modular Magnetic Tool Wall (French Cleat System)**  
  Full wall system with magnetic snap-on holders for calipers, spatulas, flush cutters, hex keys. Everything off the desk = focused work surface for filming.

- [ ] **P35 — ADHD Fidget Dock (Desk Integrated)**  
  Clickable slider or spinning disc mechanism in a weighted base with a permanent desk home. It doesn't get lost because it can't leave the base. Authentic ADHD content angle.

---

## 📅 Priority Start Order

| Day | Project | Unlocks |
|-----|---------|---------|
| Day 1 | P02 — Filament Runout Sensor | Moonraker automation + educational content simultaneously |
| Day 1 | P15 — Overhead Camera Gantry | Every future print becomes filmable; feeds the media pipeline |
| Day 2 | P30 — Kanban Rail | Queue visibility; ADHD workflow immediately improved |
| Day 3 | P22 — Halbach Array Kit | First pure educational episode |
| Day 4 | P13 — API Status Light | Infrastructure content + actual forge monitoring value |

---

## Material Notes

- **Default filament:** PETG (all structural forge pieces and accessories)
- **Premium/functional:** ABS (high-detail commissions, heat-adjacent parts)
- **Prototype only:** PLA
- **Post-processing:** Cerakote for cannabis accessories and heat-adjacent parts; XTC-3D epoxy for decorative/tray pieces

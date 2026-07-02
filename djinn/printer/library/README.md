# Typhon's Forge — Model Library

## ⚠️ Binary files moved 2026-07-01

The actual STL/3MF/gcode library (formerly `~/printer-files/library/` on Salomon, 3.9G) has
moved to **Typhon** at `C:\Forge\models\library` (reachable over Tailscale,
`ssh typhon@100.69.41.74`), matching Typhon's role as the shop/slicing machine. `Desktop/Review`
also moved to `C:\Forge\models\review`. Historical/archival material
(`printer-files/archive/`, `printer-files/vault-printer/`, and low-value calibration/staging
files) moved to **Oroborus** (`192.168.1.154:~/print-library-archive/`) as cold storage.

Salomon keeps only: this metadata (reports, index.json), and the confirmed-working
Penelope/Calliope files needed for actual print execution (mario pipe, Forge coins, proxy
recycler — see `UNCONFIRMED-PRINTS.md` for everything else's status).

**Camood files were entirely excluded from this migration** — left exactly where they were,
untouched, since that piece is under active troubleshooting.

Full migration detail: `logs/reports/2026-07-01_print-library-migration.md`.

## Directory Structure (historical — describes the old Salomon-local layout)

```
printer-files/library/          [now on Typhon: C:\Forge\models\library]
├── originals/
│   ├── external/       ← Cults3D, Thingiverse, MakerWorld — untouched originals
│   ├── terp-tribe/     ← Terp Tribe community designs
│   └── forge/          ← Typhon's Forge originals (Javier's)
└── cored/
    ├── external/       ← bored + marked, print-ready (external source)
    ├── terp-tribe/     ← bored + marked (Terp Tribe)
    └── forge/          ← bored + marked (forge originals)

Obsidian/djinn/printer/library/
├── index.json          ← machine-readable attribution manifest
├── README.md           ← this file
├── UNCONFIRMED-PRINTS.md ← checklist of pieces needing print-outcome confirmation
└── pieces/             ← per-piece human-readable reports
    └── <id>.md
```

## Categories

| Category | Source | Commercial Use |
|----------|--------|----------------|
| `external` | Downloaded — Cults3D, Thingiverse, etc. | **Must verify license per piece** |
| `terp-tribe` | Terp Tribe community | **Governed by Terp Tribe agreement** |
| `forge` | Typhon's Forge originals | Unrestricted — Javier owns these |

## Compliance Rule

**Never list an `external` piece for sale until `compliance_status` in `index.json` is `verified-commercial`.**

The workflow:
1. Download model → save to `originals/external/` — **do not modify the original**
2. Run `djinn-bore-core` → output goes to `cored/external/`
3. Create piece report in `pieces/<id>.md`
4. Add entry to `index.json` — set `compliance_status: pending-review`
5. Visit the source URL, record designer and license
6. If commercial-ok: update `compliance_status: verified-commercial`, fill attribution block
7. If personal-only: update `compliance_status: verified-personal-only` — piece is display/personal only

## Adding a New Piece

```bash
# 1. Save original (use the Cults3D slug or a clean name as the ID)
cp downloaded.stl ~/printer-files/library/originals/external/<id>_original.stl

# 2. Core it
djinn-bore-core ~/printer-files/library/originals/external/<id>_original.stl \
  --output ~/printer-files/library/cored/external/<id>_cored.stl

# 3. Create piece report: copy pieces/applacrabus.md as template
# 4. Add entry to index.json

# For Terp Tribe pieces: use terp-tribe/ subdirs
# For forge originals: use forge/ subdirs — no attribution step needed
```

## Registered Pieces

| ID | Name | Platform | Creator | License | Shop OK? |
|----|------|----------|---------|---------|----------|
| applacrabus | Applacrabus (Apple w/ Crab Claws) | Cults3D | Midnight3DPrinting | CC BY-SA 4.0 | ✅ with credit |
| tardis | Doctor Who TARDIS | Cults3D | LuliasMartch | CC BY 4.0 | ✅ with credit |
| puffco-proxy-tornadocycler | Puffco Proxy Tornadocycler | Cults3D | FabrizioCreations | Cults PU / No AI | ❌ personal only |
| puffco-proxy-stand-joshtf | Puffco Proxy Stand | Printables | joshtf | All Rights Reserved | ❌ personal only |
| puffco-proxy-toilet-cup | Proxy Core Toilet Cup | MakerWorld | PENDING | PENDING | ⚠ unknown |
| puffco-proxy-travel-pack | Proxy All-in-One Travel Pack | MakerWorld | PENDING | PENDING | ⚠ unknown |
| duff-beer-pen-holder | Duff Beer Pen Holder | MakerWorld | PENDING | PENDING | ⚠ unknown |
| doctor-pen-holder | Doctor Pen Holder / Lab Coat | MakerWorld | PENDING | PENDING | ⚠ unknown |

**MakerWorld note:** Bambu Lab blocks all automated fetching — requires a logged-in browser session. Open both URLs manually to complete the pending entries.

*Update this table when adding pieces.*

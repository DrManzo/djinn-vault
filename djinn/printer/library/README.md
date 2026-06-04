# Typhon's Forge — Model Library

## Directory Structure

```
printer-files/library/
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
| puffco-proxy-tornadocycler | Puffco Proxy Tornadocycler | Cults3D | FabrizioCreations | Cults PU / No AI | ❌ personal only |
| puffco-proxy-stand-joshtf | Puffco Proxy Stand | Printables | joshtf | All Rights Reserved | ❌ personal only |
| puffco-proxy-toilet-cup | Proxy Core Toilet Cup | MakerWorld | PENDING | PENDING | ⚠ unknown |
| puffco-proxy-travel-pack | Proxy All-in-One Travel Pack | MakerWorld | PENDING | PENDING | ⚠ unknown |

**MakerWorld note:** Bambu Lab blocks all automated fetching — requires a logged-in browser session. Open both URLs manually to complete the pending entries.

*Update this table when adding pieces.*

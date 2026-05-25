# Typhon's Forge — Hashtag Bank

Curated, categorized hashtag library for all Typhon's Forge content.
Maintained by `hashtag-agent`. Updated weekly via `djinn-hashtag-update`.

## Structure

```
hashtag-bank/
├── 3d-printing/
│   ├── general.md       — core printing tags
│   ├── materials.md     — pla, petg, resin, filament
│   ├── tools.md         — prusa, bambu, orca, ender
│   └── community.md     — maker, makerspace, diy
├── cannabis/
│   ├── general.md       — broad + mid + micro + shadowban notes
│   ├── culture.md       — lifestyle, stoner culture
│   ├── education.md     — science, advocacy (safer on Instagram)
│   └── industry.md      — business, products, accessories
├── typhons-forge/
│   └── brand.md         — brand tags, always include #typhonsforge
├── crossover/
│   └── maker-culture.md — 3D printing + cannabis intersection
└── platform-rules/
    └── instagram.md     — limits, shadowban risks, rotation strategy
```

## How publish-prep uses this

`djinn-media-publish-prep` reads all files in this bank and passes them
to the caption LLM with the rotation strategy. The LLM selects a mix of
broad + mid + micro + brand tags appropriate for the post type.

## Updating

```bash
djinn-hashtag-update --research     # agent searches for trending tags, proposes additions
djinn-hashtag-update --add "#newtag" --category cannabis/culture --tier micro
djinn-hashtag-update --report       # show current bank stats
```

Or trigger from OpenClaw: `hashtags update` / `hashtags report`

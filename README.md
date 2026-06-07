# Djinn Vault — Obsidian Configuration

This vault serves as Djinn's memory and knowledge layer. It integrates with the LBlack script production pipeline and feeds context to the Djinn system.

## Structure

```
Obsidian/
├── .obsidian/              # Obsidian app config
├── inbox/                  # Quick capture — raw ideas, voice memos, fleeting thoughts
├── scripts/                # Video script production pipeline (LBlack integration)
│   ├── 01-prompt/          # Prompts sent to Ollama for drafting
│   ├── 02-draft/           # First-pass AI output
│   ├── 03-grammar-check/   # script-check.sh reports and feedback
│   ├── 04-links/           # Reference URLs, source links
│   ├── 05-resources/       # PDFs, images, benchmarks, screenshots
│   ├── 06-research/        # Notes on things to investigate before recording
│   ├── 07-review/          # Self-review checklists, revision notes
│   └── 08-final/           # Ready-to-record scripts
│       └── video-name/
│           ├── script.md
│           └── architecture.md
├── djinn/                  # Djinn's operational memory
│   ├── decisions/          # Architecture Decision Records
│   ├── projects/           # Active project context notes
│   ├── research/           # Domain research notes
│   ├── people/             # Relationship notes
│   └── logs/               # Session summaries, interaction logs
└── references/             # Permanent reference library
```

## Script Pipeline Workflow

1. **Capture** — Drop raw ideas into `inbox/`
2. **Prompt** — Move to `scripts/01-prompt/`, write the Ollama prompt using a template
3. **Draft** — Run the prompt, save output to `scripts/02-draft/`
4. **Check** — Run `script-check.sh`, save report to `scripts/03-grammar-check/`
5. **Research** — Add links and resources to `scripts/04-links/` and `scripts/05-resources/`
6. **Investigate** — Note things to research in `scripts/06-research/`
7. **Review** — Self-review in `scripts/07-review/`
8. **Final** — Move to `scripts/08-final/video-name/` when ready to record

## Djinn Integration

The `djinn/` directory feeds context to the Djinn system:
- `decisions/` — Why certain architectural choices were made
- `projects/` — Current state of each project (Meanas, Faust, Source Keeper, etc.)
- `research/` — Domain-specific notes (psychology, law, cyber, finance)
- `people/` — Relationship context (Mira, Mira, sponsor, etc.)
- `logs/` — Session summaries of Djinn interactions

## Naming Conventions

- **Files:** `kebab-case.md`
- **Directories:** `kebab-case/`
- **Tags:** `#domain/subdomain` (e.g., `#psychology/shadow-work`, `#business/meanas`)
- **Links:** `[[Internal Link]]` for cross-references

## Tags

- `#script/draft` — Script in draft stage
- `#script/review` — Script under review
- `#script/final` — Script ready to record
- `#djinn/decision` — Architecture decision
- `#djinn/memory` — Persistent fact
- `#research/active` — Active research topic
- `#project/meanas` — Meanas-related
- `#project/faust` — Faust CLI-related
- `#project/source-keeper` — Source Keeper-related
- `#project/citeassist` — CiteAssist-related

# djinn/personal — PA Layer Phase Beta

**Tasks implemented:** TASK-075 through TASK-079  
**Commit date:** 2026-06-16  
**Status:** Ready for local deployment on Salomon

---

## Setup

### 1. Run the migration

```bash
cd ~/djinn-personal-db   # or wherever personal.db lives
python3 ~/djinn-vault/djinn/personal/db/migrate_v2.py
```

This creates all Phase Beta tables and adds `entry_source` to `black_book_log`.
Safe to re-run — fully idempotent.

### 2. Wire the handlers into your gateway bot

In your `djinn-personal-gateway/bot.py`, add:

```python
import sys
sys.path.insert(0, "/path/to/djinn-vault")  # adjust to your vault path

from djinn.personal.gateway_handlers import register_handlers

# After: application = Application.builder().token(TOKEN).build()
register_handlers(application)
```

That replaces manual handler registration for all Phase Beta commands.

### 3. Update djinn-morning to use the new briefing composer

```python
from djinn.personal.modules.briefing import compose_brief_with_buttons

msg = compose_brief_with_buttons()
# send msg['text'] with msg['buttons'] as inline keyboard
```

---

## Module Map

| Module | Task | What it does |
|--------|------|--------------|
| `modules/db.py` | all | Shared SQLite connection |
| `modules/deadlines.py` | TASK-075 | GCU deadline engine, LSAT tracker |
| `modules/blackbook.py` | TASK-076 | Low-friction `/log`, gated `/reflect` |
| `modules/flare.py` | TASK-077 | Colitis flare flag, health log |
| `modules/recovery.py` | TASK-078 | Step work, craving log, meeting attendance |
| `modules/creative.py` | TASK-079 | Writing sessions, Aethoria streak, gym |
| `modules/briefing.py` | all | Morning brief composer (integrates all modules) |
| `gateway_handlers.py` | all | Telegram command handlers |
| `db/schema_v2.sql` | all | Phase Beta SQLite schema |
| `db/migrate_v2.py` | all | One-time migration script |

---

## New Commands

| Command | Task | What it does |
|---------|------|--------------|
| `/school` | 075 | Full 7-day academic deadline view |
| `/deadline add COURSE "label" YYYY-MM-DD` | 075 | Add one-time deadline |
| `/deadline done ID` | 075 | Mark deadline complete |
| `/lsat` | 075 | LSAT week status |
| `/lsat done LR` | 075 | Log LSAT session |
| `/lsat goal text` | 075 | Set week LSAT goal |
| `/log text` | 076 | Zero-friction Black Book entry |
| `/reflect` | 076 | Ollama reflection question (gated at 3+ entries) |
| `/flare` | 077 | Flag colitis flare day (quiet mode) |
| `/flare clear` | 077 | Clear flare flag |
| `/health` | 077 | Health summary |
| `/weight 238.5` | 077 | Log weight (never in briefing) |
| `/step` | 078 | Step work status |
| `/step start N` | 078 | Start working step N |
| `/step done` | 078 | Advance to next step |
| `/sponsor_contact note` | 078 | Log sponsor contact |
| `/craving 7 tag` | 078 | Log craving (local only) |
| `/craving week` | 078 | Ollama craving pattern (local only) |
| `/meeting attended` | 078 | Log meeting attendance |
| `/meeting missed` | 078 | Log missed meeting |
| `/meeting week` | 078 | Week attendance view |
| `/write 30 note` | 079 | Log writing session |
| `/aethoria` | 079 | Aethoria streak + week status |
| `/aethoria_goal text` | 079 | Set week writing goal |
| `/gym` | 079 | Log trainer session |

---

## Design Constraints Honored

- **Local-first always** — craving log, step notes, Black Book entries, health flags never touch cloud LLM
- **Ollama only** for `/reflect` and `/craving week` private content
- **One Telegram bot** — all handlers register into existing `djinn-personal-gateway`
- **Morning brief ≤ 90 words** — hard cap enforced in `briefing.py`
- **One action item per morning** — briefing composer picks highest-priority item
- **Flare day = quiet mode** — all streaks pause, no guilt signals
- **ADHD-safe** — `/log` is one step, `/gym` is one tap, `/craving` is three seconds
- **People tracking suspended** — not in any module this cycle

---

*— Marcus | 2026-06-16 | TASK-075–079*

# forge/queue/ — deprecated (2026-07-12)

This markdown-file queue mechanism is superseded by the unified shop
dashboard's `orders` table in `~/.local/share/djinn-shop/shop.db`, served
at the dashboard's `/queue` and `/orders` routes. Nothing in `forge/shop/`
or `~/.local/bin/djinn-*` reads or writes this directory anymore (verified
2026-07-12) — it's dead infrastructure, not actively used.

One leftover file, `print_20260624_000249.md`, records a `mario-pipe-marked.stl`
job as `status: queued` from 2026-06-24 with no completion entry — looks
orphaned at first glance, but it isn't: `forge/prints/` shows that file was
printed at least seven times since, as recently as 2026-07-12 (today). The
job was fulfilled; this queue entry is just a dead record from before this
directory stopped being read. Left in place as a historical artifact, not
deleted.

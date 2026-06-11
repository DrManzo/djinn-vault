"""synapsis.py — Cross-reference observations to vault entries.

For each incoming observation, synapsis looks up related vault notes
by domain/event keyword and generates backlinks via linker.py.

This is intentionally a stub in the initial POC — flesh out once
you have a corpus of real observations to cross-reference against.
"""

from pathlib import Path

VAULT_BASE = Path.home() / "Obsidian" / "djinn" / "hellhound"


def cross_reference(obs: dict) -> list[str]:
    """
    Given an observation dict, return a list of vault note paths
    that are related to this observation.

    Current strategy: simple keyword scan of vault filenames.
    Future: embed + vector search, or sqlite FTS.
    """
    domain = obs.get("domain", "").lower()
    event  = obs.get("event",  "").lower()
    keywords = {domain, event} - {""}   # nonempty only

    matches = []
    for md_file in VAULT_BASE.rglob("*.md"):
        stem = md_file.stem.lower()
        if any(kw in stem for kw in keywords):
            matches.append(str(md_file))

    return matches

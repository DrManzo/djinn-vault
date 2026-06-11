"""linker.py — Generate backlinks between related vault entries.

Called by synapsis when cross_reference() finds related notes.
Appends a backlink block to the target note if not already present.
"""

from pathlib import Path


def maybe_backlink(source_note: Path, target_path: str) -> None:
    """
    Add a backlink from source_note → target_path in the target file.
    Idempotent: will not add the same backlink twice.
    """
    target = Path(target_path)
    if not target.exists():
        return

    backlink = f"[[{source_note.stem}]]"
    content  = target.read_text()

    if backlink in content:
        return   # already linked

    # Append backlinks section
    if "## Backlinks" not in content:
        content += "\n## Backlinks\n"
    content += f"- {backlink}\n"
    target.write_text(content)

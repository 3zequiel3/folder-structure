"""Materialize a tree dict into directories on disk."""
from pathlib import Path


def materialize(node, base):
    """Create `base` and everything under `node`.

    A falsy node ({} or None) is a leaf directory and receives a `.gitkeep`.
    Returns the list of `.gitkeep` Paths created.
    """
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    if not node:
        gitkeep = base / ".gitkeep"
        gitkeep.touch()
        return [gitkeep]
    created = []
    for name, children in node.items():
        created += materialize(children, base / name)
    return created

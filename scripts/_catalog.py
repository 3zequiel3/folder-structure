"""Load catalog fragments from references/."""
from pathlib import Path
import yaml

REFS = Path(__file__).resolve().parent.parent / "references"


class CatalogError(Exception):
    """Raised on a missing/invalid catalog fragment or unknown selection."""


def load_yaml(path):
    path = Path(path)
    if not path.exists():
        raise CatalogError(f"missing fragment: {path}")
    data = yaml.safe_load(path.read_text()) or {}
    if not isinstance(data, dict):
        raise CatalogError(f"fragment is not a mapping: {path}")
    return data


def load_architecture(side, name):
    return load_yaml(REFS / "architectures" / side / f"{name}.yaml")


def load_stack(side, name):
    return load_yaml(REFS / "stacks" / side / f"{name}.yaml")


def load_topologies():
    return load_yaml(REFS / "topologies.yaml")

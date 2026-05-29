import _catalog
from _catalog import REFS


def _arch_slot_names(side):
    names = set()
    for f in (REFS / "architectures" / side).glob("*.yaml"):
        names |= set((_catalog.load_yaml(f).get("slots") or {}).keys())
    return names


def test_every_stack_injects_into_a_known_slot():
    for side in ("backend", "frontend"):
        known = _arch_slot_names(side)
        for f in (REFS / "stacks" / side).glob("*.yaml"):
            inject = _catalog.load_yaml(f).get("inject") or {}
            for slot in inject:
                assert slot in known, (
                    f"{side}/{f.name} injects into unknown slot '{slot}' "
                    f"(no {side} architecture defines it) — likely a typo")


def test_every_stack_declares_a_valid_nesting():
    valid = {"feature-first", "layer-first", "flat"}
    for side in ("backend", "frontend"):
        for f in (REFS / "stacks" / side).glob("*.yaml"):
            nesting = _catalog.load_yaml(f).get("nesting")
            assert nesting in valid, f"{side}/{f.name} has invalid nesting '{nesting}'"

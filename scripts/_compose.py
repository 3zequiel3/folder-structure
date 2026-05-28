"""Compose a structure dict from catalog fragments."""
from copy import deepcopy

from _catalog import (CatalogError, load_architecture, load_stack,
                      load_topologies)


def build_slots(arch, stack):
    """Return {slot_name: [dir, ...]} = arch default dirs + best-effort injections."""
    arch_slots = arch.get("slots", {}) or {}
    inject = stack.get("inject", {}) or {}
    slots = {}
    for slot_name, slot_def in arch_slots.items():
        dirs = list((slot_def or {}).get("dirs", []) or [])
        dirs += inject.get(slot_name, [])          # skipped if slot absent
        slots[slot_name] = dirs
    return slots


def _dirs_to_node(dirs):
    return {d: None for d in dirs} if dirs else None


def _slots_node(slots):
    return {name: _dirs_to_node(dirs) for name, dirs in slots.items()}


def compose_side(arch, stack):
    """Build the directory subtree for one side (backend or frontend)."""
    nesting = stack.get("nesting", "feature-first")
    root = stack.get("root", {}) or {}
    base = root.get("base", "src")
    module_token = stack.get("module_token", "modules")
    sn = _slots_node(build_slots(arch, stack))

    base_content = {}
    for extra in root.get("base_extra", []) or []:
        base_content[extra] = None

    if nesting == "feature-first":
        base_content[module_token] = {"{module}": sn}
    elif nesting == "layer-first":
        for slot_name, node in sn.items():
            base_content[slot_name] = {"{module}": node}
    elif nesting == "flat":
        for slot_name, node in sn.items():
            base_content[slot_name] = node
    else:
        raise CatalogError(f"unknown nesting '{nesting}'")

    tree = {base: base_content}
    for scaffold_dir in root.get("scaffold", []) or []:
        if scaffold_dir != base:
            tree.setdefault(scaffold_dir, None)
    return tree

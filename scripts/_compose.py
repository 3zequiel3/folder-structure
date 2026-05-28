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


def mount_at(tree, mount, subtree):
    """Place `subtree` at the `mount` path ('' = merge at root) inside `tree`."""
    if not mount:
        merged = dict(tree)
        merged.update(subtree)
        return merged
    parts = mount.split("/")
    node = tree
    for part in parts[:-1]:
        child = node.get(part)
        if not isinstance(child, dict):
            child = {}
            node[part] = child
        node = child
    node[parts[-1]] = subtree
    return tree


def compose(selections):
    """Build a structure dict {'root': str, 'tree': node} from user selections.

    selections = {
      'root': str, 'topology': str,
      'backend': {'arch': str, 'stack': str, 'nesting': str?}?,
      'frontend': {'arch': str, 'stack': str, 'nesting': str?}?,
    }
    """
    topo_name = selections["topology"]
    topologies = load_topologies()
    if topo_name not in topologies:
        raise CatalogError(f"unknown topology '{topo_name}'")
    topo = topologies[topo_name] or {}

    sides = [s for s in ("backend", "frontend") if selections.get(s)]
    max_sides = topo.get("max_sides")
    if max_sides is not None and len(sides) > max_sides:
        raise CatalogError(
            f"topology '{topo_name}' allows at most {max_sides} side(s), got {len(sides)}")

    tree = deepcopy(topo.get("scaffold", {}) or {})
    mounts = topo.get("mounts", {}) or {}

    for side in sides:
        sel = selections[side]
        arch = load_architecture(side, sel["arch"])
        stack = load_stack(side, sel["stack"])
        if sel.get("nesting"):
            stack = {**stack, "nesting": sel["nesting"]}
        subtree = compose_side(arch, stack)
        tree = mount_at(tree, mounts.get(side, ""), subtree)

    return {"root": selections["root"], "tree": tree}

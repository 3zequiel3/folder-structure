"""folder-structure CLI: compose a folder tree from the catalog, or materialize one."""
import argparse
import sys
from pathlib import Path

import yaml

from _compose import compose
from _materialize import materialize


def render_tree(node, prefix=""):
    """Return ASCII lines for a tree node (dirs only)."""
    lines = []
    if not node:
        return lines
    items = list(node.items())
    for i, (name, child) in enumerate(items):
        last = i == len(items) - 1
        lines.append(prefix + ("└── " if last else "├── ") + name + "/")
        lines += render_tree(child, prefix + ("    " if last else "│   "))
    return lines


def _selections_from_args(args):
    selections = {"root": args.root, "topology": args.topology}
    if args.backend_arch and args.backend_stack:
        selections["backend"] = {"arch": args.backend_arch, "stack": args.backend_stack}
        if args.backend_nesting:
            selections["backend"]["nesting"] = args.backend_nesting
    if args.frontend_arch and args.frontend_stack:
        selections["frontend"] = {"arch": args.frontend_arch, "stack": args.frontend_stack}
        if args.frontend_nesting:
            selections["frontend"]["nesting"] = args.frontend_nesting
    return selections


def _check_pair(arch, stack, side):
    if bool(arch) != bool(stack):
        raise SystemExit(
            f"error: --{side}-arch and --{side}-stack must be provided together")


def cmd_compose(args):
    _check_pair(args.backend_arch, args.backend_stack, "backend")
    _check_pair(args.frontend_arch, args.frontend_stack, "frontend")
    structure = compose(_selections_from_args(args))
    if args.out:
        Path(args.out).write_text(yaml.safe_dump(structure, sort_keys=False))
    print(f"root: {structure['root']}")
    for line in render_tree(structure["tree"]):
        print(line)
    return 0


def cmd_materialize(args):
    try:
        data = yaml.safe_load(Path(args.from_yaml).read_text())
    except yaml.YAMLError as exc:
        print(f"error: invalid YAML in {args.from_yaml}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(data, dict) or "root" not in data or "tree" not in data:
        print(f"error: {args.from_yaml} must contain 'root' and 'tree' keys",
              file=sys.stderr)
        return 1
    target = Path(args.into) / data["root"]
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"error: target {target} is not empty (use --force)", file=sys.stderr)
        return 1
    created = materialize(data["tree"], target)
    print(f"created {len(created)} leaf dirs under {target}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="scaffold")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compose", help="compose a structure.yaml from selections")
    c.add_argument("--root", required=True)
    c.add_argument("--topology", required=True)
    c.add_argument("--backend-arch")
    c.add_argument("--backend-stack")
    c.add_argument("--backend-nesting")
    c.add_argument("--frontend-arch")
    c.add_argument("--frontend-stack")
    c.add_argument("--frontend-nesting")
    c.add_argument("--out")
    c.set_defaults(func=cmd_compose)

    m = sub.add_parser("materialize", help="create dirs from a structure.yaml")
    m.add_argument("--from-yaml", required=True, dest="from_yaml")
    m.add_argument("--into", default=".")
    m.add_argument("--force", action="store_true")
    m.set_defaults(func=cmd_materialize)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

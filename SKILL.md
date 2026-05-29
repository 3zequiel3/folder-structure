---
name: folder-structure
description: >
  Use when starting a new project and the user wants to create the folder
  structure for a backend and/or frontend. Interviews the user about stack and
  architecture, composes the optimal folder tree from a catalog, lets the user
  edit it, then creates the directories. Triggers on "armá la estructura de
  carpetas", "scaffold the folders", "qué estructura uso para X", "create the
  project structure".
---

# folder-structure

Interview the user, compose a folder tree from the catalog, negotiate it over a
`structure.yaml`, then materialize it. Output is **directories only** (with
`.gitkeep`) — never code or config file contents.

## Interview (one question at a time)

1. **Scope:** frontend, backend, or both?
2. **Topology:** single app, monorepo (Turborepo), or cross-language
   (`frontend/` + `backend/`, e.g. Next + FastAPI)? Recommend a default from the
   scope and stacks and say why; only show the menu if they want to deviate.
3. **Per backend:** technology (fastapi / nestjs / express) → architecture
   (layered / clean / hexagonal). Explain that `clean` separates
   `domain/application/infrastructure/presentation` (entity ≠ ORM model) while
   `layered` is the flat package-by-feature module.
4. **Per frontend:** technology (next / react-vite) → pattern (feature-based /
   fsd / atomic / container-presentational).
5. **Nesting** (backend only): organize by feature (screaming) or by technical
   layer? Sets `--backend-nesting feature-first|layer-first`.
6. **Example module (optional):** want a concrete example module instead of the
   `{module}` placeholder? If so, name it (e.g. `users`) → sets `--example-module <name>`.
   Otherwise leave the `{module}` template for the user to rename.

## Compose, show, negotiate

Run from the skill directory:

```bash
python scripts/scaffold.py compose \
  --root <project-name> --topology <topology> \
  --backend-arch <arch> --backend-stack <stack> [--backend-nesting <n>] \
  --frontend-arch <arch> --frontend-stack <stack> \
  [--example-module <name>] \
  --out structure.yaml
```

Show the printed tree. Let the user edit `structure.yaml` directly (or edit it
for them on request). A `null`/empty node is a leaf dir that will get `.gitkeep`.
The `"{module}"` placeholder is a template — duplicate and rename it per real
feature (e.g. `users`, `orders`) before materializing.

## Materialize

Once approved:

```bash
python scripts/scaffold.py materialize --from-yaml structure.yaml --into .
```

It refuses to write into a non-empty target unless `--force` is passed.

## Novel stack not in the catalog

If `--*-stack <x>` errors with "missing fragment", the stack is not in the
catalog. Look up its idiomatic structure in official docs (context7), write a new
fragment under `references/stacks/<side>/<x>.yaml` following the existing ones,
and TELL THE USER this fragment is new and lower-confidence. Do not invent
structure from generic web search.

## Catalog reference

- `references/architectures/{backend,frontend}/*.yaml` — define named layer
  *slots* (the architecture's authority).
- `references/stacks/{backend,frontend}/*.yaml` — declare `nesting`, root layout,
  and `inject` dirs per slot.
- `references/topologies.yaml` — root wrapper + mount points.

Adding a stack or architecture is one new fragment — the script composes any
combination. See `docs/superpowers/specs/2026-05-28-folder-structure-design.md`.

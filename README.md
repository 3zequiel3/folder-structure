# folder-structure

A Claude Code skill that interviews you about your stack and architecture, then
scaffolds the **optimal folder tree** for your project. Output is **directories
only** (with `.gitkeep` so git tracks them) — never code or config file contents.

The "best structure" is not improvised on each run: architecture layouts
(clean / hexagonal / layered, feature-based / FSD / atomic / container-presentational)
are **baked into a catalog**. The composition is deterministic; the model only
runs the interview and the negotiation.

## How it works

Composition is **three orthogonal overlays**, applied in order:

```
TOPOLOGY            →  ARCHITECTURE         →  STACK
(root wrapper)         (defines layer slots)   (injects dirs into slots +
                                                nesting strategy)
```

- **Topology** — the repo shape: `single-app`, `monorepo-turborepo`, or
  `cross-lang` (`frontend/` + `backend/`).
- **Architecture** — defines the named *layer slots* (the authority on structure).
  Backend: `clean`, `hexagonal`, `layered`. Frontend: `feature-based`, `fsd`,
  `atomic`, `container-presentational`.
- **Stack** — declares the `nesting` strategy (`feature-first` / `layer-first` /
  `flat`) and *injects* framework dirs into the architecture's slots.
  Backend: `fastapi`, `nestjs`, `express`. Frontend: `next`, `react-vite`.

The slot contract is ports-and-adapters applied to the tool itself: architecture
fragments **define** slot names, stack fragments **reference** them to inject dirs.

Two phases: **compose** (produce a `structure.yaml` and print the tree, no disk
writes) and **materialize** (create the directories from the agreed YAML). The
negotiation always happens over the editable `structure.yaml`.

> `clean` ≠ `layered`. `clean` separates `domain / application / infrastructure /
> presentation` (the domain entity is distinct from the ORM model, enforced by the
> folder boundary). `layered` is the flat package-by-feature module
> (`router / service / uow / repository / model / schemas`). Screaming Architecture
> is not a separate option — it is `nesting: feature-first`.

## Usage

### As a Claude Code skill

Ask Claude to scaffold a project structure (e.g. *"armá la estructura de carpetas
para un backend FastAPI con clean architecture"*). The skill runs the interview,
shows the tree, lets you edit it, and creates the directories.

### As a CLI

Requires Python 3.11+ and PyYAML (`pip install -r requirements.txt`).

Compose a tree and write the contract:

```bash
python scripts/scaffold.py compose \
  --root my-api --topology single-app \
  --backend-arch clean --backend-stack fastapi --backend-nesting feature-first \
  --out structure.yaml
```

Edit `structure.yaml` if you want (a `null` node is a leaf dir that gets
`.gitkeep`; `"{module}"` is a template — duplicate and rename it per real feature),
then materialize:

```bash
python scripts/scaffold.py materialize --from-yaml structure.yaml --into .
```

`materialize` refuses to write into a non-empty target unless `--force` is given.

#### Example — `clean` + `fastapi`, feature-first

```
my-api/
└── app/
    ├── config/
    └── modules/
        └── {module}/
            ├── domain/         (entities, value-objects)
            ├── application/    (use-cases, ports, dtos)
            ├── infrastructure/ (repositories, models, uow, db)
            └── presentation/   (routers)
└── tests/
```

## Repository layout

```
SKILL.md                  # skill entry: interview flow + invocation
requirements.txt          # pyyaml, pytest
scripts/
  scaffold.py             # CLI (compose / materialize)
  _compose.py             # three-overlay merge engine
  _catalog.py             # fragment loaders + CatalogError
  _materialize.py         # tree dict -> dirs + .gitkeep
references/
  topologies.yaml
  architectures/{backend,frontend}/*.yaml   # define layer slots
  stacks/{backend,frontend}/*.yaml          # inject dirs + nesting
```

## Extending the catalog

Adding a stack or architecture is **one new YAML fragment** — the engine composes
any combination. For a stack not yet in the catalog, look up its idiomatic layout
in the official docs, add `references/stacks/<side>/<name>.yaml` following the
existing fragments, and you are done.

## Roadmap

- **v1.1:** more fragments — `go`, `spring-boot` (backend); `vue`, `nuxt`,
  `angular` (frontend); `monorepo-nx` (topology).
- **v2:** deployment axis — Docker / Vercel file placement.

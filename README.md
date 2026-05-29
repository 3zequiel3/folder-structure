# folder-structure

Una skill de Claude Code que te entrevista sobre tu stack y tu arquitectura y luego
genera el **árbol de carpetas óptimo** para tu proyecto. La salida es **solo
directorios** (con `.gitkeep` para que git los rastree); nunca código ni contenido de
archivos de configuración.

La "mejor estructura" no se improvisa en cada corrida: los layouts de arquitectura
(clean / hexagonal / layered, feature-based / FSD / atomic / container-presentational)
están **codificados en un catálogo**. La composición es determinista; el modelo solo
conduce la entrevista y la negociación.

## Cómo funciona

La composición son **tres capas ortogonales**, aplicadas en orden:

```
TOPOLOGÍA           →  ARQUITECTURA        →  STACK
(envoltorio raíz)      (define los slots)     (inyecta dirs en los slots +
                                               estrategia de nesting)
```

- **Topología** — la forma del repo: `single-app`, `monorepo-turborepo` o
  `cross-lang` (`frontend/` + `backend/`).
- **Arquitectura** — define los *slots de capa* con nombre (la autoridad sobre la
  estructura). Backend: `clean`, `hexagonal`, `layered`. Frontend: `feature-based`,
  `fsd`, `atomic`, `container-presentational`.
- **Stack** — declara la estrategia de `nesting` (`feature-first` / `layer-first` /
  `flat`) e *inyecta* los directorios del framework en los slots de la arquitectura.
  Backend: `fastapi`, `nestjs`, `express`. Frontend: `next`, `react-vite`.

El contrato de slots es puertos-y-adaptadores aplicado a la propia herramienta: los
fragmentos de arquitectura **definen** los nombres de slot, y los fragmentos de stack
los **referencian** para inyectar directorios.

Dos fases: **compose** (produce un `structure.yaml` e imprime el árbol, sin escribir en
disco) y **materialize** (crea los directorios a partir del YAML acordado). La
negociación siempre ocurre sobre el `structure.yaml` editable.

> `clean` ≠ `layered`. `clean` separa `domain / application / infrastructure /
> presentation` (la entidad de dominio es distinta del modelo ORM, forzado por el
> límite de carpeta). `layered` es el módulo plano por feature
> (`router / service / uow / repository / model / schemas`). Screaming Architecture
> no es una opción aparte: es `nesting: feature-first`.

## Uso

### Como skill de Claude Code

Pídele a Claude que arme la estructura de un proyecto (por ejemplo: *"armá la
estructura de carpetas para un backend FastAPI con clean architecture"*). La skill
conduce la entrevista, muestra el árbol, permite editarlo y crea los directorios.

### Como CLI

Requiere Python 3.11+ y PyYAML (`pip install -r requirements.txt`).

Componer un árbol y escribir el contrato:

```bash
python scripts/scaffold.py compose \
  --root my-api --topology single-app \
  --backend-arch clean --backend-stack fastapi --backend-nesting feature-first \
  --out structure.yaml
```

Pasa `--example-module users` para materializar un módulo concreto `users/` en lugar
del placeholder `{module}`.

Edita el `structure.yaml` si lo necesitas (un nodo `null` es un directorio hoja que
recibe `.gitkeep`; `"{module}"` es una plantilla: duplícala y renómbrala por cada
feature real), y luego materializa:

```bash
python scripts/scaffold.py materialize --from-yaml structure.yaml --into .
```

`materialize` se niega a escribir en un destino no vacío salvo que pases `--force`.

#### Ejemplo — `clean` + `fastapi`, feature-first

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

## Detección brownfield (proyecto existente)

Si el directorio destino ya tiene un scaffold (por ejemplo después de `npm create vite`,
`create-next-app`, o un repo FastAPI existente), ejecuta primero la detección:

```bash
python scripts/scaffold.py detect --into <project-dir>
```

Infiere el framework (`next`, `react-vite`, `fastapi`, `nestjs`, …), el gestor de
paquetes (`pnpm`, `uv`, `npm`, …) y el `source_root` existente (`src`, `app`, …). El
gestor de paquetes es **solo informativo**: no cambia el árbol de carpetas (esta skill
es solo-directorios).

Usa el reporte para pre-llenar la entrevista y omitir las preguntas que ya puedes
responder. Luego materializa la arquitectura sobre el proyecto existente con
`--merge`:

```bash
python scripts/scaffold.py materialize --from-yaml structure.yaml --into <parent-dir> --merge
```

`--merge` hace que materialize sea aditivo: solo crea los directorios que faltan y nunca
sobrescribe nada de lo que ya está.

## Estructura del repositorio

```
SKILL.md                  # entrada de la skill: flujo de entrevista + invocación
requirements.txt          # pyyaml, pytest
scripts/
  scaffold.py             # CLI (compose / materialize / detect)
  _compose.py             # motor de merge de tres capas
  _catalog.py             # carga de fragmentos + CatalogError
  _materialize.py         # árbol dict -> dirs + .gitkeep
  _detect.py              # detección brownfield (framework / package manager / layout)
references/
  topologies.yaml
  architectures/{backend,frontend}/*.yaml   # definen los slots de capa
  stacks/{backend,frontend}/*.yaml          # inyectan dirs + nesting
```

## Extender el catálogo

Agregar un stack o una arquitectura es **un solo fragmento YAML nuevo**: el motor
compone cualquier combinación. Para un stack que todavía no está en el catálogo, busca
su layout idiomático en la documentación oficial, agrega
`references/stacks/<side>/<name>.yaml` siguiendo los fragmentos existentes, y listo.

## Roadmap

- **v1.1:** más fragmentos — `go`, `spring-boot` (backend); `vue`, `nuxt`,
  `angular` (frontend); `monorepo-nx` (topología).
- **v2:** eje de despliegue — ubicación de archivos Docker / Vercel.
```

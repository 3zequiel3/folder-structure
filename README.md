# folder-structure

Skill para armar la **estructura de carpetas óptima** de un proyecto (backend y/o frontend) a partir de tu stack y arquitectura, sin tener que decidir el layout a mano.

---

## ¿Qué hace?

Le pides al agente que arme la estructura, te hace unas pocas preguntas (tecnología, arquitectura) y **crea las carpetas solo** — con `.gitkeep` para que git las rastree. Genera **solo directorios**: nunca código ni archivos de configuración.

La "mejor estructura" no se improvisa: los layouts de arquitectura están **codificados en un catálogo** (clean / hexagonal / layered en backend; feature-based / FSD / atomic / container-presentational en frontend). El agente conduce la entrevista; la composición del árbol es determinista.

Tiene **dos modos** que se activan automáticamente:

- **Greenfield** — proyecto nuevo o vacío: te entrevista de cero (stack → arquitectura) y crea el árbol completo.
- **Brownfield** — proyecto que ya scaffoldeaste (`create-vite`, `create-next-app`, un repo FastAPI…): **detecta** framework, package manager y dónde está tu `src/`, pregunta solo lo que falta (típicamente la arquitectura) y **mete las capas encima sin pisar nada**.

---

## Instalación

```bash
npx skills add https://github.com/3zequiel3/folder-structure
```

La skill queda disponible para tu agente. Se carga automáticamente cuando le pidas armar, crear o scaffoldear la estructura de carpetas.

---

## Uso

### Proyecto nuevo (greenfield)

```
Tu repo:
proyecto/
└── (vacío)

Le decís al agente:
"armá la estructura de carpetas para un backend FastAPI con clean architecture"
```

→ El agente pregunta lo necesario (topología, arquitectura, nesting, y si quieres un módulo de ejemplo), muestra el árbol propuesto, lo ajustas si hace falta, y **crea las carpetas**.

### Proyecto existente (brownfield)

```
Tu repo:
mi-app/
├── package.json        # ya corriste npm create vite
├── pnpm-lock.yaml
└── src/

Le decís al agente:
"armá la estructura feature-based sobre este proyecto"
```

→ El agente **detecta** que es `react-vite` + `pnpm` + `src/`, pregunta solo la arquitectura/patrón, y **agrega las capas dentro de tu `src/` sin tocar lo que ya está** (es aditivo, nunca sobrescribe).

---

## Estructura generada (ejemplo)

`backend` · `fastapi` · `clean` · feature-first:

```
mi-api/
└── app/
    ├── config/
    └── modules/
        └── users/                 # módulo de ejemplo (o {module} como plantilla)
            ├── domain/            # entities, value-objects
            ├── application/       # use-cases, ports, dtos
            ├── infrastructure/    # repositories, models, uow, db
            └── presentation/      # routers
└── tests/
```

El árbol cambia según lo que elijas: `clean` separa las 4 capas (la entidad de dominio es distinta del modelo ORM); `layered` da el módulo plano (`router / service / uow / repository / model / schemas`). "Organizar por feature" (screaming) vs "por capa" se elige en la entrevista.

---

## Por qué esta estructura

- **Determinista, no improvisada**: el mismo stack + arquitectura siempre da el mismo árbol, tomado de un catálogo, no de lo que rankee un blog ese día.
- **El catálogo es la autoridad de arquitectura**: clean/hexagonal/layered con sus capas y reglas de dependencia bien definidas — `clean` ≠ `layered`, y no se confunden.
- **Componible**: agregar un stack o una arquitectura es un solo fragmento YAML; el motor compone cualquier combinación (topología × arquitectura × stack).
- **No invasiva**: solo crea carpetas, nunca pisa archivos. En proyectos existentes se suma a lo que ya hay.

---

## Uso manual (opcional)

No hace falta — el agente corre todo esto por ti. Pero si quieres usarlo a mano (requiere Python 3.11+ y PyYAML):

```bash
# detectar un proyecto existente
python scripts/scaffold.py detect --into <dir>

# componer el árbol (escribe structure.yaml, no toca el disco)
python scripts/scaffold.py compose --root mi-api --topology single-app \
  --backend-arch clean --backend-stack fastapi --example-module users \
  --out structure.yaml

# materializar (crea las carpetas; --merge para sumar sobre un proyecto existente)
python scripts/scaffold.py materialize --from-yaml structure.yaml --into .
```

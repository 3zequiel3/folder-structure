"""Brownfield detection: inspect an existing project directory and report
the detected topology, stacks, package managers, and source roots."""
from __future__ import annotations

import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Package-manager helpers
# ---------------------------------------------------------------------------

def detect_js_package_manager(d: Path) -> str | None:
    """Return the JS package manager based on lockfiles present in d."""
    if (d / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (d / "yarn.lock").exists():
        return "yarn"
    if (d / "bun.lockb").exists():
        return "bun"
    if (d / "package-lock.json").exists():
        return "npm"
    return None


def detect_py_package_manager(d: Path) -> str | None:
    """Return the Python package manager based on lockfiles/config present in d."""
    if (d / "uv.lock").exists():
        return "uv"
    if (d / "poetry.lock").exists():
        return "poetry"
    if (d / "Pipfile.lock").exists() or (d / "Pipfile").exists():
        return "pipenv"
    if (d / "requirements.txt").exists():
        return "pip"
    if (d / "pyproject.toml").exists():
        return "pip"
    return None


# ---------------------------------------------------------------------------
# Single-directory classifier
# ---------------------------------------------------------------------------

def classify_project(d: Path) -> dict | None:
    """Inspect a single directory and return its classification or None.

    Returns a dict with keys: side, stack, package_manager, source_root.
    Returns None if no recognizable project markers exist.
    """
    if not d.is_dir():
        return None

    # --- JS/TS path ---
    pkg_json = d / "package.json"
    if pkg_json.exists():
        try:
            pkg = json.loads(pkg_json.read_text())
        except (json.JSONDecodeError, OSError):
            pkg = {}

        deps: dict = {}
        deps.update(pkg.get("dependencies") or {})
        deps.update(pkg.get("devDependencies") or {})

        side: str | None = None
        stack: str | None = None

        if "next" in deps:
            side = "frontend"
            stack = "next"
        elif "@nestjs/core" in deps:
            side = "backend"
            stack = "nestjs"
        elif "express" in deps:
            side = "backend"
            stack = "express"
        elif "vite" in deps and "react" in deps:
            side = "frontend"
            stack = "react-vite"
        elif "vue" in deps:
            side = "frontend"
            stack = None  # vue not in v1 catalog
        else:
            side = None
            stack = None

        pm = detect_js_package_manager(d)

        # source_root: frontend prefers src then app; backend prefers app then src
        if side == "frontend":
            source_root_candidates = ["src", "app"]
        else:
            source_root_candidates = ["app", "src"]

        source_root: str | None = None
        for candidate in source_root_candidates:
            if (d / candidate).is_dir():
                source_root = candidate
                break

        return {
            "side": side,
            "stack": stack,
            "package_manager": pm,
            "source_root": source_root,
        }

    # --- Python path ---
    py_markers = (d / "pyproject.toml").exists() or (d / "requirements.txt").exists()
    if py_markers:
        text_parts: list[str] = []
        for fname in ("pyproject.toml", "requirements.txt"):
            fpath = d / fname
            if fpath.exists():
                try:
                    text_parts.append(fpath.read_text())
                except OSError:
                    pass
        combined = "\n".join(text_parts)

        stack_py: str | None = "fastapi" if "fastapi" in combined.lower() else None
        pm_py = detect_py_package_manager(d)

        # source_root: backend prefers app then src
        source_root_py: str | None = None
        for candidate in ("app", "src"):
            if (d / candidate).is_dir():
                source_root_py = candidate
                break

        return {
            "side": "backend",
            "stack": stack_py,
            "package_manager": pm_py,
            "source_root": source_root_py,
        }

    # --- Go path ---
    if (d / "go.mod").exists():
        source_root_go: str | None = None
        for candidate in ("app", "src"):
            if (d / candidate).is_dir():
                source_root_go = candidate
                break
        return {
            "side": "backend",
            "stack": "go",  # not in v1 catalog
            "package_manager": "gomod",
            "source_root": source_root_go,
        }

    return None


# ---------------------------------------------------------------------------
# Top-level detect
# ---------------------------------------------------------------------------

def detect(root: Path) -> dict:
    """Inspect *root* and return a detection report.

    Returns:
        {
            "topology": str,
            "backend": dict | None,
            "frontend": dict | None,
            "notes": [str],
        }
    """
    root = Path(root)

    # --- Topology ---
    if (root / "turbo.json").exists():
        topology = "monorepo-turborepo"
    elif (root / "nx.json").exists():
        topology = "monorepo-nx"
    elif (root / "frontend").is_dir() and (root / "backend").is_dir():
        topology = "cross-lang"
    else:
        topology = "single-app"

    # --- Collect dirs to classify ---
    dirs_to_classify: list[Path] = []
    if topology == "cross-lang":
        dirs_to_classify = [root / "frontend", root / "backend"]
    elif topology in ("monorepo-turborepo", "monorepo-nx"):
        apps_dir = root / "apps"
        if apps_dir.is_dir():
            dirs_to_classify = sorted(
                [p for p in apps_dir.iterdir() if p.is_dir()],
                key=lambda p: p.name,
            )
        else:
            dirs_to_classify = [root]
    else:  # single-app
        dirs_to_classify = [root]

    # --- Classify and assign ---
    backend: dict | None = None
    frontend: dict | None = None
    notes: list[str] = []
    any_recognized = False

    for d in dirs_to_classify:
        result = classify_project(d)
        if result is None:
            continue

        any_recognized = True
        side = result["side"]
        stack = result["stack"]
        payload = {
            "stack": stack,
            "package_manager": result["package_manager"],
            "source_root": result["source_root"],
        }

        # Notes for unsupported frameworks
        if side is not None and stack is None:
            # Try to identify the unsupported framework for better messaging
            pkg_json = d / "package.json"
            note_added = False
            if pkg_json.exists():
                try:
                    pkg = json.loads(pkg_json.read_text())
                    deps: dict = {}
                    deps.update(pkg.get("dependencies") or {})
                    deps.update(pkg.get("devDependencies") or {})
                    if "vue" in deps:
                        notes.append("vue detected (not in v1 catalog)")
                        note_added = True
                except (json.JSONDecodeError, OSError):
                    pass
            if not note_added:
                # go stack
                if (d / "go.mod").exists():
                    notes.append("go detected (not in v1 catalog)")
        elif side is None and stack is None:
            # Classified but no side determined — treat as unrecognized
            any_recognized = False

        if side == "backend" and backend is None:
            backend = payload
        elif side == "frontend" and frontend is None:
            frontend = payload

    # Check for go separately — stack "go" is recognized but unsupported
    # Re-pass to catch go notes
    for d in dirs_to_classify:
        if (d / "go.mod").exists() and not (d / "package.json").exists():
            note = "go detected (not in v1 catalog)"
            if note not in notes:
                notes.append(note)

    if not any_recognized:
        notes.append("no recognizable project found")

    return {
        "topology": topology,
        "backend": backend,
        "frontend": frontend,
        "notes": notes,
    }

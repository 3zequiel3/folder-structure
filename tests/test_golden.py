from pathlib import Path

import yaml

import _compose

GOLDEN = Path(__file__).resolve().parent / "golden"

CASES = {
    "clean-fastapi.yaml": {
        "root": "my-api", "topology": "single-app",
        "backend": {"arch": "clean", "stack": "fastapi"},
    },
    "layered-fastapi.yaml": {
        "root": "my-api", "topology": "single-app",
        "backend": {"arch": "layered", "stack": "fastapi"},
    },
    "fsd-react-vite.yaml": {
        "root": "my-web", "topology": "single-app",
        "frontend": {"arch": "fsd", "stack": "react-vite"},
    },
    "monorepo-nestjs-hexagonal-feature.yaml": {
        "root": "my-monorepo", "topology": "monorepo-turborepo",
        "backend": {"arch": "hexagonal", "stack": "nestjs"},
        "frontend": {"arch": "feature-based", "stack": "react-vite"},
    },
}


def test_golden_compose():
    for filename, selections in CASES.items():
        expected = yaml.safe_load((GOLDEN / filename).read_text())
        actual = _compose.compose(selections)
        assert actual == expected, f"mismatch for {filename}"

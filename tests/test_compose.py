import pytest
import _compose
from _catalog import CatalogError


def test_mount_at_root_merges():
    tree = {"packages": {"ui": None}}
    sub = {"app": {"modules": None}, "tests": None}
    out = _compose.mount_at(tree, "", sub)
    assert out == {"packages": {"ui": None}, "app": {"modules": None}, "tests": None}


def test_mount_at_path_creates_intermediate():
    tree = {"packages": {"ui": None}}
    sub = {"src": None}
    out = _compose.mount_at(tree, "apps/api", sub)
    assert out == {"packages": {"ui": None}, "apps": {"api": {"src": None}}}


def test_compose_single_app_backend_only(monkeypatch):
    monkeypatch.setattr(_compose, "load_topologies",
                        lambda: {"single-app": {"scaffold": {}, "mounts":
                                 {"backend": "", "frontend": ""}, "max_sides": 1}})
    monkeypatch.setattr(_compose, "load_architecture",
                        lambda side, name: {"slots": {"domain": {"dirs": ["entities"]}}})
    monkeypatch.setattr(_compose, "load_stack",
                        lambda side, name: {"nesting": "feature-first",
                                            "root": {"base": "app", "scaffold": ["app", "tests"]},
                                            "module_token": "modules", "inject": {}})
    structure = _compose.compose({
        "root": "my-api", "topology": "single-app",
        "backend": {"arch": "clean", "stack": "fastapi"},
    })
    assert structure == {
        "root": "my-api",
        "tree": {
            "app": {"modules": {"{module}": {"domain": {"entities": None}}}},
            "tests": None,
        },
    }


def test_compose_single_app_rejects_two_sides(monkeypatch):
    monkeypatch.setattr(_compose, "load_topologies",
                        lambda: {"single-app": {"scaffold": {}, "mounts":
                                 {"backend": "", "frontend": ""}, "max_sides": 1}})
    with pytest.raises(CatalogError) as exc:
        _compose.compose({
            "root": "x", "topology": "single-app",
            "backend": {"arch": "clean", "stack": "fastapi"},
            "frontend": {"arch": "fsd", "stack": "react-vite"},
        })
    assert "single-app" in str(exc.value)


def test_compose_unknown_topology(monkeypatch):
    monkeypatch.setattr(_compose, "load_topologies", lambda: {})
    with pytest.raises(CatalogError) as exc:
        _compose.compose({"root": "x", "topology": "nope",
                          "backend": {"arch": "clean", "stack": "fastapi"}})
    assert "unknown topology" in str(exc.value)

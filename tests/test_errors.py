import pytest
import _compose
from _catalog import CatalogError, load_architecture


def test_unknown_nesting_raises():
    arch = {"slots": {"domain": {"dirs": ["entities"]}}}
    stack = {"nesting": "sideways", "root": {"base": "app", "scaffold": ["app"]},
             "module_token": "modules", "inject": {}}
    with pytest.raises(CatalogError) as exc:
        _compose.compose_side(arch, stack)
    assert "unknown nesting" in str(exc.value)


def test_unknown_architecture_file_raises():
    with pytest.raises(CatalogError) as exc:
        load_architecture("backend", "does-not-exist")
    assert "missing fragment" in str(exc.value)

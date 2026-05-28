import pytest
import _catalog


def test_load_yaml_missing_raises(tmp_path):
    with pytest.raises(_catalog.CatalogError) as exc:
        _catalog.load_yaml(tmp_path / "nope.yaml")
    assert "missing fragment" in str(exc.value)


def test_load_yaml_reads_dict(tmp_path):
    f = tmp_path / "x.yaml"
    f.write_text("a: 1\nb:\n")
    assert _catalog.load_yaml(f) == {"a": 1, "b": None}


def test_load_yaml_empty_file_is_empty_dict(tmp_path):
    f = tmp_path / "empty.yaml"
    f.write_text("")
    assert _catalog.load_yaml(f) == {}

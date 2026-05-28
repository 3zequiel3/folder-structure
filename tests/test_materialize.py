import _materialize as materialize_mod


def test_leaf_dir_gets_gitkeep(tmp_path):
    tree = {"domain": {"entities": None}, "tests": None}
    created = materialize_mod.materialize(tree, tmp_path / "app")

    assert (tmp_path / "app" / "domain" / "entities" / ".gitkeep").is_file()
    assert (tmp_path / "app" / "tests" / ".gitkeep").is_file()
    # intermediate dirs exist but get NO .gitkeep
    assert (tmp_path / "app" / "domain").is_dir()
    assert not (tmp_path / "app" / "domain" / ".gitkeep").exists()
    # returns the list of .gitkeep files created
    assert len(created) == 2


def test_empty_dict_is_a_leaf(tmp_path):
    materialize_mod.materialize({"a": {}}, tmp_path)
    assert (tmp_path / "a" / ".gitkeep").is_file()


def test_idempotent(tmp_path):
    tree = {"a": None}
    materialize_mod.materialize(tree, tmp_path)
    materialize_mod.materialize(tree, tmp_path)  # must not raise
    assert (tmp_path / "a" / ".gitkeep").is_file()

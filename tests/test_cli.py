import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SCAFFOLD = Path(__file__).resolve().parent.parent / "scripts" / "scaffold.py"
import scaffold  # noqa: E402  (on path via conftest)


def test_render_tree_ascii():
    tree = {"app": {"domain": None}, "tests": None}
    lines = scaffold.render_tree(tree)
    assert lines == [
        "├── app/",
        "│   └── domain/",
        "└── tests/",
    ]


def test_compose_subcommand_writes_structure(tmp_path):
    out = tmp_path / "structure.yaml"
    # uses the real catalog authored in the next unit; expected to fail until then.
    rc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "compose",
         "--root", "my-api", "--topology", "single-app",
         "--backend-arch", "clean", "--backend-stack", "fastapi",
         "--out", str(out)],
        capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    data = yaml.safe_load(out.read_text())
    assert data["root"] == "my-api"
    assert "app" in data["tree"]


def test_materialize_subcommand_creates_dirs(tmp_path):
    structure = {"root": "demo", "tree": {"app": {"domain": None}, "tests": None}}
    sfile = tmp_path / "structure.yaml"
    sfile.write_text(yaml.safe_dump(structure))
    rc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "materialize",
         "--from-yaml", str(sfile), "--into", str(tmp_path)],
        capture_output=True, text=True)
    assert rc.returncode == 0, rc.stderr
    assert (tmp_path / "demo" / "app" / "domain" / ".gitkeep").is_file()
    assert (tmp_path / "demo" / "tests" / ".gitkeep").is_file()


def test_compose_rejects_half_a_pair():
    args = scaffold.build_parser().parse_args(
        ["compose", "--root", "x", "--topology", "single-app", "--backend-arch", "clean"])
    with pytest.raises(SystemExit):
        scaffold.cmd_compose(args)


def test_materialize_rejects_malformed_yaml(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("root: [unclosed\n")
    import subprocess, sys
    rc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "materialize", "--from-yaml", str(bad)],
        capture_output=True, text=True)
    assert rc.returncode == 1
    assert "invalid YAML" in rc.stderr


def test_materialize_rejects_missing_keys(tmp_path):
    incomplete = tmp_path / "x.yaml"
    incomplete.write_text("hello: world\n")
    import subprocess, sys
    rc = subprocess.run(
        [sys.executable, str(SCAFFOLD), "materialize", "--from-yaml", str(incomplete)],
        capture_output=True, text=True)
    assert rc.returncode == 1
    assert "must contain 'root' and 'tree'" in rc.stderr

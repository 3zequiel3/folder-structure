import _compose


CLEAN = {
    "slots": {
        "domain": {"dirs": ["entities", "value-objects"]},
        "application": {"dirs": ["use-cases", "ports", "dtos"]},
        "infrastructure": {"dirs": []},
        "presentation": {"dirs": []},
    }
}

FASTAPI = {
    "nesting": "feature-first",
    "root": {"base": "app", "base_extra": ["config"], "scaffold": ["app", "tests"]},
    "module_token": "modules",
    "inject": {
        "infrastructure": ["repositories", "models", "uow", "db"],
        "presentation": ["routers"],
    },
}


def test_build_slots_merges_arch_dirs_with_injections():
    slots = _compose.build_slots(CLEAN, FASTAPI)
    assert slots["domain"] == ["entities", "value-objects"]
    assert slots["infrastructure"] == ["repositories", "models", "uow", "db"]
    assert slots["presentation"] == ["routers"]


def test_inject_into_missing_slot_is_skipped():
    arch = {"slots": {"domain": {"dirs": ["entities"]}}}
    stack = {"nesting": "feature-first", "root": {"base": "app", "scaffold": ["app"]},
             "module_token": "modules", "inject": {"nonexistent": ["x"]}}
    slots = _compose.build_slots(arch, stack)
    assert slots == {"domain": ["entities"]}


def test_compose_side_feature_first():
    tree = _compose.compose_side(CLEAN, FASTAPI)
    assert tree == {
        "app": {
            "config": None,
            "modules": {
                "{module}": {
                    "domain": {"entities": None, "value-objects": None},
                    "application": {"use-cases": None, "ports": None, "dtos": None},
                    "infrastructure": {"repositories": None, "models": None,
                                       "uow": None, "db": None},
                    "presentation": {"routers": None},
                }
            },
        },
        "tests": None,
    }

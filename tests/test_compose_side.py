import _compose
from copy import deepcopy


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


def deepcopy_stack_with_nesting(nesting):
    stack = deepcopy(FASTAPI)
    stack["nesting"] = nesting
    return stack


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


def test_compose_side_layer_first():
    stack = deepcopy_stack_with_nesting("layer-first")
    tree = _compose.compose_side(CLEAN, stack)
    assert tree == {
        "app": {
            "config": None,
            "domain": {"{module}": {"entities": None, "value-objects": None}},
            "application": {"{module}": {"use-cases": None, "ports": None, "dtos": None}},
            "infrastructure": {"{module}": {"repositories": None, "models": None,
                                            "uow": None, "db": None}},
            "presentation": {"{module}": {"routers": None}},
        },
        "tests": None,
    }


FSD = {
    "slots": {
        "app": {"dirs": ["providers"]},
        "pages": {"dirs": []},
        "widgets": {"dirs": []},
        "features": {"dirs": []},
        "entities": {"dirs": []},
        "shared": {"dirs": ["api", "config", "lib", "ui"]},
    }
}
REACT_VITE = {
    "nesting": "flat",
    "root": {"base": "src", "scaffold": ["src", "public"]},
    "inject": {},
}


def test_compose_side_flat():
    tree = _compose.compose_side(FSD, REACT_VITE)
    assert tree == {
        "src": {
            "app": {"providers": None},
            "pages": None,
            "widgets": None,
            "features": None,
            "entities": None,
            "shared": {"api": None, "config": None, "lib": None, "ui": None},
        },
        "public": None,
    }

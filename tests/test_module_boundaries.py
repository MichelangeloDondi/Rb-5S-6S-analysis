"""B4: the fibre layer is a leaf, and the guard proves it rather than trusting it.

WHY THIS EXISTS. `rb5s6s/fibre.py` models a future apparatus. Core modules
model the one the archive measured. If a core module ever imports the fibre
layer, the published analysis acquires a dependency on unbuilt hardware, and
the dependency would be invisible: everything would still pass, because the
fibre module imports cleanly. The failure would surface only when someone
tried to reproduce the archive without it.

WHY A CEILING TEST. A guard that has never fired is indistinguishable from a
guard that cannot fire. Each rule below has a companion test that PLANTS a
violation in a temporary copy of the tree and asserts the checker rejects it,
so the guard's own sensitivity is under test and not assumed.
"""
import ast
import shutil
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "rb5s6s"

# Modules the published analysis is built from. None of these may reach into
# the prospective layer.
LEAF_MODULES = {"fibre", "fit_joint"}


def _imports_of(path: Path):
    """Every module name this file imports, plain and relative-from forms."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                names.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0])
            # `from . import fibre` names the module in the alias list
            if node.level and node.module is None:
                for a in node.names:
                    names.add(a.name.split(".")[0])
    return names


def _violations(pkg_dir: Path):
    bad = []
    for path in sorted(pkg_dir.glob("*.py")):
        if path.stem in LEAF_MODULES:
            continue
        hit = _imports_of(path) & LEAF_MODULES
        if hit:
            bad.append((path.name, sorted(hit)))
    return bad


def test_no_core_module_imports_a_leaf():
    assert _violations(PKG) == [], (
        "a core module imports the prospective layer; the published analysis "
        "must not depend on unbuilt hardware")


def test_the_guard_fires_when_a_violation_is_planted():
    """The ceiling test. Without this, a broken checker reads as a clean tree."""
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "rb5s6s"
        shutil.copytree(PKG, copy)
        target = copy / "lineshape.py"
        target.write_text("from . import fibre\n" + target.read_text(encoding="utf-8"),
                          encoding="utf-8")
        found = _violations(copy)
        assert found, "the planted violation was not detected"
        assert any(n == "lineshape.py" for n, _ in found)


def test_the_leaf_exists_or_the_guard_is_vacuous():
    """A guard over an empty set passes for the wrong reason, so say which."""
    present = {m for m in LEAF_MODULES if (PKG / f"{m}.py").exists()}
    if not present:
        pytest.skip("no leaf module present yet; the guard is armed and vacuous")
    assert present

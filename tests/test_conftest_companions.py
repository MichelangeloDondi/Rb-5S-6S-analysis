"""The autouse fixture that puts `stark.COMPANIONS` back, planted both ways.

Importing `scripts/run_three_channel_forecast.py` switches the saturation
companion on package-wide, at module level and for a good reason: its pool
spawns and a worker re-imports the file, so an assignment in the parent's frame
would reach no child. The suite's protection is the conftest fixture, and a
fixture nothing exercises is an assertion.

The order these two run in is the point. The first leaves the global switched
on, exactly as a producer-loading test does; the second asserts it came back.
pytest runs them in file order, so a broken fixture fails the second.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rb5s6s import stark

ROOT = Path(__file__).resolve().parents[1]


def test_a_test_may_switch_the_companion_on():
    """Stands in for any test that loads a producer which sets the layer."""
    assert stark.COMPANIONS is None, (
        "the companion was already on when this test started, so the fixture "
        "did not restore it after an earlier test")
    stark.COMPANIONS = {"ratio": 1.2367, "scale": 1.0, "cycles": 1.0}
    assert stark.companion_gamma_mhz(5.8, "4192") > 1.0, \
        "the layer should be live once the global is set"


def test_the_next_test_gets_it_back_off():
    """The restoration, seen from the test that would otherwise be poisoned.

    Three stark tests failed this way on 2026-09-09, reading kappa 0.449
    against a committed 0.0, because a new module sorted ahead of them."""
    assert stark.COMPANIONS is None, (
        "stark.COMPANIONS leaked from the previous test; the conftest fixture "
        "is not restoring it")
    assert stark.companion_gamma_mhz(5.8, "4192") == 0.0, \
        "with the global unset the companion must contribute nothing"


def _module_scope_script_imports(source: str) -> list[str]:
    """Imports of anything under scripts/ at a test file's MODULE scope.

    The fixture above restores the global between tests, which is the wrong
    boundary on its own. A producer imported at module scope runs during
    pytest COLLECTION, before any fixture setup, so the first test's snapshot
    would capture an already-poisoned value and every restore after it would
    put the poison back. `scripts/` has no `__init__.py`, but implicit
    namespace packages make `from scripts.run_three_channel_forecast import X`
    resolve anyway, so nothing about the layout prevents it. The safe idiom,
    which every current test already uses, is to load the producer inside the
    test body.

    MODULE SCOPE IS NOT `tree.body` (2026-09-09, round two). The first form
    walked the direct children of the module only, so a producer import inside
    a `try/except ImportError`, an `if`, or a `with` was invisible while still
    executing at collection time, and `importlib.import_module("scripts...")`
    and `__import__("scripts...")` were invisible in any position. Two readers
    each planted a different bypass and reproduced the poisoning through it,
    and a third and fourth turned up when the function was run over a whole
    table instead of over the shapes already reported. What module scope MEANS is everything
    that runs on import, which is the whole tree with function and class bodies
    cut out, and that is what this walks now. The parametrised test below
    carries every shape as a row, so the next spelling is a row and not a
    round."""
    import ast
    tree = ast.parse(source)
    hits = []

    def _walk(node):
        for child in ast.iter_child_nodes(node):
            # a function or class body does not run at import
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef)):
                continue
            if isinstance(child, ast.Import):
                hits.extend(a.name for a in child.names
                            if a.name.split(".")[0] == "scripts")
            elif isinstance(child, ast.ImportFrom):
                if (child.module or "").split(".")[0] == "scripts":
                    hits.append(child.module)
            elif isinstance(child, ast.Call):
                fn = child.func
                name = (fn.attr if isinstance(fn, ast.Attribute) else
                        fn.id if isinstance(fn, ast.Name) else "")
                if name in ("import_module", "__import__") and child.args:
                    arg = child.args[0]
                    if (isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                            and arg.value.split(".")[0] == "scripts"):
                        hits.append(arg.value)
            _walk(child)

    _walk(tree)
    return hits


def test_no_test_imports_a_producer_at_module_scope():
    """Collection-time import poisoning, made impossible rather than absent."""
    offenders = {}
    for path in sorted((ROOT / "tests").glob("*.py")):
        hits = _module_scope_script_imports(path.read_text(encoding="utf-8"))
        if hits:
            offenders[path.name] = hits
    assert not offenders, (
        "these import a producer at module scope, which runs it during pytest "
        f"collection, so the conftest fixture cannot help: {offenders}. Load it "
        "inside the test body with importlib instead.")


@pytest.mark.parametrize("src,fires", [
    ("from scripts.run_three_channel_forecast import forecast_cell\n", True),
    ("import scripts.run_kernel_inhomogeneity as k\n", True),
    ("import scripts\n", True),
    # THE FOUR BYPASSES OF 2026-09-09, each an executed reproduction before it
    # was a row. Two readers planted one apiece and reproduced the poisoning
    # through them, and the other two came from running the function over this
    # whole table instead of over the shapes already reported.
    ("try:\n    import scripts.run_x\nexcept ImportError:\n    pass\n", True),
    ("if True:\n    import scripts.run_x\n", True),
    ("import importlib\nk = importlib.import_module('scripts.run_x')\n", True),
    ("__import__('scripts.run_x')\n", True),
    ("import contextlib\nwith contextlib.suppress(Exception):\n    import scripts.run_x\n", True),
    # the safe idiom every current test uses
    ("def test_x():\n    from scripts.run_x import y\n    assert y\n", False),
    ("class C:\n    import scripts.run_x\n", False),
    ("def go():\n    return __import__('scripts.run_x')\n", False),
    ("import importlib.util\nspec = importlib.util.spec_from_file_location('m', P)\n", False),
    ("from rb5s6s import stark\n", False),
])
def test_the_module_scope_guard_fires_on_the_shape_it_names(src, fires):
    """Both directions, including the in-body form that must stay allowed."""
    assert bool(_module_scope_script_imports(src)) is fires, src


def _run_two_modules(tmp_path, with_module_restore: bool):
    """Two modules in a fresh pytest: the first switches the layer on inside
    a MODULE-scoped fixture and the module collected after it asserts it is off. The temp conftest
    borrows the real fixtures by executing tests/conftest.py from its own
    path, so what is planted is the shipped code and not a copy of it."""
    import subprocess
    import sys
    import textwrap
    tmp_path.mkdir(parents=True, exist_ok=True)
    real = ROOT / "tests" / "conftest.py"
    names = ["_restore_stark_companions"] + (
        ["_restore_stark_companions_per_module"] if with_module_restore else [])
    (tmp_path / "conftest.py").write_text(textwrap.dedent(f"""
        import importlib.util
        _spec = importlib.util.spec_from_file_location("real_conftest", {str(real)!r})
        _m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
        """) + "".join(f"{n} = _m.{n}\n" for n in names))
    (tmp_path / "test_a_pollutes.py").write_text(textwrap.dedent("""
        import pytest
        from rb5s6s import stark

        @pytest.fixture(scope="module")
        def loader():
            stark.COMPANIONS = {"ratio": 1.2367, "scale": 1.0}
            return True

        def test_uses_the_loader(loader):
            assert stark.COMPANIONS is not None
        """))
    (tmp_path / "test_b_reads.py").write_text(textwrap.dedent("""
        from rb5s6s import stark

        def test_the_layer_is_off_in_the_next_module():
            assert stark.COMPANIONS is None
        """))
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "--rootdir", str(tmp_path), "test_a_pollutes.py", "test_b_reads.py"],
                       cwd=tmp_path, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def test_a_module_scoped_loader_is_undone_at_module_teardown(tmp_path):
    """The 2026-09-13 gate: the taxonomy module's module-scoped loader left
    the layer on for `test_stark.py` on the same worker. With the module-scoped
    restore the next module sees it off."""
    rc, out = _run_two_modules(tmp_path / "with", True)
    assert rc == 0, out


def test_the_per_test_restore_alone_cannot_undo_a_module_scoped_loader(tmp_path):
    """The negative direction: the same two modules under only the per-test
    fixture fail in the second module, which is the defect the module-scoped
    fixture exists for. If this passes, the plant no longer discriminates."""
    rc, out = _run_two_modules(tmp_path / "without", False)
    assert rc != 0 and "test_the_layer_is_off_in_the_next_module" in out, out

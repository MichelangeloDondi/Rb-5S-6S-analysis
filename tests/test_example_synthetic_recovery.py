"""The package's own self-validation example must keep working.

WHY THIS EXISTS. `examples/synthetic_recovery.py` is gate P2 of the release
candidate: it builds a line whose parameters are known, fits it with the same
`fit_condition` the archive's results were produced with, and reports the
recovery against the fit's own errors. An example that silently stops running,
or silently stops recovering, is worse than no example, because a reader takes
it as evidence the machinery works.

The test also pins the two properties that make the example a RELEASE artifact
rather than a research script: it reads no archive data, and it imports nothing
from the private tree.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

EX = pathlib.Path(__file__).resolve().parents[1] / "examples" / "synthetic_recovery.py"
ROOT = EX.parents[1]


def test_the_example_runs_and_recovers(tmp_path):
    """Run it from a directory that is not the repository, with no env set."""
    env = {"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT)}
    r = subprocess.run([sys.executable, str(EX)], cwd=tmp_path, env=env,
                       capture_output=True, text=True)
    assert r.returncode == 0, f"example failed:\n{r.stdout}\n{r.stderr}"
    assert "VERDICT: PASS" in r.stdout, r.stdout
    assert "RECOVERY" in r.stdout and "ASSUMPTIONS" in r.stdout


def test_the_example_reads_no_dataset_and_no_private_tree():
    """The couplings that would make it a research script.

    CODE ONLY. The module docstring legitimately MENTIONS results/ and docs/
    when telling the reader where the experiment-specific numbers live, and an
    earlier version of this test failed on that sentence. A prose mention is
    not a dependency, which is the same false positive the package boundary
    inventory produces from its own regex.
    """
    import ast
    src = EX.read_text()
    tree = ast.parse(src)
    body = tree.body[1:] if (tree.body and isinstance(tree.body[0], ast.Expr)
                             and isinstance(tree.body[0].value, ast.Constant)
                             ) else tree.body
    code = "\n".join(ast.unparse(n) for n in body)
    for forbidden in ("private/", "data_raw", "RB5S6S_SESSION", "results/",
                      "load_manifest", "trace_path", "open("):
        assert forbidden not in code, f"example reaches for {forbidden}"


def test_the_example_uses_the_declared_public_surface():
    """Generation comes from the public builder, not a private helper.

    `_shared_profile_grid` would work and is what the research code uses. The
    example deliberately uses `composite_profile`, which is in `rb5s6s.__all__`,
    so that what the example demonstrates is the SUPPORTED surface.
    """
    src = EX.read_text()
    assert "composite_profile" in src
    assert "_shared_profile_grid" not in src
    import rb5s6s
    assert "composite_profile" in rb5s6s.__all__

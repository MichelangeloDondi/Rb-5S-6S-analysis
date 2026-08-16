"""Every python snippet in the wiki runs, from a clean interpreter.

A documentation snippet is a claim that the code does something, and an
unexecuted one is a claim nobody checked. They go stale in the quietest way
available: a keyword argument is renamed, a return type becomes a dict with
different keys, and the prose keeps saying otherwise for months.

This runs each block in a subprocess with only the repository on the path, so
a snippet that depends on the test session's imports, on a fixture, or on the
working directory fails here rather than in a reader's terminal. Snippets are
expected to be self-contained and to print something.

Two of the six blocks were written with a wrong signature and a wrong dict key
on the first attempt, which is the whole argument for this file existing.
"""
from pathlib import Path
import re
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "docs" / "wiki"

BLOCK = re.compile(r"```python\n(.*?)```", re.S)


def _blocks():
    out = []
    for page in sorted(WIKI.glob("*.md")):
        for i, code in enumerate(BLOCK.findall(page.read_text(encoding="utf-8"))):
            out.append((f"{page.name}#{i}", code))
    return out


CASES = _blocks()


def test_the_wiki_has_runnable_snippets():
    """A guard over an empty set passes for the wrong reason.

    If every snippet is deleted this file would go green while checking
    nothing, so it asserts its own subject exists before checking it.
    """
    assert CASES, (
        "no python snippets found in docs/wiki/, so this guard is checking "
        "nothing. Either the snippets were removed, in which case delete this "
        "file, or the fence syntax changed and the pattern needs updating.")


@pytest.mark.parametrize("name,code", CASES, ids=[c[0] for c in CASES])
def test_wiki_snippet_runs(name, code):
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, cwd=ROOT, timeout=180,
        env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(ROOT),
             "HOME": str(Path.home()), "MPLBACKEND": "Agg"})
    assert proc.returncode == 0, (
        f"the snippet in docs/wiki/{name} does not run:\n{proc.stderr[-1500:]}")
    assert proc.stdout.strip(), (
        f"the snippet in docs/wiki/{name} runs and prints nothing, so a "
        f"reader cannot tell what it demonstrates")

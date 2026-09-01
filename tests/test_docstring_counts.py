"""A docstring's count of its own assertions is a claim; count it.

The class shipped twice in one file in one night: a plant docstring
said "every direction" over six of eight, was repaired to "eight
assertions" over a body holding nine. Both survived reading because a
number beside code is trusted. This guard parses every tracked test
docstring for the forms "<N> assertions" and "<N> asserts" (number words through twelve
are read) and compares N against the ast count of Assert nodes in
that function. It does NOT read "<N> directions" or any other counted
noun -- the first motivating instance ("every direction" over six of
eight) would have needed a directions-to-branches map no parser here
has, and a guard claiming a form it cannot parse was itself an audit
finding. The graded population is small today (one docstring); the
guard exists for the next count somebody writes.

Plant, verified at introduction and held by the in-file control
below: lowering a claimed count by one fails that function alone.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORDS = {w: i for i, w in enumerate(
    ("zero one two three four five six seven eight nine ten eleven "
     "twelve").split())}
# \w+ already matches digit runs, so a separate \d+ alternative was dead
CLAIM = re.compile(r"\b(\w+)\s+assert(?:ion)?s\b", re.I)


def _n(tok: str) -> int | None:
    if tok.isdigit():
        return int(tok)
    return WORDS.get(tok.lower())


def test_assertion_counts_match_their_bodies():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "tests/*.py"],
        capture_output=True, text=True).stdout.split()
    wrong = []
    for rel in tracked:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            doc = ast.get_docstring(fn) or ""
            for m in CLAIM.finditer(doc):
                n = _n(m.group(1))
                if n is None:
                    continue
                real = sum(isinstance(x, ast.Assert) for x in ast.walk(fn))
                if real != n:
                    wrong.append(f"{rel}::{fn.name}: docstring claims "
                                 f"{n} assertions, body holds {real}")
    assert not wrong, (
        "a count beside code drifted from the code:\n  "
        + "\n  ".join(wrong))


def test_the_plant_fires_through_the_real_parser():
    """The in-file control: a source string with a lying count is caught
    by the same regex+ast path the tracked scan uses."""
    import textwrap
    src = textwrap.dedent('''
        def test_x():
            """Two assertions."""
            assert 1
            assert 2
            assert 3
    ''')
    tree = ast.parse(src)
    fn = tree.body[0]
    doc = ast.get_docstring(fn)
    m = CLAIM.search(doc)
    assert m and _n(m.group(1)) == 2
    assert sum(isinstance(x, ast.Assert) for x in ast.walk(fn)) == 3


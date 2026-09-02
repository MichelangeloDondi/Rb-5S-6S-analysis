"""A docstring beside a population constant carries no file-count numeral.

Three audit rounds in one night each caught a module docstring whose
file count had drifted from its own tuple (seven-plus-four over ten,
then ten over twelve, in the same file across two repairs). The counts
were prose beside code, so no guard read them. The mechanizable form
of the lesson is the convention the last repair adopted: THE TUPLE IS
THE COUNT, and a module that defines a population constant states no
"<N> files" in its module docstring at all.

FALSE-PASS DIRECTION, stated first, both faces: a module whose
population lives under a name this list does not carry is not graded
(extend POPULATION_NAMES when a new constant style appears), and the
scope is tests/ alone, so a population module under rb5s6s/ or
scripts/ is outside this guard entirely.

Plant, verified at introduction: reinserting the historical "ten
files" into the shape ratchet's docstring in a scratch copy fails
that module alone through this parser.
"""
from __future__ import annotations

import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# extended from an audit's enumeration (the first draft carried a dead
# name and missed four live constants); the set is NOT exhaustive, and
# a fresh sweep at audit time found further uncovered constants with
# no live defect behind them, so widening waits for a finding
POPULATION_NAMES = {"POPULATION", "SURFACE", "SKIP_EXACT",
                    "RAIL_EXCLUDE", "SKIP_PREFIXES",
                    "FIBRE_ONLY_RESULTS", "INDEX_FILES",
                    "GENERATED", "GITIGNORED_PROSE"}
COUNT = re.compile(
    r"(?<![\w-])(one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|\d+)\s+files?(?![\w-])", re.I)


def _modules():
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "tests/*.py"],
        capture_output=True, text=True).stdout.split()
    return tracked


def test_population_docstrings_carry_no_file_counts():
    bad = []
    for rel in _modules():
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        names = {t.id for n in tree.body if isinstance(n, ast.Assign)
                 for t in n.targets if isinstance(t, ast.Name)}
        if not (names & POPULATION_NAMES):
            continue
        doc = ast.get_docstring(tree) or ""
        m = COUNT.search(doc)
        if m:
            bad.append(f"{rel}: {m.group(0)!r}")
    assert not bad, (
        "a module docstring counts files beside the constant that IS the "
        "count; the tuple is the count and prose stopped carrying one:\n  "
        + "\n  ".join(bad))


def test_the_plant_fires_through_the_real_parser():
    src = (ROOT / "tests/test_prose_shape.py").read_text(encoding="utf-8")
    planted = src.replace(
        "POPULATION: the files in the tuple below",
        "POPULATION: the ten files in the tuple below", 1)
    assert planted != src, "the plant anchor left test_prose_shape"
    tree = ast.parse(planted)
    doc = ast.get_docstring(tree) or ""
    assert COUNT.search(doc), "the plant must be visible to the parser"
    assert not COUNT.search(ast.get_docstring(ast.parse(src)) or "")

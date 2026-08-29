"""Every inline data reference resolves, and the seeded floor holds.

THE SYSTEM (private/REFERENCE_SYSTEM_DESIGN_2026-08-24.md, implemented at
the owner's instruction). A quoted number carries its reference inline as
a markdown link whose target is the source file and whose title is a
machine-readable key. The reader gets one click to the source. This suite
hook gets the other half: `scripts/check_references.py` resolves every
key and compares the link text, the number the reader actually reads,
against the source value at the printed precision, so a regenerated CSV
fails every stale quoting site by name and staleness cannot be committed.

The floor exists because the resolver alone has a deletion blind spot: a
reference removed with its sentence resolves nothing and fails nothing.
Holding the count at its seeded floor means the corpus can only gain
references, which is the same falling-debt shape every ratchet here uses.

This replaces the hand-maintained QUOTED registry that
test_quantities_index_is_complete.py carried from 2026-08-23 to
2026-08-24: eight numbers, each needing a Python edit to cover, the
registry's own docstring naming the limitation. Those eight are now
inline references on their pages, checked by the same resolver as
everything else.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The seeded floor: 4 case-page headline numbers, 8 migrated registry
# numbers on the quantities pages, and 3 adjudication anchors in the
# theory note, plus the ledger generator's 3 emitted headline bounds. Raise it when a seeding wave lands, never lower it.
REFERENCE_FLOOR = 18


def _run():
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_references.py")],
        capture_output=True, text=True)


def test_every_reference_resolves_to_its_source():
    out = _run()
    assert out.returncode == 0, (
        "references failed to resolve, and each line below names a quoting "
        "site to repair, which is the anti-staleness contract working:\n"
        + out.stdout + out.stderr)


def test_the_reference_count_holds_its_floor():
    out = _run()
    first = out.stdout.splitlines()[0] if out.stdout else ""
    n = int(first.split()[1]) if first.startswith("check_references:") else 0
    assert n >= REFERENCE_FLOOR, (
        f"the corpus carries {n} references against a floor of "
        f"{REFERENCE_FLOOR}. References were deleted, and a deleted "
        f"reference is a quoting site the resolver can no longer protect: "
        f"restore them or re-seed deliberately, raising the floor in this "
        f"file with the wave that does it.")


def test_the_committed_graph_is_fresh():
    """docs/reference_graph.json equals what the checker derives now.

    The graph is the derived dependents map, generated and never
    hand-edited, and this is the same freshness contract the literature
    index lives under: regenerate, compare, and a mismatch says re-run
    `scripts/check_references.py --graph` and commit the result. Without
    this the graph would rot the day after it was first committed, which
    is the fate of every derived artifact nothing regenerates.
    """
    graph_path = ROOT / "docs" / "reference_graph.json"
    assert graph_path.exists(), (
        "docs/reference_graph.json is missing: run "
        "scripts/check_references.py --graph and commit it")
    before = graph_path.read_text(encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_references.py"),
         "--graph"], capture_output=True, text=True)
    after = graph_path.read_text(encoding="utf-8")
    if before != after:
        graph_path.write_text(before, encoding="utf-8")
    assert out.returncode == 0, out.stdout + out.stderr
    assert before == after, (
        "the committed reference graph is stale: re-run "
        "scripts/check_references.py --graph and commit the result")


def test_an_ambiguous_coordinate_is_refused_not_resolved_to_the_first_row(tmp_path):
    """A resolver that can match several rows must refuse, not choose.

    WHY THIS EXISTS. `_csv_cell` matched the first two columns and returned on
    the FIRST hit. A release board found two live coordinates that named more
    than one row: three cell rows shared `gamma_coll_err`, separated only by a
    `basis` cell, and two onf rows shared `minutes_per_trace`. Neither
    published number was wrong, because in both cases the first row happened
    to be the one quoted -- which is the exact shape of a false pass, and the
    reason the resolver may not choose.

    THE SECOND FAILURE MODE OF A RESOLVER. A checker that merely MATCHES can
    only fail to find. A checker that RESOLVES can find the wrong thing and
    report success, and nobody looks for that. Ask of any resolver not only
    whether it found something but whether it could have found more than one.

    Planted here rather than against the tree because the tree now has no
    ambiguous coordinate left: the producer gives those rows distinct
    quantities. A guard whose only plant is a state the tree no longer holds
    is a guard with no plant, so the fixture carries the state.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_references", ROOT / "scripts" / "check_references.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    results = tmp_path / "results"
    results.mkdir()
    (results / "amb.csv").write_text(
        "arm,quantity,value,unit,basis,status\n"
        "cell,g_err,0.015,MHz,5 traces,ENVELOPE\n"
        "cell,g_err,0.007,MHz,20 traces,ENVELOPE\n"
        "cell,unique_row,1.234,MHz,only one,ENVELOPE\n")
    mod.RESULTS = results

    assert mod._csv_cell("amb", "cell", "g_err") is mod.AMBIGUOUS, (
        "a coordinate naming two rows must be refused; returning the first "
        "row silently validates prose against a value it may not mean")
    assert mod._csv_cell("amb", "cell", "unique_row") == "1.234", (
        "the false-positive direction: a unique coordinate must still resolve"
    )
    assert mod._csv_cell("amb", "cell", "absent") is None, (
        "a coordinate naming no row is DANGLING, which is a different "
        "finding from AMBIGUOUS and must stay distinguishable")

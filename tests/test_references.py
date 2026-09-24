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


def test_the_committed_graph_is_fresh(tmp_path):
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
    # THE FRESH GRAPH IS WRITTEN BESIDE THE TEST, NEVER OVER THE TRACKED FILE (2026-09-25). This test
    # used to regenerate docs/reference_graph.json in place and write the committed text back when they
    # differed, so for the length of one write the tracked file was truncated under any concurrent
    # reader, and the floor now runs its lanes concurrently; a killed run could also leave it rewritten.
    fresh = tmp_path / "reference_graph.json"
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_references.py"),
         "--graph", "--graph-out", str(fresh)], capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
    after = fresh.read_text(encoding="utf-8")
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


def test_a_constant_reference_resolves_to_the_package_and_refuses_a_wrong_digit():
    """`ref:constant:<NAME>[:<unit>]` binds a page's number to `rb5s6s/constants.py`.

    WHY THIS EXISTS. The natural width on two platform-neutral pages was bound
    on 2026-09-17 to a fibre-only file's row that merely echoes
    `GAMMA_NAT_HZ`, and the platform lane refused the citation. The constant's
    module is that quantity's SSOT, so the checker resolves it there. Both
    directions are planted: the right digits at the page's unit resolve, a
    moved digit is a finding, a name the module lacks and a unit the scheme
    lacks resolve to nothing rather than to something.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_references", ROOT / "scripts" / "check_references.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from rb5s6s import constants as K

    src = mod._constant_value("GAMMA_NAT_HZ", "MHz")
    assert src is not None and mod._matches(f"{K.GAMMA_NAT_HZ * 1e-6:.4f}", src), (
        "the constant at the page's unit must resolve at the page's own digits")
    assert not mod._matches(f"{K.GAMMA_NAT_HZ * 1e-6 + 0.01:.4f}", src), (
        "a number one hundredth off the constant must be a finding")
    assert mod._constant_value("GAMMA_NAT_HZ", "") is not None
    assert mod._constant_value("GAMMA_NAT_HZ", "1e-6") == src, (
        "a numeric scale is the same binding as its unit word")
    assert mod._constant_value("NOT_A_CONSTANT_OF_THIS_PACKAGE", "MHz") is None, (
        "a name the module lacks resolves to nothing, never to a default")
    assert mod._constant_value("GAMMA_NAT_HZ", "furlongs") is None, (
        "a unit the scheme lacks resolves to nothing")


def test_the_fixer_names_the_sentence_a_moved_value_sits_in():
    """--fix keeps a bound number current and says nothing about the claim around it.

    This was earned on 2026-09-22: an estimator passage was rewritten to
    "close to tied" while its own cells had moved apart, so a rewrite now prints the sentence for
    a person to re-read. A table row is one cell, not one sentence, and the two units differ.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_references_sentence", Path(__file__).resolve().parents[1] / "scripts" / "check_references.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    row = '| a | the correlation moves [0.0009](x.csv "ref:a:b:c") over a wider span | b |\n'
    prose = "Plain prose here. The value [7.42](y.csv) sits in this one. A third sentence follows.\n"
    text = row + prose
    cell = mod._sentence_at(text, text.index("0.0009"))
    assert cell.startswith("the correlation moves") and cell.endswith("wider span"), cell
    assert "| b |" not in cell, "a table cell stops at its own pipes"
    got = mod._sentence_at(text, text.index("7.42"))
    assert got == "The value [7.42](y.csv) sits in this one.", got
    assert len(mod._sentence_at("x" * 1000 + " [1.0](y)", 1002)) <= 300, "one long row cannot bury the list"


def test_a_bound_pair_prints_two_significant_digits_and_the_value_at_its_decimals(tmp_path):
    """The owner's order of 2026-09-24, planted both ways: "Fix the SSOT issues once for all, so to have
    always 2 significant digits of uncertainty and automatic propagation across the replacement in
    prose too".

    A value reference, the plus-or-minus connector and a reference to the SAME row's err column are a
    PAIR: the uncertainty prints at two significant digits and the value at its decimals. A lone value
    prints at the page's own decimals and never beyond its cell's, so --fix can drop a digit and never
    invent one ("438.40" had become "413.10"). A one-digit uncertainty prints as its cell holds it and
    is never padded with a zero nobody measured; that cell is the producer's debt.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_references", ROOT / "scripts" / "check_references.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    results = tmp_path / "results"
    results.mkdir()
    (results / "pair.csv").write_text(
        "quantity,key,value,err,unit,status\n"
        "bias,a,-0.8324,0.0834,MHz,DIAGNOSTIC\n"
        "edge,a,1.23456,0.0996,MHz,DIAGNOSTIC\n"
        "thin,a,0.5412,0.007,MHz,DIAGNOSTIC\n")
    mod.RESULTS = results
    mod._csv_cell.cache_clear()
    # the arithmetic, the re-rounding edge and the cap on digits the source does not hold
    assert mod.two_sig("0.0834") == ("0.083", 3)
    assert mod.two_sig("0.0996") == ("0.10", 2)
    assert mod.two_sig("0.007") == ("0.007", 3), "a one-digit cell must not print as 0.0070"
    assert mod.two_sig("12.34") == ("12", 0)
    assert mod.two_sig("0") is None and mod.two_sig("") is None
    # the renderer
    assert mod.canonical("-0.8324", "-0.8324", "value", "0.0834") == "-0.832"
    assert mod.canonical("0.0834", "0.0834", "err") == "0.083"
    assert mod.canonical("1.23456", "1.23456", "value", "0.0996") == "1.23"
    assert mod.canonical("413.10", "413.1") == "413.1", "a lone value never carries a digit its cell lacks"
    assert mod.canonical("413", "413.1") == "413", "the page's own coarser rounding is kept"
    # the detector, both ways
    page = ('the bias is [-0.8324](results/pair.csv "ref:pair:bias:a") ± '
            '[0.0834](results/pair.csv "ref:pair:bias:a:err") MHz.\n')
    assert mod._pair_roles(page, list(mod.LINK.finditer(page))) == {0: ("value", "0.0834"), 1: ("err", "0.0834")}
    other = ('x [1.23](results/pair.csv "ref:pair:edge:a") ± '
             '[0.0834](results/pair.csv "ref:pair:bias:a:err")')
    assert mod._pair_roles(other, list(mod.LINK.finditer(other))) == {}, \
        "an uncertainty read from ANOTHER row is not this value's pair"
    # the check mode, both ways
    assert not mod._is_current("-0.8324", "-0.8324", "value", "0.0834"), "a pair off the rule must read stale"
    assert mod._is_current("-0.832", "-0.8324", "value", "0.0834")
    assert mod._is_current("−0.832", "-0.8324", "value", "0.0834"), "the typographic minus is the same number"
    assert mod._is_current("0.083", "0.0834", "err", "0.0834")
    assert not mod._is_current("0.0834", "0.0834", "err", "0.0834")

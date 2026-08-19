"""Every committed result CSV is either freshness-checked or registered as not.

`scripts/verify_results_fresh.py` re-runs each producer and diffs its output
against the committed CSV. It can only do that for files named in its CHEAP or
EXPENSIVE dicts, and those dicts are edited when a producer is added and not
when an output is added, so they drift one file at a time and nothing says so.

That drift had already happened and was invisible. On 2026-08-19 the two dicts
covered 27 of 46 committed CSVs: NINETEEN FILES, 41 per cent of the record, were
compared against nothing in either mode. The gap was not confined to the
harmless tail. Four of the nineteen were BOUND files, and `stark_joint.csv` is
cited in CLAIMS and appears in 26 documents. Every drift hunt run against that
guard came back clean because the guard could only ever see 59 per cent of the
record, and a green from a partial guard reads exactly like a green from a
complete one.

So the rule here is not that everything must be checked. Some producers cannot
run in an ordinary checkout, and pretending otherwise would trade a silent gap
for a broken one. The rule is that ABSENCE MUST BE A WRITTEN DECISION: a
committed CSV appears in CHEAP, in EXPENSIVE, or in UNCOVERED with a stated
reason, and a new file that lands in none of the three fails here.

The counts print on every run rather than only on failure, because a guard that
reports a fraction should show the fraction it is reporting.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
CHECKER = ROOT / "scripts" / "verify_results_fresh.py"


def _dict(name: str) -> dict:
    """Read one module-level dict literal without importing the checker.

    Importing would pull in the checker's own dependencies and run its argument
    parsing, and this guard is about what the file SAYS rather than what it does.
    """
    src = CHECKER.read_text()
    m = re.search(rf"^{name} = (\{{.*?^\}})", src, re.S | re.M)
    assert m, f"{name} is not a module-level dict literal in {CHECKER.name}"
    return ast.literal_eval(m.group(1))


def test_every_committed_result_is_checked_or_registered():
    cheap, expensive, uncovered = _dict("CHEAP"), _dict("EXPENSIVE"), _dict("UNCOVERED")
    checked = {csv for d in (cheap, expensive) for outs in d.values() for csv in outs}
    committed = {p.name for p in RESULTS.glob("*.csv")}

    unaccounted = sorted(committed - checked - set(uncovered))
    print(
        f"results CSVs {len(committed)}: "
        f"{len(checked & committed)} freshness-checked, "
        f"{len(set(uncovered) & committed)} registered uncovered, "
        f"{len(unaccounted)} unaccounted"
    )
    assert not unaccounted, (
        "these committed CSVs are compared against nothing and are not "
        "registered as deliberately uncovered:\n  "
        + "\n  ".join(unaccounted)
        + "\n\nAdd each to CHEAP or EXPENSIVE in scripts/verify_results_fresh.py, "
        "or to UNCOVERED with the reason it cannot be checked."
    )


def test_the_uncovered_registry_names_only_real_files_and_gives_reasons():
    """A registry that outlives its files becomes a place to hide things."""
    uncovered = _dict("UNCOVERED")
    committed = {p.name for p in RESULTS.glob("*.csv")}

    stale = sorted(set(uncovered) - committed)
    assert not stale, (
        "UNCOVERED names files that are not committed, so the exemption is "
        f"pointing at nothing: {stale}"
    )
    # A reason short enough to be a label is not a reason.
    thin = sorted(k for k, v in uncovered.items() if len(v.split()) < 12)
    assert not thin, f"UNCOVERED entries without a substantive reason: {thin}"


def test_no_csv_is_claimed_by_two_producers():
    """One output, one producer. Two would make a diff ambiguous."""
    cheap, expensive = _dict("CHEAP"), _dict("EXPENSIVE")
    seen: dict[str, str] = {}
    clashes = []
    for scope in (cheap, expensive):
        for producer, outs in scope.items():
            for csv in outs:
                if csv in seen:
                    clashes.append(f"{csv}: {seen[csv]} and {producer}")
                seen[csv] = producer
    assert not clashes, "a CSV is listed under more than one producer:\n  " + "\n  ".join(clashes)

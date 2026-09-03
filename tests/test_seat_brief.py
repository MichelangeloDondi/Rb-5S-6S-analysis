"""The standing seat brief's own guards.

WHY IT EXISTS. The brief emitter was written because every seat brief
in this record had been hand-typed by the convener from memory, and on
2026-09-02 that omitted the one instruction that mattered: a seat
reached for `git stash` on a shared stack and took the board's own tree
out of the index for seven minutes while three other seats read it.

An emitter that silently stopped carrying that instruction would put
the record back where it was, and nothing else would notice - the
briefs are prose handed to an agent, graded by no gate. So the
instructions the incidents earned are pinned here by name.

Failure mode guarded: a brief that no longer carries the lesson it
was built for, which looks exactly like a brief.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
_MOD = ROOT / "private" / "checks" / "seat_brief.py"

pytestmark = pytest.mark.skipif(
    not _MOD.is_file(),
    reason="the governance tree is private and absent from the mirror")

if _MOD.is_file():
    _spec = importlib.util.spec_from_file_location("seat_brief", _MOD)
    sb = importlib.util.module_from_spec(_spec)
    sys.modules.setdefault("seat_brief", sb)
    _spec.loader.exec_module(sb)


def test_the_brief_forbids_the_stash_and_says_what_to_do_instead():
    """The chain-of-custody incident of 2026-09-02, in the one place a
    seat will actually read it. A prohibition with no alternative is
    how the original brief failed: it said restore what you plant and
    left the seat to choose the tool."""
    s = sb.STANDING
    assert "NEVER use `git stash`" in s
    assert "cp <file> /tmp/" in s, (
        "the brief forbids the stash without naming the pattern that "
        "replaces it, which is the shape that caused the incident")
    assert "git archive" in s, (
        "a seat reading another commit's tree has no sanctioned route")


def test_the_brief_asks_for_both_lists_and_a_severity():
    """Near misses are the leading indicator and a report without them
    has not read hard enough. The severity vocabulary is LOGIC 0c.17's
    and a brief that omits it gets CONFIRM/REFUTE back."""
    s = sb.STANDING
    for token in ("BREACHES", "NEAR MISSES", "CRITICAL", "SEVERE",
                  "MODERATE", "MINOR"):
        assert token in s, f"the brief never asks for {token}"


def test_the_brief_tells_a_seat_to_refute_the_brief():
    """Two figures in a convener's brief were wrong on 2026-09-02 and
    the seat that grepped for them caught both. A brief that presents
    its own numbers as given gives that up."""
    assert "Grep the artefact for a literal" in sb.STANDING


def test_every_required_seat_has_a_lens():
    """The NAME used to say every seat and the body checked one.

    That is the test-name-against-test-body shape, and it mattered:
    the brief shipped with lenses for six of the ten required seats,
    and `--seat protocols` returned nothing to a reader who had been
    asked for exactly that lens. The roster is the authority, so the
    roster is what this reads."""
    ledger = ROOT / "private" / "checks" / "board_ledger.py"
    if not ledger.is_file():
        pytest.skip("the ledger is private and absent from the mirror")
    # IMPORTED, not parsed. The roster is a frozenset(...) call rather
    # than a bare literal, so `ast.literal_eval` returned nothing and
    # this guard graded an empty population on its first run - caught
    # only because it refuses to pass on one, which is the whole point
    # of that assertion.
    import importlib.util as _il
    _s = _il.spec_from_file_location("_ledger_probe", ledger)
    _m = _il.module_from_spec(_s)
    try:
        _s.loader.exec_module(_m)
    except SystemExit:
        pass
    required = set(getattr(_m, "REQUIRED_SEATS", ())) | set(
        getattr(_m, "RELEASE_SEATS", ()))
    assert required, (
        "no seat roster was read, so this guard is grading an empty "
        "population and would pass over a brief with no lenses at all")
    missing = sorted(required - set(sb.LENSES))
    assert not missing, (
        "these seats sit on every board and the brief has no lens for "
        f"them, so each gets the standing text and nothing else: {missing}")


def test_an_unknown_seat_name_is_reported_and_does_not_raise(capsys):
    """The emitter names what it knows rather than failing silently.

    Whether an OFF-ROSTER name should exit non-zero is a live design
    question, recorded as owed in
    `private/governance_design/ENFORCEMENT_UNIT_2026-09-02.md` section
    H1. This pins only that the caller is told, which the previous
    version conflated with the claim above."""
    assert sb.main(["seat_brief.py", "--seat", "physics"]) == 0
    assert "FALSE PASS" in capsys.readouterr().out
    assert sb.main(["seat_brief.py", "--seat", "nosuchseat"]) == 0
    assert "known:" in capsys.readouterr().out

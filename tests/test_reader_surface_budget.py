"""The pages a reader meets first are a measured quantity that may only fall.

WHY THIS EXISTS. An outside reading of this repository in August 2026 made
one argument by subtraction: half a million words of documentation is
compatible with extraordinary rigour, with an author who cannot stop
producing artifacts, and with heavy machine generation, and it
DISCRIMINATES BETWEEN NONE OF THEM. A record that grows faster than a
reader can absorb argues against itself.

The reading proposed a ratchet and it was deferred, on the ground that its
seed depended on a restructuring the owner had not approved. That reasoning
was wrong and the same window proved it: the volume finding landed, and the
very next commit added eleven hundred words. On 2026-08-26 a full day was
spent cutting fifty-six thousand words out of docs/, and the same day added
two hundred and sixty-eight to the README. Intentions have never held here
and machines have. A budget seeded today stops the regrowth today, and
re-seeding it after a restructuring is one command.

WHAT IS COUNTED, and the scope is the argument. Not the whole tree: the
FRONT PATH, the pages a reader meets before deciding whether to keep
reading. The wiki, the literature corpus, the preregistrations and the
design chapters are entered deliberately by a reader who already wants
them, and they carry their own guards. This budget is about what stands
between arriving and understanding.

RAISING IT IS ALLOWED AND COSTS A DELIBERATE ACT, the same shape as every
other ratchet here: re-record with --relax after a genuine addition, so the
new number is a decision someone made rather than a drift nobody saw.

RAISED ONCE, five words, and the reason is the point of the whole file.
A register sweep rewrote a provenance sentence in the results ledger's
producer so that it claimed a cross-check against an apparatus log. No such
log establishes that fact, which rests on one person's memory, and the
repaired sentence carries the RECOLLECTION tag instead. It runs five words
longer than the invented one. A budget that made that trade the other way
would be a budget worth deleting.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUDGET_FILE = Path(__file__).with_name("_reader_surface_budget.json")

# The front path, in the order a reader walks it.
#
# THE BLIND REGION, measured 2026-08-26 and stated here because this list was
# HAND-TYPED and a hand-typed list is the failure this repository spent the
# same day mechanising against. START_HERE.md's routing table sends a reader
# to one of TEN first destinations depending on why they came. Four of the ten
# are budgeted below. Six are not: docs/wiki/README.md (3,086 words),
# docs/THEORY_NOTE.md (11,552), docs/ADAPTING.md (5,125), docs/PLAN.md
# (2,663), docs/APPARATUS.md (8,789), and docs/BIG_PICTURE.md, which is added
# here because it is the FIRST destination for "here for the physics result",
# the single most likely reason a hiring reader opens this repository at all.
#
# Budgeting all ten would take the measured surface from 31,476 words to
# 62,691. That is not refused for cost. It is refused because the scope of
# this guard IS its argument: it measures what stands between arriving and
# understanding, and a reader who has chosen THEORY_NOTE or APPARATUS has
# already decided to keep reading. The line is a judgement, it is drawn here,
# and it is written down so that a later session finds a decision rather than
# an oversight.
SURFACE = [
    "README.md",
    "START_HERE.md",
    "docs/plan/00_the-case.md",
    "docs/BIG_PICTURE.md",
    "docs/RESULTS.md",
    "docs/CLAIMS.md",
    "docs/GLOSSARY.md",
]


def _words(rel: str) -> int:
    p = ROOT / rel
    return len(p.read_text(encoding="utf-8").split()) if p.is_file() else 0


def _counts() -> dict:
    return {rel: _words(rel) for rel in SURFACE}


def _budget() -> dict:
    return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))


def test_the_budget_file_covers_the_surface():
    """A budget that has quietly stopped naming a page cannot hold it."""
    assert BUDGET_FILE.is_file(), (
        f"{BUDGET_FILE.name} is missing. Re-record it with:\n"
        f"  python tests/test_reader_surface_budget.py --relax")
    b = _budget()
    missing = [r for r in SURFACE if r not in b]
    assert not missing, (
        "the surface list gained pages the budget does not cover, so they "
        "are unbudgeted and can grow without limit:\n  " + "\n  ".join(missing))


@pytest.mark.parametrize("rel", SURFACE)
def test_no_front_page_grows(rel, capsys):
    """Per page, because one page absorbing another's cut is not a cut."""
    now, cap = _words(rel), _budget().get(rel, 0)
    with capsys.disabled():
        if now != cap:
            print(f"\n  {rel}: {now} words against a budget of {cap}")
    assert now <= cap, (
        f"{rel} grew from {cap} to {now} words. The front path is what a "
        f"reader meets before deciding whether to keep reading, and it may "
        f"only fall. Move the addition to the page that owns the subject, "
        f"or cut something here. After a genuine addition, re-record:\n"
        f"  python tests/test_reader_surface_budget.py --relax")


def test_the_front_path_total_only_falls(capsys):
    """The per-page checks alone let text migrate around the surface."""
    now = sum(_counts().values())
    cap = sum(_budget().get(r, 0) for r in SURFACE)
    with capsys.disabled():
        print(f"\n  front path: {now} words against a budget of {cap}")
    assert now <= cap, (
        f"the front path grew from {cap} to {now} words in total.")


def test_the_budget_is_not_looser_than_reality():
    """A budget above the real count leaves room for a silent regression."""
    slack = {r: (_budget().get(r, 0), _words(r)) for r in SURFACE
             if _budget().get(r, 0) > _words(r)}
    assert not slack, (
        "the budget is looser than the pages are, which is room for growth "
        "nobody would see. Re-record it:\n  "
        + "\n  ".join(f"{r}: budget {b}, actual {a}"
                      for r, (b, a) in sorted(slack.items()))
        + "\n  python tests/test_reader_surface_budget.py --relax")


if __name__ == "__main__":   # python tests/test_reader_surface_budget.py --relax
    if "--relax" in sys.argv:
        before = _budget() if BUDGET_FILE.is_file() else {}
        now = _counts()
        BUDGET_FILE.write_text(json.dumps(now, indent=1, sort_keys=True) + "\n",
                               encoding="utf-8")
        b, a = sum(before.values()), sum(now.values())
        print(f"reader surface re-recorded: {b} -> {a} ({a - b:+d})")
    else:
        print(__doc__.strip().split("\n")[0])

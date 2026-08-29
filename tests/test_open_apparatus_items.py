"""An open apparatus item is spanned by a producer, or nothing rests on it.

WHY THIS EXISTS. On 2026-08-28 a forecast of the next campaign used the 2025
archive's lock drift rate as though it described the lock, which had been
repaired on 2026-08-16. Two chapters of the plan already said so. The failure
was not arithmetic: it was using a number for an apparatus that no longer
exists, because nothing forced the unknowns to be enumerated in one place with
what the forecast does about each.

WHAT THIS GUARD CHECKS, and it is deliberately narrow. Every row of the open
items table in docs/plan/12_open-apparatus-items.md must say, in its last
column, EITHER which committed `results/*.csv` spans the unknown, OR that no
forecast rests on it. Those are the only two honest states for a number
nobody has measured. A row that names neither is an unknown being carried
silently, which is the thing that went wrong.

WHAT IT DOES NOT CHECK. It cannot verify that the producer really spans the
item, only that a row claims one and that the file exists. That is the same
limit every citation guard here has, and it is recorded rather than papered
over.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHAPTER = ROOT / "docs" / "plan" / "12_open-apparatus-items.md"
RESULTS = ROOT / "results"

_CSV = re.compile(r"`?results/([a-z0-9_]+\.csv)`?")
_NOTHING_RESTS = "no forecast rests on it"


def _rows() -> list[tuple[str, str]]:
    """(item, how-the-forecast-proceeds) for each data row of the table."""
    out = []
    for line in CHAPTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != 4 or cells[0].startswith("---") or cells[0] == "item":
            continue
        out.append((cells[0], cells[3]))
    return out


def test_the_chapter_exists_and_has_rows():
    """A guard over an empty set reports a zero that reads as a pass."""
    assert CHAPTER.is_file(), f"{CHAPTER} is missing"
    assert len(_rows()) >= 3, "the open-items table has fewer rows than the "\
        "known unknowns, so it is not being kept"


@pytest.mark.parametrize("item, handling", _rows(),
                         ids=[r[0][:40] for r in _rows()])
def test_every_open_item_is_spanned_or_disclaimed(item, handling):
    named = _CSV.findall(handling)
    if _NOTHING_RESTS in handling.lower():
        return
    assert named, (
        f"the open item {item!r} names neither a producer that spans it nor "
        f"the words {_NOTHING_RESTS!r}. An unmeasured apparatus number must "
        "be spanned by a committed forecast or explicitly rest under nothing")
    for csv_name in named:
        assert (RESULTS / csv_name).is_file(), (
            f"{item!r} claims results/{csv_name} spans it, and that file does "
            "not exist")


def test_the_repaired_lock_is_listed():
    """The instance that produced this guard, kept as a live check.

    The lock was repaired 2026-08-16 and its residual drift is unmeasured. If
    a future session measures it, this row moves out of the table and this
    test is updated with the measurement, not deleted.
    """
    items = " ".join(i for i, _ in _rows()).lower()
    assert "lock" in items, "the repaired lock's residual drift is unmeasured "\
        "and must stay listed until it is measured"


# ---------------------------------------------------------------------------
# THE PLANT. This guard shipped without one, and the rule it broke is the
# repository's own: break the thing it protects, confirm it fires, restore,
# confirm it passes, and state the plant. A guard nobody has seen fail is a
# guard whose passing means nothing.
#
# It is written against the checking LOGIC rather than by editing the chapter
# on disk, because a test that mutates a tracked file leaves the tree dirty
# when it fails, which is the class this record already pays for elsewhere.
# ---------------------------------------------------------------------------

def _verdict(handling: str) -> bool:
    """The guard's own rule, factored so a plant can exercise it."""
    if _NOTHING_RESTS in handling.lower():
        return True
    named = _CSV.findall(handling)
    return bool(named) and all((RESULTS / n).is_file() for n in named)


def test_the_guard_accepts_the_two_honest_states():
    assert _verdict("spanned from 0 to 40 kHz per minute in "
                    "`results/projections.csv`")
    assert _verdict("no forecast rests on it")


def test_the_guard_rejects_an_unknown_carried_silently():
    """PLANT: a row that names neither a producer nor the disclaimer."""
    assert not _verdict("we will find out during the campaign")
    assert not _verdict("estimated at 20 nm from experience")


def test_the_guard_rejects_a_producer_that_does_not_exist():
    """PLANT: a row citing a file that is not in results/."""
    assert not _verdict("spanned in `results/no_such_file.csv`")


def test_the_live_chapter_would_fail_if_a_row_lost_its_handling():
    """The plant applied to a real row rather than to an invented string."""
    rows = _rows()
    assert rows, "no rows to plant against"
    assert all(_verdict(h) for _, h in rows), "the live chapter must pass"
    assert not _verdict(rows[0][1].replace("results/", "resultz/")
                        .replace(_NOTHING_RESTS, "it will be fine"))

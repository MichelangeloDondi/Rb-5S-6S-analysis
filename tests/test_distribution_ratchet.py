"""A ratchet on quantities that report a worst case where a spread belongs.

Protocol rule 19.82, amendment 2026-08-22, clause B. A quantity that varies
across a population is quoted with its spread. Two instances in one day made
this a machine rather than a sentence: a ratio quoted at 3.4 from a single
draw sat at 3.18 plus or minus 0.20 across nine seeds, and a reproduction gap
quoted at its maximum hid a median four orders of magnitude below it. The
second one voided a preregistered run.

WHY A RATCHET, AND THE MEASUREMENT THAT FORCED IT. The obvious guard is the
assertion that every row keyed `max` or `worst` carries a sibling median. That
guard was measured against this corpus BEFORE it was written, which is the
only reason it is not what shipped. It fails immediately: 17 such rows live in
8 files, and two of those files carry no spread row of any kind. It also
matches quantities for which a median is not a defined object. `apex_argmax`
is a location. `ratio_85_up_max` is a design maximum, one number by
construction. A median of an argmax is not a thing.

The status column cannot do the discriminating either, which was the cheaper
design and was measured too: all 17 rows carry `DIAGNOSTIC`, so the existing
vocabulary separates none of them.

So this records a per-file budget that can only fall, the mechanism
`test_prose_style_ratchet.py` already runs for prose and this repository
already understands. Nothing is retrofitted today. Every producer that gains a
spread lowers a number and locks the gain in.

THE ESCAPE. A row leaves the budget in one of two ways: it gains a spread, or
it declares itself single valued by carrying the token `single_valued` in any
of its own cells, with a reason. A bound is legitimately a worst case. The
declaration is deliberately explicit rather than inferred, because the whole
failure being guarded against is a worst case that LOOKED like a summary.

Run `python tests/test_distribution_ratchet.py --relax` after a genuine pass
to re-record. Raising a budget by hand means admitting a producer got worse.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "_distribution_baseline.json"

# The columns this repository actually uses to name a quantity. Measured, not
# guessed: an earlier scan of `quantity` and `key` alone saw 3 files where 8
# exist, and the difference was entirely `name` and `metric` columns. A guard
# that reads fewer columns than the corpus writes is a guard with a blind spot.
KEY_COLUMNS = ("quantity", "key", "name", "metric", "statistic", "label")

# `_max` and `_worst` as whole words. `climax` and `maximal` are not matches.
WORST_CASE = re.compile(r"(^|_)(max|worst)(_|$)|_(max|worst)$", re.I)

# A sibling row carrying any of these means the file reports the distribution
# somewhere. This is recorded as metadata in the report, NOT used to exempt a
# row: proximity in a file is not the same as being the same quantity, and
# treating it as one is how a max gets a median that belongs to something else.
SPREAD = re.compile(
    r"(^|_)(median|mean|p50|std|sigma|spread|iqr|percentile|p\d\d)(_|$)", re.I)

# The escape token, and the FORM it must take. An independent audit on
# 2026-08-23 broke the first version, which was a bare case-insensitive
# substring test over the whole row. Three ways past it, all reproduced:
# a note reading "this quantity is NOT single_valued across seeds" exempted the
# row while SAYING THE OPPOSITE, and a note mentioning an unrelated file called
# `single_valued_candidates.csv` exempted it by coincidence. The docstring
# above claims the declaration is explicit rather than inferred, and a
# substring test does not deliver that.
#
# So the token must appear as a whole word, must not be immediately negated,
# and must be followed by a reason of at least a few characters.
DECLARED = "single_valued"
_DECLARED_RE = re.compile(
    r"(?<![\w-])single_valued\b\s*[:,-]?\s*(?P<reason>\S.{3,})", re.I)
_NEGATED_RE = re.compile(r"\b(not|never|isn't|is not|no)\s+single_valued\b", re.I)


def _declares(cells: list[str]) -> bool:
    """True when ONE cell carries a well-formed single_valued declaration.

    Per cell, not over the joined row. Joining was the first attempt and it
    let the NEXT COLUMN supply the reason: a row whose note read exactly
    "single_valued" passed because the status column's "DIAGNOSTIC" landed
    where the reason should be. The declaration and its reason live in the
    same cell or it is not a declaration.
    """
    for cell in cells:
        if _NEGATED_RE.search(cell):
            continue
        m = _DECLARED_RE.search(cell)
        if m is None:
            continue
        reason = m.group("reason").strip()
        if reason.lower().startswith((".csv", "_candidates")):
            continue        # a filename mention is not a declaration
        return True
    return False


def _tracked_csvs() -> list[str]:
    """Result CSVs this commit would ship: tracked, PLUS untracked not ignored.

    The second half is not optional, for the reason `test_prose_style_ratchet`
    records at length: `git ls-files` cannot see a new file, so a producer
    could add a CSV, watch the gate pass, and commit a file the guard never
    read. That happened once already, to a different guard, on 2026-08-15.
    """
    tracked = subprocess.run(["git", "ls-files", "results/*.csv"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    new = subprocess.run(["git", "ls-files", "--others", "--exclude-standard",
                          "results/*.csv"], cwd=ROOT,
                         capture_output=True, text=True)
    untracked = new.stdout.split() if new.returncode == 0 else []
    return sorted(set(tracked) | set(untracked))


def _undeclared(path: Path) -> tuple[int, int]:
    """(undeclared worst-case entries, spread entries) for one CSV.

    Long-format files are read by their keyed rows. Wide-format files, which
    have no key column and name their quantities in the header, are read by
    their column names instead.
    """
    try:
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
    except (OSError, csv.Error, UnicodeDecodeError):
        return (0, 0)
    if not rows:
        return (0, 0)
    key_cols = [c for c in rows[0] if c and c.lower() in KEY_COLUMNS]
    if not key_cols:
        # WIDE FORMAT, and this branch used to return (0, 0) in silence.
        #
        # An independent audit on 2026-08-23 found the silence and called it a
        # whitelist gap. Measuring it showed something larger and different:
        # 26 of the 63 committed result CSVs carry no key column at all,
        # because they are wide tables whose quantity names are COLUMN HEADERS
        # rather than row keys. The guard was blind to two fifths of the
        # corpus, and no bypass had to be contrived to reach that state.
        #
        # So wide files are scanned on their headers instead of skipped. The
        # blast radius was measured before this was written, as the amendment
        # in protocol 19.82 requires: exactly ONE wide file carries a worst-case
        # column, `ruler_rate_model.csv`'s `t_max_epoch`, so this covers 26 more
        # files for one baseline entry and demands no retrofit.
        bad = sum(1 for c in rows[0] if c and WORST_CASE.search(c.strip()))
        spread = sum(1 for c in rows[0] if c and SPREAD.search(c.strip()))
        return (bad, spread)
    bad = spread = 0
    for row in rows:
        # EVERY key column, matched SEPARATELY. A file carrying both
        # `quantity` and `key` names a row with the PAIR, and reading only the
        # first made the counter blind to the second. Joining them instead was
        # the first repair and it was worse: `_max$` stops matching once a
        # second column follows it, so the count silently FELL from 17 to 12
        # and three files vanished from the report. Both mistakes were caught
        # by the planted-row test on the day this was written.
        # .strip() is load-bearing: WORST_CASE anchors on `_` or end of
        # string, so a single trailing space in the key cell made
        # `ratio_up_max ` invisible to it. Reproduced by the same audit.
        names = [str(row.get(c) or "").strip() for c in key_cols]
        if any(SPREAD.search(n) for n in names):
            spread += 1
        if not any(WORST_CASE.search(n) for n in names):
            continue
        cells = [str(v) for v in row.values() if v]
        if not _declares(cells):
            bad += 1
    return (bad, spread)


def _current() -> dict[str, int]:
    counts = {}
    for rel in _tracked_csvs():
        p = ROOT / rel
        if not p.exists():          # staged deletion
            continue
        bad, _ = _undeclared(p)
        if bad:
            counts[rel] = bad
    return counts


def test_no_producer_gains_an_undeclared_worst_case():
    """Undeclared worst-case rows may fall or hold, never rise."""
    baseline = json.loads(BASELINE.read_text())
    current = _current()

    worse = []
    for rel, now in sorted(current.items()):
        was = baseline.get(rel)
        if was is None:
            worse.append(f"{rel}: NEW file with {now}")
        elif now > was:
            worse.append(f"{rel}: {was} -> {now} (+{now - was})")

    assert not worse, (
        "a producer gained a bare worst case. Quote the distribution: a "
        "quantity that varies across a population carries its spread. If the "
        f"row is a bound and one number is the whole of it, put {DECLARED!r} "
        "in the row with a reason.\n  " + "\n  ".join(worse)
        + "\n\nAfter a genuine pass, re-record with:"
          "\n  python tests/test_distribution_ratchet.py --relax")


def test_the_counter_sees_a_planted_row(tmp_path):
    """The ceiling test: plant one of each and check the counter separates them.

    A ratchet whose counter is broken passes forever while the corpus rots,
    and it passes most convincingly on the day it is written. So the counter
    is exercised against a file built to have one of each case.
    """
    p = tmp_path / "planted.csv"
    p.write_text(
        "quantity,key,value,unit,note,status\n"
        "a,worst_rel_diff,1.0,,,DIAGNOSTIC\n"           # counted
        "b,ratio_up_max,2.0,,,DIAGNOSTIC\n"             # counted
        f"c,bound_max,3.0,,{DECLARED}: a limit,BOUND\n"  # declared, not counted
        "d,median_gap,4.0,,,DIAGNOSTIC\n"               # a spread row
        "e,climax_of_scan,5.0,,,DIAGNOSTIC\n",          # substring, not a match
        encoding="utf-8")
    assert _undeclared(p) == (2, 1)


def test_the_declaration_cannot_be_faked(tmp_path):
    """Three ways past the escape token, all found by an audit on 2026-08-23.

    The first version tested `"single_valued" in row_text.lower()`. A note
    SAYING THE OPPOSITE exempted the row, and so did an unrelated filename that
    happened to contain the token. A bare token with no reason exempted it too,
    though the docstring promises the declaration carries one.
    """
    def one(note, key="worst_rel_diff"):
        f = tmp_path / f"c{abs(hash(note)) % 10**8}.csv"
        f.write_text("quantity,key,value,note,status\n"
                     f"a,{key},1.0,{note},DIAGNOSTIC\n", encoding="utf-8")
        return _undeclared(f)[0]

    assert one("") == 1, "an undeclared row must count"
    assert one("single_valued: it is a preregistered bound") == 0, \
        "a well-formed declaration must exempt"
    # the three fakes
    assert one("this quantity is NOT single_valued across seeds") == 1, \
        "a NEGATED declaration must not exempt"
    assert one("see single_valued_candidates.csv for context") == 1, \
        "the token inside an unrelated filename must not exempt"
    assert one("single_valued") == 1, \
        "a bare token with no reason must not exempt"


def test_trailing_whitespace_cannot_hide_a_row(tmp_path):
    """`ratio_up_max ` used to be invisible, because WORST_CASE anchors on
    `_` or end of string and the key cell was never stripped."""
    f = tmp_path / "ws.csv"
    f.write_text("quantity,key,value,status\n"
                 "a,ratio_up_max ,1.0,DIAGNOSTIC\n", encoding="utf-8")
    assert _undeclared(f)[0] == 1


def test_a_wide_format_file_is_read_by_its_headers(tmp_path):
    """26 of the 63 committed results are wide tables with no key column.

    They returned (0, 0) before a row was read until 2026-08-23, so the guard
    was blind to two fifths of the corpus.
    """
    f = tmp_path / "wide.csv"
    f.write_text("peak,t_min_epoch,t_max_epoch,rate_median,status\n"
                 "4121,1.0,2.0,3.0,DIAGNOSTIC\n", encoding="utf-8")
    assert _undeclared(f) == (1, 1)


if __name__ == "__main__":  # `python tests/test_distribution_ratchet.py --relax`
    import sys
    if "--relax" in sys.argv:
        cur = _current()
        old = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
        BASELINE.write_text(json.dumps(cur, indent=1, sort_keys=True) + "\n")
        before, after = sum(old.values()), sum(cur.values())
        print(f"baseline re-recorded: {before} -> {after} ({after - before:+d})")
    else:
        for rel, n in sorted(_current().items()):
            bad, spread = _undeclared(ROOT / rel)
            print(f"{rel:46} undeclared={bad}  spread_rows={spread}")
        print(f"total undeclared: {sum(_current().values())}")

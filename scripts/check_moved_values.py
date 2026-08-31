#!/usr/bin/env python3
"""Every literal a results/ cell has EVER held is grepped for in the tree.

    python scripts/check_moved_values.py [--history N]   # default N = 40

WHY THIS EXISTS. `check_references.py` resolves numbers carrying a `ref:`
tag, so its population is the MARKED set. On 2026-08-28 a wave corrected
every marked copy of eighteen moved values and left every plain typed copy
stale: a hand-typed mode table in a campaign chapter, five cells in the
correction record the release note cites as its disclosure, four docstrings
inside the module the repair fixed, a producer comment, and a CSV note's
reference to its own sibling row. This population is the COMPLEMENT of the
citation checker's.

FOUR DEFECTS FOUND BY ONE BOARD ON 2026-08-29, AND THE REPAIRS ARE HERE.
The first form of this file diffed two named commits. Three seats found it
vacuous over the very class it was built for, and a fourth proved why on the
history rather than arguing it.

* THE VALUE COLUMN WAS READ AT POSITION 2, on a docstring claim that
  `(scope, quantity, value)` is "the shape every results CSV in this tree
  uses". Measured 2026-08-31: 80 CSVs (this count moved with the tree; the
  header-shape census below was taken at 78). For the
  `quantity,value,unit` shape the old key embedded the changing value and
  read the UNIT as the value, so detection on those files was 0 BY
  CONSTRUCTION. That false universal was written in the docstring of the
  fixture built to catch false universals. The column is found by NAME now.
* A BAND NEVER ENTERED THE POPULATION. The row filter demanded a bare
  decimal, and a band (`73 to 98`) is the dominant value shape in the fibre
  CSVs -- the files this guard was written for. Bands are graded as bands,
  and their endpoints separately.
* `docs/history/` WAS SKIPPED WHOLESALE, on the ground that a hit there is
  the account of the change. True of the `was` column and false of the `now`
  column, and a stale `now` cell in the page a release note names as its
  disclosure is what found this. The skip is column-aware now.
* THE WINDOW WAS ONE DIFF AND IT WAS THE WRONG ONE. A value that moved
  before the chosen base is invisible, and every value this board caught had
  moved in the commit BEFORE the base a brief handed the seats. The window is
  now the whole unpushed RANGE -- every literal a cell held at any commit in
  `origin/main..HEAD` -- so a wave is graded as a wave. It is deliberately
  not the file's whole history: measured over 156 commits the run returned
  1,765 findings, because prose legitimately quotes values retired long ago,
  and a guard whose findings are mostly false trains the eye to skip it.

WHAT WAS TRIED AND REJECTED, because a rejected design is worth more than a
silent one. A seat proposed grading NEAR NEIGHBOURS of current values -- any
number within a few per cent of a committed cell -- so that a value which was
never right, rather than one that moved, would also be caught. Implemented,
it returned 16,552 findings on a clean tree, because a file citing one CSV is
compared against every cell of it and an unrelated `50.37 A` matches a `52.4`
from another row. A guard whose findings are mostly false trains the eye to
skip it, which is worse than no guard. The class it aimed at is real and is
the first blind region below, named rather than covered by a noisy check.

THE PLANT FAILED, AND THAT IS THE MOST USEFUL THING THIS FILE KNOWS.
Three of the board's own defects were re-inserted to confirm the rewrite
caught them -- a stale `now` cell in `docs/history/09`, a stale mode area in
this package's docstrings, a stale band in a note. **It fired on none of
them**, and the reason is not a bug:

* `results/onf_lever_ranking.csv` and `results/guided_mode_tables.csv` DO NOT
  EXIST at `origin/main`. They were born in this wave, so no value in them
  has ever moved and the retired-literal set for them is empty.
* `0.611` appears nowhere in any CSV's history: `git log -S` over
  `guided_mode_tables.csv` returns nothing. It was a docstring figure
  computed under the pre-Malitson silica index.
* `4.955` was likewise never a committed cell.

So THE DOMINANT DEFECT CLASS OF 2026-08-29 IS NOT THE ONE THIS FILE
DETECTS. It is not "a value moved and its copies went stale" but "a number
was written into prose that never matched the CSV at all", and no
propagation check in any window can see it, because there is nothing to have
moved from. The counter for that class already exists and is not a new
guard: a number carrying a `ref:` tag is RESOLVED against its cell by
`check_references.py`, so it cannot be born wrong. Every defect that board
found was an untagged plain number. Widen the tagged population; do not
widen this one.

What this file does still catch is real and is what it was built for: the
2026-08-28 wave moved eighteen committed values and left every untagged copy
stale across six files. That class recurs and this is the cheap detector for
it. A synthetic instance is pinned in `tests/test_moved_values.py`, because
a guard whose only plant FAILED must carry one that passes.

THE FALSE-PASS DIRECTION, MEASURED RATHER THAN GUESSED.

* A NUMBER THAT WAS NEVER COMMITTED CANNOT BE SEEN, per the plant above.
  `74 to 99 kHz` was hand-typed into a note in the same commit that computed
  `73 to 98` into the CSV, so it was wrong from birth. This is a PROPAGATION
  check; a number typed wrong the first time needs a reader or a `ref:` tag.
* A PARTIALLY stale band is invisible: matching is on the whole band string,
  so `73 to 181` where the cell holds `73 to 98` and `98 to 181` is retired
  matches neither. Its endpoints are advisory only, because a bare `181`
  collides with `range(0, 181, 5)`.
* A file NEW in the graded range contributes nothing, since none of its
  values has moved. This is the first-commit blindness this record already
  names, arriving in a third instrument.
* A number in no CSV cell at all is ungradeable however far it drifts:
  `fibre.py`'s `0.46725`, the `485 to 796` diagnostic pasted into five
  places, the intermediate `0.3686` an exponential comparison quotes.
* A copy in a file that quotes the number WITHOUT naming its CSV is out of
  scope, and that scope is what makes the run readable: unscoped, the first
  form returned 281 hits of which nearly all were collisions.
* A stale copy at a precision the CSV does not use (`0.61` for `0.611`).
* A value restated in words.
* A CSV with no `value` column is skipped, and the run PRINTS how many,
  because a skipped file is not a checked one.

Exit 1 on any finding, 0 when clean, 2 on usage or when nothing could be
compared. The gate distinguishes them: 2 is not a clean bill.
"""
from __future__ import annotations

import csv
import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The whole unpushed wave. A wave is what the commit team reads and what a port
# carries, so it is the unit a propagation check should grade.
DEFAULT_BASE = "origin/main"

ROW_GONE = "(row retired)"

# Columns that describe a row rather than identify it. Everything else is the
# row's key, which is what lets an old literal be reported with the row it
# belonged to. Reading the key at a fixed POSITION is the defect above.
_DESCRIPTIVE = {"value", "err", "err_lo", "err_hi", "err_lo16", "err_hi84",
                "err_kind", "unit", "note", "basis", "status", "source",
                "formula", "assumptions", "evidence_class", "aux",
                "aux_unit", "measured", "predicted"}

# A hit on one of these is an ACCOUNT of the change, which is what it is for.
ACCOUNT_MARKERS = (
    "until 2026-", "corrected 2026-", "used to read", "used to say",
    "retired", "retracted", "withdrawn", "no longer", "earlier draft",
    "was wrong", "formerly", "stood at", "read as",
    # Added 2026-08-29 from the forms a clean run actually reported as
    # findings: every one was a sentence doing its job. Guessed markers are
    # how a skip list ends up wrong on the day it is written.
    "used to", "in place of", "hardcoded", "it asserted", "that band read",
    "assumed_parameter", "legacy", "before the solve", "replaced",
)

# Under private/: captured process output and regenerable bulk, not claims.
# A suite log QUOTES a failing assertion, so grading it reports the defect the
# log exists to record; `cache/` holds a board's queued findings, which quote
# the stale value on purpose.
_PRIVATE_SKIP = {".git", "cache", "run_logs", "internal", "Manuals",
                 "qc_gallery", "qc_gallery_prev_layout", "__pycache__"}

BINARY_SUFFIXES = (".png", ".pdf", ".jpg", ".jpeg", ".npz", ".npy", ".gz",
                   ".zip", ".ico", ".woff", ".woff2", ".ttf", ".xlsx")

ADVISORY_CAP = 12

# A dated filename under private/ is a RECORD by this repository's own
# convention -- a closure note, a morning brief, an audit, a transcript --
# and a record quotes retired values deliberately. The release note, the
# protocols and the checkers carry no date and stay in the population, which
# is the gap this scan was extended to cover.
_DATED = re.compile(r"20\d\d-\d\d-\d\d")

_NUM_ONLY = re.compile(r"-?\d+(?:\.\d+)?")
_BAND_ONLY = re.compile(r"(-?\d+(?:\.\d+)?)\s+to\s+(-?\d+(?:\.\d+)?)")


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout


def _batch_blobs(specs: list[str]) -> dict[str, str]:
    """{`<sha>:<path>`: contents} in ONE git process.

    A `git show` per commit per file is 78 x 40 subprocesses and took longer
    than the gate step it sits in. `git cat-file --batch` reads every blob
    from one pipe, which is the same work in one fork.
    """
    if not specs:
        return {}
    proc = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch"],
                          input=("\n".join(specs) + "\n").encode(),
                          capture_output=True)
    out, i, got = proc.stdout, 0, {}
    for spec in specs:
        nl = out.find(b"\n", i)
        if nl < 0:
            break
        header = out[i:nl].decode("utf-8", "replace").split()
        if len(header) < 3:          # "<oid> missing"
            i = nl + 1
            continue
        size = int(header[2])
        got[spec] = out[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        i = nl + 1 + size + 1        # payload plus its trailing newline
    return got


def _sig_digits(s: str) -> int:
    """Significant digits, so distinctiveness is measured and not guessed."""
    return len(re.sub(r"[-.]", "", s).lstrip("0")) or 1


def _rows(text: str) -> list[dict[str, str]] | None:
    try:
        rows = list(csv.DictReader(io.StringIO(text)))
    except csv.Error:
        return None
    if not rows or "value" not in rows[0]:
        return None
    return rows


def _keyed(rows: list[dict[str, str]]) -> dict[tuple, str]:
    """{identity key: value cell}. The key is every non-descriptive column."""
    out: dict[tuple, str] = {}
    for i, row in enumerate(rows):
        key = tuple((k, (v or "").strip()) for k, v in row.items()
                    if k and k not in _DESCRIPTIVE)
        out[key or (("_row", str(i)),)] = (row.get("value") or "").strip()
    return out


def _literals(cell: str) -> list[tuple[str, bool]]:
    """[(literal, blocks)] a cell contributes: itself, and a band's endpoints.

    A band ENDPOINT on its own collides constantly -- `range(0, 181, 5)` in a
    test hit the retired `98 to 181` band -- while the band STRING is
    distinctive. So the endpoints are carried for reporting and do not block.
    """
    cell = cell.strip().strip('"')
    m = _BAND_ONLY.fullmatch(cell)
    if m:
        return [(cell, True), (m.group(1), False), (m.group(2), False)]
    if _NUM_ONLY.fullmatch(cell):
        return [(cell, True)]
    return []


def retired_literals(base: str) -> tuple[
        dict[str, dict[str, tuple[str, str]]], list[str], int]:
    """{csv: {retired literal: (row key, what it holds now)}}, skipped, commits.

    Every literal the `value` column held at ANY commit in `base..HEAD`,
    and at `base` itself, MINUS everything the file holds now anywhere in it
    -- so a value that merely moved from one row to another is not reported.

    THE RANGE IS THE UNIT, NOT THE COMMIT. Reading one diff was the defect:
    the values this wave left stale had moved in the commit before the base a
    brief named, so three separate invocations all reported clean.
    """
    stale: dict[str, dict[str, tuple[str, str]]] = {}
    skipped: list[str] = []
    commits = 0
    for p in sorted((ROOT / "results").glob("*.csv")):
        rel = p.relative_to(ROOT).as_posix()
        rows = _rows(p.read_text(encoding="utf-8", errors="replace"))
        if rows is None:
            skipped.append(rel)
            continue
        now = _keyed(rows)
        current = {lit for cell in now.values()
                   for lit, _ in _literals(cell)}
        history = _git("log", "--format=%H", f"{base}..HEAD",
                       "--", rel).split() + [base]
        commits += len(history)
        blobs = _batch_blobs([f"{h}:{rel}" for h in history])
        for spec in blobs:
            old = _rows(blobs[spec])
            if old is None:
                continue
            for key, cell in _keyed(old).items():
                for lit, blocks in _literals(cell):
                    if lit in current:
                        continue
                    name = " ".join(v for _, v in key if v)[:52]
                    stale.setdefault(rel, {}).setdefault(
                        lit, (name, now.get(key, ROW_GONE), blocks))
    return stale, skipped, commits


def history_now_columns(lines: list[str]) -> dict[int, set[int]]:
    """For docs/history/ tables, the cell indices carrying the NEW value.

    Those tables are `| quantity | was | now | file |`. Grading the whole row
    reports the `was` cell, which is the account and is what the old wholesale
    directory skip was really avoiding; skipping the directory instead blinded
    the guard to `now`. The columns are read from each table's own header.
    """
    graded: dict[int, set[int]] = {}
    current: set[int] | None = None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            current = None
            continue
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if current is None:
            if "was" in cells and ({"now", "to"} & set(cells)):
                current = {j for j, c in enumerate(cells) if c in ("now", "to")}
            else:
                current = set(range(len(cells)))
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue                                    # the |---| separator
        graded[i] = current
    return graded


def scannable() -> list[Path]:
    """Tracked text files, PLUS private/, which git here cannot see any more.

    `private/` became its own repository on 2026-08-29, so `git ls-files` in
    THIS repository does not list it, and the release note a board convenes to
    bless had no propagation protection at all -- structurally and
    permanently, rather than by a decision anyone took. Only files that NAME a
    results CSV are opened, so the correspondence and career material there
    are never read.
    """
    out = [ROOT / f for f in _git("ls-files").split()
           if not f.startswith("results/") and not f.endswith(BINARY_SUFFIXES)]
    priv = ROOT / "private"
    if priv.is_dir():
        # THE POPULATION IS NAMED, NOT GLOBBED, and it is narrow on purpose.
        # This scan was extended into private/ for ONE artifact: the release
        # note, which a board convenes to bless and which no propagation
        # check could see. Recursing further swept in the board reports,
        # which quote the stale value they FOUND, and `manuscripts/`,
        # where a median delta chi-square of 232 collided with a retired
        # transit width. Both are records, and a record quoting a retired
        # value is doing its job. Correspondence and career material are
        # never opened at all.
        for pat in ("*.md", "checks/*.py"):
            out += [q for q in sorted(priv.glob(pat))
                    if q.is_file() and not _DATED.search(q.name)]
    return out


def scan(stale: dict[str, dict[str, tuple[str, str]]],
         paths: list[Path]) -> tuple[list[str], list[str]]:
    findings: list[str] = []
    advisories: list[str] = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            rel = path.relative_to(ROOT).as_posix()
        except ValueError:
            rel = str(path)
        cited = [c for c in stale if c in text or Path(c).name in text]
        if not cited:
            continue
        lines = text.splitlines()
        hist_cols = (history_now_columns(lines)
                     if rel.startswith("docs/history/") else None)
        for n, line in enumerate(lines, 1):
            if any(m in line.lower() for m in ACCOUNT_MARKERS):
                continue
            if hist_cols is not None:
                keep = hist_cols.get(n - 1)
                if keep is None:
                    continue
                cells = line.strip().strip("|").split("|")
                probe = " ".join(c for j, c in enumerate(cells) if j in keep)
            else:
                probe = line
            # THE LINE IS TOKENISED ONCE, not searched once per literal.
            # Searching per literal is O(retired x lines) and took longer
            # than the gate step this sits in; the tokens on a line are a
            # handful, so the comparison is a set lookup.
            written = {m.group(0) for m in _NUM_ONLY.finditer(probe)}
            written |= {f"{m.group(1)} to {m.group(2)}"
                        for m in _BAND_ONLY.finditer(probe)}
            if not written:
                continue
            for csv_rel in cited:
                for lit in written & stale[csv_rel].keys():
                    row, now, blocks = stale[csv_rel][lit]
                    msg = (f"{rel}:{n}: writes {lit!r}, which {csv_rel} "
                           f"({row}) now holds as {now!r}\n"
                           f"      {line.strip()[:92]}")
                    # A RETIRED ROW IS NOT A STALE COPY. When the row itself
                    # is gone the record is SUPPOSED to keep quoting its old
                    # value, in the chapter explaining why it went: the
                    # `neff_band = 1.08 to 1.25` retirement alone produced
                    # most of one clean run's findings, every one of them a
                    # sentence doing its job. Reported, never blocking.
                    distinctive = blocks and (" to " in lit
                                              or _sig_digits(lit) >= 3)
                    if now == ROW_GONE or not distinctive:
                        advisories.append(msg)
                    else:
                        findings.append(msg)
    return findings, advisories


def main(argv: list[str]) -> int:
    base = argv[1] if len(argv) > 1 else DEFAULT_BASE
    if not _git("rev-parse", "--verify", base).strip():
        fallback = "HEAD~1"
        print(f"check_moved_values: cannot resolve {base!r}; falling back to "
              f"{fallback}, which is a NARROWER window than intended.")
        base = fallback
        if not _git("rev-parse", "--verify", base).strip():
            print("check_moved_values: no usable base, so nothing was "
                  "compared and this silence is not evidence.")
            return 2

    stale, skipped, commits = retired_literals(base)
    n_lit = sum(len(v) for v in stale.values())
    print(f"check_moved_values: {n_lit} retired literal(s) from "
          f"{len(stale)} CSV(s) over {commits} commit(s) of history; "
          f"{len(skipped)} CSV(s) carry no `value` column and were NOT checked")
    if not stale:
        # AN EMPTY RESULT HAS TWO CAUSES AND ONLY ONE IS A BROKEN WINDOW.
        # Until 2026-08-29 both returned 2, so a commit touching no results/
        # CSV could never satisfy this check: the gate refused a test-only
        # commit on the ground that a propagation checker had found no
        # propagation to check. That is a guard whose passing state is
        # unreachable, which this record has built once before and named.
        touched = [ln for ln in _git("diff", "--name-only", base, "HEAD")
                   .splitlines() if ln.startswith("results/")
                   and ln.endswith(".csv")]
        if not touched:
            print("  NOTHING TO CHECK, and that is COMPLETE rather than "
                  "empty: no results/ CSV changed in this window, so no "
                  "value could have moved and there is nothing to compare.")
            return 0
        print("  NOTHING TO CHECK: results/ CSVs changed in this window but "
              "no value moved, so this compares nothing and its silence is "
              "not evidence.")
        return 2

    findings, advisories = scan(stale, scannable())

    if advisories:
        print(f"\n  ADVISORY, {len(advisories)} hit(s) on literals under "
              f"three significant digits, which collide easily. These never "
              f"fail the run and need a person:")
        for a in advisories[:ADVISORY_CAP]:
            print(f"    {a}")
        if len(advisories) > ADVISORY_CAP:
            print(f"    ... and {len(advisories) - ADVISORY_CAP} more, not "
                  f"listed. Read them with a wider cap before trusting this "
                  f"line.")

    if findings:
        print(f"\ncheck_moved_values: FAIL, {len(findings)} stale copy(ies) "
              f"of a retired literal\n")
        for f in findings:
            print(f"  {f}")
        print("\n  Each carries no ref: tag, so the citation checker cannot "
              "see it.\n  Fix it, or move the sentence into an account that "
              "says the value is retired.")
        return 1

    print("\ncheck_moved_values: clean on distinctive retired literals "
          "and bands")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

"""The err-cell format ratchet: nonconforming cells only fall per file.

LOGIC 8a.2 (two significant digits on the uncertainty, the value
matching its decimals) was guarded on markdown and on figure canvases
while the committed results' own err columns had no reader: an audit
counted 397 of 544 cells across 21 files falling short. A ban would
demand hundreds of regenerations in one wave, so this is the ratchet
form the agonistic counter established: each file's nonconforming
count is frozen at today's measurement and may only fall, and the
producers that regenerate a file pay its debt through the shared
`rb5s6s.pmfmt` cells. Reseeding takes --reseed --reason and lands a
row in the ratchet history book.

FALSE-PASS DIRECTION, stated first: a CSV without an `err` column
head, or an empty err cell, contributes nothing, so a producer that
DROPS its uncertainties reads as conforming here; the
carries-an-uncertainty guard owns that direction.

Plant, held by the in-file control: a three-significant-digit cell
fails conformance through the same checker the scan uses.
"""
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

from rb5s6s.pmfmt import fmt_err, in_plain_band

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_results_err_format_baseline.json")
BOOK = Path(__file__).with_name("_ratchet_history.md")


def _conforms(value: str, err: str) -> bool:
    try:
        e = float(err)
    except ValueError:
        return True          # non-numeric err notes are not cells
    canonical = fmt_err(e)
    if err.strip() != canonical:
        return False
    # 8a.2a: a plain cell outside the plain-decimal band is nonconforming
    # even when its digits are right -- the factored form is owed, and
    # the ratchet counts it rather than blessing it
    try:
        v = float(value)
    except ValueError:
        v = 0.0
    if not in_plain_band(v, e):
        return False
    edec = len(err.split(".")[1]) if "." in err else 0
    vdec = len(value.split(".")[1]) if "." in value else 0
    return vdec == edec


def _counts() -> dict[str, int]:
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "results/*.csv"],
        capture_output=True, text=True).stdout.split()
    out: dict[str, int] = {}
    for rel in tracked:
        path = ROOT / rel
        if not path.is_file():
            continue
        with open(path, newline="") as fh:
            reader = csv.DictReader(fh)
            if not reader.fieldnames or "err" not in reader.fieldnames:
                continue
            if "value" not in reader.fieldnames:
                continue
            vfield = "value"
            n = sum(1 for row in reader
                    if (row.get("err") or "").strip()
                    and not _conforms((row.get(vfield) or "").strip(),
                                      row["err"].strip()))
        if n:
            out[rel] = n
    return out


def test_the_population_is_alive():
    """A ratchet that matches nothing is not a ratchet (the axis and
    distribution ratchets carry the same control): the scan must see
    the tracked results corpus, not an empty ls-files."""
    counts = _counts()
    assert len(counts) >= 10, (
        f"the err-format scan sees {len(counts)} files against a corpus "
        "in the twenties; the population plumbing broke")


def test_the_baseline_is_not_slack():
    """The other direction: a paid-down file keeps its old ceiling only
    until this fires, so every fall is re-recorded through the book and
    cannot silently regress."""
    import json as _json
    base = _json.loads(BASELINE.read_text())["files"]
    now = _counts()
    slack = {r: (base[r], now.get(r, 0)) for r in base
             if now.get(r, 0) < base[r]}
    assert not slack, (
        "counts fell below their frozen ceilings; record the falls: "
        "python tests/test_results_err_format.py --reseed --reason "
        '"..." -- ' + ", ".join(f"{r} {a}->{b}" for r, (a, b)
                                in sorted(slack.items())))


def test_err_cells_only_fall():
    base = json.loads(BASELINE.read_text())["files"]
    worse = []
    for rel, n in _counts().items():
        was = base.get(rel, 0)
        if n > was:
            worse.append(f"{rel}: {was} -> {n}")
    assert not worse, (
        "err cells fell out of the two-digit rule where the count was "
        "frozen; write them through rb5s6s.pmfmt.pm_cells, or reseed "
        "with a reason the book records:\n  " + "\n  ".join(worse))


def test_the_conformance_plant_fires():
    assert _conforms("3.00", "0.78")
    assert not _conforms("3.001", "0.779"), "three digits must fail"
    assert not _conforms("3.0", "0.78"), "decimal mismatch must fail"
    assert _conforms("1.2", "note text")
    # the band's own plant: digits conform (fmt_err(320) is 320) while
    # the magnitude sits outside the plain band, so only the 8a.2a arm
    # can refuse it -- the arm's live marginal is zero on the committed
    # corpus and this is what keeps it exercised
    assert not _conforms("100", "320"), "the band arm must refuse"
    assert not _conforms("0.0002", "0.0009"), "the too-small side too"


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        i = sys.argv.index("--reason") if "--reason" in sys.argv else -1
        if i < 0 or i + 1 >= len(sys.argv):
            raise SystemExit('reseed refuses without --reason "..."')
        new = {"files": _counts()}
        old_total = 0
        if BASELINE.exists():
            old_total = sum(json.loads(
                BASELINE.read_text())["files"].values())
        BASELINE.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        from datetime import date
        with BOOK.open("a") as fh:
            fh.write(f"| {date.today()} | results_err_format | reseed "
                     f"{old_total} -> {sum(new['files'].values())} | "
                     f"{sys.argv[i + 1].replace(chr(124), chr(47))} |\n")
        print(f"seeded {len(new['files'])} files, "
              f"total {sum(new['files'].values())}")

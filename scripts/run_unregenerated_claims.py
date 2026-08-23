#!/usr/bin/env python
"""A governed row about ungoverned numbers.

WHY THIS FILE EXISTS. On 2026-08-23 a published regression was found whose
numbers no committed producer computes and no results/ row holds, and the audit
that followed found the same of seven of the ten notes it read. The structural
reason is that EVERY freshness instrument in this repository starts from a
results/ row: verify_results_fresh compares a CSV to its producer, and the
committed-CSV test does the same. A number that never became a row is outside
the domain of both, so the guarantee "results/ is regenerated and checked" says
nothing at all about it.

The notes now DECLARE what they stand on, in prose, with a `provenance:` token.
Prose is where the problem started. This producer reads those declarations and
emits them as rows, so the size of the gap becomes a number the freshness
machinery grades like any other, and so a reader can count it without opening
ten files.

WHAT THIS DOES NOT DO. It does not give any of those numbers a producer. Seven
notes still rest on computations nothing regenerates, and this file measures
that rather than repairing it. A row saying NO_PRODUCER is an honest label on a
gap, and reading it as closure would be the exact error it exists to prevent.

WHY IT SCANS RATHER THAN LISTS. A hardcoded inventory here would be a literal
in a producer, which is the failure this repository has already met twice: a
figure drew a retracted value from a literal in its generator, and a bootstrap
factor reached docs/RESULTS.md the same way. So the rows are DERIVED from the
declarations in docs/notes/, and a declaration that changes without this being
re-run fails the freshness test. The instrument is subject to the rule it
enforces.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs" / "notes"
OUT = ROOT / "results" / "unregenerated_claims.csv"

DECL = re.compile(
    r"provenance:\s*(?P<kind>`?results/[A-Za-z0-9_./-]+\.csv`?"
    r"|`?[A-Za-z0-9_./-]+\.py::[A-Za-z_][A-Za-z0-9_]*`?"
    r"|DESIGN|PREREG|INDEX|NO_PRODUCER)",
    re.I,
)
# The same widened claim pattern the ratchet uses. Kept in step deliberately:
# the two files disagreeing about what a claim is, is how the first version
# reported a clean corpus while a page carrying sixteen numbers scored one.
CLAIM = re.compile(
    r"(?<![\w.])[-+]?\d+(?:\.\d+)?\s*"
    r"(?:sigma|per cent|%|MHz|kHz|Hz|uK|mK|mW|W|mbar|nm|um|ms|counts?|dof)"
    r"|\*\*[-+]?\d+(?:\.\d+)?\*\*",
    re.I,
)
# "**N numeric claims on this page remain unaccounted for.**"
ORPHANS = re.compile(r"\*\*(?P<n>\d+)\s+numeric claims? on this page remains? unaccounted for", re.I)
NONE_LEFT = re.compile(r"No claim on this page is unaccounted for", re.I)


def _scan() -> list[dict]:
    rows = []
    for p in sorted(NOTES.glob("*.md")):
        text = p.read_text()
        m = DECL.search(text)
        if not m:
            continue
        kind = m.group("kind").strip("`")
        mo = ORPHANS.search(text)
        if mo:
            orphans = int(mo.group("n"))
        elif NONE_LEFT.search(text):
            orphans = 0
        else:
            orphans = -1          # declared, count not stated
        rows.append({"note": p.name, "kind": kind, "orphans": orphans})
    return rows


def _undeclared() -> dict:
    """Notes that carry numeric claims and declare nothing at all."""
    out = {}
    for p in sorted(NOTES.glob("*.md")):
        text = p.read_text()
        n = len(CLAIM.findall(text))
        if n and not DECL.search(text):
            out[p.name] = n
    return out


def main() -> int:
    scanned = _scan()
    rows = []

    def add(scope, quantity, value, unit, note):
        rows.append({"scope": scope, "quantity": quantity, "value": value,
                     "unit": unit, "note": note, "status": "DIAGNOSTIC"})

    no_producer = [r for r in scanned if r["kind"].upper() == "NO_PRODUCER"]
    has_csv = [r for r in scanned if r["kind"].lower().startswith("results/")]
    has_code = [r for r in scanned if ".py::" in r["kind"]]
    design = [r for r in scanned if r["kind"].upper() in ("DESIGN", "PREREG", "INDEX")]
    counted = [r for r in scanned if r["orphans"] > 0]

    add("SUMMARY", "notes_declared", len(scanned), "count",
        "notes under docs/notes/ carrying a provenance declaration. The ratchet "
        "in tests/test_note_provenance_ratchet.py holds the undeclared count at "
        "zero, which means every note SAYS what it stands on and NOT that every "
        "number is graded")
    add("SUMMARY", "notes_no_producer", len(no_producer), "count",
        "notes whose own argument rests on numbers no committed producer "
        "regenerates. These are published and ungoverned by every freshness "
        "instrument here, because all of them start from a results/ row")
    add("SUMMARY", "notes_with_results_home", len(has_csv), "count",
        "notes whose headline numbers were traced to a committed CSV")
    add("SUMMARY", "notes_with_code_producer", len(has_code), "count",
        "notes regenerated by a committed pure function rather than a CSV. This "
        "kind did not exist until 2026-08-23, and its absence had produced a "
        "FALSE NO_PRODUCER declaration, because the only available options were "
        "worse than the truth")
    undeclared = _undeclared()
    add("SUMMARY", "notes_undeclared", len(undeclared), "count",
        "notes carrying numeric claims that declare NOTHING. This is the "
        "instrument's own recorded debt and it is reported here rather than "
        "left in a test baseline, because the first version of this file scored "
        "it at ZERO using a claim pattern that could not see most numbers")
    add("SUMMARY", "undeclared_claims_total", sum(undeclared.values()), "count",
        "numeric claims on those undeclared notes")
    add("SUMMARY", "notes_design_or_index", len(design), "count",
        "notes whose numbers are proposed parameters, preregistered thresholds "
        "or quoted from their own children, so no results/ home is expected")
    add("SUMMARY", "orphan_claims_total", sum(r["orphans"] for r in counted), "count",
        "individual numeric claims unaccounted for INSIDE declared notes, "
        "summed over the notes that state a count. A declared note is not a "
        "clean note")

    for r in sorted(scanned, key=lambda x: (x["kind"].upper() != "NO_PRODUCER", x["note"])):
        add(r["note"], "provenance", r["kind"], "declaration",
            f"{r['orphans']} claim(s) unaccounted for on this page"
            if r["orphans"] >= 0 else "declared, count not stated")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scope", "quantity", "value", "unit", "note", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} with {len(rows)} rows")
    for r in rows[:5]:
        print(f"  {r['scope']:12} {r['quantity']:26} {r['value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

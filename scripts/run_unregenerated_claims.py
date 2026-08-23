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



# --- the consequence partition, added 2026-08-23 ------------------------------
# COUNTING the gap was the easy half. What matters is whether an ungoverned
# number reaches a surface a reader ACTS on, so this partitions the claims of
# every NO_PRODUCER note into three classes and reports the one that matters.
#
# TWO FILTERS, both learned by measuring before asserting. First, a value under
# three significant figures cannot be grepped against a repository full of
# numbers: auditing `99.8` returned five matches and all five were noise,
# including a detector saturation voltage of 399.8 V. Those go in their own
# counted class rather than into the answer. Second, and this one inverted the
# result: a NO_PRODUCER note still QUOTES committed values, so the first
# version of this partition returned 30 reader-facing hits that were dominated
# by peak identifiers (993.4121 nm) and by grounded numbers the note cites,
# such as kappa_ub95 and the committed natural width. Excluding values that
# appear in any results/ CSV takes the answer from 30 to ONE.
VALUE = re.compile(
    r"(?<![\w.])([-+]?\d+\.\d+)\s*"
    r"(sigma|per cent|%|MHz|kHz|Hz|uK|mK|mW|W|mbar|nm|um|ms)", re.I)
NO_PROD = re.compile(r"provenance:\s*`?NO_PRODUCER", re.I)
FRONT_GLOBS = ("docs/RESULTS.md", "docs/BIG_PICTURE.md", "docs/CLAIMS.md",
               "README.md", "docs/big_picture/*.md", "docs/wiki/*.md",
               "docs/plan/*.md")


def _sigfigs(v: str) -> int:
    d = v.lstrip("+-").replace(".", "").lstrip("0")
    return len(d.rstrip("0")) if d else 0


def _partition() -> dict:
    front = []
    for g in FRONT_GLOBS:
        front.extend(sorted(ROOT.glob(g)) if "*" in g else
                     ([ROOT / g] if (ROOT / g).is_file() else []))
    front_text = {f.name: f.read_text(errors="ignore") for f in front}
    # THIS FILE IS EXCLUDED FROM ITS OWN GROUNDING TEST, and the freshness
    # guard is what found the need. The partition NAMES the reader-facing
    # orphan in a note column, so a second run found 0.6325 inside
    # unregenerated_claims.csv, counted it as present in results/, and
    # reclassified it from orphan to quoted. The instrument was eating its own
    # output and the count moved 40 to 41 between runs.
    # THE PRINCIPLE, not just the fix: a value appearing in the provenance
    # instrument's own prose is not evidence that a producer regenerates it.
    # Self-reference is not provenance.
    results_blob = "".join(f.read_text(errors="ignore")
                           for f in sorted((ROOT / "results").glob("*.csv"))
                           if f.name != OUT.name)

    generic = quoted = 0
    reader_facing = []
    for p in sorted(NOTES.glob("*.md")):
        text = p.read_text()
        if not NO_PROD.search(text):
            continue
        seen = set()
        for m in VALUE.finditer(text):
            v = m.group(1)
            if (v, p.name) in seen:
                continue
            seen.add((v, p.name))
            if _sigfigs(v) < 3:
                generic += 1
                continue
            if v in results_blob:          # the note cites a committed row
                quoted += 1
                continue
            where = [n for n, t in front_text.items() if v in t]
            if where:
                reader_facing.append(f"{p.name}: {v} {m.group(2)} -> {', '.join(where[:3])}")
    return {"generic": generic, "quoted": quoted, "reader_facing": reader_facing}


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

    part = _partition()
    add("PARTITION", "claims_too_generic_to_grep", part["generic"], "count",
        "values under three significant figures in NO_PRODUCER notes. Grepping "
        "these against a repository full of numbers returns noise, so they are "
        "counted here rather than answered. Auditing 99.8 returned five matches "
        "and all five were false, one of them a detector saturation voltage")
    add("PARTITION", "claims_quoted_from_results", part["quoted"], "count",
        "values in NO_PRODUCER notes that DO appear in a committed CSV. A note "
        "resting on ungoverned numbers still cites grounded ones, and counting "
        "those as orphans took an earlier version of this partition from ONE "
        "reader-facing hit to thirty")
    add("PARTITION", "orphans_on_reader_facing_surfaces",
        len(part["reader_facing"]), "count",
        "THE NUMBER THAT MATTERS: ungoverned values quoted on a page a reader "
        "acts on. " + ("; ".join(part["reader_facing"]) if part["reader_facing"]
                       else "none") + ". A release blocker is an entry here with "
        "neither a producer nor a disclosure")
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

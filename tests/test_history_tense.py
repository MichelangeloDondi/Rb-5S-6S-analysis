"""A history entry may carry a replaced NUMBER. It may not assert the present.

WHY THIS EXISTS, and it is a genuinely new class rather than a sibling of the
guards already in `test_history_form.py`. On 2026-08-27 two correction-record
entries were found asserting a state that had since changed:

  * `history/08` said a sentence "now states the exclusion's two-sigma
    strength", written when that was true and left standing after the
    strength was retired;
  * `history/01` said "The calibrated prediction is 0.348 MHz", in the
    present tense, after that row was retagged and a later value replaced
    the one it names.

**Neither is a wrong number, which is exactly why nothing caught them.**
History is the one place in this repository where a replaced value is
licensed to appear, so every sweep that hunts retracted digits skips
`docs/history/` by design. That licence is what makes a stale TENSE invisible
here and nowhere else.

WHAT ALREADY EXISTED AND COULD NOT SEE IT:

  * `test_history_form.py::test_no_entry_runs_long` caps entries at 150 words.
    A stale tense is short.
  * `test_history_form.py::test_entries_naming_no_live_value_file_only_fall`
    is the nearest relative and the reason this guard is narrow: it already
    requires an entry's "now" VALUE to name a file where the live value can
    be read. It has no purchase on a "now" claim about PROSE, which names no
    value and so owes no file.
  * `test_reference_coverage.py` counts unreferenced decimals, and both
    defects are decimal-free in the offending clause.

THE RULE. An entry records what was DONE, in the past tense. "The sentence was
rewritten to define S0" is durable. "The sentence now defines S0" is a claim
about the present that decays the moment the sentence changes again, and the
correction record is the last place anyone will look for it.

THE ESCAPE, deliberately narrow: a present-tense clause that names a
`results/` path is fine, because that is the checkable form the sibling guard
already governs. Everything else is flagged with a falling baseline, because
the existing entries are a debt to pay down and not a wall to hit today.

THIS GUARD'S BLIND REGION, measured before it was admitted rather than
discovered later. It catches the FIRST defect above and is SILENT on the
second, and that is deliberate. "The calibrated prediction is 0.348 MHz"
names a VALUE, and an entry naming a value already owes a live-value file
under `test_entries_naming_no_live_value_file_only_fall`, whose budget stands
at eleven entries. So the second defect is a debt in an EXISTING guard, not a
gap needing a new one, and paying that budget down is what closes it. I
measured the alternative: a present-tense-copula-plus-number pattern fires
ten times across the correction record, almost all of them inside legitimate
was-and-now table cells. A guard reporting mostly false positives has a zero
that means nothing, which is the failure this repository names as a blind
ratchet. So the pattern was refused and the coverage stated instead.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_history_tense_baseline.json")

# "now <verb>" and bare present-tense state claims. Deliberately not a general
# tense detector: this bank is the shapes the two real defects took.
_PRESENT = re.compile(
    r"\bnow\s+(?:states?|reads?|says?|carr(?:y|ies)|quotes?|defines?|stands?|holds?|names?|points?|labels?|identif(?:y|ies)|calls?|marks?|terms?|lists?|cites?|shows?|gives?|takes?|uses?)\b"
    r"|\bis\s+currently\b"
    r"|\bthe\s+current\s+value\s+is\b"
    r"|\brepaired\s+in\s+the\s+commit\s+that\s+follows\b",   # a promise read as a fact (docs/history/02, 2026-09-04)
    re.I)
# a clause naming a results/ path is the checkable form the sibling guard owns
_ESCAPE = re.compile(r"results/[\w./-]+\.csv")
# the escape applies only to a claim carrying a number in its clause; the class
# excludes semicolons only, since a results path carries a period of its own
# and the sentence is already the unit (a seat planted "now names results/x.csv,
# 0.611 MHz", 2026-09-04)
_NUMERIC = re.compile(r"\bnow\s+\w+\s+[^;]*?(?<![\w/.-])-?\d", re.I)   # a digit inside a filename (kernel_k3.csv) is not a number


def _claim_flagged(sent: str) -> bool:
    """A sentence is flagged when it carries a present-tense claim and is not
    escaped: the escape needs a results/ path AND a number in the claim."""
    m = _PRESENT.search(sent)
    return bool(m) and not (_ESCAPE.search(sent) and _NUMERIC.search(sent))


def _units(para: list[str]) -> list[str]:
    """The units a paragraph is judged in: a table row is its own unit (a cell
    must not borrow a neighbouring cell's path or number to escape), and prose
    splits at every stop followed by whitespace, so a sentence that starts with
    a lowercase path cannot merge with the claim before it (a seat planted
    that, 2026-09-04; a capital-lookahead splitter had merged them)."""
    if any(ln.lstrip().startswith("|") for ln in para):
        # each CELL is a unit: a claim in one cell must not borrow a path or
        # number from another cell of the same row (a seat planted that too)
        return [c.strip() for ln in para for c in ln.strip().strip("|").split("|") if c.strip()]
    return re.split(r"(?<=[.!?])\s+", " ".join(ln.strip() for ln in para))


def _entries() -> list[tuple[str, int, str]]:
    # the hub joined 2026-09-04 (H11a: every guard that reads the record reads
    # the hub and the chapters); its count entered the baseline as debt
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "docs/history/*.md", "docs/HISTORY.md"],
                         capture_output=True, text=True)
    found = []
    for rel in out.stdout.split():
        path = ROOT / rel
        if not path.exists():
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        # sentence-scoped since 2026-09-04: the escape is judged on the
        # sentence carrying the claim, so a reflow that moves a clause onto
        # the line of a results/ path cannot excuse it (a seat planted that)
        start = 0
        while start < len(lines):
            end = start
            while end < len(lines) and lines[end].strip():
                end += 1
            para = lines[start:end]
            for sent in _units(para):
                m = _PRESENT.search(sent)
                if _claim_flagged(sent):
                    # the line of the match, or of its first word when the match
                    # straddles a wrapped line (the default pointed at the
                    # paragraph's first line, a seat found, 2026-09-04)
                    k = next((j for j, ln in enumerate(para) if m.group(0) in ln), None)
                    if k is None:
                        k = next((j for j, ln in enumerate(para) if m.group(0).split()[0] in ln), 0)
                    found.append((rel, start + k + 1, sent.strip()[:110]))
            start = end + 1
    return found


def _counts() -> dict[str, int]:
    c: dict[str, int] = {}
    for rel, _, _ in _entries():
        c[rel] = c.get(rel, 0) + 1
    return c


def test_the_escape_needs_a_number_and_reads_it_on_either_side_of_the_path():
    """The worked examples of the bank's comment, as a test: a claim naming a
    file and no number stays flagged; a number before or after the path
    escapes (the after case failed until 2026-09-04, when the class
    excluded the period every results path carries)."""
    assert _claim_flagged("The sentence now names results/x.csv.")
    assert not _claim_flagged("The sentence now names 0.611 MHz, in results/x.csv.")
    assert not _claim_flagged("The sentence now names results/x.csv, 0.611 MHz.")
    assert _claim_flagged("The sentence now names it as the duel's, near the archive's own.")
    assert _claim_flagged("The table now names results/kernel_k3.csv as the source.")
    assert not _claim_flagged("The row now reads -0.978 MHz, in results/x.csv.")


def test_the_units_split_prose_at_every_stop_and_keep_rows_apart():
    """A violation cannot borrow the next sentence's path and number: the
    splitter cuts at every stop, whatever follows, and a table row stands
    alone (a seat's plant of 2026-09-04 merged two sentences under a
    capital-lookahead splitter and the count did not move)."""
    units = _units(["The retained value now identifies the wrong isotope entirely.",
                    "results/plant_test.csv carries 0.611 MHz for the corrected row."])
    assert len(units) == 2 and _claim_flagged(units[0]) and not _claim_flagged(units[1])
    cells = _units(["| a | now states 0.611 (`results/x.csv`) | b |"])
    assert len(cells) == 3 and not _claim_flagged(cells[1]), "a cell with its own path and number escapes on its own"
    cross = _units(["| a | now states 0.611 | `results/x.csv` |"])
    assert _claim_flagged(cross[1]), "a cell cannot borrow the next cell's path"
    lone = _units(["| a | now states the wrong sign | b |", "| c | 0.611 | `results/x.csv` |"])
    assert _claim_flagged(lone[1]), "a cell cannot borrow the next row's path and number"


def test_present_tense_claims_in_history_only_fall():
    current = _counts()
    base = json.loads(BASELINE.read_text()) if BASELINE.is_file() else {}
    risen = {k: (base.get(k, 0), v) for k, v in current.items()
             if v > base.get(k, 0)}
    detail = "\n  ".join(f"{rel}:{ln}: {txt}" for rel, ln, txt in _entries()
                         if rel in risen)
    assert not risen, (
        "a correction-record entry gained a present-tense claim about the "
        "current state. History is licensed to carry replaced NUMBERS, which "
        "is why a stale TENSE is invisible here: every digit sweep skips "
        "docs/history/ by design. Write what was DONE, in the past tense, or "
        "name the results/ file where the live value can be read.\n  "
        + detail +
        "\n\nAfter a genuine addition: python tests/test_history_tense.py --reseed")


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        BASELINE.write_text(json.dumps(_counts(), indent=1, sort_keys=True) + "\n")
        print(f"reseeded {BASELINE.name} over {len(_counts())} file(s)")

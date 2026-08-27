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
    r"\bnow\s+(?:states|reads|says|carries|quotes|defines|stands|holds)\b"
    r"|\bis\s+currently\b"
    r"|\bthe\s+current\s+value\s+is\b",
    re.I)
# a clause naming a results/ path is the checkable form the sibling guard owns
_ESCAPE = re.compile(r"results/[\w./-]+\.csv")


def _entries() -> list[tuple[str, int, str]]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "docs/history/*.md"],
                         capture_output=True, text=True)
    found = []
    for rel in out.stdout.split():
        path = ROOT / rel
        if not path.exists():
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _PRESENT.search(line) and not _ESCAPE.search(line):
                found.append((rel, i, line.strip()[:110]))
    return found


def _counts() -> dict[str, int]:
    c: dict[str, int] = {}
    for rel, _, _ in _entries():
        c[rel] = c.get(rel, 0) + 1
    return c


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

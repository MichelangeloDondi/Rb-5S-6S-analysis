"""A retraction is not complete until the retracted string is absent.

WHY THIS EXISTS, and it is the most-requested guard in this repository's
history: four independent board seats across two rounds proposed it from
different evidence on 2026-08-27, and it was built only after five hand
sweeps had failed on one phrase.

THE FAILURE IT ANSWERS. A claim is withdrawn on the pages the withdrawal
touched, and re-enters on a page that only cites them. On 2026-08-27 one
retracted summary -- a binary count of leave-one-out arms -- survived in
FOUR places after being removed from eight, and three of the four were
written by the same wave that was retracting it: a plan table cell that
cited RESULTS.md C3f as its authority while contradicting it, a
preregistration bracket, and a matplotlib docstring whose own next sentence
named this very class. A fourth, in a producer's f-string, would have been
REGENERATED into a committed CSV.

WHY EVERY EXISTING GUARD MISSED IT, which is the design constraint:

  * `test_docs_math_render` and `test_docs_links` parametrise over
    `*.md`. A literal inside `scripts/*.py` is invisible to them.
  * The prose banks in `test_repo_hygiene.py` read tracked prose files,
    not `results/*.csv` note columns.
  * `verify_results_fresh.py` re-runs producers, and `stark_joint.csv` is
    UNCOVERED there by written decision, so its notes can never be reached
    that way at all.
  * A hand grep is a hand-chosen population. Mine matched
    "three of the four arms" and the surviving text read "three of four
    leave-one-out arms". That is the population-of-measurement principle:
    a validation claim is only as strong as the population visible to the
    validator.

So this scans a STATED SUBSET of the tracked set, and it reads committed
bytes, which means it needs no producer to run and reaches the files freshness
cannot. The subset is every tracked file whose suffix is in _TEXT_SUFFIXES,
minus bulk numeric csv. It is not the whole tracked set and this comment said
it was until a board seat read the file: 86 png, 11 jpg, one ipynb and one bib
are outside it. Saying WHOLE here while the population assertion below checks
a floor is exactly the overclaim this guard exists to forbid, committed in its
own opening paragraph.

TWO MATCHING RULES EARN THEIR PLACE. Text is WHITESPACE-FLATTENED before
matching, because a phrase broken across a line defeats a line-based grep
and this record has already paid for that once. And a hit is FORGIVEN when
a retraction marker sits within a stated window of it, because the record
must be able to quote a retracted claim in order to retract it -- the
correction record, the history chapters and the withdrawal sentences
themselves all legitimately contain the string.

CHECKED TWICE AGAINST A BROKEN TREE, and the first check did not fire,
which is what measures the blind region below.

  * First: the phrase was inserted into `run_stark_joint.py`'s corrected
    note, which already carries "withdrawn 2026-08-27" a few words away.
    The guard stayed GREEN. That is the marker window forgiving a hit
    because a retraction marker for the SAME claim sat beside it, which is
    correct behaviour and a demonstration that this guard cannot police
    text that lives inside a retraction.
  * Second: the phrase was appended to `docs/GLOSSARY.md`, with no marker
    within the window, which is the shape the real defect had. The guard
    went RED, named the file and quoted the span. Restored, green.

The real 2026-08-27 defect had no marker near it in any of its sites, so
this guard would have fired on its own finding, which is the condition this
repository requires of a new guard before it is admitted.

THIS GUARD'S BLIND REGION, measured rather than discovered later, and the
first check above is the measurement. The marker window is character-counted and not
sentence-aware, so a retraction marker belonging to a DIFFERENT nearby claim
will forgive a hit that deserves to fail. That is a false negative and it was chosen deliberately:
the alternative, a bank whose exemption list must be maintained per file,
is the design that failed for `test_lit_quotes_are_verbatim` and trained
the eye to skip failures. The bank is also opt-in -- it catches what it was
told about and nothing else, so it does not replace reading.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BANK = Path(__file__).with_name("_retracted_phrases.json")

# Text-ish tracked files. Binary and data blobs are skipped: a retracted
# phrase cannot hide in a PNG, and the digitised CSVs are numbers.
_TEXT_SUFFIXES = {".md", ".py", ".csv", ".sh", ".toml", ".cff", ".yml", ".yaml", ".json"}
# Skip by (directory, suffix) and NEVER by directory alone. A wholesale
# directory skip blinds this guard to prose living beside binary assets:
# figures/README.md is a real caption table, edited in this very wave, and a
# prefix skip made it permanently invisible. Binaries are already excluded by
# _TEXT_SUFFIXES, so what is left to skip is bulk NUMERIC csv.
# data_recovered/ holds raw trace csv of the same character and is NOT skipped.
# That is deliberate and safe: scanning more can only add findings, never hide
# one, and the cost is milliseconds.
_SKIP_NUMERIC_CSV = ("docs/apparatus/", "data_raw/")


def _tracked_text_files() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                         capture_output=True, text=True)
    keep = []
    for rel in out.stdout.split("\n"):
        if not rel or Path(rel).suffix not in _TEXT_SUFFIXES:
            continue
        if rel.endswith(".csv") and any(rel.startswith(d) for d in _SKIP_NUMERIC_CSV):
            continue
        if rel == "tests/_retracted_phrases.json" or rel == "tests/test_retracted_phrases.py":
            continue          # the bank names the phrases; it is not a survival
        keep.append(rel)
    return keep


def _bank() -> dict:
    return json.loads(BANK.read_text(encoding="utf-8"))


def _flat(text: str) -> str:
    """Collapse whitespace so a wrapped phrase still matches."""
    return re.sub(r"\s+", " ", text)


@pytest.mark.parametrize("entry", _bank()["entries"],
                         ids=lambda e: e["pattern"][:34])
def test_a_retracted_phrase_does_not_survive_in_the_tree(entry):
    markers = [m.lower() for m in _bank()["markers"]]
    pat = re.compile(entry["pattern"], re.I)
    win = int(entry.get("marker_window", 400))
    hits = []
    for rel in _tracked_text_files():
        path = ROOT / rel
        try:
            flat = _flat(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
        for m in pat.finditer(flat):
            ctx = flat[max(0, m.start() - win):m.end() + win].lower()
            if any(k in ctx for k in markers):
                continue      # quoted inside its own retraction
            hits.append(f"{rel}: ...{flat[max(0, m.start() - 90):m.end() + 90].strip()}...")
    assert not hits, (
        f"a phrase retired on {entry['retired']} survives in the tree, outside "
        f"any retraction marker.\n\nWHY IT WAS RETIRED: {entry['why']}\n\n"
        + "\n".join(f"  {h}" for h in hits[:8])
        + "\n\nEither rewrite the site, or if it is quoting the claim in order "
          "to withdraw it, put a retraction marker within "
          f"{win} characters of it.")


def test_the_banks_population_is_stated_and_does_not_collapse():
    """A guard that scans nothing passes. State what it actually reads.

    This does NOT claim to read the whole tracked set: binaries and bulk
    numeric csv are out by design, so the population is a stated subset and
    the assertion below is a floor against silent collapse, not a claim of
    completeness. An earlier name for this test asserted completeness while
    checking a floor, which is the thing this file exists to forbid.
    """
    files = _tracked_text_files()
    assert len(files) > 200, f"population collapsed to {len(files)} files"
    # prose beside binary assets must be IN, which a directory skip broke once
    assert "figures/README.md" in files
    kinds = {Path(f).suffix for f in files}
    # the three populations every prior guard was missing, named explicitly
    for need in (".py", ".csv", ".md"):
        assert need in kinds, f"{need} files are not in this guard's population"
    assert any(f.startswith("scripts/") for f in files)
    assert any(f.startswith("results/") for f in files)

"""Unreferenced decimal claims per file fall and never rise.

The resolver in test_references.py checks the references that exist. This
ratchet is about the ones that do not: a decimal number in prose with no
inline reference is a claim the anti-staleness machinery cannot protect,
exactly the class that produced the retracted band digits and the four
public figures with no producer. It cannot be banned outright, because a
date, a version and a section number are numbers too, so it takes the
falling-baseline shape every debt here takes: seeded at the measured
counts, allowed down, never up.

THE MEASURE, stated so its blind region is on record: decimal tokens
(digits, a point, digits) in prose, after code spans, fenced blocks, math,
link targets, URLs and file paths are stripped, excluding tokens already
inside a reference link's text. Integers are not counted, which spares
dates and counts and misses integer-valued claims; a paraphrase carries no
token at all. Both misses are recorded in the design note rather than
discovered later.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_reference_coverage_baseline.json")

_STRIP = re.compile(
    r"```.*?```|`[^`]*`|\$\$.*?\$\$|\$[^$\n]*\$"
    r"|\[(?P<t>[^\]]+)\]\(\s*[^)\s]+\s+\"ref:[^\"]+\"\s*\)"  # referenced
    r"|\]\([^)]*\)|https?://\S+"
    r"|\b[\w/.-]+\.(?:md|csv|py|png|jpg|jpeg|json|sh|txt|pdf|yml|toml)\b"
    r"|^\s{4,}\S.*$",
    re.S | re.M)
_DECIMAL = re.compile(r"\b\d+\.\d+\b")


def _tracked_markdown() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files",
                          "docs/*.md", "README.md"],
                         capture_output=True, text=True)
    return out.stdout.split()


def _counts() -> dict[str, int]:
    # Re-seeded 2026-08-25 for ONE decimal: docs/ADAPTING.md's units
    # section illustrates the metres-for-nanometres trap with "microns
    # give 0.99". That is a pedagogical example of a WRONG input, not a
    # claim about the apparatus, so it has no source to reference and
    # referencing it would be false. Recorded here because a re-seed
    # without its reason is how a falling ratchet stops falling.
    #
    # Re-seeded again for the wiki figure captions, and the re-seed is
    # only recorded because the guard EARNED it. Seven pages gained one
    # decimal each, every one of them in a caption under a new figure.
    # Each was resolved to its source before the seed moved: 2.405 is the
    # first zero of J0; 993.4192 nm, 5.41 MHz, 11.86 bits, leverage 0.94
    # and the factor 3.2 all resolve to committed rows. The seventh did
    # NOT. A caption put the 6.25 MHz tooth spacing on the transition
    # axis, where the constant is Omega and not Omega/2, and reading the
    # page to fix it found the same error three lines above in prose. A
    # caption is a claim surface that gets less scrutiny than the prose
    # it sits under, which is the fig15 class exactly.
    #
    # Re-seeded a third time for the eight docs/history/ chapters, which are
    # new files rather than new claims: docs/HISTORY.md became a hub over a
    # directory and its entries moved out under it. The hub's count did not
    # fall, because the hub keeps a quantity index that restates each
    # entry's old and new value on purpose, so the same decimal is now
    # counted in two files. That duplication is the index's whole function
    # and it is also a place a value could drift, which is why it is
    # written down here rather than absorbed silently.
    counts: dict[str, int] = {}
    for rel in _tracked_markdown():
        path = ROOT / rel
        if not path.exists() or rel.startswith("docs/lit/"):
            continue
        text = _STRIP.sub(" ", path.read_text(encoding="utf-8"))
        n = len(_DECIMAL.findall(text))
        if n:
            counts[rel] = n
    return counts


def test_unreferenced_decimals_only_fall():
    current = _counts()
    baseline = json.loads(BASELINE.read_text())
    grew = {k: (baseline.get(k, 0), v) for k, v in current.items()
            if v > baseline.get(k, 0)}
    assert not grew, (
        "files gained unreferenced decimal claims. Either add an inline "
        "reference to the source (the design note has the syntax) or, "
        "after confirming the additions are legitimate, re-seed with "
        "python tests/test_reference_coverage.py --reseed:\n  "
        + "\n  ".join(f"{k}: {a} -> {b}" for k, (a, b) in sorted(grew.items())))


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        BASELINE.write_text(json.dumps(_counts(), indent=1, sort_keys=True)
                            + "\n")
        print(f"reseeded {BASELINE.name} over {len(_counts())} files")

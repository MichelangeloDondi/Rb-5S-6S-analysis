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
        "after a genuine review, re-seed with "
        "python tests/test_reference_coverage.py --reseed:\n  "
        + "\n  ".join(f"{k}: {a} -> {b}" for k, (a, b) in sorted(grew.items())))


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        BASELINE.write_text(json.dumps(_counts(), indent=1, sort_keys=True)
                            + "\n")
        print(f"reseeded {BASELINE.name} over {len(_counts())} files")

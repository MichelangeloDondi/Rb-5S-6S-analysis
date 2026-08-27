"""docs/HISTORY.md keeps the form the history protocol fixes for it.

WHY THIS EXISTS. The correction record is the file a reader opens to decide
whether a number can be trusted, and it is the file most easily read the
wrong way. Fifty-nine entries at a median of 263 words read as a monument to
error. The same facts at sixty words each, indexed by quantity, read as a
record in which every number has a traceable lineage. The information is the
same and the inference a reader draws is opposite, so the form is not
cosmetic and is checked here.

The rules are private/HISTORY_PROTOCOL.md. Two of them are mechanical and
live here. H10, that every register bank except the retired-value one reads
this file, is enforced in test_repo_hygiene.py by a per-label exemption
rather than by the blanket one the file used to sit on.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "docs" / "HISTORY.md"
CHAPTERS = ROOT / "docs" / "history"


def _history_sources() -> list[Path]:
    """The hub plus every chapter under it.

    The record became a hub over a directory on 2026-08-26, the same shape
    docs/plan/ and docs/big_picture/ already use. This guard reads BOTH, so
    a chapter cannot become the place the rules do not reach, which is the
    exemption failure this file's own subject already demonstrated once.
    """
    out = [HISTORY] if HISTORY.is_file() else []
    if CHAPTERS.is_dir():
        out += sorted(CHAPTERS.glob("*.md"))
    return out

# H3. An entry is at most this many words. A correction needing more has a
# home elsewhere and the entry points at it. The ceiling is generous against
# the protocol's own target so that a genuinely intricate lineage fits.
ENTRY_WORDS = 120
CEILING_SLACK = 1.25          # a fifth over, before the test calls it a defect

# Sections that are not entries: the header block and the reader-facing
# apparatus at the top of the file.
_NOT_AN_ENTRY = re.compile(
    r"^## (How to use this file"
    r"|What moved, and where the live value is"
    r"|Why this file exists"
    r"|The chapters"
    r"|The bound history)\b")


def _sections() -> list[tuple[str, str]]:
    out = []
    for src in _history_sources():
        text = src.read_text(encoding="utf-8")
        for block in re.split(r"\n(?=## )", text):
            if not block.startswith("## "):
                continue
            out.append((block.split("\n", 1)[0], block))
    return out


def _entries() -> list[tuple[str, str]]:
    return [(h, b) for h, b in _sections() if not _NOT_AN_ENTRY.match(h)]


def test_the_file_has_entries_at_all():
    """A guard that silently measures nothing passes forever."""
    assert len(_entries()) >= 20, (
        f"only {len(_entries())} entries parsed out of "
        f"{len(_sections())} sections: the entry heading convention moved "
        f"and this guard stopped seeing the file")


def test_no_entry_runs_long(capsys):
    """H3. Length is the signal, and it was pointing the wrong way."""
    ceiling = int(ENTRY_WORDS * CEILING_SLACK)
    long = []
    for head, body in _entries():
        # tables carry lineage compactly and are not prose
        prose = "\n".join(ln for ln in body.split("\n")
                          if not ln.lstrip().startswith("|"))
        n = len(prose.split())
        if n > ceiling:
            long.append(f"{n:5d}w  {head[:74]}")
    with capsys.disabled():
        counts = [len("\n".join(ln for ln in b.split("\n")
                                if not ln.lstrip().startswith("|")).split())
                  for _, b in _entries()]
        counts.sort()
        print(f"\n  history: {len(counts)} entries, median "
              f"{counts[len(counts) // 2]}w, longest {counts[-1]}w")
    assert not long, (
        f"entries over the {ceiling}-word ceiling (H3, target {ENTRY_WORDS}). "
        f"An entry is four facts: the quantity, what it was, what it is now "
        f"with its file, and the cause in one clause. Reasoning belongs on "
        f"the page carrying the live value, and a lesson belongs in the rule "
        f"that now enforces it.\n  " + "\n  ".join(long))


# H11. The file never summarises itself. A count of corrections is not a
# quantity anyone needs, and stating it invites the reading this file exists
# to prevent.
# The pattern must demand a QUANTITY. Its first version matched any word
# before the noun, so "a correction" and "day entries" fired it, which is
# the guard crying wolf on its own subject matter.
_COUNT = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven"
          r"|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen"
          r"|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
          r"|hundred|dozens?|several|many|numerous)")
_NOUN = r"(?:corrections?|entries|retractions?|withdrawals?|mistakes?|errors?)"
_SELF_SUMMARY = [
    # (?<![\d-]) keeps a DATE out of it: "The 2026-08-17 corrections" is an
    # entry heading, not the record counting itself.
    rf"(?<![\d-])\b{_COUNT}[- ]?(?:{_COUNT})?\s+{_NOUN}\b",
    rf"\b{_NOUN}\s+(?:so far|to date|in total|and counting)\b",
    rf"\bthis (?:file|record|page) (?:now )?(?:holds|carries|contains|lists)"
    rf"\s+{_COUNT}\b",
]


@pytest.mark.parametrize("pattern", _SELF_SUMMARY)
def test_the_file_does_not_count_itself(pattern):
    """H11. No total, no tally, no framing of how many things were wrong."""
    flat = " ".join(" ".join(s.read_text(encoding="utf-8")
                             for s in _history_sources()).split())
    hits = [m.group(0) for m in re.finditer(pattern, flat, re.I)]
    assert not hits, (
        "the correction record counts its own corrections. The number of "
        "mistakes is not a quantity a reader needs, and printing it invites "
        "the reading the file exists to prevent (H11).\n  "
        + "\n  ".join(hits[:6]))


# H2 and H6 as a FALLING BUDGET, not a wall. Fourteen entries name no file
# for the live value, and every one of them inherited that from an original
# that named none either: the rewrite was forbidden to invent a path, and
# the agents correctly refused rather than guessing one. Recording the debt
# at its measured size makes it visible and lets it only shrink, which is
# the pattern this repository already uses for provenance. Lower it by
# finding the real live-value file for an entry, never by deleting the
# entry or by pointing it somewhere plausible.
# 14 -> 11 on 2026-08-26. Three were paid down by naming the file that
# actually holds the live value: the waist entry gained its lit note, the
# emphasis-capitals entry gained the test and allowlist that hold the rule
# now, and the polarizability entry written the same day named its CSV row
# from the start. Lower this again only by finding a real home for an entry,
# never by deleting the entry or pointing it somewhere plausible.
NAKED_ENTRY_BUDGET = 11


def test_entries_naming_no_live_value_file_only_fall(capsys):
    """H2 and H6. An entry that retires a value says where the live one is.

    Checked as a link or a backticked path somewhere in the entry, which is
    the weakest form of the rule that can be mechanised: whether the target
    is the RIGHT file is a reading, not a test.
    """
    naked = []
    for head, body in _entries():
        if not (re.search(r"\]\([^)]+\)", body) or re.search(r"`[\w./-]+\.(?:csv|md|py)`", body)):
            naked.append(head[:74])
    with capsys.disabled():
        print(f"\n  history: {len(naked)} entries owe a live-value file "
              f"(budget {NAKED_ENTRY_BUDGET})")
    assert len(naked) <= NAKED_ENTRY_BUDGET, (
        f"{len(naked)} entries retire a value without naming a file where "
        f"the live value lives, against a budget of {NAKED_ENTRY_BUDGET}. A "
        f"reader who lands on one has nowhere to go (H2, H6):\n  "
        + "\n  ".join(naked))

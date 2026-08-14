"""No document repeats a long block of itself.

WHY THIS EXISTS. `START_HERE.md` carried the same twenty-eight lines twice,
one after the other, in both repositories. The block contained the run
instructions, a code fence, the reproducibility sentence and two bullets, so
a reader following the five-minute path met the whole section, then met it
again. It had been that way through several releases and every gate was
green, because nothing anywhere compares a document against itself.

It also carried a factual error into the public tree twice rather than once,
which is the second reason this check is worth its cost: a duplicated block
duplicates whatever is wrong inside it, and doubles the chance a correction
misses a copy.

WHAT IT DOES NOT CATCH, deliberately. Tables and fenced code repeat for good
reasons. The append-only preregistrations quote the data an addendum amends,
which is the contract those documents are written under, and two of them do
exactly that today at eight and six lines. So table rows and fence contents
are excluded from the count, and the threshold sits above the largest
legitimate prose repeat measured across every tracked document rather than
at some round number.

MEASURED BEFORE CHOOSING THE THRESHOLD (2026-08-14, both repositories, 177
tracked `.md` each): exactly three files contained a repeated block of four
or more identical non-blank lines. START_HERE at twenty-two,
PREREGISTRATION_RESULTS at eight, and the ruler preregistration at six, the
last of which is entirely table rows. Ten is therefore clean today with the
duplication removed, and it leaves the two append-only records room to keep
doing what they are for.

SCOPE IS WHAT GIT TRACKS, and that is not a detail. The first version of this
guard walked the filesystem, which scanned 180 documents in the working
repository and 177 in the mirror, because a working tree also carries
untracked notes and scratch directories that no clone ever sees. A guard that
reads a different set of files in each repository is one nobody can trust, and
one that fails on somebody's untracked notes gets weakened rather than obeyed.
The subject here is PUBLISHED documents, so the denominator is
`git ls-files`.
"""
from __future__ import annotations

import subprocess

import pytest

from rb5s6s import config as C

# Prose lines in one repeated block. Chosen from the measurement in the
# docstring: above the largest legitimate repeat, below the defect that
# prompted the check.
MAX_REPEATED_PROSE_LINES = 10


def _tracked_markdown():
    """Every committed `.md`, or None when this is not a git checkout."""
    try:
        done = subprocess.run(
            ["git", "-C", str(C.REPO_ROOT), "ls-files", "--", "*.md"],
            capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return sorted(done.stdout.split())


def _documents():
    rels = _tracked_markdown()
    if rels is None:
        return []
    out = []
    for rel in rels:
        path = C.REPO_ROOT / rel
        if not path.is_file():          # deleted but still staged
            continue
        out.append((rel, path.read_text(encoding="utf-8").split("\n")))
    return out


def _prose_mask(lines):
    """True where a line counts toward duplication.

    A table row or a line inside a fence repeats legitimately, so neither
    counts. Blank lines carry no content and would otherwise let two
    unrelated paragraphs join across whitespace.
    """
    mask, in_fence = [], False
    for raw in lines:
        line = raw.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            mask.append(False)
            continue
        mask.append(bool(line) and not in_fence and not line.startswith("|"))
    return mask


def longest_repeated_block(lines):
    """(prose lines, first start, second start) of the longest repeat, 1-based.

    Two occurrences of the same run of lines, non-overlapping. Returns
    (0, None, None) when the document never repeats itself.
    """
    mask = _prose_mask(lines)
    where = {}
    for i, raw in enumerate(lines):
        if mask[i]:
            where.setdefault(raw.strip(), []).append(i)

    best = (0, None, None)
    for occurrences in where.values():
        if len(occurrences) < 2:
            continue
        for a_idx, i in enumerate(occurrences):
            for j in occurrences[a_idx + 1:]:
                run = 0
                while (j + run < len(lines) and i + run < j
                       and lines[i + run].strip() == lines[j + run].strip()):
                    run += 1
                prose = sum(1 for k in range(i, i + run) if mask[k])
                if prose > best[0]:
                    best = (prose, i + 1, j + 1)
    return best


_DOCS = _documents()


@pytest.mark.parametrize("rel,lines", _DOCS, ids=[r for r, _ in _DOCS])
def test_a_document_does_not_repeat_a_long_block_of_itself(rel, lines):
    """A reader who meets the same section twice stops trusting the map."""
    count, first, second = longest_repeated_block(lines)
    assert count <= MAX_REPEATED_PROSE_LINES, (
        f"{rel} repeats {count} lines of prose verbatim, at line {first} and "
        f"again at line {second}. Delete one copy, or if both are wanted, "
        f"replace the second with a link to the first. Tables and fenced code "
        f"are already excluded from this count.")


def test_the_detector_can_see_duplication_at_all():
    """The positive control, because an empty result proves nothing.

    Two preregistrations legitimately restate the data their addenda amend.
    Those repeats sit below the threshold and are not defects, but they are
    the proof that this detector is looking: if a refactor breaks the
    scanner, or `git ls-files` stops resolving, the checks above would pass
    vacuously and silently, which is the failure mode this project has hit
    more than once.
    """
    if _tracked_markdown() is None:
        pytest.skip("not a git checkout, so the tracked-file scope is unavailable")
    assert len(_DOCS) > 100, (
        f"the duplication guard is reading {len(_DOCS)} documents, which is "
        f"far fewer than this repository tracks. Has the scope broken?")
    found = [(rel, longest_repeated_block(lines)[0]) for rel, lines in _DOCS]
    detected = [rel for rel, n in found if n >= 4]
    assert detected, (
        "the duplication detector reports that no document in the repository "
        "repeats even four consecutive lines of prose, which was not true of "
        "any measured state of this tree. The scanner is broken, not the "
        "documents.")

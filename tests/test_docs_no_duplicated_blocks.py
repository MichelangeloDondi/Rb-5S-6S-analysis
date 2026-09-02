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
last of which is entirely table rows. RE-MEASURED 2026-09-01 when the
threshold fell to nine: the largest legitimate within-file repeat is eight
prose lines (PREREGISTRATION_RESULTS, its addendum quoting the data it
amends), so nine clears the live population by one line — a deliberate
one-line margin, measured again rather than inherited.

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
MAX_REPEATED_PROSE_LINES = 9


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

# ---------------------------------------------------------------------------
# The cross-file pass (prose-ratchet v2, 2026-09-01). The within-file test
# above cannot see the hub carrying a chapter's forty-five lines verbatim,
# which is exactly what docs/BIG_PICTURE.md did against big_picture/07 until
# the day this landed: two copies of one analysis, one link-path apart, so a
# correction to either would have missed the other. Nine-line prose shingles
# (the within-file threshold) are hashed per document and collisions across
# DIFFERENT documents are reported with both locations. The hub now carries
# a short non-verbatim summary with one pointer instead, so the pass starts green.

SHINGLE = MAX_REPEATED_PROSE_LINES


def _prose_shingles(lines):
    """Yield (start_line_1based, tuple_of_stripped_prose_lines) windows."""
    mask = _prose_mask(lines)
    prose = [(i + 1, lines[i].strip()) for i in range(len(lines)) if mask[i]]
    for k in range(len(prose) - SHINGLE + 1):
        window = prose[k:k + SHINGLE]
        yield window[0][0], tuple(t for _, t in window)


def test_no_document_repeats_a_block_of_another(capsys):
    """A block living in two documents doubles every future correction.

    docs/lit/ is outside this pass for the same reason it is outside the
    prose banks: bibliographic stubs share templated frontmatter and dated
    demotion flags by design (the first live run found exactly that —
    roy2017 and ray2020, two placeholder records demoted the same day),
    and that is not the hub-carrying-a-chapter class this exists to stop.
    """
    seen = {}
    hits = []
    for rel, lines in _DOCS:
        if rel.startswith("docs/lit/"):
            continue
        for start, window in _prose_shingles(lines):
            key = hash(window)
            if key in seen and seen[key][0] != rel:
                other_rel, other_start = seen[key]
                hits.append(f"{rel}:{start} repeats {other_rel}:{other_start}")
                break  # one report per file pair is enough to act on
            seen.setdefault(key, (rel, start))
    # the guard reports its own margin the way the budget reports its
    # totals (through capsys.disabled, which survives the gate's -rfE):
    # a margin one line under the threshold was found only when a
    # reader went looking, and a printed number is read at every run
    margin_k = 0
    for k in range(SHINGLE - 1, 0, -1):
        seen_k: dict[int, str] = {}
        found = False
        for rel, lines in _DOCS:
            if rel.startswith("docs/lit/"):
                continue
            mask = _prose_mask(lines)
            prose = [lines[i].strip() for i in range(len(lines)) if mask[i]]
            for j in range(len(prose) - k + 1):
                key = hash(tuple(prose[j:j + k]))
                if key in seen_k and seen_k[key] != rel:
                    found = True
                    break
                seen_k.setdefault(key, rel)
            if found:
                break
        if found:
            margin_k = k
            break
    with capsys.disabled():
        print(f"\n  cross-file margin: longest repeat {margin_k} lines "
              f"against a threshold of {SHINGLE}")
    assert not hits, (
        f"a {SHINGLE}-line prose block appears verbatim in two documents. "
        "Keep the copy where the analysis lives and replace the other with "
        "a pointer to it:\n  " + "\n  ".join(sorted(set(hits))))


# --------------------------------------------------------------------
# THE SHORT ADJACENT REPEAT, which the long-block ratchet cannot see
# --------------------------------------------------------------------
# MAX_REPEATED_PROSE_LINES is 9 because that is where legitimate long
# repeats live. It is the right threshold for the class it was written
# for and the wrong one for the class that actually bit: on 2026-09-02 a
# patch script re-run from the top appended two lines twice, and the
# duplicate sat IMMEDIATELY after its original inside one blockquote,
# nine lines under the ratchet's reach (escape E14).
#
# An immediately adjacent repeat is a different animal from a long one.
# Prose repeats a paragraph at distance for emphasis or structure; it
# does not repeat two lines back to back. So this check needs no
# threshold negotiation: any block of two or more non-trivial lines
# followed instantly by its own copy is a copy-paste artefact.


def _adjacent_repeat(lines, min_len=2):
    """The first (start, length) whose block is immediately followed by
    an identical block, or None. Blank and structural lines do not
    count toward a block, so a table of repeated separators is not a
    finding."""
    body = [(i, ln.rstrip()) for i, ln in enumerate(lines)
            if ln.strip() and not set(ln.strip()) <= set("|-> #*_=")]
    text = [b for _, b in body]
    for n in range(len(text) // 2, min_len - 1, -1):
        for i in range(len(text) - 2 * n + 1):
            if text[i:i + n] == text[i + n:i + 2 * n]:
                return body[i][0] + 1, n
    return None


@pytest.mark.parametrize("rel,lines", _DOCS, ids=[r for r, _ in _DOCS])
def test_no_document_repeats_a_block_immediately_after_itself(rel, lines):
    """The E14 class: a copy-paste append that lands its duplicate
    directly beneath the original. No threshold, because prose does not
    do this on purpose."""
    hit = _adjacent_repeat(lines)
    assert hit is None, (
        f"docs/{rel} line {hit[0]}: {hit[1]} lines are repeated "
        "immediately after themselves. That is the copy-paste shape "
        "escape E14 recorded, which the long-block ratchet is nine "
        "lines too coarse to see. Delete the duplicate.")


def test_the_adjacent_detector_fires_on_the_real_incident():
    """Planted with the actual E14 content rather than an invented
    string, so the guard is known to catch the thing it was written
    for."""
    real = [
        "> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)",
        "> explains the measurement in six sentences, then defines every term",
        "> and symbol used anywhere in this repository.",
        "> explains the measurement in six sentences, then defines every term",
        "> and symbol used anywhere in this repository.",
    ]
    hit = _adjacent_repeat(real)
    assert hit is not None and hit[1] == 2, (
        "the detector cannot see the duplication it exists for")
    fixed = real[:3]
    assert _adjacent_repeat(fixed) is None, (
        "the detector fires on the corrected form, which would make it "
        "unusable")

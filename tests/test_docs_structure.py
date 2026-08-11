"""Long documents must open with the things that make them enterable.

WHY THIS EXISTS. The repository runs to a few hundred thousand words and its
hardest problem for a new reader is not that anything is wrong, it is that
several documents open with ten thousand words and no way to tell whether they
are the right document. The methods chapters solved this long ago with a
four-line header saying what the chapter asks, what it assumes, what it gives
and when to skip it. None of the six largest top-level documents had adopted
it, and none pointed at a glossary, because there was no glossary.

Both are now rules in `docs/STYLE.md` under "Document structure", and this is
what keeps them true as documents grow past the threshold. It is a check on
SHAPE and never on wording, so it cannot be satisfied by a formula: a header
whose "Skip if" line says nothing useful passes here and fails a reader, which
is a judgement no test should be asked to make.

Scope. Every tracked `.md` under docs/ above the word threshold, minus the
exemptions below, each of which is exempt for a stated structural reason rather
than because it is inconvenient.
"""
from __future__ import annotations

import re

import pytest

from rb5s6s import config as C

WORD_THRESHOLD = 2500

# Exempt, each for a reason that is about the document's kind, not its length.
_EXEMPT = {
    # generated: the header would have to live in the generator, and the ledger
    # is reached from RESULTS-shaped links rather than read front to back
    "RESULTS.md",
    # an index rather than a document: it is all pointers already
    "LITERATURE_INDEX.md",
    "methods.md",
    # the glossary IS the vocabulary door, so pointing it at itself is circular
    "GLOSSARY.md",
    # append-only records whose entry point is their own summary table, added
    # before this rule existed and serving the same purpose
    "PREREGISTRATION_RESULTS.md",
}

_HEADER_LINES = ("**The question.**", "**Takes.**", "**Gives.**", "**Skip if.**")


def _docs():
    for path in sorted(C.REPO_ROOT.glob("docs/**/*.md")):
        rel = path.relative_to(C.REPO_ROOT / "docs").as_posix()
        if rel.split("/")[-1] in _EXEMPT:
            continue
        if rel.startswith("lit/"):        # one note per paper, short by design
            continue
        text = path.read_text(encoding="utf-8")
        if len(text.split()) < WORD_THRESHOLD:
            continue
        yield rel, text


def _ids():
    return [rel for rel, _ in _docs()]


@pytest.mark.parametrize("rel,text", list(_docs()), ids=_ids())
def test_a_long_document_opens_with_the_reader_header(rel, text):
    """The four lines that let a reader decide whether this is their document."""
    head = "\n".join(text.splitlines()[:60])
    missing = [ln for ln in _HEADER_LINES if ln not in head]
    assert not missing, (
        f"docs/{rel} runs past {WORD_THRESHOLD} words without the reader "
        f"header in its first 60 lines. Missing: {missing}. See docs/STYLE.md, "
        f"'Document structure', and any methods chapter for the pattern.")


@pytest.mark.parametrize("rel,text", list(_docs()), ids=_ids())
def test_a_long_document_points_at_the_glossary(rel, text):
    """A reader arriving from a search result has no front door otherwise."""
    head = "\n".join(text.splitlines()[:60])
    assert re.search(r"GLOSSARY\.md", head), (
        f"docs/{rel} runs past {WORD_THRESHOLD} words without pointing at "
        f"GLOSSARY.md in its first 60 lines. One blockquote, near the top. See "
        f"docs/STYLE.md, 'Document structure'.")


def test_the_threshold_actually_selects_documents():
    """A guard that silently matches nothing is worse than no guard.

    If a refactor renames docs/ or the exemption list swallows everything, the
    two checks above would pass vacuously. This is the check on the check.
    """
    selected = _ids()
    assert len(selected) >= 5, (
        f"the structure guard is only looking at {selected}, which is too few "
        f"to be doing its job. Has docs/ moved, or has _EXEMPT grown?")

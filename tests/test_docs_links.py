"""
Reference-resolution gate: every internal link, image, anchor, and run-command in
the docs must point at something that exists.

A repo whose README carries its own GitHub URL and whose eight methods chapters
cross-link each other is one file-rename away from a dead link — invisible until
someone (a reviewer, a collaborator) clicks it. This gate makes that mechanical:

  (a) markdown links / image embeds `](path)` resolve to a real file;
  (b) an `#anchor` on such a link (or a same-file `#anchor`) matches a real
      heading in the target — the failure mode the methods.md -> methods/ split
      could have introduced;
  (c) `python scripts/x.py` commands in the README's ```bash blocks name real
      files (tracking `cd`, since cwd changes within a block).

External URLs (http/https/mailto) are not checked — that needs the network and
is not this gate's job. The fourth ported EIT sister-repo gate, after CANONICAL
(numbers), figure-fingerprint (figures), and math-render (equations).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
# Dot-directories excluded so a nested checkout -- a full second copy of the
# repo -- is not parametrised in alongside the real docs. See the note in
# test_docs_math_render.py.
# `private/` is gitignored and never published, so CI (which clones from git)
# never sees it. Scanning it locally made the suite disagree with CI: a draft
# moved there kept its docs-relative links and failed a check that only ever
# applied to published files. Excluded 2026-07-31 so local matches CI.
# git-aware rather than a hand-maintained skip list. The comment above records
# one prior incident of private/ being scanned locally and disagreeing with CI;
# asking git removes that class entirely (rule 19.24, tests/_fileset.py).
from _fileset import tracked_and_new as _tan            # noqa: E402
DOCS = sorted(ROOT / p for p in _tan("*.md")
              if not p.startswith("PDF_papers/"))


def _slug(heading: str) -> str:
    """GitHub's heading -> anchor slug: lowercase, punctuation stripped
    (em-dashes included), then EVERY space becomes a hyphen -- runs are NOT
    collapsed, so "A — B" yields "a--b". Verified against GitHub's rendered
    file HTML 2026-07-24."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return s.replace(" ", "-")


def _anchor_set(text: str) -> set:
    """All anchors a doc offers, with GitHub's duplicate numbering: the second
    identical heading gets -1, the third -2, ..."""
    out, seen = set(), {}
    for h in re.findall(r"^#{1,6}\s+(.*)$", text, re.M):
        base = _slug(h)
        k = seen.get(base, 0)
        seen[base] = k + 1
        out.add(base if k == 0 else f"{base}-{k}")
    return out


# anchors offered by each doc, keyed by path relative to ROOT
_ANCHORS = {
    str(p.relative_to(ROOT)): _anchor_set(p.read_text(encoding="utf-8"))
    for p in DOCS
}


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_doc_references_resolve(doc):
    rel = doc.relative_to(ROOT)
    text = doc.read_text(encoding="utf-8")
    base = doc.parent
    problems = []

    # (a)+(b) links / images, with optional #anchor
    for tgt in re.findall(r"\]\(([^)]+)\)", text):
        t = tgt.strip()
        if t.startswith(("http://", "https://", "mailto:")):
            continue
        path, _, anchor = t.partition("#")
        if path:
            fp = (base / path).resolve()
            if not fp.exists():
                problems.append(f"link -> {tgt} (missing file)")
                continue
            key = str(fp.relative_to(ROOT)) if ROOT in fp.parents else None
        else:
            key = str(rel)                      # same-file anchor
        if anchor and key in _ANCHORS and anchor not in _ANCHORS[key]:
            problems.append(f"link -> {tgt} (no heading '#{anchor}' in {key})")

    # (c) run-commands in bash blocks (cwd follows cd)
    for block in re.findall(r"```bash\n(.*?)```", text, re.S):
        cwd = ROOT
        for line in block.splitlines():
            m = re.match(r"\s*cd\s+(\S+)", line)
            if m:
                cwd = (cwd / m.group(1)).resolve()
                continue
            for script in re.findall(r"python3?\s+([\w./-]+\.py)", line):
                if not (cwd / script).exists():
                    problems.append(f"command -> {script} (not found from cwd)")

    assert not problems, f"{rel}: unresolved references:\n  " + "\n  ".join(problems)


# ---------------------------------------------------------------------------
# Bare section pointers.
#
# The gate above resolves `](path)` links and `#anchor` fragments. It says
# nothing about `PLAN §7` or `DATA §5`, which are how the three long planning
# documents are cited throughout, and which no machinery checked at all: a
# methods chapter cited PLAN §7 for the wavemeter shots, which live in §11,
# and nothing noticed. These three files are the ones cited this way often
# enough to drift.

_POINTER_TARGETS = {
    "PLAN": "docs/PLAN.md",
    "DATA": "docs/DATA.md",
    "THEORY_NOTE": "docs/THEORY_NOTE.md",
}
_SECTION_NUMBER = r"[0-9]+(?:\.[0-9]+)*[a-z]?"
_HEADING = re.compile(rf"^(#{{1,6}})\s+({_SECTION_NUMBER})[.)\s]", re.M)


def _sections_offered(text: str) -> set:
    """Every section label a document can be cited by.

    Three shapes are in use. Numbered headings (`## 7. The width and collision
    program`). Bold run-in sub-items, which PLAN §7 uses instead of headings
    (`**7d. The matched-PM ruler ...**`). And plain numbered list items inside
    a section, which DATA §3 uses and which are cited as `§3.4`.
    """
    out = {m.group(2) for m in _HEADING.finditer(text)}
    out |= set(re.findall(rf"^\*\*({_SECTION_NUMBER})[.)]", text, re.M))
    marks = [(m.start(), m.group(2)) for m in _HEADING.finditer(text)]
    for i, (pos, num) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        for item in re.findall(r"^ {0,3}(\d+)\.\s", text[pos:end], re.M):
            out.add(f"{num}.{item}")
    return out


_OFFERED = {
    name: _sections_offered((ROOT / rel).read_text(encoding="utf-8"))
    for name, rel in _POINTER_TARGETS.items()
}
_POINTER = re.compile(
    rf"\b(PLAN|DATA|THEORY_NOTE)(?:\.md)?`?\s*§\s*({_SECTION_NUMBER})")

# Only the documents that carry a pointer are parametrised. Running this over
# the other ninety would add ninety cases that check nothing.
_CITING = [p for p in DOCS if _POINTER.search(p.read_text(encoding="utf-8"))]


@pytest.mark.parametrize("doc", _CITING, ids=lambda p: str(p.relative_to(ROOT)))
def test_bare_section_pointers_resolve(doc):
    text = doc.read_text(encoding="utf-8")
    dead = []
    for name, num in _POINTER.findall(text):
        if num not in _OFFERED[name]:
            dead.append(f"{name} §{num} (no such section in "
                        f"{_POINTER_TARGETS[name]})")
    assert not dead, (f"{doc.relative_to(ROOT)}: section pointers that resolve "
                      "to nothing:\n  " + "\n  ".join(sorted(set(dead))))

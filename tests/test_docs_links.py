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
DOCS = sorted(p for p in ROOT.rglob("*.md")
              if ".venv" not in p.parts and "PDF_papers" not in p.parts
              and "node_modules" not in p.parts)


def _slug(heading: str) -> str:
    """Approximate GitHub's heading -> anchor slug (lowercase, punctuation
    stripped, spaces to hyphens). Good enough for the plain ASCII headings here."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


# anchors offered by each doc, keyed by path relative to ROOT
_ANCHORS = {
    str(p.relative_to(ROOT)): {_slug(h) for h in
                               re.findall(r"^#{1,6}\s+(.*)$", p.read_text(encoding="utf-8"), re.M)}
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

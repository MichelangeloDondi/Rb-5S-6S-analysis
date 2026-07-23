r"""
Math-render gate: every `$…$` / `$$…$$` span must survive GitHub's markdown-to-
MathJax pipeline.

The failure this catches is invisible in a local editor and only appears once
GitHub renders the page: GitHub's markdown eats a backslash before ANY ASCII
*punctuation* character INSIDE a math span (CommonMark backslash-escaping runs
before MathJax sees the content). Confirmed on the live repo — the headline
boxed beta bound rendered as a red "Extra open brace or missing close brace"
box, because `\%` became a bare `%`, which MathJax treats as a comment that ate
the rest of the equation including `\boxed`'s closing brace.

The rule is general, not a list of the cases seen so far. A backslash before a
LETTER (`\alpha`, `\otimes`, `\quad`) is a normal command and is safe; a
backslash before an ASCII punctuation character is eaten. The usual offenders
and their fixes:
    \%            percent   -> move the % OUTSIDE the math ($…$ then %); MathJax
                              also treats a bare % as a comment, so it must not
                              appear in math at all.
    \, \; \: \!   spacing   -> drop them (LaTeX already spaces around relations)
    \{  \}        braces    -> \lbrace \rbrace
    \\            row break -> \cr
    \|            norm      -> \Vert
Also flagged: a non-ASCII glyph inside \text{}/\mathrm{} (an em/en dash, a real
µ), which GitHub's renderer does not reliably resolve — write it outside the
text group or as ASCII.

`\ ` (backslash-space) is NOT flagged: space is not punctuation, so the
backslash survives and MathJax reads it as an explicit space — which is why the
`225\ \text{mW}` spacing used throughout renders fine.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# every tracked-ish .md except vendored PDFs and the venv
DOCS = [p for p in ROOT.rglob("*.md")
        if ".venv" not in p.parts and "PDF_papers" not in p.parts
        and "node_modules" not in p.parts]

_PUNCT = re.compile(r"\\([!-/:-@\[-`{-~])")          # backslash + ASCII punctuation
_TEXTGRP = re.compile(r"\\(?:text|mathrm|mathbf|textrm)\{([^{}]*)\}")
_FIX = {"%": "move % outside the math span (bare % is a MathJax comment)",
        ",": "drop it", ";": "drop it", ":": "drop it", "!": "drop it",
        "{": "\\lbrace", "}": "\\rbrace", "\\": "\\cr", "|": "\\Vert"}


def _math_spans(text: str):
    text = re.sub(r"```.*?```", "", text, flags=re.S)     # fenced code is not math
    spans = [(m.group(1), text[:m.start()].count("\n") + 1)
             for m in re.finditer(r"\$\$(.+?)\$\$", text, re.S)]
    rest = re.sub(r"\$\$.+?\$\$", "", text, flags=re.S)   # then inline, on the remainder
    spans += [(m.group(1), rest[:m.start()].count("\n") + 1)
              for m in re.finditer(r"\$([^$\n]+)\$", rest)]
    return text, spans


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_math_renders_on_github(doc):
    rel = doc.relative_to(ROOT)
    raw = doc.read_text(encoding="utf-8")
    stripped, spans = _math_spans(raw)
    problems = []

    # (a) unbalanced $$ -> a display block never closes
    if stripped.count("$$") % 2:
        problems.append(f"{rel}: odd number of $$ ({stripped.count('$$')}) — a display block never closes")

    for span, ln in spans:
        # (b) backslash before ASCII punctuation — markdown eats the backslash
        for m in _PUNCT.finditer(span):
            ch = m.group(1)
            problems.append(f"{rel}:~{ln}: '\\{ch}' in math — markdown eats the backslash; "
                            f"{_FIX.get(ch, 'use a letter-based command')}")
        # (c) non-ASCII glyph inside a text group
        for g in _TEXTGRP.findall(span):
            bad = "".join(c for c in g if ord(c) > 127)
            if bad:
                problems.append(f"{rel}:~{ln}: non-ASCII {bad!r} inside \\text{{}} — may not render on GitHub")

    # (d) a bare | inside math on a markdown table row — eaten as a column separator
    for n, line in enumerate(raw.split("\n"), 1):
        if line.lstrip().startswith("|") and any("|" in m for m in re.findall(r"\$([^$\n]+)\$", line)):
            problems.append(f"{rel}:{n}: bare | inside math on a table row — markdown eats it as a column separator")

    assert not problems, "GitHub math-render problems:\n  " + "\n  ".join(problems)


# --------------------------------------------------------------------------
# A `$…$` span must not straddle a newline.
# --------------------------------------------------------------------------
# GitHub's inline math is single-line: a span opened on one source line and
# closed on the next is emitted as LITERAL LaTeX on the rendered page. This is
# invisible locally (editors and most previewers join the lines) and was
# reported from the live page 2026-07-23 as "raw latex" in THEORY_NOTE.md and
# PAPER1_SKELETON.md. Seven spans were wrapped across the repo. The check is a
# per-line dollar-parity test, which is exactly the condition.
def test_no_inline_math_span_wraps_a_line():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    bad = []
    for rel in [p for p in out.stdout.split("\n") if p]:
        if rel.startswith("docs/lit/"):
            continue
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        in_fence = False
        for i, line in enumerate(text.split("\n"), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            # display math ($$) opens and closes on its own lines by design
            if line.strip().startswith("$$") or line.strip().endswith("$$"):
                continue
            if line.count("$") % 2 == 1:
                bad.append(f"{rel}:{i}: {line.strip()[:95]}")
    assert not bad, (
        "inline math span left open at end of line — GitHub renders these as "
        "literal LaTeX because $…$ does not cross a newline; join the lines:\n  "
        + "\n  ".join(bad[:15]))

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

Two further failure modes, both measured against GitHub's own renderer rather
than assumed. The public `POST /markdown` endpoint returns the HTML that goes
to the page before MathJax runs, so what the math pass is handed can be read
off directly.

ADJACENCY. GitHub opens an inline span only where the `$` follows a line start,
whitespace, `(` or `*`, and closes it only where the `$` is followed by
something other than a letter or a digit. Where either side fails, the whole
span is emitted as raw source: `$^{171}$Yb` stays literally that on the page,
which is how a lit note can carry two dozen isotope labels and still look right
in a local editor. Read off the renderer case by case: `2$\Delta$`,
`a-$\kappa$`, `en–$\mu$`, `m$d$`, `]$b$`, `/$c$`, `"$a$"` and `$p$4` all came
back raw, while a line start, a space, `($y$)` and `**$z$**` all rendered. The
`*` allowance is deliberately loose. `**$z$**` renders but `*$b$*` does not, so
single-asterisk emphasis wrapped tight around math is one break this check lets
through.

ANGLE BRACKETS. The markdown pass turns `<` and `>` into HTML entities before
MathJax sees the span, and on the inline path it escapes twice, so `$a < b$`
reaches MathJax as the entity text rather than as `<`. Write `\lt` and `\gt`.
A `$$…$$` block standing as its own paragraph escapes only once and does
survive today. The check covers it anyway, because a `$$` line takes the inline
path the moment the blank line above it goes away, and the repository already
had one `$$` span sitting inside a paragraph for exactly that reason.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Every tracked-ish .md except vendored PDFs, the venv, and anything under a
# dot-directory. The dot-directory rule is load-bearing: a nested checkout (a
# stray `git worktree`, a tool cache) is a COMPLETE second copy of the repo, so
# without it this module silently ran twice -- once on the real docs and once on
# a stale snapshot -- and inflated the suite by ~170 cases. Found 2026-07-29,
# when the advertised count fell by that much after one such copy was removed.
# `private/` excluded for the same reason as in test_docs_links.py: it is
# gitignored, so CI never sees it and local runs should not either.
# git-aware, so every ignored path is excluded without a list to maintain
# (rule 19.24, tests/_fileset.py). PDF_papers stays excluded on its own merits:
# it is tracked but is a vendored reprint area, not repository prose.
from _fileset import tracked_and_new as _tan            # noqa: E402
DOCS = [ROOT / p for p in _tan("*.md") if not p.startswith("PDF_papers/")]

_PUNCT = re.compile(r"\\([!-/:-@\[-`{-~])")          # backslash + ASCII punctuation
_TEXTGRP = re.compile(r"\\(?:text|mathrm|mathbf|textrm)\{([^{}]*)\}")
_FIX = {"%": "move % outside the math span (bare % is a MathJax comment)",
        ",": "drop it", ";": "drop it", ":": "drop it", "!": "drop it",
        "{": "\\lbrace", "}": "\\rbrace", "\\": "\\cr", "|": "\\Vert"}
_ANGLE = re.compile(r"[<>]")
_ALNUM = re.compile(r"[A-Za-z0-9]")
_OPEN_OK = "(*"                                      # besides a line start and whitespace


def _blank(m: re.Match) -> str:
    """Spaces in place of the match, newlines kept, so line numbers stay exact."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _spans_in_context(text: str):
    """Every span GitHub will hand to MathJax, with the characters around it.

    Fenced code AND inline `code` are blanked out. A `$…$` written between
    backticks documents the syntax instead of being an equation, which is how
    STYLE.md and this module's own docstring write it, and it never reaches the
    math pass.

    Yields (body, line, char before, char after, quoted fragment). A display
    span reports newlines for the two characters, because `$$` sits on its own
    line by design and the adjacency rule does not apply to it.
    """
    text = re.sub(r"```.*?```", _blank, text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", _blank, text)
    out = [(m.group(1), text[:m.start()].count("\n") + 1, "\n", "\n",
            m.group(0)[:70])
           for m in re.finditer(r"\$\$(.+?)\$\$", text, re.S)]
    rest = re.sub(r"\$\$.+?\$\$", _blank, text, flags=re.S)
    for m in re.finditer(r"\$([^$\n]+)\$", rest):
        out.append((m.group(1), rest[:m.start()].count("\n") + 1,
                    rest[m.start() - 1] if m.start() else "\n",
                    rest[m.end()] if m.end() < len(rest) else "\n",
                    rest[max(0, m.start() - 12):m.end() + 12].strip()))
    return out


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

    lines = raw.split("\n")
    for body, ln, before, after, frag in _spans_in_context(raw):
        # A quotation is reproduced as the source wrote it. Where a quoted
        # symbol cannot render on this platform, the platform loses: altering
        # the characters inside quotation marks to satisfy a rendering rule
        # would make the quote no longer a quote. The exemption is the span
        # whose opening $ sits against the quotation mark on a marked verbatim
        # line, and nothing else on that line: an early version skipped the
        # whole line, and a planted `cm$^{-3}$` beside a quotation went
        # unreported.
        if (before in "“\"" and 0 < ln <= len(lines)
                and "Verbatim:" in lines[ln - 1]):
            continue
        # (e) adjacency: GitHub opens an inline span only after a line start,
        #     whitespace, `(` or `*`, and closes it only before a non-alphanumeric
        if not (before.isspace() or before in _OPEN_OK):
            problems.append(f"{rel}:{ln}: {frag!r}: {before!r} sits before the opening $, "
                            "so GitHub leaves the whole span as raw source on the page "
                            "(measured against its renderer, not assumed). Put a space, "
                            "a `(` or a `**` in front of it, or move the character inside the math.")
        if _ALNUM.match(after):
            problems.append(f"{rel}:{ln}: {frag!r}: {after!r} follows the closing $, "
                            "so GitHub leaves the whole span as raw source on the page "
                            "(measured against its renderer, not assumed). Pull the character "
                            "into the math, as in $^{171}\\text{Yb}$.")
        # (f) < or > anywhere in math: entity-escaped before MathJax sees it
        if _ANGLE.search(body):
            problems.append(f"{rel}:{ln}: {frag!r}: < or > inside math. Markdown escapes it to an "
                            "HTML entity before the math pass, so MathJax is handed the entity "
                            "text rather than the sign. Use \\lt and \\gt.")

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
    from _fileset import tracked_and_new
    class _O:
        pass
    out = _O()
    out.stdout = "\n".join(tracked_and_new("*.md"))
    if not out.stdout:
        pytest.skip("not a git checkout")
    # The blanket docs/lit/ exemption is gone. It carried no reason, and it hid
    # eight wrapped spans in seven lit notes, which was every wrapped span the
    # repository had. Exactly one line under docs/lit/ is odd-parity without
    # being a math span at all: biraben1974.md's provenance note, where a lone
    # `$` sits inside an HTML comment quoting the scan's garbled OCR ("3S-5S"
    # reads as "3$-5S"). An HTML comment reaches no renderer, so the narrow
    # replacement is to skip comments in every file rather than one directory.
    bad = []
    for rel in [p for p in out.stdout.split("\n") if p]:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        in_fence = in_comment = False
        for i, line in enumerate(text.split("\n"), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if in_comment:
                in_comment = "-->" not in line
                continue
            if "<!--" in line and "-->" not in line:
                in_comment = True
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


def test_table_rows_are_single_lines():
    """Every row of a GFM table is one physical line with the header's pipes.

    WHY. A qualifier added to docs/methods.md's chapter table wrapped row 3
    across two lines (2026-08-31): GFM parses per line, so the cell truncated
    mid-clause and the continuation rendered as a spurious one-cell row on
    the methods hub. Independent passes found it repeatedly and measured
    that both existing table-adjacent guards select lines by startswith('|'),
    leaving a wrapped continuation outside every population. Verified by
    re-wrapping that row and watching this test fire.

    THE RULE. Inside a table block (from a |---| delimiter line until the
    first blank line), every non-blank line either starts with '|' or is an
    HTML comment, and a wrapped cell shows its exact signature: a line that
    does not start with a pipe but ends with one, directly under a row. Two
    wider rules were tried in this same edit and withdrawn against the tree:
    pipe-count equality false-fires on GFM's optional trailing pipes and on
    pipes inside code spans, and until-blank-line block scanning false-fires
    on the prose that legally ends a table without a blank line. The
    signature rule fires on the one true positive and on nothing else.
    """
    import re
    bad = []
    for doc in DOCS:
        lines = (ROOT / doc).read_text(encoding="utf-8").splitlines()
        in_fence = False
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
            if not in_fence and re.match(r"^\|[\s:|-]+\|$", line.strip()) \
                    and "-" in line:
                j = i + 1
                while j < len(lines) and lines[j].strip():
                    row = lines[j].lstrip()
                    if not (row.startswith("|") or row.startswith("<!--")):
                        if row.rstrip().endswith("|"):
                            bad.append(f"{doc}:{j+1}: wrapped table cell "
                                       f"(no leading pipe, trailing pipe): "
                                       f"{row[:60]!r}")
                        break              # a non-row line ends the table
                    j += 1
                i = j
            else:
                i += 1
    assert not bad, ("broken table rows (a table row must be one physical "
                     "line):\n  " + "\n  ".join(bad[:12]))


def test_symmetric_kernel_claims_carry_their_centring():
    """No tracked page claims symmetric kernels add nothing to the asymmetry
    without the self-centred qualifier in the same paragraph.

    WHY. The claim's unqualified form was retracted, re-qualified, and then
    found surviving on the canonical concept page itself, twelve lines below
    its own correction (2026-08-31). The qualifier is
    physics, not style: the cancellation holds only for a window symmetric
    about the line's own centre, and only up to the truncation fraction
    results/cumulant_window_check.csv measures. Verified by restoring the
    wiki's old unqualified sentence and watching this test fire.
    """
    import re
    pat = re.compile(r"contribut\w*\s+(?:nothing|zero)[^.]{0,80}"
                     r"(?:\\kappa_3|κ₃|third cumulant|asymmetry|odd)",
                     re.I)
    bad = []
    for doc in DOCS:
        text = (ROOT / doc).read_text(encoding="utf-8")
        for para in text.split("\n\n"):
            if pat.search(para) and "self-centred" not in para \
                    and "self-centering" not in para:
                bad.append(f"{doc}: {para.strip()[:90]!r}")
    assert not bad, ("symmetric-kernel cancellation stated without its "
                     "self-centred qualifier in the paragraph:\n  "
                     + "\n  ".join(bad[:8]))

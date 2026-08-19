"""Where a note ASSERTS a quotation is verbatim, check it against the source PDF.

Why this exists (2026-07-30). A claim-by-claim audit of the literature notes
against their source PDFs found, among the confirmed defects, the one class that
is unambiguously mechanical: a quotation with a word substituted inside the
quotation marks. `patterson2018` rendered

    "the spectrum is given only by the local potential felt by the atoms"

as "... the local frequency SHIFT felt by the atoms" — and the substituted
phrase was then used as the paper's endorsement of this repository's own
modelling assumption. The phrase "frequency shift" appears nowhere in that
paper. A human re-reading the note cannot catch that, because the note is
internally consistent with the misquote. Only the source catches it, and a
machine can do that every run instead of once a session.

**Scope is opt-in, and that was a deliberate reversal.** The first version of
this guard checked *every* quoted span in every held note. It flagged 12 of 15
notes, and essentially all of it was noise: these notes quote the repository's
own voice constantly — "keep the distribution, close it in form", "we measure a
lineshape in an ONF too" — and correction lines quote the wrong text on purpose
in order to retract it. A guard with an exemption list longer than its findings
is worse than no guard, because it trains the eye to skip failures.

So the rule is inverted. A quotation is checked when the note **claims** it is
verbatim — when the enclosing paragraph says so, which is already the house
convention ("**Abstract, verbatim.**", "Verbatim:", "**The numbers, verbatim.**").
That is exactly the population where a substitution does damage: a passage
presented to the reader as the source's own words.

Caveats kept honest:

- Skipped when `PDF_papers/` is absent, which is CI's situation — that tree is
  gitignored and never published.
- Spans containing an ellipsis are skipped: an elided quotation cannot match
  literally, and stitching around "..." would invite false passes.
- PDF text extraction mangles ligatures, dashes and the degree sign; `_norm`
  handles those. The residual cost is that this catches *word substitution*,
  not punctuation drift — the right trade, since one changes meaning and the
  other does not.

To exempt a genuinely-verbatim quotation that is not from the held file (the
published version where we hold a preprint, a quoted email, a secondary source),
put an inline marker in the paragraph and say where it came from:

    "...phrase..." <!-- not-from-pdf: quoted from the published version -->
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIT_DIR = ROOT / "docs" / "lit"
PDF_DIR = ROOT / "PDF_papers"

MIN_WORDS = 6

_PDFS_PRESENT = any(PDF_DIR.glob("*.pdf"))

pytestmark = pytest.mark.skipif(
    not _PDFS_PRESENT,
    reason="PDF_papers/ is gitignored and absent (CI); nothing to check against",
)

_QUOTE_RE = re.compile(r'[“"]([^“”"\n]{20,})[”"]')
_EXEMPT_RE = re.compile(r"<!--\s*not-from-pdf:")
_VERBATIM_RE = re.compile(r"\bverbatim\b", re.I)
_ELLIPSIS_RE = re.compile(r"\.\.\.|…")

# Everything text extraction and ASCII transliteration disagree about. The
# notes are written in ASCII ("beta/2pi", "+-", "x 10^-7"); the PDFs carry the
# typeset originals. Both sides are mapped onto the same tokens before matching.
_SUBS = {
    # ligatures
    "ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl",
    # Greek, to the spellings the notes use
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon",
    "κ": "kappa", "λ": "lambda", "μ": "u", "µ": "u", "ν": "nu", "π": "pi",
    "ρ": "rho", "σ": "sigma", "τ": "tau", "χ": "chi", "ω": "omega",
    "Γ": "gamma", "Δ": "delta", "Ω": "omega", "Σ": "sigma", "Φ": "phi",
    # operators and marks the notes transliterate
    "±": "+-", "×": "x", "·": " ", "→": "->", "≈": "~", "≤": "<=", "≥": ">=",
    "−": "-", "–": "-", "—": "-", "’": "'", "‘": "'", "°": "",
    # superscript digits, which extraction emits raw and notes write as ^n
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-",
    # subscript digits likewise
    "₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4", "₅": "5",
    "₆": "6", "₇": "7", "₈": "8", "₉": "9",
}
# "/C176" and friends: how pdf text layers encode glyphs with no ASCII form.
_ARTEFACT_RE = re.compile(r"/c\d{2,3}", re.I)
# Bracketed reference markers -- "[14]", "[4, 17, 34]". Dropping these from the
# middle of a quotation is universal editorial practice and carries no meaning,
# so they are stripped from BOTH sides rather than treated as a mismatch.
# (arora2012 quotes "...45.57(17) ns with branching ratios..." where the paper
# has "...45.57(17) ns [14] with branching ratios...".)
_REFMARK_RE = re.compile(r"\[\s*\d+(?:\s*[,\u2013-]\s*\d+)*\s*\]")


def _norm(s: str) -> str:
    """Reduce a string to bare lowercase alphanumerics, with NO spaces.

    Dropping whitespace entirely is what makes this workable, and it solves
    three problems at once that separate rules could not:

    - **PDF hyphenation.** Extraction returns "Conse- quently" for a word broken
      across a line; with spaces gone that is "consequently", which is what the
      note says.
    - **Transliteration spacing.** The note writes "beta/2pi", the PDF layer
      "β/ 2π" with a stray space; both collapse to "beta2pi".
    - **Markdown emphasis inside a quotation.** "**4.144(3)**" and "4.144(3)"
      become the same token.

    The cost is that word ORDER is still enforced but word BOUNDARIES are not,
    so in principle two different texts could collide. For the >= MIN_WORDS
    spans this guard checks, a collision is negligible; a substituted word still
    changes the string and is still caught, which is the whole point.

    Digits are KEPT: a substituted number inside a quotation is as bad as a
    substituted word.
    """
    s = _REFMARK_RE.sub(" ", s)
    for a, b in _SUBS.items():
        s = s.replace(a, b)
    s = _ARTEFACT_RE.sub("", s.lower())
    return re.sub(r"[^a-z0-9]+", "", s)


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("'\"")
    return out


def _asserted_quotes(note: Path):
    """(line, quotation) for quotes in a paragraph that claims verbatimness.

    Paragraph-scoped rather than line-scoped because these notes hard-wrap: the
    "**Abstract, verbatim.**" marker and the quotation it introduces are usually
    several lines apart, and the quotation itself spans line breaks. Each
    paragraph is rejoined into one line before matching, so wrapping does not
    matter.
    """
    text = note.read_text(encoding="utf-8")
    out = []
    line_no = 1
    for para in text.split("\n\n"):
        if _VERBATIM_RE.search(para) and not _EXEMPT_RE.search(para):
            joined = " ".join(para.split())
            for m in _QUOTE_RE.finditer(joined):
                q = m.group(1).strip()
                if len(q.split()) >= MIN_WORDS and not _ELLIPSIS_RE.search(q):
                    out.append((line_no, q))
        line_no += para.count("\n") + 2
    return out


def _held_with_asserted_quotes():
    out = []
    for p in sorted(LIT_DIR.glob("*.md")):
        fm = _frontmatter(p)
        if fm.get("held") != "true":
            continue
        pdf = fm.get("pdf")
        if not pdf or pdf in ("null", "None"):
            continue
        full = ROOT / pdf
        if full.exists() and _asserted_quotes(p):
            out.append((p.stem, p, full))
    return out


_CHECKED = _held_with_asserted_quotes()


def _pdf_text(pdf: Path) -> str:
    pypdf = pytest.importorskip(
        "pypdf", reason="pypdf not installed; the quotation guard needs it")
    try:
        reader = pypdf.PdfReader(str(pdf))
        return _norm(" ".join(page.extract_text() or "" for page in reader.pages))
    except Exception as exc:  # an unparseable PDF is not a note defect
        pytest.skip(f"could not extract text from {pdf.name}: {exc}")


@pytest.mark.slow
@pytest.mark.parametrize("key,note,pdf", _CHECKED, ids=[k for k, _, _ in _CHECKED])
def test_asserted_quotations_are_verbatim(key, note, pdf):
    haystack = _pdf_text(pdf)
    missing = []
    for lineno, q in _asserted_quotes(note):
        if _norm(q) not in haystack:
            missing.append(f"{note.relative_to(ROOT)}:~{lineno}: {q[:130]}")

    assert not missing, (
        f"{key}: passage(s) presented as VERBATIM but not found in {pdf.name}. "
        f"This is the check that would have caught 'local potential' becoming "
        f"'local frequency shift' on 2026-07-30. Fix the quotation against the "
        f"source; drop the word 'verbatim' if it is a paraphrase; or mark the "
        f"paragraph '<!-- not-from-pdf: <where it came from> -->' if it is "
        f"quoted from somewhere other than the held file:\n  " + "\n  ".join(missing))

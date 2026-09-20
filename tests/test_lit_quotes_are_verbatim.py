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

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIT_DIR = ROOT / "docs" / "lit"
PDF_DIR = ROOT / "PDF_papers"

MIN_WORDS = 6

# ONE NAMED PREDICATE FOR THIS QUESTION, IMPORTED AND NOT REDEFINED
# (2026-09-11, escape E52's fourth site). This was
# `any(PDF_DIR.glob("*.pdf"))`, non-recursive, and it gates a MODULE-WIDE
# skipif: reading False wrongly here disables the verbatim-quote guard for every
# literature note at once, where the sites already repaired only skip one
# assertion inside a module that keeps running. E52's sweep read every
# reference in the other module and stopped at that module's edge, which is
# the population failure this record keeps meeting.
from test_lit_consistency import _the_shelf_is_here  # noqa: E402

_PDFS_PRESENT = _the_shelf_is_here()

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
# LaTeX macros the notes write inside $...$ where the PDF's text layer carries the symbol, mapped onto
# the SAME tokens _SUBS maps the symbol to, so both sides meet in the middle. Measured before shipping
# (2026-09-20, F217): with NFKC this rescues 9 of 39 unmatched quotations and breaks 0 matching ones.
_MACROS = {
    r"\geq": ">=", r"\ge": ">=", r"\leq": "<=", r"\le": "<=", r"\rightarrow": "->", r"\to": "->",
    r"\ll": "<<", r"\gg": ">>", r"\simeq": "~", r"\approx": "~", r"\sim": "~", r"\pm": "+-",
    r"\times": "x", r"\cdot": " ", r"\varepsilon": "epsilon", r"\epsilon": "epsilon",
    r"\alpha": "alpha", r"\beta": "beta", r"\gamma": "gamma", r"\delta": "delta", r"\kappa": "kappa",
    r"\lambda": "lambda", r"\mu": "u", r"\nu": "nu", r"\pi": "pi", r"\rho": "rho", r"\sigma": "sigma",
    r"\tau": "tau", r"\chi": "chi", r"\omega": "omega", r"\Gamma": "gamma", r"\Delta": "delta",
    r"\Omega": "omega", r"\infty": "inf", r"\sqrt": "sqrt", r"\mathrm": "", r"\text": "",
}
_MACRO_ORDER = sorted(_MACROS, key=len, reverse=True)   # longest first: \geq before \ge
# The members baseline: digests of (note, quotation) pairs KNOWN not to match on 2026-09-20, seeded from
# the shelf census (F217). It records what is known, not how much, so it may only shrink: a new unmatched
# quotation anywhere fails at once, and a member that starts matching must leave (re-seed).
_BASELINE_PATH = Path(__file__).with_name("_quote_baseline.json")


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
    s = unicodedata.normalize("NFKC", s)          # italic maths, letter subscripts, more ligatures
    for a in _MACRO_ORDER:
        s = s.replace(a, _MACROS[a] + " ")
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

_FM_END = re.compile(r"^---\s*$", re.M)


def _all_quotes(note: Path):
    """(line, quotation) for EVERY quoted span in the note's BODY, whatever its paragraph says.

    Quotation marks around MIN_WORDS words in a literature note ARE the assertion of verbatimness
    (F215, 2026-09-20: a fabricated phrase rode through `_asserted_quotes` because its paragraph did
    not say "verbatim"). The front matter is skipped (titles live there in quotes), as are paragraphs
    carrying the `not-from-pdf` marker and spans with an ellipsis, exactly as above.
    """
    text = note.read_text(encoding="utf-8")
    ends = [m.end() for m in _FM_END.finditer(text)]
    body_start = ends[1] if len(ends) >= 2 else 0
    out, pos, line_no = [], 0, 1
    for para in text.split("\n\n"):
        start, at = line_no, pos
        line_no += para.count("\n") + 2
        pos += len(para) + 2
        if at < body_start or _EXEMPT_RE.search(para):
            continue
        joined = " ".join(para.split())
        for m in _QUOTE_RE.finditer(joined):
            q = m.group(1).strip()
            if len(q.split()) >= MIN_WORDS and not _ELLIPSIS_RE.search(q):
                out.append((start, q))
    return out


def _held_with_any_quotes():
    out = []
    for p in sorted(LIT_DIR.glob("*.md")):
        fm = _frontmatter(p)
        pdf = fm.get("pdf")
        if fm.get("held") != "true" or not pdf or pdf in ("null", "None"):
            continue
        full = ROOT / pdf
        if full.exists() and _all_quotes(p):
            out.append((p.stem, p, full))
    return out


_CHECKED_ALL = _held_with_any_quotes()


def _digest(key: str, quote: str) -> str:
    return hashlib.sha256(f"{key}\n{_norm(quote)}".encode()).hexdigest()[:16]


def _baseline() -> dict:
    if not _BASELINE_PATH.exists():
        return {"members": {}}
    return json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))


def _extract(pdf: Path):
    """Normalised text of the PDF, or None when it cannot be read (not a note defect)."""
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf))
        return _norm(" ".join(page.extract_text() or "" for page in reader.pages))
    except Exception:
        return None


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


@pytest.mark.slow
@pytest.mark.parametrize("key,note,pdf", _CHECKED_ALL, ids=[k for k, _, _ in _CHECKED_ALL])
def test_every_quotation_is_verbatim_or_a_known_debt(key, note, pdf):
    """Every quoted span, asserted or not, is in the PDF -- or is a member of the baseline.

    Two failures, kept apart because they mean opposite things: a NEW unmatched quotation (fabrication
    or paraphrase in quotation marks: fix it, or mark the paragraph not-from-pdf); and a STALE member
    (a known debt that now matches, or was removed: the baseline must shrink, re-seed it).
    """
    haystack = _pdf_text(pdf)
    known = set(_baseline()["members"].get(key, []))
    new, missing_digests = [], set()
    for lineno, q in _all_quotes(note):
        if _norm(q) not in haystack:
            d = _digest(key, q)
            missing_digests.add(d)
            if d not in known:
                new.append(f"{note.relative_to(ROOT)}:~{lineno}: {q[:130]}")
    assert not new, (
        f"{key}: quotation(s) not found in {pdf.name} and not a known debt. A phrase in quotation "
        f"marks is presented as verbatim whether or not the paragraph says so (F215: a fabricated "
        f"quote escaped that way). Fix it against the source, or mark the paragraph "
        f"'<!-- not-from-pdf: <where it came from> -->':\n  " + "\n  ".join(new))
    stale = known - missing_digests
    assert not stale, (
        f"{key}: {len(stale)} baseline member(s) no longer unmatched -- the debt was paid or the "
        f"quotation removed, so the baseline must shrink: python tests/test_lit_quotes_are_verbatim.py "
        f"--reseed --reason '<what was fixed>'")


def test_the_widened_quote_guard_sees_the_shapes_that_escaped(tmp_path):
    """PLANTED on F215's own case and on the two normaliser gaps the census measured."""
    note = tmp_path / "planted.md"
    note.write_text('---\ncitekey: planted\nheld: true\npdf: PDF_papers/x.pdf\n---\n# planted\n\n'
                    'The paper reports that "the laser beam is not a plane wave" (p. 3).\n', encoding="utf-8")
    assert _asserted_quotes(note) == [], "the old finder must ignore it (that is the blind spot)"
    assert len(_all_quotes(note)) == 1, "the widened finder must see the unasserted quotation"
    assert _norm("for $d \\ge 3$ vanish") == _norm("for d \u2265 3 vanish"), "a LaTeX macro against its symbol"
    assert _norm("samples $m$, which") == _norm("samples \U0001d45a, which"), "NFKC: italic maths"
    assert _norm("spectral estimate accounts") != _norm("spectral estimator accounts"), "a substituted word"
    assert _digest("a", "x y z") != _digest("b", "x y z"), "the digest is keyed on the note"


@pytest.mark.slow
def test_the_escaped_substitution_is_now_caught_against_its_pdf():
    """The exact word swap that rode through on 2026-09-20 ('estimate' for the paper's 'estimator')."""
    note = LIT_DIR / "sifft2026.md"
    fm = _frontmatter(note) if note.exists() else {}
    pdf = ROOT / str(fm.get("pdf") or "")
    if fm.get("held") != "true" or not pdf.is_file():
        pytest.skip("sifft2026 not held here")
    hay = _extract(pdf)
    if hay is None:
        pytest.skip("sifft2026's PDF unreadable")
    assert _norm("it is essential that the spectral estimator accounts for the window length") in hay
    assert _norm("it is essential that the spectral estimate accounts for the window length") not in hay


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="re-seed the known-unmatched baseline from the shelf")
    ap.add_argument("--reseed", action="store_true")
    ap.add_argument("--reason", default=None)
    a = ap.parse_args(argv)
    if not a.reseed:
        ap.error("--reseed --reason '<why>' is the only action")
    if not a.reason:
        ap.error("--reason is required: the baseline records what is known, and why it moved")
    members, notes, quotes = {}, 0, 0
    for key, note, pdf in _CHECKED_ALL:
        hay = _extract(pdf)
        if hay is None:
            continue
        notes += 1
        ds = []
        for _, q in _all_quotes(note):
            quotes += 1
            if _norm(q) not in hay:
                ds.append(_digest(key, q))
        if ds:
            members[key] = sorted(ds)
    import datetime
    _BASELINE_PATH.write_text(json.dumps({
        "_what": "digests of (note, quotation) pairs known NOT to match their PDF; may only shrink",
        "_seeded": datetime.date.today().isoformat(), "_reason": a.reason,
        "members": members}, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    n = sum(len(v) for v in members.values())
    print(f"baseline: {n} unmatched quotations in {len(members)} notes, of {quotes} quotations in {notes} notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

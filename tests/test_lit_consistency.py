"""
SINGLE SOURCE OF TRUTH for the literature: one file per paper under docs/lit/,
from which docs/references.bib and PDF_papers/README.md are GENERATED.

Why this file exists. The literature metadata used to live in three hand-kept
stores keyed by the same citekey -- LITERATURE.md prose, references.bib, and the
PDF_papers holdings table -- with nothing keeping them in step, and it had
drifted: 11 citekeys were cited with no bib entry, one quarantined key was still
cited, the bib header said "31 entries" over 53, and a near-duplicate pair
(rajasree2020 / rajasree2020spin) was unguarded. The fix makes docs/lit/<key>.md
the one place a paper's facts live and regenerates the other two views from it
(scripts/build_lit_index.py). This test is the wire that keeps them honest:

  (A) resolution:  every backtick citekey used in the manuscript docs resolves
      to a docs/lit/<key>.md -- except a documented KNOWN_DANGLING allowlist
      (tracked-but-not-yet-held papers, still bib-less during migration) and a
      QUARANTINE set (cited only to say "do NOT cite", must have no lit file).
  (B) schema:  each lit file's frontmatter is present and well-typed
      (citekey==filename, controlled enums, typed booleans, loci vocabulary).
  (C) holdings:  held<->pdf<->filesystem agree (path under PDF_papers/; the
      file exists locally, where the gitignored PDFs are present -- degraded to
      a path-only check on CI, which has no PDFs).
  (D) freshness:  re-running the generator in memory reproduces the committed
      references.bib and PDF_papers/README.md byte-for-byte -- the drift gate.
  (E) collision:  no citekey is an accidental strict prefix of another (the
      rajasree2020/...spin trap), beyond an intentional-pairs allowlist.

To add a paper: write docs/lit/<key>.md, run scripts/build_lit_index.py, commit
the three. To cite a not-yet-held paper: add its key to KNOWN_DANGLING here.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LIT_DIR = ROOT / "docs" / "lit"
BIB = ROOT / "docs" / "references.bib"
PDF_DIR = ROOT / "PDF_papers"
PDF_README = PDF_DIR / "README.md"

# load the generator (scripts/ is not a package) so parser + emitters have one source
_spec = importlib.util.spec_from_file_location(
    "build_lit_index", ROOT / "scripts" / "build_lit_index.py")
bli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bli)

# --------------------------------------------------------------------------- #
# documented exceptions (shrink these as migration proceeds)                   #
# --------------------------------------------------------------------------- #

# Cited in LITERATURE.md with inline bib details but no PDF and no lit file yet
# (reported, not held). Allowed to dangle; promote to a lit file when a PDF lands.
KNOWN_DANGLING = {
    "li2024perspective", "wieman1987", "yudin2020", "feng2026", "lidou2024",
    "nunes2024", "weiss2018", "sadeghi2026", "bevilacqua2012", "bjorkholm1976",
}

# Cited ONLY to forbid citing (malformed / superseded). Must have no lit file.
QUARANTINE = {"drago2026"}

# Legitimate prefix pairs (a base key and a variant of the same lineage).
INTENTIONAL_PREFIX_PAIRS = {("rajasree2020", "rajasree2020spin")}

# A backtick token shaped like a bibtex key: >=2 leading letters, a 4-digit year,
# optional suffix. Tight enough to skip `M16`, `power_025`, `4121nm`, `rb5s6s`.
_CITE_RE = re.compile(r"`([a-z][a-zA-Z]+\d{4}[a-zA-Z0-9]*)`")
# markdown links into the lit store, e.g. [orson2021](lit/orson2021.md)
_LINK_RE = re.compile(r"\]\((?:\.\./)?lit/([a-zA-Z0-9_]+)\.md\)")

_TYPE_OK = {"article", "inproceedings", "misc"}
_STATUS_OK = {"VERIFIED", "REPORTED"}
_ROUTING_OK = {"CITE", "FEED"}
_LOCI_RE = re.compile(r"^(P1|P2|THEORY|constants|methods/\d{2}|M\d+)(:.+)?$")

_PDFS_PRESENT = any(PDF_DIR.glob("*.pdf"))  # True locally, False on CI (gitignored)


def _lit_keys():
    return {p.stem for p in LIT_DIR.glob("*.md")}


def _manuscript_docs():
    """The prose docs that cite the literature (NOT docs/lit/*, whose bodies
    reference sibling keys in free prose)."""
    return ([p for p in (ROOT / "docs").glob("*.md")]
            + [p for p in (ROOT / "docs" / "methods").glob("*.md")]
            + [ROOT / "README.md"])


def _cited_keys():
    keys = {}
    for d in _manuscript_docs():
        if not d.exists():
            continue
        text = d.read_text()
        for k in _CITE_RE.findall(text) + _LINK_RE.findall(text):
            keys.setdefault(k, set()).add(d.name)
    return keys


def _fm(key):
    return bli._parse_frontmatter((LIT_DIR / f"{key}.md").read_text())


# --------------------------------------------------------------------------- #
# (A) every cited citekey resolves, or is a documented exception               #
# --------------------------------------------------------------------------- #
def test_cited_keys_resolve():
    lit = _lit_keys()
    allowed = lit | KNOWN_DANGLING | QUARANTINE
    unresolved = {k: sorted(v) for k, v in _cited_keys().items() if k not in allowed}
    assert not unresolved, (
        "citekeys cited in the docs with no docs/lit/<key>.md and not in the "
        "KNOWN_DANGLING/QUARANTINE allowlists (add a lit file or the allowlist):\n  "
        + "\n  ".join(f"{k}  (in {', '.join(v)})" for k, v in sorted(unresolved.items())))


def test_quarantine_has_no_lit_file():
    lit = _lit_keys()
    leaked = sorted(QUARANTINE & lit)
    assert not leaked, (
        f"QUARANTINE keys must have NO lit file (they are cited only to forbid "
        f"citing): {leaked}")


def test_allowlists_are_not_stale():
    """A dangling/quarantined key that has since gained a lit file must leave the
    allowlist, so the exceptions never quietly outlive their reason."""
    lit = _lit_keys()
    stale_dangling = sorted(KNOWN_DANGLING & lit)
    assert not stale_dangling, (
        f"these KNOWN_DANGLING keys now HAVE a lit file -- remove them from the "
        f"allowlist: {stale_dangling}")
    cited = set(_cited_keys())
    unused = sorted((KNOWN_DANGLING | QUARANTINE) - cited)
    assert not unused, (
        f"these allowlisted keys are no longer cited anywhere -- drop them from "
        f"KNOWN_DANGLING/QUARANTINE: {unused}")


# --------------------------------------------------------------------------- #
# (B) frontmatter schema                                                        #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_frontmatter_well_typed(key):
    fm = _fm(key)
    assert fm.get("citekey") == key, f"citekey '{fm.get('citekey')}' != filename '{key}'"
    for req in ("type", "title", "authors", "status", "summary"):
        assert fm.get(req) not in (None, "", []), f"{key}: missing/empty '{req}'"
    assert fm["type"] in _TYPE_OK, f"{key}: type '{fm['type']}' not in {_TYPE_OK}"
    assert fm["status"] in _STATUS_OK, f"{key}: status '{fm['status']}' not in {_STATUS_OK}"
    assert isinstance(fm.get("authors"), list), f"{key}: authors must be a list"
    assert isinstance(fm.get("held"), bool), f"{key}: held must be a bool"
    routing = fm.get("routing") or []
    assert set(routing) <= _ROUTING_OK, f"{key}: routing {routing} not subset of {_ROUTING_OK}"
    for locus in (fm.get("loci") or []):
        assert _LOCI_RE.match(locus), f"{key}: locus '{locus}' fails the controlled vocabulary"


# --------------------------------------------------------------------------- #
# (C) held <-> pdf <-> filesystem                                              #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_held_pdf_filesystem(key):
    fm = _fm(key)
    pdf = fm.get("pdf")
    if fm.get("held"):
        assert pdf, f"{key}: held:true but no pdf path"
        assert pdf.startswith("PDF_papers/"), f"{key}: pdf '{pdf}' not under PDF_papers/"
        if _PDFS_PRESENT:  # local run: the gitignored PDFs are on disk
            assert (ROOT / pdf).exists(), (
                f"{key}: held:true, pdf '{pdf}' does not exist on disk")
    elif pdf:  # not held but a path given -> must be well-formed
        assert pdf.startswith("PDF_papers/"), f"{key}: pdf '{pdf}' not under PDF_papers/"


# --------------------------------------------------------------------------- #
# (D) generator freshness -- the drift gate                                    #
# --------------------------------------------------------------------------- #
def test_generated_bib_is_fresh():
    entries = bli.load_lit()
    fresh = bli.emit_bib(entries)
    assert BIB.read_text() == fresh, (
        "docs/references.bib is stale -- re-run scripts/build_lit_index.py and "
        "commit the result.")


def test_generated_readme_is_fresh():
    entries = bli.load_lit()
    fresh = bli.emit_readme(entries)
    assert PDF_README.read_text() == fresh, (
        "PDF_papers/README.md is stale -- re-run scripts/build_lit_index.py and "
        "commit the result.")


# --------------------------------------------------------------------------- #
# (E) accidental prefix-collision guard                                        #
# --------------------------------------------------------------------------- #
def test_no_accidental_prefix_collisions():
    keys = sorted(_lit_keys())
    collisions = []
    for a in keys:
        for b in keys:
            if a != b and b.startswith(a) and (a, b) not in INTENTIONAL_PREFIX_PAIRS:
                collisions.append((a, b))
    assert not collisions, (
        "citekey is a strict prefix of another (likely an accidental near-duplicate; "
        "add to INTENTIONAL_PREFIX_PAIRS if deliberate):\n  "
        + "\n  ".join(f"{a} <| {b}" for a, b in collisions))

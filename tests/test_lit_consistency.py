"""
SINGLE SOURCE OF TRUTH for the literature: one file per paper under docs/lit/,
from which docs/references.bib and docs/LITERATURE_INDEX.md are GENERATED.

Why this file exists. The literature metadata used to live in three hand-kept
stores keyed by the same citekey -- LITERATURE.md prose, references.bib, and the
PDF_papers holdings table -- with nothing keeping them in step, and it had
drifted: 11 citekeys were cited with no bib entry, one excluded key was still
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
      references.bib and docs/LITERATURE_INDEX.md byte-for-byte -- the drift gate.
  (E) collision:  no citekey is an accidental strict prefix of another (the
      rajasree2020/...spin trap), beyond an intentional-pairs allowlist.

To add a paper: write docs/lit/<key>.md, run scripts/build_lit_index.py, commit
the three. To cite a not-yet-held paper: add its key to KNOWN_DANGLING here.
"""

from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path

import pytest

# The names that belong in citation context and nowhere else live in the
# hygiene module as truncated digests. Reuse that set and its tokenizer rather
# than restating either here.
from test_repo_hygiene import _NAME_DIGESTS, _WORD

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
    # wieman1987 left this list 2026-07-30: it now has a note at REPORTED with a
    # full bibliographic record (PRL 58, 1738; DOI 10.1103/PhysRevLett.58.1738).
    # Still not held -- 1987, pre-arXiv, APS 403 without a subscription.
    # li2024perspective left this list 2026-08-22: now a REPORTED note with the
    # unit publication list's full record (J. Phys. Photon. 6, 021002 (2024),
    # DOI 10.1088/2515-7647/ad3d19). Not held -- the IOP PDF resists scripted
    # retrieval; upgrade through institutional access and a full read.
    # feng2026 left this list 2026-08-03: now docs/lit/feng2026.md, held and
    # VERIFIED (Opt. Lett. 51, 1363-1366 (2026), DOI 10.1364/OL.589640).
    # lidou2024 still wanted, not yet supplied.
    "lidou2024",
    # bevilacqua2012 RETIRED 2026-07-30: a misattribution. PRA 86, 012501
    # (2012) is Bruvelis et al., now docs/lit/bruvelis2012.md. The old key is
    # not aliased, so nothing can cite the wrong author by accident.
    # sadeghi2026 and quirk2024 left this list 2026-07-30: both fetched from
    # arXiv, read, and noted. patterson2018 was a must-read surfaced by
    # sadeghi2026 ref [25] -- PRA 97, 032509 (2018), spectral asymmetry in the
    # van der Waals potential of an ONF, the direct precedent for the nanofibre extension.
    "nunes2024", "weiss2018",
    # (sieradzan2004 was described here as having no lit file, on the strength of
    # a PDF add that "did not land". That is FALSE and was removed 2026-07-31:
    # docs/lit/sieradzan2004.md exists, held and VERIFIED, with the arXiv
    # preprint physics/0308092 on disk. The stale comment sat directly above the
    # allow-list and read as if it were justifying an entry in it.)
    # boustimi2002 (PRB 65, 155402): sague2007's ref [15], long carried here as
    # the second theory input the Patterson refit needs. Confirmed paywalled
    # again 2026-07-30 (no arXiv preprint, no repository copy, no OA route; real
    # title is "van der Waals interaction between an atom and a metallic
    # nanowire" -- the citation elsewhere is a paraphrase). DEMOTED 2026-07-31
    # and no longer on the critical path: Sague CALCULATED their own vdW shift
    # and cite this for the method, and both Boustimi papers work the metallic
    # wire while the fibres are silica. frawley2012 replaces it and is HELD --
    # frawley2012 was supplied by the experimenter 2026-07-31 and is held.
    # boustimi2002 stays in this list only because the notes still name it.
    "boustimi2002",
}

# Cited ONLY to forbid citing (malformed / superseded). Must have no lit file.
QUARANTINE = {
    "drago2026",
    # bevilacqua2012: a MISATTRIBUTION, not a bad paper. PRA 86, 012501 (2012)
    # is Bruvelis et al. (docs/lit/bruvelis2012.md); there is no Bevilacqua
    # among the authors. The key is excluded rather than aliased so that
    # the only place it may appear is the correction that retires it.
    "bevilacqua2012",
}

# Legitimate prefix pairs (a base key and a variant of the same lineage).
INTENTIONAL_PREFIX_PAIRS = {
    ("li2024", "li2024b"),  # same year, same 778 nm line, different first authors; cross-referenced in both notes
    # li2024 is a Wang/Li atomic-clock shift-compensation paper. The
    # perspective is Li, Wenfang and the whole OIST unit in J. Phys.
    # Photonics. Different people, different journals, and the longer key
    # predates its own note: docs/LITERATURE.md cited it while it sat on
    # KNOWN_DANGLING, so renaming it would break those citing sites.
    ("li2024", "li2024perspective"),
("rajasree2020", "rajasree2020spin"),
    # THREE distinct Rajasree 2020 documents, and conflating them is not
    # hypothetical: until 2026-07-31 both LITERATURE.md and rajasree2020.md
    # attributed the thesis's 993 nm vapour-cell apparatus to the PRR paper's
    # key. rajasree2020 = PRR 2, 012038 (cold Rydberg near an ONF, no warm
    # cell); rajasree2020thesis = the OIST PhD thesis, whose section 5.2 IS
    # that cell apparatus and carries the density.py N(T) FEED.
    ("rajasree2020", "rajasree2020thesis"),
    # same first author, same year, different papers: JOSA B 9 2163
    # (with Lambropoulos) and Opt. Commun. 91 343 (with Klimcak)
    ("camparo1992", "camparo1992b"),
}

# A backtick token shaped like a bibtex key: >=2 leading letters, a 4-digit year,
# optional suffix. Tight enough to skip `M16`, `power_025`, `4121nm`, `rb5s6s`.
_CITE_RE = re.compile(r"`([a-z][a-zA-Z]+\d{4}[a-zA-Z0-9]*)`")
# markdown links into the lit store, e.g. [orson2021](lit/orson2021.md)
_LINK_RE = re.compile(r"\]\((?:\.\./)?lit/([a-zA-Z0-9_]+)\.md\)")

_TYPE_OK = {"article", "inproceedings", "misc"}
_STATUS_OK = {"VERIFIED", "REPORTED"}
_ROUTING_OK = {"CITE", "FEED"}
_LOCI_RE = re.compile(r"^(P1|P2|THEORY|constants|methods/\d{2}|M\d+[a-z]?)(:.+)?$")

_PDFS_PRESENT = any(PDF_DIR.glob("*.pdf"))  # True locally, False on CI (gitignored)


def _lit_notes(d):
    """The per-paper notes under docs/lit, which is every markdown file there
    except its README. The README is a door into the directory and carries no
    citekey frontmatter, so every check that reads frontmatter must skip it."""
    from _fileset import tracked_and_new
    rel = str(d.relative_to(ROOT))
    return [ROOT / p for p in tracked_and_new(f"{rel}/*.md")
            if not p.endswith("/README.md")]


def _lit_keys():
    """The citekeys, as a SORTED TUPLE rather than a set.

    A set here was a real defect, not a style point. Four of this file's
    parametrize sites passed it unsorted, and Python randomises string
    hashing per process, so every process enumerated the same 123 keys in a
    different order. One process never notices. Under pytest-xdist the
    workers disagreed about the ORDER of 492 collected tests and the run
    died at collection before a single test executed, on 2026-08-13.

    It stays a SET, because three call sites do set algebra on it, and
    every parametrize site sorts. If a new parametrize site is added,
    sort there too.
    """
    return {p.stem for p in _lit_notes(LIT_DIR)}


def _manuscript_docs():
    """The prose docs that cite the literature (NOT docs/lit/*, whose bodies
    reference sibling keys in free prose)."""
    from _fileset import tracked_and_new
    # :(glob) pathspecs, because a BARE git pathspec lets * cross slashes:
    # "docs/*.md" matches 169 files recursively where this selector wants the
    # 22 top-level ones. Verified 2026-08-15 by domain diff (31 both ways).
    # docs/wiki/*.md joined 2026-08-16. The wiki pages cite the same
    # literature the chapters do, so a citekey typo there has to fail here
    # too. They sit one level down like the chapters, so the same explicit
    # glob per directory is what includes them.
    return [ROOT / p for p in
            tracked_and_new(":(glob)docs/*.md", ":(glob)docs/methods/*.md",
                            ":(glob)docs/wiki/*.md", "README.md")]


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


def _digest(word: str) -> str:
    return hashlib.sha256(word.lower().encode()).hexdigest()[:16]


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


def test_excluded_set_has_no_lit_file():
    lit = _lit_keys()
    leaked = sorted(QUARANTINE & lit)
    assert not leaked, (
        f"QUARANTINE keys must have NO lit file (they are cited only to forbid "
        f"citing): {leaked}")


def test_allowlists_are_not_stale():
    """A dangling/excluded key that has since gained a lit file must leave the
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
    for req in ("type", "title", "authors", "status", "summary", "section"):
        assert fm.get(req) not in (None, "", []), f"{key}: missing/empty '{req}'"
    assert fm["type"] in _TYPE_OK, f"{key}: type '{fm['type']}' not in {_TYPE_OK}"
    assert fm["status"] in _STATUS_OK, f"{key}: status '{fm['status']}' not in {_STATUS_OK}"
    assert fm["section"] in bli.SECTION_SLUGS, (
        f"{key}: section '{fm['section']}' not in {bli.SECTION_SLUGS}")
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


def test_generated_public_index_is_fresh():
    entries = bli.load_lit()
    fresh = bli.emit_public_index(entries)
    assert (ROOT / "docs" / "LITERATURE_INDEX.md").read_text() == fresh, (
        "docs/LITERATURE_INDEX.md is stale -- re-run scripts/build_lit_index.py "
        "and commit the result.")


def test_generated_local_readme_is_fresh_when_present():
    """PDF_papers/README.md is the LOCAL holdings table (untracked since
    2026-07-23: a public folder named PDF_papers displaying held publisher-PDF
    filenames reads as a shelf of copyrighted papers, though none is
    distributed). Gate it only where it exists."""
    if not PDF_README.exists():
        pytest.skip("local holdings index absent (untracked; fine in CI)")
    entries = bli.load_lit()
    fresh = bli.emit_readme(entries)
    assert PDF_README.read_text() == fresh, (
        "PDF_papers/README.md (local) is stale -- re-run "
        "scripts/build_lit_index.py.")


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


# --------------------------------------------------------------------------
# Rendering hygiene of the frontmatter (added 2026-07-22)
#
# The frontmatter is displayed by GitHub as a table at the top of each note
# AND is the source for references.bib, so it serves two renderers with
# opposite needs. Three real defects motivated these checks:
#   * LaTeX accent macros in author names showed as "S\'ile" on the public
#     page instead of "Síle" — an author name, mangled.
#   * Unquoted arXiv IDs are parsed as floats, so 2201.06000 displayed as
#     2201.06 (a different, invalid identifier).
#   * Inline $...$ maths in `summary` renders literally, both in the note and
#     in the generated holdings table.
# `title:` and `pages:` are deliberately exempt: they carry publisher/BibTeX
# form ({Rb}, $6S_{1/2}$, 855--865) because they feed the .bib.
# --------------------------------------------------------------------------

_BIB_FIELDS = re.compile(r"^\s*(title|pages|journal|booktitle|publisher):")


def _lit_lines(key):
    return (LIT_DIR / f"{key}.md").read_text(encoding="utf-8").split("\n")


@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_author_names_are_unicode_not_latex(key):
    """Author fields must be readable on the page: unicode accents, no macros."""
    bad, in_authors = [], False
    for i, line in enumerate(_lit_lines(key), 1):
        if re.match(r"\s*authors:", line):
            in_authors = True
            continue
        if in_authors and re.match(r"\s*\w+:", line):
            in_authors = False
        if in_authors and "\\" in line:
            bad.append(f"{key}.md:{i}: {line.strip()}")
    assert not bad, (
        "LaTeX escape in an author name (use the unicode character — it is "
        "safe for modern BibTeX and correct on the rendered page):\n  "
        + "\n  ".join(bad)
    )


@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_arxiv_ids_survive_yaml_parsing(key):
    """An unquoted NNNN.NNNN0 is a float to YAML and loses its trailing zero."""
    for i, line in enumerate(_lit_lines(key), 1):
        m = re.match(r"\s*arxiv:\s*(.+?)\s*$", line)
        if not m:
            continue
        raw = m.group(1)
        if raw in ("null", "~", ""):
            continue
        if raw[0] in "'\"":
            continue
        if re.fullmatch(r"\d+\.\d+", raw) and raw.rstrip("0") != raw:
            pytest.fail(
                f"{key}.md:{i}: arxiv: {raw} is unquoted and ends in 0, so a "
                f"YAML parser reads it as the float {float(raw)}. Quote it."
            )


@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_summary_has_no_inline_math(key):
    """`summary` feeds both the rendered note and the generated holdings
    table; GitHub shows inline $...$ literally in both."""
    inline = re.compile(r"(?<!\$)\$(?!\$)[^$\n]{1,80}\$(?!\$)")
    bad, in_summary = [], False
    for i, line in enumerate(_lit_lines(key), 1):
        if re.match(r"\s*summary:", line):
            in_summary = True
        elif in_summary and re.match(r"\s*\w+:", line):
            in_summary = False
        if in_summary and not _BIB_FIELDS.match(line):
            for m in inline.finditer(line):
                bad.append(f"{key}.md:{i}: {m.group(0)}")
    assert not bad, (
        "inline maths in `summary` (use unicode: ⁸⁷Rb, 5S₁/₂, →):\n  "
        + "\n  ".join(bad)
    )


@pytest.mark.parametrize("key", sorted(_lit_keys()))
def test_no_process_language_in_lit_notes(key):
    """docs/lit/ is exempt from the repo-wide phrase guards so that published
    titles and quoted abstract wording survive verbatim. That exemption must
    not become a hiding place for drafting-process language or for naming
    someone in a working role.

    Whoever wrote the paper may be named anywhere in its note, so the note's
    own `authors:` list is exempt. Everyone else is matched through the shared
    digest set, which keeps the rule enforceable without any file carrying a
    list of people in the clear.
    """
    pat = re.compile(
        r"\buser(?:'s)?\b|digestion turn|\bas discussed\b|\bper your\b"
        r"|\bchatgpt\b|\bclaude\b|\banthropic\b",
        re.I,
    )
    # The reading-diary class, added 2026-08-26 on the owner's instruction:
    # a literature note is an annotated-bibliography entry, never a reading
    # diary. It does not name itself, date its own reading, draw lessons,
    # plan adoptions, or narrate its own past claims (docs/HISTORY.md holds
    # any superseded claim). "review" stays allowed here alone, for journal
    # names and the review-article genre. Enforced on the BODY only: the
    # frontmatter's qa_flags and summary are preserved QA records, kept
    # byte-stable by the note conventions, and they may name the note.
    diary = re.compile(
        r"\bthis note\b|\bread 20\d\d-|\bthe lesson\b"
        r"|\bworth (?:adopting|noting|stating)\b"
        r"|\bpreviously (?:concluded|claimed|stated)\b"
        r"|\bexperimenters?\b|\badversarial(?:ly)?\b"
        r"|\bexternal(?:ly)? check|\bpreregist\w+\b|\badjudicat\w+\b",
        re.I,
    )
    authors = " ".join(str(a) for a in (_fm(key).get("authors") or []))
    watched = _NAME_DIGESTS - {_digest(w) for w in _WORD.findall(authors)}
    bad = []
    in_front = False
    front_done = False
    for i, line in enumerate(_lit_lines(key), 1):
        if line.strip() == "---" and not front_done:
            in_front = not in_front
            if not in_front:
                front_done = True
            continue
        named = any(_digest(w) in watched for w in _WORD.findall(line))
        body_hit = (not in_front and front_done) and diary.search(line)
        if pat.search(line) or named or body_hit:
            bad.append(f"{key}.md:{i}: {line.strip()[:100]}")
    assert not bad, "process language in a literature note:\n  " + "\n  ".join(bad)


def test_narrative_docs_do_not_argue_from_unverified_papers():
    """A REPORTED note is one nobody in this repo has actually read.

    Cataloguing such a paper is fine -- that is what LITERATURE.md and
    LITERATURE_INDEX.md are for. Citing it in a document that ARGUES is not:
    BIG_PICTURE once carried "[Bandi 2025]'s review says the same of the
    field", attributing a specific finding to a paper held: false,
    status: REPORTED. The claim happened to be plausible, which is exactly why
    it survived review by eye.
    """
    import re

    reported = set()
    for note in _lit_notes(ROOT / "docs" / "lit"):
        t = note.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^status:\s*(\S+)", t, re.M)
        if m and m.group(1).strip() == "REPORTED":
            reported.add(note.stem)
    if not reported:
        # Every one of the 72 notes is currently VERIFIED, so this guard has
        # been executing zero comparisons: dormant, not passing. That is the
        # intended end state and not a defect, because a paper
        # nobody has read normally has no note at all, it sits in the dangling
        # list. Say so out loud rather than returning silently, so an empty
        # population reads as a deliberate state in `-rs` output and anyone
        # reintroducing the REPORTED status gets the guard back automatically.
        pytest.skip("no note carries status: REPORTED -- nothing to guard "
                    "(every note is VERIFIED; an unread paper normally has no "
                    "note at all and sits in the KNOWN_DANGLING allowlist)")

    CATALOGUES = {"docs/LITERATURE.md", "docs/LITERATURE_INDEX.md"}
    from _fileset import tracked_and_new
    tracked = tracked_and_new("docs/*.md", "README.md")
    hits = []
    for rel in tracked:
        if rel in CATALOGUES or "/lit/" in rel:
            continue
        for i, line in enumerate(
                (ROOT / rel).read_text(encoding="utf-8",
                                       errors="replace").split("\n"), 1):
            for key in re.findall(r"\(lit/([a-z0-9]+)\.md\)", line):
                if key in reported:
                    hits.append(f"{rel}:{i}: cites {key} (status REPORTED)")
    assert not hits, (
        "a narrative document argues from a paper nobody here has read; "
        "either verify the source or drop the claim:\n  " + "\n  ".join(hits))


def test_verified_status_requires_a_real_bibliographic_record():
    """LITERATURE.md defines the tiers: "VERIFIED means we read the source
    itself; REPORTED means a literature-scout summary we have not yet read in
    full". A note whose TITLE is a bracketed description rather than the paper's
    title, or whose author list ends in a bare "others", is a record nobody has
    checked against the paper -- so it cannot be VERIFIED.

    Found 2026-07-30, when the status field turned out to be non-discriminating:
    72 of 72 notes said VERIFIED and REPORTED was used zero times, while three
    of them carried placeholder titles and three a stub author list. Those were
    demoted (ray2020, roy2017, callejo2025 -- none cited anywhere that argues).
    borde1976 is the exception and is allowed here only because it carries an
    explicit verify_flag saying so: it IS cited, in methods/02 and the
    manuscript skeleton, so demoting it silently would have left an argument
    resting on a REPORTED source, which the same rule forbids.

    The escape hatch is deliberate and narrow: a placeholder record may keep
    VERIFIED only if a verify_flag names the defect, so the gap is visible in
    the note and in the generated bib rather than implied by its absence.
    """
    import re

    offenders = []
    for note in sorted(_lit_notes(ROOT / "docs" / "lit")):
        txt = note.read_text(encoding="utf-8")
        if not txt.startswith("---"):
            continue
        fm = txt.split("---")[1]
        status = re.search(r"^status:\s*(\S+)", fm, re.M)
        if not status or status.group(1).strip() != "VERIFIED":
            continue
        title = re.search(r"^title:\s*(.*)$", fm, re.M)
        placeholder = bool(title and title.group(1).strip().strip("'\"").startswith("["))
        stub_author = bool(re.search(r"^\s*-\s*others\s*$", fm, re.M))
        if not (placeholder or stub_author):
            continue
        flagged = "PLACEHOLDER" in fm.upper()
        if not flagged:
            why = "placeholder title" if placeholder else "stub author list"
            offenders.append(f"{note.name}: VERIFIED with a {why} and no verify_flag saying so")
    assert not offenders, (
        "status: VERIFIED asserts the source was read; these records were never "
        "checked against the paper:\n  " + "\n  ".join(offenders) +
        "\nEither demote to REPORTED, fill the record, or add a verify_flag "
        "naming the gap.")


# VERIFIED notes that predate the verified_date convention and carry no date
# anywhere in the file. Frozen 2026-07-30 so the debt can only SHRINK: a new
# note cannot join this list, and one that gains a date must leave it.
# 53 notes were dateless before that pass; 20 had the date sitting in their body
# prose and were backfilled from it. These 30 have none to recover, so the date
# has to come from whoever reads the paper next.
UNDATED_VERIFIED = {
    "ahern2025", "amy2017", "andeweg2026", "antypas2018", "araujo2021",
    "ayachitula2024", "bala2026",
    "biraben2019", "borde1976", "chevrollier2012", "fioretti1998",
    "gerginov2018", "gomez2005", "grimm2000", "hamilton2023",
    "lehmann2021", "martin2018", "newman2021", "nieddu2019", "poulin2002",
    "rajasree2020", "safronova2004", "safronova2006",
    "sautenkov2026", "snadden1996", "spiegelman2022", "stalnaker2006",
}


def test_verified_notes_carry_a_verification_date():
    """"VERIFIED means we read the source itself" (LITERATURE.md). A claim to
    have read something on no stated date is not checkable, and 53 of 72 notes
    carried exactly that.

    This freezes the debt rather than papering over it. UNDATED_VERIFIED lists
    the notes whose date could not be recovered from their own body; everything
    else must carry one. So a NEW note cannot be VERIFIED without a date, and
    the list can only shrink -- the second assertion fails if a listed note
    gains a date and is not removed, which is what stops the allowlist
    outliving its reason.
    """
    import re

    missing, stale = [], []
    for note in sorted(_lit_notes(ROOT / "docs" / "lit")):
        txt = note.read_text(encoding="utf-8")
        if not txt.startswith("---"):
            continue
        fm = txt.split("---")[1]
        st = re.search(r"^status:\s*(\S+)", fm, re.M)
        if not st or st.group(1).strip() != "VERIFIED":
            continue
        vd = re.search(r"^verified_date:\s*(\S+)", fm, re.M)
        dated = bool(vd and vd.group(1).strip() != "null")
        if dated and note.stem in UNDATED_VERIFIED:
            stale.append(note.stem)
        if not dated and note.stem not in UNDATED_VERIFIED:
            missing.append(note.stem)

    assert not missing, (
        "VERIFIED with no verified_date, and not on the frozen debt list:\n  "
        + "\n  ".join(missing)
        + "\nEither date it, demote it to REPORTED, or -- only if it predates "
          "the convention and its body carries no date -- add it to "
          "UNDATED_VERIFIED with a reason.")
    assert not stale, (
        "these notes now HAVE a verified_date -- remove them from "
        f"UNDATED_VERIFIED so the list keeps shrinking: {sorted(stale)}")


# Keys that deliberately do NOT name their paper's first author. Each needs a
# verify_flag in its note saying so, because the mismatch is otherwise
# indistinguishable from the misattribution that motivated this guard.
CITEKEY_NOT_FIRST_AUTHOR = {
    "bandi2025",        # Obaze-Adeleke, Semon & Bandi; key names the corresponding author
    "steck_rb",         # a data compilation, not an author-year key
}


def test_citekey_matches_its_first_author():
    """The error this catches actually happened, and would have reached a referee.

    PRA 86, 012501 (2012) was carried for months as `bevilacqua2012`. Volume,
    page, year and the physics description were all correct; the author was not
    -- Crossref gives Bruvelis, Ulmanis, Bezuglov, Miculis, Andreeva, Mahrov,
    Tretyakov and Ekers, with no Bevilacqua among them. The key is marked CITE,
    so the manuscript would have credited the transit-Voigt result to somebody
    who did not write it, in a citation nobody could resolve.

    So: a citekey must agree with the first author its own note records. That is
    a purely internal check -- it cannot tell whether the authors field is right,
    only whether the key and the field tell the same story -- but the
    bevilacqua2012 note never existed, and the moment one was written the
    mismatch would have been visible. Genuine exceptions (a key naming a
    corresponding author, a data compilation) are allowlisted and must carry a
    verify_flag explaining themselves, so a silent mismatch cannot hide among
    them.
    """
    import re
    import unicodedata

    def norm(s):
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
        return re.sub(r"[^a-z]", "", s.lower())

    bad, undocumented = [], []
    for note in sorted(_lit_notes(LIT_DIR)):
        fm = bli._parse_frontmatter(note.read_text(encoding="utf-8"))
        authors = fm.get("authors") or []
        if not authors:
            continue
        surname = norm(str(authors[0]).split(",")[0])
        prefix = re.sub(r"\d.*$", "", note.stem)
        agrees = bool(surname and prefix) and (
            prefix.startswith(surname[:5]) or surname.startswith(prefix[:5]))
        if agrees:
            continue
        if note.stem not in CITEKEY_NOT_FIRST_AUTHOR:
            bad.append(f"{note.stem}: first author is {authors[0]!r}")
        else:
            flags = " ".join(fm.get("verify_flags") or []).upper()
            if "CITEKEY" not in flags:
                undocumented.append(note.stem)

    assert not bad, (
        "citekey disagrees with the note's own first author -- either the key or "
        "the authors field is wrong, and one of them will reach a referee:\n  "
        + "\n  ".join(bad)
        + "\nIf the key deliberately names someone else (a corresponding author, "
          "a compilation), add it to CITEKEY_NOT_FIRST_AUTHOR *and* put a "
          "verify_flag in the note saying so.")
    assert not undocumented, (
        "these keys are allowlisted as not-first-author but their notes carry no "
        f"verify_flag explaining it: {sorted(undocumented)}")

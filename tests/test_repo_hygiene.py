"""Repository hygiene: what must never enter the public history, and the
house conventions that keep the published documents consistent.

Every check reads `git ls-files` — the TRACKED set — so local working files
(correspondence drafts, reviewer notes, personal documents kept in the tree
for convenience) are never scanned and cannot trip a check. That is the point:
the guards describe what is published, not what happens to sit on disk.

Motivation, in order of severity:

1. The personal/correspondence documents were protected only by
   .git/info/exclude, which is local to a single clone. A fresh clone on
   another machine had no protection, and one `git add docs/` there would
   have published them. .gitignore now carries generic patterns and this
   module fails if any matching path is ever tracked anyway.
2. A repo-wide editorial pass (2026-07) removed drafting-process language and
   an aphoristic register from the published documents. Without a guard the
   same phrasing returns with the next batch of writing.
3. Colleagues were named in internal-process roles ("X must be able to take
   over", "ask X") on public pages, before those roles had been agreed. Names
   belong in citation context; the allowlist below encodes that distinction.
"""

from __future__ import annotations

import ast
import hashlib
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _tracked(*globs: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", *globs],
                         capture_output=True, text=True)
    if out.returncode != 0:                       # no git (tarball): skip
        pytest.skip("not a git checkout")
    return [p for p in out.stdout.split("\n") if p]


# --------------------------------------------------------------------------
# 1. Private material must never be tracked
# --------------------------------------------------------------------------
#
# Working material that is not part of the published record: the local working
# folder, personal and correspondence documents, unpublished drafts, and the
# reference-setup notes and photographs, which carry equipment serials. Both
# spellings of each pattern are listed, because a glob that assumed one
# spelling let three files through once.
PRIVATE_GLOBS = ["private/*", "private/**/*", "CLAUDE.md", "docs/brief_*",
                 "docs/*audit*", "docs/*red_team*", "docs/*redteam*",
                 "docs/ChatGPT*", "ChatGPT*",
                 "docs/CV_*", "docs/*inquiry*", "docs/linkedin*", "*.docx",
                 "docs/PAPERS_PORTFOLIO.md",
                 "docs/PAPER1_SKELETON.md", "docs/paper1/*",
                 "docs/reference_setup/*", "docs/reference_setup/**/*",
                 "docs/*.tex"]
# docs/*.tex joined the same day. Three private files sat in docs/ held out by
# filename globs alone, which is the failure mode this list already records
# once, and they now live under private/ with the glob as the second line of
# defence.


def test_no_private_documents_tracked():
    tracked = _tracked(*PRIVATE_GLOBS)
    assert not tracked, (
        "private/correspondence files are tracked and would be published:\n  "
        + "\n  ".join(tracked)
        + "\n(they belong in the working tree only — see .gitignore)"
    )


def test_no_personal_contact_details_in_tracked_files():
    """The unibo address is deliberate (README About); a personal mail address
    or a phone number in the published tree is not."""
    bad = re.compile(r"[\w.+-]+@gmail\.com|\+\d{2}[\s-]?\d{3}[\s-]?\d{6,}")
    hits = []
    for rel in _tracked("*.md", "*.py", "*.toml", "*.cff", "*.yml", "*.yaml"):
        try:
            txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.split("\n"), 1):
            if bad.search(line):
                hits.append(f"{rel}:{i}")
    assert not hits, "personal contact details in tracked files: " + ", ".join(hits)


# --------------------------------------------------------------------------
# 2. Drafting-process artifacts and the aphoristic register
# --------------------------------------------------------------------------
# Narrow, exact phrases only. Precise technical constructions ("an upper
# bound, not a detection") are legitimate and must keep working — the bank
# below is a list of specific removed sentences, not a pattern for "X, not Y".
FORBIDDEN = {
    "drafting-process reference": [
        r"\buser(?:'s)?\b(?!name)", r"\bdigestion turn\b", r"\bas discussed\b",
        r"\bper your\b", r"\byou asked\b", r"\bas requested\b",
    ],
    "assistant/tool name": [
        r"\bchatgpt\b", r"\bclaude\b", r"\banthropic\b", r"\bopenai\b",
        r"\bcopilot\b", r"\bas an ai\b", r"\blanguage model\b",
    ],
    # PORTED FROM THE MIRROR 2026-08-10. This bank was added to the public
    # repository on 2026-08-09 by owner instruction and the sweep ran on both
    # trees, but only the mirror got the BANK, so for a day the archive was not
    # enforcing a rule the mirror enforced, in the repository where writing
    # happens first. The two banks are now identical and any addition goes into
    # both in the same pass. The common thread is vocabulary that belongs to
    # how the work was managed rather than to what it found.
    #
    # "wave" is deliberately NOT here. Every bare occurrence in this tree is
    # physics (four-wave-mixing, matter-wave, millimetre-wave) and the process
    # sense was already removed, so a pattern for it would fire only on
    # standing waves and wavelengths.
    #
    # NAMED 2026-08-10 and NOT YET HERE, because each needs a sweep first and
    # the two largest need the owner to choose the replacement term: prehistory
    # (58 occurrences), plumbing (5), archive and archival (947), quarantine
    # (282), win/wins/winning (58), prize (3). The rule is in the rendering
    # protocol section 2.1 with the counts and the replacements, and it governs
    # anything newly written from that date. Moving a word from that list to
    # this bank is the last step of its sweep, not the first.
    "internal process vocabulary": [
        r"red[- ]?team",
        r"\bprice[sd]?\b", r"\bpricing\b",
        r"supersed",
        r"\bbasins?\b", r"\bbasin-\w+",
        r"\btiers?\b", r"\bTier\s+\d",
        r"\blong pole\b",
        r"\btrouble", r"\btriage",
        r"\bknown-red\b", r"plant[- ]verif",
    ],
    "aphoristic register": [
        r"is itself an?\b", r"is itself the\b",
        r"a test passed, not a tuning",
        # Generalizes what were two exact strings ("the honest headline", "the
        # honest through-line") after a same-day audit found the register
        # recurring as "the honest reading/comparison/statement/case/summary/
        # weak point/end state" across docs/BIG_PICTURE.md,
        # docs/THEORY_NOTE.md, docs/PREREGISTRATION_RESULTS.md,
        # docs/PREREGISTRATION_timestamps.md and docs/lit/*.md (2026-07-30).
        # Matching just "the honest <word>" catches all of these, including
        # hyphenated tails like "through-line", since re.search only needs
        # the pattern present as a substring.
        r"the honest \w+",
        r"not a hedge but",
        r"cannot be scooped", r"not a failed measurement",
        r"laundered into", r"not a hunch", r"selling point",
        r"price of admission", r"self-certifies",
    ],
}

# docs/lit/ are per-paper notes: published titles/abstract wording are quoted
# there verbatim and must not be edited to satisfy a style rule.
SKIP_PREFIXES = ("docs/lit/",)

# Files that DEFINE these rules necessarily quote the phrases they forbid —
# the style guide as worked examples, the guard modules as patterns. They are
# the specification, not instances of the problem. Any new file that encodes
# the rules belongs here too.
SKIP_EXACT = {"docs/STYLE.md", "tests/test_repo_hygiene.py",
              "tests/test_lit_consistency.py",
              # These three detect stale and replaced values in the documents
              # and the figures, so their patterns and their test names must
              # name the vocabulary of supersession. Added 2026-08-09 with the
              # internal-process bank: they are the specification again, the
              # same reason the two above are here.
              "tests/test_docs_canonical.py",
              "tests/test_ramp_geometry_docs.py",
              "tests/test_svg_canonical.py"}


def _about_to_be_tracked(*globs: str) -> list[str]:
    """Files git would add on the next `git add -A`, i.e. untracked and not ignored.

    WHY THIS EXISTS. On 2026-08-13 a gate passed on a tree, the new test file
    in it was then staged, and the commit that shipped FAILED this very guard:
    the phrase it banned sat in a file the guard could not see, because
    `git ls-files` lists tracked files only and the file was still untracked
    when the gate ran. The gated tree and the pushed tree differed by exactly
    the visibility of that file.

    A guard has to read what is about to ship, not what already shipped, so
    the prose sweep now covers both. This is the same fault as the canvas
    guard that measured pre-layout figures: the artifact examined was not the
    artifact delivered.
    """
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--others",
         "--exclude-standard", *globs],
        capture_output=True, text=True)
    if out.returncode != 0:
        return []
    return [p for p in out.stdout.split("\n") if p]


def _prose_files() -> list[str]:
    candidates = _tracked("*.md", "*.py") + _about_to_be_tracked("*.md", "*.py")
    return [p for p in candidates
            if not p.startswith(SKIP_PREFIXES) and p not in SKIP_EXACT]


@pytest.mark.parametrize("label", sorted(FORBIDDEN))
def test_no_forbidden_phrases(label):
    pats = [re.compile(p, re.I) for p in FORBIDDEN[label]]
    hits = []
    for rel in _prose_files():
        try:
            txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.split("\n"), 1):
            for pat in pats:
                if pat.search(line):
                    hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, f"{label} in published files:\n  " + "\n  ".join(hits[:20])


def test_no_doubled_words():
    """Catches find/replace wreckage generically ('an a fixed-lock session',
    'measurement measurement', 'fixed-lock fixed-lock') rather than by
    enumerating the specific breakages of one incident.

    Scans Markdown AND Python: the first version of this check looked only at
    prose, and a later substitution pass left six ungrammatical fragments in
    shipped modules (two of which printed to stdout on every run) that it
    could not see."""
    dbl = re.compile(r"\b(\w{2,})\s+\1\b", re.I)
    # article + article ("an a fixed-lock session") and possessive + article
    # ("the session's a fixed lock") -- both are the signature of substituting
    # a noun phrase over text that already had a determiner. Checked on
    # line-JOINED text, because the real breakages straddled a line wrap.
    art = re.compile(r"\b(?:an?|the)\s+(?:an?|the)\s", re.I)
    poss = re.compile(r"\b\w+'s\s+(?:an?|the)\s", re.I)
    known_ok = {"had had", "that that"}
    # A repeated group of DIGITS is not a doubled word: instrument readouts
    # are quoted as displayed ("12.500 000 000 0 MHz"), and \w matches digits.
    digits_only = re.compile(r"^[\d\s.,]+$")
    hits = []
    for rel in _prose_files():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        lines, in_fence, kept = txt.split("\n"), False, []
        for i, line in enumerate(lines, 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence:
                kept.append((i, line))
        for idx, (i, line) in enumerate(kept):
            # Join with the following retained line so a wrapped defect is
            # seen -- but only in prose: consecutive Python statements are
            # independent, and joining them invents "matplotlib matplotlib".
            nxt = kept[idx + 1][1] if idx + 1 < len(kept) else ""
            joined = (line + " " + nxt) if rel.endswith(".md") else line
            for rx, label in ((dbl, ""), (art, " (article doubling)"),
                              (poss, " (possessive + article)")):
                for m in rx.finditer(joined):
                    frag = " ".join(m.group(0).split())
                    if frag.lower() in known_ok or digits_only.match(frag):
                        continue
                    # only report if the defect starts on THIS line
                    if m.start() < len(line):
                        hits.append(f"{rel}:{i}: '{frag}'{label}")
    assert not hits, "doubled words:\n  " + "\n  ".join(hits[:20])


# --------------------------------------------------------------------------
# 2b. Retired factual claims
# --------------------------------------------------------------------------
# "No timestamps exist anywhere" was true of what the archival analysis could
# see, and became false on 2026-07-22 when a backup carrying them surfaced. The
# unqualified form must not return: it is the premise limitation row 5 and the
# collisional chronology both rest on, and a reader who meets it will not go
# looking for the audit. The qualified forms ("no acquisition clock was
# available to the archival analysis", "no clock was available to it") are the
# supported ones.
_RETIRED_TIMESTAMP = re.compile(
    r"no timestamps? (?:exist|surviv|are available)\w*\s+(?:anywhere|at all)?|"
    r"timestamps? (?:do not|don't) exist", re.I)


# Quoting the retired claim IN ORDER TO retire it is correct and must keep
# working -- the pre-registration and any results report necessarily do it.
# Marker may sit on the following line, since prose wraps.
_RETRACTION_MARKER = re.compile(
    r"supersed|retired|no longer|corrected|was true of|already false|"
    r"stated it flatly", re.I)


def test_retired_no_timestamps_claim_stays_retired():
    hits = []
    for rel in _prose_files():
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8",
                                           errors="replace").split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if not _RETIRED_TIMESTAMP.search(line):
                continue
            scope = line + " " + (lines[i] if i < len(lines) else "")
            if not _RETRACTION_MARKER.search(scope):
                hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "the unqualified 'no timestamps exist' claim is back; a backup "
        "carrying them surfaced 2026-07-22 and is under pre-registered audit "
        "(docs/PREREGISTRATION_timestamps.md). Say what was available to the "
        "ARCHIVAL ANALYSIS instead:\n  " + "\n  ".join(hits))


# --------------------------------------------------------------------------
# 3. Names: citation context only
# --------------------------------------------------------------------------
# Names that belong in citation context and nowhere else. They are held as
# truncated digests rather than in the clear, so that enforcing the rule does
# not require this file to publish a list of people, which would be the same
# disclosure by another route. To cite one of these authors, add the citekey
# file under docs/lit/ and cite it: that path is exempt, which is exactly the
# distinction being enforced. To add a name, append the first sixteen hex
# characters of the sha256 of its lowercased form.
_NAME_DIGESTS = frozenset({
    "cc221ffa81c06c3e", "1a30ed961f81b1d8", "5bf8920cae2ee242",
    "9a2806fa28fa2490", "7008a96aa67d858a", "094a367b026246fb",
})

_WORD = re.compile(r"[A-Z][\wÀ-ÿ'’-]{1,20}")


def test_no_colleagues_named_in_process_roles():
    hits = []
    for rel in _prose_files():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(txt.split("\n"), 1):
            for word in _WORD.findall(line):
                d = hashlib.sha256(word.lower().encode()).hexdigest()[:16]
                if d in _NAME_DIGESTS:
                    hits.append(f"{rel}:{i}: {line.strip()[:90]}")
                    break
    assert not hits, (
        "a person is named in a published working document:\n  "
        + "\n  ".join(hits)
        + "\n(cite via docs/lit/ instead, which is the exempt path)"
    )


# --------------------------------------------------------------------------
# 4. Commit-message house rules (HEAD only — history is immutable)
# --------------------------------------------------------------------------
def test_head_commit_message_has_no_generated_trailers():
    msg = subprocess.run(["git", "-C", str(ROOT), "log", "-1", "--format=%B"],
                         capture_output=True, text=True)
    if msg.returncode != 0:
        pytest.skip("not a git checkout")
    body = msg.stdout
    banned = ["Co-Authored-By", "Co-authored-by", "Generated with"]
    found = [b for b in banned if b in body]
    assert not found, f"HEAD commit message contains {found}"


# --------------------------------------------------------------------------
# 5. Scope of record: pinned to the export format, not to recollection
# --------------------------------------------------------------------------
# The repo attributed the archive to a "LeCroy WaveSurfer 3104z" in six places
# (docs, constants, the CSV parser's docstrings, a QC test). It was taken on
# the Agilent/Keysight InfiniiVision DSO-X 3054A -- the LeCroy on the same
# bench would not trigger. The files settle it without needing anyone's memory:
# `x-axis,N` / `second,Volt` is the InfiniiVision CSV signature; LeCroy writes
# a different header block. This test keeps the two consistent.
# Matching any mention of "LeCroy" and excusing it on nearby context proved too
# permissive -- a planted "Scope: LeCroy WaveSurfer 3104z" was excused by the
# correct sentence two lines below it. So match the ATTRIBUTION CONSTRUCTIONS
# instead: the phrasings that name a LeCroy AS the source of the traces.
_LECROY_ATTRIB = re.compile(
    r"scope\s*[:(]\s*(?:teledyne\s+)?lecroy|"
    r"our scope \(\s*(?:teledyne\s+)?lecroy|"
    r"lecroy\s+(?:csv|export)|"
    r"read one lecroy|"
    r"(?:from|on)\s+(?:the\s+)?lecroy\s+wavesurfer", re.I)


def test_no_lecroy_attribution_for_the_archive():
    hits = []
    for rel in _prose_files():
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8",
                                           errors="replace").split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if _LECROY_ATTRIB.search(line) and not re.search(
                    r"\bnot\b|instead of|rather than", line, re.I):
                hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "the archive is attributed to a LeCroy scope; it was taken on the "
        "Agilent/Keysight InfiniiVision DSO-X 3054A (the CSV header signature "
        "`x-axis,N`/`second,Volt` proves it, and the LeCroy would not "
        "trigger):\n  " + "\n  ".join(hits))


# --------------------------------------------------------------------------
# 5. docs/lit/ notes: no reader-tailoring language
# --------------------------------------------------------------------------
# docs/lit/ is exempt from every other guard above (published titles/abstracts
# are quoted verbatim there and must not be edited to satisfy a style rule --
# see SKIP_PREFIXES). That exemption is a blind spot for anything that ISN'T
# a citation. A literature note states why a paper matters to this work, the
# same way for every reader, and must not be written for a particular reader.
# The name guard above cannot catch that, because names ARE legitimate here
# (author lists). This guards the TAILORING WORDS instead, name-independent.
_TAILORING_WORDS = re.compile(
    r"\bpitch\b|\bsell(?:s|ing)?\s+(?:to|the)\b|\bappeals?\s+to\b|"
    r"\bwould\s+resonate\b|\bfor\s+(?:the\s+)?(?:target\s+reader|PI)\b",
    re.I)


def test_lit_notes_are_not_tailored_to_a_reader():
    hits = []
    for rel in _tracked("docs/lit/*.md"):
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8",
                                           errors="replace").split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            if _TAILORING_WORDS.search(line):
                hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "a docs/lit/ note reads as tailored to one specific reader, not as "
        "a plain relevance note every reader sees the same way:\n  "
        + "\n  ".join(hits))


# --------------------------------------------------------------------------
# 6. Version bookkeeping: pyproject and CITATION.cff must agree
# --------------------------------------------------------------------------
# They diverged silently once (pyproject stale at 1.1.0 while CITATION.cff
# and the release tags advanced to 1.4.0, caught 2026-07-25) because nothing
# compared them. The release TAG is not checked here -- tagging happens after
# the version-bump commit, so requiring tag==file would make that commit
# unlandable; the release process itself aligns the tag.
def test_pyproject_and_citation_versions_agree():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    pv = re.search(r'^version = "([^"]+)"', pyproject, re.M)
    cv = re.search(r"^version: (\S+)", citation, re.M)
    assert pv and cv, "version fields missing from pyproject.toml or CITATION.cff"
    assert pv.group(1) == cv.group(1), (
        f"version drift: pyproject.toml says {pv.group(1)}, "
        f"CITATION.cff says {cv.group(1)} -- bump them together")


def _github_anchors(markdown: str) -> set[str]:
    """The anchor ids GitHub will mint for a document's headings.

    Punctuation is dropped and each surviving space becomes one hyphen -- so
    ``a — b`` yields ``a--b``, the em dash leaving its two spaces behind. A
    repeated heading gets ``-1``, ``-2``, ... appended.
    """
    import collections
    seen: collections.Counter[str] = collections.Counter()
    out: set[str] = set()
    for head in re.findall(r"^#{2,6} (.+)$", markdown, re.M):
        base = re.sub(r"[^\w\s\-]", "", head.strip().lower()).replace(" ", "-")
        out.add(base if not seen[base] else f"{base}-{seen[base]}")
        seen[base] += 1
    return out


def test_audit_addenda_are_all_reachable_from_its_toc():
    """Addenda 15 and 16 were written without TOC entries and sat unlinked.

    The audit report is long enough that an addendum missing from the
    contents is, in practice, an addendum nobody finds.
    """
    path = ROOT / "docs" / "PREREGISTRATION_RESULTS.md"
    text = path.read_text(encoding="utf-8")
    listed = set(re.findall(r"^\s*- \[([^\]]+)\]\(#[^)]+\)", text, re.M))
    missing = [
        h for h in re.findall(r"^#{2,3} ((?:Addendum|Postscript) .+)$", text, re.M)
        if h not in listed
    ]
    assert not missing, "not linked from the table of contents:\n  " + "\n  ".join(missing)


def test_audit_toc_anchors_all_resolve():
    path = ROOT / "docs" / "PREREGISTRATION_RESULTS.md"
    text = path.read_text(encoding="utf-8")
    anchors = _github_anchors(text)
    broken = [
        a for a in re.findall(r"^\s*- \[[^\]]+\]\(#([^)]+)\)", text, re.M)
        if a not in anchors
    ]
    assert not broken, "table-of-contents links that go nowhere:\n  " + "\n  ".join(broken)


def test_audit_summary_covers_the_latest_addendum():
    """The one-page summary stopped at addendum 14 while 15-17 existed.

    A reader who reads only the top of the report should not be three
    findings behind. Requiring the highest-numbered addendum to appear in
    the summary is weak enough not to force a row for every postscript, and
    strong enough to catch the drift.
    """
    path = ROOT / "docs" / "PREREGISTRATION_RESULTS.md"
    text = path.read_text(encoding="utf-8")
    numbers = [int(n) for n in re.findall(r"^## Addendum (\d+),", text, re.M)]
    assert numbers, "no addenda found -- has the report been restructured?"
    latest = max(numbers)
    # Look for the summary TABLE CELL form, "| ... | addendum N |". Matching
    # loose prose would be satisfied by the table of contents, which names
    # every addendum by construction and so can never go stale.
    # Slice at the FIRST "## Addendum" heading of any form. The first addendum
    # in this report is unnumbered ("## Addendum, 2026-07-23"), so anchoring on
    # "## Addendum 1," silently fell through to scanning the whole document --
    # which happens to pass today only because no addendum-cell appears lower
    # down, and would stop guarding the moment one did.
    first = re.search(r"^## Addendum", text, re.M)
    summary = text[:first.start()] if first else text
    cells = re.findall(r"\|\s*addend(?:um|a)\s*([\d\s,–-]+)(?:postscript)?\s*\|",
                       summary, re.I)
    covered = {int(n) for c in cells for n in re.findall(r"\d+", c)}
    assert latest in covered, (
        f"addendum {latest} has no row in the one-page summary table "
        f"(summarised: {sorted(covered)}) -- the top of the report is behind "
        "the bottom of it")


# results files git deliberately does not track -- reading one unconditionally
# in a test passes locally (the dump is lying around from a pipeline run) and
# fails in CI and on a fresh clone. This bit once, in the M17 freshness canary.
_GITIGNORED_RESULTS = ("qc_metrics.csv",)


def test_no_test_reads_a_gitignored_results_file_unconditionally():
    """A test that opens a gitignored CSV must guard it with an existence check.

    The failure mode is invisible locally: the file is present because a
    pipeline run left it there, so the suite is green on the machine that
    wrote the test and red everywhere else. Requiring an `.exists()` /
    `.is_file()` guard in the same file is a coarse check, but it is exactly
    the discipline that was missing when this bit.
    """
    offenders = []
    for path in (ROOT / "tests").glob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        for name in _GITIGNORED_RESULTS:
            if name not in text:
                continue
            guarded = (".exists()" in text or ".is_file()" in text
                       or "requires_raw_traces" in text
                       or "raw_traces_available" in text)
            if not guarded:
                offenders.append(f"{path.name} reads {name} without an existence guard")
    assert not offenders, "\n".join(offenders)


def test_module_range_glosses_are_not_stale():
    """`M0–M<n>` range glosses must not stop below the highest module.

    The audit found methods/08, __init__, a README line and a planning
    document all frozen at an old top module while M17 existed. The highest
    module is read from methods.md's pipeline line, so this tracks reality
    automatically.
    """
    methods = (ROOT / "docs" / "methods.md").read_text(encoding="utf-8")
    top = max(int(n) for n in re.findall(r"\bM(\d+)\b", methods))
    stale = []
    for path in list((ROOT / "docs").rglob("*.md")) + [ROOT / "README.md",
                                                        ROOT / "rb5s6s" / "__init__.py"]:
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"M0\s*[–-]\s*M?(\d+)", text):
            hi = int(m.group(1))
            # a range that ends below `top` is stale UNLESS it is explicitly a
            # historical/pipeline-stage range (those name the older scheme)
            line = text[max(0, m.start() - 160):m.start() + 40]
            # exempt only an EXPLICIT older-scheme marker, not any prose that
            # happens to contain "pipeline" -- "the vapour-cell pipeline (M0-M17)"
            # is a live range, "M8 outputs, the older pipeline-stage numbering"
            # is not.
            historical = re.search(r"pipeline[- ]stage|stage numbering|older"
                                   r"|historical|deprecated", line, re.I)
            if hi < top and not historical:
                stale.append(f"{path.relative_to(ROOT)}: 'M0-M{hi}' but modules run to M{top}")
    assert not stale, "\n".join(stale)


def test_every_module_code_in_methods_is_in_the_module_grid():
    """Every `M<n>` written anywhere in `docs/methods.md` must appear in the
    module grid table.

    The guard above reads the MAXIMUM code, so it cannot see a hole, and the
    grid heading writes `M0 ... M24 ...` with an ellipsis, which defeats that
    guard's range regex besides. Neither notices a module that ships, gets
    named in the script map, and never reaches the grid a reader consults.
    Membership is the check that works.

    Sub-stage codes (M4b, M4e) are deliberately outside the pattern: the word
    boundary after the digits excludes them, exactly as in the range guard.
    """
    text = (ROOT / "docs" / "methods.md").read_text(encoding="utf-8")
    grid = {int(n) for line in text.splitlines()
            if line.lstrip().startswith("|")
            for n in re.findall(r"\bM(\d+)\b", line)}
    assert grid, "no module grid table found in docs/methods.md"
    used = {int(n) for n in re.findall(r"\bM(\d+)\b", text)}
    missing = sorted(used - grid)
    assert not missing, (
        "modules named in docs/methods.md but absent from its module grid: "
        + ", ".join(f"M{n}" for n in missing)
        + ". Add a grid row for each, and widen the grid heading's range to "
          "match.")


def test_sigma_sharing_producer_does_not_overclaim():
    """The M4c sharing check is under-powered (chi2/dof ~0.2-0.6, i.e. error bars
    too large to discriminate), so its verdict is CONSISTENCY, not confirmation.
    run_sigma_laser_sharing.py once printed that the timing concern was 'answered
    POSITIVELY -- the peaks did see a common laser width' while docs/RESULTS.md
    had already walked that back to 'untested'. Producer stdout is what a reader
    running the pipeline actually sees, so it must not carry the stronger claim
    the analysis retracted."""
    src = (ROOT / "scripts" / "run_sigma_laser_sharing.py").read_text()
    banned = ["answered POSITIVELY", "is LICENSED", "did see a common laser width"]
    hits = [b for b in banned if b in src and "withdrawn" not in src.split(b)[1][:400]]
    assert not hits, f"retracted sharing claim back in the producer: {hits}"
    assert "UNDER-POWERED" in src or "under-powered" in src, \
        "the under-powered caveat must stay in the producer's finding"


def test_every_library_module_appears_in_the_methods_map():
    """A module can ship without ever being documented, and three did: the
    methods.md grid stopped at M16 while M17-M20 existed, and two library
    modules were listed under scripts/ where no such runnable exists. Check the
    map against the filesystem so the listing cannot drift behind the code."""
    import re
    mods = {p.stem for p in (ROOT / "rb5s6s").glob("*.py")
            if p.stem not in {"__init__"}}
    text = (ROOT / "docs" / "methods.md").read_text()
    block = re.search(r"^rb5s6s/(.*?)^scripts/", text, re.S | re.M)
    assert block, "could not find the rb5s6s/ block in the methods.md repository map"
    listed = set(re.findall(r"[a-z_][a-z0-9_]*", block.group(1)))
    missing = sorted(m for m in mods if m not in listed)
    assert not missing, (
        f"library modules absent from docs/methods.md's repository map: {missing}")


def test_no_tracked_artifact_schedules_the_fixed_lock_session():
    """PLAN is explicit that the follow-up session is "not scheduled", that "no
    date is assumed" and that the spec "names no operator, no dates". Four
    tracked artifacts nonetheless called it "October" -- a producer docstring,
    its stdout, the results README and a preregistration addendum -- which is a
    commitment the plan of record does not make. Keep it out."""
    import re
    offenders = []
    months = re.compile(r"\b(January|February|March|April|May|June|July|August|"
                        r"September|October|November|December)\b")
    for rel in _tracked("scripts/*.py", "rb5s6s/*.py", "results/README.md"):
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        for m in months.finditer(txt):
            line = txt[:m.start()].count("\n") + 1
            ctx = txt[max(0, m.start() - 90):m.start() + 60]
            # dated provenance notes ("fixed 2026-07-11", "July 2025 campaign")
            # are fine; a bare month naming the FUTURE session is not
            if re.search(r"\d{4}", ctx) or "campaign" in ctx.lower():
                continue
            offenders.append(f"{rel}:{line}: {m.group(0)} in {ctx[-70:]!r}")
    assert not offenders, (
        "a tracked artifact schedules the fixed-lock session; PLAN assumes no "
        "date:\n  " + "\n  ".join(offenders))


# Names whose values are NOT bit-reproducible across platforms: special
# functions and iterative solvers, where two scipy builds legitimately differ
# in the last few ulp. Plain IEEE arithmetic (add, multiply, sqrt, dot) is
# reproducible and is deliberately not listed.
_PLATFORM_SENSITIVE = {
    "ppf", "isf", "cdf", "sf", "logcdf", "logsf", "interval",
    "gammaln", "erf", "erfc", "betainc", "gammainc", "wofz", "voigt_profile",
    "minimize", "least_squares", "curve_fit", "root_scalar", "brentq",
    "quad", "solve_ivp", "eig", "eigh", "svd", "lstsq",
}
_TOLERANCE_FLOOR = 1e-9


def test_no_test_pins_a_platform_sensitive_value_below_the_floor():
    """Comparisons against special functions stay at 1e-9 or looser.

    The mirror's Linux scipy computed a Student-t quantile 1.8e-12 from the
    value the committing Mac had written into the results table, so a 1e-12
    assertion passed the local gate and failed the only CI that publishes.
    A test that pins such a value tighter than the floor is measuring which
    scipy build produced the table, not whether the number reproduces.
    Plain arithmetic is exempt because IEEE guarantees it.
    """
    offenders = []
    for path in (ROOT / "tests").glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
            tainted = set()
            for node in ast.walk(fn):
                if not isinstance(node, ast.Call):
                    continue
                called = (node.func.attr if isinstance(node.func, ast.Attribute)
                          else getattr(node.func, "id", ""))
                if called not in _PLATFORM_SENSITIVE:
                    continue
                parent = getattr(node, "_assign_targets", None)
                if parent:
                    tainted.update(parent)
            # second pass: assignment targets fed by a sensitive call
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign) and any(
                        (c.func.attr if isinstance(c.func, ast.Attribute)
                         else getattr(c.func, "id", "")) in _PLATFORM_SENSITIVE
                        for c in ast.walk(node.value) if isinstance(c, ast.Call)):
                    tainted.update(t.id for t in ast.walk(node)
                                   if isinstance(t, ast.Name)
                                   and isinstance(t.ctx, ast.Store))
            for cmp_node in [n for n in ast.walk(fn) if isinstance(n, ast.Compare)]:
                if not cmp_node.comparators:
                    continue
                rhs = cmp_node.comparators[-1]
                if not (isinstance(rhs, ast.Constant)
                        and isinstance(rhs.value, float)
                        and rhs.value < _TOLERANCE_FLOOR):
                    continue
                used = {n.id for n in ast.walk(cmp_node.left)
                        if isinstance(n, ast.Name)}
                calls = {(c.func.attr if isinstance(c.func, ast.Attribute)
                          else getattr(c.func, "id", ""))
                         for c in ast.walk(cmp_node.left) if isinstance(c, ast.Call)}
                if (used & tainted) or (calls & _PLATFORM_SENSITIVE):
                    offenders.append(
                        f"{path.name}:{cmp_node.lineno} pins a platform-sensitive "
                        f"value at {rhs.value:g}, tighter than the {_TOLERANCE_FLOOR:g} floor")
    assert not offenders, (
        "tolerance below the cross-platform floor:\n  " + "\n  ".join(offenders)
        + "\nRelax to 1e-9, or recompute both sides in the same process.")

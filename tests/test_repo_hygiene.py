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
    for rel in _shipping("*.md", "*.py", "*.toml", "*.cff", "*.yml", "*.yaml"):
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
    # A retired value printed outside docs/HISTORY.md (2026-08-16). STYLE.md
    # licenses exactly one file to print a value the record no longer believes,
    # and that rule had no mechanical backing until this entry, so it held only
    # for as long as someone remembered it. _FORBIDDEN_EXEMPT_FILES already
    # exempts HISTORY.md by name, which is why this is a label here rather than
    # a test of its own.
    #
    # THE TOKENS ARE PHRASES, NOT BARE NUMBERS, deliberately. A guard on "0.246"
    # or "800 MHz" would fire on live physics: 800 MHz is a current design
    # parameter for the running-wave arm. Each token below was checked against
    # the whole published tree when this was written and occurs ONLY in
    # HISTORY.md or nowhere, so the guard starts green with no exemptions. A
    # future hit means either a retired value came back or a token is being
    # reused for a live quantity, and the second is fixed by narrowing the
    # token, never by adding an exemption.
    "retired value outside HISTORY.md": [
        r"shares no machinery",
        r"three to eight times",
        r"1\.6 mrad",
        r"p ?= ?0\.0078",
        r"\b7/7\b",
    ],
    "drafting-process reference": [
        r"\buser(?:'s)?\b(?!name)", r"\bdigestion turn\b", r"\bas discussed\b",
        r"\bper your\b", r"\byou asked\b", r"\bas requested\b",
    ],
    # OWNER INSTRUCTION 2026-08-19. Both words import a register this record
    # does not want. "Risk" turns a stated failure mode into a mood, and its
    # honest replacements are already in use here: failure mode, what would
    # defeat the session, the objection a referee would raise, the empty case.
    # "Pitch" frames a scientific case as a sale. Legitimate technical senses
    # exist (a quoted title, a frozen preregistration record) and those lines
    # carry a term-of-art marker with a reason rather than an exemption.
    "sales and mood register": [
        r"\brisks?\b", r"\brisk(?:y|ed|ing|ier|iest)\b",
        r"\bat risk\b", r"\bpitch(?:es|ed|ing)?\b",
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
    # NAMED 2026-08-10 and NOT YET HERE, because each needs a sweep first.
    # Moving a word from that list to this bank is the last step of its
    # sweep, not the first. UPDATE 2026-08-14: the replacement terms are now
    # decided (record/dataset for the former self-description, date-based
    # session names, the experimenter/the author for the editorial voice) and
    # the sweep runs in two stages. Stage 1, DONE, renamed every tracked
    # FILENAME and code identifier off the banned stems, and the filename
    # guard below holds that. Stage 2 is the prose sweep, and the prose
    # patterns for archiv/prehistor/effort/rehears/pilot join THIS bank in
    # the same commit as that sweep, per the rule above.
    "care performed rather than exercised": [
        # Announcing an improvement over a previous, sloppier state tells a
        # reader nothing about the physics and everything about the author's
        # self-image. Owner instruction, 2026-08-13, on the retro-fraction
        # assumption: state it, say it will be measured, do not explain how
        # honest we are to flag it.
        #
        # NOT banned, and the distinction is the whole difficulty: "measured
        # rather than assumed" and "deliberately not claimed" carry real
        # content, the first a provenance and the second the difference
        # between a choice and an oversight. Only the self-regarding forms
        # are listed.
        r"rather than asserted at",
        r"now (?:carried|assumed|stated|treated)[^.]{0,40}rather than asserted",
        r"rather than hoped for",
        r"rather than quietly \w+ing",
        r"\bwe are (?:careful|honest|transparent) (?:to|about|in)",
        r"worth stating plainly rather than",
    ],
    # THE PUBLIC RECORD HAS NO ADDRESSEE (owner rule, 2026-08-21). It is a
    # self-contained scientific record, never a pitch to a named person or a
    # specific laboratory, and it must not carry unpublished lab state or
    # references to private documents. Found shipping three times in one day
    # before this bank existed ("the lab holds", "an internal scaffold",
    # "this laboratory"), fixed the same day.
    "addressee and private-state register": [
        r"the lab holds", r"our group", r"the group's",
        r"this laborator", r"internal scaffold",
        r"collaboration", r"beam[- ]time ask",
        r"class of proposal",
    ],
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
        # META-NARRATION (2026-08-20, owner). Prose that comments on the
        # document's own shape rather than stating what a section holds:
        # "N pages is too many to read in order, and the clusters below are a
        # taxonomy rather than a route. These are routes." A reference
        # document says what is in it. The X-not-Y frame is the recurring
        # carrier, so it is matched where it takes the document's own
        # structure as its subject rather than a physical claim.
        r"too many to read", r"read in order, and",
        r"(?:are|is) a taxonomy rather than",
        r"a chain, not a filing", r"these are routes",
    ],
    # APPLICANT-AWARE REGISTER (2026-08-20, owner order). A public record
    # states what is in it and lets a reader draw conclusions. Three things
    # break that. It must not frame itself as evidence ABOUT ITS AUTHOR
    # ("evaluating the author's judgement"), it must not route readers by the
    # author's private purposes ("writing a thesis chapter"), and it must not
    # leak internal shorthand for either ("the bus test", which names a
    # handover standard in the vocabulary of the people who coined it).
    #
    # Measured before it was written: seven hits across docs/wiki/README.md,
    # docs/RELEASE_CHECKLIST.md and docs/plan/01, every one of them a phrase
    # the owner named on reading the public wiki index. The patterns are
    # stored SPLIT so this file is not itself the eighth: each is assembled
    # from parts at load time, which also keeps the release-note checker,
    # which imports these banks, from flagging its own source.
    "applicant-aware register": [
        r"the " + r"author" + r"'s judg",
        r"evaluating the " + r"author",
        r"judging whether the analysis",
        r"writing a " + r"thesis" + r" chapter",
        r"\bbus[- ]" + r"test\b",
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
              "tests/test_svg_canonical.py",
              # The quantities guard forbids "tier" as a name for a
              # measurement level, so it has to write the word it forbids.
              # The specification again, for the fourth time.
              "tests/test_quantities_index_is_complete.py"}


def _shipping(*globs: str) -> list[str]:
    """What this commit would ship: tracked plus untracked-and-not-ignored.

    The union lives in `_fileset` so the four checks below and the nine other
    modules that had built it by hand cannot drift apart again (rule 19.24).
    `_tracked` stays as it is, for the one check that genuinely means TRACKED,
    namely that no private document is in the tracked set.
    """
    from _fileset import tracked_and_new
    return tracked_and_new(*globs)


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


# The one file whose SUBJECT is superseded values, so it must be able to name
# them, exactly as the protocol and the lessons file must print the vocabulary
# they govern. Exempt BY DESIGN and by name, which is different from a file
# drifting out of a guard's reach (2026-08-15, rule 19.16a).
_FORBIDDEN_EXEMPT_FILES = {"docs/HISTORY.md"}


# THE TERM-OF-ART MARKER (2026-08-19). Some banned words have a legitimate
# technical sense somewhere in this tree: a quoted literature title, a frozen
# preregistration record that must not be edited after the fact, a statistical
# term with no synonym. Distorting those to satisfy a vocabulary rule makes
# the document worse, and adding whole files to the exempt set makes the
# guard blind to everything else in them.
#
# So a SINGLE LINE may be marked, and the marker must carry a reason. Write
#     <!-- term-of-art: <why this word has to stand here> -->
# on the line itself or on the line immediately above it, in Markdown, or the
# same text in a Python comment. A bare marker with no reason does not count,
# which is the whole point: the cost of keeping the word is writing down why.
# Three ALPHABETIC words at least. Counting bare tokens let the comment's own
# closing "-->" pay for one of them, so "term-of-art: quoted block" passed on
# two real words. The reason has to read as a reason.
_MARKER = re.compile(r"term-of-art:\s*(?:[A-Za-z][\w'-]*\W+){2,}[A-Za-z][\w'-]*")


def _marked(lines, i):
    """True if a reasoned marker heads the block line i (1-based) sits in.

    The scope is the paragraph: search upward from the line until a blank one.
    Line scope was tried first and is too tight to use. A wrapped sentence can
    put the same word on two consecutive lines, and interleaving HTML comments
    inside a frozen preregistration record to satisfy a guard damages the
    record the marker exists to protect. A marker therefore heads the block it
    excuses, and stops at the blank line, so it can never quietly cover a
    whole file.
    """
    k = i - 1
    while k >= 0 and lines[k].strip():
        if _MARKER.search(lines[k]):
            return True
        k -= 1
    return False


@pytest.mark.parametrize("label", sorted(FORBIDDEN))
def test_no_forbidden_phrases(label):
    pats = [re.compile(p, re.I) for p in FORBIDDEN[label]]
    hits = []
    for rel in _prose_files():
        if rel in _FORBIDDEN_EXEMPT_FILES:
            continue
        try:
            txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = txt.split("\n")
        for i, line in enumerate(lines, 1):
            for pat in pats:
                if pat.search(line) and not _marked(lines, i):
                    hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (f"{label} in published files:\n  " + "\n  ".join(hits[:20])
                      + "\n\nIf a word genuinely has to stand, mark its line with "
                        "<!-- term-of-art: reason --> and say why.")


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
    for rel in _shipping("docs/lit/*.md"):
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
    from _fileset import tracked_and_new as _tan
    for path in [ROOT / p for p in _tan("docs/*.md", "docs/**/*.md")] + [ROOT / "README.md",
                                                        ROOT / "rb5s6s" / "__init__.py"]:
        text = path.read_text(encoding="utf-8")
        # The separator is spelled at least four ways in this tree: an en
        # dash, a hyphen, an ellipsis, and the word "to". A guard that knew
        # only the first two passed over 'M0 ... M33' in methods.md and
        # 'M1 to M30' in GLOSSARY.md while catching the en-dash form in the
        # same sweep, which is a guard reporting green on the spelling it
        # happens to know. The start is still pinned to M0 or M1 so a genuine
        # sub-range like 'M23 to M25' is not read as a gloss of the whole set.
        for m in re.finditer(r"M[01]\s*(?:[\u2013\u2014-]|\u2026|\.\.\.|\bto\b)"
                             r"\s*M?(\d+)", text):
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
    for rel in _shipping("scripts/*.py", "rb5s6s/*.py", "results/README.md"):
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        for m in months.finditer(txt):
            line = txt[:m.start()].count("\n") + 1
            ctx = txt[max(0, m.start() - 90):m.start() + 60]
            # dated provenance notes ("fixed 2026-07-11", "July 2025 campaign")
            # are fine; a bare month naming the FUTURE session is not
            if re.search(r"\d{4}", ctx) or "campaign" in ctx.lower():
                continue
            # 2026-08-14: a day number against the month is also a DATE and not
            # a schedule. The sessions are now named by date ("the 4 July
            # evening session"), which is the same dated-provenance case the
            # year test already exempts, reached by a different spelling. A
            # bare "October" still fires, which is the whole point of the rule.
            before = txt[max(0, m.start() - 12):m.start()]
            after = txt[m.end():m.end() + 12]
            if (re.search(r"\b([1-9]|[12]\d|3[01])(st|nd|rd|th)?[\s\-]+$", before)
                    or re.match(r"[\s\-]+([1-9]|[12]\d|3[01])\b", after)):
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


# --------------------------------------------------------------------------
# Filenames and identifiers carry the same vocabulary rule as prose
# --------------------------------------------------------------------------

# Stage 1 of the 2026-08-14 vocabulary sweep renamed every tracked path off
# these stems, and this guard is what stops them coming back. Prose is NOT
# checked here: that is stage 2, and its patterns join the FORBIDDEN bank
# above in the same commit as the sweep, per the rule stated there.
#
# WHY FILENAMES NEED THEIR OWN GUARD. A path is the one piece of text a
# reader meets before opening anything, it appears in every link and every
# error message, and unlike prose it cannot be softened by context. It is
# also the form the prose ratchet and the register guards never see, because
# both read file CONTENTS.
_BANNED_PATH_STEMS = (
    "archiv",       # -> record (the thing) / dataset (the data)
    "owner",        # -> the experimenter (bench) / the author (editorial)
    "prehistor",    # -> the dated session that it actually names
    "rehears",      # -> likewise: sessions are named by their date
    "quarantin",    # -> excluded
    "trouble",
    "effort",
)

# The GitHub URL of the private source repository is still literally
# `Rb-5S-6S-analysis-archive` until the owner renames it on GitHub, so a
# script that names it is stating a fact, not using the word. Same for the
# two guard files that must spell the stems to forbid them.
_PATH_STEM_EXEMPT_CONTENT = {
    "scripts/sync_public.sh",
    "tests/test_repo_hygiene.py",
    "docs/STYLE.md",
}


def test_no_tracked_path_carries_a_retired_word():
    """Filenames are the surface a reader meets first."""
    offenders = [p for p in _tracked() + _about_to_be_tracked()
                 if any(s in p.lower() for s in _BANNED_PATH_STEMS)]
    assert not offenders, (
        "tracked paths still carry retired vocabulary:\n  "
        + "\n  ".join(sorted(offenders))
        + "\nRename the path and reroute every inbound link; the replacement "
          "terms are recorded in docs/STYLE.md.")


def test_the_retired_words_are_gone_from_code_identifiers():
    """Prose is stage 2; identifiers are stage 1 and are held here.

    Checks Python and shell SOURCE for the stems in identifier position
    (a stem touching a word character on either side, e.g. `archive_dir`,
    `PREHISTORY_DIR`, `load_rehearsal`) rather than every occurrence, so
    ordinary prose inside a docstring does not fail this test before its
    own sweep lands. That split is deliberate: it lets stage 1 be guarded
    the moment it is done instead of waiting for stage 2.
    """
    import re as _re
    pat = _re.compile(
        r"(?:\w[_.]?(?:" + "|".join(_BANNED_PATH_STEMS) + r")"
        r"|(?:" + "|".join(_BANNED_PATH_STEMS) + r")\w*[_(])", _re.I)
    offenders = []
    for rel in _tracked("*.py", "*.sh") + _about_to_be_tracked("*.py", "*.sh"):
        if rel in _PATH_STEM_EXEMPT_CONTENT:
            continue
        try:
            text = (ROOT / rel).read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue                      # comments are stage 2's prose
            m = pat.search(line)
            if m:
                offenders.append(f"{rel}:{i}: {m.group(0)}")
    assert not offenders, (
        "retired vocabulary survives in code identifiers:\n  "
        + "\n  ".join(offenders[:40])
        + f"\n({len(offenders)} total). Stage 1 renamed these; see docs/STYLE.md.")


# --------------------------------------------------------------------------
# The retired beam waists
# --------------------------------------------------------------------------
#
# w0 has been re-pinned three times: a 32 um Gaussian-optics nominal, a ~50 um
# transit inference, and the adopted 64 um lineage measurement (Nieddu 2019's
# explicit 1/e^2 diameter of 128 um). Each move left statements behind that
# quoted the value of their day, and on 2026-08-14 one of them cost real time:
# a 45-70 um range that four files correctly mark as the superseded LINE-ONLY
# inference was read as a live constraint on the waist. The value is in one
# place, constants.W0_MEASURED_M, and prose that repeats a retired number
# beside a live claim is what this guard is for.
_RETIRED_WAISTS_UM = ("32", "50", "90")

# Legitimate uses of those numbers next to a waist word, each for a reason:
_WAIST_EXEMPT = {
    # frozen by the experimenter's rule: rename the file, freeze the body
    "docs/PREREGISTRATION_RESULTS.md",
    "docs/PREREGISTRATION_timestamps.md",
    # the note whose SUBJECT is the re-pin, and the chapter that narrates it
    "docs/notes/transit_width_resolved.md",
    "docs/methods/02_the_lineshape.md",
    # other groups' geometries, quoted from their papers
    "docs/lit/biraben1979.md",
    "docs/lit/perrella2013.md",
    "docs/lit/rajasree2020thesis.md",
    # the constant's own docstring, which must be able to narrate its history
    "rb5s6s/constants.py",
    # design scans that sweep a range of waists on purpose
    "scripts/run_geometry_design.py",
    # this file, which has to name the numbers to guard them
    "tests/test_repo_hygiene.py",
    # THE history file, the one place a superseded value is licensed to appear
    # (2026-08-15: history is confined there and every other page states only
    # what is live, so this guard exempts it BY DESIGN rather than by accident)
    "docs/HISTORY.md",
}


def test_no_live_claim_quotes_a_retired_waist():
    """A retired waist beside a live claim is how a stale number gets believed.

    2026-08-14: `rb5s6s/stark.py` said the inflated bound "BRACKETS the
    predicted ~0.6 MHz (w0 = 50 um)" long after the adopted waist moved to
    64 um and the prediction to 0.35, and `ramp_transit.py` illustrated a
    transit rate "at w0 = 50 um". Neither was wrong when written. Both read as
    current."""
    import re
    pat = re.compile(
        r"(w_?0|waist)\D{0,40}\b(" + "|".join(_RETIRED_WAISTS_UM) + r")\s*(um|µm)"
        r"|\b(" + "|".join(_RETIRED_WAISTS_UM) + r")\s*(um|µm)\D{0,40}(w_?0|waist)",
        re.I)
    # a line that says so is history, not a live claim. The marker may sit on
    # the neighbouring line, because prose wraps and a comment explaining a
    # past defect often opens a line above the number it is explaining, so the
    # window is three lines rather than one.
    hist = re.compile(r"(?i)retir|retract|supersed|replac|no longer|former|"
                      r"\bwas\b|old |until |before |histor|EXCLUD|disfavou|"
                      r"previous|nominal|RETIRED|inference")
    offenders = []
    for rel in _shipping("*.md", "docs/*.md", "docs/methods/*.md",
                        "docs/notes/*.md", "scripts/*.py", "rb5s6s/*.py",
                        "results/*.md"):
        if rel in _WAIST_EXEMPT or rel.endswith("_prereg.md"):
            continue
        lines = (ROOT / rel).read_text(encoding="utf-8",
                                       errors="ignore").splitlines()
        for n, line in enumerate(lines, 1):
            if not pat.search(line):
                continue
            window = " ".join(lines[max(0, n - 2):n + 1])
            if hist.search(window):
                continue
            offenders.append(f"{rel}:{n}: {line.strip()[:88]}")
    assert not offenders, (
        "a retired waist (32/50/90 um) is quoted beside a live claim. The "
        "adopted value is constants.W0_MEASURED_M = 64 um. Say that, or mark "
        "the sentence as history:\n  " + "\n  ".join(offenders[:20]))


def test_history_is_confined_to_the_history_file():
    """Superseded values live in HISTORY.md and nowhere else.

    The compromise the experimenter set on 2026-08-15, after a stale beam
    waist repeated across three forward-looking documents outvoted the one
    page that was right: keep the history, because the reason a number moved
    is often the most useful thing about it, but keep it in ONE file so no
    reader can mistake it for a live value.

    This checks the architecture rather than every number: the history file
    exists, says what it is for, is reachable from the documents that used to
    carry history, and no other document announces itself as a history table.
    """
    hist = ROOT / "docs" / "HISTORY.md"
    assert hist.is_file(), (
        "docs/HISTORY.md is missing, so superseded values have nowhere "
        "licensed to live and will scatter back into the working documents")
    text = hist.read_text(encoding="utf-8")
    assert "superseded" in text.lower(), (
        "HISTORY.md no longer says what it is for")

    # the page that used to hold the bound history must point at it, or a
    # reader following the old path finds nothing
    data = (ROOT / "docs" / "DATA.md").read_text(encoding="utf-8")
    assert "HISTORY.md" in data, (
        "docs/DATA.md no longer points at HISTORY.md, so the bound history "
        "is unreachable from where it used to live")

    # and no OTHER document may declare itself a history table
    offenders = []
    for rel in [f"docs/{q.name}" for q in (ROOT / "docs").glob("*.md")] + ["README.md"]:
        if rel == "docs/HISTORY.md":
            continue
        f = ROOT / rel
        if not f.is_file():
            continue
        body = f.read_text(encoding="utf-8").lower()
        for phrase in ("## the bound history", "# the bound history",
                       "history table is the one place"):
            if phrase in body:
                offenders.append(f"{rel}: contains {phrase!r}")
    assert not offenders, (
        "history has escaped HISTORY.md:\n  " + "\n  ".join(offenders))


# A docstring that names a function the code no longer has is stale in a way no
# phrase list can catch: the prose was true when written and the machinery moved
# underneath it. Added 2026-08-16 with the N6 sweep, which found zero hits, so
# this guard starts green and its job is to keep it that way.
def test_a_docstring_names_no_identifier_the_tree_lacks():
    """A docstring that writes `name()` claims a callable of that name exists.

    ONLY THE CALL FORM IS CHECKED, and that narrowing is the whole design. A
    bare backquoted word in this repository is as likely to be a CSV column, a
    module basename, a directory, a status label or a literature key as an
    identifier: the first version of this guard checked those too and returned
    39 hits, every one a false positive. Trailing parentheses are the one
    unambiguous claim that something is callable.

    The haystack is what the tree DEFINES or IMPORTS, never its raw text, since
    a docstring is part of the source of its own file and searching the text
    makes the test vacuous. Both failure modes were found by planting, not by
    reading (2026-08-16).
    """
    import ast

    files = [p for r in ("rb5s6s", "scripts", "tests")
             for p in (ROOT / r).rglob("*.py")]
    src = {p: p.read_text(encoding="utf-8", errors="replace") for p in files}

    # The haystack is what the tree DEFINES or IMPORTS, never its raw text.
    # Searching the raw text makes this test vacuous, since a docstring is part
    # of the source of the file that contains it, so every name it mentions is
    # trivially "present". Caught by planting a fake name and watching the
    # first version of this guard pass (2026-08-16).
    known: set[str] = set()
    for text in src.values():
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
                known.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                known.add(node.id)
            elif isinstance(node, ast.arg):
                known.add(node.arg)
            elif isinstance(node, ast.Attribute):
                known.add(node.attr)
            elif isinstance(node, ast.keyword) and node.arg:
                known.add(node.arg)
            elif isinstance(node, ast.alias):
                known.add((node.asname or node.name).split(".")[0])
    bad = set()
    for path, text in src.items():
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Module, ast.FunctionDef,
                                     ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            doc = ast.get_docstring(node)
            if not doc:
                continue
            for tok in re.findall(r"`([A-Za-z_][A-Za-z0-9_]{3,})\(\)`", doc):
                if tok not in known:
                    bad.add(f"{path.relative_to(ROOT)}: `{tok}`")
    assert not bad, ("a docstring names an identifier the tree does not "
                     "contain:\n  " + "\n  ".join(sorted(bad)))

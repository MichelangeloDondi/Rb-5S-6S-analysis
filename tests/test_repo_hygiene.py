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
PRIVATE_GLOBS = ["docs/brief_*", "docs/*audit*", "docs/*red_team*",
                 "docs/CV_*", "docs/*inquiry*", "docs/linkedin*", "*.docx",
                 # publication-strategy planning: process, unpublished
                 # 2026-07-23 (Sile/Brion/Lan would read plans about their
                 # own labs/roles that were never agreed with them)
                 "docs/PAPERS_PORTFOLIO.md"]
# docs/reference_setup/ is deliberately NOT listed: its lab photos are already
# excluded by their own .gitignore rule (they carry equipment serials and a
# name), while whether the notes alongside them are published is an open
# decision. Blanket-ignoring the directory would silently settle it, and would
# also defeat the negation that keeps the placeholder file addable.


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
    "aphoristic register": [
        r"is itself an?\b", r"is itself the\b",
        r"a test passed, not a tuning", r"the honest headline",
        r"the honest through-line", r"not a hedge but",
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
              "tests/test_lit_consistency.py"}


def _prose_files() -> list[str]:
    return [p for p in _tracked("*.md", "*.py")
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
# Surnames that must not appear in the published tree in a process role.
# To cite one of these authors, add the citekey file under docs/lit/ and cite
# it — that path is exempt, which is exactly the distinction being enforced.
PROCESS_NAMES = [r"\bZohreh\b", r"\bEtienne\b", r"\bSíle\b", r"\bSile\b"]


def test_no_colleagues_named_in_process_roles():
    pats = [re.compile(p) for p in PROCESS_NAMES]
    hits = []
    for rel in _prose_files():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(txt.split("\n"), 1):
            for pat in pats:
                if pat.search(line):
                    hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "colleague named in a published working document:\n  "
        + "\n  ".join(hits)
        + "\n(roles are for the people involved to agree; cite via docs/lit/ instead)"
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

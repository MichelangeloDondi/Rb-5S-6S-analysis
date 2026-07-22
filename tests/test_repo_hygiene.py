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
                 "docs/CV_*", "docs/*inquiry*", "docs/linkedin*", "*.docx"]
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
        r"is itself a result", r"is itself the central",
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
    enumerating the specific breakages of one incident."""
    dbl = re.compile(r"\b(\w{2,})\s+\1\b", re.I)
    known_ok = {"had had", "that that"}
    hits = []
    for rel in _prose_files():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        in_fence = False
        for i, line in enumerate(txt.split("\n"), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in dbl.finditer(line):
                if m.group(0).lower() not in known_ok:
                    hits.append(f"{rel}:{i}: '{m.group(0)}'")
    assert not hits, "doubled words:\n  " + "\n  ".join(hits[:20])


# --------------------------------------------------------------------------
# 3. Names: citation context only
# --------------------------------------------------------------------------
# Surnames that must not appear in the published tree in a process role.
# To cite one of these authors, add the citekey file under docs/lit/ and cite
# it — that path is exempt, which is exactly the distinction being enforced.
PROCESS_NAMES = [r"\bZohreh\b", r"\bEtienne\b"]


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

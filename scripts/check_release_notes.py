#!/usr/bin/env python3
"""Check a release body against the same rules the tracked documents obey.

    python scripts/check_release_notes.py NOTES.md

WHY THIS EXISTS. On 2026-08-09 two published release bodies were found carrying
raw mathematics: `cm$^{-3}$` and `$\\pm$0.0043` rendered as source on the
release page, inside the paragraph that explained the rendering rule. The guard
added the same night checks every tracked markdown file and passed, because a
release body is not a tracked file. It is pasted into an API, so it lives
outside the repository and outside every check the repository owns.

The lesson recorded then was to ask, of any mechanised rule, what surface the
mechanism cannot reach. For this project those surfaces are release notes,
commit messages, the profile fields and anything pasted into a web form. This
script closes the first of them by importing the rules rather than restating
them, so a bank extended in the test suite is extended here at the same moment.

What it checks, all of it borrowed:

* the FORBIDDEN banks of tests/test_repo_hygiene.py, which is where the
  internal-process vocabulary and the aphoristic register live
* the GitHub inline-math adjacency rule of tests/test_docs_math_render.py,
  measured against GitHub's own renderer rather than assumed
* the house punctuation rule, no em-dashes and no semicolons
* the release-note style rules' mechanical half (docs/RELEASE_NOTE_STYLE.md,
  2026-08-26, written after a reading of every published note): a
  refusal ceiling on the body, no internal shorthand codes
  outside file paths, and the narrative-register markers that reading
  measured in every published note. Passing `--self-check` skips these
  three, for the protocol-file self-audits of LOGIC 17.3, whose subjects
  are long by design and quote the register they ban.

Exit status is 1 on any finding, 2 on usage, 3 when a required rule bank
cannot be loaded, so a checker that lost its rules can never report clean.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))


def _load_rules():
    """Import the banks from the test modules, so there is one definition.

    THE FILLER BANK WAS MISSING UNTIL THE BOARD'S THIRD CONVENING. This
    guard imported only test_repo_hygiene.FORBIDDEN, so the zero-cost
    filler list and the vague-judgement ban, both of which exist BECAUSE of
    a release note, were invisible to the one checker release notes get.
    They are pulled in here by name.
    """
    from test_repo_hygiene import FORBIDDEN
    banks = {label: [re.compile(p, re.I) for p in pats]
             for label, pats in FORBIDDEN.items()}
    # A failed import here once left the filler bank silently missing and
    # the checker printing clean, so a missing bank is now a hard stop
    # (exit 3 in main) and never a pass.
    import test_prose_style_ratchet as _r
    extra = [re.escape(w) for w in _r.FILLER_PHRASES]
    extra.append(_r.VAGUE_JUDGEMENT.pattern)
    banks["filler and vague judgement"] = [
        re.compile(rf"\b{p}\b" if not p.startswith("\\b") else p, re.I)
        for p in extra]
    math_checks = None
    try:
        import test_docs_math_render as m
        for name in ("_math_problems", "math_problems", "_problems"):
            if hasattr(m, name):
                math_checks = getattr(m, name)
                break
    except Exception:
        pass
    return banks, math_checks


def _fallback_math(text: str) -> list[str]:
    """The adjacency rule, restated only if the test module exposes no helper.

    A `$...$` span opens only when the character before the opening `$` is
    line-start, whitespace, `(` or `*`, and closes only when the character
    after is not alphanumeric. `<` and `>` inside math are entity-escaped
    before the math pass and can never render.
    """
    out = []
    fenced = False
    for i, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        # Inline code spans are quoted source, and GitHub renders no math inside
        # one, so a `cm$^{-3}$` written as an example of the defect is correct
        # usage. Strip the spans before looking. Found 2026-08-09 by running this
        # script on the rendering protocol, whose whole job is to quote the
        # broken forms: it reported nine defects that were all worked examples.
        line = re.sub(r"`[^`]*`", "", line)
        for m in re.finditer(r"(?<!\\)\$([^$\n]{1,200}?)(?<!\\)\$", line):
            before = line[m.start() - 1] if m.start() else " "
            after = line[m.end()] if m.end() < len(line) else " "
            if before not in " \t([*" and m.start():
                out.append(f"{i}: {before!r} sits before the opening $ of "
                           f"{m.group(0)[:34]!r}, so the span stays raw")
            if after.isalnum():
                out.append(f"{i}: {after!r} follows the closing $ of "
                           f"{m.group(0)[:34]!r}, so the span stays raw")
            if "<" in m.group(1) or ">" in m.group(1):
                out.append(f"{i}: angle bracket inside {m.group(0)[:34]!r}; "
                           "use \\lt and \\gt")
    return out


# The style rules' mechanical half (docs/RELEASE_NOTE_STYLE.md). The word
# ceiling is the refusal level and the target is 300. The code pattern
# spares file paths (results/kernel_k4.csv stays citable) by refusing only
# codes that stand as their own word outside a path or code span, and it
# spares physics vocabulary that shares the shape: "the M1 transition" and
# "the C3 dispersion coefficient" name multipoles and dispersion physics,
# recognised when any of the next three words names the physics.
# THE RULE SAYS 300 AND THIS REFUSED AT 400, so a note already breaching the
# stated rule passed the checker written for it. N2 has TWO numbers and they
# are not the same one: a body "stays at or under 300 words" and the checker
# "refuses above 400". An edit earlier on 2026-08-28 collapsed them, so the
# checker refused at the target and left no band between advice and refusal.
WORD_CEILING = 400
WORD_TARGET = 300
_CODE = re.compile(r"(?<![\w/.-])([MCKP]\d{1,2}[a-z]?)(?![\w/.-])")
_PHYSICS_NEXT = ("transition", "coefficient", "multipole", "admixture",
                 "dispersion")
# Register markers measured 2026-08-26 in every published note. Literal phrases, kept few and unambiguous so a false
# positive is nearly impossible. The voice reader carries the
# semantic half.
NARRATIVE_MARKERS = [
    "two things happened",
    "which is exactly",
    "which is precisely",
    "the story",
    "not a claim, a measurement",
    "survives and sharpens",
    "interrogated to exhaustion",
    "and that is a result",
    "and that is the recommendation",
]


def _paragraphs(text: str, strip_code: bool = True) -> list[tuple[int, str]]:
    """(start_line, flattened prose) per paragraph, code fences skipped,
    inline code spans stripped, bullets treated as their own paragraphs.

    Every content pattern in this file matches against the FLATTENED
    paragraph, never a physical line. A banned phrase spanning a hard
    line wrap defeated a per-line guard on a public page once before, and
    the first version of this function's callers repeated the class on
    the day they were written: a wrapped "M1 / transition" pair defeated
    the physics allowance, and a wrapped banned phrase passed unseen.
    """
    out: list[tuple[int, str]] = []
    fenced = False
    buf: list[str] = []
    start = 0
    for i, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        bullet = bool(re.match(r"\s*[*-]\s", line))
        if fenced or not line.strip() or bullet:
            if buf:
                out.append((start, " ".join(buf)))
                buf = []
            if fenced or not line.strip():
                continue
        cleaned = (re.sub(r"`[^`]*`", "", line) if strip_code else line).strip()
        if not buf:
            start = i
        buf.append(cleaned)
    if buf:
        out.append((start, " ".join(buf)))
    return out


# N3'S MECHANISM, added 2026-08-28 after the owner said the withdrawn v4.3 and
# v4.4
# notes failed "mainly because the physics was wrong and/or confused". Every
# rule above this one is about REGISTER, and a reading of those notes found
# ten physics defects, seven of them unreachable by any register rule: a
# waist no producer computes, a bound divided by a point prediction, a null
# reported as a size. What they share is that no number named where it lives.
#
# THIS IS NOT A NEW RULE AND MUST NOT BECOME ONE. N3 already says every
# number names its committed file in the same sentence, and it had no
# mechanism, so the first draft of this check invented a sibling N12 for a
# rule that existed. The ceiling rule refuses exactly that: a defect an
# existing rule already covers is evidence for MECHANISING that rule, never
# for adding another beside it.
#
# The check is the weakest mechanical form of N3 that would have fired on the
# withdrawn notes: a paragraph stating a quantity in a physical unit also
# names a source. The unit list keeps the population tight -- a bare integer
# is a count, a version or a date, and is not N3's business.
_UNITED = re.compile(
    r"(?<![\w.])\d+(?:\.\d+)?\s*"
    r"(?:MHz|kHz|GHz|Hz|nm|um|µm|mm|mW|W|a\.u\.|atomic units|sigma|σ)\b")
# A citation is a tracked path, a results row key, or a markdown link. The
# note may also discharge one by naming the producer that makes the number.
_CITED = re.compile(
    r"`[\w./-]+\.(?:csv|py|md)`|\]\([^)]+\)|results/|scripts/run_")


def _uncited_quantities(paragraphs: list[tuple[int, str]]) -> list[str]:
    """N3, mechanised. A paragraph quoting a united quantity names its source.

    Fails when a release body states a physical quantity and the paragraph
    carries no path, no results row and no link -- the shape every one of
    the withdrawn notes' physics defects had in common.
    """
    out = []
    for ln, flat in paragraphs:
        hits = [m.group(0).strip() for m in _UNITED.finditer(flat)]
        if not hits or _CITED.search(flat):
            continue
        quoted = ", ".join(sorted(set(hits)))
        out.append(f"[style N3] paragraph at line {ln}: quantity "
                   f"{quoted} with no committed row, producer or link: "
                   f"{flat[:64]}")
    return out


_TEXT: list[str] = [""]


def _protocol_findings(paragraphs: list[tuple[int, str]],
                       n_words: int) -> list[str]:
    out = []
    if n_words > WORD_CEILING:
        out.append(f"[style N2] body is {n_words} words against the "
                   f"{WORD_CEILING}-word refusal ceiling (target {WORD_TARGET})")
    elif n_words > WORD_TARGET:
        print(f"  check_release_notes: ADVISORY, {n_words} words against "
              f"N2's {WORD_TARGET}-word target (refusal is {WORD_CEILING})")
    for ln, flat in paragraphs:
        for m in _CODE.finditer(flat):
            following = re.findall(r"[A-Za-z-]+", flat[m.end():])[:3]
            if any(w.lower() in _PHYSICS_NEXT for w in following):
                continue
            out.append(f"[style N4] paragraph at line {ln}: internal code "
                       f"{m.group(0)!r} outside a file path: {flat[:70]}")
        low = flat.lower()
        for phrase in NARRATIVE_MARKERS:
            if phrase in low:
                out.append(f"[style N7] paragraph at line {ln}: register "
                           f"marker {phrase!r}: {flat[:70]}")
    # N3 reads paragraphs with the code spans KEPT. The default strip is
    # right for the register banks, which must not flag a banned word inside
    # a quoted path, and it is fatal here: a citation in this house IS a
    # backticked path, so the first draft of this check could never see one
    # and fired on every paragraph that obeyed the rule.
    out.extend(_uncited_quantities(_paragraphs(_TEXT[0], strip_code=False)))
    return out


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--self-check"]
    self_check = "--self-check" in argv[1:]
    if len(args) != 1:
        print(__doc__.strip().split("\n")[2].strip())
        return 2
    path = Path(args[0])
    if not path.exists():
        print(f"check_release_notes: no such file: {path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        banks, math_helper = _load_rules()
    except Exception as exc:
        print(f"check_release_notes: a required rule bank failed to load "
              f"({type(exc).__name__}: {exc}), refusing to report clean")
        return 3

    findings: list[str] = []

    paragraphs = _paragraphs(text)
    for label, pats in sorted(banks.items()):
        for ln, flat in paragraphs:
            for pat in pats:
                if pat.search(flat):
                    findings.append(f"[{label}] paragraph at line {ln}: "
                                    f"{flat[:88]}")

    # The test module exposes no callable helper on this tree, so the
    # restated rule below is the one that runs. math_helper is kept so a
    # future helper is picked up here the day it exists.
    del math_helper
    for problem in _fallback_math(text):
        findings.append(f"[math would render as source] {problem}")

    for i, line in enumerate(text.split("\n"), 1):
        if "—" in line:
            findings.append(f"[punctuation] {i}: em-dash: {line.strip()[:80]}")
        # The indent test reads the RAW line: an lstrip()ed line can never
        # start with whitespace, which made the first version's exemption
        # for indented code unreachable.
        if (";" in line and not line.startswith(("    ", "\t"))
                and not line.lstrip().startswith("```")):
            findings.append(f"[punctuation] {i}: semicolon: {line.strip()[:80]}")

    if not self_check:
        _TEXT[0] = text
        findings.extend(_protocol_findings(paragraphs, len(text.split())))

    if findings:
        print(f"check_release_notes: FAIL, {len(findings)} finding(s) in {path}\n")
        for f in findings:
            print(f"  {f}")
        print("\n  A release body is not a tracked file, so nothing else checks it.")
        return 1

    n = len(text.split())
    print(f"check_release_notes: clean ({n} words, {path.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

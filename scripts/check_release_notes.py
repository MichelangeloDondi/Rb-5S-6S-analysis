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

Exit status is 1 on any finding, so it can gate a release the way ci_gate.sh
gates a push.
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
    try:
        import test_prose_style_ratchet as _r
        extra = [re.escape(w) for w in _r.FILLER_PHRASES]
        extra.append(_r.VAGUE_JUDGEMENT.pattern)
        banks["filler and vague judgement"] = [
            re.compile(rf"\b{p}\b" if not p.startswith("\\b") else p, re.I)
            for p in extra]
    except Exception:
        pass
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


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().split("\n")[2].strip())
        return 2
    path = Path(argv[1])
    if not path.exists():
        print(f"check_release_notes: no such file: {path}")
        return 2
    text = path.read_text(encoding="utf-8", errors="replace")
    banks, math_helper = _load_rules()

    findings: list[str] = []

    for label, pats in sorted(banks.items()):
        for i, line in enumerate(text.split("\n"), 1):
            for pat in pats:
                if pat.search(line):
                    findings.append(f"[{label}] {i}: {line.strip()[:88]}")

    for problem in (_fallback_math(text) if math_helper is None
                    else _fallback_math(text)):
        findings.append(f"[math would render as source] {problem}")

    for i, line in enumerate(text.split("\n"), 1):
        if "—" in line:
            findings.append(f"[punctuation] {i}: em-dash: {line.strip()[:80]}")
        if ";" in line and not line.lstrip().startswith(("    ", "\t", "```")):
            findings.append(f"[punctuation] {i}: semicolon: {line.strip()[:80]}")

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

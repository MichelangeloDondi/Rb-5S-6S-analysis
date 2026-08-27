"""Every bold span in tracked prose opens and closes.

WHY THIS EXISTS, and it is a genuinely new class rather than a sibling of an
existing guard. On 2026-08-27 a correction wave left an unclosed `**` in the
flagship case page and, after the repair, another in the generated results
ledger. The consequence is not cosmetic: an odd count inverts the open/close
role of EVERY bold span from that point to the end of the document, so a page
renders with the wrong words emphasised and, on the case page, with the
sentence stating the record's central claim broken in half.

WHAT ALREADY EXISTED AND COULD NOT SEE IT, checked before this file was
written rather than assumed:

  * `test_docs_no_duplicated_blocks.py` flags four or more identical repeated
    LINES. The defect was a few duplicated words across a line break.
  * `test_prose_style_ratchet.py` counts em-dashes, semicolons, constructions
    and emphasis capitals. None of those is a delimiter.
  * `test_reader_surface_budget.py` counts words, and a duplicated word does
    not move a budget measurably.
  * `test_docs_math_render.py` is the nearest relative, and it is about `$`
    spans and GitHub's math renderer, not about `**`.

So four guards were in the area and the defect went through all four, twice.

THE TWO BLIND REGIONS, both stated because a guard's zero is only worth what its
population is. FIRST, this counts `**` and tests PARITY, so two independent
unclosed spans in one file sum to an even total and pass. Parity is what
catches the defect this was written for, a single stray delimiter, and it is
not a general balance check. SECOND, the false positive below.

ONE FALSE POSITIVE TO AVOID. A fenced Python block containing a power
operator, `x ** 2`, contributes bold tokens that are not markup. Fences are
stripped before counting, which is also why the count is taken per file and
not per line: a bold span may legitimately wrap across lines.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_FENCE = re.compile(r"```.*?```", re.S)
_INLINE_CODE = re.compile(r"`[^`\n]*`")


def _tracked_markdown() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md"],
        capture_output=True, text=True)
    return out.stdout.split()


def _bold_tokens(text: str) -> int:
    """Bold delimiters outside code, where `** 2` is arithmetic and not markup."""
    text = _FENCE.sub(" ", text)
    text = _INLINE_CODE.sub(" ", text)
    return len(re.findall(r"\*\*", text))


def test_every_bold_span_closes():
    odd = []
    for rel in _tracked_markdown():
        path = ROOT / rel
        if not path.exists():
            continue
        n = _bold_tokens(path.read_text(encoding="utf-8"))
        if n % 2:
            odd.append(f"{rel}: {n} bold delimiters, which is odd, so one "
                       f"span never closes and every bold run after it "
                       f"renders inverted")
    assert not odd, (
        "unclosed bold spans in tracked prose:\n  " + "\n  ".join(odd))

"""W1 GUARD DRAFT (lands in tests/ with W1's first floor): a markdown table row
with MORE cells than its header is refused.

The README's mechanism table shipped a row with an extra pipe on 2026-09-12 and
GitHub rendered the row with its last cell dropped: the front page's "lifted by"
column read "calculated". `test_table_rows_are_single_lines` disclaims
pipe-count equality because a trailing pipe or a code span false-fires it; the
narrowed form here counts cells the way GFM does (strip one leading and one
trailing pipe, split on pipes outside backticks) and refuses only a row LONGER
than its header, which neither false-fire produces. Plant: a synthetic row
with an extra pipe fails, the same row without it passes, a row with a pipe
inside a code span passes.
"""
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def _cells(row: str) -> int:
    body = row.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    body = re.sub(r"`[^`]*`", "code", body)          # pipes inside code spans are not cell breaks
    body = body.replace("\\|", "escaped")
    return len(body.split("|"))

def _tables(text: str):
    lines = text.split("\n")
    i = 0
    while i < len(lines) - 1:
        if lines[i].lstrip().startswith("|") and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            header = _cells(lines[i]); j = i + 2
            while j < len(lines) and lines[j].lstrip().startswith("|"):
                yield i + 1, header, j + 1, _cells(lines[j]); j += 1
            i = j
        else:
            i += 1

def overlong_rows(path: Path) -> list[str]:
    return [f"{path}:{row} has {n} cells against a header of {h} (header line {hl})"
            for hl, h, row, n in _tables(path.read_text()) if n > h]

def test_no_tracked_table_row_is_longer_than_its_header():
    files = subprocess.check_output(["git", "ls-files", "*.md"], cwd=ROOT).decode().split()
    bad = [b for f in files for b in overlong_rows(ROOT / f)]
    assert not bad, "a table row longer than its header renders with its last cells dropped:\n  " + "\n  ".join(bad)

def test_the_guard_fires_on_the_extra_pipe_and_not_on_a_code_span(tmp_path):
    good = "| a | b |\n|---|---|\n| 1 | `x|y` |\n| 2 | 3 |\n"
    bad = "| a | b |\n|---|---|\n| 1 || 2 |\n"
    (tmp_path / "g.md").write_text(good); (tmp_path / "b.md").write_text(bad)
    assert overlong_rows(tmp_path / "g.md") == []
    assert len(overlong_rows(tmp_path / "b.md")) == 1

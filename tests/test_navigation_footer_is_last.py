"""A page's navigation footer is its last line, on every tracked page that has one.

A plan chapter once shipped with 41 lines below its footer, so a reader who
followed its next-page link never reached them. The population is found,
never listed: a navigation line is the wiki's arrow form (`[← ...](...)`) or
the chapters' italic form with a middot between links, past the page's first
five lines (the wiki's line-three breadcrumb is not a footer). The last such
line must be the page's last non-empty line, and a page with two is refused,
since a second footer below stranded content is the escape's own shape. The
complement is asserted: no page outside the population ends in a line that
looks like a footer by a looser test. Every plan and big-picture chapter must
carry one, so a chapter cannot leave the population by dropping its footer,
and the population's size is asserted so a failed `git ls-files` cannot pass
as an empty green.
"""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARROW = re.compile(r"^\[←[^\n]*\]\([^\n]*\)")
ITALIC = re.compile(r"^\*\[[^\n]*\]\([^\n]*\)[^\n]* · [^\n]*\*\s*$")
LOOSE = re.compile(r"^\*?\[[^\]]*\]\([^)]*\.md[^)]*\).*(·|→)")
HEADER_LINES = 5


def _ls(*patterns):
    r = subprocess.run(["git", "-C", str(ROOT), "ls-files", *patterns],
                       capture_output=True, text=True, check=True)
    return r.stdout.split()


def is_footer_line(line):
    return bool(ARROW.match(line) or ITALIC.match(line))


def footer_lines(lines):
    """Indices of navigation lines past the header."""
    return [i for i, line in enumerate(lines) if i >= HEADER_LINES and is_footer_line(line)]


def gap_below(lines):
    """None with no footer; -1 with more than one; else the non-empty lines below it."""
    idx = footer_lines(lines)
    if not idx:
        return None
    if len(idx) > 1:
        return -1
    return len([line for line in lines[idx[0] + 1:] if line.strip()])


def _lines(rel):
    return (ROOT / rel).read_text(encoding="utf-8").split("\n")


PAGES = _ls("*.md")
POPULATION = [p for p in PAGES if footer_lines(_lines(p))]
CHAPTERS = _ls("docs/plan/*.md", "docs/big_picture/*.md")


def test_the_population_is_not_empty():
    assert len(PAGES) > 100 and len(POPULATION) > 50 and len(CHAPTERS) > 10


@pytest.mark.parametrize("rel", POPULATION)
def test_the_footer_is_the_last_line(rel):
    gap = gap_below(_lines(rel))
    assert gap != -1, f"{rel}: two footers; content sits between them, move the first one down"
    assert gap == 0, f"{rel}: {gap} non-empty line(s) sit below the navigation footer; move the footer to the end"


@pytest.mark.parametrize("rel", CHAPTERS)
def test_every_chapter_carries_a_footer(rel):
    assert footer_lines(_lines(rel)), f"{rel} carries no navigation footer, so its reader has no way on"


def test_the_complement_is_empty():
    """The pages the predicate rejects must not end in a footer by a looser
    test: a discovery that cannot list what it excluded is a hand list."""
    stray = []
    for rel in PAGES:
        if rel in POPULATION:
            continue
        tail = [line for line in _lines(rel) if line.strip()][-3:]
        if any(LOOSE.search(line) for line in tail):
            stray.append(rel)
    assert not stray, f"pages ending in a footer-shaped line the predicate rejects: {stray}"


def test_the_guard_fires_on_the_escape_shape():
    pad = ["# x", "", "text", "", "more", ""]
    base = pad + ["---", "", "*[a](a.md) · [b](b.md)*"]
    assert gap_below(base) == 0
    assert gap_below(base + ["", "orphan"]) == 1
    assert gap_below(base + ["", "orphan", "", "*[a](a.md) · [b](b.md)*"]) == -1
    assert gap_below(base + ["", "orphan", "", "*[Figure 3](../figures/f.png) shows it*"]) == 2   # the aside is not a footer, so it counts as content below
    assert gap_below(pad + ["[← prev](p.md) · [next →](n.md)"]) == 0
    assert gap_below(pad + ["[← prev](p.md) · [next →](n.md)", "", "orphan"]) == 1
    wiki = ["# page", "", "[← wiki index](README.md) · *A, 1 of 9* · [Next →](n.md)", "", "text", "", "---", "", "[← Prev](p.md) · *A, 1 of 9* · [Next →](n.md)"]
    assert footer_lines(wiki) == [8] and gap_below(wiki) == 0
    assert gap_below(["# bare", "", "text"]) is None

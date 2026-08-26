"""Every wiki page is linked from the wiki index, and every link has a page.

The same failure the results index had: an index is written when a directory
is tidied and not when a file is added, so it drifts one page at a time and
nothing says so. A page nobody can reach from the index is a page nobody
reads, and an index entry with no page is worse, because it survives a
deletion and sends a reader looking for something that is not there.

`test_docs_links` already checks that a link RESOLVES. This checks the other
direction, that a page is REACHED, which no link checker can see.

The count is printed on every run rather than only on failure. A guard that
finds its subject by pattern has to show what it found, because passing on
the wrong subject looks exactly like passing on the right one.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WIKI = ROOT / "docs" / "wiki"
INDEX = WIKI / "README.md"


def _pages():
    return {p.name for p in WIKI.glob("*.md") if p.name != "README.md"}


def _linked(text):
    return set(re.findall(r"\]\((?!\.\./|https?:)([A-Za-z0-9_-]+\.md)\)", text))


def test_every_wiki_page_is_linked_from_the_index(capsys):
    pages = _pages()
    linked = _linked(INDEX.read_text(encoding="utf-8"))
    with capsys.disabled():
        print(f"\n  wiki index: {len(pages)} pages on disk, "
              f"{len(linked)} linked from README.md")
    missing = sorted(pages - linked)
    assert not missing, (
        "these wiki pages exist but nothing in docs/wiki/README.md links to "
        "them, so a reader arriving at the index cannot find them:\n  "
        + "\n  ".join(missing))


def test_every_index_entry_has_a_page():
    dangling = sorted(_linked(INDEX.read_text(encoding="utf-8")) - _pages())
    assert not dangling, (
        "docs/wiki/README.md links to these pages and they do not exist:\n  "
        + "\n  ".join(dangling))


def test_every_wiki_panel_has_a_producer():
    """A committed teaching panel is reproducible or it is not committed.

    The result gallery has this guard for figures/; docs/wiki/figures/ is
    outside its glob, so it needs its own. Same rule, same reason: a PNG
    nobody can redraw is a number nobody can check.
    """
    src = (ROOT / "scripts" / "make_wiki_figures.py").read_text(
        encoding="utf-8")
    saved = set(re.findall(r'_save\(fig,\s*"([^"]+\.png)"', src))
    committed = {p.name for p in (WIKI / "figures").glob("*.png")}
    orphans = sorted(committed - saved)
    assert not orphans, (
        "these wiki panels are committed with no _save call in "
        "scripts/make_wiki_figures.py, so nothing reproduces them:\n  "
        + "\n  ".join(orphans))


def test_the_page_navigation_follows_the_index_order():
    """Prev/next on each page matches the order the index actually lists.

    The methods chapters carry this navigation and the wiki did not, so a
    reader arriving on one page could not walk the cluster. Hand-written
    links would drift from the index the first time a page moved, so the
    expected order is DERIVED from docs/wiki/README.md here and compared
    against what the pages say. Reorder the index and this test tells you
    which pages disagree with it.
    """
    text = INDEX.read_text(encoding="utf-8")
    clusters, current = {}, None
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("## Planned"):
            current = line[3:].strip()
            # any single-letter cluster prefix. The list was A to D until the
            # wiki grew a fifth cluster on 2026-08-16, at which point a
            # hard-coded list silently stopped stripping and the position
            # lines disagreed with themselves.
            if re.match(r"^[A-Z]\.\s", current):
                current = current[2:].strip()
            clusters[current] = []
        elif current and line.startswith("| ["):
            m = re.match(r"\| \[[^\]]+\]\(([a-z0-9-]+)\.md\)", line)
            if m:
                clusters[current].append(m.group(1))
    clusters = {k: v for k, v in clusters.items() if v}
    assert clusters, "no clusters parsed from the index"

    bad = []
    for cluster, pages in clusters.items():
        for i, slug in enumerate(pages):
            body = (WIKI / f"{slug}.md").read_text(encoding="utf-8")
            tail = body.rsplit("---", 1)[-1]
            want_prev = f"({pages[i-1]}.md)" if i else "(README.md)"
            want_next = (f"({pages[i+1]}.md)" if i + 1 < len(pages)
                         else "(README.md)")
            where = f"{cluster}, {i+1} of {len(pages)}"
            if want_prev not in tail:
                bad.append(f"{slug}: previous link should point at {want_prev}")
            if want_next not in tail:
                bad.append(f"{slug}: next link should point at {want_next}")
            if where not in tail:
                bad.append(f"{slug}: position should read {where!r}")
    assert not bad, ("page navigation disagrees with the order in "
                     "docs/wiki/README.md:\n  " + "\n  ".join(bad))

_WORDS = {
    # The correction count fell to the small integers on 2026-08-26, when the
    # corrections moved out of the pages and into docs/HISTORY.md where the
    # history protocol puts them. A map that only spans the counts of the
    # day it was written turns a real improvement into a guard failure.
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "forty-nine": 49, "fifty": 50, "fifty-one": 51,
    "fifty-two": 52, "fifty-three": 53, "fifty-four": 54, "fifty-five": 55,
}

# A correction section says where THIS project got the concept wrong. "What can go
# wrong" is the generic hazard section every page carries and is not one.
#
# "Values that moved" JOINED 2026-08-26, and the reason is worth more than the
# line. This guard was GREEN while eight pages carried a correction section it
# could not recognise, because the pattern enumerated the heading forms that
# existed when it was written and a later pass introduced a ninth. The count it
# compared against the index was therefore true of one page and blind to eight,
# and an outside reading found the discrepancy that the guard was built to find.
# A detector that enumerates known forms goes quietly stale every time the
# corpus grows a new one, so this list is checked whenever a page gains a
# section heading that names a value.
_CORRECTION_SECTION = re.compile(
    r"^## (What this repository got wrong.*"
    r"|Values that moved.*"
    r"|.*, 20\d\d-\d\d-\d\d"
    r"|A .*that was not .*"
    r"|A .*that was actually .*"
    r"|Two claims this twin refuted.*)$", re.M)


def _spelled(text, tail):
    """The number word immediately before `tail`, as an int."""
    m = re.search(r"\b([A-Za-z-]+)\s+" + tail, text)
    if not m:
        return None
    return _WORDS.get(m.group(1).lower())


def test_the_index_counts_what_is_actually_there(capsys):
    """The two spelled-out counts on the index page are not stale.

    Reachability is checked above and cannot see a NUMBER written in prose.
    Both counts here have drifted before: the module-range gloss in
    docs/methods/ went stale the day a module was added, and its guard caught
    it, which is the only reason this one exists for the wiki.
    """
    text = INDEX.read_text(encoding="utf-8")
    pages = _pages()
    corrected = sorted(n for n in pages
                     if _CORRECTION_SECTION.search((WIKI / n).read_text(encoding="utf-8")))
    with capsys.disabled():
        print(f"\n  wiki counts: {len(pages)} pages, "
              f"{len(corrected)} carrying a correction section")
    said_pages = _spelled(text, "pages in")
    said_scars = _spelled(text, "of these pages")
    assert said_pages == len(pages), (
        f"docs/wiki/README.md says {said_pages} pages, {len(pages)} are on "
        "disk. Write the number in words, and update both places it appears.")
    assert said_scars == len(corrected), (
        f"docs/wiki/README.md says {said_scars} pages carry a correction section, "
        f"{len(corrected)} do:\n  " + "\n  ".join(corrected))

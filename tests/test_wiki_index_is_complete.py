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

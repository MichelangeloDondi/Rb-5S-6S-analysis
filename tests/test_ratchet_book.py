"""The ratchet history has one writer, and it writes nothing for nothing.

A re-run reseed that appends an identical row is the shape that halted the
chain of 2026-09-08 three times; six tests each carried their own append, and
a wave that repaired three left three. The book's writer is
`tests/_ratchet_book.record`, planted here on a temporary book in both
directions. The guard over the other modules is structural rather than a
pattern over call shapes, because a pattern passed a bare `open()` and a
renamed path in the same round (the adoption and register seats): a module
is refused when any open or write call reaches the book through its path,
through a name bound in a statement that carries the path, or through a name
imported from the helper. Reading the book is allowed, and so is naming it
in a list of tracked files, which is why two honest modules survive a
guard that a bare mention would have refused.
"""
import ast
from pathlib import Path

import pytest

import _ratchet_book as book

ROOT = Path(__file__).resolve().parents[1]
BOOK_NAME = "_ratchet_history"
OPENERS = ("open", "write_text", "write_bytes", "write")


def _carries_path(node) -> bool:
    return any(isinstance(n, ast.Constant) and isinstance(n.value, str)
               and BOOK_NAME in n.value for n in ast.walk(node))


def writes_the_book(source: str) -> list[str]:
    """Calls that open or write the book, as `line: call` strings."""
    tree = ast.parse(source)
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "_ratchet_book":
            bound.update(a.asname or a.name for a in node.names)
        elif isinstance(node, ast.Import):
            bound.update(a.asname or a.name for a in node.names
                         if a.name == "_ratchet_book")
        elif isinstance(node, (ast.Assign, ast.AnnAssign)) and _carries_path(node):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            bound.update(n.id for t in targets for n in ast.walk(t)
                         if isinstance(n, ast.Name))
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        attr = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if attr not in OPENERS:
            continue
        names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
        if _carries_path(node) or names & bound:
            hits.append(f"line {node.lineno}: {ast.unparse(node)[:80]}")
    return hits


def test_no_module_writes_the_book_itself():
    offenders = {}
    for p in sorted(list((ROOT / "tests").glob("*.py")) + list((ROOT / "scripts").glob("*.py"))):
        if p.name == "_ratchet_book.py":
            continue
        hits = writes_the_book(p.read_text(encoding="utf-8"))
        if hits:
            offenders[p.name] = hits
    assert not offenders, f"these open or write tests/_ratchet_history.md; go through _ratchet_book.record: {offenders}"


REFUSED = [
    'from pathlib import Path\nBOOK = Path("x").with_name("_ratchet_history.md")\nBOOK.open("a").write("row")\n',
    'from pathlib import Path\nHIST = Path("tests/_ratchet_history.md")\nopen(HIST, "a")\n',
    'from _ratchet_book import BOOK as B\nB.write_text("")\n',
    'import _ratchet_book as book\nbook.BOOK.open("a")\n',
    'from pathlib import Path\nPath("tests/_ratchet_history.md").write_text("")\n',
]
ALLOWED = [
    'from pathlib import Path\nrows = Path(__file__).with_name("_ratchet_history.md").read_text()\n',
    'TRACKED = ("tests/_ratchet_book.py", "tests/_ratchet_history.md")\n',
    'from _ratchet_book import record\nrecord("t", "reseed", {}, {}, "nothing")\n',
    '"""tests/_ratchet_history.md is the book this module never touches."""\nx = 1\n',
]


@pytest.mark.parametrize("src", REFUSED)
def test_the_guard_refuses_every_write_shape(src):
    assert writes_the_book(src), src


@pytest.mark.parametrize("src", ALLOWED)
def test_the_guard_allows_reading_and_naming(src):
    assert not writes_the_book(src), src


def test_record_writes_one_row_on_movement_and_none_otherwise(tmp_path, monkeypatch):
    fake = tmp_path / "book.md"
    fake.write_text("| date | tool | action | reason |\n")
    monkeypatch.setattr(book, "BOOK", fake)
    assert book.record("plant", "reseed 1 -> 1", {"a": 1}, {"a": 1}, "nothing moved") is False
    assert fake.read_text().count("\n") == 1
    assert book.record("plant", "reseed 1 -> 2", {"a": 1}, {"a": 2}, "a | moved") is True
    lines = fake.read_text().splitlines()
    assert len(lines) == 2 and lines[1].endswith("| a / moved |") and "| plant | reseed 1 -> 2 |" in lines[1]
    assert book.record("plant", "reseed", 5, 5, "totals equal") is False

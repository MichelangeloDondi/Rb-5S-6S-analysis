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


RATCHET_TOOLS = (
    "test_agonistic_ratchet.py", "test_prose_shape.py",
    "test_prose_style_ratchet.py", "test_reader_surface_budget.py",
    "test_reference_coverage.py", "test_results_err_format.py",
)


def test_every_ratchet_tool_hands_record_its_own_baseline_write():
    """`commit` defaults to None, so a caller can forget it and still pass.

    The ordering guarantee this module exists for is that the baseline is
    written and THEN the row is booked, so a refused reason leaves neither.
    A caller that writes its own baseline separately and calls `record`
    without `commit` gets no such ordering, and nothing detected that: the
    default made the omission silent. This walks the tool population and
    requires the keyword at every call site.

    Repairing the POPULATION and not the last name found missing: the tuple
    above is checked against the tools that actually own a baseline, so a new
    ratchet cannot join by being forgotten here.
    """
    import re
    missing, unseen = [], []
    for name in RATCHET_TOOLS:
        p = ROOT / "tests" / name
        if not p.is_file():
            unseen.append(name)
            continue
        src = p.read_text(encoding="utf-8")
        # NO WORD BOUNDARY. Every tool imports it as `record as _record`, and
        # `_` is a word character, so `\brecord` matched none of them and this
        # guard's population was empty on its first run. That is the failure
        # mode it exists to catch, met in its own implementation.
        pat = r"(?<![A-Za-z0-9])_?record\s*\("
        if not re.findall(pat, src):
            missing.append(f"{name}: never calls record()")
            continue
        for m in re.finditer(pat, src):
            seg = src[m.end():m.end() + 600]
            depth, end = 1, 0
            for i, ch in enumerate(seg):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if "commit=" not in seg[:end]:
                missing.append(f"{name}: a record() call omits commit=")
    assert not unseen, f"named ratchet tools that do not exist: {unseen}"
    assert not missing, (
        "a ratchet tool calls record() without handing it the baseline "
        "write, so the write-then-book ordering is not enforced for it:\n  "
        + "\n  ".join(missing))


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
    assert book.record("plant", "reseed 1 -> 2", {"a": 1}, {"a": 2}, "it moved") is True
    lines = fake.read_text().splitlines()
    assert len(lines) == 2 and lines[1].endswith("| it moved |")
    assert "| plant | reseed 1 -> 2; a 1 -> 2 |" in lines[1]
    assert book.record("plant", "reseed", 5, 5, "totals equal") is False


def test_the_row_carries_the_files_that_moved_and_counts_the_tail(tmp_path, monkeypatch):
    """The movement cell is derived from the baselines, never from the reason.

    A reseed's only per-file account was the free text a caller wrote, so a
    reason could credit a file whose count never moved. The cell now names the
    movers, largest first, and counts the rest rather than listing a hundred."""
    fake = tmp_path / "book.md"
    fake.write_text("| date | tool | action | reason |\n")
    monkeypatch.setattr(book, "BOOK", fake)
    before = {f"docs/f{i}.md": i for i in range(20)}
    after = dict(before, **{f"docs/f{i}.md": i + i for i in range(1, 12)})
    assert book.record("plant", "reseed", before, after, "eleven files") is True
    cell = fake.read_text().splitlines()[1].split("|")[3]
    assert "docs/f11.md 11 -> 22" in cell            # the largest mover leads
    assert cell.index("docs/f11.md") < cell.index("docs/f10.md")
    assert "and 5 more" in cell                      # eleven moved, six listed
    assert "docs/f0.md" not in cell and "docs/f19.md" not in cell
    # a total-comparing tool has no per-file account and says so
    assert book.record("plant", "relax", 28835, 28836, "one word") is True
    assert "28835 -> 28836" in fake.read_text().splitlines()[2]


def test_a_reason_crediting_a_file_that_did_not_move_is_refused(tmp_path, monkeypatch):
    """The exact instance: a reseed reason naming a page whose count stood.

    Prose about a chapter is untouched, because the refusal is keyed on the
    baseline's own keys, which are paths."""
    fake = tmp_path / "book.md"
    fake.write_text("| date | tool | action | reason |\n")
    monkeypatch.setattr(book, "BOOK", fake)
    before = {"docs/moved.md": 1, "docs/still.md": 7}
    after = {"docs/moved.md": 2, "docs/still.md": 7}
    with pytest.raises(SystemExit) as e:
        book.record("plant", "reseed", before, after,
                    "docs/still.md gained a tag")
    assert "docs/still.md" in str(e.value)
    assert fake.read_text().count("\n") == 1, "the refused row must not be written"
    # a reason that names what moved books, and so does prose naming no key
    assert book.record("plant", "reseed", before, after,
                       "the chapter that still stands gained nothing") is True


def test_a_tool_that_nests_its_counts_still_names_the_file(tmp_path, monkeypatch):
    """One instrument wraps its map in a `files` key and the others do not.

    Read at the top level that row would have said `files` changed, which is
    the shape of an account that is present and says nothing. The leaf name is
    what the reason has to be checkable against, so the movement cell carries
    it and the refusal grades it."""
    fake = tmp_path / "book.md"
    fake.write_text("| date | tool | action | reason |\n")
    monkeypatch.setattr(book, "BOOK", fake)
    before = {"files": {"results/a.csv": 1, "results/b.csv": 2}}
    after = {"files": {"results/a.csv": 3, "results/b.csv": 2}}
    assert book.record("plant", "reseed 3 -> 5", before, after, "a gained two") is True
    cell = fake.read_text().splitlines()[1].split("|")[3]
    assert "results/a.csv 1 -> 3" in cell and "files" not in cell
    with pytest.raises(SystemExit):
        book.record("plant", "reseed", before, after, "results/b.csv moved")


# --------------------------------------------------------------------------
# E43: the baseline write belongs INSIDE record, after its refusals
# --------------------------------------------------------------------------
# Every ratchet writer wrote its baseline and then called `record`, so a reason
# the credited-key check refused left the movement on disk with no row to
# explain it: the check that exists to force a reason was what produced a
# movement without one. `record` performs the write now, through `commit`, and
# these three cases pin the ordering in both directions. The first fails
# against the retired arrangement, which is what makes it evidence.


def test_a_refused_reason_leaves_the_baseline_untouched(tmp_path, monkeypatch):
    """The negative case, and the whole reason `commit` exists.

    Under the retired order the caller had already written the baseline when
    the refusal fired, so the movement shipped with no row. Here the write is
    handed to `record` and must not happen at all.
    """
    fake = tmp_path / "book.md"
    fake.write_text("# book\n", encoding="utf-8")
    monkeypatch.setattr(book, "BOOK", fake)
    baseline = tmp_path / "baseline.json"
    baseline.write_text("ORIGINAL", encoding="utf-8")

    before = {"moved.md": 1, "still.md": 7}
    after = {"moved.md": 2, "still.md": 7}
    written = []

    def commit():
        written.append(True)
        baseline.write_text("MOVED", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        # the reason credits still.md, whose count did not move
        book.record("t", "reseed", before, after, "still.md carried it",
                    commit=commit)

    # THE MESSAGE MUST SAY THE BASELINE IS UNTOUCHED. Until 2026-09-10 it said
    # only what was wrong with the reason, so a reader who had just been
    # refused could not tell from it whether the movement had already landed
    # on disk and needed undoing. The behaviour was right and the message did
    # not describe it.
    said = str(exc.value)
    assert "BASELINE WAS NOT WRITTEN" in said, (
        "the refusal does not tell the caller the baseline is untouched, so "
        f"it cannot be acted on without reading this module: {said}")

    assert not written, "the baseline write ran despite the refusal"
    assert baseline.read_text() == "ORIGINAL", (
        "a refused reason moved the baseline, which is escape E43")
    assert "reseed" not in fake.read_text(), "a refused reason booked a row"


def test_the_retired_caller_order_is_what_loses_the_row(tmp_path, monkeypatch):
    """The escape reproduced, so the repair is measured against it.

    E43 is not a property of `record` alone: it is the CALLER writing first.
    This runs both arrangements against the same refusal and asserts they
    differ, which is the only way to show the new one fixes anything. Under
    the retired order the baseline moves and the book stays empty, which is a
    ratchet movement with no reason -- exactly what the refusal exists to
    prevent.
    """
    fake = tmp_path / "book.md"
    fake.write_text("# book\n", encoding="utf-8")
    monkeypatch.setattr(book, "BOOK", fake)
    before = {"moved.md": 1, "still.md": 7}
    after = {"moved.md": 2, "still.md": 7}
    reason = "still.md carried it"          # credits a file that did not move

    # THE RETIRED ARRANGEMENT, EXPRESSED AS THE CALLER THAT PRODUCED IT. Its
    # write is unconditional, so asserting afterwards that the baseline moved
    # would be a tautology: the line above guarantees it. The first draft of
    # this test did exactly that, which is the row-that-cannot-fail pattern
    # this record retired from the transition ladder the same morning. What is
    # asserted instead is the thing that can fail, that `record` REFUSED and
    # booked nothing, so the movement stands with no row explaining it.
    # AND THE FILE IS GONE, 2026-09-10. The arm used to write a `retired.json`
    # twice and never read it: an inert write that made the arm look like it
    # tested something it did not. What the retired ORDER can actually be held
    # to is that `record`, called with no commit after the caller has already
    # moved, still refuses and still books nothing. The baseline's state under
    # that order is guaranteed by the caller's own line and is not evidence.
    retired_refused = False
    try:
        book.record("t", "reseed", before, after, reason)   # caller moved first
    except SystemExit:
        retired_refused = True
    assert retired_refused, "the retired arrangement did not reach the refusal"
    assert "reseed" not in fake.read_text(), (
        "the retired arrangement booked a row, so it is not the escape")

    repaired = tmp_path / "repaired.json"
    repaired.write_text("ORIGINAL", encoding="utf-8")
    with pytest.raises(SystemExit):
        book.record("t", "reseed", before, after, reason,
                    commit=lambda: repaired.write_text("MOVED", encoding="utf-8"))
    assert repaired.read_text() == "ORIGINAL", (
        "the repaired arrangement moved the baseline on a refused reason")

    assert "reseed" not in fake.read_text(), "neither arrangement books a row"


def test_an_accepted_reason_writes_the_baseline_then_the_row(tmp_path,
                                                             monkeypatch):
    """The positive case, and the order is asserted, not just the outcome."""
    fake = tmp_path / "book.md"
    fake.write_text("# book\n", encoding="utf-8")
    monkeypatch.setattr(book, "BOOK", fake)
    order = []

    def commit():
        order.append("baseline")

    assert book.record("t", "reseed", {"a.md": 1}, {"a.md": 2},
                       "a.md gained one", commit=commit) is True
    order.append("row")
    assert order == ["baseline", "row"]
    rows = [r for r in fake.read_text().splitlines() if r.startswith("| ")]
    assert len(rows) == 1, f"expected exactly one row, got {rows}"
    assert "a.md 1 -> 2" in rows[0]


def test_no_movement_writes_neither_the_baseline_nor_a_row(tmp_path,
                                                           monkeypatch):
    """`commit` must not fire when there is nothing to book."""
    fake = tmp_path / "book.md"
    fake.write_text("# book\n", encoding="utf-8")
    monkeypatch.setattr(book, "BOOK", fake)
    written = []
    assert book.record("t", "reseed", {"a.md": 1}, {"a.md": 1}, "nothing moved",
                       commit=lambda: written.append(True)) is False
    assert not written, "the baseline was written for a movement that is not one"
    assert fake.read_text() == "# book\n"


def test_a_caller_with_no_baseline_still_works(tmp_path, monkeypatch):
    """`commit` is optional, so callers that write nothing are unaffected."""
    fake = tmp_path / "book.md"
    fake.write_text("# book\n", encoding="utf-8")
    monkeypatch.setattr(book, "BOOK", fake)
    assert book.record("t", "reseed", {"a.md": 1}, {"a.md": 2},
                       "a.md gained one") is True
    assert "a.md 1 -> 2" in fake.read_text()

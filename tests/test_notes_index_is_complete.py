"""Every working note has a row in the notes index, and the rows name real files.

Written 2026-08-20 after a count found four of the twenty-two notes absent
from the table in docs/notes/README.md, one of them a preregistration, which
is the kind of file the index's own preamble says the directory exists to
hold. The preamble's file counts had drifted too and were made count-free as
a stopgap, but a stopgap is not a guard. This is the guard, on the pattern
of test_results_index_is_complete.py: the drift enters one note at a time,
when a file lands without a row, and until now nothing said so.

Both directions matter. A note with no row is a note a reader cannot use. A
row naming a file that is not there sends the reader after something
missing, which is worse, because it survives a deletion. A non-markdown
file in the directory counts as described when the note of the same stem is
in the table, which is how the campaign-only Stark profile carries its CSV.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "docs" / "notes"
INDEX = NOTES / "README.md"


def _notes():
    return {p.name for p in NOTES.iterdir()
            if p.is_file() and p.name != "README.md"}


def test_every_note_is_described_in_the_index():
    text = INDEX.read_text(encoding="utf-8")
    missing = sorted(
        name for name in _notes()
        if name not in text and Path(name).stem + ".md" not in text)
    assert not missing, (
        "these notes have no row in docs/notes/README.md, so a reader who "
        "opens the directory cannot tell what they are or whether they were "
        "written before or after the data:\n  " + "\n  ".join(missing))


def test_the_index_names_no_note_that_is_not_there():
    text = INDEX.read_text(encoding="utf-8")
    named = set(re.findall(r"\]\(([A-Za-z0-9_]+\.md)\)", text))
    phantom = sorted(name for name in named if not (NOTES / name).is_file())
    assert not phantom, (
        "docs/notes/README.md links notes that are not in docs/notes/:\n  "
        + "\n  ".join(phantom))

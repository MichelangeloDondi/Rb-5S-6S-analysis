"""The one writer of tests/_ratchet_history.md.

Every reseed and relax in tests/ records its movement here, and a movement of
nothing records nothing: on 2026-09-08 a re-run chain appended identical rows
through six separate writers and the duplicate-block guard halted three times.
`tests/test_ratchet_book.py` refuses any test that opens the book for append
on its own. `before` and `after` are whatever the tool compares, dicts or
totals; the row is written only when they differ.
"""
from datetime import date
from pathlib import Path

BOOK = Path(__file__).with_name("_ratchet_history.md")


def record(tool: str, action: str, before, after, reason: str) -> bool:
    """Append one row when something moved; print and write nothing otherwise."""
    if before == after:
        print("  (no key moved, no row written)")
        return False
    row = f"| {date.today()} | {tool} | {action} | {reason.replace('|', '/')} |\n"
    with BOOK.open("a", encoding="utf-8") as fh:
        fh.write(row)
    return True

"""The one writer of tests/_ratchet_history.md.

Every reseed and relax in tests/ records its movement here, and a movement of
nothing records nothing: on 2026-09-08 a re-run chain appended identical rows
through six separate writers and the duplicate-block guard halted three times.
`tests/test_ratchet_book.py` refuses any test that opens the book for append
on its own. `before` and `after` are whatever the tool compares, dicts or
totals; the row is written only when they differ.

THE ROW CARRIES THE MEASURED MOVEMENT AND NOT ONLY THE REASON (2026-09-08).
Until then the only per-file account of a reseed was the free text a caller
wrote, so a reason could credit a file whose count never moved and nothing in
the book could contradict it. `record` now derives the moving keys from the
two baselines it is already given and writes them into the movement cell, and
it refuses a reason that names a key which did not move. The refusal is keyed
on the baseline's own keys, which are paths, so prose about a chapter is
untouched and only a literal credit is graded.
"""
from datetime import date
from pathlib import Path

BOOK = Path(__file__).with_name("_ratchet_history.md")
MAX_KEYS = 6


def _leaves(d: dict) -> dict:
    """The per-file counts, whatever depth the tool nests them at.

    One tool wraps its map in a `files` key and the others do not, so a naive
    read of the top level would have written one row saying that `files`
    changed. Leaf names collide only if two branches carry the same file, and
    then both keep their branch so the row stays unambiguous."""
    flat, seen = {}, set()
    stack = [("", d)]
    while stack:
        prefix, node = stack.pop()
        for k, v in node.items():
            key = f"{prefix}{k}"
            if isinstance(v, dict):
                stack.append((f"{key}.", v))
            elif k in seen:
                flat = {(f"{key}." + kk if kk == k else kk): vv
                        for kk, vv in flat.items()}
                flat[key] = v
            else:
                seen.add(k)
                flat[k] = v
    return flat


def _cell(before, after) -> str:
    """The per-file movement, measured from the baselines the tool compared.

    Totals pass through as a totals movement, since a tool that compares one
    number has no per-file account to give. A dict names the keys that moved,
    largest first where the values subtract, with the tail counted rather than
    listed so a first seed does not write a hundred-key row."""
    if not (isinstance(before, dict) and isinstance(after, dict)):
        return f"{before} -> {after}"
    before, after = _leaves(before), _leaves(after)
    parts = []
    for k in set(before) | set(after):
        b, a = before.get(k), after.get(k)
        if b == a:
            continue
        try:
            size = abs(float(a) - float(b))
        except (TypeError, ValueError):
            size = float("inf") if b is None or a is None else 0.0
        parts.append((size, str(k), f"{k} {b} -> {a}"))
    parts.sort(key=lambda t: (-t[0], t[1]))
    shown = "; ".join(t[2] for t in parts[:MAX_KEYS])
    rest = len(parts) - MAX_KEYS
    return (shown + f"; and {rest} more") if rest > 0 else shown


def record(tool: str, action: str, before, after, reason: str) -> bool:
    """Append one row when something moved; print and write nothing otherwise."""
    if before == after:
        print("  (no key moved, no row written)")
        return False
    if isinstance(before, dict) and isinstance(after, dict):
        b_leaf, a_leaf = _leaves(before), _leaves(after)
        credited = sorted(k for k in set(b_leaf) & set(a_leaf)
                          if b_leaf[k] == a_leaf[k] and str(k) in reason)
        if credited:
            raise SystemExit(
                f"REFUSING to book a reason crediting {credited}, whose "
                f"count did not move; name what moved, which this row now "
                f"carries beside it")
    moved = _cell(before, after).replace("|", "/")
    row = (f"| {date.today()} | {tool} | {action}; {moved} | "
           f"{reason.replace('|', '/')} |\n")
    with BOOK.open("a", encoding="utf-8") as fh:
        fh.write(row)
    return True

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


def _names(key: str, reason: str) -> bool:
    """Does `reason` name `key`, as a key and not as the tail of another one?

    A BARE SUBSTRING TEST REFUSES A CORRECT REASON (2026-09-11). The baseline
    holds both `README.md` and `results/README.md`; a reason naming the second
    contains the first, so a movement in `results/README.md` was refused for
    crediting a `README.md` that had not moved, and the refusal's own advice
    ("name a key that actually moved") could not be followed. A key is named
    only where it starts at a path boundary: the start of the string, or after
    a character that is neither a path separator nor part of a name.

    AND A NESTED BASELINE FLATTENS TO A DOTTED FULL PATH, WHICH KILLED THE
    REFUSAL OUTRIGHT (2026-09-12). `_leaves` joins the branches, so a key from
    a nested tool reads `files.docs/GLOSSARY.md.longest_para.longest_para`, and
    no reason a person writes contains that string. Every nested-baseline
    reason therefore passed whatever it credited, which is the guard passing on
    a population it could not match rather than on a clean diff. The key's
    FILE-LIKE segments are what a reason names, so they are what is tested, and
    the whole key is still accepted for the flat tools.
    """
    import re as _re

    def _hit(k: str) -> bool:
        # A RIGHT BOUNDARY AS WELL AS A LEFT ONE. Without it `_hit("py")`
        # matches inside "pytest", so "reran pytest after the widening"
        # credited 337 of 488 keys across the live baselines.
        return bool(_re.search(r"(?<![\w./-])" + _re.escape(k) + r"(?![\w-])",
                               reason))

    if _hit(key):
        return True
    # A file-like token inside the dotted key, and every suffix of it that
    # still starts at a path boundary: a reason naming `GLOSSARY.md` must
    # match a key reading `files.docs/GLOSSARY.md.longest_para.longest_para`,
    # and naming `results/README.md` must still not match a bare `README.md`.
    # STRIP THE STRUCTURAL WRAPPER, NEVER A DIRECTORY. `_leaves` prefixes one
    # tool's keys with `files.`, which is bookkeeping and not part of the path,
    # so it comes off. The directory does NOT: a key stored as
    # `results/README.md` is credited by a reason naming `results/README.md`
    # and not by one naming a bare `README.md`, because the baseline holds
    # three README.md keys and a bare mention cannot say which moved. That is
    # the same separation the 2026-09-11 repair was written for, read in the
    # other direction, and walking the token down to its basename broke it.
    for m in _re.finditer(r"[\w./-]+\.(?:md|py|json|csv|txt|sh|ipynb)\b", key):
        tok = _re.sub(r"^files\.", "", m.group(0))
        if "/" in tok or "." in tok:
            if _hit(tok):
                return True
    return False


def _leaves(d: dict) -> dict:
    """The per-file counts, whatever depth the tool nests them at.

    One tool wraps its map in a `files` key and the others do not, so a naive
    read of the top level would have written one row saying that `files`
    changed. Leaf names collide only if two branches carry the same file, and
    then both keep their branch so the row stays unambiguous."""
    # EVERY NESTED LEAF KEEPS ITS FULL PATH (2026-09-12). The first form kept
    # a leaf bare until a second branch carried the same name and then renamed
    # the earlier leaf under the CURRENT branch's path, so whichever file was
    # walked second absorbed the first file's value under a doubled key, and
    # three book rows credited docs/plan/00's 366 and 94 to GLOSSARY.md and
    # big_picture/01 (replayed 2026-09-12, and tests/test_ratchet_book.py
    # carries the two-file case). A top-level leaf stays bare, which is what the
    # flat tools' rows already read.
    # A leaf directly under one wrapper level (the `files` map of a flat tool)
    # stays bare, which is what those tools' rows already read; a leaf two or
    # more levels down keeps its whole path.
    flat = {}
    stack = [((), d)]
    while stack:
        path, node = stack.pop()
        for k, v in node.items():
            full = path + (k,)
            if isinstance(v, dict):
                stack.append((full, v))
            else:
                flat[full[-1] if len(full) <= 2 else ".".join(full)] = v
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


def record(tool: str, action: str, before, after, reason: str,
           commit=None) -> bool:
    """Append one row when something moved; print and write nothing otherwise.

    `commit`, when given, is the caller's own baseline write, and this function
    performs it. IT IS CALLED HERE AND ONLY AFTER EVERY REFUSAL HAS CLEARED,
    which is the whole point of the argument.

    Until 2026-09-10 every caller wrote its baseline first and then called this
    (escape E43). The credited-key refusal below raises SystemExit, so on a
    refused reason the movement was already on disk and the row explaining it
    was never written: the check that exists to force a reason was the thing
    that produced a movement without one. Two call sites even carried a comment
    defending the order, that a dying write should leave no row. That still
    holds here, because a `commit` that raises does so before the row is
    appended, and now a REFUSAL leaves the baseline untouched as well.

    A caller with no baseline to write passes nothing and is unaffected.
    """
    if before == after:
        print("  (no key moved, no row written)")
        return False
    if isinstance(before, dict) and isinstance(after, dict):
        b_leaf, a_leaf = _leaves(before), _leaves(after)
        credited = sorted(k for k in set(b_leaf) & set(a_leaf)
                          if b_leaf[k] == a_leaf[k] and _names(str(k), reason))
        if credited:
            raise SystemExit(
                f"REFUSING to book a reason crediting {credited}, whose "
                f"count did not move. Name what moved, which this row now "
                f"carries beside it.\n"
                f"  THE BASELINE WAS NOT WRITTEN. This refusal happens "
                f"before the caller's commit, so nothing moved on disk and "
                f"there is nothing to undo. Re-run with a reason naming a "
                f"key that actually moved.")
    if commit is not None:
        commit()
    moved = _cell(before, after).replace("|", "/")
    row = (f"| {date.today()} | {tool} | {action}; {moved} | "
           f"{reason.replace('|', '/')} |\n")
    with BOOK.open("a", encoding="utf-8") as fh:
        fh.write(row)
    return True

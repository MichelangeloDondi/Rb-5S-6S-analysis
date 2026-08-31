#!/usr/bin/env python3
"""Decide the suite's contribution to the gate's verdict.

Prints exactly one line: ``PASS`` (rc was zero), ``PASS_MODULO <n,m>``
(every FAILED or ERROR test id in the log matches a gate-excusable
signature in ``private/COMMON_CAUSE_REGISTER.md``), or ``FAIL``. The
word on stdout is the whole interface: the caller acts on it, and this
process exits 0 on every input it can classify, including malformed
arguments (classified FAIL), so a ``set -e`` shell is never killed by
the decision itself. ``PASS_MODULO`` becomes the gate's verdict only
after every downstream stage completes; the gate script owns that.

Fail-closed by construction: a missing or unreadable register excuses
nothing; a nonzero rc with an empty failure list (a collection crash) is
FAIL; an ``ERROR`` line counts exactly like ``FAILED`` (fixture and
teardown errors are failures); an entry with no ``signature-tests:``
line of its own excuses nothing (no inheritance from the previous
entry); a signature without ``::`` is ignored, so a bare filename can
never excuse a whole-file collection error; a log that contains
``drifted from`` is never excusable, whatever ids it carries -- a
committed CSV that stops matching its producer is special-cause by
definition, and this veto outranks every register entry.

Register format contract (stated beside the entries, in the register's
header): each ``## <n>`` entry carries at most one ``signature-tests:``
line -- one physical line, space-separated full ``file::test`` ids
without parameters -- and one ``gate-excusable:`` line whose value
starts with ``yes``, ``no``, or ``conditional``. Only ``yes`` excuses;
``conditional`` marks an entry whose reading rule needs a human, and
this parser treats it as ``no``. tests/test_gate_verdict.py pins the
live register's parse as an exact map, so editing a machine line there
means updating that test in the same change.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "private" / "COMMON_CAUSE_REGISTER.md"

# Presence of this string in the pytest log vetoes every excuse: a
# freshness drift is never common-cause. Kept here, not per-entry, so a
# future entry cannot opt out of it.
DRIFT_VETO = "drifted from"


def excusable_map() -> dict[str, set[str]]:
    """entry number -> its signature ids, for gate-excusable: yes only."""
    try:
        text = REGISTER.read_text(encoding="utf-8")
    except OSError:
        return {}
    out: dict[str, set[str]] = {}
    num, sigs = None, set()
    excusable = False
    for line in text.splitlines() + ["## end"]:
        if line.startswith("## "):
            if num is not None and excusable and sigs:
                out[num] = sigs
            m = re.match(r"## (\d+)", line)
            num = m.group(1) if m else None
            sigs, excusable = set(), False
        elif line.startswith("signature-tests:"):
            ids = line.split(":", 1)[1].split()
            sigs = {i for i in ids if "::" in i}
        elif line.startswith("gate-excusable:"):
            # exactly `yes` -- `yes, but ...` is a condition wearing a
            # yes, and a condition is read by a person, never by the gate
            excusable = line.split(":", 1)[1].strip().lower() == "yes"
    return out


def failures(log_text: str) -> set[str]:
    ids = set()
    for line in log_text.splitlines():
        m = re.match(r"(?:FAILED|ERROR) (\S+)", line)
        if m:
            ids.add(re.sub(r"\[.*", "", m.group(1)))
    return ids


def verdict(rc: int, log_text: str) -> str:
    if rc == 0:
        return "PASS"
    if DRIFT_VETO in log_text:
        return "FAIL"
    failed = failures(log_text)
    if not failed:
        return "FAIL"
    emap = excusable_map()
    allsigs = set().union(*emap.values()) if emap else set()
    if not failed <= allsigs:
        return "FAIL"
    entries = sorted((n for n, s in emap.items() if s & failed), key=int)
    return "PASS_MODULO " + ",".join(entries)


def main() -> int:
    if len(sys.argv) != 3:
        print("FAIL")
        return 0
    try:
        rc = int(sys.argv[1])
    except ValueError:
        print("FAIL")
        return 0
    try:
        text = Path(sys.argv[2]).read_text(encoding="utf-8",
                                           errors="replace")
    except OSError:
        print("FAIL")
        return 0
    print(verdict(rc, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())

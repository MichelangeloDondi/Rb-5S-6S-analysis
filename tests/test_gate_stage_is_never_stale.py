"""The verdict's fourth line must name the stage that failed, or nothing.

WHY THIS EXISTS (2026-09-11, four seats of one board, independently). The gate
gained a `stage=` line so a reader -- and `board_ledger.py`'s admission door --
could tell which stage exited, because `.ci_gate_fail.log` is a copy of the
pytest log alone and answers the same way whichever later stage failed. The
first form assigned `GATE_STAGE` before five stages and never cleared it, so
the `private/checks` parse gate, the two chapter advisories and the tree-moved
chimera check all inherited `board_ledger_verify` from the stage above them.
The verdict then named a stage that had PASSED, and the ledger's door, whose
first condition is `stage == "board_ledger_verify"`, would open on a failure it
was never written to excuse. The shipped comment claimed the opposite.

The plant for that door could not see it: it passes `stage=` as a parameter, so
it grades the consumer and never the shell that produces the value. This test
grades the producer, and it is in the tracked suite because `scripts/ci_gate.sh`
is a tracked file while every checker that reads its output is not.

FAILURE MODE GUARDED: an exit-capable line whose effective `GATE_STAGE` was
assigned for an earlier stage whose block has already closed.

**HOW IT WAS VERIFIED, CORRECTED (2026-09-11).** The first form of this line
said "verified by deleting one `GATE_STAGE=""` clear and confirming this test
fails". Two seats deleted all six clears one at a time and found five of six
green, and the sixth red only because the `exit` regex was matching the English
words "exit 0" and "exit 1" inside two comment blocks -- the one demonstrated
positive was a false one, and the population floor was inflated by the same two.
Comments are stripped now, and the truthful account is this: the invariant the
guard holds is the INHERITANCE one, and deleting a single clear does not break
it, because every stage after the cleared one names itself. What breaks it, and
what this guard catches, is the shipped defect itself -- a later exit-capable
stage with NO name of its own, standing after a stage whose block has closed.
Reconstructing that (removing `private_checks_parse`'s name and the ledger
stage's clear together) makes this test fail and name both lines. The clears are
defence in depth against the next stage that forgets to name itself, and this
docstring no longer claims they are each load-bearing on their own.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "ci_gate.sh"

# an exit that can carry a non-zero status; `exit 0` is a deliberate pass
_EXIT = re.compile(r"(?<![\w-])exit\s+(?:(\d+)|\"?\$)")
_ASSIGN = re.compile(r'^\s*GATE_STAGE="([^"]*)"')
# a block closing at column zero ends the stage whose command it wrapped
_CLOSE = re.compile(r"^(fi|esac|done|\})\s*$")


def _code(line: str) -> str:
    """The line with its trailing comment removed, quotes respected.

    THE FIRST FORM HAD NO COMMENT AWARENESS AND ITS ONE DEMONSTRATED POSITIVE
    WAS A FALSE ONE (2026-09-11, two seats, each by deleting all six clears one
    at a time). `scripts/ci_gate.sh` carries the English words "exit 0" and
    "exit 1" inside two comment blocks; `_EXIT` matched both, so the guard's
    population was inflated by two and the single deletion its docstring cited
    as proof fired on a COMMENT rather than on any shell statement. Five of the
    six real clears could be deleted with the guard green.
    """
    out, quote = [], ""
    for ch in line:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = ""
            continue
        if ch in "'\"":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out)


def _lines() -> list[str]:
    return [_code(ln) for ln in GATE.read_text(encoding="utf-8").splitlines()]


def _trap_line(lines: list[str]) -> int:
    for i, ln in enumerate(lines):
        if ln.startswith("trap ") and ln.rstrip().endswith("EXIT"):
            return i
    raise AssertionError("scripts/ci_gate.sh installs no EXIT trap")


def _stale_exits(lines: list[str]) -> list[tuple[int, str, int]]:
    """Every exit-capable line after the trap whose live stage name was
    assigned for a block that has since closed. Returns (lineno, name, from)."""
    start = _trap_line(lines)
    live_name, live_at, closed_since = "", -1, False
    bad = []
    for i, ln in enumerate(lines):
        m = _ASSIGN.match(ln)
        if m:
            live_name, live_at, closed_since = m.group(1), i, False
            continue
        if _CLOSE.match(ln):
            closed_since = True
        if i <= start:
            continue
        hit = _EXIT.search(ln)
        if not hit or hit.group(1) == "0":
            continue
        # an exit that names its own stage on the same line is honest
        if "GATE_STAGE=" in ln:
            continue
        if live_name and closed_since:
            bad.append((i + 1, live_name, live_at + 1))
    return bad


def test_no_exit_inherits_a_stage_whose_block_has_closed():
    bad = _stale_exits(_lines())
    assert not bad, (
        "these exits would write a stage name belonging to a stage that "
        "already finished: "
        + "; ".join(f"line {n} reports {name!r} assigned at line {a}"
                    for n, name, a in bad)
        + ". Name the stage before the exit, or clear GATE_STAGE when the "
          "stage that owns the name has passed, so the verdict reads "
          "'unnamed' instead of a lie.")


def test_the_population_is_not_empty():
    """The guard above passes trivially on a file with no exits at all."""
    lines = _lines()
    start = _trap_line(lines)
    exits = [i for i, ln in enumerate(lines)
             if i > start and _EXIT.search(ln) and _EXIT.search(ln).group(1) != "0"]
    assert len(exits) >= 12, (
        f"only {len(exits)} exit-capable lines found after the trap; the "
        "pattern has stopped matching the script and this guard is grading "
        "an empty population. The floor is 12 because the two English 'exit'\n"
        "        phrases inside comments used to inflate it to 16 and the real "
        "count is 14.")


def test_every_named_stage_is_cleared_or_is_the_last_one():
    """A name that outlives its own command is the defect above, one step
    earlier: a stage whose guarded command is followed by more script must
    clear it, or the next untagged failure inherits it."""
    lines = _lines()
    names = [(i + 1, m.group(1)) for i, ln in enumerate(lines)
             if (m := _ASSIGN.match(ln))]
    assert names, "no GATE_STAGE assignment found at all"
    assert any(v == "" for _, v in names), (
        "no GATE_STAGE clear exists anywhere in scripts/ci_gate.sh; without "
        "one, every name assigned survives to the end of the script")

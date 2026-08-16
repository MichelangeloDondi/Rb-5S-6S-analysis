#!/usr/bin/env python3
"""Rewrite the advertised test counts in docs/methods.md from the real suite.

    ./.venv/bin/python scripts/update_test_counts.py          # rewrite
    ./.venv/bin/python scripts/update_test_counts.py --check  # report only

WHY THIS EXISTS. The suite size is quoted in three places in docs/methods.md,
and it went stale FIVE times between 2026-08-15 and 2026-08-17. Not once was
that carelessness about the rule: every occurrence was found by the guard,
fixed at every site, and stale again within hours. The reason is structural.
Several tests are parametrized over documentation files, so ADDING A PAGE
CHANGES THE TEST COUNT, and a wiki wave of thirteen pages moved it by more
than a hundred. A number that changes whenever prose changes cannot be
maintained by remembering to change it.

Rule 19.36 says a check naming one site has found a symptom rather than the
extent, and that rule was obeyed each time. The audit-7 entry recorded the
residue as a standing debt with the remedy named: generate the count rather
than assert it. This is that remedy.

WHAT IT DOES NOT DO. It does not run the tests. Collection alone is enough to
count them and takes seconds, whereas running the battery takes minutes, and
the quantity being advertised is how many tests exist rather than how many
pass.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
METHODS = ROOT / "docs" / "methods.md"


def _collect(*extra: str) -> int:
    """How many tests pytest collects, without running any of them.

    THE SLOW COUNT IS NOT total-minus-collected-without-runslow, which was
    this script's first version and returned zero slow tests. The `slow`
    tests are SKIPPED at run time rather than deselected at collection, so
    collection returns the same total either way. Counting them needs the
    marker expression, and its line reads "53/2416 tests collected (2363
    deselected)", which is a DIFFERENT sentence from the plain total.
    """
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *extra],
        cwd=ROOT, capture_output=True, text=True)
    m = re.search(r"(\d+)/\d+\s+tests? collected", out.stdout)   # marker form
    if m:
        return int(m.group(1))
    m = re.search(r"(\d+)\s+tests? collected", out.stdout)        # plain total
    if not m:
        raise SystemExit("could not read a collected count from pytest:\n"
                         + out.stdout[-2000:])
    return int(m.group(1))


def main() -> int:
    full = _collect()
    slow = _collect("-m", "slow")
    fast = full - slow
    text = METHODS.read_text(encoding="utf-8")

    # The three sites, each pinned by the words around the number so a
    # coincidental integer elsewhere is never touched.
    subs = (
        (re.compile(r"\b\d+-test battery \(\d+ fast [^)]*?\+ \d+ `slow`"),
         f"{full}-test battery ({fast} fast ~4 min + {slow} `slow`"),
        (re.compile(r"(pytest -q\s+# )\d+( fast tests)"),
         rf"\g<1>{fast}\g<2>"),
        (re.compile(r"(--runslow\s+# full )\d+"),
         rf"\g<1>{full}"),
    )
    new = text
    for pat, rep in subs:
        new, n = pat.subn(rep, new)
        if n == 0:
            raise SystemExit(f"pattern found no site in docs/methods.md: "
                             f"{pat.pattern!r}. The wording changed, so this "
                             f"script has to change with it rather than "
                             f"silently updating nothing.")

    if "--check" in sys.argv:
        state = "current" if new == text else "STALE"
        print(f"suite: {full} total ({fast} fast + {slow} slow); "
              f"docs/methods.md is {state}")
        return 0 if new == text else 1

    if new == text:
        print(f"docs/methods.md already current: {full} ({fast} + {slow})")
        return 0
    METHODS.write_text(new, encoding="utf-8")
    print(f"docs/methods.md updated: {full} total, {fast} fast, {slow} slow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

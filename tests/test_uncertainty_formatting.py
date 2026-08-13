#!/usr/bin/env python3
"""Value-and-uncertainty pairs follow the community convention.

The convention is protocol 8a, which adopts the BIPM guide's presentation and
the form CODATA, NIST and the field's journals use:

  * a Gaussian uncertainty carries EXACTLY TWO significant digits,
  * the value is rounded to the same decimal place as the second of those
    digits, so the pair reads as one statement rather than two numbers.

        6.7 ± 2.9        right
        6.744 ± 2.9      wrong, the value claims a thousandth the pair denies
        6.74 ± 2.94      ALSO WRONG, 2.94 is three digits (corrected
                         2026-08-13, having stood here as "right")
        4.8 ± 2.4        wrong here, one digit on the uncertainty

WHY THIS IS A BUDGET AND NOT A BAN. Measured 2026-08-13: 74 pairs in the
tracked prose, 23 already correct, 47 with a one-digit uncertainty, 4 with
mismatched decimals. The 47 CANNOT simply be reformatted, and the reason
matters. `results/wavemeter_reconstruction.csv` stores `value=0.62 err=0.03`,
so the second digit does not exist anywhere in the record: it was rounded at
production. Writing 0.030 would invent precision rather than restore it, which
is the exact fault the convention exists to prevent.

So the repair belongs in the PRODUCERS, which must write two digits into the
CSVs, after which the prose regenerates. Until then this guard works the way
the prose ratchet does, as a budget that may only shrink. A new violation
fails; the inherited ones are counted and visible.

Frozen records are exempt, as in protocol 2.1a and 8a.5, and so are the
reading notes, whose numbers are other people's.

FOUR OF THE 51 WILL NEVER BE FIXED, and that is correct. All four are the
same quotation, Cao 2025's published 40 plus or minus 0.54 kHz/mTorr, which
fails on the value's decimals because that is how they published it. Protocol
8a.5 exempts another author's value quoted verbatim, and the guard does not
try to detect quotation mechanically, so those four sit inside the budget as
a permanent floor rather than as work.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_uncertainty_baseline.json")
SKIP = ("PREREGISTRATION", "/lit/")

# An uncertainty a PERSON CHOSE keeps the precision they chose (protocol
# 8a.5). RHO_RETRO_ERR = 0.04 is a declared one-sigma on an assumed retro
# return fraction, so printing 0.040 would claim the assumption is known to
# two digits. The test is provenance, not size. `check_carriers.py` holds
# the same exemption, and the two lists must agree or the repository and its
# outbound documents disagree about the same number.
DECLARED = {("0.94", "0.04")}
PAIR = re.compile(r"(-?\d+\.?\d*)\s*(?:±|\+/-)\s*(\d+\.?\d*)")


def _sig(text: str) -> int:
    """A trailing zero AFTER a decimal point is significant.

    This counted them backwards until 2026-08-13, the same inversion the
    sibling formatter test documents as fixed. Fixing it there and not here
    is why a live three-digit uncertainty went unreported by this guard.
    """
    digits = text.replace(".", "").lstrip("0")
    return len(digits) if "." in text else (len(digits.rstrip("0")) or 1)


def _dec(text: str) -> int:
    return len(text.split(".")[1]) if "." in text else 0


def _violations() -> list[str]:
    # Tracked AND about-to-be-tracked, protocol 14.1a. Scanning only
    # `git ls-files` made this guard blind to any newly written file until
    # it was staged, which is the fault repaired in test_repo_hygiene the
    # same day and not ported here at the time.
    tracked = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                             capture_output=True, text=True).stdout.split()
    fresh = subprocess.run(["git", "ls-files", "--others",
                            "--exclude-standard", "*.md"], cwd=ROOT,
                           capture_output=True, text=True).stdout.split()
    out = tracked + fresh
    bad = []
    for rel in out:
        if any(k in rel for k in SKIP):
            continue
        path = ROOT / rel
        if not path.exists():
            continue
        for n, line in enumerate(path.read_text().splitlines(), 1):
            for m in PAIR.finditer(line):
                value, unc = m.group(1), m.group(2)
                if (value, unc) in DECLARED:
                    continue
                if _sig(unc) != 2:
                    bad.append(f"{rel}:{n} {m.group(0)!r} uncertainty has "
                               f"{_sig(unc)} significant digits, not 2")
                elif _dec(value) != _dec(unc):
                    bad.append(f"{rel}:{n} {m.group(0)!r} value has "
                               f"{_dec(value)} decimals against the "
                               f"uncertainty's {_dec(unc)}")
    return bad


def test_no_new_uncertainty_formatting_violations():
    """A budget that may only shrink, never grow."""
    bad = _violations()
    if not BASELINE.exists():
        BASELINE.write_text(json.dumps({"count": len(bad)}, indent=2) + "\n")
        pytest.skip(f"baseline recorded at {len(bad)}")
    allowed = json.loads(BASELINE.read_text())["count"]
    assert len(bad) <= allowed, (
        f"{len(bad)} value-and-uncertainty formatting violations against a "
        f"budget of {allowed}. Protocol 8a.2: two significant digits on the "
        f"uncertainty, and the value rounded to the second of them.\n  "
        + "\n  ".join(bad[:12]))
    if len(bad) < allowed:
        BASELINE.write_text(json.dumps({"count": len(bad)}, indent=2) + "\n")


def test_the_guard_actually_finds_the_known_shapes():
    """Checked on a known match and a known non-match, because a budget
    guard that matches nothing passes without examining anything.
    """
    assert _sig("2.9") == 2 and _sig("0.03") == 1 and _sig("24") == 2
    assert _dec("6.744") == 3 and _dec("40") == 0

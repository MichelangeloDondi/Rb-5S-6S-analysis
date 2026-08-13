#!/usr/bin/env python3
"""`make_figures.pm` formats a pair at two significant digits, always.

The convention is protocol 8a.2: the uncertainty carries exactly two
significant digits and the value is rounded to the same decimal place, so the
pair reads as one statement rather than two numbers.

WHY A FUNCTION RATHER THAN A FORMAT STRING. A fixed `:.4f` is decimals, not
significant digits, and the two diverge in both directions. For an
uncertainty of 0.0304 two decimals give 0.03, one digit. For 24.09 they give
24.09, four. On the figure this guard protects, a background slope printed as
0.00003 +/- 0.00003 hid the fact that the value is smaller than its own
uncertainty, which the correct 0.000026 +/- 0.000034 shows at a glance.

TWO CASES NEED SCIENTIFIC NOTATION, and both are about an ambiguity plain
decimal cannot resolve. 2600 reads as four significant digits while carrying
two, and a bare 10 cannot say whether it carries one digit or two, while 24
can. Both take the shared-decade form, which is what CODATA does.
"""
from __future__ import annotations

import importlib.util
import random
import re
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "_mf_pm", Path(__file__).resolve().parents[1] / "scripts" / "make_figures.py")
_mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mf)
pm = _mf.pm

SCI = re.compile(r"^\((-?[\d.]+) ± ([\d.]+)\)\$?[^0-9]*10\^\{?(-?\d+)\}?\$?")


def _sig_and_match(text: str) -> tuple[int, bool]:
    """Significant digits of the printed uncertainty, and whether the value
    sits on the same decimal place.

    A trailing zero AFTER a decimal point is significant, so 0.000060 is two
    digits. Stripping trailing zeros unconditionally is right only for a bare
    integer, where they are ambiguous, and getting that backwards made a
    correct formatter look broken on 1918 of 20000 pairs.
    """
    m = SCI.match(text)
    vtxt, etxt = (m.group(1), m.group(2)) if m else text.split(" ± ")
    digits = etxt.replace(".", "").replace("-", "").lstrip("0")
    sig = len(digits) if "." in etxt else len(digits.rstrip("0"))
    vdp = len(vtxt.split(".")[1]) if "." in vtxt else 0
    edp = len(etxt.split(".")[1]) if "." in etxt else 0
    return sig, vdp == edp


@pytest.mark.parametrize("value,err,expected", [
    (6.744,    2.9351,  "6.7 ± 2.9"),
    (-161.03,  0.6838,  "-161.03 ± 0.68"),
    (-33.8,   24.0936,  "-34 ± 24"),
    (0.62,     0.0304,  "0.620 ± 0.030"),
    (4.75,     2.37,    "4.8 ± 2.4"),
    (0.0183,   0.00016, "0.01830 ± 0.00016"),
    (1.9,      0.099,   "1.900 ± 0.099"),
    (2.6e-5,   3.4e-5,  r"(2.6 ± 3.4)$\,\times\,10^{-5}$"),
    (-70043.3, 2629.7,  r"(-70.0 ± 2.6)$\,\times\,10^{3}$"),
    (127.206,  162.226, r"(1.3 ± 1.6)$\,\times\,10^{2}$"),
])
def test_named_cases(value, err, expected):
    assert pm(value, err) == expected


def test_two_significant_digits_over_fourteen_decades():
    """The property, not a sample of it."""
    rng = random.Random(11)
    bad = []
    for _ in range(20000):
        err = 10 ** rng.uniform(-8, 6) * rng.choice([1, 2.5, 9.9, 9.99])
        value = err * rng.uniform(-500, 500)
        text = pm(value, err)
        sig, matched = _sig_and_match(text)
        if sig != 2 or not matched:
            bad.append(f"pm({value:g}, {err:g}) = {text!r} "
                       f"sig={sig} decimals_matched={matched}")
    assert not bad, (f"{len(bad)} of 20000 pairs break protocol 8a.2:\n  "
                     + "\n  ".join(bad[:8]))


def test_a_missing_uncertainty_is_not_invented():
    """No error means no plus-or-minus, never a fabricated one."""
    assert "±" not in pm(1.234, None)
    assert "±" not in pm(1.234, 0.0)
    assert "±" not in pm(1.234, float("nan"))


def test_every_drawn_pair_goes_through_pm():
    """No hand-formatted value-and-uncertainty pair survives in the generator.

    The rule became code precisely because choosing digits by eye failed
    twice in one day, in the protocol's own worked example and in this
    test's first expected values. A hand-formatted pair reintroduces the
    choice, so the only lines allowed to write a plus-or-minus between two
    formatted numbers are pm's own two return statements.
    """
    src = (Path(__file__).resolve().parents[1] / "scripts"
           / "make_figures.py").read_text()
    offenders = []
    inside_pm = False
    for n, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("def "):
            inside_pm = stripped.startswith("def pm(")
        if "±" not in line or stripped.startswith("#"):
            continue
        if inside_pm or "pm(" in line or "pm_row(" in line:
            continue
        offenders.append(f"{n}: {stripped[:80]}")
    assert not offenders, (
        "hand-formatted pairs on a canvas, protocol 8a.2 wants pm():\n  "
        + "\n  ".join(offenders))


@pytest.mark.parametrize("value,kind,expected", [
    (0.963, "upper", "< 0.97"),     # the case that was wrong on the figure
    (0.963, "lower", "> 0.96"),
    (0.217, "upper", "< 0.22"),
    (0.211, "upper", "< 0.22"),
    (0.219, "lower", "> 0.21"),
    (0.960, "upper", "< 0.96"),     # already on the grid, do not inflate it
    (0.960, "lower", "> 0.96"),
])
def test_a_bound_rounds_away_from_the_allowed_region(value, kind, expected):
    """Protocol 8a.3. An upper limit rounds UP, a lower limit rounds DOWN.

    Rounding to nearest tightens the claim: the record's 95 per cent upper
    bound on the AC-Stark coefficient is 0.963 MHz/W, and a plain two-decimal
    format printed "< 0.96" on the shipped figure, which is a tighter limit
    than the data support. Of all the directions to be wrong in, a record
    built on refusing to overclaim can least afford that one.

    A value already on the rounding grid must not be inflated, which is why
    0.960 stays 0.96 in both directions.
    """
    assert _mf.bound(value, 2, kind) == expected


@pytest.mark.parametrize("value,err,expected", [
    (1e6, 0.5, "1000000.00 ± 0.50"),   # big value, small error: plain is fine
    (1e6, 24,  "1000000 ± 24"),
])
def test_a_large_value_with_a_small_error_stays_in_plain_decimal(
        value, err, expected):
    """A magnitude test on the VALUE sent this case to the decade form.

    The scale there comes from the uncertainty's decade, so 1e6 +/- 0.5
    printed as (10000000.0 +/- 5.0) x 10^-1: more digits, not fewer, and a
    factored decade that helps nobody. Leading zeros are what the decade
    form cures, and a large value has none.
    """
    assert pm(value, err) == expected


@pytest.mark.parametrize("err", [0, 0.0, -1.0, float("nan"), float("inf"), None])
def test_a_missing_uncertainty_is_stated_rather_than_dropped(err):
    """8a.1 admits a bare value only beside a reason it has no uncertainty.

    A non-finite error is a real fit failure, not a hypothetical, and
    printing the value alone turned that failure into a number a reader
    would take at face value. The absence has to be visible.
    """
    text = pm(1.5, err)
    assert "±" not in text
    assert "uncertainty" in text, f"absence not stated: {text!r}"

"""
SVG CANONICAL: physics numbers on hand-authored drawings, checked against the
same SSOT discipline as test_docs_canonical.

Why this file exists. A hand-authored SVG is invisible to every other guard:
test_figure_register and test_figures_fresh cover only scripts/make_figures.py
outputs, and test_docs_canonical scans only markdown. So numbers drawn on the
bench schematic went stale unseen. It quoted w0 ~ 50 um, a value matching
neither the replaced 32 um naive estimate nor the measured 64 um prior, and
asserted rho ~ 1 where the analysis of record assumes 0.94 +- 0.04. This file
closes the class. Every tracked *.svg under docs/ is scanned for the quantities
a drawing is likely to quote (the waist, the retro ratio rho, MHz comb
frequencies, MHz/min drift rates), and every number found must equal the
canonical value derived live from rb5s6s.constants.

Scope mirrors the registry note in test_docs_canonical: guarded here are the
adopted analysis inputs a re-analysis can move. Fixed bench hardware labels
(f = 150 mm, the 70-130 C oven range, the preamp gain setting) are established
by APPARATUS.md and the photographs, not by a re-run, and stay unguarded.

A number outside the allowed set is not always an error. It may be a new
quantity the drawing legitimately quotes. The fix is then to extend
SVG_QUANTITIES with a value derived from its SSOT, never to loosen a pattern.
"""

from __future__ import annotations

import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from rb5s6s import constants as K

ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = "docs/apparatus/apparatus_schematic.svg"


def _tracked_svgs():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "docs/*.svg"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    return [p for p in out.stdout.split("\n") if p]


def _normalize(s: str) -> str:
    """Collapse the notational freedom of a drawing label so ONE regex per
    quantity works: subscript zero, both mu codepoints, ascii 'um', the
    approximation signs and the two spellings of plus-minus."""
    s = s.replace("₀", "0")                  # w SUBSCRIPT ZERO -> w0
    s = s.replace("μ", "µ")             # GREEK MU -> MICRO SIGN
    s = re.sub(r"\bum\b", "µm", s)
    s = s.replace("≈", "~").replace("≃", "~").replace("∼", "~")
    s = s.replace("+/-", "±").replace("+-", "±")
    return s


def _svg_text_runs(rel):
    """The human-readable runs of an SVG: <text> content including nested
    tspans, plus <title> and <desc>. Attributes, geometry and XML comments
    never enter, so coordinates and colour codes cannot false-positive."""
    root = ET.parse(ROOT / rel).getroot()
    runs = []
    for el in root.iter():
        if isinstance(el.tag, str) and el.tag.rsplit("}", 1)[-1] in ("text", "title", "desc"):
            runs.append(_normalize(" ".join("".join(el.itertext()).split())))
    return runs


# --------------------------------------------------------------------------- #
# THE REGISTRY.  Each entry:                                                    #
#   name      : human label                                                     #
#   canonical : the allowed values, derived live from the SSOT                  #
#   source    : where the truth lives, quoted in the failure message            #
#   find      : regex (post-normalization) capturing the number at each quote   #
# Every capture in every tracked SVG must equal one canonical value.            #
# --------------------------------------------------------------------------- #
_NUM = r"([0-9]+(?:\.[0-9]+)?)"

SVG_QUANTITIES = [
    dict(
        name="beam waist (µm)",
        canonical=lambda: [K.W0_MEASURED_M * 1e6],
        source="rb5s6s.constants.W0_MEASURED_M, the adopted Rajasree-lineage prior",
        find=re.compile(rf"(?:\bw0\b|waist)[^0-9]{{0,12}}{_NUM}\s*µm", re.I),
    ),
    dict(
        name="retro amplitude ratio rho",
        canonical=lambda: [K.RHO_RETRO],
        source="rb5s6s.constants.RHO_RETRO, assumed rather than asserted at 1",
        find=re.compile(rf"(?:ρ|\brho\b)[^0-9±]{{0,12}}{_NUM}", re.I),
    ),
    dict(
        name="rho one-sigma uncertainty",
        canonical=lambda: [K.RHO_RETRO_ERR],
        source="rb5s6s.constants.RHO_RETRO_ERR",
        find=re.compile(rf"(?:ρ|\brho\b)[^±]{{0,16}}±\s*{_NUM}", re.I),
    ),
    dict(
        # 12.5 is both the EOM drive and the transition-axis tooth spacing,
        # 6.25 is the laser-axis tooth spacing. Any other MHz figure on a
        # drawing is either stale or a new quantity to register here.
        name="comb frequency (MHz)",
        canonical=lambda: [K.OMEGA_EOM_HZ / 1e6, K.TOOTH_SPACING_LASER_HZ / 1e6],
        source="rb5s6s.constants.OMEGA_EOM_HZ and TOOTH_SPACING_LASER_HZ",
        find=re.compile(rf"{_NUM}\s*MHz(?!\s*/)"),
    ),
    dict(
        # 4 MHz/min is the archival envelope constant. 0.02 MHz/min is the
        # in-campaign held-lock bound quoted by README and BIG_PICTURE (the
        # +0.016 [+0.007, +0.025] state-space fit, results report addenda).
        # That one has no CSV to read, so it is the registry's one literal.
        name="drift rate (MHz/min)",
        canonical=lambda: [K.DRIFT_RATE_LASER_HZ_PER_MIN / 1e6, 0.02],
        source="rb5s6s.constants.DRIFT_RATE_LASER_HZ_PER_MIN (envelope) and the "
               "held-lock bound of order 0.02 MHz/min (README, BIG_PICTURE)",
        find=re.compile(rf"{_NUM}\s*MHz\s*/\s*min"),
    ),
]

_BY_NAME = {q["name"]: q for q in SVG_QUANTITIES}


def _violations(runs):
    bad = []
    for q in SVG_QUANTITIES:
        allowed = q["canonical"]()
        for run in runs:
            for m in q["find"].finditer(run):
                x = float(m.group(1))
                if not any(abs(x - c) <= 1e-9 * max(1.0, abs(c)) for c in allowed):
                    bad.append(f"{q['name']}: {m.group(0)!r} is not one of "
                               f"{[f'{c:g}' for c in allowed]} ({q['source']})")
    return bad


def test_the_scan_reaches_the_schematic_and_reads_its_waist():
    """Vacuity guard doubling as an extraction self-test. If the schematic is
    moved, renamed or stops quoting the measured waist (the one number every
    absolute result rides on), or if the text extraction silently breaks, the
    whole file would otherwise pass while checking nothing."""
    svgs = _tracked_svgs()
    assert SCHEMATIC in svgs, (
        f"{SCHEMATIC} is no longer a tracked SVG. If the drawing moved, update "
        f"SCHEMATIC here too.")
    runs = _svg_text_runs(SCHEMATIC)
    hits = [m for r in runs for m in _BY_NAME["beam waist (µm)"]["find"].finditer(r)]
    assert hits, (
        "the schematic no longer quotes the beam waist, or the SVG text "
        "extraction broke. If the label was removed deliberately, update this "
        "guard together with the drawing.")


def test_svg_numbers_match_the_canonical_registry():
    bad = []
    for rel in _tracked_svgs():
        bad += [f"{rel}: {v}" for v in _violations(_svg_text_runs(rel))]
    assert not bad, (
        "a hand-authored SVG quotes a physics number the SSOT does not "
        "support, which is how the schematic came to carry w0 ~ 50 um and "
        "rho ~ 1. Fix the drawing, or register a genuinely new "
        "quantity in SVG_QUANTITIES with its SSOT source:\n  "
        + "\n  ".join(bad))


# --------------------------------------------------------------------------- #
# Targeted tripwire: a replaced waist must not reappear even WITHOUT a       #
# w0/waist label to anchor the registry regex ("beam focused to 50 µm").        #
# Mirrors the REPLACED tripwire of test_docs_canonical.                       #
# --------------------------------------------------------------------------- #
_STALE_WAIST = re.compile(r"\b(?:50|32)\s*µm")
_ALLOW_STALE = re.compile(r"supersed|naive|was |earlier|excluded|not ", re.I)


def test_no_superseded_waist_value_in_any_svg():
    hits = []
    for rel in _tracked_svgs():
        for run in _svg_text_runs(rel):
            if _STALE_WAIST.search(run) and not _ALLOW_STALE.search(run):
                hits.append(f"{rel}: {run[:80]!r}")
    assert not hits, (
        "a replaced waist value (the stale 50 or the naive 32) reappears on "
        "a drawing without being marked replaced:\n  " + "\n  ".join(hits))


# --------------------------------------------------------------------------- #
# Self-tests: a stale label must raise a violation in every notation a drawing #
# might use, and the corrected labels must not. These keep the regexes honest   #
# against notation drift without touching the tracked drawing.                  #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("planted", [
    "w₀ ~ 50 µm",              # the stale waist label, as drawn
    "w0 ~ 50 um",                   # ascii variant
    "waist 32 µm",                  # the replaced naive estimate
    "ρ ~ 1",                        # rho asserted rather than assumed
    "rho = 1",
    "(ρ 0.94 ± 0.05 assumed)",      # right value, wrong uncertainty
    "teeth every 6.3 MHz",
    "drift 1 MHz/min",
])
def test_planted_stale_value_is_caught(planted):
    assert _violations([_normalize(planted)]), (
        f"the registry no longer catches the stale label {planted!r}")


def test_planted_canonical_labels_pass():
    ok = ["w₀ ≈ 64 µm", "(ρ 0.94 ± 0.04 assumed)", "12.5 MHz resonant",
          "AFG31021, 12.5 MHz, 10 Vpp", "6.25 MHz between teeth",
          "drift envelope 4 MHz/min",
          "f = 150 mm", "70-130 °C, foil-wrapped"]   # out of scope, must not trip
    bad = _violations([_normalize(s) for s in ok])
    assert not bad, f"a correct or out-of-scope label now trips the guard: {bad}"

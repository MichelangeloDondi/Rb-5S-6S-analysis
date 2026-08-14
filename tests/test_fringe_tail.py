"""
The fringe-tail MC (rb5s6s/fringe_tail.py) must reproduce the ground-truth
standing-wave numbers: the fringe modulation is symmetric so the MEAN pull is
preserved, but it suppresses the ramp skew by an amount that is negligible at a
large archival waist and material at the small (config S) 16 um waist, and both
the skew suppression and the variance inflation scale with the fringe-modulation
variance. The single-block estimator at the reference draw reproduces the
earlier direct Monte-Carlo to the digit; pooling blocks tames the third-moment
noise into a stable, byte-reproducible fact.

The last section pins the SIZE of that suppression, as every document quotes it,
to the committed results/fringe_tail.csv.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pytest

from rb5s6s.constants import TAU_6S_S
from rb5s6s.fringe_tail import fringe_tail_mc

ROOT = Path(__file__).resolve().parents[1]

# Frozen ANCHOR geometries, not the live configuration: 50 um / 0.6 MHz is the
# waist the earlier direct Monte-Carlo was run at, kept so the estimator can be
# checked against it to the digit. The committed CSV is produced at
# config.W0_MEASURED_M (64 um) -- see scripts/run_fringe_tail.py.
_RECORD = dict(w0_m=50e-6, s0_mhz=0.6)
_SMALL = dict(w0_m=16e-6, s0_mhz=5.7)

# The intrinsic standardized skew of the triangular ramp, 18^1.5/135 = +0.566.
G1_TRIANGLE = 18 ** 1.5 / 135


def test_reproduces_reference_direct_mc_at_the_anchor_draw():
    # one 3e5-atom block at the reference seed reproduces the earlier direct MC:
    # d_skew -0.038 (archival) and -0.143 (config S).
    a = fringe_tail_mc(**_RECORD, rho=1.0, seed=7, n_atoms=300_000)
    o = fringe_tail_mc(**_SMALL, rho=1.0, seed=7, n_atoms=300_000)
    assert a["d_skew"] == pytest.approx(-0.0382, abs=1e-3), a
    assert o["d_skew"] == pytest.approx(-0.1429, abs=1e-3), o


def test_mean_pull_preserved_by_the_symmetric_fringe():
    # E[x] = 0 for the fringe modulation, so the centroid pull is unchanged
    # (the fringe preserves the mean). The transit path factor is sqrt(2/3) ~ 0.816 and the
    # wedge centroid is -(2/3) sqrt(2/3) S0 ~ -0.544 S0.
    r = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=300_000, n_blocks=4, seed=1)
    assert r["mean_over_s0"] == pytest.approx(r["mean_nofringe_over_s0"],
                                              abs=2e-3), r
    assert r["kappa_path"] == pytest.approx(np.sqrt(2.0 / 3.0), abs=2e-3), r
    assert r["mean_over_s0"] == pytest.approx(-(2.0 / 3.0) * np.sqrt(2.0 / 3.0),
                                              abs=3e-3), r


@pytest.mark.slow
def test_skew_suppressed_and_scales_with_waist():
    a = fringe_tail_mc(**_RECORD, rho=1.0, n_atoms=10 ** 6, n_blocks=8, seed=1)
    o = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=10 ** 6, n_blocks=8, seed=1)
    # suppression is negative (same sign as the divergence rider), and larger at
    # the small (config S) waist than at the archival waist
    assert a["d_skew"] < 0.0 and o["d_skew"] < 0.0, (a, o)
    assert o["d_skew"] < a["d_skew"], (a["d_skew"], o["d_skew"])
    # seed-robust magnitudes: ~-0.05 archival, ~-0.16 config S
    assert a["d_skew"] == pytest.approx(-0.052, abs=0.012), a
    assert o["d_skew"] == pytest.approx(-0.156, abs=0.018), o
    # config-S suppression is a material fraction of the +0.566 triangle skew
    assert abs(o["d_skew"]) > 0.20 * 0.5657, o


@pytest.mark.slow
def test_third_cumulant_and_variance_coefficients():
    # the memory's leverages, in the convention f_res = 2 Var(x): the variance
    # inflation (as a fraction of the un-inflated wedge variance) is +4.5 f_res,
    # and the third-cumulant identity is exact.
    o = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=10 ** 6, n_blocks=8, seed=1)
    f_res = 2.0 * o["f_res_var"]
    exc_over_var0 = (o["var"] - o["var_nofringe"]) / o["var_nofringe"]
    assert exc_over_var0 / f_res == pytest.approx(4.5, abs=0.3), o
    # the standardized-skew leverage is negative and O(-10) per f_res
    assert -14.0 < o["d_skew"] / f_res < -8.0, o


def test_shorter_coherence_window_resolves_more_fringe():
    # capping the window at tau_6S (< the config-S transit) leaves more fringe
    # unaveraged -> larger resolved fraction and larger third-cumulant change
    trans = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=300_000, n_blocks=4, seed=1)
    tau6s = fringe_tail_mc(**_SMALL, rho=1.0, coherence_s=TAU_6S_S,
                           n_atoms=300_000, n_blocks=4, seed=1)
    assert tau6s["window_frac"] > trans["window_frac"], (trans, tau6s)
    assert tau6s["frac_resolved"] > trans["frac_resolved"], (trans, tau6s)
    assert abs(tau6s["d_kappa3"]) > abs(trans["d_kappa3"]), (trans, tau6s)


def test_byte_reproducible_at_fixed_seed():
    a = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=50_000, n_blocks=3, seed=7)
    b = fringe_tail_mc(**_SMALL, rho=1.0, n_atoms=50_000, n_blocks=3, seed=7)
    assert a["d_skew"] == b["d_skew"] and a["kappa3"] == b["kappa3"]


# --------------------------------------------------------------------------
# Docs <-> results/fringe_tail.csv sync for the quoted skew suppression.
#
# The stale-number incident this pins (2026-08-09): six sites quoted the
# suppression, in three values and two conventions. "~5-8%" (constants.py,
# stalnaker2006.md) was |d_skew| itself, an absolute change in a dimensionless
# skew, carrying a percent sign, computed at the retired 50 um waist; "9-14%"
# (THEORY_NOTE, LITERATURE) was |d_skew|/g1 at that same retired waist; "~25%"
# was the 16 um figure a waist earlier. Only "26-28%" was current, and no site
# said what the percentage was OF. The one convention is |d_skew| over the
# intrinsic triangle skew g1; every site that states a number is pinned to the
# committed CSV here, and rb5s6s/constants.py states the convention instead of
# restating the number. The same failure and the same fix as the g1 sign-flip
# tables in tests/test_ramp_geometry_docs.py.
# --------------------------------------------------------------------------
def _suppression_pct(prefix: str) -> str:
    """The rounded |d_skew|/g1 range for one regime, read from the CSV."""
    with open(ROOT / "results" / "fringe_tail.csv", encoding="utf-8") as fh:
        v = [abs(float(r["value"])) / G1_TRIANGLE * 100.0
             for r in csv.DictReader(fh)
             if r["quantity"] == "d_skew" and r["key"].startswith(prefix)]
    assert v, f"no d_skew rows for regime {prefix!r} in results/fringe_tail.csv"
    return f"{min(v):.0f}-{max(v):.0f}%"


# (document, regime key prefixes it quotes: "2025_" = the measured w0, "S_" = 16 um)
SUPPRESSION_SITES = [
    ("docs/RESULTS.md", ("S_",)),
    ("docs/PLAN.md", ("S_",)),
    ("results/README.md", ("S_",)),
    ("docs/THEORY_NOTE.md", ("2025_", "S_")),
    ("docs/LITERATURE.md", ("2025_", "S_")),
    ("docs/lit/stalnaker2006.md", ("2025_", "S_")),
]


@pytest.mark.parametrize("relpath,prefixes", SUPPRESSION_SITES)
def test_quoted_skew_suppression_matches_the_committed_csv(relpath, prefixes):
    txt = (ROOT / relpath).read_text(encoding="utf-8")
    for prefix in prefixes:
        want = _suppression_pct(prefix)
        # both dash conventions: the generated ledger writes ASCII, the prose
        # documents write an en-dash
        if not any(w in txt for w in (want, want.replace("-", "–"))):
            raise AssertionError(
                f"{relpath} does not carry the computed {prefix.rstrip('_')} "
                f"suppression {want}. results/fringe_tail.csv is the source; "
                f"docs/RESULTS.md is generated, so fix "
                f"scripts/make_results_ledger.py and regenerate it.")


def test_constants_cites_the_computed_source_rather_than_restating_it():
    """constants.py carries the PHYSICS of the fringe tail, not its size. A
    number in a module docstring is the one nothing regenerates, and this one
    went two waists stale in two conventions before anyone read it against the
    CSV. It must now name the file that holds the number and the normalisation
    used to read it, and state no range of its own."""
    txt = (ROOT / "rb5s6s" / "constants.py").read_text(encoding="utf-8")
    para = txt.split("Fringe averaging (Stalnaker")[1].split('"""')[0]
    for cite in ("rb5s6s/fringe_tail.py", "results/fringe_tail.csv", "d_skew"):
        assert cite in para, f"the fringe note no longer cites {cite}"
    assert "18^1.5/135" in para, \
        "the normalisation must be written out, not left to the reader"
    restated = re.findall(r"~?\s*\d+\s*-\s*\d+\s*%", para)
    assert not restated, \
        f"the fringe note restates a suppression range: {restated}"

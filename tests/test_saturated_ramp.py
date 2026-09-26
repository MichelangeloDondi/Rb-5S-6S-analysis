"""The saturated shift density: the weak limit is the triangle, and the band's node agrees with its
Monte Carlo through the axial mixture.

WHY THIS EXISTS (F131 to F133, 2026-09-17). Below about 56 um the model's ramp parted company with its own
Monte Carlo: at 40 um and 225 mW the third moment read 15 per cent off, and the separating variable was the
on-axis intensity, not the temperature. The producer's own weak-field arm agreed with the model at every node,
so the model's ramp WAS the weak-field ramp and the term the band needed was the saturation of the excitation
weight, p_sat(x) proportional to G(P x) / x.

WHAT THE FIRST VERSION OF THIS FILE ASSERTED, AND WHY IT WAS RED (the reproducibility seat, 2026-09-18).
It compared the TRANSVERSE density's mu3 ratio, 0.8890, against 1 - 0.1534 = 0.8466, and 0.8466 is F131's
mc-against-the-weak-field-MODEL reading, a different pair of numbers from the one F133 validated. F133
validated the derived density against the Monte Carlo's OWN saturated-over-weak-field ratio, which at this node
is -0.0032933 / -0.0038461 = 0.8562, and the transverse density lands 3.8 per cent from it -- F133's own
"max 0.0382" over 813 nodes, the factorisation error F133a states in the docstring. The old assertion was
therefore 5.0 per cent from a reference it should not have used, and it shipped to a board unrun because
`prefloor.sh` grades prose and doc surfaces and no gate ran beside this board (D3). Both halves of that are
findings of the round; this file is the repair.

Three failure modes, each its own test, and the second is the one that matters:
 1. the weak-drive limit returns `local_ramp_density` to 1e-6 WITH ITS SIGN, so a power in milliwatts (which
    puts the rate table five decades from saturation) reads as the triangle and a sign regression on
    `RAMP_SIDE` cannot pass hidden inside a magnitude comparison;
 2. AT THE NODE, through the axial mixture at its own z_ratio, the model agrees with the Monte Carlo inside the
    gate's own `ramp_mu3_rel` tolerance -- read from the committed `results/kernel_mc.csv`, which is what the
    kernel gate judges and what the Cell fits with;
 3. the transverse factorisation's error against the Monte Carlo's own ratio stays inside F133a's stated 4 per
    cent, which is the number the docstring carries, so a change that widens it fails here and not in a
    fifteen-minute node re-run.
"""
from __future__ import annotations

import csv
import pathlib

import numpy as np
import pytest

from rb5s6s import lineshape as L
from rb5s6s._compat import trapezoid

ROOT = pathlib.Path(__file__).resolve().parents[1]
X = np.linspace(0.0, 1.0, 4001)
#: 41.0, not 40.0 (C6c): 40 um sits below the bore's floor (about 40.87-40.89 um,
#: `beam_field.ClippedBeam`/`lineshape.aperture_onaxis_factor_actual`), so no kernel Monte Carlo
#: node can be built there any more; 41.0 is at or above the floor for both. The row itself is
#: still absent from the committed `results/kernel_mc.csv` at the fold's model digest, so this test
#: fails for a NAMED reason (needs a fresh node run) rather than at an unreachable waist.
NODE = "w41.0_m1.00_r0.940_T130_P225"

#: the Monte Carlo's own saturated-over-weak-field third moment at NODE, -0.0032933 / -0.0038461, from the
#: node's artefact under the live kernel cache. It is the reference F133 validated the derived density against
#: over 813 nodes (median 0.0000, max 0.0382). Carried as a number because `results/kernel_mc.csv` publishes
#: the saturated arm and the model, not the weak-field arm, and a test may not read `private/`.
MC_SAT_OVER_WEAK = 0.8562
FACTORISATION_ERR = 0.04          # F133a's stated error of the transverse factorisation at the deepest node


def _moments(x, p):
    a = trapezoid(p, x)
    m = trapezoid(x * p, x) / a
    mu2 = trapezoid((x - m) ** 2 * p, x) / a
    mu3 = trapezoid((x - m) ** 3 * p, x) / a
    return m, mu2, mu3


def test_the_weak_drive_limit_is_the_triangle_to_1e_6_with_its_sign():
    weak = L.local_ramp_density(X)
    sat = L.saturated_ramp_density(X, 1e-6, 40e-6, 130.0, 0.94)
    assert float(np.max(np.abs(sat - weak))) < 1e-6
    m, _mu2, mu3 = _moments(X, sat)
    assert abs(m - 2.0 / 3.0) < 1e-6
    # THE SIGN IS PINNED, NOT ABSOLUTED. The first version compared |mu3| with |ramp_mu3|, which a flipped
    # RAMP_SIDE passes -- the one regression class the commit before this one spent itself repairing.
    assert mu3 < 0.0, "the blue-sided triangle's third moment is negative (RAMP_SIDE, O27)"
    assert abs(mu3 - L.ramp_mu3(1.0)) < 1e-6


def test_the_mixture_moments_reproduce_the_axial_closed_form():
    weak = L.local_ramp_density(X)
    for zr in (0.26, 0.667):
        mm = L.ramp_mixture_moments(1.0, zr, X, weak)
        ma = L.stark_ramp_axial_moments(1.0, zr, n_photon=2)
        assert abs(mm["mean"] - ma["mean"]) < 1e-5
        assert abs(mm["var"] - ma["var"]) < 1e-5
        assert abs(mm["mu3"] - ma["skew_standardized"] * ma["var"] ** 1.5) < 1e-5
    mm0 = L.ramp_mixture_moments(1.0, 0.0, X, weak)
    assert abs(mm0["mean"] - 2.0 / 3.0) < 1e-4 and abs(abs(mm0["mu3"]) - 1.0 / 135.0) < 1e-5


def test_the_band_node_agrees_with_its_monte_carlo_through_the_mixture():
    """The claim the model actually rests on: at 40 um and 225 mW the recorded Monte Carlo and the recorded
    model agree inside the kernel gate's own `ramp_mu3_rel` tolerance. Read from the committed table."""
    from rb5s6s.kernel_gate import READINGS

    row = None
    with (ROOT / "results" / "kernel_mc.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["node"] == NODE and r["quantity"] == "ramp_mu3_rel":
                row = r
    assert row is not None, f"{NODE}'s ramp_mu3_rel row is absent from results/kernel_mc.csv"
    mc, model = float(row["mc"]), float(row["model"])
    assert mc < 0.0 and model < 0.0, "both are blue-sided third moments and negative (O27)"
    dev = abs(mc - model) / abs(model)
    assert dev < READINGS["ramp_mu3_rel"], (
        f"the node's Monte Carlo and model differ by {dev:.4f}, over the gate's "
        f"{READINGS['ramp_mu3_rel']}: the weak-field reference read 0.153 here before F133's term")


def test_the_transverse_factorisation_stays_inside_its_stated_error():
    """The derived density is TRANSVERSE and the gate's reference is the AXIAL mixture, so the factorisation
    carries an error F133a measured at 4 per cent at the deepest node. This pins it there, and pins that a
    unit slip in the power does NOT land inside it."""
    weak = L.local_ramp_density(X)
    sat = L.saturated_ramp_density(X, 0.225, 40e-6, 130.0, 0.94)
    _m, _mu2, mu3w = _moments(X, weak)
    _m, _mu2, mu3s = _moments(X, sat)
    ratio = mu3s / mu3w
    dev = abs(ratio - MC_SAT_OVER_WEAK) / MC_SAT_OVER_WEAK
    assert dev < FACTORISATION_ERR, (
        f"the transverse density's saturated-over-weak ratio is {ratio:.4f} against the Monte Carlo's "
        f"{MC_SAT_OVER_WEAK}, {dev:.4f} apart, over F133a's stated {FACTORISATION_ERR}")
    slipped = L.saturated_ramp_density(X, 225.0 * 1e-3 * 1e-3, 40e-6, 130.0, 0.94)   # a milliwatt-for-watt slip
    _m, _mu2, mu3x = _moments(X, slipped)
    assert abs(mu3x / mu3w - MC_SAT_OVER_WEAK) / MC_SAT_OVER_WEAK > FACTORISATION_ERR, (
        "a power five decades from saturation returns the triangle, and the triangle must NOT pass this test")


@pytest.mark.parametrize("power_w", [0.225, 0.125])
def test_saturation_lowers_the_mean_shift_and_the_density_stays_normalised(power_w):
    sat = L.saturated_ramp_density(X, power_w, 40e-6, 130.0, 0.94)
    assert abs(trapezoid(sat, X) - 1.0) < 1e-9
    assert sat[0] == 0.0 and np.all(sat >= 0.0)
    m, _, _ = _moments(X, sat)
    assert m < 2.0 / 3.0

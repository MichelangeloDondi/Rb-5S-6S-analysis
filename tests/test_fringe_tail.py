"""
The fringe-tail MC (rb5s6s/fringe_tail.py) must reproduce the ground-truth
standing-wave numbers: the fringe modulation is symmetric so the MEAN pull is
preserved, but it suppresses the ramp skew by an amount that is negligible at
the archival 50 um waist and material at the small (config S) 16 um waist, and both the
skew suppression and the variance inflation scale with the fringe-modulation
variance. The single-block estimator at the reference draw reproduces the
earlier direct Monte-Carlo to the digit; pooling blocks tames the third-moment
noise into a stable, byte-reproducible fact.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.constants import TAU_6S_S
from rb5s6s.fringe_tail import fringe_tail_mc

_ARCHIVAL = dict(w0_m=50e-6, s0_mhz=0.6)
_SMALL = dict(w0_m=16e-6, s0_mhz=5.7)


def test_reproduces_reference_direct_mc_at_the_anchor_draw():
    # one 3e5-atom block at the reference seed reproduces the earlier direct MC:
    # d_skew -0.038 (archival) and -0.143 (config S).
    a = fringe_tail_mc(**_ARCHIVAL, rho=1.0, seed=7, n_atoms=300_000)
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
    a = fringe_tail_mc(**_ARCHIVAL, rho=1.0, n_atoms=10 ** 6, n_blocks=8, seed=1)
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

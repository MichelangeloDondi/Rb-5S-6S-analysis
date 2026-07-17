"""
The 2D profile likelihood (rb5s6s/identifiability.width_profile_2d) must be a
faithful global complement to the local covariance: on synthetic data with
known widths, the profile map must cover the truth (dchi2 below a loose ~95%
gate of 9, slack over 5.99 against the ~5% statistical flake), place its
minimum on the truth's valley, and show a straight (non-banana) floor whose
slope matches the local covariance's own prediction -- and the pure-math
helpers (sub-grid argmin, valley floor) must be exact on analytic inputs. A
profile map that failed any of these would be worse than no map: it would lend
false global authority to the local picture.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency
from rb5s6s.identifiability import (width_identifiability, width_profile_2d,
                                    subgrid_argmin, valley_floor)

NU = to_frequency(np.arange(2000) * 0.5 - 500.0, 0.08514)
GC_TRUE, SL_TRUE, TR_TRUE = 0.4, 1.4, 1.2


def _synth(ntr=3, seed=3):
    rng = np.random.default_rng(seed)
    F, V = [], []
    for _ in range(ntr):
        c = rng.normal(0.0, 1.0)
        p = model_profile(NU - c, gamma_coll=GC_TRUE, sigma_laser_fwhm=SL_TRUE,
                          transit_fwhm=TR_TRUE, s0=0.0)
        v = p / p.max()
        sig = np.sqrt((3e-3) ** 2 + 2e-5 * np.maximum(v, 0.0))
        V.append(v + rng.normal(0.0, 1.0, len(v)) * sig); F.append(NU.copy())
    return F, V


def test_subgrid_argmin_exact_on_a_parabola():
    x = np.linspace(0.0, 2.0, 9)
    x0 = 0.83                                     # NOT on a grid node
    y = (x - x0) ** 2 + 5.0
    assert abs(subgrid_argmin(x, y) - x0) < 1e-9
    # argmin at an edge falls back to the node (no extrapolation)
    y_edge = (x - (-1.0)) ** 2
    assert subgrid_argmin(x, y_edge) == x[0]


def test_valley_floor_straight_line_recovered():
    # an analytic straight valley: dchi2 = ((gc - (a*sl + b)) / w)^2
    gc = np.linspace(0.0, 1.0, 41); sl = np.linspace(1.0, 2.0, 21)
    a, b, w = 0.5, -0.2, 0.05
    D = ((gc[None, :] - (a * sl[:, None] + b)) / w) ** 2
    fl = valley_floor(gc, sl, D, within=np.inf)
    assert abs(fl["ridge_slope"] - a) < 1e-3
    assert fl["banana_rms"] < 1e-6                # perfectly straight
    # a genuinely curved (quadratic) floor must be flagged by the RMS
    Dc = ((gc[None, :] - (2.0 * (sl[:, None] - 1.5) ** 2 + 0.2)) / w) ** 2
    flc = valley_floor(gc, sl, Dc, within=np.inf)
    assert flc["banana_rms"] > 5 * (gc[1] - gc[0])


@pytest.mark.slow
def test_profile_covers_truth_with_straight_floor():
    F, V = _synth()
    gcg = np.linspace(0.15, 0.65, 9)              # truth 0.40 mid-grid
    slg = np.linspace(1.15, 1.65, 7)              # truth 1.40 mid-grid
    p = width_profile_2d(F, V, law=None, gc_grid=gcg, sl_grid=slg,
                         transit_seed=TR_TRUE, nu_step=0.02)
    D = np.asarray(p["dchi2"])
    i_true = int(np.argmin(np.abs(np.asarray(p["sl_grid"]) - SL_TRUE)))
    j_true = int(np.argmin(np.abs(np.asarray(p["gc_grid"]) - GC_TRUE)))
    # the truth must lie inside (or at) the joint-95% region of its own data
    assert D[i_true, j_true] < 9.0, D[i_true, j_true]
    # the surface is a real map: the minimum is unique-ish and the far corner is excluded
    assert D.max() > 25.0, D.max()
    # THE consistency claim of the whole construction: in the Gaussian limit the
    # profile floor's slope equals the local covariance's marginal prediction
    # cov_gc_sl / var_sl -- with transit PROFILED the sign can differ from the
    # naive 2-width Voigt anticorrelation (less Gaussian pulls in more cuspy
    # transit, whose wings displace gamma_coll), so we test against the
    # covariance itself, not against a sign convention.
    fl = valley_floor(p["gc_grid"], p["sl_grid"], D, within=25.0)
    rloc = width_identifiability(F, V, law=None, seeds=(GC_TRUE, SL_TRUE, TR_TRUE))
    slope_pred = rloc["cov"][0][1] / rloc["cov"][1][1]
    assert np.sign(fl["ridge_slope"]) == np.sign(slope_pred), (fl, slope_pred)
    assert abs(fl["ridge_slope"] - slope_pred) < 0.5 * abs(slope_pred) + 0.1, \
        (fl["ridge_slope"], slope_pred)
    # and the valley is straight at this scale -- no banana
    assert fl["banana_rms"] < 2.0 * fl["gc_step"], fl

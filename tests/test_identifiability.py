"""
The identifiability analysis (rb5s6s/identifiability.py) must detect the known
width degeneracy: on synthetic data whose three widths all broaden the same
line, the fit must recover them but the covariance must show the split is
ill-constrained -- a large condition number, strong width-vs-width
anticorrelation, and a total-width direction far better constrained than the
split. This is the check that the degeneracy the analysis *claims* (why transit
is fixed and sigma_laser is a bound) is really present and really quantified.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency
from rb5s6s.identifiability import width_identifiability, WIDTHS

NU = to_frequency(np.arange(2000) * 0.5 - 500.0, 0.08514)


def _synth(gc=0.4, sl=1.4, tr=1.2, ntr=5, seed=3):
    rng = np.random.default_rng(seed)
    F, V = [], []
    for _ in range(ntr):
        c = rng.normal(0.0, 1.0)
        p = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=sl, transit_fwhm=tr, s0=0.0)
        v = p / p.max()
        sig = np.sqrt((3e-3) ** 2 + 2e-5 * np.maximum(v, 0.0))
        V.append(v + rng.normal(0.0, 1.0, len(v)) * sig); F.append(NU.copy())
    return F, V


@pytest.mark.slow
def test_width_split_is_ill_conditioned_but_total_is_not():
    r = width_identifiability(*_synth())
    gc_i = WIDTHS.index("gamma_coll")
    tr_i = WIDTHS.index("transit")
    # the two Lorentzian-like widths trade off strongly -> the split is degenerate
    assert r["corr"][gc_i][tr_i] < -0.5, r["corr"]
    # ill-conditioned: one combination is essentially unconstrained
    assert r["condition_number"] > 50, r["condition_number"]
    # and the honest headline: the total width is far better constrained than the split
    assert r["worst_constrained_sigma"] > 5 * r["best_constrained_sigma"], r
    # the fit still recovers the injected widths (identifiable in aggregate)
    assert abs(r["fit"]["sigma_laser"] - 1.4) < 0.4

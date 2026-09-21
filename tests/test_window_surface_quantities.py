"""
The window surface's reference and its estimator return THE SAME QUANTITY (F274, 2026-09-21).

Three defects of one class fired in one day after the O33 rename from cumulants to moments, each found by a
downstream run and none by a guard: lookups keyed on the old prefix (F264), a second estimator in a harness
(F270), and this one, the noiseless reference `_direct` returning the CUMULANT map under keys the estimator
`_estimate` fills with central MOMENTS, so every admission verdict compared mu_n with kappa_n. This module is the
guard: on a noiseless line with no baseline, `_direct` and `_estimate` are BOTH sampled on the same fine grid, ten
times the archive's own spacing, and agree order by order within the admission's own scaled tolerance, while a
reference that returns cumulants is refused by the same comparison. Both sides share the one grid ON PURPOSE
(`_grids()` also returns the archive's own coarser one, bound and unused in both tests below): putting the
estimator on the archive's grid instead would also test whether that coarser sampling resolves the window edge,
which it does not to a part in a thousand for an x^6-weighted moment (0.7 per cent of mu2^3 at 5 MHz for this
line) -- a real, separate failure mode the admission machinery already names as "unresolved at the archive's
sampling" elsewhere, and one this guard must not answer by accident while asking only whether the reference and
the estimator compute the same quantity.
"""
from __future__ import annotations

import numpy as np
import pytest

from conftest import load_script_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = load_script_module("run_window_surface", ROOT / "scripts" / "run_window_surface.py")
ORDERS = (2, 3, 4, 5, 6, 7)
TOL = 1e-3          # the admission's own tolerance, scaled by mu2^(n/2)


def _line(x):
    """A skewed, narrow line whose far strips carry nothing, so the strip baseline is inert."""
    return np.exp(-0.5 * (x / 1.3) ** 2) + 0.25 * np.exp(-0.5 * ((x - 0.8) / 0.9) ** 2)


def _grids():
    coarse = np.arange(-40.0, 40.0 + 1e-9, 0.04)
    fine = np.arange(-40.0, 40.0 + 1e-9, 0.004)
    return coarse, fine


def _scaled_gap(a, b, W):
    mu2 = abs(b[2])
    return {n: abs(a[n] - b[n]) / mu2 ** (n / 2.0) for n in ORDERS}


@pytest.mark.parametrize("W", (2.0, 5.0, 13.0))
def test_the_reference_and_the_estimator_are_the_same_quantity(W):
    # BOTH ON THE FINE GRID: the subject is the QUANTITY, and the archive grid's own failure to resolve an
    # x^6-weighted window edge (0.7 per cent of mu2^3 at 5 MHz for this line) is what the admission refuses as
    # "unresolved at the archive's sampling", a different question this guard must not answer by accident
    _coarse, fine = _grids()
    ref = WS._direct(fine, _line(fine), W, ORDERS)
    est = WS._estimate(fine, _line(fine), W, ORDERS)
    gaps = _scaled_gap(ref, est, W)
    worst = max(gaps, key=gaps.get)
    assert gaps[worst] < TOL, (f"at W = {W:g} MHz order {worst} the reference and the estimator differ by "
                               f"{gaps[worst]:.3g} of mu2^(n/2): they are not the same quantity (F274)")


def test_a_reference_returning_cumulants_is_refused_by_the_same_comparison():
    """The negative plant: F274's own defect, a cumulant map returned under the moment keys, fails the comparison
    above at fourth order, so the guard discriminates and is not passing by construction."""
    _coarse, fine = _grids()
    W = 5.0
    mu = WS._direct(fine, _line(fine), W, (2, 3, 4))
    as_cumulant = dict(mu)
    as_cumulant[4] = mu[4] - 3.0 * mu[2] ** 2          # kappa4, what the reference used to return
    est = WS._estimate(fine, _line(fine), W, (2, 3, 4))
    gap4 = abs(as_cumulant[4] - est[4]) / abs(est[2]) ** 2
    assert gap4 > 100 * TOL, gap4

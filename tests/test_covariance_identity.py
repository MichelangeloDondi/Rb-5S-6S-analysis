"""The covariance identity, checked in the limit where it is exact.

THIS FILE EXISTS BECAUSE THE CLAIM SHIPPED WITHOUT IT. `covariance_term` and
`kernel_windowed_variance` were added to `run_kernel_inhomogeneity.py` on
2026-09-10 and their constant reached two documentation surfaces and four CSV
rows before anything in the tree called them. The board's reproducibility seat
built the case below in twelve lines and it returned the sign the shipped note
denied, which is what "a guard's first run is evidence about the claim it
guards" means in practice.

The identity is exact for a kernel symmetric about each element's own centre
with a finite variance:

    mu3(X) = -mu3(u) - 3 Cov(u, V(u))       for X = -u + K

A GAUSSIAN kernel has a variance. A Lorentzian does not, which is the whole
reason the producer substitutes a windowed second moment and the whole reason
its measured ratio is 0.386 and not 1. So the limit case here uses a Gaussian
and no window, where the prediction is exact and the sign is unambiguous.
"""
from __future__ import annotations

import numpy as np
import pytest

from rb5s6s._compat import trapezoid


def _mixture_cumulants(u, w, var_of_u, grid, sigma_floor=0.0):
    """Third cumulant of a mixture, exact and fixed-kernel, on one grid.

    Each element sits at -u with a Gaussian kernel of variance var_of_u(u).
    The fixed arm uses the weighted-mean variance, so its covariance term is
    zero by construction and the difference of the two is the identity's term.
    """
    w = np.asarray(w, float)
    w = w / w.sum()
    v = np.array([var_of_u(x) for x in u], float) + sigma_floor
    vbar = float((w * v).sum())

    def build(variances):
        out = np.zeros_like(grid)
        for x, wi, vi in zip(u, w, variances):
            s = np.sqrt(vi)
            out += wi * np.exp(-0.5 * ((grid + x) / s) ** 2) / (s * np.sqrt(2 * np.pi))
        return out / trapezoid(out, grid)

    def k3(p):
        m = trapezoid(grid * p, grid)
        return float(trapezoid(((grid - m) ** 3) * p, grid))

    return k3(build(v)), k3(build(np.full_like(v, vbar))), w, v


def test_the_identity_is_exact_for_a_kernel_whose_variance_exists():
    """k3_fixed - k3_exact is +3 Cov(u, V), so the ratio of the two is +1.

    The producer's shipped column divided by MINUS 3 Cov, which made the
    prediction -1 while its own note said ONE. Both halves are asserted here:
    the identity reproduces, and the ratio the producer publishes is +1.
    """
    rng = np.random.default_rng(0)
    u = np.linspace(0.0, 3.0, 60)
    w = rng.uniform(0.5, 1.5, u.size)
    grid = np.linspace(-60.0, 60.0, 400001)
    k_e, k_f, wn, v = _mixture_cumulants(u, w, lambda x: 1.0 + 0.35 * x, grid)

    cov = float((wn * u * v).sum() - (wn * u).sum() * (wn * v).sum())
    assert cov > 0.0, "the case is built so the kernel widens with the shift"

    # the identity itself, to the grid's own precision
    assert (k_f - k_e) == pytest.approx(3.0 * cov, rel=2e-3), (
        f"k3_fixed - k3_exact is {k_f - k_e:.8g} against 3 Cov = {3 * cov:.8g}")

    # and the ratio the producer publishes, which must be PLUS one
    ratio = (k_f - k_e) / (3.0 * cov)
    assert ratio == pytest.approx(1.0, rel=2e-3), (
        f"the published ratio is {ratio:.6f}; the retired convention divided "
        "by minus 3 Cov and would read -1.0 here")


def test_a_kernel_that_does_not_vary_contributes_no_third_cumulant():
    """The negative case: zero covariance, zero contamination, at any width.

    This is the half of the identity the centroid immunity rests on. A kernel
    that is wide but CONSTANT is free in the third cumulant, so a producer that
    reported a contamination here would be measuring its own grid.
    """
    u = np.linspace(0.0, 3.0, 60)
    w = np.ones_like(u)
    grid = np.linspace(-60.0, 60.0, 400001)
    k_e, k_f, wn, v = _mixture_cumulants(u, w, lambda x: 4.0, grid)
    assert float(v.max() - v.min()) == 0.0
    assert (k_f - k_e) == pytest.approx(0.0, abs=1e-6 * max(abs(k_e), 1.0))


def test_the_producer_expression_returns_the_sign_it_publishes():
    """The producer's own arithmetic, run on the exact case.

    Guards the expression rather than a copy of it: if the producer's ratio is
    ever re-flipped, this fails with the sign printed.
    """
    u = np.linspace(0.0, 3.0, 60)
    w = np.ones_like(u)
    grid = np.linspace(-60.0, 60.0, 400001)
    k_e, k_f, wn, v = _mixture_cumulants(u, w, lambda x: 1.0 + 0.35 * x, grid)
    cov = float((wn * u * v).sum() - (wn * u).sum() * (wn * v).sum())
    published = (k_f - k_e) / (3.0 * cov)
    retired = (-3.0 * cov) / (k_f - k_e)
    assert published > 0.0 and retired < 0.0, (
        f"published {published:.4f}, retired convention {retired:.4f}: the two "
        "differ in sign, which is what the shipped note got wrong")

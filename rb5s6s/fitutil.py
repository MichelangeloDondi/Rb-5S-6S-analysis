"""
Shared fit utilities
====================

Robust parameter covariance from a least_squares Jacobian.
"""

from __future__ import annotations

import numpy as np


def feasible_p0(p0, lo, hi):
    """Project a seed vector into [lo, hi] before least_squares.

    scipy's least_squares HARD-RAISES 'x0 is infeasible' if any seed violates
    a bound -- so a single mis-seeded block would crash a whole global fit.
    Clipping projects the seed into the feasible box so the
    optimizer starts legally and degrades gracefully. A tiny inward margin
    keeps the seed strictly interior (scipy dislikes seeds exactly on a bound
    for some methods)."""
    p0 = np.asarray(p0, float)
    lo = np.asarray(lo, float)
    hi = np.asarray(hi, float)
    span = np.where(np.isfinite(hi - lo), hi - lo, 0.0)
    eps = np.where(span > 0, 1e-9 * span, 0.0)
    return np.minimum(np.maximum(p0, lo + eps), hi - eps)


def cov_from_jac(jac: np.ndarray) -> np.ndarray:
    """Covariance (J^T J)^-1 via SVD, WITHOUT forming J^T J.

    Forming J^T J squares the condition number and, when parameters span very
    different scales (amplitudes ~1, centers ~MHz, beta_self ~0.1 multiplied
    by densities ~10), overflows/loses precision (observed on the M4 global
    fit). SVD of J directly, with tiny singular values truncated, is the
    standard robust route (this is what scipy.optimize.curve_fit does).
    """
    _, s, VT = np.linalg.svd(jac, full_matrices=False)
    thresh = np.finfo(float).eps * max(jac.shape) * (s[0] if s.size else 0.0)
    # divide ONLY the safe singular values (np.where would evaluate 1/s for
    # the zero entries too, raising a divide warning)
    s_inv2 = np.zeros_like(s)
    good = s > thresh
    s_inv2[good] = 1.0 / s[good] ** 2
    # Genuinely unconstrained nuisance directions (e.g. a background slope on
    # a flat trace) give legitimately huge variances; forming the full matrix
    # can overflow in BLAS (mislabeled "divide by zero"). The truncation above
    # is correct and the well-constrained diagonal entries we actually read
    # (beta, sigma_laser, delta) are finite -- so suppress that internal noise.
    with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
        cov = (VT.T * s_inv2) @ VT
    return cov

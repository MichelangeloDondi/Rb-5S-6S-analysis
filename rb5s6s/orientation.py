"""
The sweep direction of a trace as a latent sign, and the likelihood that carries it
====================================================================================

Owner order O69 (2026-09-27): "you have to check for each trace the sign of the symmetry and then take it into
account for the join fit".

THE PROBLEM. The 2025 traces were taken with no trigger and on a random side of the scan (the owner, 2026-09-27),
while every trace's frequency axis is built as (t - mean t) times one positive rate per condition
(`scripts/run_ultra_joint.py`), so a trace swept downward enters every fit mirrored. An even function of the line
does not see it; every odd one does, with its sign flipped. A record reads T_i = s_i theta + lambda + e_i, where
theta is the asymmetry fixed in FREQUENCY, which flips with the direction s_i, and lambda is whatever is fixed in
TIME, which does not (the PhD Thesis session's reading, F591). A pooled odd statistic therefore estimates
lambda + (2p - 1) theta and never the line.

WHY NOT PICK EACH TRACE'S SIGN. Orienting each trace by the sign of its own asymmetry and then fitting selects the
sign on the noise: at a per-trace signal-to-noise of 0.2 it biases the magnitude away from zero by about 0.6 of a
standard error, and it manufactures an asymmetry from none (the PhD Thesis session's D37 and E37). The archive's odd
statistics sit in that regime for most traces.

WHAT THIS MODULE DOES. Each trace's likelihood is the average over both directions,
    L_i(theta) = p_plus L_i(theta | rising) + (1 - p_plus) L_i(theta | falling),
with p_plus = 1/2 when nothing marks the direction. In chi-square units (chi2 = -2 ln L up to a constant both
orientations share) `mixture_chi2` returns -2 ln of that average, stably for any gap, and `posterior_plus` the
probability that the trace ran rising. A least-squares fitter reaches the mixture's stationary point by
expectation-maximisation: at fixed weights w_i = posterior_plus it minimises
    sum_i [ w_i chi2_i(+) + (1 - w_i) chi2_i(-) ],
which is an ordinary weighted sum of squares, then updates the weights from the new chi-squares and repeats. A trace
whose shape is clear orients itself; a noisy one stays near one half and weighs both readings. What bias remains is
measured on the twin drawn with random directions and subtracted (plan v9, step 2).

The falling orientation is the recorded axis mirrored: with nu the axis built as rising, the optical detuning of a
falling trace is -nu, so its model is evaluated at `mirror(nu) - c` with its own profiled centre c.
"""
from __future__ import annotations

import numpy as np

__all__ = ["mixture_chi2", "posterior_plus", "mirror", "em_fixed_point"]


def _check_prior(p_plus: float) -> float:
    p = float(p_plus)
    if not 0.0 < p < 1.0:
        raise ValueError(f"p_plus must lie strictly between 0 and 1, got {p_plus!r}: a prior of 0 or 1 is a "
                         "known direction, which is the ordinary one-sign fit and not this likelihood")
    return p


def mixture_chi2(chi2_plus, chi2_minus, p_plus: float = 0.5):
    """-2 ln[p e^(-chi2_plus/2) + (1 - p) e^(-chi2_minus/2)], per element, stable for any gap.

    Equal inputs return that value exactly; a gap large against one returns the smaller input plus -2 ln of the
    prior of the orientation that fits better (2 ln 2 at p = 1/2), a constant common to every trace that cancels from any
    likelihood ratio."""
    p = _check_prior(p_plus)
    a = np.asarray(chi2_plus, float)
    b = np.asarray(chi2_minus, float)
    m = np.minimum(a, b)
    return m - 2.0 * np.log(p * np.exp(-(a - m) / 2.0) + (1.0 - p) * np.exp(-(b - m) / 2.0))


def posterior_plus(chi2_plus, chi2_minus, p_plus: float = 0.5):
    """P(rising | data) = p e^(-chi2_plus/2) / [p e^(-chi2_plus/2) + (1 - p) e^(-chi2_minus/2)], stably.

    The two orientations must carry the same parameters and the same constant terms (the noise law's log-
    determinant included when the fit carries one), or the gap is not a likelihood ratio."""
    p = _check_prior(p_plus)
    z = (np.asarray(chi2_minus, float) - np.asarray(chi2_plus, float)) / 2.0 + np.log(p / (1.0 - p))
    return np.exp(-np.logaddexp(0.0, -z))


def mirror(nu):
    """The detuning axis of the falling orientation, given the axis built as rising."""
    return -np.asarray(nu, float)


def em_fixed_point(chi2_fn, theta0, n_traces: int, p_plus: float = 0.5, minimise=None, tol: float = 1e-9,
                   max_iter: int = 200):
    """The expectation-maximisation loop, for a caller whose model is small enough to hand over whole.

    `chi2_fn(theta)` returns two arrays of length `n_traces`, the per-trace chi-squares of the rising and the
    falling orientation at theta. `minimise(objective, theta)` returns the theta minimising `objective`, a scalar
    function of theta (a bounded scalar search for a one-parameter model). Returns (theta, weights, iterations).
    The fitter in `scripts/run_ultra_joint.py` runs the same two steps inside its own outer loop instead, because
    its M-step is a least-squares solve with profiled centres."""
    if minimise is None:
        raise ValueError("em_fixed_point needs a minimiser: the M-step is the caller's model")
    # THE FIRST E-STEP COMES FROM THE START, never from even weights: at w = 1/2 for every trace the M-step
    # objective is symmetric in the asymmetry and returns zero, and zero is a fixed point the loop never leaves
    # (found by this module's own test on its first run). So the start must carry a nonzero asymmetry, and a
    # fitter runs several (the multi-start rule of plan v9, step 6).
    theta = theta0
    a0, b0 = chi2_fn(theta)
    w = posterior_plus(a0, b0, p_plus)
    if w.shape != (int(n_traces),):
        raise ValueError(f"chi2_fn returned {w.shape[0] if w.ndim else 1} traces, expected {n_traces}")
    for it in range(1, int(max_iter) + 1):
        w_fixed = w.copy()
        theta_new = minimise(lambda th: float(np.sum(w_fixed * chi2_fn(th)[0] + (1.0 - w_fixed) * chi2_fn(th)[1])),
                             theta)
        a, b = chi2_fn(theta_new)
        w = posterior_plus(a, b, p_plus)
        moved = float(np.max(np.abs(np.atleast_1d(np.asarray(theta_new, float) - np.asarray(theta, float)))))
        theta = theta_new
        if moved < tol:
            return theta, w, it
    return theta, w, int(max_iter)

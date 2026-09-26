"""Windowed, self-centred moments of a line, converged to a tolerance and
taken on the pedestal-subtracted trace.

The windowed moment is the record's shift channel (`docs/methods/10`): a
window of half-width W is centred on its own first moment by a fixed-point
iteration, and the central moments of the normalised trace inside it are the
estimator. Three producers carried their own copy of that iteration at a fixed
twenty passes with the trace clipped at zero and no baseline removed. This
module replaces the copies, and it exists because of what one of them did on a
POWER LADDER on 2026-09-06.

**Cumulants are retired from this module (owner order O49, 2026-09-22)**: it
carried `windowed_cumulants`, `windowed_cumulant` and `cumulants_from_central_moments`
until that day, converting the same central-moment array a caller could read
directly. `windowed_moments` below is the one estimator this module offers now.

**The fixed point is the line's own centroid, and the pedestal sets how fast
it is reached.** With a flat pedestal b under the line inside the window, the
window's mass is the line's area A plus the pedestal's 2bW, and one pass moves the
centre to (A mu + 2bW c) / (A + 2bW): the fixed point is mu, the line's
centroid, but the residual shrinks by the pedestal's share 2bW / (A + 2bW) per
pass. A bright line converges in a few passes; the lowest rung of a power
ladder, whose amplitude falls as the power squared while the detector offset
does not, converges slowly, and at twenty passes the centre still carries an
error delta.

**And a centring error on a pedestal is a fake third moment that grows as
the window cubed.** The pedestal's own third moment about its centre is zero;
about a point delta off it, the uniform's third moment is -delta W^2 per unit
mass, so the fake term is of order -(2bW / (A + 2bW)) delta W^2. Measured on
the twin's noiseless lowest rung (a beam at the retired waist convention, 50 mW, the 1 per cent offset
a third of the peak): at a 6 MHz half-width twenty passes read 0.0308e-3
where eighty passes read 0.0006e-3, and at 24 MHz they read 31.8e-3 where
eighty passes read -0.0012e-3, while the centre itself agreed to four
decimals; one rung lower, at 25 mW, the same twenty passes read 3.1e-3. An earlier window scan met the same class at a narrow window and answered it with a
convergence check; this module makes the check the estimator's own return
value.

**The pedestal also dilutes the normalisation, which bends a power law.** The
normalised trace inside the window includes the pedestal's mass, so the
estimator reads the line's moment times the line's SHARE of the window, and
along a power ladder that share is not constant. Subtracting the pedestal
first is what the standard analysis does with its per-trace baseline, and the
estimator does it here from the trace's own far wings.

Returned beside every value: the converged centre, the pass count, whether the
tolerance was reached, and the baseline removed. A caller that ignores the
flag has been told.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple, Union

import numpy as np

from ._compat import trapezoid

__all__ = ["wing_baseline", "linear_baseline", "windowed_moments"]


def linear_baseline(grid: np.ndarray, y: np.ndarray, strip_a, strip_b) -> np.ndarray:
    """A straight line through the medians of two strips of the trace, given as
    (lo, hi) in the grid's units, evaluated on the whole grid. Why a LINE and
    not a level: a modulation tooth tens of MHz from the line leaves a
    Lorentzian tail whose tilt across a 6 MHz window is a third moment of the
    same order as the ramp's own, because the cubic weight puts the window
    edges in control (measured 2026-09-06 at a 40 MHz spacing: a constant
    0.03 in normalised units against the ramp's 0.12 at the top rung and 0.0002
    at the bottom). The caller names strips that are clear of every line."""
    grid = np.asarray(grid, dtype=float); y = np.asarray(y, dtype=float)
    xs, ys = [], []
    for lo, hi in (strip_a, strip_b):
        m = (grid >= lo) & (grid <= hi)
        if not m.any():
            raise ValueError(f"linear_baseline: the strip ({lo}, {hi}) holds no grid point")
        xs.append(float(np.median(grid[m]))); ys.append(float(np.median(y[m])))
    slope = (ys[1] - ys[0]) / (xs[1] - xs[0])
    return ys[0] + slope * (grid - xs[0])


def wing_baseline(grid: np.ndarray, y: np.ndarray, fraction: float = 0.1) -> float:
    """The median of the trace over the outer `fraction` of the grid on each
    side, a pedestal estimate that a line, a noise realisation or a modulation
    tooth inside the body of the scan does not move."""
    grid = np.asarray(grid, dtype=float)
    span = grid.max() - grid.min()
    wings = (grid <= grid.min() + fraction * span) | (grid >= grid.max() - fraction * span)
    return float(np.median(np.asarray(y, dtype=float)[wings]))


def _centred_window_moments(grid: np.ndarray, y: np.ndarray, half_width: float, top: int, *,
                            baseline: Union[str, float, None] = "wings", n_points: int = 4001,
                            tol: float = 1e-7, max_passes: int = 400,
                            centre0: Optional[float] = None) -> Tuple[Optional[np.ndarray], Dict[str, float]]:
    """The quadrature behind `windowed_moments` (and, until O49 retired it, `windowed_cumulants`
    beside it): recentre the window on its own first moment by the fixed-point iteration, then
    return the central moments mu_1..mu_top (mu_1 ~ 0 by construction) of the normalised trace
    inside it. `top` is the HIGHEST order the caller wants, and it builds its own return from
    this ONE array, so the centring and the interpolation run once regardless of how the
    caller's `orders` is shaped. Returns `(None, info)` on any failure (a non-positive window, or
    a centring that walks the window off the trace) so a caller can build its own NaN dict for
    its own orders;
    `info` is passed straight through either way.

    `baseline` is "wings" (the default: `wing_baseline` of this trace), a number
    to subtract, None to take the trace as it is, or ("linear", (lo, hi),
    (lo, hi)) for `linear_baseline` through two strips the caller knows to be
    clear of every line, which removes the tilt a distant tooth's tail leaves
    across the window. The trace is NOT clipped at zero: clipping a noisy
    zero-mean baseline manufactures a positive pedestal of about 0.4 sigma,
    which is the dilution this module removes. The window is recentred until
    the centre moves by less than `tol` (in the grid's units) or `max_passes`
    is reached; the info dict carries `centre`, `passes`, `converged` (1.0
    or 0.0) and `baseline` (the level removed, or the linear baseline's median).
    """
    grid = np.asarray(grid, dtype=float)
    y = np.asarray(y, dtype=float)
    if isinstance(baseline, str) and baseline == "wings":
        b = wing_baseline(grid, y)
    elif baseline is None:
        b = 0.0
    elif isinstance(baseline, (tuple, list)) and len(baseline) == 3 and baseline[0] == "linear":
        line = linear_baseline(grid, y, baseline[1], baseline[2])
        y = y - line
        b = float(np.median(line))
        line = None
        baseline = "applied"
    else:
        b = float(baseline)
    if baseline != "applied":
        y = y - b
    w = float(half_width)
    c = float(centre0) if centre0 is not None else float(grid[np.argmax(y)])
    converged = False
    passes = 0

    def _outside(centre: float) -> bool:
        """True when the window would reach past the trace.

        WHY THIS REFUSES RATHER THAN CLAMPING. `np.interp` holds the end value
        for any abscissa outside the grid, so a window wider than the trace is
        filled with a constant equal to the last sample. That is not a tail: it
        is a rectangular pedestal whose third moment grows without bound, and
        the estimator previously returned it with `converged` set to one. On a
        +-60 MHz grid an asymmetric line gave mu3 = 0.855 at a 50 MHz
        half-width, -26.7 at 62 and -2778 at 120, converged at every step.
        The corruption begins BEFORE the edge, because `wing_baseline` reads a
        region the clamp has already flattened."""
        return (centre - w) < grid[0] or (centre + w) > grid[-1]

    if _outside(c):
        return None, {"centre": c, "passes": 0.0, "converged": 0.0,
                      "baseline": b, "in_span": 0.0}
    for passes in range(1, max_passes + 1):
        g = np.linspace(c - w, c + w, n_points)
        yy = np.interp(g, grid, y)
        s = trapezoid(yy, g)
        if s <= 0:
            return None, {"centre": c, "passes": float(passes), "converged": 0.0, "baseline": b}
        c_new = trapezoid(g * yy, g) / s
        moved = abs(c_new - c)
        c = c_new
        if _outside(c):
            # the centring wandered until the window left the trace
            return None, {"centre": c, "passes": float(passes),
                          "converged": 0.0, "baseline": b, "in_span": 0.0}
        if moved < tol:
            converged = True
            break
    g = np.linspace(c - w, c + w, n_points)
    yy = np.interp(g, grid, y)
    s = trapezoid(yy, g)
    if s <= 0:
        return None, {"centre": c, "passes": float(passes), "converged": 0.0, "baseline": b}
    yy = yy / s
    m1 = trapezoid(g * yy, g)
    mu = np.array([trapezoid((g - m1) ** k * yy, g) for k in range(1, top + 1)])
    return mu, {"centre": c, "passes": float(passes),
                "converged": 1.0 if converged else 0.0, "baseline": b,
                "in_span": 1.0}


def windowed_moments(grid: np.ndarray, y: np.ndarray, half_width: float, orders=(3, 5, 7), *,
                     baseline: Union[str, float, None] = "wings", n_points: int = 4001,
                     tol: float = 1e-7, max_passes: int = 400,
                     centre0: Optional[float] = None) -> Tuple[Dict[int, float], Dict[str, float]]:
    """The self-centred windowed CENTRAL MOMENTS of several orders from ONE centring
    (owner order O33, 2026-09-20, with the cumulant basis retired outright by O49,
    2026-09-22): the window, centring, baseline and convergence machinery of
    `_centred_window_moments`, selecting mu_n directly from its central-moment array.
    mu_2 == kappa_2 and mu_3 == kappa_3 exactly, so a value this function returns at
    those two orders is unchanged from what the retired cumulant conversion would have
    given; they diverge at order 4 and above, where kappa_n is a cancelling combination
    of mu_n and lower moments (F211: k4 crosses zero across the window grid for a
    Lorentzian while mu4, an absolute even moment, cannot). See `_centred_window_moments`
    for the window, the baseline conventions and the convergence report; a window whose
    integral is not positive returns NaN for every order, as the copies this module
    replaced did.

    F451: a non-integer order RAISES rather than being rounded to one. `_centred_window_moments`
    builds an array of INTEGER-order central moments and this function selects mu[o - 1] from it,
    so a caller asking for order 4.5 was silently handed mu_4 under the 4.5 key, a different
    statistic than the one named. A fractional order is a real, well-defined quantity (the
    closed-form check 3**(x / 2) / (x + 1) holds at x = 3.5, 4.5 and 6.5 too, not only at even
    integers), so the refusal names what a caller who wants one would still have to build:
    E|nu|^x for an even x, E[sign(nu) |nu|^x] for an odd x, neither of which this function
    computes today.
    """
    for o in orders:
        if float(o) != int(o):
            raise ValueError(
                f"windowed_moments: order {o!r} is not an integer. This function selects mu_n, a "
                "central moment, from an array built at integer orders only, and a fractional "
                "order would need E|nu|^x (even x) or E[sign(nu) |nu|^x] (odd x) built and "
                "validated on its own, never obtained by rounding to the nearest integer.")
    orders = tuple(int(o) for o in orders)
    nan = {o: float("nan") for o in orders}
    top = max(orders)
    mu, info = _centred_window_moments(grid, y, half_width, top, baseline=baseline,
                                       n_points=n_points, tol=tol, max_passes=max_passes,
                                       centre0=centre0)
    if mu is None:
        return nan, info
    values = {o: float(mu[o - 1]) for o in orders}
    return values, info

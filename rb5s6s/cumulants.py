"""Windowed, self-centred cumulants of a line, converged to a tolerance and
taken on the pedestal-subtracted trace.

The windowed cumulant is the record's shift channel (`docs/methods/10`): a
window of half-width W is centred on its own first moment by a fixed-point
iteration, and the central moments of the normalised trace inside it are the
estimator. Three producers carried their own copy of that iteration at a fixed
twenty passes with the trace clipped at zero and no baseline removed. This
module replaces the copies, and it exists because of what one of them did on a
POWER LADDER on 2026-09-06.

**The fixed point is the line's own centroid, and the pedestal sets how fast
it is reached.** With a flat pedestal b under the line inside the window, the
window's mass is the line's area A plus the pedestal's 2bW, and one pass moves the
centre to (A mu + 2bW c) / (A + 2bW): the fixed point is mu, the line's
centroid, but the residual shrinks by the pedestal's share 2bW / (A + 2bW) per
pass. A bright line converges in a few passes; the lowest rung of a power
ladder, whose amplitude falls as the power squared while the detector offset
does not, converges slowly, and at twenty passes the centre still carries an
error delta.

**And a centring error on a pedestal is a fake third cumulant that grows as
the window cubed.** The pedestal's own third moment about its centre is zero;
about a point delta off it, the uniform's third moment is -delta W^2 per unit
mass, so the fake term is of order -(2bW / (A + 2bW)) delta W^2. Measured on
the twin's noiseless lowest rung (a 64 um beam, 50 mW, the 1 per cent offset
a third of the peak): at a 6 MHz half-width twenty passes read 0.0308e-3
where eighty passes read 0.0006e-3, and at 24 MHz they read 31.8e-3 where
eighty passes read -0.0012e-3, while the centre itself agreed to four
decimals; one rung lower, at 25 mW, the same twenty passes read 3.1e-3. An earlier window scan met the same class at a narrow window and answered it with a
convergence check; this module makes the check the estimator's own return
value.

**The pedestal also dilutes the normalisation, which bends a power law.** The
normalised trace inside the window includes the pedestal's mass, so the
estimator reads the line's cumulant times the line's SHARE of the window, and
along a power ladder that share is not constant. Subtracting the pedestal
first is what the standard analysis does with its per-trace baseline, and the
estimator does it here from the trace's own far wings.

Returned beside every value: the converged centre, the pass count, whether the
tolerance was reached, and the baseline removed. A caller that ignores the
flag has been told.
"""
from __future__ import annotations

from math import comb
from typing import Dict, Optional, Tuple, Union

import numpy as np

from ._compat import trapezoid

__all__ = ["wing_baseline", "linear_baseline", "windowed_cumulant", "windowed_cumulants", "cumulants_from_central_moments"]


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


def cumulants_from_central_moments(mu: np.ndarray) -> np.ndarray:
    """Cumulants kappa_1..kappa_n from central moments mu_1..mu_n (mu_1 = 0),
    by kappa_n = mu_n - sum_{m=1}^{n-1} C(n-1, m-1) kappa_m mu_{n-m}. For n = 3
    this is mu_3 itself; for n = 5 it is mu_5 - 10 mu_2 mu_3."""
    mu = np.asarray(mu, dtype=float)
    kappa = np.zeros_like(mu)
    for n in range(1, mu.size + 1):
        s = 0.0
        for m in range(1, n):
            s += comb(n - 1, m - 1) * kappa[m - 1] * mu[n - m - 1]
        kappa[n - 1] = mu[n - 1] - s
    return kappa


def windowed_cumulants(grid: np.ndarray, y: np.ndarray, half_width: float, orders=(3, 5, 7), *,
                       baseline: Union[str, float, None] = "wings", n_points: int = 4001,
                       tol: float = 1e-7, max_passes: int = 400,
                       centre0: Optional[float] = None) -> Tuple[Dict[int, float], Dict[str, float]]:
    """The self-centred windowed cumulants of several orders from ONE centring.

    `baseline` is "wings" (the default: `wing_baseline` of this trace), a number
    to subtract, None to take the trace as it is, or ("linear", (lo, hi),
    (lo, hi)) for `linear_baseline` through two strips the caller knows to be
    clear of every line, which removes the tilt a distant tooth's tail leaves
    across the window. The trace is NOT clipped at zero: clipping a noisy
    zero-mean baseline manufactures a positive pedestal of about 0.4 sigma,
    which is the dilution this module removes. The window is recentred until
    the centre moves by less than `tol` (in the grid's units) or `max_passes`
    is reached; the second return carries `centre`, `passes`, `converged` (1.0
    or 0.0) and `baseline` (the level removed, or the linear baseline's median).
    A window whose integral is not positive returns NaN for every order, as the
    copies did.
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
    orders = tuple(int(o) for o in orders)
    c = float(centre0) if centre0 is not None else float(grid[np.argmax(y)])
    converged = False
    passes = 0
    nan = {o: float("nan") for o in orders}

    def _outside(centre: float) -> bool:
        """True when the window would reach past the trace.

        WHY THIS REFUSES RATHER THAN CLAMPING. `np.interp` holds the end value
        for any abscissa outside the grid, so a window wider than the trace is
        filled with a constant equal to the last sample. That is not a tail: it
        is a rectangular pedestal whose third moment grows without bound, and
        the estimator previously returned it with `converged` set to one. On a
        +-60 MHz grid an asymmetric line gave k3 = 0.855 at a 50 MHz
        half-width, -26.7 at 62 and -2778 at 120, converged at every step.
        The corruption begins BEFORE the edge, because `wing_baseline` reads a
        region the clamp has already flattened."""
        return (centre - w) < grid[0] or (centre + w) > grid[-1]

    if _outside(c):
        return nan, {"centre": c, "passes": 0.0, "converged": 0.0,
                     "baseline": b, "in_span": 0.0}
    for passes in range(1, max_passes + 1):
        g = np.linspace(c - w, c + w, n_points)
        yy = np.interp(g, grid, y)
        s = trapezoid(yy, g)
        if s <= 0:
            return nan, {"centre": c, "passes": float(passes), "converged": 0.0, "baseline": b}
        c_new = trapezoid(g * yy, g) / s
        moved = abs(c_new - c)
        c = c_new
        if _outside(c):
            # the centring wandered until the window left the trace
            return nan, {"centre": c, "passes": float(passes),
                         "converged": 0.0, "baseline": b, "in_span": 0.0}
        if moved < tol:
            converged = True
            break
    g = np.linspace(c - w, c + w, n_points)
    yy = np.interp(g, grid, y)
    s = trapezoid(yy, g)
    if s <= 0:
        return nan, {"centre": c, "passes": float(passes), "converged": 0.0, "baseline": b}
    yy = yy / s
    m1 = trapezoid(g * yy, g)
    top = max(orders)
    mu = np.array([trapezoid((g - m1) ** k * yy, g) for k in range(1, top + 1)])
    kappa = cumulants_from_central_moments(mu)
    values = {o: float(kappa[o - 1]) for o in orders}
    return values, {"centre": c, "passes": float(passes),
                    "converged": 1.0 if converged else 0.0, "baseline": b,
                    "in_span": 1.0}


def windowed_cumulant(grid: np.ndarray, y: np.ndarray, half_width: float, order: int = 3, *,
                      baseline: Union[str, float, None] = "wings", n_points: int = 4001,
                      tol: float = 1e-7, max_passes: int = 400,
                      centre0: Optional[float] = None) -> Tuple[float, Dict[str, float]]:
    """One order of `windowed_cumulants`, same arguments and same second return."""
    values, info = windowed_cumulants(grid, y, half_width, (order,), baseline=baseline, n_points=n_points,
                                      tol=tol, max_passes=max_passes, centre0=centre0)
    return values[order], info

"""C6c's coordinate infrastructure for the ultra-joint moment likelihood (owner O43, O46; plan A100,
A121, A129; rule W1) -- the answer to the owner's repeated question (O43, O46 on 2026-09-22) of why
chapter 7 uses the windowed moments only as diagnostics and never for parameter estimation: they were
never turned into a likelihood term. This module is that term's machinery, built as a NEW, standalone
package module per A129 ("outside kernel_gate.model_population(), so no node re-opens and no running
chain sees them"): nothing here is imported by any existing module, and nothing existing is edited.
The wiring into the Cell, the closure and the kernel gate is a LATER commit (A129's own words); this
module only has to be correct and tested on its own.

WHAT IS HERE, AND WHERE ITS RULES COME FROM (private/PLAN_2026-09-18_CONSOLIDATED.md unless noted):

(a) `windowed_moments_fixed_centre` -- central moments about a GIVEN, externally supplied centre,
    with exactly `rb5s6s.cumulants.windowed_moments`'s window, interpolation and quadrature
    conventions, but no re-centring iteration. F287 measured why this has to exist:
    `windowed_moments(centre0=...)` re-centres to the trace's OWN noisy centroid on its very first
    pass, so it cannot hold a centre fixed, and self-centring is F284's/F287's diagnosed CAUSE of the
    even moments' narrow-window bias (E[mu2_hat] = mu2 - Var(mu1_hat)): "mu2@0.5 bias/SE -5.17 and
    -4.84 self-centred against -0.05 and +1.10 on the known centre" (F287). A121: "a fixed-centre
    estimator added to rb5s6s.cumulants (a population module, so it rides a node re-run)" -- landing
    it there is deferred; it lives here instead, by A129's explicit instruction, so it is usable now.

(b) `cross_product_estimate` -- F284 point 2 / F287 point 2: a statistic that reuses one moment
    estimate more than once (mu3^2, the mu2^3 denominator, mu1^3, mu5*mu3) carries a self-correlation
    or self-variance term on a SINGLE replica (E[mu3_hat^2] = mu3^2 + Var(mu3_hat)); building it
    instead from a PRODUCT of two INDEPENDENT replicas (the up- and down-sweep of one trace, or two
    repeats) removes that term by construction: E[mu3_up mu3_down] = mu3^2. F287 measured the payoff:
    "mean |bias/SE| over the eight windows falls from 8.62 to 0.87 for mu3^2/mu2^3".

(c) The coordinate catalogue (`Coordinate`, `build_catalogue`, `s0_w0_power`, `raw_window_moment`,
    `window_derivative`, `tent_window_moment`) -- A100: orders 1 to 12 at each window; the owner's
    named ratios with their S0 power computed mechanically as the ratio's total order (F283, A100.6);
    window derivatives built from F297's closed form (Leibniz's rule on the RAW, un-normalised moment
    M_n(W) = integral (x-c)^n f(x) over [c-W, c+W]: dM_n/dW = W^n [f(c+W) + (-1)^n f(c-W)], fixed by
    the line's two edge values at every order, so the derivative family has RANK TWO across n and this
    module offers at most one even- and one odd-order representative per window, tagged so
    `select_coordinates` refuses the rest); and window integrals built as TENT-window moments (F297:
    "the integral of M_n over W from 0 to W_max is the n-th moment under a TENT window ... a different
    window shape and not a new statistic"), computed as one direct quadrature rather than as a
    numerical sum of `raw_window_moment` over a grid of W (the two are mathematically identical by
    Fubini's theorem -- swap the order of the x- and W-integrals -- and the direct form halves the
    numerical error for the same cost; `tests/test_moment_coords.py` checks the identity).

(d) `select_coordinates` -- rule W1's four admission clauses, applied at one noise level (the archive
    rung by default) to a twin-measured table of per-(coordinate, window) trials:
      (a) SE(bias) <= 0.2 x sd(statistic over replicas) (bought with replicas: R=25 gives it, R=100
          gives half of it);
      (b) the bias is FORECASTABLE across the truth grid (the twin table's own `forecast_ok`; a cell
          that fails this is a function bias(theta) to carry, not a number, and this module refuses
          it; a cell where forecastability has not yet been checked is carried DIAGNOSTIC, not
          refused, since W1(b) only refuses a cell that FAILS the check);
      (c) the statistic is above its numerical floor at that window (the halved-grid check; F218/F282:
          mu8 fails this at 21 MHz, mu12 above 1 MHz);
      (d) the leverage clause (A45.5): the sensitivity table gives the cell at least one per cent of
          the parameter's total information at the archive rung. A58: until that table exists, a cell
          with `leverage=None` reads `leverage_unmeasured` and is carried DIAGNOSTIC, never refused,
          unless the caller passes `require_leverage=True`.
    Then A100.1's structural refusal, mechanised rather than asserted: "A RATIO IS A FUNCTION OF ITS
    MEMBERS, so it adds no information and CAN DESTROY THE FIT" -- a candidate whose full set of
    algebraic prerequisites (`depends_on`, e.g. a ratio's two members, at the SAME or a DIFFERENT
    window: A100.1's own two examples, "a ratio together with both its members" and "a derivative
    together with the two windows it differences") is already admitted is refused as an exact function
    of what is already in the vector, in EITHER admission order; and F297's rank-two rule is enforced
    through `rank_group` tags, admitting at most one representative per (window, parity) group.

(e) `hartlap_factor`, `shrink_to_diagonal`, `replica_covariance`, `moment_block_nll`,
    `dodelson_schneider_factor` -- F284 point 4 / F287 point 3: "about 60 coordinates from 500 replicas
    need the Hartlap factor (N - p - 2)/(N - 1) ... and some shrinkage" (Hartlap, Simon & Schneider
    2007, A&A 464, 399; the condition number was measured at "near 1e42 before shrinkage and 1e32
    after" on the real 229-to-287-coordinate tables of
    `private/cache/plan_2026-09-18/observable_space_v2_*_cov.npz`). The shrinkage estimator is the same
    Ledoit-Wolf-toward-the-diagonal construction validated in
    `private/cache/plan_2026-09-16/p18_observable_space_v2.py`'s `_ledoit_wolf_diagonal` (sklearn's
    `ledoit_wolf` if installed, else a hand-rolled Schafer-Strimmer 2005 shrink-to-diagonal with the
    intensity reported), reproduced here as the package's own tested copy.

    THE STACK IS REFUSED, AND HERE IS WHY (a correction applied 2026-09-22, checked
    against Hartlap et al. 2007 directly before landing). Hartlap's factor unbiases E[S^-1] for `S` an
    UNSHRUNK sample covariance of Gaussian, independent replicas -- a Wishart matrix, which is exactly
    what its derivation needs. A Ledoit-Wolf or Schafer-Strimmer shrunk covariance is biased toward its
    target BY CONSTRUCTION, is not Wishart-distributed, and Hartlap's factor has no licence to correct
    its inverse. So `replica_covariance(shrinkage=True)` never Hartlap-scales its precision
    (`.hartlap` reads `None`, the reason is in `.shrinkage_engine`); a shrunk precision's actual
    coverage is calibrated against the twin's own replicas, never assumed from either paper. The
    module's DEFAULT is what both papers license together at this record's own regime, p/R about 0.1
    (A100.7: "about fifty coordinates at R = 500"): the plain sample covariance (`shrinkage=False`)
    with Sellentin & Heavens 2016 (MNRAS 456, L132)'s multivariate-t likelihood
    (`moment_block_nll`'s default `form="sellentin_heavens"`), which carries the covariance's own
    estimation uncertainty into the likelihood's SHAPE instead of rescaling the precision matrix, and
    takes no Hartlap factor of its own. `form="hartlap"` (the plain Gaussian quadratic form, Hartlap-
    scaled) stays as the named alternative, and `shrinkage=True` stays available as an explicit opt-in
    for a regime with p/R well above 0.1, where the plain sample covariance is too ill-conditioned to
    invert usefully at all (F287's "condition numbers near 1e42").

    `dodelson_schneider_factor` (Dodelson & Schneider 2013, PRD 88, 063537, Eqs. 27-28) is a SEPARATE,
    later correction: the inflation of a FITTED parameter covariance (obtained downstream, after a fit
    that used either NLL form above) from the covariance matrix itself being noisy, `1 + B(n_data -
    n_params)`. It stacks with, and does not replace, whichever of the two likelihood forms above was
    used to do the fit.

WHAT IS NOT HERE. The twin table (b, coordinate, window, level) rows this module's `select_coordinates`
and `replica_covariance` consume are built by a producer that runs the volume model over many
replicas -- A129 names it `rb5s6s/twin_volume.py`, built alongside this module by a separate piece of
work. Nothing here reads `results/`, `data_raw/`, or any other module under `rb5s6s/`; every function
takes its data as plain arrays, dicts or dataclass rows, so it is testable and usable standalone.

A100.6's caveat is repeated everywhere this module computes an S0 power: the ramp-dominated total-order
rule (`s0_w0_power`) holds ONLY on a ramp-dominated line, because mu2 in particular also carries the
natural, collisional and transit widths, which do not scale as a power of S0 at all. Every caller states
that scope beside the number; nothing here asserts it silently.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

import numpy as np

from rb5s6s._compat import trapezoid
from rb5s6s.cumulants import linear_baseline, wing_baseline

__all__ = [
    "windowed_moments_fixed_centre",
    "raw_window_moment",
    "window_derivative",
    "tent_window_moment",
    "cross_product_estimate",
    "Coordinate",
    "NAMED_RATIOS",
    "NAMED_ANCHOR",
    "s0_w0_power",
    "build_catalogue",
    "CoordinateTrial",
    "Selection",
    "select_coordinates",
    "hartlap_factor",
    "dodelson_schneider_factor",
    "shrink_to_diagonal",
    "ReplicaCovariance",
    "replica_covariance",
    "moment_block_nll",
    "monomial_to_legendre",
    "legendre_window_moments",
    "whitened_set_bias",
    "shannon_coordinate_budget",
    "moment_s0_support",
]

BaselineArg = Union[str, float, None, Tuple[str, Tuple[float, float], Tuple[float, float]]]


# ----------------------------------------------------------------------------------------------------
# Shared quadrature core, matching rb5s6s.cumulants._centred_window_moments' conventions exactly
# (the baseline handling, the interpolated grid, the trapezoid normalisation) minus the recentring
# iteration -- see the module docstring, item (a).
# ----------------------------------------------------------------------------------------------------

def _apply_baseline(grid: np.ndarray, y: np.ndarray, baseline: BaselineArg) -> np.ndarray:
    """The baseline convention of `cumulants._centred_window_moments`, reproduced exactly: "wings"
    subtracts `wing_baseline`'s scalar pedestal, None leaves the trace as it is, a number subtracts
    that scalar, and `("linear", (lo, hi), (lo, hi))` subtracts `linear_baseline`'s line through two
    named strips. Both helpers are imported from `rb5s6s.cumulants` rather than re-derived, so the two
    modules can never quietly disagree on what "wings" or "linear" means."""
    if isinstance(baseline, str) and baseline == "wings":
        return y - wing_baseline(grid, y)
    if baseline is None:
        return y
    if isinstance(baseline, (tuple, list)) and len(baseline) == 3 and baseline[0] == "linear":
        line = linear_baseline(grid, y, baseline[1], baseline[2])
        return y - line
    return y - float(baseline)


def _fixed_centre_core(nu: np.ndarray, y: np.ndarray, centre: float, half_width: float, top: int,
                        baseline: BaselineArg, n_points: int
                        ) -> Tuple[Optional[np.ndarray], Dict[str, float]]:
    """Central moments mu_1..mu_top about the FIXED `centre`, over [centre - half_width, centre +
    half_width], from one quadrature -- no iteration, no recentring. Returns `(None, info)` when the
    window would reach past the trace or the windowed area is not positive, matching
    `_centred_window_moments`'s own refusal contract (`info["in_span"]` says which)."""
    grid = np.asarray(nu, dtype=float)
    yb = _apply_baseline(grid, np.asarray(y, dtype=float), baseline)
    w = float(half_width)
    c = float(centre)
    if w <= 0:
        raise ValueError(f"_fixed_centre_core: half_width must be positive, got {w!r}")
    if (c - w) < grid[0] or (c + w) > grid[-1]:
        return None, {"centre": c, "in_span": 0.0}
    g = np.linspace(c - w, c + w, n_points)
    yy = np.interp(g, grid, yb)
    area = trapezoid(yy, g)
    if not (area > 0):
        return None, {"centre": c, "in_span": 1.0, "area": float(area)}
    yyn = yy / area
    mu = np.array([trapezoid((g - c) ** k * yyn, g) for k in range(1, top + 1)])
    return mu, {"centre": c, "in_span": 1.0, "area": float(area)}


def windowed_moments_fixed_centre(nu: np.ndarray, y: np.ndarray, centre: float,
                                   windows: Sequence[float], orders: Sequence[int],
                                   baseline: BaselineArg = None, n_points: int = 4001
                                   ) -> Tuple[Dict[float, Dict[int, float]], Dict[float, Dict[str, float]]]:
    """Central moments about a GIVEN, FIXED centre, at every window in `windows` and every order in
    `orders`, with exactly `cumulants.windowed_moments`' window, interpolation and quadrature
    conventions (see `_fixed_centre_core`). The two AGREE when `centre` is the self-converged centre
    `windowed_moments` itself returns (`info["centre"]` of its own second return value) -- checked in
    `tests/test_moment_coords.py` -- because at convergence that centre IS (to the iteration's own
    tolerance) the window's own first moment, which is exactly what `windowed_moments` centres on.

    Unlike `cumulants.windowed_moments`, this takes MANY windows in one call (the coordinate catalogue
    needs orders 1 to 12 at every window of the grid, A100), and takes an externally supplied centre
    rather than discovering one, which is the whole point (F287): a self-converged centre is a NOISY
    estimate of the line's own position, and centring the moments on it manufactures a bias
    (E[mu2_hat] = mu2 - Var(mu1_hat), growing with order) that centring on a centre the caller already
    knows -- the twin's own injected truth, or the line's independently fitted centroid -- removes.

    Returns `(values, info)`: `values[window][order]` is the central moment (nan if that window's
    quadrature failed); `info[window]` carries `centre` (echoed back), `in_span` (1.0 unless the window
    reached past the trace) and `area` (the window's own raw mass, for a caller that wants to see the
    line's share of the window before trusting a high order there).
    """
    windows = tuple(float(w) for w in windows)
    orders = tuple(int(o) for o in orders)
    if not windows:
        raise ValueError("windowed_moments_fixed_centre: windows is empty")
    if not orders:
        raise ValueError("windowed_moments_fixed_centre: orders is empty")
    top = max(orders)
    values: Dict[float, Dict[int, float]] = {}
    info: Dict[float, Dict[str, float]] = {}
    for w in windows:
        mu, inf = _fixed_centre_core(nu, y, centre, w, top, baseline, n_points)
        info[w] = inf
        if mu is None:
            values[w] = {o: float("nan") for o in orders}
            continue
        values[w] = {o: float(mu[o - 1]) for o in orders}
    return values, info


def raw_window_moment(nu: np.ndarray, y: np.ndarray, centre: float, half_width: float, order: int,
                       baseline: BaselineArg = None, n_points: int = 4001) -> float:
    """The UN-normalised n-th moment about a fixed centre, N_n(W) = integral_{c-W}^{c+W} (x-c)^n f(x)
    dx with f the baseline-subtracted trace -- the numerator alone, with no division by the window's
    own area. This is the quantity F297's window-derivative and window-integral identities are stated
    for ("For a raw moment about a FIXED centre c ... M_n(W) = integral of (x - c)^n f(x)"); it is a
    building block for `window_derivative` and the Fubini identity `tent_window_moment` implements
    directly, not a general-purpose replacement for `windowed_moments_fixed_centre`'s NORMALISED
    central moments. Returns nan if the window would reach past the trace.
    """
    grid = np.asarray(nu, dtype=float)
    yb = _apply_baseline(grid, np.asarray(y, dtype=float), baseline)
    w = float(half_width)
    c = float(centre)
    n = int(order)
    if w <= 0:
        raise ValueError(f"raw_window_moment: half_width must be positive, got {w!r}")
    if (c - w) < grid[0] or (c + w) > grid[-1]:
        return float("nan")
    g = np.linspace(c - w, c + w, n_points)
    yy = np.interp(g, grid, yb)
    return float(trapezoid((g - c) ** n * yy, g))


def window_derivative(nu: np.ndarray, y: np.ndarray, centre: float, half_width: float, order: int,
                       baseline: BaselineArg = None) -> float:
    """dM_n/dW at (centre, half_width), F297's closed form via Leibniz's rule on the raw moment
    `raw_window_moment`:

        dM_n/dW = W^n [f(c+W) + (-1)^n f(c-W)]

    a point evaluation of the (baseline-subtracted) trace at the two window edges c-W and c+W -- no
    quadrature at all, unlike `raw_window_moment` itself. F297: "at one window every order's derivative
    is fixed by the line's TWO edge values: at one window every order's derivative is fixed by the
    line's TWO edge values, so the derivative coordinates across n have rank two, the even orders
    reading the edge SUM and the odd the edge DIFFERENCE, each scaled by W^n." Consequence for the
    catalogue (A100.5, F297): build at most one even- and one odd-order derivative per window --
    `build_catalogue` offers exactly that pair, and `select_coordinates` refuses any further order at
    the same window as an exact multiple of the one already admitted (its `rank_group` tag).

    Returns nan if the window would reach past the trace.
    """
    grid = np.asarray(nu, dtype=float)
    yb = _apply_baseline(grid, np.asarray(y, dtype=float), baseline)
    w = float(half_width)
    c = float(centre)
    n = int(order)
    if w <= 0:
        raise ValueError(f"window_derivative: half_width must be positive, got {w!r}")
    if (c - w) < grid[0] or (c + w) > grid[-1]:
        return float("nan")
    f_hi = float(np.interp(c + w, grid, yb))
    f_lo = float(np.interp(c - w, grid, yb))
    sign = 1.0 if n % 2 == 0 else -1.0
    return (w ** n) * (f_hi + sign * f_lo)


def tent_window_moment(nu: np.ndarray, y: np.ndarray, centre: float, w_max: float, order: int,
                        baseline: BaselineArg = None, n_points: int = 4001,
                        normalize: bool = True) -> float:
    """The n-th moment of the trace under a TENT (triangular) window of half-width `w_max` centred on
    `centre`: weight (w_max - |x - centre|) over [centre - w_max, centre + w_max], zero outside it.

    F297: "the integral of M_n over W from 0 to W_max is the n-th moment under a TENT window ... a
    different window shape and not a new statistic." This function computes that integral coordinate
    DIRECTLY, as this one quadrature, rather than by numerically summing `raw_window_moment` over a
    grid of W: the two are identical by Fubini's theorem (swap the x- and W-integrals; a point x is
    inside every rectangular window of half-width W >= |x - centre|, so it is counted over a W-span of
    length `w_max - |x - centre|`), and the direct form has one quadrature's error instead of two
    stacked ones (`tests/test_moment_coords.py` checks the identity against a literal W-grid sum of
    `raw_window_moment`).

    `normalize=True` (the default) divides by the tent window's own zeroth moment (its total weighted
    mass), matching `windowed_moments_fixed_centre`'s central-moment convention, so this reads as a
    genuine "moment" of the trace under the tent window. `normalize=False` returns F297's literal raw
    quantity, the one the Fubini identity is checked against. Returns nan if the window would reach
    past the trace, or (normalised only) if the tent-weighted mass is not positive.
    """
    grid = np.asarray(nu, dtype=float)
    yb = _apply_baseline(grid, np.asarray(y, dtype=float), baseline)
    wmax = float(w_max)
    c = float(centre)
    n = int(order)
    if wmax <= 0:
        raise ValueError(f"tent_window_moment: w_max must be positive, got {wmax!r}")
    if (c - wmax) < grid[0] or (c + wmax) > grid[-1]:
        return float("nan")
    g = np.linspace(c - wmax, c + wmax, n_points)
    yy = np.interp(g, grid, yb)
    tent = wmax - np.abs(g - c)
    weighted = yy * tent
    num = trapezoid((g - c) ** n * weighted, g)
    if not normalize:
        return float(num)
    mass = trapezoid(weighted, g)
    if not (mass > 0):
        return float("nan")
    return float(num / mass)


# ----------------------------------------------------------------------------------------------------
# (b) The cross-product estimator (F284 point 2, F287 point 2)
# ----------------------------------------------------------------------------------------------------

def cross_product_estimate(*replicas: Iterable[float]) -> Tuple[float, float]:
    """The unbiased cross-product estimator of a product of expectations, from two (or more)
    INDEPENDENT replica arrays of a statistic, or of several statistics whose product is wanted (F284
    point 2, F287 point 2): with `a` and `b` two length-R arrays of a statistic measured on
    INDEPENDENT noise realisations of the SAME underlying trace (the up- and the down-sweep of one
    scan, or two repeats), `mean(a * b)` is unbiased for `E[a] * E[b]`, because the two replicas' noise
    is independent and `E[a*b] = E[a]*E[b]`. The naive single-replica square `mean(a**2)` instead
    targets `E[a]^2 + Var(a)`, which is what F284/F287 diagnose as the dominant narrow-window bias of
    every "squared or product" coordinate (mu3^2/mu2^3's numerator, mu1^3/mu3, mu2^3's denominator,
    mu5*mu3).

    Called with more than two arrays it generalises to an unbiased estimator of a product of THREE OR
    MORE independent expectations (e.g. an mu2^3 denominator built from three independent replicas
    rather than a squared pair), by the same argument (independence makes the expectation of a product
    the product of expectations). The record's own producer (F287's `cross_products`) in fact only ever
    pairs TWO replicas per value even for cubic denominators, using SYMMETRISED combinations of the
    pair (e.g. `(m2a*m2b)**1.5` for an mu2^3 denominator, since mu2 is always positive); building THAT
    specific construction is the caller's job (a monomial in already-baseline-corrected replica
    arrays), this function's job is only the one general primitive: the product of independent
    replicas, averaged, with its own standard error.

    Example, reproducing F287's own `mu3^2/mu2^3 (cross)` construction from this primitive: given
    length-R arrays `mu3_a, mu3_b, mu2_a, mu2_b` (mu3 and mu2 at one window, from two independent
    sweeps a and b of each of R replicas), the per-replica cross ratio
    `(mu3_a * mu3_b) / (mu2_a * mu2_b) ** 1.5` is an array of R values, each one an estimate of
    mu3^2/mu2^3 with the same-replica self-correlation term removed; averaging THAT array (a plain
    `numpy.mean`/`numpy.std`, not another call to this function) is F287's reported quantity. This
    function supplies the unbiased numerator, `cross_product_estimate(mu3_a, mu3_b)`, and the same
    call shape for the denominator's pieces; composing them into the specific ratio is a producer's
    job, not this general primitive's.

    Returns `(estimate, standard_error)`, the standard error being the replica-to-replica scatter of
    the per-replica product divided by sqrt(R) (a plain standard error of the mean, ddof=1). Raises if
    fewer than two arrays are given, if they are not all the same length, or if fewer than two paired
    replicas are available (no standard error is defined from one number).
    """
    arrays = [np.asarray(list(a) if not hasattr(a, "__len__") else a, dtype=float) for a in replicas]
    if len(arrays) < 2:
        raise ValueError("cross_product_estimate: need at least two independent replica arrays")
    n = arrays[0].size
    for a in arrays[1:]:
        if a.size != n:
            raise ValueError("cross_product_estimate: replica arrays must have the same length "
                              f"({[a.size for a in arrays]})")
    if n < 2:
        raise ValueError("cross_product_estimate: need at least two paired replicas for a standard error")
    prod = np.ones(n, dtype=float)
    for a in arrays:
        prod = prod * a
    est = float(np.mean(prod))
    se = float(np.std(prod, ddof=1) / math.sqrt(n))
    return est, se


# ----------------------------------------------------------------------------------------------------
# (c) The coordinate catalogue: orders, ratios, derivatives, integrals, each with its S0 power
# ----------------------------------------------------------------------------------------------------

def s0_w0_power(factors: Iterable[Tuple[int, int]]) -> Tuple[int, int]:
    """(w0_power, S0_power) of a monomial of ramp central moments -- `factors` an iterable of
    (order, power) pairs, e.g. `((4, 1), (2, -2))` for mu4/mu2^2 -- in the RAMP-DOMINATED LIMIT
    (A100.6, F283): a pure ramp central moment of order n scales as S0^n with NO independent w0
    dependence once expressed through S0 (matching A45's own (w0, S0) exponent plane, which gives the
    ramp's odd orders the pair (0, 3) for mu3, i.e. w0 power zero, S0 power 3 -- its OWN order), so
    a monomial's pair is `(0, sum(order * power for order, power in factors))`: "the S0 power of a
    ratio of ramp moments is its total order" (F283), mechanical and never eyeballed (A100.6).
    Reproduces F283's own worked examples: mu4/mu2^2 -> (0, 0), mu3^2/mu2^3 -> (0, 0), mu1^3/mu3 ->
    (0, 0) (all S0-FREE), mu5/mu3 -> (0, 2) (S0-BEARING, "a shift meter, not an anchor").

    HOLDS ONLY ON A RAMP-DOMINATED LINE. mu2 in particular also carries the natural, collisional and
    transit widths, none of which scales as a power of S0 (A100.6's own caveat, repeated here because
    this is the one function every S0-power number in this module's catalogue is computed from): a
    caller states that scope beside the number, this function does not know whether it holds for the
    trace it is being applied to.
    """
    total = sum(int(order) * int(power) for order, power in factors)
    return 0, int(total)


# F283's owner-named ratios (mu_n as (order, power) pairs); F283's exact ramp-dominated anchors (the
# thin-window, weak-field ramp density 2s/S0^2 on [0, S0], W -> infinity, u -> 0), reproduced here as
# plain numbers and cross-checked against independent rationals in this module's own tests.
NAMED_RATIOS: Dict[str, Tuple[Tuple[int, int], ...]] = {
    "mu4/mu2^2": ((4, 1), (2, -2)),
    "mu3^2/mu2^3": ((3, 2), (2, -3)),
    "mu1^3/mu3": ((1, 3), (3, -1)),
    "mu5/mu3": ((5, 1), (3, -1)),
}
NAMED_ANCHOR: Dict[str, float] = {
    "mu4/mu2^2": 12.0 / 5.0,
    "mu3^2/mu2^3": 8.0 / 25.0,
    "mu1^3/mu3": -40.0,
    "mu5/mu3": 20.0 / 63.0,
}


@dataclass(frozen=True)
class Coordinate:
    """One catalogue entry: WHAT a coordinate is, structurally, before any twin measures its bias.

    `name` -- e.g. "mu4", "mu4/mu2^2", "mu4/mu2^2 (cross)", "dmu2/dW", "tent_mu2".
    `window` -- the half-width (rect window) or tent half-width this coordinate is evaluated at.
    `kind` -- "moment" | "ratio" | "cross_ratio" | "derivative" | "integral".
    `factors` -- the (order, power) monomial this coordinate is built from; empty for a derivative or
        an integral coordinate, which are not monomials in the bare moments (F297).
    `s0_power`, `w0_power` -- from `s0_w0_power(factors)` for a moment/ratio/cross_ratio coordinate
        (ramp-dominated limit, A100.6); `None` for a derivative or integral coordinate, because F297
        gives their GEOMETRIC relation to the rectangular moments but not (yet) a derived S0/w0 scaling
        law, and this module asserts only what has actually been derived.
    `order` -- the coordinate's own order (the n of mu_n, or of the derivative/integral it carries).
    `depends_on` -- OTHER catalogue coordinates, as (name, window) pairs, whose SIMULTANEOUS presence
        with this one makes the covariance singular by construction (A100.1: "a ratio together with
        both its members"); empty for a bare moment or a derivative/integral coordinate.
    `rank_group` -- coordinates sharing a non-None `rank_group` are, at that window, EXACT scalar
        multiples of one another (F297's rank-two derivative family); `select_coordinates` admits at
        most one representative per group.
    `replicas_needed` -- how many INDEPENDENT replicas one value of this coordinate consumes (1 for a
        plain moment or a naive ratio, 2 for a cross-product-built one, matching F287's own
        construction, which pairs replicas rather than needing as many as the monomial's total power).
    `anchor` -- the ramp-dominated closed-form value at W -> infinity, u -> 0 (F283), where known.
    """
    name: str
    window: float
    kind: str
    factors: Tuple[Tuple[int, int], ...] = ()
    s0_power: Optional[int] = None
    w0_power: Optional[int] = None
    order: Optional[int] = None
    depends_on: Tuple[Tuple[str, float], ...] = ()
    rank_group: Optional[str] = None
    replicas_needed: int = 1
    anchor: Optional[float] = None

    def trial(self, level: str, bias: float, bias_se: float, replica_sd: float, **kw) -> "CoordinateTrial":
        """Build a `CoordinateTrial` (the twin-measured counterpart) for this catalogue entry,
        carrying over its structural fields (`depends_on`, `rank_group`) automatically so a caller
        supplies only what the twin actually measured."""
        return CoordinateTrial(coordinate=self.name, window=self.window, level=level, bias=bias,
                                bias_se=bias_se, replica_sd=replica_sd, depends_on=self.depends_on,
                                rank_group=self.rank_group, **kw)


def build_catalogue(windows: Sequence[float], max_order: int = 12, *, min_order: int = 1,
                     ratios: Mapping[str, Tuple[Tuple[int, int], ...]] = NAMED_RATIOS,
                     even_derivative_order: int = 2, odd_derivative_order: int = 3,
                     integral_orders: Sequence[int] = (1, 2, 3, 4)) -> Tuple[Coordinate, ...]:
    """The full observable-space catalogue of A100: bare central moments `min_order`..`max_order` (1
    to 12 by default), the named ratios (and their cross-product-built twins, F284/F287), one even- and
    one odd-order window derivative per window (F297's rank-two rule), and a set of window-integral
    (tent-window moment) coordinates -- at every window in `windows`.

    This is a STRUCTURAL catalogue: it says what each coordinate IS and what it exactly-algebraically
    depends on, not what its bias is. A caller (the twin harness, `rb5s6s/twin_volume.py` per A129)
    measures each entry's bias/SE/replica-sd/forecastability/leverage and turns it into a
    `CoordinateTrial` (via `Coordinate.trial(...)`) for `select_coordinates`.

    `even_derivative_order`/`odd_derivative_order` pick WHICH order's derivative represents its parity
    at each window (F297: every order's derivative is a scalar multiple of the same two edge values, so
    the choice of representative keeps all the information, only convenience -- order 2 and 3 are the
    ones already read elsewhere in this record). `integral_orders` are the orders `tent_mu{n}` is built
    for; every one is independent of the rectangular-window catalogue (a tent window is a DIFFERENT
    window shape, F297, not an exact function of the rectangular moments already listed), so none of
    them carries a `depends_on` entry.
    """
    windows = tuple(float(w) for w in windows)
    if not windows:
        raise ValueError("build_catalogue: windows is empty")
    if max_order < min_order:
        raise ValueError(f"build_catalogue: max_order ({max_order}) < min_order ({min_order})")
    coords: List[Coordinate] = []
    for w in windows:
        for n in range(min_order, max_order + 1):
            w0p, s0p = s0_w0_power(((n, 1),))
            coords.append(Coordinate(name=f"mu{n}", window=w, kind="moment", factors=((n, 1),),
                                      s0_power=s0p, w0_power=w0p, order=n))
        for name, factors in ratios.items():
            depends = tuple((f"mu{n}", w) for n, _p in factors)
            w0p, s0p = s0_w0_power(factors)
            anchor = NAMED_ANCHOR.get(name)
            coords.append(Coordinate(name=name, window=w, kind="ratio", factors=factors,
                                      s0_power=s0p, w0_power=w0p, depends_on=depends, anchor=anchor))
            # the cross-product-built twin (F284 point 2, F287): an INDEPENDENT-replica-pair
            # construction with the same exact-function relation to its members (A100.1's caution
            # applies to both forms alike, since both are still monomials in mu2, mu4, ... at this
            # window -- see cross_product_estimate's own docstring for the caveat on what "unbiased"
            # covers here).
            coords.append(Coordinate(name=f"{name} (cross)", window=w, kind="cross_ratio",
                                      factors=factors, s0_power=s0p, w0_power=w0p, depends_on=depends,
                                      replicas_needed=2, anchor=anchor))
        # F297: at most one even- and one odd-order window derivative per window.
        coords.append(Coordinate(name=f"dmu{even_derivative_order}/dW", window=w, kind="derivative",
                                  order=even_derivative_order, rank_group=f"deriv_even@{w:g}"))
        coords.append(Coordinate(name=f"dmu{odd_derivative_order}/dW", window=w, kind="derivative",
                                  order=odd_derivative_order, rank_group=f"deriv_odd@{w:g}"))
        for n in integral_orders:
            coords.append(Coordinate(name=f"tent_mu{n}", window=w, kind="integral", order=n))
    return tuple(coords)


# ----------------------------------------------------------------------------------------------------
# (d) Selection under rule W1, and A100.1's structural (singular-covariance) refusal
# ----------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class CoordinateTrial:
    """One twin-measured trial of a catalogue coordinate at one noise level: what
    `select_coordinates` reads to apply rule W1. `coordinate` and `window` together key the cell (rule
    W1: "a (statistic, window) cell"); `level` is the noise rung this trial was measured at ("archive",
    "n10", "noiseless", ... -- any label the caller's twin harness uses, matching
    `rb5s6s.ladder_gate.NOISE_SCALE`'s keys is conventional but not enforced here).

    `bias`, `bias_se`, `replica_sd` -- W1(a): admitted only if `bias_se <= se_frac * replica_sd`.
    `resolved` -- W1(c): the halved-grid numerical-floor check; True unless the caller's twin measured
        this cell below its floor (F218, F282: mu8 above 5 MHz, mu12 above 1 MHz).
    `forecast_ok` -- W1(b): `True` if the bias at this (coordinate, window)'s truth is predicted by its
        neighbours' interpolation within its own SE; `False` if it fails that check (refused); `None`
        if the check has not been run yet (carried DIAGNOSTIC, never refused on this clause alone).
    `leverage` -- W1(d): the fraction (0 to 1) of the parameter's total Fisher information this cell
        carries at the archive rung; `None` means unmeasured (A58: "until T0e builds the sensitivity
        table, W1(d) reads leverage_unmeasured"), carried DIAGNOSTIC rather than refused unless the
        caller passes `require_leverage=True`.
    `depends_on`, `rank_group` -- A100.1's and F297's structural fields, normally carried over from the
        `Coordinate` catalogue entry via `Coordinate.trial(...)` rather than set by hand.
    """
    coordinate: str
    window: float
    level: str
    bias: float
    bias_se: float
    replica_sd: float
    resolved: bool = True
    forecast_ok: Optional[bool] = None
    leverage: Optional[float] = None
    depends_on: Tuple[Tuple[str, float], ...] = ()
    rank_group: Optional[str] = None

    @property
    def key(self) -> Tuple[str, float]:
        return (self.coordinate, self.window)


def _field(row, name: str, default=None):
    """Read `name` off a table row that may be a `CoordinateTrial`, any other object with the same
    attributes, or a plain mapping (e.g. one CSV/TSV row read as a dict) -- so `select_coordinates`
    works directly on a twin harness's dict-based table without forcing it through the dataclass."""
    if isinstance(row, Mapping):
        return row.get(name, default)
    return getattr(row, name, default)


@dataclass(frozen=True)
class Selection:
    """The result of `select_coordinates`: every input cell appears in exactly one of the three
    buckets, keyed by `(coordinate, window)`. `admitted` is a tuple (in admission order, best-behaved
    first, A100.2); `diagnostic` and `refused` map each cell to the reason it was set aside."""
    admitted: Tuple[Tuple[str, float], ...]
    diagnostic: Dict[Tuple[str, float], str] = field(default_factory=dict)
    refused: Dict[Tuple[str, float], str] = field(default_factory=dict)

    def __post_init__(self):
        admitted_set = set(self.admitted)
        if len(admitted_set) != len(self.admitted):
            raise ValueError("Selection: a cell is admitted more than once")
        overlap = (admitted_set & set(self.diagnostic)) | (admitted_set & set(self.refused)) \
            | (set(self.diagnostic) & set(self.refused))
        if overlap:
            raise ValueError(f"Selection: {sorted(overlap)} placed in more than one bucket")


def select_coordinates(table: Iterable, *, level: str = "archive", se_frac: float = 0.2,
                        leverage_threshold: float = 0.01, require_leverage: bool = False) -> Selection:
    """Rule W1 applied to a twin table of per-(coordinate, window) trials at one noise LEVEL (the
    archive rung by default; `private/PLAN_2026-09-18_CONSOLIDATED.md`, "Rule W1 -- when a (statistic,
    window) cell is admitted"), followed by A100.1's structural refusal of an exactly-redundant
    coordinate.

    `table` is any iterable of rows exposing `coordinate`, `window`, `level`, `bias`, `bias_se`,
    `replica_sd` and optionally `resolved`, `forecast_ok`, `leverage`, `depends_on`, `rank_group`
    (`CoordinateTrial` instances, or plain dicts with the same keys -- see `_field`). Exactly one row
    per `(coordinate, window)` is expected at the given `level`; a duplicate raises.

    STAGE ONE, rule W1's four clauses, each cell judged independently:
      (a) `bias_se <= se_frac * replica_sd` (se_frac = 0.2 by default, W1(a): "SE(bias) <= 0.2 x
          sd(statistic over replicas)"). A non-finite or non-positive `replica_sd`, or a non-finite
          `bias_se`, refuses outright (there is nothing W1(a) can certify about such a cell).
      (b) `forecast_ok is not False` (W1(b)). `False` refuses; `None` (not yet checked) demotes to
          DIAGNOSTIC rather than refusing, since W1(b) only refuses a cell that FAILS the
          interpolation check, not one nobody has run it on yet.
      (c) `resolved is not False` (W1(c), the halved-grid numerical-floor check) -- `False` refuses.
      (d) `leverage >= leverage_threshold` (W1(d), A45.5's one-per-cent-of-information clause).
          `leverage is None` reads `leverage_unmeasured` (A58) and is DIAGNOSTIC, not refused, unless
          `require_leverage=True`; a measured leverage below the threshold is DIAGNOSTIC (it is a real
          number, just a small one, so the cell is not thrown away, only kept out of the fitted
          vector).
    A cell passing all four is a PASS candidate.

    STAGE TWO, A100.1: PASS candidates are ranked best-behaved first (ascending |bias| / replica_sd,
    A100.2: "the vector takes the coordinates whose bias is smallest or best forecastable"), then
    admitted greedily. A candidate is refused, in EITHER admission order:
      - if every coordinate its `depends_on` names is ALREADY admitted (it is an exact function of what
        is already in the vector -- A100.1's "a ratio together with both its members"); or
      - if admitting it would COMPLETE the `depends_on` set of an ALREADY-admitted coordinate (the
        reverse order: the ratio got in first, and this candidate is the last of its members); or
      - if it shares a non-None `rank_group` with a coordinate already admitted (F297: every order's
        window derivative at one window is an exact scalar multiple of the same two edge values, so a
        second one at the same window adds no rank).

    Returns a `Selection`. Every input cell at `level` appears in exactly one of `.admitted`,
    `.diagnostic` or `.refused`.
    """
    rows = [r for r in table if _field(r, "level") == level]
    if not rows:
        raise ValueError(f"select_coordinates: no rows at level {level!r}")
    cells: Dict[Tuple[str, float], object] = {}
    for r in rows:
        key = (str(_field(r, "coordinate")), float(_field(r, "window")))
        if key in cells:
            raise ValueError(f"select_coordinates: duplicate row for coordinate {key[0]!r} at "
                              f"window {key[1]:g}, level {level!r}")
        cells[key] = r

    status: Dict[Tuple[str, float], str] = {}
    reason: Dict[Tuple[str, float], str] = {}
    for key, r in cells.items():
        sd = _field(r, "replica_sd")
        se = _field(r, "bias_se")
        if sd is None or not math.isfinite(sd) or not (sd > 0):
            status[key], reason[key] = "REFUSED", "W1(a): replica_sd is not a usable positive number"
            continue
        if se is None or not math.isfinite(se):
            status[key], reason[key] = "REFUSED", "W1(a): bias_se is not a usable number"
            continue
        if se > se_frac * sd:
            status[key], reason[key] = "REFUSED", f"W1(a): bias_se/replica_sd = {se / sd:.3g} > {se_frac:g}"
            continue
        if _field(r, "resolved", True) is False:
            status[key], reason[key] = "REFUSED", "W1(c): below its numerical floor (halved-grid check)"
            continue
        if _field(r, "forecast_ok", None) is False:
            status[key], reason[key] = "REFUSED", "W1(b): bias not forecastable across neighbouring truths"
            continue
        leverage = _field(r, "leverage", None)
        if leverage is None:
            if require_leverage:
                status[key] = "REFUSED"
                reason[key] = "W1(d): leverage unmeasured (A58) and require_leverage=True"
            else:
                status[key] = "DIAGNOSTIC"
                reason[key] = "W1(d): leverage unmeasured (A58); carried diagnostic"
            continue
        if leverage < leverage_threshold:
            status[key] = "DIAGNOSTIC"
            reason[key] = f"W1(d): leverage {leverage:.3g} < {leverage_threshold:g}"
            continue
        if _field(r, "forecast_ok", None) is None:
            status[key] = "DIAGNOSTIC"
            reason[key] = "W1(b): forecastability not yet checked"
            continue
        status[key], reason[key] = "PASS", "W1(a)-(d) satisfied"

    passed = [k for k, s in status.items() if s == "PASS"]

    def _rank(k):
        r = cells[k]
        sd = _field(r, "replica_sd")
        bias = _field(r, "bias")
        bias = 0.0 if bias is None else abs(bias)
        return (bias / sd if sd else float("inf"), k[0], k[1])
    passed.sort(key=_rank)

    def _deps(k) -> Tuple[Tuple[str, float], ...]:
        return tuple(tuple(d) for d in (_field(cells[k], "depends_on", ()) or ()))

    admitted: List[Tuple[str, float]] = []
    admitted_set: set = set()
    group_used: Dict[str, Tuple[str, float]] = {}
    refused: Dict[Tuple[str, float], str] = {k: v for k, v in reason.items() if status[k] == "REFUSED"}
    diagnostic: Dict[Tuple[str, float], str] = {k: v for k, v in reason.items() if status[k] == "DIAGNOSTIC"}

    for key in passed:
        group = _field(cells[key], "rank_group", None)
        if group is not None and group in group_used:
            other = group_used[group]
            refused[key] = (f"F297: rank_group {group!r} already has an admitted representative "
                             f"({other[0]}@{other[1]:g}); a second order at this window is an exact "
                             f"scalar multiple of the first")
            continue
        depends_on = _deps(key)
        missing = [d for d in depends_on if d not in admitted_set]
        if depends_on and not missing:
            refused[key] = ("A100.1: an exact function of " +
                             ", ".join(f"{n}@{w:g}" for n, w in depends_on) + ", already admitted")
            continue
        tentative = admitted_set | {key}
        completed = [a for a in admitted
                     if key in _deps(a) and _depends_on_fully_in(_deps(a), tentative)]
        if completed:
            refused[key] = ("A100.1: admitting this would complete the exact dependency set of " +
                             ", ".join(f"{n}@{w:g}" for n, w in completed))
            continue
        admitted.append(key)
        admitted_set.add(key)
        if group is not None:
            group_used[group] = key

    return Selection(admitted=tuple(admitted), diagnostic=diagnostic, refused=refused)


def _depends_on_fully_in(deps: Tuple[Tuple[str, float], ...], present: set) -> bool:
    """True iff every entry of `deps` is in `present` -- factored out of `select_coordinates` only so
    the intent (A100.1's "fully satisfied prerequisite set") reads as one named call at its call site."""
    return all(d in present for d in deps)


# ----------------------------------------------------------------------------------------------------
# (e) Replica covariance (Hartlap + Ledoit-Wolf shrinkage) and the moment block's log-likelihood
# ----------------------------------------------------------------------------------------------------

def hartlap_factor(n_rep: int, n_data: int) -> float:
    """The Hartlap, Simon & Schneider (2007, A&A 464, 399) debiasing factor on the INVERSE of a sample
    covariance estimated from `n_rep` independent replicas of an `n_data`-dimensional statistic:

        alpha = (n_rep - n_data - 2) / (n_rep - 1)

    so that `alpha * S^-1` is unbiased for the true precision matrix Sigma^-1 when `S` is the sample
    covariance of Gaussian data (E[S^-1] = Sigma^-1 / alpha). Returned AS COMPUTED, never clipped: for
    `n_rep <= n_data + 2` it is zero or negative, which this record reads as a replica count too small
    for the vector attempted -- F287's own measurement, "the Hartlap factor negative on 31 of 32
    conditions at the archive level" with the full ~230-coordinate space, is exactly A100.7's budget
    ("the ultra-joint fit is a SELECTION over the reparameterised grid") made concrete, and a caller
    silently clipping this to a small positive number would hide that signal rather than act on it.
    """
    n_rep = int(n_rep)
    n_data = int(n_data)
    if n_rep < 2:
        raise ValueError(f"hartlap_factor: need at least two replicas, got {n_rep}")
    if n_data < 1:
        raise ValueError(f"hartlap_factor: n_data must be at least 1, got {n_data}")
    return (n_rep - n_data - 2) / (n_rep - 1)


def dodelson_schneider_factor(n_rep: int, n_data: int, n_params: int) -> float:
    """The Dodelson & Schneider (2013, PRD 88, 063537, Eqs. 27-28) inflation of a FITTED parameter
    covariance from the data covariance itself being a noisy estimate from `n_rep` replicas:

        B = (n_rep - n_data - 2) / ((n_rep - n_data - 1) * (n_rep - n_data - 4))
        factor = 1 + B * (n_data - n_params)

    so that `factor * Cov_hat(theta)` is the corrected parameter covariance, `Cov_hat(theta)` the one
    obtained from a standard fit (e.g. the inverse Fisher/Hessian matrix) using the `n_data`-dimensional
    data vector and `n_params` fitted parameters. This is a SEPARATE, LATER correction from either
    `moment_block_nll` form: it inflates the covariance of the FITTED PARAMETERS after a fit, whichever
    likelihood form (`"hartlap"` or `"sellentin_heavens"`) was used to obtain them, and does not replace
    either one -- the two kinds of correction answer different questions (the likelihood's own shape at
    fixed data, versus how much extra the parameter estimate scatters because the covariance it was fit
    against was itself estimated from a finite number of replicas).

    Returned AS COMPUTED (never clipped), matching `hartlap_factor`'s own convention. `B`'s denominator
    vanishes at `n_rep = n_data + 1` or `n_rep = n_data + 4`, where this raises; away from those two
    points `B` is finite but changes sign as `n_rep - n_data` crosses 1 and 4, and Dodelson & Schneider's
    own derivation assumes `n_rep > n_data + 4` for a positive, sensible inflation, which the caller
    should check when it matters, not this function.
    """
    n_rep = int(n_rep)
    n_data = int(n_data)
    n_params = int(n_params)
    if n_rep < 1 or n_data < 1 or n_params < 0:
        raise ValueError(f"dodelson_schneider_factor: need n_rep >= 1, n_data >= 1, n_params >= 0, "
                          f"got ({n_rep}, {n_data}, {n_params})")
    d = n_rep - n_data
    denom = (d - 1) * (d - 4)
    if denom == 0:
        raise ValueError(f"dodelson_schneider_factor: undefined at n_rep - n_data = {d} "
                          f"(the denominator (d-1)(d-4) vanishes at d = 1 or d = 4)")
    b = (d - 2) / denom
    return 1.0 + b * (n_data - n_params)


def shrink_to_diagonal(X: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, str]:
    """Ledoit-Wolf-style shrinkage of the sample covariance of `X` (n_rep x n_data) toward its own
    diagonal: `sklearn.covariance.ledoit_wolf` if installed, else a hand-rolled Schafer-Strimmer
    (2005)-style estimator -- the same construction validated in
    `private/cache/plan_2026-09-16/p18_observable_space_v2.py`'s `_ledoit_wolf_diagonal` (F284 point 4,
    F287 point 3), reproduced here as the package's own tested copy, since sklearn is not one of this
    project's declared dependencies. The shrinkage intensity minimises the expected Frobenius loss of
    shrinking every OFF-diagonal entry toward zero while the diagonal is kept exact:

        kappa = sum_{i != j} Var-hat(s_ij) / sum_{i != j} s_ij^2,  clipped to [0, 1]

    with Var-hat(s_ij) the usual N/(N-1)^3 * sum_k (w_kij - wbar_ij)^2 of the per-sample outer products
    w_kij = (x_ki - xbar_i)(x_kj - xbar_j), computed without ever forming the (N, P, P) tensor, via the
    Frobenius identity ||outer(x_k, x_k) - Wbar||_F^2 = (x_k . x_k)^2 - 2 x_k^T Wbar x_k + ||Wbar||_F^2 (kappa
    is scale-invariant, so using the /N-normalised Wbar throughout both the numerator and the
    denominator is exact, not an approximation of using the /(N-1) sample covariance instead).

    Returns `(S, S_shrunk, kappa, engine)`: the plain sample covariance, the shrunk one, the shrinkage
    intensity in [0, 1], and a string naming which engine computed it.
    """
    X = np.asarray(X, dtype=float)
    n, p = X.shape
    try:
        from sklearn.covariance import ledoit_wolf  # noqa: PLC0415 -- optional, checked directly
        S_shrunk, kappa = ledoit_wolf(X)
        Xc = X - X.mean(0)
        S = (Xc.T @ Xc) / max(n - 1, 1)
        return S, np.asarray(S_shrunk, dtype=float), float(kappa), "sklearn.covariance.ledoit_wolf"
    except ImportError:
        pass
    Xc = X - X.mean(0)
    S = (Xc.T @ Xc) / max(n - 1, 1)
    if n < 3 or p < 2:
        return S, S.copy(), 0.0, "diagonal-shrinkage (Schafer-Strimmer): n or p too small, kappa=0"
    Wbar = S * (n - 1) / n
    norms2 = np.einsum("ki,ki->k", Xc, Xc)
    quad = np.einsum("ki,ij,kj->k", Xc, Wbar, Xc)
    frob2_wbar = float(np.sum(Wbar ** 2))
    term = norms2 ** 2 - 2.0 * quad + frob2_wbar
    c = n / (n - 1.0) ** 3
    pi_total = c * float(term.sum())
    diag_dev = Xc ** 2 - np.diag(Wbar)[None, :]
    pi_diag = c * float((diag_dev ** 2).sum())
    pi_off = max(pi_total - pi_diag, 0.0)
    lam_off = float((Wbar ** 2).sum() - (np.diag(Wbar) ** 2).sum())
    kappa = 0.0 if lam_off <= 0 else float(np.clip(pi_off / lam_off, 0.0, 1.0))
    S_shrunk = S.copy()
    off = ~np.eye(p, dtype=bool)
    S_shrunk[off] = (1.0 - kappa) * S[off]
    return S, S_shrunk, kappa, "diagonal-shrinkage (Schafer-Strimmer): sklearn unavailable"


@dataclass(frozen=True)
class ReplicaCovariance:
    """The covariance of a replica-measured coordinate vector. `cov` is the plain sample covariance;
    `cov_shrunk` is it after `shrink_to_diagonal` (equal to `cov` when `shrinkage=False`); `precision`
    is the matrix `moment_block_nll`'s quadratic form wants directly (its `precision=` argument);
    `cond_before`/`cond_after` are `cov`'s and `cov_shrunk`'s condition numbers (F287: "condition
    numbers near 1e42 before shrinkage and 1e32 after").

    `hartlap` and `precision` are built DIFFERENTLY depending on `shrinkage` (a
    correction, 2026-09-22): Hartlap, Simon & Schneider (2007)'s factor unbiases the inverse of an
    UNSHRUNK Wishart sample covariance, and has no licence over a shrunk one, which is biased toward
    its target by construction. So with `shrinkage=False` (the module's own default), `hartlap` is
    `hartlap_factor(n_rep, n_data)` and `precision = hartlap * pinv(cov)`; with `shrinkage=True`,
    `hartlap` is `None` and `precision = pinv(cov_shrunk)` carries NO factor at all -- its actual
    coverage has to be calibrated against the twin's own replicas, never assumed from either paper
    (`shrinkage_engine` states this in words alongside whichever shrinkage engine ran).
    """
    coord_names: Tuple[str, ...]
    n_rep: int
    n_data: int
    cov: np.ndarray
    cov_shrunk: np.ndarray
    shrinkage_kappa: float
    shrinkage_engine: str
    hartlap: Optional[float]
    precision: np.ndarray
    cond_before: float
    cond_after: float


_NO_HARTLAP_ON_SHRUNK = ("no Hartlap factor: (n_rep-n_data-2)/(n_rep-1) unbiases the inverse of an "
                          "UNSHRUNK Wishart sample covariance (Hartlap, Simon & Schneider 2007); a "
                          "shrunk covariance is biased toward its target by construction and is not "
                          "Wishart-distributed, so that licence does not extend to it -- this "
                          "precision's coverage is calibrated on the twin's own replicas, never assumed")


def replica_covariance(X: np.ndarray, coord_names: Optional[Sequence[str]] = None, *,
                        shrinkage: bool = False) -> ReplicaCovariance:
    """Build the `ReplicaCovariance` of a (n_rep, n_data) matrix of replica-measured coordinate
    vectors: one row per independent twin replica, one column per admitted coordinate (typically
    `Selection.admitted` from `select_coordinates`, read off the same replicas the bias table came
    from).

    `shrinkage=False` (the DEFAULT, a correction of 2026-09-22): the plain sample covariance,
    Hartlap-corrected -- what both Hartlap (2007) and Sellentin & Heavens (2016) license at this
    record's own regime, p/R about 0.1 (A100.7: "about fifty coordinates at R = 500"), and the pairing
    `moment_block_nll`'s own default (`form="sellentin_heavens"`) is built to use (which reads `cov`
    directly and does not consult this function's `precision` at all).

    `shrinkage=True`: `shrink_to_diagonal`'s Ledoit-Wolf-style shrunk covariance, for a regime with p/R
    well above 0.1 where the plain sample covariance is too ill-conditioned to invert usefully (F287:
    "condition numbers near 1e42"). Its `precision` carries NO Hartlap factor (see `ReplicaCovariance`
    and `_NO_HARTLAP_ON_SHRUNK`): stack `form="hartlap"` in `moment_block_nll` with this `precision` ONLY
    once the resulting coverage has actually been checked against the twin, not on the strength of
    either paper alone.
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError(f"replica_covariance: X must be 2-D (n_rep, n_data), got shape {X.shape}")
    n_rep, n_data = X.shape
    if coord_names is None:
        coord_names = tuple(f"c{i}" for i in range(n_data))
    coord_names = tuple(coord_names)
    if len(coord_names) != n_data:
        raise ValueError(f"replica_covariance: {len(coord_names)} names for {n_data} columns")
    with np.errstate(divide="ignore", invalid="ignore"):
        cond_before = float(np.linalg.cond(np.cov(X, rowvar=False)))
    if shrinkage:
        S, S_shrunk, kappa, engine = shrink_to_diagonal(X)
        hl: Optional[float] = None
        precision = np.linalg.pinv(S_shrunk)
        engine = f"{engine}; {_NO_HARTLAP_ON_SHRUNK}"
    else:
        Xc = X - X.mean(0)
        S = (Xc.T @ Xc) / max(n_rep - 1, 1)
        S_shrunk, kappa = S.copy(), 0.0
        hl = hartlap_factor(n_rep, n_data)
        precision = hl * np.linalg.pinv(S_shrunk)
        engine = ("none (shrinkage=False): the plain sample covariance, Hartlap-corrected "
                  "(Hartlap, Simon & Schneider 2007; valid here because the covariance is unshrunk)")
    cond_after = float(np.linalg.cond(S_shrunk))
    return ReplicaCovariance(coord_names=coord_names, n_rep=n_rep, n_data=n_data, cov=S,
                              cov_shrunk=S_shrunk, shrinkage_kappa=kappa, shrinkage_engine=engine,
                              hartlap=hl, precision=precision, cond_before=cond_before,
                              cond_after=cond_after)


def moment_block_nll(observed: np.ndarray, predicted: np.ndarray, cov: np.ndarray, *,
                      precision: Optional[np.ndarray] = None, n_rep: Optional[int] = None,
                      form: str = "sellentin_heavens") -> float:
    """Minus twice the log-likelihood (up to an additive, parameter-independent constant) of one
    moment block: `observed` and `predicted` are length-p vectors (the admitted coordinates' twin-mean
    and model-predicted values, bias already subtracted on the data side per this record's standing
    rule), `cov` is their (p, p) covariance -- the PLAIN sample covariance for the default form below
    (`replica_covariance(shrinkage=False).cov`), since that form supplies its own correction for `cov`
    being a noisy estimate and does not want it pre-shrunk or pre-scaled.

    `form="sellentin_heavens"` (DEFAULT, a correction of 2026-09-22 -- see the module
    docstring's item (e) for why this and not "hartlap" is the default at this record's own p/R):
    Sellentin & Heavens 2016 (MNRAS 456, L132 letters). The covariance's own estimation uncertainty is
    carried into the likelihood's SHAPE instead of rescaling the precision matrix, replacing the
    Gaussian by a multivariate-t-like form with no Hartlap correction of its own (the two corrections
    are not stacked -- the heavier tails already carry the inflation):

        -2 ln L = n_rep * ln(1 + r^T Sigma_hat^-1 r / (n_rep - 1)) + ln det(Sigma_hat)

    using the PLAIN (un-Hartlap-scaled) `inv(cov)`, or `precision` if supplied directly. Requires
    `n_rep > 1` always (the degrees of freedom, `n_rep - 1`, appear inside the form itself, not only as
    a debiasing factor). As `n_rep` grows this form tends to the plain Gaussian quadratic form `quad +
    ln det(Sigma_hat)` (checked in `tests/test_moment_coords.py`): writing `q` for the quadratic form,
    `n ln(1 + q/(n-1)) - q -> q(2-q)/(2n)`, not `q^2/(2n)` alone (the two coincide only at q=1; verified
    here by direct Taylor expansion and numerically, both agreeing to four significant figures against
    `q(2-q)/(2n)` at n = 1e5 for q = 1, 3 and 8, where `q^2/(2n)` alone is off by a sign at q = 3 and 8).

    `form="hartlap"`: the ordinary Gaussian quadratic form, with the precision Hartlap-scaled unless an
    already-scaled `precision` is supplied directly. Pair this with a PLAIN, unshrunk `cov`
    (`replica_covariance(shrinkage=False)`) -- Hartlap's factor has no licence over a shrunk covariance
    (see the module docstring's item (e) and `ReplicaCovariance`'s own docstring):

        -2 ln L = alpha * (r^T Sigma_hat^-1 r) + ln det(Sigma_hat)      [alpha = hartlap_factor(n_rep, p)]

    `precision`, if given, is used AS-IS for the quadratic form (e.g. `ReplicaCovariance.precision`,
    already Hartlap-scaled) and `n_rep` is then optional; `cov` is still required and still supplies
    the log-determinant term (so `precision` and `cov` must describe the SAME covariance -- passing a
    `precision` built from a different matrix than `cov` silently mismatches the two terms). Without an
    explicit `precision`, `n_rep` is required so the Hartlap factor can be computed and applied to
    `inv(cov)`.

    Raises if `cov` is not positive definite, if `form` is not one of the two named above, or if a
    required `n_rep` is missing. Returns a plain float (never an array).
    """
    if form not in ("hartlap", "sellentin_heavens"):
        raise ValueError(f"moment_block_nll: unknown form {form!r}; want 'hartlap' or 'sellentin_heavens'")
    r = np.asarray(observed, dtype=float) - np.asarray(predicted, dtype=float)
    cov = np.asarray(cov, dtype=float)
    if cov.ndim != 2 or cov.shape[0] != cov.shape[1] or cov.shape[0] != r.size:
        raise ValueError(f"moment_block_nll: cov must be ({r.size}, {r.size}), got {cov.shape}")
    sign, logdet = np.linalg.slogdet(cov)
    if sign <= 0:
        raise ValueError("moment_block_nll: cov is not positive definite")
    p = r.size

    if precision is not None:
        prec = np.asarray(precision, dtype=float)
        if prec.shape != cov.shape:
            raise ValueError(f"moment_block_nll: precision shape {prec.shape} does not match cov {cov.shape}")
    else:
        prec = np.linalg.inv(cov)
        if form == "hartlap":
            if n_rep is None:
                raise ValueError("moment_block_nll: form='hartlap' needs n_rep to apply the Hartlap "
                                  "factor when `precision` is not given directly")
            prec = hartlap_factor(n_rep, p) * prec

    quad = float(r @ prec @ r)
    if form == "hartlap":
        return quad + logdet

    if n_rep is None:
        raise ValueError("moment_block_nll: form='sellentin_heavens' needs n_rep")
    nu = int(n_rep) - 1
    if nu <= 0:
        raise ValueError(f"moment_block_nll: form='sellentin_heavens' needs n_rep > 1, got {n_rep}")
    return float(n_rep) * math.log1p(quad / nu) + logdet


# ----------------------------------------------------------------------------------------------------
# A132.1, A132.2 and A132.7 (the thesis side's section 6, 2026-09-22): rule W1 acts on the SET in
# the window's Legendre basis; a coordinate's S0 power is read from its cumulant expansion; and the
# coordinate budget is a per-condition Shannon count.
# ----------------------------------------------------------------------------------------------------

def monomial_to_legendre(max_order: int) -> np.ndarray:
    """T with t^n = sum_k T[n, k] P_k(t) on [-1, 1], for n, k = 0..max_order (lower triangular).

    A vector of window moments in the monomial basis, m_n = integral t^n f dt, is T @ l with l the
    Legendre projections `legendre_window_moments` returns, so a covariance or a bias measured on the
    monomial basis moves to the Legendre one as T^-1 C T^-T. That product is exact and ill-conditioned
    (A132.1: the raw moments of orders 0 to 12 under white noise have a Hankel covariance of condition
    number 2.96e8), which is why the projections themselves are computed by quadrature, not through it.
    """
    from numpy.polynomial import legendre as _leg
    n = int(max_order) + 1
    if n < 1:
        raise ValueError(f"monomial_to_legendre: max_order must be >= 0, got {max_order!r}")
    T = np.zeros((n, n))
    for k in range(n):
        c = np.zeros(k + 1)
        c[k] = 1.0
        row = _leg.poly2leg(c)
        T[k, :len(row)] = row
    return T


def legendre_window_moments(nu: np.ndarray, y: np.ndarray, centre: float, half_width: float,
                            max_order: int, baseline: BaselineArg = None, n_points: int = 4001) -> np.ndarray:
    """The window's LEGENDRE projections, L_k = integral_{c-W}^{c+W} P_k((x - c)/W) f(x) dx for
    k = 0..max_order, f the baseline-subtracted trace, UN-normalised (the area is L_0): A132.1's basis.

    Under white noise of constant variance the projections are uncorrelated, Cov(L_j, L_k) proportional
    to delta_jk 2/(2k + 1), where the raw moments' correlation has a condition number near 8e7 at order
    12, so a set statistic computed here reads the bias and not the basis. Same window, interpolation and
    quadrature conventions as `raw_window_moment`. Returns an all-nan vector when the window reaches past
    the trace.
    """
    from numpy.polynomial import legendre as _leg
    grid = np.asarray(nu, dtype=float)
    yb = _apply_baseline(grid, np.asarray(y, dtype=float), baseline)
    w, c, n = float(half_width), float(centre), int(max_order)
    if w <= 0:
        raise ValueError(f"legendre_window_moments: half_width must be positive, got {w!r}")
    if (c - w) < grid[0] or (c + w) > grid[-1]:
        return np.full(n + 1, np.nan)
    g = np.linspace(c - w, c + w, n_points)
    yy = np.interp(g, grid, yb)
    tt = (g - c) / w
    out = np.empty(n + 1)
    for k in range(n + 1):
        coef = np.zeros(k + 1)
        coef[k] = 1.0
        out[k] = trapezoid(_leg.legval(tt, coef) * yy, g)
    return out


def whitened_set_bias(bias: np.ndarray, cov: np.ndarray, n_rep: Optional[int] = None) -> Dict[str, float]:
    """A132.1: rule W1(a) acts on the admitted SET, not coordinate by coordinate.

    A bias of 0.1 sd on every raw moment of orders 0 to 12 reads a whitened b' Sigma^-1 b of 0.031 with
    its signs aligned and 5.99e5 with the worst signs, so a per-coordinate clause bounds nothing. This
    returns the set's whitened bias `chi2` = b' Sigma^-1 b, its null expectation `null_mean` = p / R when
    the bias and Sigma come from the same R replicas (the bias's own sampling error, whitened, has
    expectation trace(Sigma^-1 Sigma / R) = p / R; nan when `n_rep` is not given), `p`, and `cond`, the
    condition number of Sigma. Computed by a Cholesky solve and REFUSED (ValueError) when Sigma is not
    positive definite: a singular set is A100.1's ratio beside its members, not a small bias.
    """
    b = np.asarray(bias, dtype=float).ravel()
    S = np.asarray(cov, dtype=float)
    if S.shape != (b.size, b.size):
        raise ValueError(f"whitened_set_bias: cov is {S.shape}, bias has {b.size} coordinates")
    if not (np.all(np.isfinite(b)) and np.all(np.isfinite(S))):
        raise ValueError("whitened_set_bias: a non-finite bias or covariance entry")
    try:
        Lc = np.linalg.cholesky(S)
    except np.linalg.LinAlgError as e:
        raise ValueError("whitened_set_bias: the covariance is not positive definite, so the set carries a "
                         "coordinate that is a function of the others (A100.1)") from e
    z = np.linalg.solve(Lc, b)
    p = int(b.size)
    return {"chi2": float(z @ z), "null_mean": (p / float(n_rep)) if n_rep else float("nan"),
            "p": float(p), "cond": float(np.linalg.cond(S))}


def shannon_coordinate_budget(half_width_mhz: float, gamma_mhz: float, snr: float) -> float:
    """A132.7 (bunker1983): about 2 W t_c independent numbers per trace, where t_c = ln(snr)/(pi Gamma) is
    the time at which a Lorentzian line of FWHM Gamma has its Fourier transform, exp(-pi Gamma t), fall to
    1/snr of its peak; beyond it the transform is noise. W and Gamma in MHz, so t_c is in microseconds and
    the count is dimensionless. The windows are NESTED, so a set of windows shares the budget of the widest
    and never sums them. At Gamma = 3 MHz and snr = 1000 give 31 at 21 MHz and 19 at 13.
    """
    if not (half_width_mhz > 0 and gamma_mhz > 0 and snr > 1):
        raise ValueError("shannon_coordinate_budget: needs half_width_mhz > 0, gamma_mhz > 0 and snr > 1")
    return 2.0 * float(half_width_mhz) * math.log(float(snr)) / (math.pi * float(gamma_mhz))


def moment_s0_support(order: int, clean: Iterable[int] = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)) -> Tuple[int, ...]:
    """A132.2: the S0 powers present in the central moment mu_n once it is written through CUMULANTS.

    Cumulants above the first are origin-free and ADD under convolution, so each is the ramp's (S0^k)
    plus the rest of the line's; a cumulant whose rest vanishes is CLEAN (every k >= 3 for a Gaussian
    rest, the odd k >= 3 for any symmetric one: pass `clean` accordingly), and kappa_2 is never clean,
    since the natural, collisional, transit and laser widths all sit in it. The moment-cumulant relation
    mu_n = sum_k C(n-1, k-1) kappa_k mu_(n-k), with kappa_1 = 0 about the mean, then gives mu_n as a
    polynomial in S0, and this returns its powers. A moment is homogeneous, and `s0_w0_power`'s
    total-order rule holds for it, exactly when the support is (n,): mu_3 = kappa_3 is, mu_4 = kappa_4 +
    3 kappa_2^2 is not (support (0, 2, 4)), which is A100.6's caveat made computable rather than stated.

    This stays a cumulant recursion and not a rename (owner order O49, 2026-09-22: A132.2 was
    withdrawn at its source, method_vs_literature.md section 6.8). The S0 support this function
    returns is the canonical, separable form's, because the recursion above separates the ramp's own
    S0 powers from the rest of the line's ONLY through cumulants' additivity under convolution, which
    the volume model does not have (its kernel varies across the collected volume, the record's own
    rule that a convolution is a condition and not a form). The volume model's S0 and w0 powers are instead read
    off its OWN moments directly, across S0 and w0 ladders (C6c), never through this recursion.
    """
    n = int(order)
    if n < 0:
        raise ValueError(f"moment_s0_support: order must be >= 0, got {order!r}")
    clean = {int(k) for k in clean}

    def kappa(k: int) -> Dict[int, float]:
        if k == 1:
            return {}
        return {k: 1.0} if k in clean else {k: 1.0, 0: 1.0}

    def mul(a: Dict[int, float], b: Dict[int, float], s: float = 1.0) -> Dict[int, float]:
        out: Dict[int, float] = {}
        for i, x in a.items():
            for j, v in b.items():
                out[i + j] = out.get(i + j, 0.0) + s * x * v
        return out

    mu: List[Dict[int, float]] = [{0: 1.0}]
    for m in range(1, n + 1):
        acc: Dict[int, float] = {}
        for k in range(1, m + 1):
            for pw, v in mul(kappa(k), mu[m - k], float(math.comb(m - 1, k - 1))).items():
                acc[pw] = acc.get(pw, 0.0) + v
        mu.append({pw: v for pw, v in acc.items() if v != 0.0})
    return tuple(sorted(mu[n]))


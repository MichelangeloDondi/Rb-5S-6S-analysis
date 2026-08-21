"""The digital twin: simulate the experiment you have not built, then read its precision.

WHAT THIS IS. The same forward model this package fits real data with can
GENERATE data, so an experiment can be run in software before a single optic
is mounted: choose a line and an apparatus, synthesise the traces the real
instrument would record, fit them back with the same fitter the real data
would meet, and read the achievable precision from the fit's own covariance.
That loop, simulate -> fit -> identify what is degenerate -> change the
design -> forecast again, is the package's actual value to a stranger, and
this module is its public form.

TWO FUNCTIONS CARRY IT. `synthetic_traces` generates the data, with noise
either as a constant fraction of peak (the simple mode every tutorial starts
with) or as a MEASURED noise law evaluated through `rb5s6s.noise.sigma_of_v`,
so a characterised detector simulates under its own measured law rather
than under a convenient one. `forecast_precision` is the design study: Monte-Carlo over
synthetic_traces -> fit_condition at the chosen design point, returning the
median parameter uncertainties, the scalings measured by RE-RUNNING the study
at scaled designs rather than by asserting exponents, and the ceilings the
model layer provides (blackbody via `blackbody.t_max`, pumping depletion via
`cascade.amplitude_factor`).

WHAT THIS IS NOT. Not a closed-form Fisher forecast: the numbers come from
the same nonlinear fitter the real data would meet, which is slower and
honest. Not a substitute for `scripts/run_projections.py`, which is this
campaign's bespoke projection report over its own committed record.

VALIDITY DOMAIN, per the estimand contract. A forecast holds for the stated
truth, design and noise model, and for nothing else. Every returned mapping
carries an `assumptions` entry naming them, and a forecast whose assumptions
are not read is a number, not a forecast.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.special import jv

from .lineshape import composite_profile
from .linefit import fit_condition
from .noise import sigma_of_v

__all__ = ["synthetic_traces", "forecast_precision", "n_eff",
           "external_constraint_gain"]


def n_eff(n: int, tau_int: float) -> float:
    """Effective number of independent samples: n over the correlation time.

    The quantity is defined in `rb5s6s.sharing_bic`'s docstring and was
    computed inline in three places before this helper existed. It is the
    repository's effective-sample-size convention, an approximation rather
    than a theorem, and downstream information criteria that use it must pair
    it with the WHITENED chi-square (see `rb5s6s.model_compare`).
    """
    if n <= 0:
        raise ValueError(f"sample count must be positive: {n}")
    if tau_int < 1.0:
        raise ValueError(f"tau_int below one sample is not meaningful: {tau_int}")
    return n / tau_int


def synthetic_traces(gamma_coll: float, sigma_laser: float, transit_fwhm: float,
                     *, span_mhz: float = 60.0, n_points: int = 2000,
                     n_traces: int = 5, noise: object = 0.004,
                     amp: float = 1.0, amp_spread: float = 0.05,
                     offset: float = 0.010, offset_spread: float = 0.002,
                     centre_mhz: float = 0.0,
                     laser_kind: str = "gaussian", gamma_l: float = 0.0,
                     rng: Optional[np.random.Generator] = None,
                     ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Generate the traces your instrument would record for this line.

    The pattern is `examples/synthetic_recovery.py`'s, promoted to the public
    API: the composite profile on a fine grid, interpolated onto the chosen
    frequency axis, normalised, then given per-trace amplitude and offset
    spread so the repeats differ the way real repeats do.

    ``noise`` is either a float, the standard deviation as a FRACTION OF PEAK
    added i.i.d. per point (the simple mode), or a noise-law dict as returned
    by `rb5s6s.noise.condition_noise_model`, in which case each point's sigma
    comes from the law evaluated at that point's signal level, which is how
    the real detector behaves.

    Returns (freqs, volts), each a list of arrays, one per trace, in the form
    `fit_condition` accepts.
    """
    if rng is None:
        rng = np.random.default_rng()
    nu = np.linspace(-span_mhz, span_mhz, n_points)
    # gamma_l and laser_kind reach the GENERATOR as well as the fitter
    # (2026-08-21). K2's hostile worlds are generated here and fitted by
    # linefit, so a twin that cannot INJECT a Lorentzian laser component
    # cannot test whether the fitter recovers one, and a coverage or
    # false-positive rate measured on a twin that only ever emits Gaussian
    # kernels would be a statement about a world the question is not about.
    grid, prof = composite_profile(gamma_coll, sigma_laser, transit_fwhm,
                                   laser_kind, gamma_l=gamma_l)
    shape = np.interp(nu - centre_mhz, grid, prof, left=0.0, right=0.0)
    peak = shape.max()
    if peak <= 0.0:
        raise ValueError("the composite profile vanished on this axis: widen "
                         "span_mhz or check the widths")
    shape = shape / peak

    freqs: List[np.ndarray] = []
    volts: List[np.ndarray] = []
    for i in range(n_traces):
        a = amp * (1.0 + amp_spread * i)
        base = offset + offset_spread * i
        clean = a * shape + base
        if isinstance(noise, dict):
            sig = np.asarray([sigma_of_v(v, noise) for v in clean])
            v = clean + sig * rng.standard_normal(nu.size)
        else:
            v = clean + float(noise) * a * rng.standard_normal(nu.size)
        freqs.append(nu.copy())
        volts.append(v)
    return freqs, volts


def _one_trial(truth: Dict, design: Dict, rng: np.random.Generator) -> Dict:
    freqs, volts = synthetic_traces(
        truth["gamma_coll"], truth["sigma_laser"], truth["transit_fwhm"],
        span_mhz=design.get("span_mhz", 60.0),
        n_points=design.get("n_points", 2000),
        n_traces=design.get("n_traces", 5),
        noise=design.get("noise", 0.004),
        amp=design.get("amp", 1.0),
        rng=rng)
    return fit_condition(freqs, volts, T_C=design.get("T_C", 130.0),
                         transit_fwhm=truth["transit_fwhm"],
                         law=design.get("law"))


def forecast_precision(truth: Dict, design: Dict, *, n_trials: int = 8,
                       seed: int = 0, scalings: bool = True) -> Dict:
    """Forecast what your design would measure, by running it in software.

    ``truth`` holds the line you believe you have: gamma_coll, sigma_laser
    and transit_fwhm, in MHz FWHM on the transition axis. ``design`` holds
    the apparatus choices: span_mhz, n_points, n_traces, noise (fraction of
    peak or a measured law), amp, and T_C.

    The forecast is a Monte-Carlo over ``synthetic_traces -> fit_condition``:
    the returned uncertainties are the medians of the fit's own reported
    errors across ``n_trials`` independent datasets, so they are what the
    real analysis would report, not a linearised bound.

    With ``scalings=True`` the study is RE-RUN at doubled power (amplitude
    scaled by four and noise fraction halved, which is the two-photon
    signal-to-noise arithmetic where signal goes as power squared and shot
    noise as its root), at doubled repeats, and at doubled points, and the
    measured ratios are returned. Measuring the exponent instead of asserting
    it costs three more Monte-Carlos and removes an assumption.
    """
    rng = np.random.default_rng(seed)
    trials = [_one_trial(truth, design, rng) for _ in range(n_trials)]

    def med(key: str) -> float:
        vals = [t[key] for t in trials if key in t and np.isfinite(t[key])]
        return float(np.median(vals)) if vals else float("nan")

    out: Dict = {
        "gamma_coll_err": med("gamma_coll_err"),
        "sigma_laser_err": med("sigma_laser_err"),
        "corr_laser_coll": med("corr_laser_coll"),
        "chi2_red": med("chi2_red"),
        "n_trials": n_trials,
        "assumptions": (
            "truth as stated, design as stated, noise model as stated, "
            "transit width held fixed at its true value, and the two-photon "
            "SNR arithmetic (signal ~ P^2, shot noise ~ P) for the power "
            "scaling"),
    }

    if scalings:
        base = out["gamma_coll_err"]
        scaled: Dict[str, float] = {}
        for label, mod in (
            ("power_x2", {"amp": design.get("amp", 1.0) * 4.0,
                          "noise": _scaled_noise(design, 0.5)}),
            ("repeats_x2", {"n_traces": design.get("n_traces", 5) * 2}),
            ("points_x2", {"n_points": design.get("n_points", 2000) * 2}),
        ):
            d2 = dict(design)
            d2.update(mod)
            rng2 = np.random.default_rng(seed + 1)
            t2 = [_one_trial(truth, d2, rng2) for _ in range(max(4, n_trials // 2))]
            vals = [t["gamma_coll_err"] for t in t2 if np.isfinite(t.get("gamma_coll_err", np.nan))]
            scaled[label] = float(np.median(vals)) / base if vals and base else float("nan")
        out["gamma_coll_err_ratio"] = scaled
    return out


def _scaled_noise(design: Dict, factor: float) -> object:
    noise = design.get("noise", 0.004)
    if isinstance(noise, dict):
        # A measured law scales with the light through its signal argument
        # automatically; the fraction-of-peak shortcut needs the explicit
        # factor. Returning the law unchanged is correct because sigma_of_v
        # is evaluated at the SCALED signal level.
        return noise
    return float(noise) * factor


def comb_tooth_weights(two_beta, n_orders=8, drive_hz=None, retro_delay_s=None):
    """Two-photon comb tooth weights, in and beyond the zero-delay limit.

    The textbook weights J_s(2*beta)^2 assume every pathway pair (n, s-n)
    interferes with zero relative phase. With the modulator in the COMMON
    path, one photon comes from the retro beam delayed by tau, the pathway
    (n, s-n) carries a phase (s-n)*Omega*tau, and the coherent sum collapses
    exactly to a single tone at EFFECTIVE depth 2*beta*cos(pi*f*tau): the
    tooth weights become J_s(2 beta cos(pi f tau))^2 for an atom at delay
    tau, averaged over the cell. The crossover pairs (k, -k) that cancel out
    of the carrier at zero delay return to it under the average, which is
    why a smeared carrier never nulls at 2*beta = 2.405.

    Parameters. two_beta: the total modulation depth 2*beta. n_orders: the
    weights are returned for s = 0 .. n_orders-1 (negative orders mirror
    them under pure PM). drive_hz and retro_delay_s: the drive frequency and
    the (min, max) one-way-plus-return delay between the forward and retro
    photons across the cell; leave both None for the zero-delay limit.

    Returns a numpy array w with w[s] the weight of tooth s. The invariant
    w[0] + 2*sum(w[1:]) = 1 holds in both limits (phase modulation conserves
    the two-photon signal), and the tests assert it.

    Validity. Pure phase modulation on the common path, or no modulation on
    the forward arm. Residual amplitude modulation adds a MEASURED deviation
    on top of either limit (the +-k height asymmetry of constants.py). With
    the modulator in the retro arm alone the pathways carry distinct s and
    never interfere, so the zero-delay formula is exact at any drive; that
    placement is what plan chapter 8 section 10b.4a now prescribes for the
    coincidence block.
    """
    s = np.arange(n_orders)
    if drive_hz is None and retro_delay_s is None:
        return jv(s, two_beta) ** 2
    if drive_hz is None or retro_delay_s is None:
        raise ValueError("give both drive_hz and retro_delay_s, or neither")
    lo, hi = retro_delay_s
    tau = np.linspace(lo, hi, 2001)
    eff = two_beta * np.cos(np.pi * drive_hz * tau)
    return np.array([float(np.mean(jv(k, eff) ** 2)) for k in s])


def external_constraint_gain(correlation: float) -> float:
    """What pinning one side of a correlated pair buys the other, as a factor.

    For a jointly estimated pair with correlation rho, learning one parameter
    exactly reduces the other's variance to (1 - rho^2) of its joint value, so
    its uncertainty falls by

        sqrt(1 - rho^2).

    THIS IS WHY AN INDEPENDENT MEASUREMENT IS A DESIGN LEVER AND MORE DATA IS
    NOT. Collecting more traces or a wider span shrinks both uncertainties
    while leaving rho essentially untouched, because rho is a property of the
    lineshape rather than of the sample size. An external constraint changes
    rho's consequences instead, and at rho near -0.92 it is worth a factor of
    about 2.5 on the partner parameter, which no plausible increase in data
    volume matches.

    Returns the FACTOR the partner's uncertainty is multiplied by, so smaller
    is better and 1.0 means the pair was already independent.
    """
    if not -1.0 < correlation < 1.0:
        raise ValueError(f"correlation must lie strictly inside (-1, 1): {correlation}")
    return math.sqrt(1.0 - correlation ** 2)

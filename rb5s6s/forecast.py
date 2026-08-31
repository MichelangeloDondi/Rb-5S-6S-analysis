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

from . import blackbody, cascade, stark
from .lineshape import composite_profile, model_profile
from .linefit import fit_condition
from .noise import sigma_of_v

__all__ = ["synthetic_traces", "build_world_trace", "forecast_precision",
           "n_eff", "external_constraint_gain"]


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
                     s0: float = 0.0,
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

    ``s0`` IS THE ONE ASYMMETRIC TERM, and it defaults to zero (2026-08-30).
    Until it existed this generator only ever called `composite_profile`, whose
    three kernels are all symmetric, so every trace it had ever produced had a
    skewness of about 1e-16. That matters more than it sounds: the AC-Stark
    ramp is the only asymmetric term in the model, and the asymmetry it puts
    into the line is the observable this record is built on. Its third
    cumulant is +S0^3/135 (sign per docs/methods/03 and stark_ramp's own
    axis), and the statement of what a windowed readout keeps of it was
    replaced, the account in docs/history/02): the Lorentzian's even
    cumulants diverge, its odd moments cancel under a window symmetric about
    the line's own centre, so a SELF-CENTRED windowed kappa_3 keeps a
    truncation-limited fraction of the ramp's value
    (results/cumulant_window_check.csv, survival rows) while a lab-frame
    window under drift takes on (2/pi)*gamma*delta*W of first-cumulant
    leakage (gamma the half-width). Drift immunity belongs to self-centred readouts,
    the fit's free per-scan centre above all. Derivation and numbers:
    docs/wiki/third-cumulant.md. A generator
    that cannot emit the asymmetry cannot forecast a precision on it, and
    cannot test a fitter against it.

    WHY THE DEFAULT IS ZERO, AND WHAT IT COSTS. At the 2025 configuration the
    ramp broadens a 5.3 MHz line by about 2 kHz against a 24 kHz fit error on
    gamma_coll. That is derivable from the ramp's own variance, S0^2/18, added
    in quadrature -- physics and algebra, no Monte-Carlo -- so the omission
    costs nothing there, and every committed row of
    `results/campaign_twin_forecast.csv` was produced without it. The s0 = 0
    branch below is the ORIGINAL code path, untouched, so those rows do not
    move. The omission stops being safe at about S0 = 0.91 MHz, where the
    added width equals the fit error; at the proposed w0 = 16 um focus S0 rises
    roughly sixteenfold, since S0 goes as 1/w0^2, and the ramp then dominates
    the width budget. FORECAST THAT SESSION WITH s0 SET.

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
    # The same argument is why s0 reaches the generator, one term later.
    if s0 > 0.0:
        # model_profile convolves lineshape.stark_ramp, so the -2/3 S0 pull and
        # the skew both come from the library rather than from a literal here,
        # and the ramp's coded SIDE is inherited rather than re-chosen (it is
        # an open question: tests/test_ramp_side_matches_the_polarizability).
        shape = model_profile(nu - centre_mhz, gamma_coll=gamma_coll,
                              sigma_laser_fwhm=sigma_laser,
                              transit_fwhm=transit_fwhm, s0=s0,
                              laser_kind=laser_kind, gamma_l=gamma_l)
    else:
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


def build_world_trace(power_w: float, kappa: float, t_c: float,
                     order_idx: int, n_rungs: int,
                     rng: np.random.Generator, layers: Dict, *,
                     positions: Dict[str, float], shares: Dict[str, float],
                     gamma_coll: float, sigma_laser_fwhm: float,
                     transit_fwhm: float, power_max_w: float,
                     cycles_at_max: float, drift_mhz_total: float,
                     noise_frac_bright: float, adc_levels: int,
                     range_headroom: float = 1.25,
                     offset: float = 0.01) -> Tuple[np.ndarray, np.ndarray, Dict]:
    """One campaign trace: every peak in `positions`, one vertical range.

    Promoted from `examples/campaign_twin.py` (2026-08-31) so the example
    became a caller and the physics layers became options of this one public
    path. Each `layers` key is a committed claim the twin can switch on to
    test and off to isolate: ``cascade`` (pumping depletion of the
    amplitudes, `rb5s6s.cascade`), ``saturation`` (drive-dependent companion
    width, `rb5s6s.stark`), ``stark`` (the AC-Stark ramp convolved through
    `model_profile` -- the one asymmetric term; a rigid shift instead of the
    convolution is exactly the defect this builder was corrected for),
    ``bbr`` (the blackbody centre shift), ``drift`` (a linear session drift
    of the common centre across the rung order), ``quantise`` (the ADC step
    of one snug vertical range anchored `range_headroom` above the brightest
    peak). A missing key raises KeyError on purpose, the
    `annotate_results_status` convention: every layer must be decided, not
    defaulted into.

    The noise is shot-like, sigma growing as the root of the local signal
    and anchored so the brightest rung's peak carries `noise_frac_bright` of
    itself -- the regime the 2025 noise law measured (variance linear in
    signal). Amplitudes scale as the two-photon P^2 with the hyperfine
    `shares`; positions and shares stay caller-owned so their provenance
    stays beside their values, in the example or the scenario layer.

    Returns (nu, volts, truth_amps): the frequency axis (MHz, transition
    axis), the one recorded trace, and each peak's injected amplitude.
    """
    nu = np.linspace(min(positions.values()) - 60.0, 60.0, 6000)
    s0 = kappa * power_w
    p_rel = (power_w / power_max_w)

    v = np.zeros_like(nu)
    truth_amps = {}
    for peak, share in shares.items():
        amp = share * p_rel ** 2                      # two-photon: signal ~ P^2
        if layers["cascade"]:
            amp *= cascade.amplitude_factor(peak, cycles_at_max * p_rel)
        gamma = gamma_coll
        if layers["saturation"]:
            gamma = gamma + stark.companion_gamma_mhz(s0, peak)
        centre = positions[peak]
        if layers["bbr"]:
            centre += -blackbody.shift_hz(273.15 + t_c) / 1e6
        if layers["drift"]:
            centre += drift_mhz_total * (order_idx / max(n_rungs - 1, 1) - 0.5)
        # THE RAMP IS CONVOLVED, NOT APPLIED AS A SHIFT (corrected
        # 2026-08-30): a rigid translation carries only the first moment and
        # leaves the trace symmetric, while the self-centred windowed third
        # cumulant (docs/wiki/third-cumulant.md) is the channel this record
        # is built on. model_profile convolves lineshape.stark_ramp, so the
        # pull and the skew both come from the library, and the ramp's coded
        # SIDE is inherited rather than re-chosen (it is an open question:
        # tests/test_ramp_side_matches_the_polarizability).
        shape = model_profile(nu - centre,
                              gamma_coll=gamma,
                              sigma_laser_fwhm=sigma_laser_fwhm,
                              transit_fwhm=transit_fwhm,
                              s0=(s0 if layers["stark"] else 0.0))
        v += amp * (shape / shape.max())
        truth_amps[peak] = amp
    v += offset                                        # detector offset
    # shot-like noise: sigma grows as the root of the LOCAL signal, anchored
    # so the brightest rung's peak carries noise_frac_bright of itself; the
    # noise falls with the signal while the quantisation step does not,
    # which is what makes one vertical range survivable at the dim rung.
    bright_peak = max(shares.values()) + offset
    sigma = noise_frac_bright * np.sqrt(np.clip(v, 0.0, None) * bright_peak)
    v = v + sigma * rng.standard_normal(nu.size)
    if layers["quantise"]:
        step = range_headroom * (max(shares.values()) + offset) / adc_levels
        v = np.round(v / step) * step
    return nu, v, truth_amps


def _one_trial(truth: Dict, design: Dict, rng: np.random.Generator) -> Dict:
    # s0 is a property of the WORLD, so it lives in `truth` beside the widths,
    # not in `design` beside the acquisition settings. Absent, it is zero and
    # both generator and fitter behave exactly as they did before 2026-08-30.
    s0 = float(truth.get("s0", 0.0))
    freqs, volts = synthetic_traces(
        truth["gamma_coll"], truth["sigma_laser"], truth["transit_fwhm"],
        span_mhz=design.get("span_mhz", 60.0),
        n_points=design.get("n_points", 2000),
        n_traces=design.get("n_traces", 5),
        noise=design.get("noise", 0.004),
        amp=design.get("amp", 1.0),
        s0=s0,
        rng=rng)
    # The fitter is MATCHED to the injected ramp by default. `design["fit_s0"]`
    # deliberately mismatches it, which is how the twin measures what omitting
    # the ramp costs the widths rather than assuming it costs nothing: at the
    # 2025 S0 the answer is about 0.1 sigma on gamma_coll, and at a tight focus
    # it is not. A twin that generates and fits with the same s0 can never see
    # that, the way this one could not see it while s0 did not exist.
    return fit_condition(freqs, volts, T_C=design.get("T_C", 130.0),
                         transit_fwhm=truth["transit_fwhm"],
                         s0=float(design.get("fit_s0", s0)),
                         law=design.get("law"))


def forecast_precision(truth: Dict, design: Dict, *, n_trials: int = 8,
                       seed: int = 0, scalings: bool = True,
                       return_trials: bool = False) -> Dict:
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
        # return_trials=True adds the raw per-trial list, so a caller can
        # state the world-to-world spread of the reported error instead of
        # quoting the median as if it were exact. Additive, default off:
        # every committed CSV predates the key and does not read it.
        **({"gamma_coll_err_trials":
            [t.get("gamma_coll_err", float("nan")) for t in trials]}
           if return_trials else {}),
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

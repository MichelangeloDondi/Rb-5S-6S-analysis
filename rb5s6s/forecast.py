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

import inspect
import math
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.special import jv

from . import blackbody, cascade, model_registry, stark, twin_volume
from .fullmodel import full_profile
from .lineshape import (composite_profile, local_ramp_density, model_profile,
                        ramp_mixture, stark_ramp)
from .linefit import fit_condition, GNAT_MHZ, JOINT_N_PATH, JOINT_SEED, JOINT_Z_RATIO
from .constants import W0_CENTRAL_M
from .noise import sigma_of_v
from .volume_line import GaussianBeam

__all__ = ["synthetic_traces", "build_world_trace", "forecast_precision",
           "n_eff", "external_constraint_gain", "twin_preflight"]


def twin_preflight(executes, registry: Optional[str], *, T_C: float, power_w: float = 0.0) -> dict:
    """O58: a twin refuses BEFORE its first draw unless it is the registry's twin, or a declared study.

    `executes` is the set of registry term ids the configured generator WILL apply, read off its own
    knobs by the caller. `registry=None` is a run standing behind a result: it must carry exactly the
    twin's registry terms at the regime (`model_registry.preflight`). A string is a STUDY's reason, six
    words or more, and every term the configuration drops or adds is declared with it: the weak-field
    width study, the layered generator (which never carries the joint line's chirp), a unit test of the
    noise layer. Returns the block a manifest carries."""
    regime = "2025" if (float(T_C) <= 130.0 + 1e-9 and float(power_w) <= 0.270 + 1e-9) else "campaign"
    executes = set(executes)
    if registry is None:
        return model_registry.preflight("twin", regime, executes)
    carried = set(model_registry.carried_term_ids("twin", regime))
    why = str(registry)
    return model_registry.preflight("twin", regime, executes, scope="study",
                                    gaps={t: why for t in carried - executes},
                                    extras={t: why for t in executes - carried})


def _correlate(w: np.ndarray, tau_int: float) -> np.ndarray:
    """Filter unit-variance white noise to a measured integrated correlation time.

    THE TWIN DREW INDEPENDENT SAMPLES UNTIL 2026-09-12 AND THE CHARTER SAYS IT
    MUST NOT. The repository's standing rules bind the exhibit to a twin that
    injects the measured noise correlation, and all three generator sites called
    `rng.standard_normal` directly. `synthetic_traces` is the sharp case: it
    accepts the committed noise model as a dict and reads its amplitude
    coefficients through `sigma_of_v`, while `tau_int` sat unused in the same
    dictionary `load_noise_model` returned. `n_eff` below divided sample counts
    by a correlation the generator never produced.

    An AR(1) with coefficient `a` has autocorrelation `a**k` and integrated
    time `(1+a)/(1-a)`, so `a = (tau_int-1)/(tau_int+1)` hits the measured
    time, and the `sqrt(1-a*a)` factor holds the marginal variance at one so
    the amplitude law is untouched.

    AT `tau_int = 1.0` THIS RETURNS ITS INPUT UNCHANGED, which is what keeps
    every existing caller and every committed CSV byte-identical: white is the
    default and a caller opts in.

    THE DEFAULT IS WHITE AND ON THIS ARCHIVE THAT IS CORRECT, which is the
    opposite of what this function was written to fix and is why the paragraph
    stands. `run_twin_completeness.py` compares real and twin wings under ONE
    estimator: the archive reads 0.960 +- 0.076 after a linear detrend, the
    twin white 0.823 +- 0.061, and the twin driven at the committed `tau_int`
    2.09 +- 0.14. So white reproduces the archive's detrended residual and the
    law's time, fed to an AR(1), overstates it.

    WHAT THE LAW'S `tau_int` MEASURES IS A TILT, NOT A BROADBAND CORRELATION.
    The same archive wings read 1.88 +- 0.13 with only the mean removed, and a
    straight line takes that back to 0.96, while an AR(1) survives both
    removals. So the committed 2.515 is dominated by a slow baseline tilt
    within each trace, and synthesising it here as an AR(1) models the wrong
    process. The missing twin term is that per-trace tilt, which this builder
    does not generate: its `drift` layer moves the common CENTRE across the
    rung order and leaves the baseline flat.

    AN AR(1) COSTS 1.59 TIMES ON A FITTED WIDTH and that number is an upper
    bound on what correlation can do here, not the archive's penalty. A free
    linear baseline in the fit does NOT absorb it, measured both ways, because
    a broadband correlation is not a trend. Pass `tau_int` when a broadband
    process is what you mean; do not pass the law's value expecting the
    archive's noise.

    THE COMMITTED LAW IS NOT SELF-CONSISTENT AND THIS TAKES THE CONSERVATIVE
    BRANCH. `results/noise_model.csv` gives `tau_int = 2.515` beside
    `rho1 = 0.098`, and an AR(1) at that first lag has an integrated time of
    1.217, so the measured integral is 2.07 times what its own first lag
    implies: a small first lag with a long tail, which one AR(1) cannot be both
    of. A statistic's variance is set by the INTEGRATED time, so that is what
    is matched; the synthesised first lag is then 0.431 against a measured
    0.098, and saying so here is the point. Matching `rho1` instead would
    understate the correlation and overstate the information.
    """
    if not (tau_int > 1.0):
        if tau_int < 1.0:
            raise ValueError(
                f"tau_int below one sample is not a correlation time: {tau_int}")
        return w
    a = (tau_int - 1.0) / (tau_int + 1.0)
    root = math.sqrt(1.0 - a * a)
    x = np.empty_like(w)
    x[0] = w[0]
    for i in range(1, w.size):
        x[i] = a * x[i - 1] + root * w[i]
    return x


def _traces_from_shape(nu: np.ndarray, shape: np.ndarray, *, n_traces: int, noise: object,
                       amp: float, amp_spread: float, offset: float, offset_spread: float,
                       halo_fraction: float, tau_int: Optional[float], residual_source,
                       rng: np.random.Generator) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """THE SHARED NOISE LAYER (C6b noise wave, 2026-09-22): every trace `synthetic_traces` below
    returns, under EITHER `model`, gets its per-trace amplitude/offset spread, its halo, its
    correlated noise and its residual-seam draw from here. Noise is added AFTER the clean line
    exists and does not depend on the model form that built `shape` (peak-normalised, one peak
    of 1.0), so this is the ONE copy of that logic: before this wave `model="joint"` traces were
    built by `twin_volume.synthetic_traces`'s own, separate, i.i.d.-only noise loop, which is why
    `tau_int`, `residual_source` and a non-zero `halo_fraction` used to raise under `model="joint"`
    instead of being silently dropped -- they are threaded here instead, unconditionally.

    `noise` is either a float (the i.i.d./correlated standard deviation as a fraction of peak) or
    a noise-law dict (`rb5s6s.noise.condition_noise_model`/`load_noise_model`), each point's sigma
    then read through `sigma_of_v`. `tau_int` (explicit, or read from the noise-law dict's own
    `tau_int` when `tau_int is None`) filters unit-variance white noise to that integrated
    correlation time (`_correlate`). `residual_source`, a callable `(rng, n) -> array` of n
    unit-variance samples, REPLACES that filtered draw outright when given (the moving-block
    resamples of `scripts/run_residual_resampling.py`). `halo_fraction` raises the per-trace
    amplitude by a fixed fraction, flat across the scan (the trapped-light re-excitation term).
    """
    freqs: List[np.ndarray] = []
    volts: List[np.ndarray] = []
    for i in range(int(n_traces)):
        a = float(amp) * (1.0 + float(amp_spread) * i) * (1.0 + float(halo_fraction))
        base = float(offset) + float(offset_spread) * i
        clean = a * shape + base
        _tau = (tau_int if tau_int is not None
                else (float(noise.get("tau_int", 1.0))
                      if isinstance(noise, dict) else 1.0))
        _w = (np.asarray(residual_source(rng, nu.size), float) if residual_source is not None
              else _correlate(rng.standard_normal(nu.size), _tau))
        if isinstance(noise, dict):
            sig = np.asarray([sigma_of_v(v, noise) for v in clean])
            v = clean + sig * _w
        else:
            v = clean + float(noise) * a * _w
        freqs.append(nu.copy())
        volts.append(v)
    return freqs, volts


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


# ---------------------------------------------------------------------------------------------------------------------
# THE WORLD A TRACE WAS DRAWN FROM TRAVELS WITH IT, AND THE TWIN'S FITTER REFUSES A WORLD IT DOES NOT DESCRIBE
# (F559, F560, 2026-09-26). One class fired twice in one night: leg 1 of the twin validation fitted a world drawn on the
# separable line with a fitter on the joint line, and the kernel worlds drew every temperature rung at 110 C and fitted
# each at its own. Each was a sentence nobody could check. So every trace `synthetic_traces` and `build_world_trace`
# return is a `WorldTrace`, an array that carries what its clean line was drawn at through arithmetic, masking and
# pickling, and `fit_world` / `fit_world_beta` compare it with the fitter's own settings before the fit, reading the
# fitter's defaults from its signature rather than restating them. The door is here and not in `linefit`, which sits in
# the kernel digest, so a guard there would re-open every node; `tests/test_twin_world_fit_door.py` refuses a twin
# harness that calls the fitter around it.
# ---------------------------------------------------------------------------------------------------------------------

class WorldTrace(np.ndarray):
    """A synthetic trace carrying `world`, the dict of what its clean line was drawn at: `form` ("joint",
    "convolution" or "separable"), `T_C`, `s0`, `w0_m`, `m2`, `z_ratio` and `transit_fwhm`, each None where the form
    does not read it. Slicing, masking, pickling and arithmetic with a scalar keep it; `np.asarray`, `np.interp` and
    `np.concatenate` return a plain array, which `fit_world` refuses as a trace with no world. A full reduction
    returns a plain scalar, so `v.max()` is the number it was before the tag existed.

    AN ARRAY OPERATION AFTER THE DRAW CHANGES THE WORLD (F566): adding or multiplying an
    array into a trace (a tilt, a second line, a harness's own noise) makes a line the generator did not draw, so
    the result's world carries `post_draw` and the door refuses it unless declared. A scalar (an amplitude, an
    offset, a rounding step) leaves it as drawn: the fitter carries each trace's amplitude and baseline."""

    world: Optional[Dict] = None

    def __new__(cls, values, world: Dict):
        obj = np.asarray(values, dtype=float).view(cls)
        obj.world = dict(world)
        return obj

    def __array_finalize__(self, obj):
        self.world = getattr(obj, "world", None)

    def __array_wrap__(self, arr, context=None, return_scalar=False):
        if return_scalar or np.ndim(arr) == 0:
            return np.asarray(arr)[()]
        return super().__array_wrap__(arr, context, return_scalar)

    def __array_ufunc__(self, ufunc, method, *inputs, out=None, **kwargs):
        worlds = [x.world for x in inputs if isinstance(x, WorldTrace) and x.world is not None]
        arrays = sum(1 for x in inputs if isinstance(x, np.ndarray) and x.size > 1)
        base = [x.view(np.ndarray) if isinstance(x, WorldTrace) else x for x in inputs]
        if out is not None:
            kwargs["out"] = tuple(o.view(np.ndarray) if isinstance(o, WorldTrace) else o for o in out)
        result = getattr(ufunc, method)(*base, **kwargs)
        if method != "__call__" or not worlds:
            return result
        world = dict(worlds[0])
        if arrays > 1:
            world["post_draw"] = True

        def wrap(r):
            if not isinstance(r, np.ndarray) or r.ndim == 0:
                return r
            w = r.view(WorldTrace)
            w.world = world
            return w
        return tuple(wrap(r) for r in result) if isinstance(result, tuple) else wrap(result)

    def __reduce__(self):
        fn, args, state = super().__reduce__()
        return fn, args, (state, self.world)

    def __setstate__(self, state):
        nd_state, world = state
        super().__setstate__(nd_state)
        self.world = world


class WorldFitterMismatch(ValueError):
    """The twin's fitter was handed a world it does not describe (F559, F560)."""


#: which fitter form describes which world form: the joint line is fitted by the joint table, and both the
#: convolution line and the layered separable line by the convolution composer (F555: leg 1 passes on its own form)
WORLD_FIT_FORM = {"joint": "joint", "convolution": "convolution", "separable": "convolution"}
#: a declared mismatch names what it measures, at the model registry's own minimum length for a reason
MIN_WORLD_REASON_WORDS = 6


def _world_same(a, b) -> bool:
    return (a is not None and b is not None
            and math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=1e-12))


def world_disagreements(world: Dict, *, model: str, T_C: float, s0: float, w0_m: float, m2: float,
                        z_ratio: float, transit_fwhm: float, fit_transit: bool,
                        transit_default: float, laser_kind: str = "gaussian", gamma_l: float = 0.0,
                        fit_gamma_l: bool = False) -> List[str]:
    """Every way a fitter's settings disagree with `world`, in words; empty when they agree. Pure, so its
    boundaries are planted without a fit. Across forms only the form is reported, since the other keys are read
    against the form's own. `transit_default` is the fitter's own default transit, so a transit passed to a joint
    fitter, which never reads it, is reported as the silent no-op it is (F560)."""
    if world.get("post_draw"):
        return ["post-draw: an array was added to or multiplied into the line after the generator drew it, a change "
                "the fitter does not model (F566)"]
    form = world.get("form")
    want = WORLD_FIT_FORM.get(form)
    if want is None:
        return [f"the world's form {form!r} is not one this door knows ({sorted(WORLD_FIT_FORM)})"]
    out: List[str] = []
    same_form = model == want
    if not same_form:
        out.append(f"form: the world is drawn on the {form} line and the fitter reads model={model!r}, whose match "
                   f"is model={want!r} (F559)")
    if world.get("T_C") is not None and not _world_same(world["T_C"], T_C):
        out.append(f"temperature: the world is drawn at {world['T_C']} C and fitted at {T_C} C (F560)")
    if not _world_same(world.get("s0", 0.0), s0):
        out.append(f"shift: the world's S0 is {world.get('s0')} MHz and the fitter's is {s0} MHz")
    # THE LASER KERNEL AND THE GAS WIDTH (F566): both joint branches honour them, and a
    # world that carries either differently from the fitter is a misspecification the harness must declare
    if world.get("laser_kind", "gaussian") != laser_kind:
        out.append(f"laser kernel: the world's is {world.get('laser_kind')!r} and the fitter's {laser_kind!r}")
    if not fit_gamma_l and not _world_same(world.get("gamma_l", 0.0), gamma_l):
        out.append(f"gas width: the world carries a Lorentzian of {world.get('gamma_l')} MHz and the fitter holds "
                   f"{gamma_l} MHz fixed")
    if same_form and form == "joint":
        for key, fitv in (("w0_m", w0_m), ("m2", m2), ("z_ratio", z_ratio)):
            if not _world_same(world.get(key), fitv):
                out.append(f"{key}: the world's is {world.get(key)} and the fitter's is {fitv}")
        if not _world_same(transit_fwhm, transit_default):
            out.append(f"transit: {transit_fwhm} MHz was passed to the joint fitter, which never reads it (the "
                       "table's transit is the ensemble's at the waist and temperature); pass none, or study a "
                       "transit with model='convolution' on both sides (F560)")
    elif same_form and not fit_transit and not _world_same(world.get("transit_fwhm"), transit_fwhm):
        out.append(f"transit: the world's transit width is {world.get('transit_fwhm')} MHz and the fitter holds "
                   f"{transit_fwhm} MHz")
    return out


def _kind(msg: str) -> str:
    return msg.split(":", 1)[0].strip()


def check_world_fit(volts, *, where: str, reason: Optional[Dict[str, str]], **fit) -> List[str]:
    """Raise `WorldFitterMismatch` unless every trace in `volts` carries a world the fitter's settings `fit`
    describe (`world_disagreements`). A declared `reason` of at least `MIN_WORLD_REASON_WORDS` words admits a
    disagreement, and the disagreements are returned, so a comparison arm (a world fitted by the other form, or a
    ramp left out of the fitter, on purpose) states at its call what it measures. A trace with no world is refused
    whatever the reason: a real trace goes to `linefit.fit_condition`, never through this door."""
    worlds = [getattr(v, "world", None) for v in volts]
    bare = sum(w is None for w in worlds)
    if bare:
        raise WorldFitterMismatch(
            f"{where}: {bare} of {len(worlds)} traces carry no world. A twin trace comes from `synthetic_traces` "
            "or `build_world_trace`, which tag it; an operation that drops the tag (`np.asarray`, `np.interp`, "
            "`np.concatenate`) is re-tagged with `WorldTrace(values, trace.world)`. A real trace goes to "
            "`linefit.fit_condition`, never here.")
    seen, msgs = set(), []
    for w in worlds:
        key = tuple(sorted(w.items()))
        if key not in seen:
            seen.add(key)
            msgs += world_disagreements(w, **fit)
    if not msgs:
        return []
    if reason is not None and not isinstance(reason, dict):
        raise WorldFitterMismatch(f"{where}: world_mismatch_reason is keyed by the disagreement it admits "
                                  f"(a dict of kind to reason, F566), not {type(reason).__name__}")
    reason = reason or {}
    unadmitted = [m for m in msgs if len(str(reason.get(_kind(m), "")).split()) < MIN_WORLD_REASON_WORDS]
    if not unadmitted:
        return msgs
    raise WorldFitterMismatch(
        f"{where}: the fitter does not describe the world these traces were drawn from:\n  - "
        + "\n  - ".join(unadmitted)
        + f"\nFit with the world's own settings, or declare world_mismatch_reason={{kind: reason}} naming each "
        f"kind ({', '.join(sorted({_kind(m) for m in unadmitted}))}) in at least {MIN_WORLD_REASON_WORDS} words "
        "saying what the mismatch measures.")


def _defaults(fn) -> Dict:
    return {k: p.default for k, p in inspect.signature(fn).parameters.items()
            if p.default is not inspect.Parameter.empty}


def fit_world(freqs, volts, *, world_mismatch_reason: Optional[Dict[str, str]] = None, **fit_kw) -> Dict:
    """`linefit.fit_condition` for TWIN traces, after `check_world_fit` against the fitter's own settings, its
    defaults read from its signature. Every keyword reaches the fitter unchanged."""
    if "T_C" not in fit_kw:
        raise TypeError("fit_world: T_C is required, as linefit.fit_condition requires it")
    d = _defaults(fit_condition)
    kw = {**d, **fit_kw}
    check_world_fit(volts, where="fit_world", reason=world_mismatch_reason, model=kw["model"], T_C=kw["T_C"],
                    s0=kw["s0"], w0_m=kw["w0_m"], m2=kw["m2"], z_ratio=kw["z_ratio"],
                    transit_fwhm=kw["transit_fwhm"], fit_transit=kw["fit_transit"],
                    transit_default=d["transit_fwhm"], laser_kind=kw["laser_kind"], gamma_l=kw["gamma_l"],
                    fit_gamma_l=kw["fit_gamma_l"])
    return fit_condition(freqs, volts, **fit_kw)


def fit_world_beta(conditions: List[Dict], *, world_mismatch_reason: Optional[Dict[str, str]] = None,
                   **beta_kw) -> Dict:
    """`beta.fit_beta_self` for TWIN conditions, after `check_world_fit` on every condition's traces at that
    condition's own temperature. The beta fit carries no shift channel (its own docstring), so it is checked at
    S0 = 0; under the convolution form each condition's transit is the one the fit itself derives
    (`linefit.transit_fwhm_at_T`)."""
    from .beta import fit_beta_self
    from .linefit import transit_fwhm_at_T
    d = _defaults(fit_beta_self)
    kw = {**d, **beta_kw}
    for cond in conditions:
        if kw["model"] == "joint":
            tr, tr_default = kw["transit_ref_mhz"], d["transit_ref_mhz"]
        else:
            tr = tr_default = transit_fwhm_at_T(cond["T_C"], kw["transit_ref_mhz"], kw["T_ref_C"])
        check_world_fit(cond["volts"], where=f"fit_world_beta at {cond['T_C']} C", reason=world_mismatch_reason,
                        model=kw["model"], T_C=cond["T_C"], s0=0.0, w0_m=kw["w0_m"], m2=kw["m2"],
                        z_ratio=kw["z_ratio"], transit_fwhm=tr, fit_transit=kw["fit_transit"],
                        transit_default=tr_default, laser_kind=kw["laser_kind"], gamma_l=kw["gamma_l"],
                        fit_gamma_l=kw["fit_gamma_l"])
    return fit_beta_self(conditions, **beta_kw)


def synthetic_traces(gamma_coll: float, sigma_laser: float, transit_fwhm: float,
                     *, span_mhz: float = 60.0, n_points: int = 2000,
                     n_traces: int = 5, noise: object = 0.004,
                     amp: float = 1.0, amp_spread: float = 0.05,
                     offset: float = 0.010, offset_spread: float = 0.002,
                     centre_mhz: float = 0.0,
                     laser_kind: str = "gaussian", gamma_l: float = 0.0,
                     tau_int: Optional[float] = None,
                     s0: float = 0.0, halo_fraction: float = 0.0,
                     rng: Optional[np.random.Generator] = None,
                     residual_source=None,
                     model: str = "joint", T_C: Optional[float] = None,
                     w0_m: float = W0_CENTRAL_M, m2: float = 1.0,
                     z_ratio: float = JOINT_Z_RATIO, n_path: int = JOINT_N_PATH,
                     seed: int = JOINT_SEED, registry: Optional[str] = None,
                     ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Generate the traces your instrument would record for this line.

    `model` (owner order O49, the C6b wide wave: "the model... is not anymore a
    convolution"). THE DEFAULT IS `"joint"`: the world's CLEAN LINE is drawn from
    `volume_line.joint_spectrum`'s atom-sampled two-time line, through `twin_volume.
    world_shape` (never `volume_line.JointTable` -- "the world must be the Monte
    Carlo, never the fitter's table", `twin_volume`'s own charter), at a beam built from
    `w0_m` (default `constants.W0_CENTRAL_M`) and `m2`, and this call's own `T_C`, which the joint model
    REQUIRES and never defaults (F560); the convolution arm keeps 110.0. `transit_fwhm`
    IS NOT READ under this model: the transit comes from the atom-sampled ensemble at
    (w0_m, T_C), the same emergent quantity `linefit.fit_condition(model="joint")` now
    reports instead of fitting, so a twin generated here and a fit made there share the
    SAME forward model exactly (`_one_trial` below threads `T_C`/`model`/`w0_m`/`m2` to
    both). `gamma_coll`/`sigma_laser`/`gamma_l`/`laser_kind`/`s0` carry across unchanged:
    `s0` is the same on-axis AC-Stark S0 either model reads, and `gamma_coll`/`gamma_l`
    bundle into the table's homogeneous Lorentzian exactly as `linefit._shared_profile_grid`
    does.

    THE NOISE LAYER IS THE SAME ONE EITHER MODEL USES (C6b noise wave, 2026-09-22:
    `_traces_from_shape` below). Noise is added AFTER the clean line exists and does not
    depend on the model form, so `tau_int`-correlated noise (explicit, or carried by a noise-
    law dict's own `tau_int`), `residual_source` (the moving-block resamples of
    `scripts/run_residual_resampling.py`) and `halo_fraction` all reach a `model="joint"`
    trace exactly as they reach a `model="convolution"` one, through the one shared helper,
    never a second copy of that logic. UNTIL THIS WAVE, `twin_volume.synthetic_traces`'s own
    simpler (i.i.d.-only) noise layer stood in for `model="joint"` instead, and `tau_int`,
    `residual_source` and a non-zero `halo_fraction` raised under `model="joint"` instead of
    being silently dropped. `twin_volume.world_shape` (the peak-normalised world line alone,
    with no noise layer of its own) is what this branch calls now, so the refusal no longer
    applies and every one of those three keywords is read under either model.

    `model="convolution"` is the pre-existing separable form below (`model_profile`/
    `composite_profile`), kept callable as the named comparison arm and byte-identical to
    every trace generated before this parameter existed.

    ``residual_source`` (PLAN v2 Phase 3, 2026-09-18): a callable ``(rng, n) -> array`` of n
    unit-variance samples that REPLACES the Gaussian draw, so a twin can carry the archive's own
    residual shape (the moving-block resamples of `scripts/run_residual_resampling.py`). The
    amplitude law (`noise` as a float or as the measured law) is applied to the samples either
    way; ``None`` is the Gaussian draw every committed cell was made with, byte-identical.

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
    moment is -S0^3/135 on the blue side (lineshape.RAMP_SIDE, docs/methods/03), and the statement of what a windowed readout keeps of it was
    replaced (the account is in the private correction record): the Lorentzian's even
    moments diverge, its odd moments cancel under a window symmetric about
    the line's own centre, so a SELF-CENTRED windowed mu_3 keeps a
    truncation-limited fraction of the ramp's value
    (results/cumulant_window_check.csv, survival rows) while a lab-frame
    window under drift takes on (2/pi)*gamma*delta*W of first-moment
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

    ``registry`` (O58): None for a run behind a result, which must carry exactly the registry's
    twin terms, or a STUDY's reason of six words or more (`twin_preflight`). The default s0 = 0
    world has no ramp and no chirp, so it is a study and says so; the convolution arm never carries
    the joint line's chirp or its collected window. Nothing is drawn before the door admits.

    Returns (freqs, volts), each a list of arrays, one per trace, in the form
    `fit_condition` accepts.
    """
    if model not in ("joint", "convolution"):
        raise ValueError(f"synthetic_traces: model must be 'joint' or 'convolution', "
                         f"got {model!r}")
    # THE WORLD'S TEMPERATURE IS THE CALLER'S, NEVER A DEFAULT (F560, 2026-09-26): under the
    # joint model the world is drawn at `T_C`, and four callers passed none while their fits read 120 or 130 C, so
    # every rung was drawn at the old 110 C default and the kernel worlds' beta_self read about 7 per cent low. The
    # convolution arm does not draw at `T_C` and keeps its old default, byte for byte.
    if T_C is None:
        if model == "joint":
            raise ValueError("synthetic_traces(model='joint') draws the world at T_C: pass the temperature the fit "
                             "reads (F560: a world drawn at a default while its fit read another condition)")
        T_C = 110.0
    _ex = {"natural_width", "transit"}
    if s0 > 0.0:
        _ex.add("ac_stark_ramp")
    if gamma_coll > 0.0:
        _ex.add("self_broadening_vdw")
    if sigma_laser > 0.0:
        _ex.add("laser_kernel")
    if halo_fraction > 0.0:
        _ex.add("radiation_trapping")
    if model == "joint":
        _ex.add("beam_quality_m2")
        if s0 > 0.0:
            _ex.add("transit_chirp")
        if z_ratio > 0.0:
            _ex.add("axial_collection_window")
    twin_preflight(_ex, registry, T_C=T_C)
    if model == "joint":
        # THE REFUSAL IS GONE (C6b noise wave, 2026-09-22): `twin_volume.world_shape` returns
        # only the peak-normalised clean line, with no noise layer of its own to be silently
        # short of `tau_int`/`residual_source`/`halo_fraction`, so every one of the three
        # reaches this trace exactly as it reaches a `model="convolution"` one, through the
        # SAME `_traces_from_shape` helper below.
        # gaussian-limit: the layered forecast generator is an approximation of the joint twin of record, and it owes the bore (registry bore-limited-recompute)
        beam = GaussianBeam(float(w0_m), float(m2))
        _lorentz_laser = laser_kind != "gaussian"
        homog = (GNAT_MHZ + max(gamma_coll, 0.0) + max(gamma_l, 0.0)
                + (max(sigma_laser, 0.0) if _lorentz_laser else 0.0))
        sigma_for_line = 0.0 if _lorentz_laser else max(sigma_laser, 0.0)
        if rng is None:
            # the SAME default derivation `twin_volume.synthetic_traces` used to make for this
            # call before this wave: never from entropy, so a trace set is reproducible from
            # its arguments alone.
            rng = np.random.default_rng(np.random.SeedSequence([int(seed), 1]))
        nu, shape = twin_volume.world_shape(
            beam=beam, T_C=T_C, S0_mhz=s0, gamma_hom_mhz=homog,
            sigma_laser_mhz=sigma_for_line, z_ratio=z_ratio, span_mhz=span_mhz,
            n_points=n_points, centre_mhz=centre_mhz, n_path=n_path, seed=seed)
        freqs, volts = _traces_from_shape(nu, shape, n_traces=n_traces, noise=noise, amp=amp,
                                          amp_spread=amp_spread, offset=offset,
                                          offset_spread=offset_spread, halo_fraction=halo_fraction,
                                          tau_int=tau_int, residual_source=residual_source, rng=rng)
        _world = {"form": "joint", "T_C": float(T_C), "s0": float(s0), "w0_m": float(w0_m), "m2": float(m2),
                  "z_ratio": float(z_ratio), "transit_fwhm": None, "laser_kind": laser_kind,
                  "gamma_l": float(gamma_l), "halo_fraction": float(halo_fraction)}
        return freqs, [WorldTrace(v, _world) for v in volts]
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
        # model_profile convolves lineshape.stark_ramp, so the 2/3 S0 pull and
        # the skew both come from the library rather than from a literal here,
        # and the ramp's coded SIDE (lineshape.RAMP_SIDE) is inherited rather than re-chosen.
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

    # The trapped-light halo raises the collected amplitude by a fixed fraction of the primary
    # rate. It does NOT reshape the line: the trapped photon is the D-line cascade photon, whose
    # frequency is unrelated to the 993 nm two-photon detuning, so the term is flat across the
    # scan (docs/methods/04 section 2.7). THE CORRELATION COMES FROM THE LAW THE CALLER ALREADY
    # PASSED: `noise` as a dict is the committed model, and its `tau_int` used to sit unused here
    # while its amplitude coefficients were read one line below. A caller who hands over the
    # measured law now gets the measured correlation without asking for it, which is the charter
    # sentence. An explicit `tau_int` overrides, and a float `noise` carries no law so it stays
    # white unless told otherwise. `_traces_from_shape` (C6b noise wave) is this SAME logic,
    # shared with `model="joint"` above instead of kept as a second copy here.
    freqs, volts = _traces_from_shape(nu, shape, n_traces=n_traces, noise=noise, amp=amp,
                                      amp_spread=amp_spread, offset=offset, offset_spread=offset_spread,
                                      halo_fraction=halo_fraction, tau_int=tau_int,
                                      residual_source=residual_source, rng=rng)
    _world = {"form": "convolution", "T_C": None, "s0": float(s0), "w0_m": None, "m2": None,
              "z_ratio": None, "transit_fwhm": float(transit_fwhm), "laser_kind": laser_kind,
              "gamma_l": float(gamma_l), "halo_fraction": float(halo_fraction)}
    return freqs, [WorldTrace(v, _world) for v in volts]


def build_world_trace(power_w: float, kappa: float, t_c: float,
                     order_idx: int, n_rungs: int,
                     rng: np.random.Generator, layers: Dict, *,
                     positions: Dict[str, float], shares: Dict[str, float],
                     gamma_coll: float, sigma_laser_fwhm: float,
                     transit_fwhm: float, power_max_w: float,
                     cycles_at_max: float, drift_mhz_total: float,
                     noise_frac_bright: float, adc_levels: int,
                     range_headroom: float = 1.25,
                     halo_fraction: float = 0.0,
                     gamma_l: float = 0.0,
                     laser_kind: str = "gaussian",
                     resolve_shift: bool = False,
                     tooth_of: Optional[Dict[str, str]] = None,
                     offset: float = 0.01,
                     range_anchor: str = "global",
                     grid_span: Optional[Tuple[float, float]] = None,
                     z_ratio: Optional[float] = None,
                     fringe_density: Optional[Tuple[np.ndarray, np.ndarray]] = None,
                     t_bbr_k: Optional[float] = None,
                     pedestal_height_frac: float = 0.0,
                     retro_tilt_rad: float = 0.0,
                     m2: float = 1.0,
                     tau_int: float = 1.0,
                     baseline_tilt_sigma: float = 0.0,
                     noise_floor_v: float = 0.0,
                     w0_m: Optional[float] = None,
                     omega_mhz: Optional[float] = None,
                     registry: Optional[str] = None,
                     model: str = "separable",
                     ) -> Tuple[np.ndarray, np.ndarray, Dict]:
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

    Five keywords are opt-in and off by default, so a call written before
    them is byte-identical. ``gamma_l`` and ``laser_kind`` give the laser
    kernel a Lorentzian component or form. ``halo_fraction`` adds the
    trapped-light re-excitation as a flat amplitude factor. ``resolve_shift``
    makes the internal convolution grid resolve the light shift as well as
    the kernels: left off, a shift well below the kernel widths sits inside
    one grid cell, which overstates the third moment by 68 per cent at
    0.18 MHz and misreads it by a few per cent at the archive's shift of about 0.35, while at 1.0 MHz
    and above the two settings agree to every printed digit. Set it for any
    small-shift moment study. ``tooth_of`` maps a position key to the physical
    peak it is a tooth of, for an EOM comb; None is the identity.

    ``registry`` (O58): this is the LAYERED generator, a registered approximation of the joint
    twin that never carries the joint line's chirp, so every call is a STUDY and names its reason,
    six words or more (`twin_preflight`); None is refused before anything is drawn.

    ``model`` (F559, V7.2's W2): "separable" draws each peak through `fullmodel.full_profile`, the
    convolution of a closed-form transit with the ramp and the Voigt, and stays the default so every
    committed table made through this path is unchanged until its consumer moves. "joint" draws each
    peak's clean line from `twin_volume.world_shape`, the atom-sampled Monte Carlo line
    `synthetic_traces(model="joint")` draws, at the beam (`w0_m`, `m2`), `t_c`, the shift, the
    homogeneous width and the laser width, with the collection window of `z_ratio` (the fitter's
    `JOINT_Z_RATIO` when None), which is the line `fit_condition`'s default describes. The layers
    that act on amplitudes, centres, the range and the noise act on it as on the separable line; the
    terms the joint world does not carry (the pedestal, the retro tilt, a Rabi-frequency companion,
    a fringe tail) are REFUSED under it, never dropped. Leg 1 failed on the two forms side by side (F559).

    Returns (nu, volts, truth_amps): the frequency axis (MHz, transition
    axis), the one recorded trace, and each peak's injected amplitude.
    """
    _ex = {"natural_width", "transit"}
    # the caller's own window, before the separable path folds M2 into it: the joint branch carries M2 in the
    # beam itself, so it reads this one and M2 is never counted twice
    _z_ratio_arg = z_ratio
    if sigma_laser_fwhm > 0.0:
        _ex.add("laser_kernel")
    if gamma_coll > 0.0:
        _ex.add("self_broadening_vdw")
    if layers["stark"] and kappa * power_w > 0.0:
        _ex.add("ac_stark_ramp")
    if layers["saturation"]:
        _ex.add("saturation")
    if layers["cascade"]:
        _ex |= {"depletion_cascade", "hyperfine_pumping"}
    if layers["bbr"]:
        _ex.add("blackbody")
    if halo_fraction > 0.0:
        _ex.add("radiation_trapping")
    if (z_ratio is not None and float(z_ratio) > 0.0) or float(m2) != 1.0:
        _ex |= {"axial_collection_window", "beam_quality_m2"}
    if fringe_density is not None:
        _ex.add("fringe_tail")
    if pedestal_height_frac > 0.0:
        _ex.add("doppler_pedestal")
    if retro_tilt_rad > 0.0:
        _ex.add("retro_tilt")
    if model not in ("separable", "joint"):
        raise ValueError(f"build_world_trace: model must be 'separable' or 'joint', got {model!r}")
    if model == "joint":
        _unc = [n for n, on in (("pedestal_height_frac", pedestal_height_frac > 0.0),
                                ("retro_tilt_rad", retro_tilt_rad > 0.0),
                                ("omega_mhz", omega_mhz is not None),
                                ("fringe_density", fringe_density is not None)) if on]
        if _unc:
            raise ValueError(f"build_world_trace(model='joint') does not carry {', '.join(_unc)}: the joint "
                             "world line has no such term, and dropping it silently is the defect F559 names")
        _ex |= {"beam_quality_m2", "axial_collection_window"}
        if layers["stark"] and kappa * power_w > 0.0:
            _ex.add("transit_chirp")
    twin_preflight(_ex, registry, T_C=t_c, power_w=power_w)
    if grid_span is None:
        nu = np.linspace(min(positions.values()) - 60.0, 60.0, 6000)
    else:
        # OPT-IN: the default grid runs from 60 MHz below the lowest line to
        # +60 and is asymmetric under a comb, so a wing that a baseline is read
        # from can sit on a tooth. A caller with a comb names a span that clears
        # every tooth, and the step is the default's at a SINGLE line on zero,
        # 120/5999 MHz. The default's own step is (120 - min(positions))/5999,
        # so under a comb the default is coarser than this one rather than equal
        # to it, which an earlier comment here got wrong.
        lo, hi = float(grid_span[0]), float(grid_span[1])
        nu = np.linspace(lo, hi, int(round((hi - lo) / (120.0 / 5999))) + 1)
    s0 = kappa * power_w
    # THE TWO AXIAL TERMS (2026-09-08), both off by default so every committed
    # CSV made through this path is unchanged: the collection window's
    # divergence (`z_ratio`, from constants.collection_z_ratio at the cell's
    # waist) and the standing wave's fringe-resolved tail (`fringe_density`,
    # from fringe_tail.fringe_shift_density once per cell, since it is
    # S0-independent). Either alone or both together are one mixture,
    # lineshape.ramp_mixture; the pure transverse ramp is model_profile's own
    # default, so the default path is byte-identical (tests/test_ramp_threading).
    # BEAM QUALITY ENTERS THROUGH THE COLLECTION RATIO AND NOWHERE ELSE, so it
    # is folded into z_ratio here. Without this the builder passes its own
    # `profile` closure to full_profile, whose own m2 branch then stands down,
    # and m2 is accepted and ignored -- a no-op switch found by checking both
    # halves rather than by reading the code (2026-09-12).
    if float(m2) != 1.0:
        if w0_m is None:
            raise ValueError("m2 != 1 needs w0_m: beam quality reaches the line "
                             "only through the collection ratio, which needs a waist")
        from . import constants as _K
        z_ratio = float(m2) * (_K.collection_z_ratio(w0_m=float(w0_m))
                               if z_ratio is None else z_ratio)
    if z_ratio is None and fringe_density is None:
        profile = stark_ramp
    else:
        if fringe_density is None:
            _xg = np.linspace(0.0, 1.0, 4001)      # BLUE support (O27)
            _gx = local_ramp_density(_xg)
        else:
            _xg, _gx = fringe_density
        _zr = 0.0 if z_ratio is None else float(z_ratio)

        _memo: Dict = {}

        def profile(nu_, s0_, _xg=_xg, _gx=_gx, _zr=_zr, _memo=_memo):
            # one evaluation per (shift, grid): the peaks of a trace share
            # the shift and the convolution grid, so the mixture is paid once
            key = (float(s0_), nu_.shape[0], float(nu_[0]), float(nu_[1] - nu_[0]))
            if key not in _memo:
                _memo[key] = ramp_mixture(nu_, s0_, _zr, _xg, _gx)
            return _memo[key]
    p_rel = (power_w / power_max_w)

    v = np.zeros_like(nu)
    truth_amps = {}
    for peak, share in shares.items():
        amp = share * p_rel ** 2                      # two-photon: signal ~ P^2
        amp *= (1.0 + halo_fraction)                  # trapped-light halo, flat in nu
        # an EOM comb's teeth are the SAME physical line excited through
        # different photon pairs, so a tooth keyed "4192@+12.5" looks up its
        # cascade and saturation under "4192"; identity when no map is given
        phys = (tooth_of or {}).get(peak, peak)
        # A TOOTH IS DRIVEN AT ITS OWN RATE, AND BROADENED AT ITS OWN RABI
        # FREQUENCY (2026-09-06, A83 and A86). A phase modulation redistributes
        # a line's two-photon excitation among its teeth while leaving the
        # intensity, and so the light shift, untouched. The two-photon
        # AMPLITUDE into the tooth at order k is J_k(2 beta), so the tooth's
        # rate is J_k(2 beta)^2 of the line's and its Rabi frequency is
        # J_k(2 beta) of it: the rate scale below is that fraction, because
        # the weights sum to one, and the Rabi scale is its square root. The
        # scale needs no Bessel call and no lookup outside the caller's own
        # shares. Applied only under a tooth_of map: without one both scales
        # are exactly one and every existing output is byte-identical.
        rate = 1.0
        if tooth_of is not None:
            own = sum(s for q, s in shares.items()
                      if (tooth_of or {}).get(q, q) == phys)
            if own > 0.0:
                rate = share / own
        if layers["cascade"]:
            # depletion counts cycles, so a dim tooth accumulates fewer of
            # them; before this it was depleted as if driven at the whole
            # line's rate, which made depletion look depth-independent.
            amp *= cascade.amplitude_factor(phys, cycles_at_max * p_rel * rate)
        gamma = gamma_coll
        if layers["saturation"]:
            # the companion width is power broadening, which follows the
            # tooth's RABI frequency and not the intensity: the model keys it
            # on s0 as the proxy for that Rabi frequency, so a tooth's proxy
            # is s0 times J_k(2 beta), the square root of its rate share. The
            # light shift itself does not carry this factor, since it is set
            # by the whole spectrum. Before this every tooth was broadened as
            # if it carried the line's whole drive, which is the one term that
            # would have made a depth ladder read a false constant width.
            gamma = gamma + stark.companion_gamma_mhz(s0 * float(np.sqrt(rate)), phys)
        centre = positions[peak]
        if layers["bbr"]:
            # THE RADIATION TEMPERATURE IS THE WALLS', NOT THE ATOMS'. They
            # coincide in a heated cell and they do not in a MOT or a cold
            # hollow-core fibre, where atoms at microkelvin sit inside a
            # chamber at room temperature; passing the kinetic temperature
            # there computes the blackbody shift of a sample at absolute zero.
            # Default None keeps the cell's behaviour byte-identical.
            t_rad_k = 273.15 + t_c if t_bbr_k is None else float(t_bbr_k)
            centre += -blackbody.shift_hz(t_rad_k) / 1e6
        if layers["drift"]:
            centre += drift_mhz_total * (order_idx / max(n_rungs - 1, 1) - 0.5)
        # THE RAMP IS CONVOLVED, NOT APPLIED AS A SHIFT (corrected
        # 2026-08-30): a rigid translation carries only the first moment and
        # leaves the trace symmetric, while the self-centred windowed third
        # moment (docs/wiki/third-cumulant.md) is the channel this record
        # is built on. model_profile convolves lineshape.stark_ramp, so the
        # pull and the skew both come from the library, and the ramp's coded
        # SIDE is inherited rather than re-chosen (it is an open question:
        # tests/test_ramp_side_matches_the_polarizability).
        # THE TWO CAMPAIGN TERMS (2026-09-12), both off by default so every
        # committed CSV through this path is unchanged: the co-propagating
        # Doppler pedestal, and the residual Doppler width an imperfectly
        # retro-reflected beam leaves. The second broadens WITHOUT shifting,
        # which no other term here does, so it is the one a Sobol scan should
        # rank against the waist.
        # THE FULL-MODEL PATH, taken only when a term outside model_profile is
        # asked for, so the default stays byte-identical. `omega_mhz` is the one
        # that changes a PARAMETERISATION rather than adding a term: the
        # saturation below is tied to the fitted shift, and passing Omega
        # frees it from that, which is what lets it survive the zero this
        # archive drives the shift to.
        # THE TWIN IS ALWAYS ON THE FULL MODEL (owner, 2026-09-18: "make sure that
        # the twin is using the full and correct model (so, with also the gases)").
        # Until today this read `full_profile if _fm else model_profile`, taking the
        # full path only when a pedestal, tilt, m2 or Omega was asked for, and
        # otherwise staying on model_profile "for byte-identical committed output".
        # THAT BYTE-IDENTITY IS REAL AND IT IS WHY THE FALLBACK BOUGHT NOTHING:
        # measured 2026-09-18, full_profile at its defaults equals model_profile to
        # 0.0 of peak on this record's own axes. So the fallback never protected a
        # number; it only kept a SECOND PATH that could diverge from the first
        # without any caller noticing, which is the defect this record calls a
        # switch that is thrown and does nothing. One path now.
        #
        # AND REMOVING IT IS NOT, BY ITSELF, THE FULL MODEL. A term is live only
        # when its PARAMETER is non-default: the pedestal, the tilt, m2, Omega and
        # `gamma_l` (the permeated-gas family's Lorentzian, which is the same
        # parameter as the laser's Lorentzian arm because Lorentzians add) all
        # reach the line through this call and all default to off. What makes the
        # twin full is a CALLER that sets them, and `results/twin_term_census.csv`
        # regenerated from this source is the instrument that says which are set.
        _prof = full_profile
        _extra = dict(pedestal_height_frac=pedestal_height_frac,
                      retro_tilt_rad=retro_tilt_rad, T_C=t_c,
                      peak=peak, m2=m2, w0_m=w0_m)
        if omega_mhz is not None:
            # REFUSE THE DOUBLE COUNT (2026-09-12). The
            # `saturation` layer already adds `companion_gamma_mhz` above,
            # and `full_profile` would add `saturation_companion_mhz` here:
            # with both the built line ran 5.4809 MHz against 5.4209 for
            # either alone. They are two spellings of one term, so asking
            # for both is a caller error and not a configuration.
            if layers.get("saturation"):
                raise ValueError(
                    "omega_mhz and layers['saturation'] both add the "
                    "saturation companion, which double counts it. Pass "
                    "omega_mhz with the layer OFF to parameterise the "
                    "companion by the Rabi frequency, or leave omega_mhz "
                    "None and let the layer key it on the light shift.")
            _extra["omega_mhz"] = float(omega_mhz) * float(np.sqrt(rate))
        if model == "joint":
            _lor = laser_kind != "gaussian"
            _hom = (GNAT_MHZ + max(gamma, 0.0) + max(gamma_l, 0.0)
                    + (max(sigma_laser_fwhm, 0.0) if _lor else 0.0))
            _span = float(np.max(np.abs(nu - centre))) + 1.0
            _gx, _gs = twin_volume.world_shape(
                # gaussian-limit: the joint world line owes the bore until V7.3 draws it in the fitter's clipped beam (F564)
                beam=GaussianBeam(float(W0_CENTRAL_M if w0_m is None else w0_m), float(m2)), T_C=float(t_c),
                S0_mhz=(s0 if layers["stark"] else 0.0), gamma_hom_mhz=_hom,
                sigma_laser_mhz=(0.0 if _lor else max(sigma_laser_fwhm, 0.0)),
                z_ratio=(JOINT_Z_RATIO if _z_ratio_arg is None else float(_z_ratio_arg)), span_mhz=_span,
                n_points=int(round(2.0 * _span / 0.02)) + 1, centre_mhz=0.0, n_path=JOINT_N_PATH, seed=JOINT_SEED)
            shape = np.interp(nu - centre, _gx, _gs, left=0.0, right=0.0)
            v += amp * (shape / shape.max())
            truth_amps[peak] = amp
            continue
        shape = _prof(nu - centre,
                              gamma_coll=gamma,
                              sigma_laser_fwhm=sigma_laser_fwhm,
                              transit_fwhm=transit_fwhm,
                              gamma_l=gamma_l,
                              laser_kind=laser_kind,
                              profile=profile,
                              # A33: the internal convolution grid is sized by
                              # the narrowest KERNEL and never by the shift, so
                              # a small shift can sit inside one cell. Opt-in
                              # and False by default, so every committed CSV
                              # made through this path is unchanged. The cost
                              # of leaving it False is measured rather than
                              # asserted: results/moment_power_map.csv carries
                              # the windowed third-moment power both ways.
                              resolve_shift=resolve_shift,
                              s0=(s0 if layers["stark"] else 0.0), **_extra)
        v += amp * (shape / shape.max())
        truth_amps[peak] = amp
    v += offset                                        # detector offset
    # shot-like noise: sigma grows as the root of the LOCAL signal, anchored
    # so the brightest rung's peak carries noise_frac_bright of itself; the
    # noise falls with the signal while the quantisation step does not,
    # which is what makes one vertical range survivable at the dim rung.
    # `range_anchor` says which vertical range the noise and the ADC step
    # anchor to. "global" is the proposed campaign's design: ONE range,
    # snug on the full-power brightest peak, held across the whole ladder.
    # "per_rung" is what the 2025 bench actually did: it re-ranged as the
    # power fell (the display-epoch moves docs/RESULTS.md C3e records), so
    # each rung's noise and step follow its own brightest signal. The twin
    # validation's closed loop needs the second to reproduce the record's
    # own error scale; the default stays "global" and every earlier caller
    # is unchanged.
    if range_anchor == "per_rung":
        bright_peak = max(shares.values()) * p_rel ** 2 + offset
    elif range_anchor == "global":
        bright_peak = max(shares.values()) + offset
    else:
        raise ValueError(f"unknown range_anchor {range_anchor!r}")
    # THE SIGNAL-INDEPENDENT FLOOR, which this builder did not carry and the
    # committed law does. `noise.sigma_of_v` floors every weight at the law's
    # `a`, its own docstring calling it "the fitted dark floor... the noise at
    # any signal level cannot be below the zero-signal noise", and at the
    # p_sweep role that is 3.64 mV. The shot-like term below goes to ZERO where
    # the signal does, so in the wings the twin had essentially no noise at all
    # while the real traces sit on the floor: measured scale-free at matched
    # peak amplitude, the archive's wing noise is 3.17 times the twin's.
    #
    # It is added in quadrature because the two are independent, and defaults
    # to zero so every trace this builder made before 2026-09-12 is unchanged.
    # A caller with the committed law passes `law["a"]`.
    sigma = np.hypot(
        noise_frac_bright * np.sqrt(np.clip(v, 0.0, None) * bright_peak),
        float(noise_floor_v))
    # `tau_int` defaults to 1.0, which is white and byte-identical to every
    # trace this builder made before 2026-09-12. See `_correlate` for what the
    # default costs and why the committed law's own two numbers disagree.
    v = v + sigma * _correlate(rng.standard_normal(nu.size), tau_int)
    # THE PER-TRACE BASELINE TILT, which the real traces carry and this builder
    # did not. `run_twin_completeness.py` compares wing statistics on real and
    # simulated traces and finds the correlation time 1.88 with the mean
    # removed against 0.96 once a straight line is taken out: a broadband
    # correlation survives both removals and a slow tilt does not, so what the
    # real wings hold is a tilt. Measured over forty canonical traces it is
    # 0.49 +- 0.04 of the residual sigma across a 400-sample wing, and its mean
    # is 5.7 sigma from zero, so it is systematic and not scatter.
    #
    # `drift` is a DIFFERENT term and does not cover this: it moves the common
    # centre across the rung order and leaves each baseline flat.
    #
    # The rise is stated across the FULL grid in units of the noise sigma at
    # the brightest peak, and the default of zero leaves every trace this
    # builder has ever made byte-identical.
    if baseline_tilt_sigma:
        _ramp = np.linspace(-0.5, 0.5, nu.size)
        v = v + baseline_tilt_sigma * noise_frac_bright * bright_peak * _ramp
    if layers["quantise"]:
        step = range_headroom * bright_peak / adc_levels
        v = np.round(v / step) * step
    _s0w = float(s0 if layers["stark"] else 0.0)
    if model == "joint":
        _world = {"form": "joint", "T_C": float(t_c), "s0": _s0w,
                  "w0_m": float(W0_CENTRAL_M if w0_m is None else w0_m), "m2": float(m2),
                  "z_ratio": float(JOINT_Z_RATIO if _z_ratio_arg is None else _z_ratio_arg), "transit_fwhm": None,
                  "laser_kind": laser_kind, "gamma_l": float(gamma_l), "halo_fraction": float(halo_fraction)}
    else:
        _world = {"form": "separable", "T_C": float(t_c), "s0": _s0w,
                  "w0_m": None if w0_m is None else float(w0_m), "m2": float(m2),
                  "z_ratio": None if z_ratio is None else float(z_ratio), "transit_fwhm": float(transit_fwhm),
                  "laser_kind": laser_kind, "gamma_l": float(gamma_l), "halo_fraction": float(halo_fraction)}
    return nu, WorldTrace(v, _world), truth_amps


def _one_trial(truth: Dict, design: Dict, rng: np.random.Generator) -> Dict:
    # s0 is a property of the WORLD, so it lives in `truth` beside the widths,
    # not in `design` beside the acquisition settings. Absent, it is zero and
    # both generator and fitter behave exactly as they did before 2026-08-30.
    s0 = float(truth.get("s0", 0.0))
    # `model` (owner order O49): read once here so the SAME choice reaches both the
    # generator and the fitter, and `T_C` likewise -- before this fix `synthetic_traces`
    # took no T_C at all, so under model="joint" (the new default on both sides) the
    # world was drawn at `synthetic_traces`'s own default T_C while the fit read
    # `design.get("T_C", 130.0)`, a silent mismatch this threading removes.
    model = design.get("model", "joint")
    T_C = design.get("T_C", 130.0)
    w0_m = design.get("w0_m", W0_CENTRAL_M)
    m2 = design.get("m2", 1.0)
    freqs, volts = synthetic_traces(
        truth["gamma_coll"], truth["sigma_laser"], truth["transit_fwhm"],
        span_mhz=design.get("span_mhz", 60.0),
        n_points=design.get("n_points", 2000),
        n_traces=design.get("n_traces", 5),
        noise=design.get("noise", 0.004),
        amp=design.get("amp", 1.0),
        s0=s0, model=model, T_C=T_C, w0_m=w0_m, m2=m2,
        rng=rng, registry=design.get("registry"))
    # The fitter is MATCHED to the injected ramp by default. `design["fit_s0"]`
    # deliberately mismatches it, which is how the twin measures what omitting
    # the ramp costs the widths rather than assuming it costs nothing: at the
    # 2025 S0 the answer is about 0.1 sigma on gamma_coll, and at a tight focus
    # it is not. A twin that generates and fits with the same s0 can never see
    # that, the way this one could not see it while s0 did not exist.
    fit_kw = dict(T_C=T_C, s0=float(design.get("fit_s0", s0)), law=design.get("law"), model=model,
                  w0_m=w0_m, m2=m2)
    if model == "convolution":
        fit_kw["transit_fwhm"] = truth["transit_fwhm"]
    return fit_world(freqs, volts, world_mismatch_reason=(
        {"shift": "design['fit_s0'] sets the fitter's ramp apart from the world's on purpose, measuring what "
                   "omitting or mis-sizing the ramp costs the widths"} if "fit_s0" in design else None), **fit_kw)


def forecast_precision(truth: Dict, design: Dict, *, n_trials: int = 8,
                       seed: int = 0, scalings: bool = True,
                       return_trials: bool = False, registry: Optional[str] = None) -> Dict:
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

    ``registry`` (O58) is the twin's declaration, threaded to every trial's `synthetic_traces`:
    None for a result run, or a study's reason of six words or more (`twin_preflight`). A design
    dict may carry it too, as ``design["registry"]``, and the keyword is used when both are given.
    """
    if registry is not None:
        design = {**design, "registry": registry}
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
            [t.get("gamma_coll_err", float("nan")) for t in trials],
            # and the fit's own width correlation per trial, so a caller can put the trials'
            # scale beside a move of the median (V7.1, F552)
            "corr_laser_coll_trials":
            [t.get("corr_laser_coll", float("nan")) for t in trials]}
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

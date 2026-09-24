"""
Joint lineshape fit per condition (module M3, fit layer)
========================================================

Takes a condition's back-to-back repeats (already loaded as time/volt), maps
time -> transition frequency with that block's M2 rate, and jointly fits the
composite model of rb5s6s.lineshape:

  SHARED across the repeats (the physics of the condition):
    gamma_coll       collisional Lorentzian FWHM  (the beta_self target)
    sigma_laser      laser-kernel FWHM (already x2 for two photons)
    [transit_fwhm]   optional; usually FIXED per T by sqrt(T) scaling
  PER TRACE (nuisance):
    A_i              amplitude
    center_i         line center (floats freely — 2025 drift lives here)
    b0_i, b1_i       linear background

Weights come from the M1 noise law (sigma(V)); reported parameter errors are
inflated by sqrt(tau_int) for wing-noise correlation and sqrt(chi2_red) when
the fit is imperfect (conservative, matching M2).

WHY joint-with-shared-shape: the 5 repeats see the SAME physical line at
(nearly) the same conditions; only the drift-shifted center and PMT gain
differ. Sharing the shape is what turns 5 noisy traces into one precise width
while letting each center float — the design that makes the drifted 2025 data
usable at all.

THE HARD PART (documented, closure-tested): sigma_laser (a Gaussian core) and
gamma_nat+gamma_coll (a Lorentzian) form a Voigt whose two widths are
partially degenerate — the "fit-level face of the confound". fit_condition
returns the full covariance so the sigma_laser<->gamma_coll correlation is
visible, and test_linefit quantifies the recoverable precision at campaign
SNR before any real number is trusted.

CONSEQUENCES OF THE DEGENERACY (closure-measured at SNR~130, 5 repeats):
corr(sigma_laser, gamma_coll) ~ -0.9. So:
  * the TOTAL Voigt width (their combination) is robust and the individual
    split is not, so never quote a single-condition sigma_laser or gamma_coll
    as physics without its error and this correlation.
  * beta_self must ride on the gamma_coll DIFFERENCE across temperature
    (density lever arm), where the shared/systematic laser contribution
    largely cancels, NOT on absolute per-condition gamma_coll.
  * these synthetics generate AND fit with the SAME model, so they bound the
    fitter's numerics and the statistical degeneracy ONLY — not model
    mismatch (is the laser kernel really Gaussian? the transit really a
    two-sided exponential?). Model-form sensitivity is a separate study
    (laser_kind toggle + the cold-dim cusp BIC test) and its spread is a
    systematic on top of these statistical errors.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

import numpy as np
from scipy.optimize import least_squares
from scipy.signal import fftconvolve

from . import config as C
from .constants import GAMMA_NAT_HZ, W0_CENTRAL_M, transit_fwhm_from_w0
from ._compat import trapezoid
from .lineshape import lorentzian, gaussian, two_sided_exponential, stark_ramp
from .noise import signal_level, sigma_of_v
from .fitutil import cov_from_jac, feasible_p0
from .volume_line import GaussianBeam, JointTable, HOMOG_MARGIN_MHZ, HOMOG_STEP_MHZ

GNAT_MHZ = GAMMA_NAT_HZ / 1e6

# =====================================================================================
# THE NON-CONVOLVING (JOINT) MODEL, owner order O49 (re-sent 15:1x, replacing
# C6B_DESIGN.md's "linefit is out of scope"): "the model (either for the twin and in
# general) is not anymore a convolution". `fit_condition`'s inhomogeneous part -- the
# transit kernel and the AC-Stark shift, formerly two independent convolution factors
# (`_shared_profile_grid`'s old body, kept below as the `model="convolution"` arm) --
# becomes ONE joint table per condition (`volume_line.JointTable`, F294), built at the
# record's own waist (`constants.W0_CENTRAL_M`) and the condition's own temperature, with
# the homogeneous Lorentzian (natural + collisional [+ the permeated-gas family]) and the
# laser's Gaussian convolved ONCE at evaluation time -- exact, per F294/F317, and not the
# approximation being removed. S0 is the table's own axis, so a caller that fits or scans
# S0 shares the same cached table across every trial value. Here S0 is fixed per call, as
# it always was, and the table is built ONCE before the optimiser runs, not once per
# `_shared_profile_grid` evaluation, since neither S0 nor the waist ever moves within
# one `fit_condition` call. THE TRANSIT WIDTH STOPS BEING A FREE PARAMETER under this
# model: it is the table's own, an emergent property of the atom-sampled ensemble at
# (w0_m, T_C), so `fit_transit=True` is refused instead of silently ignored.
# =====================================================================================

#: Atom count for the per-condition table's Monte Carlo, and its bracketing seed. Measured
#: in the C6b wide wave (`private/cache/plan_2026-09-18/c6b_wide_2026-09-22/REPORT.md`): a
#: 2x2 (S0, w0) grid costs about 2.8 s to build at this n_path on this machine (four atom-MC
#: nodes, though the tight bracket below means only one is ever queried -- see
#: `condition_joint_table`). It costs 5.4 s at 8000 and 1.4 s at 2000. One table evaluation
#: afterward (the Lorentzian/Gaussian convolution `JointTable.profile` does at every
#: optimiser iteration) costs under 3 ms regardless. The table is cached per (T_C, s0, w0,
#: m2, z_ratio, n_path, seed), so this cost is paid once per condition, not once per fit
#: iteration nor once per Monte-Carlo trial at a fixed design point.
JOINT_N_PATH = 4000
JOINT_SEED = 0
#: The C6b wave's own default collection ratio (`private/cache/plan_2026-09-18/
#: C6B_CONVOLUTION_MAP.md`'s F293/F294 pre-wave node, 0.605). `volume_line`'s and
#: `twin_volume`'s own tests use the same rounded value.
JOINT_Z_RATIO = 0.6
#: The S0 and w0 grid brackets are as tight as floating point allows while staying
#: strictly ascending (`JointTable.__init__` requires it): the condition's own (s0, w0) is
#: always queried exactly at the grid's lower node, so bilinear interpolation returns that
#: node's own computed value with NO interpolation error. The bracket exists only because
#: `JointTable` is a general (S0, w0) interpolant and always needs two points per axis
#: (its own `__init__` guard). A zero S0 needs a strictly positive second node too.
_JOINT_S0_BRACKET_FRAC = 0.01
_JOINT_S0_BRACKET_FLOOR_MHZ = 0.01
_JOINT_W0_BRACKET_FRAC = 1e-6

#: Cache of built per-condition tables, keyed on every input that changes the table's own
#: content. Cleared wholesale past `_JOINT_TABLE_CACHE_MAX` entries, mirroring
#: `twin_volume._WORLD_CACHE`'s own convention instead of evicting by age, since a fit run
#: touches at most a few dozen distinct conditions.
_JOINT_TABLE_CACHE: Dict[tuple, "JointTable"] = {}
_JOINT_TABLE_CACHE_MAX = 64


def condition_joint_table(T_C: float, s0_mhz: float, *, w0_m: float = W0_CENTRAL_M,
                          m2: float = 1.0, z_ratio: float = JOINT_Z_RATIO,
                          n_path: int = JOINT_N_PATH, seed: int = JOINT_SEED,
                          beam_factory: Optional[Callable[[float], object]] = None,
                          ) -> "JointTable":
    """The condition's own `volume_line.JointTable`, built once and cached.

    A 2x2 (S0, w0) grid bracketing the condition's own (s0_mhz, w0_m) as tightly as
    floating point allows (see the module-level bracket constants above), so every
    `.profile(...)` query below lands exactly on the grid's lower node. This function
    exists to give `fit_condition`/`fit_global`/`fit_beta_self`/`sharing_bic`/
    `lever_crosscheck_beta` ONE shared, cached table-build path instead of five, not to
    interpolate across a scan. A caller that DOES scan or fit S0 or w0 still benefits,
    since each distinct value gets its own cached table keyed by this function's own
    arguments.

    Costs four atom-Monte-Carlo evaluations (the 2x2 grid), of which only one is ever
    read. See `JOINT_N_PATH`'s docstring for the measured cost. `delta_mhz` spans the
    widest window `fit_condition` ever fits against (`config.FIT_HALFWIDTH_MAX_MHZ`) plus
    `volume_line.HOMOG_MARGIN_MHZ`'s own margin for the homogeneous convolution's reach, at
    `volume_line.HOMOG_STEP_MHZ`'s own step -- the SAME margin and step the rest of this
    wave's homogeneous-convolution code uses (`volume_line.joint_spectrum`), reused here
    instead of re-derived.

    `beam_factory` (C6b noise wave, 2026-09-22, the lever cross-check's replacement axis):
    ``None`` (the default) keeps the exact existing beam, `lambda w0v: GaussianBeam(w0v, m2)`,
    and the exact existing cache key -- byte-identical to every call made before this
    parameter existed. A caller wanting a DIFFERENT beam (e.g. `beam_field.ClippedBeam`, for
    the model-form axis `lever_crosscheck.lever_crosscheck_beta` reads under `model="joint"`)
    passes its own factory. The cache then keys on its `id()` instead of trying to hash an
    arbitrary callable, so a fresh factory object is always a cache miss (correct, since its
    OUTPUT cannot be inferred from (w0, m2) alone) while the default path's caching is
    unaffected.
    """
    key = (round(float(T_C), 6), round(float(s0_mhz), 9), round(float(w0_m), 12),
          round(float(m2), 6), round(float(z_ratio), 6), int(n_path), int(seed),
          id(beam_factory) if beam_factory is not None else None)
    table = _JOINT_TABLE_CACHE.get(key)
    if table is not None:
        return table
    s0 = max(float(s0_mhz), 0.0)
    s0_hi = s0 + max(s0 * _JOINT_S0_BRACKET_FRAC, _JOINT_S0_BRACKET_FLOOR_MHZ)
    w0 = float(w0_m)
    w0_hi = w0 * (1.0 + _JOINT_W0_BRACKET_FRAC)
    half_mhz = HOMOG_MARGIN_MHZ + C.FIT_HALFWIDTH_MAX_MHZ
    delta_mhz = np.arange(-half_mhz, half_mhz + HOMOG_STEP_MHZ, HOMOG_STEP_MHZ)
    m2 = float(m2)
    # gaussian-limit: the fitter's joint table defaults to the ideal beam and owes the bore, the registry's bore-limited-recompute, until a caller passes the clipped factory
    _factory = beam_factory if beam_factory is not None else (lambda w0v: GaussianBeam(float(w0v), m2))
    table = JointTable.build(
        S0_grid=np.array([s0, s0_hi]), w0_grid=np.array([w0, w0_hi]), delta_mhz=delta_mhz,
        m2=m2, T_C=float(T_C), n_path=int(n_path), seed=int(seed), z_ratio=float(z_ratio),
        beam_factory=_factory)
    if len(_JOINT_TABLE_CACHE) >= _JOINT_TABLE_CACHE_MAX:
        _JOINT_TABLE_CACHE.clear()
    _JOINT_TABLE_CACHE[key] = table
    return table


def joint_condition_profile(gamma_coll: float, sigma_laser: float, laser_kind: str, *,
                            gamma_l: float = 0.0, s0: float = 0.0, T_C: float,
                            w0_m: float = W0_CENTRAL_M, m2: float = 1.0,
                            z_ratio: float = JOINT_Z_RATIO, n_path: int = JOINT_N_PATH,
                            seed: int = JOINT_SEED,
                            beam_factory: Optional[Callable[[float], object]] = None):
    """The non-convolving analogue of `lineshape.composite_profile`/the transit-and-shift
    block of `_shared_profile_grid`: the condition's own `JointTable`
    (`condition_joint_table`, cached), evaluated at this trial's homogeneous width and
    laser width. Returns `(g, prof)`, matching `_shared_profile_grid`'s own convention
    (`g` the frequency grid, `prof` the area-normalised profile on it), so every caller
    that consumes that pair (`np.interp(freqs - centre, g, prof, ...)`) needs no change of
    its own beyond selecting `model="joint"`.

    The homogeneous-width split mirrors `_shared_profile_grid` exactly: `homog` bundles the
    natural width, `gamma_coll` and `gamma_l`, and `sigma_laser` too, added in FWHM as an
    exact Lorentzian, when `laser_kind != "gaussian"`. The DEFAULT `laser_kind="gaussian"`
    keeps `sigma_laser` as the table's own separate Gaussian convolution instead.

    `beam_factory`: threaded straight to `condition_joint_table` (its own docstring). ``None``
    is byte-identical to every call made before this parameter existed.
    """
    if T_C is None:
        raise ValueError("joint_condition_profile needs T_C: the atom-sampled table is "
                         "built at a temperature, never inferred or left implicit")
    _lorentz_laser = laser_kind != "gaussian"
    homog = (GNAT_MHZ + max(gamma_coll, 0.0) + max(gamma_l, 0.0)
            + (max(sigma_laser, 0.0) if _lorentz_laser else 0.0))
    sigma_for_table = 0.0 if _lorentz_laser else max(sigma_laser, 0.0)
    table = condition_joint_table(T_C, s0, w0_m=w0_m, m2=m2, z_ratio=z_ratio, n_path=n_path,
                                  seed=seed, beam_factory=beam_factory)
    g = table.delta_mhz
    prof = table.profile(g, s0_mhz=s0, w0_m=w0_m, gamma_hom_mhz=homog,
                         sigma_laser_mhz=sigma_for_table)
    return g, prof


def to_frequency(t_ms: np.ndarray, rate_transition_mhz_per_ms: float) -> np.ndarray:
    """Map the raw time axis to TRANSITION frequency (MHz). The origin is
    arbitrary (per-trace center absorbs it), so we reference to t=0."""
    return t_ms * rate_transition_mhz_per_ms


def _shared_profile_grid(gamma_coll, sigma_laser, transit_fwhm, s0, laser_kind,
                         gamma_l: float = 0.0,
                         dnu_floor: float = 1e-3,
                         profile: Callable[[np.ndarray, np.ndarray], np.ndarray] = stark_ramp,
                         transit_kind: str = "exp",
                         model: str = "convolution", T_C: Optional[float] = None,
                         w0_m: float = W0_CENTRAL_M, m2: float = 1.0,
                         z_ratio: float = JOINT_Z_RATIO, n_path: int = JOINT_N_PATH,
                         seed: int = JOINT_SEED):
    """Build the area-normalized shared line shape ONCE on a fine grid; the
    per-trace fit interpolates it at (nu - center). Returns (grid, profile).

    `model` selects the composer (owner order O49, the C6b wide wave). THE FUNCTION'S OWN
    DEFAULT STAYS `"convolution"`, the pre-existing separable form below, UNCHANGED and
    byte-identical to every call made before this parameter existed -- this helper is
    called positionally, with the pre-existing five-argument signature, from over a dozen
    scripts and tests outside `fit_condition` (`scripts/run_stark_joint.py`,
    `run_kernel_k4.py`, `run_width_pinning.py`, `make_figures.py`, `tests/
    test_transit_kind.py`, `test_laser_kind_degeneracy.py`, among others), none of which
    pass `model=`, and every one of them tests or uses the convolution machinery
    specifically (a transit-kernel form, a far-wing level, a saturation-probe patch) --
    so changing this function's OWN default would silently swap what they exercise.
    `fit_condition` is the only caller in this module that passes `model="joint"`
    explicitly, which is where the wave's new default actually lives.

    `model="joint"` routes the transit-and-shift block through `joint_condition_profile`
    (the condition's own `volume_line.JointTable`, `T_C` and `w0_m` at the record's own
    waist by default) instead of convolving `transit_kind`'s analytic kernel with
    `profile`'s shift density. `T_C` is then required, since the table is built at a
    temperature, and `profile`/`transit_kind` must stay at their defaults, since the
    joint line samples atoms directly and has no seam for either. Passing a non-default
    value raises instead of silently ignoring it.

    dnu_floor is the coarsest the internal grid step may get when a width
    parameter collapses. The 1e-3 MHz default reproduces every committed
    result bit-for-bit. M23's optimizer probes near-zero sigma_laser, where
    a 1e-3 step means ~1e5-point grids and the direct convolutions here go
    quadratic (minutes per profile); it passes 2e-2, which changes the
    profile by < 3e-6 of peak against lines that are never narrower than
    4 MHz (test_stark_joint has the equivalence test). The convolutions are
    FFT-based since 2026-08-01 -- identical to within float noise at any
    floor, and what makes the M23 corner cheap.

    transit_kind selects the transit kernel's MODEL FORM, mirroring
    lineshape.composite_profile: 'exp' is the Biraben-Cagnac two-sided
    exponential (the cusp, the default, byte-identical to the behaviour
    before this parameter existed, which test_transit_kind pins); 'gaussian'
    is a Gaussian of the same FWHM, making the whole line a pure Voigt.
    Threaded here 2026-08-15 so the global fits can run the same model-form
    check the beta_self path already could. Measured that day on beta_self:
    the Gaussian branch is rejected by the joint density-ladder test for this
    dataset and configuration (delta chi2 +365 to +1851 at equal k and n), so
    the 18-23 per cent beta shift it produces is a SENSITIVITY result, not a
    model-form uncertainty (rule 19.25 and the transit-modelform finding).
    """
    if model == "joint":
        if profile is not stark_ramp:
            raise ValueError(
                "_shared_profile_grid: model='joint' has no seam for a custom shift-density "
                "profile (the joint line samples atoms directly instead of convolving a "
                "density). Pass model='convolution' to use an adapted geometry.")
        if transit_kind != "exp":
            raise ValueError(
                "_shared_profile_grid: model='joint' has no transit_kind knob (the transit "
                "comes from the atom-sampled table, never an analytic kernel). Pass "
                "model='convolution' to select a transit kernel form.")
        return joint_condition_profile(gamma_coll, sigma_laser, laser_kind, gamma_l=gamma_l,
                                       s0=s0, T_C=T_C, w0_m=w0_m, m2=m2, z_ratio=z_ratio,
                                       n_path=n_path, seed=seed)
    if model != "convolution":
        raise ValueError(f"_shared_profile_grid: model must be 'joint' or 'convolution', "
                         f"got {model!r}")
    # A Lorentzian laser kernel is ADDED, not convolved: two Lorentzians
    # convolve to their summed width exactly, and doing it on a finite grid
    # instead made the profile depend on how the total was SPLIT, at up to
    # 3.7e-3 of peak, purely through tail truncation. See the long note in
    # lineshape.composite_profile and results/kernel_identifiability.csv.
    # gamma_l, the mixed G+L kernel's Lorentzian component, ADDED for the
    # exactness reason in lineshape.composite_profile's note. Default 0.0 is
    # bit-identical to the pre-change module.
    _lorentz_laser = laser_kind != "gaussian"
    homog = (GNAT_MHZ + max(gamma_coll, 0.0) + max(gamma_l, 0.0)
             + (max(sigma_laser, 0.0) if _lorentz_laser else 0.0))
    widths = ([homog] + ([] if _lorentz_laser else [max(sigma_laser, 1e-6)])
              + [max(transit_fwhm, 1e-6)] + ([s0] if s0 > 0 else []))
    span = 6.0 * (sum(widths) + max(widths)) + 5.0
    dnu = max(min(widths) / 12.0, dnu_floor)
    n = int(np.ceil(span / dnu))
    g = np.arange(-n, n + 1) * dnu
    prof = lorentzian(g, homog)
    if not _lorentz_laser:
        prof = fftconvolve(prof, gaussian(g, sigma_laser), "same") * dnu
    tk = (two_sided_exponential(g, transit_fwhm) if transit_kind == "exp"
          else gaussian(g, transit_fwhm))
    prof = fftconvolve(prof, tk, "same") * dnu
    if s0 > 0:
        prof = fftconvolve(prof, profile(g, s0), "same") * dnu
    area = trapezoid(prof, g)
    return g, (prof / area if area > 0 else prof)


def adaptive_halfwidth(freqs: np.ndarray, volts: np.ndarray) -> float:
    """Fit half-width (MHz) for one trace: FIT_HALFWIDTH_FWHM_MULT times the
    trace's own model-independent FWHM, clipped to [MIN, MAX]. Scales with the
    line so the same fraction of Lorentzian wing is kept whether narrow or
    collisionally broadened, while the MAX cap always excludes the ~40 MHz
    off-center-sweep mirror. `freqs` is the transition-frequency axis (MHz);
    contiguous_fwhm_ms is axis-agnostic (returns the x-span in freqs' units)."""
    from .qc import contiguous_fwhm_ms
    fwhm = contiguous_fwhm_ms(freqs, volts)  # MHz here (freqs axis)
    hw = C.FIT_HALFWIDTH_FWHM_MULT * fwhm
    return float(min(max(hw, C.FIT_HALFWIDTH_MIN_MHZ), C.FIT_HALFWIDTH_MAX_MHZ))


def transit_fwhm_at_T(T_C: float, transit_ref_mhz: float, T_ref_C: float = 110.0,
                      isotope: int | None = None) -> float:
    """Transit FWHM at temperature T from a reference value, enforcing the
    sqrt(T) thermal scaling (T in kelvin).

    ISOTOPE (added 2026-08-10, owner instruction, OPT-IN). The transit width
    goes as the thermal speed, which goes as 1/sqrt(mass), so the two isotopes
    do not share it: 85Rb is 1.169 per cent faster than 87Rb at the same
    temperature and its transit kernel is wider by the same fraction, 11 kHz at
    130 C. Passing isotope=85 or 87 applies that, referenced to the
    abundance-weighted mean so a shared reference value keeps its meaning.

    THE DEFAULT IS None, WHICH REPRODUCES THE SHARED BEHAVIOUR BYTE FOR BYTE,
    and that is deliberate. Every committed fit shares one transit width across
    both isotopes, and the misassignment that causes is almost entirely a
    constant OFFSET rather than a density slope: the gap runs 10.53 to
    11.42 kHz across the 52-fold density lever, so a straight line through it
    has a slope of 0.000026 MHz per 1e12 cm^-3, which is 0.4 per cent of one
    sigma on the measured beta85 minus beta87. The offset is absorbed by the
    per-peak core width, which is free in every construction here. So the
    isotope split does NOT move the collisional coefficients and switching it
    on silently would produce a diff with no physics in it.

    Where it does matter, and why the argument exists: the quoted transit width
    itself, which is stated to 0.01 MHz; the transit TIME, 1.17 per cent
    shorter for 85Rb, which sets the hyperfine-pumping depletion of
    scripts/run_zeeman_depletion.py; and the Doppler pedestal a wide scan would
    measure, where 1.17 per cent of 942 MHz is 11 MHz and is resolvable, which
    makes the mass difference a handle rather than a nuisance.
    """
    # transit_ref_mhz is a WIDTH IN MHZ, not a waist. The distinction needs
    # a guard because the wrong call is the natural one and it did not raise:
    # `transit_fwhm_at_T(130.0, W0_CENTRAL_M)` accepted a waist in metres
    # and returned 0.0001 MHz, four orders of magnitude low, silently. Found
    # by the clean-install-from-GitHub gate on 2026-08-13, where it was the
    # first thing a reader of the public surface tried.
    #
    # The band separates the two quantities rather than pinning the physics:
    # every transit width in the committed record lies between 0.0026 and
    # 5.65 MHz, while a waist in metres is of order 1e-5. Anything outside
    # [1e-3, 1e3) MHz is a unit error, not an unusual apparatus.
    if not (1e-3 <= float(transit_ref_mhz) < 1e3):
        raise ValueError(
            f"transit_ref_mhz={transit_ref_mhz!r} is not a transit width in "
            f"MHz. Values of order 1e-5 are a beam waist in metres passed "
            f"where a width was wanted: use transit_fwhm_from_w0(w0, T_C) "
            f"for that. The committed record spans 0.0026 to 5.65 MHz.")
    scaled = transit_ref_mhz * np.sqrt((T_C + 273.15) / (T_ref_C + 273.15))
    if isotope is None:
        return scaled
    from .constants import (ABUNDANCE_RB85, ABUNDANCE_RB87, M_RB85_KG,
                            M_RB87_KG)
    ratio = np.sqrt(M_RB87_KG / M_RB85_KG)          # v(85) / v(87)
    mean = ABUNDANCE_RB85 * ratio + ABUNDANCE_RB87  # keeps the shared value's meaning
    return scaled * (ratio if int(isotope) == 85 else 1.0) / mean


def _profile_fwhm(g: np.ndarray, prof: np.ndarray) -> float:
    """Full width at half maximum of a profile sampled on a grid."""
    above = np.flatnonzero(prof >= 0.5 * prof.max())
    return float(g[above[-1]] - g[above[0]]) if above.size else 0.0


def fit_condition(freqs: List[np.ndarray], volts: List[np.ndarray], *,
                  T_C: float, law: Optional[Dict] = None, s0: float = 0.0,
                  transit_fwhm: float = C.TRANSIT_FWHM_PLACEHOLDER_MHZ, fit_transit: bool = False,
                  laser_kind: str = "gaussian", trim_tails: bool = False,
                  gamma_l: float = 0.0, fit_gamma_l: bool = False,
                  halfwidth_mult: float = 1.0, fix_sigma_laser: float = None, fix_gamma_coll: float = None,
                  profile: Callable[[np.ndarray, float], np.ndarray] = stark_ramp,
                  model: str = "joint", w0_m: float = W0_CENTRAL_M, m2: float = 1.0,
                  z_ratio: float = JOINT_Z_RATIO, joint_n_path: int = JOINT_N_PATH,
                  joint_seed: int = JOINT_SEED) -> Dict:
    """Joint fit of one condition's repeats. `freqs` already in transition MHz.

    Shared free params: gamma_coll, sigma_laser (+ transit_fwhm if fit_transit and
    model="convolution"). Per-trace free params: A_i, center_i, b0_i, b1_i.

    `model` (owner order O49, the C6b wide wave: "the model... is not anymore a
    convolution") selects the composer `_shared_profile_grid` builds every shared line
    from. THE DEFAULT IS `"joint"`: the inhomogeneous part (transit and AC-Stark shift,
    formerly two independent convolution factors) becomes the condition's own
    `volume_line.JointTable` (`joint_condition_profile`, cached per (T_C, s0, w0_m, m2,
    z_ratio) by `condition_joint_table`), built at the record's own waist (`w0_m`,
    default `constants.W0_CENTRAL_M`) and this condition's own `T_C`, with S0 as the
    table's own axis (fixed at this call's `s0`, since `fit_condition` never frees S0
    itself) and the homogeneous Lorentzian plus the laser's Gaussian convolved ONCE at
    evaluation time -- exact (F294/F317), and not the approximation being removed.
    `model="convolution"` is the pre-existing separable form, kept callable as the named
    comparison arm and byte-identical to every fit made before this parameter existed.

    TWO CONSEQUENCES OF `model="joint"`, each refused instead of silently ignored:
    * THE TRANSIT WIDTH STOPS BEING A FREE PARAMETER: it is the table's own, an emergent
      property of the atom-sampled ensemble at (w0_m, T_C), so `fit_transit=True` raises.
      The returned `"transit_fwhm"` is then `constants.transit_fwhm_from_w0(w0_m, T_C)`,
      the closed-form ensemble value at that waist and temperature (the same function
      `config.TRANSIT_FWHM_PLACEHOLDER_MHZ` itself is built from), not a fitted number.
    * `profile` MUST stay at its `stark_ramp` default: the joint line samples atoms
      directly and has no seam for an adapted shift-density geometry (`model="convolution"`
      is where `profile` reaches the fit, exactly as before).

    TWO CONVENTIONS A CALLER MUST KNOW, stated here because this is where they
    are used rather than only where they are defined:
      * `sigma_laser` IS A FWHM, not a standard deviation, despite the name.
        The module docstring says so and the name does not, which is exactly
        the trap protocol rule 19.18 exists for.
      * `transit_fwhm` is the width of a TWO-SIDED EXPONENTIAL kernel by
        default, the Biraben-Cagnac cusp, not a Gaussian. `transit_kind` on
        `_shared_profile_grid` selects the form, and the Gaussian branch makes
        the composite a pure Voigt. The two differ by 18 to 23 per cent on
        beta_self for this dataset, so the choice is not cosmetic.
    Returns dict with shared values+errors, per-trace params, chi2_red, cov of
    the shared block, and the sigma_laser<->gamma_coll correlation.

    `profile` is the light-geometry seam, with the same contract as
    lineshape.model_profile's: profile(grid, s0) -> the area-normalized shift
    density convolved in when s0 > 0. The stark_ramp default is the
    focused-beam triangle every committed fit used; an adapted geometry
    passes a closure over lineshape.stark_from_intensity_profile.

    `trim_tails` runs the residual-tail trimmer (rb5s6s.trim) as a SINGLE
    second pass: fit once, cut any sustained positive residual tail outside a
    core of one fitted full width either side of each fitted centre, refit
    once, stop. It does not touch the adaptive fit window, which is a separate
    and earlier decision, and it cannot reach the line because of the core
    guard. The per-trace record comes back as `trim_records`. Default off, so a
    plain call reproduces the fit as it stood before the trimmer existed.

    `halfwidth_mult` SCALES the adaptive fit window, and exists so the window
    can be treated as a robustness axis rather than a fixed choice. It
    multiplies each trace's own adaptive half-width, so a scan keeps the same
    fraction of every line's wing whether that line is narrow or collisionally
    broadened. 1.0 is the committed window and is bit-identical to the call
    before this parameter existed.

    THE CAP IS NOT NEGOTIABLE AND IS THE REASON THIS IS A MULTIPLIER RATHER
    THAN A FREE WIDTH. The off-centre-sweep mirror re-crosses the line about
    40 MHz away, so FIT_HALFWIDTH_MAX_MHZ is re-applied after scaling: a scan
    that widened past it would be fitting the mirror, and would report the
    resulting bias as a window trend. Widening therefore SATURATES rather than
    continuing, which a reader of the output has to know.
    """
    if model not in ("joint", "convolution"):
        raise ValueError(f"fit_condition: model must be 'joint' or 'convolution', got {model!r}")
    if model == "joint":
        if fit_transit:
            raise ValueError(
                "fit_condition: fit_transit=True is incompatible with model='joint': the "
                "transit width is derived from (w0_m, T_C) through the atom-sampled table, "
                "never fit. Pass model='convolution' to fit a free transit width.")
        if profile is not stark_ramp:
            raise ValueError(
                "fit_condition: model='joint' has no seam for a custom shift-density profile "
                "(the joint line samples atoms directly). Pass model='convolution' for an "
                "adapted geometry.")
    ntr = len(freqs)
    # per-trace seeds from simple moments
    centers0, amps0, b0s = [], [], []
    sigmas = []
    for nu, v in zip(freqs, volts):
        lev, base = signal_level(v)
        ipk = int(np.argmax(lev))
        centers0.append(float(nu[ipk])); amps0.append(float(lev.max())); b0s.append(float(base))
        if law is not None:
            sigmas.append(sigma_of_v(np.maximum(lev, 0.0), law))
        else:
            sigmas.append(np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)))
    tau = max(law.get("tau_eff", law.get("tau_int", 1.0)), 1.0) if law is not None else 1.0   # F36: the residuals' own time when the loader carries it

    # Window each trace about its seed center, EXCLUDING any off-center-sweep
    # mirror crossing (~40 MHz away) that the full-window single-line fit would
    # otherwise treat as unmodelled signal and let bias the baseline/width.
    # (flagged 2026-07-11.) The half-width is ADAPTIVE -- a multiple of the
    # trace's own measured FWHM, clipped to [MIN, MAX] -- not the fixed
    # FIT_HALFWIDTH_MHZ this comment used to name, which no longer exists:
    # see adaptive_halfwidth() and config.FIT_HALFWIDTH_FWHM_MULT.
    wf, wv, ws = [], [], []
    for i in range(ntr):
        hw = min(adaptive_halfwidth(freqs[i], volts[i]) * halfwidth_mult,
                 C.FIT_HALFWIDTH_MAX_MHZ)
        m = np.abs(freqs[i] - centers0[i]) <= hw
        wf.append(freqs[i][m]); wv.append(volts[i][m]); ws.append(sigmas[i][m])
    freqs, volts, sigmas = wf, wv, ws

    # CORRELATED-NOISE WEIGHTING: each sample's sigma
    # is inflated by sqrt(tau_int) INSIDE the fit, so the optimizer sees each
    # trace's true information content (tau correlated samples ~ one
    # independent one). Diagnostics (chi2, per-trace residuals) use the
    # UNSCALED sigma, for which E[chi2_red]=1 for a perfect model regardless
    # of correlation. Previously tau multiplied the final covariance as one
    # scalar -- wrong exposure for shared vs nuisance parameters.
    sigmas_raw = sigmas
    sigmas = [s * np.sqrt(tau) for s in sigmas_raw]

    # parameter vector:
    #   [gamma_coll, sigma_laser, (transit?), (gamma_l?)] + per-trace [A, c, b0, b1]
    # gamma_l is APPENDED AFTER transit, never inserted. Callers and tests read
    # sol.x[0] and sol.x[1] and the covariance's [0,1] element by position, so
    # inserting a shared parameter ahead of them would silently re-point every
    # one of those reads at a different quantity. Appending cannot.
    nshared = 2 + (1 if fit_transit else 0) + (1 if fit_gamma_l else 0)
    p0 = ([0.5, 1.0] + ([transit_fwhm] if fit_transit else [])
          + ([max(gamma_l, 0.05)] if fit_gamma_l else []))
    for i in range(ntr):
        p0 += [amps0[i], centers0[i], b0s[i], 0.0]
    p0 = np.array(p0)
    lo = ([0.0, 0.0] + ([0.05] if fit_transit else [])
          + ([0.0] if fit_gamma_l else []) + [(-np.inf)] * (4 * ntr))
    hi = ([50.0, 50.0] + ([10.0] if fit_transit else [])
          + ([50.0] if fit_gamma_l else []) + [np.inf] * (4 * ntr))
    lo = np.array(lo, float); hi = np.array(hi, float)
    if fix_sigma_laser is not None:
        # THE PER-TRACE MODE (F36, the per-parameter calibration): one trace cannot carry
        # the laser width and the collisional width apart, so a single-trace fit pins the width at
        # the condition's pooled value and reads the rest; the bounds are pinched to the value, the
        # seed sits on it, and the returned sigma_laser_err is the pinch and not a measurement.
        _v = float(fix_sigma_laser); lo[1] = _v - 1e-9; hi[1] = _v + 1e-9; p0[1] = _v
    if fix_gamma_coll is not None:
        # the complementary pass: the collisional width pinned, the laser width read per trace
        _v = float(fix_gamma_coll); lo[0] = _v - 1e-9; hi[0] = _v + 1e-9; p0[0] = _v
    # keep amplitudes non-negative, widths in-range
    for i in range(ntr):
        lo[nshared + 4 * i] = 0.0  # A_i >= 0

    _i_gl = 2 + (1 if fit_transit else 0)   # gamma_l's slot when it is free

    def unpack(p):
        gc, sl = p[0], p[1]
        tr = p[2] if fit_transit else transit_fwhm
        gl = p[_i_gl] if fit_gamma_l else gamma_l
        return gc, sl, tr, gl

    def residuals(p):
        gc, sl, tr, gl = unpack(p)
        g, prof = _shared_profile_grid(gc, sl, transit_fwhm_at_T(T_C, tr) if fit_transit else tr,
                                       s0, laser_kind, gl, profile=profile, model=model, T_C=T_C,
                                       w0_m=w0_m, m2=m2, z_ratio=z_ratio, n_path=joint_n_path,
                                       seed=joint_seed)
        out = []
        for i in range(ntr):
            A, c, b0, b1 = p[nshared + 4 * i: nshared + 4 * i + 4]
            pred = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            out.append((volts[i] - pred) / sigmas[i])
        return np.concatenate(out)

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=40000)
    if not sol.success:
        raise RuntimeError(f"condition fit failed: {sol.message}")

    # --- second pass: cut sustained residual tails, once ---
    trim_records = [{"trimmed": False, "trim_start_ms": float("nan"),
                     "trim_end_ms": float("nan"), "trim_reason": "",
                     "n_trimmed": 0} for _ in range(ntr)]
    if trim_tails:
        from .trim import tail_trim
        gc0, sl0, tr0, gl0 = unpack(sol.x)
        g, prof = _shared_profile_grid(
            gc0, sl0, transit_fwhm_at_T(T_C, tr0) if fit_transit else tr0,
            s0, laser_kind, gl0, profile=profile, model=model, T_C=T_C, w0_m=w0_m, m2=m2,
            z_ratio=z_ratio, n_path=joint_n_path, seed=joint_seed)
        guard = C.TRIM_CORE_GUARD_FWHM_MULT * _profile_fwhm(g, prof)
        any_trim = False
        for i in range(ntr):
            A, c, b0, b1 = sol.x[nshared + 4 * i: nshared + 4 * i + 4]
            pred = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
            inside = np.flatnonzero(np.abs(freqs[i] - c) <= guard)
            if inside.size == 0:
                continue
            rec = tail_trim(freqs[i], volts[i] - pred,
                            int(inside[0]), int(inside[-1]))
            trim_records[i] = {k: rec[k] for k in
                               ("trimmed", "trim_start_ms", "trim_end_ms",
                                "trim_reason", "n_trimmed")}
            if rec["trimmed"]:
                any_trim = True
                keep = rec["mask"]
                freqs[i], volts[i] = freqs[i][keep], volts[i][keep]
                sigmas[i], sigmas_raw[i] = sigmas[i][keep], sigmas_raw[i][keep]
        if any_trim:
            # Seeded from the ORIGINAL start, not from the contaminated
            # optimum. The trim changed the data, so the refit is a fresh
            # answer to a different question, and seeding it at a parameter
            # sitting on its own bound is how a fit that railed on the
            # contamination stays railed after the contamination is gone.
            sol = least_squares(residuals, p0, bounds=(lo, hi), max_nfev=40000)
            if not sol.success:
                raise RuntimeError(f"condition refit after trim failed: {sol.message}")

    ndata = sum(len(v) for v in volts)
    dof = max(ndata - len(p0), 1)
    # raw chi2 (unscaled sigma) is the goodness-of-fit diagnostic; with the
    # uniform per-condition tau it is exactly tau x the fitted chi2.
    chi2_red = float(2.0 * sol.cost / dof) * tau
    # Covariance: the tau weighting already lives in the whitened Jacobian.
    # The max(chi2_red, 1) rescale is a DOCUMENTED ONE-SIDED (conservative)
    # choice: model imperfection inflates errors, but chi2_red < 1 (noise
    # model overestimates sigma, or overfitting) does NOT shrink them -- the
    # noise model then sets the error floor. That state is flagged below.
    if fix_sigma_laser is not None or fix_gamma_coll is not None:
        # THE CONDITIONAL COVARIANCE (F42, 10:55): a width pinned by pinched bounds still has its
        # column in the Jacobian, so the full inverse is the MARGINAL covariance carrying the
        # sigma_laser-gamma_coll anticorrelation (-0.96) while the repeats' scatter is conditional
        # on the pinned width; the pinned column leaves the inverse and its own bar reads zero
        _drop = 1 if fix_sigma_laser is not None else 0
        _J = np.delete(sol.jac, _drop, axis=1)
        _c = cov_from_jac(_J) * max(chi2_red, 1.0)
        cov = np.zeros((sol.jac.shape[1], sol.jac.shape[1])); _keep = [k for k in range(sol.jac.shape[1]) if k != _drop]
        cov[np.ix_(_keep, _keep)] = _c
        _cov_marginal = cov_from_jac(sol.jac) * max(chi2_red, 1.0)   # the full inverse, kept for the Schur check (F44)
    else:
        cov = cov_from_jac(sol.jac) * max(chi2_red, 1.0)
        _cov_marginal = cov

    # Per-trace residual diagnostics (audit request, 2026-07-11): a good
    # joint fit must be good for EVERY trace, not on average. For each trace
    # we report its own chi2_red, the lag-1 autocorrelation of standardized
    # residuals (structure/misfit shows as positive lag-1), and their skew
    # (asymmetric misfit, e.g. an unmodelled shoulder).
    diag = []
    for i in range(ntr):
        # gl0, the FITTED gamma_l, not the fixed input. The diagnostics below
        # (chi2, lag1, skew) are residuals against the model, so building that
        # model from the input value while the fit had freed the parameter
        # would compute every diagnostic against a line the fit did not choose.
        gc0, sl0, tr0, gl0 = unpack(sol.x)
        g, prof = _shared_profile_grid(gc0, sl0,
                                       transit_fwhm_at_T(T_C, tr0) if fit_transit else tr0,
                                       s0, laser_kind, gl0, profile=profile, model=model, T_C=T_C,
                                       w0_m=w0_m, m2=m2, z_ratio=z_ratio, n_path=joint_n_path,
                                       seed=joint_seed)
        A, c, b0, b1 = sol.x[nshared + 4 * i: nshared + 4 * i + 4]
        pred = A * np.interp(freqs[i] - c, g, prof, left=0.0, right=0.0) + b0 + b1 * freqs[i]
        r = (volts[i] - pred) / sigmas_raw[i]   # diagnostics on UNSCALED sigma
        r0 = r - r.mean()
        lag1 = float(np.dot(r0[:-1], r0[1:]) / max(np.dot(r0, r0), 1e-12))
        diag.append({"chi2_red": float(np.mean(r ** 2)),
                     "lag1": lag1,
                     "skew": float(np.mean(r0 ** 3) / max(np.std(r0) ** 3, 1e-12))})

    gc, sl, tr, gl = unpack(sol.x)
    err = np.sqrt(np.clip(np.diag(cov), 0, None))
    corr_gs = float(cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])) if cov[0, 0] > 0 and cov[1, 1] > 0 else np.nan
    # the final shared profile and its full width, for the core check's mask (F42)
    _gc_f, _sl_f, _tr_f, _gl_f = unpack(sol.x)
    _g_final, _prof_final = _shared_profile_grid(_gc_f, _sl_f, transit_fwhm_at_T(T_C, _tr_f) if fit_transit else _tr_f,
                                                 s0, laser_kind, _gl_f, profile=profile, model=model,
                                                 T_C=T_C, w0_m=w0_m, m2=m2, z_ratio=z_ratio,
                                                 n_path=joint_n_path, seed=joint_seed)
    _half = 0.5 * float(np.max(_prof_final)); _idx = np.where(_prof_final >= _half)[0]
    _fwhm_final = float(_g_final[_idx[-1]] - _g_final[_idx[0]]) if _idx.size else float("nan")
    # THE REPORTED transit_fwhm (owner order O49): under model="joint" it is never a fitted
    # number (fit_transit=True is refused above), but the table's OWN emergent transit width,
    # the closed-form ensemble value at this call's (w0_m, T_C) -- constants.transit_fwhm_from_w0,
    # the SAME function config.TRANSIT_FWHM_PLACEHOLDER_MHZ is built from. Under
    # model="convolution" this is exactly the pre-existing expression, unchanged.
    _transit_fwhm_reported = (transit_fwhm_from_w0(w0_m, T_C) if model == "joint"
                              else float(transit_fwhm_at_T(T_C, tr) if fit_transit else tr))
    return {
        "gamma_coll": float(gc), "gamma_coll_err": float(err[0]),
        "sigma_laser": float(sl), "sigma_laser_err": float(err[1]),
        "transit_fwhm": float(_transit_fwhm_reported),
        "transit_fitted": bool(fit_transit),
        "model": model,
        # Gamma_L,equiv. Named for what it is: a Lorentzian-EQUIVALENT width.
        # It is not f_L and it is not "the laser linewidth"; attribution to the
        # laser is licensed by the K5 triangle, never by this fit.
        "gamma_l": float(gl), "gamma_l_fitted": bool(fit_gamma_l),
        "gamma_l_err": float(err[_i_gl]) if fit_gamma_l else float("nan"),
        "gamma_l_at_bound": bool(fit_gamma_l and gl <= 1e-9),
        "chi2_red": chi2_red, "n_traces": ntr,
        "noise_floor_limited": bool(chi2_red < 0.8),  # errors set by the noise model, not the fit
        # bound_active flags (2026-07-16): scipy's covariance ignores active
        # bounds, so a parameter pinned at its 0 rail wears a symmetric
        # Gaussian error where the true interval is one-sided. The flag
        # travels with the number so a reader can see which errors carry
        # that caveat.
        "gamma_coll_at_bound": bool(gc <= 1e-9),
        "sigma_laser_at_bound": bool(sl <= 1e-9),
        "corr_laser_coll": corr_gs,
        "centers": [float(sol.x[nshared + 4 * i + 1]) for i in range(ntr)],
        # the per-trace bars from the same covariance (F42: their pulls pool like the width's)
        "amps_err": [float(np.sqrt(max(cov[nshared + 4 * i, nshared + 4 * i], 0.0))) if cov.shape[0] > nshared + 4 * i else float("nan") for i in range(ntr)],
        "centers_err": [float(np.sqrt(max(cov[nshared + 4 * i + 1, nshared + 4 * i + 1], 0.0))) if cov.shape[0] > nshared + 4 * i + 1 else float("nan") for i in range(ntr)],
        "amps": [float(sol.x[nshared + 4 * i]) for i in range(ntr)],
        "gamma_coll_err_marginal": float(np.sqrt(max(_cov_marginal[0, 0], 0.0))), "sigma_laser_err_marginal": float(np.sqrt(max(_cov_marginal[1, 1], 0.0))),
        "corr_marginal": float(_cov_marginal[0, 1] / np.sqrt(_cov_marginal[0, 0] * _cov_marginal[1, 1])) if _cov_marginal[0, 0] > 0 and _cov_marginal[1, 1] > 0 else float("nan"),
        # THE CORE CHECK OF THE NOISE LAW (F42, 2026-09-17): the whitened residual per trace at the
        # solution and, per sample, whether it lies within one fitted full width of the trace's
        # centre; a law fitted on the wings and extrapolated to the core through bV + cV^2 is read
        # against the core's own residual variance by the producer, per condition
        "whitened_residuals": [np.asarray((volts[i] - (sol.x[nshared + 4 * i] * np.interp(freqs[i] - sol.x[nshared + 4 * i + 1], _g_final, _prof_final, left=0.0, right=0.0) + sol.x[nshared + 4 * i + 2] + sol.x[nshared + 4 * i + 3] * freqs[i])) / sigmas[i]) for i in range(ntr)],
        "core_masks": [np.abs(freqs[i] - sol.x[nshared + 4 * i + 1]) <= _fwhm_final for i in range(ntr)],
        # BASELINES COMPLETE THE SET (2026-08-22). centers and amps alone do
        # not let a caller rebuild the fitted model, because each trace also
        # carries its own linear background, so any consumer wanting residuals
        # had to refit or duplicate this function's parameter packing. K4's
        # residual atlas is the first such consumer. Purely additive: this
        # reads values already in sol.x and changes no computation, so every
        # committed number is untouched.
        "baselines": [(float(sol.x[nshared + 4 * i + 2]),
                       float(sol.x[nshared + 4 * i + 3])) for i in range(ntr)],
        "per_trace_diag": diag,
        # one record per input trace, in input order, whether or not trimming
        # ran: the caller writes these into results/trim_report.csv
        "trim_records": trim_records,
    }

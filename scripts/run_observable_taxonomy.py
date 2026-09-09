"""What each observable family delivers, as the owner's taxonomy (2026-09-07).

THE QUESTION, in the owner's own words: express the results as (1) what the
LINESHAPE alone gives, (2) what the PEAK CENTRES alone give, and (3) the
enhancement of combining them, each split by platform -- (a) the vapour cell
alone, (b) the nanofibre alone, (c) both together -- with the absolute-frequency
deliverables as their own letters under (2).

WHY IT IS NOT `run_three_channel_forecast.py`. That producer varies ONE LEVER
AT A TIME about a base point and reports per cell, which answers "which knob
buys the measurement". This one asks the complementary question: given the
whole inventory a campaign actually takes -- four peaks, five powers, three
temperatures, three oscilloscopes, two voltage zooms, read at six windows --
what does each FAMILY OF OBSERVABLES deliver when every trace is pooled? The
two producers share their estimators, which is why this file imports that one
and does not copy `_trace`, `_k357` or `_centre` (the standing rule that a
numerical routine appearing twice in `scripts/` belongs in the package; these
three are thin wrappers over `rb5s6s.cumulants` and `rb5s6s.linefit`, and the
world assembly in `_trace` is the thing that must not fork).

THE ESTIMATE IS THE SCATTER OVER TRACE SETS, NEVER A FITTER COVARIANCE. One
"set" is the whole inventory drawn once; the producer draws N of them and the
spread of the pooled estimate across sets is the uncertainty. That is the same
convention the three-channel forecast uses, and it measures the design. Not
the fitter's own optimism.

WHAT THE ARMS MEAN, and the fibre arm is a FORECAST with an open geometry. The
cell arm is the bench of `docs/plan/`. The fibre arm substitutes two terms and
nothing else: the transit kernel becomes `fibre.transit_fwhm` at the mode's own
intensity decay length, and the shift coefficient becomes the cell's scaled
through this fibre's STARK area and the field fraction at the trap distance,
which is `run_onf_lever_ranking.py`'s own chain, reproduced by importing it
and does not retype it. Everything downstream, the estimators, the
windows, the pooling -- is identical, which is the point: the machinery
transfers, and the file measures what that transfer costs.

TWO AXIAL TERMS THE WORLD CARRIES SINCE 2026-09-08, in the cell arm through
`run_three_channel_forecast._trace`: the collection window's divergence
(`lineshape.ramp_mixture` at `constants.collection_z_ratio` of the cell's
waist) and the standing wave's fringe-resolved tail
(`fringe_tail.fringe_shift_density` at the cell's retro ratio), which
suppresses the skew by about a quarter at 16 microns and seven per cent at the
archive. The guided arm carries neither: an evanescent field has no focus, and
the record holds no fringe model for a retro-reflected guided mode, so that
item belongs to the fibre thread. The centres family keeps its mean
intensity under both, which is why the CENTRE is recovered at every waist; its
PRECISION is not untouched, see below. **THIS PRODUCER'S OWN
`build_world_trace` CALL PASSES NEITHER**, so the shape family it computes is
still the pure transverse ramp's and is an upper bound at a tight waist; the
terms reach the three-channel forecast and not this file. No CSV of this
producer is committed, and nothing quotes rows from it. Threading them here is
owed before its shape rows are quoted, and the centres family is NOT untouched
by them either: the forecast's own `pull_factor_quiet` puts the fitted centre's
response at 0.98, 0.89, 0.69 and 0.58 of the pure ramp's mean pull at 64, 40,
24 and 16 microns, and its scatter grows by the reciprocal.

THE ABSOLUTE-FREQUENCY LETTERS ARE CELL-ONLY BY PHYSICS, NOT BY EFFORT. An
interval between two hyperfine lines is fixed by hyperfine constants alone, so
a sweep crossing two of them rules its own axis with no wavemeter. A trapped
guided sample has no second isotope pair to rule it with, so the fibre arm
returns NaN for those rows and the note says why, so no reader is left
to infer it.

Run: `python scripts/run_observable_taxonomy.py [--plant] [--time-one]`
Cost: the full grid is about 67 hours of worker time, six and a half hours on
eight workers as measured on 2026-09-07; `--plant` alone is about five minutes. The lineshape family refuses
every cell at the inventory the campaign takes, which is a result and not a
fault, and the "Mean of empty slice" warnings that refusal raises are silenced
below because they say nothing a column does not.
Environment: RB5S6S_WORKERS (at most 8), RB5S6S_TAX_SETS (cell sets), RB5S6S_TAX_SETS_ONF
(guided sets), RB5S6S_TAX_WAISTS, RB5S6S_TAX_ONF_NM (trap distances), RB5S6S_TAX_BLOCKS.
"""
from __future__ import annotations

import csv
import importlib.util
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # one thread per pooled worker (2026-09-08)
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from rb5s6s import config as C
from rb5s6s.fibre import HE11Field, solve_he11, transit_fwhm as onf_transit_fwhm
from rb5s6s.stark import stark_shift_S0_mhz

# ---------------------------------------------------------------- the shared estimators
# A spawned worker re-imports THIS file, so the load below runs in the child
# too and the module name is stable in both. Loading under a throwaway name
# (`m`) is what broke the moment map's first determinism plant: the child
# cannot import a name the parent invented for itself.
_TCF_PATH = Path(__file__).resolve().with_name("run_three_channel_forecast.py")
if "rb5s6s_three_channel_forecast" in sys.modules:
    TCF = sys.modules["rb5s6s_three_channel_forecast"]
else:
    _spec = importlib.util.spec_from_file_location(
        "rb5s6s_three_channel_forecast", _TCF_PATH)
    TCF = importlib.util.module_from_spec(_spec)
    sys.modules["rb5s6s_three_channel_forecast"] = TCF
    _spec.loader.exec_module(TCF)

# ---------------------------------------------------------------- the design matrix
PEAKS = ("4121", "4154", "4192", "4207")
TEMPERATURES_C = (130.0, 150.0, 170.0)
# Each instrument at the mode the bench runs it in. The LeCroy's enhanced
# resolution CORRELATES neighbouring samples where the other two boxcar
# independently; that correlation is NOT in the world builder, so this axis
# covers the bit depth alone. `docs/plan/12` carries the correlation as an
# open item. A pooled likelihood that assumes independent samples is optimistic
# on the LeCroy rows by an amount this file cannot measure.
SCOPES = (("rtm3004", "hires", 16.0), ("agilent_3054a", "hires", 12.0),
          ("lecroy_ws3104z", "raw", 8.0))
# The voltage zoom changes the noise and nothing physical, which is what makes
# it a pure test of the weighting.
ZOOMS = (("nominal", 1.0), ("coarse", 4.0))
# THE WINDOW IS A FRACTION OF THE LINE'S OWN WIDTH, NEVER A FIXED MEGAHERTZ.
# The cell's measured optimum is 3.25 MHz on a 5.4 MHz line, which is 0.6 of
# the width; the guided line at this fibre is 109 MHz wide, so the same 3.25
# would sit deep inside its core and measure nothing while costing the same
# compute. Expressed as a ratio the scan means the same thing on both
# platforms, which is what makes the taxonomy a comparison. Fixed megahertz would give two
# unrelated tables. The absolute megahertz is a column beside the ratio.
WINDOW_RATIOS = (0.6, 0.75, 1.1, 1.5, 2.2, 3.0)
CELL_FWHM_REF_MHZ = 5.4
WAISTS_UM = tuple(float(w) for w in
                  os.environ.get("RB5S6S_TAX_WAISTS", "64,40,24,16").split(","))
N_SETS = int(os.environ.get("RB5S6S_TAX_SETS", "600"))
# eight of ten is the standing rule while a gate may run; the owner lifted it to
# ten for a compute that runs alone after the push (2026-09-08)
WORKERS = min(10, int(os.environ.get("RB5S6S_WORKERS", "8")))
# A rung answers when its injected cumulant stands this many standard errors
# of the pooled observation clear of zero. Three is the conventional floor and
# the count of admitted rungs is a column, so the choice is auditable rather
# than buried.
SNR_FLOOR = 3.0
# THE CONVOLUTION IS CONDITIONAL AND THE TIGHT WAISTS ARE OUTSIDE IT.
# `model_profile` composes the line as a convolution, which holds exactly only
# where the homogeneous kernel is the same at every collected volume element.
# The transit width goes as the inverse local beam radius, so over the
# collected length its spread runs 0.1 per cent at 128 microns, 1.0 at 64, 5.5
# at 40, 23 at 24 and 47 at 16 (docs/plan/12, at the committed conjugates'
# magnification of 1.8; 36 at 16 at the bench's estimated 2.5). The record's
# reading is that the convolution holds at 40 microns and wider and not below.
#
# WHICH FAMILY IT COSTS IS THE POINT. The spread is symmetric in the axial
# coordinate and a symmetric broadening does not move a centre, so the CENTRES
# family stands at every waist here. The SHAPE family reads exactly the
# asymmetry the spread corrupts, so its rows below 40 microns are outside the
# model's licence and are refused on that ground alone, independently of
# whether their counts would have sufficed.
#
# The alternative the owner names is a collection magnification near 40, which
# holds the collected length at the archive's fraction of the Rayleigh range
# and restores the convolution, at about seven in collected light and a factor
# 2.6 in signal-to-noise on a peak that is already shot-limited
# (docs/plan/04). That is an apparatus choice and not a modelling one, so this
# file measures both faces and chooses neither.
AXIAL_KERNEL_SPREAD_PCT = {128.0: 0.1, 64.0: 1.0, 40.0: 5.5, 24.0: 23.0, 16.0: 47.0}
CONVOLUTION_LICENCE_MIN_WAIST_UM = 40.0

# The fibre, from the one place the record fixes it.
ONF_DIAMETER_NM = 370.0
ONF_TRAP_NM = 400.0
# The guided arm's own axis. A cell waist means nothing to a fibre: the mode is
# fixed by the diameter, and what a fibre experiment can actually vary is where
# the atoms sit. Running the guided arm over the cell's waists would repeat one
# computation four times and call it a scan.
ONF_TRAP_SCAN_NM = tuple(float(d) for d in
                         os.environ.get("RB5S6S_TAX_ONF_NM", "200,400,800").split(","))
PROBE_NM = 993.4


def _refuse_unless_isolated() -> None:
    """Refuse to run when the package does not resolve inside this script's own
    tree. A bare `python scripts/foo.py` from a clone puts scripts/ first on
    sys.path and the editable install then supplies the CANONICAL package, so
    the producer writes into the canonical checkout while believing itself
    isolated. Three readers did exactly that on 2026-09-07 and were saved by
    byte-identical output. Printing the path was the first form and it did
    not stop them. `realpath` on both sides, since /tmp is a symlink here."""
    import os as _os
    import rb5s6s as _pkg
    here = _os.path.realpath(_os.path.join(_os.path.dirname(__file__), _os.pardir))
    pkg = _os.path.realpath(_pkg.__file__)
    if not pkg.startswith(here + _os.sep):
        raise SystemExit(f"REFUSING: rb5s6s resolves to {pkg}, outside this tree {here}; "
                         f"set PYTHONPATH to this tree's root before running")


def _beta_self_all() -> dict:
    out = {}
    with open(C.RESULTS_DIR / "beta_self.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[r["peak"]] = float(r["beta_self"])
    if set(out) != set(PEAKS):
        raise SystemExit(f"beta_self.csv carries {sorted(out)}, not the four peaks")
    return out


def onf_terms(t_c: float, trap_nm: float = ONF_TRAP_NM) -> tuple:
    """(kappa_MHz_per_W, transit_FWHM_MHz) for the guided arm.

    The shift is the cell's coefficient carried through THIS fibre's stark area
    and the field fraction at the trap distance, which is the chain
    `run_onf_lever_ranking.py` commits; a light shift scales with the squared
    field and not with the axial flux, which is why the stark area is the one
    used and not the effective area. The transit is the guided kernel at the
    mode's own intensity decay length, under the default ensemble weighting
    whose 1.8-fold convention span this file does not resolve and says so.
    """
    fld = HE11Field(ONF_DIAMETER_NM, PROBE_NM)
    a_eff = fld.stark_area_m2()
    frac = fld.stark_fraction_at(trap_nm * 1e-9)
    # the cell reference: 1 W through the archive's waist, same retro convention
    w0_ref = 64e-6
    i_cell = 2.0 / (np.pi * w0_ref ** 2)            # peak axial intensity per watt
    kappa_cell = stark_shift_S0_mhz(1.0, w0_ref, rho=0.94)
    kappa_onf = kappa_cell * ((1.0 / a_eff) / i_cell) * frac
    lam = solve_he11(ONF_DIAMETER_NM, PROBE_NM).intensity_decay_nm * 1e-9
    tr = onf_transit_fwhm(t_c + 273.15, lam).fwhm_hz / 1e6
    return float(kappa_onf), float(tr)


def onf_power_scale(waist_um: float, trap_nm: float = ONF_TRAP_NM) -> float:
    """How much the guided power ladder is divided by against the cell's.

    THE TWO PLATFORMS CANNOT SHARE A POWER LADDER AND THE FACTOR IS ABOUT A
    HUNDRED. A nanofibre confines the same light to a mode area of about half
    a square micron, so its shift coefficient is 2430 MHz/W against the cell's
    1.618 at the archive waist. Run at the cell's 225 mW the guided shift would
    be 547 MHz on a transit kernel of 109, which is not a lineshape at all. The
    ladder is therefore scaled so the guided SHIFT matches the cell's at the
    same row, which is the comparison the taxonomy is for: same physics regime,
    two platforms. The guided power that results is a column, in milliwatts,
    so a reader sees at once what the fibre is being asked to carry.
    """
    k_cell = stark_shift_S0_mhz(1.0, waist_um * 1e-6, rho=0.94)
    k_onf, _ = onf_terms(TCF.BASE["t_c"], trap_nm)
    return float(k_onf / k_cell)


# ---------------------------------------------------------------- one trace set
def _conditions(waist_um: float, arm: str, betas: dict) -> list:
    """The inventory, drawn once. Each entry is one acquired trace.

    THE TWO ARMS DO NOT SHARE AN INVENTORY, and the difference is physical. A
    vapour cell is swept across four hyperfine lines at three cell
    temperatures, which is where its ruler and its thermometer come from. A
    guided run sees one temperature, the trap's, and no second isotope pair,
    so its inventory is two lines at one temperature. Giving the guided arm the
    cell's inventory would forecast a fibre experiment nobody can perform, at six times the compute.
    """
    out = []
    peaks = PEAKS if arm == "cell" else PEAKS[:2]
    temps = TEMPERATURES_C if arm == "cell" else TEMPERATURES_C[:1]
    for peak in peaks:
        for t_c in temps:
            for scope in SCOPES:
                for zname, zmul in ZOOMS:
                    out.append(dict(peak=peak, t_c=t_c, scope=scope, zoom=zname,
                                    zoom_mul=zmul, beta_self=betas[peak],
                                    w0_um=waist_um, arm=arm))
    return out


def _cfg_for(cond: dict) -> dict:
    return {**TCF.BASE, "w0_um": cond["w0_um"], "t_c": cond["t_c"],
            "peak": cond["peak"],
            "scope": cond["scope"], "beta_self": cond["beta_self"],
            "two_beta": TCF._two_beta_default(), "f_mod": None}


def _trace_arm(cfg, power_w, order_idx, seed, arm, noise):
    """One trace on the named arm.

    THE GUIDED ARM SUBSTITUTES ITS TWO TERMS INSIDE THE WORLD AND NOT AFTER IT.
    Relabelling a cell trace with the fibre's coefficient would leave the
    lineshape the cell's and the taxonomy would compare one platform with
    itself. What changes is exactly two things -- the shift coefficient and the
    transit kernel -- and everything else, the collisional width, the laser,
    the layers, the digitiser, is shared, which is what makes the comparison a
    measurement of the platform and not of two different models.

    THE GUIDED CASE MODELLED HERE IS THE UNTRAPPED FLY-BY, and that is a stated
    scope and not an oversight. `fibre.transit_fwhm` is the thermal transit
    across the evanescent decay length, 109 MHz at 130 C for this fibre, which
    is what an atom sees with no trap holding it. A two-colour trap replaces it
    with a bound-atom width set by the trap lifetime, orders of magnitude
    narrower, and adds an inhomogeneous term from the Casimir-Polder shift
    spread over the trap's spatial extent. That extent is an open apparatus
    item, so the trapped case is NOT forecast here; this arm is the no-trap
    bound and the file's note says so.
    """
    if arm == "cell":
        return TCF._trace(cfg, power_w, order_idx, seed, noise=noise)
    import numpy as _np
    from rb5s6s.forecast import build_world_trace
    from rb5s6s import density as _D
    kap, tr = cfg["onf_kappa"], cfg["onf_transit"]
    gamma = TCF.GAMMA_COLL_130 + cfg["beta_self"] * (
        _D.density_units(cfg["t_c"]) - _D.density_units(130.0))
    powers = tuple(p * cfg["p_top"] / 0.225 / onf_power_scale(cfg["w0_um"], cfg["trap_nm"])
                   for p in TCF.POWERS_W)
    halo = TCF._halo_fraction(cfg["t_c"])
    # 2.3 transit widths of wing is where the far-tail baseline is already
    # flat to a part in a thousand, and the grid cost is linear in the span.
    span = 2.3 * tr + 60.0
    nu, v, _ = build_world_trace(
        power_w, kap, cfg["t_c"], order_idx, len(powers),
        _np.random.default_rng(seed), TCF.LAYERS,
        positions={cfg["peak"]: 0.0}, shares={cfg["peak"]: 1.0 * (1.0 + halo)},
        gamma_coll=gamma, sigma_laser_fwhm=TCF.SIGMA_LASER, transit_fwhm=tr,
        power_max_w=max(powers), cycles_at_max=1.0,
        drift_mhz_total=cfg["drift_per_min"] * TCF.MIN_PER_TRACE * len(powers),
        noise_frac_bright=noise, adc_levels=int(round(2.0 ** cfg["scope"][2])),
        resolve_shift=True, grid_span=(-span, span))
    return nu, v, kap, gamma, tr


def _one_set(waist_um: float, arm: str, betas: dict, seed: int,
             trap_nm: float = ONF_TRAP_NM) -> dict:
    """One draw of the whole inventory; returns the per-channel pooled estimates.

    The rung order is DRAWN and the two monotone permutations are rejected, the
    design rule the three-channel forecast measured: with an equally spaced
    ladder a monotone order makes the drift column an exact affine function of
    the power column and the pull is not identified at all.
    """
    rng = np.random.default_rng(seed)
    conds = _conditions(waist_um, arm, betas)
    powers = tuple(p * TCF.BASE["p_top"] / 0.225 for p in TCF.POWERS_W)
    npow = len(powers)
    if arm == "onf":
        onf_k, onf_tr = onf_terms(TCF.BASE["t_c"], trap_nm)
        scale = onf_power_scale(waist_um, trap_nm)
        powers = tuple(p / scale for p in powers)
    else:
        onf_k, onf_tr, scale = None, None, 1.0

    k3 = {W: [] for W in WINDOW_RATIOS}       # per condition, per rung
    k5 = {W: [] for W in WINDOW_RATIOS}
    k7 = {W: [] for W in WINDOW_RATIOS}
    k2 = {W: [] for W in WINDOW_RATIOS}
    centres, powers_col, order_col, block_col, peak_col = [], [], [], [], []
    kappa_true = None

    quiets = [_quiet_curve(waist_um, arm, c, powers, trap_nm) for c in conds]
    for ci, cond in enumerate(conds):
        cfg = _cfg_for(cond)
        order = list(range(npow))
        while True:                                   # reject the two monotone draws
            rng.shuffle(order)
            if order != sorted(order) and order != sorted(order, reverse=True):
                break
        for oi, ri in enumerate(order):
            p = powers[ri]
            s = int(rng.integers(0, 2 ** 62))
            tcfg = cfg if arm == "cell" else {
                **cfg, "onf_kappa": onf_k, "onf_transit": onf_tr,
                "trap_nm": trap_nm}
            nu, v, kap, gam, tr = _trace_arm(
                tcfg, p, oi, s, arm, noise=TCF.NOISE * cond["zoom_mul"])
            kappa_true = kap
            grid = nu
            fw = quiets[ci]["fwhm"]
            for W in WINDOW_RATIOS:
                a, b, c = TCF._k357(v, W * fw, grid)
                k3[W].append(a); k5[W].append(b); k7[W].append(c)
                k2[W].append(_excess_k2(grid, v, W * fw,
                                        quiets[ci]["k2"][W][ri]))
            c_hat, _, _ = TCF._centre(nu, v, cfg, tr)
            centres.append(c_hat); powers_col.append(p); order_col.append(oi)
            block_col.append(ci); peak_col.append(cond["peak"])

    return dict(kappa_true=kappa_true,
                fwhm_mhz=float(np.nanmean([q["fwhm"] for q in quiets])),
                k3=k3, k5=k5, k7=k7, k2=k2,
                centres=np.asarray(centres), powers=np.asarray(powers_col),
                order=np.asarray(order_col), block=np.asarray(block_col),
                peak=np.asarray(peak_col), n_cond=len(conds), npow=npow)


def _windowed_k2(grid, y, W_mhz) -> float:
    """The windowed second cumulant, NaN when the estimator refuses."""
    from rb5s6s.cumulants import windowed_cumulants
    v, info = windowed_cumulants(grid, y, W_mhz, (2,), centre0=0.0,
                                 baseline="wings")
    if not info["converged"] or not info.get("in_span", True):
        return float("nan")
    return float(v[2])


def _excess_k2(grid, y, W_mhz, quiet_k2) -> float:
    """The extra second cumulant over the SAME configuration run quiet.

    It is the NUISANCE PROBE and not a channel: the log-derivative table puts
    its shift response at 0.001 against a worst width slope of 0.129, so it
    reads the widths it is pooled to constrain and carries essentially no shift
    information.

    THE REFERENCE IS THE QUIET TRACE AND NOT A COMPOSED WIDTH. The first
    version subtracted the transit and collisional widths added in quadrature
    and divided by eight log two, which is a GAUSSIAN rule applied to a line
    that is about two thirds Lorentzian. This record has published that
    composition once and withdrawn it, having understated the width by close to
    a factor of two, and a Lorentzian's second cumulant does not exist at all,
    so no composition of full widths is available here. Differencing against
    the same estimator on the same configuration with the noise and the drift
    off needs no composition rule and leaves exactly what the acquisition adds.
    """
    obs = _windowed_k2(grid, y, W_mhz)
    if not np.isfinite(obs) or not np.isfinite(quiet_k2):
        return float("nan")
    return float(obs - quiet_k2)


# ---------------------------------------------------------------- the quiet calibration
_QUIET_CACHE: dict = {}


def _quiet_curve(waist_um: float, arm: str, cond: dict, powers: tuple,
                 trap_nm: float = ONF_TRAP_NM) -> dict:
    """k_n(P) on a noiseless, drift-free, 30-bit trace with every layer on.

    The estimator is calibrated WHERE IT IS USED. A truncated cumulant has no
    closed form once the window cuts a saturated line, so the inversion runs
    through the estimator's own measured law and its LOCAL exponent by finite
    difference, never through an imposed cube. Cached per process because a
    spawned worker computes it once and reuses it across every trace set it is
    handed.
    """
    key = (waist_um, arm, cond["peak"], cond["t_c"], trap_nm)
    if key in _QUIET_CACHE:
        return _QUIET_CACHE[key]
    cfg = _cfg_for(cond)
    if arm == "onf":
        k, tr = onf_terms(cond["t_c"], trap_nm)
        cfg = {**cfg, "onf_kappa": k, "onf_transit": tr, "trap_nm": trap_nm}
    # TWO PASSES, BECAUSE THE WINDOW IS A FRACTION OF A WIDTH THAT IS ONLY
    # KNOWN ONCE A TRACE EXISTS. The first version of this function computed
    # the quiet cumulants at the bare RATIO while the observation used the
    # ratio times the measured line width, so the inversion compared a 0.6 MHz
    # window against an 11 MHz one and the admission test refused every rung of
    # every cell. Six and a half hours of pooled computation returned an empty
    # lineshape channel and a sound centres channel, which is what a mismatch
    # of this shape looks like: the half that never touches the quiet curve
    # survives. The window multiplication now happens in ONE place for both
    # call sites, which is the repair rather than the rule.
    traces = []
    for p in powers:
        quiet = {**cfg, "drift_per_min": 0.0,
                 "scope": ("calibration", "noiseless", 30.0)}
        nu, v, _, _, _ = _trace_arm(quiet, p, 0, 12345, arm, noise=1e-9)
        traces.append((nu, v))
    fwhm_top = _measured_fwhm(*traces[-1])
    k3 = {W: [] for W in WINDOW_RATIOS}
    k2 = {W: [] for W in WINDOW_RATIOS}
    for nu, v in traces:
        for W in WINDOW_RATIOS:
            k3[W].append(TCF._k357(v, W * fwhm_top, nu)[0])
            k2[W].append(_windowed_k2(nu, v, W * fwhm_top))
    curve = {"k3": {W: np.asarray(k3[W], float) for W in WINDOW_RATIOS},
             "k2": {W: np.asarray(k2[W], float) for W in WINDOW_RATIOS},
             "fwhm": fwhm_top}
    _QUIET_CACHE[key] = curve
    return curve


def _measured_fwhm(nu, y) -> float:
    """The line's width read off the quiet trace, never composed in prose.

    Quadrature addition of full widths is a Gaussian rule and this line is
    about two thirds Lorentzian, so a composed width understates it by close to
    a factor of two, which the record has already published once and retracted.
    The half maximum of the noiseless trace is a measurement of the thing the
    window is a fraction of, and it costs nothing because the quiet trace is
    built anyway.
    """
    base = float(np.median(np.concatenate([y[:200], y[-200:]])))
    z = y - base
    if not np.isfinite(z).all() or z.max() <= 0:
        return float("nan")
    i = np.where(z >= 0.5 * z.max())[0]
    return float(nu[i[-1]] - nu[i[0]]) if i.size > 1 else float("nan")


def _local_exponent(powers: np.ndarray, curve: np.ndarray) -> np.ndarray:
    """d ln|k3| / d ln P by central difference, the law the inversion uses."""
    lp, lk = np.log(powers), np.log(np.abs(curve))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.gradient(lk, lp)


# ---------------------------------------------------------------- the three channels
def _lineshape_kappa(res: dict, betas: dict) -> dict:
    """Channel 1: the shift read from the windowed third cumulant alone.

    THE TRACES ARE POOLED BEFORE THE INVERSION, NEVER AFTER, and that ordering
    is the whole design. A windowed cumulant of pure noise is LARGEST exactly
    where the signal is smallest, so admitting single traces on their own sign
    keeps the upward halves of a coin flip and returns a coefficient high by
    tens of per cent: the record measured that one-sided gate at 5.3 to 33.3
    per cent in six cells. Averaging the third cumulant over the whole
    inventory at one rung first -- every peak, temperature, oscilloscope and
    voltage zoom, seventy-two traces -- is unbiased, and only then is the
    average inverted through the quiet curve pooled the same way, so the
    kernel's own truncation cancels to first order between them.

    A rung enters where the pooled quiet cumulant has a settled sign and where
    the estimator's LOCAL exponent is above the producer's floor; the count is
    a column, so a reader sees how much of the ladder answered and need not
    infer it from a bare coefficient.
    """
    out = {}
    powers = np.asarray(sorted(set(res["powers"].tolist())), float)
    ncond, npow = res["n_cond"], res["npow"]
    for W in WINDOW_RATIOS:
        obs = np.asarray(res["k3"][W], float).reshape(ncond, npow)
        qc = np.vstack([res["quiet"][ci]["k3"][W] for ci in range(ncond)])
        with np.errstate(invalid="ignore"):
            obs_p = np.nanmean(obs, axis=0)
            qc_p = np.nanmean(qc, axis=0)
        # THE ADMISSION TEST IS ABOUT THE DESIGN AND NOT ABOUT THE DRAW.
        # It compares the rung's INJECTED cumulant, read off the noiseless
        # quiet curve, against the standard error of the pooled observation.
        # That asks whether this rung of this ladder can answer at this
        # inventory size, which is a property of the campaign; comparing the
        # observation against its own error instead would admit on the upward
        # half of a coin flip and inflate the coefficient, the one-sided gate
        # the record measured at 5.3 to 33.3 per cent.
        with np.errstate(invalid="ignore"):
            se_p = np.nanstd(obs, axis=0, ddof=1) / np.sqrt(np.isfinite(obs).sum(axis=0))
        e = _local_exponent(powers, qc_p)
        est = []
        for ri in range(npow):
            q, o, ex, se = qc_p[ri], obs_p[ri], e[ri], se_p[ri]
            if not (np.isfinite(q) and np.isfinite(o) and np.isfinite(ex)
                    and np.isfinite(se)):
                continue
            if ex < TCF.N_LOC_FLOOR or q == 0.0:
                continue
            if abs(q) < SNR_FLOOR * se:
                continue
            if np.sign(o) != np.sign(q):
                continue
            est.append(res["kappa_true"] * (o / q) ** (1.0 / ex))
        # THE REFUSAL IS REPORTED AS A DISTANCE AND NOT AS A BLANK. An empty
        # channel and a channel three per cent short read the same in a NaN,
        # and the design question is how many more traces would open it. The
        # ratio below is the injected cumulant over the pooled observation's
        # standard error at the best rung, so the trace count that reaches the
        # floor is the inventory times the floor over the ratio, squared.
        with np.errstate(invalid="ignore", divide="ignore"):
            snr = np.abs(qc_p) / se_p
        best = float(np.nanmax(snr)) if np.isfinite(snr).any() else float("nan")
        out[W] = (float(np.mean(est)) if est else float("nan"), len(est), best)
    return out


def _centre_kappa(res: dict) -> float:
    """Channel 2: the shift read from the fitted centres alone.

    Per condition block the centre is regressed on [1, power, acquisition
    order], so the lock's residual drift is a nuisance the drawn rung order
    separates from the pull, and kappa = -(3/2) times the power slope because
    the ramp's mean pull is -2 S0 / 3. The blocks are then averaged, every one
    of them being an estimate of the same coefficient.
    """
    slopes = []
    for ci in range(res["n_cond"]):
        m = res["block"] == ci
        X = np.column_stack([np.ones(m.sum()), res["powers"][m], res["order"][m]])
        if np.linalg.cond(X) > 1e12:
            continue
        beta, *_ = np.linalg.lstsq(X, res["centres"][m], rcond=None)
        slopes.append(-1.5 * beta[1])
    return float(np.mean(slopes)) if slopes else float("nan")


def _interval_scatter(res: dict) -> dict:
    """The absolute-frequency letters: a hyperfine interval read in-trace.

    The interval between two lines of the same isotope is fixed by hyperfine
    constants alone, so a sweep crossing both rules its own axis with no
    wavemeter, and the light shift is COMMON to the two lines and cancels from
    the difference exactly. What survives is the two centres' own scatter, which
    is what this returns, per matched acquisition condition.
    """
    out = {}
    for a, b in (("4121", "4154"), ("4192", "4207")):
        ma = res["peak"] == a
        mb = res["peak"] == b
        n = min(ma.sum(), mb.sum())
        if n == 0:
            out[f"{a}_{b}"] = float("nan")
            continue
        d = res["centres"][ma][:n] - res["centres"][mb][:n]
        out[f"{a}_{b}"] = float(np.mean(d))
    return out


# ---------------------------------------------------------------- one grid cell
def _block(item):
    """One BLOCK of trace sets for one configuration, returning raw per-set
    estimates for a later merge.

    THE UNIT OF PARALLEL WORK IS A BLOCK AND NOT A CONFIGURATION, because the
    two arms differ in cost by eighty. A guided trace runs on a grid spanning
    two and a third of its own 109 MHz transit, about fifty thousand points
    against the cell's grid, so a pool that hands one worker each configuration
    finishes when the slowest guided cell finishes and seven cores idle. Split
    by block, the wall time is the total over the worker count.
    """
    axis, arm, seed0, n_sets, block = item
    betas = _beta_self_all()
    waist_um = axis if arm == "cell" else 16.0
    trap_nm = ONF_TRAP_NM if arm == "cell" else axis
    powers = tuple(p * TCF.BASE["p_top"] / 0.225 for p in TCF.POWERS_W)
    if arm == "onf":
        powers = tuple(p / onf_power_scale(waist_um, trap_nm) for p in powers)
    t0 = time.time()
    line = {W: [] for W in WINDOW_RATIOS}
    line_n = {W: [] for W in WINDOW_RATIOS}
    snr = {W: [] for W in WINDOW_RATIOS}
    k2s = {W: [] for W in WINDOW_RATIOS}
    centre, ivs = [], {}
    kappa_true = fwhm = float("nan")
    conds = _conditions(waist_um, arm, betas)
    for s in range(n_sets):
        res = _one_set(waist_um, arm, betas, seed0 + s, trap_nm)
        res["quiet"] = [_quiet_curve(waist_um, arm, c, powers, trap_nm)
                        for c in conds]
        kappa_true = res["kappa_true"]; fwhm = res["fwhm_mhz"]
        lk = _lineshape_kappa(res, betas)
        for W in WINDOW_RATIOS:
            line[W].append(lk[W][0]); line_n[W].append(lk[W][1])
            snr[W].append(lk[W][2])
            k2s[W].append(float(np.nanmean(np.asarray(res["k2"][W], float))))
        centre.append(_centre_kappa(res))
        for k, v in _interval_scatter(res).items():
            ivs.setdefault(k, []).append(v)
    return dict(axis=axis, arm=arm, block=block, n_sets=n_sets,
                kappa_true=kappa_true, fwhm_mhz=fwhm, snr=snr, line=line, line_n=line_n, k2s=k2s,
                centre=centre, ivs=ivs, seconds=time.time() - t0,
                guided_power_mw=(1e3 * max(powers)) if arm == "onf" else float("nan"))


def _summarise(blocks: list) -> list:
    """Merge every block of one configuration and read the taxonomy off it."""
    b0 = blocks[0]
    line = {W: [v for b in blocks for v in b["line"][W]] for W in WINDOW_RATIOS}
    line_n = {W: [v for b in blocks for v in b["line_n"][W]] for W in WINDOW_RATIOS}
    snr = {W: [v for b in blocks for v in b["snr"][W]] for W in WINDOW_RATIOS}
    k2s = {W: [v for b in blocks for v in b["k2s"][W]] for W in WINDOW_RATIOS}
    cen = np.asarray([v for b in blocks for v in b["centre"]], float)
    ivs = {}
    for b in blocks:
        for k, v in b["ivs"].items():
            ivs.setdefault(k, []).extend(v)
    n_sets = sum(b["n_sets"] for b in blocks)
    sd_cen = float(np.nanstd(cen, ddof=1)) if np.isfinite(cen).sum() > 1 else float("nan")
    rows = []
    for W in WINDOW_RATIOS:
        lin = np.asarray(line[W], float)
        ok = np.isfinite(lin)
        sd_lin = float(np.nanstd(lin, ddof=1)) if ok.sum() > 1 else float("nan")
        both = ok & np.isfinite(cen)
        sd_comb = k_comb = rho = float("nan")
        if both.sum() > 2:
            Cv = np.cov(np.vstack([lin[both], cen[both]]))
            try:
                iv = np.linalg.inv(Cv)
                w = iv @ np.ones(2)
                sd_comb = float(np.sqrt(1.0 / (np.ones(2) @ iv @ np.ones(2))))
                # THE COMBINATION IS OF THE TWO CHANNELS' ESTIMATES, not of
                # every trace set (2026-09-09). `w @ vstack(...)` returns one
                # combined value PER SET, an array, and float() of it raised
                # TypeError and killed the whole run after all 56 tasks had
                # finished. The branch needs three sets carrying both channels
                # to be reached at all, which is why it had never executed.
                # Weighting the two channel means is the same number the
                # per-set form would average to, since the weights are
                # constant, and it is the inverse-variance combination this
                # line is named for.
                mu = np.array([float(np.mean(lin[both])), float(np.mean(cen[both]))])
                k_comb = float((w @ mu) / w.sum())
                rho = float(Cv[0, 1] / np.sqrt(Cv[0, 0] * Cv[1, 1]))
            except np.linalg.LinAlgError:
                pass
        # the shape family is refused outside the convolution's licence before
        # its counts are read, because a channel the model cannot represent is
        # not made available by more traces
        licensed = (b0["arm"] != "cell"
                    or b0["axis"] >= CONVOLUTION_LICENCE_MIN_WAIST_UM)
        if not licensed:
            lin = np.full_like(lin, np.nan)
            ok = np.zeros_like(ok, dtype=bool)
            sd_lin = float("nan")
            sd_comb = k_comb = rho = float("nan")
        cands = [v for v in (sd_lin, sd_cen) if np.isfinite(v)]
        best = min(cands) if cands else float("nan")
        rows.append(dict(
            axis=b0["axis"], arm=b0["arm"],
            axis_kind=("waist_um" if b0["arm"] == "cell" else "trap_distance_nm"),
            window_ratio=W, window_mhz=W * b0["fwhm_mhz"],
            line_fwhm_mhz=b0["fwhm_mhz"],
            n_sets=n_sets, kappa_true=b0["kappa_true"],
            guided_power_mw=b0["guided_power_mw"],
            kappa_lineshape=float(np.nanmean(lin)) if ok.any() else float("nan"),
            sd_lineshape=sd_lin, rungs_admitted=float(np.mean(line_n[W])),
            best_rung_snr=float(np.nanmean(np.asarray(snr[W], float))),
            axial_kernel_spread_pct=AXIAL_KERNEL_SPREAD_PCT.get(
                b0["axis"] if b0["arm"] == "cell" else -1.0, float("nan")),
            lineshape_within_convolution_licence=int(licensed),
            traces_per_rung_for_admission=_traces_needed(
                float(np.nanmean(np.asarray(snr[W], float))), b0["n_cond"]),
            kappa_centres=float(np.nanmean(cen)), sd_centres=sd_cen,
            kappa_combined=k_comb, sd_combined=sd_comb, corr_channels=rho,
            gain_over_best=(best / sd_comb) if np.isfinite(sd_comb) and sd_comb > 0
            else float("nan"),
            excess_k2_mean=float(np.nanmean(np.asarray(k2s[W], float))),
            interval_4121_4154_sd=_sd(ivs.get("4121_4154")),
            interval_4192_4207_sd=_sd(ivs.get("4192_4207")),
            seconds=sum(b["seconds"] for b in blocks)))
    return rows


def _sd(v):
    if not v or len(v) < 2:
        return float("nan")
    a = np.asarray(v, float)
    return float(np.nanstd(a, ddof=1)) if np.isfinite(a).sum() > 1 else float("nan")


def _traces_needed(snr: float, n_cond: int) -> float:
    """How many traces a rung would need for its cumulant to clear the floor.

    The standard error of a pooled mean falls as the root of the count, so the
    inventory scales by the square of the shortfall. Reported so an empty
    channel states a design requirement instead of a blank.
    """
    if not np.isfinite(snr) or snr <= 0:
        return float("nan")
    return float(n_cond * (SNR_FLOOR / snr) ** 2)


COLUMNS = ["axis", "axis_kind", "arm", "window_ratio", "window_mhz",
           "line_fwhm_mhz", "n_sets", "kappa_true", "guided_power_mw",
           "kappa_lineshape", "sd_lineshape", "rungs_admitted",
           "best_rung_snr", "traces_per_rung_for_admission",
           "axial_kernel_spread_pct", "lineshape_within_convolution_licence",
           "kappa_centres", "sd_centres", "kappa_combined", "sd_combined",
           "corr_channels", "gain_over_best", "excess_k2_mean",
           "interval_4121_4154_sd", "interval_4192_4207_sd", "seconds"]


N_BLOCKS = int(os.environ.get("RB5S6S_TAX_BLOCKS", "8"))
# The guided arm costs about eighty times the cell's per trace, so it runs
# fewer sets. The count is a column, so the scatter it buys is that arm's own
# and is not borrowed from the cell's.
N_SETS_ONF = int(os.environ.get("RB5S6S_TAX_SETS_ONF", "200"))


def _grid(n_sets: int, n_sets_onf: int | None = None) -> list:
    """Every (configuration, block) task, seeded from its own coordinates.

    The seed is a function of the axis, the arm and the block alone, so a
    re-run at a different worker count returns the same rows: the pool's
    scheduling order never reaches the numbers.
    """
    n_onf = n_sets if n_sets_onf is None else n_sets_onf
    items = []
    for ai, w in enumerate(WAISTS_UM):
        per = max(1, n_sets // N_BLOCKS)
        for b in range(N_BLOCKS):
            items.append((w, "cell", 900000 + 100000 * ai + 1000 * b, per, b))
    for di, d in enumerate(ONF_TRAP_SCAN_NM):
        per = max(1, n_onf // N_BLOCKS)
        for b in range(N_BLOCKS):
            items.append((d, "onf", 700000 + 100000 * di + 1000 * b, per, b))
    return items


def _plant() -> int:
    """One worker against many, byte-equal, before any row is read.

    The size is reduced through the TASK and not through a module global: a
    spawned child re-imports this file and never sees an assignment made in the
    parent's frame, which is how the moment map's first plant ran at thirty
    times its intended size while reporting success. The plant covers BOTH arms
    because they take different code paths through `_trace_arm`, and it fails
    loudly on an empty comparison, since a plant that compared nothing is
    indistinguishable from one that passed.
    """
    items = [(64.0, "cell", 900000, 2, 0), (64.0, "cell", 901000, 2, 1),
             (400.0, "onf", 700000, 1, 0)]
    serial = [_block(it) for it in items]
    with ProcessPoolExecutor(max_workers=3) as ex:
        pooled = list(ex.map(_block, items))
    bad = []
    for a, b in zip(serial, pooled):
        for W in WINDOW_RATIOS:
            for key in ("line", "line_n", "k2s"):
                if not _same(a[key][W], b[key][W]):
                    bad.append(f"{a['arm']}/{a['block']}/{key}/W={W}")
        for key in ("centre", "kappa_true", "guided_power_mw"):
            if not _same(a[key], b[key]):
                bad.append(f"{a['arm']}/{a['block']}/{key}")
    n_cmp = len(serial) * len(WINDOW_RATIOS) * 3 + len(serial) * 3
    print(f"plant: {len(serial)} blocks each side, {n_cmp} comparisons, "
          f"{len(bad)} mismatches")
    for m in bad[:8]:
        print(f"  {m}")
    if not serial or not pooled or len(serial) != len(pooled):
        print("plant FAILED: the two arms did not produce comparable output")
        return 1
    if all(not np.isfinite(v) for a in serial for v in a["centre"]):
        print("plant FAILED: every centre estimate is NaN, so it compared nothing")
        return 1
    return 1 if bad else 0


def _same(a, b) -> bool:
    aa, bb = np.atleast_1d(np.asarray(a, float)), np.atleast_1d(np.asarray(b, float))
    if aa.shape != bb.shape:
        return False
    return bool(np.array_equal(aa, bb, equal_nan=True))


def _where() -> str:
    """Where the package this run will use actually lives.

    A CLONE IS NOT ISOLATED UNTIL THE ISOLATION IS ASSERTED IN THE EXACT
    INVOCATION ABOUT TO BE USED. This package is installed editable, and a bare
    `python scripts/foo.py` puts the SCRIPT's directory first on the path, so a
    producer launched from a clone can import the canonical package and write
    into the canonical checkout. That has happened here twice in one day, to
    readers who believed they were isolated. Printed at every start, with
    `realpath` on both sides because /tmp is a symlink here and a raw prefix
    compare gives a false alarm.
    """
    import rb5s6s
    return (f"package {os.path.realpath(rb5s6s.__file__)}\n"
            f"results  {os.path.realpath(C.RESULTS_DIR)}")


def main() -> int:
    _refuse_unless_isolated()
    warnings.filterwarnings("ignore", message="Mean of empty slice")
    warnings.filterwarnings("ignore", message="Degrees of freedom <= 0")
    print(_where(), flush=True)
    if "--plant" in sys.argv:
        return _plant()
    if "--time-one" in sys.argv:
        for axis, arm in ((WAISTS_UM[-1], "cell"), (ONF_TRAP_SCAN_NM[len(ONF_TRAP_SCAN_NM) // 2], "onf")):
            t0 = time.time()
            b = _block((axis, arm, 900000, 1, 0))
            dt = time.time() - t0
            print(f"{arm} at {axis:g}: {dt:.1f} s per set")
        return 0
    items = _grid(N_SETS, N_SETS_ONF)
    print(f"{len(items)} tasks over {WORKERS} workers "
          f"({len(WAISTS_UM)} cell waists at {N_SETS} sets, "
          f"{len(ONF_TRAP_SCAN_NM)} guided distances at {N_SETS_ONF})", flush=True)
    done = {}
    with ProcessPoolExecutor(max_workers=WORKERS) as ex:
        for b in ex.map(_block, items):
            done.setdefault((b["axis"], b["arm"]), []).append(b)
            print(f"  {b['arm']} {b['axis']:g} block {b['block']}: "
                  f"{b['seconds'] / 60:.1f} min", flush=True)
    out = []
    for key in sorted(done, key=lambda k: (k[1], k[0])):
        out.extend(_summarise(done[key]))
    dest = C.RESULTS_DIR / "observable_taxonomy.csv"
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for r in sorted(out, key=lambda r: (r["arm"], r["axis"], r["window_ratio"])):
            w.writerow({k: r[k] for k in COLUMNS})
    print(f"wrote {dest} with {len(out)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

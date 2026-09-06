"""The three-channel forecast: what buys the light-shift measurement back, on
the twin, one campaign lever at a time.

THE QUESTION (owner, 2026-09-06). Show that a higher power, a higher
temperature, a tighter waist, a better retro ratio, another oscilloscope, or
the EOM's RF drive at a different spacing and depth makes the coefficient
measurable; account for the repaired lock; and give three results per
configuration: the higher moments alone (the novelty), the peak shift (the
standard channel the fixed lock opens), and the two combined.

THE DESIGN. A base point and one lever varied at a time. The base
point's trace is the RF-off science trace of the 2025 design (the carrier
alone), and the EOM comb is a lever at four spacings and two depths, because
with the 12.5 MHz comb on a 16 um trace both channels die (BASE below). Every
cell is the campaign's five-rung power ladder with a drawn rung order and every
physics layer of the world builder on, replicated over N trace sets. Per cell:

  skew   k3 per rung through rb5s6s.cumulants (converged, pedestal removed,
         the window started at the carrier), inverted through the noiseless
         quiet curve's LOCAL power exponent at the rungs admitted on two
         statistics (wrong-sign fraction below 0.35, median beyond three
         standard errors); the exponent fitted free as a diagnostic; k5 and
         k7 beside it with their wrong-sign fractions and the quiet ratios'
         power slopes, so their readmission is measured
  pull   the fitted centre per rung -> a line in power with the drift as a
         nuisance in acquisition order; kappa = -(3/2) slope
  both   the two kappas' covariance over the same trace sets and the
         inverse-variance combination with it

The uncertainty of every estimate is the SCATTER across trace sets and never a
fitter covariance. The EOM comb is pure phase modulation: teeth at k f_mod on
the transition axis with heights J_k(2 beta)^2, each the same line carrying the
same ramp; residual amplitude modulation is not modelled because the owner
states the new drive has none and the record has no measured term.

    RB5S6S_WORKERS=8 python scripts/run_three_channel_forecast.py
    python scripts/run_three_channel_forecast.py --one-cell      # timing
    python scripts/run_three_channel_forecast.py --plant         # 1 vs 8
"""
from __future__ import annotations

import csv
import math
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s import density as D                                    # noqa: E402
from rb5s6s.forecast import build_world_trace                      # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz                    # noqa: E402
from rb5s6s.linefit import fit_condition                           # noqa: E402
from rb5s6s.qc import median_standard_error                        # noqa: E402
from rb5s6s.cumulants import windowed_cumulants                     # noqa: E402
from rb5s6s.ruler import bessel_tooth_weights                      # noqa: E402
from rb5s6s.amplitudes import predicted_shares                     # noqa: E402

OUT = C.RESULTS_DIR / "three_channel_forecast.csv"

# ------------------------------------------------------------------ the base point
PEAK = "4192"
POWERS_W = (0.025, 0.075, 0.125, 0.175, 0.225)     # the campaign's ladder (scenario file)
# The base point's trace is the RF-OFF science trace of the 2025 design (the
# carrier alone, the ruler taken separately). With the 12.5 MHz comb on the
# trace at a 16 um waist both channels die: the self-centred window follows a
# carrier pulled 3.9 MHz toward the -1 tooth and that tooth's tail leaks into
# it asymmetrically: measured 2026-09-06 with the cumulant window started at
# the trace's maximum, which at the measured depth is a first-order tooth,
# the skew read the wrong sign in most sets; with the window started at the
# carrier it admits no rung at that spacing, and the pull reads -53 +- 44
# against an injected 25.9 either way. The comb is therefore a design variable, measured against the RF-off base
# at four spacings and two depths, and not the base itself.
BASE = dict(w0_um=16.0, p_top=0.225, t_c=130.0, rho=0.94, scope=("rtm3004", "hires", 16.0),
            drift_per_min=0.004, f_mod=None, two_beta=None, window=6.0)
# The record's collisional width at 130 C and the committed self-broadening
# slope carry the width to other temperatures: gamma(T) = gamma(130) +
# beta_self (N(T) - N(130)), beta_self the 4192 row of results/beta_self.csv.
GAMMA_COLL_130 = 0.55
SIGMA_LASER = 1.6
MIN_PER_TRACE = 2.78                               # campaign_twin_forecast, per trace
LAYERS = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
          "drift": True, "quantise": True, "randomise": True}
NOISE = 0.004
# A carrier-only cell costs about a minute at 400 trace sets and a seven-tooth
# comb cell about eleven (642 s measured 2026-09-06), so the 21 cells take
# under ten minutes on eight workers; the scatter of kappa over 400 sets fixes its own standard
# error to about four per cent, which is what the combination's gain needs.
N_SETS = int(os.environ.get("RB5S6S_TCF_SETS", "400"))


def _beta_self() -> float:
    with open(C.RESULTS_DIR / "beta_self.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["peak"] == PEAK:
                return float(r["beta_self"])
    raise SystemExit("no 4192 row in results/beta_self.csv")


def _two_beta_default() -> float:
    """The measured modulation depth from the one place it lives. No fallback:
    at a made-up depth the first-order teeth's height against the carrier's
    inverts (J_1^2 exceeds J_0^2 at the measured 2 beta and not at 1.2), and the
    window rule that starts at the carrier would then be justified by a
    number nobody measured."""
    for mod in (C, K):
        if hasattr(mod, "RULER_MOD_DEPTH_2BETA"):
            return float(getattr(mod, "RULER_MOD_DEPTH_2BETA"))
    raise RuntimeError("RULER_MOD_DEPTH_2BETA is not in rb5s6s.config or rb5s6s.constants; "
                       "the comb's depth is a measured seam value and this producer refuses to guess it")


# ------------------------------------------------------------------ the levers
def levers():
    """The cells, each carrying EVERY seam value it needs in its own
    configuration, because a worker started by spawn re-imports this file and
    never sees a value the parent set on the module (the first form set them
    with `global` in main, and every pooled trace was built at the module's
    placeholder depth while the file was labelled with the parent's)."""
    beta_self = _beta_self(); two_beta = _two_beta_default()
    def fill(cfg):
        return {**cfg, "beta_self": beta_self,
                "two_beta": cfg["two_beta"] if cfg["two_beta"] is not None else two_beta}
    cells = [("base", fill(BASE))]
    for w in (64.0, 40.0, 24.0):
        cells.append((f"waist_{w:g}um", fill({**BASE, "w0_um": w})))
    cells.append(("power_top_0.5W", fill({**BASE, "p_top": 0.5})))
    for t in (150.0, 170.0):
        cells.append((f"temperature_{t:g}C", fill({**BASE, "t_c": t})))
    for r in (0.5, 1.0):
        cells.append((f"retro_{r:g}", fill({**BASE, "rho": r})))
    cells.append(("scope_lecroy_raw8", fill({**BASE, "scope": ("lecroy_ws3104z", "raw", 8.0)})))
    cells.append(("scope_agilent_hires12", fill({**BASE, "scope": ("agilent_3054a", "hires", 12.0)})))
    for d in (0.0, 0.04):
        cells.append((f"lock_{d:g}MHz_per_min", fill({**BASE, "drift_per_min": d})))
    for f in (8.0, 12.5, 25.0, 40.0):
        cells.append((f"eom_comb_{f:g}MHz", fill({**BASE, "f_mod": f})))
    # the depth cells need a comb, so they sit on the 2025 spacing and change
    # two keys from the base, which their names say
    cells.append(("eom_comb_12.5MHz_depth_2.405_carrier_suppressed", fill({**BASE, "f_mod": 12.5, "two_beta": 2.405})))
    cells.append(("eom_comb_12.5MHz_depth_0.6", fill({**BASE, "f_mod": 12.5, "two_beta": 0.6})))
    for w in (3.25, 8.0):
        cells.append((f"window_{w:g}MHz", fill({**BASE, "window": w})))
    return cells


# ------------------------------------------------------------------ the trace
def _comb(f_mod, two_beta: float):
    """Positions and shares of the two-photon comb about the carrier, and the
    map from each tooth to its physical peak. ``f_mod`` None is the RF-off
    science trace of the 2025 design: the carrier alone."""
    base_share = predicted_shares()[PEAK]
    if f_mod is None:
        return {PEAK: 0.0}, {PEAK: base_share}, {PEAK: PEAK}
    slots = (-3, -2, -1, 0, 1, 2, 3)
    w = bessel_tooth_weights(two_beta, slots)
    positions, shares, tooth_of = {}, {}, {}
    for k, wk in zip(slots, w):
        key = PEAK if k == 0 else f"{PEAK}@{k:+d}"
        positions[key] = k * f_mod
        shares[key] = base_share * float(wk)
        tooth_of[key] = PEAK
    return positions, shares, tooth_of


def _trace(cfg: dict, power_w: float, order_idx: int, seed: int, noise: float = NOISE):
    w0 = cfg["w0_um"] * 1e-6
    kappa = stark_shift_S0_mhz(1.0, w0, rho=cfg["rho"])          # MHz per W at this waist and retro
    gamma = GAMMA_COLL_130 + cfg["beta_self"] * (D.density_units(cfg["t_c"]) - D.density_units(130.0))
    transit = K.transit_fwhm_from_w0(w0, cfg["t_c"])
    powers = tuple(p * cfg["p_top"] / 0.225 for p in POWERS_W)
    positions, shares, tooth_of = _comb(cfg["f_mod"], cfg["two_beta"])
    drift_total = cfg["drift_per_min"] * MIN_PER_TRACE * len(powers)
    nu, v, _ = build_world_trace(
        power_w, kappa, cfg["t_c"], order_idx, len(powers), np.random.default_rng(seed), LAYERS,
        positions=positions, shares=shares, gamma_coll=gamma, sigma_laser_fwhm=SIGMA_LASER,
        transit_fwhm=transit, power_max_w=max(powers), cycles_at_max=1.0,
        drift_mhz_total=drift_total, noise_frac_bright=noise,
        adc_levels=int(round(2.0 ** cfg["scope"][2])), resolve_shift=True, tooth_of=tooth_of,
        grid_span=(None if cfg["f_mod"] is None else (-(3.0 * cfg["f_mod"] + 60.0), 3.0 * cfg["f_mod"] + 60.0)))
    return nu, v, kappa, gamma, transit


def _trace_quiet(cfg: dict, power_w: float):
    """The same configuration with noise off, the drift off and the ADC deep,
    for calibrating the estimator's constant; every physical layer stays on."""
    quiet = {**cfg, "drift_per_min": 0.0, "scope": ("calibration", "noiseless", 30.0)}
    return _trace(quiet, power_w, 0, 12345, noise=1e-9)


def _k357(y, w, grid, centre0=0.0, baseline="wings"):
    """The third, fifth and seventh windowed cumulants from one centring, NaN
    when unconverged. The background is the level of the trace's far wings
    for every cell. A straight line through strips between the carrier and its
    first teeth was tried for the wide combs and made things worse (exponent
    2.0 at 40 MHz and 1.2 at 25 against the carrier-only 2.93), because at 12
    to 16 MHz from the carrier the strips sit on the carrier's own tails,
    which the ramp makes asymmetric. The tilt the teeth leave is identical in
    the quiet trace, so the inversion below calibrates it out where the ramp
    still dominates. The fifth and seventh are recorded so their readmission
    as channels is measured on this ladder (plan 4c struck them on one point):
    the fraction of sets returning the sign opposite to the quiet curve's, and
    the quiet ratios k5/k3 and k7/k5, which carry no shift if 4c is right.
    The window STARTS AT THE CARRIER (position zero in the twin's frame, the
    line the ruler identifies), never at the trace's maximum: at the measured
    modulation depth the first-order teeth stand higher than the carrier
    (J_1^2 = 0.32 against J_0^2 = 0.22), so a window started at the maximum
    sits on a tooth and reads the wrong line."""
    v, info = windowed_cumulants(grid, y, w, (3, 5, 7), centre0=centre0, baseline=baseline)
    if not info["converged"]:
        return float("nan"), float("nan"), float("nan")
    return v[3], v[5], v[7]


def _centre(nu, y, cfg, transit):
    """The standard channel: the archive's own single-line fit of the carrier,
    s0 = 0, so the ramp's pull lands in the fitted centre. The window stops
    short of the first tooth's centre and keeps its tail, which is the overlap
    the EOM spacing variation is meant to measure: at 12.5 MHz the window is 5.75,
    at 8 MHz it is 3.5, at 25 and 40 MHz it is capped at 12."""
    half = 12.0 if cfg["f_mod"] is None else min(0.5 * cfg["f_mod"] - 0.5, 12.0)
    # the window follows the line: at a tight waist the pull moves the peak by
    # more than the window's half-width, so a window fixed at zero would fit
    # the line's edge. The peak is the smoothed maximum inside the carrier's
    # own region, well clear of the first tooth.
    core = np.abs(nu) < (12.0 if cfg["f_mod"] is None else min(0.5 * cfg["f_mod"], 12.0))
    sm = np.convolve(y[core], np.ones(15) / 15.0, mode="same")
    peak = float(nu[core][int(np.argmax(sm))])
    m = np.abs(nu - peak) < half
    res = fit_condition([nu[m] - peak], [y[m]], T_C=cfg["t_c"], transit_fwhm=transit)
    return float(res["centers"][0]) + peak, float(res["gamma_coll"]), float(res["sigma_laser"])


# ------------------------------------------------------------------ one cell
def admit_rungs(k3_sets, frac_neg_max: float = 0.35, sigma_min: float = 3.0):
    """Which rungs of a ladder the skew channel may invert, from the sets'
    third cumulants (sets by rungs). Two independent statistics, both needed:
    the fraction of sets returning a negative value below `frac_neg_max`, and
    the median beyond `sigma_min` of its own standard error. The first alone
    admitted a coin-flip rung by chance at eight sets (two of eight negative)
    and inverted its noise into a coefficient 230 times the injected one.
    The null both bars are read against: under a coin flip the fraction's
    standard deviation is 0.5 over the root of the number of sets, so at 400
    sets a fraction below 0.35 is six standard deviations from one half and at
    eight sets it happens once in seven, which is why the second bar exists.
    Returns the mask and the fraction negative per rung."""
    k3_sets = np.asarray(k3_sets, dtype=float)
    # over the FINITE values of each rung, the same population the median and
    # its standard error use; a NaN is neither negative nor a measurement
    frac_neg = np.array([float(np.mean(c[np.isfinite(c)] < 0)) if np.isfinite(c).any() else float("nan")
                         for c in k3_sets.T])
    med = np.nanmedian(k3_sets, axis=0)
    sem = np.array([median_standard_error(col[np.isfinite(col)]) for col in k3_sets.T])
    with np.errstate(invalid="ignore", divide="ignore"):
        usable = (frac_neg < frac_neg_max) & (np.abs(med) > sigma_min * sem)
    return usable, frac_neg


def _cell(item):
    name, cfg = item
    base = zlib.crc32(f"tcf:{name}".encode()) % (2 ** 31)
    powers = tuple(p * cfg["p_top"] / 0.225 for p in POWERS_W)
    kappa_true = None
    k3_sets, c_sets, k2_sets, o_sets = [], [], [], []
    k5_sets, k7_sets = [], []
    for s in range(N_SETS):
        rng = np.random.default_rng((base + 7919 * s) % (2 ** 31))
        order = rng.permutation(len(powers))
        k3r, cr, k2r = np.zeros(len(powers)), np.zeros(len(powers)), np.zeros(len(powers))
        k5r, k7r = np.zeros(len(powers)), np.zeros(len(powers))
        for idx, rung in enumerate(order):
            seed = (base + 7919 * s + 104729 * int(rung) + 31) % (2 ** 31)
            nu, y, kappa_true, gamma, transit = _trace(cfg, powers[rung], idx, seed)
            k3r[rung], k5r[rung], k7r[rung] = _k357(y, cfg["window"], nu)
            c, gc, sl = _centre(nu, y, cfg, transit)
            cr[rung] = c
            k2r[rung] = gc
        pos = np.empty(len(powers)); pos[order] = np.arange(len(powers))   # acquisition index of each rung
        k3_sets.append(k3r); c_sets.append(cr); k2_sets.append(k2r); o_sets.append(pos)
        k5_sets.append(k5r); k7_sets.append(k7r)
    k3_sets, c_sets, k2_sets = np.asarray(k3_sets), np.asarray(c_sets), np.asarray(k2_sets)
    k5_sets, k7_sets = np.asarray(k5_sets), np.asarray(k7_sets)
    P = np.asarray(powers); lp = np.log(P)
    # ---- the windowed estimator's own response, per RUNG, from one noiseless
    # trace at each power with every physical layer on: k3_quiet(P). The
    # windowed k3 is cubic in the shift only while the shift is small against
    # the line, and a 16 um top rung is not, so a single constant cannot serve
    # the ladder; the estimate inverts each usable rung through the quiet curve
    # and the exponent fitted free is reported as a diagnostic, never imposed.
    quiet = np.array([_k357(*(lambda r: (r[1], cfg["window"], r[0]))(_trace_quiet(dict(cfg), pw))) for pw in powers])
    k3_quiet, k5_quiet, k7_quiet = quiet[:, 0], quiet[:, 1], quiet[:, 2]
    # the higher orders' readmission statistics: the fraction of sets whose top
    # rung carries the sign opposite to the quiet curve's, and the quiet
    # ratios' response to power along the ladder (a log-log slope near zero is
    # the shift-free ratio 4c predicts; near three is a ratio still carrying it)
    def wrong_sign(sets, q):
        top = sets[:, -1]; top = top[np.isfinite(top)]
        return float(np.mean(np.sign(top) != np.sign(q[-1]))) if top.size and q[-1] != 0 else float("nan")
    frac_wrong_k5, frac_wrong_k7 = wrong_sign(k5_sets, k5_quiet), wrong_sign(k7_sets, k7_quiet)
    def ratio_slope(a, b):
        with np.errstate(invalid="ignore", divide="ignore"):
            r = np.log(np.abs(a / b))
        ok = np.isfinite(r)
        return float(np.polyfit(lp[ok], r[ok], 1)[0]) if ok.sum() >= 3 else float("nan")
    slope_53, slope_75 = ratio_slope(k5_quiet, k3_quiet), ratio_slope(k7_quiet, k5_quiet)
    # the quiet curve's LOCAL exponent at each rung, d ln k3 / d ln P by finite
    # difference: three in the small-shift regime, less where the window
    # truncates a large shift, and it is this exponent, not an imposed three,
    # that inverts an observation into a coefficient
    lq = np.log(np.abs(k3_quiet)); n_loc = np.gradient(lq, lp)
    expo_quiet = float(np.polyfit(lp, lq, 1)[0]) if np.all(np.isfinite(lq)) else float("nan")
    def invert(k3_obs, i):
        if (not np.isfinite(k3_obs) or k3_quiet[i] == 0 or np.sign(k3_obs) != np.sign(k3_quiet[i])
                or not np.isfinite(n_loc[i]) or abs(n_loc[i] - 3.0) > 1.0):
            return np.nan
        return kappa_true * (k3_obs / k3_quiet[i]) ** (1.0 / n_loc[i])
    # ---- skew channel, per trace set: the mean over the rungs whose sign is
    # settled across the sets (fraction negative below 0.35) AND whose median
    # stands three of its own standard errors from zero. The first alone
    # admitted a coin-flip rung by chance at eight sets (two of eight negative)
    # and inverted its noise into a coefficient 230 times the injected one;
    # the two statistics are independent and both are needed
    usable, frac_neg_rung = admit_rungs(k3_sets)
    kap_skew, expo = [], []
    for row in k3_sets:
        ok = np.isfinite(row) & (row != 0)
        if ok.sum() >= 3:
            expo.append(float(np.polyfit(lp[ok], np.log(np.abs(row[ok])), 1)[0]))
        else:
            expo.append(np.nan)
        est = [invert(row[i], i) for i in range(len(powers)) if usable[i] and np.isfinite(row[i])]
        est = [e for e in est if np.isfinite(e)]
        kap_skew.append(float(np.mean(est)) if est else np.nan)
    kap_skew = np.asarray(kap_skew); expo = np.asarray(expo)
    # THE POOLED FORM, which is how a campaign reads the channel: the median
    # k3 over all sets at each rung, whose standard error falls as one over
    # the root of the trace count, inverted once through the quiet curve at
    # the admitted rungs, with the delta-method spread. The per-set form above
    # asks each single trace to carry the sign; this form asks the trace
    # count to, and it is the form in which the count is a lever.
    pooled = []
    for i in range(len(powers)):
        col = k3_sets[:, i]; col = col[np.isfinite(col)]
        if col.size < 3:
            continue
        med = float(np.median(col)); se = median_standard_error(col)
        if not usable[i] or se <= 0 or not np.isfinite(n_loc[i]) or abs(n_loc[i] - 3.0) > 1.0:
            continue
        est = invert(med, i)
        if np.isfinite(est):
            pooled.append((est, est * (se / abs(med)) / n_loc[i]))
    if pooled:
        w_p = np.array([1.0 / s ** 2 for _, s in pooled]); e_p = np.array([e for e, _ in pooled])
        kap_pooled = float(np.sum(w_p * e_p) / np.sum(w_p)); sd_pooled = float(1.0 / np.sqrt(np.sum(w_p)))
    else:
        kap_pooled, sd_pooled = float("nan"), float("nan")
    # ---- pull channel: centre against power with the drift as a nuisance in order
    kap_pull = []
    for row, pos in zip(c_sets, o_sets):
        # centre = c0 - (2/3) kappa P + d * (acquisition index): the lock's
        # residual drift is linear in ORDER, and the drawn order is what makes
        # it separable from the pull, which is linear in POWER
        A = np.column_stack([np.ones_like(P), P, pos])
        coef = np.linalg.lstsq(A, row, rcond=None)[0]
        kap_pull.append(-1.5 * coef[1])
    kap_pull = np.asarray(kap_pull)
    frac_neg = float(frac_neg_rung[-1])
    def sig(a):
        # THE SPREAD IS ONE CONSTRUCTION FOR EVERY CHANNEL: the standard
        # deviation of the per-set estimates (ddof 1), the statistic the
        # covariance below uses, so the combined spread is comparable with the
        # single channels' and the gain cannot be inflated by a mismatched
        # denominator. The first form scaled the median's standard error back
        # by root n, 1.2533 times this, against a covariance that was not, and
        # every gain would have read 1.25 where nothing was gained.
        a = a[np.isfinite(a)]
        return (float(np.median(a)), float(np.std(a, ddof=1))) if a.size > 1 else (np.nan, np.nan)
    ks_med, ks_sd = sig(kap_skew); kp_med, kp_sd = sig(kap_pull)
    both = np.isfinite(kap_skew) & np.isfinite(kap_pull)
    if both.sum() > 2:
        cov = np.cov(kap_skew[both], kap_pull[both])
        v1, v2, c12 = cov[0, 0], cov[1, 1], cov[0, 1]
        w1 = (v2 - c12) / (v1 + v2 - 2 * c12) if (v1 + v2 - 2 * c12) > 0 else 0.5
        var_c = w1 ** 2 * v1 + (1 - w1) ** 2 * v2 + 2 * w1 * (1 - w1) * c12
        sd_comb = math.sqrt(max(var_c, 0.0)); corr = c12 / math.sqrt(v1 * v2) if v1 > 0 and v2 > 0 else float("nan")
    else:
        sd_comb, corr, w1 = float("nan"), float("nan"), float("nan")
    return dict(name=name, cfg=cfg, kappa_true=kappa_true, n_sets=N_SETS,
                kappa_skew=ks_med, sd_skew=ks_sd, expo=float(np.nanmedian(expo)),
                expo_sd=float(np.nanstd(expo)), expo_quiet=expo_quiet, frac_neg_top=frac_neg,
                frac_wrong_k5_top=frac_wrong_k5, frac_wrong_k7_top=frac_wrong_k7,
                slope_k5_over_k3=slope_53, slope_k7_over_k5=slope_75,
                kappa_pull=kp_med, sd_pull=kp_sd, corr=corr, w_skew=w1, sd_comb=sd_comb,
                kappa_skew_pooled=kap_pooled, sd_skew_pooled=sd_pooled,
                k2_top=float(np.median(k2_sets[:, -1])))


def main() -> int:
    known = {"--one-cell", "--plant"}
    bad = [a for a in sys.argv[1:] if a.startswith("-") and a not in known and not a.startswith("--tag=")]
    if bad:
        raise SystemExit(f"unknown flag(s) {bad}: the flags are --one-cell and --plant")
    workers = max(1, min(8, int(os.environ.get("RB5S6S_WORKERS", "8"))))
    cells = levers()
    if "--one-cell" in sys.argv:
        import time
        t0 = time.time(); r = _cell(cells[0]); dt = time.time() - t0
        print(f"one cell: {dt:.1f} s at {N_SETS} sets -> {len(cells)} cells, about {len(cells) * dt / 60 / workers:.0f} min at {workers} workers")
        print(f"  base: kappa true {r['kappa_true']:.3f}; skew {r['kappa_skew']:.3f} +- {r['sd_skew']:.3f} (expo {r['expo']:+.2f}, quiet {r['expo_quiet']:+.2f}, frac neg top {r['frac_neg_top']:.2f}); "
              f"pull {r['kappa_pull']:.3f} +- {r['sd_pull']:.3f}; combined sd {r['sd_comb']:.3f}, corr {r['corr']:+.2f}")
        return 0
    if "--plant" in sys.argv:
        os.environ["RB5S6S_TCF_SETS"] = "4"
        sub = cells[:3]
        def run(nw):
            with ProcessPoolExecutor(max_workers=nw) as ex:
                return list(ex.map(_cell, sub))
        ok = repr(run(1)) == repr(run(8))
        print(f"  determinism plant: 1 worker against 8 over {len(sub)} cells: {'BYTE-EQUAL' if ok else 'DIFFERENT'}")
        return 0 if ok else 1
    lock = Path("/tmp/rb5s6s_three_channel.lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise SystemExit("three-channel forecast already running; refuse")
    try:
        print(f"  {len(cells)} cells on {workers} workers", flush=True)
        with ProcessPoolExecutor(max_workers=workers) as ex:
            rows = []
            for i, r in enumerate(ex.map(_cell, cells), 1):
                rows.append(r); print(f"    {i}/{len(cells)} {r['name']}", flush=True)
    finally:
        lock.rmdir()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["lever", "w0_um", "p_top_w", "t_c", "rho", "scope", "lock_mhz_per_min", "f_mod_mhz", "two_beta", "window_mhz",
                    "n_sets", "kappa_true", "kappa_skew", "sd_skew", "exponent_free", "exponent_sd", "exponent_quiet", "frac_neg_top",
                    "frac_wrong_sign_k5_top", "frac_wrong_sign_k7_top", "quiet_slope_k5_over_k3", "quiet_slope_k7_over_k5",
                    "kappa_pull", "sd_pull", "corr", "w_skew", "sd_combined", "gain",
                    "kappa_skew_pooled", "sd_skew_pooled", "gamma_coll_top", "status", "note"])
        for r in rows:
            c = r["cfg"]; best = np.nanmin([r["sd_skew"], r["sd_pull"]])
            gain = best / r["sd_comb"] if np.isfinite(r["sd_comb"]) and r["sd_comb"] > 0 else float("nan")
            skew_read = np.isfinite(r["kappa_skew"])
            status = "DIAGNOSTIC" if np.isfinite(r["sd_pull"]) else "NULL"
            w.writerow([r["name"], f"{c['w0_um']:g}", f"{c['p_top']:g}", f"{c['t_c']:g}", f"{c['rho']:g}", f"{c['scope'][0]}/{c['scope'][1]}",
                        f"{c['drift_per_min']:g}", ("off" if c['f_mod'] is None else f"{c['f_mod']:g}"), f"{c['two_beta']:g}", f"{c['window']:g}",
                        r["n_sets"], f"{r['kappa_true']:.4f}", f"{r['kappa_skew']:.4f}", f"{r['sd_skew']:.4f}", f"{r['expo']:.3f}", f"{r['expo_sd']:.3f}", f"{r['expo_quiet']:.3f}",
                        f"{r['frac_neg_top']:.3f}",
                        f"{r['frac_wrong_k5_top']:.3f}", f"{r['frac_wrong_k7_top']:.3f}", f"{r['slope_k5_over_k3']:+.3f}", f"{r['slope_k7_over_k5']:+.3f}", f"{r['kappa_pull']:.4f}", f"{r['sd_pull']:.4f}", f"{r['corr']:.3f}", f"{r['w_skew']:.3f}",
                        f"{r['sd_comb']:.4f}", f"{gain:.3f}", f"{r['kappa_skew_pooled']:.4f}", f"{r['sd_skew_pooled']:.4f}",
                        f"{r['k2_top']:.4f}", status,
                        "one campaign lever varied from the base point, the injected coefficient in kappa_true (MHz per W at this "
                        "waist and retro ratio). kappa_skew is the third cumulant inverted through the noiseless quiet curve's local "
                        "exponent at the rungs admitted on two statistics (fraction of sets with the wrong sign below 0.35 and median "
                        f"beyond three standard errors), {'read' if skew_read else 'NaN because no rung was admitted'}. kappa_pull is the "
                        "fitted centre against power with the lock drift as a nuisance in acquisition order. Every sd is the scatter over "
                        "trace sets and gain is the better single channel's sd over the combined sd with the measured correlation. "
                        "kappa_skew_pooled inverts the median cumulant over all sets at the admitted rungs, the campaign's own "
                        "form, whose spread falls with the trace count. The "
                        "fringe-resolved standing-wave suppression of the small-waist skew (rb5s6s.fringe_tail) is not in the world "
                        "builder, so the skew channel at the tightest waists is an upper bound on what the campaign reads"])
    print(f"wrote {OUT} with {len(rows)} rows")
    return 0



if __name__ == "__main__":
    raise SystemExit(main())

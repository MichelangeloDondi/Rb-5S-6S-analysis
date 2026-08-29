#!/usr/bin/env python3
"""
M4: collisional self-broadening beta_self + the confound program.

For each peak, fit beta_self globally across the density lever with
gamma_coll(T) = beta_self * N(T) and a shared sigma_laser (rb5s6s.beta).
Then run the pre-registered confound probes and apply the
measurement-vs-bound rule.

HEADLINE CONSTRUCTION (2026-08-02, decided by Michelangelo on firsthand
apparatus authority). The beta_self headline is now the FOUR-POINT
construction: 70/90/110/130 C, dof=2, the x52.5 density lever (N(130)/N(70)),
built from the T-sweep (70/90/110 C) plus the 130 C power-sweep session's
225 mW block. There is no separate three-point (70/90/110 C, dof=1, x16.2
lever) headline kept alongside it; that construction is replaced, not
demoted to a robustness row -- one licensed construction, one bound, per
peak. The prior version of this module (and of docs/DATA.md, README.md and
the ledger) treated 130 C as an optional extra lever point excluded from the
headline because it looked like a different apparatus configuration (a power
sweep, not a temperature sweep, calibrated off before/after EOM ruler
brackets rather than the T-session's own per-block ruler). That exclusion
reasoning does not survive Michelangelo's firsthand statement: the 130 C
power-sweep session ran in the SAME optical/cell configuration as the
70/90/110 C temperature sweep (same beam path, same cell, same detection
chain). What actually differs between the two sessions is the acquisition
epoch and the axis calibration, and the calibration difference is already
handled PER SESSION -- load_t_rates() derives the T-sweep rate from the
T-session's own per-block ruler and the P-sweep rate from the P-session's
before/after bracket combination, so folding the 130 C point into one shared
density axis carries no unhandled calibration mismatch. See
# term-of-art: the private reviews directory is a filesystem path
private/reviews/digest/fig19_trend_audit.md for the prior "different
configuration" reading this decision overrides, and docs/DATA.md's clock
entry for the timing (130 C sits 2.3 h from the 110 C dwell, inside the same
continuous campaign). The remaining caveat is not a configuration break, it
is that 130 C is the extreme end of the density lever, so the fit still
leans on a short arm relative to a purpose-built session.

THE CONFOUND (docs/PLAN.md M4): temperature is monotonic with time across the
campaign, so a slow instrument drift can mimic collisional broadening. Probes
that bound the drift contribution:
  (P1) P-session line widths vs block order at FIXED 130 C (the ramp predicts
       a <=2% width effect) -- a drift monitor. NOTE (2026-07-23): block
       order is ASCENDING POWER, and the recovered timestamps show the
       session ran DESCENDING, so this axis is reversed in time. The probe
       is direction-agnostic (it asks whether width varies across the
       session at fixed T, not which way), so the bound is unaffected --
       but do not read the sign of any trend here as a drift direction.
  (P2) before/after ruler tooth-width change per peak -- fixed-condition
       instrument drift over each peak's session.
  (P3) cross-peak gamma_coll consistency at fixed T -- four lines see ONE
       density; disagreement beyond errors flags a per-peak systematic.
  (P4) sigma_laser stability (the global fit's shared laser width, and its
       covariance with beta) -- if the "collisional" trend is really laser
       drift, sigma_laser absorbs it.

PRE-REGISTERED RULE: report beta_self as a MEASUREMENT only if the probes
bound the drift contribution to <= ~1/3 of the observed gamma_coll(T) trend;
otherwise report a BOUND. Absolute value remains PRELIMINARY until the w0
knife-edge fixes the transit prior.

Outputs: results/beta_self.csv + results/beta_self_probe.csv + stdout report.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
import pathlib
from pathlib import Path

import numpy as np
from scipy.stats import t as student_t

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _producer_lock import take_producer_lock     # noqa: E402
from rb5s6s import config as C
from rb5s6s import rate_model as RM
from rb5s6s import constants as _CONST  # noqa: E402
from rb5s6s.density import density_units, N_SCALE_FRAC_SYST  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import (trace_metrics, hard_flags, ingest_flags,  # noqa: E402
                       outlier_files)
from rb5s6s.ruler import campaign_rate_relsyst  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.beta import fit_beta_self, collisional_slope  # noqa: E402
from rb5s6s.qc import contiguous_fwhm_ms  # noqa: E402

PEAKS = ("4121", "4154", "4192", "4207")
TSWEEP = ("70", "90", "110")


def raw_fwhm_mhz(recs, rate, rate_relerr=0.0):
    """Model-INDEPENDENT line FWHM per condition: smoothed half-max width (ms)
    x the verified per-block rate. No lineshape model, no laser/coll split —
    the cleanest probe of whether the width actually rises monotonically with
    density (collisional broadening must).

    The returned error combines the repeat scatter (within-block, incoherent)
    with the block's ruler-rate uncertainty (block-coherent: it scales every
    width in the block together): E = sqrt(sem^2 + (W * rate_relerr)^2)."""
    ws = []
    for r in recs:
        t, v = load_trace(trace_path(r))
        # Raw half-maximum width, DELIBERATELY model-independent: a bound
        # argued from raw widths inherits none of the lineshape model's
        # assumptions. It carries a known SNR bias (narrow at low SNR,
        # ~6% at the 70 C end) which EXAGGERATES the climb with density --
        # i.e. it pushes against this module's own conclusion, so the bound
        # is conservative w.r.t. it. Postscript to addendum 17.
        ws.append(contiguous_fwhm_ms(t, v) * rate)   # retrace-safe (shared helper)
    W = float(np.mean(ws))
    sem = float(np.std(ws, ddof=1) / np.sqrt(len(ws)))
    return W, float(np.hypot(sem, W * rate_relerr))


def condition_widths(rows, peak, trates, prates, include_130=False):
    """One line's model-independent width per condition: (N, W, E) lists.

    Split out of width_vs_density_probe (2026-08-06) so the per-line probe and
    the pooled construction below read the SAME widths by construction rather
    than by two copies of the same selection agreeing. Nothing about the
    selection changed: canonical t_sweep traces at 70/90/110 C, each block on
    its own session rate, optionally extended by the 130 C point (the 225 mW
    power-session files, on the bracket-combination rate)."""
    byT = defaultdict(list)
    for r in rows:
        if (r["flag"] == "canonical" and r["role"] == "t_sweep"
                and r["peak"] == peak and r["temperature_C"] in TSWEEP):
            byT[r["temperature_C"]].append(r)
    N, W, E = [], [], []
    for T in TSWEEP:
        if T in byT and (peak, T) in trates:
            rate, relerr = trates[(peak, T)]
            m, e = raw_fwhm_mhz(byT[T], rate, relerr)
            N.append(density_units(float(T))); W.append(m); E.append(e)
    if include_130 and peak in prates:
        recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "p_sweep"
                and r["peak"] == peak and r["power_mW"] == "225"]
        if len(recs) >= 3:
            rate, relerr = prates[peak]
            m, e = raw_fwhm_mhz(recs, rate, relerr)
            N.append(density_units(130.0)); W.append(m); E.append(e)
    return N, W, E


def width_vs_density_probe(rows, peak, trates, prates, include_130=False):
    """P0 (decisive): fit raw FWHM(N) = W0 + beta_eff*N. The RMS residual
    about that line is the BETWEEN-BLOCK systematic (laser-width drift AND
    ruler-rate uncertainty, both block-coherent) — the error the global fit's
    shared-sigma_laser assumption omits. Optionally extends the lever arm with
    the 130 C point (the 225 mW power-session files): N(130)/N(110) ~ 3.2, at
    the quantify of reaching the extreme end of the lever, with a rate from the
    bracket combination (its before/after half-difference carried as
    uncertainty). Not a cross-session comparison: the recovered clock puts the
    130 C block 2.3 h from the 110 C dwell, inside one campaign."""
    N, W, E = condition_widths(rows, peak, trates, prates, include_130)
    if len(N) < 3:
        return None
    return collisional_slope(N, W, E)


def load_t_rates():
    """Per-block transition-axis rates WITH their relative errors, plus the
    P-session bracket combination per peak.

    Rate errors are BLOCK-COHERENT: a rate error scales every width in that
    block by the same factor, so it belongs in the between-block error budget
    (audit fix, 2026-07-11 — previously omitted; at 70 C the ruler is dim and
    its 1.2-1.8% rate error contributes 0.06-0.09 MHz, co-dominant with the
    laser-width drift we had blamed alone).

    Bracket combination: rate = mean(before, after); its error adds the
    half-difference in quadrature, so a genuine in-session rate shift (4207:
    1.4%) is carried as uncertainty instead of being averaged away.

    Since 2026-08-04 the campaign-level FRACTIONAL systematics of
    results/ruler_campaign.csv are folded on top, after the rate(t) overlay
    (ruler.campaign_rate_relsyst: how much of the rate is a choice among eight
    legitimate estimators of the same blocks, and the rulers and the lines
    sitting at different places in the acquisition window). Both scale every
    width in a block together, like everything else in this budget. The
    campaign STATISTICAL error is not folded, since the per-block statistical
    error above already is it."""
    path = C.RESULTS_DIR / "ruler_blocks.csv"
    trate, brackets = {}, defaultdict(dict)
    for r in csv.DictReader(open(path)):
        rr, ee = 2.0 * float(r["rate"]), 2.0 * float(r["rate_err"])
        if r["session"] == "T":
            trate[(r["peak"], r["T"])] = (rr, ee / rr)
        else:
            brackets[r["peak"]][r["bracket"]] = (rr, ee)
    prate = {}
    for peak, br in brackets.items():
        if "before" in br and "after" in br:
            (rb, eb), (ra, ea) = br["before"], br["after"]
            mean = 0.5 * (rb + ra)
            err = np.sqrt(0.5 * (eb ** 2 + ea ** 2) + (0.5 * (rb - ra)) ** 2)
            prate[peak] = (mean, err / mean)
    trate, prate = _apply_rate_models(trate, prate)
    syst = campaign_rate_relsyst()
    if syst > 0:
        for d in (trate, prate):
            for k, (rr, rel) in list(d.items()):
                d[k] = (rr, float(np.hypot(rel, syst)))
    return trate, prate


def _apply_rate_models(trate, prate):
    """Overlay the time-resolved rate(t) model where science times exist.

    The bracket/block scheme above stays the constructor and the FALLBACK:
    any (peak, T) or peak whose science-side clock or model is missing keeps
    its committed value unchanged (in production that is the 4154 70 C
    block, whose science traces have no recovered clock). Where the model
    applies, the rate is rate(t) evaluated at the block's mean science time
    and the error is the model's, PLUS - for the P session, whose consumers
    apply ONE rate to a whole drifting ladder - the rms spread of rate(t)
    across that peak's science-trace times, in quadrature. That keeps the
    ladder-drift systematic covered while the central error falls 3-5x.
    All numbers stay transition-axis (2x laser), like the fallback."""
    models = RM.read_models()
    if not models:
        return trate, prate
    clock = RM.load_clock()
    man = defaultdict(list)
    for r in csv.DictReader(open(C.MANIFEST_CSV)):
        if r["flag"] != "canonical":
            continue
        t = clock.get(pathlib.Path(r["file"]).name.lower())
        if t is not None:
            man[(r["role"], r["peak"], r["temperature_C"])].append(t)
    for (peak, T), _ in list(trate.items()):
        m = models.get(("T", peak))
        times = man.get(("t_sweep", peak, T))
        if not m or not times:
            continue
        span = m["t_max_epoch"] - m["t_min_epoch"]
        tc = float(np.mean(times))
        if not (m["t_min_epoch"] - 0.25 * span <= tc <= m["t_max_epoch"] + 0.25 * span):
            continue
        r, rel = RM.rate_at(m, tc)
        trate[(peak, T)] = (2.0 * r, rel)
    for peak in list(prate):
        m = models.get(("P", peak))
        times = man.get(("p_sweep", peak, "130"))
        if not m or not times:
            continue
        rates = np.array([RM.rate_at(m, t)[0] for t in times])
        rc, rel = RM.rate_at(m, float(np.mean(times)))
        rel = float(np.sqrt(rel ** 2 + np.var(rates) / rc ** 2))
        prate[peak] = (2.0 * rc, rel)
    return trate, prate


def _load_block_condition(recs, T_C, rate):
    """Shared per-block trace loader: QC-filter, convert to frequency, and
    build one beta.fit condition dict. Used for both the T-sweep dwells and
    the 130 C P-sweep 225 mW block (the headline's fourth point), so the two
    share exactly the same QC and windowing path."""
    freqs, volts = [], []
    for r in recs:
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate)); volts.append(v)
    if len(volts) < 3:
        return None
    law = condition_noise_model(volts)
    return {"T_C": float(T_C), "N_units": density_units(float(T_C)),
            "freqs": freqs, "volts": volts, "law": law}


def load_conditions(rows, peak, trates, prates=None):
    """Build the beta.fit condition list for one peak: the four-point
    headline (2026-08-02) is the 70/90/110 C T-sweep plus the 130 C P-sweep
    225 mW block, one shared density axis, each block calibrated by its own
    session's rate (see the module docstring). Pass prates=None to get the
    T-sweep-only (replaced) three-point list, e.g. for a diagnostic."""
    byT = defaultdict(list)
    for r in rows:
        if (r["flag"] == "canonical" and r["role"] == "t_sweep"
                and r["peak"] == peak and r["temperature_C"] in TSWEEP):
            byT[r["temperature_C"]].append(r)
    conds = []
    for T in TSWEEP:
        entry = trates.get((peak, T))
        if entry is None:
            continue
        cond = _load_block_condition(byT[T], T, entry[0])
        if cond is not None:
            conds.append(cond)
    if prates is not None and peak in prates:
        recs130 = [r for r in rows if r["flag"] == "canonical" and r["role"] == "p_sweep"
                   and r["peak"] == peak and r["power_mW"] == "225"]
        cond130 = _load_block_condition(recs130, 130.0, prates[peak][0])
        if cond130 is not None:
            conds.append(cond130)
    return conds


# ---------------------------------------------------------------------------
# POOLING THE WIDTH SLOPE ACROSS THE FOUR LINES
# ---------------------------------------------------------------------------
# Pre-registered in docs/notes/beta_self_pooling_prereg.md (2026-08-04), and
# implemented only afterwards, which is the order that note fixes. What it
# licenses, and what this code therefore assumes:
#
#   * ONE shared slope with per-line floors, decided by physics and not by fit
#     statistics (note section 1). The four 993 nm lines are hyperfine
#     components of one dipole-forbidden transition, there is no first-order
#     resonant exchange term of the D-line type, and the R^-6 physics that
#     remains is isotope-blind to three orders below this sensitivity.
#   * The per-isotope split and the per-line spread are CHECKS with an expected
#     null, never the fit structure (note section 1).
#   * The verdict is frozen at BOUND for this release whatever the pooled
#     signal-to-noise turns out to be (note section 3). Temperature is monotone
#     in time across the campaign and the four lines of one condition sit
#     within about an hour of each other, so a slow drift enters all four with
#     the same sign and pooling divides that term by exactly one. A verdict
#     flip bought that way would be noise dressed as physics.
#   * Scope (note section 4): this pools the model-independent width-slope
#     probe, results/beta_self_probe.csv. The per-line model fit in
#     results/beta_self.csv, which the M23 and M28 joint fits consume as a
#     fixed prior at fit time, is untouched by this release.
POOL_CONDITIONS_C = (70.0, 90.0, 110.0, 130.0)
POOLED_ANCHOR_C = 70.0        # the coldest, weakest-trace end of the lever
POOLED_VARIANT = ("70-130C pooled across the four lines (shared slope, "
                  "per-line floors, prereg beta_self_pooling)")


def pooled_width_table(rows, peaks, trates, prates):
    """The sixteen model-independent widths as a (line, condition) table.

    Returns (peaks_used, N, W, E) with W and E shaped (n_line, n_cond), or None
    when the design is not balanced. Balance is a precondition rather than a
    detail: the collapse identity below, and the variance-component algebra
    that rides on it, hold because every line is measured at every condition.
    An unbalanced table has to fall back to the per-line construction rather
    than be pooled with a formula that no longer describes it."""
    N_ref, W, E, used = None, [], [], []
    for peak in peaks:
        N, w, e = condition_widths(rows, peak, trates, prates, include_130=True)
        if len(N) != len(POOL_CONDITIONS_C):
            return None
        if N_ref is None:
            N_ref = N
        elif not np.allclose(N, N_ref):
            return None
        used.append(peak); W.append(w); E.append(e)
    if len(used) < 2:
        return None
    return used, np.asarray(N_ref, float), np.asarray(W, float), np.asarray(E, float)


def profile_f_range(ss_cond, df_cond, ss_int, df_int, n_line, dchi2=3.841):
    """The 95 per cent profile range of the common-mode fraction f.

    Four conditions cannot pin f (note section 2), so the bound quotes the REML
    point value and this range is printed beside it. Reparametrizing to (f,
    total) with total = s_c^2 + s_ind^2 and profiling the total out of the
    restricted deviance at each f leaves a one-parameter curve, and the range
    is where that curve sits within the house's one-parameter 95 per cent
    threshold of 3.841. f = 1 is excluded by construction: it sends the
    per-line component to zero, and the measured interaction scatter is not
    zero."""
    f = np.linspace(0.0, 1.0, 20001)[:-1]
    k1 = f + (1.0 - f) / n_line              # V as a fraction of the total
    k2 = 1.0 - f                             # s_ind^2 as a fraction of the total
    total = (ss_cond / k1 + ss_int / k2) / (df_cond + df_int)
    dev = (df_cond * np.log(k1 * total) + ss_cond / (k1 * total)
           + df_int * np.log(k2 * total) + ss_int / (k2 * total))
    inside = dev <= dev.min() + dchi2
    return float(f[inside].min()), float(f[inside].max())


def pooled_width_slope(N, W, E=None, n_frac_syst=N_SCALE_FRAC_SYST):
    """Pooled floor-plus-slope fit of a balanced (line, condition) width table.

    THE COLLAPSE. With per-line floors, one shared slope, and errors that are
    exchangeable across lines within a condition, the generalized-least-squares
    slope on the whole table is EXACTLY the floor-plus-slope fit of the
    condition-mean widths. The mean-over-lines directions carry the slope and
    nothing else, the contrast directions carry the per-line floors and nothing
    else, and under this error model the two sets are uncorrelated, so the
    slope reads off the means alone. tests/test_beta.py checks the identity
    numerically against an explicit GLS on the sixteen points.

    THE ERROR MODEL. Each width is a per-line floor plus the shared slope plus
    a condition-common departure (variance s_c^2, one draw per condition shared
    by all four lines) plus a per-line departure (variance s_ind^2). A
    condition mean therefore has variance

        V = s_c^2 + s_ind^2 / n_line

    and that is the only variance the pooled slope sees. s_ind^2 SUBSUMES the
    within-block repeat and rate errors rather than sitting on top of them: it
    is the total independent scatter of a line about the shared law, so the two
    are never added. The returned rms_within lets that be checked instead of
    assumed, since s_ind falling below the quoted within-block error would mean
    the table is quieter than its own error bars and the decomposition is not
    describing the data.

    REML. The design is balanced, so restricted maximum likelihood on the
    sixteen points is closed form. Rotating to the mean and contrast subspaces
    separates the restricted deviance into

        D = df_cond*log V + SS_cond/V + df_int*log s_ind^2 + SS_int/s_ind^2

    with SS_cond the residual sum of squares of the condition means about the
    fitted line (df_cond = n_cond - 2) and SS_int the two-way interaction sum
    of squares (df_int = (n_line-1)(n_cond-1)). Unconstrained this gives
    V = MS_cond and s_ind^2 = MS_int outright. Where the implied s_c^2 would go
    negative it is held at zero and the one remaining component is re-estimated
    from the constrained deviance.

    DEGREES OF FREEDOM. V is a linear combination g_cond*MS_cond +
    g_int*MS_int of two independent mean squares, so its effective dof is the
    Satterthwaite value V^2 / ((g_cond*MS_cond)^2/df_cond +
    (g_int*MS_int)^2/df_int). At the interior solution g = (1, 0) and dof_eff
    is exactly df_cond, the four condition means constraining a line, which is
    the same dof the per-line construction already quotes. At the boundary the
    per-line component carries the estimate and dof_eff rises toward df_int.
    The one-sided 95 per cent bound is t(0.95, dof_eff) on the pooled slope
    error, and the density-scale systematic rides on top of it exactly as it
    does per line (rb5s6s.beta.collisional_slope).

    The verdict is BOUND unconditionally, by note section 3."""
    N = np.asarray(N, float)
    W = np.asarray(W, float)
    n_line, n_cond = W.shape
    df_cond, df_int = n_cond - 2, (n_line - 1) * (n_cond - 1)
    if df_cond < 1 or df_int < 1:
        raise ValueError("pooled slope needs >= 3 conditions and >= 2 lines")

    # the condition means and the line they define. `lever` is the fixed linear
    # functional that turns those four means into the slope, and it is reused
    # below for the anchor-narrowing share and the per-line slopes, so the
    # three quantities cannot drift apart.
    wbar_cond = W.mean(axis=0)
    Nc = N - N.mean()
    S_NN = float(np.sum(Nc ** 2))
    lever = Nc / S_NN
    slope = float(lever @ wbar_cond)
    floor = float(np.mean(wbar_cond) - slope * float(np.mean(N)))
    resid_cond = wbar_cond - (floor + slope * N)
    ss_cond = float(np.sum(resid_cond ** 2))

    # The interaction residual: what is left of a width once its own line's
    # mean and its own condition's mean are both removed. It is blind to the
    # condition-common departure, which is exactly why it isolates s_ind.
    inter = W - W.mean(axis=1, keepdims=True) - wbar_cond[None, :] + W.mean()
    ss_int = float(np.sum(inter ** 2))
    ms_cond, ms_int = ss_cond / df_cond, ss_int / df_int

    s_ind2, V = ms_int, ms_cond
    s_c2 = V - s_ind2 / n_line
    at_bound = bool(s_c2 < 0.0)
    if at_bound:
        # constrained REML with s_c^2 = 0: one component, both subspaces
        s_c2 = 0.0
        s_ind2 = (n_line * ss_cond + ss_int) / (df_cond + df_int)
        V = s_ind2 / n_line
        g_cond = df_cond / (df_cond + df_int)
        g_int = df_int / (n_line * (df_cond + df_int))
    else:
        g_cond, g_int = 1.0, 0.0
    dof_eff = float(V ** 2 / ((g_cond * ms_cond) ** 2 / df_cond
                              + (g_int * ms_int) ** 2 / df_int))

    se = float(np.sqrt(V / S_NN))
    t95 = float(student_t.ppf(0.95, dof_eff))
    bound95 = abs(slope) + t95 * se
    f_common = float(s_c2 / (s_c2 + s_ind2)) if (s_c2 + s_ind2) > 0 else 0.0
    f_lo, f_hi = profile_f_range(ss_cond, df_cond, ss_int, df_int, n_line)

    # The within-block-only slope error, the pooled counterpart of the per-line
    # `formal_err`. It is reported for the same reason it is per line: to show
    # how far the full error sits above the one the repeat scatter alone
    # would give.
    formal_err, rms_within = float("nan"), float("nan")
    if E is not None:
        E = np.asarray(E, float)
        var_mean = np.sum(E ** 2, axis=0) / n_line ** 2
        formal_err = float(np.sqrt(np.sum(lever ** 2 * var_mean)))
        rms_within = float(np.sqrt(np.mean(E ** 2)))

    return {
        "beta_eff": slope, "floor": floor,
        "formal_err": formal_err, "syst_err": se,
        "resid_rms": float(np.sqrt(V)), "snr": abs(slope) / se if se > 0 else 0.0,
        "dof": dof_eff, "t95": t95, "bound95": bound95,
        "n_frac_syst": n_frac_syst,
        "bound95_nscale": bound95 * (1.0 + n_frac_syst),
        # frozen by note section 3, whatever snr says
        "verdict": "BOUND",
        "monotonic": bool(np.all(np.diff(wbar_cond[np.argsort(N)]) > 0)),
        "s_c": float(np.sqrt(s_c2)), "s_ind": float(np.sqrt(s_ind2)),
        "s_c2": float(s_c2), "s_ind2": float(s_ind2), "V": float(V),
        "f_common": f_common, "f_lo": f_lo, "f_hi": f_hi,
        "ms_cond": ms_cond, "ms_int": ms_int,
        "df_cond": df_cond, "df_int": df_int,
        "g_cond": g_cond, "g_int": g_int, "reml_at_bound": at_bound,
        "rms_within": rms_within, "S_NN": S_NN, "lever": lever,
        "wbar_cond": wbar_cond, "resid_cond": resid_cond,
        # every width's residual under the shared slope with its own line's
        # floor, which is what "how many lines sit low there" is counted on
        "resid_line_cond": W - W.mean(axis=1, keepdims=True) - slope * Nc[None, :],
        # the per-line slopes of the SAME construction (equal weights), whose
        # mean is the pooled slope identically
        "slopes_line": W @ lever,
    }


def pooled_group_split(N, W, groups, s_ind2):
    """Two groups of lines against each other under the shared-slope model.

    The per-isotope split of note section 1, an expected null reported as a
    check and never as fit structure. The condition-common departure is shared
    by every line, so it cancels exactly in the difference of two group slopes
    and the error of the split is set by the per-line component alone,

        Var(slope_a - slope_b) = s_ind^2 * (1/n_a + 1/n_b) / S_NN.

    That cancellation is why the split tests the sharing more sharply than
    either group's own slope does."""
    N = np.asarray(N, float)
    W = np.asarray(W, float)
    groups = list(groups)
    Nc = N - N.mean()
    S_NN = float(np.sum(Nc ** 2))
    lever = Nc / S_NN
    labels = sorted(set(groups))
    slopes = {g: float(lever @ W[[i for i, x in enumerate(groups) if x == g]].mean(axis=0))
              for g in labels}
    counts = {g: sum(1 for x in groups if x == g) for g in labels}
    out = {"slopes": slopes, "counts": counts}
    if len(labels) == 2:
        lo, hi = labels
        diff = slopes[hi] - slopes[lo]
        se = float(np.sqrt(s_ind2 * (1.0 / counts[hi] + 1.0 / counts[lo]) / S_NN))
        out.update({"label": f"{hi} minus {lo}", "diff": diff, "se": se,
                    "sigma": abs(diff) / se if se > 0 else float("inf")})
    return out


def anchor_narrowing_share(pooled, N, T_C, anchor_C=POOLED_ANCHOR_C):
    """The share of the pooled slope carried by the coldest point's narrowing.

    raw_fwhm_mhz records the bias in its own docstring: a half-maximum width
    read off a weak trace comes out narrow, about 6 per cent at the 70 C end.
    It narrows the lowest-density anchor, which STEEPENS the fitted slope, so
    it can only make the bound more conservative. The size is computed here
    rather than asserted. The pooled slope is a fixed linear functional of the
    four condition means, so lifting the anchor mean onto the fitted line
    changes the slope by lever * residual, and the share is that change over
    the slope itself. Taking the anchor's MEASURED departure from the line as
    the narrowing is the conservative reading of it: it credits the narrowing
    with less of the slope than injecting a nominal 6 per cent would, because
    the fitted line follows a depressed anchor part of the way down. It also
    keeps the number computed rather than typed, which the nominal figure
    would not. Reported with it: the fractional depth of the shortfall,
    for comparison with the documented 6 per cent, and how many lines sit low
    at the anchor under their own floor."""
    T_C = np.asarray(T_C, float)
    i = int(np.argmin(np.abs(T_C - anchor_C)))
    resid = float(pooled["resid_cond"][i])
    d_slope = float(pooled["lever"][i]) * resid
    return {
        "anchor_C": float(T_C[i]),
        "share": d_slope / pooled["beta_eff"] if pooled["beta_eff"] else float("nan"),
        "shortfall_mhz": -resid,
        "shortfall_frac": -resid / float(pooled["wbar_cond"][i]),
        "slope_without": pooled["beta_eff"] - d_slope,
        "n_lines_low": int(np.sum(pooled["resid_line_cond"][:, i] < 0.0)),
    }


def pooled_probe_rows(fields, pooled, split, anchor, chi2_line, gain, worst_peak):
    """The pooled construction as rows of results/beta_self_probe.csv.

    They carry the per-line rows' fields exactly, so the file stays one table,
    and they carry headline='no'. Every consumer of this file selects the
    headline rows (the ledger, fig19's quoted bound, the coverage and
    canonical-doc tests), and promoting the pooled bound to the quoted headline
    is the owner's decision and a separate change, not a side effect of
    computing it. The quantity lives in the `peak` column behind a pooled_
    prefix, and columns that do not apply to a scalar diagnostic are left empty
    rather than filled with a zero that would read as a measured value."""
    def row(name, variant, **vals):
        r = {k: "" for k in fields}
        r["peak"], r["variant"], r["headline"] = name, variant, "no"
        r.update(vals)
        return r

    head = row("pooled_slope", POOLED_VARIANT,
               **{k: pooled[k] for k in
                  ("beta_eff", "formal_err", "syst_err", "resid_rms", "snr",
                   "dof", "t95", "bound95", "n_frac_syst", "bound95_nscale",
                   "verdict", "monotonic")})
    return [
        head,
        row("pooled_s_c", "condition-common width scatter (MHz), REML on the "
            "sixteen points", beta_eff=pooled["s_c"]),
        row("pooled_s_ind", "per-line width scatter (MHz), REML on the sixteen "
            "points, subsumes the within-block error", beta_eff=pooled["s_ind"]),
        # written so the subsumption can be checked from the table alone: this
        # must sit BELOW pooled_s_ind, or the sixteen widths are quieter than
        # their own error bars and the decomposition is not describing them
        row("pooled_rms_within", "rms within-block width error (MHz), the "
            "repeat and rate error that s_ind subsumes",
            beta_eff=pooled["rms_within"]),
        row("pooled_f_common", "common-mode fraction s_c^2/(s_c^2+s_ind^2)",
            beta_eff=pooled["f_common"]),
        row("pooled_f_common_lo", "common-mode fraction, low end of the 95% "
            "profile range (dchi2 < 3.841)", beta_eff=pooled["f_lo"]),
        row("pooled_f_common_hi", "common-mode fraction, high end of the 95% "
            "profile range (dchi2 < 3.841)", beta_eff=pooled["f_hi"]),
        row("pooled_gain_vs_worst_perline",
            f"worst per-line 95% bound ({worst_peak}) over the pooled one",
            beta_eff=gain),
        row("pooled_share_70C",
            f"share of the pooled slope carried by the {anchor['anchor_C']:.0f} C "
            "low-SNR narrowing", beta_eff=anchor["share"]),
        row("pooled_isotope_split",
            f"{split['label']} Rb pooled slope, an expected null (note section 1)",
            beta_eff=split["diff"], formal_err=split["se"], snr=split["sigma"]),
        row("pooled_perline_chi2",
            "four per-line slopes against the shared slope, chi2 per dof on "
            "their own total errors", beta_eff=chi2_line,
            dof=len(pooled["slopes_line"]) - 1),
    ]


def main() -> int:
    take_producer_lock("run_beta_self")
    rows = load_manifest()
    # Sibling outliers leave the density fits entirely. A trace whose own
    # siblings do not share its height or width is not a repeat of the same
    # condition, and the density lever is built out of repeats. Filtering the
    # manifest ONCE means every probe below sees the same trace set, which is
    # the property a per-probe filter would not have. Pre-registered in
    # docs/notes/ruler_validity_and_trim_prereg.md, amendment 2 B4.
    dropped = outlier_files()
    if dropped:
        rows = [r for r in rows if r["file"] not in dropped]
        print(f"excluding {len(dropped)} sibling outlier(s) from every fit here: "
              + ", ".join(sorted(dropped)))
    trates, prates = load_t_rates()

    results = []
    fits = {}
    for peak in PEAKS:
        conds = load_conditions(rows, peak, trates, prates)
        if len(conds) < 2:
            print(f"[skip] {peak}: {len(conds)} temperatures"); continue
        fit = fit_beta_self(conds, transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        fits[peak] = (fit, conds)
        results.append({"peak": peak, **{k: fit[k] for k in
                        ("beta_self", "beta_self_err", "sigma_laser", "sigma_laser_err",
                         "chi2_red", "corr_beta_laser", "noise_floor_limited",
                         "beta_at_bound", "sigma_laser_at_bound")}})

    with open(C.RESULTS_DIR / "beta_self.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)

    # ---- robustness swap: the M1 noise law vs UNIFORM weights -------------
    # The weights come from the measured sigma(V) law (M1). If beta depended
    # strongly on that choice, the noise model would be doing physics work it
    # was never validated for. Refit every peak with law=None (uniform) and
    # record the shift; this swap was flagged as untested (2026-07-25).
    swap_rows = []
    for peak, (fit_w, conds) in fits.items():
        uni = fit_beta_self([dict(c, law=None) for c in conds],
                            transit_ref_mhz=C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        swap_rows.append({
            "peak": peak,
            "isotope": _CONST.PEAKS[peak]["isotope"],
            "beta_m1_law": f"{fit_w['beta_self']:.4f}",
            "beta_uniform": f"{uni['beta_self']:.4f}",
            "shift": f"{uni['beta_self'] - fit_w['beta_self']:+.4f}",
            "unit": "MHz per 1e12 cm^-3",
        })
    if swap_rows:
        with open(C.RESULTS_DIR / "noise_law_swap.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(swap_rows[0].keys()))
            w.writeheader(); w.writerows(swap_rows)
        mx = max(abs(float(r["shift"])) for r in swap_rows)
        print(f"\n  NOISE-LAW SWAP (M1 weights -> uniform): max |d beta| = {mx:.4f} "
              f"MHz/1e12 -- wrote results/noise_law_swap.csv")

    print("=" * 74)
    print("beta_self (PRELIMINARY: transit on OPEN w0 prior; MHz per 1e12 cm^-3):")
    print(f"{'peak':>6s} {'beta_self':>16s} {'sigma_laser':>14s} {'chi2':>6s} {'corr(b,L)':>9s}")
    for r in results:
        print(f"{r['peak']:>6s} {r['beta_self']:>7.3f}+/-{r['beta_self_err']:<7.3f} "
              f"{r['sigma_laser']:>6.2f}+/-{r['sigma_laser_err']:<5.2f} "
              f"{r['chi2_red']:>6.2f} {r['corr_beta_laser']:>9.2f}")

    # ---- per-peak beta consistency + within-isotope pooling ----
    print(f"\n{'-'*74}\nPER-PEAK beta_self consistency (are the four values mutually OK?):")
    iso = {"4121": 87, "4207": 87, "4154": 85, "4192": 85}
    bp = {r["peak"]: (r["beta_self"], r["beta_self_err"]) for r in results}
    for isotope in (87, 85):
        ps = [p for p in ("4121", "4207", "4154", "4192") if iso[p] == isotope and p in bp]
        if len(ps) < 2:
            continue
        v = np.array([float(bp[p][0]) for p in ps])
        e = np.array([float(bp[p][1]) for p in ps])
        wmean = np.sum(v / e ** 2) / np.sum(1 / e ** 2)
        werr = 1.0 / np.sqrt(np.sum(1 / e ** 2))
        chi2 = np.sum(((v - wmean) / e) ** 2) / max(len(ps) - 1, 1)
        pull = {p: (float(bp[p][0]) - wmean) / float(bp[p][1]) for p in ps}
        worst = max(pull, key=lambda k: abs(pull[k]))
        print(f"  {isotope}Rb {ps}: pooled beta = {wmean:.4f}+/-{werr:.4f}  "
              f"chi2/dof={chi2:.1f}  "
              f"({'consistent' if chi2 < 3 else 'INCONSISTENT'}; "
              f"worst {worst} at {pull[worst]:+.1f}sigma)")
    print("  NOTE: per-peak beta (this fit, four-point, ~0.01-0.02) and the per-isotope")
    print("  global fit (fit_global, ~0.056) differ at the factor-~3 level depending on the")
    print("  sigma_laser sharing -- a model systematic; the headline stays the")
    print("  model-independent raw-width BOUND (P0 below), not any single beta value.")

    # ---- P3: cross-peak consistency of the implied gamma_coll at 110 C ----
    N110 = density_units(110.0)
    gc110 = [(r["peak"], r["beta_self"] * N110, r["beta_self_err"] * N110) for r in results]
    vals = np.array([g[1] for g in gc110]); errs = np.array([g[2] for g in gc110])
    wmean = np.sum(vals / errs ** 2) / np.sum(1 / errs ** 2)
    chi2_cross = np.sum(((vals - wmean) / errs) ** 2) / max(len(vals) - 1, 1)
    print("\n(P3) cross-peak gamma_coll @110C: " +
          ", ".join(f"{p}={v:.2f}" for p, v, e in gc110) +
          f"  | chi2/dof vs common = {chi2_cross:.1f} "
          f"({'consistent' if chi2_cross < 3 else 'INCONSISTENT -> per-peak systematic'})")

    # ---- P0 (decisive): model-independent width vs density + systematic ----
    print(f"\n{'-'*74}\n(P0) MODEL-INDEPENDENT raw-width vs density [the decisive confound probe]:")
    print(f"{'peak':>6s} {'beta_eff':>10s} {'formal':>8s} {'+syst':>8s} "
          f"{'resid':>7s} {'sig':>5s} {'mono':>5s}  verdict")
    # Single headline variant (2026-08-02): 70/90/110/130 C, dof=2, the
    # x52.5 density lever. No separate three-point row is kept; see the
    # module docstring for why.
    probe_rows = []
    variant = "70-130C (headline, four-point, same configuration, 52.5x lever)"
    print(f"  --- {variant} ---")
    for peak in PEAKS:
        pr = width_vs_density_probe(rows, peak, trates, prates, include_130=True)
        if pr is None:
            continue
        probe_rows.append({"peak": peak, "variant": variant, "headline": "yes",
                          **{k: pr[k] for k in
                          ("beta_eff", "formal_err", "syst_err", "resid_rms", "snr",
                           "dof", "t95", "bound95", "n_frac_syst",
                           "bound95_nscale", "verdict", "monotonic")}})
        print(f"{peak:>6s} {pr['beta_eff']:>10.4f} {pr['formal_err']:>8.4f} "
              f"{pr['syst_err']:>8.4f} {pr['resid_rms']:>7.3f} {pr['snr']:>5.1f} "
              f"{('yes' if pr['monotonic'] else 'NO'):>5s}  {pr['verdict']}"
              + (f" (<{pr['bound95_nscale']:.3f} @95%; t({pr['dof']})="
                 f"{pr['t95']:.2f}, x{1 + pr['n_frac_syst']:.1f} N-scale)"
                 if pr['verdict'] == 'BOUND' else ""))
    # ---- the pooled construction: ONE shared slope for the four lines -----
    # docs/notes/beta_self_pooling_prereg.md, written and committed before this
    # code existed. The per-line rows above are untouched by it: pooling adds
    # rows, it does not restate theirs.
    pooled_rows = []
    perline = {r["peak"]: r for r in probe_rows}
    table = pooled_width_table(rows, PEAKS, trates, prates)
    if table is None or len(perline) < len(PEAKS):
        print("\n(POOLED) the four-by-four design is not balanced in this "
              "checkout, so the collapse identity does not apply -- pooling "
              "skipped and the per-line rows stand alone")
    else:
        used, Npool, Wpool, Epool = table
        pooled = pooled_width_slope(Npool, Wpool, Epool)
        split = pooled_group_split(Npool, Wpool,
                                   [_CONST.PEAKS[p]["isotope"] for p in used],
                                   pooled["s_ind2"])
        anchor = anchor_narrowing_share(pooled, Npool, POOL_CONDITIONS_C)
        # Prediction 2's first half: each per-line slope against the shared one
        # on its OWN total error, which is the error that line's own bound is
        # built from. A check on the data, never the licence for sharing.
        pulls = {p: (float(perline[p]["beta_eff"]) - pooled["beta_eff"])
                 / float(perline[p]["syst_err"]) for p in used}
        chi2_line = sum(v ** 2 for v in pulls.values()) / max(len(used) - 1, 1)
        worst_peak = max(perline, key=lambda p: float(perline[p]["bound95_nscale"]))
        worst = float(perline[worst_peak]["bound95_nscale"])
        gain = worst / pooled["bound95_nscale"]
        pooled_rows = pooled_probe_rows(list(probe_rows[0].keys()), pooled, split,
                                        anchor, chi2_line, gain, worst_peak)

        print(f"\n{'-'*74}\n(POOLED) one shared slope, per-line floors "
              "[docs/notes/beta_self_pooling_prereg.md]:")
        print(f"  design: {Wpool.shape[0]} lines x {Wpool.shape[1]} conditions "
              f"({', '.join(f'{t:.0f}' for t in POOL_CONDITIONS_C)} C), "
              f"lever x{Npool.max() / Npool.min():.1f}, "
              f"lines {', '.join(used)}")
        print(f"  pooled slope = {pooled['beta_eff']:+.5f} +/- {pooled['syst_err']:.5f} "
              f"MHz per 1e12 cm^-3   (within-block only: {pooled['formal_err']:.5f})")
        print(f"  95% BOUND    < {pooled['bound95_nscale']:.5f}   "
              f"(|b| + t95*err = {pooled['bound95']:.5f}, then "
              f"x{1 + pooled['n_frac_syst']:.1f} N-scale, with "
              f"t(0.95, {pooled['dof']:.2f}) = {pooled['t95']:.2f})")
        print(f"  variance: s_c = {pooled['s_c']:.4f} MHz (condition-common), "
              f"s_ind = {pooled['s_ind']:.4f} MHz (per line), "
              f"rms within-block {pooled['rms_within']:.4f} MHz")
        print(f"            f = {pooled['f_common']:.3f} "
              f"[{pooled['f_lo']:.3f}, {pooled['f_hi']:.3f}] 95% profile, "
              f"V = {pooled['V']:.5f} MHz^2, dof_eff = {pooled['dof']:.2f}"
              + ("  (REML at the s_c = 0 boundary)" if pooled["reml_at_bound"] else ""))
        # The collapse identity at run time as well as in the tests: the
        # equal-weight per-line slopes average to the pooled slope exactly.
        ident = abs(float(np.mean(pooled["slopes_line"])) - pooled["beta_eff"])
        print(f"  collapse identity: the equal-weight per-line slopes average to "
              f"the pooled slope to {ident:.1e} MHz per 1e12 cm^-3")
        print("  CHECK per-line slopes vs the shared slope (own total errors): "
              + ", ".join(f"{p} {pulls[p]:+.1f}s" for p in used)
              + f"  chi2/dof = {chi2_line:.2f}")
        print(f"  CHECK per-isotope split {split['label']} Rb = "
              f"{split['diff']:+.5f} +/- {split['se']:.5f} "
              f"({split['sigma']:.1f} sigma from zero, and the common mode "
              f"cancels in the difference, so this error is the per-line "
              f"component alone)")
        print(f"  {anchor['anchor_C']:.0f} C low-SNR narrowing: the condition mean "
              f"sits {-100 * anchor['shortfall_frac']:+.1f}% "
              f"({-anchor['shortfall_mhz']:+.3f} MHz) off the fitted line, "
              f"{anchor['n_lines_low']}/{Wpool.shape[0]} lines low there, and it "
              f"carries {100 * anchor['share']:+.1f}% of the pooled slope "
              f"(without it {anchor['slope_without']:+.5f})")
        print(f"  worst per-line bound {worst:.5f} ({worst_peak}) -> pooled "
              f"{pooled['bound95_nscale']:.5f}, gain x{gain:.2f}")

        # ---- note section 5: the pre-registered predictions ---------------
        # Checked here rather than by eye, and printed pass or fail. Section 5
        # also fixes what happens on a failure, so it is printed with it.
        p1 = 0.25 * worst < pooled["bound95_nscale"] < worst
        p2 = chi2_line < 3.0 and split["sigma"] < 2.0
        p3 = 1.1 <= gain <= 1.8
        print("  PREREGISTERED PREDICTIONS (note section 5):")
        print(f"    1 pooled bound below the worst per-line bound and above a "
              f"quarter of it: {'HOLDS' if p1 else 'FAILS'} "
              f"({0.25 * worst:.5f} < {pooled['bound95_nscale']:.5f} < {worst:.5f})")
        print(f"    2 per-line slopes consistent with the shared slope "
              f"(chi2/dof {chi2_line:.2f} < 3) and the isotope split consistent "
              f"with zero ({split['sigma']:.1f} < 2 sigma): "
              f"{'HOLDS' if p2 else 'FAILS'}")
        print(f"    3 fractional gain inside the pre-stated 1.1 to 1.8 bracket: "
              f"{'HOLDS' if p3 else 'FAILS'} (x{gain:.2f})")
        if not (p1 and p3):
            print("    -> section 5: STOP and escalate to the owner before "
                  "anything is written on this.")
        if not p2:
            print("    -> section 5: a finding about a per-line systematic. It "
                  "goes to the owner with the pooling left unadopted.")
        print("  The verdict is BOUND by note section 3 whatever the pooled "
              "signal-to-noise says, and these rows are headline='no': "
              "adopting the pooled bound is the owner's decision.")

    with open(C.RESULTS_DIR / "beta_self_probe.csv", "w", newline="") as f:
        if probe_rows:
            w = csv.DictWriter(f, fieldnames=list(probe_rows[0].keys()))
            w.writeheader(); w.writerows(probe_rows + pooled_rows)

    n_nonmono = sum(1 for p in probe_rows if not p["monotonic"])
    print(f"\nVERDICT: {n_nonmono}/{len(probe_rows)} peaks are NON-MONOTONIC in density"
          " -- impossible for pure collisional broadening.")
    print("The between-block width scatter is the DOMINANT error: laser-width drift")
    print("across sessions is comparable to the collisional trend, so the archival")
    print("four-point lever BOUNDS beta_self (it does not measure it).")
    print("The global-fit sigmas above are OVERCONFIDENT -- they assume one shared")
    print("sigma_laser across blocks and so omit exactly this between-block drift.")
    print("=> Clean beta_self REQUIRES a fixed-lock session (two-epoch design).")

    print(f"\n{'-'*74}\nCAVEATS (all results PRELIMINARY):")
    print("  * transit fixed on the OPEN w0 prior -> absolute scale of any beta")
    print("  * headline is 70/90/110/130 C (dof=2); 130C is still the extreme end")
    print("    of the lever, same apparatus/optical configuration as 70-110C")
    print("    (Michelangelo, firsthand), differing only by session/epoch and")
    print("    per-session rate calibration (handled in load_t_rates)")
    print("  * vapor-density cold-spot systematic (density.py) on absolute N(T)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

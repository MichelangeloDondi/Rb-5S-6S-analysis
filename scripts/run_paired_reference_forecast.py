#!/usr/bin/env python3
"""Forecast the paired cell+fibre acquisition against unreferenced sweeps.

The design question (owner, 2026-08-31): what is gained by collecting
the vapour-cell traces in the very same sweep as the ONF ones, shared
timestamps, one oscilloscope. The working assessment says the surface
shift becomes differential, so the repaired lock's residual noise
drops to common mode. This producer tests that claim with the twin
rather than asserting it, across the SPAN of both unmeasured lock
quantities - the drift rate AND the per-sweep excursion - and reports
each verdict with the distance to its threshold in units of the run's
own error, saying UNRESOLVED instead of picking a side when that
distance is under one sigma.

THE TWO MODES. UNREFERENCED is the 2025 default: the fibre channel
acquired by itself, each sweep's fitted centre carrying the lock
offset whole. PAIRED adds the cell arm to the same sweep: the cell's
carrier and EOM comb pin the frequency axis and the fibre centre is
read against it. A THIRD protocol exists between them - a cell
reference on alternating separate sweeps, which subtracts the ramp at
twice the excursion variance plus the inter-sweep drift - and is
named here as a limit, not modelled.

THE GENERATOR CONTRACT. Each Monte-Carlo iteration draws ONE
laser-frequency offset (a drift ramp at a random time in the session,
plus a per-sweep excursion) and acquires it in both modes, each with
its own photon noise, as they physically would. The two arms of the
paired sweep see the one offset identically. Both modes run at the
same record depth: the archive's and the planned campaign's record
lengths sit far under the scopes' per-channel memory ceilings (see
the registry row), so enabling the second channel forces no reduction,
and photon-budget conservation makes a depth division costless for
the fibre arm in any case.

WHAT IS SHARED, AND WHAT DELIBERATELY IS NOT. The joint fit shares
the frequency offset alone. No width is shared between the arms,
because the record itself warns against it: the cell's fitted
Gaussian is a leftover at the waist, not a laser measurement
(docs/RESULTS.md, the sigma_laser caveat), and its leading candidate,
retro-tilt residual Doppler, is a geometry the guided arm does not
have. The injected Gaussians therefore differ per arm and every width
stays free per arm.

THE OBSERVABLE is the per-sweep standard deviation of the surface-
shift estimate over many sweeps, paired against unreferenced, with
the width-error ratio beside it (expected at parity: the budget is
conserved and no width is shared).

RUNG: simulation (the twin), stated per the ladder because the
central cancellation is derivable - the shared offset enters both
arms additively and subtracts exactly - and what the Monte Carlo
computes is the RESIDUAL: photon noise on the pin against the
excursion it replaces, and the fibre arm's own statistics. LIMITS, stated beside the gains: the differential
removes the LASER only (Stark, Zeeman and kernel differences between
the arms stay modelled offsets, not evaluated here); the alternating-
reference third protocol is not modelled; the branch noise models are
shot-limited analog and Poisson counting; the kernel-unification wave
refines the guided width class. Each design input carries its basis
beside it.

Needs nothing outside the repository. Writes
results/paired_reference_forecast.csv; every row's status is ENVELOPE
(a design forecast over stated spans, not a measurement of anything).
Failure mode this producer guards against: adopting or refusing the
paired geometry on rhetoric - the hub's fibre scenario may carry only
numbers this file emits, and no verdict here hides its own error.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.special import voigt_profile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.pmfmt import pm_cells  # noqa: E402

RNG_SEED = 20260902  # fixed seed; changing it changes every quoted
#   cell, and the CSV reproduces byte for byte under it
RNG = np.random.default_rng(RNG_SEED)

# --- design inputs, each with its basis ------------------------------------
DRIFT_SPAN_KHZ_MIN = (0.0, 5.0, 20.0, 40.0)   # the repaired lock's residual
#   drift is UNMEASURED (docs/plan/09 section 10c.2): spanned 0-40 kHz/min,
#   the record's own span for this open item (docs/plan/12), whose top is
#   the archive's held-lock input, 0.04 MHz/min (results/projections.csv)
JITTER_SPAN_MHZ = (0.009, 0.028, 0.05, 0.10)  # the per-sweep excursion is
#   also unmeasured for the repaired lock, and the verdicts turn on it, so
#   it is spanned, never fixed. The grid's bases, low to high: the comb
#   best-fit class, consistent with zero; the comb-as-clock 95 per cent
#   limit, which constrains the nonlinear within-sweep part and is used
#   here as the class scale for the per-sweep excursion, an identification
#   the lock characterisation will replace; a mid design class; the
#   wavemeter sd over a 24-minute window, a ceiling that double-counts the
#   ramp (all three record numbers: docs/RESULTS.md)
SWEEP_S = 10.0           # one triangle leg at the campaign's sweep class
SESSION_MIN = 8.0        # the session window class the drift ramp is
#   sampled over; sweep times are drawn uniformly in it, as sweeps land in
#   practice, so the sweeps stay exchangeable and the jackknife applies.
#   The Monte-Carlo sample size below is a separate, statistical choice
N_POINTS = 1200          # per channel per sweep after decimation, a design
#   class; both modes run at the same depth (see the registry row's basis)
SPAN_MHZ = 90.0          # one line's paired window: carrier, the +-12.5 MHz
#   EOM ruler and the guided copy. The four lines span about 5.2 GHz
#   (line_positions_mhz), so no sweep carries the quartet as an in-sweep
#   reference; a paired sweep carries the same transition through both arms
#   plus the comb, and the quartet stays pinned across sweeps as in 2025.
#   An earlier internal sketch of this geometry assumed otherwise; this
#   comment records the correction
EOM_RULER_MHZ = 12.5     # the in-scan frequency ruler of the 2025 record
#   (docs/APPARATUS.md)
SIDEBAND_AMP = 0.25     # sideband-to-carrier amplitude class, a design
#   input (the 2025 ruler's modulation depth was tuned per session)
GAMMA_CELL = 5.6         # MHz, the Lorentzian core beside the cell's own
#   Gaussian. The committed cell total FWHMs run 4.814-5.741
#   (results/linefit_conditions.csv); with SIGMA_CELL the Voigt total is
#   5.73, inside the family near its top - conservative for the pin, since
#   a broader carrier pins the axis less tightly
SIGMA_CELL = 0.353       # MHz, the cell arm's Gaussian: the committed
#   family's minimum (0.353-2.413, results/linefit_conditions.csv), the
#   least drift-contaminated fitted value. The record warns this quantity
#   is a leftover at the waist, not a laser width (docs/RESULTS.md), which
#   is exactly why no width is shared between the arms here
GAMMA_FIBRE = 3.89       # MHz, the guided kernel's Lorentzian FWHM
#   (docs/methods/09: 3.8905); the kernel-unification wave refines it
SIGMA_FIBRE = 0.30       # MHz sd, the guided kernel's own Gaussian
#   companion (docs/methods/09), distinct from the cell's by design
CELL_SNR_PEAK = 120.0    # analog carrier peak against per-point rms
#   noise AT the N_POINTS design class below, the bright reference class of
#   the 2025 record's high-SNR conditions. The cell channel is treated as
#   shot-limited like the fibre one, so its per-point noise scales with the
#   square root of the point rate when N_POINTS is perturbed; the
#   sensitivity rows below span a factor of two either way
CELL_SNR_POINTS = 1200   # the point count CELL_SNR_PEAK is quoted at
FIBRE_COUNTS_PER_MS = 32.5   # midpoint of the committed 25-40 counts/ms
#   band (docs/big_picture/09's exposure row carries the band with refs)
FIBRE_BG_FRAC = 0.05     # dark/background class relative to the line peak,
#   a design input; enters both branch noise models identically
N_SWEEPS = 384           # Monte-Carlo sweeps per configuration; the sample
#   size behind every se this producer emits, chosen so the per-
#   configuration se is small against the separations the selection
#   rows compare (their notes print the margins)
N_SWEEPS_SENS = 48       # sample for the sensitivity rows and their
#   baseline, which need direction and distinguishability, not the third
#   digit
RATIO_THRESHOLD = 0.7    # the adjudication constant: the design choice of
#   what counts as a decisive gain, owner-adjustable, with no record
#   source. Each criterion and limit row carries its distance to it in
#   sigma, so a reader can move it and see what follows


def _line(x, centre, gamma, sigma_l, amp):
    """A true Voigt, Lorentzian FWHM `gamma` convolved with a Gaussian sd
    `sigma_l`, normalised to unit peak (the committed fitters use the full
    composite; the Voigt is the defensible core for an error forecast,
    with no free shape weights to manufacture information)."""
    s = max(sigma_l, 1e-3)
    v = voigt_profile(x - centre, s, gamma / 2.0)
    return amp * v / voigt_profile(0.0, s, gamma / 2.0)


def _fibre_trace(x, delta, branch, rng, dwell_ms):
    """The fibre arm at offset `delta`, with its branch's own noise, both
    branches spending the same photon budget at this dwell."""
    fib = _line(x, delta, GAMMA_FIBRE, SIGMA_FIBRE, 1.0)
    n_sig_pk = FIBRE_COUNTS_PER_MS * dwell_ms
    if branch == "counting":
        lam = n_sig_pk * (FIBRE_BG_FRAC + fib)
        counts = rng.poisson(np.maximum(lam, 0.0))
        fib_v = counts / max(n_sig_pk, 1.0)
    else:
        # an analog readout of the same rate carries the shot noise of the
        # TOTAL count at the peak, signal plus background, referred to the
        # signal-normalised trace: sd = sqrt(N_sig + N_bg) / N_sig
        sd = np.sqrt(n_sig_pk * (1.0 + FIBRE_BG_FRAC)) / max(n_sig_pk, 1.0)
        fib_v = fib + rng.normal(0.0, sd, x.size)
    fib_sd = np.sqrt(n_sig_pk * (1.0 + FIBRE_BG_FRAC)) / max(n_sig_pk, 1.0)
    return fib_v, fib_sd


def _sweep_unref(delta, branch, rng):
    """Single-channel acquisition: the fibre line, no reference."""
    x = np.linspace(-SPAN_MHZ / 2, SPAN_MHZ / 2, N_POINTS)
    dwell_ms = SWEEP_S * 1e3 / N_POINTS
    fib_v, fib_sd = _fibre_trace(x, delta, branch, rng, dwell_ms)
    return dict(x=x, fib=fib_v, fib_sd=fib_sd)


def _sweep_paired(delta, branch, rng):
    """Two-channel acquisition of the SAME offset: the cell carrier with
    its EOM sidebands on one channel, the fibre line on the other, both
    at the same depth as the unreferenced mode (the registry row's basis:
    the per-channel memory ceilings sit orders of magnitude above this
    record-length class, so nothing forces a split)."""
    x = np.linspace(-SPAN_MHZ / 2, SPAN_MHZ / 2, N_POINTS)
    dwell_ms = SWEEP_S * 1e3 / N_POINTS
    centres = np.array([-EOM_RULER_MHZ, 0.0, EOM_RULER_MHZ])
    amps = np.array([SIDEBAND_AMP, 1.0, SIDEBAND_AMP])
    cell = np.zeros_like(x)
    for c0, a0 in zip(centres, amps):
        cell += _line(x, c0 + delta, GAMMA_CELL, SIGMA_CELL, a0)
    cell_sd = np.sqrt(x.size / float(CELL_SNR_POINTS)) / CELL_SNR_PEAK
    cell_v = cell + rng.normal(0.0, cell_sd, x.size)
    fib_v, fib_sd = _fibre_trace(x, delta, branch, rng, dwell_ms)
    return dict(x=x, cell=cell_v, fib=fib_v, centres=centres, amps=amps,
                cell_sd=cell_sd, fib_sd=fib_sd)


def _fit_unref(sw) -> tuple[float, float]:
    """Unreferenced mode: the centre absorbs the offset whole; returns
    (S_est, gamma_fibre)."""
    x, y = sw["x"], sw["fib"]

    def resid(p):
        c, g, s, a, o = p
        return _line(x, c, abs(g), abs(s), a) + o - y

    p0 = [0.0, GAMMA_FIBRE, SIGMA_FIBRE, 1.0, 0.0]
    r = least_squares(resid, p0, method="lm", max_nfev=400)
    if r.status <= 0:
        raise RuntimeError(f"unreferenced fit did not converge: {r.message}")
    return r.x[0], abs(r.x[1])


def _fit_joint(sw) -> tuple[float, float, float]:
    """Both arms of one paired sweep, sharing the frequency offset ONLY:
    the cell pins the axis, the fibre centre is read against it, and
    every width stays free per arm (the record's sigma_laser caveat is
    why). Returns (S_est, gamma_fibre, d_pinned)."""
    x, yc, yf = sw["x"], sw["cell"], sw["fib"]
    cen = sw["centres"]
    # inverse-noise weighting, derived from the sweep's own noise levels
    # rather than chosen, so both arms enter on the same footing
    w_cell = sw["fib_sd"] / sw["cell_sd"]

    def resid(p):
        d, s_shift, gf, sf, gc, sc, af, of, ac, oc = p
        cell = np.zeros_like(x)
        for c0, a0 in zip(cen, sw["amps"]):
            cell += _line(x, c0 + d, abs(gc), abs(sc), ac * a0)
        fib = _line(x, d + s_shift, abs(gf), abs(sf), af)
        return np.concatenate([(cell + oc - yc) * w_cell, fib + of - yf])

    p0 = [0.0, 0.0, GAMMA_FIBRE, SIGMA_FIBRE, GAMMA_CELL, SIGMA_CELL,
          1.0, 0.0, 1.0, 0.0]
    r = least_squares(resid, p0, method="lm", max_nfev=800)
    if r.status <= 0:
        raise RuntimeError(f"joint fit did not converge: {r.message}")
    return r.x[1], abs(r.x[2]), r.x[0]


def _jack_ratio(a, b):
    """std(b)/std(a) with its delete-one jackknife se over paired
    iterations (each iteration's two modes share one offset draw, so the
    jackknife assumes nothing about their independence)."""
    a = np.asarray(a)
    b = np.asarray(b)
    n = a.size
    full = float(np.std(b) / np.std(a))
    reps = np.array([np.std(np.delete(b, i)) / np.std(np.delete(a, i))
                     for i in range(n)])
    se = float(np.sqrt((n - 1) / n * np.sum((reps - reps.mean()) ** 2)))
    return full, se


def _config_arrays(jitter, drift, branch, n_sweeps, rng):
    """One configuration's paired Monte Carlo: per iteration one offset,
    two acquisitions, two fits."""
    s_unref, s_joint, g_unref, g_joint = [], [], [], []
    deltas, pins = [], []
    for _ in range(n_sweeps):
        t_min = rng.uniform(0.0, SESSION_MIN)
        delta = (drift * 1e-3) * t_min + rng.normal(0.0, jitter)
        su, gu = _fit_unref(_sweep_unref(delta, branch, rng))
        sj, gj, dpin = _fit_joint(_sweep_paired(delta, branch, rng))
        s_unref.append(su)
        s_joint.append(sj)
        g_unref.append(gu)
        g_joint.append(gj)
        deltas.append(delta)
        pins.append(dpin - delta)
    return s_unref, s_joint, g_unref, g_joint, deltas, pins


def _dist_and_state(ratio, se):
    """Distance from the threshold in units of the row's own se, and the
    verdict it licenses: clears / fails / unresolved under one sigma. A
    zero se resolves by side, with the distance signed accordingly."""
    if se > 0:
        dist = (RATIO_THRESHOLD - ratio) / se
    elif ratio == RATIO_THRESHOLD:
        return 0.0, "unresolved"
    else:
        dist = float(np.copysign(np.inf, RATIO_THRESHOLD - ratio))
    if dist >= 1.0:
        state = "clears"
    elif dist <= -1.0:
        state = "fails"
    else:
        state = "unresolved"
    return dist, state


def _criterion_state(worst_ratio, worst_se, runner_ratio, runner_se):
    """The span verdict: the worst configuration's side, downgraded to
    unresolved when the selection margin to the runner-up is under one
    combined sigma AND the two candidates' own states disagree (a
    same-side ambiguity cannot change the verdict). Returns
    (state, dist, margin, licensed_by), the last naming which clause
    decided an unresolved. Extracted so every branch is testable."""
    dist, state = _dist_and_state(worst_ratio, worst_se)
    margin = ((worst_ratio - runner_ratio)
              / max(float(np.hypot(worst_se, runner_se)), 1e-12))
    r_state = _dist_and_state(runner_ratio, runner_se)[1]
    licensed_by = ""
    if state == "unresolved":
        licensed_by = "the distance"
    elif margin < 1.0 and r_state != state:
        state = "unresolved"
        licensed_by = "a selection whose candidates disagree"
    return state, dist, margin, licensed_by


SENS_NAMES = ("CELL_SNR_PEAK", "N_POINTS", "SIGMA_CELL", "GAMMA_CELL",
              "GAMMA_FIBRE", "SIGMA_FIBRE", "SIDEBAND_AMP",
              "FIBRE_COUNTS_PER_MS", "FIBRE_BG_FRAC")


def _sensitivity_rows():
    """Nine design constants, each doubled and halved at the boundary-
    region configuration (the comb-limit excursion, the small drift, the
    analog branch), against a BASELINE emitted at the same seed and
    sample. Each row carries its jackknife se and its distance from the
    baseline in combined sigma, where the combination assumes
    independence and so overstates the se for the eight constants that
    keep the common-random-number pairing: their distinguishable-no is
    conservative on the cell side, while the fibre-side rows are limited
    by this sample instead. The verdict is distinguishability, not a
    threshold side. Module constants are overridden in place and
    restored, safe here: one process, one thread, own rng per eval. The
    N_POINTS rows change the draw count, which breaks the common-random-
    number pairing the others keep; their notes say so."""
    g = globals()

    def eval_ratio():
        rng = np.random.default_rng(RNG_SEED + 7)
        sa, sj = _config_arrays(0.028, 5.0, "analog",
                                N_SWEEPS_SENS, rng)[:2]
        return _jack_ratio(sa, sj)

    base_ratio, base_se = eval_ratio()
    vb, sb = pm_cells(base_ratio, base_se)
    rows = [("sensitivity", "baseline", vb, sb, "ratio",
             "the unperturbed boundary-region configuration"
             " (analog/j0.028/d5) at the sensitivity sample. Every row"
             " below is read against this one. At this sample a"
             " perturbation must move the ratio by about a fifth to"
             " read yes, and the cell-side constants cannot: the pin"
             " error sits several times under the fibre arm's own, so"
             " their no is structural, not reassuring")]
    for name in SENS_NAMES:
        base = g[name]
        for tag, factor in (("x2", 2.0), ("half", 0.5)):
            new = base * factor
            g[name] = int(new) if name == "N_POINTS" else new
            try:
                ratio, se = eval_ratio()
            finally:
                g[name] = base
            comb = float(np.hypot(se, base_se))
            dsig = (ratio - base_ratio) / comb if comb > 0 else 0.0
            if abs(dsig) < 0.05:
                dsig = 0.0
            sep = "yes" if abs(dsig) >= 1.0 else "no"
            note = (f"{name} at {tag}. Distance from baseline "
                    f"{dsig:+.1f} sigma combined. Distinguishable: {sep}")
            if name == "N_POINTS":
                note += (". This row changes the draw count, so the"
                         " common-random-number pairing is broken here")
            vr, sr = pm_cells(ratio, se)
            rows.append(("sensitivity", f"{name}_{tag}", vr, sr, "ratio",
                         note))
    return rows


_DIST_RE = re.compile(r"\d+(?:\.\d+)? sigma")


def _assert_verdict_rows(rows):
    """The producer proves the universal its notes assert - every
    criterion and limit row carries a numeric sigma distance and names
    the threshold - with both populations pinned, so a silent rename or
    a keyword-only note is caught. Module-level and pure so the test
    module can plant every failure shape against it."""
    n_limit = sum(1 for r in rows if r[0] == "limit")
    if n_limit != 2:
        raise RuntimeError(f"the limit group holds {n_limit} rows, not the"
                           " two measured ones the sentences enumerate")
    crit = [r for r in rows
            if r[0].startswith("span_") and r[1] == "criterion"]
    if len(crit) != len(JITTER_SPAN_MHZ):
        raise RuntimeError(f"{len(crit)} criterion rows against"
                           f" {len(JITTER_SPAN_MHZ)} excursion classes")
    for r in crit + [r for r in rows if r[0] == "limit"]:
        note = r[5]
        if not _DIST_RE.search(note):
            raise RuntimeError("verdict row without a numeric sigma"
                               f" distance: {r[:2]}")
        if f"{RATIO_THRESHOLD:g} threshold" not in note:
            raise RuntimeError("verdict row without its named threshold:"
                               f" {r[:2]}")


def main() -> int:
    rows = []
    per_jitter = {}
    per_jitter_states = {}
    limits = {}
    for jitter in JITTER_SPAN_MHZ:
        worst = None
        cfgs = []
        for drift in DRIFT_SPAN_KHZ_MIN:
            for branch in ("analog", "counting"):
                key = f"{branch}/j{jitter:g}/d{drift:g}"
                sa, sj, ga, gj, deltas, pins = _config_arrays(
                    jitter, drift, branch, N_SWEEPS, RNG)
                ea, ej = float(np.std(sa)), float(np.std(sj))
                va, sea = pm_cells(ea, ea / np.sqrt(2 * (N_SWEEPS - 1)))
                vj, sej = pm_cells(ej, ej / np.sqrt(2 * (N_SWEEPS - 1)))
                rows.append((key, "shift_err_unreferenced", va, sea,
                             "MHz", "per-sweep sd over sweeps"))
                rows.append((key, "shift_err_paired", vj, sej,
                             "MHz", "per-sweep sd, the offset cancelled"
                             " by the cell pin"))
                ratio, ratio_se = _jack_ratio(sa, sj)
                vr, ser = pm_cells(ratio, ratio_se)
                rows.append((key, "shift_err_ratio", vr, ser, "ratio",
                             "paired over unreferenced, delete-one"
                             " jackknife se. Smaller favours paired"))
                wratio, wse = _jack_ratio(ga, gj)
                vwr, sewr = pm_cells(wratio, wse)
                wd = abs(1.0 - wratio) / wse if wse > 0 else 0.0
                rows.append((key, "width_err_ratio", vwr, sewr, "ratio",
                             "expected at parity, the photon budget is"
                             " conserved and no width is shared (this"
                             f" row: {wd:.1f} sigma from one)"))
                cfgs.append((ratio, ratio_se, key))
                if worst is None or ratio > worst[0]:
                    worst = (ratio, ratio_se, key)
                if jitter == JITTER_SPAN_MHZ[0] and drift == 0.0:
                    limits[branch] = (ratio, ratio_se, key,
                                      float(np.std(np.asarray(sa)
                                            - np.asarray(deltas))),
                                      float(np.std(pins)))
        per_jitter[jitter] = worst
        ordered = sorted(cfgs, key=lambda r: r[0], reverse=True)
        runner = ordered[1]
        state, dist, margin, licensed_by = _criterion_state(
            worst[0], worst[1], runner[0], runner[1])
        vw, sew = pm_cells(worst[0], worst[1])
        rows.append((f"span_j{jitter:g}", "worst_shift_ratio", vw, sew,
                     "ratio",
                     "max over the drift span and both branches at this"
                     f" excursion ({worst[2]}). The err is the selected"
                     " configuration's own se, read with the margin"
                     " beside it: the runner-up"
                     f" ({runner[2]}) sits {margin:.1f} combined sigma"
                     " below. A sub-one margin whose candidates' own"
                     " states disagree makes the criterion row say"
                     " unresolved, and one whose candidates agree"
                     " leaves which configuration is worst open, not"
                     " the side"))
        side = "below" if dist >= 0 else "above"
        note = (f"the worst ratio sits {abs(dist):.1f} sigma of its"
                f" own se {side} the {RATIO_THRESHOLD:g} threshold,"
                f" with a selection margin of {margin:.1f} sigma to the"
                " runner-up")
        if state == "unresolved":
            note += (f". The side is not licensed at one sigma, here by"
                     f" {licensed_by}, so this row says unresolved")
        rows.append((f"span_j{jitter:g}", "criterion", state, "", "",
                     note))
        per_jitter_states[jitter] = state
    for branch, (ratio, se, key, f_unref, pin_sd) in sorted(
            limits.items()):
        j0 = JITTER_SPAN_MHZ[0]
        decomp = float(np.sqrt((f_unref ** 2 + pin_sd ** 2)
                               / (f_unref ** 2 + j0 ** 2)))
        d_thr = (RATIO_THRESHOLD - ratio) / se
        d_par = (1.0 - ratio) / se
        thr_side = "below" if d_thr >= 0 else "above"
        par_side = "below" if d_par >= 0 else "above"
        vl, sl = pm_cells(ratio, se)
        rows.append(("limit", f"clean_lock_ratio_{branch}", vl, sl,
                     "ratio",
                     f"restates {key}'s ratio under its decision-facing"
                     f" name: {abs(d_thr):.1f} sigma {thr_side} the"
                     f" {RATIO_THRESHOLD:g} threshold and"
                     f" {abs(d_par):.1f} sigma {par_side} parity."
                     " Parity is the floor only at exactly zero lock"
                     " noise. The derived row beside this one carries"
                     " the one-line identity"))
        sep = abs(decomp - ratio) / se if se > 0 else 0.0
        if sep >= 2.0:
            raise RuntimeError(
                f"the {branch} error-budget decomposition disagrees with"
                f" the measured clean-lock ratio by {sep:.1f} sigma")
        rows.append(("check", f"clean_lock_decomposition_{branch}",
                     f"{decomp:.2f}", "", "ratio",
                     "a consistency companion, not a separate rung:"
                     " sqrt((f^2+p^2)/(f^2+j^2)) recombines the run's"
                     f" measured fit error (f={f_unref:.5f} MHz, the"
                     " unreferenced residuals against the injected"
                     f" offsets) and pin residual (p={pin_sd:.5f} MHz,"
                     " the joint fit's pinned offset against the"
                     " injected one) with the design excursion"
                     f" j={j0:g} MHz. It sits {sep:.1f} sigma of the"
                     " measured row's se from it, and a decomposition"
                     " error above about two sigma is what it would"
                     " catch. Empty err: recomputable from the three"
                     " quoted operands"))
    states = per_jitter_states
    summary = " / ".join(f"{j:g}: {states[j]}" for j in JITTER_SPAN_MHZ)
    rows.append(("boundary", "criterion_by_excursion", summary, "", "",
                 "the criterion's state at each spanned excursion class,"
                 " from the per-class rows above. The boundary lies where"
                 " the state changes, and an unresolved class means the"
                 " run's own error does not pick a side there"))
    rows.append(("design", "ratio_threshold", f"{RATIO_THRESHOLD:g}",
                 "", "ratio",
                 "the adjudication constant: a design choice with no"
                 " record source, owner-adjustable. Each criterion and"
                 " limit row carries its distance to it, so moving"
                 " it re-reads the table"))
    rows.append(("design", "n_sweeps_per_configuration", str(N_SWEEPS),
                 "", "sweeps",
                 "the Monte-Carlo sample behind every se here. An exact"
                 " count, so the empty err is not a gap"))
    rows.append(("registry", "record_depth_note", "not binding", "", "",
                 "the 2025 archive's records ran 2000 points and the"
                 " campaign recommendation is 40000 (docs/plan/07). Both"
                 " sit far under the two stated per-channel ceilings,"
                 " by 25 to 500 times on the Agilent's 1 Mpts and 250"
                 " to 5000 on the WaveSurfer 10's 10 Mpts (the same"
                 " table, with no per-channel figure stated for the"
                 " WS3104z). The chapter's tighter figure is the"
                 " export-path cap, 64 k points, 1.6 times above the"
                 " recommended 40000, and whether that cap is per"
                 " channel with two enabled is unstated in the record,"
                 " so the no-penalty reading is conditional on it."
                 " Both modes run at one depth here"))
    rows.extend(_sensitivity_rows())
    rows.append(("decision", "adopt_paired_default", "conditional", "",
                 "",
                 "the criterion rows decide by excursion class, with"
                 " unresolved classes named as unresolved. The lock"
                 " characterisation the plan already schedules"
                 " (docs/plan/12, the drift and excursion rows) measures"
                 " the class the apparatus is actually in, and the"
                 " geometry choice follows that measurement. Threshold"
                 f" {RATIO_THRESHOLD:g} owner-adjustable. Each criterion"
                 " and limit row carries its distance in sigma, so"
                 " the threshold can be moved and re-read"))

    _assert_verdict_rows(rows)

    dst = C.RESULTS_DIR / "paired_reference_forecast.csv"
    with open(dst, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit", "note"])
        # column names follow the results/ convention (sobol et al.):
        # the first column is the row GROUP, the second the row NAME,
        # so a reference tag reads ref:stem:<group>:<name>
        w.writerows(rows)
    wtxt = "; ".join(f"j{j:g}: {per_jitter[j][0]:.2f} {states[j]}"
                     for j in JITTER_SPAN_MHZ)
    print(f"wrote {dst} ({len(rows)} rows); worst by excursion {wtxt}; "
          "decision conditional")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

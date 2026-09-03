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
import os
import re
import sys
import zlib
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.special import voigt_profile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# _producer_lock lives in scripts/, which Python puts on sys.path only
# when a script is run DIRECTLY. A test that loads this module by path
# gets no such favour, and three sibling test files do exactly that - two
# of them failed at collection and a third swallowed the ImportError in a
# bare except and reported a pass. Making the import self-sufficient is
# cheaper than remembering.
sys.path.insert(0, str(Path(__file__).resolve().parent))  # _producer_lock lives here
from _producer_lock import take_producer_lock     # noqa: E402

from rb5s6s import config as C  # noqa: E402
from rb5s6s.pmfmt import pm_cells  # noqa: E402
from rb5s6s.workers import n_workers  # noqa: E402

RNG_SEED = 20260902  # the base of every per-task seed below;
#   changing it changes every quoted cell, and the CSV
#   reproduces byte for byte under it at any worker count

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
N_SWEEPS = 384           # Monte-Carlo sweeps per configuration, PER
#   REPLICATE. The grid concatenates N_GRID_REPLICATES of these, so the
#   sample behind a grid se is the product, and the sensitivity block
#   has its own sample and its own replicate count. This constant is
#   not by itself the denominator of anything, and this comment said
#   it was the sample behind every se until the grid gained replicates
# The error-budget identity's tolerance, ABSOLUTE and not in sigma.
# A sigma bar tightens as the sample grows, so a producer calibrated at
# one draw refuses to write at six and refuses harder at twelve, while
# the thing it is meant to catch - a wrong decomposition - does not
# move with the sample at all. Measured over 48 independent draws the
# identity holds to -0.0012 +- 0.0074 and the 2-sigma bound on any real
# bias is 0.015, so this is a little over three times that bound: loose
# enough that noise never trips it, tight enough that a per-cent-level
# model error does.
DECOMP_ABS_TOL = 0.05

N_GRID_REPLICATES = 6    # independent base seeds per GRID configuration.
# The grid's rows are what docs/big_picture/09 quotes to a reader deciding
# whether to expose a nanofibre, and they were SINGLE DRAWS. Drawing the
# committed cell analog/j0.028/d5 six times at 384 sweeps gave a mean of
# 0.668 with sd 0.039, against a file that then stood at 0.716 +- 0.033,
# a value this replication retired. RE-DERIVE IT
# with this producer's own parts, in about half a minute:
#
#     for r in range(6):
#         (_k, arrays, _pid) = _cfg_job((0.028, 5.0, "analog", 384, r))
#         print(_jack_ratio(arrays[0], arrays[1]))
#
# and take the mean and the sample sd of the six. The seed-to-seed
# scatter EXCEEDED the printed within-draw error, the committed value sat at
# the top of the range, and the 0.7 threshold the page's sentence turns on
# lay inside it. Two of six draws cleared it and four did not.
#
# The jackknife was not wrong - 0.039 against 0.033 is consistent at six
# samples. One draw was simply one draw. Each sweep here draws its own time
# within the session, so sweeps are independent and replicates CONCATENATE:
# six replicates are 2304 i.i.d. sweeps, every downstream sd and jackknife
# stays valid, and the error falls by root six.
N_SENS_REPLICATES = 6    # independent base seeds per sensitivity row.
# NOT decoration and not a default, and the number below is MEASURED FROM
# THE SHIPPED CODE rather than from the construction that preceded it -
# an earlier version of this comment quoted a range from the pre-repair
# per-tag seeding, which no longer existed by the time it was read.
# The marginal row is GAMMA_FIBRE at twice its value: it shifts the ratio
# by 1.85 +- 0.36 times one run's error over these six seeds, so a SINGLE
# seed carries a spread of about 0.9 and could land anywhere from the bar
# at 1.0 to nearly three times it. Six replicates are what put the verdict
# on the right side of that bar reproducibly, and the scatter is printed
# on the row so a reader can see how far from it the answer sits.
N_SWEEPS_SENS = 48       # sample for the sensitivity rows and their
#   baseline, which need direction and distinguishability, not the third
#   digit
RATIO_THRESHOLD = 0.7    # the adjudication constant: the design choice of
#   what counts as a decisive gain, owner-adjustable, with no record
#   source. Each criterion and limit row carries its distance to it in
#   sigma, so a reader can move it and see what follows


def _task_seed(*parts) -> int:
    """A seed derived from the task's own identity, so a configuration
    draws the same numbers whatever order the tasks run in and whatever
    else is in the grid.

    zlib.crc32 rather than hash(): string hashing is per-process
    randomised, so a hash-derived seed would move between runs and fail
    freshness forever - the lesson run_scenario_forecast already
    carries. Identity rather than index: inserting a class into a span
    must not renumber the classes after it and move numbers that had no
    reason to move.
    """
    key = "|".join(f"{p}" for p in parts)
    return (RNG_SEED + zlib.crc32(key.encode())) % (2 ** 31)


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


# A pooled map dies rather than hangs. Without a timeout a spawn child
# that cannot import its function's defining module leaves the parent
# blocked in `map` forever, and a gate then reports nothing at all
# instead of a failure - which is strictly worse, because a hang has to
# be noticed by a human while a failure notices itself. Measured
# 2026-09-02 by hanging exactly that way for the length of a gate.
# The budget is generous: since the grid gained six replicates per
# configuration it runs in about two and a half minutes across six
# workers, so ten minutes is still several times the real cost and is
# only ever reached by a fault.
_POOL_TIMEOUT_S = 600


def _pooled_map(fn, tasks, nw):
    """`pool.map` with a deadline, or the sequential path when nw is 0.

    The sequential path is not a fallback, it is the DEFAULT: this
    producer runs single-process unless RB5S6S_WORKERS says otherwise,
    and the pooled path must return the identical answer, which is what
    per-task seeding buys and the determinism plant holds.
    """
    if not nw:
        return [fn(t) for t in tasks]
    import multiprocessing as _mp
    with _mp.get_context("spawn").Pool(
            min(nw, len(tasks)), initializer=_init_cfg_worker) as pool:
        try:
            return pool.map_async(fn, tasks).get(_POOL_TIMEOUT_S)
        except _mp.TimeoutError:
            pool.terminate()
            raise RuntimeError(
                f"the pooled map did not finish in {_POOL_TIMEOUT_S}s. "
                "Two causes reach here and they need different probes. If "
                "a worker cannot IMPORT this module the sequential path "
                "will not show it, because RB5S6S_WORKERS=0 never spawns: "
                "run one job through a spawn Pool by hand, or read the "
                "child's traceback on stderr. If instead the work is "
                "merely slow, RB5S6S_WORKERS=0 reproduces it and is the "
                "right probe.") from None


def _sens_verdict(rel, rel_err):
    """Does a doubled or halved constant move the ratio by more than
    the error one run has on it?

    Extracted so every branch is testable, as `_criterion_state` above
    already is. It was welded into `_sensitivity_rows` with no plant on
    any branch until 2026-09-02.

    THREE STATES, NOT TWO. A quantity whose estimate straddles the bar
    has no side, and forcing one is how the previous rule shipped a
    "yes" that cleared by 0.005 and reversed at four times the
    replicates. `at the bar` says so instead.
    """
    if not np.isfinite(rel):
        raise RuntimeError(
            "a sensitivity shift came out non-finite, which means the"
            " run error it divides by was zero: the baseline jackknife"
            " collapsed and the row would state a verdict about nothing")
    lo, hi = abs(rel) - rel_err, abs(rel) + rel_err
    if lo >= 1.0:
        return "yes"
    if hi < 1.0:
        return "no"
    return "at the bar"


def _sens_job(task):
    """One replicate of one perturbation, pure in its own task.

    Module level and picklable because the replicates are pooled: this
    block went from 19 evaluations to 108 when the verdict gained its
    replicates, which is a minute sequentially and about ten seconds
    across the workers seam.

    THE SEED IS THE REPLICATE'S, NOT THE TAG'S, and that is the whole
    design. Every perturbation inside one replicate draws the SAME
    stream as that replicate's baseline - common random numbers - so
    the difference between them is the constant's effect and not two
    samples' worth of noise. Seeding per tag instead made thirteen
    insensitive rows scatter to +-1.9 sigma and manufactured four
    "yes" verdicts out of nothing at all.
    """
    rep, name, factor = task
    rng = np.random.default_rng(_task_seed("sens", str(rep)))
    g = globals()
    if name is not None:
        base = g[name]
        new = base * factor
        g[name] = int(new) if name == "N_POINTS" else new
    try:
        sa, sj = _config_arrays(0.028, 5.0, "analog", N_SWEEPS_SENS, rng)[:2]
        ratio, se = _jack_ratio(sa, sj)
    finally:
        if name is not None:
            g[name] = base
    # the pid rides along so a determinism plant can prove it actually
    # started workers. Without it, forcing the worker count to zero left
    # the equality test comparing the sequential path against itself and
    # passing - the vacuous shape this record keeps finding.
    return (rep, name, factor), (float(ratio), float(se), os.getpid())


def _sensitivity_rows():
    """Nine design constants, each doubled and halved at the boundary-
    region configuration (the comb-limit excursion, the small drift, the
    analog branch), against a baseline drawn at the SAME seed - and the
    whole comparison repeated at N_SENS_REPLICATES independent base
    seeds.

    WHY REPLICATES AND NOT ONE SAMPLE. The pairing makes an insensitive
    row read +0.00 with a scatter of a few hundredths, which is what
    twelve of these eighteen rows do. It does not make the SENSITIVE
    rows precise: at one base seed the paired distance for
    GAMMA_FIBRE_x2 measured anywhere from -0.01 to +1.63 sigma over six
    seeds, so a yes/no taken from a single draw is a coin flip on
    exactly the rows where the answer matters. Each row therefore
    carries the MEAN distance over the replicates and the standard
    error of that mean, and the verdict is taken from the mean less
    that error - a row reads yes only where the replicates support it
    at their own edge.

    Eight of the nine constants keep the common-random-number pairing.
    N_POINTS is the ninth and cannot: changing the draw count changes
    the stream, so its two rows are unpaired and say so. The replicate
    scatter diagnoses this without being told: those two rows are the
    only ones whose verdict comes out `at the bar`, because their
    estimate straddles it. Their scatter is NOT an order above the
    others - GAMMA_FIBRE_x2 carries +-0.36 against N_POINTS_x2's +-0.40 -
    so the discriminator is the verdict state, not the size of the
    scatter, and an earlier version of this docstring claimed the
    latter.

    The combination of the two jackknife errors assumes independence
    and so overstates the denominator for the paired rows, which makes
    every no conservative. The verdict is distinguishability, not a
    threshold side.

    WHY OVERRIDING MODULE CONSTANTS IS SAFE HERE, restated because the
    old reason expired. It used to be "one process, one thread"; the
    block is now POOLED across spawn workers. What makes it safe is
    that a spawn worker holds its OWN copy of this module, each job
    sets and restores its constant inside a finally, and jobs within a
    worker run one after another - so no job ever observes another's
    override. A fork start method would break that and this producer
    does not use one."""
    tasks = [(r, None, 1.0) for r in range(N_SENS_REPLICATES)]
    tasks += [(r, name, fac)
              for name in SENS_NAMES
              for fac in (2.0, 0.5)
              for r in range(N_SENS_REPLICATES)]
    got = dict(_pooled_map(_sens_job, tasks, n_workers()))

    def _sens_stats(name, fac):
        """The two numbers a sensitivity row owes, on their own scales.

        THE PAIRED DIFFERENCE FIRST. Each replicate contributes
        d_r = v_r - b_r, perturbed minus baseline at the SAME seed. The
        pairing makes d_r reproducible where v_r and b_r separately are
        not, so the mean of d and the standard error of that mean
        estimate the shift and how well it is known.

        `z` IS WHETHER THE SHIFT IS REAL. mean(d) over its own standard
        error. It reaches sixteen for a shift of nine per cent, because
        a perfectly reproducible small effect is exactly what pairing
        is for.

        `rel` IS WHETHER THE SHIFT MATTERS, and it is the verdict's
        subject. The shift in units of the error ONE run has on the
        ratio, which is the jackknife se a campaign actually gets.
        Dividing instead by hypot(vse, bse), as this function did
        until 2026-09-02, combines two runs' independent errors for a
        quantity measured once, discards the pairing, and is
        conservative by about root two.
        """
        d, bses = [], []
        for r in range(N_SENS_REPLICATES):
            b, bse = got[(r, None, 1.0)][:2]
            v, _vse = got[(r, name, fac)][:2]
            d.append(v - b)
            bses.append(bse)
        a = np.asarray(d, float)
        sd = float(a.std(ddof=1)) if len(a) > 1 else 0.0
        sem = sd / np.sqrt(len(a)) if sd > 0 else 0.0
        z = float(a.mean() / sem) if sem > 0 else float("inf")
        run_se = float(np.mean(bses))
        rel = float(a.mean() / run_se) if run_se > 0 else 0.0
        rel_err = float(sem / run_se) if run_se > 0 else 0.0
        return rel, rel_err, z

    base_vals = np.asarray([got[(r, None, 1.0)][0]
                            for r in range(N_SENS_REPLICATES)], float)
    base_ratio = float(base_vals.mean())
    base_se = float(base_vals.std(ddof=1) / np.sqrt(len(base_vals)))
    vb, sb = pm_cells(base_ratio, base_se)
    rows = [("sensitivity", "baseline", vb, sb, "ratio",
             "the unperturbed boundary-region configuration"
             f" (analog/j0.028/d5), averaged over {N_SENS_REPLICATES}"
             " independent base seeds at the sensitivity sample, its"
             " error the scatter of that mean. Every row below is read"
             " against this one, each replicate against its own"
             " baseline so the common-random-number pairing survives"
             " the averaging")]
    for name in SENS_NAMES:
        for tag, factor in (("x2", 2.0), ("half", 0.5)):
            dsig, dsem, zsig = _sens_stats(name, factor)
            if abs(dsig) < 0.005:
                dsig = 0.0
            sep = _sens_verdict(dsig, dsem)
            vals = np.asarray([got[(r, name, factor)][0]
                               for r in range(N_SENS_REPLICATES)], float)
            note = (f"{name} at {tag} shifts the ratio by "
                    f"{dsig:+.2f} +- {dsem:.2f} times the error one run"
                    f" has on it, over {N_SENS_REPLICATES} base seeds,"
                    f" and the shift itself is resolved at"
                    f" {abs(zsig):.0f} sigma of its own paired error."
                    f" Matters at one run's error: {sep}")
            if name == "N_POINTS":
                note += (". This row changes the draw count, so the"
                         " common-random-number pairing is broken here")
            vr, sr = pm_cells(float(vals.mean()),
                              float(vals.std(ddof=1) / np.sqrt(len(vals))))
            rows.append(("sensitivity", f"{name}_{tag}", vr, sr, "ratio",
                         note))
    return rows


_DIST_RE = re.compile(r"\d+(?:\.\d+)? sigma")


def _assert_decomposition(branch, decomp, ratio, sep):
    """Refuse to write when the error-budget identity disagrees past
    the absolute tolerance.

    EXTRACTED so it can be planted. It was welded inline in `main()`,
    where reaching it needed a monkeypatched `_config_arrays` and a
    full run, and `grep decomp tests/` returned nothing at all - a
    raise path with no coverage anywhere, which is this record's
    "model-form switch that has never been thrown" wearing a different
    coat.

    ABSOLUTE, not in sigma, and the reason is in DECOMP_ABS_TOL's own
    comment: a sigma bar tightens as the sample grows while the thing
    it catches does not move with the sample at all.
    """
    gap = abs(decomp - ratio)
    if gap >= DECOMP_ABS_TOL:
        raise RuntimeError(
            f"the {branch} error-budget decomposition disagrees with the"
            f" measured clean-lock ratio by {gap:.4f}, past the absolute"
            f" tolerance {DECOMP_ABS_TOL:g}. That is {sep:.1f} of the"
            " measured row's se, but the tolerance is absolute on"
            " purpose: this is a claim about the model, and a model"
            " error does not shrink when the sample grows")


def _parity_aggregate_row(parity_sigmas):
    """The count the fibre scenario's prose quotes, emitted as a row.

    WHY A ROW AND NOT A SENTENCE. The claim "the width-error ratio
    measures at parity in thirty of its thirty-two rows" is an
    aggregate over this file, and a hand-typed aggregate is outside the
    `ref:` mechanism that keeps every neighbouring number in that
    paragraph honest. It was correct when written and had nothing
    holding it there. Computing it from the rows the producer is about
    to write means the sentence and the file cannot disagree.

    A handful of exceptions is not a defect: 32 draws under parity
    put about one and a half rows past two sigma, so two or three is
    the expected excursion and the row's note carries the count the
    run actually found. NO NUMBER IS WRITTEN HERE - an earlier version
    said "two" and the row emitted three the first time the sample
    grew.
    """
    ds = [abs(v) for _k, v in parity_sigmas]
    if not ds:
        raise RuntimeError(
            "no width_err_ratio row asserts parity, so the aggregate the"
            " fibre scenario quotes has an empty population - which is"
            " the vacuity this row exists to make visible")
    within = sum(1 for d in ds if d < 2.0)
    return ("check", "width_ratio_within_2sigma", str(within), str(len(ds)),
            "count",
            f"{within} of {len(ds)} width-error ratio rows sit within two"
            " sigma of parity, which is what the paired acquisition"
            " predicts: the photon budget is conserved and no width is"
            " shared. The err cell carries the population, not an"
            " uncertainty. Under parity 32 draws put about one and a"
            " half rows past two sigma, so the excursions are the"
            " expected count rather than a defect. The classification"
            " is made on the float, not on the rounded form printed in"
            " each row's note: rows on either side of the bar can print"
            " the same one-decimal string, and one of these does."
            " Quoted by the fibre"
            " scenario of docs/big_picture/09.")


def _assert_verdict_rows(rows):
    """The producer proves the universal its notes assert - every
    criterion and limit row carries a numeric sigma distance and names
    the threshold - with both populations pinned, so a silent rename or
    a keyword-only note is caught. Module-level and pure so the test
    module can plant every failure shape against it."""
    # the sensitivity rows state a verdict word, so they are the
    # prover's business too. They were outside it, which is how a
    # column contradicted by its own err column reached the index.
    sens = [r for r in rows if r[0] == "sensitivity" and r[1] != "baseline"]
    if len(sens) != 2 * len(SENS_NAMES):
        raise RuntimeError(
            f"{len(sens)} sensitivity rows for {len(SENS_NAMES)} constants"
            " doubled and halved: the block is short and a reader would"
            " not see which perturbation is missing")
    for r in sens:
        if "Matters at one run's error:" not in r[5]:
            raise RuntimeError(
                f"sensitivity row {r[1]} states no verdict, so its note"
                " and its err column license nothing together")
        if "times the error one run has on it" not in r[5]:
            raise RuntimeError(
                f"sensitivity row {r[1]} states a verdict without naming"
                " the denominator its number is on. A row carrying a"
                " sigma distance and an err cell owes the reader one"
                " scale, or it must say which it used")

    # AND THE CHECK ROWS, whose notes now carry the strongest
    # universals in the file: a raise threshold, a population count and
    # a statement about what a number means. The prover's own docstring
    # says it proves the universals its notes assert, and these were
    # outside it.
    checks = [r for r in rows if r[0] == "check"]
    if not checks:
        raise RuntimeError(
            "no check row was emitted, so the consistency companions "
            "and the parity count are absent and their absence would "
            "read as agreement")
    for r in checks:
        if not r[5].strip():
            raise RuntimeError(
                f"check row {r[1]} carries no note, so what it asserts "
                "is unstated and a reader cannot act on it")
        if r[1].startswith("clean_lock_decomposition_sigma") and \
                "raises" not in r[5]:
            raise RuntimeError(
                f"{r[1]} states a separation without naming the "
                "condition the producer raises on, so a reader cannot "
                "tell how close it is to writing nothing at all")

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


def _cfg_job(args):
    """One configuration, self-contained: its seed comes from its own
    identity, so this returns the same arrays whatever else is running
    and in whatever order. That is what makes the pool below safe, and
    tests/test_paired_pool_determinism.py pins it."""
    jitter, drift, branch, n_sweeps, rep = args
    rng = np.random.default_rng(
        _task_seed("cfg", str(rep), branch, jitter, drift))
    # The pid is a THIRD element, deliberately outside the value the
    # grid keys on: an equality plant must be able to prove that workers
    # really started, and must not have that proof leak into the arrays
    # it compares. Forcing the worker count to zero used to pass every
    # test in the determinism file, because the pooled arm was compared
    # against itself.
    return ((branch, jitter, drift, rep),
            _config_arrays(jitter, drift, branch, n_sweeps, rng),
            os.getpid())


def _init_cfg_worker():
    """One BLAS thread per worker: these are many small least-squares
    solves, so nested threading costs more than it buys."""
    import os as _os
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        _os.environ.setdefault(v, "1")


def _run_grid(n_sweeps):
    """Every configuration of the grid, pooled or sequential, keyed by
    identity. `pool.map` preserves order, and each job is a pure
    function of its arguments, so the mapping is the same either way -
    which is the contract rb5s6s.workers states and this producer's
    plant measures."""
    jobs = [(j, d, b, n_sweeps, r)
            for j in JITTER_SPAN_MHZ
            for d in DRIFT_SPAN_KHZ_MIN
            for b in ("analog", "counting")
            for r in range(N_GRID_REPLICATES)]
    per_rep: dict[tuple, list] = {}
    for (branch, jitter, drift, rep), arrays, _pid in _pooled_map(
            _cfg_job, jobs, n_workers()):
        per_rep.setdefault((branch, jitter, drift), []).append((rep, arrays))
    out = {}
    if len(per_rep) != 2 * len(JITTER_SPAN_MHZ) * len(DRIFT_SPAN_KHZ_MIN):
        raise RuntimeError(
            f"the grid gathered {len(per_rep)} configurations, not "
            f"{2 * len(JITTER_SPAN_MHZ) * len(DRIFT_SPAN_KHZ_MIN)}: a "
            "configuration was dropped and its row would be missing")
    for key, got in per_rep.items():
        # EVERY REPLICATE, PROVED AT RUNTIME. The design row this
        # producer emits states that each configuration carries
        # N_SWEEPS * N_GRID_REPLICATES sweeps and that every standard
        # error falls by root six. That is arithmetic until something
        # checks it against what was gathered: a replicate lost in the
        # pool would shorten the concatenation, inflate every se, and
        # leave a valid-looking CSV that no test could fail - the
        # worker-count equality would not see it either, because the
        # loss would be identical on both paths.
        if len(got) != N_GRID_REPLICATES:
            raise RuntimeError(
                f"{key} gathered {len(got)} replicates, not "
                f"{N_GRID_REPLICATES}. Every error on this "
                "configuration would be wrong and the row would still "
                "look well formed")
        if len({r for r, _a in got}) != len(got):
            raise RuntimeError(
                f"{key} gathered a repeated replicate index among "
                f"{len(got)}, so the concatenation holds one sample "
                "twice and its errors are understated. This tests "
                "uniqueness against what arrived, not against the "
                "expected count, so it stays true if the count check "
                "above is ever moved or removed")
        # AND THE SAMPLE, NOT ONLY THE CONTAINER. The three checks
        # above count replicates and their indices, and two shortfall
        # shapes walk straight past all of them: a replicate whose
        # arrays are SHORT, and a replicate carrying another's payload
        # under its own index. Both leave the row count right, the
        # index set right, and every error wrong.
        want = n_sweeps * N_GRID_REPLICATES
        # EVERY ARRAY, NOT ARRAY ZERO. A replicate is the six-tuple
        # (s_unref, s_joint, g_unref, g_joint, deltas, pins), and the
        # first version of these two checks looked at position 0 alone
        # because that is the array the rest of the function already
        # had in scope. `shift_err_ratio` - the row this whole file
        # exists to report - is built from s_joint, at position 1. A
        # plant that duplicated one replicate's s_joint onto another,
        # leaving s_unref distinct and correctly sized, passed both
        # checks and reached the CSV.
        n_arrays = len(got[0][1])
        for _r, _a in got:
            for _i, _arr in enumerate(_a):
                if len(_arr) != n_sweeps:
                    raise RuntimeError(
                        f"{key} replicate {_r} array {_i} carries "
                        f"{len(_arr)} sweeps, not {n_sweeps}: the "
                        f"concatenation would be short of {want} and "
                        "every se built on it inflated, with the row "
                        "still well formed")
        for _i in range(n_arrays):
            _sig = [tuple(a[_i][:8]) for _r, a in got]
            if len(set(_sig)) != N_GRID_REPLICATES:
                raise RuntimeError(
                    f"{key} has two replicates with identical draws in "
                    f"array {_i} under different indices, so the "
                    "concatenation repeats a sample there and the "
                    "errors built on it are understated. The index "
                    "check above cannot see this, and neither can a "
                    "check that only reads array zero")
        # SORTED BY REPLICATE, so the concatenation is the same
        # sequence whatever order the pool returned them in. This is
        # DEFENSIVE, not load-bearing today: `pool.map_async(...).get()`
        # returns in task order, measured at 192 jobs across four
        # worker processes, so the sort is currently a no-op. An
        # earlier version of this comment claimed the bytes would
        # otherwise depend on the worker count, which is not true of
        # the present code. It stays because a switch to
        # `imap_unordered`, or a partial gather, would make it true in
        # one edit and the failure would be silent.
        got.sort(key=lambda x: x[0])
        out[key] = tuple(
            [v for _rep, arrays in got for v in arrays[i]]
            for i in range(len(got[0][1])))
        # AND THE UNIVERSAL THE DESIGN ROW STATES, proved after the
        # join rather than inferred from the parts. The per-replicate
        # length check above catches a short replicate; this catches
        # anything that survives it, and it is the exact sentence the
        # emitted `design,grid_replicates` row asserts to a reader.
        for _arr in out[key]:
            if len(_arr) != want:
                raise RuntimeError(
                    f"{key} concatenated to {len(_arr)} sweeps, not "
                    f"{want}, so the design row's claim about the "
                    "sample behind every se on this configuration is "
                    "false and its errors are wrong")
    return out


def main() -> int:
    # A pooled producer is the one that most needs this: it holds most
    # of the machine for its whole run, so a second copy started because
    # the first "looked stuck" is both likelier and more damaging. The
    # the sequential producers took the lock and the three pooled ones
    # did not, which is exactly backwards. NO COUNT HERE: this comment
    # said "nineteen" where the tree held seventeen, wrong the hour it
    # was written, and a comment cannot derive what it asserts.
    take_producer_lock("run_paired_reference_forecast")
    rows = []
    per_jitter = {}
    per_jitter_states = {}
    limits = {}
    parity_sigmas: list[tuple[str, float]] = []
    grid = _run_grid(N_SWEEPS)
    for jitter in JITTER_SPAN_MHZ:
        worst = None
        cfgs = []
        for drift in DRIFT_SPAN_KHZ_MIN:
            for branch in ("analog", "counting"):
                key = f"{branch}/j{jitter:g}/d{drift:g}"
                sa, sj, ga, gj, deltas, pins = grid[(branch, jitter, drift)]
                ea, ej = float(np.std(sa)), float(np.std(sj))
                # THE ACTUAL SAMPLE, not the per-replicate constant. The
                # grid concatenates N_GRID_REPLICATES independent
                # replicates, so len(sa) is N_SWEEPS * N_GRID_REPLICATES
                # and using N_SWEEPS here would overstate every se by
                # root six.
                n_eff = len(sa)
                va, sea = pm_cells(ea, ea / np.sqrt(2 * (n_eff - 1)))
                vj, sej = pm_cells(ej, ej / np.sqrt(2 * (n_eff - 1)))
                rows.append((key, "shift_err_unreferenced", va, sea,
                             "MHz", "per-sweep sd over sweeps"))
                rows.append((key, "shift_err_paired", vj, sej,
                             "MHz", "per-sweep sd, the offset cancelled"
                             " by the cell pin"))
                ratio, ratio_se = _jack_ratio(sa, sj)
                vr, ser = pm_cells(ratio, ratio_se)
                rows.append((key, "shift_err_ratio", vr, ser, "ratio",
                             "paired over unreferenced, delete-one"
                             " jackknife se over the concatenated"
                             " replicates. Smaller favours paired. THE"
                             " ERROR IS THE ESTIMATE'S, NOT ONE"
                             " CAMPAIGN'S: a single run of"
                             f" {N_SWEEPS} sweeps would land within"
                             " about root"
                             f" {N_GRID_REPLICATES} of this se of the"
                             " value, which is the spread the row below"
                             " carries"))
                # THE DIRECT ESTIMATE, not a surrogate. Scaling the
                # pooled se by root six assumes the jackknife scales
                # exactly as one over root n, which is unchecked and
                # measured 17 per cent LOW at the boundary
                # configuration - in the direction that understates
                # what the bench would see, on the row whose whole
                # purpose is telling a reader what one campaign gives.
                # The six per-replicate ratios are already in hand and
                # their sample sd IS the quantity, so the surrogate is
                # kept only where a replicate is degenerate.
                per_rep = []
                n_one = len(sa) // N_GRID_REPLICATES
                for _r in range(N_GRID_REPLICATES):
                    lo, hi = _r * n_one, (_r + 1) * n_one
                    per_rep.append(_jack_ratio(sa[lo:hi], sj[lo:hi])[0])
                _arr = np.asarray(per_rep, float)
                one_sd = float(_arr.std(ddof=1)) if len(_arr) > 1 else 0.0
                if not (one_sd > 0):
                    one_sd = ratio_se * np.sqrt(N_GRID_REPLICATES)
                vc, sec = pm_cells(ratio, one_sd)
                rows.append((key, "shift_err_ratio_one_campaign", vc, sec,
                             "ratio",
                             "the same ratio with the spread ONE"
                             f" {N_SWEEPS}-sweep campaign would see in"
                             " its own realised value, measured as the"
                             f" sample sd of the {N_GRID_REPLICATES}"
                             " per-replicate ratios rather than by"
                             " scaling the pooled error, which assumes"
                             " a root-n law and measured 17 per cent"
                             " low at analog/j0.028/d0, the"
                             " configuration the fibre scenario quotes."
                             " The"
                             " row above"
                             " states how well this file knows the"
                             " number. This one states what the bench"
                             " would get. They stopped being the same"
                             " quantity when the grid gained"
                             " replicates"))
                wratio, wse = _jack_ratio(ga, gj)
                vwr, sewr = pm_cells(wratio, wse)
                wd = abs(1.0 - wratio) / wse if wse > 0 else 0.0
                rows.append((key, "width_err_ratio", vwr, sewr, "ratio",
                             "expected at parity, the photon budget is"
                             " conserved and no width is shared (this"
                             f" row: {wd:.1f} sigma from one)"))
                # THE FLOAT, kept beside the row that rounds it. The
                # aggregate below used to recover this by regexing its
                # own printed note, so a row anywhere in [1.95, 2.05)
                # was classified by its PRINTED form: analog/j0.009/d5
                # measures 2.0002 and the published count was right by
                # four decimal places and by luck. The class is a
                # threshold comparison made at unequal precision, and
                # the remedy is to stop re-making the comparison at a
                # different number of digits than the value carries.
                parity_sigmas.append((key, float(wd)))
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
        # THE SEPARATION IS A ROW, not only a crash condition, and the
        # row reports the ABSOLUTE gap beside the sigma because only
        # the first is a statement about the model.
        #
        # AN EARLIER VERSION OF THIS COMMENT WAS WRONG AND SAID THE
        # OPPOSITE. It claimed the gap was fixed while the error fell,
        # so the sigma would grow with the sample and abort at eight
        # replicates. Measured over 48 independent draws at this
        # configuration: mean(decomp - ratio) is -0.0012 +- 0.0074,
        # which is 0.16 sigma from zero, and the sigma runs 0.17, 0.00,
        # 0.84, 1.78, 1.30, 0.84, 0.10 at 1, 2, 3, 6, 8, 12 and 48
        # replicates. It does not grow. THE IDENTITY HOLDS, the sigma
        # is a standard-normal deviate, and the two committed files
        # already refuted the claim without any new computation: a
        # fixed gap needed both branches to rise by root six, and the
        # counting branch fell from 1.2 to 0.95.
        rows.append(("check", f"clean_lock_decomposition_sigma_{branch}",
                     f"{sep:.2f}", "", "sigma",
                     "separation between the measured clean-lock ratio"
                     " and its own error-budget decomposition, in the"
                     " measured row's se. The absolute gap is the row"
                     f" beside this one, and the producer raises on THAT"
                     f" at {DECOMP_ABS_TOL:g}, not on the sigma: a"
                     " fixed sigma bar on an error that falls with the"
                     " sample tightens every time the sample grows, and"
                     " would refuse to write about one run in eleven"
                     " under an identity that holds. This sigma is a"
                     " standard-normal deviate and a large value is a"
                     " fluctuation, not a trend"))
        rows.append(("check", f"clean_lock_decomposition_gap_{branch}",
                     f"{abs(decomp - ratio):.4f}", "", "ratio",
                     "the absolute disagreement between the measured"
                     " clean-lock ratio and its own error-budget"
                     " decomposition, which is what a model error would"
                     " move and what the producer raises on. Measured"
                     " over 48 independent draws the identity holds to"
                     " 0.0012 +- 0.0074, so the tolerance of"
                     f" {DECOMP_ABS_TOL:g} is several times the scatter"
                     " and does not tighten as the sample grows"))
        _assert_decomposition(branch, decomp, ratio, sep)
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
    rows.append(("design", "grid_replicates", str(N_GRID_REPLICATES), "",
                 "count",
                 "independent base seeds per configuration, concatenated."
                 " Each sweep draws its own time within the session, so"
                 " sweeps are independent and replicates are simply more"
                 " sweeps: the grid carries"
                 f" {N_SWEEPS * N_GRID_REPLICATES} per configuration and"
                 " every se falls by root six against the single draw"
                 " this file used to report"))
    rows.append(("design", "n_sweeps_per_configuration", str(N_SWEEPS),
                 "", "sweeps",
                 "the per-replicate sample. A GRID se stands on this"
                 f" times the {N_GRID_REPLICATES} replicates above it,"
                 " and the sensitivity block has its own sample and its"
                 " own replicate count, so this number is not by itself"
                 " the denominator of anything in the file. An exact"
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

    rows.append(_parity_aggregate_row(parity_sigmas))
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

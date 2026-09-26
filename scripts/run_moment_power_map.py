#!/usr/bin/env python
"""The S0 power of the truncated odd moments, across the conditions the archive spans.

THE QUESTION, the owner's, asked three times before it could be run: use the
twin to generate synthetic traces across many conditions -- noise level AND
noise model, Lorentzian laser component, oscilloscope, window range -- and
measure the power of S0 that each truncated moment carries. That says what the
2025 dataset can still deliver and where the new campaign should drill.

WHY IT COULD NOT BE RUN BEFORE. The two generators had complementary
capabilities: `synthetic_traces` carried `gamma_l` and `laser_kind` and no
instrument layers, `build_world_trace` carried the layers and neither kernel
argument. This grid varies the Lorentzian component AND the oscilloscope, so
neither path could produce a single cell. Both now take both (2026-09-05).

WHAT IS ALREADY SETTLED, so this study does not re-derive it. On the noiseless
production path every windowed odd moment returns a slope of 3.000, not the
3/5/7 ladder: at a shift far below the line width each odd moment is dominated
by the same leading asymmetry. And the windowed fifth order does not converge
against a Lorentzian, recovering 570, 1858 and 5946 per cent at half-windows 8,
16 and 40 UNDER THE RETIRED CUMULANT BASIS this file computed on before owner
order O49 (2026-09-22): mu_5 = kappa_5 + 10 mu_2 mu_3 carries a cross-term
kappa_5 does not, so these three figures are not re-stated as mu5's own and
are pending re-measurement on the moment basis this file now computes
(TRUE_SIGN's derivation below has the sign half of that difference already).
Those results are from ONE noiseless configuration in either basis. This map
measures whether they hold across the grid, which is the difference between an
assertion and a boundary.

THE READMISSION BARS for mu5 and mu7 are fixed before the run and are NOT the
theoretical ladder: a correctly-behaving windowed mu5 at the archive's shift
SHOULD read 3 in magnitude of its power-law slope (the readmission bar is on
the fitted power, not on the moment's own sign or scale, so it is unmoved by
the cumulant-to-moment switch above), so a bar demanding 5 would strike a
working estimator. A cell readmits an order only if its recovered fraction
sits inside 0.9 to 1.1, its fitted power matches what the windowed theory
predicts for that cell's regime, and its residual against mu3 carries
information mu3 does not. A cell that merely fails to diverge is not a
channel.

    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_moment_power_map.py --one-cell
    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_moment_power_map.py
"""
from __future__ import annotations

import csv
import hashlib
import math
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from itertools import product
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import windows
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.lineshape import RAMP_SIDE                             # noqa: E402  (O27)
from rb5s6s.forecast import build_world_trace                      # noqa: E402
# MOMENTS, NOT CUMULANTS (owner order O33, A72). At orders 5 and 7 a cumulant is a difference
# of large terms and carries a cancellation the moment does not; below fourth order the two are
# identical (k2 = mu2, k3 = mu3 exactly), so switching changes only where it should.
from rb5s6s.moments import windowed_moments                     # noqa: E402
from rb5s6s.qc import median_standard_error                        # noqa: E402

OUT = C.RESULTS_DIR / ("moment_power_map_deep.csv" if os.environ.get("RB5S6S_MPM_DEEP")
                       else "moment_power_map.csv")

# ---- the grid, the full factorial the study asked for ---------------------
GAMMA_L = (0.0, 0.1, 0.3, 0.45)      # 0.45 tops kernel_k3.csv's measured range
NOISE_LEVEL = (0.002, 0.004, 0.012)  # the archive's level and a rung either side
# THE FIFTH AXIS, and it is the one this producer found rather than planned.
# `model_profile` sizes its internal convolution grid by the narrowest KERNEL
# and never by the shift (A33), so a small shift can sit inside a single cell.
# Measured here, noiseless and with the layers off: the windowed k3 power reads
# 2.8234 at W=8 and 2.7903 at W=16 with the shipped default, against 3.0033 and
# 3.0081 with the shift resolved and 3.000 from the analytic producer. So the
# default biases the exponent by about -0.2, and since the traces a precision
# needs go as a power of that exponent, the bias compounds. Both settings are
# run so the map measures the cost of the choice instead of inheriting it.
RESOLVE = (False, True)

T_C = 130.0
# One named line, because cascade.amplitude_factor and stark.companion_gamma_mhz
# are looked up PER PEAK: a synthetic label would not reach the physics they
# carry. 4192 is the strongest share and the peak the archive's exclusion rests
# on, so it is the line whose estimator most needs characterising.
PEAK = "4192"
# Every physics layer on. `drift` is off and `drift_mhz_total` is zero, not
# because drift does not matter but because the self-centred estimator is
# exactly immune to a rigid shift, so a drift arm here would vary an axis the
# answer cannot see, which would report that insensitivity as a result.
LAYERS = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
          "drift": False, "quantise": True, "randomise": False}

# THE SCOPE AXIS, one named resolution mode per instrument, because a scope
# with several modes does not define an axis until the mode is named. Each is
# that instrument's own default_mode in rb5s6s.instruments.
SCOPES = (("lecroy_ws3104z", "raw", 8.0),
          ("agilent_3054a", "hires", 12.0),
          ("rtm3004", "hires", 16.0))
# THE NOISE-MODEL AXIS COLLAPSED, and it was right to. It was crossed with the
# level as though the two were independent, but the production generator
# implements the MEASURED shot-like law and nothing else, so a white arm could
# only be had by bypassing the generator -- which is exactly what made the
# first version of this producer wrong. What varies the noise CHARACTER here
# is the scope: the ADC step is uniform and does not fall with the signal,
# while the shot-like sigma does, so the three depths span that contrast on
# the production path instead of beside it.
WINDOW = tuple(sorted(set(windows.LEGACY) | {4.0, 8.0, 16.0}))   # the legacy set plus this map's own octaves
S0_LADDER = ((0.364, 0.5, 0.73, 1.0, 2.0) if os.environ.get("RB5S6S_MPM_DEEP")
             else (0.18, 0.364, 0.73, 1.0, 2.0))    # archive 0.364 when set (0.348 since 2026-09-17), campaign 1.0
# THE DEEP LADDER STARTS AT THE ARCHIVE. The 0.18 rung's signal-to-scatter was
# 0.05 at four thousand traces, so no affordable budget makes it a
# measurement, and the deep run answers what the 2025 shift itself can carry.
# A rung at 0.5 brackets the boundary between the archive and the campaign.
ORDERS = (3, 5, 7)

from rb5s6s.reference_point import reference_point  # noqa: E402

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "the layered world's moments against power, a registered approximation of the joint twin"
_AP = reference_point()   # F313: the archive's line, read from the committed fit and the waist, never typed
GAMMA_COLL, SIGMA_LASER, TRANSIT = _AP["gamma_coll"], _AP["sigma_laser"], _AP["transit_fwhm"]
# THE TRACE COUNT IS THE STUDY'S OWN SUBJECT, not a convenience. At the
# archive's shift and noise level a single trace's third moment is far
# smaller than its own scatter, so the map must report the signal-to-scatter it
# achieved in each cell or a reader cannot tell a measured power from noise
# wearing one. Two thousand is not enough to clear that bar anywhere on this
# grid, and the file says so in min_snr_over_rungs rather than hiding it in a
# slope. (An earlier form of this comment quoted figures taken on the FIRST
# version of this producer, which generated traces by a different path. They
# were left behind when the generator moved and are removed rather than
# re-measured, since the file's own column now carries the statement.)
# Read from the environment so a SPAWNED CHILD sees it. The plant below first
# set this with `global`, which reaches the parent only: on macOS the start
# method is spawn, every worker re-imports this file, and the plant silently
# ran at the full size it thought it had reduced. Anything a worker needs
# travels in the task or the environment, never on the parent's module.
N_TRACES = int(os.environ.get("RB5S6S_MPM_TRACES", "2000"))
FINE = np.linspace(-40.0, 40.0, 32001)
# THE TRUE SIGN OF EACH ORDER, from the ramp's own MOMENTS -- the statistic this file's own
# quadrature actually returns (`windowed_orders`, through `windowed_moments`), not the cumulant
# the table quoted until owner order O49 (2026-09-22, "make sure that all cumulants are gone").
# **RE-DERIVED, NOT RENAMED, because the two bases disagree here**: mu_3 = kappa_3 exactly, but
# mu_5 = kappa_5 + 10 mu_2 mu_3 = 1/567 + 10 (1/18)(-1/135) = -4/1701 of S0^5, the OPPOSITE sign
# from kappa_5's own +1/567 (docs/methods/03), because the cross-term dominates. mu_7 was not
# hand-derived (it needs kappa_4 and kappa_6 too) but its sign is verified negative both directly,
# by numerical quadrature of (s-mean)^7 on the closed-form density, and through
# `rb5s6s.moments.windowed_moments` on `lineshape.stark_ramp` itself, so it is stated as
# checked rather than derived. On the package's side (lineshape.RAMP_SIDE, blue since the ruling
# of 2026-09-17) every one of mu_3, mu_5 and mu_7 is negative, unlike the cumulants' alternating
# -, +, - -- this table read the red side's signs for the hours after the kernel flipped (P3).
# A statistic built on the sign of a windowed moment is read against these, never
# against zero: the first form of the per-rung status keyed on the fraction
# NEGATIVE for every order and tagged every settled fifth-order rung NULL.
TRUE_SIGN = {3: -RAMP_SIDE, 5: -RAMP_SIDE, 7: -RAMP_SIDE}
# The rung-admission bar, and the null it is read against: under a coin flip
# the fraction's standard deviation is 0.5/sqrt(n), 0.011 at two thousand
# traces and 0.0025 at forty thousand, so 0.35 sits 13 and 60 standard
# deviations below one half. It is a settled-sign bar, not a significance bar.
WRONG_SIGN_MAX = 0.35


def windowed_orders(y, w, grid, orders=ORDERS):
    """Every order from ONE centring through the package estimator
    (`rb5s6s.moments.windowed_moments`): the window recentred until it
    stops moving, the pedestal removed from the trace's own far wings, the
    window started at the line's position rather than the trace's maximum.
    An unconverged fixed point returns NaN for every order. The copy this
    replaced recentred a fixed twenty times with the trace clipped at zero,
    which converged at this producer's bright fixed power on the wide windows
    and not on the narrow ones (the top rung at a 3.25 MHz half-window moved by
    two of its own standard errors between twenty and eighty passes)."""
    v, info = windowed_moments(grid, y, w, orders, centre0=0.0)
    if not info["converged"]:
        return {o: float("nan") for o in orders}
    return v


def selfcentred_moment(y, w, order, *, grid=None):
    """One order, the form the tests call."""
    return windowed_orders(y, w, FINE if grid is None else grid, (order,))[order]


def rung_status(frac_wrong_sign):
    """DIAGNOSTIC when the rung's sign is settled against the order's true
    sign, NULL when it is a coin flip; keyed on the PUBLISHED three-decimal
    value so a reader re-derives it from the file's own columns."""
    if not np.isfinite(frac_wrong_sign):
        return "NULL"
    return "DIAGNOSTIC" if round(float(frac_wrong_sign), 3) < WRONG_SIGN_MAX else "NULL"


def _trace(s0, gamma_l, level, adc_levels, seed, resolve):
    """One trace from the PRODUCTION generator, with every physics layer on.

    The first version of this producer called `model_profile` and added its
    own noise, which exercised none of blackbody, cascade depletion,
    saturation, drift or quantisation and could not vary the oscilloscope at
    all -- so it answered a narrower question than the one asked, and left the
    kernel unification built for it unused. `build_world_trace` is the unified
    path and carries all of them.

    The shift is set directly: `power_w` is 1.0 and `kappa` is the wanted S0,
    so the ladder below is a ladder in the shift itself rather than in a power
    whose calibration would then enter the answer.
    """
    return build_world_trace(
        1.0, s0, T_C, 0, 1, np.random.default_rng(seed), LAYERS,
        positions={PEAK: 0.0}, shares={PEAK: 1.0},
        gamma_coll=GAMMA_COLL, sigma_laser_fwhm=SIGMA_LASER,
        transit_fwhm=TRANSIT, power_max_w=1.0, cycles_at_max=1.0,
        drift_mhz_total=0.0, noise_frac_bright=level,
        adc_levels=adc_levels, gamma_l=gamma_l,
        resolve_shift=resolve, registry=_TWIN_STUDY)[:2]


def _cell(spec):
    """One grid cell: fit log|k_n| against log S0 over the ladder.

    SEEDED PER TASK from the cell's own coordinates, never from a shared
    counter, so the result cannot depend on the worker count or the order in
    which cells are dispatched.
    """
    gamma_l, level, scope, window, resolve = spec
    name, mode, bits = scope
    adc = int(round(2.0 ** bits))
    key = f"mpm:{gamma_l}:{level}:{name}:{mode}:{window}:{resolve}"
    base = zlib.crc32(key.encode()) % (2 ** 31)
    rows, rung_rows = [], []
    # ONE TRACE SET PER RUNG, SHARED BY EVERY ORDER, and it matters twice. The
    # first version keyed the seed on the order too, so mu3, mu5 and mu7 were
    # measured on different traces: that makes them independent BY
    # CONSTRUCTION, which would overstate the rank of the moment family exactly
    # where this plan asks whether three moments are three equations or one
    # equation read three ways. Sharing the set lets that covariance be
    # measured. It is also cheaper, but by 1.65 and not by the 3 this comment
    # first claimed: generating a trace costs 1.7 ms and taking one moment of
    # it 1.2 ms, so the generation this change removes is not the dominant
    # cost. The figure was corrected by measuring it rather than by reasoning
    # about which step ought to dominate.
    per_rung, quiet = [], []
    for i, s0 in enumerate(S0_LADDER):
        vals = {o: [] for o in ORDERS}
        for t_i in range(N_TRACES):
            seed = (base + 7919 * i + 104729 * t_i) % (2 ** 31)
            nu, y = _trace(s0, gamma_l, level, adc, seed, resolve)
            got = windowed_orders(y, window, nu)
            for o in ORDERS:
                vals[o].append(got[o])
        per_rung.append(vals)
        # THE QUIET REFERENCE: the same rung with the noise off and the ADC
        # deep, every physics layer on, so the signal-to-scatter against the
        # injected truth and the wrong-sign fraction are read against what the
        # estimator returns for this rung and not against the ramp's own value,
        # which the window truncates
        nu_q, y_q = _trace(s0, gamma_l, 1e-9, 2 ** 30, 12345, resolve)
        quiet.append(windowed_orders(y_q, window, nu_q))

    for order in ORDERS:
        xs, ys, snr, ok = [], [], [], True
        for i, s0 in enumerate(S0_LADDER):
            arr = np.asarray([v for v in per_rung[i][order] if np.isfinite(v)])
            if arr.size < 2:
                ok = False
                break
            k = float(np.median(arr))
            # THE PER-RUNG EVIDENCE IS KEPT: a reading of the first file found that min() over the
            # ladder hid the one fact the campaign case rests on, that the low
            # rungs are sign-degenerate (half the traces negative) while the
            # upper ones reach a signal-to-scatter in the tens and hundreds.
            sem = median_standard_error(arr)              # the median's own, one helper
            k_q = quiet[i][order]
            sign_q = float(np.sign(k_q)) if np.isfinite(k_q) and k_q != 0 else TRUE_SIGN[order]
            frac_wrong = float(np.mean(np.sign(arr) != sign_q))
            snr_true = abs(k_q) / sem if (np.isfinite(k_q) and sem > 0) else float("nan")
            # THE COUNT THAT STOPS A COIN FLIP BEING ONE: the median's standard
            # error falls as one over the root of the trace count, so the count
            # at which the quiet value stands three standard errors from zero
            # is n (3 sem / |k_q|)^2. A per-trace sign fraction says nothing a
            # reader can budget; this column is the campaign's own quantity.
            n_3sigma = arr.size * (3.0 * sem / abs(k_q)) ** 2 if (np.isfinite(k_q) and k_q != 0 and sem > 0) else float("nan")
            rung_rows.append((gamma_l, level, name, mode, window, resolve, order, s0,
                              k, sem, float(np.mean(arr < 0)), int(arr.size),
                              k_q, frac_wrong, snr_true, n_3sigma))
            snr.append(abs(k) / sem if sem > 0 else float("inf"))
            if not np.isfinite(k) or k == 0.0:
                ok = False
                break
            xs.append(math.log(s0))
            ys.append(math.log(abs(k)))
        if not ok or len(xs) < 3:
            rows.append((gamma_l, level, name, mode, window, resolve, order,
                         float("nan"), float("nan"), 0,
                         float(min(snr)) if snr else float("nan")))
            continue
        x = np.asarray(xs); yv = np.asarray(ys)
        n = len(x)
        slope, intercept = np.polyfit(x, yv, 1)
        resid = yv - (slope * x + intercept)
        dof = max(n - 2, 1)
        se = float(np.sqrt((resid @ resid) / dof / max(np.sum((x - x.mean()) ** 2), 1e-30)))
        rows.append((gamma_l, level, name, mode, window, resolve, order,
                     float(slope), se, n, float(min(snr))))
    return rows, rung_rows


def _grid():
    if os.environ.get("RB5S6S_MPM_DEEP"):
        # THE DEEP RUN: the archive's own noise level, the deepest scope, the
        # shift resolved, and only the two axes that decide whether the
        # channel is usable at the 2025 shift; sized by traces, not cells
        return list(product(GAMMA_L, (0.004,), (SCOPES[2],), WINDOW, (True,)))
    return list(product(GAMMA_L, NOISE_LEVEL, SCOPES, WINDOW, RESOLVE))


def main() -> int:
    known = {"--one-cell", "--plant", "--from", "--n", "--dump", "--combine"}
    bad = [a for a in sys.argv[1:] if a.startswith("-") and a not in known and not a.startswith("--tag=")]
    if bad:
        raise SystemExit(f"unknown flag(s) {bad}: the flags are --one-cell and --plant, "
                         "and a bare run launches the whole grid")
    workers = max(1, min(8, int(os.environ.get("RB5S6S_WORKERS", "8"))))
    cells = _grid()
    if "--one-cell" in sys.argv:
        import time
        t0 = time.time()
        rows, _ = _cell(cells[len(cells) // 2])
        dt = time.time() - t0
        print(f"one cell: {dt:.1f} s")
        print(f"grid is {len(cells)} cells -> {len(cells) * dt / 60:.0f} core-min, "
              f"about {len(cells) * dt / 60 / workers:.0f} min at {workers} workers")
        for r in rows:
            print(f"  order {r[6]}: slope {r[7]:+.3f} +- {r[8]:.3f} "
                  f"over {r[9]} rungs, min snr {r[10]:.2f}")
        return 0

    if "--plant" in sys.argv:
        # THE DETERMINISM PLANT, re-runnable and inside the producer rather
        # than beside it. A first attempt ran it from a heredoc through
        # importlib, which names the module "m"; spawned children cannot
        # import that, so the plant failed on its own harness and said
        # nothing about the producer. A real script file is importable by
        # the children, which is why this lives here.
        os.environ["RB5S6S_MPM_TRACES"] = "60"   # seeding path unchanged
        sub = cells[:6]
        def run(nw):
            with ProcessPoolExecutor(max_workers=nw) as ex:
                return list(ex.map(_cell, sub))
        a, b = run(1), run(8)
        ok = repr(a) == repr(b)
        print(f"  determinism plant: 1 worker against 8 over {len(sub)} cells: "
              f"{'BYTE-EQUAL' if ok else 'DIFFERENT'}")
        if not ok:
            for x, y in zip(a, b):
                if repr(x) != repr(y):
                    print("   first divergence:", x[0][0] if x[0] else x, "|", y[0][0] if y[0] else y); break
            return 1
        return 0

    # WAVES (C6a, 2026-09-22): the grid is 432 cells, 83 minutes at five workers under load, past the wave cap, so
    # `--from F --n N --dump P` computes cells F..F+N-1 and dumps their rows, and `--combine DIR` writes the two
    # CSVs from every dump in cell order. The cells are seeded each on its own (the plant above: one worker and
    # eight byte-equal), so the waves return exactly the one-process grid; `private/checks/wave_runner.py` walks it.
    if "--from" in sys.argv:
        import json
        lo = int(sys.argv[sys.argv.index("--from") + 1]); n = int(sys.argv[sys.argv.index("--n") + 1])
        dump = Path(sys.argv[sys.argv.index("--dump") + 1])
        out, out_rungs = _compute(cells[lo:lo + n], workers)
        dump.write_text(json.dumps({"from": lo, "out": out, "out_rungs": out_rungs}))
        print(f"wrote cells {lo}..{min(lo + n, len(cells)) - 1} to {dump}")
        return 0
    if "--combine" in sys.argv:
        import json
        d = Path(sys.argv[sys.argv.index("--combine") + 1])
        parts = sorted((json.loads(f.read_text()) for f in d.glob("wave_*.json")), key=lambda x: x["from"])
        out = [r for part in parts for r in part["out"]]
        out_rungs = [r for part in parts for r in part["out_rungs"]]
        if len(out) != len(cells):
            raise SystemExit(f"--combine: {len(out)} of {len(cells)} cells have a dump in {d}; the grid is not complete")
        return _write(out, out_rungs)

    # a half-hour eight-worker job into a shared results/ takes a lock, as
    # run_coverage_grid.py does; the lock belongs to the job
    # keyed on the checkout, so a scratch clone's run and this checkout's do
    # not refuse each other; the lock belongs to the job AND its tree
    lock = Path("/tmp") / f"rb5s6s_moment_power_map_{hashlib.sha1(str(ROOT).encode()).hexdigest()[:8]}.lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise SystemExit("moment-power map already running; refuse")
    try:
        return _run(cells, workers)
    finally:
        lock.rmdir()


def _run(cells, workers) -> int:
    return _write(*_compute(cells, workers))


def _compute(cells, workers):
    """The cells' rows, collected in cell order (the CSV bytes never depend on completion order)."""
    print(f"  {len(cells)} cells on {workers} workers", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        # COLLECTED IN ORDER, so the CSV bytes do not depend on completion
        # order. The progress line is ordered too and says nothing about which
        # cell finished when, so it cannot be mistaken for a timing.
        out, out_rungs = [], []
        for i, (rows, rung_rows) in enumerate(ex.map(_cell, cells), 1):
            out.append(rows); out_rungs.append(rung_rows)
            if i % 24 == 0 or i == len(cells):
                print(f"    {i}/{len(cells)} cells collected", flush=True)

    return out, out_rungs


def _write(out, out_rungs) -> int:
    """Write the two CSVs from the cells' rows, in cell order."""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["gamma_l_mhz", "noise_level", "scope", "scope_mode", "window_mhz", "resolve_shift",
                    "order", "s0_power", "s0_power_err", "rungs_used",
                    "min_snr_over_rungs", "status", "note"])
        for rows in out:
            for r in rows:
                # The producer tags its own rows, which is why this file sits
                # in the row-tagged list of annotate_results_status.py. Every
                # row is a property of the ESTIMATOR measured on synthetic
                # traces, so nothing here is MEASURED in the record's sense.
                # A cell whose estimator returned nothing usable is NULL, not
                # a slope with a wide error: the distinction is the difference
                # between a weak measurement and no measurement.
                # rungs_used is 0 or the full ladder, never between, because a
                # rung failure abandons the order; the rule says so instead of
                # wearing a threshold nothing can reach
                status = "DIAGNOSTIC" if r[9] == len(S0_LADDER) else "NULL"
                note = ("the fitted power of S0 carried by the windowed moment "
                        "of this order at this configuration, from a log-log fit "
                        "over the S0 ladder -- NaN means the estimator returned a "
                        "non-finite or zero moment on some rung")
                w.writerow([f"{r[0]:g}", f"{r[1]:g}", r[2], r[3], f"{r[4]:g}",
                            str(r[5]).lower(), r[6], f"{r[7]:.4f}",
                            f"{r[8]:.4f}", r[9], f"{r[10]:.3f}", status, note])
    print(f"wrote {OUT} with {sum(len(r) for r in out)} rows")
    RUNGS = OUT.with_name(OUT.stem + "_rungs.csv")
    with RUNGS.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["gamma_l_mhz", "noise_level", "scope", "scope_mode", "window_mhz",
                    "resolve_shift", "order", "s0_mhz", "k_median", "k_se_median",
                    "frac_negative", "n_traces", "k_quiet", "frac_wrong_sign", "snr_true",
                    "traces_to_3sigma", "status", "note"])
        for rr in out_rungs:
            for r in rr:
                w.writerow([f"{r[0]:g}", f"{r[1]:g}", r[2], r[3], f"{r[4]:g}", str(r[5]).lower(),
                            r[6], f"{r[7]:g}", f"{r[8]:.6e}", f"{r[9]:.3e}", f"{r[10]:.3f}", r[11],
                            f"{r[12]:.6e}", f"{r[13]:.3f}", f"{r[14]:.3f}", f"{r[15]:.3e}",
                            rung_status(round(r[13], 3)),
                            "one rung of the ladder: the median windowed moment of this order over "
                            "n_traces twin traces, its standard error as a median, the fraction of "
                            "traces returning a negative value, the same estimator's value on a "
                            "noiseless trace of this rung (k_quiet), the fraction of traces whose sign "
                            "differs from k_quiet's (the fifth order's true sign is negative), and "
                            "the quiet value over the standard error, and the trace count at which the "
                            "median would stand three standard errors from zero, n (3 se / k_quiet)^2. The status is DIAGNOSTIC when "
                            "frac_wrong_sign is below 0.35, which under a coin flip sits 13 standard "
                            "deviations below one half at two thousand traces and 60 at forty thousand"])
    print(f"wrote {RUNGS} with {sum(len(r) for r in out_rungs)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

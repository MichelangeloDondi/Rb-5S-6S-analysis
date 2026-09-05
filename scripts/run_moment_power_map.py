#!/usr/bin/env python
"""The S0 power of the truncated odd cumulants, across the conditions the archive spans.

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
production path every windowed odd cumulant returns a slope of 3.000, not the
3/5/7 ladder: at a shift far below the line width each odd moment is dominated
by the same leading asymmetry. And the windowed k5 does not converge against a
Lorentzian, recovering 570, 1858 and 5946 per cent at half-windows 8, 16 and
40. Those results are from ONE noiseless configuration. This map measures
whether they hold across the grid, which is the difference between an assertion
and a boundary.

THE READMISSION BARS for k5 and k7 are fixed before the run and are NOT the
theoretical ladder: a correctly-behaving windowed k5 at the archive's shift
SHOULD read 3, so a bar demanding 5 would strike a working estimator. A cell
readmits an order only if its recovered fraction sits inside 0.9 to 1.1, its
fitted power matches what the windowed theory predicts for that cell's regime,
and its residual against k3 carries information k3 does not. A cell that merely
fails to diverge is not a channel.

    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_moment_power_map.py --one-cell
    RB5S6S_WORKERS=8 .venv/bin/python scripts/run_moment_power_map.py
"""
from __future__ import annotations

import csv
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

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.forecast import build_world_trace                      # noqa: E402
from rb5s6s._compat import trapezoid as tz                        # noqa: E402

OUT = C.RESULTS_DIR / "moment_power_map.csv"

# ---- the grid, per the plan's section 4e ---------------------------------
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
WINDOW = (3.25, 4.0, 6.0, 8.0, 12.0, 16.0)   # 3.25 is the measured optimum
S0_LADDER = (0.18, 0.364, 0.73, 1.0, 2.0)    # archive 0.364, campaign 1.0
ORDERS = (3, 5, 7)

GAMMA_COLL, SIGMA_LASER, TRANSIT = 0.55, 1.6, 0.9575
# THE TRACE COUNT IS THE STUDY'S OWN SUBJECT, not a convenience. At the
# archive's shift and noise level a single trace's third cumulant is far
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
M_WINDOW = 4001
FINE = np.linspace(-40.0, 40.0, 32001)
PASSES = 20


def _central(g, yy, m1, n):
    return float(tz((g - m1) ** n * yy, g))


def selfcentred_cumulant(y, w, order, *, grid=None, m_pts=M_WINDOW, passes=PASSES):
    """Windowed cumulant of the given odd order about the self-centre.

    The window is RESAMPLED onto its own uniform grid rather than masked on the
    ambient one: a mask snaps both edges to grid points, and for a small
    windowed moment that edge noise swamped the physics badly enough to flip a
    committed sign. Twenty fixed-point passes, because four left an earlier
    row wrong by a factor of two.
    """
    amb = FINE if grid is None else grid
    c = 0.0
    for _ in range(passes):
        g = np.linspace(c - w, c + w, m_pts)
        yy = np.clip(np.interp(g, amb, y), 0, None)
        s = tz(yy, g)
        if s <= 0:
            return float("nan")
        yy = yy / s
        c = tz(g * yy, g)
    g = np.linspace(c - w, c + w, m_pts)
    yy = np.clip(np.interp(g, amb, y), 0, None)
    s = tz(yy, g)
    if s <= 0:
        return float("nan")
    yy = yy / s
    m1 = tz(g * yy, g)
    mu = {n: _central(g, yy, m1, n) for n in range(2, order + 1)}
    # cumulants from central moments, written out rather than recursed so the
    # cancellation structure is visible to a reader checking the algebra
    if order == 3:
        return mu[3]
    if order == 5:
        return mu[5] - 10.0 * mu[3] * mu[2]
    if order == 7:
        return (mu[7] - 21.0 * mu[5] * mu[2] - 35.0 * mu[4] * mu[3]
                + 210.0 * mu[3] * mu[2] ** 2)
    raise ValueError(f"order {order} not supported")


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
        resolve_shift=resolve)[:2]


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
    rows = []
    # ONE TRACE SET PER RUNG, SHARED BY EVERY ORDER, and it matters twice. The
    # first version keyed the seed on the order too, so k3, k5 and k7 were
    # measured on different traces: that makes them independent BY
    # CONSTRUCTION, which would overstate the rank of the moment family exactly
    # where this plan asks whether three cumulants are three equations or one
    # equation read three ways. Sharing the set lets that covariance be
    # measured. It is also cheaper, but by 1.65 and not by the 3 this comment
    # first claimed: generating a trace costs 1.7 ms and taking one moment of
    # it 1.2 ms, so the generation this change removes is not the dominant
    # cost. The figure was corrected by measuring it rather than by reasoning
    # about which step ought to dominate.
    per_rung = []
    for i, s0 in enumerate(S0_LADDER):
        vals = {o: [] for o in ORDERS}
        for t_i in range(N_TRACES):
            seed = (base + 7919 * i + 104729 * t_i) % (2 ** 31)
            nu, y = _trace(s0, gamma_l, level, adc, seed, resolve)
            for o in ORDERS:
                vals[o].append(selfcentred_cumulant(y, window, o, grid=nu))
        per_rung.append(vals)

    for order in ORDERS:
        xs, ys, snr, ok = [], [], [], True
        for i, s0 in enumerate(S0_LADDER):
            arr = np.asarray([v for v in per_rung[i][order] if np.isfinite(v)])
            if arr.size < 2:
                ok = False
                break
            k = float(np.median(arr))
            sem = float(np.std(arr, ddof=1) / math.sqrt(arr.size))
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
    return rows


def _grid():
    return list(product(GAMMA_L, NOISE_LEVEL, SCOPES, WINDOW, RESOLVE))


def main() -> int:
    known = {"--one-cell", "--plant"}
    bad = [a for a in sys.argv[1:] if a.startswith("-") and a not in known and not a.startswith("--tag=")]
    if bad:
        raise SystemExit(f"unknown flag(s) {bad}: the flags are --one-cell and --plant, "
                         "and a bare run launches the whole grid")
    workers = max(1, min(8, int(os.environ.get("RB5S6S_WORKERS", "8"))))
    cells = _grid()
    if "--one-cell" in sys.argv:
        import time
        t0 = time.time()
        rows = _cell(cells[len(cells) // 2])
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
                    print("   first divergence:", x[0], "|", y[0]); break
            return 1
        return 0

    # a half-hour eight-worker job into a shared results/ takes a lock, as
    # run_coverage_grid.py does; the lock belongs to the job
    lock = Path("/tmp/rb5s6s_moment_power_map.lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise SystemExit("moment-power map already running; refuse")
    try:
        return _run(cells, workers)
    finally:
        lock.rmdir()


def _run(cells, workers) -> int:
    print(f"  {len(cells)} cells on {workers} workers", flush=True)
    with ProcessPoolExecutor(max_workers=workers) as ex:
        # COLLECTED IN ORDER, so the CSV bytes do not depend on completion
        # order. The progress line is ordered too and says nothing about which
        # cell finished when, so it cannot be mistaken for a timing.
        out = []
        for i, rows in enumerate(ex.map(_cell, cells), 1):
            out.append(rows)
            if i % 24 == 0 or i == len(cells):
                print(f"    {i}/{len(cells)} cells collected", flush=True)

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
                note = ("the fitted power of S0 carried by the windowed cumulant "
                        "of this order at this configuration, from a log-log fit "
                        "over the S0 ladder; NaN means the estimator returned a "
                        "non-finite or zero cumulant on some rung")
                w.writerow([f"{r[0]:g}", f"{r[1]:g}", r[2], r[3], f"{r[4]:g}",
                            str(r[5]).lower(), r[6], f"{r[7]:.4f}",
                            f"{r[8]:.4f}", r[9], f"{r[10]:.3f}", status, note])
    print(f"wrote {OUT} with {sum(len(r) for r in out)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

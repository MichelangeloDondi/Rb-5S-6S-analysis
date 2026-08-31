#!/usr/bin/env python3
"""Leg 2 of the twin validation: coverage under mismatch, a grid not a point.

Truth carries a defect the fitter lacks; each configuration measures how
often the fitter's 95 per cent gamma_coll interval covers the injected
0.55 MHz, at 1000 trials, so the coverage carries a binomial error near
0.7 per cent. The grid is defect shape by defect size, per the
preregistration in the governance record: the convolved ramp fitted as
absent (the flagship omission, three sizes), a Lorentzian laser component
fitted as Gaussian (three sizes), the saturation companion width (three
sizes through the worst peak's coefficient), cascade depletion (three
cycle counts, expected inert in an amplitude-free fit and measured rather
than assumed), and the nominal no-defect row, whose 0.95 within 0.02 is
the harness's own gage. The broken-kernel plant (truth transit halved)
must drop nominal coverage below 0.90 or the leg cannot fail.

Noise is the committed measured law at the bench's own volts, the
realistic mode leg 3 landed; the design is the record's five traces of
two thousand points. Runs on eight workers, one trial one seed
(crc32 of config and index), so the CSV reproduces exactly. A lock
directory refuses a second copy. About forty minutes.

Output: results/coverage_grid.csv.
"""
from __future__ import annotations

import csv
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import stark  # noqa: E402
from rb5s6s.forecast import synthetic_traces  # noqa: E402
from rb5s6s.linefit import fit_condition  # noqa: E402
from rb5s6s.noise import load_noise_model  # noqa: E402

GAMMA, SIGMA, TRANSIT = 0.55, 1.6, 1.8
AMP_V = 0.8
N_TRIALS = 1000
WORKERS = min(8, os.cpu_count() or 1)

CONFIGS = [("nominal", "none", 0.0)]
CONFIGS += [("ramp_omitted", "s0", s) for s in (0.35, 2.5, 5.6)]
# The Lorentzian-component defect keeps the Gaussian kernel and ADDS
# gamma_l, which is what lineshape's homogeneous sum does under a gaussian
# kind; the first run of this grid set laser_kind="lorentzian" instead,
# which RE-TYPES the 1.6 MHz Gaussian as Lorentzian, a form flip that
# zeroed coverage at every size and measured the wrong axis. The flip is
# kept as its own single row below, because it is the switch-audit lever.
CONFIGS += [("lorentz_component", "gamma_l", g) for g in (0.1, 0.3, 0.6)]
CONFIGS += [("laser_form_flipped", "kind", 1.0)]
CONFIGS += [("saturation", "companion", s) for s in (0.35, 2.5, 5.6)]
CONFIGS += [("cascade", "cycles", c) for c in (1.0, 3.0, 6.0)]
CONFIGS += [("broken_kernel_plant", "transit_half", 1.0)]


def one_trial(args) -> bool:
    shape, knob, size, idx = args
    seed = zlib.crc32(f"{shape}:{size}:{idx}".encode()) % (2 ** 31)
    rng = np.random.default_rng(seed)
    law = one_trial.law
    gen = {"gamma_coll": GAMMA, "sigma_laser": SIGMA,
           "transit_fwhm": TRANSIT, "s0": 0.0,
           "laser_kind": "gaussian", "gamma_l": 0.0}
    fit_transit = TRANSIT
    if knob == "s0":
        gen["s0"] = size
    elif knob == "gamma_l":
        gen["gamma_l"] = size          # added component, kind stays gaussian
    elif knob == "kind":
        gen["laser_kind"] = "lorentzian"
    elif knob == "companion":
        gen["gamma_coll"] = GAMMA + stark.companion_gamma_mhz(size, "4121")
    elif knob == "transit_half":
        gen["transit_fwhm"] = TRANSIT / 2.0
    # cascade depletes amplitudes; with per-trace free amplitudes the
    # channel is expected inert, and the grid measures that instead of
    # asserting it. The generator's amp is scaled by the survival factor.
    amp = AMP_V
    if knob == "cycles":
        from rb5s6s import cascade
        amp = AMP_V * cascade.amplitude_factor("4121", size)
    freqs, volts = synthetic_traces(
        gen["gamma_coll"], gen["sigma_laser"], gen["transit_fwhm"],
        n_traces=5, n_points=2000, noise=law, amp=amp,
        laser_kind=gen["laser_kind"], gamma_l=gen["gamma_l"],
        s0=gen["s0"], rng=rng)
    res = fit_condition(freqs, volts, T_C=130.0, transit_fwhm=fit_transit,
                        law=law)
    lo = res["gamma_coll"] - 1.96 * res["gamma_coll_err"]
    hi = res["gamma_coll"] + 1.96 * res["gamma_coll_err"]
    return lo <= GAMMA <= hi


def _init():
    one_trial.law = load_noise_model(
        ROOT / "results" / "noise_model.csv", role="p_sweep", pool="median")


def main() -> int:
    lock = Path("/tmp/rb5s6s_coverage_grid.lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise SystemExit("coverage grid already running; refuse")
    try:
        _init()
        rows = []
        for shape, knob, size in CONFIGS:
            args = [(shape, knob, size, i) for i in range(N_TRIALS)]
            with ProcessPoolExecutor(max_workers=WORKERS,
                                     initializer=_init) as ex:
                hits = sum(ex.map(one_trial, args, chunksize=25))
            cov = hits / N_TRIALS
            err = float(np.sqrt(cov * (1 - cov) / N_TRIALS))
            rows.append([shape, f"{size:g}", f"{cov:.3f}", f"{err:.3f}",
                         "fraction",
                         f"{hits} of {N_TRIALS} intervals cover the "
                         "injected 0.55 MHz, binomial err", "DIAGNOSTIC"])
            print(f"  {shape:22s} size {size:g}: {cov:.3f} +/- {err:.3f}",
                  flush=True)
        nom = next(float(r[2]) for r in rows if r[0] == "nominal")
        plant = next(float(r[2]) for r in rows
                     if r[0] == "broken_kernel_plant")
        rows.append(["B1_nominal_covers", str(abs(nom - 0.95) <= 0.02), "",
                     "", "", f"nominal {nom:.3f} within 0.02 of 0.95 "
                     "(preregistered): the harness's own gage",
                     "DIAGNOSTIC"])
        rows.append(["G2_plant_fails", str(plant < 0.90), "", "", "",
                     f"the halved-transit plant covers at {plant:.3f}, "
                     "required below 0.90: a leg that cannot fail has "
                     "measured nothing", "DIAGNOSTIC"])
        out = ROOT / "results" / "coverage_grid.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["defect", "size", "value", "err", "unit", "note",
                        "status"])
            w.writerows(rows)
        print(f"wrote {out.relative_to(ROOT)}")
        return 0
    finally:
        lock.rmdir()


if __name__ == "__main__":
    sys.exit(main())

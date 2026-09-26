#!/usr/bin/env python3
"""Leg 2 of the twin validation: coverage under mismatch, a grid not a point.

Truth carries a defect the fitter lacks; each configuration measures how
often the fitter's 95 per cent gamma_coll interval covers the injected
collisional width (the reference point's, `GAMMA` below), at 1000 trials, so the coverage carries a binomial error near
0.7 per cent. The grid is defect shape by defect size, per the
preregistration in the governance record: the convolved ramp fitted as
absent (the flagship omission, three sizes), a Lorentzian laser component
fitted as Gaussian (three sizes), the saturation companion width (three
sizes through the worst peak's coefficient), cascade depletion (three
cycle counts, expected inert in an amplitude-free fit and measured rather
than assumed), and the nominal no-defect row, whose 0.95 within 0.02 is
the harness's own gage. The broken-kernel plant (the truth's transit halved,
by drawing the world at twice the fitter's waist, since the joint world's
transit is the ensemble's at the waist and an injected transit is never
read)
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
import json
import os
import sys
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s.config import RESULTS_DIR as _RESULTS_DIR  # noqa: E402  (F480: results where RB5S6S_RESULTS_DIR points)

from rb5s6s import constants as K  # noqa: E402
from rb5s6s import stark  # noqa: E402
from rb5s6s.forecast import fit_world, synthetic_traces  # noqa: E402
from rb5s6s.noise import load_noise_model  # noqa: E402
from rb5s6s.pmfmt import pm_cells  # noqa: E402   # coverage and its binomial err at two significant digits (owner, 2026-09-24)

# MHz. The transit is the twin's own, where a retired 1.8 stood until
# 2026-09-05: the record's transit at the waist convention of that day and 130 C was 0.9575,
# so the literal was 88 per cent high and no committed row ever held 1.8. The
# same triple was repaired in run_estimator_duel.py on 2026-09-04 and this
# producer was missed by that sweep, which is why the value is now DERIVED
# here rather than typed -- a literal cannot be missed by a sweep it cannot
# be the subject of.
from rb5s6s.reference_point import reference_point  # noqa: E402

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "the width fitter's coverage grid, a study of its bars at weak field"
#: the two rows that put the fitter apart from the world on purpose, declared at the world door (forecast.fit_world)
_RAMP_OMITTED = ("the flagship omission: the world carries the ramp and the fitter fits it as absent, which is "
                 "the defect this row measures")
_PLANT = ("the broken-kernel plant draws the world at twice the fitter's waist, halving its transit, so the "
          "leg can fail")
_LORENTZ = ("the world adds a Lorentzian laser component the fitter's Gaussian kernel does not hold, the defect "
            "this row measures")
_FORM_FLIP = ("the world's laser kernel is Lorentzian and the fitter's Gaussian, the switch-audit lever this row "
              "measures")
_AP = reference_point()   # F313: the archive's line, read from the committed fit and the waist, never typed
GAMMA, SIGMA = _AP["gamma_coll"], _AP["sigma_laser"]
TRANSIT = K.transit_fwhm_from_w0(K.W0_CENTRAL_M, T_C=130.0)
AMP_V = 0.8
N_TRIALS = 1000
# the pool honours RB5S6S_WORKERS, the share with the thesis session (2026-09-26); the CSV is the same at any count
WORKERS = max(1, min(8, int(os.environ.get("RB5S6S_WORKERS", "8")), os.cpu_count() or 1))

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
    w0_world = K.W0_CENTRAL_M
    if knob == "s0":
        gen["s0"] = size
    elif knob == "gamma_l":
        gen["gamma_l"] = size          # added component, kind stays gaussian
    elif knob == "kind":
        gen["laser_kind"] = "lorentzian"
    elif knob == "companion":
        gen["gamma_coll"] = GAMMA + stark.companion_gamma_mhz(size, "4121")
    elif knob == "transit_half":
        w0_world = 2.0 * K.W0_CENTRAL_M     # the joint world's transit goes as one over the waist
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
        s0=gen["s0"], rng=rng, T_C=130.0, w0_m=w0_world, registry=_TWIN_STUDY)
    res = fit_world(freqs, volts, T_C=130.0, law=law, world_mismatch_reason=(
        {"s0": {"shift": _RAMP_OMITTED}, "transit_half": {"w0_m": _PLANT}, "gamma_l": {"gas width": _LORENTZ},
         "kind": {"laser kernel": _FORM_FLIP}}.get(knob)))
    lo = res["gamma_coll"] - 1.96 * res["gamma_coll_err"]
    hi = res["gamma_coll"] + 1.96 * res["gamma_coll_err"]
    return lo <= GAMMA <= hi


def _init():
    one_trial.law = load_noise_model(
        _RESULTS_DIR / "noise_model.csv", role="p_sweep", pool="median")


def _unit_hits(k: int) -> int:
    """Configuration `k`'s covering intervals out of N_TRIALS. Each trial seeds itself from its configuration and
    index (`one_trial`), so a unit computed in its own process returns exactly what the one-process run returns."""
    shape, knob, size = CONFIGS[k]
    args = [(shape, knob, size, i) for i in range(N_TRIALS)]
    with ProcessPoolExecutor(max_workers=WORKERS, initializer=_init) as ex:
        return int(sum(ex.map(one_trial, args, chunksize=25)))


def _rows(hits_by_k: dict) -> list:
    rows = []
    for k, (shape, knob, size) in enumerate(CONFIGS):
        hits = hits_by_k[k]
        cov = hits / N_TRIALS
        err = float(np.sqrt(cov * (1 - cov) / N_TRIALS))
        rows.append([shape, f"{size:g}", *pm_cells(cov, err),
                     "fraction",
                     f"{hits} of {N_TRIALS} intervals cover the "
                     f"injected {GAMMA:.4f} MHz, binomial err", "DIAGNOSTIC"])
        print(f"  {shape:22s} size {size:g}: {cov:.3f} +/- {err:.3f}", flush=True)
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
    return rows


def main() -> int:
    """No argument runs every configuration in-process, as before. THE CONFIGURATIONS ARE THE RUN'S UNITS
    (2026-09-26, V7.2): `--from K --n N --dump PATH` computes configurations K..K+N-1 (from zero) and dumps their
    hits, and `--combine DIR` assembles every `wave_*.json` in DIR into the CSV, refusing while a configuration has no
    dump, so `private/checks/wave_runner.py` walks the 4.7-hour run a slice per wave (the chain ledger measured it at
    16 799 s in one piece). The lock guards the CSV, so a slice that only dumps does not take it."""
    argv = sys.argv[1:]
    if "--from" in argv:
        lo = int(argv[argv.index("--from") + 1])
        n = int(argv[argv.index("--n") + 1])
        dump = Path(argv[argv.index("--dump") + 1])
        _init()
        out = {str(k): _unit_hits(k) for k in range(lo, min(lo + n, len(CONFIGS)))}
        dump.write_text(json.dumps(out))
        print(f"wrote configurations {sorted(out, key=int)} to {dump}")
        return 0
    lock = Path("/tmp/rb5s6s_coverage_grid.lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise SystemExit("coverage grid already running; refuse")
    try:
        if "--combine" in argv:
            d = Path(argv[argv.index("--combine") + 1])
            hits_by_k = {}
            for f in sorted(d.glob("wave_*.json")):
                for k, h in json.loads(f.read_text()).items():
                    hits_by_k[int(k)] = int(h)
            missing = [k for k in range(len(CONFIGS)) if k not in hits_by_k]
            if missing:
                raise SystemExit(f"--combine: configurations {missing} have no dump in {d}; the run is not complete")
        else:
            _init()
            hits_by_k = {k: _unit_hits(k) for k in range(len(CONFIGS))}
        rows = _rows(hits_by_k)
        out = _RESULTS_DIR / "coverage_grid.csv"
        with out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["defect", "size", "value", "err", "unit", "note",
                        "status"])
            w.writerows(rows)
        print(f"wrote {out}")
        return 0
    finally:
        lock.rmdir()


if __name__ == "__main__":
    sys.exit(main())

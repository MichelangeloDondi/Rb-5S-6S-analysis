"""What pinning the laser width buys the collisional width, by simulation.

Four public documents quote a specific comparison: at the measured noise law,
a fit with the collisional and laser widths BOTH free recovers gamma_coll
with a scatter of 0.0396 MHz across realisations, and the same fit with the
laser width KNOWN recovers it with 0.0235 MHz, a factor of 1.7. Until
2026-08-18 no committed script produced those numbers. This is that producer,
written after the fact and run to adjudicate the quoted pair: reproduce it,
or correct the record to what this script measures.

CONSTRUCTION, stated so the numbers cannot be quoted without it. One bright
condition of five repeats on the campaign's own axis (0.08514 MHz per ms,
2000 points at 0.5 ms), truth gamma_coll 0.60 MHz and sigma_laser 1.40 MHz
over the fixed transit kernel, per-trace centre drift of 1 MHz, three per
cent gain scatter, and signal-dependent noise with the test suite's measured
coefficients (a = 3e-3, b = 2e-5, the shape `condition_noise_model` fits on
real conditions). Two estimators per realisation: the production
`fit_condition`, which frees gamma_coll and sigma_laser jointly, and a
sigma-pinned twin that holds sigma_laser at TRUTH, built on the same
`_shared_profile_grid` evaluation so the two differ only in the freed set.
The reported numbers are the standard deviation and mean bias of the
recovered gamma_coll over the realisations, per estimator.

The extended-lever variants (--temps) rerun the same comparison at the
150 and 170 C transit kernels for the plan's proposed hotter blocks, for the
quantities dossier's improved-bound projection.

Diagnostic. Writes private/run_logs/width_pinning_<seed>.csv and prints the
summary. Nothing in results/ moves.
"""
from __future__ import annotations

import argparse
import csv
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C                                 # noqa: E402
from rb5s6s.lineshape import model_profile                     # noqa: E402
from rb5s6s.linefit import (_shared_profile_grid, fit_condition,  # noqa: E402
                            to_frequency, transit_fwhm_at_T)

RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)
GC_TRUE, SL_TRUE = 0.60, 1.40
NOISE_A, NOISE_B = 3e-3, 2e-5


def synth(rng, transit):
    freqs, volts = [], []
    for _ in range(5):
        c = rng.normal(0.0, 1.0)
        g = 1.0 + rng.normal(0.0, 0.03)
        prof = model_profile(NU - c, gamma_coll=GC_TRUE,
                             sigma_laser_fwhm=SL_TRUE, transit_fwhm=transit)
        v = g * prof / prof.max()
        sig = np.sqrt(NOISE_A ** 2 + NOISE_B * np.maximum(v, 0.0))
        volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
        freqs.append(NU.copy())
    return freqs, volts


def fit_sigma_pinned(freqs, volts, transit):
    """gamma_coll with sigma_laser held at truth, per-trace nuisances free."""
    from scipy.optimize import least_squares
    n = len(freqs)

    def resid(p):
        gc = p[0]
        g, prof = _shared_profile_grid(gc, SL_TRUE, transit, 0.0, "gaussian")
        out = []
        for i in range(n):
            A, cc, b0, b1 = p[1 + 4 * i: 5 + 4 * i]
            mdl = A * np.interp(freqs[i] - cc, g, prof, left=0., right=0.)
            mdl = mdl + b0 + b1 * freqs[i]
            sig = np.sqrt(NOISE_A ** 2 + NOISE_B * np.maximum(volts[i], 0.0))
            out.append((volts[i] - mdl) / sig)
        return np.concatenate(out)

    p0 = [GC_TRUE]
    lo = [0.0]; hi = [10.0]
    for i in range(n):
        pk = float(np.max(volts[i]))
        c0 = float(NU[int(np.argmax(volts[i]))])
        g, prof = _shared_profile_grid(GC_TRUE, SL_TRUE, transit, 0.0,
                                       "gaussian")
        p0 += [pk / prof.max(), c0, 0.0, 0.0]
        lo += [0.0, c0 - 8.0, -np.inf, -np.inf]
        hi += [np.inf, c0 + 8.0, np.inf, np.inf]
    s = least_squares(resid, p0, bounds=(lo, hi), x_scale="jac", ftol=1e-10)
    return float(s.x[0])


def run(trials, seed, t_c):
    transit = transit_fwhm_at_T(t_c, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    rng = np.random.default_rng(seed)
    free, pinned = [], []
    for _ in range(trials):
        freqs, volts = synth(rng, transit)
        fit = fit_condition(freqs, volts, T_C=t_c, transit_fwhm=transit)
        free.append(float(fit["gamma_coll"]))
        pinned.append(fit_sigma_pinned(freqs, volts, transit))
    fr, pi = np.array(free), np.array(pinned)
    return dict(
        T_C=t_c, trials=trials, transit=round(transit, 4),
        scatter_free=round(float(fr.std(ddof=1)), 4),
        scatter_pinned=round(float(pi.std(ddof=1)), 4),
        ratio=round(float(fr.std(ddof=1) / pi.std(ddof=1)), 2),
        bias_free=round(float(fr.mean() - GC_TRUE), 4),
        bias_pinned=round(float(pi.mean() - GC_TRUE), 4))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--seed", type=int, default=C.RNG_SEED)
    ap.add_argument("--temps", type=float, nargs="*", default=[130.0])
    a = ap.parse_args()
    rows = [run(a.trials, a.seed, t) for t in a.temps]
    out = ROOT / "private/run_logs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"width_pinning_{a.seed}.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for r in rows:
        print(f"T={r['T_C']:.0f}C  free {r['scatter_free']:.4f} MHz  "
              f"sigma-known {r['scatter_pinned']:.4f} MHz  "
              f"ratio {r['ratio']:.2f}  bias {r['bias_free']:+.4f} -> "
              f"{r['bias_pinned']:+.4f}")
    print(f"rows -> {path}")
    print("DIAGNOSTIC. Nothing in results/ moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

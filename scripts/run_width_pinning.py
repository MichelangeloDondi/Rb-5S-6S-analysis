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

WHY IT RUNS AN ENSEMBLE OF SEEDS (2026-08-19). The ratio of two Monte-Carlo
standard deviations varies from seed to seed, and at 200 trials that spread
is about six per cent. The first version of this script reported
ONE seed, and the 3.4 that four documents then quoted turned out to be the
largest of nine draws of the same experiment, which run 2.86 to 3.45. A single
draw quoted to two significant figures is the same defect as the
unreproducible pair this script was written to replace, one generation later.
So the default is an ensemble and the quotable number is its mean with its
spread. Pass --replicates 1 for a single seed when iterating.

WHY THE CORRELATION IS REPORTED BESIDE THE RATIO. What pinning buys is
arithmetic before it is a simulation: conditioning on one member of a
correlated pair leaves the other with sqrt(1 - rho^2) of its uncertainty, so
the factor is 1/sqrt(1 - rho^2) and depends on the correlation alone. That
formula evaluated at this record's median correlation of -0.90 gives 2.29,
which reads as a disagreement with what is measured here and is not one: this
condition fits its OWN correlation, near -0.9417, where the same formula gives
2.97. The rows below carry both constructions so they cannot drift apart
unnoticed. The correlation is stable to four decimals across every seed, which
is what the arithmetic predicts, since a correlation is a property of the
design rather than of the noise draw.

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


def run_one(trials, seed, t_c):
    transit = transit_fwhm_at_T(t_c, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    rng = np.random.default_rng(seed)
    free, pinned, corr = [], [], []
    for _ in range(trials):
        freqs, volts = synth(rng, transit)
        fit = fit_condition(freqs, volts, T_C=t_c, transit_fwhm=transit)
        free.append(float(fit["gamma_coll"]))
        pinned.append(fit_sigma_pinned(freqs, volts, transit))
        r = fit.get("corr_laser_coll")
        if r is not None and np.isfinite(r):
            corr.append(float(r))
    fr, pi = np.array(free), np.array(pinned)
    rho = float(np.median(corr)) if corr else float("nan")
    # 1/sqrt(1-rho^2): what the covariance arithmetic predicts the same
    # pinning should buy, so the row carries both constructions at once.
    predicted = (float(1.0 / np.sqrt(1.0 - rho ** 2))
                 if np.isfinite(rho) and abs(rho) < 1 else float("nan"))
    return dict(
        T_C=t_c, trials=trials, seed=seed, transit=round(transit, 4),
        numpy=np.__version__, python=".".join(str(v) for v in
                                              sys.version_info[:3]),
        scatter_free=round(float(fr.std(ddof=1)), 4),
        scatter_pinned=round(float(pi.std(ddof=1)), 4),
        ratio=round(float(fr.std(ddof=1) / pi.std(ddof=1)), 2),
        corr_laser_coll=round(rho, 4),
        ratio_predicted=round(predicted, 2),
        bias_free=round(float(fr.mean() - GC_TRUE), 4),
        bias_pinned=round(float(pi.mean() - GC_TRUE), 4))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--seed", type=int, default=C.RNG_SEED)
    ap.add_argument("--replicates", type=int, default=9,
                    help="consecutive seeds from --seed. The ratio is a "
                         "random variable and one draw is not a result.")
    ap.add_argument("--temps", type=float, nargs="*", default=[130.0])
    a = ap.parse_args()
    rows = [run_one(a.trials, a.seed + k, t)
            for t in a.temps for k in range(a.replicates)]
    out = ROOT / "private/run_logs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"width_pinning_{a.seed}.csv"
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    for t_c in a.temps:
        band = [r for r in rows if r["T_C"] == t_c]
        ratios = np.array([r["ratio"] for r in band])
        rho = float(np.median([r["corr_laser_coll"] for r in band]))
        pred = float(np.median([r["ratio_predicted"] for r in band]))
        sd = float(ratios.std(ddof=1)) if len(ratios) > 1 else float("nan")
        print(f"T={t_c:.0f}C  {len(band)} seeds x {a.trials} trials")
        print(f"        free {np.mean([r['scatter_free'] for r in band]):.4f}"
              f" MHz   sigma-known "
              f"{np.mean([r['scatter_pinned'] for r in band]):.4f} MHz")
        print(f"        ratio {ratios.mean():.2f} +/- {sd:.2f} across seeds, "
              f"range {ratios.min():.2f} to {ratios.max():.2f}")
        print(f"        this condition fits rho = {rho:.4f}, where "
              f"1/sqrt(1-rho^2) predicts {pred:.2f}")
    print(f"rows -> {path}")
    print("DIAGNOSTIC. Nothing in results/ moved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

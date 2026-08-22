#!/usr/bin/env python
"""O2: the fibre twin, preregistered in private/reviews/O2_PREREG_2026-08-22.md.

O2 IS A DESIGN VALIDATION, NOT AN EXPERIMENTAL RESULT. It validates that the
proposed design can identify the intended quantities under specified synthetic
worlds. It does NOT demonstrate that the real fibre experiment will.

THE FIBRE DOES NOT MEASURE LASER LINEWIDTH. It measures whether the observed
homogeneous component moves as the transit law predicts when temperature
varies.

WHY THE STRUCTURE IS WHAT IT IS. The fibre transit kernel is LORENTZIAN, so it
adds EXACTLY to every other Lorentzian term. The observable at one rung is
therefore a single Lorentzian total plus a Gaussian sigma_G, and the individual
Lorentzian terms have no separate existence there at all. That is not a
limitation of the fit; it is the algebra. The ladder is the only lever: across
rungs the transit term moves with temperature and the rest does not, so
Gamma_L is an INTERCEPT and transit is a SLOPE.

This is why world D shares O2-A's generator with the ladder collapsed to one
rung. Passing world D means FAILING to split, and the two results are directly
comparable because the machinery is identical.
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C          # noqa: E402
from rb5s6s.lineshape import composite_profile  # noqa: E402
from rb5s6s.fibre import transit_fwhm   # noqa: E402

OUT = C.RESULTS_DIR / "fibre_twin.csv"

LADDER_K = (20e-6, 60e-6, 150e-6)      # the preregistered ladder
GAMMA_L_TRUE_MHZ = 0.398               # a common component of the measured size
SIGMA_G_TRUE_MHZ = 0.30                # a Gaussian laser contribution
LAMBDA_EDGES_M = (0.13e-6, 0.24e-6)    # both decay-length band edges
# THE WORLD'S INFORMATION CONTENT IS CALIBRATED, NOT CHOSEN (2026-08-22).
# A twin run at an arbitrary signal-to-noise answers "can this design work at a
# level I picked", which is not the question. The archive DEMONSTRATES a total
# width per condition to 0.0032 MHz (docs/BIG_PICTURE.md, Q-WIDTH-01, where the
# split direction is a factor of twenty worse at 0.0624 MHz -- two different
# quantities that both get called a width error, so the well-constrained one is
# named here explicitly). These settings reproduce that 3.2 kHz per rung, so
# the twin assumes exactly the precision already achieved and no better.
#
# Measured while calibrating: the estimator is EXACTLY unbiased at zero noise
# (both parameters recovered to -0.00 kHz), and its scatter is linear in the
# noise amplitude -- 3.81, 7.72 and 14.00 kHz at 0.003, 0.006 and 0.012. So the
# error here is statistical, not a grid or interpolation artefact.
NOISE = 0.0025                         # fractional, on the peak
NPTS = 1201
SPAN_MHZ = 12.0
PER_RUNG_TARGET_KHZ = 3.2              # the demonstrated precision this matches
PER_RUNG_SD_MHZ = 0.00402              # the per-rung scatter these settings achieve
# O2-B's detector is the ONE degree of freedom three rungs leave against two
# free parameters, so the critical value is the standard one-dof chi-square
# point at a 5 per cent false-positive rate. It is not tuned after a result.
O2B_CHI2_CRIT = 3.8415
O2B_DEPARTURES_MHZ = (0.005, 0.010, 0.020, 0.040)

TARGET_GAMMA_L_KHZ = 12.2
TARGET_SIGMA_G_KHZ = 11.6
COVERAGE = 0.95


def _rung_total_mhz(T_k, lam_m, alpha=1.0):
    """Total Lorentzian width at one rung: the common part plus transit."""
    tr = transit_fwhm(T_k, lam_m, convention="mean", alpha=alpha)
    return GAMMA_L_TRUE_MHZ + tr.fwhm_hz / 1e6


def _spectrum(total_lor_mhz, sigma_g_mhz, rng):
    """One noisy rung. The Lorentzian total enters through gamma_l, which is
    the additive Lorentzian channel; transit_fwhm is left at zero because the
    transit contribution is ALREADY inside the total by exact additivity."""
    grid, prof = composite_profile(0.0, sigma_g_mhz, 0.0,
                                   laser_kind="gaussian", transit_kind="exp",
                                   gamma_l=total_lor_mhz)
    x = np.linspace(-SPAN_MHZ, SPAN_MHZ, NPTS)
    y = np.interp(x, grid, prof)
    y = y / y.max()
    return x, y + rng.normal(0.0, NOISE, size=x.shape)


def _fit_rung(x, y):
    """Recover (total Lorentzian, sigma_G) from one rung. Two parameters, and
    no attempt to split the Lorentzian, because at one rung it cannot be."""
    def resid(p):
        lor, sig, amp = p
        grid, prof = composite_profile(0.0, abs(sig), 0.0,
                                       laser_kind="gaussian",
                                       transit_kind="exp", gamma_l=abs(lor))
        m = np.interp(x, grid, prof)
        m = m / m.max()
        return amp * m - y
    r = least_squares(resid, [0.6, 0.3, 1.0],
                      bounds=([1e-4, 1e-4, 0.2], [8.0, 4.0, 3.0]))
    return abs(r.x[0]), abs(r.x[1]), r.cost, r.success


def _ladder_intercept(temps_k, totals_mhz, lam_m):
    """Decompose total(T) = Gamma_L + s * f(T), fitting BOTH parameters.

    THE FIRST VERSION OF THIS FUNCTION LEAKED, AND WORLD D CAUGHT IT. It
    subtracted the transit computed from the TRUE decay length and fitted only
    an additive constant, which hands the estimator a quantity the real
    apparatus does not have. World D then reported 99.8 per cent coverage at a
    SINGLE rung, where the split cannot exist at all — and the preregistration
    had already written down what that outcome would mean: the generator is
    leaking information, so the twin is wrong rather than the design.

    The estimator that does not leak carries TWO free parameters. `f(T)` is the shape of
    the transit law at a reference decay length, and the free scale `s`
    absorbs 1/Lambda, which is exactly the quantity no independent measurement
    pins. So the ladder must determine the Lambda scale AND the intercept
    together, and the counting is the design: three rungs against two
    parameters is identifiable with one degree of freedom left over, one rung
    against two parameters is not.
    """
    f = np.array([transit_fwhm(T, lam_m, "mean").fwhm_hz / 1e6
                  for T in temps_k])
    A = np.column_stack([np.ones_like(f), f])
    sol, *_ = np.linalg.lstsq(A, np.asarray(totals_mhz, dtype=float), rcond=None)
    return float(sol[0])


def run_o2a(n_trials, lam_m, seed0=0, alpha=1.0, single_rung=False):
    ladder = (LADDER_K[1],) if single_rung else LADDER_K
    ok_g, ok_s, gl_err, sg_err, fails = 0, 0, [], [], 0
    for i in range(n_trials):
        rng = np.random.default_rng(seed0 + i)
        totals, sigs, bad = [], [], False
        for T in ladder:
            true_tot = _rung_total_mhz(T, lam_m, alpha)
            x, y = _spectrum(true_tot, SIGMA_G_TRUE_MHZ, rng)
            lor, sig, _, good = _fit_rung(x, y)
            if not good:
                bad = True
                break
            totals.append(lor)
            sigs.append(sig)
        if bad:
            fails += 1
            continue
        gl_hat = _ladder_intercept(ladder, totals, lam_m)
        sg_hat = float(np.mean(sigs))
        dg = abs(gl_hat - GAMMA_L_TRUE_MHZ) * 1e3
        ds = abs(sg_hat - SIGMA_G_TRUE_MHZ) * 1e3
        gl_err.append(dg)
        sg_err.append(ds)
        ok_g += dg < TARGET_GAMMA_L_KHZ
        ok_s += ds < TARGET_SIGMA_G_KHZ
    n = max(n_trials, 1)
    return dict(n=n_trials, failures=fails,
                cov_gamma_l=ok_g / n, cov_sigma_g=ok_s / n,
                med_gamma_l_khz=float(np.median(gl_err)) if gl_err else float("nan"),
                med_sigma_g_khz=float(np.median(sg_err)) if sg_err else float("nan"))


def _ladder_residual_chi2(temps_k, totals_mhz, lam_m, sd_mhz):
    """Residual chi-square of the two-parameter ladder fit.

    Three rungs against two free parameters leaves ONE degree of freedom, and
    that single dof is the whole detector: under common truth the residual is
    noise, and a rung-to-rung departure inflates it. This is why O2-B needs no
    new machinery, only the fit already used by O2-A.
    """
    f = np.array([transit_fwhm(T, lam_m, "mean").fwhm_hz / 1e6
                  for T in temps_k])
    A = np.column_stack([np.ones_like(f), f])
    y = np.asarray(totals_mhz, dtype=float)
    sol, *_ = np.linalg.lstsq(A, y, rcond=None)
    r = y - A @ sol
    return float(np.sum((r / sd_mhz) ** 2))


def run_o2b(n_trials, lam_m, departure_mhz, seed0, crit):
    """O2-B: the rung-to-rung departure this design can DETECT.

    term-of-art: naming both here is the disclaimer itself, stating that one
    is not evidence about the other, which is the whole reason the guard exists.

    NOT K2.5. K2.5 varies four spectral PEAKS, different hyperfine lines and
    isotopes. This varies TEMPERATURE RUNGS on one line. A result here is
    silent about that, and a mechanical guard in tests/test_repo_hygiene.py
    forbids citing one as evidence about the other.

    A NECESSARY-CONDITION TEST ONLY: it reports what the design would notice,
    not what is true of the apparatus.
    """
    hits = 0
    for i in range(n_trials):
        rng = np.random.default_rng(seed0 + i)
        totals = []
        # alternate the departure across rungs so it cannot be absorbed by
        # either free parameter: a constant shift hides in the intercept and a
        # linear one hides in the scale, so only an alternating pattern tests
        # the dof that is actually left over.
        for k, T in enumerate(LADDER_K):
            sign = 1.0 if k % 2 == 0 else -1.0
            true_tot = _rung_total_mhz(T, lam_m) + sign * departure_mhz / 2.0
            x, y = _spectrum(true_tot, SIGMA_G_TRUE_MHZ, rng)
            lor, _, _, ok = _fit_rung(x, y)
            if not ok:
                break
            totals.append(lor)
        if len(totals) != len(LADDER_K):
            continue
        chi2 = _ladder_residual_chi2(LADDER_K, totals, lam_m,
                                     PER_RUNG_SD_MHZ)
        hits += chi2 > crit
    return hits / max(n_trials, 1)


def main() -> int:
    ap = argparse.ArgumentParser()
    # N FIXED FROM A TIMED TRIAL BEFORE THE RUN, as the preregistration
    # requires: 0.03 s per rung fit, three rungs, so 500 trials is about 45 s
    # per world. 500 matches the count K2 preregistered, so the two coverage
    # statements are read on the same scale.
    ap.add_argument("--trials", type=int, default=500)
    a = ap.parse_args()

    rows = []

    def add(world, quantity, value, unit, note, status="DIAGNOSTIC"):
        rows.append(dict(world=world, quantity=quantity, value=value,
                         unit=unit, note=note, status=status))

    add("ALL", "design_validation_only", "TRUE", "flag",
        "O2 validates that the design can identify the intended quantities "
        "under synthetic worlds. It does not demonstrate that the real fibre "
        "experiment will")
    add("ALL", "measures_laser_linewidth", "FALSE", "flag",
        "the fibre tests whether the homogeneous component moves as the "
        "transit law predicts, which is not a laser linewidth measurement")
    add("ALL", "velocity_convention", "mean", "convention",
        "typed on the estimator; rms differs by about 6 per cent")

    # THE COVERAGE ROWS ARE UNREADABLE WITHOUT THESE TWO. A coverage fraction
    # is a statement about a world's information content as much as about the
    # design, and would be a different number at a different signal-to-noise.
    # Carrying the assumption as rows means a reader of this file alone can see
    # what the design was asked to do it WITH.
    add("ALL", "per_rung_sd_khz", f"{PER_RUNG_SD_MHZ * 1e3:.2f}", "kHz",
        "the per-rung scatter on the total width that these settings achieve; "
        "every coverage row below assumes it")
    add("ALL", "per_rung_demonstrated_khz", f"{PER_RUNG_TARGET_KHZ:.1f}", "kHz",
        "what the record already achieves per condition on a total width "
        "(docs/BIG_PICTURE.md, Q-WIDTH-01, where the SPLIT direction is a "
        "factor of twenty worse at 62.4 kHz and carries the same name). The "
        "world is calibrated against this rather than chosen, and sits just "
        "outside it, which is the conservative direction")

    for lam in LAMBDA_EDGES_M:
        tag = f"lambda_{lam*1e9:.0f}nm"
        r = run_o2a(a.trials, lam)
        add(f"O2A_{tag}", "coverage_gamma_l", f"{r['cov_gamma_l']:.4f}", "fraction",
            f"target >= {COVERAGE} within {TARGET_GAMMA_L_KHZ} kHz")
        add(f"O2A_{tag}", "coverage_sigma_g", f"{r['cov_sigma_g']:.4f}", "fraction",
            f"target >= {COVERAGE} within {TARGET_SIGMA_G_KHZ} kHz")
        add(f"O2A_{tag}", "median_abs_err_gamma_l", f"{r['med_gamma_l_khz']:.3f}",
            "kHz", "median absolute error over trials")
        add(f"O2A_{tag}", "trials", r["n"], "count", f"failures {r['failures']}")

        # World D: the SAME generator with the ladder collapsed to one rung.
        d = run_o2a(a.trials, lam, seed0=10_000, single_rung=True)
        add(f"WORLD_D_{tag}", "coverage_gamma_l", f"{d['cov_gamma_l']:.4f}",
            "fraction",
            "INVERTED pass condition: at one rung the split must FAIL, so a "
            "LOW coverage here is the passing result")

    # World F: a wrong temperature law, as an alpha ladder.
    for alpha in (0.35, 0.6, 1.0):
        f = run_o2a(a.trials, LAMBDA_EDGES_M[0], seed0=20_000, alpha=alpha)
        add(f"WORLD_F_alpha_{alpha}", "coverage_gamma_l",
            f"{f['cov_gamma_l']:.4f}", "fraction",
            "data generated under T**(alpha/2), fitted under the correct law; "
            "the alpha at which coverage collapses is the departure the design "
            "can detect")

    # term-of-art: this comment names both in order to deny the inference
    # O2-B: the rung-to-rung departure the design can detect. NOT K2.5.
    fp = run_o2b(a.trials, LAMBDA_EDGES_M[0], 0.0, 30_000, O2B_CHI2_CRIT)
    add("O2B", "false_positive_rate", f"{fp:.4f}", "fraction",
        "detection rate at ZERO departure; the nominal 0.05 is the design "
        "point, and a measured value far from it means the assumed per-rung "
        "scatter is wrong rather than the design")
    for d in O2B_DEPARTURES_MHZ:
        r = run_o2b(a.trials, LAMBDA_EDGES_M[0], d, 40_000, O2B_CHI2_CRIT)
        # term-of-art: the row names both precisely to deny the inference, so
        # the reader of the CSV meets the denial rather than only the number.
        add(f"O2B_departure_{int(d*1000)}kHz", "detection_rate", f"{r:.4f}",
            "fraction",
            "NECESSARY-CONDITION test on TEMPERATURE RUNGS of one line. This "
            "is not evidence about K2.5, which varies four spectral PEAKS "
            "across different hyperfine lines and isotopes")

    add("ALL", "band_edge_licensing",
        "DISAGREEMENT_MEANS_UNIDENTIFIABLE", "sentence",
        "the lever and its calibration are the same order, about 83 kHz. If "
        "the two band edges disagree, the world is unidentifiable unless "
        "Lambda is pinned independently. It does not license choosing the "
        "edge that gives the better answer")

    with OUT.open("w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    print(f"wrote {OUT} with {len(rows)} rows")
    for r in rows:
        print(f"  {r['world']:<24} {r['quantity']:<26} {r['value']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""How the residual skew falls as the line brightens, and what that excludes.

THE QUESTION. The committed per-condition residual skew is large and positive
at low power and falls as the line brightens. Two mechanisms predict that fall
and they predict different exponents, so the exponent discriminates them:

    Poisson shot-noise skewness      skew proportional to amp ** (-1/2)
    a fixed-absolute-amplitude term  skew proportional to amp ** (-1)

The second is the candidate the measurement plan carried for the near-core
asymmetry, sized at about half a per cent of the bright signal, which is the
band-excess scale. This module measures the exponent on committed data.

WHY LINEAR SPACE. The obvious fit is a straight line through log(skew) against
log(amp), and it is wrong here. The highest-amplitude points have skews
consistent with zero and one of them is negative, so the log transform cannot
take it and silently drops exactly the point that carries the slope, while
relative-error weighting in log space downweights its neighbours for the same
reason. Run both ways on this dataset the two disagree by more than four
sigma and only the linear-space fit is right. A power law whose values
approach zero is fitted in linear space against absolute errors.

WHY THE SCATTER SETS THE ERROR. The four lines return exponents that disagree
with each other beyond their own uncertainties, so the uncertainty on their
mean is taken from their scatter rather than from the individual errors, which
is the wider and honest choice.

THE CEILING TEST RUNS FIRST AND ALWAYS, AND IT CHANGED THE ANSWER. Injecting
a known -1.0 into this dataset's own amplitudes and errors, the estimator
returns about -2.3 with a scatter of 2.4: anchored to the same low-power skew,
a -1 law puts the high-amplitude skews far below their own error bars, so the
amplitude lever carries almost no information there. The fit covariance is
therefore NOT the right error for an exclusion, because it describes the
sampling distribution at the fitted exponent and not at the excluded one.

SO THE EXCLUSION IS COMPUTED BY SIMULATION. For each hypothesis the whole
four-line dataset is generated under it, each line anchored to its own
lowest-power skew, the same estimator is run, and the p-value is the fraction
of draws whose four-line mean is at least as high as the observed one. A first
version of this module quoted 6.6 sigma against the fixed-amplitude
hypothesis from the fit covariance. Read this way it is p = 0.01, about
2.6 sigma, stable across five seeds at 1500 draws.

    python scripts/run_skew_scaling.py             # writes results/skew_scaling.csv
    python scripts/run_skew_scaling.py --draws 2000
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SHOT_NOISE_EXPONENT = -0.5
FIXED_AMPLITUDE_EXPONENT = -1.0


def _power_law(amp, scale, exponent):
    return scale * amp ** exponent


def fit_exponent(amp, skew, skew_err):
    """The exponent of skew = scale * amp**exponent, with its own error.

    Linear space, absolute errors, nothing dropped. Returns
    (exponent, error, chi2, dof).
    """
    amp = np.asarray(amp, float)
    skew = np.asarray(skew, float)
    skew_err = np.asarray(skew_err, float)
    seed_scale = float(skew[0] * amp[0] ** 0.5) if skew[0] > 0 else 1.0
    popt, pcov = curve_fit(_power_law, amp, skew, p0=[seed_scale, SHOT_NOISE_EXPONENT],
                           sigma=skew_err, absolute_sigma=True, maxfev=40000)
    resid = (skew - _power_law(amp, *popt)) / skew_err
    return (float(popt[1]), float(np.sqrt(np.diag(pcov))[1]),
            float(np.sum(resid ** 2)), int(len(amp) - 2))


def simulate_hypothesis(dataset, injected, draws, rng):
    """Generate the WHOLE four-line dataset under one hypothesis and estimate it.

    Each line is anchored to its own lowest-power skew, so the injected world
    reproduces the observed low-power amplitude and differs only in how the
    skew falls. Returns the array of four-line mean exponents, which IS the
    sampling distribution the exclusion is read from.
    """
    means = []
    for _ in range(draws):
        per_line = []
        for amp, skew, skew_err in dataset:
            scale = skew[0] / amp[0] ** injected
            noisy = _power_law(amp, scale, injected) + rng.normal(0.0, skew_err)
            try:
                e, _, _, _ = fit_exponent(amp, noisy, skew_err)
            except Exception:
                e = np.nan
            per_line.append(e)
        per_line = np.asarray(per_line, float)
        if np.isfinite(per_line).all():
            means.append(float(per_line.mean()))
    return np.asarray(means, float)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    # 1500, not 400. The committed CSV was made at 1500, which is also the
    # number this module's own docstring calls stable across five seeds, so a
    # default of 400 meant the DEFAULT INVOCATION DID NOT REPRODUCE THE
    # COMMITTED FILE. Rule 19.75: the quotable number is the default
    # invocation's number. Caught by the gate's freshness check on
    # 2026-08-20, which saw the simulated scatter move from 0.301 to 0.543
    # because a standard error over 400 draws is not one over 1500.
    ap.add_argument("--draws", type=int, default=1500,
                    help="simulation draws per hypothesis (default 1500)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    src = REPO / "results" / "power_sweep.csv"
    rows = list(csv.DictReader(open(src)))
    peaks = sorted({r["peak"] for r in rows})
    rng = np.random.default_rng(args.seed)

    out = [["quantity", "key", "value", "err", "unit", "status"]]
    exponents, errors = [], []

    for pk in peaks:
        sub = sorted((r for r in rows if r["peak"] == pk),
                     key=lambda r: float(r["power_mW"]))
        amp = np.array([float(r["amp"]) for r in sub])
        skew = np.array([float(r["resid_skew"]) for r in sub])
        serr = np.array([float(r["resid_skew_err"]) for r in sub])
        e, ee, chi2, dof = fit_exponent(amp, skew, serr)
        exponents.append(e)
        errors.append(ee)
        out.append(["skew_amp_exponent", pk, f"{e:.3f}", f"{ee:.3f}",
                    "dimensionless; skew = scale x amp**exponent, linear-space "
                    "weighted fit over the power sweep's own amplitude lever",
                    "DIAGNOSTIC"])
        out.append(["skew_amp_fit_chi2_red", pk, f"{chi2 / dof:.2f}", "",
                    f"reduced chi-square of that fit on {dof} degrees of freedom",
                    "DIAGNOSTIC"])

    ex = np.asarray(exponents)
    scatter = float(ex.std(ddof=1))
    mean = float(ex.mean())
    sem = scatter / np.sqrt(len(ex))
    out.append(["skew_amp_exponent", "mean over the four lines", f"{mean:.3f}",
                f"{sem:.3f}",
                "dimensionless; the error is the SCATTER of the four lines "
                "divided by root four, which is wider than their individual "
                "errors because they disagree beyond them", "DIAGNOSTIC"])
    out.append(["skew_amp_exponent_line_scatter", "four lines", f"{scatter:.3f}",
                "", "dimensionless standard deviation of the four exponents",
                "DIAGNOSTIC"])

    # THE EXCLUSION, BY SIMULATION. Not from the fit covariance, which
    # describes the sampling distribution at the FITTED exponent rather than
    # at the excluded one, and which differs between them by a factor of
    # twenty in scatter on this dataset.
    dataset = []
    for pk in peaks:
        sub = sorted((r for r in rows if r["peak"] == pk),
                     key=lambda r: float(r["power_mW"]))
        dataset.append((np.array([float(r["amp"]) for r in sub]),
                        np.array([float(r["resid_skew"]) for r in sub]),
                        np.array([float(r["resid_skew_err"]) for r in sub])))

    for label, injected in (("shot_noise", SHOT_NOISE_EXPONENT),
                            ("fixed_amplitude", FIXED_AMPLITUDE_EXPONENT)):
        draws = simulate_hypothesis(dataset, injected, args.draws, rng)
        p_value = float(np.mean(draws >= mean)) if draws.size else float("nan")
        out.append([f"skew_hypothesis_recovered_{label}", "four-line mean",
                    f"{draws.mean():.3f}", f"{draws.std(ddof=1):.3f}",
                    f"four-line mean exponent recovered from data generated at "
                    f"{injected}, {draws.size} draws. The SCATTER is the ceiling "
                    "test: where it is large the amplitude lever carries no "
                    "information at that exponent", "DIAGNOSTIC"])
        out.append([f"skew_hypothesis_p_{label}", "one-sided", f"{p_value:.3f}",
                    "", f"fraction of worlds with exponent {injected} whose "
                    "four-line mean is at least as high as the observed one",
                    "DIAGNOSTIC"])
        print(f"hypothesis {injected}: recovered {draws.mean():+.3f} +/- "
              f"{draws.std(ddof=1):.3f}, p = {p_value:.3f}")

    dst = REPO / "results" / "skew_scaling.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh).writerows(out)
    print(f"\nmeasured exponent {mean:+.3f} +/- {sem:.3f} "
          f"(line scatter {scatter:.3f})")
    print(f"wrote {dst.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

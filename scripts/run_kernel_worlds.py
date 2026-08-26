#!/usr/bin/env python
"""K2: five hostile worlds for the mixed G+L kernel, run on the density ladder.

WHAT THIS ANSWERS. Whether a fitted Gamma_L,equiv may be read as a measurement,
and under which conditions. Preregistered in
# term-of-art: the private reviews directory is a filesystem path
private/reviews/K2_PREREG_2026-08-21.md BEFORE any world ran: the five worlds,
the acceptance thresholds, the null's attainability, and the trial count with
the precision argument that sets it.

WHY EVERY WORLD IS MULTI-CONDITION. At a fixed condition gamma_coll and
Gamma_L,equiv are EXACTLY degenerate, because both are Lorentzian widths and
Lorentzians add: measured over six injected values, the recovered SUM tracks
the true sum to a part in a thousand while the split is arbitrary. The lever
that separates them is DENSITY, since gamma_coll is beta*N(T) and a laser width
is not. A single-condition world would therefore be measuring the sum and
would answer a different question from the one asked.

THE WORLDS.
  A  true Gaussian laser, gamma_l = 0     false-positive rate on Gamma_L
  B  true mixed G+L, gamma_l > 0          coverage of the stated interval
  C  wrong baseline model                 is Gamma_L manufactured by baseline error
  D  wrong transit kernel                 is Gamma_L manufactured by transit error
  E  exact-symmetry world                 does the GRID manufacture Gamma_L

E IS DIFFERENT IN KIND. It tests the instrument rather than the model. An
estimator that manufactures Gamma_L out of discretisation produces neither
measurements nor bounds, so E failing halts K3 rather than qualifying it. This
is not hypothetical: on 2026-08-20 a finite-grid convolution made the profile
depend on how a fixed total width was SPLIT, at up to 3.7e-3 of peak, which
against this archive's noise carries up to 70-sigma of matched-filter leverage
along exactly the direction a kernel inference has to measure.
"""
from __future__ import annotations

import csv
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                       # noqa: E402
from rb5s6s.beta import fit_beta_self                # noqa: E402
from rb5s6s.forecast import synthetic_traces         # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T         # noqa: E402

OUT = C.RESULTS_DIR / "kernel_worlds.csv"

N_TRIALS = 500          # preregistered; see the prereg note for the precision argument
BETA_TRUE = 0.30        # MHz per density unit
SIGMA_L = 3.0           # MHz, the Gaussian laser component
GL_TRUE_MIXED = 0.60    # MHz, world B's injected Gamma_L,equiv
LADDER_C = (110.0, 120.0, 130.0)     # the narrow ladder the archive actually has
TREF = C.TRANSIT_FWHM_PLACEHOLDER_MHZ
T_REF_C = 110.0
FPR_THRESHOLD_MHZ = 0.15   # preregistered: "a Gamma_L above this counts as a detection"


def _n_units(T_C: float) -> float:
    return 10.0 ** ((T_C - T_REF_C) / 40.0)


def _conditions(seed: int, gl_true: float, *, world: str):
    """One trial's temperature ladder. The world's flaw is injected HERE, in the
    data, never in the fitter: a world is a wrong DATASET met by the standard
    estimator, which is what misspecification means."""
    rng = np.random.default_rng(seed)
    conds = []
    for T in LADDER_C:
        n = _n_units(T)
        tr = transit_fwhm_at_T(T, TREF, T_REF_C)
        if world == "D":
            # wrong transit kernel: data carry a Gaussian transit, the fitter
            # will assume the two-sided exponential it always assumes
            f, v = synthetic_traces(BETA_TRUE * n, SIGMA_L, tr, gamma_l=gl_true,
                                    n_traces=3, n_points=1500, noise=0.004, rng=rng)
            g, prof = __import__("rb5s6s.lineshape", fromlist=["x"]).composite_profile(
                BETA_TRUE * n, SIGMA_L, tr, "gaussian", transit_kind="gaussian",
                gamma_l=gl_true)
            v = [np.interp(fi, g, prof / prof.max()) * 1.0 + 0.010
                 + rng.normal(0.0, 0.004, size=fi.size) for fi in f]
        else:
            f, v = synthetic_traces(BETA_TRUE * n, SIGMA_L, tr, gamma_l=gl_true,
                                    n_traces=3, n_points=1500, noise=0.004, rng=rng)
        if world == "C":
            # wrong baseline: the data carry a quadratic tilt the fitter's
            # linear baseline cannot absorb
            v = [vi + 2.0e-5 * (fi - fi.mean()) ** 2 for fi, vi in zip(f, v)]
        conds.append(dict(T_C=T, N_units=n, freqs=f, volts=v, law=None))
    return conds


def _one(args):
    seed, world = args
    gl_true = GL_TRUE_MIXED if world == "B" else 0.0
    try:
        out = fit_beta_self(_conditions(seed, gl_true, world=world),
                            transit_ref_mhz=TREF, T_ref_C=T_REF_C,
                            fit_gamma_l=True)
    except Exception:
        return None
    return (float(out["gamma_l"]), float(out["gamma_l_err"]),
            float(out["beta_self"]), float(out["beta_self_err"]),
            bool(out["gamma_l_at_bound"]))


def _run(world: str, n: int):
    with ProcessPoolExecutor(max_workers=8) as ex:
        res = list(ex.map(_one, [(s, world) for s in range(n)], chunksize=8))
    return [r for r in res if r is not None]


def main(argv=None) -> int:
    # The count is a COMMAND-LINE argument with the preregistered value as its
    # default, not an environment variable: an env var set in one shell and
    # forgotten in another has silently changed what a producer measured in
    # this repository before. The count actually used is written into the CSV,
    # so a reader never has to trust the invocation.
    argv = list(sys.argv[1:] if argv is None else argv)
    n_trials = N_TRIALS
    if "--trials" in argv:
        n_trials = int(argv[argv.index("--trials") + 1])

    rows = []

    def add(world, quantity, value, unit, note):
        rows.append(dict(world=world, quantity=quantity, value=value,
                         unit=unit, note=note, status="DIAGNOSTIC"))

    for world in ("A", "B", "C", "D"):
        res = _run(world, n_trials)
        gl = np.array([r[0] for r in res])
        ge = np.array([r[1] for r in res])
        n_ok = len(res)
        add(world, "trials_completed", f"{n_ok}", "count",
            f"of {n_trials} requested ({N_TRIALS} is the preregistered value); "
            "failures are dropped and counted here")
        add(world, "gamma_l_median", f"{np.median(gl):.4f}", "MHz",
            "median fitted Gamma_L,equiv across trials")
        if world == "B":
            # coverage of the stated interval around the injected truth
            lo, hi = gl - ge, gl + ge
            cov = float(np.mean((lo <= GL_TRUE_MIXED) & (GL_TRUE_MIXED <= hi)))
            add(world, "injected_gamma_l", f"{GL_TRUE_MIXED:.4f}", "MHz",
                "the truth this world's coverage is measured against")
            add(world, "coverage_1sigma", f"{cov:.4f}", "fraction",
                "fraction of trials whose one-sigma interval contains the truth; "
                "nominal 0.68. A shortfall does not block K3 but forces every "
                "quoted interval to be recalibrated against this number first")
            add(world, "gamma_l_bias", f"{np.mean(gl) - GL_TRUE_MIXED:+.4f}", "MHz",
                "mean fitted minus injected")
        else:
            fpr = float(np.mean(gl > FPR_THRESHOLD_MHZ))
            se = float(np.sqrt(max(fpr * (1 - fpr), 1e-12) / max(n_ok, 1)))
            add(world, "false_positive_rate", f"{fpr:.4f}", "fraction",
                f"fraction of trials with fitted Gamma_L above the preregistered "
                f"{FPR_THRESHOLD_MHZ} MHz detection threshold, given a TRUE zero. "
                f"Binomial standard error {se:.4f}. Recorded as its number: a "
                "near-threshold pass is not a green light")
            add(world, "false_positive_rate_se", f"{se:.4f}", "fraction",
                "binomial standard error at the measured rate and count")

    # ---- WORLD E: the instrument, not the model -------------------------
    # The exact symmetry: gamma_coll and Gamma_L,equiv are both Lorentzian
    # widths, so a fixed SUM split differently must give a bit-identical
    # profile. Any departure is the grid manufacturing a distinction.
    from rb5s6s.lineshape import composite_profile
    worst = 0.0
    for total in (1.0, 2.0, 4.0):
        ref = None
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            g, prof = composite_profile(total * (1 - frac), SIGMA_L, 0.93,
                                        gamma_l=total * frac)
            if ref is None:
                ref_g, ref = g, prof
            else:
                if g.shape != ref.shape or not np.array_equal(g, ref_g):
                    worst = float("inf")
                else:
                    worst = max(worst, float(np.max(np.abs(prof - ref))))
    add("E", "split_invariance_max_abs_deviation", f"{worst:.3e}", "profile units",
        "maximum change in the profile when a FIXED total Lorentzian width is "
        "re-split between gamma_coll and Gamma_L,equiv. The continuum identity "
        "says this is exactly zero. Nonzero means the grid is manufacturing the "
        "separability the kernel inference has to measure, which is the "
        "2026-08-20 artefact")
    add("E", "verdict", "PASS" if worst == 0.0 else "FAIL", "verdict",
        "E tests the instrument rather than the model, so a failure halts K3 "
        "instead of qualifying it")

    add("all", "trials_per_world_used", f"{n_trials}", "count",
        f"the count this run used. The preregistered value is {N_TRIALS}, set by "
        "the precision the acceptance thresholds need rather than by the clock")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"  {r['world']}  {r['quantity']:<34} {r['value']:>12} {r['unit']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

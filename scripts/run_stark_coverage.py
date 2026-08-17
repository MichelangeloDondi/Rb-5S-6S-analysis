#!/usr/bin/env python3
"""
M14: injection-recovery COVERAGE of the AC-Stark power-lever 95% bound.

WHY THIS EXISTS. `rb5s6s/stark.py` retires the Wald bound in its own docstring
with the words "its 'sigma' is a finite-difference artifact and carries no 95%
coverage", and `docs/HISTORY.md` records the 3.1 MHz Wald value being replaced
for exactly that reason. The replacement is a profile-chi2 bound at the
over-dispersion-scaled threshold 2.706 x max(chi2_red, 1). Whether THAT
construction covers 95 per cent has never been measured. `results/coverage.csv`
is the same study for the COLLISIONAL bound (M13) and covers only beta_self:
grep its `quantity` column and no Stark row appears.

The gap matters because the fit rails at kappa = 0, which is the lower bound of
the parameter. At a boundary the likelihood-ratio statistic is not chi2_1: the
classical result is a half-and-half mixture of chi2_0 and chi2_1, under which
the one-sided 2.706 threshold is CONSERVATIVE rather than exact. Conservative
is safe for a published upper limit and would mean the quoted bound is looser
than it needs to be. The opposite is also possible once over-dispersion
scaling and a nuisance re-minimisation are layered on top, and only simulation
tells the two apart.

WHAT IT MEASURES, per arm and per true kappa:

    coverage    P(kappa_ub95 >= kappa_true), target 0.95
    bias        mean(kappa_hat) - kappa_true
    rail rate   P(kappa_hat == 0), the boundary the construction exists for
    tightness   mean(kappa_ub95), how much is paid for the coverage

for BOTH the profile bound and the Wald bound, so the docstring's claim about
Wald is measured rather than repeated.

TWO NOISE ARMS, because the production data are over-dispersed:

    nominal        sigma = fwhm_err as quoted. chi2_red -> 1, so the threshold
                   scaling max(chi2_red, 1) is inactive and this isolates the
                   2.706 threshold itself.
    overdispersed  sigma = sqrt(3.7047) x fwhm_err, the scatter the real
                   20-cell grid actually shows. This is the production path,
                   and it is the arm whose number should be quoted.

THE TRUTH MODEL IS THE ESTIMATOR'S OWN. `_simulate` calls `_fwhm_of`,
`companion_gamma_mhz` and `companion_transit_mhz` imported from `rb5s6s.stark`,
at the per-peak sigma_laser the real fit returns. So this measures the INTERVAL
CONSTRUCTION and not model misspecification. A misspecification arm is a
separate study and is deliberately not folded in here, because a coverage
number that mixes the two cannot be attributed.

OUTPUT IS DIAGNOSTIC. One row per trial to `private/run_logs/`, nothing into
`results/`, no committed number touched, following the precedent
`scripts/run_s0_block_bootstrap.py` set. Its preregistration is
`docs/notes/stark_coverage_prereg.md`, committed with this script.

    ./.venv/bin/python scripts/run_stark_coverage.py --trials 2500 --workers 8
    ./.venv/bin/python scripts/run_stark_coverage.py --trials 20 --workers 4  # smoke
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from datetime import datetime, timezone
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import stark as S  # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T  # noqa: E402

# Frozen by the preregistration. Changing any of these invalidates the run.
SEED = 20260817
T_C = 130.0
P_QUOTE_W = 0.225

# The ladder spans the boundary the construction exists for, through both
# quoted bounds, to beyond them. Values are kappa in MHz per W; the S0 at
# 225 mW each one implies is in the prereg table.
KAPPA_TRUE = (0.00, 0.25, 0.50, 0.78, 1.15, 1.56, 2.00, 2.81,
               4.00, 5.50, 7.00, 9.00)
ARMS = ("nominal", "overdispersed")

# Set from the base fit in main(). The percentile of THIS value inside the
# simulated distribution says whether the published bound is a typical
# realisation or a lucky one, which no single fit can tell you.
OBSERVED_UB95 = float("nan")


def _load_grid() -> dict:
    grid = {}
    with open(C.RESULTS_DIR / "power_sweep.csv") as fh:
        for r in csv.DictReader(fh):
            grid[(r["peak"], float(r["power_mW"]) / 1000.0)] = (
                float(r["fwhm"]), float(r["fwhm_err"]))
    return grid


def _truth(kappa_true: float, sigma_by_peak: dict, items, transit: float):
    """Noise-free FWHM per cell, from the ESTIMATOR'S OWN forward model."""
    out = []
    for (peak, P), _ in items:
        s0 = kappa_true * P
        out.append(S._fwhm_of(
            0.6 + S.companion_gamma_mhz(s0, peak),
            sigma_by_peak[peak],
            S.companion_transit_mhz(transit, s0, peak),
            s0, np.arange(-45.0, 45.0, 0.01)))
    return np.array(out)


_CTX: dict = {}


def _init(ctx):
    _CTX.update(ctx)


def _trial(job):
    arm, kappa_true, i = job
    items = _CTX["items"]
    clean = _CTX["clean"][kappa_true]
    errs = _CTX["errs"]
    scale = _CTX["scale"][arm]
    # One independent stream per (arm, kappa, trial), so a re-run of any single
    # cell reproduces bit for bit and cells never share draws.
    ss = np.random.SeedSequence([SEED, ARMS.index(arm),
                                 int(round(kappa_true * 1000)), i])
    rng = np.random.default_rng(ss)
    noisy = clean + rng.normal(0.0, errs * scale)
    grid = {k: (float(f), float(e))
            for (k, _), f, e in zip(items, noisy, errs)}
    t0 = time.time()
    try:
        res = S.fit_stark_sweep(grid, T_C=T_C)
    except Exception as exc:                       # a failed fit is data
        return dict(arm=arm, kappa_true=kappa_true, trial=i, ok=0,
                    error=type(exc).__name__, seconds=round(time.time() - t0, 3))
    return dict(
        arm=arm, kappa_true=kappa_true, trial=i, ok=1, error="",
        kappa_hat=res["kappa"], chi2_red=res["chi2_red"],
        kappa_ub95_profile=res["kappa_ub95_profile"],
        kappa_ub95_wald=res["kappa_ub95"],
        railed=int(res["kappa"] <= 1e-9),
        covered_profile=int(res["kappa_ub95_profile"] >= kappa_true),
        covered_wald=int(res["kappa_ub95"] >= kappa_true),
        seconds=round(time.time() - t0, 3))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=2500)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--outdir", default=None)
    a = ap.parse_args()

    grid = _load_grid()
    items = sorted(grid.items())
    errs = np.array([e for _, (_, e) in items])
    base = S.fit_stark_sweep(grid, T_C=T_C)
    transit = transit_fwhm_at_T(T_C, S.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    sigma_by_peak = base["sigma_laser_by_peak"]
    od = float(np.sqrt(max(base["chi2_red"], 1.0)))
    global OBSERVED_UB95
    OBSERVED_UB95 = float(base["kappa_ub95_profile"])

    clean = {k: _truth(k, sigma_by_peak, items, transit) for k in KAPPA_TRUE}
    ctx = dict(items=items, errs=errs, clean=clean,
               scale={"nominal": 1.0, "overdispersed": od})

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    outdir = Path(a.outdir) if a.outdir else (
        ROOT / "private" / "run_logs" / f"stark_coverage_{stamp}")
    outdir.mkdir(parents=True, exist_ok=True)

    jobs = [(arm, k, i) for arm in ARMS for k in KAPPA_TRUE
            for i in range(a.trials)]
    print(f"M14 Stark-bound coverage\n  base fit: kappa={base['kappa']:.4f}, "
          f"ub95_profile={base['kappa_ub95_profile']:.4f} MHz/W, "
          f"chi2_red={base['chi2_red']:.4f}\n  over-dispersion scale = "
          f"{od:.4f}\n  {len(ARMS)} arms x {len(KAPPA_TRUE)} kappa x "
          f"{a.trials} trials = {len(jobs)} fits on {a.workers} workers",
          flush=True)

    rows = []
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(ctx,)) as pool:
        for n, r in enumerate(pool.imap_unordered(_trial, jobs, chunksize=8), 1):
            rows.append(r)
            if n % 500 == 0:
                el = time.time() - t0
                print(f"  {n}/{len(jobs)}  {el/60:.1f} min elapsed, "
                      f"{el/n*(len(jobs)-n)/60:.1f} min left", flush=True)

    fields = ["arm", "kappa_true", "trial", "ok", "error", "kappa_hat",
              "chi2_red", "kappa_ub95_profile", "kappa_ub95_wald", "railed",
              "covered_profile", "covered_wald", "seconds"]
    with open(outdir / "trials.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})

    with open(outdir / "summary.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "kappa_true", "s0_225_true", "n_ok", "n_failed",
                    "coverage_profile", "coverage_profile_mcse",
                    "coverage_wald", "bias_kappa", "rail_rate",
                    "mean_ub95_profile", "median_ub95_profile",
                    "pctile_of_observed_bound",
                    "mean_ub95_wald", "mean_chi2_red"])
        for arm in ARMS:
            for k in KAPPA_TRUE:
                sel = [r for r in rows
                       if r["arm"] == arm and r["kappa_true"] == k and r["ok"]]
                nf = sum(1 for r in rows if r["arm"] == arm
                         and r["kappa_true"] == k and not r["ok"])
                if not sel:
                    w.writerow([arm, k, k * P_QUOTE_W, 0, nf] + [""] * 10)
                    continue
                n = len(sel)
                cp = float(np.mean([r["covered_profile"] for r in sel]))
                w.writerow([
                    arm, f"{k:.2f}", f"{k * P_QUOTE_W:.4f}", n, nf,
                    f"{cp:.4f}", f"{np.sqrt(cp * (1 - cp) / n):.4f}",
                    f"{np.mean([r['covered_wald'] for r in sel]):.4f}",
                    f"{np.mean([r['kappa_hat'] for r in sel]) - k:+.4f}",
                    f"{np.mean([r['railed'] for r in sel]):.4f}",
                    f"{np.mean([r['kappa_ub95_profile'] for r in sel]):.4f}",
                    f"{np.median([r['kappa_ub95_profile'] for r in sel]):.4f}",
                    f"{100.0 * np.mean([r['kappa_ub95_profile'] <= OBSERVED_UB95 for r in sel]):.1f}",
                    f"{np.mean([r['kappa_ub95_wald'] for r in sel]):.4f}",
                    f"{np.mean([r['chi2_red'] for r in sel]):.4f}"])

    print(f"\nwrote {outdir}/trials.csv and summary.csv "
          f"in {(time.time()-t0)/3600:.2f} h")
    print("DIAGNOSTIC. Nothing in results/ moved and no committed bound "
          "changed. The prereg postscript adjudicates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

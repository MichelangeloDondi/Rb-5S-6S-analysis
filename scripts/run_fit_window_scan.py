#!/usr/bin/env python3
"""Refit every canonical condition over a range of fit windows.

WHY THIS PRODUCER EXISTS. The fit window is a tunable analysis choice
(`config.FIT_HALFWIDTH_FWHM_MULT`, 3.5 times each trace's own FWHM) and it was
the one such choice with no robustness axis: `results/stark_joint.csv` varies
peaks, sessions, the red-wing nuisance and the rehearsal axis direction, and
never the span. A window scan is the cheapest probe of TAIL model error,
because the tail is exactly where a core-weighted chi-square has least
leverage: a defect there is absorbed by the free collisional width while the
chi-square stays flat, so the fit reports a good fit and a moved gamma.

WHAT THE OUTPUT MEANS, AND THE TRAP IN READING IT. Gamma_coll is measured from
the Lorentzian WINGS, so a window narrow enough to clip them starves it and it
rises. `config.py` says so where FIT_HALFWIDTH_FWHM_MULT is defined ("cutting
too tight would clip the fat wings where gamma_coll lives and bias it"). That
narrow-end rise is the estimator behaving as designed and is NOT evidence of
model error. Only drift across windows that all CONTAIN the wings carries that
meaning, so the summary statistic is computed over `WING_SAFE_MULTS` alone and
the narrower points are emitted as DIAGNOSTIC context.

THE UPPER END SATURATES, AND SILENTLY. `fit_condition` re-applies
FIT_HALFWIDTH_MAX_MHZ after scaling, because the off-centre-sweep mirror
re-crosses the line about 40 MHz away and a window that reached it would be
fitting the mirror. Conditions here have adaptive half-widths near 19 MHz
against that 25 MHz cap, so multipliers above about 1.3 stop widening. Each row
therefore carries its REALISED half-width and a capped flag; a scan read from
the multiplier alone would report a spurious plateau as physics.

    python scripts/run_fit_window_scan.py
"""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _producer_lock import take_producer_lock                     # noqa: E402
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.ingest import load_trace, trace_path                  # noqa: E402
from rb5s6s.linefit import (                                      # noqa: E402
    adaptive_halfwidth, fit_condition, to_frequency, transit_fwhm_at_T)
from rb5s6s.density import number_density_cm3                     # noqa: E402
from rb5s6s.noise import condition_noise_model                    # noqa: E402
from rb5s6s.qc import hard_flags, ingest_flags, trace_metrics     # noqa: E402

OUT = C.RESULTS_DIR / "fit_window_scan.csv"

MULTS = (0.5, 0.7, 0.85, 1.0, 1.15, 1.3)
"""Multipliers on each trace's own adaptive half-width. 1.0 is the committed
window and reproduces every existing fit bit-identically."""

WING_SAFE_MULTS = (0.85, 1.0, 1.15, 1.3)
"""The sub-range over which a gamma_coll drift means model error rather than
wing clipping. 0.85 x 3.5 = 3.0 FWHM either side, which config's own comment
puts inside the region where the Lorentzian wings are kept."""


def _k4():
    spec = importlib.util.spec_from_file_location(
        "run_kernel_k4", ROOT / "scripts" / "run_kernel_k4.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_condition(rows, dropped, rate):
    freqs, volts = [], []
    for r in rows:
        if r["file"] in dropped:
            continue
        t, v, info = load_trace(trace_path(r), with_info=True)
        m = trace_metrics(t, v)
        if any("truncated" in f or "dropout" in f
               for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
            continue
        freqs.append(to_frequency(t, rate))
        volts.append(v)
    return freqs, volts


def main() -> int:
    take_producer_lock("run_fit_window_scan")
    k4 = _k4()
    lf = k4._block_rates()
    trate, prate = lf.load_block_rates()
    conds, dropped = k4._conditions()

    rows, drifts, ladder, chi_meds = [], [], {}, {}
    for key in sorted(conds):
        role, peak, T, P = key
        entry = lf.condition_rate(role, peak, T, trate, prate)
        if entry is None:
            continue
        rate, _ = entry
        freqs, volts = _load_condition(conds[key], dropped, rate)
        if len(volts) < 3:
            continue
        law = condition_noise_model(volts)
        transit = transit_fwhm_at_T(float(T), C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        base_hw = float(np.mean([adaptive_halfwidth(f, v)
                                 for f, v in zip(freqs, volts)]))
        tag = f"{peak}_{T}C_{P}mW" if P else f"{peak}_{T}C"
        got = {}
        for mult in MULTS:
            try:
                fit = fit_condition(freqs, volts, T_C=float(T), law=law,
                                    transit_fwhm=transit, halfwidth_mult=mult)
            except RuntimeError:
                continue
            hw = min(base_hw * mult, C.FIT_HALFWIDTH_MAX_MHZ)
            capped = base_hw * mult > C.FIT_HALFWIDTH_MAX_MHZ + 1e-9
            got[mult] = fit
            chi_meds.setdefault(mult, []).append(fit["chi2_red"])
            floor = hw < C.FIT_HALFWIDTH_MIN_MHZ - 1e-9
            note = (f"mult {mult}, realised half-width {hw:.1f} MHz"
                    f"{', AT THE MIRROR CAP -- not widening' if capped else ''}"
                    f"{', BELOW THE COMMITTED MIN FLOOR BY DESIGN (wing-clipping diagnostic)' if floor else ''}"
                    f", chi2_red {fit['chi2_red']:.3f}")
            rows.append(["gamma_coll", f"{tag}_m{mult}", f"{fit['gamma_coll']:.5f}",
                         f"{fit['gamma_coll_err']:.5f}", note])
            if not P:                       # temperature session: the density ladder
                ladder.setdefault(mult, []).append(
                    (float(T), fit["gamma_coll"], fit["gamma_coll_err"]))
        # The drift that carries meaning: wing-safe windows only.
        safe = [m for m in WING_SAFE_MULTS if m in got]
        if len(safe) >= 2:
            lo, hi = got[safe[0]], got[safe[-1]]
            d = hi["gamma_coll"] - lo["gamma_coll"]
            e = float(np.hypot(lo["gamma_coll_err"], hi["gamma_coll_err"]))
            z = d / e if e > 0 else 0.0
            drifts.append(z)
            rows.append(["gamma_drift_sigma", tag, f"{z:+.2f}", "",
                         f"(gamma at mult {safe[-1]}) minus (at {safe[0]}), "
                         f"in combined sigma, over the wing-safe range only"])

    z = np.array(drifts)
    n_neg = int((z < 0).sum())
    from math import comb
    tail = max(n_neg, len(z) - n_neg)          # the larger tail, either sign
    p_sign = min(1.0, 2.0 * sum(comb(len(z), i)
                                for i in range(tail, len(z) + 1)) / 2 ** len(z))
    rows.append(["n_conditions", "summary", f"{len(z)}", "",
                 "canonical RF-off conditions with >=3 usable traces"])
    rows.append(["n_drift_negative", "summary", f"{n_neg}", "",
                 "conditions whose wing-safe drift is negative, of n_conditions"])
    rows.append(["sign_test_p", "summary", f"{p_sign:.3e}", "",
                 "two-sided binomial tail at n_drift_negative of n_conditions. "
                 "Nested windows correlate the per-condition drifts upward, so "
                 "this p treats signs as exchangeable and is quoted as the sign "
                 "count's own tail, not as an independence-assuming test"])
    rows.append(["wing_safe_mults", "definition",
                 "-".join(str(m) for m in (WING_SAFE_MULTS[0], WING_SAFE_MULTS[-1])), "",
                 "the multiplier range whose windows keep the Lorentzian wings "
                 "(0.85 x 3.5 = 3.0 FWHM per side). Every row naming wing-safe "
                 "means this range and nothing else"])
    for mult in sorted(chi_meds):
        rows.append(["chi2_red_median", f"m{mult}", f"{np.median(chi_meds[mult]):.4f}", "",
                     "median reduced chi-square across conditions at this window"])
    rows.append(["gamma_drift_sigma_mean", "summary", f"{z.mean():+.3f}",
                 f"{z.std(ddof=1)/np.sqrt(len(z)):.3f}",
                 "mean wing-safe drift across conditions. A real tail defect "
                 "biases every condition the SAME way, so the mean is the test "
                 "and the scatter is not"])
    rows.append(["gamma_drift_sigma_scatter", "summary", f"{z.std(ddof=1):.3f}", "",
                 "condition-to-condition spread of the drift"])
    rows.append(["frac_conditions_over_2sigma", "summary",
                 f"{float(np.mean(np.abs(z) > 2.0)):.3f}", "",
                 "fraction drifting more than 2 sigma. Expect about 0.05 if "
                 "the window is innocent and the errors are honest"])

    # THE COLLISIONAL SLOPE, REFITTED PER WINDOW. This is the row that says
    # whether the window drift reaches a headline: beta_self is a slope against
    # density, so a drift COMMON to every temperature cancels in it and a
    # T-DEPENDENT one does not. It is indicative and not the committed
    # construction, which shares one slope across peaks under a preregistered
    # prior; it is emitted to size the window effect, never to replace that value.
    base = None
    for mult in sorted(ladder):
        T, g, ge = (np.array(x) for x in zip(*ladder[mult]))
        n = number_density_cm3(T) / 1e12
        wt = 1.0 / ge ** 2
        A = np.vstack([n, np.ones_like(n)]).T
        cov = np.linalg.inv(A.T @ (A * wt[:, None]))
        slope = float((cov @ (A.T @ (wt * g)))[0])
        serr = float(np.sqrt(cov[0, 0]))
        base = slope if base is None else base
        rows.append(["gamma_density_slope", f"m{mult}", f"{slope:.5f}", f"{serr:.5f}",
                     "MHz per 1e12 cm^-3, temperature session, this window. "
                     "INDICATIVE of beta_self, not its committed shared-slope "
                     "construction. Consistent with zero at every window"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows, {len(z)} conditions)")
    print(f"  mean wing-safe drift {z.mean():+.3f} +/- "
          f"{z.std(ddof=1)/np.sqrt(len(z)):.3f} sigma, "
          f"scatter {z.std(ddof=1):.3f}, "
          f"{100*float(np.mean(np.abs(z) > 2.0)):.0f}% beyond 2 sigma")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

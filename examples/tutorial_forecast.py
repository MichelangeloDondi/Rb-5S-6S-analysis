#!/usr/bin/env python3
"""Every code block of docs/TUTORIAL.md, in order, runnable.

WHAT THIS IS FOR. The tutorial teaches a loop: choose an experiment,
simulate it, fit it, find what is degenerate, change the measurement,
forecast again. This file IS that loop, so the prose can never drift from
code that runs. Read them side by side.

NO ARCHIVE DATA IS READ. Runs from a bare clone:

    python examples/tutorial_forecast.py
"""
from __future__ import annotations

import sys

import numpy as np

from rb5s6s.forecast import (external_constraint_gain,
                             forecast_precision, synthetic_traces)
from rb5s6s.linefit import fit_condition

YOUR_LINE = {
    "name": "my transition",
    "gamma_coll": 0.5,
    "sigma_laser": 1.5,
    "transit_fwhm": 1.8,
}


def chapter_3_generate(rng):
    print("3. GENERATE the data your instrument would record")
    freqs, volts = synthetic_traces(
        YOUR_LINE["gamma_coll"], YOUR_LINE["sigma_laser"],
        YOUR_LINE["transit_fwhm"], span_mhz=60.0, n_points=2000,
        n_traces=5, noise=0.004, rng=rng)
    print(f"   {len(freqs)} traces of {len(freqs[0])} points, "
          f"peak {max(volts[0]):.3f} V\n")
    return freqs, volts


def chapter_4_fit(freqs, volts):
    print("4. FIT it back, and judge by the PULL")
    res = fit_condition(freqs, volts, T_C=130.0,
                        transit_fwhm=YOUR_LINE["transit_fwhm"])
    ok = True
    for name in ("gamma_coll", "sigma_laser"):
        pull = abs(res[name] - YOUR_LINE[name]) / res[f"{name}_err"]
        ok &= pull < 3.0
        print(f"   {name:12s} truth {YOUR_LINE[name]:.3f}  fitted "
              f"{res[name]:.3f} +/- {res[f'{name}_err']:.3f}  pull {pull:.2f}")
    print(f"   recovery within three of its own error: {ok}\n")
    return res, ok


def chapter_5_degeneracy(res, rng):
    print("5. FIND what is degenerate, by breaking it on purpose")
    print(f"   laser-collision correlation: {res['corr_laser_coll']:+.3f}")
    f2, v2 = synthetic_traces(YOUR_LINE["gamma_coll"], YOUR_LINE["sigma_laser"],
                              YOUR_LINE["transit_fwhm"], n_points=2000,
                              n_traces=5, noise=0.04, rng=rng)
    r2 = fit_condition(f2, v2, T_C=130.0, transit_fwhm=YOUR_LINE["transit_fwhm"])
    grew = r2["gamma_coll_err"] > res["gamma_coll_err"]
    pull2 = abs(r2["gamma_coll"] - YOUR_LINE["gamma_coll"]) / r2["gamma_coll_err"]
    print(f"   noise x10 -> error {res['gamma_coll_err']:.4f} becomes "
          f"{r2['gamma_coll_err']:.4f} (grew: {grew}), pull {pull2:.2f}")
    print("   honest failure: the error grows and the pull does not\n")
    return grew and pull2 < 3.0


def chapter_6_break_it(rng):
    print("6. CHANGE the measurement, and learn what does NOT work first")
    truth = (YOUR_LINE["gamma_coll"], YOUR_LINE["sigma_laser"],
             YOUR_LINE["transit_fwhm"])
    rows = []
    for label, kw in (("baseline, 60 MHz span, 5 traces", {}),
                      ("wider span, 300 MHz", {"span_mhz": 300.0, "n_points": 9000}),
                      ("ten times the traces", {"n_traces": 50})):
        f, v = synthetic_traces(*truth, noise=0.004,
                                rng=np.random.default_rng(5), **kw)
        r = fit_condition(f, v, T_C=130.0, transit_fwhm=truth[2])
        rows.append((label, r["corr_laser_coll"], r["gamma_coll_err"]))
        print(f"   {label:34s} corr {r['corr_laser_coll']:+.4f}  "
              f"gamma err {r['gamma_coll_err']:.4f}")
    spread = max(abs(a[1]) for a in rows) - min(abs(a[1]) for a in rows)
    print(f"   the correlation moves by {spread:.3f} across all of that: the "
          f"degeneracy is a property of the LINESHAPE, not of how much data "
          f"you collect")
    rho = rows[0][1]
    gain = external_constraint_gain(rho)
    print(f"   an INDEPENDENT laser-width measurement multiplies the "
          f"gamma_coll uncertainty by {gain:.3f}, a factor {1/gain:.1f} "
          f"improvement, which no amount of scanning matches")
    print("   that is why the campaign plan ranks it near the top\n")
    return spread < 0.05


def chapter_7_forecast():
    print("7. FORECAST your own experiment")
    out = forecast_precision(
        truth={k: YOUR_LINE[k] for k in ("gamma_coll", "sigma_laser", "transit_fwhm")},
        design={"n_points": 1200, "n_traces": 4, "noise": 0.004, "T_C": 130.0},
        n_trials=4, scalings=True)
    print(f"   gamma_coll uncertainty : {out['gamma_coll_err']:.4f} MHz")
    print(f"   sigma_laser uncertainty: {out['sigma_laser_err']:.4f} MHz")
    print(f"   correlation            : {out['corr_laser_coll']:+.3f}")
    for k, r in out["gamma_coll_err_ratio"].items():
        print(f"   {k:12s} -> uncertainty ratio {r:.3f}")
    print(f"   assumptions: {out['assumptions'][:70]}...\n")
    return out


def main() -> int:
    rng = np.random.default_rng(20260819)
    print(__doc__.splitlines()[0], "\n")
    freqs, volts = chapter_3_generate(rng)
    res, ok4 = chapter_4_fit(freqs, volts)
    ok5 = chapter_5_degeneracy(res, rng)
    ok6 = chapter_6_break_it(rng)
    chapter_7_forecast()
    ok = ok4 and ok5 and ok6
    print(f"VERDICT: {'PASS' if ok else 'FAIL'}, the loop closes: the twin "
          f"generated data, recovered its truth within the fit's own errors, "
          f"failed honestly when degraded, and forecast a design that has "
          f"not been built.")
    print("Next: python examples/campaign_twin.py, the same method applied to "
          "a real planned campaign.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

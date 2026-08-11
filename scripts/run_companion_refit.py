#!/usr/bin/env python3
"""The companion-inclusive refit, run against its own preregistration.

CONTRACT: docs/notes/companion_inclusive_refit_prereg.md, committed before this
script was written. It fixes five predictions and four stop conditions, and
nothing here may be edited to make a prediction come true. The outcome goes in
as a POSTSCRIPT to that note, never into its body.

WHAT IT RUNS, in the order the prereg sets.

  Stop condition 1 FIRST, before any result is read: the unpatched fit must
  reproduce the committed numbers exactly. If it does not, the option is not
  inert and nothing downstream means anything.

  Then the width-only bound (C3d) with the companions in the model, at both
  ends of the shift-to-Rabi ratio band, which is the one number in the chain
  this record gives as a band rather than a value.

  Then the per-line scale A, which is the whole reason the refit is
  interesting: hyperfine pumping is the only one of the three same-signature
  broadeners that differs between the four lines, so a joint fit with the four
  branching fractions HELD FIXED and one free scale is the only separation this
  method admits without a stable frequency reference.

THE CENTRAL PREDICTION IS A PREDICTION OF FAILURE. The prereg computes, in
advance and with the arithmetic shown, that this archive sees its own computed
companion at 0.02 to 0.05 sigma and returns a bound of A < 31 to 69. Scoring
that honestly is the point: a separation that appears anyway is a finding about
something else, and the record already names the candidates.

    ./.venv/bin/python scripts/run_companion_refit.py
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import stark  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_saturation_probe import _grid  # noqa: E402

RATIO_BAND = (1.2367, 1.2951)
A_GRID = tuple(float(a) for a in
               (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 31.0, 50.0, 69.0, 100.0))


def _committed(quantity: str, key: str) -> float:
    with open(C.RESULTS_DIR / "stark_sweep.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["quantity"] == quantity and r["key"] == key:
                return float(r["value"])
    raise KeyError(quantity)


def run(companions: dict | None) -> dict:
    stark.COMPANIONS = companions
    try:
        return stark.fit_stark_sweep(_grid())
    finally:
        stark.COMPANIONS = None


def _chi2_at_fixed_kappa(scale: float, ratio: float) -> float:
    """chi2 with kappa pinned and only the four per-peak cores free.

    Rebuilt here rather than borrowed, because fit_stark_sweep profiles kappa
    and this has to hold it. Everything else is production: the same
    _fwhm_of, the same companion terms, the same grid.
    """
    from scipy.optimize import least_squares

    grid = _grid()
    items = sorted(grid.items())
    peaks = sorted({p for (p, _P) in grid})
    idx = {p: i for i, p in enumerate(peaks)}
    nu = np.arange(-45.0, 45.0, 0.01)
    kappa = stark.fit_stark_sweep(grid)["kappa_pred"]
    stark.COMPANIONS = {"ratio": ratio, "scale": scale}
    try:
        def resid(sl):
            out = []
            for (peak, P), (f, ferr) in items:
                s0 = kappa * P
                fm = stark._fwhm_of(
                    0.6 + stark.companion_gamma_mhz(s0, peak), sl[idx[peak]],
                    stark.companion_transit_mhz(0.96, s0, peak), s0, nu)
                out.append((fm - f) / ferr)
            return np.array(out)
        sol = least_squares(resid, np.full(len(peaks), 1.5),
                            bounds=(np.zeros(len(peaks)),
                                    np.full(len(peaks), np.inf)),
                            max_nfev=2000)
        return float(np.sum(sol.fun ** 2))
    finally:
        stark.COMPANIONS = None


def _chi2_at(companions: dict | None, kappa: float) -> float:
    """chi2 with kappa SET to a caller's value, cores free. See _chi2_at_fixed_kappa.

    Identical construction, with kappa an argument rather than the predicted
    value, so the surface can be profiled in kappa instead of cut at one point.

    TAKES THE COMPANION DICT WHOLE rather than deriving it from the scale, and
    that is a correction. A first version passed None when the scale was zero,
    which silently turned the SATURATION term off as well, so the row at
    A = 0 was production and every other row was saturation plus pumping.
    The two differ by 27 units of chi2 at the predicted kappa, and reading that
    as a local minimum rather than as two different models is exactly the error
    this signature now prevents. Three reference points are printed instead.

    Three starts because a single start from 1.5 lands in a local minimum at
    small nonzero kappa and puts a 1.3-unit wobble into an otherwise smooth
    profile.
    """
    from scipy.optimize import least_squares

    grid = _grid()
    items = sorted(grid.items())
    peaks = sorted({p for (p, _P) in grid})
    idx = {p: i for i, p in enumerate(peaks)}
    nu = np.arange(-45.0, 45.0, 0.01)
    stark.COMPANIONS = companions
    try:
        def resid(sl):
            out = []
            for (peak, P), (f, ferr) in items:
                s0 = kappa * P
                fm = stark._fwhm_of(
                    0.6 + stark.companion_gamma_mhz(s0, peak), sl[idx[peak]],
                    stark.companion_transit_mhz(0.96, s0, peak), s0, nu)
                out.append((fm - f) / ferr)
            return np.array(out)
        best = np.inf
        for start in (0.8, 1.5, 2.5):
            sol = least_squares(resid, np.full(len(peaks), start),
                                bounds=(np.zeros(len(peaks)),
                                        np.full(len(peaks), np.inf)),
                                max_nfev=4000)
            best = min(best, float(np.sum(sol.fun ** 2)))
        return best
    finally:
        stark.COMPANIONS = None


def main() -> int:
    t0 = time.time()
    print("=" * 78)
    print("STOP CONDITION 1  the unpatched fit reproduces the committed numbers")
    base = run(None)
    want = _committed("S0_225mW_ub95_profile", "shared")
    got = base["S0_225_ub95_profile"]
    # Compare at the precision the CSV actually STORES. A first version used a
    # 1e-6 tolerance against a value written to three decimals and stopped on
    # 0.632 against 0.63250, which is the file's formatting and not the model.
    # The stronger check ran first and passed: scripts/run_stark_sweep.py
    # reproduces the whole committed CSV byte for byte with the option present
    # and off, which is what inert means.
    print(f"  committed {want:.3f} MHz   this run {got:.3f} MHz   "
          f"difference at stored precision {abs(round(got, 3) - want):.2e}")
    if abs(round(got, 3) - want) > 1e-9:
        print("  STOP. The option is not inert, so nothing below means anything.")
        return 1
    print("  inert, and the committed CSV re-runs byte-identical. Proceeding.")

    print()
    print("=" * 78)
    print("PREDICTION 2  the shared bound tightens by the factors already measured")
    print(f"  {'ratio':>8} {'S0(225) ub95':>14} {'tightening':>12}")
    for ratio in RATIO_BAND:
        r = run({"ratio": ratio, "scale": 1.0})
        s0 = r["S0_225_ub95_profile"]
        print(f"  {ratio:8.4f} {s0:14.4f} {want/s0 if s0 > 0 else float('nan'):12.2f}")
    print("  the prereg predicts about 2.8 and calls anything beyond 3 a stop")
    print("  condition rather than a result.")

    print()
    print("=" * 78)
    print("PREDICTION 1  the per-line scale A, which is predicted NOT to be measured")
    print("  Each A is a separate fit with the four branching fractions FIXED")
    print("  and only the scale multiplying them, so the profile below is in A.")
    print()
    # KAPPA IS HELD FIXED, and that correction is the substance of this run.
    # A first version left kappa free, and the fit simply drove it to zero: A
    # enters only as A x sat(S0) with S0 = kappa*P, so at kappa = 0 the whole
    # companion vanishes and A is unidentifiable BY CONSTRUCTION. The symptom
    # was chi2 identical to four decimals from A = 2 to A = 100, which is not a
    # profile but an escape. Holding kappa at the value the polarizability
    # predicts is what makes A carry the per-line contrast and nothing else,
    # and it makes the result explicitly conditional on that kappa, which is
    # what the reader needs in order to discount it.
    print(f"  {'A':>7} {'chi2':>12} {'dchi2':>9}    (kappa fixed at its "
          f"predicted value)")
    rows = []
    for a in A_GRID:
        rows.append((a, _chi2_at_fixed_kappa(a, RATIO_BAND[0])))
    c0 = min(x[1] for x in rows)
    for a, c in rows:
        print(f"  {a:7.1f} {c:12.4f} {c-c0:9.4f}")
    dchi = [(a, c - c0) for a, c in rows]
    ub = None
    for (a1, d1), (a2, d2) in zip(dchi, dchi[1:]):
        if d1 <= 2.706 < d2:
            ub = a1 + (a2 - a1) * (2.706 - d1) / (d2 - d1)
            break
    print()
    if ub is None:
        print(f"  A is UNBOUNDED on this grid: dchi2 never reaches 2.706 by "
              f"A = {A_GRID[-1]:.0f}.")
        print("  That is prediction 1 in its strongest form. The archive cannot")
        print("  see its own computed companion at all, let alone measure it.")
    else:
        print(f"  95 per cent one-sided bound on A: {ub:.1f}")
        print(f"  the prereg predicted 31 to 69. "
              f"{'INSIDE' if 31 <= ub <= 69 else 'OUTSIDE'} that range.")
    print(f"  A = 1 is the computed companion, and its dchi2 is "
          f"{dict(dchi).get(1.0, float('nan')):.4f}, which is "
          f"{np.sqrt(max(dict(dchi).get(1.0, 0.0), 0.0)):.3f} sigma.")

    print()
    print("=" * 78)
    print("PREDICTION 1 AGAIN, WITH KAPPA PROFILED RATHER THAN PINNED")
    print("  The two cuts above disagree because they are the same surface read")
    print("  along different lines. This maps it: for each A, minimise over")
    print("  kappa instead of holding it, which is what a fit would actually do.")
    print()
    kp = base["kappa_pred"]
    ks = np.round(np.linspace(0.0, kp, 25), 4)
    r0 = RATIO_BAND[0]
    print(f"  kappa_pred = {kp:.4f} MHz/W is where the pinned cut was taken")
    print()
    models = [("production, no companions", None),
              ("saturation only", {"ratio": r0, "scale": 0.0})]
    models += [(f"saturation + pumping, A = {a:g}", {"ratio": r0, "scale": a})
               for a in (0.5, 1.0, 2.0, 4.0, 8.0, 16.0)]
    print(f"  {'model':>34} {'kappa_hat':>10} {'chi2':>10} {'at kappa=0':>11}")
    prof = []
    for label, comp in models:
        cs = [_chi2_at(comp, k) for k in ks]
        j = int(np.argmin(cs))
        prof.append((label, ks[j], cs[j], cs[0]))
        print(f"  {label:>34} {ks[j]:10.4f} {cs[j]:10.4f} {cs[0]:11.4f}")
    print()
    print("  THE kappa = 0 COLUMN IS AN EXACT SELF-CHECK. Both companions are")
    print("  proportional to S0 = kappa*P, so they must vanish there and every")
    print("  row must return the production chi2.")
    null = prof[1][2]      # saturation only, which is the null for pumping
    print()
    print("  dchi2 measured against SATURATION ONLY, which is the right null")
    print("  for a question about the pumping scale:")
    print(f"  {'model':>34} {'dchi2':>9} {'sigma':>7}")
    for label, _k, c, _z in prof:
        d = c - null
        print(f"  {label:>34} {d:9.4f} "
              f"{np.sqrt(abs(d)):7.2f}{'' if d >= 0 else '  (better)'}")

    print()
    print("=" * 78)
    print(f"({(time.time()-t0)/60:.1f} min) Nothing was written. The outcome goes")
    print("into the preregistration as a postscript, never into its body.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

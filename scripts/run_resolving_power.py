#!/usr/bin/env python3
"""
M17 -- resolving power: which observables can answer the density question?

Every archival result is reported as a MEASURED value or as a BOUND, and
those statuses were each argued separately -- by monotonicity tests, by
degeneracy analysis, by model comparison. This module asks whether one
number predicts them all.

The idea is the one the pilot investigation kept running into (addendum 17
and its postscript): an observable is only as informative as the ratio
between how much it MOVES across the conditions of interest and how much it
scatters when nothing physical is changing. Both are measurable here:

  dynamic range  ln(max/min) of the per-dwell mean over the 70-130 C sweep
  block noise    relative scatter between blocks at FIXED conditions, taken
                 from the 130 C power ladder -- five blocks at one
                 temperature, where the width is power-independent (the C3
                 null) so any spread between them is instrumental
  ratio          the dynamic range measured in block-noise units

Both are in log space because these are multiplicative quantities; mixing a
log ratio for one and a fractional range for another is what made the first
version of this table wrong.

The ratio reproduces the archive's own status assignments, which is the
result: amplitude resolves the sweep ~45x over and is the one place the
archive extracts a NUMBER (the cold spot, addendum 16); the widths sit at
1.5-5 and are exactly where it reports BOUNDS.

It is also predictive, and that is what it is for. The October prescription
(PLAN 8) has two halves -- hot points at 150-170 C to grow the signal, and
interleaving with per-trace power logging to shrink the block noise. The
projection at the end shows the temperature lever ALONE buys only ~1-3 sigma
per block, so the second half is not a refinement of the first: both are
load-bearing.

Writes results/resolving_power.csv. Status DIAGNOSTIC -- this measures the
experiment's sensitivity, not the atom.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C  # noqa: E402

# PLAN M4 / BIG_PICTURE 4: the collisional width moves this much once the
# sweep reaches 150-170 C. Quoted as a range because beta_self is a bound.
HOT_POINT_SIGNAL_MHZ = (0.07, 0.25)


def _sweep_and_ladder():
    d = pd.read_csv(C.RESULTS_DIR / "linefit_conditions.csv")
    sweep = d[(d.role == "t_sweep") | ((d.role == "p_sweep") & (d["T"] == 130))]
    ladder = d[(d.role == "p_sweep") & (d["T"] == 130)]
    return d, sweep, ladder


def _rel_block_noise(frame: pd.DataFrame, col: str) -> float:
    """Relative scatter between blocks at fixed conditions, averaged over peaks."""
    g = frame.groupby("peak")[col]
    return float((g.std() / g.mean()).mean())


def main() -> int:
    _, sweep, ladder = _sweep_and_ladder()
    rows = []

    for col in ("total_fwhm", "gamma_coll", "sigma_laser"):
        per_T = sweep.groupby("T")[col].mean()
        rng = float(np.log(per_T.max() / per_T.min()))
        noise = _rel_block_noise(ladder, col)
        rows.append((col, rng, noise, rng / noise))

    # amplitude: the density lever proper. Its block noise is measured on the
    # same ladder after removing the P^2 dependence, so what remains is
    # instrumental (alignment, lock state, the un-logged power).
    amp = pd.read_csv(C.RESULTS_DIR / "amplitude_trapping.csv")
    per_T = amp.groupby("T").amp.mean()
    rng = float(np.log(per_T.max() / per_T.min()))
    q = pd.read_csv(C.RESULTS_DIR / "qc_metrics.csv")
    lad = q[(q.role == "p_sweep") & (q.temperature_C == 130)].dropna(subset=["power_mW"])
    lad = lad.assign(scaled=lad.height_v / (lad.power_mW / 100.0) ** 2)
    noise = _rel_block_noise(lad, "scaled")
    rows.append(("amplitude", rng, noise, rng / noise))

    def verdict(r: float) -> str:
        return "RESOLVES" if r > 10 else "MARGINAL" if r > 3 else "CANNOT_RESOLVE"

    print("M17 -- resolving power for the 70-130 C density question")
    print("(dynamic range in block-noise units; both in log space)\n")
    print(f"  {'observable':<13} {'range':>7} {'noise':>7} {'ratio':>7}   verdict")
    for name, rg, no, r in rows:
        print(f"  {name:<13} {rg:>7.2f} {no:>7.1%} {r:>7.1f}   {verdict(r)}")

    print("\nThe archive reports, having argued each separately:")
    print("  amplitude   -> the cold spot as a NUMBER (addendum 16)")
    print("  total_fwhm  -> beta_self as a BOUND (C1)")
    print("  gamma_coll  -> a residual FLOOR, not resolved collisions (C1)")
    print("  sigma_laser -> a BOUND, degenerate with w0 (C2)")
    print("-> one ratio predicts all four statuses.")

    # ---- what October's two prescriptions each buy ------------------------
    w = float(sweep.total_fwhm.mean())
    noise_w = w * _rel_block_noise(ladder, "total_fwhm")
    print(f"\nPROJECTION. total_fwhm block noise = {noise_w:.3f} MHz.")
    print("PLAN M4's 150-170 C points move the collisional width "
          f"{HOT_POINT_SIGNAL_MHZ[0]}-{HOT_POINT_SIGNAL_MHZ[1]} MHz:\n")
    print(f"  {'scenario':<46} {'per-block sigma':>15}")
    proj = []
    for lbl, sig, nz, tag in (
            ("2025 as taken, 70-130 C", 0.02, noise_w, "archival"),
            ("hot points only, block noise unchanged", HOT_POINT_SIGNAL_MHZ[0], noise_w, "hot_only_low"),
            ("hot points only, optimistic end", HOT_POINT_SIGNAL_MHZ[1], noise_w, "hot_only_high"),
            ("hot points AND block noise cut 4x", HOT_POINT_SIGNAL_MHZ[0], noise_w / 4, "both_low"),
            ("hot points AND block noise cut 4x, optimistic", HOT_POINT_SIGNAL_MHZ[1], noise_w / 4, "both_high")):
        print(f"  {lbl:<46} {sig/nz:>15.1f}")
        proj.append((tag, sig, nz, sig / nz))
    print("\n-> the temperature lever alone buys ~1-3 sigma per block. The")
    print("   interleaving and per-trace power logging that cut the block noise")
    print("   are co-limiting, not a refinement: both halves are load-bearing.")

    out = C.RESULTS_DIR / "resolving_power.csv"
    with open(out, "w", newline="") as f:
        wtr = csv.writer(f)
        # `signal` and `noise` mean different things in the two row kinds, so
        # `units` says which -- the observable rows are log-space and
        # dimensionless, the projections are widths in MHz.
        wtr.writerow(["kind", "observable", "signal", "noise", "ratio",
                      "units", "verdict"])
        for name, rg, no, r in rows:
            wtr.writerow(["observable", name, f"{rg:.6g}", f"{no:.6g}",
                          f"{r:.6g}", "ln_range_vs_rel_scatter", verdict(r)])
        for tag, sig, nz, r in proj:
            wtr.writerow(["projection", tag, f"{sig:.6g}", f"{nz:.6g}",
                          f"{r:.6g}", "MHz", "PLAN_8_projection"])
    print(f"\nwrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

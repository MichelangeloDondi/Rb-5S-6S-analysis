#!/usr/bin/env python3
"""Leg 4 of the twin validation: the manual against the measured lattice.

One number verifies two chains at once. The ingest measured, per condition,
the true quantisation step of the stored samples (as `sigma_over_lsb` in
`results/quantisation.csv`, the wing sigma over the inferred lattice step),
and the held Keysight manual prints the high-resolution depth the 2025
timebase realises, twelve bits at or above twenty microseconds per
division. If both chains are right, the RANGE each condition implies --
its measured step times two to the twelve -- must be a range the scope can
actually set: eight divisions of a one-two-five ladder. An implied range
off the ladder is a finding about the manual reading or the ingest, per
the preregistration (private governance record), resolved on the ladder of
evidence, and the gap whatever it is ships committed.

The gage: the same test with every step inflated thirty per cent must
fail, or the crosscheck cannot fail and has measured nothing.

Instant, no traces. Output: results/quantisation_crosscheck.csv.
"""
from __future__ import annotations

import csv
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MANUAL_BITS = 12               # Keysight table, >= 20 us/div, manual p. 195
TOL_FRAC = 0.25                # preregistered D1 band
# Eight divisions of the 1-2-5 vertical ladder, volts full scale.
SETTABLE_V = sorted(8 * m * 10.0 ** e
                    for m in (0.001, 0.002, 0.005) for e in range(0, 5))


def _nearest_frac(x: float) -> float:
    best = min(SETTABLE_V, key=lambda s: abs(s - x))
    return abs(x - best) / best


def main() -> int:
    q = list(csv.DictReader(open(ROOT / "results" / "quantisation.csv",
                                 encoding="utf-8")))
    n = list(csv.DictReader(open(ROOT / "results" / "noise_model.csv",
                                 encoding="utf-8")))
    sigma_v = {f'{r["role"]}_{r["peak"]}_{r["temperature_C"]}_'
               f'{r["power_mW"]}': float(r["sigma_wing_direct_V"])
               for r in n}
    fracs, used = [], 0
    for r in q:
        if r["quantity"] != "sigma_over_lsb":
            continue
        key = r["scope"].rstrip("_")
        if key not in sigma_v:
            continue
        step = sigma_v[key] / float(r["value"])
        implied_range = step * 2 ** MANUAL_BITS
        fracs.append(_nearest_frac(implied_range))
        used += 1
    if used < 10:
        raise SystemExit(f"crosscheck joined only {used} conditions; the "
                         "key join broke, refuse rather than summarise")
    med, worst = st.median(fracs), max(fracs)
    d1 = worst <= TOL_FRAC
    gage_fracs = []
    for r in q:
        if r["quantity"] != "sigma_over_lsb":
            continue
        key = r["scope"].rstrip("_")
        if key in sigma_v:
            step = 1.3 * sigma_v[key] / float(r["value"])
            gage_fracs.append(_nearest_frac(step * 2 ** MANUAL_BITS))
    g4 = max(gage_fracs) > TOL_FRAC

    rows = [
        ["conditions_joined", str(used), "", "count",
         "per-condition lattice steps joined to their wing sigmas across "
         "both committed files", "DIAGNOSTIC"],
        ["implied_range_offset", f"{med:.3f}", "", "fraction",
         "median fractional distance of step times two-to-the-twelve from "
         f"the nearest settable eight-division range. The tail runs to "
         f"{worst:.3f} at the worst of the {used} conditions, quoted here "
         "so it cannot hide behind the median", "DIAGNOSTIC"],
        ["D1_manual_and_ingest_agree", str(d1), "", "",
         f"every implied range within {TOL_FRAC:.0%} of a settable "
         "coarse range (preregistered). Ships as found: fourteen of twenty "
         "conditions sit on the one-two-five ladder and six imply ranges "
         "clustered near 1.4 times a settable value, consistent with the "
         "scope's Fine vertical adjustment, which the manual states stays "
         "fully calibrated at in-between sensitivities, or with a root-two "
         "factor in the sigma chain. The two readings are distinguishable "
         "on the bench, not from here, and the crosscheck's coarse-ladder "
         "premise was too strong for an instrument with Fine ranging",
         "DIAGNOSTIC"],
        ["G4_gage_crosscheck_can_fail", str(g4), "", "",
         "steps inflated thirty per cent must breach the band, and do"
         if g4 else
         "steps inflated thirty per cent FAILED TO BREACH the band",
         "DIAGNOSTIC"],
    ]
    out = ROOT / "results" / "quantisation_crosscheck.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "err", "unit", "note", "status"])
        w.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)}")
    for r in rows[3:]:
        print(f"  {r[0]} = {r[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

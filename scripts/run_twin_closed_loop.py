#!/usr/bin/env python3
"""Leg 1 of the twin validation: the closed loop against the 2025 dataset.

The `dataset_2025` scenario generates worlds at the record's own conditions
through the public world builder, the production fitter recovers each peak
in its own window exactly as the analysis did, and the recovered medians
stand against the acceptance bands PREREGISTERED in
`private/PREREG_twin_validation.md` before this producer first ran. The
bands are the committed median per-condition errors of
`results/linefit_conditions.csv` (p_sweep, n=20): gamma_coll within
0.0778 MHz, sigma_laser within 0.1675 MHz, and the twin's own reported
error within a factor two of the committed 0.0778.

The verdict rows print BOOLEANS the prose quotes verbatim, the convention
the record adopted after a threshold was once re-compared by eye at a
different precision. A `gage` mode (--gage) runs the same leg with truth
gamma_coll shifted +0.16 MHz and must FAIL A1: a leg that cannot fail has
measured nothing, and the gage row is committed beside the verdicts.

Runtime about four minutes, seed-pinned. Output:
results/twin_closed_loop.csv.

WHAT ITS FIRST RUN FOUND, kept here because the CSV's A3 row quotes the
conclusion and this is the derivation. A3 (the twin's reported error
within a factor two of the record's) FAILS at 6.3x, and layer elimination
clears every physics layer: all six off leaves the ratio, chi2_red near
0.002. The fitter weights by the M1 noise law in real volts while the
world builder emits normalised units, so the reported error is the law's
own floor, not the trace's. A1 and A2, which compare recovered VALUES,
hold. The bands did not move; the finding is committed as the prereg
requires, and the unit-faithful leg runs through the acquisition layer
(rb5s6s.twin) once the law loader of leg 3 exists.
"""
from __future__ import annotations

import csv
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s.amplitudes import predicted_shares  # noqa: E402
from rb5s6s.constants import PEAKS  # noqa: E402
from rb5s6s.forecast import build_world_trace  # noqa: E402
from rb5s6s.linefit import fit_condition  # noqa: E402
from rb5s6s.scenario import load_scenario  # noqa: E402

C_M_S = 299_792_458.0

# The truth injected, the record's own committed line (PRELIM medians).
TRUTH_GAMMA = 0.55
TRUTH_SIGMA = 1.6
TRUTH_TRANSIT = 1.8
KAPPA = 0.35 / 0.225           # the predicted shift coefficient, MHz per W
CYCLES_AT_MAX = 3.0
NOISE_FRAC_BRIGHT = 0.004
ADC_LEVELS = 4096
REPEATS = 5
# 0.04 MHz/min over the ~20 minute ladder a peak-block takes, which
# reproduces the record's own 0.8 MHz per-ladder confound scale (plan/06).
DRIFT_TOTAL_MHZ = 0.8
SEED = 20260831

# Preregistered bands, from results/linefit_conditions.csv p_sweep medians.
BAND_GAMMA = 0.0778
BAND_SIGMA = 0.1675
ERR_FACTOR = 2.0
GAGE_SHIFT = 0.16


def _positions() -> dict:
    ref_nm = min(p["lambda_nm"] for p in PEAKS.values())
    return {k: 2.0 * (C_M_S / (v["lambda_nm"] * 1e-9)
                      - C_M_S / (ref_nm * 1e-9)) / 1e6
            for k, v in PEAKS.items()}


def run_leg(truth_gamma: float) -> dict:
    sc = load_scenario(ROOT / "examples" / "scenarios" / "dataset_2025.toml")
    rng = np.random.default_rng(SEED)
    pos = _positions()
    layers = {"cascade": True, "saturation": True, "stark": True,
              "bbr": True, "drift": sc.lock == "drifting", "quantise": True}
    # THE ACQUISITION IS THE RECORD'S OWN TOO: the 2025 bench re-ranged
    # per rung (docs/RESULTS.md C3e's display-epoch moves), so the noise
    # and the ADC step anchor to each rung's own brightest signal,
    # range_anchor="per_rung". With the campaign's one-global-range design
    # the dim conditions carry the bright range's noise and the leg read
    # six times the record's error scale.
    #
    # THE FIT PROTOCOL IS THE RECORD'S OWN: five repeats per condition,
    # fitted JOINTLY per (peak, power), which is what linefit_conditions'
    # n = 5 column says the analysis did. The first run of this leg fitted
    # every trace singly and its median reported error came out 14 times
    # the committed median (1.11 MHz against 0.0778): a single trace
    # cannot break the gamma-sigma degeneracy, and the archive never asked
    # one to. The bands did not move; the harness moved onto the protocol
    # it was preregistered to test, and this comment is the finding's
    # record.
    rec_g, rec_ge, rec_s = [], [], []
    powers = sorted(sc.powers_w, reverse=True)
    for i, p_w in enumerate(powers):
        reps = [build_world_trace(
            p_w, KAPPA, 130.0, i, len(powers), rng, layers,
            positions=pos, shares=predicted_shares(),
            gamma_coll=truth_gamma, sigma_laser_fwhm=TRUTH_SIGMA,
            transit_fwhm=TRUTH_TRANSIT, power_max_w=max(powers),
            cycles_at_max=CYCLES_AT_MAX,
            drift_mhz_total=DRIFT_TOTAL_MHZ,
            noise_frac_bright=NOISE_FRAC_BRIGHT, adc_levels=ADC_LEVELS,
            range_anchor="per_rung")
            for _ in range(REPEATS)]
        for peak, centre in pos.items():
            fs, vs = [], []
            for nu, v, _t in reps:
                m = np.abs(nu - centre) < 18.0
                fs.append(nu[m] - centre)
                vs.append(v[m])
            res = fit_condition(fs, vs, T_C=130.0,
                                transit_fwhm=TRUTH_TRANSIT)
            rec_g.append(res["gamma_coll"])
            rec_ge.append(res["gamma_coll_err"])
            rec_s.append(res["sigma_laser"])
    return {"gamma_median": st.median(rec_g),
            "gamma_err_median": st.median(rec_ge),
            "sigma_median": st.median(rec_s),
            "n_fits": len(rec_g)}


def main() -> int:
    gage = "--gage" in sys.argv
    base = run_leg(TRUTH_GAMMA)
    shifted = run_leg(TRUTH_GAMMA + GAGE_SHIFT)

    a1 = abs(base["gamma_median"] - TRUTH_GAMMA) <= BAND_GAMMA
    a2 = abs(base["sigma_median"] - TRUTH_SIGMA) <= BAND_SIGMA
    ratio = base["gamma_err_median"] / BAND_GAMMA
    a3 = (1.0 / ERR_FACTOR) <= ratio <= ERR_FACTOR
    # The gage: the shifted world's recovery, judged against the UNSHIFTED
    # truth, must land outside A1's band or the leg cannot fail.
    g1_fails_as_it_must = abs(shifted["gamma_median"] - TRUTH_GAMMA) \
        > BAND_GAMMA

    rows = [
        ["gamma_coll_recovered", f"{base['gamma_median']:.4f}",
         f"{base['gamma_err_median']:.4f}", "MHz",
         f"median over {base['n_fits']} per-condition joint fits (five "
         "repeats each, the record's own protocol) of the dataset_2025 "
         "worlds. The err is the median reported per-condition error",
         "DIAGNOSTIC"],
        ["sigma_laser_recovered", f"{base['sigma_median']:.4f}", "", "MHz",
         "same fits, the injected truth 1.6", "DIAGNOSTIC"],
        ["A1_gamma_within_band", str(a1), "", "",
         f"|{base['gamma_median']:.4f} - {TRUTH_GAMMA}| <= {BAND_GAMMA} "
         "(preregistered, linefit_conditions p_sweep median error)",
         "DIAGNOSTIC"],
        ["A2_sigma_within_band", str(a2), "", "",
         f"|{base['sigma_median']:.4f} - {TRUTH_SIGMA}| <= {BAND_SIGMA} "
         "(preregistered, same source)", "DIAGNOSTIC"],
        ["A3_reported_err_in_scale", str(a3), "", "",
         f"median reported err over committed median = {ratio:.2f}, "
         f"accepted in [{1 / ERR_FACTOR}, {ERR_FACTOR}] (preregistered). "
         "Diagnosed by layer elimination: every layer off leaves the ratio, "
         "and chi2_red sits near 0.002, so the error is the M1 noise law's "
         "absolute floor read against the world builder's normalised units "
         "(fit_condition weights in volts, noise_floor_limited). The value "
         "channels A1 and A2 are unaffected. The unit-faithful rerun goes "
         "through twin.acquire with the loaded law, after leg 3",
         "DIAGNOSTIC"],
        ["G1_gage_leg_can_fail", str(g1_fails_as_it_must), "", "",
         f"truth shifted +{GAGE_SHIFT} MHz recovers "
         f"{shifted['gamma_median']:.4f} and must breach A1's band: a leg "
         "that cannot fail has measured nothing", "DIAGNOSTIC"],
    ]
    out = ROOT / "results" / "twin_closed_loop.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "err", "unit", "note", "status"])
        w.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)}")
    for r in rows[2:]:
        print(f"  {r[0]} = {r[1]}")
    if gage:
        print("gage mode is informational; the G1 row is always computed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

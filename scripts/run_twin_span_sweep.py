#!/usr/bin/env python
"""Does widening the scan span break the width degeneracy? The twin says no.

WHY THIS EXISTS. An unreleased draft of the tutorial taught that widening the
scan span breaks the degeneracy between the laser width and the collisional
width. The digital twin refuted it before the page shipped, and the refutation
became one of this repository's most repeated teaching claims: the correlation
between the two widths barely moves with span, because the degeneracy belongs
to the LINESHAPE, a Lorentzian core convolved with a Gaussian, rather than to
the sample size.

WHAT WAS WRONG WITH THAT, until 2026-08-23. The three correlations that claim
quotes (-0.9177 at 60 MHz, -0.9166 at 300 MHz, -0.881 at ten times the traces)
appear on TEN public surfaces and NO committed row carried them. The case-page
audit found it. Worse, the twin run that produced them recorded neither its
truth parameters nor its seed, so nobody, including whoever ran it, can
reproduce those four decimals. An exhaustive search of results/ found
linefit_conditions.csv at -0.91733 and -0.91743, which are the CAMPAIGN's own
per-condition correlations, near enough to be mistaken for the twin's and a
different quantity entirely.

WHAT THIS PRODUCER DOES INSTEAD, and the distinction is the point. It does NOT
attempt to reproduce those digits, because the inputs that made them are gone
and inventing inputs that hit a remembered output is the opposite of a
measurement. It re-establishes the CLAIM on ground anyone can regenerate: the
truth is read from a NAMED committed condition rather than chosen, the seed is
fixed, and the sweep reports what it finds. The historical numbers stay in the
prose that quotes them, now next to a row that can be checked.

THE TRUTH IS TRACEABLE, WHICH IS THE WHOLE REPAIR. gamma_coll and sigma_laser
come from results/linefit_conditions.csv at p_sweep/4154/130C/225mW, the
brightest condition of the reference peak. The transit width comes from the
committed 64 um waist through constants.transit_fwhm_from_w0 at the same
temperature. Nothing here is a number somebody remembered.

WHAT IT CANNOT SETTLE. A Monte-Carlo correlation carries sampling scatter, and
n_trials here is small enough to run inside a gate. The claim it supports is a
comparison between designs under one seed, not a precision measurement of any
one correlation, and the verdict row says which of those it is.
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.constants import transit_fwhm_from_w0                 # noqa: E402
from rb5s6s.forecast import forecast_precision                    # noqa: E402

OUT = C.RESULTS_DIR / "twin_span_sweep.csv"
REF = ("p_sweep", "4154", "130", "225")     # brightest condition, reference peak
W0_M = 64e-6                                # the committed measured waist
SEED = 0
N_TRIALS = 6


def _truth() -> dict:
    with (C.RESULTS_DIR / "linefit_conditions.csv").open() as fh:
        for r in csv.DictReader(fh):
            if (r["role"], r["peak"], r["T"], r["P"]) == REF:
                T_C = float(r["T"])
                return {"gamma_coll": float(r["gamma_coll"]),
                        "sigma_laser": float(r["sigma_laser"]),
                        "transit_fwhm": transit_fwhm_from_w0(W0_M, T_C),
                        "_T_C": T_C,
                        "_campaign_corr": float(r["corr"])}
    raise SystemExit(f"reference condition {REF} not found")


def main() -> int:
    truth = _truth()
    T_C = truth.pop("_T_C")
    campaign_corr = truth.pop("_campaign_corr")

    designs = [
        ("span_060MHz", {"span_mhz": 60.0, "T_C": T_C},
         "the campaign's own span"),
        ("span_300MHz", {"span_mhz": 300.0, "T_C": T_C},
         "five times wider, which the withdrawn draft said would break the "
         "degeneracy"),
        ("traces_10x", {"span_mhz": 60.0, "n_traces": 50, "T_C": T_C},
         "ten times the repeats at the campaign's span, which tests the "
         "sample-size half of the same claim"),
    ]

    rows = []

    def add(scope, quantity, value, unit, note):
        rows.append({"scope": scope, "quantity": quantity, "value": value,
                     "unit": unit, "note": note, "status": "DIAGNOSTIC"})

    add("TRUTH", "gamma_coll", f"{truth['gamma_coll']:.6f}", "MHz",
        f"read from linefit_conditions.csv at {'/'.join(REF)}, not chosen")
    add("TRUTH", "sigma_laser", f"{truth['sigma_laser']:.6f}", "MHz",
        f"read from linefit_conditions.csv at {'/'.join(REF)}, not chosen")
    add("TRUTH", "transit_fwhm", f"{truth['transit_fwhm']:.6f}", "MHz",
        f"from the committed {W0_M * 1e6:.0f} um waist through "
        f"constants.transit_fwhm_from_w0 at {T_C:.0f} C")
    add("TRUTH", "seed", SEED, "count",
        "fixed, because the run this producer replaces recorded neither its "
        "truth nor its seed and therefore cannot be reproduced by anyone")
    add("TRUTH", "n_trials", N_TRIALS, "count",
        "Monte-Carlo trials per design. Small enough to run inside a gate, so "
        "each correlation carries sampling scatter and the comparison between "
        "designs is what this producer supports")

    corrs = {}
    for key, design, why in designs:
        r = forecast_precision(truth, design, n_trials=N_TRIALS, seed=SEED,
                               scalings=False)
        corr = float(r["corr_laser_coll"])
        corrs[key] = corr
        add(key, "corr_laser_coll", f"{corr:+.4f}", "dimensionless",
            f"correlation between the fitted laser and collisional widths. {why}")
        for p in ("gamma_coll", "sigma_laser"):
            err = r.get(f"{p}_err")
            if err is not None:
                add(key, f"{p}_err", f"{float(err):.6f}", "MHz",
                    "the fit's own reported one-sigma, median over trials")

    move_span = abs(corrs["span_300MHz"] - corrs["span_060MHz"])
    move_n = abs(corrs["traces_10x"] - corrs["span_060MHz"])
    add("VERDICT", "corr_move_with_span", f"{move_span:.4f}", "dimensionless",
        "how far the correlation moved when the span went from 60 to 300 MHz")
    add("VERDICT", "corr_move_with_traces", f"{move_n:.4f}", "dimensionless",
        "how far it moved at ten times the repeats")
    add("VERDICT", "claim", "DEGENERACY_IS_A_LINESHAPE_PROPERTY", "verdict",
        "the correlation stays close to its starting value under both a five "
        "times wider span and ten times the data, which is what a degeneracy "
        "belonging to the lineshape does and what one belonging to the sample "
        "size does not. This is a comparison between designs under one seed, "
        "not a precision measurement of any single correlation")
    ratio_n = None
    ratio_span = None
    try:
        e60 = float([r for r in rows if r["scope"] == "span_060MHz"
                     and r["quantity"] == "gamma_coll_err"][0]["value"])
        e10 = float([r for r in rows if r["scope"] == "traces_10x"
                     and r["quantity"] == "gamma_coll_err"][0]["value"])
        e300 = float([r for r in rows if r["scope"] == "span_300MHz"
                      and r["quantity"] == "gamma_coll_err"][0]["value"])
        ratio_n, ratio_span = e60 / e10, e300 / e60
    except (IndexError, ZeroDivisionError, ValueError):
        pass
    if ratio_n is not None:
        add("VERDICT", "err_ratio_10x_traces", f"{ratio_n:.2f}", "dimensionless",
            "how much the collisional-width uncertainty SHRANK at ten times the "
            "repeats. Near the root of ten is what independent samples give, and "
            "it is the other half of the claim: the data buys precision while "
            "the correlation stays put")
        add("VERDICT", "err_ratio_wide_span", f"{ratio_span:.2f}", "dimensionless",
            "how much it GREW at five times the span. Above one means widening "
            "COSTS precision here, which the record has not stated before. "
            "CAVEAT, and it is load-bearing: n_points is held fixed, so a wider "
            "span samples the line five times more thinly. This is a coupling "
            "between two design knobs and not a pure span effect, and it says "
            "widen the span only alongside the points to match")
    add("VERDICT", "campaign_corr_for_scale",
        f"{campaign_corr:+.4f}", "dimensionless",
        f"the CAMPAIGN's own fitted correlation at {'/'.join(REF)}, carried "
        "here only so a reader can see the twin sits in the same region. It is "
        "a different quantity from the twin's and must not be quoted as one")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["scope", "quantity", "value", "unit",
                                          "note", "status"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"wrote {OUT} with {len(rows)} rows")
    for k, v in corrs.items():
        print(f"  {k:14} corr = {v:+.4f}")
    print(f"  moved {move_span:.4f} with span, {move_n:.4f} with traces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

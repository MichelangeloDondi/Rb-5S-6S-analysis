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
committed central waist (constants.W0_CENTRAL_M, 42.38 um) through constants.transit_fwhm_from_w0 at the same
temperature. Nothing here is a number somebody remembered.

WHAT IT CANNOT SETTLE. A Monte-Carlo correlation carries sampling scatter, and
n_trials here is small enough to run inside a gate. The claim it supports is a
comparison between designs under one seed, not a precision measurement of any
one correlation, and the verdict row says which of those it is.

THE CLAIM IS COMPUTED, SINCE V7.1 (F552). Until 2026-09-26 the claim row was a
constant this producer wrote whatever the moves read, and on the table rebuilt at
the calculated waist the correlation moved by 0.15 at ten times the traces while
the row still said it stayed put. Each design's correlation now carries the
standard error of its median over the trials, each move is read in units of the
two errors in quadrature, and `_verdict` names the claim from those two readings.
At leading order a replicated design scales the information matrix and leaves its
correlation unchanged, so a move with the traces is the fit's nonlinearity at the
one-trace precision or the seed's draw, never a property of the sample size.

AND THE RECORD'S OWN CORRELATION IS A CELL. The CAMPAIGN rows carry the median,
the quartiles and the extremes of the per-condition correlations in
linefit_conditions.csv, with the conditioning factor 1/sqrt(1 - corr^2) at each:
what an independent laser width buys the collisional width. Sixteen pages quoted
these as copies, and the rebuild at the calculated waist reached none of them.
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.constants import W0_CENTRAL_M, transit_fwhm_from_w0  # noqa: E402
from rb5s6s.forecast import forecast_precision                    # noqa: E402

#: O58: this module's twin runs are a declared STUDY, and this is its reason
_TWIN_STUDY = "the twin's span sweep, a study of the width channel's grid"

OUT = C.RESULTS_DIR / "twin_span_sweep.csv"
REF = ("p_sweep", "4154", "130", "225")     # brightest condition, reference peak
W0_M = W0_CENTRAL_M                        # the committed waist convention, read from the
                                            # constant so it follows a change rather than
                                            # standing as a copy of it (ssot-guard, 2026-09-18)
SEED = 0
N_TRIALS = 6
#: a move is RESOLVED when it exceeds this many of its trials' standard errors (F552)
Z_MOVED = 2.0
#: and MATERIAL when it changes what an independent laser width buys, the conditioning factor
#: 1/sqrt(1 - corr^2), by at least this fraction. Added when the first computed verdict called a
#: 0.0089 move of the correlation a span effect: resolved at 47 standard errors because the trials
#: agree to four decimals, and a 6 per cent change of the factor. The claim is about the second.
PIN_MATERIAL = 0.10
#: the standard error of a sample median is this times sd/sqrt(n) under normal theory
MEDIAN_SE = 1.2533


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


def _campaign_rows() -> list:
    """Every condition of linefit_conditions.csv whose fit carries a width correlation."""
    with (C.RESULTS_DIR / "linefit_conditions.csv").open() as fh:
        return [r for r in csv.DictReader(fh) if (r.get("corr") or "").strip()]


def _pin_factor(corr: float) -> float:
    """What fixing one member of a correlated pair buys the other: 1/sqrt(1 - corr^2)."""
    return float(1.0 / np.sqrt(1.0 - corr * corr))


def _inert(z: float, pin_change: float) -> bool:
    """A design leaves the degeneracy where it was unless its move is both resolved and material (F552)."""
    return bool(z < Z_MOVED or abs(pin_change) < PIN_MATERIAL)


def _verdict(span_inert: bool, traces_inert: bool) -> tuple:
    """F552: the claim row, COMPUTED from the two readings and never written as a constant.

    A reading is inert when `_inert` says so. The four cases name different claims, so a table whose moves
    change cannot keep a claim they refute."""
    tail = (f" A move counts when it is resolved, above {Z_MOVED:g} of its trials' standard errors, and "
            f"material, changing the conditioning factor by {PIN_MATERIAL * 100:.0f} per cent or more. This "
            "is a comparison between designs under one seed, not a precision measurement of any single "
            "correlation")
    if span_inert and traces_inert:
        return ("DEGENERACY_IS_A_LINESHAPE_PROPERTY",
                "neither a five times wider span nor ten times the data moves the correlation materially, "
                "which is what a degeneracy belonging to the lineshape does and what one belonging to the "
                "sample size does not." + tail)
    if span_inert:
        return ("SPAN_INERT_SAMPLE_SIZE_OPEN",
                "a five times wider span leaves the degeneracy where it was, so a wider scan does not reach "
                "it, while ten times the data moved it materially. At leading order a replicated design "
                "scales the information matrix and leaves its correlation unchanged, so that move is the "
                "fit's nonlinearity at the one-trace precision or this seed's draw, and repeating over seeds "
                "tells them apart." + tail)
    if traces_inert:
        return ("SPAN_MOVES_IT",
                "a five times wider span moved the correlation materially and ten times the data did not, "
                "so the span reaches the degeneracy and the sample size does not." + tail)
    return ("BOTH_MOVE_IT",
            "both a five times wider span and ten times the data moved the correlation materially." + tail)


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

    corrs, ses, pins = {}, {}, {}
    for key, design, why in designs:
        # return_trials adds keys and draws nothing, so every value below is the one
        # the call without it returned
        r = forecast_precision(truth, design, n_trials=N_TRIALS, seed=SEED,
                               scalings=False, return_trials=True, registry=_TWIN_STUDY)
        corr = float(r["corr_laser_coll"])
        corrs[key] = corr
        add(key, "corr_laser_coll", f"{corr:+.4f}", "dimensionless",
            f"correlation between the fitted laser and collisional widths. {why}")
        tr = np.asarray(r["corr_laser_coll_trials"], float)
        tr = tr[np.isfinite(tr)]
        se = (MEDIAN_SE * float(np.std(tr, ddof=1)) / np.sqrt(tr.size)
              if tr.size > 1 else float("nan"))
        ses[key] = se
        add(key, "corr_laser_coll_se", f"{se:.4f}", "dimensionless",
            f"standard error of that median over the {tr.size} trials, {MEDIAN_SE} sd/sqrt(n) "
            "under normal theory. At this many trials it is a scale for the moves below and "
            "not a precise bar")
        pins[key] = _pin_factor(corr)
        add(key, "pin_factor", f"{pins[key]:.4f}", "dimensionless",
            "1/sqrt(1 - corr^2): the factor by which fixing the laser width shrinks the "
            "collisional width's uncertainty at this design's correlation")
        for p in ("gamma_coll", "sigma_laser"):
            err = r.get(f"{p}_err")
            if err is not None:
                add(key, f"{p}_err", f"{float(err):.6f}", "MHz",
                    "the fit's own reported one-sigma, median over trials")

    move_span = abs(corrs["span_300MHz"] - corrs["span_060MHz"])
    move_n = abs(corrs["traces_10x"] - corrs["span_060MHz"])
    z_span = move_span / float(np.hypot(ses["span_300MHz"], ses["span_060MHz"]))
    z_n = move_n / float(np.hypot(ses["traces_10x"], ses["span_060MHz"]))
    add("VERDICT", "corr_move_with_span", f"{move_span:.4f}", "dimensionless",
        "how far the correlation moved when the span went from 60 to 300 MHz")
    add("VERDICT", "corr_move_with_span_z", f"{z_span:.2f}", "sigma",
        "that move over the two medians' standard errors in quadrature")
    add("VERDICT", "corr_move_with_traces", f"{move_n:.4f}", "dimensionless",
        "how far it moved at ten times the repeats")
    add("VERDICT", "corr_move_with_traces_z", f"{z_n:.2f}", "sigma",
        "that move over the two medians' standard errors in quadrature")
    dpin_span = pins["span_300MHz"] / pins["span_060MHz"] - 1.0
    dpin_n = pins["traces_10x"] / pins["span_060MHz"] - 1.0
    add("VERDICT", "pin_change_with_span", f"{dpin_span:+.4f}", "fraction",
        "the relative change of the conditioning factor with the five times wider span: what the move "
        "does to the purchase of an independent laser width")
    add("VERDICT", "pin_change_with_traces", f"{dpin_n:+.4f}", "fraction",
        "the same at ten times the repeats")
    span_inert, traces_inert = _inert(z_span, dpin_span), _inert(z_n, dpin_n)
    claim, claim_why = _verdict(span_inert, traces_inert)
    add("VERDICT", "claim", claim, "verdict", claim_why)
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
            "it is the other half of the claim: the data buys precision "
            + ("while the correlation stays put" if traces_inert
               else "while the correlation moved, which the claim row reads"))
        add("VERDICT", "err_ratio_wide_span", f"{ratio_span:.2f}", "dimensionless",
            "how much it GREW at five times the span. Above one means widening "
            "COSTS precision here, which the record has not stated before. "
            "CAVEAT, and it is load-bearing: n_points is held fixed, so a wider "
            "span samples the line five times more thinly. This is a coupling "
            "between two design knobs and not a pure span effect, and it says "
            "widen the span only alongside the points to match")
    add("VERDICT", "campaign_corr_for_scale",
        f"{campaign_corr:+.4f}", "dimensionless",
        f"the CAMPAIGN's own fitted correlation at {'/'.join(REF)}, carried beside the "
        "twin's for scale. It is a different quantity from the twin's and must not be quoted "
        "as one: the twin's design takes the forecast's defaults (a noise of 0.004 of peak, "
        "five traces, 2000 points), not this condition's own noise law")
    add("VERDICT", "twin_minus_campaign_corr",
        f"{corrs['span_060MHz'] - campaign_corr:+.4f}", "dimensionless",
        "the twin at its reference design less the record's own fit at the same condition. A "
        "gap this size says the default design does not reproduce this condition's width "
        "correlation, which a run at the condition's own noise law and trace count tests (F553)")

    rows_c = _campaign_rows()
    cc = np.asarray([float(r["corr"]) for r in rows_c], float)
    q25, med, q75 = (float(v) for v in np.percentile(cc, [25, 50, 75]))
    lo, hi = float(cc.min()), float(cc.max())
    where = "across the conditions of linefit_conditions.csv"
    add("CAMPAIGN", "n_conditions", int(cc.size), "count",
        "the conditions of linefit_conditions.csv whose fit carries a width correlation")
    for q, v, what in (("median", med, "the median"),
                       ("q25", q25, "the 25th percentile, the more negative quartile"),
                       ("q75", q75, "the 75th percentile, the less negative quartile"),
                       ("most_negative", lo, "the most negative"),
                       ("least_negative", hi, "the least negative")):
        add("CAMPAIGN", f"corr_{q}", f"{v:+.4f}", "dimensionless",
            f"{what} of the record's own fitted laser-collisional width correlation {where}")
        add("CAMPAIGN", f"pin_factor_{q}", f"{_pin_factor(v):.4f}", "dimensionless",
            f"1/sqrt(1 - corr^2) at {what} correlation: what an independent laser width buys "
            "the collisional width's uncertainty there")

    # the power arm alone, which is the population fig10 draws and two pages describe
    arm = [r for r in rows_c if r["role"] == REF[0]]
    ca = np.asarray([float(r["corr"]) for r in arm], float)
    gc, gce, sl, sle, tw, twe = (np.asarray([float(r[k]) for r in arm], float) for k in (
        "gamma_coll", "gamma_coll_err", "sigma_laser", "sigma_laser_err", "total_fwhm", "total_fwhm_err"))
    add("CAMPAIGN", "n_conditions_power_arm", int(ca.size), "count",
        "the power arm's conditions, all at 130 C: the population fig10 draws")
    add("CAMPAIGN", "corr_median_power_arm", f"{float(np.median(ca)):+.4f}", "dimensionless",
        "the median width correlation over the power arm's conditions")
    add("CAMPAIGN", "n_negative_lorentzian_power_arm", int(np.sum(gc - gce < 0.0)), "count",
        "power-arm conditions whose one-sigma ellipse reaches a negative collisional width: the "
        "fitted value below its own one sigma")
    add("CAMPAIGN", "n_negative_gaussian_power_arm", int(np.sum(sl - sle < 0.0)), "count",
        "the same for the laser width")
    add("CAMPAIGN", "total_fwhm_relerr_median_power_arm_pct",
        f"{100.0 * float(np.median(twe / tw)):.2f}", "per cent",
        "the median relative one-sigma of the fitted total width over the power arm's conditions: "
        "the quantity the fit does measure")

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

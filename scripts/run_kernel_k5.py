#!/usr/bin/env python
"""K5: the attribution triangle. Is the non-Gaussian component THE LASER?

Preregistered in private/reviews/K3_PREREG_2026-08-21.md. K3 established that a
Lorentzian-equivalent homogeneous width of about 0.4 MHz is present and
identified. K3 is not permitted to call it the laser. This producer asks
whether anything else in the record licenses that arrow.

THE TRIANGLE.
  leg A  spectroscopic evidence: G+L against G. Done by K3.
  leg B  INDEPENDENT laser evidence carried through a transfer to a predicted
         kernel.
  leg C  cross-consistency of predicted against inferred.
Only leg C licenses "attributable to the laser", and leg C cannot be attempted
until leg B's transfer is classified validated, limited or not-established.

THE UNITS RULE, and why this producer exists rather than a sentence. The one
in-situ laser measurement in this record is the comb read as a clock: a bound
on the laser's NON-REPEATING, NON-LINEAR frequency excursion, 28.3 kHz on the
transition axis at 95 per cent, at an averaging time of 0.147 s. That is an
EXCURSION STATISTIC AT ONE AVERAGING SCALE. Gamma_L,equiv is a LINEWIDTH. They
are different kinds of quantity in the same units, and putting them beside each
other without a transfer is the error the units rule forbids. This file
computes what the transfer would have to be, and what it is worth.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                          # noqa: E402

OUT = C.RESULTS_DIR / "kernel_k5.csv"


def _read(path, key_col, val_col, want):
    with (C.RESULTS_DIR / path).open() as fh:
        for r in csv.DictReader(fh):
            if r.get(key_col) == want:
                return r
    return None


def main() -> int:
    rows = []

    def add(leg, quantity, value, unit, note):
        rows.append(dict(leg=leg, quantity=quantity, value=value, unit=unit,
                         note=note, status="DIAGNOSTIC"))

    # ---- leg A: what K3 established -------------------------------------
    k3 = {}
    with (C.RESULTS_DIR / "kernel_k3.csv").open() as fh:
        for r in csv.DictReader(fh):
            if r["scope"] == "all":
                k3[r["quantity"]] = r["value"]
    gamma_l_mhz = float(k3["k2p5_gamma_l_weighted_mean"])
    add("A", "gamma_l_equiv_transition", f"{gamma_l_mhz:.6f}", "MHz",
        "inverse-variance mean across peaks from kernel_k3.csv, on the "
        "transition axis the lineshape is fitted on")
    add("A", "verdict", "PRESENT_AND_IDENTIFIED", "verdict",
        "a non-Gaussian homogeneous component, preferred by a nested "
        "likelihood ratio at every peak. Says nothing about its origin")

    # ---- leg B: the independent laser evidence --------------------------
    ts = {}
    with (C.RESULTS_DIR / "ruler_tooth_scatter.csv").open() as fh:
        for r in csv.DictReader(fh):
            ts[r["quantity"]] = r["value"]
    tau = float(ts["tau"])
    exc_ub_transition_hz = float(ts["excursion_ub95_transition"]) * 1e3
    add("B", "comb_excursion_ub95_transition", f"{exc_ub_transition_hz/1e3:.4f}",
        "kHz", "95 per cent upper limit on the NON-LINEAR, NON-REPEATING "
        "excursion. A linear drift within a sweep is exactly degenerate with "
        "the sweep rate and is NOT bounded by it")
    add("B", "comb_tau", f"{tau:.4f}", "s",
        "the averaging time. The bound is a statement at THIS scale and "
        "carries no information at others without a noise model")

    # THE TRANSFER, and the assumption it rests on. The only noise model under
    # which an excursion at one averaging time converts to a linewidth at all
    # is WHITE frequency noise, for which a one-sided PSD S_nu (Hz^2/Hz) gives
    # a Lorentzian of FWHM = pi * S_nu, and a frequency averaged over tau has
    # variance S_nu / (2 tau). The record states the noise TYPE is measured
    # nowhere, so this conversion is an assumption and is labelled as one.
    s_nu_from_line = gamma_l_mhz * 1e6 / math.pi
    sigma_pred_hz = math.sqrt(s_nu_from_line / (2.0 * tau))
    add("B", "predicted_excursion_if_line_were_laser", f"{sigma_pred_hz/1e3:.4f}",
        "kHz", "excursion at tau this kernel WOULD produce if it were white "
        "frequency noise. Compare against the 28.3 kHz the comb can exclude")
    ratio_insens = exc_ub_transition_hz / sigma_pred_hz
    add("B", "comb_insensitivity_factor", f"{ratio_insens:.1f}", "dimensionless",
        "how much larger the comb's exclusion threshold is than the signal a "
        "laser origin would produce at this averaging time. Above one the "
        "measurement cannot see the hypothesis")

    s_nu_from_comb = 2.0 * tau * exc_ub_transition_hz ** 2
    gamma_allowed_mhz = math.pi * s_nu_from_comb / 1e6
    add("B", "gamma_l_permitted_by_comb", f"{gamma_allowed_mhz:.1f}", "MHz",
        "the largest Lorentzian width the comb bound permits under the same "
        "white-noise assumption. Compare against the 0.4 MHz measured")
    add("B", "headroom_factor", f"{gamma_allowed_mhz / gamma_l_mhz:.0f}",
        "dimensionless",
        "ratio of what the comb permits to what K3 measured. A constraint "
        "worth having would be of order one")

    # WHERE THIS BOUND SITS, corrected 2026-08-21. A first version of this
    # producer compared the clock's band against "of order the linewidth", on
    # the free-running-lineshape argument. These lines are SCANNED, so the
    # width integrates noise over the scan's own timescale, which
    # docs/plan/07_acquisition-settings.md gives as 24 Hz to 1.5 MHz for the
    # science blocks. The correct statement is narrower and still sufficient:
    # this bound was taken at the CAMPAIGN rate, so its clock sits at 6.8 Hz,
    # BELOW the band the science blocks integrate, and it is besides far too
    # loose. A block at ten times the rate would sit inside that band, and
    # that is a different measurement which kernel_k7.csv ranks.
    f_comb_hz = 1.0 / tau
    add("B", "clock_band_of_this_bound", f"{f_comb_hz:.2f}", "Hz",
        "one over the averaging time of the EXISTING bound, taken at the "
        "campaign scan rate")
    add("B", "science_block_width_band", "24 Hz to 1.5 MHz", "band",
        "the band the scanned science blocks' widths actually integrate. This "
        "bound's clock sits below it, so it does not sample the noise that "
        "broadened those lines")
    add("B", "a_faster_block_would_reach_it", "68 Hz at ten times the rate",
        "band",
        "which is inside the science band. That measurement has not been run "
        "and is ranked in kernel_k7.csv. Nothing here argues against it")

    add("B", "transfer_classification", "NOT_ESTABLISHED", "classification",
        "for the measurement ALREADY TAKEN. Its clock sits below the band the "
        "scanned widths integrate, the conversion to a linewidth needs a noise "
        "TYPE the record does not measure, and granting the most favourable "
        "type the bound is still orders of magnitude too loose. This is a "
        "statement about the existing bound and NOT about the faster block "
        "that would sit inside the band")

    # ---- leg C ----------------------------------------------------------
    add("C", "attempted", "NO", "verdict",
        "leg C compares a PREDICTED kernel against the inferred one. Leg B "
        "produced no prediction, only a bound too loose to constrain, so there "
        "is nothing to cross-check and no numerical combination is permitted")
    add("C", "laser_attribution", "NOT_LICENSED", "verdict",
        "the arrow from 'a non-Gaussian homogeneous component is present' to "
        "'it is the laser' is not carried by any measurement ALREADY TAKEN. "
        "K3's finding stands as a statement about the LINE, not about its "
        "origin. Two unrun measurements would carry it, and kernel_k7.csv "
        "ranks them")

    # ---- K6, which RUNS AFTER K5 and not beside it ----------------------
    # K5's transfer classification IS the class over which K6's numerator is
    # taken. Computing R_kernel before K5 would be a ratio over an undefined
    # class. K5 returned NOT_ESTABLISHED, so no numerical combination with the
    # comb is permitted and the class stays the data-allowed fallback, which
    # is the two-member class K3 already used. R_kernel is therefore final at
    # K3's value, and the PROVISIONAL flag resolves rather than being removed.
    u_stat = float(k3["U_statistical"])
    u_kern = float(k3["U_kernel"])
    add("K6", "class_used", "DATA_ALLOWED_FALLBACK", "classification",
        "K5 classified the transfer NOT_ESTABLISHED, so the admissible class "
        "is not narrowed by any independent laser evidence and stays the "
        "two-member class {G, G+L} the data alone allow")
    add("K6", "U_statistical", f"{u_stat:.6f}", "MHz per density unit",
        "mean one-sigma statistical error on beta_self from the G+L fits")
    add("K6", "U_kernel", f"{u_kern:.6f}", "MHz per density unit",
        "half-range of beta_self over the fallback class, on the same "
        "one-sigma-like footing. NOT a supremum")
    add("K6", "R_kernel", f"{u_kern / u_stat:.4f}", "dimensionless",
        "final at this value rather than provisional: K5 could not narrow the "
        "class, so the fallback K3 used is the class")
    add("K6", "stop_condition",
        "FIRED" if u_kern > u_stat else "not fired", "verdict",
        "U_kernel exceeding U_statistical means repetitions of the CURRENT "
        "construction no longer buy the coefficient. What buys it is an "
        "instrument that constrains the kernel independently, which is what "
        "K7 ranks")

    add("all", "what_would_close_it",
        "a frequency-noise spectrum measured in the band of the linewidth",
        "requirement",
        "the lock's own error signal, a self-heterodyne or beat measurement, "
        "or a fast-scan comb block sampling inside that band. Each is a "
        "candidate K7 ranks; none has been run")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"  {r['leg']:<4} {r['quantity']:<38} {r['value']:>28} {r['unit']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

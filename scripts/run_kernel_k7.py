#!/usr/bin/env python
"""K7: rank the routes that would close the kernel question, by what they reach.

K6 fired the stop condition: R_kernel = 3.24, so the kernel systematic dominates
the statistical error and repetitions of the current construction no longer buy
the coefficient. K5 then found that laser attribution is not licensed, because
no measurement in this record constrains the frequency noise in the band that
produces a Lorentzian wing.

So the ranking is not "which route is cheapest". It is WHICH ROUTES REACH THE
BAND AT ALL, and only among those, what each costs.

THE BAND, CORRECTED 2026-08-21. A first version of this producer took the band
to be "of order the linewidth", about 400 kHz, on the reasoning that a
Lorentzian wing is produced by noise at Fourier frequencies of order the width.
THAT IS THE BAND FOR A FREE-RUNNING LASER'S INTRINSIC LINESHAPE, AND THESE
LINES ARE NOT MEASURED THAT WAY. They are SCANNED, so the observed width
integrates laser noise over the SCAN's own timescale: from one over the time to
cross the line up to the per-point sampling rate, which
docs/plan/07_acquisition-settings.md states as 24 Hz to 1.5 MHz for the science
blocks at the campaign rate.

That correction matters because it reverses a verdict. Within ONE block the
clock band and the width band scale together and their ratio never closes, but
the laser's noise spectrum is a property of the laser, so the bands of
DIFFERENT blocks compose: a block at ten times the campaign rate has its tooth
clock sampling at 68 Hz, which is inside the band the ordinary-rate science
blocks integrate. One fast block therefore measures, in situ, part of the very
noise that broadens the slow blocks' lines.

THE COMB CLOCK'S REACH IS ARITHMETIC, NOT OPINION. The tooth clock averages
over tau = tooth_spacing / scan_rate, so the Fourier frequency it samples is
scan_rate / tooth_spacing. Both factors are campaign variables: the scan rate,
and now the EOM drive, which the next campaign can change. This producer
computes the reach at each combination rather than asserting one.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                    # noqa: E402
from rb5s6s import constants as K                 # noqa: E402

OUT = C.RESULTS_DIR / "kernel_k7.csv"


def main() -> int:
    rows = []

    def add(route, quantity, value, unit, note):
        rows.append(dict(route=route, quantity=quantity, value=value,
                         unit=unit, note=note, status="DIAGNOSTIC"))

    k3 = {r["quantity"]: r["value"] for r in
          csv.DictReader((C.RESULTS_DIR / "kernel_k3.csv").open())
          if r["scope"] == "all"}
    gamma_l_hz = float(k3["k2p5_gamma_l_weighted_mean"]) * 1e6
    r_kernel = float(k3["R_kernel"])
    add("all", "band_that_must_be_reached", "24 Hz to 1.5 MHz", "band",
        "the band the SCANNED science blocks' widths integrate, from one over "
        "the line-crossing time up to the per-point sampling rate "
        "(docs/plan/07_acquisition-settings.md). A scanned line integrates "
        "laser noise over the scan's timescale, NOT over a band of order the "
        "linewidth, which is the free-running-lineshape argument and does not "
        "apply here")
    add("all", "band_earlier_reasoning_kept_for_audit", f"{gamma_l_hz/1e3:.1f}", "kHz",
        "the band a first version of this producer used, of order the measured "
        "width. Kept so the correction is auditable: it is the right band for "
        "an intrinsic free-running lineshape and the wrong one for a scanned "
        "measurement")
    add("all", "R_kernel_at_entry", f"{r_kernel:.4f}", "dimensionless",
        "the kernel systematic already dominates the statistical error, which "
        "is why this ranking is about reach rather than about precision")

    # ---- route 1: the comb clock, at every campaign setting -------------
    ts = {r["quantity"]: r["value"] for r in
          csv.DictReader((C.RESULTS_DIR / "ruler_tooth_scatter.csv").open())}
    tau_now = float(ts["tau"])
    spacing_now = K.TOOTH_SPACING_TRANSITION_HZ
    rate_now = spacing_now / tau_now
    add("comb_clock", "campaign_scan_rate", f"{rate_now/1e6:.1f}", "MHz/s",
        "implied by the committed averaging time and tooth spacing")
    for rate_mult in (1, 10, 100):
        for f_mhz in (12.5, 0.5):
            tau = (f_mhz * 1e6) / (rate_now * rate_mult)
            band = 1.0 / tau
            add("comb_clock",
                f"reach_rate_x{rate_mult}_eom_{f_mhz}MHz",
                f"{band/1e3:.3f}", "kHz",
                f"Fourier frequency sampled at {rate_mult} times the campaign "
                f"scan rate with {f_mhz} MHz teeth. Compare with the "
                f"{gamma_l_hz/1e3:.0f} kHz band that carries the answer")
    reach_x10 = (rate_now * 10) / spacing_now
    add("comb_clock", "reach_at_x10_rate", f"{reach_x10:.1f}", "Hz",
        "a block at ten times the campaign rate. This sits INSIDE the 24 Hz to "
        "1.5 MHz band the ordinary-rate science blocks integrate, which is the "
        "composition the plan chapter describes")
    add("comb_clock", "discrimination_slow_noise", "180", "kHz",
        "excursion the fast clock would see if the fitted Gaussian is SLOW "
        "laser noise (docs/plan/07_acquisition-settings.md)")
    add("comb_clock", "discrimination_fast_noise", "4", "kHz",
        "excursion if it is FAST noise instead. Tooth centres resolve 96 kHz "
        "each, so one block separates the two readings by a factor near 45")
    add("comb_clock", "verdict", "REACHES_THE_BAND", "verdict",
        "corrected 2026-08-21. The route composes a fast block's clock band "
        "with the slow blocks' width band, and it carries a preregistered "
        "discrimination with a stated separation")

    # ---- route 2: a direct frequency-noise measurement ------------------
    add("noise_spectrum", "reach", "all Fourier frequencies to the detector bandwidth",
        "qualitative",
        "the lock's own error signal, a self-heterodyne delay line, or a beat "
        "against a second laser measure the PSD as a FUNCTION of Fourier "
        "frequency rather than at one averaging time, so the band is covered "
        "by construction rather than by scan-rate arithmetic")
    add("noise_spectrum", "cell_time_cost", "none", "qualitative",
        "the error signal exists whenever the lock runs, so this route costs "
        "no spectroscopy time at all")
    add("noise_spectrum", "verdict", "REACHES_THE_BAND", "verdict",
        "the only route in this record that closes K5's leg B directly")

    # ---- route 3: the nanofibre platform -------------------------------
    add("nanofibre", "reach", "an independent lineshape, not a noise spectrum",
        "qualitative",
        "the fibre measures the LINE again under a different transit and "
        "density regime, so it constrains the kernel by consistency rather "
        "than by measuring the noise. It does not close leg B, it adds an "
        "independent leg A")
    add("nanofibre", "verdict", "COMPLEMENTARY_NOT_SUFFICIENT", "verdict",
        "valuable against the transit and density degeneracies and silent on "
        "the origin question, which is what leg B is for")

    # ---- the ranking ----------------------------------------------------
    add("all", "rank_1", "noise_spectrum", "route",
        "reaches the band, costs no cell time, and is the only route that "
        "closes the attribution")
    add("all", "rank_2", "nanofibre", "route",
        "does not close the attribution but adds an independent measurement "
        "of the same kernel under different degeneracies")
    add("all", "rank_3", "comb_clock", "route",
        "reaches the band and carries a stated discrimination, and is ranked "
        "third only because it needs cell time the error-signal route does "
        "not. Its EXISTING bound, taken at the campaign rate, is separately "
        "too loose to constrain the kernel (kernel_k5.csv); that is a "
        "statement about the measurement already taken and not about the fast "
        "block this row ranks")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"  {r['route']:<15} {r['quantity']:<32} {r['value']:>16} {r['unit']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python
"""K7: rank the routes that would close the kernel question, by what they reach.

K6 fired the stop condition: R_kernel = 3.24, so the kernel systematic dominates
the statistical error and repetitions of the current construction no longer buy
the coefficient. K5 then found that laser attribution is not licensed, because
no measurement in this record constrains the frequency noise in the band that
produces a Lorentzian wing.

So the ranking is not "which route is cheapest". It is WHICH ROUTES REACH THE
BAND AT ALL, and only among those, what each costs.

THE BAND. A frequency-noise component at Fourier frequency f well BELOW the
linewidth broadens the line towards a Gaussian; one well ABOVE it produces
Lorentzian wings. The crossover is of order the linewidth itself, here the
0.398 MHz Gamma_L,equiv that K3 measured. A route that samples far below that
band constrains the GAUSSIAN side and is silent on the Lorentzian content, no
matter how precise it is.

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
    add("all", "band_that_must_be_reached", f"{gamma_l_hz/1e3:.1f}", "kHz",
        "Fourier frequency of order the measured Gamma_L,equiv. Below it a "
        "noise component broadens towards a Gaussian, above it towards a "
        "Lorentzian, so this is the band that carries the answer")
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
    best_band = (rate_now * 100) / (0.5e6)
    add("comb_clock", "best_reachable_band", f"{best_band/1e3:.1f}", "kHz",
        "the most favourable combination the next campaign could run, a "
        "hundredfold faster scan with the lowest useful EOM drive")
    add("comb_clock", "shortfall_at_best", f"{gamma_l_hz/best_band:.0f}",
        "dimensionless",
        "how far the best reachable setting still falls short of the band. "
        "Above one means the route cannot answer the question at any setting "
        "the campaign can reach")
    add("comb_clock", "verdict", "CANNOT_REACH_THE_BAND", "verdict",
        "the route constrains the SLOW noise that broadens towards a Gaussian, "
        "which is worth having and is not the Lorentzian content it is listed "
        "as a route to")

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
        "cannot reach the band at any campaign setting. Retained for what it "
        "does measure, the slow non-repeating excursion, and demoted from the "
        "role of a route to the Lorentzian content")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"  {r['route']:<15} {r['quantity']:<32} {r['value']:>16} {r['unit']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Known-truth recovery on synthetic data, using only the public API.

    python examples/synthetic_recovery.py

WHAT THIS IS FOR. Before trusting a fit, ask whether the machinery can recover
an answer it already knows. This example builds a line whose parameters ARE
known, fits it with the same function the archive's own results were produced
with, and reports the difference against the fit's own uncertainty. It is the
package's self-validation, and it is deliberately the first thing a reader
runs.

WHAT IT IS NOT. It is not the rubidium 5S to 6S experiment and it does not
reproduce any published number. The physical model here is the package's
general composite line shape with parameters chosen for the demonstration.
The experiment-specific results, their status labels and their caveats live in
the repository's results/ and docs/, and nothing in this file asserts a
physical claim about rubidium.

NO ARCHIVE DATA IS READ. This runs from a bare clone with no environment
variables set and no raw traces present, which is the point: the analysis
machinery is separable from the dataset it was written for.
"""
from __future__ import annotations

import math

import numpy as np

from rb5s6s import composite_profile, transit_fwhm_from_w0
from rb5s6s.linefit import fit_condition


# The truth. Everything downstream is derived from these three numbers, and the
# report at the end compares back to them.
GAMMA_COLL_TRUE = 0.60      # MHz, the collisional width
SIGMA_LASER_TRUE = 1.40     # MHz, the laser kernel FWHM (a FWHM, not a sigma,
                            # despite the name: see rb5s6s/linefit.py)
W0_M = 64e-6                # m, beam waist, sets the transit kernel
T_C = 130.0                 # C, sets the thermal speed in the transit kernel
N_TRACES = 4
NOISE_FRAC = 0.004          # of peak, per sample
SPAN_MHZ = 18.0
N_POINTS = 1200


def audit(transit_fwhm: float) -> None:
    """State the assumptions BEFORE fitting anything.

    Every one of these is a modelling choice the fit cannot discover for
    itself, so a reader who disagrees with one of them knows immediately that
    the recovery below does not apply to their case.
    """
    print("ASSUMPTIONS, stated before the fit")
    print("  line model      Lorentzian(natural + collisional) convolved with")
    print("                  a laser kernel and a transit kernel")
    print("  laser kernel    gaussian, and its parameter is a FWHM")
    print("  transit kernel  two-sided exponential, the Biraben-Cagnac cusp")
    print(f"  transit FWHM    {transit_fwhm:.4f} MHz, fixed, from w0 = "
          f"{W0_M*1e6:.0f} um at {T_C:.0f} C")
    print("  background      per trace, linear and free")
    print("  amplitude       per trace, free")
    print("  centre          per trace, free")
    print("  noise           gaussian, constant, independent between samples")
    print("                  (the archive's own fits use a signal-dependent")
    print("                   noise law instead, which this example does not)")
    print()


def make_traces(transit_fwhm: float, rng: np.random.Generator):
    """Synthetic traces from the PUBLIC line-shape builder."""
    nu = np.linspace(-SPAN_MHZ, SPAN_MHZ, N_POINTS)
    grid, prof = composite_profile(GAMMA_COLL_TRUE, SIGMA_LASER_TRUE,
                                   transit_fwhm)
    shape = np.interp(nu, grid, prof, left=0.0, right=0.0)
    shape = shape / shape.max()
    freqs, volts = [], []
    for i in range(N_TRACES):
        amp = 1.0 + 0.05 * i                 # traces differ, as real ones do
        offset = 0.010 + 0.002 * i
        v = amp * shape + offset + NOISE_FRAC * rng.standard_normal(nu.size)
        freqs.append(nu.copy())
        volts.append(v)
    return freqs, volts


def main() -> int:
    transit_fwhm = transit_fwhm_from_w0(W0_M, 110.0) * math.sqrt(
        (T_C + 273.15) / 383.15)
    audit(transit_fwhm)

    rng = np.random.default_rng(20260816)
    freqs, volts = make_traces(transit_fwhm, rng)
    print(f"{N_TRACES} synthetic traces, {N_POINTS} points over "
          f"+-{SPAN_MHZ:.0f} MHz, noise {100*NOISE_FRAC:.1f} per cent of peak\n")

    res = fit_condition(freqs, volts, T_C=T_C, transit_fwhm=transit_fwhm)

    print("RECOVERY, the point of the example")
    print(f"{'parameter':>14} {'true':>9} {'fitted':>12} {'error':>9} {'pull':>7}")
    ok = True
    for name, true in (("gamma_coll", GAMMA_COLL_TRUE),
                       ("sigma_laser", SIGMA_LASER_TRUE)):
        got = float(res[name])
        err = float(res.get(f"{name}_err", float("nan")))
        pull = (got - true) / err if err and np.isfinite(err) else float("nan")
        print(f"{name:>14} {true:9.4f} {got:12.4f} {err:9.4f} {pull:+7.2f}")
        if not (np.isfinite(pull) and abs(pull) < 3.0):
            ok = False
    print(f"\n  reduced chi-squared {float(res.get('chi2_red', float('nan'))):.3f}")
    print(f"  correlation(gamma_coll, sigma_laser) "
          f"{float(res.get('corr_laser_coll', float('nan'))):+.3f}")
    print("\n  That correlation is the point of the next paragraph: the two")
    print("  widths are strongly anti-correlated, so a fit can trade one")
    print("  against the other. Recovering both here means the SYNTHETIC data")
    print("  constrain the pair. It does not mean any real dataset does.")

    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'}, "
          "every parameter recovered within 3 of its own standard error.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

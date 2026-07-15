#!/usr/bin/env python3
"""
M9: transit-broadening Monte-Carlo -- magnitude, budget impact, kernel shape.

Answers the three objections to "just measure w0" (README 2.5) with a
first-principles computation: 3D-MB velocities, the z-dependent w(z), and the
collection average. Reports (1) the transit FWHM vs w0 / T / collection range,
(2) what that implies for the natural (X) transit (X) laser budget and hence
the 2025 laser width, and (3) how far the phenomenological two-sided
exponential is from the MC kernel.

All in the weak-field, straight-line, flux-weighted approximation; absolute
values ride on the OPEN w0 and the (a fixed-lock session) collection geometry. (An earlier
version omitted the crossing-flux factor and ran ~2x too narrow with a spurious
divergent cusp; fixed 2026-07-12 -- see transit_mc.py.) Outputs:
results/transit_mc.csv.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s._compat import trapezoid  # noqa: E402  (np.trapezoid is numpy 2.0+)
from rb5s6s.constants import GAMMA_NAT_HZ  # noqa: E402
from rb5s6s.transit_mc import transit_added_fwhm_mc, transit_lineshape_mc  # noqa: E402
from rb5s6s.lineshape import lorentzian  # noqa: E402

GNAT = GAMMA_NAT_HZ / 1e6
OBSERVED = 5.25  # MHz, observed total FWHM at the reference condition


def _add_and_err(w0_m, z_half_m, n_full=300_000, n_err=50_000, k_seeds=4):
    """Transit added-FWHM at full n (default seed, so the value is unchanged
    and reproducible), plus its MONTE-CARLO SAMPLING error. The error is the
    seed-to-seed spread at a reduced n_err, scaled by ~1/sqrt(n) to the full
    sample -- cheap, and it is the honest per-point uncertainty (the curve's
    DOMINANT uncertainty is the OPEN w0 on the x-axis, not this)."""
    add = transit_added_fwhm_mc(w0_m=w0_m, T_C=110, z_half_range_m=z_half_m, n_atoms=n_full)
    vals = [transit_added_fwhm_mc(w0_m=w0_m, T_C=110, z_half_range_m=z_half_m,
                                  n_atoms=n_err, seed=C.RNG_SEED + 1 + i)
            for i in range(k_seeds)]
    err = float(np.std(vals, ddof=1) * np.sqrt(n_err / n_full))
    return add, err


def main() -> int:
    out = []
    print("=" * 74)
    print("(M9) TRANSIT MONTE-CARLO -- 3D MB + w(z) + collection")
    print(f"  natural (fixed) {GNAT:.2f} MHz; observed total ~{OBSERVED} MHz. The transit")
    print("  kernel is a finite two-sided exponential (Biraben-Cagnac cusp), so we quote")
    print("  the PHYSICAL observable: how much it ADDS to the natural line once convolved.\n")
    print("  transit CONTRIBUTION to observable FWHM vs w0 (110 C, thin near-focus):")
    print(f"  {'w0':>5s} {'+transit':>9s} {'nat(x)transit':>14s}  interpretation")
    for w0 in (32, 40, 50, 65, 90):
        add, err = _add_and_err(w0 * 1e-6, 0.3e-3)
        natx = GNAT + add
        if natx > OBSERVED + 0.1:
            note = "OVERSHOOTS observed -> w0 EXCLUDED"
        elif natx >= OBSERVED - 0.15:
            note = "~fills budget -> laser NARROW"
        else:
            note = "leaves room for laser"
        out.append({"w0_um": w0, "T_C": 110, "collection": "thin",
                    "transit_added_fwhm": add, "nat_conv_transit": natx,
                    "nat_conv_transit_err": err})
        print(f"  {w0:>4d}u {add:>+9.2f} {natx:>14.2f} +/-{err:.3f}  {note}")

    print("\n  collection-range dependence (w0=50 um, 110 C) -- objection #1:")
    for Z in (0.3, 1.0, 3.0, 6.0):
        add, err = _add_and_err(50e-6, Z * 1e-3)
        out.append({"w0_um": 50, "T_C": 110, "collection": f"{Z}mm",
                    "transit_added_fwhm": add, "nat_conv_transit": GNAT + add,
                    "nat_conv_transit_err": err})
        print(f"    z_half={Z:.1f} mm: +{add:.2f} MHz")

    # kernel shape: excess kurtosis (cusp) vs Gaussian
    nu = np.arange(-12, 12, 0.01)
    L = transit_lineshape_mc(nu, w0_m=50e-6, T_C=110, z_half_range_m=0.3e-3, n_atoms=300_000)
    Ln = L / trapezoid(L, nu)
    m2 = trapezoid(nu ** 2 * Ln, nu); m4 = trapezoid(nu ** 4 * Ln, nu)
    kurt = m4 / m2 ** 2 - 3.0

    with open(C.RESULTS_DIR / "transit_mc.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    print(f"\n{'-'*74}\nWHAT IT MEANS (transit physics corrected 2026-07-12 -- flux factor):")
    print("  * The transit contribution is ~2.1 MHz at w0=32 um and ~1.2 MHz at 50 um.")
    print("    At 32 um, natural (x) transit already EXCEEDS the observed 5.25 MHz line,")
    print("    so 32 um is EXCLUDED; the observed width is consistent with w0 ~ 45-70 um")
    print("    (central ~50). transit and the laser Gaussian remain DEGENERATE via w0:")
    print("      - w0 ~< 40 um: transit alone ~fills the 5.25 MHz => laser NARROW/none;")
    print("      - w0 = 50 um (prior): transit ~1.2, leaving ~0.8 MHz laser axis for laser.")
    print("    The MC does NOT settle narrow-vs-not by itself -- it QUANTIFIES the w0")
    print("    degeneracy; the fixed-lock session's knife-edge w0 is the decisive measurement.")
    print(f"  * objection #1 (collection over many mm): a real tens-of-% effect on the")
    print("    transit -- needs the fixed-lock session's measured collection profile.")
    print(f"  * the kernel is a finite cusp (excess kurtosis {kurt:.1f}, Gaussian=0): the")
    print("    phenomenological two-sided exponential is close but under-represents the")
    print("    core, so the fits should adopt this MC kernel once w0 + collection are known.")
    print("  * the earlier ~factor-2 'excitation-weighting' caveat is RESOLVED: the")
    print("    missing crossing-flux factor was the one real bug; no residual factor-2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

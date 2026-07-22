#!/usr/bin/env python3
"""
Ramp-law moment coefficients vs collection geometry (PLAN §8.3).

Review 2026-07-12 #3 required extending the triangular-ramp model to the
diverging-beam collection geometry before the small-waist skew can be
interpreted. This script evaluates the closed-form axial-averaged shift
density (lineshape.stark_ramp_axial) at the three proposed configurations
and prints the moment coefficients the fits would need.

CONDITIONAL PREDICTION (2026-07-12; conditionality made explicit
2026-07-22): the standardized skewness g1 changes sign at Z_c/z_R ~ 1.12.
The pure transverse triangle gives g1 = +0.566; a long collection window
mixes in out-of-focus (weak-shift) regions, piling weight near zero shift
with a tail toward -S0, driving g1 negative (~ -0.35 at the 16 um config
with the +/-2 mm placeholder window). Whether config S actually sits past
the crossover depends on the UNMEASURED collection geometry: Z_c is the
imaging field of view r_PMT/M (M = v/u for the side-viewing f = 18 mm
lens), so the flip needs r_PMT/M > ~0.9 mm at 16 um, and plausible bench
layouts land on both sides (short-conjugate/high-M: g1 ~ +0.5, no flip;
1:1 relay or large photocathode: g1 ~ -0.3 to -0.5). Measuring u, v and the
cathode's active extent ALONG the beam image (L_par; the R636-10 cathode is a
3 x 12 mm rectangle (the tube housed in the Thorlabs PXT1/M module;
experimenter-confirmed 2026-07-23), so its rotation changes Z_c by x4) settles it; near the crossover,
moving the PMT (changing M) is a design knob. If the condition holds, a
session sees POSITIVE skew at the large waist and NEGATIVE at the small
one — a sign flip no instrumental asymmetry (none of which depends on
z_R) can mimic. The naive "skew scales as S0^3 = x64" reading of the small
waist is wrong in SIGN at the placeholder geometry; the third cumulant
there is ~ -0.35 in units of the 2025 on-axis S0^3 (vs +0.0074 for the
2025 triangle).

Caveats: uniform collection weight on |z| <= Z_c is a placeholder (the
solid angle varies <2% across such windows, so the top-hat FORM is fair —
the width is the unknown); Z_c is OPEN until the collection-geometry
measurement (config lists an envelope). Quasi-static in z is safe: an atom
moves ~30 um axially between excitation and 795 nm emission, negligible vs
z_R (mm scale).

Outputs: stdout table only (predictions, not archival results — deliberately
NOT written to results/, which is reserved for measured numbers).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import LAMBDA_LASER_M  # noqa: E402
from rb5s6s.lineshape import stark_ramp_axial_moments  # noqa: E402

TRIANGLE_G1 = 18.0 ** 1.5 / 135.0


def main() -> int:
    print("=" * 78)
    print("RAMP-LAW MOMENTS vs COLLECTION GEOMETRY  (predictions for PLAN §8.3)")
    print(f"pure transverse triangle: mean/S0 = -2/3, var/mean^2 = 1/8, "
          f"g1 = +{TRIANGLE_G1:.4f}")
    print(f"{'config':>24s} {'z_R(mm)':>8s} {'Z/z_R':>6s} {'mean/S0':>8s} "
          f"{'var/mean^2':>10s} {'g1':>8s}")
    for name, w0_um in C.RAMP_GEOMETRY_CONFIGS_UM.items():
        z_r = np.pi * (w0_um * 1e-6) ** 2 / LAMBDA_LASER_M
        for z_c_mm in C.RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE:
            zr = z_c_mm * 1e-3 / z_r
            m = stark_ramp_axial_moments(1.0, zr)
            print(f"{name:>24s} {z_r * 1e3:8.2f} {zr:6.2f} {m['mean']:8.4f} "
                  f"{m['var'] / m['mean'] ** 2:10.4f} "
                  f"{m['skew_standardized']:+8.4f}")
        print()
    print("Reading: g1 stays ~ +0.56 at BOTH the 60 um config and the ~50 um 2025")
    print("archival geometry (clean form test -- the larger corrected waist makes the")
    print("archival ramp nearly a pure triangle), and FLIPS SIGN only at the 16 um")
    print("config AT THE PLACEHOLDER Z_c -- the flip needs r_PMT/M > ~0.9 mm there")
    print("(measure u, v, and the cathode extent ALONG the beam image L_par;")
    print("Z_c = L_par/(2M) -- module docstring / PLAN 8.3 #4). Geometry")
    print("permitting, the two-config skew comparison is a sign-flip test, not a")
    print("magnitude hunt.")
    print()
    print("=" * 78)
    print("INSTALL DECISION: cathode orientation  (PLAN §8.3 #4)")
    zr = {w: np.pi * (w * 1e-6) ** 2 / LAMBDA_LASER_M
          for w in C.RAMP_GEOMETRY_CONFIGS_UM.values()}
    w_l, w_s = max(zr), min(zr)
    short, long_ = C.RAMP_PMT_CATHODE_MM
    print(f"{'orientation':>20s} {'M':>4s} {'Z_c(mm)':>8s} "
          f"{'g1@' + str(w_l) + 'um':>9s} {'g1@' + str(w_s) + 'um':>9s} {'flip':>5s}")
    for label, l_par in (("landscape", long_), ("portrait", short)):
        for mag in C.RAMP_RELAY_MAGNIFICATION_ENVELOPE:
            z_c = l_par / (2 * mag) * 1e-3
            a_, b_ = (stark_ramp_axial_moments(1.0, z_c / zr[w])["skew_standardized"]
                      for w in (w_l, w_s))
            print(f"{label + ' (' + str(l_par) + ' mm)':>20s} {mag:4.1f} "
                  f"{z_c * 1e3:8.2f} {a_:+9.3f} {b_:+9.3f} "
                  f"{'YES' if a_ > 0 > b_ else 'no':>5s}")
    print()
    print("Portrait falls BELOW the 0.90 mm flip threshold at every plausible M:")
    print("it does not weaken the sign-flip test, it removes it. Landscape also")
    print("keeps the cathode from being the limiting aperture, so the image-plane")
    print("slit sets Z_c -- which is the knob the sweep below uses.")
    print()
    print("=" * 78)
    print(f"SLIT SCAN at the small waist ({w_s} um): g1(Z_c) at FIXED atoms,")
    print("power, lock and waist -- only the collection geometry moves.")
    print(f"{'Z_c(mm)':>9s} {'g1@' + str(w_l) + 'um':>9s} {'g1@' + str(w_s) + 'um':>9s} "
          f"{'signal@' + str(w_s) + 'um':>12s}")
    for z_c_mm in (0.5, 1.0, 2.0, 3.0):
        z_c = z_c_mm * 1e-3
        a_, b_ = (stark_ramp_axial_moments(1.0, z_c / zr[w])["skew_standardized"]
                  for w in (w_l, w_s))
        # two-photon rate per unit length ~ 1/(1+(z/z_R)^2): fraction within +-Z_c
        frac = 2 * np.arctan(z_c / zr[w_s]) / np.pi
        print(f"{z_c_mm:9.1f} {a_:+9.3f} {b_:+9.3f} {frac:11.0%}")
    print()
    print("g1 walks from POSITIVE to NEGATIVE through zero on a slit alone, at one")
    print("waist -- a cleaner test than the two-waist flip, which unavoidably moves")
    print("S0, transit time and sampled density together. The same scan MEASURES the")
    print("collection profile, so it calibrates its own axis. Caveat: the top-hat")
    print("collection model and a singlet that aberrates at its working NA -- which")
    print("is why the scan, not the imaging formula, is the number of record.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

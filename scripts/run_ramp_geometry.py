#!/usr/bin/env python3
"""
Ramp-law moment coefficients vs collection geometry (October PLAN §8.3).

Review 2026-07-12 #3 required extending the triangular-ramp model to the
diverging-beam collection geometry before the small-waist skew can be
interpreted. This script evaluates the closed-form axial-averaged shift
density (lineshape.stark_ramp_axial) at the three October configurations
and prints the moment coefficients the fits will need.

HEADLINE PREDICTION (2026-07-12): the standardized skewness g1 CHANGES SIGN
near Z/z_R ~ 1.2. The pure transverse triangle gives g1 = +0.566; a long
collection window mixes in out-of-focus (weak-shift) regions, piling weight
near zero shift with a tail toward -S0, driving g1 negative (~ -0.35 at the
16 um config with a +/-2 mm window). So October should see POSITIVE skew at
the large waist and NEGATIVE skew at the small waist — a sign flip across
configurations that no instrumental asymmetry (which knows nothing about
z_R) can mimic. The naive "skew scales as S0^3 = x64" reading of the small
waist is wrong in SIGN; the absolute third cumulant there is ~ -0.35 in
units of the 2025 on-axis S0^3 (vs +0.0074 for the 2025 triangle) — a ~47x
magnitude gain AND a flipped sign.

Caveats: uniform collection weight on |z| <= Z_c is a placeholder; Z_c is
OPEN until the October collection-geometry measurement (config lists an
envelope). Quasi-static in z is safe: an atom moves ~30 um axially between
excitation and 795 nm emission, negligible vs z_R (mm scale).

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
    print("config -> the October two-config skew comparison is a sign-flip test, not")
    print("a magnitude hunt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

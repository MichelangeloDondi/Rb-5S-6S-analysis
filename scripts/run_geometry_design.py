#!/usr/bin/env python3
"""
Two geometry choices for a future fixed-lock session, computed rather than argued:
a running-wave retro arm, and the beam waist.

    ./.venv/bin/python scripts/run_geometry_design.py

This is a DESIGN calculation, not a result. It writes nothing and touches no
committed number. docs/notes/running_wave_and_waist_design.md is written from
its output, and both were produced only after the first pass at each was found
wrong, which is why the two failure modes are printed alongside the answers.

DESIGN 1, A RUNNING WAVE. Shifting one arm in frequency by Delta makes the
interference pattern run instead of stand, so the intensity an atom sees is
modulated and it responds to the fringe mean. The record needs that because the
Doppler-free line accepts every axial velocity, and the near-transverse atoms sit
at a frozen fringe and sample the node-to-antinode arcsine, which suppresses the
ramp skew (constants.DELTA_ALPHA_AU, rb5s6s/fringe_tail.py).

The first pass set Delta by the wrong criterion: 80 MHz, chosen because it is
23 natural widths, so no atom can follow the modulation. That criterion is
necessary and not sufficient. A frozen fringe is not a slow modulation, it is a
RESONANCE between the atom and the pattern: the phase an atom sees advances at
2 k v_z - Delta, so shifting Delta does not remove the frozen-fringe class, it
MOVES it from v_z = 0 to the co-moving speed v_fringe = Delta lambda / 2. What
matters is how many atoms are there, so the real criterion is thermal:

    v_fringe must outrun the axial thermal spread, not the linewidth.

At 130 C the one-dimensional rms axial speed is 196 m/s, so Delta must clear
2 sigma_v / lambda = 395 MHz, an order of magnitude above the first pass. The
table below prints the Maxwell-Boltzmann weight at the co-moving speed, which is
the fraction of the frozen-fringe population that survives.

DESIGN 2, THE WAIST. Small waist raises the shift as one over the waist squared
and the skew goes as the shift cubed, so the pull toward a small waist is strong.
Three things push back, and the first pass carried only one of them.

  * the axial average over the collection region suppresses and then REVERSES the
    skew, crossing zero at Z_c/z_R = 1.12 (the committed
    lineshape.stark_ramp_axial_moments)
  * transit broadening grows as one over the waist (constants.transit_fwhm_from_w0)
  * SATURATION, which the first pass ignored entirely and which is the one that
    matters most. The ramp law weights each shift by the signal it produces, and
    the two-photon signal goes as intensity squared only while the drive is weak.
    The saturation parameter goes as the FOURTH power of one over the waist, so it
    runs away: 0.033 at 64 um becomes 0.53 at 32 um and 8.5 at 16 um, all at
    225 mW. Where it is large the weight flattens toward a constant, the effective
    exponent falls toward one, and the pure transverse skew vanishes at n = 1 by
    the module's own docstring.

So the moments here are integrated with the SATURATED weight, the steady-state
excited fraction, rather than with intensity squared. The integral is checked
against the committed unsaturated machinery in the last block, which is what
licenses the saturated numbers.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s._compat import trapezoid  # noqa: E402
from rb5s6s import stark  # noqa: E402
from rb5s6s.constants import (GAMMA_NAT_HZ, K_B_J_PER_K,  # noqa: E402
                              LAMBDA_LASER_M, M_RB87_KG,
                              transit_fwhm_from_w0)
from rb5s6s.hyperpolarizability import two_photon_rabi_hz  # noqa: E402
from rb5s6s.lineshape import (stark_ramp_axial_moments,  # noqa: E402
                              stark_shift_S0_mhz)

G_MHZ = GAMMA_NAT_HZ / 1e6
T_C = 130.0
P_MAX_W = 0.225
# the collection half-length: the middle of the envelope config.py documents for
# the current single-lens imaging geometry, read from there so it cannot go stale
ZC_M = C.RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE[1] * 1e-3
GC_MHZ, SL_MHZ = 0.60, 1.50        # representative campaign core widths
NU = np.arange(-45.0, 45.0, 0.01)
TOOTH_LASER_MHZ = 6.25


def rayleigh_range_m(w0_m: float) -> float:
    return math.pi * w0_m ** 2 / LAMBDA_LASER_M


# --------------------------------------------------------------- design 1
def running_wave_table() -> None:
    sigma_v = math.sqrt(K_B_J_PER_K * (T_C + 273.15) / M_RB87_KG)
    crit_hz = 2.0 * sigma_v / LAMBDA_LASER_M
    print("=" * 78)
    print("DESIGN 1  a running wave: which velocity class stays frozen")
    print(f"  one-dimensional rms axial speed at {T_C:.0f} C = {sigma_v:.0f} m/s")
    print(f"  criterion  Delta >> 2 sigma_v / lambda = {crit_hz/1e6:.0f} MHz")
    print(f"  (the first pass used {G_MHZ:.2f} MHz x 23 = 80 MHz, which is the "
          f"wrong criterion)\n")
    print(f"  {'Delta':>8} {'v_fringe':>9} {'/sigma_v':>9} {'MB weight':>10} "
          f"{'/Gamma':>7} {'laser offset':>13} {'teeth':>8}")
    for d_hz in (40e6, 80e6, 200e6, 400e6, 800e6, 1600e6):
        v = d_hz * LAMBDA_LASER_M / 2.0
        w = math.exp(-v * v / (2.0 * sigma_v ** 2))
        off = d_hz / 2.0 / 1e6
        print(f"  {d_hz/1e6:7.0f}M {v:8.0f} m/s {v/sigma_v:9.2f} {w:10.3f} "
              f"{d_hz/GAMMA_NAT_HZ:7.0f} {off:10.0f} MHz {off/TOOTH_LASER_MHZ:8.2f}")
    print("\n  The MB weight column IS the answer: at 80 MHz it is 0.98, so 98 per")
    print("  cent of the frozen-fringe population is still frozen, just at a")
    print("  different speed. Two thirds of it survives even at 400 MHz.")
    print("  Note the tooth column: 400, 800 and 1600 MHz land on exact integer")
    print("  multiples of the ruler spacing, so a working Delta must be detuned")
    print("  from them deliberately (810 MHz gives 64.80 teeth, 5 MHz clear).")
    resid = (800e6 / (2.99792458e8 / LAMBDA_LASER_M)) * 465.5e6
    print(f"  Residual Doppler at 800 MHz is {resid/1e3:.1f} kHz against the "
          f"{G_MHZ:.2f} MHz\n  natural width, so the Doppler-free property "
          f"survives the larger shift.")


# --------------------------------------------------------------- design 2
def ramp_moments(w0_m: float, power_w: float, zc_m: float,
                 saturate: bool = True, n_u: int = 600, n_z: int = 601) -> dict:
    """Signal-weighted moments of the ramp shift over the collection region.

    The weight is the steady-state excited fraction s/2/(1+s) when saturate is
    True and the weak-field s/2 (that is, intensity squared) when it is False.
    The False branch must reproduce stark_ramp_axial_moments, and does.
    """
    z_r = rayleigh_range_m(w0_m)
    s0 = stark_shift_S0_mhz(power_w, w0_m, rho=C.RHO_RETRO)
    sat00 = 2.0 * (two_photon_rabi_hz(power_w, w0_m, C.RHO_RETRO) / 1e6 / G_MHZ) ** 2
    z = np.linspace(-zc_m, zc_m, n_z)
    u = np.linspace(0.0, 30.0, n_u)          # u = 2 r^2 / w(z)^2
    uu, zz = np.meshgrid(u, z / z_r, indexing="ij")
    frac = np.exp(-uu) / (1.0 + zz ** 2)     # I / I(0,0)
    shift = -s0 * frac
    sat = sat00 * frac ** 2
    weight = (sat / 2.0) / (1.0 + sat) if saturate else sat / 2.0
    # dV = w0^2 (1 + zeta^2) du dz / 4; the w0^2 is kept so signal comparisons
    # across waists mean something
    dv = weight * w0_m ** 2 * (1.0 + zz ** 2)

    def integrate(field):
        return trapezoid(trapezoid(field, u, axis=0), z)

    norm = integrate(dv)
    m = [integrate(dv * shift ** k) / norm for k in (1, 2, 3)]
    var = m[1] - m[0] ** 2
    kappa3 = m[2] - 3.0 * m[0] * m[1] + 2.0 * m[0] ** 3
    return {"s0": s0, "sat00": sat00, "sat_w": integrate(dv * sat) / norm,
            "mean": m[0], "var": var, "kappa3": kappa3,
            "g1": kappa3 / var ** 1.5, "signal": norm,
            "zc_over_zr": zc_m / z_r}


def total_fwhm_mhz(w0_m: float, s0: float, sat_weighted: float) -> float:
    """The fit's own width, with the saturation increment the companion note
    established. Leaving it out is what made the first figure of merit reward
    the deeply saturated rows."""
    extra = G_MHZ * (math.sqrt(1.0 + sat_weighted) - 1.0)
    return stark._fwhm_of(GC_MHZ + extra, SL_MHZ,
                          transit_fwhm_from_w0(w0_m, T_C), s0, NU)


def waist_table() -> None:
    print()
    print("=" * 78)
    print(f"DESIGN 2  the waist, at {P_MAX_W*1e3:.0f} mW and a "
          f"{ZC_M*1e3:.1f} mm collection half-length")
    print("  figure of merit = |kappa3| / width^3 x sqrt(signal), the "
          "shot-noise-limited\n  significance of the third cumulant, "
          "relative to the present waist\n")
    print(f"  {'w0':>5} {'Zc/zR':>6} {'sat':>7} {'S0':>7} {'g1':>8} "
          f"{'g1 weak':>8} {'kappa3':>10} {'FWHM':>7} {'signal':>9} {'FoM':>8}")
    ref = None
    for w0_um in (64, 48, 40, 32, 24, 16):
        w0 = w0_um * 1e-6
        wet = ramp_moments(w0, P_MAX_W, ZC_M)
        dry = ramp_moments(w0, P_MAX_W, ZC_M, saturate=False)
        fw = total_fwhm_mhz(w0, wet["s0"], wet["sat_w"])
        fom = abs(wet["kappa3"]) / fw ** 3 * math.sqrt(wet["signal"])
        ref = ref or fom
        print(f"  {w0_um:5d} {wet['zc_over_zr']:6.2f} {wet['sat00']:7.3f} "
              f"{wet['s0']:7.3f} {wet['g1']:+8.3f} {dry['g1']:+8.3f} "
              f"{wet['kappa3']:10.4f} {fw:7.3f} {wet['signal']:9.2e} "
              f"{fom/ref:8.1f}")
    print("\n  Read the two skew columns together. Saturation SHRINKS the skew")
    print("  where it is positive and GROWS it where it is negative, because")
    print("  flattening the weight lowers the effective exponent, the transverse")
    print("  skew vanishes at n = 1, and what is left is the axial term. At 16 um")
    print("  it changes the prediction by a factor of about three, and 16 um is")
    print("  the waist the record's small-waist session is written around.")

    print("\n  matched intensity instead of matched power (P as w0 squared):")
    for w0_um in (64, 32, 16):
        w0 = w0_um * 1e-6
        p = P_MAX_W * (w0_um / 64.0) ** 2
        m = ramp_moments(w0, p, ZC_M)
        print(f"    w0 = {w0_um:3d} um at {p*1e3:6.1f} mW: sat = "
              f"{m['sat00']:.4f}, S0 = {m['s0']:.3f} MHz, g1 = {m['g1']:+.3f}")
    print("    The shift is IDENTICAL at matched intensity, so a smaller waist")
    print("    buys no shift at all on its own. It buys the intensity a limited")
    print("    power can reach, and it pays for it in saturation and in the")
    print("    axial average. That is the whole trade, stated as an identity.")


def cross_check() -> None:
    print()
    print("=" * 78)
    print("CHECK  the weak-field branch against the committed axial machinery")
    print(f"  {'w0':>5} {'Zc/zR':>7} {'committed g1':>13} {'this integral':>14}")
    for w0_um in (64, 32, 24, 16):
        w0 = w0_um * 1e-6
        ratio = ZC_M / rayleigh_range_m(w0)
        committed = stark_ramp_axial_moments(1.0, z_ratio=ratio)
        mine = ramp_moments(w0, P_MAX_W, ZC_M, saturate=False)
        print(f"  {w0_um:5d} {ratio:7.2f} {committed['skew_standardized']:+13.4f} "
              f"{mine['g1']:+14.4f}")
    print("  Agreement to about two per cent on a two-dimensional quadrature")
    print("  against a one-dimensional analytic one is what licenses the")
    print("  saturated numbers above, which have no committed counterpart.")


def main() -> int:
    running_wave_table()
    waist_table()
    cross_check()
    print()
    print("=" * 78)
    print("Nothing was written. See docs/notes/running_wave_and_waist_design.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

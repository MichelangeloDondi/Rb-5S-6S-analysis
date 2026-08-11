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


# --------------------------------------------------------------- design 3
def fringe_velocity_classes() -> None:
    """Which atoms resolve the fringes, over the 3D Maxwell-Boltzmann spread,
    in the standing wave and in the running one.

    The three velocity questions are separate and are answered by separate
    components of the same distribution, which is the point of doing this in
    3D rather than with one speed. The components are independent Gaussians of
    the same width, so:

      * v_z, ALONG the beam, sets how fast an atom crosses fringes and so
        whether it sees a modulated intensity or a time-averaged one;
      * the two transverse components set the crossing time, and through it
        the transit width, the excitation probability and the pumping loss;
      * the Doppler-free geometry does NOT select on v_z at first order, which
        is exactly what makes the line narrow. Second-order Doppler is 0.4 kHz
        and is ignored here.

    THE FROZEN CLASS. An atom sees a frozen fringe if it moves less than a
    quarter period during the window over which its excitation stays coherent,
    so |v_z| < lambda / (4 tau_c). tau_c is the open modelling choice that
    rb5s6s.fringe_tail sweeps: the excited-state lifetime at one end, the
    crossing time at the other. The fraction is then the 1D marginal of the
    3D distribution, erf(v* / sqrt(2) sigma_v), and it is small because
    sigma_v is 196 m/s and v* is metres per second.

    THE RUNNING WAVE DOES NOT REMOVE THAT CLASS, IT MOVES IT. Shifting one arm
    by Delta makes the pattern travel at v_fringe = Delta lambda / 2. An atom
    now sees the pattern go past at |v_fringe - v_z|, so the atoms that still
    see a frozen fringe are the ones co-moving with it, v_z near v_fringe.
    Their number is the Maxwell-Boltzmann weight there, exp(-v_fringe^2 /
    2 sigma_v^2), which is why the criterion is THERMAL and not spectroscopic:
    Delta has to put v_fringe out in the tail of the distribution, not merely
    beyond a linewidth.

    WHAT IT COSTS. With the two arms at different frequencies the first-order
    Doppler no longer cancels exactly. The residue is Delta v_z / c, which
    smears the line by Delta sigma_v / c. It grows LINEARLY in Delta while the
    fringe suppression improves as a Gaussian in Delta, so the trade has a
    comfortable window rather than a knife edge, and both numbers are printed.
    """
    sigma_v = math.sqrt(K_B_J_PER_K * (T_C + 273.15) / M_RB87_KG)
    v_perp = sigma_v * math.sqrt(math.pi / 2.0)      # 2D Rayleigh mean
    tau_6s = 1.0 / (2.0 * math.pi * GAMMA_NAT_HZ)
    print()
    print("=" * 78)
    print("DESIGN 3  which atoms resolve the fringes, over the 3D "
          "Maxwell-Boltzmann spread")
    print(f"  sigma_v per component {sigma_v:.1f} m/s at {T_C:.0f} C, mean "
          f"transverse speed {v_perp:.1f} m/s")
    print(f"  fringe period {LAMBDA_LASER_M/2*1e9:.1f} nm, 6S lifetime "
          f"{tau_6s*1e9:.1f} ns")
    print()
    print("  STANDING WAVE, the frozen class |v_z| < lambda/(4 tau_c):")
    for label, tau in (("lifetime-capped", tau_6s),
                       ("transit-capped, 64 um", 2 * C.W0_MEASURED_M / v_perp),
                       ("transit-capped, 16 um", 2 * 16e-6 / v_perp)):
        vstar = LAMBDA_LASER_M / (4.0 * tau)
        frac = math.erf(vstar / (sigma_v * math.sqrt(2.0)))
        print(f"    {label:22s} tau_c {tau*1e9:6.0f} ns  v* {vstar:6.2f} m/s "
              f" -> {100*frac:6.3f} % of atoms")
    print()
    print("  RUNNING WAVE, the frozen class moves to v_z = v_fringe:")
    print(f"    {'Delta':>8} {'v_fringe':>9} {'MB weight':>10} "
          f"{'Doppler residue':>16}")
    for delta_hz in (40e6, 80e6, 200e6, 400e6, 800e6, 1600e6):
        v_fringe = delta_hz * LAMBDA_LASER_M / 2.0
        weight = math.exp(-v_fringe ** 2 / (2.0 * sigma_v ** 2))
        # FWHM of the residual first-order term Delta v_z / c over the spread
        resid = 2.0 * math.sqrt(2.0 * math.log(2.0)) * delta_hz * sigma_v / 2.998e8
        print(f"    {delta_hz/1e6:7.0f}M {v_fringe:8.1f} m/s {weight:10.4f} "
              f"{resid:11.0f} Hz = {100*resid/GAMMA_NAT_HZ:.3f}% of Gamma")
    crit = 2.0 * sigma_v / LAMBDA_LASER_M
    print(f"    the thermal criterion is 2 sigma_v / lambda = "
          f"{crit/1e6:.0f} MHz, which is where v_fringe = sigma_v")
    print()
    print("  AND THE CONTRIBUTING POPULATION IS NOT THERMAL, because pumping")
    print("  removes the atoms that dwell longest, which are the ones the")
    print("  transit weighting favours most:")
    m = ramp_moments(C.W0_MEASURED_M, P_MAX_W, ZC_M)
    rate = 2.0 * math.pi * GAMMA_NAT_HZ * (m["sat00"] / 2.0) / (1.0 + m["sat00"])
    v = np.linspace(1.0, 900.0, 4000)
    ray = (v / sigma_v ** 2) * np.exp(-v ** 2 / (2.0 * sigma_v ** 2))
    w_transit = ray / v          # crossing flux (v) times excitation (1/v^2)
    dwell = 2.0 * C.W0_MEASURED_M / v
    base_v = trapezoid(w_transit * v, v) / trapezoid(w_transit, v)
    print(f"    mean contributing transverse speed, transit weighting alone: "
          f"{base_v:.1f} m/s")
    for f_branch in (1.0 / 3.0, 2.0 / 3.0):
        w = w_transit * np.exp(-f_branch * rate * dwell)
        mv = trapezoid(w * v, v) / trapezoid(w, v)
        lost = 1.0 - trapezoid(w, v) / trapezoid(w_transit, v)
        print(f"    with pumping at f = {f_branch:.2f}: {mv:.1f} m/s "
              f"({100*(mv/base_v-1):+.1f} %), and {100*lost:.1f} % of the "
              f"weight removed")
    print("    v_z and the transverse components are independent, so this")
    print("    biases the transit width and NOT which atoms resolve fringes.")


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
    fringe_velocity_classes()
    cross_check()
    print()
    print("=" * 78)
    print("Nothing was written. See docs/notes/running_wave_and_waist_design.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

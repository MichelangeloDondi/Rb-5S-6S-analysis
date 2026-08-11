#!/usr/bin/env python3
"""What a next campaign's conditions do to the effects this record just measured.

WHY THIS EXISTS (2026-08-10, owner instruction). The record proposes a hotter
cell, more power, a tighter waist and eventually a different transition, and it
argues each of those from the light shift alone. Six effects were quantified on
this archive over the last two days, and every one of them scales differently
with those four knobs. This projects them, so a session is chosen on the whole
budget rather than on the one term that motivated it.

THREE RESULTS, and the second is a warning about a session the record already
recommends.

  1. THE PER-LINE LEVER BECOMES SPENDABLE AT A TIGHTER WAIST. Hyperfine pumping
     is the only one of the three same-signature broadeners that differs between
     the four lines, so a joint fit over them is the only separation that does
     not need a stable frequency reference. On this archive the lever is 3 kHz
     against an 88 kHz block scatter, short by a factor of thirty. It grows as
     the saturation width, which grows as P^2/w0^4, so it is spendable at 16 um
     with no extra power at all. Scored two ways: against the 2025 scatter in
     absolute terms, and against the same FRACTIONAL stability applied to the
     wider line that condition produces, which is the defensible one. It
     survives both, because the lever is linear in the saturation term while the
     total width is a quadrature sum with a fixed natural core in it.

  2. THE HOT EXTENSION IS WHERE TRAPPING STOPS BEING A FOOTNOTE. The record
     proposes 150 to 170 C to reach densities where a collisional effect could
     clear the block-noise floor. The infrared halo re-excitation runs 1.1 per
     cent at 130 C, 8.9 at 150 and 30.6 at 170. beta_self is read from WIDTHS
     and is untouched. Every AMPLITUDE comparison taken in the same session is
     not, and that is where M7 and M10 live. At 30 per cent the argument that
     the halo merely rescales the amplitude is also being asked to hold further
     than it was derived for.

  3. THE BLACKBODY TEST ORDERS THE TRANSITION MENU, and the menu did not carry
     it. What couples the upper state to the thermal field is the gap to the
     nearest nP, and that gap SHRINKS as the upper state climbs. The occupation
     number spans five orders of magnitude across a menu whose entries differ by
     less than a factor of two in drive wavelength: 4D and 6S are free of it,
     5D and 7S want watching, and 8S and 9S are in a different regime entirely.

WHAT IS NOT PROJECTED HERE, deliberately. The isotope transit split goes as
sqrt(T) and moves by 4 per cent over the whole extension, which changes nothing.
The ramp's own skew against waist is already in
docs/notes/running_wave_and_waist_design.md and is not repeated.

STATUS. The lever and saturation columns are exact given the model. The halo is
ENVELOPE and carries the standoff band of results/trapping_channels.csv. The
blackbody column is exact given the line list, with the upper-state energies
taken from the verified two-photon wavelengths of the transition menu and the nP
ladder from this package's own LINES_5S. Writes nothing.

    ./.venv/bin/python scripts/run_campaign_conditions.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import stark  # noqa: E402
from rb5s6s.constants import TAU_6S_S, transit_fwhm_from_w0  # noqa: E402
from rb5s6s.density import d1_optical_depth_per_cm, number_density_cm3  # noqa: E402
from rb5s6s.polarizability import E_6S_CM, LINES_5S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_blackbody_channels as B  # noqa: E402
import run_saturation_probe as SP  # noqa: E402
import run_trapping_channels as T  # noqa: E402
from run_geometry_design import ramp_moments  # noqa: E402

F_PER_LINE = (0.3725, 0.3476, 0.2483, 0.2235)   # run_zeeman_depletion checks 3 and 7
OBS_2025_MHZ, BLOCK_2025_MHZ = 5.25, 0.088
SIGMA_LASER_MHZ = 1.09                           # the record's own laser-axis bound
NU = np.arange(-90.0, 90.0, 0.01)
# the verified two-photon wavelengths of the transition menu, nm
MENU_NM = (("6S1/2", None), ("5D5/2", 778.0), ("7S1/2", 760.0),
           ("8S1/2", 697.0), ("9S1/2", 660.0), ("4D_J", 1033.0))


def lever_row(w0_um: float, p_mw: float) -> dict:
    """Everything the width budget does at one (waist, power)."""
    w0 = w0_um * 1e-6
    m = ramp_moments(w0, p_mw / 1000.0, 2.2e-3)
    tr = transit_fwhm_from_w0(w0, 403.15)
    base = stark._fwhm_of(0.0, SIGMA_LASER_MHZ, tr, 0.0, NU)
    ramp = stark._fwhm_of(0.0, SIGMA_LASER_MHZ, tr, m["s0"], NU) - base
    sat = SP.saturation_increment_mhz(m["s0"], 1.2367)
    total = base + ramp + sat
    lever = sat * (max(F_PER_LINE) - min(F_PER_LINE))
    return {"s0": m["s0"], "sat_par": m["sat_w"], "transit": tr, "ramp": ramp,
            "sat": sat, "total": total, "lever": lever,
            "vs_abs": lever / BLOCK_2025_MHZ,
            "vs_frac": lever / (total * BLOCK_2025_MHZ / OBS_2025_MHZ)}


def main() -> int:
    print("=" * 78)
    print("1  THE PER-LINE LEVER against waist and power")
    print("   Only the pumping term differs between the four lines, so the")
    print("   lever is (fmax - fmin) times the saturation width. It has to beat")
    print("   the block-to-block width scatter to be spendable.")
    print()
    print(f"   {'w0':>5} {'P':>6} {'S0':>7} {'s':>7} {'transit':>8} {'ramp':>8} "
          f"{'sat':>9} {'total':>7} {'lever':>8} {'/88kHz':>7} {'/frac':>6}")
    for w0_um in (64.0, 40.0, 32.0, 24.0, 16.0):
        for p_mw in (225.0, 500.0, 1000.0):
            r = lever_row(w0_um, p_mw)
            print(f"   {w0_um:4.0f}u {p_mw:5.0f}m {r['s0']:7.3f} "
                  f"{r['sat_par']:7.3f} {r['transit']:8.2f} {1e3*r['ramp']:7.0f}k "
                  f"{1e3*r['sat']:8.0f}k {r['total']:7.2f} {1e3*r['lever']:7.0f}k "
                  f"{r['vs_abs']:7.2f} {r['vs_frac']:6.2f}")
        print()
    print("   The 88 kHz scatter is 1.68 per cent of the 5.25 MHz line it was")
    print("   measured on, and a wider line will not hold 88 kHz, so the LAST")
    print("   column is the one to act on. It still clears 3 at 16 um and")
    print("   225 mW, which is the current power. The separation this archive")
    print("   misses by thirty is bought by the waist, not by the laser.")
    print()
    print("   THE CATCH, and it is the same one the skew already has: the lever")
    print("   is spendable exactly where the weak-field ramp law is least valid.")
    print("   At 16 um the saturation parameter is 1.0, so the fit that spends")
    print("   the lever has to carry the saturation term rather than treat it as")
    print("   a companion, which is the preregistered refit's construction.")

    print()
    print("=" * 78)
    print("2  THE 150 TO 170 C EXTENSION the record proposes for beta_self")
    lam12, a12 = T._leg(*T.LINES_6S[0][:2])
    lam32, a32 = T._leg(*T.LINES_6S[1][:2])
    b12 = a12 / (a12 + a32)
    s12 = T._sigma_peak_cm2(lam12, a12, 2, 2)
    m = ramp_moments(C.W0_MEASURED_M, 0.225, 2.2e-3)
    f_ex = (m["sat_w"] / 2.0) / (1.0 + m["sat_w"])
    z_r = math.pi * C.W0_MEASURED_M ** 2 / 993.4e-9
    v_beam = math.pi * C.W0_MEASURED_M ** 2 * (2.0 * z_r) * 1e6
    print()
    print(f"   {'T':>5} {'n (1e12)':>10} {'tau/cm':>8} {'halo re-exc':>12} "
          f"{'band':>17} {'6S->6P ppm':>11} {'BBR shift':>10}")
    for t_c in (110.0, 130.0, 150.0, 170.0):
        pct = T.halo_reexcitation(t_c, T.STANDOFF_CM, f_ex, b12, s12, v_beam)[2]
        lo, hi = T.halo_band(t_c, f_ex, b12, s12, v_beam)
        up = 0.0
        for e_cm, d_au, g in ((23715.081, 9.72, 2.0), (23792.591, 13.645, 1.0)):
            lam = 1e7 / (e_cm - E_6S_CM) * 1e-9
            up += B.nbar(lam, t_c + 273.15) * B.einstein_a(lam, d_au) * g
        print(f"   {t_c:4.0f}C {number_density_cm3(t_c)/1e12:10.1f} "
              f"{d1_optical_depth_per_cm(t_c, 85):8.1f} {pct:11.2f}% "
              f"{lo:6.2f} to {hi:6.2f}% {up*TAU_6S_S*1e6:11.1f} "
              f"{B.bbr_shift_hz(t_c + 273.15):9.1f}")
    print()
    print("   beta_self is read from WIDTHS and none of this reaches it. The")
    print("   amplitude comparisons of M7 and M10 are a different matter: the")
    print("   halo grows thirtyfold over the extension and is a third of the")
    print("   primary rate at 170 C. Two consequences for a session plan. Take")
    print("   the amplitude work at the COLD end and the width work at the hot")
    print("   end. And vary the standoff deliberately at one hot condition,")
    print("   because that is the measurement that turns this envelope into a")
    print("   number, and it costs one translation stage.")

    print()
    print("=" * 78)
    print("3  THE BLACKBODY TEST ON THE TRANSITION MENU")
    print("   What couples an upper state to the thermal field is the gap to the")
    print("   nearest nP, and that gap SHRINKS as the state climbs. Upper-state")
    print("   energies from the menu's own verified two-photon wavelengths, the")
    print("   nP ladder from this package's LINES_5S.")
    print()
    p_ladder = sorted(e for e, _, _ in LINES_5S)
    h, kb, cl = 6.62607015e-34, 1.380649e-23, 2.99792458e8
    print(f"   {'upper':>7} {'2-photon':>9} {'nearest nP gap':>15} {'hv/kT':>7} "
          f"{'nbar (130C)':>12} {'verdict':>11}")
    for label, lam2 in MENU_NM:
        e_up = E_6S_CM if lam2 is None else 2e7 / lam2
        gap_cm = abs(min(p_ladder, key=lambda e: abs(e - e_up)) - e_up)
        x = h * cl * gap_cm * 100.0 / (kb * 403.15)
        nb = 1.0 / math.expm1(x) if x < 700 else 0.0
        verdict = ("negligible" if nb < 1e-4
                   else "watch" if nb < 1e-2 else "MATTERS")
        print(f"   {label:>7} {2e7/e_up:8.0f}n {1e4/gap_cm:14.2f}u {x:7.2f} "
              f"{nb:12.3e} {verdict:>11}")
    print()
    print("   6S and 4D are free of it. 5D and 7S want watching. 8S and 9S are")
    print("   in another regime: a quarter of a photon per mode at 9S means")
    print("   blackbody transfer out of the upper state at a fair fraction of")
    print("   its own decay rate, which is a systematic and not a footnote. In a")
    print("   HOT cell this argues for the low end of the ladder, and it is a")
    print("   criterion the menu was choosing without.")
    print()
    print("=" * 78)
    print("Nothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

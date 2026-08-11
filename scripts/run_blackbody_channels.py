#!/usr/bin/env python3
"""Blackbody radiation in a 400 K cell: every channel it could act through.

WHY THIS EXISTS (2026-08-10, owner question). The cell runs at 70 to 130 C, so
it sits inside its own blackbody field, and nothing in this record had computed
what that field does. The question was put in two halves, and they have
different answers, which is the reason for a script rather than a sentence.

  (a) Does blackbody light re-drive 5P to 6S on the 1324 and 1367 nm cascade
      legs, the way trapped light does?
  (b) Does it touch the 795 nm fluorescence we detect?

WHAT SETS EVERY ANSWER is one number. At 403 K the blackbody PHOTON spectrum
peaks near 7.2 um, and every line in this cascade is between 0.79 and 2.8 um.
The occupation number goes as exp(-h nu / kT), so a factor of nine in
wavelength is a factor of 1e-12 in photons.

  (a) NO, BY TWELVE ORDERS OF MAGNITUDE. The occupation numbers are 2.0e-12 at
      1324 nm and 4.6e-12 at 1367 nm, so blackbody light drives 5P to 6S at
      7.4e-6 and 3.3e-5 per second. The trapped-infrared halo of
      run_trapping_channels.py re-excites at about 1.9e3 per second, so
      blackbody light is 1e-8 of a channel that is itself one per cent. There
      is no version of this experiment where that matters.

  (b) NO, AND FOR A DIFFERENT REASON IN EACH DIRECTION. Stimulated emission on
      D1 runs at 1.2e-12 per second against a 28 ns lifetime, which is
      nothing. The blackbody BACKGROUND at the detector is bounded not by the
      50 dB of 795 nm filtering but by the photocathode's own red edge. The
      tube of record is an R636-10 in a Thorlabs PXT1/M housing, an attribution
      that came from Nieddu 2019 on a different bench and was reconciled with
      the in-campaign photograph only in 2026 (APPARATUS). Nothing here rests
      on it: a GaAs response ends near 900 nm, but ANY photocathode whose red
      edge is below a couple of microns is blind to a 7.2 um peak, and no
      photocathode has one above that. In the band it can respond to at all the whole
      cell wall emits 3.0e3 photons per second at 70 C and 3.6e6 at 130 C,
      before any collection solid angle and before the filters. That is a
      per-mille background at the hottest point at worst, it is FLAT in laser
      frequency, and the fits carry a free baseline per trace. The archive
      also bounds it empirically without knowing it: M1 measured the
      shot-noise coefficient FLAT from 70 to 130 C, which a background growing
      by three orders of magnitude would have broken.

TWO THINGS THAT ARE NOT NEGLIGIBLE, and they are why this is worth committing.

  1. THE ONE REAL BLACKBODY CHANNEL IS 6S TO 6P, at 2.73 and 2.79 um, where
     the occupation number is 2e-6 rather than 2e-12 because those lines sit
     much closer to the blackbody peak. It transfers out of 6S at about 44 per
     second against a natural decay of 2.19e7, so it is a leak of 2 parts per
     million out of the detected cascade. Negligible here and worth naming,
     because it rises steeply with temperature and the record's own outlook
     proposes a 150 to 170 C extension.

  2. THE BLACKBODY AC-STARK SHIFT IS HUNDREDS OF HERTZ, not the ~1 Hz the
     ground state alone would give, because the differential polarizability is
     5171 minus 318 a.u. and because the 6S resonances sit inside the
     blackbody band rather than far above it. Computed by integrating this
     package's own dynamic polarizabilities over the Planck spectrum. It shifts
     the line and does not broaden it, so it cannot touch beta_self, and the
     centres are unusable in this archive anyway. It is stated for the
     fixed-lock session, where it is a T^4 systematic on the very observable
     that session exists to measure.

A CORRECTION TO MY OWN FIRST WRITE-UP OF THIS, 2026-08-10. I reported the
long-wavelength limit of alpha_5s, 318.3 a.u. against the accepted 318.8, as a
free check of a module that had "never been checked at DC". IT ALREADY WAS.
results/polarizability.csv carries alpha_5s_static = 318.28 and alpha_6s_static
= 5167.0 as committed DIAGNOSTIC rows, each with its own Monte-Carlo band, the
first validated against Holmgren 2010 and the second calibrated to the
Safronova-group value. So what this integration provides is a consistency check
on ITSELF, reproducing 318.3 and 5171.1 against those committed 318.28 and
5167.0, and not a new check of the module. The failure was not grepping the
record before claiming a gap in it, which is a standing rule here and was not
followed.

STATUS. The occupation numbers and rates are EXACT given the line data. The
detector background is ENVELOPE (it uses the cell's nominal 25 by 100 mm and no
collection solid angle, so it is an upper bound). The shift is a converged
PRINCIPAL VALUE through the two 6S to 6P poles, and its error bar is the
committed alpha_6s_static band carried through, read from
results/polarizability.csv rather than typed.

WRITES results/blackbody_channels.csv, with its own status and err_kind columns
(so the annotator skips it). Reads results/polarizability.csv, so it runs after
run_polarizability.py in run_all.sh.

    ./.venv/bin/python scripts/run_blackbody_channels.py
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import TAU_5P12_S, TAU_6S_S  # noqa: E402
from rb5s6s.polarizability import (E_6S_CM, LINES_6S, alpha_5s,  # noqa: E402
                                   alpha_6s)

H = 6.62607015e-34
KB = 1.380649e-23
CL = 2.99792458e8
EPS0 = 8.8541878128e-12
A0 = 5.29177210903e-11
E_C = 1.602176634e-19
HBAR = 1.054571817e-34
LAM_D1_M = 794.979e-9
CELL_D_M, CELL_L_M = 0.025, 0.100      # EXPERIMENTER, 10 per cent, see APPARATUS
# GaAs response of the R636-10 in its PXT1/M housing. The tube attribution is
# ASSUMED rather than measured here (it came from Nieddu 2019, a different
# bench, and APPARATUS records how it was reconciled with the in-campaign
# photograph), and DATASHEET for the band itself, not confirmed against the
# sheet. Neither matters: any cathode whose red edge is below a couple of
# microns is blind to a 7.2 um peak, so widening this band by an octave, or
# swapping the tube, changes nothing that follows.
CATHODE_NM = (300.0, 900.0)
# The 6S to 6P resonances sit INSIDE the 403 K blackbody band, so the shift
# integral runs through two poles and needs a principal value. They are 2.16 per
# cent apart in frequency, which is the whole difficulty: any symmetric window
# wider than about one per cent MERGES them, and then the pairing centre is the
# midpoint of the merged window rather than a pole, which is not a principal
# value at all. It is stable to the last printed digit from 0.2 to 1.0 per cent.
POLE_CM = (23715.081, 23792.591)       # 6P3/2 and 6P1/2, NIST ASD
POLE_HALF_WIDTH = 0.005                # fraction of the pole frequency


def nbar(lam_m: float, t_k: float) -> float:
    """Planck occupation number of one mode at this wavelength."""
    x = H * CL / (lam_m * KB * t_k)
    return 1.0 / math.expm1(x) if x < 700.0 else 0.0


def einstein_a(lam_m: float, d_au: float) -> float:
    omega = 2.0 * math.pi * CL / lam_m
    d = d_au * E_C * A0
    return omega ** 3 * d ** 2 / (3.0 * math.pi * EPS0 * HBAR * CL ** 3 * 2)


def photon_exitance(t_k: float, lo_nm: float, hi_nm: float,
                    n: int = 40000) -> float:
    """Photons per second per m^2 into the hemisphere, band-limited."""
    lo, hi = lo_nm * 1e-9, hi_nm * 1e-9
    step = (hi - lo) / n
    tot = 0.0
    for i in range(n):
        lam = lo + (i + 0.5) * step
        x = H * CL / (lam * KB * t_k)
        if x > 700.0:
            continue
        tot += 2.0 * math.pi * CL / lam ** 4 / math.expm1(x) * step
    return tot


def _shift_integrand(nu: float, t_k: float) -> float:
    """d(shift)/d(nu) in Hz per Hz, in the convention this repository pins,
    dE = -(1/2) alpha <E^2>."""
    x = H * nu / (KB * t_k)
    if nu <= 0.0 or x > 700.0:
        return 0.0
    e2 = 8.0 * math.pi * H * nu ** 3 / CL ** 3 / math.expm1(x) / EPS0
    lam_nm = CL / nu * 1e9
    d_alpha = (alpha_6s(lam_nm) - alpha_5s(lam_nm)) * 4.0 * math.pi * EPS0 * A0 ** 3
    return -0.5 * d_alpha * e2 / H


def _nonresonant_shift_hz(t_k: float, lam_min_m: float = 3.2e-6,
                          n: int = 8000) -> float:
    """The same integral with the resonances excluded rather than handled.

    Kept only so the principal value can be compared against it, which is how
    the size of the resonant contribution is reported instead of guessed.
    """
    lo, hi = 1e11, CL / lam_min_m
    step = (hi - lo) / n
    return sum(_shift_integrand(lo + (k + 0.5) * step, t_k)
               for k in range(n)) * step


def bbr_shift_hz(t_k: float, half_width: float = POLE_HALF_WIDTH,
                 n_sym: int = 3000, n_reg: int = 5000) -> float:
    """Differential 5S to 6S blackbody shift, transition axis, in Hz.

    A PRINCIPAL VALUE. Away from the poles this is ordinary quadrature. Across
    each pole the integrand is sampled in pairs equidistant either side of the
    pole itself, so the divergent halves cancel, which is what a principal
    value is.

    TWO EARLIER ATTEMPTS, both recorded because each was wrong in an
    instructive way. The first ran a uniform grid straight through the poles
    and wobbled by about 10 Hz depending on how the grid happened to straddle
    them. The second excluded the resonances entirely by cutting the band at
    3.2 um, which is defensible but leaves an unquantified residue and was
    reported as one. The third paired symmetrically but used windows wide
    enough to MERGE the two poles, so the pairing centre was the midpoint
    between them and not a pole, and it looked converged while being wrong.
    Only the per-pole narrow window is right, and the tell is that it is stable
    to the last printed digit from 0.2 to 1.0 per cent while the merged one
    moved by 10 Hz over the same range.

    The resonances turn out to contribute -0.33 Hz at 70 C and -2.44 Hz at
    130 C, so the earlier 10 Hz residue was an artefact of the straddling
    rather than a real uncertainty.
    """
    poles = sorted(CL * (e - E_6S_CM) * 100.0 for e in POLE_CM)
    wins = [(p * (1 - half_width), p * (1 + half_width)) for p in poles]
    if wins[0][1] >= wins[1][0]:
        raise ValueError("windows merged: the pairing centre would not be a pole")
    lo, hi = 1e11, 2.5e14
    tot = 0.0
    for a, b in ((lo, wins[0][0]), (wins[0][1], wins[1][0]), (wins[1][1], hi)):
        step = (b - a) / n_reg
        tot += sum(_shift_integrand(a + (k + 0.5) * step, t_k)
                   for k in range(n_reg)) * step
    for p, (a, b) in zip(poles, wins):
        step = (b - a) / (2 * n_sym)
        for k in range(n_sym):
            d = (k + 0.5) * step
            tot += (_shift_integrand(p - d, t_k)
                    + _shift_integrand(p + d, t_k)) * step
    return tot


def alpha6s_fractional_band() -> float:
    """Half-width of the committed alpha_6s_static band, as a fraction.

    Read from results/polarizability.csv rather than typed, because that file
    is where this repository's static polarizabilities and their Monte-Carlo
    bands already live. The blackbody shift is linear in the differential
    polarizability, so this fraction carries straight onto it.
    """
    path = C.RESULTS_DIR / "polarizability.csv"
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            if row["quantity"] == "alpha_6s_static":
                v = float(row["value"])
                lo, hi = float(row["err_lo16"]), float(row["err_hi84"])
                return 0.5 * (hi - lo) / v
    raise KeyError("alpha_6s_static not in polarizability.csv")


def main() -> int:
    print("=" * 78)
    print("WHAT SETS EVERY ANSWER")
    print(f"  the blackbody photon spectrum at 130 C peaks near "
          f"{2897.8/403.15:.1f} um (Wien)")
    print("  every line of this cascade is between 0.79 and 2.8 um")
    print()
    print("OCCUPATION NUMBERS AND THE RATES THEY DRIVE, at 130 C")
    print(f"  {'transition':>18} {'lambda':>10} {'hv/kT':>7} {'nbar':>11} "
          f"{'A (/s)':>10} {'nbar*A':>11}")
    legs = []
    for (e_cm, d_au, _), name in zip(LINES_6S[:2], ("6S -> 5P1/2", "6S -> 5P3/2")):
        lam = 1e7 / (E_6S_CM - e_cm) * 1e-9
        a = einstein_a(lam, d_au)
        n = nbar(lam, 403.15)
        legs.append((name, lam, a, n))
        print(f"  {name:>18} {lam*1e9:9.1f}n {H*CL/(lam*KB*403.15):7.2f} "
              f"{n:11.3e} {a:10.3e} {n*a:11.3e}")
    a_d1 = 1.0 / TAU_5P12_S
    n_d1 = nbar(LAM_D1_M, 403.15)
    print(f"  {'5P1/2 -> 5S (D1)':>18} {LAM_D1_M*1e9:9.1f}n "
          f"{H*CL/(LAM_D1_M*KB*403.15):7.2f} {n_d1:11.3e} {a_d1:10.3e} "
          f"{n_d1*a_d1:11.3e}")
    up = 0.0
    for e_cm, d_au, tag, g_ratio in ((23715.081, 9.72, "6S -> 6P3/2", 2.0),
                                     (23792.591, 13.645, "6S -> 6P1/2", 1.0)):
        lam = 1e7 / (e_cm - E_6S_CM) * 1e-9
        a = einstein_a(lam, d_au)
        n = nbar(lam, 403.15)
        up += n * a * g_ratio
        print(f"  {tag:>18} {lam*1e6:8.2f}um {H*CL/(lam*KB*403.15):7.2f} "
              f"{n:11.3e} {a:10.3e} {n*a:11.3e}")

    print()
    print("(a) DOES BLACKBODY LIGHT RE-DRIVE 5P TO 6S?  No.")
    for name, _, a, n in legs:
        print(f"    {name.replace('6S ->', '')} upward: {n*a*0.5:.3e} /s")
    print("    the trapped-infrared halo does it at about 1.9e3 /s "
          "(run_trapping_channels.py, 1.07 per cent of the primary rate)")
    print(f"    natural 6S decay for scale: {1.0/TAU_6S_S:.3e} /s")

    print()
    print("    THE ONE REAL BLACKBODY CHANNEL IS 6S TO 6P, because 2.7 um sits")
    print(f"    near the blackbody peak where 1.3 um does not: {up:.1f} /s out")
    print(f"    of 6S, which is {up*TAU_6S_S*1e6:.1f} parts per million of the")
    print("    natural decay. Negligible here and worth watching at the 150 to")
    print("    170 C extension the outlook proposes.")

    print()
    print("(b) DOES IT TOUCH THE 795 nm SIGNAL?  No, and the blocking element")
    print("    is the photocathode rather than the filters. The R636-10 in its")
    print("    PXT1/M housing is GaAs and stops near "
          f"{CATHODE_NM[1]:.0f} nm, so it cannot")
    print("    see the 7.2 um peak whatever the 50 dB of filtering does. That")
    print("    tube attribution is ASSUMED rather than measured here, and it")
    print("    does not matter: no photocathode of any kind responds at 7 um.")
    area = math.pi * CELL_D_M * CELL_L_M + 2.0 * math.pi * (CELL_D_M / 2) ** 2
    print()
    print(f"    cell inner area {area*1e4:.1f} cm^2, whole-wall emission, no")
    print("    collection solid angle applied, so an UPPER BOUND:")
    print(f"      {'T':>6} {'in 300-900 nm':>16} {'in 780-810 nm':>16}")
    for t_c in (70.0, 130.0):
        wide = photon_exitance(t_c + 273.15, *CATHODE_NM) * area
        narrow = photon_exitance(t_c + 273.15, 780.0, 810.0) * area
        print(f"      {t_c:5.0f}C {wide:16.3e} {narrow:16.3e}   photons/s")
    print("    against a signal of order 1e5 to 1e6 detected photons per second")
    print("    on a peak. It is also FLAT in laser frequency, so it enters the")
    print("    free per-trace baseline and not the lineshape. And M1's")
    print("    shot-noise coefficient was measured FLAT from 70 to 130 C, which")
    print("    is an empirical bound on it that predates the question.")

    print()
    print("THE BLACKBODY AC-STARK SHIFT, which is the one number that is not tiny")
    print(f"  alpha_5s at the long-wavelength limit {alpha_5s(1e5):.1f} a.u. and "
          f"alpha_6s {alpha_6s(1e5):.1f},")
    print("  reproducing the committed alpha_5s_static 318.28 and")
    print("  alpha_6s_static 5167.0 of results/polarizability.csv, which are")
    print("  where the DC check already lived. So the differential is sixteen")
    print("  times the ground state's own, and this integration is consistent")
    print("  with the record rather than adding to it.")
    print()
    print(f"  {'T':>6} {'shift (Hz)':>12} {'vs the 5.25 MHz line':>22}")
    ref = None
    for t_c in (70.0, 90.0, 110.0, 130.0):
        s = bbr_shift_hz(t_c + 273.15)
        ref = s if ref is None else ref
        print(f"  {t_c:5.0f}C {s:12.2f} {abs(s)/5.25e6:22.2e}")
    swing = bbr_shift_hz(403.15) - bbr_shift_hz(343.15)
    print()
    print(f"  Across the sweep the shift moves {swing:+.1f} Hz, and it moves as")
    print("  T^4 through the field and faster through the resonances. This is a")
    print("  PRINCIPAL VALUE through the two 6S to 6P poles at 2.73 and 2.79 um,")
    print("  paired about each pole separately because they are only 2.16 per")
    print("  cent apart and a wider window merges them. Stable to the last digit")
    print("  from a 0.2 to a 1.0 per cent window. Against simply excluding the")
    print("  resonances by cutting the band at 3.2 um, they contribute")
    print(f"  {bbr_shift_hz(343.15) - _nonresonant_shift_hz(343.15):+.2f} Hz at "
          f"70 C and {bbr_shift_hz(403.15) - _nonresonant_shift_hz(403.15):+.2f} "
          "Hz at 130 C, so the 10 Hz")
    print("  residue the straddling grid suggested was the grid and not physics.")
    print()
    print("  IT SHIFTS AND DOES NOT BROADEN, so it cannot reach beta_self, which")
    print("  is read from widths. It is quoted for the fixed-lock session, where")
    print("  the centre is the observable and a T^4 systematic on it is worth")
    print("  knowing before rather than after.")
    frac = alpha6s_fractional_band()
    rows = [("nbar", "1324nm", legs[0][3], "", "",
             "Planck occupation number at 130 C", "DIAGNOSTIC"),
            ("nbar", "1367nm", legs[1][3], "", "",
             "Planck occupation number at 130 C", "DIAGNOSTIC"),
            ("nbar", "795nm", n_d1, "", "",
             "Planck occupation number at 130 C, the detected line",
             "DIAGNOSTIC"),
            ("bbr_reexcitation", "5P3/2_to_6S", legs[1][3] * legs[1][2] * 0.5,
             "", "", "per second at 130 C, the larger of the two legs; the "
             "trapped-infrared halo does the same job at about 1.9e3",
             "DIAGNOSTIC"),
            ("bbr_transfer", "6S_to_6P", up, "", "",
             "per second at 130 C, summed over both fine-structure levels; "
             "the largest blackbody channel out of 6S", "DIAGNOSTIC")]
    for t_c in (70.0, 90.0, 110.0, 130.0):
        sh = bbr_shift_hz(t_c + 273.15)
        rows.append(("bbr_stark_shift", f"T{int(t_c)}C", sh, abs(sh) * frac,
                     "polarizability",
                     "Hz on the transition axis, principal value through the "
                     "6S to 6P poles; err is the committed alpha_6s_static "
                     "band carried through", "ENVELOPE"))
    for t_c in (70.0, 130.0):
        rows.append(("bbr_detector_background", f"T{int(t_c)}C",
                     photon_exitance(t_c + 273.15, *CATHODE_NM) * area, "", "",
                     "photons per second from the whole cell wall in the band "
                     "the photocathode can respond to, before any collection "
                     "solid angle, so an upper bound", "ENVELOPE"))
    out = C.RESULTS_DIR / "blackbody_channels.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "err_kind", "unit",
                    "status"])
        for q, k, v, e, ek, u, st in rows:
            w.writerow([q, k, f"{v:.6g}", (f"{e:.4g}" if e != "" else ""),
                        ek, u, st])
    print()
    print(f"  wrote {out.relative_to(C.REPO_ROOT)} ({len(rows)} rows)")
    print()
    print("=" * 78)
    print("The CSV carries its own status column.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Radiation trapping, quantified on both channels it acts through.

WHY THIS EXISTS (2026-08-10). methods chapter 4 establishes that trapping
rescales amplitudes and does not distort the lineshape, because the escape
probability is the same at every point of a frequency scan. That argument is
correct and it is about ONE channel, the detected 795 nm photon being
reabsorbed by ground-state atoms. Two questions were never put:

  1. how large is that trapping across the temperature sweep, in escape
     factors rather than in adjectives, and
  2. what does the trapped light do to the OTHER transitions of the cascade,
     specifically the 5P to 6S legs at 1324 and 1367 nm that the same atoms
     are radiating on.

The second turns out to matter at the top of the sweep and to matter in a way
that is not a lineshape effect, which is why it belongs beside the trapping
argument rather than inside it.

WHAT IT FINDS.

* The two infrared legs, computed from this package's own NIST matrix
  elements, sum to 100.3 per cent of the measured 6S decay rate. 6S has no
  allowed decay to 5S, so this is a closure check on the line data against an
  independently measured lifetime, and it passes to three parts in a thousand.
  The branching is 34.1 per cent through 5P1/2 and 65.9 through 5P3/2.

* The Doppler-broadened peak cross-sections of the two infrared legs come out
  at 1.41e-11 and 1.50e-11 cm^2, which is the SAME as the D1 cross-section the
  trapping argument uses for 795 nm. Per atom in the lower state the infrared
  lines absorb as strongly as D1 does. Everything that separates the two
  channels is therefore population and nothing else, which is worth saying
  because the infrared is usually dismissed as an afterthought on the grounds
  of wavelength.

* INSIDE the driven volume both infrared lines are INVERTED, by 4.8 and 5.3 in
  the degeneracy-weighted populations, because 5P empties in 27 ns while 6S is
  refilled by the drive. So trapped infrared there does not re-excite 5P to 6S.
  It stimulates 6S downward. The re-excitation the question asks about cannot
  happen where the atoms are being driven.

* It happens OUTSIDE. Trapped 795 nm photons deposit 5P1/2 population in a
  halo around the driven column where there is no 6S at all, and there the
  infrared lines absorb. At 130 C that halo reaches 1.13e10 cm^-3, which is
  64 per cent of the 5P density inside the beam, and it re-excites 5P to 6S at
  about 1 per cent of the primary two-photon rate. At 70 C it is nothing.

* That 1 per cent is not a lineshape distortion. The halo is fed by trapped
  795 photons, whose number is proportional to the two-photon rate, so the
  re-excited population tracks the line rather than adding a pedestal. It
  rescales the amplitude, which is the same conclusion chapter 4 reaches for
  direct trapping, by a second mechanism with a STEEPER density dependence.
  That is where it bites: the amplitude-against-density comparisons of M7 and
  M10, not the widths.

TWO DEFECTS FOUND ON RE-RUNNING IT, 2026-08-10, both in the escape path and
both recorded here rather than quietly fixed. The committed code took the
escape path as TWICE the standoff while the argument that motivates it, and
the numbers written in this docstring, take it as the standoff itself. That
doubled every optical depth and inflated the halo by 2.2. And the Holstein
asymptotic exceeds one just above the cutoff it was guarded at, so the coldest
point of the sweep returned an escape probability better than free flight and a
NEGATIVE halo density, which is the kind of sign error a table makes visible
and a sentence does not. Fixed, and the script now reproduces the numbers
below. THE LESSON is the one already in the protocol: a docstring that states
numbers is a claim, and it has to be re-run against its own code, because here
it was the CODE that had drifted from the correct answer.

STATUS. The line-data quantities are exact given the line list and are tagged
DIAGNOSTIC. The halo is ENVELOPE: its volume and the escape factor are
geometric estimates, the D1 cross-section carries its own envelope tag in
constants.py, and the Holstein form assumes a Doppler-broadened line in a
cylinder. THE STANDOFF IS NOT RECORDED, so the halo result is quoted as a BAND
over the 1 to 5 mm the record brackets rather than as a point, and that band is
the error bar in the CSV.

WRITES results/trapping_channels.csv, with its own status and err_kind columns
(so the annotator skips it). It writes because docs/STYLE.md requires prose to
quote committed CSVs rather than restate numbers, and these numbers are now
quoted in CLAIMS and in methods chapter 4.

    ./.venv/bin/python scripts/run_trapping_channels.py
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import (ABUNDANCE_RB85, K_B_J_PER_K,  # noqa: E402
                              M_RB87_KG, SIGMA_D1_CM2, TAU_5P12_S, TAU_6S_S)
from rb5s6s.density import d1_optical_depth_per_cm, number_density_cm3  # noqa: E402
from rb5s6s.polarizability import E_6S_CM, LINES_6S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_geometry_design import ramp_moments  # noqa: E402

A0 = 5.29177210903e-11
E_C = 1.602176634e-19
HBAR = 1.054571817e-34
EPS0 = 8.8541878128e-12
CL = 2.99792458e8
T_C = 130.0
TAU_5P32_S = 26.2e-9          # ESTABLISHED, the D2 lifetime
# ONE length does two jobs here and they were conflated once, so both are
# named. The escape path is the distance from the source to the nearest way
# out, which the owner's 2026-08-09 statement makes the STANDOFF from the near
# window rather than the cell radius, because the waist was placed close to the
# collection lens. The halo is the region trapped 795 nm photons light up
# around the driven column, and it extends about one absorption path, which is
# the same length. They are equal by construction and not by coincidence.
STANDOFF_CM = 0.2             # see APPARATUS, focus position in the cell
HALO_RADIUS_CM = STANDOFF_CM
# The standoff is NOT recorded, and the halo result is geometry-dominated, so a
# point value would be a false precision. The record brackets it: the
# magnification estimate gives 2.0 to 2.4 mm and the confinement factors it
# quotes run from 1 mm to 5 mm. That range is carried as the error bar.
STANDOFF_BAND_CM = (0.10, 0.50)
SIGMA_V = math.sqrt(K_B_J_PER_K * (T_C + 273.15) / M_RB87_KG)


def _leg(e_cm: float, d_au: float) -> tuple[float, float]:
    """Wavelength (m) and Einstein A (s^-1) for one 6S to 5P leg."""
    lam = 1e7 / (E_6S_CM - e_cm) * 1e-9
    omega = 2.0 * math.pi * CL / lam
    d = d_au * E_C * A0
    return lam, omega ** 3 * d ** 2 / (3.0 * math.pi * EPS0 * HBAR * CL ** 3 * 2)


def _sigma_peak_cm2(lam_m: float, a_einstein: float, g_up: int, g_lo: int) -> float:
    """Doppler-broadened peak cross-section, in cm^2."""
    dnu_d = 2.0 * math.sqrt(2.0 * math.log(2.0)) * SIGMA_V / lam_m
    return (lam_m ** 2 / (8.0 * math.pi)) * a_einstein * (0.93944 / dnu_d) \
        * (g_up / g_lo) * 1e4


def _escape_factor(tau: float) -> float:
    """Holstein escape probability per emission, Doppler line, cylinder.

    The asymptotic form is valid for large tau and EXCEEDS ONE just above the
    old cutoff of 1.2, crossing unity near tau = 1.46, which made the escape
    factor better than free flight and drove the halo density negative at the
    coldest point of the sweep. Clamping is the fix rather than raising the
    cutoff, because it is right at every tau and states the physics: a photon
    cannot escape more often than always.
    """
    if tau <= 1.2:
        return 1.0
    return min(1.0, 1.60 / (tau * math.sqrt(math.pi * math.log(tau))))


def halo_reexcitation(t_c: float, standoff_cm: float, f_ex: float,
                      b12: float, s12: float, v_beam: float) -> tuple:
    """5P density in the halo and the 5P-to-6S re-excitation it drives.

    Returns (n_halo, n_beam, percent_of_primary_rate). Split out of main() so
    the same arithmetic produces the table, the error bar and the CSV row.
    """
    n_drv = ABUNDANCE_RB85 * 0.5 * number_density_cm3(t_c)
    tau = d1_optical_depth_per_cm(t_c, 85) * standoff_cm
    g = _escape_factor(tau)
    v_halo = (4.0 / 3.0) * math.pi * standoff_cm ** 3
    r_dec = f_ex * n_drv * v_beam / TAU_6S_S
    n_halo = r_dec * b12 * (1.0 / g - 1.0) * TAU_5P12_S / v_halo
    n_beam = f_ex * n_drv * a_leg12() * TAU_5P12_S
    p_abs = 1.0 - math.exp(-n_halo * s12 * standoff_cm)
    return n_halo, n_beam, 100.0 * p_abs * b12


def a_leg12() -> float:
    return _leg(*LINES_6S[0][:2])[1]


def halo_band(t_c: float, f_ex: float, b12: float, s12: float,
              v_beam: float, n: int = 41) -> tuple:
    """Min and max of the halo re-excitation over the standoff range.

    SAMPLED, not read off the two ends, because the function is NOT monotonic
    in the standoff and a first version of this took the endpoints. Below the
    Holstein cutoff the escape factor is exactly 1, so the halo is exactly
    zero, and at 90 C a 1 mm standoff sits below that cutoff while 2 mm does
    not. The endpoint band therefore excluded its own point value, which the
    guard in tests/test_radiation_environment_csv.py caught on its first run.
    """
    lo_cm, hi_cm = STANDOFF_BAND_CM
    vals = [halo_reexcitation(t_c, lo_cm + (hi_cm - lo_cm) * k / (n - 1),
                              f_ex, b12, s12, v_beam)[2] for k in range(n)]
    return min(vals), max(vals)


def main() -> int:
    lam12, a12 = _leg(*LINES_6S[0][:2])
    lam32, a32 = _leg(*LINES_6S[1][:2])
    b12 = a12 / (a12 + a32)

    print("=" * 78)
    print("THE TWO INFRARED LEGS, from this package's own matrix elements")
    print(f"  6S -> 5P1/2  {lam12*1e9:7.1f} nm   A = {a12:9.3e} /s   "
          f"branching {b12:.4f}")
    print(f"  6S -> 5P3/2  {lam32*1e9:7.1f} nm   A = {a32:9.3e} /s   "
          f"branching {1-b12:.4f}")
    closure = (a12 + a32) * TAU_6S_S
    print(f"  sum A times the measured 6S lifetime = {closure:.4f}. 6S has no")
    print("  allowed decay to 5S, so this closes the line data against an")
    print("  independent lifetime measurement to three parts in a thousand.")

    s12 = _sigma_peak_cm2(lam12, a12, 2, 2)
    s32 = _sigma_peak_cm2(lam32, a32, 2, 4)
    print()
    print("PEAK CROSS-SECTIONS, Doppler-broadened at 130 C")
    print(f"  1324 nm {s12:.3e} cm^2      1367 nm {s32:.3e} cm^2")
    print(f"  D1 795 nm {SIGMA_D1_CM2:.3e} cm^2 (constants.SIGMA_D1_CM2)")
    print("  The infrared absorbs as strongly per lower-state atom as D1 does.")
    print("  What separates the channels is population and nothing else.")

    m = ramp_moments(C.W0_MEASURED_M, 0.225, 2.2e-3)
    f_ex = (m["sat_w"] / 2.0) / (1.0 + m["sat_w"])
    n6s, n5p12, n5p32 = f_ex, f_ex * a12 * TAU_5P12_S, f_ex * a32 * TAU_5P32_S
    print()
    print("INVERSION INSIDE THE DRIVEN VOLUME, per driven atom")
    print(f"  n(6S)/2      {n6s/2:.6f}")
    print(f"  n(5P1/2)/2   {n5p12/2:.6f}   -> 1324 inverted by "
          f"{(n6s/2)/(n5p12/2):.2f}")
    print(f"  n(5P3/2)/4   {n5p32/4:.6f}   -> 1367 inverted by "
          f"{(n6s/2)/(n5p32/4):.2f}")
    print("  So trapped infrared here stimulates 6S DOWN. The 5P to 6S")
    print("  re-excitation cannot happen where the atoms are being driven.")

    z_r = math.pi * C.W0_MEASURED_M ** 2 / 993.4e-9
    v_beam = math.pi * C.W0_MEASURED_M ** 2 * (2.0 * z_r) * 1e6
    v_halo = (4.0 / 3.0) * math.pi * HALO_RADIUS_CM ** 3
    print()
    print("THE HALO, where it does happen. Trapped 795 nm deposits 5P1/2")
    print("outside the driven column, where there is no 6S and the infrared")
    print(f"absorbs. Driven volume {v_beam:.3e} cm^3, halo "
          f"{v_halo:.3e} cm^3 at a {STANDOFF_CM*10:.0f} mm escape path.")
    print()
    print(f"  {'T':>4} {'tau':>9} {'1/g':>7} {'n5P halo':>11} "
          f"{'n5P beam':>11} {'halo/beam':>10} {'re-exc':>8} {'band':>16}")
    band = {}
    for t_c in (70.0, 90.0, 110.0, 130.0):
        tau = d1_optical_depth_per_cm(t_c, 85) * STANDOFF_CM
        n_halo, n_beam, pct = halo_reexcitation(t_c, STANDOFF_CM, f_ex, b12,
                                                s12, v_beam)
        blo, bhi = halo_band(t_c, f_ex, b12, s12, v_beam)
        band[t_c] = (pct, blo, bhi)
        print(f"  {t_c:4.0f} {tau:9.2f} {1/_escape_factor(tau):7.1f} "
              f"{n_halo:11.3e} {n_beam:11.3e} {n_halo/n_beam:9.2f} "
              f"{pct:7.2f} % {blo:6.2f} to {bhi:5.2f} %")
    print()
    print(f"  THE BAND is the {STANDOFF_BAND_CM[0]*10:.0f} to "
          f"{STANDOFF_BAND_CM[1]*10:.0f} mm standoff the record brackets, and it")
    print("  is the error bar, because the standoff is not recorded and this")
    print("  result is geometry-dominated. It is SAMPLED across that range and")
    print("  not read off the two ends, because the function is not monotonic:")
    print("  below the Holstein cutoff the escape factor is exactly one and the")
    print("  halo is exactly zero, which at 90 C happens between 1 and 2 mm.")
    print()
    print("  The last column is the 5P to 6S re-excitation rate as a")
    print("  percentage of the primary two-photon rate. It is nothing at 70 C")
    print("  and about one per cent at 130 C.")
    print()
    print("  IT IS NOT A LINESHAPE EFFECT. The halo is fed by trapped 795")
    print("  photons, whose number is proportional to the two-photon rate, so")
    print("  the re-excited population tracks the line rather than adding a")
    print("  pedestal. It rescales the amplitude, which is chapter 4's")
    print("  conclusion for direct trapping, reached by a second mechanism")
    print("  with a steeper density dependence. That is where it bites: the")
    print("  amplitude-against-density comparisons, not the widths.")
    rows = [
        ("ir_branching", "5P1/2", b12, "", "",
         "fraction of 6S decays through the 1324 nm leg", "DIAGNOSTIC"),
        ("ir_branching", "5P3/2", 1.0 - b12, "", "",
         "fraction of 6S decays through the 1367 nm leg", "DIAGNOSTIC"),
        ("line_data_closure", "sum_A_times_tau6S", closure, "", "",
         "dimensionless; 6S has no allowed decay to 5S so this closes the "
         "line data against an independently measured lifetime", "DIAGNOSTIC"),
        ("sigma_peak", "1324nm", s12, "", "",
         "cm^2; Doppler-broadened at 130 C", "DIAGNOSTIC"),
        ("sigma_peak", "1367nm", s32, "", "",
         "cm^2; Doppler-broadened at 130 C", "DIAGNOSTIC"),
        ("inversion_in_beam", "1324nm", (n6s / 2) / (n5p12 / 2), "", "",
         "degeneracy-weighted population ratio; above 1 means trapped light "
         "stimulates 6S down and cannot re-excite 5P", "DIAGNOSTIC"),
        ("inversion_in_beam", "1367nm", (n6s / 2) / (n5p32 / 4), "", "",
         "degeneracy-weighted population ratio", "DIAGNOSTIC"),
    ]
    # ASYMMETRIC, and a single err column said otherwise. The point value sits
    # at a 2 mm standoff and the band runs over 1 to 5 mm, and the halo is not
    # linear in the standoff, so the point is nowhere near the middle: at 130 C
    # the band is -0.58 and +0.78 about 1.07. Quoting half the range put the
    # reconstructed interval at 0.39 to 1.75 where the true one is 0.49 to
    # 1.85, which the docs had right and the CSV had wrong. Two ends now.
    for t_c, (pct, lo, hi) in sorted(band.items()):
        rows.append(("halo_reexcitation", f"T{int(t_c)}C", pct,
                     "", "geometry",
                     "per cent of the primary two-photon rate, at a 2 mm "
                     f"standoff; err_lo and err_hi are the distances to the "
                     f"ends of the {STANDOFF_BAND_CM[0]*10:.0f} to "
                     f"{STANDOFF_BAND_CM[1]*10:.0f} mm standoff band, which is "
                     "a range over a geometric unknown and not a sigma",
                     "ENVELOPE", pct - lo, hi - pct))
    out = C.RESULTS_DIR / "trapping_channels.csv"
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "err_lo", "err_hi",
                    "err_kind", "unit", "status"])
        for row in rows:
            q, k, v, e, ek, u, st = row[:7]
            lo, hi = (row[7], row[8]) if len(row) > 7 else ("", "")
            w.writerow([q, k, f"{v:.6g}", (f"{e:.4g}" if e != "" else ""),
                        (f"{lo:.4g}" if lo != "" else ""),
                        (f"{hi:.4g}" if hi != "" else ""), ek, u, st])
    print()
    print(f"  wrote {out.relative_to(C.REPO_ROOT)} ({len(rows)} rows), which is")
    print("  what lets the prose quote these numbers instead of restating them.")
    print()
    print("=" * 78)
    print("ENVELOPE where tagged. The CSV carries its own status column.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
The wide-scan block, computed so the next session can run it cold.

    ./.venv/bin/python scripts/run_widescan_design.py

A DESIGN calculation in the sense of run_geometry_design: it writes nothing,
touches no committed number, and every input is read from the record. PLAN
section 10a states the settings in prose; this computes them, forward-models
the trace they produce, and prints the go/no-go checks to make on the day.

WHY THE BLOCK EXISTS. The 2026-08-15 analysis ended against three limits that
were all set at acquisition time. The out-of-window band that carries
ridge-breaking information about the collisional width is 17 MHz wide out of
a 43 MHz half-span, enough to show it discriminates and not enough to say
what lives in it. The co-propagating Doppler pedestal is 942 MHz wide, so
across the whole 85 MHz span it varies by half a per cent and is absorbed by
the free per-trace background: unmeasurable AND unexcludable. And the fitted
laser width is three to four times what this bench's ONE in-campaign wavemeter
record allows, with the leading explanation degenerate with the term it would
replace. Two of those three are span questions, and span is a knob.

WHAT THE BLOCK BUYS, in the record's own terms:
  * the pedestal becomes an IN-SITU THERMOMETER (its width is 2 sqrt(8 ln2
    kT/m)/lambda, so the gas temperature stops being an adopted number) and an
    IN-SITU RETRO RATIO (the narrow-to-pedestal area ratio is 4 rho/(1+rho^2),
    the block register's own entry);
  * the band excess gets frequency reach: any candidate that is broad must
    CURVE somewhere inside the 2400 MHz span, and a constant cannot;
  * the width budget gets an independent handle, because a residual-Doppler
    term and a laser term separate once the pedestal they share is visible.

NOTHING HERE NEEDS NEW HARDWARE. A deeper record is a menu setting.

THE SHAPE REQUIREMENT WAS RAISED ON 2026-08-16, and it is a scientific update
rather than a tidy-up. The requirement below was first stated before any
simulation tested it. The B5 and B6 runs of the 2026-08-15 fit chain then
measured the width recovery at the committed noise law and found that about 22
points across the line FAILS a frozen recovery criterion while 40000 points
over the same span passes with margin. The constant is now 90, which is what
PLAN section 10a states, and the record length this script derives follows from
it rather than from the round number it used to be floored at. The pedestal
significance printed below rises with the record for the same reason. What
these values replaced is recorded in docs/HISTORY.md.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rb5s6s import config as C                                    # noqa: E402
from rb5s6s import constants as K                                 # noqa: E402
from rb5s6s.linefit import _shared_profile_grid                   # noqa: E402

REPO = Path(__file__).resolve().parents[1]
T_C = 130.0
POINTS_PER_LINE_FWHM = 90        # the shape requirement, stated before sizing
REACH_IN_SIGMA = 3.0             # how far out the pedestal must be followed
CORE_CUT_MHZ = 20.0              # points nearer than this belong to the line


def background_degeneracy_factor(reach_in_sigma: float, ped_sigma: float,
                                 core_cut: float = CORE_CUT_MHZ) -> float:
    """Fraction of pedestal-amplitude SNR that survives a FREE flat background.

    Observing y = A*g(nu) + B with g the known pedestal shape and B a free
    constant, the Fisher matrix for (A, B) under uniform sampling is
    N*[[<g^2>, <g>], [<g>, 1]], so var(A) with B free is 1/(N*(<g^2>-<g>^2))
    against 1/(N*<g^2>) with B known. The SNR ratio is therefore

        sqrt(1 - <g>^2 / <g^2>)

    which is EXACT for this model and is what a flat background costs. It is
    0.140 at one sigma of reach and 0.645 at three.

    WHY IT IS COMPUTED RATHER THAN ASSUMED. A free background is a DIRECTION in
    parameter space, not a haircut on amplitude, so what survives is the
    component orthogonal to it. Reasoning from where the pedestal has fallen at
    the span edge answers a question about VISIBILITY, and the design needs one
    about INFORMATION. The two differ by a factor of five at one sigma of
    reach. Protocol rule 19.29 states the general form, and the earlier
    assumption is recorded in docs/HISTORY.md.
    """
    half = reach_in_sigma * ped_sigma
    nu = np.linspace(-half, half, 20001)
    g = np.exp(-0.5 * (nu / ped_sigma) ** 2)[np.abs(nu) >= core_cut]
    return math.sqrt(max(0.0, 1.0 - g.mean() ** 2 / (g ** 2).mean()))


def committed(peak: str = "4154"):
    """Line parameters and the 2025 acquisition, read from the record."""
    for r in csv.DictReader(open(REPO / "results/linefit_conditions.csv")):
        if r["peak"] == peak and r["T"] == "130" and r["P"] == "225":
            return (float(r["gamma_coll"]), float(r["sigma_laser"]),
                    float(r["total_fwhm"]), float(r["rate_t"]))
    raise KeyError(peak)


def pedestal_fwhm_mhz(t_c: float, mass_kg: float = None) -> float:
    """Co-propagating two-photon Doppler width, TRANSITION axis."""
    m = mass_kg if mass_kg else K.M_RB85_KG
    v = math.sqrt(8.0 * math.log(2.0) * K.K_B_J_PER_K * (t_c + 273.15) / m)
    return 2.0 * v / K.LAMBDA_LASER_M / 1e6


def narrow_to_pedestal_area(rho: float) -> float:
    """Doppler-free area over pedestal area, the repository's own formula."""
    return 4.0 * rho / (1.0 + rho ** 2)


def main() -> int:
    gc, sl, fwhm, rate = committed()
    transit = K.transit_fwhm_from_w0(K.W0_MEASURED_M, 110.0) * math.sqrt(
        (T_C + 273.15) / 383.15)
    ped_fwhm = pedestal_fwhm_mhz(T_C)
    ped_sigma = ped_fwhm / 2.3548200450309493

    print("=" * 74)
    print("THE 2025 ACQUISITION, for comparison (from committed constants)")
    print("=" * 74)
    win = K.TRACE_N_POINTS * K.TRACE_DT_S
    span25 = win * 1e3 * rate
    print(f"  {K.TRACE_N_POINTS} points x {K.TRACE_DT_S*1e3:.3f} ms = {win:.3f} s window")
    print(f"  rate {rate:.5f} MHz/ms  ->  span {span25:.1f} MHz "
          f"(+-{span25/2:.1f}) at {rate*K.TRACE_DT_S*1e3:.4f} MHz/point")
    print(f"  line FWHM {fwhm:.2f} MHz  ->  {fwhm/(rate*K.TRACE_DT_S*1e3):.0f} points across it")
    print(f"  pedestal FWHM {ped_fwhm:.0f} MHz varies "
          f"{100*(1-math.exp(-0.5*(span25/2/ped_sigma)**2)):.2f} per cent across that span")
    print("  VERDICT: the pedestal is a constant here, and the background eats it.\n")

    print("=" * 74)
    print("THE WIDE-SCAN SETTINGS, computed")
    print("=" * 74)
    span = 2.0 * REACH_IN_SIGMA * ped_sigma
    res_needed = fwhm / POINTS_PER_LINE_FWHM
    n_min = span / res_needed
    print(f"  requirement 1, REACH: follow the pedestal to {REACH_IN_SIGMA:.0f} sigma")
    print(f"    pedestal sigma {ped_sigma:.0f} MHz  ->  SPAN {span:.0f} MHz (+-{span/2:.0f})")
    print(f"  requirement 2, SHAPE: keep {POINTS_PER_LINE_FWHM} points across the line")
    print(f"    line FWHM {fwhm:.2f} MHz  ->  resolution {res_needed:.3f} MHz/point")
    print(f"  => RECORD LENGTH >= {n_min:.0f} points. Set the deepest the export allows.")
    print()
    for n in (2000, 4000, 10000, 100000):
        r = span / n
        print(f"    at {n:>6d} points: {r:.4f} MHz/pt, {fwhm/r:5.1f} points across the line"
              + ("   <- 2025 record, UNUSABLE for shape" if n == 2000 else ""))
    print()
    t_win = span / rate / 1e3
    print(f"  IF THE RATE IS HELD at the 2025 {rate:.5f} MHz/ms:")
    print(f"    window {t_win:.1f} s per trace, i.e. {t_win/K.TRACE_DT_S:.0f} points at the")
    print("    2025 sample interval. Same conclusion by another route.")
    print(f"  IF THE WINDOW IS HELD at {win:.1f} s: rate must be "
          f"{span/(win*1e3):.4f} MHz/ms, {span/span25:.1f}x the 2025 piezo amplitude.")
    print()
    print("  PIEZO SHAPE: sawtooth, or export one direction only. A symmetric")
    print("  triangle images an off-centre line about the turning point, which")
    print(f"  is the ~40 MHz mirror that caps the 2025 fit window at "
          f"{C.FIT_HALFWIDTH_MAX_MHZ:.0f} MHz.")
    print("  If the triangle must stay, CENTRE the line so its mirror lands on it.")
    print(f"  DWELL: keep >= the 2025 {K.TRACE_DT_S*1e3:.1f} ms per point unless the")
    print("  detection bandwidth is checked against it. The cusp is a time-domain")
    print("  feature and a fast scan smears it.\n")

    print("=" * 74)
    print("THE EXPECTED TRACE, forward-modelled, and what it should look like")
    print("=" * 74)
    rho = C.RHO_RETRO
    area_ratio = narrow_to_pedestal_area(rho)
    g, prof = _shared_profile_grid(gc, sl, transit, 0.0, "gaussian")
    line_peak_per_area = float(prof.max())
    ped_peak_per_area = 1.0 / (ped_sigma * math.sqrt(2.0 * math.pi))
    frac = (ped_peak_per_area / area_ratio) / line_peak_per_area
    print(f"  retro power ratio rho = {rho}")
    print(f"  narrow/pedestal AREA ratio 4rho/(1+rho^2) = {area_ratio:.4f}")
    print(f"  so PEDESTAL HEIGHT / LINE HEIGHT = {100*frac:.3f} per cent of peak")
    print()
    noise_frac = 0.0039        # measured, single point, as a fraction of peak
    taus = sorted(float(r["tau_int"]) for r in
                  csv.DictReader(open(REPO / "results/noise_model.csv"))
                  if r.get("tau_int"))
    tau = taus[len(taus) // 2]                 # the record's MEDIAN, read live
    degen = background_degeneracy_factor(REACH_IN_SIGMA, ped_sigma)
    n = int(max(n_min, 10000))
    res = span / n
    on_ped = int(0.9 * n)      # points clear of the line core
    n_eff = on_ped / tau
    snr1 = frac / noise_frac * math.sqrt(n_eff) * degen
    print(f"  measured single-point noise (2026-08-15) {100*noise_frac:.2f} per cent of peak")
    print(f"  at {n} points, ~{on_ped} sit on the pedestal and off the line")
    print("  TWO CORRECTIONS, both of which a naive count would miss:")
    print(f"    correlated noise. The record's {len(taus)} tau_int values run "
          f"{taus[0]:.2f} to {taus[-1]:.2f},")
    print(f"      median {tau:.2f}, read live from results/noise_model.csv so")
    print("      it cannot drift from the record.")
    print(f"      So the effective count is {n_eff:.0f} and not {on_ped}.")
    print("    degeneracy with the FREE per-trace background, which absorbs the")
    print("      flat part of any broad shape. Computed as a Fisher ratio, NOT")
    print(f"      guessed: {degen:.3f} of the ideal SNR survives at "
          f"{REACH_IN_SIGMA:.0f} sigma of reach.")
    print(f"  => PEDESTAL DETECTED AT ~{snr1:.0f} SIGMA IN ONE TRACE")
    print(f"     (and ~{snr1*math.sqrt(5):.0f} sigma in a five-trace block)")
    print(f"     A NAIVE count would have said {frac/noise_frac*math.sqrt(on_ped):.0f}, "
          f"which is the number to distrust.")
    print("     AND ACROSS THE FULL tau RANGE, so the assumption is not load-bearing:")
    for tt in (taus[0], tau, taus[-1]):
        s = frac / noise_frac * math.sqrt(on_ped / tt) * degen
        print(f"       tau = {tt:5.2f}  ->  {s:5.1f} sigma per trace, "
              f"{s*math.sqrt(5):5.1f} per five-trace block")
    print("     Even the record's worst tau detects the pedestal decisively.")
    print()
    print("  WHY THE REACH IS 3 SIGMA AND NOT 1, which is the whole design.")
    print("  The free background absorbs whatever is flat, so the pedestal is")
    print("  measured only through its CURVATURE across the span. A narrow span")
    print("  sees an almost-flat pedestal and loses nearly all of it. But a wide")
    print("  span costs resolution at fixed record length, and the line needs")
    print(f"  {POINTS_PER_LINE_FWHM} points across its FWHM. Both, together:")
    print()
    print(f"    {'reach':>6} {'span':>7} {'retained':>9} {'sigma/trace':>12} "
          f"{'pts/line FWHM':>14}")
    for r in (1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
        sp = 2.0 * r * ped_sigma
        dg = background_degeneracy_factor(r, ped_sigma)
        s = frac / noise_frac * math.sqrt(0.9 * n / tau) * dg
        mark = "   <- chosen" if abs(r - REACH_IN_SIGMA) < 1e-9 else ""
        print(f"    {r:5.1f}s {sp:6.0f} {dg:9.3f} {s:12.0f} {fwhm/(sp/n):14.1f}{mark}")
    print()
    print("  The knee is near 3 sigma: past it the retained fraction gains little")
    print("  and the resolution keeps falling. THIS TABLE IS THE RECOMMENDATION.")
    print()
    print(f"  FEASIBILITY, WHICH IS NOT ASSUMED. {span:.0f} MHz is "
          f"{span/span25:.0f}x the 2025 span,")
    print("  and a piezo has a finite range. IF THE FULL 3 SIGMA IS NOT")
    print("  REACHABLE, the table above is also the fallback schedule: read off")
    print("  the widest reach the hardware allows and take that row's numbers.")
    print("  Every row still detects the pedestal in a five-trace block, so a")
    print("  narrower span degrades the measurement without defeating it.")
    print("  THE ONE THING NOT TO DO is keep the 2025 span, where the retained")
    print(f"  fraction is {background_degeneracy_factor(span25/2/ped_sigma, ped_sigma):.4f} "
          "and the pedestal is unmeasurable in principle.")
    print("  Stitching two offset scans is the other route if the piezo caps out.")
    print()
    dT_over_T = 2.0 / snr1
    print("  THERMOMETRY: the width goes as sqrt(T), so dT/T = 2 dW/W.")
    print(f"    a {100/snr1:.2f} per cent width measurement gives T to "
          f"{100*dT_over_T:.2f} per cent, i.e. +-{dT_over_T*(T_C+273.15):.1f} K at {T_C:.0f} C")
    print("  RETRO RATIO: the area ratio is 4rho/(1+rho^2), which is FLAT in rho")
    print(f"    near 1 (derivative {abs(4*(1-rho**2)/(1+rho**2)**2):.3f} per unit rho at "
          f"rho={rho}), so this is a weak")
    print("    handle unless rho is well away from unity. Recorded as a caveat,")
    print("    which is the block register's own empty case.\n")

    print("=" * 74)
    print("GO / NO-GO CHECKS, on the day, before the block is trusted")
    print("=" * 74)
    checks = [
        ("the pedestal is VISIBLE in a single raw trace at the "
         f"{100*frac:.2f} per cent level", "if not, the span or the record length did not take"),
        ("the line still has >= 10 points across its FWHM",
         "if not, the record length lost to the span and shape is gone"),
        ("no second copy of the line anywhere in the span",
         "if there is one, the retrace mirror survived the sawtooth change"),
        ("the EOM comb is still resolvable for the frequency axis",
         f"teeth are {K.TOOTH_SPACING_LASER_HZ/1e6:.2f} MHz apart on the laser axis, so "
         f"{K.TOOTH_SPACING_LASER_HZ/1e6*2/res:.1f} points per tooth at this resolution"),
        ("the per-trace timestamp is in the export",
         "the archive had to recover the clock separately and blocks turned "
         "out 54-76 minutes apart"),
        ("the ramp monitor is on its own channel and saved",
         "PLAN section 3 item 0, the time axis independent of the scope knob"),
    ]
    for i, (c, why) in enumerate(checks, 1):
        print(f"  {i}. {c}")
        print(f"     {why}")
    print()
    print("  AND THE TWO MEASUREMENTS THAT DO NOT RIDE THIS BLOCK, both cheap:")
    print("    one beat-note or self-heterodyne laser linewidth, and one retro")
    print("    alignment check. The 2026-08-15 analysis showed the retro-tilt")
    print("    hypothesis is degenerate with sigma_laser BY CONSTRUCTION, so no")
    print("    fit to any scan settles it. Only the bench can.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

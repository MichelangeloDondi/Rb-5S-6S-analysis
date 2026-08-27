#!/usr/bin/env python3
"""
M16: dynamic polarizabilities of 5S/6S, the independent Delta_alpha recompute,
and the 5S-6S magic wavelengths.

Validates the model against measurements it does not use (the 790.032 nm 5S
tune-out, the static polarizabilities), recomputes Delta_alpha(993) -- SAME
magnitude as Orson 2021's 1093 a.u. within ~5%, OPPOSITE sign, the flagged
finding of rb5s6s/polarizability.py -- and reports the (unpublished) 5S-6S
magic crossings and alpha_6S(1064) with Monte-Carlo uncertainty bands.

Writes results/polarizability.csv.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import DELTA_ALPHA_AU  # noqa: E402
from rb5s6s.polarizability import (alpha_5s, alpha_6s, delta_alpha,  # noqa: E402
                                   TAIL_6S,
                                   tuneout_5s, magic_wavelengths, mc_band,
                                   _alpha, LINES_5S, LINES_6S, E_6S_CM,
                                   _POLES_6S_NM)
from scipy.optimize import brentq  # noqa: E402


def _cross_window(lam0: float, half: float = 25.0):
    """A brentq window about a crossing, clipped inside its pole-free segment
    (the 6S->nP resonances bound where the difference is finite)."""
    lo, hi = lam0 - half, lam0 + half
    for p in _POLES_6S_NM:
        if lam0 < p < hi:
            hi = p - 1.5
        if lo < p < lam0:
            lo = p + 1.5
    return lo, hi


def _a5(kw5, lam):
    return _alpha(LINES_5S, lam, 0.0, kw5["tail"], kw5["core"], kw5["scale"])


def _a6(kw6, lam):
    return _alpha(LINES_6S, lam, E_6S_CM, kw6["tail"], kw6["core"], kw6["scale"])


def main() -> int:
    print("=" * 74)
    print("(M16) DYNAMIC POLARIZABILITIES 5S/6S -- validation, Delta_alpha, magic")
    a5s, a6s = alpha_5s(0.0), alpha_6s(0.0)
    t0 = tuneout_5s()
    # THE DRIVE WAVELENGTH IS THE LITERATURE LINE, not 993.0 and not the
    # campaign file label. Until 2026-08-26 every row named "_993" was
    # computed at exactly 993.0 nm, 418 pm from the line, which moved
    # alpha_5s by 1.2 a.u. and put the value at the real line BELOW that
    # row's own 16th percentile: the band excluded the number the row named.
    #
    # 993.4181 nm is 2e7 / E_6S_CM, the NIST ASD level, and NOT 993.4192,
    # which is the campaign's own file label. The owner's instruction,
    # 2026-08-26: his wavemeter was never calibrated, and constants.
    # label_offset_mhz measures those labels reading +292 MHz high,
    # common-mode to 19 MHz across the four lines. A physical input must not
    # inherit an instrument the record documents as uncalibrated. The two
    # differ by 1.1 pm and 0.002 a.u., so this is provenance rather than
    # arithmetic, which is the reason to get it right rather than to shrug.
    LAM_DRIVE_NM = 2e7 / E_6S_CM

    da993 = delta_alpha(LAM_DRIVE_NM)
    a6_1064 = alpha_6s(1064.0)
    magic = magic_wavelengths()

    # Monte-Carlo bands on the six quantities that used to ship without one.
    # Added 2026-08-10: the same mc_band() the file already uses for
    # Delta_alpha, alpha_6S(1064) and the magic crossings, applied to the
    # rest of the model's outputs so every quantity in this file carries the
    # same uncertainty machinery rather than four of ten having none.
    b_a5s = mc_band(lambda k5, k6: _a5(k5, 0.0))
    b_a6s = mc_band(lambda k5, k6: _a6(k6, 0.0))
    b_t0 = mc_band(lambda k5, k6: brentq(lambda x: _a5(k5, x), 781.0, 794.0,
                                         xtol=1e-6))
    b_a5_993 = mc_band(lambda k5, k6: _a5(k5, LAM_DRIVE_NM))
    b_a6_993 = mc_band(lambda k5, k6: _a6(k6, LAM_DRIVE_NM))
    b_a6_1064 = mc_band(lambda k5, k6: _a6(k6, 1064.0))

    print("\n  VALIDATION (anchors the model does not use):")
    print(f"    alpha_5S(0)  = {a5s:8.2f} au   (measured 318.79(1.42))")
    print(f"    alpha_6S(0)  = {a6s:8.1f} au   (Safronova-group 5167(22); tail calibrated)")
    print(f"    5S tune-out  = {t0:9.3f} nm  (measured 790.032326(32))")
    print("\n  THE DIFFERENTIAL AT 993 nm (the independent recompute):")
    b = mc_band(lambda k5, k6: _a6(k6, LAM_DRIVE_NM) - _a5(k5, LAM_DRIVE_NM))
    print(f"    Delta_alpha(993) = {da993:+.0f} au  [band {b['lo']:+.0f} .. {b['hi']:+.0f}]")
    # The label said Orson's while reading the record's own constant, and the
    # abs() numerator over a signed denominator printed -200% after the
    # 2026-08-24 sign adjudication. Both sides are magnitudes now.
    print(f"    |Delta_alpha| vs the package default {abs(DELTA_ALPHA_AU):.0f}: "
          f"{abs(da993) / abs(DELTA_ALPHA_AU) - 1.0:+.2%} -- magnitude CONFIRMED;")
    print("    the SIGN is opposite (alpha_6S(993) < 0: 6S pushed up, 5S down =>")
    print("    BLUE shift). Flagged for adjudication; archival results are")
    print("    sign-immune (they use |Delta_alpha|). See THEORY_NOTE section 5.")
    print("\n  DESIGN NUMBERS (unpublished; ENVELOPE):")
    print(f"    alpha_6S(1064) = {a6_1064:+.1f} au  (a 1064 trap arm is NOT line-neutral)")
    bands = {}
    for lam, aval in magic:
        wlo, whi = _cross_window(lam)

        def _cross(k5, k6, a=wlo, b=whi):
            return brentq(lambda x: _a6(k6, x) - _a5(k5, x), a, b, xtol=1e-5)
        bands[lam] = cb = mc_band(_cross)
        print(f"    MAGIC 5S-6S: {lam:8.2f} nm (alpha {aval:+.0f} au)  "
              f"[band {cb['lo']:.2f} .. {cb['hi']:.2f}; {cb['failed']} of "
              f"{cb['n'] + cb['failed']} draws left the window]")

    # every entry below is a 1500-draw 16-84% Monte-Carlo band now, so one
    # already-computed pair of columns carries all of them, not a substring
    # inside "unit" that only four of ten rows ever had.
    with open(C.RESULTS_DIR / "polarizability.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "err_lo16", "err_hi84", "unit",
                    "status"])
        w.writerow(["alpha_5s_static", "model", f"{a5s:.2f}",
                    f"{b_a5s['lo']:.2f}", f"{b_a5s['hi']:.2f}",
                    "au; validation vs measured 318.79(1.42) (Holmgren 2010)", "DIAGNOSTIC"])
        w.writerow(["alpha_6s_static", "model", f"{a6s:.1f}",
                    f"{b_a6s['lo']:.1f}", f"{b_a6s['hi']:.1f}",
                    "au; tail calibrated to the Safronova-group 5167(22)", "DIAGNOSTIC"])
        w.writerow(["tuneout_5s", "model", f"{t0:.4f}",
                    f"{b_t0['lo']:.4f}", f"{b_t0['hi']:.4f}",
                    "nm; validation vs measured 790.032326(32) "
                    "(Leonard 2015 as corrected by the 2017 erratum)", "DIAGNOSTIC"])
        # The two states SEPARATELY at 993 nm. These carry the sign argument:
        # 993 nm lies in the gap between the 6S->5P cascade (1324/1367 nm) and
        # the 5S D lines (780/795 nm), so it is BLUE of 6S's nearest strong
        # lines and RED of 5S's. Opposite detuning signs => opposite
        # polarizability signs => the difference cannot come out positive,
        # whatever the matrix elements do.
        w.writerow(["alpha_5s_993", "model", f"{alpha_5s(LAM_DRIVE_NM):.1f}",
                    f"{b_a5_993['lo']:.1f}", f"{b_a5_993['hi']:.1f}",
                    "au; POSITIVE -- 993 nm is red of the D1/D2 lines (795/780 nm)", "DIAGNOSTIC"])
        w.writerow(["alpha_6s_993", "model", f"{alpha_6s(LAM_DRIVE_NM):.1f}",
                    f"{b_a6_993['lo']:.1f}", f"{b_a6_993['hi']:.1f}",
                    "au; NEGATIVE -- 993 nm is blue of the 6S->5P cascade "
                    "(1324/1367 nm), the dominant 6S term", "DIAGNOSTIC"])
        # THE TAIL'S FREQUENCY DEPENDENCE, a ONE-SIDED systematic the
        # Monte-Carlo band cannot see. TAIL_6S stands for every 6S->nP state
        # above the explicit 8P list and is added as a CONSTANT, but the
        # drive at 993 nm sits inside that series, between 9P (922.7/923.7
        # nm) and 8P (1028.7/1030.7). Each omitted state therefore carries
        # dE > w and is enhanced by dE^2/(dE^2 - w^2) > 1, all of one sign,
        # so no cancellation is available. mc_band draws TAIL_6S's AMPLITUDE
        # and never its dispersion, which is why "tail uncertainties
        # propagated" overstated what was propagated.
        #
        # The enhancement runs 2.23 at the ionisation limit to 7.38 at 9P,
        # so the flat 3.4 should be 7.6 to 25.1, making delta_alpha LESS
        # negative by 4.2 to 21.7 a.u. Even the smallest correction reaches
        # the 16-84 band's own edge. RESOLVING IT NEEDS THE 6S->9P..12P
        # REDUCED MATRIX ELEMENTS, which no held paper carries: arora2012
        # was read for them on 2026-08-26 and tabulates only 6s-5p. Until
        # those exist the correction is stated as a range and not applied,
        # because choosing a weighting inside it would be inventing the data
        # that is missing.
        _w_cm = 1e7 / LAM_DRIVE_NM
        _enh = lambda e_cm: (e_cm - E_6S_CM) ** 2 / (
            (e_cm - E_6S_CM) ** 2 - _w_cm ** 2)
        _lo_corr = TAIL_6S * (_enh(33690.798) - 1.0)   # ionisation limit
        _hi_corr = TAIL_6S * (_enh(30958.91) - 1.0)    # 9P1/2, the nearest
        w.writerow(["delta_alpha_993_tail_dispersion", "systematic",
                    f"{_lo_corr:.1f}", f"{_lo_corr:.1f}", f"{_hi_corr:.1f}",
                    "au, ONE-SIDED and additive to delta_alpha_993, making it "
                    "less negative. The 6S tail is added flat while the drive "
                    "sits inside the 6S->nP series, so every omitted state is "
                    "enhanced and all of one sign. Range spans the ionisation "
                    "limit to 9P1/2. NOT APPLIED: needs the 6S->9P..12P "
                    "reduced matrix elements, which no held paper carries",
                    "ENVELOPE"])
        w.writerow(["delta_alpha_993", "model", f"{da993:.0f}",
                    f"{b['lo']:.0f}", f"{b['hi']:.0f}",
                    "au (alpha_6S - alpha_5S); |value| within ~5% of Orson "
                    "2021's 1093 but OPPOSITE sign (6S pushed up at 993 nm "
                    "=> blue shift) -- ADJUDICATED 2026-08-24 and now the package default, a decision on the theory and not a measurement, the sign being unset by experiment, archival results sign-immune. "
                    "One defect is open and it is the size of the band: the 6S line list stops at 8P where the 5S list runs to 12P, and the tail that stands in for the omitted states is calibrated at the static limit while the drive sits between 8P and 9P, where the first omitted term is enhanced sevenfold. See delta_alpha_993_tail_dispersion, which sizes it and is deliberately not applied", "DIAGNOSTIC"])
        w.writerow(["alpha_6s_1064", "model", f"{a6_1064:.1f}",
                    f"{b_a6_1064['lo']:.1f}", f"{b_a6_1064['hi']:.1f}",
                    "au; small and negative -- a 1064 nm trap arm adds nearly the "
                    "full alpha_5S(1064) ~ +687 au to the differential shift", "ENVELOPE"])
        for lam, aval in magic:
            cb = bands[lam]
            w.writerow(["magic_5s6s", f"{lam:.0f}nm", f"{lam:.2f}",
                        f"{cb['lo']:.2f}", f"{cb['hi']:.2f}",
                        f"nm; alpha there {aval:.0f} au (trapping both states); "
                        f"unpublished (searched 2026-07-17); scalar only -- "
                        f"vector shifts near the 6S-5P lines need their own "
                        f"treatment before a trap design", "ENVELOPE"])
    print("\n  Wrote results/polarizability.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

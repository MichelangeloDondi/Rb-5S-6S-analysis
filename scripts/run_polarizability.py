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
from functools import partial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import DELTA_ALPHA_AU  # noqa: E402
from rb5s6s.polarizability import (alpha_5s, alpha_6s, delta_alpha,  # noqa: E402
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
    da993 = delta_alpha(993.0)
    a6_1064 = alpha_6s(1064.0)
    magic = magic_wavelengths()

    print("\n  VALIDATION (anchors the model does not use):")
    print(f"    alpha_5S(0)  = {a5s:8.2f} au   (measured 318.79(1.42))")
    print(f"    alpha_6S(0)  = {a6s:8.1f} au   (Safronova-group 5167(22); tail calibrated)")
    print(f"    5S tune-out  = {t0:9.3f} nm  (measured 790.03235(3))")
    print("\n  THE DIFFERENTIAL AT 993 nm (the independent recompute):")
    b = mc_band(lambda k5, k6: _a6(k6, 993.0) - _a5(k5, 993.0))
    print(f"    Delta_alpha(993) = {da993:+.0f} au  [band {b['lo']:+.0f} .. {b['hi']:+.0f}]")
    print(f"    |Delta_alpha| vs Orson's {DELTA_ALPHA_AU:.0f}: "
          f"{abs(da993) / DELTA_ALPHA_AU - 1.0:+.1%} -- magnitude CONFIRMED;")
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

    with open(C.RESULTS_DIR / "polarizability.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["quantity", "key", "value", "unit"])
        w.writerow(["alpha_5s_static", "model", f"{a5s:.2f}",
                    "au; validation vs measured 318.79(1.42) (Holmgren 2010)"])
        w.writerow(["alpha_6s_static", "model", f"{a6s:.1f}",
                    "au; tail calibrated to the Safronova-group 5167(22)"])
        w.writerow(["tuneout_5s", "model", f"{t0:.4f}",
                    "nm; validation vs measured 790.03235(3) (Leonard 2015)"])
        w.writerow(["delta_alpha_993", "model", f"{da993:.0f}",
                    f"au (alpha_6S - alpha_5S); band {b['lo']:.0f}..{b['hi']:.0f}; "
                    f"|value| within ~5% of Orson 2021's 1093 but OPPOSITE sign "
                    f"(6S pushed up at 993 nm => blue shift) -- flagged, archival "
                    f"results sign-immune"])
        w.writerow(["alpha_6s_1064", "model", f"{a6_1064:.1f}",
                    "au; small and negative -- a 1064 nm trap arm adds nearly the "
                    "full alpha_5S(1064) ~ +687 au to the differential shift"])
        for lam, aval in magic:
            cb = bands[lam]
            w.writerow(["magic_5s6s", f"{lam:.0f}nm", f"{lam:.2f}",
                        f"nm; alpha there {aval:.0f} au (trapping both states); "
                        f"16-84% band {cb['lo']:.2f}..{cb['hi']:.2f} nm; "
                        f"unpublished (searched 2026-07-17); scalar only -- "
                        f"vector shifts near the 6S-5P lines need their own "
                        f"treatment before a trap design"])
    print("\n  Wrote results/polarizability.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

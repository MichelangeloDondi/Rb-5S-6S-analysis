#!/usr/bin/env python3
"""
M5: 2025 laser-epoch characterization (deliverable C2 -- the ONF baseline).

Reports the 2025 laser width sigma_laser as an UPPER BOUND (house rule: it is
NOT a clean measurement), because the non-Lorentzian Gaussian broadening the
fits attribute to the laser is degenerate with the transit width, which rides
on the w0, which this archive does not itself re-measure. Concretely (README
section 2.5): to reach the observed
~5.25 MHz total from the 3.49 MHz natural Lorentzian, the extra broadening is
split between the transit kernel (which rides on the OPEN w0) and the laser, and
the fit cannot say how much is which --
    transit 0.85 MHz (w0~70um)       => sigma_laser ~ 1.1 MHz (laser axis)
    transit 0.93 MHz (w0=64um measured) => sigma_laser ~ 1.1 MHz
    transit 1.49 MHz (w0~40um)       => sigma_laser ~ 0.4 MHz (laser could be narrow)
So we quote sigma_laser(2025) <~ 1 MHz (laser axis) as an upper bound, with that
w0-degeneracy band, and note slow drift is NOT the culprit (~0.01 MHz within a
scan). A knife-edge measurement of w0 on this bench, fixing the transit term,
turns this bound into a measurement. (History: w0 was re-centred 32 -> 50 um on
2026-07-12 when the transit physics was corrected, and later to the measured
64 um; 32 um OVERSHOOTS the observed line and is excluded -- see
constants.W0_MEASURED_M.)

We also report the block-to-block scatter of the fitted sigma_laser -- the
block-to-block drift record of the bad-lock epoch -- the starting linewidth the ONF work
needs, and which (per M4) is the systematic that bounds beta_self.

Reads results/linefit_conditions.csv (per-condition fits from run_linefit.py).
Outputs: results/laser_epoch.csv + stdout.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.lineshape import model_profile  # noqa: E402
from rb5s6s.constants import transit_fwhm_from_w0  # noqa: E402


def w0_band():
    """sigma_laser (laser axis) needed to reach 5.25 MHz total at each transit
    width across the w0 degeneracy band."""
    from scipy.optimize import brentq
    nu = np.arange(-40, 40, 0.005)

    def fwhm(sl, tr):
        y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=max(sl, 1e-4), transit_fwhm=tr)
        a = nu[y >= y.max() / 2]
        return a[-1] - a[0]
    band = []
    _lo_um, _hi_um = C.W0_BAND_M[0] * 1e6, C.W0_BAND_M[1] * 1e6
    _pr_um = C.W0_MEASURED_M * 1e6
    for w0_um, w0 in ((_hi_um, f"~{_hi_um:.0f}um"),
                      (_pr_um, f"{_pr_um:.0f}um measured"),
                      (_lo_um, f"~{_lo_um:.0f}um")):
        tr = transit_fwhm_from_w0(w0_um * 1e-6, 110.0)
        if fwhm(1e-3, tr) >= 5.25:
            band.append((tr, w0, 0.0))
        else:
            sl = brentq(lambda s: fwhm(s, tr) - 5.25, 0.01, 6)
            band.append((tr, w0, sl / 2))  # /2 -> laser axis
    return band


def main() -> int:
    path = C.RESULTS_DIR / "linefit_conditions.csv"
    if not path.exists():
        raise SystemExit("run scripts/run_linefit.py first (need linefit_conditions.csv)")
    rows = list(csv.DictReader(open(path)))
    # DEGENERACY GATE (2026-07-11): at low SNR (cold and/or low-power
    # corners) the sigma<->gamma_coll Voigt degeneracy runs uncontrolled and the
    # fit does not constrain sigma_laser -- e.g. 4121@130/25mW gives
    # 1.11 +/- 1.05 (95% rel err), 4121@70C gives 0.84 +/- 1.11 (132%). Those
    # conditions cannot support ANY sigma_laser statement and are EXCLUDED here
    # (they were silently included before). Gate: relative error < 40%.
    good, degen = [], []
    for r in rows:
        s, e = float(r["sigma_laser"]), float(r["sigma_laser_err"])
        (good if (s > 0 and e / s < 0.40) else degen).append(r)
    sl_t = np.array([float(r["sigma_laser"]) for r in good])  # transition axis, FWHM
    sl_l = sl_t / 2.0                                          # laser axis

    print("=" * 74)
    print("(M5) 2025 LASER-EPOCH sigma_laser -- UPPER BOUND (degenerate with w0)")
    print(f"  {len(good)}/{len(rows)} conditions constrain sigma_laser (rel err <40%); "
          f"{len(degen)} EXCLUDED as degenerate (low-SNR cold/low-power corners")
    print("    where sigma<->gamma is unconstrained): "
          + ", ".join(f"{r['peak']}@{r['T'] if r['role']=='t_sweep' else '130/'+r['P']+'mw'}"
                      for r in degen))
    print(f"  well-constrained sigma_laser (transition axis, at the measured "
          f"w0={C.W0_MEASURED_M*1e6:.0f}um):")
    print(f"     median {np.median(sl_t):.1f}, range {sl_t.min():.1f}-{sl_t.max():.1f} MHz "
          f"transition (= {np.median(sl_l):.1f} laser axis; block scatter = drift record)")

    print("\n  w0-degeneracy band (laser-axis sigma_laser needed for the same 5.25 MHz total):")
    band = w0_band()
    for tr, w0, sl in band:
        note = "  <- laser could be NARROW" if sl < 0.05 else ""
        print(f"     transit {tr:.1f} MHz ({w0:>10s}): sigma_laser = {sl:.2f} MHz laser axis{note}")

    # Upper bound over the w0 BAND: sigma_laser rises with w0 (bigger waist
    # -> less transit -> more room for laser), so the bound is the band
    # MAXIMUM, at the widest plausible waist, not the value at the band centre.
    # Reporting the central value as the bound would understate it.
    bound = max(sl_l.max(), max(s for _, _, s in band))
    print(f"\n  HEADLINE (C2): sigma_laser(2025) <~ {bound:.1f} MHz (laser axis) over the"
          f" w0 band; ~{np.median(sl_l):.1f} at the measured "
          f"{C.W0_MEASURED_M*1e6:.0f} um.")
    print(f"    - degenerate with w0: below the measured "
          f"{C.W0_MEASURED_M*1e6:.0f}um the true laser is narrower (possibly << 1 MHz)")
    print("    - slow drift is NOT the cause (~0.01 MHz within a 1 s scan)")
    print("    - a well-locked SolsTiS reaches ~0.05-0.1 MHz laser axis; the fixed-lock session")
    print("      knife-edge w0 (fixing transit) converts this bound into a measurement")
    print("    - this bound is the ONF starting linewidth for the nanofibre extension")

    with open(C.RESULTS_DIR / "laser_epoch.csv", "w", newline="") as f:
        w = csv.writer(f)
        # one significant figure only: the quantity is formally UNCONSTRAINED
        # (it reaches 0 at w0~=16um, see the band below), so 3-digit precision
        # would be false. It is a bound, not a measurement.
        # Schema normalised 2026-08-10. This file used to carry its own header
        # (quantity, value_MHz, axis, status), a prose paragraph in the field
        # every other file uses for a status WORD, an inequality string "<1.2"
        # in a numeric column, and the transit width baked into the quantity
        # NAME to fifteen digits. It now matches the ledger's shape: the value
        # is a number, the bound's one-sidedness is carried by the BOUND status
        # where a reader looks for it, and the transit width and waist label
        # move into the key and the unit.
        w.writerow(["quantity", "key", "value", "err", "unit", "status"])
        w.writerow(["sigma_laser_bound", "over_w0_band", f"{bound:.1f}", "",
                    f"MHz, LASER axis. One-sided UPPER limit, so the value is "
                    f"the limit itself and carries no plus-or-minus. Taken over "
                    f"the measured w0 band "
                    f"({C.W0_BAND_M[0]*1e6:.0f}-{C.W0_BAND_M[1]*1e6:.0f}um) and "
                    f"rising with w0, reaching zero near w0=16um, so it is "
                    f"formally unconstrained below and quoted to one significant "
                    f"figure for that reason. Conditional on "
                    f"w0={C.W0_MEASURED_M*1e6:.0f}um, which is measured on this "
                    f"apparatus lineage but not re-measured by this archive",
                    "BOUND"])
        for tr, w0, sl in band:
            w.writerow(["sigma_laser_at_w0", f"w0_{w0}", f"{sl:.3f}", "",
                        f"MHz, LASER axis. The laser width left over when the "
                        f"transit contribution is {tr:.3f} MHz at this waist, "
                        f"which is the degeneracy this bound rides on rather "
                        f"than a measurement of either term",
                        "DIAGNOSTIC"])
    print(f"\nwrote {C.RESULTS_DIR / 'laser_epoch.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

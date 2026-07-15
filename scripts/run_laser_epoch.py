#!/usr/bin/env python3
"""
M5: 2025 laser-epoch characterization (deliverable C2 -- the ONF baseline).

Reports the 2025 laser width sigma_laser as an UPPER BOUND (house rule: it is
NOT a clean measurement), because the non-Lorentzian Gaussian broadening the
fits attribute to the laser is degenerate with the transit width, which rides
on the OPEN w0 prior. Concretely (README section 2.5): to reach the observed
~5.25 MHz total from the 3.49 MHz natural Lorentzian, the extra broadening is
split between the transit kernel (which rides on the OPEN w0) and the laser, and
the fit cannot say how much is which --
    transit 0.92 MHz (w0~65um)       => sigma_laser ~ 1.1 MHz (laser axis)
    transit 1.20 MHz (w0=50um prior) => sigma_laser ~ 0.8 MHz
    transit 1.49 MHz (w0~40um)       => sigma_laser ~ 0.4 MHz (laser could be narrow)
So we quote sigma_laser(2025) <~ 1 MHz (laser axis) as an upper bound, with that
w0-degeneracy band, and note slow drift is NOT the culprit (~0.01 MHz within a
scan). The knife-edge measurement w0 turns this bound into a measurement. (w0 was
re-centred 32 -> 50 um 2026-07-12 when the transit physics was corrected; 32 um
now OVERSHOOTS the observed line and is excluded -- see constants.W0_PRIOR_M.)

We also report the block-to-block scatter of the fitted sigma_laser -- the
"drift diary" of the bad-lock epoch -- which is what Zohreh needs as the ONF
starting linewidth, and which (per M4) is the systematic that bounds beta_self.

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
    prior -- the honest degeneracy band."""
    from scipy.optimize import brentq
    nu = np.arange(-40, 40, 0.005)

    def fwhm(sl, tr):
        y = model_profile(nu, gamma_coll=0.0, sigma_laser_fwhm=max(sl, 1e-4), transit_fwhm=tr)
        a = nu[y >= y.max() / 2]
        return a[-1] - a[0]
    band = []
    for w0_um, w0 in ((65.0, "~65um"), (50.0, "50um prior"), (40.0, "~40um")):
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
    print(f"    where sigma<->gamma is unconstrained): "
          + ", ".join(f"{r['peak']}@{r['T'] if r['role']=='t_sweep' else '130/'+r['P']+'mw'}"
                      for r in degen))
    print(f"  well-constrained sigma_laser (transition axis, at the w0=50um prior):")
    print(f"     median {np.median(sl_t):.1f}, range {sl_t.min():.1f}-{sl_t.max():.1f} MHz "
          f"transition (= {np.median(sl_l):.1f} laser axis; block scatter = drift diary)")

    print(f"\n  w0-degeneracy band (laser-axis sigma_laser needed for the same 5.25 MHz total):")
    band = w0_band()
    for tr, w0, sl in band:
        note = "  <- laser could be NARROW" if sl < 0.05 else ""
        print(f"     transit {tr:.1f} MHz ({w0:>10s}): sigma_laser = {sl:.2f} MHz laser axis{note}")

    print(f"\n  HEADLINE (C2): sigma_laser(2025) <~ {sl_l.max():.1f} MHz (laser axis), UPPER BOUND.")
    print("    - degenerate with w0: if w0 < 50um the true laser is narrower (possibly << 1 MHz)")
    print("    - slow drift is NOT the cause (~0.01 MHz within a 1 s scan)")
    print("    - a well-locked SolsTiS reaches ~0.05-0.1 MHz laser axis; the fixed-lock session")
    print("      knife-edge w0 (fixing transit) converts this bound into a measurement")
    print("    - this bound is the ONF starting linewidth for Paper 2")

    with open(C.RESULTS_DIR / "laser_epoch.csv", "w", newline="") as f:
        w = csv.writer(f)
        # one significant figure only: the quantity is formally UNCONSTRAINED
        # (it reaches 0 at w0~=16um, see the band below), so 3-digit precision
        # would be false. It is a bound, not a measurement.
        w.writerow(["quantity", "value_MHz", "axis", "status"])
        w.writerow(["sigma_laser_bound", f"<{sl_l.max():.1f}", "laser",
                    "UPPER_BOUND@w0prior; =0 at w0~16um; unmeasurable pending knife-edge"])
        for tr, w0, sl in band:
            w.writerow([f"sigma_laser_at_transit_{tr}", f"{sl:.3f}", "laser", f"w0_{w0}"])
    print(f"\nwrote {C.RESULTS_DIR / 'laser_epoch.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""What the committed widths say about a polarisation-opened magnetic term.

THE MECHANISM, AND ITS RETRACTION. This producer was written for a channel
that is not open. A DIFFERENCE between the two beams, from birefringent
windows or a mirror off normal, was thought to open a rank-1 coupling and
make Delta m_F = +-1 weakly allowed. It does not. Both photons are drawn
from ONE laser, so the two time orderings share a single energy denominator,
the two-photon amplitude is symmetric under exchanging the two polarisation
vectors, and rank 1 is exactly the antisymmetric part a symmetric bilinear
cannot carry. The retraction is argued in rb5s6s/polarisation.py and in
docs/wiki/magnetic-sublevels.md, both 2026-08-20.

WHAT THE BOUND STILL CONSTRAINS. The comparison below never depended on
which mechanism opens the satellite, only on the satellite carrying an
uncancelled g_F, so it survives the retraction as a bound on ANY g_F-scaling
term. One such term is open. A two-atom cooperative channel puts a satellite
at 2 g_F mu_B B, the Delta m_F = +-2 position, because a PAIR can accept the
two units of angular momentum a single J=1/2 atom must refuse
(rb5s6s/cooperative.py). It sits ten orders below the main line, so what
follows is a ceiling on it rather than a measurement of it.

THE TEST THE ATOM SUPPLIES. The broadening from a weak satellite pair goes as
the square of its offset, so it scales as g_F squared. For an S1/2 state
g_F is g_J/(2I+1) up to sign, one half for rubidium-87 and one third for
rubidium-85, so the term must appear 2.25 times larger on the 87 lines than
on the 85 lines AT THE SAME field, power and temperature. That ratio is
fixed by atomic structure and by nothing else, which is what makes it a
discriminant rather than a fit.

WHAT THIS PRODUCER DOES AND DOES NOT GIVE. It compares the committed
per-condition widths of the two isotopes and turns the difference into a
bound on the mechanism. It cannot MEASURE the mechanism, because any other
effect that differs between isotopes lands in the same difference: the mass
ratio through the transit width, the abundance through the optical depth, the
hyperfine structure through the pumping. The bound is therefore conservative
by construction, and it is the first bound this record has carried on this
term at all.

    python scripts/run_polarisation_bound.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s.cascade import DRIVEN_F                       # noqa: E402
from rb5s6s.polarisation import (GF_S_HALF, extra_width_mhz,  # noqa: E402
                                 vector_ratio,
                                 vector_spread_mhz)

FWHM_NOMINAL = 5.37


def _s0_225():
    """The two differential scalar shifts the record carries at 225 mW, each
    read from the file that owns it rather than hard-coded.

    THEY ARE DIFFERENT STATEMENTS and this producer used to conflate them. The
    CALIBRATED PREDICTION is what the light shift is expected to be. The 95 per
    cent UPPER BOUND is what the widths permit, and it happens to sit BELOW the
    prediction. A systematic has to be sized against the larger of the two, so
    the prediction is the headline here and the bound is carried beside it.

    THEY COME FROM DIFFERENT FILES, and that is the 2026-09-04 repair. Both
    used to be read from results/stark_joint.csv, which the freshness check
    exempts because its producer needs an excluded trace tree and about five
    hours. That reason covers the bound, which the traces determine. It does
    not cover the prediction, which is computed from constants alone, and that
    row still stands at the polarizability this record retired on 2026-08-25:
    0.348 MHz where the adopted value gives 0.364. Sizing a systematic against
    the smaller number understated it by 4.8 per cent, in the flattering
    direction. The prediction now comes from results/stark_sweep.csv, which IS
    in the checked set and carries the current value. The bound stays in the
    joint file, because the sweep's row of that name is a replaced diagnostic
    of a different construction and reads 2.205.
    """
    import csv as _csv
    def _row(fname, key):
        src = REPO / "results" / fname
        with open(src) as fh:
            for r in _csv.DictReader(fh):
                if r["quantity"] == key:
                    return float(r["value"])
        raise KeyError(f"{fname} is missing {key!r}, so the vector spread "
                       f"cannot be sized against a named shift")
    return _row("stark_sweep.csv", "S0_225mW_pred"), _row("stark_joint.csv", "S0_225mW_ub95")


def _weighted(vals, errs):
    w = 1.0 / np.asarray(errs) ** 2
    return float(np.sum(np.asarray(vals) * w) / np.sum(w)), float(np.sqrt(1.0 / np.sum(w)))


def main() -> int:
    src = REPO / "results" / "linefit_conditions.csv"
    rows = [r for r in csv.DictReader(open(src))
            if r.get("total_fwhm") and r.get("total_fwhm_err")
            and r["peak"] in DRIVEN_F]
    if not rows:
        print("no usable rows in results/linefit_conditions.csv")
        return 1

    out = [["quantity", "key", "value", "err", "unit", "status"]]
    per_iso = {}
    for r in rows:
        iso, _ = DRIVEN_F[r["peak"]]
        per_iso.setdefault(iso, ([], []))
        per_iso[iso][0].append(float(r["total_fwhm"]))
        per_iso[iso][1].append(float(r["total_fwhm_err"]))

    means = {}
    for iso, (v, e) in sorted(per_iso.items()):
        m, s = _weighted(v, e)
        means[iso] = (m, s)
        print(f"  {iso}: mean FWHM {m:.4f} +/- {s:.4f} MHz over {len(v)} conditions")
        out.append(["mean_fwhm", iso, f"{m:.4f}", f"{s:.4f}",
                    "MHz, inverse-variance mean of the committed per-condition "
                    "widths for this isotope's two lines", "DIAGNOSTIC"])

    (m87, s87), (m85, s85) = means["87Rb"], means["85Rb"]
    d, de = m87 - m85, float(np.hypot(s87, s85))
    print(f"\n  isotope difference {d*1e3:+.1f} +/- {de*1e3:.1f} kHz "
          f"({abs(d)/de:.1f} sigma)")
    out.append(["isotope_width_difference", "87 minus 85", f"{d:.5f}", f"{de:.5f}",
                "MHz. A Delta m_F = +-1 term would appear here scaled by "
                "g_F squared, 2.25 times larger on 87 than on 85", "DIAGNOSTIC"])

    # The 87 term's own size, from the difference and the fixed 2.25 ratio.
    contrast = 1.0 - (GF_S_HALF["85Rb"] / GF_S_HALF["87Rb"]) ** 2
    lim95 = (abs(d) + 1.96 * de) / contrast
    print(f"  the g_F-squared contrast is {contrast:.3f}, so the 87Rb term is "
          f"under {lim95*1e3:.0f} kHz at 95 per cent")
    out.append(["dmf1_broadening_ub95", "87Rb", f"{lim95:.5f}", "",
                "MHz, 95 per cent upper limit on any g_F-squared-scaling "
                "broadening of the rubidium-87 lines, from the isotope "
                "difference alone. CONSERVATIVE: every other isotope-dependent "
                "effect is absorbed into the same difference", "BOUND"])

    # What that limit permits, as a field-and-mismatch curve.
    print("\n  what the limit permits, as (field, mismatch) pairs:")
    for b in (50.0, 100.0, 200.0, 500.0):
        lo, hi = 0.0, 89.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if extra_width_mhz("87Rb", b, mid, FWHM_NOMINAL) < lim95:
                lo = mid
            else:
                hi = mid
        print(f"    B = {b:5.0f} uT: mismatch angles up to {lo:4.1f} deg are allowed")
        out.append(["mismatch_ub95_at_field", f"{b:.0f}uT", f"{lo:.2f}", "",
                    "degrees. RETRACTED CHANNEL, kept as the historical form "
                    "of the constraint: a forward-to-retro mismatch does not "
                    "open Delta m_F = +-1, because the two-photon amplitude is "
                    "symmetric in the two beams for photons from one laser, so "
                    "rank 1 is absent. The arithmetic is correct and the "
                    "question does not arise", "ARTIFACT"])

    # Route 1, for contrast: the vector light shift, which ellipticity DOES
    # produce directly and which is far too small to see.
    vr = vector_ratio()
    s0_pred, s0_bound = _s0_225()
    vs = vector_spread_mhz(s0_pred, 1.0)
    vs_bound = vector_spread_mhz(s0_bound, 1.0)
    print("\n  for contrast, the vector light shift ellipticity does produce:")
    print(f"    |d alpha_v / d alpha_s| = {vr:.5f}")
    print(f"    spread {vs*1e3:.2f} kHz on the prediction S0 = {s0_pred:.3f} MHz")
    print(f"    spread {vs_bound*1e3:.2f} kHz on the bound S0 = {s0_bound:.3f} MHz")
    out.append(["vector_ratio", "993.4nm", f"{vr:.5f}", "",
                "|differential vector over differential scalar polarizability| "
                "from the committed line lists", "DIAGNOSTIC"])
    out.append(["vector_spread_at_225mW_pred", "fully circular",
                f"{vs:.5f}", "",
                f"MHz, the m_F spread the vector light shift opens at 225 mW "
                f"for fully circular light, sized against the PREDICTED "
                f"S0_225mW_pred = {s0_pred:.3f} MHz, an ENVELOPE conditional "
                f"on a waist not measured in the cell and on an assumed "
                f"retro ratio. This is the headline, because a systematic is "
                f"sized against the larger of the two available shifts",
                "DIAGNOSTIC"])
    out.append(["vector_spread_at_225mW_bound", "fully circular",
                f"{vs_bound:.5f}", "",
                f"MHz, the same spread sized against the 95 per cent upper "
                f"BOUND S0_225mW_ub95 = {s0_bound:.3f} MHz instead. Carried "
                f"because the bound sits BELOW the prediction, so quoting it "
                f"understates the systematic by a third", "DIAGNOSTIC"])
    out.append(["vector_centre_shift_per_projection", "87Rb",
                f"{vs / 4.0:.5f}", "",
                "MHz per unit of mean population projection, at 225 mW and "
                "full circularity. The spread divided by 2F, since the shift "
                "is odd in m_F and cancels in the mean over a symmetric "
                "population", "DIAGNOSTIC"])
    out.append(["vector_centre_shift_per_projection", "85Rb",
                f"{vs / 6.0:.5f}", "",
                "MHz per unit of mean population projection, at 225 mW and "
                "full circularity. The isotope contrast is the discriminant, "
                "since the per-unit shift differs by the ratio of 2F",
                "DIAGNOSTIC"])

    dst = REPO / "results" / "polarisation_bound.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh).writerows(out)
    print(f"\nwrote {dst.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

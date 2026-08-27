#!/usr/bin/env python3
"""
The collisional (pressure) shift: the borrowed bound, and what this atom expects
===============================================================================

Writes `results/collisional_shift_bound.csv`. The lineshape carries a
collisional WIDTH and no collisional SHIFT term, and collisions do both, so
the absence has to be given a number. This producer computes that number
from the record's own vapour-pressure chain instead of from hand arithmetic
in prose.

WHY THIS EXISTS, and it is worth stating because the file is small. Every
figure it emits was previously a digit typed into `docs/UNCERTAINTY.md` and
`docs/lit/rahaman2022.md`. On 2026-08-26 the five-seat board recomputed
them and four were wrong or unwarranted in the same paragraph pair:

  * a differential quoted "across this campaign's range" was arithmetically
    the 110-130 C span, three sentences after the text insisted on the
    four-point 70/90/110/130 grid -- the identical frame error the board had
    just corrected in the paragraph above, re-authored one paragraph down;
  * `rb5s6s/density.py` mandates in its own docstring that consumers
    "multiply their quoted upper bounds by (1 + N_SCALE_FRAC_SYST)" for the
    spread between published vapour-pressure correlations, and the table
    applied no inflation, in the section whose subject is what is not
    covered;
  * a borrowed genus-level CEILING was set beside a central EXTRAPOLATION
    for this atom and the coincidence read as two routes agreeing, when two
    numbers of equal size, one a ceiling and one an expectation, say the
    ceiling is SATURATED;
  * and the two "independent" routes both run through Zameroski 2014.

A producer answers three of those four by construction. The temperature
range becomes an argument, so it cannot silently be a different range from
the one the prose claims. The density systematic becomes a line of code
rather than a step someone remembers. And once the expectation is a ROW
beside the bound row, the saturation is visible on the page instead of
being something a reader has to derive. The fourth, the shared provenance,
is a fact about the sources and is stated in the notes.

AXIS. Every frequency here is on the TRANSITION axis, which is twice the
laser axis. That is not an inference from the arithmetic -- a multiplication
inherits the axis of its input rate, so the warrant has to come from the
source. It does: Zameroski 2014's INTRODUCTION states "We define nu = 2 nu_L", and
its fitting-method paragraph, before section 2.2, states that the rates
"are reported with respect to the atomic frequency (nu = 2 nu_L) and not
laser frequency". Both placements were read off the page after a first
draft of this comment put them in the wrong sections twice, in a file whose
own headline repair was a wrongly cited section number. Also,
this record's own `docs/lit/zameroski2014.md` carries the restatement of
Morzynski's laser-axis figure onto that axis. The unit field of every row
below says the axis, because the one comparison in this family that went
wrong went wrong by mixing them.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import density as D  # noqa: E402
from rb5s6s import vanderwaals as V  # noqa: E402

# The campaign's own four-point set point grid. An argument, not a sentence:
# the defect this producer answers was a differential computed over a subset
# of this grid while the prose named the whole of it.
GRID_C = (70.0, 90.0, 110.0, 130.0)

# Orson 2021 section 3 bounds the 5S-6S density shift, which it records as
# never having been measured, from other Rb and Cs transitions. The figure is
# theirs by citation and Zameroski 2014's by measurement: their reference [25]
# is Zameroski, and the ceiling is set by Zameroski's 5S-5D5/2 self-shift of
# -27 +/- 2 kHz/mTorr. So this is a GENUS-level limit, not a measurement of
# this line, and it is not independent of the expectation below.
ORSON_BOUND_MHZ_PER_TORR = 30.0

# The shift-to-broadening ratio, measured twice in the held literature and
# agreeing: Zameroski 2014 section 2.2 gives the 85Rb 5S-5D5/2 self pair as
# -27(2) over 79(4) kHz/mTorr, and Rahaman 2022 gives the Cs 6S-7D3/2 pair as
# -1.38 over 4.18 kHz per 1e12 cm^-3. Both are -0.33 of the FWHM.
#
# REFERRED TO FWHM, and the normalisation is the trap. -0.33 of FWHM is the
# same quantity as -0.66 of HWHM; a sentence in this record compared the
# first against a classical HWHM-referred value and read the factor of two as
# a physical discrepancy. The classical Lindholm-Foley value for a -C6/R^6
# potential is about -0.73 of HWHM, i.e. -0.36 of FWHM, so measurement and
# theory agree to about ten per cent rather than differing by two.
SHIFT_TO_WIDTH_FWHM = -0.33


def _rows():
    f = D.N_SCALE_FRAC_SYST
    bounds, expects = {}, {}

    # beta_self(6S) per density, anchored ONCE at Zameroski's own cell
    # temperature (393 K, their stated conversion point), because the T
    # argument of beta_self_anchored only converts their per-mTorr rate to a
    # per-density rate through the ideal gas law. A first draft called that
    # argument a mean-relative-speed dependence and re-anchored per grid
    # point, which applied an exponent of 1.0 in T where impact theory
    # (gamma proportional to n v^0.6) gives 0.3. The speed factor is applied
    # explicitly below instead, and it is small: 0.96 at 70 C.
    ZAMEROSKI_T_K = 393.15
    beta6_anchor = V.beta_self_anchored(T_K=ZAMEROSKI_T_K)["beta6_khz"]
    raws = {}
    for T in GRID_C:
        p_torr = D.vapor_pressure_torr(T)
        raws[T] = ORSON_BOUND_MHZ_PER_TORR * p_torr
        bounds[T] = raws[T] * (1.0 + f)
        speed = ((T + 273.15) / ZAMEROSKI_T_K) ** 0.3
        n12 = D.number_density_cm3(T) / 1e12
        expects[T] = SHIFT_TO_WIDTH_FWHM * beta6_anchor * speed * n12 / 1e3

    for T in GRID_C:
        yield ["bound", f"shift_bound_{int(T)}C", f"{bounds[T]:.5f}",
               "MHz, transition axis",
               f"vapour pressure {D.vapor_pressure_torr(T):.3e} Torr times the "
               f"borrowed {ORSON_BOUND_MHZ_PER_TORR:g} MHz/Torr ceiling, "
               f"inflated by (1 + {f:g}) for the spread between published "
               f"vapour-pressure correlations as density.py mandates. A "
               f"genus-level limit borrowed from other transitions, not a "
               f"measurement of this line", "BOUND"]

    lo, hi = min(bounds.values()), max(bounds.values())
    yield ["bound", "shift_bound_differential", f"{hi - lo:.5f}",
           "MHz, transition axis",
           f"across the campaign's own grid, {'/'.join(str(int(t)) for t in GRID_C)} C. "
           f"The spread of the borrowed bound over the sweep, quoted beside "
           f"the absolute bound because it is the smaller scale. It is NOT "
           f"the width bias, and the mechanism this note used to give for "
           f"that was withdrawn 2026-08-27: beta.py floats a centre PER "
           f"TRACE, and density is constant within a trace at a fixed set "
           f"point, so a collisional shift is absorbed whether or not it "
           f"varies across the sweep. Both figures are ceilings on a channel "
           f"the forward model does not carry", "BOUND"]

    for T in GRID_C:
        yield ["expectation", f"shift_expected_{int(T)}C", f"{expects[T]:.5f}",
               "MHz, transition axis",
               f"the shift this atom is EXPECTED to have, not a bound: "
               f"beta_self(6S) anchored ONCE at 120 C, with the impact-theory "
               f"speed factor (T/393.15)**0.3 applied separately rather than "
               f"re-anchored per grid point, times the measured "
               f"shift-to-width ratio {SHIFT_TO_WIDTH_FWHM:g} of FWHM. Negative "
               f"because a van der Waals interaction shifts the line red. "
               f"Anchored on Zameroski's 7S rate, so it is NOT independent of "
               f"the bound above", "ENVELOPE"]

    elo, ehi = min(expects.values()), max(expects.values())
    e_diff = abs(ehi - elo)
    yield ["expectation", "shift_expected_differential", f"{e_diff:.5f}",
           "MHz, transition axis",
           "the expected differential across the same grid, the quantity to "
           "compare against shift_bound_differential", "ENVELOPE"]

    raw_lo, raw_hi = min(raws.values()), max(raws.values())
    yield ["expectation", "expectation_over_bound",
           f"{e_diff / (raw_hi - raw_lo):.3f}",
           "dimensionless",
           "how much of the borrowed ceiling the record's own expectation "
           "uses, computed raw against raw: both scale with the same vapour "
           "density, so the density-scale systematic is common-mode and "
           "cancels in the ratio. A first draft divided the central "
           "expectation by the INFLATED ceiling, 0.73, understating the "
           "saturation. Near 1 means the ceiling is nearly used up by the "
           "expectation, so the two agreeing in size is one route reaching "
           "its own limit, not two routes corroborating", "DIAGNOSTIC"]

    # Orson's own null, converted to the same units as the bound above, so a
    # comparison against it stops being hand arithmetic in prose. Their search
    # resolution is 6 MHz on the LASER axis, hence 12 on the transition axis,
    # over the density span their abstract states.
    orson_span_cm3 = 5e13 - 3e11
    yield ["comparison", "orson_null_as_shift_rate",
           f"{2 * 6.0 / (orson_span_cm3 / 1e12):.4f}",
           "MHz per 1e12 cm^-3, transition axis",
           "Orson 2021's density-shift null read as a rate: twice their 6 MHz "
           "one-photon resolution, over the 3e11 to 5e13 cm^-3 span their "
           "abstract states. It bounds a SHIFT and this record's neighbouring "
           "column bounds a WIDTH, so the two are not the same quantity. The "
           "row exists because a table cell compared them and called the gap "
           "three orders of magnitude when the like-for-like figure is the "
           "orson_density_null_over_implied row below, about 24. An "
           "intermediate draft of that correction said five to eight",
           "BOUND"]

    # The width column converted to the SHIFT it implies, through the
    # measured shift-to-width ratio, so the comparison against Orson's
    # density null stops being a width set beside a shift. Read from the
    # committed pooled bound rather than typed.
    pooled = _pooled_width_bound()
    if pooled is not None:
        implied = abs(SHIFT_TO_WIDTH_FWHM) * pooled
        yield ["comparison", "width_bound_as_shift_rate", f"{implied:.4f}",
               "MHz per 1e12 cm^-3, transition axis",
               f"the pooled self-broadening bound {pooled:g} times the "
               f"measured shift-to-width ratio {abs(SHIFT_TO_WIDTH_FWHM):g}: "
               f"the shift rate this record's width channel implies, at the "
               f"same 95 per cent as the width bound it derives from. The "
               f"per-peak bounds up to 0.05 imply up to 0.017", "BOUND"]
        orson_rate = 2 * 6.0 / ((5e13 - 3e11) / 1e12)
        yield ["comparison", "orson_density_null_over_implied",
               f"{orson_rate / implied:.1f}", "dimensionless",
               "Orson's density null as a shift rate over the implied shift "
               "bound above, now the same quantity on both sides. Their "
               "figure is a ONE SIGMA resolution (their section 2 defines "
               "every quoted resolution as one sigma) against this record's "
               "95 per cent, so the gap grows once the levels are matched",
               "DIAGNOSTIC"]

    s0 = _light_shift_comparator()
    if s0 is not None:
        yield ["comparison", "light_shift_bound_comparator", f"{s0:.4f}",
               "MHz, transition axis",
               "read from results/stark_joint.csv S0_225mW_ub95, the joint "
               "three-session 95 per cent bound at the campaign's maximum "
               "power. Read rather than typed, so this row cannot drift from "
               "the bound it compares against", "BOUND"]
        yield ["comparison", "light_shift_over_collisional", f"{s0 / (hi - lo):.2f}",
               "dimensionless",
               "how much larger the light-shift bound is than the collisional "
               "differential, both on the transition axis. The collisional "
               "shift is not separable from zero by this dataset. NOTE that "
               "the numerator would TIGHTEN under the saturation companion, "
               "which is measured but uncommitted for the four reasons "
               "results/saturation_companion.csv states, so this ratio is "
               "computed on the committed bound and is the loose one",
               "DIAGNOSTIC"]


def _pooled_width_bound():
    """The pooled self-broadening bound, read from its own file."""
    path = C.RESULTS_DIR / "beta_self_probe.csv"
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            # wide table: one row per peak, the pooled construction in the
            # `peak` column, and the density-scale-inflated bound in its own
            # named column
            if (row.get("peak") or "").strip() == "pooled_slope":
                try:
                    return float(row["bound95_nscale"])
                except (TypeError, ValueError, KeyError):
                    return None
    return None


def _light_shift_comparator():
    """The light-shift bound, READ from its own file rather than typed here."""
    path = C.RESULTS_DIR / "stark_joint.csv"
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("quantity") == "S0_225mW_ub95":
                return float(row["value"])
    return None


def main():
    out = C.RESULTS_DIR / "collisional_shift_bound.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "quantity", "value", "unit", "note", "status"])
        for row in _rows():
            w.writerow(row)
    print(f"wrote {out}")
    for row in _rows():
        print(f"  {row[0]:12s} {row[1]:34s} {row[2]:>10s}  {row[3]}")


if __name__ == "__main__":
    main()

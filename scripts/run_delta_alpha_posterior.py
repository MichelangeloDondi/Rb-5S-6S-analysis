#!/usr/bin/env python3
"""
What this dataset says about the differential polarizability, and how much of
that answer is the choice of construction
=========================================

Writes `results/delta_alpha_posterior.csv`. The record computes Delta_alpha
from atomic structure and compares the light shift that implies against a
bound. This producer runs the comparison the other way round: it takes the
geometry as a stated input and asks what the DATA alone say about
|Delta_alpha|.

WHY THIS EXISTS. On 2026-08-27 the owner asked for the result "with its own
uncertainty". The answer was computed in a chat message and propagated
toward eight reader-facing surfaces with no committed row behind it, which
is the rule this same session had just written about to break on the most
consequential number in the record. So the number gets a producer.

WHAT THE FIRST VERSION OF THIS FILE GOT WRONG, kept here because the defect
is the reason for the present design. It reconstructed the kappa profile as
a truncated Gaussian whose width was solved so that the reconstruction's
POSTERIOR 95th percentile reproduced the committed kappa_ub95. But the
committed kappa_ub95 is not a posterior percentile: `run_stark_joint.ub95`
reads it off the Delta_chi2 = 2.706 crossing. Calibrating one construction
to reproduce the other forced the width to 0.494 where the committed
profile's own curvature implies about 0.72, and every derived number came
out 1.46 times too sharp. The present version uses the committed profile
DIRECTLY and reconstructs nothing.

WHAT IT RETURNS, and the three are different objects:

  * a POINT value, which the committed grid does not resolve. The profile is
    stored on a kappa grid of step 0.25, one step is 182 a.u., and
    Delta_chi2 at kappa = 0 is 0.12, which is smaller than the profile's own
    point-to-point numerical scatter. There is no detection here to quote a
    central value for, and the row says so;
  * the committed LIMIT transferred through the geometry, which is the
    record's own construction and therefore the quoted one;
  * the same committed profile read as a POSTERIOR with a flat prior on
    kappa >= 0. It gives a limit about 23 per cent higher, and the row
    decomposes that: a Gaussian carrying this profile's own curvature already
    separates the two constructions by 1.104 with no shape involved, because
    a one-sided crossing and a posterior quantile answer different questions.
    Only the residual is shape, and it lives at the SHOULDER near kappa 1 to
    2. A first version of this file said "flatter near zero", which is the
    wrong region and the wrong cause: below kappa = 1 the profile and its
    fitted Gaussian agree to within the profile's own numerical scatter, so
    the core carries none of the effect either way.

**That spread is why no significance is quoted to three digits.** It is not
by itself a reason the prediction is unexcluded: both limits still sit below
the computed value, and what falsifies the exclusion is its subset
dependence, the drop-4192 arm crossing above the prediction.

WHAT IT IS CONDITIONAL ON, stated here because the rows cannot carry it:

  1. THE COMPANIONS. The AC-Stark ramp, atomic saturation and hyperfine
     pumping all broaden as the square of the power and all scale as the
     inverse fourth power of the waist, so the fit cannot separate them and
     attributes every P-squared growth it sees to kappa. The limit therefore
     bounds their SUM. Note the DIRECTION, which is easy to get backwards:
     as a constraint on the ramp alone the limit is conservative, so the
     companions make the gap against the prediction harder to explain, not
     easier.
  2. THE GEOMETRY. w0 is not measured in the cell, and `constants.py` calls
     the retro ratio an assumption rather than a measurement. Both enter as
     stated priors, and the budget rows below give their size.
  3. THE SIGN. The width channel is sensitive to |Delta_alpha| only. No sign
     is set by these data.
"""

import csv
import sys
from pathlib import Path

import numpy as np
from math import erfc, sqrt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import constants as K  # noqa: E402
from rb5s6s.lineshape import aperture_spread_factor, stark_shift_S0_mhz  # noqa: E402

# The owner's stated priors, 2026-08-27, RE-CENTRED 2026-09-21 (O44/F280) on the bore-limited
# central value: W0_PRIOR_M now tracks constants.W0_CENTRAL_M directly rather than duplicating
# its number, closing the "name-vs-truth" gap the previous literal-plus-comment form carried
# (private/cache/plan_2026-09-18/RETIRE_64UM_INVENTORY.md Section 2). W0_PRIOR_ERR_M's 3 um width
# was sized around the retired lineage convention's own provenance and is NOT re-derived here --
# that is a physics judgement about how confidently this bore-limited value transfers, owed to the
# wave that regenerates delta_alpha_posterior.csv, not a mechanical substitution.
W0_PRIOR_M, W0_PRIOR_ERR_M = K.W0_CENTRAL_M, 3e-6
RHO_PRIOR, RHO_PRIOR_ERR = 0.94, 0.04
W0_PINNED_M = K.W0_CENTRAL_M
P_REF_W = 0.225                      # the campaign's maximum power
N_DRAW = 200_000
SEED = 20260827


def _joint() -> tuple[dict, np.ndarray, np.ndarray]:
    """The committed rows, and the committed profile as (kappa, Delta_chi2)."""
    with (C.RESULTS_DIR / "stark_joint.csv").open(newline="",
                                                  encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    named = {r["quantity"]: r for r in rows if r["quantity"] != "profile_point"}
    pts = sorted((float(r["key"]), float(r["value"]))
                 for r in rows if r["quantity"] == "profile_point")
    kap = np.array([a for a, _ in pts])
    dchi2 = np.array([b for _, b in pts])
    return named, kap, dchi2 - dchi2.min()


def _rows():
    named, kap, dchi2 = _joint()
    k_ub95 = float(named["kappa_ub95"]["value"])
    dchi2_0 = float(named["dchi2_kappa0"]["value"])

    # An adjacent pair whose fitted chi2 falls as kappa RISES cannot be
    # physical and is therefore the profile's own numerical noise. It sets
    # the resolution floor for any statement about the minimum. Under the
    # retired convention such a pair sat beside that convention's prediction
    # point, which run_stark_joint writes to two decimals, so its label was a
    # ROUNDED WRITE and not a coordinate, and an audit caught the first
    # version of this row reading it as one.
    # FOUND AND NOT ASSUMED (C6a, 2026-09-22): at the calculated waist no profile point sits at 1.54, and the
    # nearest-point lookup read the 1.50 point twice and wrote a fall of zero under a sentence describing a fall.
    # Every adjacent pair above the minimum is read now, and the largest fall is the floor, keyed from the data.
    imin = int(np.argmin(dchi2))
    falls = [(float(dchi2[i] - dchi2[i + 1]), float(kap[i]), float(kap[i + 1]))
             for i in range(imin, len(kap) - 1) if dchi2[i + 1] < dchi2[i]]
    scatter, k_fall_a, k_fall_b = max(falls) if falls else (0.0, float("nan"), float("nan"))

    # a.u. per (MHz per W): stark_shift_S0_mhz is linear in delta_alpha_au,
    # so one evaluation inverts it exactly.
    # F39: kappa is read from the WIDTH channel, which reads the spread of the shift
    # distribution under the rate weighting, so the clipped focus enters through the SPREAD
    # factor F(w0) (0.6964 at W0_CENTRAL_M, O44/F280's bore-limited value) and not the on-axis
    # c; the conversion divides by it, so the same kappa buys a larger delta-alpha. This SPREAD
    # factor is still the free-focus convention (aperture_spread_factor takes the unclipped
    # input's own focus, same as aperture_onaxis_factor did before F280); only the ON-AXIS
    # factor gained an actual-convention form (lineshape.aperture_onaxis_factor_actual) in this
    # window, so a same-reading correction to THIS number is F280's own stated open item.
    conv = P_REF_W / (stark_shift_S0_mhz(P_REF_W, W0_PRIOR_M, RHO_PRIOR, 1.0)
                      * aperture_spread_factor(W0_PRIOR_M))
    conv_pinned = P_REF_W / (stark_shift_S0_mhz(P_REF_W, W0_PINNED_M, RHO_PRIOR, 1.0)
                             * aperture_spread_factor(W0_PINNED_M))

    # The spacing that limits a claim about the MINIMUM is the one that
    # brackets the minimum, not the smallest spacing anywhere on the grid.
    # The first version took np.diff(kap).min(), which under the retired
    # convention was the 0.04 beside that convention's prediction point, 1.3
    # units away, and formerly argued a 149 a.u. vertex was unresolved beside
    # a step five times smaller than it.
    j = int(np.argmin(dchi2))
    local = [kap[j + 1] - kap[j] if j + 1 < len(kap) else np.inf,
             kap[j] - kap[j - 1] if j > 0 else np.inf]
    grid_quantum = float(min(local) * conv)

    # the vertex of a parabola through the three lowest committed points,
    # which is the most the grid supports saying about a central value
    a, b, _ = np.polyfit(kap[:3], dchi2[:3], 2)
    vertex_au = float(-b / (2 * a) * conv)

    rng = np.random.default_rng(SEED)
    w0 = rng.normal(W0_PRIOR_M, W0_PRIOR_ERR_M, N_DRAW)
    # rho is capped at 1: more light returning than went in is unphysical,
    # and constants.py names both residual effects as pushing rho below 1.
    rho = np.clip(rng.normal(RHO_PRIOR, RHO_PRIOR_ERR, N_DRAW), None, 1.0)
    keep = w0 > 0
    w0, rho = w0[keep], rho[keep]
    conv_draw = P_REF_W / (stark_shift_S0_mhz(P_REF_W, w0, rho, 1.0)
                           * aperture_spread_factor(w0))            # F39, the width channel's factor

    # (a) the committed construction, transferred. The 95 per cent is already
    # inside k_ub95, so the geometry prior is reported as the spread OF THE
    # LIMIT and never folded in as a second percentile.
    ub_profile = k_ub95 * conv
    ub_profile_err = float((k_ub95 * conv_draw).std())

    # (b) the same profile read as a posterior, flat prior on kappa >= 0
    fine = np.linspace(0.0, kap.max(), 600_001)
    w = np.exp(-0.5 * np.interp(fine, kap, dchi2))
    cdf = np.cumsum(w)
    cdf /= cdf[-1]
    draw = np.interp(rng.random(w0.size), cdf, fine)
    da_post = draw * conv_draw
    ub_post = float(np.percentile(da_post, 95))
    mean, sd = float(da_post.mean()), float(da_post.std())
    sd_data = float((draw * conv).std())
    sd_geom = float((draw.mean() * conv_draw).std())

    # THE SPREAD IS TAKEN AT FIXED GEOMETRY ON BOTH SIDES. The first
    # version divided a geometry-marginalised percentile by a
    # central-geometry limit, so the ratio mixed the construction change
    # with a marginalisation -- the same not-like-for-like class the
    # coverage postscript already withdrew once.
    k_post = float(np.interp(0.95, cdf, fine))
    spread = k_post / k_ub95

    # ...and decomposed, because most of it is not a property of THIS
    # profile at all. A Gaussian carrying the profile's own curvature
    # reproduces the committed crossing, and already separates the two
    # constructions by gauss_ratio with no shape involved.
    qa, qb, _ = np.polyfit(kap[:3], dchi2[:3], 2)
    mu_g, sig_g = -qb / (2 * qa), 1.0 / np.sqrt(qa)
    g = np.linspace(0.0, 10.0, 1_000_001)
    wg = np.exp(-0.5 * ((g - mu_g) / sig_g) ** 2)
    cg = np.cumsum(wg)
    cg /= cg[-1]
    gauss_ratio = float(np.interp(0.95, cg, g)
                        / (mu_g + np.sqrt(2.706) * sig_g))
    # where the profile departs from that Gaussian, read at the committed points and not described
    gdev = ((kap - mu_g) / sig_g) ** 2 - dchi2
    i_dev = int(np.argmax(gdev))

    # the tail probability under BOTH constructions, because it is not
    # construction-independent either and the first version said it was
    def _p_crossing(val: float) -> float:
        return 0.5 * erfc(sqrt(float(np.interp(val / conv, kap, dchi2)) / 2))

    cond = (f"conditional on the three P-squared channels being inseparable "
            f"so this bounds their sum, and on w0 = {W0_PRIOR_M * 1e6:g} +- "
            f"{W0_PRIOR_ERR_M * 1e6:g} um with rho = {RHO_PRIOR:g} +- "
            f"{RHO_PRIOR_ERR:g}")

    yield ["limit", "delta_alpha_abs_ub95_profile", f"{ub_profile:.0f}",
           f"{ub_profile_err:.0f}", "a.u., magnitude only",
           f"THE QUOTED LIMIT, because it is the record's own construction: "
           f"the committed kappa_ub95 = {k_ub95:g} read off the Delta_chi2 = "
           f"2.706 crossing, carried through the geometry at w0 = "
           f"{W0_PRIOR_M * 1e6:g} um. The err column is ENTIRELY geometric, "
           f"because the crossing itself is a fixed committed number, so "
           f"tighter beam metrology WOULD sharpen this row even though it "
           f"would not sharpen the posterior below. The width channel's "
           f"factor here is the free-focus convention's (aperture_spread_factor), "
           f"not the same-reading one F280 maps for the bench's clipped beam, "
           f"which is larger at this waist, so this limit is conservative until "
           f"the same-reading spread factor lands. {cond}", "BOUND"]
    yield ["limit", "delta_alpha_abs_ub95_profile_at_pinned_w0",
           f"{k_ub95 * conv_pinned:.0f}", "", "a.u., magnitude only",
           f"the same crossing at W0_CENTRAL_M = {W0_PINNED_M * 1e6:g} um, "
           f"the record's pinned central value, against the row above at the "
           f"owner's stated prior centre of {W0_PRIOR_M * 1e6:g}. The two "
           f"differ by exactly ({W0_PRIOR_M / W0_PINNED_M:.4f})^2 and by "
           f"nothing else, so agreement between any two numbers computed this "
           f"way is arithmetic and never corroboration", "DIAGNOSTIC"]
    yield ["limit", "delta_alpha_abs_ub95_posterior", f"{ub_post:.0f}", "",
           "a.u., magnitude only",
           f"the SAME committed profile read as a posterior with a flat "
           f"prior on kappa >= 0, geometry marginalised over {da_post.size} "
           f"draws. Higher than the crossing, and construction_spread below "
           f"says how much of that is generic and how much is this profile. "
           f"{cond}", "BOUND"]
    yield ["limit", "construction_spread", f"{spread:.3f}", "", "ratio",
           f"posterior over crossing, BOTH at the central geometry so the "
           f"ratio isolates the construction and nothing else. A first "
           f"version divided a geometry-marginalised percentile by a "
           f"central-geometry limit and mixed the two. DECOMPOSED: a Gaussian "
           f"carrying this profile's own curvature reproduces the committed "
           f"crossing to four digits and already separates the constructions "
           f"by {gauss_ratio:.3f}, so most of the gap is the generic "
           f"difference between a one-sided crossing and a posterior quantile "
           f"and would exist for an exactly Gaussian likelihood. Only "
           f"{spread / gauss_ratio:.3f} is this profile's shape: among the committed points the profile sits "
           f"furthest below that Gaussian at kappa {kap[i_dev]:.2f}, by {gdev[i_dev]:.2f} in Delta_chi2",
           "DIAGNOSTIC"]
    yield ["estimator", "sigma_from_zero", f"{np.sqrt(dchi2_0):.2f}", "",
           "sigma",
           "sqrt of the committed Delta_chi2 at kappa = 0. "
           + ("Consistent with no shift at all" if np.sqrt(dchi2_0) < 2.0 else "Short of a detection")
           + ", which is why the licensed statement is a limit and not a value", "DIAGNOSTIC"]
    yield ["estimator", "delta_alpha_abs_vertex", f"{vertex_au:.0f}", "",
           "a.u., magnitude only",
           f"the vertex of a parabola through the three lowest committed "
           f"profile points. NOT A MEASUREMENT: the grid spacing that "
           f"BRACKETS the minimum is {grid_quantum:.0f} a.u., "
           + ("larger than" if grid_quantum > vertex_au else "smaller than")
           + f" this value, and Delta_chi2 at zero is {dchi2_0:g}"
           + (f", below the profile's own numerical scatter of {scatter:g}" if dchi2_0 < scatter else "")
           + ". The central value is unresolved and this row exists to say by how much",
           "DIAGNOSTIC"]
    yield ["posterior", "delta_alpha_abs_mean", f"{mean:.0f}", f"{sd:.0f}",
           "a.u., magnitude only",
           f"posterior mean and standard deviation. The truncation at zero "
           f"makes the mean positive whatever the data say, so the ratio of "
           f"this value to this error is NOT a significance and must never "
           f"be quoted as one. {cond}", "DIAGNOSTIC"]
    yield ["budget", "err_from_data", f"{sd_data:.0f}", "", "a.u.",
           "the committed kappa profile's own contribution to the posterior "
           "spread", "DIAGNOSTIC"]
    yield ["budget", "err_from_geometry", f"{sd_geom:.0f}", "", "a.u.",
           f"the stated geometry priors' contribution to the POSTERIOR "
           f"spread, which is {100 * sd_geom / sd:.1f} per cent of it on the "
           f"sigma scale. Do not carry this to the quoted limit: that row's "
           f"whole error bar is geometric", "DIAGNOSTIC"]
    yield ["budget", "geometry_share_of_variance",
           f"{(sd_geom / sd) ** 2:.4f}", "", "fraction",
           "the geometry priors' share of the posterior VARIANCE. A share of "
           "variance is the square of a share of sigma, so this number is "
           "the smallest honest way to state the geometry's weight and it "
           "applies to the posterior alone. Sharpening the priors would not "
           "sharpen the posterior, and WOULD sharpen the quoted limit",
           "DIAGNOSTIC"]
    for name, val in (("computed_here", abs(K.DELTA_ALPHA_AU)),
                      ("orson2021", abs(K.DELTA_ALPHA_AU_ORSON2021))):
        # A PROBABILITY UNDER 1e-4 IS WRITTEN IN ITS OWN DIGITS (C6a, 2026-09-22): at the calculated waist both
        # comparisons read 0.0000 at four decimals, which says nothing about how far out the tail is
        n_above = int((da_post > val).sum())
        p_post = n_above / da_post.size

        def _fmt(x: float) -> str:
            return f"{x:.4f}" if x >= 1e-4 else f"{x:.1e}"
        yield ["comparison", f"posterior_prob_above_{name}",
               _fmt(p_post) if n_above else "0", "", "probability",
               f"posterior probability that |Delta_alpha| exceeds {val:g} "
               f"a.u., {n_above} of {da_post.size} draws"
               + ("" if n_above else f", so it is below {1.0 / da_post.size:.0e}")
               + f". Under the CROSSING construction the same comparison "
               f"gives {_fmt(_p_crossing(val))}. The two candidate values sit "
               f"{_fmt(abs(_p_crossing(abs(K.DELTA_ALPHA_AU)) - _p_crossing(abs(K.DELTA_ALPHA_AU_ORSON2021))))} apart "
               f"under the crossing"
               + (f", and the profile's own numerical noise ({scatter:.2f} in chi2 between the adjacent points "
                  f"keyed {k_fall_a:.2f} and {k_fall_b:.2f}) forbids reading an ordering between them" if falls else "")
               + ". The tension is real under both and neither may be quoted to three digits",
               "DIAGNOSTIC"]
    yield ["provenance", "profile_numerical_scatter", f"{scatter:.2f}", "",
           "dimensionless",
           (f"the committed profile carries adjacent points keyed {k_fall_a:.2f} and {k_fall_b:.2f} whose "
            f"fitted chi2 FALLS as kappa rises, by {scatter:g}. That cannot be physical, so it is the profile's "
            f"own numerical noise" + (", and it exceeds Delta_chi2 at kappa = 0" if scatter > dchi2_0 else "")
            if falls else
            "the committed profile rises monotonically above its minimum at every one of its points, so no "
            "adjacent pair shows numerical noise and this row reads zero: the floor sits below the grid's own "
            "resolution and is not measured here"), "DIAGNOSTIC"]


def main() -> int:
    out = C.RESULTS_DIR / "delta_alpha_posterior.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scope", "quantity", "value", "err", "unit", "note",
                    "status"])
        for row in _rows():
            w.writerow(row)
    print(f"wrote {out}")
    for row in _rows():
        print(f"  {row[0]:11s} {row[1]:34s} {row[2]:>8s} "
              f"{('+- ' + row[3]) if row[3] else '':>8s}  {row[4]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402

# The owner's stated priors, 2026-08-27. W0_PRIOR_M is the centre of the
# committed 62-68 um band; the pinned constant is 64 um, and the two are
# named separately here because a first draft of the prose conditioned on one
# and compared against the other four lines apart.
W0_PRIOR_M, W0_PRIOR_ERR_M = 65e-6, 3e-6
RHO_PRIOR, RHO_PRIOR_ERR = 0.94, 0.04
W0_PINNED_M = 64e-6                  # constants.W0_MEASURED_M
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

    # The grid carries an adjacent pair whose fitted chi2 falls as kappa
    # RISES, which cannot be physical and is therefore the profile's own
    # numerical noise. It sets the resolution floor for any statement about
    # the minimum. The pair's keys read 1.50 and 1.54, but run_stark_joint
    # writes that column as f"{kap:.2f}" and the second point is the
    # prediction point at KAPPA_PRED = 1.545, so the label is a ROUNDED
    # WRITE and not a coordinate. A board caught the first version of this
    # row reading it as one.
    i50, i54 = int(np.argmin(abs(kap - 1.50))), int(np.argmin(abs(kap - 1.54)))
    scatter = float(abs(dchi2[i50] - dchi2[i54]))

    # a.u. per (MHz per W): stark_shift_S0_mhz is linear in delta_alpha_au,
    # so one evaluation inverts it exactly.
    conv = P_REF_W / stark_shift_S0_mhz(P_REF_W, W0_PRIOR_M, RHO_PRIOR, 1.0)
    conv_pinned = P_REF_W / stark_shift_S0_mhz(P_REF_W, W0_PINNED_M,
                                               RHO_PRIOR, 1.0)

    # The spacing that limits a claim about the MINIMUM is the one that
    # brackets the minimum, not the smallest spacing anywhere on the grid.
    # The first version took np.diff(kap).min(), which is the 0.04 of the
    # 1.50/1.545 pair sitting 1.3 units away, and then argued a 149 a.u.
    # vertex was unresolved beside a step five times smaller than it.
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
    conv_draw = P_REF_W / stark_shift_S0_mhz(P_REF_W, w0, rho, 1.0)

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
           f"would not sharpen the posterior below. {cond}", "BOUND"]
    yield ["limit", "delta_alpha_abs_ub95_profile_at_pinned_w0",
           f"{k_ub95 * conv_pinned:.0f}", "", "a.u., magnitude only",
           f"the same crossing at W0_MEASURED_M = {W0_PINNED_M * 1e6:g} um, "
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
           f"{spread / gauss_ratio:.3f} is this profile's shape, and it comes "
           f"from the SHOULDER near kappa 1 to 2 where the profile is "
           f"flatter than that Gaussian. Below kappa = 1 the two agree to "
           f"within this profile's own numerical scatter, so the core "
           f"carries none of it",
           "DIAGNOSTIC"]
    yield ["estimator", "sigma_from_zero", f"{np.sqrt(dchi2_0):.2f}", "",
           "sigma",
           "sqrt of the committed Delta_chi2 at kappa = 0. Consistent with "
           "no shift at all, which is why the licensed statement is a limit "
           "and not a value", "DIAGNOSTIC"]
    yield ["estimator", "delta_alpha_abs_vertex", f"{vertex_au:.0f}", "",
           "a.u., magnitude only",
           f"the vertex of a parabola through the three lowest committed "
           f"profile points. NOT A MEASUREMENT: the grid spacing that "
           f"BRACKETS the minimum is {grid_quantum:.0f} a.u., larger than "
           f"this value, and Delta_chi2 at zero is {dchi2_0:g}, below the "
           f"profile's own numerical scatter of {scatter:g}. The central "
           f"value is unresolved and this row exists to say by how much",
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
        yield ["comparison", f"posterior_prob_above_{name}",
               f"{float((da_post > val).mean()):.4f}", "", "probability",
               f"posterior probability that |Delta_alpha| exceeds {val:g} "
               f"a.u. Under the CROSSING construction the same comparison "
               f"gives {_p_crossing(val):.4f}, so this figure moves by about "
               f"a factor of two, most of that being the construction and about a tenth the geometry marginalisation. The two candidate "
               f"values sit 0.0004 apart under the crossing, which is BELOW "
               f"this profile's own numerical noise floor: the 1.50/1.54 pair "
               f"differ by 0.24 in chi2, worth 0.0025 in p here, so no "
               f"ordering between them may be read. The tension is "
               f"real under both and neither may be quoted to three digits",
               "DIAGNOSTIC"]
    yield ["provenance", "profile_numerical_scatter", f"{scatter:.2f}", "",
           "dimensionless",
           f"the committed profile carries adjacent points keyed 1.50 and "
           f"1.54 whose fitted chi2 FALLS as kappa rises, by {scatter:g}. "
           f"That cannot be physical, so it is the profile's own numerical "
           f"noise, and it exceeds Delta_chi2 at kappa = 0. The 1.54 key is a "
           f"rounded write of the prediction point at 1.545, so it is a label "
           f"and not a coordinate", "DIAGNOSTIC"]


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

#!/usr/bin/env python3
"""
What a further measurement campaign would buy, as computed projections.

WHO ACTS ON THIS AND WHAT CHANGES FOR THEM. The reader is the host deciding
bench time. Today the case for a session is carried by prose ("converts bounds
into measurements", "3 to 12 sigma"). This script replaces each of those
sentences with a number derived from the archive's own measured precision and
the design parameters `docs/PLAN.md` already states, so the decision is read off
a table instead of off an adjective. Six families are projected: the fixed-lock
pull channel, beta_self, the 7S adjudication, the 778 nm calibration rung, the
magic-wavelength scan, and the guided-mode option.

WHAT THIS IS NOT. Nothing here is a measurement, and no row is evidence about
the atom. Every row is a projection of an instrument's reach under a stated
assumption set, and the assumption set travels in the row. The projections are
tagged ENVELOPE and the inputs they are built from are tagged CALIB, so nothing
in this file can be mistaken for a result even by a script that never opens the
prose.

RATE-DEPENDENT INPUTS AND THE SECOND PASS. Every input below that is quoted in
MHz rides on the campaign sweep rate, which is the calibration currently
committed in `results/ruler_campaign.csv`. That calibration is under
re-validation (`docs/notes/ruler_validity_and_trim_prereg.md`), and the
re-validation can move it. Nothing in this script hard-codes a rate-dependent
number: the per-trace centre precision, the block-to-block width scatter, the
per-block ruler spacing precision and the ruler linearity bound are all read
live from the committed CSVs at run time. Re-running this script after the
recompute lands therefore re-derives every projection at the corrected
calibration, with no edit to this file. That re-run is the owner's second pass
and is the only action the correction requires here.

INPUTS, all committed:
  results/stark_centres.csv          per-trace centre precision
  results/linefit_conditions.csv     block-to-block width scatter
  results/ruler_blocks.csv           per-block ruler spacing precision
  results/ruler_campaign.csv         ruler linearity bound
  results/beta_self_probe.csv        the four-point construction's t quantile
  rb5s6s.density                     the density lever
  rb5s6s.lineshape, rb5s6s.constants the ramp moments and the predicted shift
  rb5s6s.vanderwaals                 the anchored beta_self expectation
  rb5s6s.polarizability (via CSV)    the two disputed polarizability signs
  docs/PLAN.md                       the stated session parameters
  docs/lit/zameroski2014.md, wang2025.md, cao2025.md, hamilton2023.md
  docs/notes/guided_mode_two_photon_design.md

Writes results/projections.csv. Status ENVELOPE for every projection and CALIB
for every carried input, registered in scripts/annotate_results_status.py.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C          # noqa: E402
from rb5s6s import constants as K       # noqa: E402
from rb5s6s import density, lineshape, vanderwaals   # noqa: E402

# --------------------------------------------------------------------------- #
# PLAN's stated session parameters. Every value below is quoted from            #
# docs/PLAN.md at the section named beside it, and nothing else in this file    #
# is typed by hand.                                                            #
# --------------------------------------------------------------------------- #
PLAN_W0_CONFIG_L_M = 60e-6        # PLAN 4.1, the width workhorse
PLAN_ZC_CONFIG_L_M = 3.16e-3      # PLAN 6, landscape cathode at M = 1.9
PLAN_LOCK_DRIFT_LASER_MHZ_PER_MIN = 0.02   # PLAN 2, from APPARATUS 6
PLAN_CYCLE_MIN = 10.0             # PLAN 10.4, the mini-P excursion cadence
PLAN_N_POWERS = 8                 # PLAN 9 D4, "randomized, ~8 powers"
PLAN_N_PEAKS = 4                  # PLAN 7, four peaks interleaved per block
PLAN_BLOCK_NOISE_CUT = 4.0        # PLAN 3 item 3, interleaving plus power logging
PLAN_T_GRID_C = (70, 90, 110, 130, 170)   # PLAN 7, five blocks reaching 150-170
PLAN_COLD_SPOT_LAG_K = 20         # PLAN 8 item 3, the archive's face-value lag
PLAN_INTENSITY_AXIS_FRAC = 0.15   # PLAN 5, the differential-transit anchor
PLAN_MORNING_CYCLES = 24          # PLAN 9 D4, a four-hour morning at PLAN_CYCLE_MIN

# The archive's own power ladder, which sets the span of the projected grid.
ARCHIVE_P_MIN_W, ARCHIVE_P_MAX_W = 0.025, 0.225
QUOTE_P_W = 0.225                 # the campaign maximum every bound is quoted at

# The density-scale systematic the archival bound already folds in.
N_SCALE_FRAC = 0.20               # results/beta_self_probe.csv, n_frac_syst

# Published rates the projections are measured against. Each is the value its
# lit note verified from the held PDF, with the note named in the row.
ZAMEROSKI_7S_KHZ_PER_MTORR = (129.0, 11.0)     # docs/lit/zameroski2014.md
WANG_7S_KHZ_PER_MTORR = (320.0, 10.0)          # docs/lit/wang2025.md
CAO_5D_KHZ_PER_MTORR = (40.0, 0.54)            # docs/lit/cao2025.md
ZAMEROSKI_CM3_PER_MTORR = 2.40e13              # at 403 K, docs/lit/zameroski2014.md
CAO_CM3_PER_MTORR = 2.28e13                    # at 423 K, docs/lit/cao2025.md

# Hamilton's magic wavelength and the pole that bounds a scan across it.
HAMILTON_MAGIC_NM, HAMILTON_MAGIC_ERR_NM = 776.179, 0.005   # docs/lit/hamilton2023.md
POLE_5P32_5D52_NM = 776.0        # FUTURE_TRANSITIONS_titsapph.md 3.3

# The guided-mode design note's own working point.
GUIDED_MODE_RADIUS_M = 10e-6     # notes/guided_mode_two_photon_design.md 2.2
GUIDED_POWER_W = 0.100
GUIDED_RHO = 1.0
GUIDED_DELTA_ALPHA_AU = 1144.6
GUIDED_HOT_FILL_COUNTS_PER_S = 2.8e5   # carried, not recomputable here
GUIDED_ANCHOR_GAP = (16, 47)


def _rows_out():
    return []


def _add(rows, quantity, key, value, err, unit, formula, assumptions, source):
    rows.append(dict(quantity=quantity, key=key,
                     value=f"{value:.6g}" if value is not None else "",
                     err=f"{err:.6g}" if err is not None else "",
                     unit=unit, formula=formula, assumptions=assumptions,
                     source=source))


# --------------------------------------------------------------------------- #
# Inputs read live from the committed archive                                   #
# --------------------------------------------------------------------------- #
def read_inputs() -> dict:
    centres = pd.read_csv(C.RESULTS_DIR / "stark_centres.csv")
    linear = centres[centres.drift_model == "linear"].iloc[0]
    sigma_centre_laser = float(linear.resid_mhz)

    lf = pd.read_csv(C.RESULTS_DIR / "linefit_conditions.csv")
    sweep = lf[(lf.role == "t_sweep") | ((lf.role == "p_sweep") & (lf["T"] == 130))]
    ladder = lf[(lf.role == "p_sweep") & (lf["T"] == 130)]
    g = ladder.groupby("peak")["total_fwhm"]
    rel_block = float((g.std() / g.mean()).mean())
    width_mean = float(sweep.total_fwhm.mean())

    rb = pd.read_csv(C.RESULTS_DIR / "ruler_blocks.csv")
    ruler_rel = float((rb.delta_err_ms / rb.delta_ms).median())

    rc = pd.read_csv(C.RESULTS_DIR / "ruler_campaign.csv").iloc[0]
    linearity_rel = float(rc.position_mismatch_relerr)

    probe = pd.read_csv(C.RESULTS_DIR / "beta_self_probe.csv")
    t95_four_point = float(probe.t95.iloc[0])

    pol = pd.read_csv(C.RESULTS_DIR / "polarizability.csv")
    da_recompute = abs(float(
        pol[(pol.quantity == "delta_alpha_993") & (pol.key == "model")].value.iloc[0]))

    return dict(
        sigma_centre_laser=sigma_centre_laser,
        sigma_centre_transition=2.0 * sigma_centre_laser,
        rel_block=rel_block, width_mean=width_mean,
        sigma_width_block=width_mean * rel_block,
        ruler_rel=ruler_rel, linearity_rel=linearity_rel,
        t95_four_point=t95_four_point, da_recompute=da_recompute)


def density_lever(grid_c, lag_k: int) -> float:
    """sqrt(sum of squared deviations of N about its mean) over the T grid, in
    units of 1e12 cm^-3. This is the denominator of a least-squares slope, so a
    width uncertainty divided by it is the uncertainty on beta_self."""
    n = np.array([float(density.number_density_cm3(t - lag_k)) for t in grid_c]) / 1e12
    return float(np.sqrt(((n - n.mean()) ** 2).sum()))


def power_lever(n_points: int) -> float:
    """sqrt(sum of squared deviations of P about its mean) over a log grid
    spanning the archive's own ladder, in W. The denominator of the pull slope."""
    p = np.geomspace(ARCHIVE_P_MIN_W, ARCHIVE_P_MAX_W, n_points)
    return float(np.sqrt(((p - p.mean()) ** 2).sum()))


def sigma_new_for_separation(gap: float, sigma_published: float,
                             n_sigma: float) -> float:
    """Largest new-measurement uncertainty that still separates two published
    values by `n_sigma`, given the larger of their own errors. Solves
    gap / sqrt(sigma_new^2 + sigma_published^2) = n_sigma. Returns nan where the
    published errors alone already exhaust the gap."""
    inside = (gap / n_sigma) ** 2 - sigma_published ** 2
    return float(np.sqrt(inside)) if inside > 0 else float("nan")


# --------------------------------------------------------------------------- #
# 1. The fixed-lock pull channel                                                #
# --------------------------------------------------------------------------- #
def project_pull(rows, inp) -> dict:
    z_r = np.pi * PLAN_W0_CONFIG_L_M ** 2 / K.LAMBDA_LASER_M
    pull_coeff = abs(lineshape.ramp_moment_contributions(
        1.0, PLAN_ZC_CONFIG_L_M / z_r)["pull"])
    s_pp = power_lever(PLAN_N_POWERS)

    drift_transition = 2.0 * PLAN_LOCK_DRIFT_LASER_MHZ_PER_MIN
    sigma_drift = drift_transition * PLAN_CYCLE_MIN / np.sqrt(12.0)

    # Per cycle: the centre-fit term averages over the four interleaved peaks,
    # the lock-drift term does not, because the four peaks of one cycle sit
    # inside the same ten minutes and share it.
    sigma_slope = np.sqrt(
        (inp["sigma_centre_transition"] / (np.sqrt(PLAN_N_PEAKS) * s_pp)) ** 2
        + (sigma_drift / s_pp) ** 2)
    sigma_s0_cycle = QUOTE_P_W * sigma_slope / pull_coeff

    s0_pred = lineshape.stark_shift_S0_mhz(
        QUOTE_P_W, K.W0_PRIOR_M, K.RHO_RETRO, K.DELTA_ALPHA_AU)
    s0_pred_recompute = lineshape.stark_shift_S0_mhz(
        QUOTE_P_W, K.W0_PRIOR_M, K.RHO_RETRO, inp["da_recompute"])
    sign_gap = s0_pred + s0_pred_recompute

    _add(rows, "input_centre_precision_per_trace", "archive", 2.0 * inp["sigma_centre_laser"],
         None, "MHz, transition axis",
         "2 x resid_mhz of the epoch-offset linear-drift fit",
         "conservative: measured under the 2025 drifting lock, so it still "
         "carries uncorrected drift that a fixed lock removes",
         "results/stark_centres.csv")
    _add(rows, "input_lock_drift_rate", "held lock", 2.0 * PLAN_LOCK_DRIFT_LASER_MHZ_PER_MIN,
         None, "MHz per min, transition axis",
         "2 x the held-lock bound of PLAN 2",
         "the archive's own held-lock bound, not the borrowed cavity figure of "
         "Ayachitula 2024 and not the photographed cavity-locked rate",
         "docs/PLAN.md 2, docs/APPARATUS.md 6")
    _add(rows, "input_ramp_pull_coefficient", "config L", pull_coeff, None,
         "dimensionless",
         "mean of the axially averaged ramp over S0, at Z_c / z_R",
         f"config L waist {PLAN_W0_CONFIG_L_M * 1e6:.0f} um and collection "
         f"half-window {PLAN_ZC_CONFIG_L_M * 1e3:.2f} mm, PLAN 4.1 and PLAN 6",
         "rb5s6s.lineshape.ramp_moment_contributions")
    _add(rows, "input_S0_predicted", "225 mW", s0_pred, None, "MHz, transition axis",
         "stark_shift_S0_mhz at the committed waist prior and retro ratio",
         "the prediction the archival bound is compared against",
         "rb5s6s.constants, rb5s6s.lineshape")
    _add(rows, "input_intensity_axis_systematic", "differential transit anchor",
         PLAN_INTENSITY_AXIS_FRAC, None, "fraction",
         "the intensity-axis accuracy PLAN 5 attributes to the S minus L "
         "transit width difference measured to 5 to 7 percent",
         "adopted from PLAN rather than re-derived, and read as one sigma",
         "docs/PLAN.md 5")
    _add(rows, "input_density_scale_systematic", "archival", N_SCALE_FRAC, None,
         "fraction",
         "the density-scale systematic the archival bound already folds in",
         "carried unchanged, and it is what the absorption channel of PLAN 8 "
         "would replace with a measurement",
         "results/beta_self_probe.csv n_frac_syst")

    for cycles, label in ((6, "6 per day, 1 day"),
                          (PLAN_MORNING_CYCLES, "24 per day, 1 day"),
                          (2 * PLAN_MORNING_CYCLES, "24 per day, 2 days")):
        sigma = sigma_s0_cycle / np.sqrt(cycles)
        frac_da = np.sqrt((sigma / s0_pred) ** 2 + PLAN_INTENSITY_AXIS_FRAC ** 2)
        common = (
            f"{cycles} randomized power cycles of {PLAN_CYCLE_MIN:.0f} min, "
            f"{PLAN_N_POWERS} rungs log spaced over the archive's own "
            f"{ARCHIVE_P_MIN_W * 1e3:.0f}-{ARCHIVE_P_MAX_W * 1e3:.0f} mW ladder, "
            f"one trace per rung, {PLAN_N_PEAKS} peaks interleaved, config L, "
            "centre precision at the archival per-trace value, lock drift at "
            "the held-lock bound and common to the four peaks of a cycle")
        _add(rows, "proj_pull_S0_sigma", label, sigma, None, "MHz, transition axis",
             "0.225 x sqrt(sigma_centre^2 / (4 Spp) + sigma_drift^2 / Spp) "
             "/ |mean/S0| / sqrt(cycles), Spp the power lever",
             common, "docs/PLAN.md 9 D4, PLAN 7, PLAN 10.4")
        _add(rows, "proj_pull_S0_over_prediction", label, s0_pred / sigma, None,
             "sigma",
             "predicted S0(225 mW) divided by the projected uncertainty",
             common + "; prediction at the committed waist prior",
             "results/stark_joint.csv S0_225mW_pred")
        _add(rows, "proj_deltaalpha_frac", label, frac_da, None, "fraction, 1 sigma",
             "quadrature sum of the fractional shift uncertainty and the "
             "intensity-axis systematic",
             common + f"; intensity axis anchored to {PLAN_INTENSITY_AXIS_FRAC:.0%} "
             "by the differential transit width of PLAN 5",
             "docs/PLAN.md 5")
        _add(rows, "proj_deltaalpha_sign_separation", label, sign_gap / sigma, None,
             "sigma",
             "|S0(+Delta-alpha) - S0(-Delta-alpha)| divided by the projected "
             "uncertainty, both evaluated at the committed waist prior",
             common + "; the two signs are the pinned +1093 a.u. and the "
             "recomputed -1145 a.u., both evaluated at the committed waist "
             "prior, so a common intensity-scale error moves the separation "
             "even though it cannot move which sign the pull has",
             "rb5s6s.constants DELTA_ALPHA_AU, results/polarizability.csv")

    return dict(sigma_s0_cycle=sigma_s0_cycle, s0_pred=s0_pred)


# --------------------------------------------------------------------------- #
# 2. beta_self, bound to measurement                                            #
# --------------------------------------------------------------------------- #
def project_beta(rows, inp) -> dict:
    anchor = vanderwaals.beta_self_anchored()
    beta_expected_mhz = anchor["beta6_khz"] / 1e3

    sigma_w_raw = inp["sigma_width_block"]
    sigma_w_cut = sigma_w_raw / PLAN_BLOCK_NOISE_CUT
    sigma_axis = inp["ruler_rel"] * inp["width_mean"]
    sigma_w_eff = float(np.hypot(sigma_w_cut, sigma_axis))

    lever_lag = density_lever(PLAN_T_GRID_C, PLAN_COLD_SPOT_LAG_K)
    lever_nolag = density_lever(PLAN_T_GRID_C, 0)
    t95_five = float(stats.t.ppf(0.95, len(PLAN_T_GRID_C) - 2))

    _add(rows, "input_block_width_scatter", "archive", sigma_w_raw, None, "MHz",
         "mean total width over the 70-130 C sweep times the mean per-peak "
         "relative block scatter of the 130 C power ladder",
         "measured where the width is power independent, so the spread between "
         "blocks is instrumental",
         "results/linefit_conditions.csv, reproduced in results/resolving_power.csv")
    _add(rows, "input_block_width_scatter_interleaved", "projected", sigma_w_cut,
         None, "MHz",
         f"the archival block scatter divided by {PLAN_BLOCK_NOISE_CUT:.0f}",
         "the cut PLAN 3 item 3 attributes to interleaving plus per-trace power "
         "logging, adopted rather than re-derived",
         "docs/PLAN.md 3")
    _add(rows, "input_ruler_spacing_precision", "per block", inp["ruler_rel"], None,
         "fraction",
         "median over blocks of the tooth-spacing error divided by the spacing",
         "the frequency axis each block carries, which scales every width "
         "measured on it",
         "results/ruler_blocks.csv")
    _add(rows, "input_ruler_linearity_bound", "campaign", inp["linearity_rel"], None,
         "fraction",
         "the committed position-mismatch bound read against the sweep "
         "nonlinearity map",
         "the rulers and the lines sit at different places in the acquisition "
         "window",
         "results/ruler_campaign.csv, results/ruler_nlmap.csv")
    _add(rows, "input_density_lever", "20 K cold-spot lag", lever_lag, None,
         "1e12 cm^-3",
         "sqrt of the summed squared deviations of N about its mean over the "
         "five-block T grid, densities read at T minus the lag",
         f"grid {PLAN_T_GRID_C} C, cold-spot lag {PLAN_COLD_SPOT_LAG_K} K, "
         "which is the archive's own face-value preference",
         "rb5s6s.density, docs/PLAN.md 7 and 8")
    _add(rows, "input_density_lever", "no lag", lever_nolag, None, "1e12 cm^-3",
         "the same sum with densities read at the nominal set points",
         "the optimistic end, valid only if the cold spot is absent",
         "rb5s6s.density")
    _add(rows, "input_beta_self_expected", "vdW anchored", anchor["beta6_khz"],
         anchor["beta6_err_khz"], "kHz per 1e12 cm^-3",
         "the measured 7S rate carried across one rung by the computed C6 ratio",
         "one external measurement in the chain, and the ratio is the module's "
         "own Casimir-Polder integrals",
         "rb5s6s.vanderwaals.beta_self_anchored, docs/lit/zameroski2014.md")

    out = {}
    for lever, lag_label in ((lever_lag, "20 K cold-spot lag"),
                             (lever_nolag, "no lag")):
        for sigma_w, noise_label in ((sigma_w_eff, "interleaved"),
                                     (float(np.hypot(sigma_w_raw, sigma_axis)),
                                      "archival block noise")):
            key = f"{noise_label}, {lag_label}"
            sigma_beta_mhz = sigma_w / lever
            sigma_beta_khz = sigma_beta_mhz * 1e3
            detect = beta_expected_mhz / sigma_beta_mhz
            frac = float(np.hypot(sigma_beta_mhz / beta_expected_mhz, N_SCALE_FRAC))
            assumptions = (
                f"five T blocks per peak on the grid {PLAN_T_GRID_C} C, one "
                "block per point, interleaved temperature order over two "
                "opposite-direction days, per-block width uncertainty the "
                f"{noise_label} value combined in quadrature with the ruler "
                f"axis term, density lever with {lag_label}")
            _add(rows, "proj_beta_self_sigma", key, sigma_beta_khz, None,
                 "kHz per 1e12 cm^-3",
                 "per-block width uncertainty divided by the density lever",
                 assumptions, "docs/PLAN.md 7, results/linefit_conditions.csv")
            _add(rows, "proj_beta_self_detection_sigma", key, detect, None, "sigma",
                 "the anchored expectation divided by the projected uncertainty",
                 assumptions + "; the density-scale systematic does not enter a "
                 "detection, because a scale error cannot move zero",
                 "rb5s6s.vanderwaals.beta_self_anchored")
            _add(rows, "proj_beta_self_frac", key, frac, None, "fraction, 1 sigma",
                 "quadrature sum of the statistical fraction and the "
                 f"{N_SCALE_FRAC:.0%} density-scale systematic",
                 assumptions, "results/beta_self_probe.csv n_frac_syst")
            if key == "interleaved, 20 K cold-spot lag":
                out = dict(sigma_beta_mhz=sigma_beta_mhz, detect=detect)

    _add(rows, "proj_beta_self_t_quantile", "five blocks", t95_five, None,
         "dimensionless",
         "Student t at 95% on three residual degrees of freedom",
         "five T blocks and two fitted parameters, against the four-point "
         f"construction's own {inp['t95_four_point']:.2f} on two",
         "docs/PLAN.md 7, results/beta_self_probe.csv t95")
    out["sigma_w_eff"] = sigma_w_eff
    out["lever_lag"] = lever_lag
    return out


# --------------------------------------------------------------------------- #
# 3. The 7S adjudication                                                        #
# --------------------------------------------------------------------------- #
def project_7s(rows, beta_out) -> None:
    zam, zam_err = ZAMEROSKI_7S_KHZ_PER_MTORR
    wang, wang_err = WANG_7S_KHZ_PER_MTORR
    published_err = max(zam_err, wang_err)

    khz_per_mtorr_per_mhz_per_1e12 = ZAMEROSKI_CM3_PER_MTORR / 1e12 * 1e3
    delivered = beta_out["sigma_beta_mhz"] * khz_per_mtorr_per_mhz_per_1e12

    for wang_fwhm, label in ((wang, "Wang read as FWHM"),
                             (2 * wang, "Wang read as HWHM")):
        gap = abs(wang_fwhm - zam)
        needed = sigma_new_for_separation(gap, published_err, 5.0)
        assumptions = (
            f"the two published rates are {zam:.0f} +/- {zam_err:.0f} and "
            f"{wang_fwhm:.0f} +/- {wang_err:.0f} kHz/mTorr under this reading, "
            "and the new measurement must sit five sigma from each once the "
            "larger published error is folded in")
        _add(rows, "proj_7s_precision_needed", label, needed, None, "kHz/mTorr",
             "sqrt((gap / 5)^2 - published error^2)",
             assumptions, "docs/lit/zameroski2014.md, docs/lit/wang2025.md")
        _add(rows, "proj_7s_margin", label, needed / delivered, None,
             "dimensionless",
             "the required precision divided by the projected precision",
             assumptions + "; the projection is the same five-block design as "
             "the 993 nm row, run on the 760 nm line",
             "results/projections.csv proj_7s_precision_delivered")

    _add(rows, "proj_7s_precision_delivered", "same-instrument session", delivered,
         None, "kHz/mTorr",
         "the projected beta_self uncertainty converted at Zameroski's own "
         "403 K density scale",
         "the same five-block interleaved design as the 993 nm projection, with "
         "the archive's absolute per-block width scatter and per-block ruler "
         "spacing precision carried over unchanged to the 760 nm line, and the "
         "20 K cold-spot lag applied",
         "results/ruler_blocks.csv, results/linefit_conditions.csv, "
         "docs/lit/zameroski2014.md")


# --------------------------------------------------------------------------- #
# 4. The 778 nm calibration rung                                                #
# --------------------------------------------------------------------------- #
def project_778(rows, beta_out) -> None:
    cao, cao_err = CAO_5D_KHZ_PER_MTORR
    khz_per_mtorr_per_mhz_per_1e12 = CAO_CM3_PER_MTORR / 1e12 * 1e3
    delivered = beta_out["sigma_beta_mhz"] * khz_per_mtorr_per_mhz_per_1e12

    tests = (
        ("factor-two convention error at 3 sigma",
         sigma_new_for_separation(cao, cao_err, 3.0),
         "sqrt((discrepancy / 3)^2 - published error^2), discrepancy the full "
         "published value",
         "a validation is meaningful only if it could reject the factor of two "
         "that an unstated HWHM against FWHM convention introduces, which is "
         "the failure mode this literature actually has"),
        ("20 percent method bias at 3 sigma",
         sigma_new_for_separation(0.20 * cao, cao_err, 3.0),
         "sqrt((discrepancy / 3)^2 - published error^2), discrepancy one fifth "
         "of the published value",
         "the level at which a passive-method bias would be a finding rather "
         "than a bookkeeping error"),
        ("match the published precision",
         cao_err,
         "the published one-sigma error itself",
         "the strongest reading, where the comparison is limited by the "
         "published value rather than by the new one"),
    )
    for label, needed, formula, why in tests:
        assumptions = (
            f"the published value is {cao:.0f} +/- {cao_err:.2f} kHz/mTorr with "
            f"the FWHM convention stated, and {why}")
        _add(rows, "proj_778_precision_needed", label, needed, None, "kHz/mTorr",
             formula, assumptions, "docs/lit/cao2025.md")
        _add(rows, "proj_778_margin", label, needed / delivered, None,
             "dimensionless",
             "the required precision divided by the projected precision, above "
             "one where the test would have power",
             assumptions, "results/projections.csv proj_778_precision_delivered")

    _add(rows, "proj_778_precision_delivered", "same-instrument session", delivered,
         None, "kHz/mTorr",
         "the projected beta_self uncertainty converted at Cao's own 423 K "
         "density scale",
         "the same five-block interleaved design as the 993 nm projection, with "
         "the archive's demonstrated per-condition width precision carried over "
         "unchanged to the 778 nm line, and the 20 K cold-spot lag applied",
         "results/linefit_conditions.csv, docs/lit/cao2025.md")
    _add(rows, "proj_778_precision_delivered_frac", "same-instrument session",
         delivered / cao, None, "fraction of the published value",
         "the projected precision divided by the published coefficient",
         "as above, against Cao's 1.3 percent",
         "docs/lit/cao2025.md")


# --------------------------------------------------------------------------- #
# 5. The magic-wavelength scan                                                  #
# --------------------------------------------------------------------------- #
def project_magic(rows, inp) -> None:
    lam_m = HAMILTON_MAGIC_NM * 1e-9
    target_hz = K.C_M_PER_S * (HAMILTON_MAGIC_ERR_NM * 1e-9) / lam_m ** 2
    span_nm = HAMILTON_MAGIC_NM - POLE_5P32_5D52_NM
    axis_rel = float(np.hypot(inp["ruler_rel"], inp["linearity_rel"]))

    _add(rows, "proj_magic_776_target", "Hamilton 5 pm", target_hz / 1e9, None,
         "GHz, laser axis",
         "c times the published wavelength uncertainty divided by the "
         "wavelength squared",
         "matching the published determination means placing the zero crossing "
         "to its own 5 pm",
         "docs/lit/hamilton2023.md")
    _add(rows, "proj_magic_776_axis_term", "ruler axis", axis_rel, None, "fraction",
         "per-block ruler spacing precision and the committed linearity bound "
         "in quadrature",
         "this scales any detuning read on the archive's own axis, so at the "
         "megahertz scale of a line it is tens of kilohertz and cannot reach "
         "the gigahertz scale of the 5 pm target",
         "results/ruler_blocks.csv, results/ruler_campaign.csv")
    _add(rows, "proj_magic_776_usable_half_span", "blue side", span_nm, None, "nm",
         "the magic wavelength minus the 5P3/2 to 5D5/2 pole",
         "a symmetric scan cannot cross the pole, so the pole sets the half "
         "span and the red side is not the limit",
         "docs/FUTURE_TRANSITIONS_titsapph.md 3.3")

    for n_points in (9, 21):
        step = 2 * span_nm / (n_points - 1)
        frac = HAMILTON_MAGIC_ERR_NM * np.sqrt(n_points) / span_nm
        label = f"{n_points} points"
        assumptions = (
            f"a symmetric scan of {n_points} points across plus and minus "
            f"{span_nm:.3f} nm of the crossing, the shift observable linear in "
            "wavelength over that span, and the perturbing beam mode matched to "
            "the drive so the closed-form shift distribution still holds")
        _add(rows, "proj_magic_776_scan_step", label, step, None, "nm",
             "twice the half span divided by the number of intervals",
             assumptions, "docs/FUTURE_TRANSITIONS_titsapph.md 3.1")
        _add(rows, "proj_magic_776_point_precision", label, frac, None,
             "fraction of the shift at the span edge",
             "target wavelength uncertainty times sqrt(points) divided by the "
             "half span, from the zero-crossing error of a centred linear fit",
             assumptions + "; quoted as a fraction because this repository does "
             "not compute the 5D differential polarizability, so the absolute "
             "shift at the span edge is not available here",
             "docs/FUTURE_TRANSITIONS_titsapph.md 3.3")

    _add(rows, "proj_magic_776_archive_width_precision", "per block",
         inp["rel_block"], None, "fraction",
         "the archive's demonstrated per-condition relative width precision",
         "the closest committed analogue to a per-point precision on a shift "
         "observable, and a different observable, so it bounds the comparison "
         "rather than settling it",
         "results/linefit_conditions.csv")


# --------------------------------------------------------------------------- #
# 6. The guided-mode option                                                     #
# --------------------------------------------------------------------------- #
def project_guided(rows) -> None:
    s0_at_power = lineshape.stark_shift_S0_mhz(
        GUIDED_POWER_W, GUIDED_MODE_RADIUS_M, GUIDED_RHO, GUIDED_DELTA_ALPHA_AU)
    gamma_nat_mhz = K.GAMMA_NAT_HZ / 1e6
    ceiling_mw = 1e3 * GUIDED_POWER_W * gamma_nat_mhz / s0_at_power

    _add(rows, "proj_guided_count_rate", "hot fill at the usable power",
         GUIDED_HOT_FILL_COUNTS_PER_S, None, "counts per s",
         "the design note's first-principles rate chain at 100 C over 10 cm of "
         "filled fibre, carried rather than recomputed",
         "a 10 um mode radius, perfect counter-propagating overlap, and the "
         f"note's own open anchor gap of {GUIDED_ANCHOR_GAP[0]} to "
         f"{GUIDED_ANCHOR_GAP[1]} between the first-principles rate and the "
         "archive's detected photons, which divides this figure",
         "docs/notes/guided_mode_two_photon_design.md 2.2")
    _add(rows, "proj_guided_power_ceiling", "S0 equals the natural width",
         ceiling_mw, None, "mW",
         "the power at which the on-axis shift equals the 6S natural width, "
         "recomputed from the module the note used",
         "a 10 um mode radius and unit overlap, and the note's reading that "
         "light shift rather than available power sets the ceiling",
         "rb5s6s.lineshape, docs/notes/guided_mode_two_photon_design.md 2.2")


def main() -> int:
    inp = read_inputs()
    rows = _rows_out()

    pull = project_pull(rows, inp)
    beta = project_beta(rows, inp)
    project_7s(rows, beta)
    project_778(rows, beta)
    project_magic(rows, inp)
    project_guided(rows)

    out = C.RESULTS_DIR / "projections.csv"
    fields = ["quantity", "key", "value", "err", "unit", "formula",
              "assumptions", "source"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print("PROJECTIONS. What a further campaign would buy, at the current "
          "calibration.\n")
    print(f"  per-trace centre precision   {inp['sigma_centre_transition']:.3f} MHz "
          "transition, from the archive's own epoch-offset fit")
    print(f"  block width scatter          {inp['sigma_width_block']:.4f} MHz, "
          f"cut to {inp['sigma_width_block'] / PLAN_BLOCK_NOISE_CUT:.4f} by "
          "interleaving")
    print(f"  ruler spacing precision      {inp['ruler_rel']:.2%} per block")
    print(f"  pull channel, one cycle      {pull['sigma_s0_cycle']:.3f} MHz on "
          f"S0(225 mW), against a predicted {pull['s0_pred']:.3f}")
    print(f"  beta_self, five blocks       {beta['sigma_beta_mhz'] * 1e3:.3f} kHz "
          f"per 1e12, a {beta['detect']:.1f} sigma reach on the expected 3.5\n")
    print(f"wrote {out.relative_to(ROOT)} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

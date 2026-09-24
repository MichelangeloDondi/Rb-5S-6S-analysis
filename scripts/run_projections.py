#!/usr/bin/env python3
"""
What a further measurement campaign would buy, as computed projections.

WHO ACTS ON THIS AND WHAT CHANGES FOR THEM. The reader is the host deciding
bench time. Today the case for a session is carried by prose ("converts bounds
into measurements", "3 to 12 sigma"). This script replaces each of those
sentences with a number derived from the dataset's own measured precision and
the design parameters `docs/PLAN.md` already states, so the decision is read off
a table instead of off an adjective. Eight families are projected: the fixed-lock
pull channel, beta_self, the drive sources and what they deliver, the Doppler
pedestal as a wide-scan add-on, the 7S adjudication, the 778 nm calibration
rung, the magic-wavelength scan, and the guided-mode option.

THERE IS NO LIGHT-SHIFT CEILING HERE, AND THERE WAS ONE UNTIL 2026-09-18 (owner
order O32). Sections 3 to 5 published a drive power at which the on-axis shift
reaches a tenth of the line width, called it a ceiling the bench must stay under,
and carried a second reading of the 7S and 778 precisions derated to it. The
construct is retracted. This record MODELS the light shift: the ramp is a term of
the forward model, its higher moments are the main aim's own channel, and the S0
channel is a measurement rather than a nuisance, so a tenth of a width is signal
and not a limit. It also inverted with the waist -- at 40 to 45 microns the
"ceiling" falls below the archive's own 225 mW, which would make the dataset
illegal by its own table. What does bound the drive power is saturation, the
companion line, depletion and the ruler, each of which the model carries, and
each of which is accounted for in its own place rather than as one number here.

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
calibration, with no edit to this file. That re-run is the author's second pass
and is the only action the correction requires here.

INPUTS, all committed:
  results/stark_centres.csv          per-trace centre precision
  results/linefit_conditions.csv     block-to-block width scatter
  results/ruler_blocks.csv           per-block ruler spacing precision
  results/ruler_campaign.csv         ruler linearity bound
  results/beta_self_probe.csv        the four-point construction's t quantile
  results/qc_metrics.csv             the per-trace peak signal to noise
  rb5s6s.density                     the density lever
  rb5s6s.lineshape, rb5s6s.constants the ramp moments and the predicted shift
  rb5s6s.vanderwaals                 the anchored beta_self expectation
  rb5s6s.polarizability (via CSV)    the two disputed polarizability signs
  rb5s6s.polarizability              the per-rung differential polarizabilities
  docs/PLAN.md                       the stated session parameters
  docs/lit/zameroski2014.md, wang2025.md, cao2025.md, hamilton2023.md
  docs/lit/feng2026.md, li2024b.md, poulin2002.md   the 778 nm source class
  docs/FUTURE_TRANSITIONS_titsapph.md 3.3   the Hamilton-anchored 5D construction
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
from rb5s6s import density, lineshape, polarizability as pol, vanderwaals   # noqa: E402
from rb5s6s.stark import kappa_pred_per_watt   # noqa: E402  (SSOT: one predicted coefficient)

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
PLAN_COLD_SPOT_LAG_K = 20         # PLAN 8 item 3, the dataset's face-value lag
PLAN_INTENSITY_AXIS_FRAC = 0.15   # PLAN 5, the differential-transit anchor
PLAN_MORNING_CYCLES = 24          # PLAN 9 D4, a four-hour morning at PLAN_CYCLE_MIN

# The dataset's own power ladder, which sets the span of the projected grid.
RECORD_P_MIN_W, RECORD_P_MAX_W = 0.025, 0.225
QUOTE_P_W = 0.225                 # the campaign maximum every bound is quoted at

# The density-scale systematic the recorded bound already folds in.
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

# --------------------------------------------------------------------------- #
# The Doppler pedestal: the wide-scan add-on and its two observables.           #
#                                                                               #
# The retro-reflected drive makes two kinds of two-photon event. One photon      #
# from each beam gives the Doppler-free line the dataset fits. Two photons from  #
# the SAME beam give a line first-order Doppler broadened at 2 k v, which is     #
# near a gigahertz here and sits under the narrow line as a pedestal. The        #
# pedestal is not a nuisance. It carries two numbers this record currently       #
# assumes: its width is a thermometer for the atoms actually in the beam, and    #
# its area against the narrow line's area measures the retro ratio.              #
#                                                                               #
# The design below is one acquisition change and no new hardware: the same       #
# 2000-point, one-second trace the dataset already takes, swept over a wide      #
# span instead of a narrow one. No lock quality is required, because a width     #
# of a gigahertz does not care about a megahertz of drift.                       #
# --------------------------------------------------------------------------- #
WIDE_SCAN_SPAN_LASER_GHZ = 5.0    # laser axis, so 10 GHz on the transition axis
WIDE_SCAN_T_C = 130               # the dataset's own top block, where the SNR is quoted
WIDE_SCAN_ISOTOPE_KG = K.M_RB85_KG   # the abundant isotope sets the design pedestal

# Delivered drive power of record for each named source class. The bench's own
# figure is QUOTE_P_W, the dataset's ladder maximum through the cell. The 778 nm
# figure is what a held demonstration of the fibre-amplifier architecture puts
# on its cell, which is a floor under the class and not its maximum.
FENG_778_DELIVERED_W = 0.030      # docs/lit/feng2026.md

# The guided-mode design note's own working point.
GUIDED_MODE_RADIUS_M = 10e-6     # notes/guided_mode_two_photon_design.md 2.2
GUIDED_POWER_W = 0.100
GUIDED_RHO = 1.0
GUIDED_DELTA_ALPHA_AU = abs(K.DELTA_ALPHA_AU)   # read by NAME, never copied:
# this line was a literal copy of the static-tail value for months and was one of the twelve edits
# the 2026-09-15 polarizability move needed. ssot_guard.py refuses the copy now.


def _rows_out():
    return []


def _add(rows, quantity, key, value, err, unit, formula, assumptions, source):
    rows.append(dict(quantity=quantity, key=key,
                     value=f"{value:.6g}" if value is not None else "",
                     err=f"{err:.6g}" if err is not None else "",
                     unit=unit, formula=formula, assumptions=assumptions,
                     source=source))


# --------------------------------------------------------------------------- #
# Inputs read live from the committed record                                    #
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

    qc = pd.read_csv(C.RESULTS_DIR / "qc_metrics.csv")
    peak_snr = float(qc[qc.flag == "canonical"].snr.median())


    return dict(
        sigma_centre_laser=sigma_centre_laser,
        sigma_centre_transition=2.0 * sigma_centre_laser,
        rel_block=rel_block, width_mean=width_mean,
        sigma_width_block=width_mean * rel_block,
        ruler_rel=ruler_rel, linearity_rel=linearity_rel,
        rate_laser_mhz_per_ms=float(rc.rate_laser), peak_snr=peak_snr,
        t95_four_point=t95_four_point)


def density_lever(grid_c, lag_k: int) -> float:
    """sqrt(sum of squared deviations of N about its mean) over the T grid, in
    units of 1e12 cm^-3. This is the denominator of a least-squares slope, so a
    width uncertainty divided by it is the uncertainty on beta_self."""
    n = np.array([float(density.number_density_cm3(t - lag_k)) for t in grid_c]) / 1e12
    return float(np.sqrt(((n - n.mean()) ** 2).sum()))


def power_lever(n_points: int) -> float:
    """sqrt(sum of squared deviations of P about its mean) over a log grid
    spanning the dataset's own ladder, in W. The denominator of the pull slope."""
    p = np.geomspace(RECORD_P_MIN_W, RECORD_P_MAX_W, n_points)
    return float(np.sqrt(((p - p.mean()) ** 2).sum()))


def sigma_new_for_separation(gap: float, sigma_published: float,
                             n_sigma: float) -> float:
    """Largest new-measurement uncertainty that still separates two published
    values by `n_sigma`, given the larger of their own errors. Solves
    gap / sqrt(sigma_new^2 + sigma_published^2) = n_sigma. Returns nan where the
    published errors alone already exhaust the gap."""
    inside = (gap / n_sigma) ** 2 - sigma_published ** 2
    return float(np.sqrt(inside)) if inside > 0 else float("nan")


def rung_wavelength_nm(e_upper_cm: float) -> float:
    """Two-photon drive wavelength of a 5S to upper-state rung, nm in vacuum.
    Two photons share the term energy, so lambda = 2e7 / E[cm^-1]. The term
    energies are the NIST values rb5s6s.polarizability already carries."""
    return 2e7 / e_upper_cm


# The three rungs, each with the differential polarizability it is entitled to.
RUNGS = (
    ("993 nm, 5S to 6S", pol.E_6S_CM, lambda lam: K.DELTA_ALPHA_AU,
     "rb5s6s.constants.DELTA_ALPHA_AU, the dynamic sum of results/polarizability_deep.csv"),
    ("760 nm, 5S to 7S", pol.E_7S_CM, pol.delta_alpha_7s,
     "rb5s6s.polarizability.delta_alpha_7s"),
    ("778 nm, 5S to 5D5/2", pol.E_5D52_CM, pol.delta_alpha_5d,
     "docs/FUTURE_TRANSITIONS_titsapph.md 3.3, docs/lit/hamilton2023.md"),
)


def delivered_rate(inp, beta_out, scale: float, cm3_per_mtorr: float) -> float:
    """Self-broadening precision the five-block design delivers, kHz per mTorr,
    when the SNR-limited part of the per-block width uncertainty is multiplied
    by `scale`. The ruler axis term is a calibration of the frequency axis and
    does not move with signal, so it is held."""
    sigma_w = float(np.hypot(inp["sigma_width_block"] / PLAN_BLOCK_NOISE_CUT * scale,
                             inp["ruler_rel"] * inp["width_mean"]))
    return sigma_w / beta_out["lever_lag"] * cm3_per_mtorr / 1e12 * 1e3


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

    # ONE PREDICTED COEFFICIENT (2026-09-17): the record's prediction per recorded watt carries the
    # aperture's on-axis factor, so both signs are evaluated through it. Until that day this read
    # stark_shift_S0_mhz without the factor, and the other sign's arm read the static-tail
    # recompute's magnitude where its own note named Orson's +1093 (P7).
    s0_pred = kappa_pred_per_watt(K.W0_CENTRAL_M, K.RHO_RETRO) * QUOTE_P_W
    s0_pred_other_sign = (lineshape.stark_shift_S0_mhz(
        QUOTE_P_W, K.W0_CENTRAL_M, K.RHO_RETRO, K.DELTA_ALPHA_AU_ORSON2021)
        * lineshape.aperture_onaxis_factor_actual(K.W0_CENTRAL_M))
    sign_gap = s0_pred + s0_pred_other_sign

    _add(rows, "input_centre_precision_per_trace", "archive", 2.0 * inp["sigma_centre_laser"],
         None, "MHz, transition axis",
         "2 x resid_mhz of the epoch-offset linear-drift fit",
         "conservative: measured under the 2025 drifting lock, so it still "
         "carries uncorrected drift that a fixed lock removes",
         "results/stark_centres.csv")
    _add(rows, "input_lock_drift_rate", "held lock", 2.0 * PLAN_LOCK_DRIFT_LASER_MHZ_PER_MIN,
         None, "MHz per min, transition axis",
         "2 x the held-lock bound of PLAN 2",
         "the record's own held-lock bound, not the borrowed cavity figure of "
         "Ayachitula 2024 and not the photographed cavity-locked rate",
         "docs/PLAN.md 2, docs/APPARATUS.md 6")
    _add(rows, "input_ramp_pull_coefficient", "config L", pull_coeff, None,
         "dimensionless",
         "mean of the axially averaged ramp over S0, at Z_c / z_R",
         f"config L waist {PLAN_W0_CONFIG_L_M * 1e6:.0f} um and collection "
         f"half-window {PLAN_ZC_CONFIG_L_M * 1e3:.2f} mm, PLAN 4.1 and PLAN 6",
         "rb5s6s.lineshape.ramp_moment_contributions")
    _add(rows, "input_S0_predicted", "225 mW", s0_pred, None, "MHz, transition axis",
         "stark.kappa_pred_per_watt times the quoted power, at the waist convention and retro ratio",
         "the prediction the recorded bound is compared against",
         "rb5s6s.stark.kappa_pred_per_watt")
    _add(rows, "input_intensity_axis_systematic", "differential transit anchor",
         PLAN_INTENSITY_AXIS_FRAC, None, "fraction",
         "the intensity-axis accuracy PLAN 5 attributes to the S minus L "
         "transit width difference measured to 5 to 7 percent",
         "adopted from PLAN rather than re-derived, and read as one sigma",
         "docs/PLAN.md 5")
    _add(rows, "input_density_scale_systematic", "archival", N_SCALE_FRAC, None,
         "fraction",
         "the density-scale systematic the recorded bound already folds in",
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
            f"{PLAN_N_POWERS} rungs log spaced over the dataset's own "
            f"{RECORD_P_MIN_W * 1e3:.0f}-{RECORD_P_MAX_W * 1e3:.0f} mW ladder, "
            f"one trace per rung, {PLAN_N_PEAKS} peaks interleaved, config L, "
            "centre precision at the dataset's per-trace value, lock drift at "
            "the held-lock bound and common to the four peaks of a cycle")
        _add(rows, "proj_pull_S0_sigma", label, sigma, None, "MHz, transition axis",
             "0.225 x sqrt(sigma_centre^2 / (4 Spp) + sigma_drift^2 / Spp) "
             "/ |mean/S0| / sqrt(cycles), Spp the power lever",
             common, "docs/PLAN.md 9 D4, PLAN 7, PLAN 10.4")
        _add(rows, "proj_pull_S0_over_prediction", label, s0_pred / sigma, None,
             "sigma",
             "predicted S0(225 mW) divided by the projected uncertainty",
             common + ". prediction at the committed waist convention",
             "results/stark_joint.csv S0_225mW_pred")
        _add(rows, "proj_deltaalpha_frac", label, frac_da, None, "fraction, 1 sigma",
             "quadrature sum of the fractional shift uncertainty and the "
             "intensity-axis systematic",
             common + f". intensity axis anchored to {PLAN_INTENSITY_AXIS_FRAC:.0%} "
             "by the differential transit width of PLAN 5",
             "docs/PLAN.md 5")
        _add(rows, "proj_deltaalpha_sign_separation", label, sign_gap / sigma, None,
             "sigma",
             "|S0(+Delta-alpha) - S0(-Delta-alpha)| divided by the projected "
             "uncertainty, both evaluated at the waist convention",
             common + ". the two signs are Orson 2021's +1093 a.u. and this "
             "record's own, both through the aperture's on-axis factor at the waist convention "
             "prior, so a common intensity-scale error moves the separation "
             "even though it cannot move which sign the pull has",
             "rb5s6s.constants DELTA_ALPHA_AU and DELTA_ALPHA_AU_ORSON2021")

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
         f"the dataset's block scatter divided by {PLAN_BLOCK_NOISE_CUT:.0f}",
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
         "which is the dataset's own face-value preference",
         "rb5s6s.density, docs/PLAN.md 7 and 8")
    _add(rows, "input_density_lever", "no lag", lever_nolag, None, "1e12 cm^-3",
         "the same sum with densities read at the nominal set points",
         "the optimistic end, valid only if the cold spot is absent",
         "rb5s6s.density")
    _add(rows, "input_beta_self_expected", "vdW anchored", anchor["beta6_khz"],
         vanderwaals.beta_self_budget()["err_khz"], "kHz per 1e12 cm^-3",   # the SSOT budget's bar (10.64 per cent), not the anchor's own (F38)
         "the measured 7S rate carried across one rung by the computed "
         "difference-coefficient ratio (Delta C6, the 2026-08-05 adjudication "
         "in docs/notes/vdw_difference_potential_and_4d_channel.md)",
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
                 assumptions + ". the density-scale systematic does not enter a "
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
# 3. The drive sources on each rung and the power each class delivers          #
# --------------------------------------------------------------------------- #


def project_sources(rows) -> None:
    """One row per rung naming the viable source class and the power it delivers.

    The question these answer is which rungs need the titanium sapphire and which a
    diode class already reaches. Until 2026-09-18 the row divided that power by a
    retracted "light-shift ceiling" (O32), which made the answer a ratio to a limit
    this record does not have; it is the delivered power itself now."""
    classes = (
        ("993 nm, 5S to 6S",
         "the titanium sapphire on the bench, or a diode-seeded ytterbium "
         "fibre amplifier at its band edge",
         QUOTE_P_W, "the dataset's own delivered ladder maximum",
         "Power still buys signal on this rung, so the titanium sapphire is not "
         "made unnecessary. The "
         "ytterbium fibre alternative would run at the short-wavelength edge "
         "of its gain band, and no held source in this repository states a "
         "delivered power there, so that reach is UNCERTAIN and the headroom "
         "below is the titanium sapphire's",
         "docs/PLAN.md 9 D4, results/linefit_conditions.csv"),
        ("760 nm, 5S to 7S",
         "an extended-cavity diode with a tapered amplifier",
         QUOTE_P_W, "the dataset's own delivered ladder maximum",
         "The delivered power below is already ample on this rung, so the "
         "titanium sapphire is unnecessary here. The named "
         "class is established practice at 760 nm rather than a claim from a "
         "held source: no note in docs/lit states a tapered-amplifier output "
         "at this wavelength, which is the LIT GAP here, so what is quantified "
         "is the requirement the class has to clear",
         "docs/FUTURE_TRANSITIONS_titsapph.md 2"),
        ("778 nm, 5S to 5D5/2",
         "a 1556 nm fibre amplifier with second-harmonic generation",
         FENG_778_DELIVERED_W, "a held demonstration of that architecture",
         "This is the compact-clock community's own architecture on this line, "
         "stated in a held and verified note: a 1556.2 nm fibre laser doubled "
         "in periodically poled lithium niobate, 30 mW on the cell. The same "
         "architecture appears in a second held note. The delivered power is "
         "that demonstration's operating point rather than the class maximum, "
         "so the headroom below is a floor. The titanium sapphire is "
         "unnecessary on this rung",
         "docs/lit/feng2026.md, docs/lit/li2024b.md, docs/lit/poulin2002.md"),
    )
    for label, source_class, delivered_w, power_source, note, cite in classes:
        # WHAT THE BENCH DELIVERS, AND NOT WHAT IT MAY NOT EXCEED (owner, 2026-09-17, O32). This row
        # divided the delivered power by a "light-shift ceiling" until 2026-09-18. That construct is
        # retracted: this record MODELS the light shift, its ramp is a term of the forward model and
        # its higher moments are the main aim's own channel, so a tenth of a line width is signal and
        # not a limit. What actually bounds the drive power is saturation, the companion line,
        # depletion and the ruler, each of which the model carries and none of which is a ceiling.
        _add(rows, "proj_source_delivered_power", f"{label}, {source_class}",
             delivered_w * 1e3, None, "mW",
             "the class's demonstrated drive power on the cell",
             f"{power_source}. " + note, cite)


def doppler_pedestal_fwhm_mhz(t_c: float, mass_kg: float) -> float:
    """FWHM of the co-propagating two-photon pedestal, MHz on the TRANSITION
    axis. Both photons come from one beam, so the resonance moves with the full
    2 k v and the width is 2 sqrt(8 ln2 kT/m) / lambda."""
    v = np.sqrt(8.0 * np.log(2.0) * K.K_B_J_PER_K * (t_c + 273.15) / mass_kg)
    return 2.0 * v / K.LAMBDA_LASER_M / 1e6


def narrow_to_pedestal_ratio(rho: float) -> float:
    """Integrated Doppler-free area divided by integrated pedestal area.

    The positive-frequency field is E_f exp(ikz) + E_r exp(-ikz), and the
    two-photon amplitude is its square, which has three terms: exp(2ikz) and
    exp(-2ikz), each Doppler shifted by 2 k v, and a cross term with no z
    dependence, which is the Doppler-free line. Squaring for the rate gives
    I_f^2 + I_r^2 under the pedestal against 4 I_f I_r under the narrow line, so
    with rho the retro POWER ratio the ratio is 4 rho / (1 + rho^2). At rho = 1
    it is 2, which is the textbook factor between the Doppler-free signal and
    its background for equal counter-propagating beams."""
    return 4.0 * rho / (1.0 + rho ** 2)


def d_ratio_d_rho(rho: float) -> float:
    """Derivative of the area ratio with respect to the retro power ratio. It
    vanishes at rho = 1, which is the whole difficulty of this channel."""
    return 4.0 * (1.0 - rho ** 2) / (1.0 + rho ** 2) ** 2


# --------------------------------------------------------------------------- #
# 2b. The rungs' own drive wavelength: polarizability and waist                 #
# --------------------------------------------------------------------------- #
def project_rungs(rows) -> None:
    """Per rung, the differential polarizability at its own drive and the waist that drive reaches.

    RESTORED 2026-09-18. These two rows predate the light-shift ceiling and are
    independent of it, but they were emitted from inside the loop that computed it,
    so stripping the retracted ceiling (O32) took them out with it and left RUNGS
    consumed by nothing. A reference in FUTURE_TRANSITIONS went DANGLING and that is
    how the loss was found, which is the anti-staleness contract doing its job on its
    author. The waist is a function of the drive wavelength and not a property of the
    bench alone, w0 = lambda f / (pi w_in), so a rung evaluated at the 993 nm waist
    describes a focus no single lens reaches (A137)."""
    for label, _e_cm, d_alpha_fn, source in RUNGS:
        lam = 1e7 / _e_cm * 2.0
        d_alpha = abs(float(d_alpha_fn(lam)))
        w0_drive = K.waist_at_drive(lam, input_beam="aperture")
        w0_drive_alt = K.waist_at_drive(lam, input_beam="resonator")
        _add(rows, "input_rung_delta_alpha", label, d_alpha, None, "a.u.",
             "magnitude of alpha(upper) minus alpha(5S) at the rung's own "
             "two-photon drive wavelength",
             f"drive wavelength {lam:.3f} nm from the NIST term energy. The "
             "993 nm value is the module's own recompute, whose sign is under "
             "dispute and whose magnitude sits 5 percent above the pinned "
             f"{K.DELTA_ALPHA_AU:.0f} a.u. of record. The 778 nm value is "
             "scalar only",
             source)
        _add(rows, "input_rung_waist_at_drive", label, w0_drive * 1e6, None, "um",
             "the reference waist scaled to this rung's own drive wavelength "
             "through the same lens and the same input beam",
             f"rb5s6s.constants.waist_at_drive, aperture-limited input beam, "
             f"the f = {K.DRIVE_LENS_F_M * 1e3:.0f} mm plano-convex L1 with its "
             f"own dispersion, focal length {K.drive_lens_focal_m(lam) * 1e3:.2f} "
             f"mm here. The unclipped-resonator reading is "
             f"{w0_drive_alt * 1e6:.2f} um and the pair brackets the input-beam "
             "regime the record does not pin (A136)",
             "rb5s6s.constants.waist_at_drive, docs/APPARATUS.md 1.2")


# --------------------------------------------------------------------------- #
# 4. The Doppler pedestal as a campaign observable                              #
# --------------------------------------------------------------------------- #
def project_pedestal(rows, inp) -> None:
    """Two observables from one wide scan: the pedestal width as an in-situ
    thermometer, and the narrow-to-pedestal area ratio as an in-situ retro
    ratio. Both are quoted per single one-second scan and as the stacking time
    that reaches the number each would replace."""
    span_mhz = 2e3 * WIDE_SCAN_SPAN_LASER_GHZ          # transition axis
    dnu = span_mhz / K.TRACE_N_POINTS                  # per-point spacing, MHz
    scan_s = K.TRACE_N_POINTS * K.TRACE_DT_S           # seconds per scan

    w_ped = doppler_pedestal_fwhm_mhz(WIDE_SCAN_T_C, WIDE_SCAN_ISOTOPE_KG)
    s_ped = w_ped / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    w_narrow = inp["width_mean"]
    snr = inp["peak_snr"]
    ratio = narrow_to_pedestal_ratio(K.RHO_RETRO)
    slope = abs(d_ratio_d_rho(K.RHO_RETRO))

    # Pedestal peak height in units of the per-point noise. Equal areas, so the
    # height falls by the width ratio and by the area ratio together. Both
    # profiles are given the Gaussian area factor, which cancels.
    snr_ped = snr * w_narrow / (ratio * w_ped)

    # Gaussian least squares on white noise with amplitude, centre and width
    # free. Centre is orthogonal by symmetry, amplitude is not, and marginalising
    # over it is the factor of three between these two expressions.
    frac_width = (1.0 / snr_ped) * np.sqrt(8.0 * dnu / (np.sqrt(np.pi) * s_ped))
    frac_area = (1.0 / snr_ped) * np.sqrt(3.0 * dnu / (np.sqrt(np.pi) * s_ped))

    frac_t = 2.0 * frac_width                    # T goes as the width squared
    sigma_rho = ratio * frac_area / slope

    # The density curve's own leverage: how hard a fractional error in the
    # temperature hits the number density it implies.
    h = 0.01
    dlnn_dlnt = float(
        (np.log(density.number_density_cm3(WIDE_SCAN_T_C + h))
         - np.log(density.number_density_cm3(WIDE_SCAN_T_C - h))) / (2.0 * h)
        * (WIDE_SCAN_T_C + 273.15))

    frac_t_target = N_SCALE_FRAC / dlnn_dlnt
    hours_t = scan_s * (frac_t / frac_t_target) ** 2 / 3600.0
    hours_rho = scan_s * (sigma_rho / K.RHO_RETRO_ERR) ** 2 / 3600.0
    comb_gain = float(PLAN_N_PEAKS)              # four pedestals, one width

    comb_caveat = (
        "the four hyperfine components sit about a gigahertz apart on the laser "
        "axis and their pedestals are near a gigahertz wide, so what is fitted "
        "is a four-pedestal comb and not one Gaussian. The splittings are known "
        "to kilohertz and the relative amplitudes are measured in "
        "results/amplitude_ratios.csv, so the comb is fittable, and the row is "
        "the conservative end: the summed pedestal is four times the mean "
        "single-peak one, which is a factor of four in amplitude and sixteen in "
        "session length, against the comb's own spread correlating with the "
        "width it is there to measure")
    design = (
        f"one {scan_s:.0f} s trace of {K.TRACE_N_POINTS} points swept over "
        f"{WIDE_SCAN_SPAN_LASER_GHZ:.0f} GHz on the laser axis, which is "
        f"{span_mhz / 1e3:.0f} GHz on the transition axis and covers the "
        "hyperfine comb with about one pedestal width of clean wing on each "
        "side, at the dataset's own per-point dwell and at its quoted drive "
        f"power, which is bounded by saturation, the companion line, depletion and "
        "the ruler rather than by any light-shift limit. White noise at "
        "the dataset's own per-trace level and nothing else: a broad low "
        "feature also has to be separated from the scattered-light background, "
        "which this projection does not model")

    _add(rows, "input_pedestal_width", f"{WIDE_SCAN_T_C} C, 85Rb", w_ped, None,
         "MHz, transition axis",
         "2 sqrt(8 ln2 kT / m) / lambda, the full 2 k v first-order Doppler "
         "width of the co-propagating two-photon line",
         "the abundant isotope at the dataset's own top temperature block. The "
         "width goes as the square root of the temperature, which is what makes "
         "it a thermometer",
         "rb5s6s.constants")
    _add(rows, "input_record_scan_span", "one archival trace",
         2e3 * inp["rate_laser_mhz_per_ms"] * K.TRACE_N_POINTS * K.TRACE_DT_S,
         None, "MHz, transition axis",
         "twice the campaign sweep rate times the one-second acquisition window",
         "this is why the dataset cannot do either measurement. The window is a "
         "small fraction of the pedestal width, so the dataset samples only the "
         "pedestal's flat top, which its linear baseline absorbs. The dataset "
         "can bound the retro ratio through that offset and cannot fit the "
         "width at all",
         "results/ruler_campaign.csv, rb5s6s.constants")
    _add(rows, "input_peak_snr", "canonical traces", snr, None, "dimensionless",
         "median over the canonical traces of the fitted height divided by the "
         "wing noise",
         "a median over the whole power ladder rather than a value at the "
         "quoted power, so it is the conservative end",
         "results/qc_metrics.csv")
    _add(rows, "input_narrow_to_pedestal_ratio", "at the adopted retro ratio",
         ratio, None, "dimensionless",
         "4 rho / (1 + rho^2), integrated areas",
         f"at the adopted rho = {K.RHO_RETRO:.2f}. The function peaks at rho = 1 "
         f"where its slope vanishes, and here the slope is {slope:.3f} per unit "
         "rho, so the ratio is a weak lever on the very quantity it measures. "
         "It is also symmetric under rho to 1/rho, resolved only by the physical "
         "fact that a retro beam loses power",
         "rb5s6s.constants RHO_RETRO")
    _add(rows, "input_density_temperature_leverage", f"{WIDE_SCAN_T_C} C",
         dlnn_dlnt, None, "dimensionless",
         "d ln n / d ln T on the committed vapour-pressure curve",
         "a fractional temperature error is amplified by this factor into the "
         "number density, which is what makes an in-situ thermometer worth "
         "having and also what makes it expensive",
         "rb5s6s.density")

    _add(rows, "proj_pedestal_frac_T", "one wide scan", frac_t, None,
         "fraction, 1 sigma",
         "twice the fractional Gaussian width precision, (1/SNR_pedestal) "
         "sqrt(8 dnu / (sqrt(pi) sigma_pedestal)), amplitude and centre free",
         design + ". " + comb_caveat, "results/qc_metrics.csv")
    _add(rows, "proj_pedestal_frac_T", "one wide scan, four-pedestal comb",
         frac_t / comb_gain, None, "fraction, 1 sigma",
         "the same with the pedestal amplitude multiplied by the number of "
         "hyperfine components",
         design + ". " + comb_caveat, "results/amplitude_ratios.csv")
    _add(rows, "proj_pedestal_thermometry_hours", "to match the density scale",
         hours_t, None, "hours",
         "the stacking time at which the fractional temperature precision "
         "reaches the density-scale systematic divided by the vapour curve's "
         "own leverage",
         design + ". This is what the thermometer would and would not settle: "
         "it measures the kinetic temperature of the atoms in the beam, so it "
         "pins the T that enters the density curve. It does not measure the "
         "cold spot, which is a different surface, so the cold-spot lag needs "
         "this together with an absorption measurement of the density itself. "
         + comb_caveat, "rb5s6s.density, results/beta_self_probe.csv")
    _add(rows, "proj_pedestal_thermometry_hours",
         "to match the density scale, four-pedestal comb",
         hours_t / comb_gain ** 2, None, "hours",
         "the same with the comb's summed amplitude, so sixteen times shorter",
         design + ". " + comb_caveat, "results/amplitude_ratios.csv")

    _add(rows, "proj_pedestal_sigma_rho", "one wide scan", sigma_rho, None,
         "1 sigma on the retro power ratio",
         "the fractional area precision (1/SNR_pedestal) sqrt(3 dnu / (sqrt(pi) "
         "sigma_pedestal)) times the ratio, divided by the ratio's slope in rho",
         design + ". " + comb_caveat, "results/qc_metrics.csv")
    _add(rows, "proj_pedestal_sigma_rho", "one wide scan, four-pedestal comb",
         sigma_rho / comb_gain, None, "1 sigma on the retro power ratio",
         "the same with the comb's summed amplitude",
         design + ". " + comb_caveat, "results/amplitude_ratios.csv")
    _add(rows, "proj_pedestal_rho_hours", "to match the adopted prior", hours_rho,
         None, "hours",
         "the stacking time at which the projected sigma on rho reaches the "
         "adopted prior's own uncertainty",
         design + f". The adopted prior is {K.RHO_RETRO:.2f} +/- "
         f"{K.RHO_RETRO_ERR:.2f} and is not a measurement on this bench, so "
         "matching it converts an assumption into a same-trace number rather "
         "than improving on one. " + comb_caveat,
         "rb5s6s.constants RHO_RETRO_ERR")
    _add(rows, "proj_pedestal_rho_hours",
         "to match the adopted prior, four-pedestal comb",
         hours_rho / comb_gain ** 2, None, "hours",
         "the same with the comb's summed amplitude, so sixteen times shorter",
         design + ". " + comb_caveat, "results/amplitude_ratios.csv")


# --------------------------------------------------------------------------- #
# 5. The 7S adjudication                                                        #
# --------------------------------------------------------------------------- #
def project_7s(rows, inp, beta_out) -> None:
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
             assumptions + ". the projection is the same five-block design as "
             "the 993 nm row, run on the 760 nm line",
             "results/projections.csv proj_7s_precision_delivered")
        _add(rows, "proj_7s_averaging_to_margin_one", label,
             max(1.0, (delivered / needed) ** 2), None, "sessions",
             "the square of the shortfall in margin, floored at one, which is "
             "the number of repeats of the five-block design that brings the "
             "margin to one",
             "the same five-block design at the dataset's own drive power",
             "results/projections.csv proj_7s_margin")

    _add(rows, "proj_7s_precision_delivered", "same-instrument session", delivered,
         None, "kHz/mTorr",
         "the projected beta_self uncertainty converted at Zameroski's own "
         "403 K density scale",
         "the same five-block interleaved design as the 993 nm projection, with "
         "the dataset's absolute per-block width scatter and per-block ruler "
         "spacing precision carried over unchanged to the 760 nm line, and the "
         "20 K cold-spot lag applied",
         "results/ruler_blocks.csv, results/linefit_conditions.csv, "
         "docs/lit/zameroski2014.md")


# --------------------------------------------------------------------------- #
# 6. The 778 nm calibration rung                                                #
# --------------------------------------------------------------------------- #
def project_778(rows, inp, beta_out) -> None:
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
        _add(rows, "proj_778_averaging_to_margin_one", label,
             max(1.0, (delivered / needed) ** 2), None, "sessions",
             "the square of the shortfall in margin, floored at one, which is "
             "the number of repeats of the five-block design that brings the "
             "margin to one",
             "the same five-block design at the dataset's own drive power",
             "results/projections.csv proj_778_margin")

    _add(rows, "proj_778_precision_delivered", "same-instrument session", delivered,
         None, "kHz/mTorr",
         "the projected beta_self uncertainty converted at Cao's own 423 K "
         "density scale",
         "the same five-block interleaved design as the 993 nm projection, with "
         "the dataset's demonstrated per-condition width precision carried over "
         "unchanged to the 778 nm line, and the 20 K cold-spot lag applied",
         "results/linefit_conditions.csv, docs/lit/cao2025.md")
    _add(rows, "proj_778_precision_delivered_frac", "same-instrument session",
         delivered / cao, None, "fraction of the published value",
         "the projected precision divided by the published coefficient",
         "as above, against Cao's 1.3 percent",
         "docs/lit/cao2025.md")


# --------------------------------------------------------------------------- #
# 7. The magic-wavelength scan                                                  #
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
         "this scales any detuning read on the dataset's own axis, so at the "
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
             assumptions + ". quoted as a fraction because this repository "
             "computes no independent 5D differential polarizability. The "
             "Hamilton-anchored polarizability construction this file uses is "
             "evaluated at the drive wavelength, two nanometres from the "
             "near-resonant pole, and it is not carried to the span edge, "
             "which sits a fifth of a nanometre from that pole where the "
             "single-pole shape is no longer a safe stand-in",
             "docs/FUTURE_TRANSITIONS_titsapph.md 3.3")

    _add(rows, "proj_magic_776_record_width_precision", "per block",
         inp["rel_block"], None, "fraction",
         "the dataset's demonstrated per-condition relative width precision",
         "the closest committed analogue to a per-point precision on a shift "
         "observable, and a different observable, so it bounds the comparison "
         "rather than settling it",
         "results/linefit_conditions.csv")


# --------------------------------------------------------------------------- #
# 8. The guided-mode option                                                     #
# --------------------------------------------------------------------------- #
def project_guided(rows) -> None:
    # THE GUIDED ARM CARRIES ITS SHIFT AS SIGNAL (F147, owner order O32, 2026-09-19). The two rows this
    # function wrote until 2026-09-19 -- the drive power at which the on-axis shift equals the natural
    # width, and a hot-fill count rate carried at that power -- were the light-shift construct the order
    # strips from the cell, under another name in the fibre. Their values stand in private/history/ and
    # in the git history; what remains here is the shift itself at the note's geometry, a quantity of the
    # forward model, so a reader of the guided case sees the size of the term and not a bound on it.
    s0_at_power = lineshape.stark_shift_S0_mhz(
        GUIDED_POWER_W, GUIDED_MODE_RADIUS_M, GUIDED_RHO, GUIDED_DELTA_ALPHA_AU)
    _add(rows, "proj_guided_s0", f"{1e3 * GUIDED_POWER_W:.0f} mW per direction, {1e6 * GUIDED_MODE_RADIUS_M:.0f} um mode radius",
         s0_at_power, None, "MHz",
         "the on-axis AC-Stark shift of the 6S line at the design note's guided geometry, from the module "
         "the cell's own ramp uses. It is a term of the forward model in the fibre exactly as in the cell",
         "a 10 um mode radius, perfect counter-propagating overlap (rho = 1 against the cell's 0.94) and "
         "the pinned polarizability. The drive power is bounded by saturation, depletion, the trap's own "
         "differential shift and the readout's reabsorption, never by this term",
         "rb5s6s.lineshape, docs/notes/guided_mode_two_photon_design.md 2.2")


def main() -> int:
    inp = read_inputs()
    rows = _rows_out()

    pull = project_pull(rows, inp)
    beta = project_beta(rows, inp)
    project_sources(rows)
    project_rungs(rows)
    project_pedestal(rows, inp)
    project_7s(rows, inp, beta)
    project_778(rows, inp, beta)
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
          "transition, from the dataset's own epoch-offset fit")
    print(f"  block width scatter          {inp['sigma_width_block']:.4f} MHz, "
          f"cut to {inp['sigma_width_block'] / PLAN_BLOCK_NOISE_CUT:.4f} by "
          "interleaving")
    print(f"  ruler spacing precision      {inp['ruler_rel']:.2%} per block")
    print(f"  pull channel, one cycle      {pull['sigma_s0_cycle']:.3f} MHz on "
          f"S0(225 mW), against a predicted {pull['s0_pred']:.3f}")
    print(f"  beta_self, five blocks       {beta['sigma_beta_mhz'] * 1e3:.3f} kHz "
          f"per 1e12, a {beta['detect']:.1f} sigma reach on the expected 3.5")
    print()
    print(f"wrote {out.relative_to(ROOT)} with {len(rows)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""The nanofiber candidate, sized: what an ONF measurement would buy this record.

WHY A PRODUCER AND NOT A PARAGRAPH. The campaign prescription ranks candidate
measurements by what uncertainty each removes per unit bench time, and a
candidate argued in prose carries numbers nobody can recompute. Every quantity
in docs/notes/onf_candidate.md comes from this file, every row below carries
its BASIS, and the basis vocabulary is a contract:

    committed_input      read from this repository's constants or results
    cited_literature     an outside number with its citation in the note
    assumed_parameter    an apparatus parameter this repo does not know; the
                         note names the measurement that replaces it
    derived_expectation  arithmetic on the rows above. A PREDICTION, never a
                         measurement, per the rule that a recommendation is
                         measured in data where data exist and labelled an
                         expectation where they do not (protocol 19.65).

THE LINEAGE THIS SITS IN, read before the estimates were made and cited
rather than re-derived. This transition has ALREADY been driven at an optical
nanofibre with cold atoms: docs/lit/rajasree2020spin.md (5S-6S through the
evanescent field of a 400 nm ONF, 25 to 40 counts per millisecond, which is
the measured feasibility anchor this file uses instead of a rate estimate,
plus the polarisation law and the nonparaxial circular-null minimum of ~13
per cent in theory and ~25 per cent in practice) and docs/lit/gokhroo2022.md
(the two-peak pushing profile near the fibre on our exact line, OBSERVED and
never modelled: no fitted lineshape, no Casimir-Polder content). The gap that
audit establishes is a quantitative near-surface LINESHAPE, not a standalone
surface coefficient, and that is what the atom-surface rows below serve.

WHAT IS BEING SIZED. Three distinct instruments one apparatus provides:

  A. COLD ATOMS, TRAP OFF. MOT atoms drifting through the evanescent field.
     Collisions are negligible at MOT density and transit is ~1e2 kHz, so the
     line is natural width (known) + laser contribution + small transit: an
     independent measurement of the laser's width, the identifying rung of
     the intercept ladder that the cell data can only bound.
  B. THE ATOM-SURFACE TAIL. Evanescent excitation samples atoms 50-300 nm
     from silica, where the atom-surface potential shifts 5S and 6S
     differently and red-shifts the line by an amount that depends on
     distance. THE POTENTIAL HAS TWO COMPONENTS, not one:
     docs/lit/pennetta2026.md measures, on this exact class of platform,
     Casimir-Polder attraction PLUS an electrostatic term from surface
     charges on the silica, which is device- and time-dependent and must be
     calibrated per run rather than carried as a universal constant. The
     rows below give the CP part only, with a near-field C3/z^3 scaling that
     crosses over to a retarded C4/z^4 form at larger distance
     (docs/lit/ton2026.md measures that crossover, and reads a kHz-level
     shift out of the lineshape, which is the template here).
  C. HOT VAPOR. Transit becomes ~1e2 MHz and dominates the line, which turns
     the transit KERNEL into the measured object instead of a small
     correction. Hot Rb degrades fiber transmission by adsorption.

A FEASIBILITY BOUND ON ALL THREE, from docs/lit/piotrowski2026.md: probe
light scattering heats nanophotonic-trapped atoms, so near-field probing is
inherently TRANSIENT, with coupling and atom number decaying during the
measurement. The probe powers below are therefore ceilings on an integration
window, not settings that can be held indefinitely.

The Stark geometry is a fourth, free, item: model_profile's `profile` seam
takes a closure over stark_from_intensity_profile with its own intensities and
volume measure, written for exactly this kind of geometry change and never yet
exercised on one.

    python scripts/run_onf_candidate.py
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.constants import (GAMMA_NAT_HZ, W0_MEASURED_M,        # noqa: E402
                              RHO_RETRO, PEAKS,
                              K_B_J_PER_K, M_RB87_KG)
from rb5s6s.density import density_units, N_UNIT_CM3              # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T                      # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz                   # noqa: E402

OUT = C.RESULTS_DIR / "onf_candidate.csv"

# ---------------------------------------------------------------------------
# assumed parameters: apparatus values this repository does not know. Each is
# a placeholder for a measurement or a mode solution, and the note says
# which. Bands are carried where the ignorance is a range.
# ---------------------------------------------------------------------------
LAMBDA_NM = PEAKS["4121"]["lambda_nm"]      # drive wavelength, committed
NEFF_BAND = (1.08, 1.25)                    # guided-mode index at 993 nm
AEFF_UM2 = 0.5                              # effective mode area at the surface
P_GUIDED_W = 1e-3                           # guided drive power for the estimates
P_PROBE_W = 50e-6                           # reduced probe power (Stark hygiene)
MOT_T_K = 150e-6                            # MOT temperature
MOT_N_CM3 = 1e10                            # MOT peak density
MOT_OVERLAP_M = 0.6e-3                      # MOT-waist overlap length
HOT_OVERLAP_M = 2e-3                        # hot-vapor waist region used
FIBER_RADIUS_NM = 200.0                     # 400 nm ONF, the fibre rajasree2020spin
                                            # drove this line through
C3_5S_HZ_UM3 = 845.0                        # Rb 5S vs fused silica, literature
C3_RATIO_BAND = (3.0, 6.0)                  # C3(6S)/C3(5S), expectation band
CELL_T_C = 130.0                            # the cell reference condition
CELL_P_W = 0.225


def _lambda_evanescent_nm(neff: float) -> float:
    """1/e decay length of evanescent intensity ~ lambda / (2 pi sqrt(neff^2-1))."""
    return LAMBDA_NM / (2.0 * math.pi * math.sqrt(neff * neff - 1.0))


def main() -> int:
    rows = []

    def add(q, v, unit, basis, note):
        rows.append(dict(quantity=q, value=v, unit=unit, basis=basis,
                         note=note, status="DIAGNOSTIC"))

    # ---- committed inputs the estimates stand on --------------------------
    gnat = GAMMA_NAT_HZ / 1e6
    add("gamma_nat", f"{gnat:.4f}", "MHz", "committed_input",
        "constants.GAMMA_NAT_HZ from tau(6S) = 45.57 ns")
    tr_cell = transit_fwhm_at_T(CELL_T_C, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    add("transit_cell_130C", f"{tr_cell:.4f}", "MHz", "committed_input",
        "transit_fwhm_at_T at the cell waist W0_MEASURED_M = 64 um")
    with (C.RESULTS_DIR / "beta_self.csv").open() as fh:
        betas = [float(r["beta_self"]) for r in csv.DictReader(fh)]
    beta_med = sorted(betas)[len(betas) // 2]
    add("beta_self_median", f"{beta_med:.4f}", "MHz per 1e12 cm^-3",
        "committed_input", "median over the four peaks of results/beta_self.csv")
    n_cell = density_units(CELL_T_C)
    add("density_cell_130C", f"{n_cell:.3f}", "1e12 cm^-3", "committed_input",
        "density.density_units at the cell reference condition")
    i_cell = (1.0 + RHO_RETRO) * 2.0 * CELL_P_W / (math.pi * W0_MEASURED_M ** 2)
    add("intensity_cell_eff", f"{i_cell:.3e}", "W m^-2", "committed_input",
        "time-averaged fwd+retro on-axis intensity at 225 mW, w0 = 64 um, "
        "rho = 0.94 (the constants.py convention)")
    s0_cell = stark_shift_S0_mhz(CELL_P_W, W0_MEASURED_M, RHO_RETRO)
    add("S0_cell_225mW", f"{s0_cell:.3f}", "MHz", "committed_input",
        "stark_shift_S0_mhz at the cell reference condition")

    # ---- the fiber's geometry, assumed until the lab replaces it ----------
    add("neff_band", f"{NEFF_BAND[0]:.2f} to {NEFF_BAND[1]:.2f}", "",
        "assumed_parameter",
        "guided-mode index at 993 nm for a 400 nm class ONF. REPLACE with the "
        "value computed from the actual fiber diameter")
    lam_lo = _lambda_evanescent_nm(NEFF_BAND[1])
    lam_hi = _lambda_evanescent_nm(NEFF_BAND[0])
    lam_c = _lambda_evanescent_nm(0.5 * (NEFF_BAND[0] + NEFF_BAND[1]))
    add("evanescent_decay_length", f"{lam_lo:.0f} to {lam_hi:.0f}", "nm",
        "derived_expectation",
        f"lambda/(2 pi sqrt(neff^2-1)) across the neff band, central {lam_c:.0f}")
    add("mode_area_eff", f"{AEFF_UM2:.2f}", "um^2", "assumed_parameter",
        "effective area for surface intensity. REPLACE with the mode solution")
    add("fiber_diameter", f"{2 * FIBER_RADIUS_NM:.0f}", "nm", "cited_literature",
        "the ONF rajasree2020spin drove 5S-6S through with cold atoms. NOTE a "
        "discrepancy to settle: the internal manuscript scaffold describes the "
        "group's fibres as ~650 nm waist, which is not the fibre of the "
        "cold-atom 5S-6S measurement")
    add("measured_count_rate_evanescent", "25 to 40", "counts per ms",
        "cited_literature",
        "rajasree2020spin, cold 87Rb around a 400 nm ONF on THIS transition. "
        "This is the feasibility anchor: the signal question is answered by a "
        "published measurement on this platform, so the per-atom rate ratios "
        "below are context for the Stark budget rather than the case for "
        "detectability")
    add("circular_null_minimum", "13 theory, 25 practice", "per cent",
        "cited_literature",
        "rajasree2020spin: the guided mode's longitudinal component prevents a "
        "true circular null, so the two-photon rate has a MINIMUM rather than a "
        "zero. The polarisation at the atom is not the polarisation at the "
        "input, which is a systematic and also a tomography handle")

    # ---- instrument A: cold atoms, trap off -------------------------------
    v_ratio = math.sqrt(MOT_T_K / (CELL_T_C + 273.15))
    geo = W0_MEASURED_M * 1e9 / lam_c
    tr_cold = tr_cell * geo * v_ratio
    add("transit_onf_cold_scaled_LEGACY", f"{tr_cold * 1e3:.0f}", "kHz",
        "derived_expectation",
        f"NO LONGER USED as of 2026-08-21, kept so the correction is "
        f"auditable. Cell "
        f"transit scaled by geometry x{geo:.0f} and thermal speed "
        f"x{v_ratio:.1e}. The scaling carries the CELL's Gaussian-beam "
        "convention onto an exponential profile, which the rows below derive "
        "directly instead")

    # ---- O1: the transit kernel derived for the profile the atoms actually
    # cross, rather than scaled from the profile they do not.
    #
    # THE SHAPE CHANGES, NOT ONLY THE WIDTH. A Gaussian beam gives the
    # Biraben-Cagnac two-sided exponential in FREQUENCY, which is the cusp the
    # cell's kernel uses. An atom on a radial pass through an evanescent field
    # sees I(t) = I0 exp(-v|t|/Lambda), a two-sided exponential IN TIME, whose
    # transform is a LORENTZIAN of FWHM v/(pi Lambda).
    #
    # THE CONSEQUENCE IS THE POINT. A Lorentzian transit width ADDS into the
    # homogeneous width, exactly as gamma_coll and Gamma_L,equiv do, so in the
    # fibre the transit term is NOT a separable nuisance: it enters the same
    # exact degeneracy the kernel work just characterised. A fibre measurement
    # of Gamma_L,equiv therefore needs either an independent Lambda, which the
    # EOM teeth cannot supply at any drive, or a lever that moves the transit
    # while leaving the kernel fixed. The molasses temperature ladder is that
    # lever, and it is the fibre's analogue of the cell's density ladder.
    v_cold = math.sqrt(K_B_J_PER_K * MOT_T_K / M_RB87_KG)
    for lam_nm, tag in ((211.0, "min"), (388.0, "max")):
        fw = v_cold / (math.pi * lam_nm * 1e-9)
        add(f"transit_onf_cold_lorentzian_{tag}_decay", f"{fw / 1e3:.1f}", "kHz",
            "derived_expectation",
            f"FWHM v/(pi Lambda), TRANSITION AXIS, at Lambda = {lam_nm:.0f} nm and "
            f"T = 150 uK, "
            "for the exponential evanescent profile. The kernel is a "
            "LORENTZIAN, not the cell's cusp")
    add("transit_onf_cold_band", "98 to 181", "kHz", "derived_expectation",
        "the transit term on the TRANSITION AXIS across the 211 to 388 nm "
        "decay-length band. O2's "
        "injection-recovery runs at BOTH edges, because a world whose known "
        "component moves by a third is a different test at each")
    add("transit_onf_kernel_shape", "Lorentzian", "shape", "derived_expectation",
        "and therefore ADDITIVE with gamma_coll and Gamma_L,equiv rather than "
        "separable from them. This is the fibre's version of the degeneracy "
        "the cell resolves with density, and the molasses sqrt(T) ladder is "
        "the lever that resolves it here")

    gc_mot = beta_med * (MOT_N_CM3 / N_UNIT_CM3)
    add("gamma_coll_at_MOT_density", f"{gc_mot * 1e6:.1f}", "Hz",
        "derived_expectation",
        "beta_self times 1e10 cm^-3: collisions are gone at MOT density")
    add("cold_line_budget",
        f"{gnat:.2f} + laser + {tr_cold:.3f}", "MHz", "derived_expectation",
        "the cold-ONF line is KNOWN natural width plus the laser contribution "
        "plus a transit term two orders below both: an independent laser-width "
        "instrument, which is the identifying rung of the intercept ladder")

    # ---- drive strength and its Stark cost --------------------------------
    i_onf = P_GUIDED_W / (AEFF_UM2 * 1e-12)
    add("intensity_onf_1mW", f"{i_onf:.3e}", "W m^-2", "derived_expectation",
        "guided power over effective area, evaluated at the surface")
    add("intensity_ratio_onf_over_cell", f"{i_onf / i_cell:.0f}", "",
        "derived_expectation",
        "1 mW guided against the 225 mW cell reference")
    add("two_photon_rate_ratio_per_atom", f"{(i_onf / i_cell) ** 2:.0f}", "",
        "derived_expectation", "intensity ratio squared")
    s0_onf = s0_cell * i_onf / i_cell
    add("S0_onf_1mW", f"{s0_onf:.1f}", "MHz", "derived_expectation",
        "the cell Stark shift scaled by intensity: at 1 mW the drive's own "
        "light shift DOMINATES the line, so 1 mW is a Stark-geometry "
        "instrument, not a spectroscopy setting")
    i_probe = P_PROBE_W / (AEFF_UM2 * 1e-12)
    add("S0_onf_50uW", f"{s0_cell * i_probe / i_cell:.2f}", "MHz",
        "derived_expectation",
        "the spectroscopy setting: Stark comparable to the cell's, per-atom "
        f"rate still x{(i_probe / i_cell) ** 2:.1f} the cell's")

    # ---- atom numbers -----------------------------------------------------
    a_um = FIBER_RADIUS_NM * 1e-3
    lam_um = lam_c * 1e-3
    shell_um2 = math.pi * ((a_um + lam_um) ** 2 - a_um ** 2)
    v_mot_cm3 = shell_um2 * (MOT_OVERLAP_M * 1e6) * 1e-12
    add("atoms_in_evanescent_MOT", f"{MOT_N_CM3 * v_mot_cm3:.1f}", "",
        "derived_expectation",
        f"evanescent shell ({shell_um2:.2f} um^2 cross-section) times "
        f"{MOT_OVERLAP_M * 1e3:.1f} mm overlap at 1e10 cm^-3: a few atoms on "
        "average, the regime the Rydberg-near-fiber detection already works in")
    n_hot_cm3 = n_cell * N_UNIT_CM3
    v_hot_cm3 = shell_um2 * (HOT_OVERLAP_M * 1e6) * 1e-12
    add("atoms_in_evanescent_hot", f"{n_hot_cm3 * v_hot_cm3:.0f}", "",
        "derived_expectation",
        "the same shell in 130 C vapor over a 2 mm region")

    # ---- instrument C: hot vapor, the transit kernel ----------------------
    tr_hot = tr_cell * geo
    add("transit_onf_hot_130C", f"{tr_hot:.0f}", "MHz", "derived_expectation",
        "cell transit scaled by geometry alone: transit goes from a small "
        "component of the cell line to essentially all of the ONF line, so "
        "the transit KERNEL becomes the measured object. The evanescent "
        "profile is exponential, not Gaussian, so this tests the transit "
        "machinery on a second geometry rather than re-testing the cusp")

    # ---- instrument B: the atom-surface tail ------------------------------
    add("C3_5S_silica", f"{C3_5S_HZ_UM3:.0f}", "Hz um^3", "cited_literature",
        "Rb ground state against fused silica, ~5.6e-49 J m^3. The note "
        "carries the citation")
    add("C3_ratio_6S_over_5S", f"{C3_RATIO_BAND[0]:.0f} to "
        f"{C3_RATIO_BAND[1]:.0f}", "", "assumed_parameter",
        "REPLACE with a Casimir-Polder sum over 6S oscillator strengths; the "
        "band brackets plausible values and the conclusion is not sensitive "
        "inside it")
    for r_nm in (50, 100, 200):
        lo = (C3_RATIO_BAND[0] - 1) * C3_5S_HZ_UM3 / (r_nm * 1e-3) ** 3 / 1e6
        hi = (C3_RATIO_BAND[1] - 1) * C3_5S_HZ_UM3 / (r_nm * 1e-3) ** 3 / 1e6
        add(f"cp_shift_at_{r_nm}nm", f"{lo:.2f} to {hi:.2f}", "MHz",
            "derived_expectation",
            "differential 5S-6S Casimir-Polder red shift at this distance in "
            "the near-field C3/z^3 form, read against the cold line budget "
            "above. NOT the whole surface shift: the electrostatic "
            "surface-charge term of pennetta2026 adds to it and is "
            "device-dependent, and the C3 form crosses to a retarded C4/z^4 "
            "at larger z (ton2026)")

    OUT.parent.mkdir(exist_ok=True)
    # ---- O0: the validation targets, as rows, before anything validates --
    # Two PER-COMPONENT numbers, not one rounded singular target. They are
    # computed from the anchor sigmas rather than quoted, so the row carries
    # the construction and a reader can see which anchor moved if it changes.
    anchor_gamma_l, anchor_sigma_g = 0.061, 0.058     # MHz, kernel_identifiability
    prior_factor = 0.2
    add("target_sigma_gamma_l", f"{prior_factor * anchor_gamma_l * 1e3:.1f}", "kHz",
        "derived_expectation",
        f"{prior_factor} x the cell-alone sigma(Gamma_L) of "
        f"{anchor_gamma_l} MHz from the absolute_anchor row of "
        "kernel_identifiability.csv. The precision a fibre measurement must "
        "reach on the LORENTZIAN laser component for the joint fit to gain "
        "what the forecast assumes")
    add("target_sigma_sigma_g", f"{prior_factor * anchor_sigma_g * 1e3:.1f}", "kHz",
        "derived_expectation",
        f"{prior_factor} x the cell-alone sigma(sigma_G) of "
        f"{anchor_sigma_g} MHz, the same requirement on the GAUSSIAN "
        "component. The two targets differ and a single rounded figure hides "
        "which component is the binding one")
    add("target_recovery_fraction", "0.36", "fraction", "committed_input",
        "the joint fit's sigma(beta) relative to the free-Gamma_L cell-alone "
        "fit when both laser components carry a prior at this strength, from "
        "the prior scan in kernel_identifiability.csv")

    # ---- the EOM ruler through the fibre ---------------------------------
    # The cell's frequency axis is built by the EOM sideband ruler. The same
    # teeth can be sent down the nanofibre, and what they are worth there is
    # decided by two ratios, both computed here from committed constants.
    #
    # The drive is a DESIGN VARIABLE for the next campaign, so these rows are
    # written as a function of it rather than at the present 12.5 MHz.
    from rb5s6s import constants as K
    spacing_transition = K.TOOTH_SPACING_TRANSITION_HZ / 1e6
    add("eom_tooth_spacing_transition", f"{spacing_transition:.4f}", "MHz",
        "committed_input",
        "constants.TOOTH_SPACING_TRANSITION_HZ; the laser-axis spacing is half "
        "of it, and the axis each number is quoted on is named per rule 19.88")

    # RESOLVABILITY. A ruler is only a ruler while its teeth are separable
    # against the broadening of the line they are laid on.
    for label, transit in (("cell_130C", tr_cell),
                           ("onf_cold", tr_cold),
                           ("onf_hot_130C", tr_hot)):
        ratio = spacing_transition / transit
        add(f"eom_teeth_per_transit_{label}", f"{ratio:.2f}", "dimensionless",
            "derived_expectation",
            f"tooth spacing {spacing_transition:.2f} MHz over the transit width "
            f"{transit:.3f} MHz at this platform and setting. Above about 3 the "
            "teeth are resolved, below 1 they are washed out")
        add(f"eom_drive_needed_{label}", f"{3.0 * transit:.1f}", "MHz",
            "derived_expectation",
            "drive at which the teeth would sit three transit widths apart on "
            "the transition axis. The present 12.5 MHz clears the cell and the "
            "cold fibre and is far below what the room-temperature fibre needs")

    # THE COST OF RAISING THE DRIVE, and why it falls on the cell and not the
    # fibre. With the modulator in the common path the pathway pairs carry a
    # phase (s-n)*Omega*tau, so the effective depth is 2*beta*cos(pi f tau) for
    # an atom at delay tau, averaged over the cloud (forecast.comb_tooth_weights).
    # The average is over the SPATIAL EXTENT of the sample, so the smearing sets
    # in at a drive inversely proportional to that extent. The cell spreads its
    # atoms over centimetres and the fibre confines them to the waist, so the
    # fibre tolerates a drive the cell cannot.
    from rb5s6s.forecast import comb_tooth_weights
    C_LIGHT = 2.998e8
    for f_mhz in (12.5, 700.0, 1500.0):
        for label, extent_m in (("cell_7cm", 0.07), ("onf_waist_2mm", 0.002)):
            w0 = comb_tooth_weights(2.405, drive_hz=f_mhz * 1e6,
                                    retro_delay_s=(0.0, 2.0 * extent_m / C_LIGHT))[0]
            add(f"eom_carrier_at_null_{label}_{int(f_mhz)}MHz", f"{w0:.6f}",
                "weight", "derived_expectation",
                "carrier tooth weight at the modulation depth 2*beta = 2.405 "
                "where an unsmeared carrier nulls exactly. A nonzero value is "
                "carrier returning under the delay average, which is a loss of "
                "the one calibration-free reference point the comb offers")
    add("eom_high_drive_is_a_fibre_capability", "cell 0.0896 vs fibre 0.000000",
        "weight at 700 MHz", "derived_expectation",
        "at the drive the room-temperature fibre would need, the cell's carrier "
        "null has filled in to about nine per cent while the fibre's is intact, "
        "because the smearing average runs over the sample's spatial extent and "
        "the waist is some thirty-five times shorter than the cell path")

    # SNAPSHOT SAMPLING pulls the drive the other way: to read several detunings
    # at once rather than scanning, teeth must fall INSIDE the line.
    for f_mhz in (0.5, 1.0, 12.5):
        add(f"eom_teeth_across_cold_line_{f_mhz}MHz",
            f"{3.49 / f_mhz:.2f}", "teeth", "derived_expectation",
            "teeth landing within the 3.49 MHz known-natural cold-fibre line at "
            "this drive. Simultaneous multi-detuning readout needs several, and "
            "the present drive puts fewer than one tooth on the line")

    # WHAT THE TEETH CANNOT DO, recorded so it is not assumed later.
    add("eom_cannot_measure_neff", "fractional span ~5e-06 at 1.5 GHz",
        "dimensionless", "derived_expectation",
        "the guided-mode index, and so the evanescent decay length, would need a "
        "dispersion lever. Even a 1.5 GHz drive spans a few parts per million of "
        "the optical frequency, so the teeth do not constrain n_eff and do not "
        "narrow the 211 to 388 nm decay-length band that dominates the cold "
        "transit estimate")

    # ---- THE EPISTEMIC CLASS OF EVERY INSTRUMENT IN THIS NOTE ------------
    # The release gate requires that no public claim exceed its epistemic
    # class, which is only checkable if the classes are written down. Three
    # classes, and the distinction is what the claim RESTS ON, not how strong it
    # feels:
    #   DEMONSTRATED       a published measurement anchors it
    #   SIMULATION-BACKED  a twin in this repository has run it
    #   PROSPECTIVE        computed from committed arithmetic, not yet simulated
    for name, cls, why in (
        ("evanescent_decay_length", "DEMONSTRATED",
         "standard guided-mode result, and the band quoted here spans the "
         "radii the published fibre work uses"),
        ("count_rate_feasibility", "DEMONSTRATED",
         "rajasree2020spin measured 25 to 40 counts per ms on this transition "
         "around a 400 nm fibre"),
        ("polarisation_rate_suppression", "DEMONSTRATED",
         "anchored on the published circular-null minimum, not on arithmetic"),
        ("transit_kernel_lorentzian", "PROSPECTIVE",
         "derived here from the evanescent profile for a radial pass. No twin "
         "has run it and no measurement anchors it. The idealisation is "
         "explicit: real atoms carry a three-dimensional velocity and the "
         "field has an axial structure this derivation does not model"),
        ("eom_ruler_reach", "PROSPECTIVE",
         "committed-input arithmetic on tooth spacing against transit width"),
        ("eom_carrier_null_at_high_drive", "PROSPECTIVE",
         "computed with the committed comb-weight function at delays this "
         "apparatus has not yet run"),
        ("joint_fisher_forecast", "PROSPECTIVE",
         "a covariance-algebra forecast. The estimator that would confirm it "
         "on synthetic data is not built, so the recovery fraction is "
         "predicted and not reproduced"),
        ("validation_targets", "PROSPECTIVE",
         "requirements derived from the forecast above and inheriting its "
         "class. They are targets, not achievements"),
    ):
        add(f"class_{name}", cls, "epistemic class", "derived_expectation", why)
    add("class_summary",
        "3 demonstrated, 5 prospective, 0 simulation-backed", "tally",
        "derived_expectation",
        "NOTHING in this note is simulation-backed yet, because the ONF twin "
        "is not built, so the release must not read as endorsing the "
        "prospective class")

    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"  {r['quantity']:<32} {r['value']:>16} {r['unit']:<16} {r['basis']}")
    print(f"\nwrote {OUT}  ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

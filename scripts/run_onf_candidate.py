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
from _producer_lock import take_producer_lock     # noqa: E402
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s.constants import (GAMMA_NAT_HZ, W0_MEASURED_M,        # noqa: E402
                              RHO_RETRO, PEAKS)
from rb5s6s.density import density_units, N_UNIT_CM3              # noqa: E402
from rb5s6s.fibre import (HE11Field, solve_he11,                   # noqa: E402
                          transit_fwhm)
from rb5s6s.polarizability import E_6S_CM                         # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T                      # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz                   # noqa: E402

OUT = C.RESULTS_DIR / "onf_candidate.csv"

# ---------------------------------------------------------------------------
# assumed parameters: apparatus values this repository does not know. Each is
# a placeholder for a measurement or a mode solution, and the note says
# which. Bands are carried where the ignorance is a range.
# ---------------------------------------------------------------------------
LAMBDA_NM = PEAKS["4121"]["lambda_nm"]      # drive wavelength, committed
DIAMETER_TOL_NM = 20.0                      # the real ignorance: no held paper
#                                             states a tolerance for these fibres,
#                                             and the campaign can measure it by
#                                             scanning the atom-surface distance
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
    """1/q, the evanescent field AMPLITUDE 1/e length, in nm.

    This docstring said "evanescent intensity" until 2026-08-27 and the
    formula never matched it. Intensity goes as exp(-2qr), so its 1/e length
    is HALF of this. The mislabel propagated into the effective mode area and
    therefore into every intensity, shift and rate quoted for a fibre here.
    """
    return LAMBDA_NM / (2.0 * math.pi * math.sqrt(neff * neff - 1.0))


def main() -> int:
    take_producer_lock("run_onf_candidate")
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
    # The mode solve uses the LITERATURE resonance 2e7/E_6S_CM, not LAMBDA_NM.
    # LAMBDA_NM is a peak label from an uncalibrated wavemeter, and the owner's
    # standing rule is that a physical input must not inherit an instrument the
    # record documents as uncalibrated. The two differ by 6 ppm, so nothing
    # numerical turns on it, which is exactly why the wrong one is easy to keep.
    lam_lit_nm = 2e7 / E_6S_CM
    d_nm = 2.0 * FIBER_RADIUS_NM
    mode = solve_he11(d_nm, lam_lit_nm)
    m_lo = solve_he11(d_nm + DIAMETER_TOL_NM, lam_lit_nm)   # thicker: shorter tail
    m_hi = solve_he11(d_nm - DIAMETER_TOL_NM, lam_lit_nm)
    add("neff_solved", f"{mode.neff:.5f}", "", "computed_mode_solution",
        f"HE11 eigenvalue solve at {d_nm:.0f} nm and the literature line "
        f"{lam_lit_nm:.4f} nm, "
        "rb5s6s.fibre.solve_he11. Its two effective-index anchors are values "
        "standard for this geometry and are cited to no paper in this record, "
        "which is an OPEN ITEM. The independent check that does exist is a "
        "separately written solver. "
        "This REPLACES the assumed neff_band of 1.08 to 1.25, which "
        "corresponds to 485 to 796 nm fibres and did not contain the fibre "
        "this file names")
    add("mode_single", f"{mode.single_mode}", "flag", "computed_mode_solution",
        f"V = {mode.v_number:.3f} against the 2.405 HE11 cutoff")
    lam_lo = m_lo.amplitude_decay_nm
    lam_hi = m_hi.amplitude_decay_nm
    lam_c = mode.amplitude_decay_nm
    add("evanescent_decay_length", f"{lam_lo:.0f} to {lam_hi:.0f}", "nm",
        "computed_mode_solution",
        f"AMPLITUDE 1/e length 1/q, central {lam_c:.0f}, across a diameter "
        f"tolerance of +-{DIAMETER_TOL_NM:.0f} nm. The band is now the "
        "DIAMETER's ignorance carried through the solve, not an assumed index "
        "range. The convention is amplitude and was labelled intensity until "
        "2026-08-27")
    add("evanescent_decay_length_intensity", f"{mode.intensity_decay_nm:.0f}",
        "nm", "computed_mode_solution",
        "1/(2q), HALF the amplitude length. Stated separately because "
        "conflating the two is a factor of two in every intensity below")
    # THE EFFECTIVE MODE AREA, SETTLED 2026-08-28 BY A VALIDATED FIELD SOLVE.
    #
    # A shell formula pi[(a+1/q)^2 - a^2] was committed here and gave 1.98
    # um^2, replacing the assumed 0.50. The commit team refuted it, and four
    # computations of the one quantity then spanned a factor of six: the
    # assumed 0.50, the shell's 1.98, a seat's Poynting integral 0.4634, and a
    # plane-wave-impedance integration 2.73.
    #
    # None was adjudicable by inspection, so `rb5s6s.fibre.HE11Field` builds
    # the vector fields and CHECKS THEM BEFORE INTEGRATING. E_z and H_phi must
    # be continuous at the glass boundary. The first attempt failed H_phi by
    # 53 per cent and the ratio was exactly n1^2, locating the error in one
    # line. Corrected, E_z closes to 6e-10, H_phi to 2e-09, and the power
    # fraction inside the glass is 23.3 per cent against the seat's
    # independently computed 23.
    #
    # THE SHELL'S 1.98 IS REFUTED: it is 3.2x the field answer, as the seat
    # said. THE ASSUMED 0.50 WAS GOOD TO 20 PER CENT, which is why nothing
    # downstream moved when it was replaced.
    #
    # The convention is quoted because the number is meaningless without it:
    # P divided by the AZIMUTHALLY AVERAGED axial flux just outside the glass.
    # The peak-flux convention gives 0.49 on the same fields, SMALLER because
    # a peak intensity is larger. This comment said 0.82 until 2026-08-28,
    # after the function had already been corrected.
    _fld = HE11Field(2 * FIBER_RADIUS_NM, lam_lit_nm)
    aeff = _fld.effective_area_m2("azimuthal_mean") * 1e12
    add("mode_area_eff", f"{aeff:.2f}", "um^2", "computed_mode_solution",
        f"P/I with I the azimuthally averaged axial Poynting flux at the "
        f"surface. The PEAK-flux convention gives "
        f"{_fld.effective_area_m2('peak')*1e12:.2f} on the same fields, so "
        f"this number is not quotable without its convention. "
        f"The canonical home for mode quantities is "
        f"results/guided_mode_tables.csv, which tabulates this and the peak "
        f"convention at all three candidate diameters. This row is kept "
        f"because every intensity below divides by it, and the two cannot "
        f"disagree: both call rb5s6s.fibre.HE11Field with the same inputs. "
        f"Fields validated by E_z and H_phi continuity before integration. "
        f"A shell "
        f"approximation giving 1.98 is refuted, and the previously assumed "
        f"0.50 was right to 20 per cent")
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
    # sees I(t) = I0 exp(-v|t|/Lambda), a two-sided exponential IN TIME. The
    # lineshape is the SQUARED magnitude of its transform, a squared
    # Lorentzian, and the Maxwell average over speeds narrows it again: the
    # FWHM is f*vbar/(pi Lambda) with f spanned 0.24 to 0.44 rather than 1.
    #
    # THE CONSEQUENCE IS THE POINT. A near-Lorentzian transit width ADDS into
    # the homogeneous width, almost as gamma_coll and Gamma_L,equiv do, so in the
    # fibre the transit term is NOT a separable nuisance: it enters the same
    # exact degeneracy the kernel work just characterised. A fibre measurement
    # of Gamma_L,equiv therefore needs either an independent Lambda, which the
    # EOM teeth cannot supply at any drive, or a lever that moves the transit
    # while leaving the kernel fixed. The molasses temperature ladder is that
    # lever, and it is the fibre's analogue of the cell's density ladder.
    # Lambda here is the INTENSITY decay length, because the two-photon
    # coupling follows I and it is the intensity envelope an atom traverses.
    # This loop ran on 211 and 388 nm until 2026-08-27, which were AMPLITUDE
    # lengths from the assumed neff band, so it was wrong twice over: the
    # wrong fibre and the wrong convention, the second making the transit a
    # factor of two too narrow.
    lam_int_lo = m_lo.intensity_decay_nm
    lam_int_hi = m_hi.intensity_decay_nm
    fws = {}
    # THE FORMULA IS CALLED, NOT RETYPED. This loop inlined
    # `v_cold / (pi * Lambda)` and therefore did not move when the package's
    # `transit_fwhm` was corrected on 2026-08-28 -- a duplicated formula is
    # outside the population of every fix applied to the original.
    #
    # The correction is a factor between 2.3 and 4.1 on the kernel: a
    # lineshape is the SQUARED magnitude of the coupling's transform, and
    # averaging that over the Maxwell distribution narrows it further. See
    # TRANSIT_KERNEL_FACTOR.
    #
    # AND THE VELOCITY HERE WAS A THIRD CONVENTION AGAIN. `v_cold` is
    # sqrt(kT/m), which is neither the package's `mean` sqrt(8kT/pi m) nor its
    # `rms` sqrt(3kT/m); it is smaller than the mean by sqrt(8/pi) = 1.60. So
    # this row carried TWO offsetting errors, an overstated kernel and an
    # understated speed, and the net move is smaller than either. Two wrongs
    # partly cancelling is the reason a duplicated formula is dangerous rather
    # than merely untidy: the result looked reasonable throughout.
    for lam_nm, tag in ((lam_int_lo, "min"), (lam_int_hi, "max")):
        fw = transit_fwhm(MOT_T_K, lam_nm * 1e-9).fwhm_hz
        fws[tag] = fw / 1e3
        add(f"transit_onf_cold_lorentzian_{tag}_decay", f"{fw / 1e3:.1f}", "kHz",
            "derived_expectation",
            f"FWHM f*v/(pi Lambda) with f the flux-weighted ensemble factor, "
            f"TRANSITION AXIS, at intensity Lambda = {lam_nm:.0f} nm and "
            f"T = 150 uK. The kernel is a SQUARED Lorentzian averaged over "
            "the Maxwell distribution, near-Lorentzian in shape and NOT the "
            "cell's cusp. This row was 2.3x larger until 2026-08-28")
    add("transit_onf_cold_band",
        f"{min(fws.values()):.0f} to {max(fws.values()):.0f}", "kHz",
        "derived_expectation",
        f"the transit term on the TRANSITION AXIS across the "
        f"{min(lam_int_lo, lam_int_hi):.0f} to {max(lam_int_lo, lam_int_hi):.0f}"
        " nm intensity decay band the diameter tolerance implies. Computed "
        "from the rows above, which it restated as a literal until 2026-08-27 "
        "and so did not move when the mode solve replaced the assumed band")
    add("transit_onf_kernel_shape", "near-Lorentzian", "shape",
        "derived_expectation",
        "a squared Lorentzian averaged over the Maxwell distribution, so "
        "widths are added as an approximation whose error is not "
        "characterised here rather than exactly. This row read 'Lorentzian' "
        "and 'ADDITIVE' two rows from the corrected transit rows in the same "
        "committed file until 2026-08-28. The ladder argument is unaffected "
        "because it rests on the sqrt(T) scaling and not on exact additivity, "
        "and the molasses ladder is still the lever that resolves it")

    gc_mot = beta_med * (MOT_N_CM3 / N_UNIT_CM3)
    add("gamma_coll_at_MOT_density", f"{gc_mot * 1e6:.1f}", "Hz",
        "derived_expectation",
        "beta_self times 1e10 cm^-3: collisions are gone at MOT density")
    add("cold_line_budget",
        f"{gnat:.2f} + laser + {min(fws.values())/1e3:.3f} to "
        f"{max(fws.values())/1e3:.3f}", "MHz", "derived_expectation",
        "natural width plus the laser contribution plus a transit term about "
        "1.6 orders below the natural width, AND the atom-surface term, which "
        "this row omitted until 2026-08-29 while the cp_shift rows below said "
        "in their own notes that they are read against it. That term is not a "
        "correction: cp_shift_at_50nm is 13.52 to 33.80 MHz against a 3.49 MHz "
        "natural width, and across the 50 to 300 nm shell evanescent "
        "excitation samples it is an inhomogeneous red tail, not a shift. "
        "So the laser-width instrument needs the trap, not merely the fibre. "
        "At a fixed 200 nm the term falls to 0.21 to 0.53 MHz and is largely "
        "common-mode. Untrapped, a broad red-shifted nuisance is degenerate "
        "with the laser width, which is the identifiability failure the fibre "
        "was proposed to break. The probe's own shift is inhomogeneous too, "
        "spreading about 0.23 MHz across the shell at S0_onf_50uW. "
        "Correction history: docs/history/09_the-guided-geometry.md")

    # ---- drive strength and its Stark cost --------------------------------
    #
    # TWO AREAS, BECAUSE TWO QUANTITIES. `aeff` divides power by the axial
    # Poynting flux and is the POWER BUDGET area. A light shift is
    # -alpha_s |E|^2 / 4, so what scales it is |E|^2, and the free-space
    # intensity carrying that field is 0.5 c eps0 |E|^2. For a guided mode
    # those differ: S_z/(0.5 c eps0 <|E|^2>) is 0.75951 on this 400 nm
    # fibre, because E_z carries no axial flux. It read 0.758 until
    # 2026-08-29, computed under the retired silica index.
    #
    # THE WAVE OF 2026-08-28 MOVED THE DISTANCE PROFILE TO |E|^2 AND LEFT THIS
    # NORMALISATION ON S_z, so every shift row was low by 32 per cent while its
    # own note said it was scaled by |E|^2. The profile and the normalisation
    # are both part of the same quantity and correcting one is not correcting
    # it.
    #
    # `i_cell` is a free-space intensity, so the guided side must be one too.
    a_stark = _fld.stark_area_m2() * 1e12
    add("mode_area_stark", f"{a_stark:.3f}", "um^2", "computed_mode_solution",
        "P over 0.5 c eps0 <|E|^2> at the surface, the area a LIGHT SHIFT "
        "divides power by. This is the 0.4634 the record carried all night as "
        "an unexplained competitor to the 0.61 mode area. It was never a "
        "competing computation of the same quantity: it is a different "
        "quantity, and both are right")
    i_onf = P_GUIDED_W / (aeff * 1e-12)
    i_onf_stark = P_GUIDED_W / (a_stark * 1e-12)
    add("intensity_onf_1mW", f"{i_onf:.3e}", "W m^-2", "derived_expectation",
        "guided power over the POWER-BUDGET area, evaluated at the surface. "
        "Use mode_area_stark for anything that multiplies a polarizability")
    add("intensity_ratio_onf_over_cell", f"{i_onf / i_cell:.0f}", "",
        "derived_expectation",
        "1 mW guided against the 225 mW cell reference, power-budget "
        "convention on both sides")
    add("two_photon_rate_ratio_per_atom", f"{(i_onf_stark / i_cell) ** 2:.0f}",
        "", "derived_expectation",
        "the |E|^2 intensity ratio squared. A two-photon rate goes as the "
        "square of the field intensity an atom sees, so it takes the Stark "
        "area and not the power-budget one")
    # WHAT AN ATOM ACTUALLY SEES, which is not the surface value.
    #
    # 2026-08-28. Every guided row above is evaluated AT THE GLASS, and the
    # note says so, but the rows were then read as the experiment's numbers.
    # No atom sits at the glass: the trap minimum of a two-colour trap is
    # hundreds of nanometres out, and the record already carries the
    # Casimir-Polder shift at 50, 100, 200 and 400 nm for that reason.
    #
    # The profile is the validated field solution, so this is a factor the
    # record can now compute rather than approximate, and it is large. Two
    # different profiles are involved and this comment conflated them until
    # 2026-08-28. The axial FLUX at 400 nm is 0.119 of the surface value on
    # this file's 400 nm fibre and sets the power budget. The LIGHT SHIFT
    # moves by |E|^2, which is 0.097 there, and the two-photon rate by its
    # square. The code below uses the second, correctly; the comment quoted
    # the first and called it the shift.
    for _d in (50.0, 100.0, 200.0, 400.0):
        _f = _fld.intensity_at(_d * 1e-9)
        _e2 = _fld.stark_fraction_at(_d * 1e-9)
        add(f"guided_intensity_fraction_at_{_d:.0f}nm", f"{_f:.4f}", "",
            "computed_mode_solution",
            "AXIAL FLUX at this distance from the surface, relative to the "
            "surface, from the validated vector field. This is the power "
            f"budget quantity. It is NOT an exponential, since q*a is "
            f"{FIBER_RADIUS_NM / mode.amplitude_decay_nm:.3f} on THIS "
            f"{2*FIBER_RADIUS_NM:.0f} nm fibre and the asymptotic form is "
            f"unavailable. This string read 0.23 until 2026-08-29, which is "
            f"the 370 nm fibre's value, so it is computed here rather than "
            f"typed")
        add(f"guided_stark_fraction_at_{_d:.0f}nm", f"{_e2:.4f}", "",
            "computed_mode_solution",
            "|E|^2 at the same place, relative to the surface, azimuthally "
            "averaged. A light shift goes as |E|^2 and NOT as the axial "
            "flux, and for a guided mode the two are not proportional "
            "because E_z carries no axial flux. Every shift row here was "
            "keyed on the flux until 2026-08-28, an error of about 20 per "
            "cent at the trap distance")
        add(f"S0_onf_1mW_at_{_d:.0f}nm", f"{s0_cell * i_onf_stark * _e2 / i_cell:.2f}",
            "MHz", "derived_expectation",
            "the drive's own light shift where an atom is, not at the glass, "
            "on the transition axis, scaled by |E|^2 and not by the axial "
            "flux. The surface value overstates it by the reciprocal of the "
            "stark fraction above")
    s0_onf = s0_cell * i_onf_stark / i_cell
    add("S0_onf_1mW", f"{s0_onf:.1f}", "MHz", "derived_expectation",
        "the cell Stark shift scaled by intensity: at 1 mW the drive's own "
        "light shift DOMINATES the line, so 1 mW is a Stark-geometry "
        "instrument, not a spectroscopy setting")
    i_probe = P_PROBE_W / (a_stark * 1e-12)
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
    #
    # THE SAME DUPLICATED-FORMULA DEFECT AS THE COLD ROWS, ONE INSTANCE LATER,
    # and the comment above those rows warns about it in as many words. This
    # row read `tr_cell * geo` until 2026-08-29: the CELL's Gaussian-beam
    # transit coefficient carried onto an exponential envelope, and scaled by
    # the AMPLITUDE decay length where the cold rows use the INTENSITY one.
    # Two errors, x0.714 from the coefficient and x2.0 from the length, so
    # they partly cancelled and the answer looked reasonable. It gave 98 MHz
    # where the record's own live route gives 140.3, a factor 1.43, and the
    # direction was OPTIMISTIC on the ruler's reach.
    #
    # It is computed here exactly as the cold rows are, so there is one route
    # and not two. That is the whole lesson of the cold repair: a formula
    # duplicated is a formula that goes stale in one copy.
    tr_hot = transit_fwhm(CELL_T_C + 273.15,
                          mode.intensity_decay_nm * 1e-9).fwhm_hz / 1e6
    # AND ITS SIBLINGS ARE A BAND, so this one is too. The cold rows carry the
    # diameter tolerance through to a min, a max and a band; the repaired hot
    # row carried the central value alone, which is a point standing where its
    # siblings span. The tolerance is the same ignorance in both regimes.
    _hot_lo = transit_fwhm(CELL_T_C + 273.15, lam_int_hi * 1e-9).fwhm_hz / 1e6
    _hot_hi = transit_fwhm(CELL_T_C + 273.15, lam_int_lo * 1e-9).fwhm_hz / 1e6
    add("transit_onf_hot_130C_band",
        f"{min(_hot_lo, _hot_hi):.0f} to {max(_hot_lo, _hot_hi):.0f}", "MHz",
        "derived_expectation",
        f"the same width across the {min(lam_int_lo, lam_int_hi):.0f} to "
        f"{max(lam_int_lo, lam_int_hi):.0f} nm intensity decay band the "
        "diameter tolerance implies, on the TRANSITION AXIS. The row "
        "BELOW is its central value, and the cold rows carry the same pair")
    add("transit_onf_hot_130C", f"{tr_hot:.1f}", "MHz", "derived_expectation",
        f"FWHM f*v/(pi Lambda) with f the flux-weighted ensemble factor, "
        f"TRANSITION AXIS, at intensity Lambda = "
        f"{mode.intensity_decay_nm:.0f} nm and T = {CELL_T_C:.0f} C. Transit "
        "goes from a small component of the cell line to essentially all of "
        "the ONF line, so the transit KERNEL becomes the measured object. "
        "This row was 98 MHz until 2026-08-29, built by scaling the cell's "
        "cusp by a geometry ratio on the amplitude length, which is the "
        "route row transit_onf_cold_scaled_LEGACY marks as no longer used")

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
    # THE COLD FIBRE IS A BAND, NOT A POINT, and it read the retired
    # single value until 2026-08-28. Its transit term spans the intensity
    # decay length the diameter tolerance implies, so the teeth ratio and the
    # drive it implies are ranges, and quoting either as a point hides the
    # widest source of uncertainty in the fibre ruler argument.
    cold_lo, cold_hi = min(fws.values()) / 1e3, max(fws.values()) / 1e3
    for label, t_lo, t_hi in (("cell_130C", tr_cell, tr_cell),
                              ("onf_cold", cold_lo, cold_hi),
                              ("onf_hot_130C", min(_hot_lo, _hot_hi),
                               max(_hot_lo, _hot_hi))):
        r_hi, r_lo = spacing_transition / t_lo, spacing_transition / t_hi
        ratio_s = (f"{r_lo:.2f}" if t_lo == t_hi
                   else f"{r_lo:.2f} to {r_hi:.2f}")
        width_s = (f"{t_lo:.3f}" if t_lo == t_hi
                   else f"{t_lo:.3f} to {t_hi:.3f}")
        add(f"eom_teeth_per_transit_{label}", ratio_s, "dimensionless",
            "derived_expectation",
            f"tooth spacing {spacing_transition:.2f} MHz over the transit width "
            f"{width_s} MHz at this platform and setting. Above about 3 the "
            "teeth are resolved, below 1 they are washed out")
        drive_s = (f"{3.0 * t_lo:.1f}" if t_lo == t_hi
                   else f"{3.0 * t_lo:.1f} to {3.0 * t_hi:.1f}")
        add(f"eom_drive_needed_{label}", drive_s, "MHz",
            "derived_expectation",
            "drive at which the teeth would sit three transit widths apart on "
            "the transition axis. The present 12.5 MHz clears the cell and the "
            "cold fibre and is far below what the 130 C fibre needs")

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
        "at 700 MHz, which is ABOVE the 358.6 to 483.4 MHz band the 130 C "
        "fibre needs and is quoted as a capability rather than as that "
        "requirement, the cell's carrier null has filled in to about nine per "
        "cent while the fibre's is intact, "
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
        f"narrow the {lam_lo:.0f} to {lam_hi:.0f} nm decay-length band that "
        "dominates the cold "
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

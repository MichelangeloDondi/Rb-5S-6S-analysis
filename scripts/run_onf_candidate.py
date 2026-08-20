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
                              RHO_RETRO, PEAKS)
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
    add("transit_onf_cold", f"{tr_cold * 1e3:.0f}", "kHz", "derived_expectation",
        f"cell transit scaled by geometry x{geo:.0f} (w0 over the decay "
        f"length) and by thermal speed x{v_ratio:.1e} (150 uK over 403 K)")
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

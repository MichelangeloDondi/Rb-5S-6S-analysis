"""The guided-mode tables that `docs/methods/09` prints, as committed rows.

WHY THIS PRODUCER EXISTS.

Chapter 9 of the methods carries three tables of numbers: the HE11 solve at
three candidate diameters, the evanescent intensity profile against distance,
and the transit kernel under four treatments. Every one of them was typed into
the prose from a computation run once in a scratch session.

**That is the defect class this record already names**: a published number with
no producer. The reference-coverage ratchet caught it as thirteen new
unreferenced decimals in one chapter, and the answer is not to re-seed
the ratchet but to make the numbers regenerable, so that
`verify_results_fresh` grades them and the prose can cite rows instead of
restating a computation.

WHAT IT COMPUTES, and each is derived rather than assumed:

* the HE11 eigenvalue solve at 350, 370 and 400 nm, giving `n_eff`, the
  amplitude and intensity decay lengths and `q*a`, which is the number that
  decides whether the exponential approximation is available at all (it is
  not: `q*a` is 0.18 to 0.32 where the asymptotic form needs `q*a >> 1`);
* the axial Poynting flux against distance from the surface, from vector
  fields validated by E_z and H_phi continuity before any integral is taken,
  beside the exponential the record used before those fields existed;
* the transit FWHM under all four kernel treatments, so the span the record
  carries is a committed row rather than a docstring constant.

THE LADDER. Rows here stand on mathematics, not simulation: the mode solve is
a root of the characteristic equation and the fields are its closed-form
solution. The only numerical step is the quadrature in the Poynting integral
and the ensemble averages behind `TRANSIT_KERNEL_FACTOR`. The
single-velocity factor has a closed form, sqrt(sqrt(2)-1), and a test asserts
it. The two ENSEMBLE factors are numerical, and until 2026-08-28 this sentence
said they were checked against a closed form when nothing checked them at all:
the only test touching them compared the committed cell against the same dict
the producer had read it from. `rb5s6s.fibre.transit_kernel_factor` is now the
route to re-derive them and a test compares the cached values against it.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _producer_lock import take_producer_lock                    # noqa: E402
from rb5s6s.fibre import (HE11Field, TRANSIT_KERNEL_FACTOR,      # noqa: E402
                          solve_he11, transit_fwhm)

OUT = ROOT / "results" / "guided_mode_tables.csv"

LINE_NM = 993.4181          # the LITERATURE line, never the wavemeter label
# THE DIAMETER TOLERANCE IS THE ONLY UNCERTAINTY THESE ROWS HAVE.
#
# A mode solve at a stated diameter is exact: it is a root of the
# characteristic equation, and the fields are its closed-form solution. What
# is uncertain is the diameter.
#
# THE 20 nm BELOW IS ASSUMED AND HAS NO SOURCE IN THIS RECORD. No held paper
# states a tolerance for these fibres, and the open item lives in the fibre
# thread at `docs/big_picture/06_next-nanofibre.md`, not in
# `docs/plan/12_open-apparatus-items.md`, which routes fibre items away from
# the platform-neutral lane. This comment cited chapter 12 until 2026-08-28,
# which made an assumed number look sourced -- the class this record names as
# a number from a conversation attributed to the record.
#
# It is the SOLE uncertainty on every row of this file, so read every `_err`
# as conditional on it. The distance-scan lever measures the diameter
# directly, and that measurement is what would replace the assumption.
#
# So every row here is emitted with a sibling `_err` obtained by re-solving at
# d +- DIAMETER_TOL_NM and halving the span. That is a propagated uncertainty
# rather than a statistical one, and it is what protocol 8a.1 asks of a
# derived quantity: the number carries an uncertainty, and the uncertainty is
# the geometry's.
#
# The alternative was to tag these rows outside the claim classes so the
# guard would skip them, which is teaching a check to pass.
DIAMETER_TOL_NM = 20.0
DIAMETERS_NM = (350.0, 370.0, 400.0)
DISTANCES_NM = (100.0, 200.0, 400.0, 600.0)
PROFILE_DIAMETER_NM = 370.0   # the fibre the campaign forecast is written for
MOT_T_K = 150e-6


def _profile_rows(add, add_pair, diameter_nm):
    """The evanescent profile of one fibre, keyed by its diameter."""
    tag = f"{diameter_nm:.0f}nm"
    for dist in DISTANCES_NM:
        key = f"{tag}_at_{dist:.0f}nm"

        def flux(dd, _d=diameter_nm, _x=dist):
            return HE11Field(_d + dd, LINE_NM).intensity_at(_x * 1e-9)

        def stark(dd, _d=diameter_nm, _x=dist):
            return HE11Field(_d + dd, LINE_NM).stark_fraction_at(_x * 1e-9)

        def expo(dd, _d=diameter_nm, _x=dist):
            return math.exp(-_x / solve_he11(_d + dd, LINE_NM).intensity_decay_nm)

        add_pair("evanescent_profile", key, "flux_fraction", flux,
                 lambda x: f"{x:.3f}", "fraction",
                 f"validated vector field, {tag} fibre",
                 "axial Poynting flux at this distance from the surface, "
                 "relative to the surface. This is the power-budget quantity")
        def stark_axis(dd, _d=diameter_nm, _x=dist):
            return HE11Field(_d + dd, LINE_NM).stark_fraction_at(_x * 1e-9,
                                                                 "peak")

        add_pair("evanescent_profile", key, "stark_fraction", stark,
                 lambda x: f"{x:.3f}", "fraction",
                 f"|E|^2 azimuthally averaged, {tag} fibre",
                 "what a light shift scales with. It is not the axial flux, "
                 "because E_z carries no axial flux, and the two differ by "
                 "about 18 per cent at the trap distance")
        add_pair("evanescent_profile", key, "stark_fraction_on_axis",
                 stark_axis, lambda x: f"{x:.3f}", "fraction",
                 f"|E|^2 on the polarisation axis, {tag} fibre",
                 "the same quantity where the field is strongest. A two-colour "
                 "trap holds atoms at particular azimuths and not uniformly "
                 "around the fibre, and this record does not state which, so "
                 "the pair is the span rather than the averaged row alone. "
                 "The TENSOR term vanishes, both states having J = 1/2 by the "
                 "Wigner-Eckart triangle rule, but the VECTOR term does not, "
                 "and a guided mode is strongly elliptically polarised near "
                 "the surface. So the azimuth is not purely a magnitude "
                 "question and this pair is a lower bound on how much it "
                 "matters. This note claimed only |E|^2 matters until "
                 "2026-08-28, which followed the tensor premise to a "
                 "conclusion it does not support")
        add_pair("evanescent_profile", key, "flux_fraction_exponential", expo,
                 lambda x: f"{x:.3f}", "fraction",
                 "exp(-d/Lambda_intensity)",
                 "the form the record used before the fields were solved, "
                 "carried so the size of that error is a row and not a memory")
        add_pair("evanescent_profile", key, "exponential_overstatement",
                 lambda dd, f=flux, e=expo: e(dd) / f(dd),
                 lambda x: f"{x:.2f}", "factor",
                 "the ratio of the two above",
                 "how much the exponential overstates the delivered "
                 "intensity. It grows with distance, so a single quoted "
                 "factor is wrong")


def main() -> None:
    take_producer_lock("run_guided_mode_tables")
    rows: list[dict] = []

    # SCOPE FIRST, QUANTITY SECOND. The reference resolver matches a `ref:`
    # key to the first two columns positionally, so a schema whose first two
    # columns do not uniquely identify a row cannot be cited at all. The first
    # draft of this file used (table, key, quantity) and every reference to it
    # would have resolved to whichever row happened to come first.
    # STATUS IS EMITTED HERE, and it was not until 2026-08-28. This file was
    # registered in the SKIP list of `annotate_results_status.py`, whose
    # entries all claim the producer writes its own provenance column, under a
    # comment saying rows carry their own status. They did not. The comment
    # described an intention as a fact, which is the class this same wave
    # corrected four times elsewhere.
    #
    # A mode solve is a CALIB quantity: it is a computed property of a stated
    # geometry, not a measurement and not a forecast. A profile ratio is
    # DIAGNOSTIC. The retired transit kernel is an ARTIFACT, carried so the
    # size of the correction stays visible and never to be read as a value.
    STATUS = {"mode_solve": "CALIB",
              "evanescent_profile": "DIAGNOSTIC",
              "transit_kernel": "CALIB"}
    # A `factor` row is a definition, so it is DIAGNOSTIC rather than a claim.
    DEFINITION_QUANTITIES = {"factor"}

    def add_pair(table, key, quantity, fn, fmt, unit, basis, note):
        """Emit a value and its sibling `_err` from the diameter tolerance."""
        add(table, key, quantity, fmt(fn(0.0)), unit, basis, note)
        hi, lo = fn(+DIAMETER_TOL_NM), fn(-DIAMETER_TOL_NM)
        add(table, key, f"{quantity}_err", fmt(abs(hi - lo) / 2.0), unit,
            f"half-span over a diameter tolerance of +-{DIAMETER_TOL_NM:.0f} nm",
            "propagated from the geometry, which is the only thing uncertain "
            "here. The solve itself is exact at a stated diameter")

    def add(table, key, quantity, value, unit, basis, note):
        status = STATUS[table]
        if quantity in DEFINITION_QUANTITIES:
            status = "DIAGNOSTIC"
        if table == "transit_kernel" and key == "amplitude_lorentzian":
            status = "ARTIFACT"
        if quantity == "flux_fraction_exponential":
            status = "ARTIFACT"
        rows.append(dict(scope=f"{table}_{key}", quantity=quantity,
                         value=value, unit=unit, basis=basis, note=note,
                         status=status))

    # ---- table 1: the mode solve at the three candidate diameters ---------
    for d in DIAMETERS_NM:
        def at(dd, _d=d):
            return solve_he11(_d + dd, LINE_NM)

        def fld_at(dd, _d=d):
            return HE11Field(_d + dd, LINE_NM)

        tag = f"{d:.0f}nm"
        add_pair("mode_solve", tag, "neff",
                 lambda dd: at(dd).neff, lambda x: f"{x:.5f}", "index",
                 "HE11 characteristic equation at the literature line",
                 "solved, not assumed. An earlier neff_band of 1.08 to 1.25 "
                 "corresponds to 485 to 796 nm fibres and did not contain any "
                 "of the three named here")
        add_pair("mode_solve", tag, "amplitude_decay_length",
                 lambda dd: at(dd).amplitude_decay_nm, lambda x: f"{x:.0f}",
                 "nm", "1/q from the same solve",
                 "the amplitude convention. The intensity length is half of "
                 "it, and conflating the two is a factor of two in every "
                 "guided intensity")
        add_pair("mode_solve", tag, "intensity_decay_length",
                 lambda dd: at(dd).intensity_decay_nm, lambda x: f"{x:.0f}",
                 "nm", "1/(2q)",
                 "the convention a two-photon coupling needs, since the "
                 "coupling follows I")
        add_pair("mode_solve", tag, "qa",
                 lambda dd: fld_at(dd).qa, lambda x: f"{x:.3f}",
                 "dimensionless", "q times the fibre radius",
                 "the number that decides whether the approximation is "
                 "available. K1(x) reduces to its exponential asymptote only "
                 "for x much greater than one, so at 0.18 to 0.32 the "
                 "exponential form is unavailable anywhere the atoms are")
        add_pair("mode_solve", tag, "mode_area_azimuthal_mean",
                 lambda dd: fld_at(dd).effective_area_m2("azimuthal_mean")*1e12,
                 lambda x: f"{x:.3f}", "um^2",
                 "P over the azimuthally averaged axial flux at the surface",
                 "the convention is part of the number. The peak convention "
                 "gives a SMALLER area, since a peak intensity is larger")
        add_pair("mode_solve", tag, "mode_area_peak",
                 lambda dd: fld_at(dd).effective_area_m2("peak")*1e12,
                 lambda x: f"{x:.3f}", "um^2",
                 "P over the peak axial flux, on the polarisation axis",
                 "quoted beside the mean so no reader takes either as the "
                 "mode area without its convention. This row read 0.824 for "
                 "one day, larger than the mean, which a peak cannot be")
        add_pair("mode_solve", tag, "power_fraction_in_glass",
                 lambda dd: (lambda t: t[1]/t[0])(fld_at(dd).power()),
                 lambda x: f"{x:.3f}", "fraction",
                 "Poynting integral inside r<a",
                 "a shell approximation that ignores this fraction overstates "
                 "the effective area, which is how a committed 1.98 um^2 arose")

    # ---- table 2: the evanescent profile, against the exponential ---------
    #
    # BOTH FIBRES, because the record carries both and mixing them is the
    # defect this file exists to make impossible. The published cold-atom
    # measurement on this transition used a 400 nm fibre; the campaign
    # forecast is written for the 370 nm one. At a 400 nm trap distance the
    # 370 nm fibre keeps 0.156 of the surface flux and the 400 nm fibre
    # 0.119, and a bare number in prose cannot say which it is.
    for diam in (PROFILE_DIAMETER_NM, 400.0):
        _profile_rows(add, add_pair, diam)

    # ---- table 3: the transit kernel under all four treatments ------------
    for kernel, factor in sorted(TRANSIT_KERNEL_FACTOR.items(),
                                 key=lambda kv: -kv[1]):
        def fw(dd, _k=kernel):
            lam = solve_he11(PROFILE_DIAMETER_NM + dd, LINE_NM).intensity_decay_nm
            return transit_fwhm(MOT_T_K, lam * 1e-9, kernel=_k).fwhm_hz / 1e3

        add_pair("transit_kernel", kernel, "fwhm", fw, lambda x: f"{x:.1f}",
                 "kHz",
                 f"factor {factor} times v_mean/(pi Lambda), transition axis",
                 "amplitude_lorentzian is the retired form and reads the "
                 "transform of the coupling as the lineshape. A lineshape is "
                 "the squared magnitude of that transform, which narrows it "
                 "by sqrt(sqrt(2)-1), and the Maxwell average narrows it "
                 "further because slow atoms interact longer")
        add("transit_kernel", kernel, "factor", f"{factor}", "dimensionless",
            "the multiplier on v_mean/(pi Lambda)",
            "A DEFINITION AND NOT A MEASUREMENT, so it carries no error bar "
            "of its own. The uncertainty on the transit kernel is the SPAN "
            "ACROSS THESE FOUR ROWS, which is a model-form choice this record "
            "does not settle, and quoting one factor with a bar would hide "
            "that. The ensemble factors are normalised to the mean speed, so "
            "pairing one with another velocity convention double counts, and "
            "transit_fwhm refuses that combination")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["scope", "quantity", "value",
                                           "unit", "basis", "note", "status"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for r in rows:
        print(f"  {r['scope']:28} {r['quantity']:30} "
              f"{r['value']:>9} {r['unit']}")


if __name__ == "__main__":
    main()

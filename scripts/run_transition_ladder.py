#!/usr/bin/env python
"""The nS and nD two-photon rungs a Ti:Sapph reaches, 650 to 1050 nm.

WHAT THIS ANSWERS. The owner's design question of 2026-09-09: with a laser
tunable across 650 to 1050 nm, what are ALL the numbers for the nS and nD
two-photon transitions from 5S, and what changes rung to rung. The existing
menu in `docs/FUTURE_TRANSITIONS_titsapph.md` section 2 is prose with three
verified rows and two mislabelled ones (register A139); this producer replaces
its arithmetic with cells.

WHAT IT DOES NOT DO. The differential polarizability is held for 6S and 7S and
anchored for 5D, and this repository holds no sum over states for 8S, 9S, 4D,
6D or 7D. Those rows carry no value and a NULL status, which is the results
vocabulary's word for a cell that returns nothing usable, because a shift
coefficient is the one quantity the campaign would act on and an estimate of it
would be acted on too.

THE ENERGIES ARE A LADDER AND NOT A LOOKUP. `polarizability.LINES_5S` holds
the nP series from n = 5 to 12 and `cooperative.IONISATION_LIMIT_CM` the limit,
so a Rydberg-Ritz fit reproduces the P series to 1.3 cm-1 and extrapolates the
S and D series from the states held exactly. The fit's own ambiguity, between
holding the package's limit and holding the accepted Rydberg constant, is
carried as `drive_wavelength_spread_nm` on every extrapolated row. It is under
0.02 nm, which is what licenses the row; it is NOT a substitute for NIST and
the note says so.

Rung 2 of the ladder throughout: closed forms and one least-squares fit, no
simulation. Serial, seconds, no lock needed.
"""
from __future__ import annotations

import csv
import math
import os
import sys

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s import hyperpolarizability as hyp                      # noqa: E402
from rb5s6s import polarizability as pol                           # noqa: E402
from rb5s6s.cooperative import IONISATION_LIMIT_CM as EION         # noqa: E402

BAND_NM = (650.0, 1050.0)
# Which Safronova 2011 Table VI entry each rung of this ladder is. The D rungs
# take the 5/2 fine-structure level, which is the one this record's own 5D work
# is built on; the 3/2 value sits within a few per cent of it in that table.
_SAFRONOVA_KEY = {"6S": "6S1/2", "7S": "7S1/2", "8S": "8S1/2", "9S": "9S1/2",
                  "4D": "4D5/2", "5D": "5D5/2", "6D": "6D5/2"}
T_C = 130.0
R_ACCEPTED = 109736.605          # Rb Rydberg constant, for the second fit only
# The D series' lower anchor. It was 2e7/1033.0, the menu's own rounded
# row, until 2026-09-10: rb5s6s.hyperpolarizability holds 4D
# exactly, the two differ by 0.31 nm in the drive, and the row published
# 0.0005 nm of error. The doublet is carried rather than a J chosen,
# because this record has not checked the 4D J labels against NIST and
# the two levels are 0.446 cm-1 apart.
E_4D3_CM, E_4D5_CM = (hyp.LEVELS["4D3/2"][2], hyp.LEVELS["4D5/2"][2])
E_4D_CM = 0.5 * (E_4D3_CM + E_4D5_CM)
E_4D_DOUBLET_CM = abs(E_4D5_CM - E_4D3_CM)
# The independent check on the D extrapolation, named so the error cell
# and the note agree. E(nD) = E(5P3/2) + 1e7/lambda(5P3/2 to nD) puts 6D
# at 697.12 nm and 7D at 660.49 against this ladder's 697.45 and 660.77.
# OWED A NIST LOOKUP: the two line wavelengths are not held here.
D_SERIES_INDEPENDENT_MISS_NM = 0.35
KB = 1.380649e-23
U_KG = 1.66053906660e-27
M85 = 84.911789738 * U_KG


# --------------------------------------------------------------------------
# the Rydberg-Ritz ladder, from this package's own held levels
# --------------------------------------------------------------------------
def _delta(n: float, d0: float, d2: float) -> float:
    """The Ritz defect, solved for its own implicit n*."""
    d = d0
    for _ in range(80):
        d = d0 + d2 / (n - d) ** 2
    return d


def _energy(n: float, R: float, eion: float, d0: float, d2: float) -> float:
    return eion - R / (n - _delta(n, d0, d2)) ** 2


def _fit_series(ns, es, R, eion, guess):
    fit = least_squares(
        lambda p: [_energy(n, R, eion, p[0], p[1]) - e for n, e in zip(ns, es)],
        guess)
    return float(fit.x[0]), float(fit.x[1]), float(np.abs(fit.fun).max())


def ladder(R: float, eion: float) -> dict:
    """Term energies for the nS and nD rungs, cm-1 above 5S."""
    d0s, d2s, _ = _fit_series([6, 7], [pol.E_6S_CM, pol.E_7S_CM], R, eion,
                              [3.13, 0.22])
    d0d, d2d, _ = _fit_series([4, 5], [E_4D_CM, pol.E_5D52_CM], R, eion,
                              [1.29, -0.1])
    out = {}
    for n in (6, 7, 8, 9):
        held = {6: pol.E_6S_CM, 7: pol.E_7S_CM}.get(n)
        out[f"{n}S"] = held if held else _energy(n, R, eion, d0s, d2s)
    for n in (4, 5, 6, 7):
        held = {5: pol.E_5D52_CM}.get(n)
        out[f"{n}D"] = held if held else (E_4D_CM if n == 4
                                          else _energy(n, R, eion, d0d, d2d))
    return out


def ritz_form_error_nm():
    """The METHOD's own extrapolation error, measured and not assumed.

    The two-fit spread below is the FIT's ambiguity and says nothing about
    whether the Ritz form extrapolates. The nP series is long enough to test
    that directly: fit two adjacent states, predict the next two, and read the
    residual over the same lever arm the S and D ladders use. Returns the worst
    absolute wavelength error in nm, and the worst over the one-step-lower
    anchors that the D series matches.

    Found on 2026-09-09 when this producer's 8S was set against the thesis
    chapter's own section 7.1, which needed a bar to adjudicate them.
    """
    p12 = [pol.LINES_5S[i][0] for i in range(0, len(pol.LINES_5S), 2)]
    ns = list(range(5, 5 + len(p12)))
    R = fit_the_p_series()[0]
    worst_high, worst_low = 0.0, 0.0
    for i in range(len(ns) - 3):
        a, b = ns[i], ns[i + 1]
        d0, d2 = least_squares(
            lambda q: [_energy(n, R, EION, q[0], q[1]) - e
                       for n, e in ((a, p12[i]), (b, p12[i + 1]))],
            [2.65, 0.37]).x
        for j in (2, 3):
            err = abs(2e7 / _energy(ns[i + j], R, EION, d0, d2)
                      - 2e7 / p12[i + j])
            if a <= 5:
                worst_low = max(worst_low, err)
            worst_high = max(worst_high, err)
    return worst_high, worst_low


def fit_the_p_series():
    """The check that licenses the extrapolation, and its residual."""
    p12 = [pol.LINES_5S[i][0] for i in range(0, len(pol.LINES_5S), 2)]
    ns = list(range(5, 5 + len(p12)))
    a = least_squares(lambda p: [_energy(n, p[0], EION, p[1], p[2]) - e
                                 for n, e in zip(ns, p12)], [109700., 2.65, .37])
    b = least_squares(lambda p: [_energy(n, R_ACCEPTED, p[0], p[1], p[2]) - e
                                 for n, e in zip(ns, p12)], [EION, 2.65, .37])
    return (float(a.x[0]), float(np.abs(a.fun).max()),
            float(b.x[0]), float(np.abs(b.fun).max()))


# --------------------------------------------------------------------------
# the per-rung quantities
# --------------------------------------------------------------------------
PROV = {"6S": "held exactly (NIST, rb5s6s.polarizability.E_6S_CM)",
        "7S": "held exactly (NIST, rb5s6s.polarizability.E_7S_CM)",
        "5D": "held exactly (NIST, rb5s6s.polarizability.E_5D52_CM)",
        "4D": "held exactly (NIST, rb5s6s.hyperpolarizability.LEVELS), the "
              "doublet centre, used as the second D anchor"}

DETECTION = {
    "6S": "795 nm, 5P1/2 to 5S, the arm the bench already has",
    "7S": "420 nm, 6P to 5S",
    "8S": "420 nm, 6P to 5S",
    "9S": "420 nm, 6P to 5S",
    # 4D DOES NOT CASCADE THROUGH 5D: it lies BELOW it. The decay is
    # 4D to 5P (1.48 um from 4D3/2, 1.53 from 4D5/2) and then 5P to 5S,
    # so the bench's installed 795 nm arm already serves the 4D3/2 leg.
    # This cell named the 5D cascade until 2026-09-10 and so reported a
    # rung with no detection arm when it has the one arm the bench owns.
    "4D": "1.48/1.53 um (4D to 5P) then 795 nm (5P1/2 to 5S), the arm the bench already has",
    "5D": "420 nm, 6P to 5S",
    "6D": "420 nm, 6P to 5S",
    "7D": "420 nm, 6P to 5S",
}


def pedestal_fwhm_mhz(e_cm: float) -> float:
    """Doppler width of the co-propagating (pedestal) component, 85Rb.

    The counter-propagating pair is Doppler-free; the co-propagating pair sees
    the full transition frequency times v/c, so the pedestal width is linear in
    the term energy and the shorter drives carry the wider pedestal."""
    dv = math.sqrt(8.0 * math.log(2.0) * KB * (T_C + 273.15) / M85)
    return e_cm * 100.0 * dv / 1e6


def five_p_enhancement(e_cm: float) -> float:
    """The 5S side of the two-photon matrix element, RELATIVE and not a rate.

    The element is a sum over intermediate nP of d(5S,j) d(j,f) / (E_j - E_f/2).
    This returns the 5S half with the upper half held COMMON, which is how it
    isolates the intermediate resonance, and it is NOT a transition rate.

    THIS DOCSTRING SAID THE PACKAGE HOLDS NO d(j,f). That is false and the
    record was corrected on 2026-09-10: LINES_6S and LINES_7S hold the upper half
    for those two rungs, and two_photon_element below sums both. Holding it
    common is a choice here and was an obligation in the sentence."""
    virt = e_cm / 2.0
    return abs(sum(d / (ej - virt) for ej, d, _ in pol.LINES_5S))


# The upper-state half, for the rungs that have one (LINES_6S, LINES_7S
# carry d(nP,6S) and d(nP,7S) over the same nP as LINES_5S). A rung absent
# from this table gets no ceiling row rather than one missing a factor.
UPPER_LINES = {"6S": pol.LINES_6S, "7S": pol.LINES_7S}

# The rung's own natural width, relative to 6S, for the rungs whose lifetime
# this package holds. A rung absent here gets no ceiling row: the ceiling is
# DEFINED against the natural width, so a rung without one has no ceiling to
# report, and holding the width common is what put a false invariance in this
# file until 2026-09-10.
GAMMA_REL = {"6S": 1.0, "7S": K.GAMMA_NAT_7S_HZ / K.GAMMA_NAT_HZ}


def _g_err(rung: str) -> float:
    """One sigma on the width ratio, from the two lifetimes' own sigmas."""
    if rung == "6S":
        return 0.0
    g = GAMMA_REL[rung]
    return g * math.hypot(K.TAU_6S_ERR_S / K.TAU_6S_S,
                          K.TAU_7S_ERR_S / K.TAU_7S_S)


def _m_err(rung: str, e_cm: float, n: int = 20000) -> float:
    """One sigma on the element ratio, DRAWN from the held sigmas.

    The reduced elements carry their own uncertainties on both halves and the
    ratio is a quotient of sums of products, so it is drawn rather than
    linearised. Seeded, so the row is reproducible. Returns 0 for the
    reference rung, whose ratio is one by construction.
    """
    upper = UPPER_LINES.get(rung)
    if upper is None or rung == "6S":
        return 0.0
    rng = np.random.default_rng(0)

    def draw(lines, e_f):
        tot = 0.0
        for (ej, d5, s5), (_e, du, su) in zip(pol.LINES_5S[:len(lines)], lines):
            tot += ((d5 + rng.normal(0.0, s5)) * (du + rng.normal(0.0, su))
                    / (ej - e_f / 2.0))
        return abs(tot)

    vals = [draw(upper, e_cm) / draw(pol.LINES_6S, pol.E_6S_CM)
            for _ in range(n)]
    return float(np.std(vals))


def two_photon_element(rung: str, e_cm: float):
    """The FULL two-photon element, both halves, or None where unheld.

    Returns sum_j d(5S,j) d(j,f) / (E_j - E_f/2) over the nP this package
    holds on both sides. The ceiling below divides Delta-alpha by this,
    and dividing by the 5S half alone put 7S at 6.27 times the 6S element
    where both halves give 1.41, which inverted the ranking it feeds.
    """
    upper = UPPER_LINES.get(rung)
    if upper is None:
        return None
    virt = e_cm / 2.0
    return abs(sum(d5 * du / (ej - virt)
                   for (ej, d5, _s), (_e2, du, _s2)
                   in zip(pol.LINES_5S[:len(upper)], upper)))


def blackbody(e_cm: float):
    """Gap to the nearest nP and the thermal occupation at that gap."""
    ej = min((l[0] for l in pol.LINES_5S), key=lambda p: abs(p - e_cm))
    gap_cm = abs(ej - e_cm)
    lam_um = 1e4 / gap_cm
    x = gap_cm * 100.0 * 6.62607015e-34 * 2.99792458e8 / (KB * (T_C + 273.15))
    return gap_cm, lam_um, 1.0 / math.expm1(x), x


def main() -> int:
    R_a, res_a, eion_b, res_b = fit_the_p_series()
    form_high, form_low = ritz_form_error_nm()
    lad_a = ladder(R_a, EION)
    lad_b = ladder(R_ACCEPTED, eion_b)

    rows = []

    def add(rung, quantity, value, unit, basis, note, status):
        rows.append(dict(rung=rung, quantity=quantity, value=value, unit=unit,
                         basis=basis, note=note, status=status))

    add("_fit", "p_series_rydberg", f"{R_a:.2f}", "cm-1",
        "Ritz fit to the eight nP states with the package's ionisation limit held",
        f"worst residual {res_a:.2f} cm-1. The accepted Rb value is "
        f"{R_ACCEPTED}, so this fit sits {abs(R_a - R_ACCEPTED):.1f} above it and "
        "the ladder is quoted under both", "DIAGNOSTIC")
    add("_fit", "ritz_form_error", f"{form_high:.4g}", "nm",
        "worst wavelength error from fitting two adjacent nP states and "
        "predicting the next two",
        f"the D series' lower anchors give {form_low:.4g} nm. This is the "
        "METHOD's error and the row above is the FIT's, and quoting only the "
        "second understates a rung by about twenty-five", "DIAGNOSTIC")
    add("_fit", "p_series_limit_at_accepted_rydberg", f"{eion_b:.2f}", "cm-1",
        "the same fit with the Rydberg constant held instead",
        f"worst residual {res_b:.2f} cm-1, and {abs(eion_b - EION):.2f} cm-1 from "
        "the package's own limit. Neither fit resolves the pair, and their spread is "
        "carried on every extrapolated wavelength below", "DIAGNOSTIC")

    for rung in sorted(lad_a, key=lambda k: -2e7 / lad_a[k]):
        e_cm = lad_a[rung]
        lam = 2e7 / e_cm
        spread = abs(lam - 2e7 / lad_b[rung])
        in_band = BAND_NM[0] <= lam <= BAND_NM[1]
        prov = PROV.get(rung, "Rydberg-Ritz from the held anchors of this series")

        add(rung, "term_energy", f"{e_cm:.3f}", "cm-1", prov,
            "above the 5S1/2 ground state", "CALIB" if rung in PROV else "PRELIM")
        add(rung, "drive_wavelength", f"{lam:.3f}", "nm",
            "two-photon, 2e7 divided by the term energy in cm-1",
            f"{'inside' if in_band else 'OUTSIDE'} the 650 to 1050 nm band this "
            "producer covers", "CALIB" if rung in PROV else "PRELIM")
        # THE UNCERTAINTY MODEL, stated once and propagated analytically.
        # Two independent inputs carry everything. The term energy's own error
        # is the spread between the two admissible Rydberg-Ritz fits on an
        # extrapolated rung, and a bound on the NIST precision on a held one.
        # The waist's error is the input-beam regime the record does not pin,
        # so the aperture and resonator readings are its two ends and half
        # their span is the one-sigma. Everything geometric is a power of the
        # waist and propagates by that power.
        # The two-fit spread is the FIT's ambiguity. The FORM's own error is
        # measured on the nP series over the same lever arm and added, since a
        # ladder quoted at the spread alone understates it by a factor of
        # twenty-five (2026-09-09, checking this ladder against the chapter).
        # The D rungs do NOT take the nP analogue. The producer said so in
        # its own note while emitting it anyway, which is a cell and a note
        # disagreeing (corrected 2026-09-10). An extrapolated D rung carries
        # the independent miss; a held one carries the doublet it averages.
        _form = form_low if rung.endswith("D") else form_high
        if rung in PROV:
            lam_err = (2e7 / E_4D_CM - 2e7 / (E_4D_CM + E_4D_DOUBLET_CM / 2)
                       if rung == "4D" else 0.0005)
        elif rung.endswith("D"):
            lam_err = D_SERIES_INDEPENDENT_MISS_NM
        else:
            lam_err = math.hypot(spread, _form)
        e_err = lam_err * e_cm / lam
        add(rung, "term_energy_err", f"{e_err:.4g}", "cm-1",
            "the two-fit spread on an extrapolated rung, a bound on the NIST "
            "precision on a held one",
            "the held rows carry 0.01 cm-1, which is conservative for levels "
            "this low and is NOT a value this repository holds", "DIAGNOSTIC")
        add(rung, "drive_wavelength_err", f"{lam_err:.4g}", "nm",
            "the two-fit spread and the Ritz form's own measured extrapolation "
            "error, in quadrature",
            "on an S rung the form error comes from fitting two adjacent nP "
            "states and predicting the next two, the same lever arm. The D "
            "series cannot be tested that way here, having two anchors, so "
            "an extrapolated D rung carries the independent miss instead: "
            "E(5P3/2) plus the 5P3/2 to nD line puts 6D 0.35 nm from this "
            "ladder. Those two line wavelengths are NOT held here and the "
            "rung is owed a NIST lookup. The 4D row carries its doublet, "
            "this record not having checked the 4D J labels", "DIAGNOSTIC")
        if not in_band:
            continue

        wa = K.waist_at_drive(lam, input_beam="aperture")
        wr = K.waist_at_drive(lam, input_beam="resonator")
        add(rung, "waist_aperture_limited", f"{wa * 1e6:.3f}", "um",
            "rb5s6s.constants.waist_at_drive through the f = 150 mm singlet",
            "the input beam held common to every drive, which is what a hard "
            "stop at the EOM gives", "CALIB")
        # The waist carries two independent errors. The input-beam regime is
        # the new one and it dominates away from the reference wavelength. The
        # reference waist's own measurement band rides along, scaled by the
        # same ratio, and it is all there is AT the reference.
        _meas_rel = 0.5 * (K.W0_BAND_M[1] - K.W0_BAND_M[0]) / K.W0_MEASURED_M
        w_err = math.hypot(0.5 * abs(wr - wa), wa * _meas_rel)
        rel_w = w_err / wa
        add(rung, "waist_aperture_limited_err", f"{w_err * 1e6:.3f}", "um",
            "the input-beam regime's half-span and the reference waist's own "
            "measured band, in quadrature",
            "the regime term is zero at the reference wavelength and dominates "
            "everywhere else, which is the point: the record does not pin the "
            "input beam (A136) and the measurement it does hold was taken at "
            "one wavelength", "DIAGNOSTIC")
        add(rung, "waist_resonator_mode", f"{wr * 1e6:.3f}", "um",
            "the same with the input radius going as the root of the wavelength",
            "the unclipped alternative. The pair brackets the regime the record "
            "does not pin (A136), and the transit ratio between rungs measures "
            "which one the bench is in", "CALIB")
        add(rung, "waist_resonator_mode_err", f"{w_err * 1e6:.3f}", "um",
            "the same combination, the two regimes being the ends of one band",
            "the pair share the interval and its half-width", "DIAGNOSTIC")
        zr_m = math.pi * wa ** 2 / (lam * 1e-9)
        add(rung, "rayleigh_range", f"{zr_m * 1e3:.3f}", "mm",
            "pi w0^2 over the drive wavelength, at the aperture-limited waist",
            "it falls with the drive because the waist does", "CALIB")
        add(rung, "rayleigh_range_err",
            f"{zr_m * 1e3 * math.hypot(2 * rel_w, lam_err / lam):.4g}", "mm",
            "two powers of the waist and one of the wavelength, in quadrature",
            "the waist term dominates by three orders", "DIAGNOSTIC")
        l_m = K.collection_z_ratio() * (math.pi * K.W0_MEASURED_M ** 2
                                        / K.LAMBDA_LASER_M)
        z_ratio = l_m / zr_m
        add(rung, "collection_z_ratio", f"{z_ratio:.4f}", "dimensionless",
            "the bench's own collection half-length over this rung's Rayleigh range",
            "THE COLLECTION OPTICS ARE NOT RETUNED BY CHANGING THE DRIVE, so the "
            "half-length is the 993 nm one and only the Rayleigh range moves. The "
            "windowed third cumulant passes through zero near 1.117 and reverses "
            "beyond it", "CALIB")
        rel_zr = math.hypot(2 * rel_w, lam_err / lam)
        add(rung, "collection_z_ratio_err", f"{z_ratio * rel_zr:.4g}",
            "dimensionless", "the inverse Rayleigh range's own relative error",
            "the collection half-length is held fixed by the optics, so it "
            "contributes nothing here and its own error is chapter 12's item",
            "DIAGNOSTIC")
        add(rung, "k3_sign_reversed_by_the_window",
            "yes" if z_ratio > 1.117 else "no", "boolean",
            "z_ratio against the null of the axial window",
            "a rung past the null reports the third cumulant with the wrong sign "
            "unless the collection window is shortened. A boolean carries no "
            "uncertainty of its own and the ratio it reads is the row above, "
            "whose error is emitted there", "DIAGNOSTIC")
        add(rung, "kernel_width_spread_across_the_ramp",
            f"{math.sqrt(1.0 + z_ratio ** 2):.3f}", "dimensionless",
            "sqrt(1 + z_ratio^2), the transit width's span over the collected volume",
            "derived in A138: at shift u the contributing slices reach "
            "sqrt(min(1+z_ratio^2, s0/u)). It is the input to the covariance that "
            "sets the third cumulant's contamination", "CALIB")
        _sp = math.sqrt(1.0 + z_ratio ** 2)
        add(rung, "kernel_width_spread_across_the_ramp_err",
            f"{z_ratio ** 2 * rel_zr / _sp:.4g}", "dimensionless",
            "the collection ratio's error carried through sqrt(1 + r^2)",
            "it vanishes as the ratio does, which is why the wide-waist rungs "
            "carry almost none of it", "DIAGNOSTIC")
        add(rung, "transit_fwhm",
            f"{K.transit_fwhm_from_w0(wa, T_C):.4f}", "MHz",
            f"ln2 v_th / (pi w0) at {T_C:.0f} C, aperture-limited waist",
            "the width that carries the geometry to the FIRST power, which is "
            "how a two-drive campaign measures the input-beam regime", "CALIB")
        add(rung, "transit_fwhm_err",
            f"{K.transit_fwhm_from_w0(wa, T_C) * rel_w:.4g}", "MHz",
            "one inverse power of the waist",
            "the cell temperature is held at its set point here and its own "
            "spread is a separate axis", "DIAGNOSTIC")
        add(rung, "doppler_pedestal_fwhm", f"{pedestal_fwhm_mhz(e_cm):.2f}", "MHz",
            "the co-propagating component's Doppler width at 130 C, 85Rb",
            "linear in the term energy, so the shorter drives carry the wider "
            "pedestal and the narrow line sits on a flatter background", "CALIB")
        add(rung, "doppler_pedestal_fwhm_err",
            f"{pedestal_fwhm_mhz(e_cm) * e_err / e_cm:.4g}", "MHz",
            "linear in the term energy, so the energy's error carries straight",
            "the temperature's own error is not in this row and would dominate "
            "it: a one kelvin drift moves the width by about a tenth of a per "
            "cent", "DIAGNOSTIC")
        # THE STATIC POLARIZABILITY THE HELD LITERATURE DOES SUPPLY (2026-09-10).
        # Safronova and Safronova 2011 Table VI carries every rung of this
        # ladder except 7D. It is STATIC, so it is not the light shift's
        # differential at any drive, and the row below says so. It ranks the
        # rungs and it is the omega -> 0 closure the dynamic sum owes.
        _st = pol.STATIC_ALPHA_A011.get(_SAFRONOVA_KEY.get(rung, ""))
        if _st:
            add(rung, "static_scalar_polarizability_upper", f"{_st[0]:.0f}", "a.u.",
                "Safronova and Safronova 2011 Table VI, the held PDF",
                "STATIC. Equation 8 of that paper carries no frequency, so this "
                "is NOT the differential the light shift reads at this rung's "
                "drive: at 688.6 nm the 8S to 5P denominator is -16467 cm-1 "
                "against a photon of 14523. It ranks the rungs and it closes "
                "the dynamic sum at zero frequency", "CALIB")
            add(rung, "static_scalar_polarizability_upper_err", f"{_st[1]:.0f}",
                "a.u.", "the paper's own parenthesised uncertainty",
                "0.2 to 5 per cent depending on the state, the nd rows being "
                "the loosest", "DIAGNOSTIC")
        else:
            add(rung, "static_scalar_polarizability_upper", "", "a.u.",
                "absent from Safronova and Safronova 2011 Table VI",
                "7D is the one rung inside this band that table does not carry",
                "DIAGNOSTIC")
        d12 = pol.E_5P12_CM - e_cm / 2.0
        d32 = pol.E_5P32_CM - e_cm / 2.0
        add(rung, "intermediate_detuning_5p12", f"{d12:.1f}", "cm-1",
            "the 5P1/2 term energy minus half this rung's own",
            "negative where the virtual level sits ABOVE the real state", "CALIB")
        add(rung, "intermediate_detuning_5p12_err", f"{e_err / 2.0:.4g}", "cm-1",
            "half the term energy's error, the 5P level being held exactly",
            "the nP ladder is this package's own and carries no stated error "
            "on its positions", "DIAGNOSTIC")
        add(rung, "intermediate_detuning_5p32", f"{d32:.1f}", "cm-1",
            "the same against 5P3/2",
            "the nearer of the two on every rung above 5D", "CALIB")
        add(rung, "intermediate_detuning_5p32_err", f"{e_err / 2.0:.4g}", "cm-1",
            "half the term energy's error, as the row above",
            "the same nP ladder and the same silence about its own error",
            "DIAGNOSTIC")
        add(rung, "five_p_enhancement_relative_to_6s",
            f"{five_p_enhancement(e_cm) / five_p_enhancement(pol.E_6S_CM):.3f}",
            "dimensionless",
            "the 5S half of the two-photon matrix element, normalised on the 6S rung",
            "RELATIVE ONLY, and the upper-state element is held COMMON here "
            "BY CHOICE so the row ranks the intermediate resonance alone. "
            "It is not a transition rate and it is not the ceiling's "
            "element: two_photon_element_relative_to_6s carries both halves "
            "where this package holds them", "DIAGNOSTIC")
        add(rung, "alpha_5s_at_the_drive", f"{pol.alpha_5s(lam):.2f}", "a.u.",
            "rb5s6s.polarizability.alpha_5s at this rung's drive wavelength",
            "the half of the differential polarizability this package holds for "
            "every rung", "CALIB")
        _b = pol.mc_band(lambda kw5, kw6: pol.alpha_5s(lam, **kw5), n=400, seed=0)
        add(rung, "alpha_5s_at_the_drive_err",
            f"{0.5 * (_b['hi'] - _b['lo']):.4g}", "a.u.",
            "half the 16 to 84 band of rb5s6s.polarizability.mc_band at 400 draws",
            "the matrix elements, cores and tails drawn from their own quoted "
            "sigmas. Near a pole the band is asymmetric and the half-span "
            "understates the far side", "DIAGNOSTIC")
        if rung == "6S":
            da = pol.delta_alpha(lam)
        elif rung == "7S":
            da = pol.delta_alpha_7s(lam)
        elif rung == "5D":
            # The Hamilton-anchored construction, promoted into the package on
            # 2026-09-09 so this producer and run_projections.py share one
            # routine. It is an ENVELOPE and scalar only, which its own rows say.
            da = pol.delta_alpha_5d(lam)
        else:
            da = None
        if da is None:
            add(rung, "differential_polarizability", "", "a.u.",
                "no sum over states for this upper level in this repository",
                "empty and NULL rather than estimated: the shift coefficient is "
                "the one quantity a campaign would act on. THE ROUTE IS NOW "
                "NAMED, which it was not before 2026-09-10: Safronova and "
                "Safronova 2011 Table II carries the reduced E1 elements for "
                "these channels, so a frequency-dependent sum on NIST energies "
                "closes it, validated at zero frequency against the static row "
                "above", "NULL")
            add(rung, "on_axis_shift_per_watt", "", "MHz per W",
                "needs the differential polarizability above", "", "NULL")
        else:
            _src = ("the Hamilton-anchored construction of "
                    "rb5s6s.polarizability.delta_alpha_5d, scalar only and an "
                    "envelope, not a sum over states" if rung == "5D"
                    else "alpha(upper) minus alpha(5S), this package's own sum "
                    "over states")
            add(rung, "differential_polarizability", f"{da:.2f}", "a.u.", _src,
                "the 993 nm sign is under dispute and the magnitude is what every "
                "bound reads", "ENVELOPE" if rung == "5D" else "CALIB")
            if rung == "6S":
                _db = pol.mc_band(
                    lambda kw5, kw6: pol.alpha_6s(lam, **kw6) - pol.alpha_5s(lam, **kw5),
                    n=400, seed=0)
                _da_note = ("both sides of the difference drawn from their own "
                            "quoted sigmas")
            else:
                _db = pol.mc_band(lambda kw5, kw6: pol.alpha_5s(lam, **kw5),
                                  n=400, seed=0)
                _da_note = ("ONLY the 5S side is drawn: mc_band samples the 5S "
                            "and 6S ladders and this package states no sigmas "
                            "for the 7S elements, so this is a LOWER BOUND on "
                            "the true error and not the error")
            _da_err = 0.5 * (_db["hi"] - _db["lo"])
            add(rung, "differential_polarizability_err", f"{_da_err:.4g}", "a.u.",
                "half the 16 to 84 band of rb5s6s.polarizability.mc_band at 400 draws",
                _da_note, "DIAGNOSTIC")
            from rb5s6s import lineshape
            add(rung, "on_axis_shift_per_watt",
                f"{lineshape.stark_shift_S0_mhz(1.0, wa, K.RHO_RETRO, abs(da)):.2f}",
                "MHz per W",
                "at this rung's OWN achievable waist and the retro ratio of record",
                "the waist is not common across rungs (A136), so this is not the "
                "polarizability ratio", "CALIB")
            _s0w = lineshape.stark_shift_S0_mhz(1.0, wa, K.RHO_RETRO, abs(da))
            add(rung, "on_axis_shift_per_watt_err",
                f"{_s0w * math.hypot(_da_err / abs(da), 2 * rel_w, K.RHO_RETRO_ERR / (1.0 + K.RHO_RETRO)):.4g}",
                "MHz per W",
                "the polarizability, two powers of the waist and the retro ratio, "
                "in quadrature",
                "the waist term dominates on every rung away from 993 nm, which "
                "is the finding this producer exists for", "DIAGNOSTIC")
        # THE LADDER'S OWN CEILING, and it is not the one the power sets
        # (owner design, 2026-09-09). The light shift goes as Delta-alpha times
        # the intensity and the two-photon Rabi frequency as |M| times it, and
        # both carry the SAME 5P denominator, so along the ladder they move
        # together. Two consequences follow with no free parameter: the shift
        # at which saturation bites goes as Delta-alpha over |M|, and the rate
        # AT that ceiling is invariant. Master plan 5s.3.
        # THE CEILING TAKES THE FULL ELEMENT, both halves, and is refused
        # where this package does not hold the upper one. It divided by the
        # 5S half until 2026-09-10, which put 7S at 0.609 (it
        # saturates EARLIER) and 2.697 at a fixed shift (a shot-noise GAIN);
        # both halves give 2.7152 and 0.1356, so the rung saturates later
        # and delivers about an eighth of the rate at a fixed shift. The
        # reading inverted, not the digits. This comment carried 2.90 and
        # 0.119 until 2026-09-10, back-solved from an m_rel of 1.317 before
        # the producer's own Delta-alpha ratio was used, so it disagreed with
        # the cells three lines below it.
        _m_abs = two_photon_element(rung, e_cm)
        _m_ref = two_photon_element("6S", pol.E_6S_CM)
        m_rel = _m_abs / _m_ref if _m_abs is not None else None
        if m_rel is not None:
            add(rung, "two_photon_element_relative_to_6s", f"{m_rel:.4f}",
                "dimensionless",
                "both halves summed over the nP this package holds, on 6S",
                "the element the ceiling divides by. The 5S-half row above "
                "ranks the intermediate resonance alone and reads higher on "
                "every rung whose upper element is the smaller half, the "
                "upper element being what that row holds common. This note "
                "carried the 7S numbers as literals until 2026-09-10 and was "
                "emitted on every rung, so the 6S row said 6.27 against 1.41 "
                "where both of its own cells read one", "DIAGNOSTIC")
            add(rung, "two_photon_element_relative_to_6s_err",
                f"{_m_err(rung, e_cm):.4g}", "dimensionless",
                "drawn from the held reduced-element sigmas on both halves, "
                "twenty thousand draws, seeded",
                "1.69 per cent on the 7S rung. The elements are summed "
                "UNSIGNED here and the nP terms above 5P carry the opposite "
                "sign to the 5P ones, about four per cent of each element, "
                "which is a systematic this row does NOT carry", "DIAGNOSTIC")
        # THE RUNG'S OWN NATURAL WIDTH IS IN ALL THREE ROWS AND WAS HELD
        # COMMON UNTIL 2026-09-10. The ceiling is the shift at which the
        # two-photon Rabi frequency reaches a fixed fraction f of the natural
        # width, so Omega = f Gamma gives S0_ceiling = f Delta-alpha Gamma/|M|,
        # and the unsaturated rate Omega^2/Gamma carries Gamma too. Holding it
        # common put the 7S ceiling at 2.715 against a true 1.405, the rate at
        # a fixed shift at 0.136 against 0.262, and made the rate at each
        # rung's own ceiling exactly one, which was then published as a
        # zero-parameter invariance. It is the width ratio, and the record
        # held tau(7s) in the Safronova 2011 PDF the same producer reads for
        # Table VI. Only the rungs whose lifetime this package holds get these
        # rows at all; the others are refused with the reason below.
        g_rel = GAMMA_REL.get(rung)
        if da is not None and m_rel is not None and g_rel is not None:
            a_rel = abs(da) / abs(pol.delta_alpha(2e7 / pol.E_6S_CM))
            add(rung, "natural_width_relative_to_6s", f"{g_rel:.4f}",
                "dimensionless",
                "the rung's own natural width over the 6S rung's, from the "
                "held lifetimes",
                "enters all three ceiling rows below. Held common at one until "
                "2026-09-10, which is what made the third of them an identity",
                "CALIB")
            add(rung, "natural_width_relative_to_6s_err", f"{_g_err(rung):.4g}",
                "dimensionless",
                "the two held lifetimes' own sigmas in quadrature, 45.57(17) "
                "and 88.07(40) ns",
                "0.59 per cent on the 7S rung. The ELEMENT ratio beside it "
                "carries 1.69 per cent from the held reduced-element sigmas, "
                "drawn rather than linearised, and the two together set the "
                "ceiling rows' own errors", "DIAGNOSTIC")
            add(rung, "saturation_shift_ceiling_relative",
                f"{a_rel * g_rel / m_rel:.4f}", "dimensionless",
                "Delta-alpha times the natural width over the matrix element, "
                "against the 6S rung",
                "the shift at which the two-photon Rabi frequency reaches a "
                "fixed fraction of the natural width. BELOW ONE MEANS THIS RUNG "
                "SATURATES EARLIER, which is the opposite of what a larger "
                "coefficient suggests on its own", "DIAGNOSTIC")
            _rel_e = (math.hypot(_g_err(rung) / g_rel, _m_err(rung, e_cm) / m_rel)
                      if rung != "6S" else 0.0)
            add(rung, "saturation_shift_ceiling_relative_err",
                f"{abs(a_rel * g_rel / m_rel) * _rel_e:.4g}", "dimensionless",
                "the width and element sigmas in quadrature, relative",
                "the differential polarizability's own uncertainty is NOT in "
                "this row: carrying it is owed", "DIAGNOSTIC")
            add(rung, "rate_at_a_fixed_shift_relative",
                f"{(m_rel / a_rel) ** 2 / g_rel:.4f}", "dimensionless",
                "the square of the matrix element over the coefficient, divided "
                "by the natural width, against 6S",
                "the shot-noise gain this rung offers at the SAME on-axis shift, "
                "which is where the ladder pays. The row below evaluates the "
                "same rate at each rung's own ceiling instead", "DIAGNOSTIC")
            _rate_e = (math.hypot(_g_err(rung) / g_rel,
                                  2 * _m_err(rung, e_cm) / m_rel)
                       if rung != "6S" else 0.0)
            add(rung, "rate_at_a_fixed_shift_relative_err",
                f"{abs((m_rel / a_rel) ** 2 / g_rel) * _rate_e:.4g}",
                "dimensionless",
                "the width sigma and twice the element sigma, in quadrature",
                "twice, because the rate carries the element squared. The "
                "differential polarizability's own uncertainty is owed here "
                "too", "DIAGNOSTIC")
            add(rung, "rate_at_its_own_ceiling_relative", f"{g_rel:.4f}",
                "dimensionless",
                "the same rate evaluated at each rung's own saturation ceiling, "
                "which reduces to the natural width ratio",
                "THIS ROW HAS BEEN READ THREE WAYS IN TWO DAYS and this is the "
                "first reading with the width in it. At the ceiling Omega = f "
                "Gamma, so the rate is f^2 Gamma and the ratio is the width "
                "ratio alone: every other factor cancels. It was published as "
                "one, first as the result and then as an algebraic identity, "
                "and both readings were artefacts of holding the width common. "
                "The ladder does NOT deliver the same signal at each rung's "
                "own saturation ceiling: a longer-lived upper state delivers "
                "less", "DIAGNOSTIC")
            add(rung, "rate_at_its_own_ceiling_relative_err",
                f"{_g_err(rung):.4g}", "dimensionless",
                "the width ratio's own sigma, since the row reduces to it",
                "every other factor cancels exactly, so this row's error is "
                "the two lifetimes' and nothing else", "DIAGNOSTIC")
        else:
            # ONE BRANCH, TWO CAUSES, AND THE REASON IS COMPUTED PER RUNG. It
            # carried a single literal naming the differential polarizability
            # until 2026-09-10, which is false for 5D alone: 5D's differential
            # is present at 28648.70 in the row four lines above, and what it
            # lacks is the upper-state line list. The reason is derived from
            # which input is actually absent, so a partial repair cannot leave
            # a true NULL wearing a false explanation.
            _absent = ("the natural width: this package holds no lifetime "
                       "for this rung's upper state"
                       if (da is not None and m_rel is not None) else
                       "the two-photon matrix element: this package holds no "
                       "upper-state line list for this rung, and the "
                       "differential polarizability above is present"
                       if da is not None else
                       "the differential polarizability, which is empty above")
            for q in ("saturation_shift_ceiling_relative",
                      "rate_at_a_fixed_shift_relative",
                      "rate_at_its_own_ceiling_relative"):
                add(rung, q, "", "dimensionless", f"needs {_absent}",
                    "empty rather than estimated: a rung ranked on part of its "
                    "own element is what produced the readings A148 retired",
                    "DIAGNOSTIC")
        gap_cm, gap_um, occ, x = blackbody(e_cm)
        add(rung, "nearest_np_gap", f"{gap_um:.2f}", "um",
            "the nearest nP level of the held ladder, as a wavelength",
            "what couples the upper state to the cell's own thermal field",
            "CALIB")
        add(rung, "nearest_np_gap_err", f"{gap_um * e_err / gap_cm:.4g}", "um",
            "the term energy's error over the gap, the nP level being exact here",
            "it is large where the gap is small, which is the high rungs",
            "DIAGNOSTIC")
        add(rung, "thermal_occupation_at_that_gap", f"{occ:.3e}", "dimensionless",
            f"1/(exp(hv/kT) - 1) at {T_C:.0f} C, hv/kT = {x:.2f}",
            "above about a per cent the thermal field moves population out of "
            "the upper state at a fair fraction of its own decay rate", "CALIB")
        add(rung, "thermal_occupation_at_that_gap_err",
            f"{occ * (1.0 + occ) * x * e_err / gap_cm:.3e}", "dimensionless",
            "the occupation's own derivative in the gap, times the gap's error",
            "the cell temperature dominates this in practice and is not in "
            "this row: ten kelvin moves the occupation by about a fifth at the "
            "high rungs", "DIAGNOSTIC")
        add(rung, "detection_arm", DETECTION[rung], "", "the cascade this rung emits on",
            "the 993 nm rung is the only one the bench's installed 795 nm filter "
            "already serves. A cascade identification is not a measured value",
            "DIAGNOSTIC")

    # RESOLVED THROUGH THE CONFIG, never built from __file__. Until 2026-09-11
    # this line joined the repository root to "results" by hand, so it ignored
    # RB5S6S_RESULTS_DIR and wrote into the live tree even when the caller had
    # redirected it. The freshness verifier then compared a committed file
    # against itself and passed.
    from rb5s6s import config as _CFG
    dest = os.path.join(str(_CFG.RESULTS_DIR), "transition_ladder.csv")
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {dest} with {len(rows)} rows")
    for rung in sorted(lad_a, key=lambda k: -2e7 / lad_a[k]):
        lam = 2e7 / lad_a[rung]
        mark = "" if BAND_NM[0] <= lam <= BAND_NM[1] else "   (out of band)"
        print(f"  {rung:>3s}  {lam:8.2f} nm{mark}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
The M16 polarizability model must reproduce precision measurements it does not
use before any derived number (the Delta_alpha recompute, the magic
wavelengths) is quotable: the measured 5S static polarizability, the measured
5S scalar tune-out between the D lines, the Safronova-group 6S static, and the
|Delta_alpha(993)| magnitude the shipped analysis rides on. A model that
misses any of these anchors has a data-entry or formula error and must not
ship its magic wavelengths.
"""

from __future__ import annotations

import pytest


from rb5s6s.polarizability import (alpha_5s, alpha_6s, alpha_7s, delta_alpha,
                                   delta_alpha_7s, tuneout_5s, magic_wavelengths,
                                   magic_5s7s, mc_band, MAGIC_5S5D52_EXP_NM,
                                   RME_5P32_5D52)


def test_static_anchors():
    # measured alpha_5S(0) = 318.79(1.42) au (Holmgren 2010)
    assert abs(alpha_5s(0.0) - 318.79) < 3.0
    # Safronova-group alpha_6S(0) = 5167(22) au (tail is calibrated to it, so
    # this checks the big valence terms carry the right energies and signs)
    assert abs(alpha_6s(0.0) - 5167.0) < 25.0


def test_measured_tuneout_reproduced():
    # Leonard et al. 2015 as corrected by their 2017 erratum (PRA 95,
    # 059901(E)): 790.032326(32) nm. The model does not use this number;
    # hitting it validates the D-line matrix-element ratio and the
    # 6P-12P + tail + core budget at the few-pm level.
    #
    # The "790.03235(3)" that stood here until 2026-07-31 appears in NEITHER
    # document -- see rb5s6s/polarizability.py:tuneout_5s. The tolerance is
    # 0.2 nm, three orders above the 0.062 pm between the published values, so
    # this assertion never distinguished them; only the provenance changed.
    assert abs(tuneout_5s() - 790.032326) < 0.2


def test_delta_alpha_993_magnitude_matches_orson():
    # Since the 2026-08-24 adjudication the package constant IS the
    # recompute's value, so the ~5-per-cent magnitude claim is against the
    # CITED Orson figure, kept under its own name. The sign relationship
    # lives in tests/test_polarizability_sign_divergence.py.
    from rb5s6s.constants import DELTA_ALPHA_AU_ORSON2021
    da = delta_alpha(993.0)
    assert abs(abs(da) / DELTA_ALPHA_AU_ORSON2021 - 1.0) < 0.10, da
    assert da < 0.0, "sign finding: alpha_6S(993) < alpha_5S(993) (blue shift)"


def test_the_993_sign_and_its_margin():
    """The sign disagreement with Orson 2021 is the item going to external
    theorists, so both halves of the claim are pinned here -- including the
    half that is NOT robust.

    alpha_5S(993) is unanimous: 993 nm is red of every strong 5S line, so every
    term is positive and no single-line revision can flip it. That is asserted
    directly.

    alpha_6S(993) is NOT unanimous -- it is a partial cancellation between the
    upward 6S-6P group (~-846) and the downward 6S-5P cascade (~+623), netting
    about -312. Its sign therefore has a finite margin, and the margin itself
    is the interesting quantity for the correspondence: it says the dispute
    lives in the 6P-vs-5P matrix-element balance. Guarded so neither the sign
    nor the margin can drift unnoticed.
    """
    from rb5s6s import polarizability as P
    a5, a6 = alpha_5s(993.0), alpha_6s(993.0)
    assert a5 > 0 > a6, (a5, a6)

    # 5S: unanimous -- scaling ANY single line by +-50% must leave it positive
    for i in range(len(P.LINES_5S)):
        for k in (0.5, 1.5):
            bumped = [list(t) for t in P.LINES_5S]
            bumped[i][1] *= k
            saved = P.LINES_5S[:]
            P.LINES_5S = [tuple(t) for t in bumped]
            try:
                assert alpha_5s(993.0) > 0, (i, k)
            finally:
                P.LINES_5S = saved

    # 6S: a cancellation. Pin the margin rather than pretend it is unanimous --
    # the two cascade lines are the ones that can flip it, and they need large
    # revisions to do so (a few percent is the plausible matrix-element error).
    def flip_factor(i):
        saved = P.LINES_6S[:]
        lo, hi = 1.0, 4.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            bumped = [list(t) for t in saved]
            bumped[i][1] *= mid
            P.LINES_6S = [tuple(t) for t in bumped]
            try:
                v = alpha_6s(993.0)
            finally:
                P.LINES_6S = saved
            if v >= 0:
                hi = mid
            else:
                lo = mid
        return 0.5 * (lo + hi)

    # index the two downward 6S->5P cascade lines by their level energies
    cascade = [i for i, (e, _, _) in enumerate(P.LINES_6S) if e < P.E_6S_CM]
    assert cascade, "no downward 6S->5P lines found"
    factors = sorted(flip_factor(i) for i in cascade)
    # the easiest flip needs a >25% strength revision; if this ever drops below
    # that, the sign has become genuinely fragile and the claim must be requalified
    assert factors[0] > 1.25, factors


def test_magic_crossings_exist_and_trap():
    magic = magic_wavelengths(950.0, 1500.0)
    lams = [m[0] for m in magic]
    # the clean crossing far from every 6S pole
    assert any(abs(l - 1204.0) < 15.0 for l in lams), lams
    # every reported crossing must trap the ground state (alpha > 0)
    assert all(a > 0.0 for _, a in magic), magic


def test_magic_search_guards_the_5s_d_lines():
    """magic_wavelengths once bracketed its search with the 6S->nP poles only,
    which is safe inside the default 950-1500 nm window but not below it: run
    from 700 nm it returned the 5S D-line poles (780.24, 794.98 nm) as
    apparent crossings with |alpha| of order 1e11 a.u. Widened searches are
    quoted in FUTURE_TRANSITIONS_titsapph.md section 3.3, so the guard must
    hold both states' pole sets."""
    magic = magic_wavelengths(700.0, 1000.0)
    assert len(magic) == 1, magic
    lam, alpha = magic[0]
    # the one real crossing, between the D lines beside the 5S tune-out
    assert abs(lam - 790.1298) < 0.01, magic
    assert abs(alpha - (-244.3)) < 1.0, magic
    for pole in (780.24, 794.98):
        assert abs(lam - pole) > 1.0, magic


def test_mc_band_deterministic():
    f = lambda k5, k6: 1.0
    b1, b2 = mc_band(f, n=50, seed=3), mc_band(f, n=50, seed=3)
    assert b1 == b2


def test_mc_band_reports_one_sigma_not_some_other_percentile():
    """mc_band's docstring promises the 16/84 percentiles, i.e. a 1-sigma band,
    and every uncertainty this module quotes is that half-width. Nothing pinned
    it: the reproducibility test above passes a CONSTANT functional, for which
    lo == hi == median whatever percentiles the code uses, so 16/84 -> 5/95
    inflated every published band x1.62 with the suite still green (mutation
    test, 2026-07-29).

    Pinned here against a functional whose spread is known analytically. Drawing
    the 5S core straight through gives Normal(CORE_5S, CORE_5S_SIG), so the
    half-width (hi-lo)/2 must come back as CORE_5S_SIG. 5/95 would return
    1.645x that and fail by a wide margin."""
    from rb5s6s.polarizability import CORE_5S, CORE_5S_SIG

    band = mc_band(lambda k5, k6: k5["core"], n=20_000, seed=11)
    assert band["failed"] == 0 and band["n"] == 20_000
    assert band["median"] == pytest.approx(CORE_5S, abs=0.05 * CORE_5S_SIG)
    half = 0.5 * (band["hi"] - band["lo"])
    assert half == pytest.approx(CORE_5S_SIG, rel=0.04), (
        f"mc_band half-width {half:.4g} is not the 1-sigma {CORE_5S_SIG:.4g}; "
        f"ratio {half / CORE_5S_SIG:.3f} (1.645 would mean 5/95 percentiles)")


# --- the Ti:Sapph ladder: 5S->7S (independent) and 5S->5D5/2 (Hamilton anchor) ---

def test_7s_static_follows_the_ns_trend():
    # 7S static is large and positive, dominated by the near-degenerate 7S-7P
    # (gap 1524 cm^-1); it must exceed the 6S static (5167) and land on the
    # 319 -> 5167 -> ~3e4 ns trend. A sign flip or an order-of-magnitude miss
    # would flag a wrong 7S-nP element or energy.
    a7 = alpha_7s(0.0)
    assert a7 > alpha_6s(0.0) > 0.0, a7
    assert 2.5e4 < a7 < 4.0e4, a7


def test_5s7s_magic_signflips_bracket_the_near_pole_and_tuneout():
    lams = [x for x, _ in magic_5s7s(700.0, 1000.0)]
    # one crossing just red of the 7S-5P3/2 pole (741 nm), one beside the 5S
    # tune-out (790.03) -- both are the light-shift sign-flip locations
    assert any(741.0 < l < 745.0 for l in lams), lams
    assert any(789.0 < l < 792.0 for l in lams), lams


def test_delta_alpha_7s_is_a_large_red_shift_at_the_760_drive():
    # 760 nm sits between the 7S-5P poles (728/741) and the 5S D lines (780/795),
    # so alpha_5S dominates and Delta_alpha = alpha_7S - alpha_5S is large positive
    d = delta_alpha_7s(760.0)
    assert d > 2000.0, d


def test_5d_anchor_is_hamilton_2023():
    # 5D5/2 is adopted, not recomputed: the magic wavelength is Hamilton 2023's
    # measured 776.179(5) nm and the near-resonant 5P3/2-5D5/2 element 1.80(6)
    assert abs(MAGIC_5S5D52_EXP_NM - 776.179) < 0.01
    assert abs(RME_5P32_5D52 - 1.80) < 0.01


def test_sign_is_anchored_to_measurements_not_to_a_convention():
    """The Delta_alpha(993) sign disagreement with Orson 2021 is the most
    falsifiable claim in the repo, so the anchor has to be explicit.

    This work's sign is not a convention choice. alpha_5S is pinned by two
    measurements the model does not fit: the static polarizability (+318.79(1.42)
    measured) and the tune-out wavelength (790.032326(32) nm measured, Leonard's
    2015 value as corrected by their 2017 erratum). A ground
    state far below resonance must be positively polarizable; if that ever comes
    out negative the sum-over-states has a global sign fault and every
    Delta_alpha statement downstream is void.

    Orson's published alpha_56 = -1093 (verified verbatim from the typeset PDF
    2026-07-29, with his convention stated in words, the SI value also negative,
    and a worked -0.66 MHz red shift this repo reproduces at -0.653) has the
    opposite sign to this work's +1145 in the same convention.
    """
    from rb5s6s.polarizability import alpha_5s, delta_alpha
    # far below every resonance the ground state is positively polarizable
    assert alpha_5s(1.0e7) > 0
    assert alpha_5s(1.0e7) == pytest.approx(318.79, abs=3.0), \
        "static alpha_5S no longer reproduces the measured value -- sign anchor lost"
    # and the disagreement, in Orson's convention
    alpha56_here = -delta_alpha(993.4)
    assert alpha56_here > 0, "this work gives alpha_56 > 0; Orson prints -1093"
    assert abs(abs(alpha56_here) / 1093.0 - 1.0) < 0.10, \
        "magnitudes no longer agree to ~5%; the sign-error diagnostic rests on that"


def test_orsons_sign_would_require_an_excluded_6S_lifetime():
    """The answer to "how do we know the sign error isn't yours".

    The Delta_alpha(993) sign hinges on alpha_6S: this work gets -312 a.u.,
    Orson's published alpha_56 = -1093 implies +1925. Reaching +1925 is not a
    matter of taste, because alpha_6S(993) is a cancellation with only one
    adjustable side. The upward 6S-6P group contributes -949 and its sign is
    structural -- at 993 nm the drive sits ABOVE the 2732 nm resonance, so
    omega > omega_0 makes every one of those denominators negative. Only the
    downward 6S-5P cascade can move, and it would have to supply +2874 instead
    of +624.

    That is a factor 4.6 in alpha, hence 2.15 in the dipole elements -- and
    those same elements set the 6S lifetime. Unscaled they give 45.42 ns
    against the MEASURED 45.57(17) ns -- Gomez 2005, itself 45.64(22) in a
    vapour cell and 45.48(25) in a MOT, averaged. (Arora & Sahoo's 45.44(8) is
    THEORY from matrix elements 4.144/6.048, essentially the ones used here, so
    it checks the arithmetic and is not a second measurement.) Scaled to reach
    Orson's sign they give 9.9 ns, ~210 sigma from the measurement.

    So the sign disagreement is not symmetric: one side is anchored to a
    measured lifetime and the other is not. This test fails if the matrix
    elements, the level energies or the prefactor ever drift enough to break
    that anchor.
    """
    from rb5s6s.polarizability import LINES_6S, E_6S_CM, CM_PER_HARTREE, alpha_5s

    alpha_fs = 1.0 / 137.035999084
    au_time = 2.4188843265857e-17
    w_drive = 1e7 / 993.4 / CM_PER_HARTREE

    def alpha6(scale_down):
        s = 0.0
        for e, d, _ in LINES_6S:
            de = (e - E_6S_CM) / CM_PER_HARTREE
            dd = d * scale_down if de < 0 else d
            s += 2.0 * de * dd * dd / (de * de - w_drive * w_drive)
        return s / 6.0

    def tau(scale_down):
        rate = 0.0
        for e, d, _ in LINES_6S:
            de = e - E_6S_CM
            if de >= 0:
                continue
            w = abs(de) / CM_PER_HARTREE
            rate += (4.0 / 3.0) * alpha_fs ** 3 * w ** 3 * (d * scale_down) ** 2 / 2.0
        return au_time / rate

    # the unscaled elements reproduce the measured lifetime
    assert tau(1.0) * 1e9 == pytest.approx(45.5, rel=0.02), \
        "6S-5P elements no longer reproduce the measured 45.5 ns lifetime"

    # the upward group's sign is structural, not fitted
    up = sum(2.0 * (de := (e - E_6S_CM) / CM_PER_HARTREE) * d * d
             / (de * de - w_drive * w_drive) / 6.0
             for e, d, _ in LINES_6S if e > E_6S_CM)
    assert up < 0, "upward 6S-6P group should be negative at 993 nm (drive above resonance)"

    # what Orson's sign costs
    from scipy.optimize import brentq
    target = alpha_5s(993.4) + 1093.0
    k = brentq(lambda x: alpha6(x) - target, 1.0, 5.0)
    assert k > 1.8, f"scale factor {k:.2f} unexpectedly small -- re-derive the argument"
    assert tau(k) * 1e9 < 15.0, (
        f"Orson's sign would need tau(6S) = {tau(k) * 1e9:.1f} ns; measured is 45.5(2)")


def test_metres_for_nanometres_raise_instead_of_answering():
    """The one unit guard, at the one trap that is silent and catastrophic.

    993.4e-9 passed to delta_alpha used to return 3.7 a.u., a plausible
    number for an impossible input, and that shape of failure is what the
    release audit found to matter most for a stranger. The experimenter's
    adjudication (2026-08-24): guard wavelengths alone, generously, and
    let every other argument trust the unit its name states, because
    eleven functions of invented ranges would ceiling someone else's
    physics. 50 nm to 50 um admits any wavelength a caller could mean.
    """
    import pytest as _pytest

    from rb5s6s import alpha_5s, alpha_6s, two_photon_matrix_element

    for fn in (delta_alpha, alpha_5s, alpha_6s, two_photon_matrix_element):
        with _pytest.raises(ValueError, match="NANOMETRES"):
            fn(993.4e-9)          # metres
        with _pytest.raises(ValueError, match="NANOMETRES"):
            fn(0.9934)            # microns
        with _pytest.raises(ValueError):
            fn(-993.4)
    # and the guard must NOT ceiling the package's own physics: the static
    # limit and the far infrared pass, which the guard's first day taught
    # when a generous band rejected the module's own lam_nm = 0 calls
    alpha_5s(0.0)
    alpha_5s(1.0e7)
    assert abs(delta_alpha(993.4) - (alpha_6s(993.4) - alpha_5s(993.4))) < 1e-9

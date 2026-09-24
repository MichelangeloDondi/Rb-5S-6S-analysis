"""Closure tests for the clipped, focused beam field (rb5s6s/beam_field.py).

Each test is PLANTED BOTH WAYS in spirit even where it is not a literal negative-case plant: (a) and
(e) check the module's own quadrature against an INDEPENDENTLY DERIVED closed form (never against
the module's own prior output), (b) checks it against the existing package's own independently
implemented closed form (`lineshape.aperture_onaxis_factor_actual`), (c) checks a genuine asymptote
two ways (a swept large input AND a separately-coded exact uniform-illumination limit), and (d)
reproduces an independent reading from the thesis side and reports the module's own converged number
against it without adjusting the module to fit.

THE REFERENCE FORMULA FOR (a) AND (e), AND WHY IT IS NOT THE NAIVE ONE. A collimated Gaussian beam
of radius w_in incident on a thin lens with its OWN waist already at the lens focuses to
w0 = lambda f / (pi w_in) at z = f from the lens -- but only in the limit that the input beam's own
Rayleigh range zR_in = pi w_in^2 / lambda is much larger than f. `ClippedBeam` computes the exact
answer (verified against this file's own independent q-parameter derivation, not assumed), which
carries a genuine, small "focus shift" away from z = f when zR_in is not >> f (a standard, textbook
Gaussian-beam-through-a-lens result, unrelated to clipping). At this file's own w_in = 2 mm,
zR_in/f is about 84, and the shift is still about 1e-2 of one Rayleigh range -- enough to move a
1e-3-tolerance test at a few Rayleigh ranges from focus, so the reference formula computed here is
the EXACT one (the same standard formula, evaluated from the true waist location z0 rather than
assuming z0 = 0), not a simplification.
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.optimize import brentq

from rb5s6s import constants as K
from rb5s6s import lineshape as L
from rb5s6s.beam_field import ClippedBeam, axial_half_intensity_depth_m, mode_weights_for_m2

LAM = K.LAMBDA_LASER_M
F = K.DRIVE_LENS_F_M


def _q_out(z_m: float, w_in_m: float, f_m: float = F, lam_m: float = LAM, d_ap_m: float = 0.0) -> complex:
    """The complex beam parameter, at z from the lens, of a Gaussian with its OWN waist w_in_m at
    a distance d_ap_m before the lens -- the exact ABCD/Collins q-transform `ClippedBeam._r_scale`
    also uses, reproduced independently here (not imported) so the test does not validate the
    module against its own formula."""
    zR_in = math.pi * w_in_m ** 2 / lam_m
    q_in = 1j * zR_in
    A = -z_m / f_m
    B = f_m + z_m * (1.0 - d_ap_m / f_m)
    C = -1.0 / f_m
    D = 1.0 - d_ap_m / f_m
    return (A * q_in + B) / (C * q_in + D)


def _focused_gaussian_reference(w_in_m: float, f_m: float = F, lam_m: float = LAM):
    """(w0, zR, z0): the EXACT focused-Gaussian waist radius, Rayleigh range and shift (z0, measured
    from the paraxial z = f plane) for a collimated input of radius w_in_m. w(z) = w0 sqrt(1 +
    ((z - z0)/zR)^2) then holds exactly (standard Gaussian-beam propagation from the TRUE waist)."""
    z0 = brentq(lambda z: _q_out(z, w_in_m, f_m, lam_m).real, -0.2 * f_m, 0.2 * f_m)
    w0 = math.sqrt(-lam_m / (math.pi * (1.0 / _q_out(z0, w_in_m, f_m, lam_m)).imag))
    zR = math.pi * w0 ** 2 / lam_m
    return w0, zR, z0


# ---------------------------------------------------------------------------------------------
# (a) the Gaussian limit: a bore far wider than the beam
# ---------------------------------------------------------------------------------------------

def test_unclipped_limit_matches_the_focused_gaussian_to_1e3():
    """w(z) and I(r, z)/I_peak follow the exact focused-Gaussian formulas (module docstring's
    q-parameter reference, reproduced independently above) to 1e-3, for a bore so wide (10x the
    input radius, transmitting 1 - exp(-200) of the power) that clipping is not the question here
    -- the Fresnel/Collins machinery away from the focal plane is."""
    w_in = 2.0e-3
    a_m = 20e-3
    beam = ClippedBeam(w_in_m=w_in, a_m=a_m, n_z=61, n_xi=140, n_rho=500, z_span_zr=3.0)
    w0, zR, z0 = _focused_gaussian_reference(w_in)

    # the beam's own reading of its focus agrees with the closed-form focused-Gaussian waist
    assert beam.actual_focus_m() == pytest.approx(w0 * math.sqrt(1.0 + (z0 / zR) ** 2), rel=1e-3)

    for z in np.linspace(-3.0 * zR, 3.0 * zR, 25):
        got_w = beam.w(float(z))
        exp_w = w0 * math.sqrt(1.0 + ((z - z0) / zR) ** 2)
        assert got_w == pytest.approx(exp_w, rel=1e-3), f"w(z) at z={z:.4e}"

    for z in np.linspace(-3.0 * zR, 3.0 * zR, 9):
        wz = w0 * math.sqrt(1.0 + ((z - z0) / zR) ** 2)
        for frac in (0.0, 0.4, 0.8, 1.2):
            b = frac * wz
            u_exp = (w0 / wz) ** 2 * math.exp(-2.0 * b ** 2 / wz ** 2)
            u_got = beam.u(float(b), float(z))
            assert u_got == pytest.approx(u_exp, rel=1e-3, abs=1e-8), f"u(b,z) at z={z:.4e}, b={b:.4e}"


def test_unclipped_limit_plant_a_narrowed_bore_breaks_it():
    """PLANT: narrowing the SAME beam's bore to something the input actually feels must break the
    match above -- otherwise the test is not sensitive to clipping at all, and the a_m = 20 mm
    choice above would be unverified as 'wide enough' rather than known to be."""
    w_in = 2.0e-3
    a_m_tight = 1.0 * w_in  # transmits exp(-2) ~ 13.5% of the power: clipping obviously matters
    beam = ClippedBeam(w_in_m=w_in, a_m=a_m_tight, n_z=21, n_xi=140, n_rho=600, z_span_zr=2.0)
    w0, zR, z0 = _focused_gaussian_reference(w_in)
    rel = abs(beam.actual_focus_m() / (w0 * math.sqrt(1.0 + (z0 / zR) ** 2)) - 1.0)
    assert rel > 1e-2, "a bore of one input radius should visibly widen the focus past the unclipped reading"


# ---------------------------------------------------------------------------------------------
# (b) the on-axis focal factor per recorded watt against lineshape.aperture_onaxis_factor_actual
# ---------------------------------------------------------------------------------------------

def test_onaxis_factor_matches_the_packages_own_closed_form():
    """At the input radius F280's own map reads 42.42 um from (2.46 mm), `onaxis_per_watt()`
    divided by a Gaussian's 2/(pi w^2) at the SAME reading reproduces
    `lineshape.aperture_onaxis_factor_actual`'s 0.8897 to 0.5 per cent -- the package's closed form
    and this module's Fresnel/Collins quadrature are independent routes to the same number."""
    beam = ClippedBeam(w_in_m=2.46e-3, n_z=31, n_xi=140, n_rho=700, z_span_zr=4.0)   # 21 misses the table's bound
    w_act = beam.actual_focus_m()
    assert w_act == pytest.approx(42.42e-6, rel=2e-3)

    ratio = beam.onaxis_per_watt() / (2.0 / (math.pi * w_act ** 2))
    reference = L.aperture_onaxis_factor_actual(w_act)
    assert reference == pytest.approx(0.8897, rel=2e-3)
    assert ratio == pytest.approx(reference, rel=5e-3)


def test_onaxis_factor_plant_the_free_focus_convention_disagrees():
    """PLANT: comparing against `aperture_onaxis_factor` (the UNCLIPPED-FOCUS convention, F108's
    other column, 0.716 at the free focus of a 42.4 um-reading input) must NOT match -- otherwise
    the test above would pass by coincidence rather than by reading the actual-focus convention."""
    beam = ClippedBeam(w_in_m=2.46e-3, n_z=31, n_xi=140, n_rho=700, z_span_zr=4.0)   # 21 misses the table's bound
    w_act = beam.actual_focus_m()
    ratio = beam.onaxis_per_watt() / (2.0 / (math.pi * w_act ** 2))
    wrong_reference = L.aperture_onaxis_factor(w_act)  # the free-focus convention, F108's OTHER number
    assert abs(ratio / wrong_reference - 1.0) > 0.1


# ---------------------------------------------------------------------------------------------
# (c) the floor: the actual focus tends to the Airy asymptote as the input radius grows
# ---------------------------------------------------------------------------------------------

def test_actual_focus_tends_to_the_uniform_illumination_floor():
    """The EXACT w_in -> infinity limit (uniform illumination over the bore, `w_in_m=inf`, no
    Gaussian apodisation at all -- a separate code path in `_mode_input_amplitude`, not a large
    but finite w_in) gives the geometric floor this bore, lens and wavelength can make. Swept finite
    inputs converge to it MONOTONICALLY from above, matching F280/F291's ~40.85-40.89 um reading."""
    floor_beam = ClippedBeam(w_in_m=math.inf, n_z=11, n_xi=300, n_rho=1200, z_span_zr=2.0, interp_tol=8e-3)
    floor = floor_beam.actual_focus_m()
    assert floor == pytest.approx(40.85e-6, rel=1e-2)

    readings = []
    for w_in in (2.0e-3, 8.0e-3, 20.0e-3, 40.0e-3):
        beam = ClippedBeam(w_in_m=w_in, n_z=11, n_xi=300, n_rho=1200, z_span_zr=2.0, interp_tol=8e-3)
        readings.append(beam.actual_focus_m())
    # monotonically decreasing toward the floor, and every one of them above it
    assert all(a > b for a, b in zip(readings, readings[1:])), readings
    assert all(r > floor for r in readings), readings
    assert readings[-1] == pytest.approx(floor, rel=5e-3)


def test_floor_plant_a_much_wider_bore_lowers_it():
    """PLANT: a wider bore must permit a tighter focus (a genuinely different floor) -- otherwise
    'the floor' above could be an artefact fixed by some other constant in the module rather than a
    real function of the aperture."""
    a_wide = 2.0 * K.EOM_APERTURE_RADIUS_M
    floor_default = ClippedBeam(w_in_m=math.inf, n_z=11, n_xi=300, n_rho=1200, z_span_zr=2.0,
                                interp_tol=8e-3).actual_focus_m()
    floor_wide = ClippedBeam(w_in_m=math.inf, a_m=a_wide, n_z=11, n_xi=300, n_rho=1200, z_span_zr=2.0,
                             interp_tol=8e-3).actual_focus_m()
    assert floor_wide < 0.6 * floor_default


# ---------------------------------------------------------------------------------------------
# (d) the axial depth from the thesis side -- slow (a fine axial grid over several mm)
# ---------------------------------------------------------------------------------------------

@pytest.mark.slow
def test_axial_half_intensity_depth_reproduces_the_reviewer_reading():
    """`axial_half_intensity_depth_m` is the ONE-SIDED depth (module docstring: the thesis side's own
    Gaussian reference number, 5.69 mm at the 42.4 um reading, is one Rayleigh range, not the full
    2 zR width). The Gaussian side is checked tightly (it is this module's own closed-form regime,
    already covered by test (a)'s machinery); the CLIPPED side is read out and compared to the
    thesis side's ~8.84 mm with a tolerance wide enough to admit a genuine small disagreement, which is
    reported rather than hidden (`private/cache/plan_2026-09-18/beam_field_report.md`)."""
    beam = ClippedBeam(w_in_m=2.46e-3, n_z=81, n_xi=140, n_rho=900, z_span_zr=3.0, interp_tol=8e-3)
    depth_clipped = axial_half_intensity_depth_m(beam, n_scan=800)

    w_act = beam.actual_focus_m()
    w_in_matched = LAM * F / (math.pi * w_act)  # the unclipped input giving this same reading
    beam_gauss = ClippedBeam(w_in_m=w_in_matched, a_m=20e-3, n_z=81, n_xi=140, n_rho=900,
                             z_span_zr=3.0, interp_tol=8e-3)
    depth_gauss = axial_half_intensity_depth_m(beam_gauss, n_scan=800)

    assert depth_gauss == pytest.approx(5.69e-3, rel=5e-3)
    assert depth_gauss == pytest.approx(math.pi * w_act ** 2 / LAM, rel=5e-3)  # = zR at that reading, closed form

    assert depth_clipped == pytest.approx(8.84e-3, rel=3e-2), (
        f"this module's converged reading is {depth_clipped * 1e3:.4f} mm against the thesis side's "
        f"~8.84 mm (private/cache/plan_2026-09-16/FINDINGS_NIGHT.md F281); see the report for the "
        f"reading, not a hidden pass/fail")


@pytest.mark.slow
def test_axial_depth_plant_a_much_wider_bore_recovers_the_gaussian_answer():
    """PLANT: with the bore opened far past where it clips (as in test (a)), the clipped-geometry
    call must reproduce the SAME Gaussian depth as the matched-input Gaussian reference above --
    otherwise `axial_half_intensity_depth_m` could be reading some property of the tabulation grid
    rather than of the beam."""
    w_in = 2.0e-3
    a_wide = 20e-3
    beam_open = ClippedBeam(w_in_m=w_in, a_m=a_wide, n_z=81, n_xi=140, n_rho=900, z_span_zr=3.0,
                            interp_tol=8e-3)
    depth_open = axial_half_intensity_depth_m(beam_open, n_scan=800)
    w0, zR, z0 = _focused_gaussian_reference(w_in)
    assert depth_open == pytest.approx(zR, rel=5e-3)


# ---------------------------------------------------------------------------------------------
# (e) M2 > 1 without the bore: the second-moment radius follows the standard embedded-Gaussian law
# ---------------------------------------------------------------------------------------------

def test_m2_mixture_second_moment_follows_the_standard_law():
    """Without clipping, `second_moment_radius_m(z)` for an m2 = 1.4 mixture follows
    w0 sqrt(1 + (z' M2 lambda / (pi w0^2))^2) with z' measured from the TRUE (shifted) waist and w0
    the FOCUSED fundamental's own waist times sqrt(M2) (module docstring's algebra, checked
    end-to-end against an independent LG(p,0) quadrature earlier in this module's development and
    reproduced here through the public API alone)."""
    w_in = 2.0e-3
    a_m = 20e-3
    m2 = 1.4
    beam = ClippedBeam(w_in_m=w_in, a_m=a_m, m2=m2, n_z=31, n_xi=200, n_rho=500, z_span_zr=2.0)

    w0_fund, zR_fund, z0 = _focused_gaussian_reference(w_in)
    w0_mix = w0_fund * math.sqrt(m2)

    assert beam.second_moment_radius_m(z0) == pytest.approx(w0_mix, rel=1e-3)
    for mult in (-2.0, -1.0, -0.5, 0.5, 1.0, 2.0):
        z = z0 + mult * zR_fund
        got = beam.second_moment_radius_m(z)
        exp = w0_mix * math.sqrt(1.0 + ((z - z0) * m2 * LAM / (math.pi * w0_mix ** 2)) ** 2)
        assert got == pytest.approx(exp, rel=1e-3), f"second_moment_radius_m at z={z:.4e}"


def test_m2_one_reduces_to_the_plain_gaussian():
    """m2 = 1.0 (the default) is the pure fundamental mode: `mode_weights_for_m2` returns the
    single (0, 1.0) mode, and `second_moment_radius_m` then agrees with `w()` (the 1/e^2 radius) at
    the waist, because <r^2> = w^2/2 for a Gaussian I proportional to exp(-2 r^2/w^2) makes the two
    conventions coincide there (module docstring: 'calibrated so a pure Gaussian ... returns the
    SAME number as w(z)')."""
    assert mode_weights_for_m2(1.0) == ((0, 1.0),)
    beam = ClippedBeam(w_in_m=2.0e-3, a_m=20e-3, m2=1.0, n_z=21, n_xi=140, n_rho=500, z_span_zr=2.0)
    assert beam.second_moment_radius_m(0.0) == pytest.approx(beam.w(0.0), rel=1e-3)


def test_m2_mixture_weights_hit_the_requested_m2_exactly():
    """PLANT / direct check of `mode_weights_for_m2`: the power-weighted sum of (2p+1) over the
    returned modes equals the requested M2 for a spread of targets, including one exactly on a mode
    boundary (m2 = 3.0, where p1 = 1 and c = 1 -- the pure p=1 mode, no p=0 admixture at all)."""
    for target in (1.0, 1.2, 1.4, 2.0, 3.0, 4.7):
        modes = mode_weights_for_m2(target)
        total_weight = sum(w for _, w in modes)
        total_m2 = sum(w * (2 * p + 1) for p, w in modes)
        assert total_weight == pytest.approx(1.0, abs=1e-9)
        assert total_m2 == pytest.approx(target, abs=1e-9)
    with pytest.raises(ValueError):
        mode_weights_for_m2(0.5)  # M2 below 1 is not a physical beam-quality factor


def test_the_clipped_focus_reproduces_urey_2004_table_2_at_the_benchs_truncation_ratio():
    """A132.5: Urey 2004's Table 2 (`docs/lit/urey2004.md`; valid for a Fresnel number of at least 5 and f# above 2, where the
    bench has 15.1 and 50) gives, at a truncation ratio w/a = 1.64 with the aperture in the lens's front focal plane (d = f), a
    1/e^2 focal radius of 42.07 um and a Strehl-0.5 depth of 8.81 mm. The bench's 1.5 mm bore and a 2.46 mm input sit at that
    ratio. Measured: 42.43 um and 8.84 mm, within one per cent of both. Planted both ways: with the bore opened to 20 mm the same
    input focuses to the unclipped Gaussian's 19.3 um with a 1.18 mm depth, and neither reading holds."""
    kw = dict(n_z=81, n_xi=140, n_rho=900, z_span_zr=3.0, interp_tol=8e-3)
    beam = ClippedBeam(w_in_m=2.46e-3, d_ap_m=F, **kw)
    assert beam.actual_focus_m() == pytest.approx(42.07e-6, rel=1e-2)
    assert axial_half_intensity_depth_m(beam, n_scan=800) == pytest.approx(8.81e-3, rel=1e-2)
    wide = ClippedBeam(w_in_m=2.46e-3, a_m=20e-3, d_ap_m=F, **kw)
    assert wide.actual_focus_m() == pytest.approx(LAM * F / (math.pi * 2.46e-3), rel=1e-2)
    assert wide.actual_focus_m() != pytest.approx(42.07e-6, rel=0.3)
    assert axial_half_intensity_depth_m(wide, n_scan=800) != pytest.approx(8.81e-3, rel=0.3)

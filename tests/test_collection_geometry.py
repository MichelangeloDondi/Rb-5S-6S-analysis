"""The fluorescence collection window, and the one-sided bias it puts on a
pure-transverse-ramp fit.

These guard three things a reading of the code alone would not catch: that the
window is derived from the apparatus rather than assumed, that an independent
quadrature reproduces the repository's own axial-ramp moments, and above all
that the correction runs in ONE direction. The last is what licenses
results/prediction_band.csv to call the window correction conservative; if the
window could raise the recovered shift, that reasoning would invert and a
tension claim would rest on it.
"""
import math

import numpy as np
import pytest
from scipy.integrate import quad

from rb5s6s import constants as K
from rb5s6s.lineshape import ramp_moment_contributions

# the pure transverse ramp, which the moments helper reaches as z_ratio -> 0
PURE = {"pull": -2.0 / 3.0, "excess_var": 1.0 / 18.0, "kappa3": 1.0 / 135.0}


def _independent_moments(z_ratio: float) -> tuple[float, float, float]:
    """Second implementation, in u = |s|/s0 rather than on a grid in s.

    Substituting t = 2 r^2/w^2 in the transverse measure gives
    2 pi r dr = (pi w^2/2) dt, and with u = a(z) exp(-t) that is dt = -du/u, so
    the two-photon weight u^2 leaves a density proportional to u at fixed z.
    The axial integral then gives f(u) = u * 2 * [Z + Z^3/3] with
    Z = min(z_ratio, sqrt(1/u - 1)), in units of the Rayleigh range. Below
    u_c = 1/(1+z_ratio^2) the window binds and the density is exactly the ramp.
    """
    gate = 2 * (z_ratio + z_ratio ** 3 / 3)
    u_c = 1 / (1 + z_ratio ** 2)
    def integral(h):
        below = gate * quad(lambda u: h(u) * u, 0, u_c, limit=200)[0]
        above = quad(lambda t: h(1 / (1 + t * t)) * 4 * t * t * (1 + t * t / 3)
                     / (1 + t * t) ** 3, 0, z_ratio, limit=200)[0]
        return below + above
    norm = integral(lambda u: 1.0)
    mean = integral(lambda u: u) / norm
    var = integral(lambda u: (u - mean) ** 2) / norm
    mu3 = integral(lambda u: (u - mean) ** 3) / norm
    return -mean, var, -mu3          # s = -s0 u, so the odd moments flip sign


def test_the_window_comes_from_the_apparatus_and_not_from_a_literal():
    """z_ratio is (cathode/2)/M over the Rayleigh range, with M from the lens."""
    z = K.collection_z_ratio()
    magnification = (K.COLLECTION_IMAGE_DIST_M - K.COLLECTION_LENS_F_M) / K.COLLECTION_LENS_F_M
    half = 0.5 * K.PMT_CATHODE_ALONG_BEAM_M / magnification
    rayleigh = math.pi * K.W0_MEASURED_M ** 2 / K.LAMBDA_LASER_M
    assert z == pytest.approx(half / rayleigh, rel=1e-12)
    # a quarter of a Rayleigh range: the thin-slice regime the ramp assumes
    assert 0.1 < z < 0.5, f"z_ratio {z} is outside the regime the record's ramp is quoted in"


def test_no_real_image_raises_instead_of_inverting_the_window():
    """image distance at or inside the focal length gives a negative
    magnification, which would silently flip the window rather than fail."""
    with pytest.raises(ValueError, match="no real image"):
        K.collection_z_ratio(image_dist_m=K.COLLECTION_LENS_F_M * 0.5)
    with pytest.raises(ValueError, match="no real image"):
        K.collection_z_ratio(image_dist_m=K.COLLECTION_LENS_F_M)


@pytest.mark.parametrize("z_ratio", [1e-6, 0.05, 0.2605, 0.5, 1.117])
def test_an_independent_quadrature_reproduces_the_axial_moments(z_ratio):
    """The repository integrates the density on a grid in s; this integrates it
    in u with the window split out analytically. Agreement to six digits is the
    cross-check that neither implementation carries a private convention."""
    got = ramp_moment_contributions(1.0, z_ratio=z_ratio)
    pull, var, kappa3 = _independent_moments(max(z_ratio, 1e-6))
    # 5e-6 is the repository grid's own discretisation at n_grid=200_001, not
    # slack: the two implementations agree to six digits everywhere else.
    assert got["pull"] == pytest.approx(pull, abs=5e-6)
    assert got["excess_var"] == pytest.approx(var, abs=5e-6)
    assert got["kappa3"] == pytest.approx(kappa3, abs=1e-7)


def test_the_zero_window_limit_is_the_pure_transverse_ramp():
    got = ramp_moment_contributions(1.0, z_ratio=1e-6)
    for key, want in PURE.items():
        assert got[key] == pytest.approx(want, rel=2e-5), key


def test_the_window_correction_is_one_sided_only_below_a_stated_window():
    """The third cumulant falls monotonically with the window, so its bias is
    one-sided everywhere. THE VARIANCE IS NOT MONOTONE: it reaches a minimum of
    0.870 of the pure ramp's at z_ratio 0.788 and returns to the pure value at
    1.691, above which the width-channel bias CHANGES SIGN and correcting for
    the window would LOWER a bound instead of raising it.

    results/prediction_band.csv calls its correction conservative, and that
    holds because the bench sits at 0.26. The claim is conditional and the
    condition is guarded here, because an unconditional reading of it was
    written into three surfaces before this test was run."""
    ref = ramp_moment_contributions(1.0, z_ratio=1e-6)
    assert K.collection_z_ratio() < 1.0, "the bench must sit well inside the one-sided region"

    previous = ref["kappa3"]
    for z_ratio in np.linspace(0.01, 3.0, 120):
        got = ramp_moment_contributions(1.0, z_ratio=float(z_ratio))
        assert got["kappa3"] <= previous + 1e-12, f"the third cumulant rose at {z_ratio}"
        previous = got["kappa3"]

    for z_ratio in np.linspace(0.01, 1.60, 40):
        got = ramp_moment_contributions(1.0, z_ratio=float(z_ratio))
        assert got["excess_var"] <= ref["excess_var"] + 1e-12, \
            f"the variance exceeded the pure ramp's at {z_ratio}, below the stated crossing"

    # and the crossing is real, so the bound above is not vacuous
    assert ramp_moment_contributions(1.0, z_ratio=1.8)["excess_var"] > ref["excess_var"]


def test_the_third_cumulant_has_a_null_beyond_the_operating_point():
    """kappa3 vanishes and reverses at a finite window, which is a design limit
    on the collection path rather than a curiosity: past it the asymmetry the
    shift is read from comes back with the wrong sign."""
    assert ramp_moment_contributions(1.0, z_ratio=1.0)["kappa3"] > 0
    assert ramp_moment_contributions(1.0, z_ratio=1.5)["kappa3"] < 0
    assert K.collection_z_ratio() < 1.0, "the bench must sit well clear of the null"

"""The supported entry point, tested as a stranger would meet it.

The package exported eighteen names until 2026-08-26 and every one was a
constant or a forward-model primitive, so a reader holding a frequency axis
and a voltage trace had no supported route into it. These tests fix what
that route promises: it is reachable from the top-level package, it recovers
a width it was not told, it says which axis it is on, and it refuses input
it cannot fit instead of returning a number.
"""
from __future__ import annotations

import numpy as np
import pytest

import rb5s6s
from rb5s6s.lineshape import model_profile, total_fwhm_mhz


def _synthetic(fwhm_mhz: float, n: int = 1, noise: float = 0.004, seed: int = 3):
    """A line built from the package's own model, so the truth is exact."""
    nu = np.linspace(-40.0, 40.0, 700)
    shape = model_profile(nu, gamma_coll=fwhm_mhz, sigma_laser_fwhm=0.5,
                          transit_fwhm=0.9334247073098216)
    shape = 0.6 * shape / shape.max()
    rng = np.random.default_rng(seed)
    traces = [shape + rng.normal(0.0, noise, nu.size) for _ in range(n)]
    truth = total_fwhm_mhz(nu, gamma_coll=fwhm_mhz, sigma_laser_fwhm=0.5,
                           transit_fwhm=0.9334247073098216)
    return nu, traces, truth


def test_the_entry_point_is_reachable_from_the_package_root():
    """The whole defect in one assertion: it must not need the layout."""
    assert "fit_linewidth" in rb5s6s.__all__
    assert callable(rb5s6s.fit_linewidth)
    # and the analysis modules under it, which were present and unreachable
    for name in ("linefit", "ingest", "fit_condition", "total_fwhm_mhz"):
        assert name in rb5s6s.__all__, name
        assert hasattr(rb5s6s, name), name


def test_the_campaign_conventions_stay_unexported():
    """Exporting a name promises it can be used correctly on other data.

    `ruler`, `trim`, `qc` and `global_fit` carry this apparatus's own
    conventions, so surfacing them would invite a stranger to apply a
    calibration that does not describe their instrument.
    """
    for name in ("ruler", "trim", "qc", "global_fit"):
        assert name not in rb5s6s.__all__, name


@pytest.mark.parametrize("truth_gamma", [4.0, 8.0, 14.0])
def test_it_recovers_a_width_it_was_not_told(truth_gamma):
    nu, traces, truth = _synthetic(truth_gamma, n=4)
    r = rb5s6s.fit_linewidth([nu] * 4, traces, T_C=110.0)
    assert abs(r.fwhm_mhz - truth) < 0.05 * truth, (r.fwhm_mhz, truth)
    assert np.isfinite(r.fwhm_err_mhz) and r.fwhm_err_mhz > 0
    assert r.n_traces == 4


def test_a_single_trace_and_a_list_of_one_agree():
    """The convenience shape must not be a different computation."""
    nu, traces, _ = _synthetic(8.0, n=1)
    bare = rb5s6s.fit_linewidth(nu, traces[0], T_C=110.0)
    listed = rb5s6s.fit_linewidth([nu], traces, T_C=110.0)
    assert bare.fwhm_mhz == pytest.approx(listed.fwhm_mhz, rel=1e-12)


def test_more_repeats_do_not_widen_the_error():
    """Averaging must help, or the error is not an error."""
    nu, traces, _ = _synthetic(8.0, n=6)
    one = rb5s6s.fit_linewidth([nu], traces[:1], T_C=110.0)
    six = rb5s6s.fit_linewidth([nu] * 6, traces, T_C=110.0)
    assert six.fwhm_err_mhz < one.fwhm_err_mhz


def test_the_axis_is_named_where_a_reader_will_look():
    """Every width here is ambiguous by a factor of two between axes."""
    nu, traces, _ = _synthetic(8.0, n=1)
    r = rb5s6s.fit_linewidth(nu, traces[0], T_C=110.0)
    assert "transition axis" in repr(r)
    assert "TRANSITION axis" in rb5s6s.api.__doc__
    assert all(k.endswith("_mhz") for k in r.components), r.components


def test_the_components_sum_to_something_that_makes_the_width():
    """The result must expose what the number is made of, not just the number."""
    nu, traces, _ = _synthetic(8.0, n=3)
    r = rb5s6s.fit_linewidth([nu] * 3, traces, T_C=110.0)
    c = r.components
    rebuilt = total_fwhm_mhz(np.arange(-120.0, 120.0, 0.002),
                             gamma_coll=c["gamma_coll_mhz"],
                             sigma_laser_fwhm=c["sigma_laser_fwhm_mhz"],
                             transit_fwhm=c["transit_fwhm_mhz"],
                             s0=c["s0_mhz"])
    assert rebuilt == pytest.approx(r.fwhm_mhz, rel=1e-3)


@pytest.mark.parametrize("bad", ["mismatched_lengths", "ragged", "too_few"])
def test_it_refuses_input_it_cannot_fit(bad):
    """A wrong shape must raise, never return a plausible number."""
    nu = np.linspace(-30, 30, 200)
    v = np.zeros_like(nu)
    with pytest.raises(ValueError):
        if bad == "mismatched_lengths":
            rb5s6s.fit_linewidth([nu, nu], [v], T_C=110.0)
        elif bad == "ragged":
            rb5s6s.fit_linewidth([nu], [v[:100]], T_C=110.0)
        else:
            rb5s6s.fit_linewidth(nu[:4], v[:4], T_C=110.0)


def test_the_public_width_and_the_internal_shim_are_one_definition():
    """Two definitions of a headline quantity is how a wrong factor survives."""
    from rb5s6s import stark
    nu = np.arange(-40, 40, 0.01)
    assert stark._fwhm_of(0.6, 1.2, 0.93, 0.3, nu) == total_fwhm_mhz(
        nu, gamma_coll=0.6, sigma_laser_fwhm=1.2, transit_fwhm=0.93, s0=0.3)

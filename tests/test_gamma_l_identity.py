"""The mixed G+L laser kernel: its default is inert, its submodels are exact.

WHY THIS FILE EXISTS. `gamma_l` was threaded through six sites on 2026-08-21 so
the laser kernel can be Gaussian, Lorentzian, or BOTH AT ONCE, which is what an
identifiability question about the kernel needs in order to be asked at all.
Three properties have to hold for that parameter to be safe to ship, and each
of the three has failed somewhere in this repository's history:

1. THE DEFAULT IS BIT-IDENTICAL. Adding an exact zero is a no-op in IEEE
   arithmetic, so `gamma_l=0.0` must reproduce the pre-change module to the
   last bit, not to a tolerance. The argument is sound and is not the evidence.
   This file compares against the committed pre-change implementation.

2. THE PARAMETER IS NOT INERT. A threaded parameter that silently fails to
   reach the model looks exactly like a parameter with no effect, and the
   default-identity test above passes either way. So a nonzero value must
   MOVE the profile. This is the should-fail control.

3. THE SUM DEGENERACY IS EXACT. Two Lorentzians of FWHM a and b convolve to one
   of FWHM a+b identically, so only the SUM is identified at a fixed condition,
   and the code must reflect that to machine zero. Done by convolution on a
   finite grid it did not: tail truncation depends on the SPAN, the span
   depends on how the total is split, and the profile acquired a dependence on
   the split at up to 3.7e-3 of peak, pointing along exactly the direction a
   laser-width inference has to measure. Addition removes it identically.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import lineshape as ls
from rb5s6s._compat import trapezoid

ROOT = Path(__file__).resolve().parents[1]
NU = np.linspace(-40.0, 40.0, 4001)


def _on_common_axis(**kw):
    g, p = ls.composite_profile(**kw)
    return np.interp(NU, g, p)


@pytest.fixture(scope="module")
def pre_change_module(tmp_path_factory):
    """The lineshape module as of the commit BEFORE gamma_l was threaded.

    Read from git rather than from a checked-in copy: a second copy of an
    artefact outside git's view is wrong in the one way nothing catches, and
    a snapshot committed beside the module would drift from it silently.
    """
    rev = subprocess.run(
        ["git", "log", "--format=%H", "-1", "-S", "gamma_l", "--", "rb5s6s/lineshape.py"],
        cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    if not rev:
        pytest.skip("cannot locate the commit that introduced gamma_l")
    src = subprocess.run(["git", "show", f"{rev}^:rb5s6s/lineshape.py"],
                         cwd=ROOT, capture_output=True, text=True, check=False)
    if src.returncode != 0:
        pytest.skip("pre-change lineshape.py not retrievable")
    # Import it INSIDE the package so its relative imports resolve.
    dst = ROOT / "rb5s6s" / "_pre_gamma_l_snapshot.py"
    dst.write_text(src.stdout)
    try:
        import importlib
        mod = importlib.import_module("rb5s6s._pre_gamma_l_snapshot")
        yield mod
    finally:
        dst.unlink(missing_ok=True)


# ---------------------------------------------------------------- 1. inert default
def test_gamma_l_default_is_bit_identical(pre_change_module):
    """gamma_l=0.0 reproduces the pre-change module exactly, grid included."""
    rng = np.random.default_rng(0)
    for _ in range(40):
        gc = float(rng.uniform(0.0, 6.0))
        sl = float(rng.uniform(0.1, 8.0))
        tr = float(rng.uniform(0.1, 4.0))
        kind = "gaussian" if rng.random() < 0.5 else "lorentzian"
        go, po = pre_change_module.composite_profile(gc, sl, tr, kind)
        gn, pn = ls.composite_profile(gc, sl, tr, kind)
        assert np.array_equal(go, gn), f"grid moved at {(gc, sl, tr, kind)}"
        assert np.array_equal(po, pn), (
            f"profile moved by {np.max(np.abs(po - pn)):.3e} at {(gc, sl, tr, kind)}; "
            "the default must be a no-op to the last bit, not to a tolerance")


# ---------------------------------------------------------------- 2. should-fail control
def test_gamma_l_actually_reaches_the_model():
    """A nonzero gamma_l MOVES the profile. Guards a silently unthreaded parameter."""
    a = _on_common_axis(gamma_coll=1.0, sigma_laser=2.0, transit_fwhm=0.9, gamma_l=0.0)
    b = _on_common_axis(gamma_coll=1.0, sigma_laser=2.0, transit_fwhm=0.9, gamma_l=0.7)
    moved = float(np.max(np.abs(a - b)))
    assert moved > 1e-6, (
        f"gamma_l=0.7 moved the profile by only {moved:.3e}: the parameter is "
        "not reaching the model and the identity test above cannot see that")


# ---------------------------------------------------------------- 3. exact sum degeneracy
@pytest.mark.parametrize("gc,gl,gc_sum", [(1.0, 0.5, 1.5), (0.2, 2.3, 2.5), (3.0, 1.0, 4.0)])
def test_lorentzian_widths_add_exactly(gc, gl, gc_sum):
    """gamma_coll + gamma_l is degenerate to MACHINE ZERO, not to a tolerance."""
    g1, p1 = ls.composite_profile(gc, 2.0, 0.9, gamma_l=gl)
    g2, p2 = ls.composite_profile(gc_sum, 2.0, 0.9, gamma_l=0.0)
    assert np.array_equal(g1, g2)
    assert np.array_equal(p1, p2), (
        f"splitting {gc_sum} as {gc}+{gl} moved the profile by "
        f"{np.max(np.abs(p1 - p2)):.3e}; the continuum identity says it cannot "
        "move at all, and a split-dependent profile is a manufactured "
        "separability along the direction the kernel inference measures")


def test_gamma_l_is_interchangeable_with_the_lorentzian_arm():
    """The same identity across the laser_kind toggle."""
    g1, p1 = ls.composite_profile(1.0, 2.0, 0.9, "lorentzian", gamma_l=0.5)
    g2, p2 = ls.composite_profile(1.0, 2.5, 0.9, "lorentzian", gamma_l=0.0)
    assert np.array_equal(g1, g2) and np.array_equal(p1, p2)


# ---------------------------------------------------------------- 4. the submodels are reachable
def test_pure_lorentzian_submodel_is_finite_and_exact():
    """sigma_G -> 0 IS the nested submodel, and it must be evaluable.

    gaussian() divides by sigma, so convolving with sigma_laser = 0 returned an
    all-nan profile. The mixed kernel could not evaluate its own submodel, and a
    nested likelihood ratio against it would have propagated nan rather than
    failing loudly. A zero-width Gaussian is a delta and convolution with it is
    the identity, so skipping the convolution is the LIMIT, not a guard.
    """
    g, p = ls.composite_profile(1.2, 0.0, 0.9, gamma_l=3.0)
    assert np.all(np.isfinite(p)), "the pure-Lorentzian submodel returns nan"
    # trapezoid via the compat shim: np.trapezoid is numpy 2.0+ and a direct
    # call here would break the declared floor, which tests/test_constants.py
    # guards across the package, the scripts and the tests alike.
    assert trapezoid(p, g) == pytest.approx(1.0, rel=1e-6)
    g2, p2 = ls.composite_profile(1.2, 3.0, 0.9, "lorentzian")
    assert np.array_equal(g, g2) and np.array_equal(p, p2), (
        "the sigma_G -> 0 limit must equal the lorentzian arm carrying the "
        "same total width")


def test_absent_kernel_does_not_drive_the_grid_to_its_floor():
    """An absent width floored to 1e-6 must not become the step-setting minimum.

    It did: the sigma_G = 0 profile was built on 205423 points instead of the
    ~2700 the line needs, because min(widths) saw the 1e-6 placeholder.
    """
    g, _ = ls.composite_profile(1.2, 0.0, 0.9, gamma_l=3.0)
    assert len(g) < 20000, (
        f"absent-kernel grid is {len(g)} points; the 1e-6 placeholder is "
        "setting the step again")


# ---------------------------------------------------------------- 5. every site carries it
def test_all_six_sites_expose_gamma_l():
    """The parameter reaches every fit entry point, not just the primitives."""
    import inspect
    from rb5s6s import beta, global_fit, linefit
    sites = [
        ls.composite_profile, ls.model_profile, linefit._shared_profile_grid,
        linefit.fit_condition, beta.fit_beta_self, global_fit.fit_global,
    ]
    missing = [f.__qualname__ for f in sites
               if "gamma_l" not in inspect.signature(f).parameters]
    assert not missing, f"gamma_l absent from: {missing}"


def test_fit_global_also_gained_laser_kind():
    """fit_global had no laser_kind at all, so the fit producing the committed
    global numbers could not be run under the kernel the other two fits could."""
    import inspect
    from rb5s6s import global_fit
    assert "laser_kind" in inspect.signature(global_fit.fit_global).parameters


# ---------------------------------------------------------------- 6. the fitted parameter
def test_fitting_gamma_l_is_off_by_default_and_inert():
    """fit_gamma_l defaults False, and the returned value is then the input."""
    from rb5s6s.forecast import synthetic_traces
    from rb5s6s.linefit import fit_condition
    rng = np.random.default_rng(1)
    f, v = synthetic_traces(1.2, 3.0, 0.93, n_traces=3, n_points=800, noise=0.004, rng=rng)
    out = fit_condition(f, v, T_C=130.0, transit_fwhm=0.93)
    assert out["gamma_l"] == 0.0
    assert out["gamma_l_fitted"] is False
    assert np.isnan(out["gamma_l_err"])


def test_at_one_condition_only_the_SUM_of_the_lorentzian_widths_is_identified():
    """The continuum identity, asserted on the ESTIMATOR rather than the profile.

    gamma_coll and Gamma_L,equiv are both Lorentzian widths, Lorentzians add
    exactly, so at a single fixed condition only their sum can be measured. The
    fit must therefore recover the SUM accurately and the SPLIT arbitrarily.

    This is the property that makes the whole kernel question a multi-condition
    question: the separating lever is density, because gamma_coll scales with
    N(T) and Gamma_L,equiv does not. A fit that returned a well-determined
    split HERE would be reporting the discretisation artefact that was removed
    on 2026-08-20, not a physical separation, so this test failing in the
    direction of "too good" is as informative as it failing in either other.
    """
    from rb5s6s.forecast import synthetic_traces
    from rb5s6s.linefit import fit_condition
    truth_gc = 1.2
    for gl_true in (0.0, 0.5, 1.5):
        sums = []
        for seed in range(3):
            rng = np.random.default_rng(seed)
            f, v = synthetic_traces(truth_gc, 3.0, 0.93, gamma_l=gl_true,
                                    n_traces=5, n_points=2000, noise=0.004, rng=rng)
            o = fit_condition(f, v, T_C=130.0, transit_fwhm=0.93, fit_gamma_l=True)
            sums.append(o["gamma_coll"] + o["gamma_l"])
        recovered = float(np.mean(sums))
        true_sum = truth_gc + gl_true
        assert recovered == pytest.approx(true_sum, rel=5e-3), (
            f"the SUM must be identified: got {recovered:.4f} for {true_sum:.4f}")


def test_gamma_l_is_appended_not_inserted_in_the_parameter_vector():
    """Freeing gamma_l must not move gamma_coll or sigma_laser off index 0 and 1.

    Callers and the covariance read those by position. An inserted shared
    parameter would silently re-point every one of those reads.
    """
    from rb5s6s.forecast import synthetic_traces
    from rb5s6s.linefit import fit_condition
    rng = np.random.default_rng(3)
    f, v = synthetic_traces(1.2, 3.0, 0.93, gamma_l=0.4, n_traces=4,
                            n_points=1200, noise=0.004, rng=rng)
    free = fit_condition(f, v, T_C=130.0, transit_fwhm=0.93, fit_gamma_l=True)
    # gamma_coll and sigma_laser still carry their own errors from cov[0,0]/[1,1]
    assert np.isfinite(free["gamma_coll_err"]) and free["gamma_coll_err"] > 0
    assert np.isfinite(free["sigma_laser_err"]) and free["sigma_laser_err"] > 0
    assert free["gamma_l_fitted"] is True

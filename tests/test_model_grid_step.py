"""The model's grid step is a public function since 2026-09-04, so a producer
that must know how many cells its ramp spans asks the model; nothing tested
it directly until a seat found the two keywords behind seven committed rows
called from producers alone. The rule, from its docstring: the narrowest
smooth kernel over the steps per kernel, the shift joining the candidates
only under resolve_shift, floored at the module floor."""
import numpy as np

from rb5s6s import lineshape as L


KW = dict(gamma_coll=0.5, sigma_laser_fwhm=2.0, transit_fwhm=1.0, gamma_nat_mhz=3.49)


def test_the_step_is_the_narrowest_kernel_over_the_module_steps():
    dnu = L.model_grid_step_mhz(s0=0.0, **KW)
    assert abs(dnu - 1.0 / L.GRID_STEPS_PER_KERNEL) < 1e-12, dnu


def test_the_shift_joins_the_candidates_only_under_resolve_shift():
    off = L.model_grid_step_mhz(s0=0.3, **KW)
    on = L.model_grid_step_mhz(s0=0.3, resolve_shift=True, **KW)
    assert abs(off - 1.0 / L.GRID_STEPS_PER_KERNEL) < 1e-12, "a shift below the narrowest kernel leaves the grid alone unless asked"
    assert abs(on - 0.3 / L.GRID_STEPS_PER_KERNEL) < 1e-12, "with resolve_shift the shift sets the step"
    wide = L.model_grid_step_mhz(s0=3.0, resolve_shift=True, **KW)
    assert abs(wide - 1.0 / L.GRID_STEPS_PER_KERNEL) < 1e-12, "a shift wider than the narrowest kernel does not"


def test_grid_steps_per_kernel_overrides_the_module_constant_and_the_floor_holds():
    fine = L.model_grid_step_mhz(s0=0.0, grid_steps_per_kernel=96, **KW)
    assert abs(fine - 1.0 / 96) < 1e-12
    floored = L.model_grid_step_mhz(gamma_coll=0.0, sigma_laser_fwhm=1e-9, transit_fwhm=1e-9, gamma_nat_mhz=1e-9, s0=0.0)
    assert floored >= L.GRID_STEP_FLOOR_MHZ
    # the boundary the 1e-9 widths step around: every width zero. The docstring
    # promises the floor unconditionally and the function used to raise here.
    assert L.model_grid_step_mhz(gamma_coll=0.0, sigma_laser_fwhm=0.0, transit_fwhm=0.0,
                                 gamma_nat_mhz=0.0, s0=0.0) == L.GRID_STEP_FLOOR_MHZ


def test_resolving_the_shift_keeps_the_profile_area_and_its_ramp_on_at_least_the_steps():
    nu = np.linspace(-30.0, 30.0, 30001)
    off = L.model_profile(nu, gamma_coll=0.5, sigma_laser_fwhm=2.0, transit_fwhm=1.0, s0=0.3)
    on = L.model_profile(nu, gamma_coll=0.5, sigma_laser_fwhm=2.0, transit_fwhm=1.0, s0=0.3, resolve_shift=True)
    # the areas are both normalised to one by construction, so an area test
    # cannot fail: the pointwise difference is what carries the claim (planted
    # 2026-09-04, an injected five-fold shift moves it a fifth of the peak and
    # fails here, where the true difference is about one part in ten thousand)
    peak = float(np.max(off))
    assert float(np.max(np.abs(on - off))) < 1e-3 * peak, "resolving the shift is a grid choice, not a physics change"
    cells = 0.3 / L.model_grid_step_mhz(gamma_coll=0.5, sigma_laser_fwhm=2.0, transit_fwhm=1.0, gamma_nat_mhz=3.49, s0=0.3, resolve_shift=True)
    assert cells >= L.GRID_STEPS_PER_KERNEL - 1e-9, "the ramp spans at least the steps per kernel once resolved"

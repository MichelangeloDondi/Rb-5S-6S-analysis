"""`full_profile`'s `volume_table` branch (C6b design item 1): wiring in the non-convolving joint
line, and the byte-identity of everything else.

Two things are checked in both directions, the record's own discipline for a switch that is
thrown (`tests/test_fullmodel.py`'s own module docstring): the default path (`volume_table=None`)
must not move a single bit, and the table path must actually reach `JointTable.profile` with the
same homogeneous and laser widths a direct call would compute, never approximate them or silently
drop a term.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K
from rb5s6s.fullmodel import doppler_pedestal_fwhm_mhz, full_profile, saturation_companion_mhz
from rb5s6s.lineshape import _kernel_widths
from rb5s6s.volume_line import JointTable

# =============================================================================================
# (a) the default path is byte-identical to what full_profile returned before this change
# =============================================================================================

#: The grid and the five parameter sets the reference array was made with. IDENTICAL, dict for
#: dict, to the one-off generator (not part of this repository) that produced
#: tests/data/full_profile_reference_c6b.npz: run once, against the UNMODIFIED full_profile (the
#: commit before the volume_table branch was added), as
#:
#:     NU = np.linspace(-40.0, 40.0, 4001)
#:     for i, kw in enumerate(CASES):
#:         out[f"case{i}"] = full_profile(NU, **kw)
#:     np.savez("tests/data/full_profile_reference_c6b.npz", nu=NU, **out)
#:
#: The five sets were chosen to cover, between them, every axis the branch below could have
#: disturbed: a varying gamma_coll/sigma_laser_fwhm/transit_fwhm, s0 = 0 (case 1), the mixed G+L
#: laser kernel (gamma_l > 0, cases 0/3/4) alongside a pure Lorentzian laser_kind (cases 1/1's
#: gamma_l), a saturation companion with a named peak (omega_mhz > 0, peak "4192"/"4121", cases 2
#: and 4), a pedestal (cases 2 and 4), a retro tilt (case 3), and one m2 != 1 call with w0_m (case
#: 4). If this file's CASES ever drifts from the generator's own, this test still passes or fails
#: honestly, it would just stop meaning what this docstring says it means, so a change to CASES
#: must regenerate the .npz the same way.
NU = np.linspace(-40.0, 40.0, 4001)
CASES = [
    dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575, s0=0.45,
         gamma_l=0.40, laser_kind="gaussian"),
    dict(gamma_coll=0.30, sigma_laser_fwhm=2.2, transit_fwhm=1.20, s0=0.0,
         gamma_l=0.15, laser_kind="lorentzian"),
    dict(gamma_coll=0.45, sigma_laser_fwhm=1.1, transit_fwhm=0.80, s0=0.60,
         gamma_l=0.0, laser_kind="gaussian", omega_mhz=0.5, peak="4192",
         pedestal_height_frac=3e-3),
    dict(gamma_coll=0.60, sigma_laser_fwhm=1.8, transit_fwhm=1.00, s0=0.35,
         gamma_l=0.25, laser_kind="gaussian", retro_tilt_rad=2.36e-3,
         T_C=110.0),
    dict(gamma_coll=0.50, sigma_laser_fwhm=1.5, transit_fwhm=0.95, s0=0.55,
         gamma_l=0.10, laser_kind="gaussian", omega_mhz=0.3, peak="4121",
         pedestal_height_frac=2e-3, m2=2.0, w0_m=K.W0_CENTRAL_M),
]

_REF = np.load(Path(__file__).parent / "data" / "full_profile_reference_c6b.npz")


def test_the_default_path_reproduces_the_precomputed_reference_bit_for_bit():
    """`volume_table=None` (its default) must return exactly what the unmodified `full_profile`
    returned, on every one of the five parameter sets above. `np.array_equal`, not `np.allclose`:
    the rule for this branch is that the default path does not move a single bit."""
    assert np.array_equal(_REF["nu"], NU)
    for i, kw in enumerate(CASES):
        y = full_profile(NU, **kw)
        assert np.array_equal(y, _REF[f"case{i}"]), i


# =============================================================================================
# (b) the volume_table branch equals what a direct table.profile call, wired by hand, gives
# =============================================================================================

@pytest.fixture(scope="module")
def small_table():
    """A small, fast JointTable (about a second to build): reused across the structural tests
    below, same recipe as `tests/test_volume_line.py`'s own `small_table` fixture."""
    S0_grid = np.linspace(0.3, 1.0, 5)
    w0_grid = np.linspace(41e-6, 44e-6, 5)
    delta_mhz = np.linspace(-20.0, 20.0, 301)
    return JointTable.build(S0_grid=S0_grid, w0_grid=w0_grid, delta_mhz=delta_mhz,
                            m2=1.0, T_C=130.0, n_path=300, seed=0, z_ratio=0.6)


#: A grid inside the table's own delta_mhz span, so no evaluation depends on the table's
#: zero-outside-the-span edge behaviour.
NU_SMALL = np.linspace(-15.0, 15.0, 601)

BASE_KW = dict(gamma_coll=0.5, sigma_laser_fwhm=1.2, gamma_l=0.2, s0=0.6,
              w0_m=42.5e-6, m2=1.0, T_C=130.0, laser_kind="gaussian",
              omega_mhz=0.0, peak=None, pump_scale=1.0, pedestal_height_frac=0.0, transit_fwhm=None)


def _expected_via_direct_table_call(table, kw):
    """The construction `full_profile(volume_table=table, **kw)` is supposed to reach: the same
    homogeneous width and laser width `model_profile` would compute (through the shared
    `_kernel_widths`, called here independently of `full_profile`'s own body), fed to
    `table.profile`, with the pedestal added exactly as `full_profile` adds it elsewhere."""
    companion = saturation_companion_mhz(kw["omega_mhz"], kw["peak"], kw["pump_scale"])
    lorentz_laser, homog, _ = _kernel_widths(kw["gamma_coll"] + companion, kw["sigma_laser_fwhm"],
                                             0.0, K.GAMMA_NAT_HZ / 1e6, kw["laser_kind"],
                                             kw["gamma_l"])
    sig_for_table = 0.0 if lorentz_laser else kw["sigma_laser_fwhm"]
    narrow = table.profile(NU_SMALL, s0_mhz=kw["s0"], w0_m=kw["w0_m"],
                           gamma_hom_mhz=homog, sigma_laser_mhz=sig_for_table)
    pedestal_height_frac = kw["pedestal_height_frac"]
    if pedestal_height_frac <= 0.0:
        return narrow
    fwhm = doppler_pedestal_fwhm_mhz(kw["T_C"])
    centre = float(NU_SMALL[int(np.argmax(narrow))])
    ped = np.exp(-4.0 * math.log(2.0) * ((NU_SMALL - centre) / fwhm) ** 2)
    return narrow + pedestal_height_frac * float(np.max(narrow)) * ped


@pytest.mark.parametrize("extra", [
    dict(),                                                    # gaussian laser, no pedestal
    dict(pedestal_height_frac=4e-3),                            # gaussian laser, with pedestal
    dict(omega_mhz=0.5, peak="4192"),                           # saturation companion switched on
    dict(laser_kind="lorentzian"),                              # lorentzian laser, no pedestal
    dict(laser_kind="lorentzian", gamma_l=0.3,
        pedestal_height_frac=2e-3, omega_mhz=0.4, peak="4121"),  # lorentzian, pedestal, companion
], ids=["gaussian", "gaussian+pedestal", "gaussian+companion", "lorentzian",
        "lorentzian+pedestal+companion"])
def test_the_volume_table_branch_equals_its_own_construction(small_table, extra):
    kw = {**BASE_KW, **extra}
    y = full_profile(NU_SMALL, volume_table=small_table, **kw)
    expected = _expected_via_direct_table_call(small_table, kw)
    rel = float(np.max(np.abs(y - expected)) / np.max(np.abs(expected)))
    assert rel < 1e-12, rel


def test_the_volume_table_branch_reaches_zero_shift_without_raising(small_table):
    """s0 = 0 is not special-cased away (unlike model_profile's own delta-spike shortcut): the
    table is looked up at s0 = 0 exactly like any other s0, because the table's coherent line
    already reduces to the shift-free transit line there. This is a smoke test, not a value
    comparison, since s0 = 0 sits below the small_table's own S0_grid (whose low edge is 0.3) and
    so is read off the low-edge cell's own extrapolation."""
    y = full_profile(NU_SMALL, volume_table=small_table, **{**BASE_KW, "s0": 0.0})
    assert np.all(np.isfinite(y))
    assert np.max(y) > 0.0


# =============================================================================================
# (c) every refusal fires
# =============================================================================================

def test_volume_table_needs_w0_m():
    table = object()   # never reached: the refusal fires before the table is used at all
    with pytest.raises(ValueError, match="needs w0_m"):
        full_profile(NU_SMALL, volume_table=table, gamma_coll=0.5, sigma_laser_fwhm=1.2, transit_fwhm=None, s0=0.6)


def test_volume_table_refuses_an_m2_mismatch(small_table):
    with pytest.raises(ValueError, match="one beam quality"):
        full_profile(NU_SMALL, volume_table=small_table, **{**BASE_KW, "m2": 3.0})


def test_volume_table_refuses_a_T_C_mismatch(small_table):
    with pytest.raises(ValueError, match="one temperature"):
        full_profile(NU_SMALL, volume_table=small_table, **{**BASE_KW, "T_C": 90.0})


def test_volume_table_refuses_a_numeric_transit_fwhm(small_table):
    with pytest.raises(ValueError, match="transit_fwhm must be None"):
        full_profile(NU_SMALL, volume_table=small_table, **{**BASE_KW, "transit_fwhm": 0.9})


def test_volume_table_refuses_a_profile_override(small_table):
    """The refusal must fire before `model_kw["profile"]` is ever handed to `table.profile`, whose
    signature has no `profile` argument to receive it."""
    with pytest.raises(ValueError, match="profile must be left out"):
        full_profile(NU_SMALL, volume_table=small_table, profile=lambda g, s: g, **BASE_KW)


def test_volume_table_refuses_an_unmirrorable_laser_kind(small_table):
    """laser_kind is honoured the way model_profile honours it (only 'gaussian' or 'lorentzian');
    a third value is refused here too, with its own message, because the table branch bypasses
    model_profile's own check entirely and so must repeat it rather than silently treat an unknown
    kind as Lorentzian (which is what `lineshape._kernel_widths`'s `!= "gaussian"` test would do if
    left unguarded)."""
    with pytest.raises(ValueError, match="two kinds only"):
        full_profile(NU_SMALL, volume_table=small_table, **{**BASE_KW, "laser_kind": "voigt"})


def test_a_transit_of_none_needs_a_table():
    """transit_fwhm stays a required keyword, so the signature every caller and `fit_full`'s term
    defaults read is unchanged; a table caller passes None, and None without a table is refused
    with its reason instead of a TypeError three calls deep inside model_profile."""
    with pytest.raises(ValueError, match="transit_fwhm is None without a volume_table"):
        full_profile(NU_SMALL, gamma_coll=0.5, sigma_laser_fwhm=1.2, transit_fwhm=None, s0=0.6)

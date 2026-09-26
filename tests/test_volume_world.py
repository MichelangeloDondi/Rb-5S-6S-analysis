"""Guards for the twin's Monte Carlo world (C6b D2 and D3, owner order O46): `Cell.physics`, the
closure's `inject(..., world_source=)` seam, and `VolumeWorld`, the atom Monte Carlo's joint line
injected in place of the fitter's own.

FAILURE MODE IF THIS FILE IS DELETED. The world could stop being the Monte Carlo without anything
noticing: `inject` quietly back on `cell.model` (the fitter judging itself), a world drawn through a
Cell whose saturated ramp or transit depletion it cannot render (the omission read as the fitter's
bias), a clipped beam whose focus is not the Cell's waist (a closure with no single truth), a shift
that does not follow the beam's own on-axis intensity, or a homogeneous width applied per atom again
(F317, whose symptom was a third moment on a symmetric line). Each is planted below.
"""
from __future__ import annotations

import inspect
import math
from pathlib import Path

import numpy as np
import pytest

from conftest import load_script_module        # noqa: E402
from rb5s6s import constants as K
from rb5s6s._compat import trapezoid
from rb5s6s.fullmodel import full_profile, saturation_companion_mhz

ROOT = Path(__file__).resolve().parents[1]
CL = load_script_module("run_ultra_joint_closure", ROOT / "scripts" / "run_ultra_joint_closure.py")
UJ = CL.UJ
W0_UM = round(K.W0_CENTRAL_M * 1e6, 4)


def _trace(P=0.225, T=130.0, peak="4192", iso=85):
    x = np.linspace(-30.0, 30.0, 1201)
    return UJ._finish(dict(T=T, P_W=P, iso=iso, session="P", peak=peak, axis="mhz", x=x, v=np.zeros_like(x),
                           law={"a": 1e-3, "b": 1e-4, "c": 0.0, "tau_int": 1.0}, tau=1.0, file="syn/0",
                           role="p_sweep"))


def _cell(ramp="weak", depletion="none", **extra):
    # the legacy door: these tests are about the world's seam, not the kernel gate's nodes, which
    # tests/test_kernel_gate.py grades through a temporary cache
    return UJ.Cell(UJ._spec("mixed", W0_UM, da=(K.DELTA_ALPHA_AU, 5.9), kernel_gate="legacy", ramp=ramp,
                            depletion=depletion, **extra), [_trace()])


def _truth(cell):
    v = {"omega_scale": 1.0, "gamma_l": 0.4}
    return np.array([v.get(n, 1.6 if n.startswith("sigma_l") else 1.0) for n in cell.names])


def _with_data(cell):
    """Give the one trace a plausible voltage, so the injection's least squares has an amplitude to find."""
    d = cell.unpack(_truth(cell))
    t = cell.traces[0]
    m = cell.model(t["x"], d, cell.per[0], t["peak"], t["session"])
    t["v"] = 2.0 * m / m.max() + 0.01
    return cell


def _moments(x, y):
    y = y / trapezoid(y, x)
    mu = trapezoid(x * y, x)
    c = x - mu
    return mu, trapezoid(c ** 2 * y, x), trapezoid(c ** 3 * y, x)


# ------------------------------------------------------------------ Cell.physics
def test_the_model_is_full_profile_of_the_cells_physics():
    """`model` is `full_profile` of `physics`, bit for bit, so the world and the fitter read one mapping."""
    cell = _cell()
    d = cell.unpack(_truth(cell))
    nu = np.linspace(-20.0, 20.0, 801)
    got = cell.model(nu, d, cell.per[0], "4192", "P")
    want = full_profile(nu, **cell.physics(d, cell.per[0], "4192", "P"))
    assert np.array_equal(got, want)
    # every key is a named parameter of full_profile, except `profile`, which reaches model_profile through
    # its keyword pass-through
    named = set(inspect.signature(full_profile).parameters)
    assert set(cell.physics(d, cell.per[0], "4192", "P")) - named == {"profile"}


# ------------------------------------------------------------------ the inject seam
def test_a_world_that_returns_the_cells_own_line_injects_what_no_world_injects():
    """The seam is transparent: at every rung the default and a world returning `cell.model` give the same traces."""
    cell = _with_data(_cell())
    p = _truth(cell)

    def same(c, d, i, t, nu):
        return c.model(nu, d, c.per[i], t["peak"], t["session"])

    for scale in (0.0, 1.0):
        a, _, _ = CL.inject(cell, p, 7, noise_scale=scale)
        b, _, _ = CL.inject(cell, p, 7, noise_scale=scale, world_source=same)
        assert np.array_equal(a[0]["v"], b[0]["v"])


def test_a_world_that_moves_the_line_moves_the_injection():
    """The seam is live: a world with its line one MHz to the blue puts the injected peak there. (The peak and
    not a wide-window centroid: the injection fits a slope as well, which moves a +-30 MHz centroid.)"""
    cell = _with_data(_cell())
    p = _truth(cell)

    def shifted(c, d, i, t, nu):
        return c.model(nu - 1.0, d, c.per[i], t["peak"], t["session"])

    a, _, _ = CL.inject(cell, p, 7, noise_scale=0.0)
    b, _, _ = CL.inject(cell, p, 7, noise_scale=0.0, world_source=shifted)
    x = cell.traces[0]["x"]
    moved = x[int(np.argmax(b[0]["v"]))] - x[int(np.argmax(a[0]["v"]))]
    assert 0.8 < moved < 1.2


# ------------------------------------------------------------------ VolumeWorld: what it refuses
def test_the_world_refuses_a_cell_carrying_a_term_it_cannot_render():
    """The saturated ramp is a term the weak-field line lacks: refused, and admitted only when named in `allow`."""
    cell = _with_data(_cell(ramp="saturated"))
    d = cell.unpack(_truth(cell))
    nu = cell.traces[0]["x"]
    with pytest.raises(ValueError, match="saturated_ramp"):
        CL.VolumeWorld(n_path=200)(cell, d, 0, cell.traces[0], nu)
    world = CL.VolumeWorld(n_path=200, allow=("saturated_ramp",))
    assert np.all(np.isfinite(world(cell, d, 0, cell.traces[0], nu)))
    assert "saturated_ramp" in world.describe()


def test_the_world_passes_the_registrys_door_before_its_first_atom():
    """O58 (2026-09-25): the closure world is a twin and is refused before its first atom unless the
    registry admits the terms it executes. Its default study reason carries it; a reason under six words does not."""
    cell = _with_data(_cell())
    d = cell.unpack(_truth(cell))
    nu = cell.traces[0]["x"]
    world = CL.VolumeWorld(n_path=200)
    assert np.all(np.isfinite(world(cell, d, 0, cell.traces[0], nu)))
    assert "the registry's door study" in world.describe()
    with pytest.raises(Exception, match="six words|reason"):
        CL.VolumeWorld(n_path=200, registry="too short")(cell, d, 0, cell.traces[0], nu)


def test_the_kernel_preflight_never_asks_below_the_bores_floor():
    """The closure's preflight span sits on the floor its grid takes, and the retired form's did not: an unclamped
    truth - 2 um fell under the lowest node the fallback purge left, so every run was refused before its first cell."""
    lo, hi = CL.preflight_span([CL.TRUTH_UM])
    assert lo == CL.GRID_UM[0]
    assert hi == max(CL.GRID_UM)
    assert CL.TRUTH_UM - 2.0 < CL.GRID_UM[0], "the planted case: the retired bound sits under the floor"
    assert CL.preflight_span([CL.TRUTH_UM], [40.0])[0] == 40.0, "an explicit diagnostic grid keeps its own waists"


def test_the_world_has_one_beam():
    """A w0-free arm's separate waist meters cannot be injected by a world with one beam."""
    cell = _with_data(_cell())
    d = dict(cell.unpack(_truth(cell)), w0_shift_rel=1.1)
    with pytest.raises(ValueError, match="one beam"):
        CL.VolumeWorld(n_path=200)(cell, d, 0, cell.traces[0], cell.traces[0]["x"])


# ------------------------------------------------------------------ VolumeWorld: what it carries
def test_the_world_reads_the_cells_physics_and_the_physical_collection_window():
    """The shift is the Cell's, the Lorentzian carries every homogeneous term the Cell's line does, the laser's
    Gaussian is the Cell's, and the half-window is the imaged half-length of the collection optics at any M2."""
    for m2 in (1.0, 1.3):
        cell = _cell(m2=m2)
        d = cell.unpack(_truth(cell))
        kw = CL.VolumeWorld(n_path=200).inputs(cell, d, 0, cell.traces[0])
        phys = cell.physics(d, cell.per[0], "4192", "P")
        assert kw["S0_mhz"] == pytest.approx(phys["s0"], rel=1e-12)
        gamma = (CL._GAMMA_NAT_MHZ + phys["gamma_coll"] + saturation_companion_mhz(phys["omega_mhz"], "4192")
                 + max(phys["gamma_l"], 0.0))
        assert kw["gamma_hom_mhz"] == pytest.approx(gamma, rel=1e-12)
        assert kw["sigma_laser_mhz"] == pytest.approx(phys["sigma_laser_fwhm"], rel=1e-12)
        magnification = (K.COLLECTION_IMAGE_DIST_M - K.COLLECTION_LENS_F_M) / K.COLLECTION_LENS_F_M
        assert kw["half_window_m"] == pytest.approx(0.5 * K.PMT_CATHODE_ALONG_BEAM_M / magnification, rel=1e-9)


def test_the_gaussian_world_with_no_shift_is_the_cells_line():
    """The plant (C6b D2, and F317's symptom): with no light shift the Monte Carlo world and the fitter's line
    are the same transit convolved with the same homogeneous and laser widths, so they agree. CALIBRATED at
    16 000 atoms at the archive's corner: 3e-4 of peak, the variance to 1e-4 and the third moment to zero.
    The per-atom Lorentzian F317 retired read a variance 4 per cent high and a third moment of -0.072 MHz^3."""
    cell = _with_data(_cell())
    d = dict(cell.unpack(_truth(cell)), alpha_rel=0.0)
    nu = np.linspace(-30.0, 30.0, 6001)
    world = CL.VolumeWorld(n_path=16000)(cell, d, 0, cell.traces[0], nu)
    model = cell.model(nu, d, cell.per[0], "4192", "P")
    assert np.max(np.abs(world / world.max() - model / model.max())) < 2e-3
    (_, vw, k3w), (_, vm, _) = _moments(nu, world), _moments(nu, model)
    assert abs(vw / vm - 1.0) < 2e-3
    assert abs(k3w) < 1e-3


@pytest.mark.xfail(strict=True, reason=(
    "with the clipped beam the default in both (the fold of 2026-09-25), the Cell's scalar bore puts the "
    "centroid 9.1 per cent from VolumeWorld's spatially resolved one against a one per cent tolerance; closing it "
    "is the full model's work (plan V6.1 and V6.3), never a wider tolerance, and an XPASS removes this mark"))
def test_the_centroid_survives_the_pairing():
    """The centroid is immune to the shift-transit pairing a convolution discards: at the archive's shift the
    world's and the fitter's means agree to one per cent (CALIBRATED 0.36 per cent at 16 000 atoms), on the blue
    side `lineshape.RAMP_SIDE` names for both."""
    cell = _with_data(_cell())
    d = cell.unpack(_truth(cell))
    nu = np.linspace(-30.0, 30.0, 6001)
    world = CL.VolumeWorld(n_path=16000)(cell, d, 0, cell.traces[0], nu)
    model = cell.model(nu, d, cell.per[0], "4192", "P")
    mw, mm = _moments(nu, world)[0], _moments(nu, model)[0]
    assert mw > 0.0 and mm > 0.0
    assert abs(mw / mm - 1.0) < 1e-2


def test_the_world_line_is_computed_once_per_condition():
    """Repeats and realisations of one condition share one world: a second call returns the cached line."""
    cell = _with_data(_cell())
    d = cell.unpack(_truth(cell))
    world = CL.VolumeWorld(n_path=300)
    nu = cell.traces[0]["x"]
    a = world(cell, d, 0, cell.traces[0], nu)
    assert len(world._lines) == 1
    b = world(cell, d, 0, cell.traces[0], nu[::2])
    assert len(world._lines) == 1 and np.array_equal(a[::2], b)


# ------------------------------------------------------------------ the clipped world (D3)
def test_a_clipped_world_must_read_the_cells_waist():
    """A clipped beam focusing elsewhere has no single truth with the Cell and is refused; built by
    `ClippedBeam.at_focus` it reads the waist, and its on-axis intensity per recorded watt is the one the Cell's
    shift already carries, to the two quadratures' agreement."""
    from rb5s6s.beam_field import ClippedBeam
    cell = _with_data(_cell())
    d = cell.unpack(_truth(cell))
    with pytest.raises(ValueError, match="at_focus"):
        CL.VolumeWorld(ClippedBeam(w_in_m=1.0e-3), n_path=200).inputs(cell, d, 0, cell.traces[0])
    beam = ClippedBeam.at_focus(cell.w0)
    world = CL.VolumeWorld(beam, n_path=200)
    kw = world.inputs(cell, d, 0, cell.traces[0])
    assert kw["S0_mhz"] / cell.physics(d, cell.per[0], "4192", "P")["s0"] == pytest.approx(1.0, abs=1e-3)
    ratio = beam.onaxis_per_watt() / (2.0 / (math.pi * cell.w0 ** 2))
    assert ratio == pytest.approx(cell.aperture_onaxis, abs=1e-3)


# ------------------------------------------------------------------ the fitter on the volume line (C6b item 2)
def _volume_cell(tmp_path, n_path=2000, **extra):
    vol = {"n_path": n_path, "seed": 7, "cache_dir": str(tmp_path)}
    return UJ.Cell(UJ._spec("mixed", W0_UM, da=(K.DELTA_ALPHA_AU, 5.9), kernel_gate="legacy", ramp=extra.pop("ramp", "weak"),
                            depletion=extra.pop("depletion", "none"), volume_line=vol, **extra), [_trace()])


def test_a_volume_cell_refuses_what_its_table_cannot_carry(tmp_path):
    """The joint table is weak-field, undepleted and holds one beam: a saturated ramp, a transit depletion or
    three floating waist meters are refused by name, never half-converted."""
    for extra, word in ((dict(ramp="saturated"), "ramp"), (dict(depletion="mc"), "depletion"),
                        (dict(w0_free=True), "w0_free")):
        with pytest.raises(ValueError, match=word):
            _volume_cell(tmp_path, **extra)


def test_a_volume_cell_passes_the_table_and_neither_the_transit_nor_the_ramp(tmp_path):
    cell = _volume_cell(tmp_path)
    d = cell.unpack(_truth(cell))
    phys = cell.physics(d, cell.per[0], "4192", "P")
    assert phys["transit_fwhm"] is None and "profile" not in phys and phys["volume_table"] is not None
    assert phys["w0_m"] == cell.w0 and phys["T_C"] == 130.0 and phys["isotope"] == 85


def test_a_volume_cell_reads_the_monte_carlo_line(tmp_path):
    """The plant of item 2: the fitter's volume line against the Monte Carlo world drawn from the same atoms.
    CALIBRATED at 2 000 and 8 000 atoms: 3.4e-5 of peak, the table's S0 interpolation and its detuning grid,
    independent of the atom count because both sides read the same atoms."""
    cell = _volume_cell(tmp_path)
    d = cell.unpack(_truth(cell))
    x = cell.traces[0]["x"]
    m = cell.model(x, d, cell.per[0], "4192", "P")
    w = CL.VolumeWorld(n_path=2000, seed=7)(cell, d, 0, cell.traces[0], x)
    assert np.max(np.abs(m / m.max() - w / w.max())) < 2e-4

"""The two axial terms reach the world builder through one mixture, and the
default path is untouched.

Until 2026-09-08 `build_world_trace` convolved the pure transverse ramp, so
the twin recovered what it injected and would not have recovered this bench's
line: the collection window's divergence (kappa3 at 0.93 of the ramp's at
64 um, reversed in sign at 16) and the standing wave's fringe-resolved tail
(a skew suppression near a quarter at 16 um) were both derived in the record
and threaded into nothing. `lineshape.ramp_mixture` carries either or both
from one local density; these tests hold it against the closed forms it
generalises, hold the fringe density against the pooled moments of the same
draws, and prove the switches are neither no-ops nor on by default.
"""
import csv
import math
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K

from rb5s6s.fringe_tail import (COHERENCE_TRANSIT, fringe_shift_density,
                               fringe_tail_mc)
from rb5s6s.forecast import build_world_trace
from rb5s6s.lineshape import (local_ramp_density, ramp_mixture, stark_ramp,
                              stark_ramp_axial)

ROOT = Path(__file__).resolve().parents[1]
NU = np.arange(-40.0, 40.0, 0.01)
XG = np.linspace(-1.0, 0.0, 4001)


@pytest.mark.parametrize("z_ratio", [0.2605, 0.667, 1.708, 4.169])
def test_the_mixture_of_the_transverse_law_is_the_axial_ramp(z_ratio):
    """The closed form zeta_m + zeta_m^3/3 is this integral done by hand."""
    f = ramp_mixture(NU, 2.0, z_ratio, XG, local_ramp_density(XG))
    ref = stark_ramp_axial(NU, 2.0, z_ratio)
    assert np.abs(f - ref).max() < 1e-3 * ref.max()
    assert abs(f.sum() * 0.01 - 1.0) < 1e-9


def test_the_mixture_at_zero_window_is_the_transverse_ramp():
    """Cell for cell the axial form's own limit; against stark_ramp it differs
    in the edge cell alone, by that function's first-moment transfer, and the
    mean is the exact -2/3 s0 either way."""
    f = ramp_mixture(NU, 2.0, 0.0, XG, local_ramp_density(XG))
    assert np.abs(f - stark_ramp_axial(NU, 2.0, 1e-12)).max() < 1e-12
    ref = stark_ramp(NU, 2.0)
    diff = np.abs(f - ref)
    assert diff.max() < 0.05 * ref.max() and (diff > 1e-3 * ref.max()).sum() <= 2
    assert (NU * f).sum() * 0.01 == pytest.approx(-2.0 / 3.0 * 2.0, abs=2e-3)


def _moments(x, dens):
    dx = x[1] - x[0]
    m = (x * dens).sum() * dx
    c = x - m
    return m, (c ** 2 * dens).sum() * dx, (c ** 3 * dens).sum() * dx


def test_the_fringe_density_without_contrast_is_the_ramp():
    """rho = 0 removes the fringe; dividing the path factor out leaves the
    record's own |x| ramp: mean -2/3, variance 1/18, third cumulant +1/135."""
    d = fringe_shift_density(w0_m=64e-6, rho=0.0, n_atoms=200_000, seed=7,
                             coherence_s=COHERENCE_TRANSIT)
    assert d["kappa_bar"] == pytest.approx(math.sqrt(2.0 / 3.0), abs=1e-9)
    m, v, k3 = _moments(d["x_grid"], d["density"])
    assert m == pytest.approx(-2.0 / 3.0, abs=0.01)
    assert v == pytest.approx(1.0 / 18.0, rel=0.05)
    assert k3 == pytest.approx(1.0 / 135.0, rel=0.10)


def test_the_binned_density_agrees_with_the_pooled_sums_and_with_fringe_tail_mc():
    """Same seed, same draws: the histogram's third cumulant in raw units is
    the power sums', and the power sums scale as S0 cubed against the MC."""
    d = fringe_shift_density(w0_m=16e-6, rho=0.94, n_atoms=200_000, seed=11,
                             coherence_s=COHERENCE_TRANSIT)
    x_raw = d["x_grid"] * d["kappa_bar"]
    _, _, k3_hist = _moments(x_raw, d["density"] / d["kappa_bar"])
    assert k3_hist == pytest.approx(d["kappa3_raw"], rel=0.02)
    mc = fringe_tail_mc(w0_m=16e-6, s0_mhz=2.0, rho=0.94, n_atoms=200_000, seed=11)
    assert mc["kappa3"] / 8.0 == pytest.approx(d["kappa3_raw"], rel=1e-6)
    # and the fringe suppresses the skew at the tight waist, as the record says
    assert mc["kappa3_nofringe"] != 0
    assert -0.45 < mc["d_kappa3"] / mc["kappa3_nofringe"] < -0.10


def _world(**kw):
    layers = {"cascade": False, "saturation": False, "stark": True,
              "bbr": False, "drift": False, "quantise": False, "randomise": False}
    return build_world_trace(
        0.225, 1.618, 130.0, 0, 1, np.random.default_rng(4), layers,
        positions={"4192": 0.0}, shares={"4192": 1.0},
        gamma_coll=0.4, sigma_laser_fwhm=2.0, transit_fwhm=0.93,
        power_max_w=0.225, cycles_at_max=1.0, drift_mhz_total=0.0,
        noise_frac_bright=1e-9, adc_levels=2 ** 16, offset=0.0, **kw)


def test_the_new_machinery_at_its_identity_setting_reproduces_the_untouched_path():
    """The switches off leave the trace the pre-2026-09-08 path produced.

    WHAT THIS CANNOT DO, said first. Comparing `_world()` with
    `_world(z_ratio=None, fringe_density=None)` compares two spellings of ONE
    call, so it holds whatever the default path does: with the ramp scaled by
    a factor, a one per cent one passed it. Scaling the SHIFT inside the
    composition is what a drift looks like; scaling the ramp's AMPLITUDE moves
    nothing at all, since the trace is peak-normalised, so under that reading
    of the same word the assertion cannot fail either. Two quantities under
    one word, and it is retired under both (2026-09-08).

    What replaces it runs the NEW machinery at the setting where it is the
    identity and requires it to reproduce the default: a zero collection
    window over the transverse density IS the pure ramp, analytically, so any
    drift in either the default path or the mixture separates them. The claim
    that every COMMITTED trace is unchanged is a claim about the committed
    CSVs and is carried by the freshness set, not by this file.
    """
    _, base, _ = _world()
    _, identity, _ = _world(z_ratio=0.0, fringe_density=(XG, local_ramp_density(XG)))
    # measured 2.1e-5 of the peak on this line, the mixture's own quadrature
    # against the closed form. WHAT IT CATCHES, measured: a shift scale of
    # 1.001 separates by 8.2e-5 and PASSES, 1.01 by 6.4e-4 and fails, so the
    # floor binds at about a seventh of a per cent and not at 'any drift'.
    assert np.abs(identity - base).max() < 1e-4 * base.max(), (
        "the mixture at its identity setting no longer reproduces the default "
        "path: one of the two moved")
    _, spelled_out, _ = _world(z_ratio=None, fringe_density=None)
    assert np.array_equal(base, spelled_out), "the two spellings must agree"


def test_neither_switch_is_a_no_op_by_a_margin_that_is_not_machine_noise():
    """`not array_equal` passes on a difference of 1e-16 and so cannot tell a
    wired term from a vestigial one (the register seat, 2026-09-08); each
    switch must move the trace by a physically visible fraction of the peak.
    """
    _, base, _ = _world()

    def moved(y):
        return float(np.abs(y - base).max() / base.max())

    # the measured margins on this line, 2026-09-08: the window moves it by
    # 6.6e-3 of the peak, the fringe by 2.1e-3, and each term moves the other's
    # trace by 6.6e-4 and 5.1e-3. The floor below is one part in ten thousand,
    # twelve orders above the 1e-16 that `not array_equal` accepts and a
    # factor of six under the smallest real movement.
    FLOOR = 1e-4
    _, axial, _ = _world(z_ratio=0.667)
    assert moved(axial) > FLOOR, moved(axial)
    d = fringe_shift_density(w0_m=16e-6, rho=0.94, n_atoms=50_000, seed=3,
                             coherence_s=COHERENCE_TRANSIT)
    _, fringed, _ = _world(fringe_density=(d["x_grid"], d["density"]))
    assert moved(fringed) > FLOOR, moved(fringed)
    _, both, _ = _world(z_ratio=0.667, fringe_density=(d["x_grid"], d["density"]))
    assert float(np.abs(both - axial).max() / base.max()) > FLOOR
    assert float(np.abs(both - fringed).max() / base.max()) > FLOOR


@pytest.mark.parametrize("label,x_grid,want", [
    ("descending", np.linspace(0.0, -1.0, 801), "refuse"),
    ("stops short of zero shift", np.linspace(-1.0, -0.2, 801), "refuse"),
    ("wholly positive", np.linspace(0.0, 1.0, 801), "refuse"),
    ("a genuinely narrower support", np.linspace(-0.5, 0.0, 801), "accept"),
    ("the transverse law's own grid", np.linspace(-1.0, 0.0, 801), "accept"),
])
def test_the_mixture_refuses_a_grid_it_would_silently_misread(label, x_grid, want):
    """`ramp_mixture` is exported and is in the ADAPTING import block, and it
    reads the support's lower edge as `x_grid[0]` while interpolating with
    zero outside. On a DESCENDING grid it returned a delta at the origin
    rather than a line, mean 0.00 against the correct -0.65, with no error
    (the adoption seat, 2026-09-08). A grid that stops short of zero shift
    renormalises to a narrower ramp the same way. A genuinely narrower support
    is legal and must still pass, which is the direction that makes this a
    contract and not a guess."""
    nu = np.linspace(-6.0, 6.0, 2001)
    g = local_ramp_density(x_grid)
    if want == "refuse":
        with pytest.raises(ValueError):
            ramp_mixture(nu, 1.0, 0.26, x_grid, g)
    else:
        assert np.isfinite(ramp_mixture(nu, 1.0, 0.26, x_grid, g)).all()


def test_the_mixture_refuses_a_malformed_density():
    """Length, finiteness and sign, each through the real call path."""
    nu = np.linspace(-6.0, 6.0, 2001)
    x = np.linspace(-1.0, 0.0, 801)
    g = local_ramp_density(x)
    for bad in (g[:-1],
                np.where(np.arange(g.size) == 10, np.nan, g),
                np.where(np.arange(g.size) == 10, -1.0, g)):
        with pytest.raises(ValueError):
            ramp_mixture(nu, 1.0, 0.26, x, bad)



def test_the_coherence_end_is_named_and_the_old_silent_default_is_refused():
    """tau_c is the module's one open modelling choice, worth a factor of
    eleven in the frozen-fringe fraction, so a caller names the end it took.

    The failure this prevents: a producer that omitted the argument took the
    transit-limited end silently and published a tolerance whose other end
    lies outside the half-span beside it. `None` is refused BY NAME rather
    than read as the cap it used to mean, so an un-updated caller stops
    instead of continuing to publish one end of a bracket as the answer."""
    for bad in (None, "cap", "", 0.0, -1e-9, float("inf")):
        with pytest.raises(ValueError):
            fringe_shift_density(w0_m=64e-6, coherence_s=bad, n_atoms=200, seed=1)


def test_the_transit_sentinel_is_the_long_window_limit_and_a_short_one_moves_it():
    """Positive, tolerance and negative in one place: the sentinel agrees with
    a window far longer than the crossing, and the 6S lifetime does not."""
    kw = dict(w0_m=16e-6, rho=0.94, n_atoms=60_000, seed=5)
    cap = fringe_shift_density(coherence_s=COHERENCE_TRANSIT, **kw)
    long_window = fringe_shift_density(coherence_s=1.0, **kw)   # 1 s >> 65 ns
    short = fringe_shift_density(coherence_s=K.TAU_6S_S, **kw)
    assert long_window["kappa3_raw"] == pytest.approx(cap["kappa3_raw"], rel=1e-9)
    # and the short window is a real movement, not the same number twice
    assert abs(short["kappa3_raw"] / cap["kappa3_raw"] - 1.0) > 0.02


def test_the_sweep_envelope_covers_the_coherence_corner_it_names():
    """The err row is at least the coherence excursion beside it.

    The producer's half-span is read as the excursion from the tolerance and
    not as half the bracket, because the coherence corner is ONE-SIDED: half a
    bracket understates a one-sided corner by a factor of two, which at
    40 microns is the difference between covering the other end of tau_c and
    printing a number that excludes it."""
    rows = {}
    with open(ROOT / "results" / "sweep_linearity.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            rows[(r["case"], r["quantity"])] = r["value"]
    cases = sorted({c for c, _ in rows})
    assert cases, "no cases read from the committed sweep"
    for case in cases:
        err = float(rows[(case, "rate_variation_tolerance_err")])
        coh = float(rows[(case, "rate_variation_tolerance_coherence_err")])
        waist = float(rows[(case, "rate_variation_tolerance_waist_err")])
        assert coh > 0.0, case
        assert err >= coh, (case, err, coh)
        assert err >= waist, (case, err, waist)

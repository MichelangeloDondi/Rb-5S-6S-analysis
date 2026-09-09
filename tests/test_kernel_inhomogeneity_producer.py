"""Guards for `scripts/run_kernel_inhomogeneity.py`.

The producer shipped with none on 2026-09-09 and three seats said so
independently: every other producer writing into `results/` has a matching
test module, and the wave's own claims table marked two of six rows as checked
by hand and not in the suite. Those two claims were true when checked, which is
the point: nothing would have caught them ceasing to be.

The cases below hold the structural facts, not the numbers, so they survive a
regeneration. Each is cheap: none calls `main()`, which takes minutes.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import constants as K
from rb5s6s import stark
from rb5s6s.lineshape import model_profile

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_kernel_inhomogeneity.py"


def _load():
    spec = importlib.util.spec_from_file_location("_kin_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_transit_kernel_is_widest_at_the_waist_not_the_window_edge():
    """The direction the producer's prose had backwards in eight cells.

    `transit_fwhm_from_w0` goes as one over the local beam radius, so the
    narrowest beam carries the widest kernel. That is the whole mechanism: the
    broad elements and the shifted elements are the same elements."""
    mod = _load()
    cells, _s0, _z = mod.volume_grid(16e-6, n_s=8, n_z=9)
    transits = [tr for _, tr, _ in cells]
    waist_slice = len(transits) // 2          # z = 0 sits at the grid's centre
    assert transits[waist_slice] == max(transits), \
        "the transit kernel must be widest at the waist"
    assert transits[0] == min(transits) or transits[-1] == min(transits), \
        "the narrowest kernel belongs to a window edge"
    assert max(transits) / min(transits) > 3.0, "at 16 um the span is fourfold"


def test_the_first_moment_does_not_depend_on_the_kernel():
    """A mixture of symmetric kernels has the density's own mean, exactly.

    This is one line of algebra and it is why the centre channel is immune. The
    producer reported a -0.43 per cent cost at 16 um until 2026-09-09; that was
    its own frequency span truncating a Lorentzian wing, not physics. If the
    span narrows again this case fails."""
    mod = _load()
    stark.COMPANIONS = {"ratio": 1.2367, "scale": 1.0}
    cells, _s0, _z = mod.volume_grid(16e-6, n_s=40, n_z=10)
    tot = sum(float(w.sum()) for _, _, w in cells)
    analytic = -sum(float((m * w).sum()) for m, _, w in cells) / tot
    exact, _ = mod.observables(mod.profile_exact(cells), 12.0)
    assert exact == pytest.approx(analytic, rel=5e-3), (exact, analytic)


def test_one_axial_slice_reproduces_the_shipped_composite_profile():
    """The reduction the claims table asserted by hand and nothing guarded."""
    mod = _load()
    stark.COMPANIONS = None
    w0 = 64e-6
    s0 = stark.stark_shift_S0_mhz(0.225, w0, K.RHO_RETRO)
    tr = K.transit_fwhm_from_w0(w0, 130.0)
    e = np.linspace(0.0, s0, 401)
    mid = 0.5 * (e[:-1] + e[1:])
    wgt = mid / mid.sum()
    mine = mod._mix([(mid, tr, wgt)], lambda s, t: mod._kernel(mod.GAMMA_COLL, t))
    ship = model_profile(mod.NU, gamma_coll=mod.GAMMA_COLL,
                         sigma_laser_fwhm=mod.SIGMA_LASER, transit_fwhm=tr,
                         s0=s0, gamma_nat_mhz=mod.GAMMA_NAT, resolve_shift=True)
    a, b = mine / mine.sum(), ship / ship.sum()
    assert float(np.abs(a - b).max() / b.max()) < 2e-3
    assert float((mod.NU * a).sum()) == pytest.approx(-2.0 * s0 / 3.0, rel=2e-3)


def test_the_saturated_kernel_is_matched_by_a_saturated_weight():
    """Broadening an element without dimming it is the inconsistency the board
    found: under the steady-state law the area falls by the same root the width
    grows by, so the weight must carry it too."""
    mod = _load()
    # THE EXPECTATION READS THE KERNEL'S OWN PARAMETERS, never the producer's
    # module literals (2026-09-09, round two). Reading `mod.COMPANION_RATIO`
    # and `mod.GAMMA_NAT` made this test a tautology about the producer: with
    # COMPANION_RATIO set to 2.0 and the kernel still at 1.2367 it passed, so
    # it could not see the two drifting apart, which is the whole failure it
    # exists to catch.
    import inspect
    from rb5s6s import stark as _stark
    # main() is what wires the layer, and it must wire it FROM the producer's
    # own constant. A second literal there is how the weight and the kernel
    # drift apart, and it is not visible from any runtime value once both are
    # set: this is the check, and the runtime one below is its consequence.
    src = inspect.getsource(mod.main)
    assert 'stark.COMPANIONS = {"ratio": COMPANION_RATIO' in src, (
        "main() no longer wires the companion from COMPANION_RATIO, so the "
        "weight's saturation ratio and the kernel's are two literals again")
    _stark.COMPANIONS = {"ratio": mod.COMPANION_RATIO, "scale": 1.0}  # as main does
    cells, s0, _z = mod.volume_grid(16e-6, n_s=60, n_z=6)
    mid, _tr, wgt = cells[len(cells) // 2]
    om = _stark.COMPANIONS["ratio"] * mid
    unsat = mid * (mid[1] - mid[0])
    ratio = (wgt / wgt.sum()) / (unsat / unsat.sum())
    assert mod.GAMMA_NAT == pytest.approx(_stark._GAMMA_MHZ, rel=1e-3), \
        "the weight's natural width and the kernel's are two names for one constant"
    expected = 1.0 / np.sqrt(1.0 + 2.0 * (om / _stark._GAMMA_MHZ) ** 2)
    assert ratio == pytest.approx(expected / expected.mean() * ratio.mean(), rel=1e-6)
    assert ratio[-1] < 0.6 * ratio[0], "the bright end must be dimmed, not only broadened"


def test_the_companion_is_the_cumulant_uncertainty_axis_and_the_grid_is_not():
    """The error row named the grid while the companion moved the value by
    threefold. Both axes are swept; this holds their ordering."""
    mod = _load()
    stark.COMPANIONS = {"ratio": 1.2367, "scale": 1.0}
    cells, _s0, _z = mod.volume_grid(64e-6, n_s=60, n_z=10)
    base = mod.observables(mod.profile_exact(cells), 6.0)[1]
    lo = mod.observables(mod.profile_exact(cells, companion_scale=1 / 3.0), 6.0)[1]
    hi = mod.observables(mod.profile_exact(cells, companion_scale=3.0), 6.0)[1]
    companion_span = abs(hi - lo)
    coarse = mod.observables(mod.profile_exact(
        mod.volume_grid(64e-6, n_s=30, n_z=10)[0]), 6.0)[1]
    assert companion_span > 10.0 * abs(base - coarse), \
        "the companion must dominate the shift-grid axis by an order or more"

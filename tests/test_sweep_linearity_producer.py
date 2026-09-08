"""Guards for `scripts/run_sweep_linearity.py`, the sweep-rate tolerance.

The producer asserts at import that every case's shift literal is the
package's own at the campaign's top power and the adopted retro ratio, so the
freshness check grades the physics and not only the arithmetic. That
assertion shipped on 2026-09-08 with no re-runnable plant, closed on a
deferral, and this is the plant: the real module source, mutated one literal
at a time, executed through the same import-time path the producer takes.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rb5s6s import constants as K
from rb5s6s import stark

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_sweep_linearity.py"
CASE_LITERAL = '("archive", 64e-6, 0.364, 6.0, True)'


def _exec(source: str) -> dict:
    """Run the producer's module-level code, which is where the check lives."""
    g = {"__name__": "_sweep_plant", "__file__": str(SCRIPT)}
    exec(compile(source, str(SCRIPT), "exec"), g)
    return g


def _first_case_shift(s0: float) -> str:
    src = SCRIPT.read_text(encoding="utf-8")
    assert src.count(CASE_LITERAL) == 1, "the archive case moved; re-anchor this plant"
    return src.replace(CASE_LITERAL, f'("archive", 64e-6, {s0!r}, 6.0, True)', 1)


def test_the_shift_literal_check_passes_the_tree_as_it_stands():
    """The negative case, and it is the file itself rather than a fixture."""
    g = _exec(SCRIPT.read_text(encoding="utf-8"))
    assert g["CASES"][0][2] == pytest.approx(
        stark.stark_shift_S0_mhz(0.225, 64e-6, K.RHO_RETRO), rel=2e-3)


@pytest.mark.parametrize("factor", [1.5, 0.5, 1.02, 0.98])
def test_a_wrong_shift_literal_is_refused_at_import(factor):
    """A literal that is not the package's stops the producer before it writes."""
    pred = stark.stark_shift_S0_mhz(0.225, 64e-6, K.RHO_RETRO)
    with pytest.raises(SystemExit) as e:
        _exec(_first_case_shift(pred * factor))
    assert "carries s0" in str(e.value) and "archive" in str(e.value)


@pytest.mark.parametrize("delta,refused", [(0.0015, False), (0.0025, True)])
def test_the_tolerance_is_probed_just_inside_and_just_outside(delta, refused):
    """Two parts in a thousand, from each side of the catch region.

    The check reads the departure against the LITERAL, so the crossing sits a
    hair above the nominal two parts in a thousand; both probes are clear of
    it by a quarter of the band."""
    pred = stark.stark_shift_S0_mhz(0.225, 64e-6, K.RHO_RETRO)
    src = _first_case_shift(pred * (1.0 + delta))
    if refused:
        with pytest.raises(SystemExit):
            _exec(src)
    else:
        _exec(src)


def test_every_case_carries_the_package_shift_and_not_only_the_first():
    """The plant mutates the archive case; the guard must cover all three, so
    the population is checked here rather than assumed from one probe."""
    g = _exec(SCRIPT.read_text(encoding="utf-8"))
    assert len(g["CASES"]) >= 3
    for name, w0, s0, _W, _lic in g["CASES"]:
        assert s0 == pytest.approx(
            stark.stark_shift_S0_mhz(0.225, w0, K.RHO_RETRO), rel=2e-3), name

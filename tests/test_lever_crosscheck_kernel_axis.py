"""The third model-form axis is WIRED, not merely declared.

The sharpest lesson this record holds about configuration is that a switch
which is thrown and does nothing is worse than one never thrown: a forecast
declared a saturation layer on, never assigned the module global it needs, and
published twenty-three cells with the term silently at zero while its own layer
table said otherwise. A test that asserts only the flag's presence passes
against that.

So the check here is behavioural and it reads the CALL: `_fit` must hand
`gamma_l` to `fit_global`, the grid's kernel cell must carry the measured value
rather than zero, and the constant must sit inside the range the kernel chain
actually fits. The expensive part, what the axis does to the coefficient, is
measured in the producer's own CSV and in this repository's private correction
record; nothing here re-runs a fit.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rb5s6s import lever_crosscheck as LC

ROOT = Path(__file__).resolve().parents[1]


def kernel_k3_range_mhz() -> tuple[float, float]:
    """What `results/kernel_k3.csv` FITS for this component, read from the file.

    It was typed as (0.315, 0.449) until a reader compared it with the file's
    own extremes, 0.314803 and 0.449389, so the typed pair rounded INWARD on
    both sides: the guard would have refused the very per-peak minimum and
    maximum it claimed to admit, and it held only because the constant sits in
    the middle. A range that bounds a constant is read from the thing it bounds.
    """
    import csv
    vals = []
    with (ROOT / "results" / "kernel_k3.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("quantity") == "gamma_l_equiv" and row.get("value"):
                try:
                    vals.append(float(row["value"]))
                except ValueError:
                    pass
    assert len(vals) >= 4, (
        f"expected one fitted component per peak, found {len(vals)}: this "
        "guard's range would otherwise be derived from a population too small "
        "to bound anything")
    return min(vals), max(vals)


def test_the_measured_component_lies_inside_what_the_kernel_chain_fits():
    lo, hi = kernel_k3_range_mhz()
    assert lo <= LC.GAMMA_L_MEASURED_MHZ <= hi, (
        f"GAMMA_L_MEASURED_MHZ={LC.GAMMA_L_MEASURED_MHZ} is outside the "
        f"{lo} to {hi} MHz that kernel_k3.csv fits, so it is not the measured "
        "value this module says it is")


def test_the_kernel_cell_is_the_primary_corner_one_step_along_the_new_axis():
    assert LC.KERNEL_CELL[:2] == LC.PRIMARY, (
        "the kernel cell must differ from the primary corner in the new axis "
        f"ALONE, or its difference is not that axis: {LC.KERNEL_CELL} against "
        f"{LC.PRIMARY}")
    assert LC.KERNEL_CELL[2] == LC.GAMMA_L_MEASURED_MHZ


def test_the_axis_is_not_a_fourth_member_of_the_published_grid():
    """`beta_err_modelform` is a pushed number defined over three cells.

    Widening its definition silently is the failure this separation exists to
    prevent, so the grid the published bar is computed from must stay at three
    two-tuples.
    """
    assert len(LC.GRID_CELLS) == 3, LC.GRID_CELLS
    assert all(len(c) == 2 for c in LC.GRID_CELLS), LC.GRID_CELLS
    assert LC.KERNEL_CELL not in LC.GRID_CELLS


def test_fit_hands_the_component_to_the_fitter(monkeypatch):
    """The wiring itself, read at the call rather than at the flag."""
    seen = {}

    def _spy(blocks, **kw):
        seen.update(kw)
        return {"beta_by_isotope": {}, "beta_err_by_isotope": {},
                "chi2_red": 1.0, "chi2_whitened": 1.0}

    monkeypatch.setattr(LC, "fit_global", _spy)
    LC._fit([], "exp", "per_T", 0.93, 110.0, LC.GAMMA_L_MEASURED_MHZ)
    assert seen.get("gamma_l") == LC.GAMMA_L_MEASURED_MHZ, (
        f"_fit did not pass the component through: fit_global saw "
        f"gamma_l={seen.get('gamma_l')!r}")


def test_the_default_call_still_asks_for_zero(monkeypatch):
    """Every existing cell must be byte-identical, which means an exact zero."""
    seen = {}

    def _spy(blocks, **kw):
        seen.update(kw)
        return {"beta_by_isotope": {}, "beta_err_by_isotope": {},
                "chi2_red": 1.0, "chi2_whitened": 1.0}

    monkeypatch.setattr(LC, "fit_global", _spy)
    LC._fit([], "exp", "per_T", 0.93, 110.0)
    assert seen.get("gamma_l") == 0.0 and isinstance(seen.get("gamma_l"), float)


@pytest.mark.parametrize("field", ["err_kernel", "kernel_cell", "kernel_beta",
                                   "kernel_chi2_red", "kernel_chi2_whitened",
                                   "primary_chi2_whitened"])
def test_the_result_reports_the_axis(field):
    """A guard on the RETURN shape, so a consumer cannot silently drop the row."""
    import inspect
    src = inspect.getsource(LC.lever_crosscheck_beta)
    assert f'"{field}"' in src, (
        f"lever_crosscheck_beta no longer returns {field!r}, so the producer's "
        "row for the new axis would vanish without any test failing")

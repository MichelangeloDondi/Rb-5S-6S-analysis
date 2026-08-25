"""The advertised front door opens, and it opens onto data.

`examples/your_line.ipynb` is named by START_HERE.md and by the README as the
place a stranger begins. Until v4.4 it never loaded a file or fitted
anything: it recomputed the forward model from a dictionary, which
demonstrates what the package can PREDICT and not what it can MEASURE. A
front door that cannot be walked through is worse than no front door, because
it is advertised.

Two things are pinned here. The notebook's code executes, so it cannot rot
into a broken tutorial while the tests stay green; and its first code cell
LOADS A FILE, so a later edit cannot quietly turn it back into a design
explorer.
"""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "examples" / "your_line.ipynb"


def _cells():
    return json.loads(NOTEBOOK.read_text(encoding="utf-8"))["cells"]


def _code_sources():
    return ["".join(c["source"]) for c in _cells() if c["cell_type"] == "code"]


def test_the_notebook_is_valid_and_has_code():
    assert NOTEBOOK.exists()
    assert len(_code_sources()) >= 3


def test_the_first_code_cell_opens_a_file_and_fits_it():
    """The whole point of the v4.4 rewrite, held here.

    Checked on the FIRST code cell specifically: a load buried at cell ten,
    after nine cells of model exploration, is the defect this replaced.
    """
    first = _code_sources()[0]
    assert "load_trace" in first, "the front door does not open a file"
    assert "fit_linewidth" in first, "the front door does not fit anything"


def test_the_example_trace_travels_with_the_package():
    """A tutorial whose data is absent from the wheel cannot be run."""
    from importlib.resources import files
    path = files("rb5s6s") / "data" / "example_trace_4121nm_225mW.csv"
    assert Path(str(path)).is_file()
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'data/*.csv' in pyproject, "package-data does not carry the trace"
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "rb5s6s/data/*.csv" in manifest, "the sdist does not carry the trace"


@pytest.mark.slow
def test_every_code_cell_executes():
    """Run the notebook the way a reader would, top to bottom, one namespace."""
    import matplotlib
    matplotlib.use("Agg")
    namespace: dict = {}
    out = io.StringIO()
    for i, src in enumerate(_code_sources()):
        try:
            with redirect_stdout(out):
                exec(compile(src, f"<your_line.ipynb cell {i}>", "exec"), namespace)
        except Exception as exc:  # pragma: no cover - the failure is the message
            pytest.fail(f"code cell {i} raised {type(exc).__name__}: {exc}\n\n{src}")
    printed = out.getvalue()
    assert "LinewidthResult" in printed, "the notebook never printed a fit result"
    assert "transition axis" in printed, "the notebook never named its axis"


@pytest.mark.slow
def test_the_fitted_width_is_the_one_the_record_reports():
    """The tutorial must not disagree with the analysis it introduces.

    The shipped trace is a campaign trace, so the width it yields and the
    component shares it prints are checkable against what this record says
    about its own line: the natural width dominates, at about two thirds.
    """
    import numpy as np
    import rb5s6s
    from importlib.resources import files
    from rb5s6s import ingest, linefit

    path = files("rb5s6s") / "data" / "example_trace_4121nm_225mW.csv"
    t_ms, volts = ingest.load_trace(str(path))
    nu = linefit.to_frequency(t_ms, 0.0850485153023648)
    nu = nu - nu[np.argmax(volts)]
    r = rb5s6s.fit_linewidth(nu, volts, T_C=130.0)

    assert 4.0 < r.fwhm_mhz < 7.0, r.fwhm_mhz
    share = r.components["gamma_nat_mhz"] / r.fwhm_mhz
    assert 0.55 < share < 0.75, (
        f"the natural width is {100 * share:.0f}% of this line; the record "
        f"says about two thirds, and a tutorial that disagrees with the "
        f"analysis it introduces teaches the wrong lesson")

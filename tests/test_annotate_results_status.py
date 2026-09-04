"""The status annotator never leaves a results CSV truncated.

On 2026-09-04 a hand-edited note cell put an unquoted comma into
results/identifiability.csv; the annotator's reader took the overflow under
the key None, its writer raised on that row with the file already open, and
the file was left with the twelve rows before it. Two guards, both planted
here: a ragged row is refused before anything is written, and the write
goes to a sibling that is renamed over the original, so a crash inside the
write cannot truncate it. Failure mode if these regress: a results file
is shortened under a tool meant to add a column, and the shortfall looks
like a producer change.
"""
from __future__ import annotations

import csv
import importlib.util
import io
import contextlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _annotator():
    spec = importlib.util.spec_from_file_location(
        "annotate_results_status", ROOT / "scripts" / "annotate_results_status.py")
    mod = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


GOOD = ("quantity,key,value,unit\n"
        "condition_number,width_block,345.1,eigenvalue ratio\n"
        "corr,gamma_coll_transit,-0.958,width-width correlation coefficient\n")
RAGGED = GOOD + "best_constrained_sigma,total_width,0.0032,MHz, an unquoted comma in the note\n"


def _run_on(tmp_path: Path, text: str, monkeypatch):
    mod = _annotator()
    target = tmp_path / "identifiability.csv"
    target.write_text(text)
    monkeypatch.setattr(mod.C, "RESULTS_DIR", tmp_path)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = mod.main()
    return rc, target


def test_a_ragged_row_is_refused_and_the_file_is_untouched(tmp_path, monkeypatch):
    mod = _annotator()
    target = tmp_path / "identifiability.csv"
    target.write_text(RAGGED)
    before = target.read_text()
    monkeypatch.setattr(mod.C, "RESULTS_DIR", tmp_path)
    with pytest.raises(SystemExit) as e, contextlib.redirect_stdout(io.StringIO()):
        mod.main()
    assert "different number of fields" in str(e.value)
    assert target.read_text() == before, "the refusal must leave the file byte-identical"
    assert not (tmp_path / "identifiability.csv.annotating").exists()


def test_a_quoted_comma_in_a_note_survives(tmp_path, monkeypatch):
    """The refusal's false-positive direction: a comma INSIDE a quoted note is
    one field and the annotator must pass it, since the producers quote what
    needs quoting. Probed by a reader on 2026-09-04 and asserted here so a
    tightening of the ragged-row check cannot break legitimate notes."""
    text = GOOD + 'width_signature_fwhm_mhz,gaussian_branch,5.4036,"MHz, FWHM with s0=0 at this branch"\n'
    rc, target = _run_on(tmp_path, text, monkeypatch)
    assert rc == 0
    rows = list(csv.DictReader(open(target)))
    assert rows[-1]["unit"].startswith("MHz, FWHM") and rows[-1]["status"] == "DIAGNOSTIC"


def test_a_well_formed_file_gains_its_status_column_atomically(tmp_path, monkeypatch):
    rc, target = _run_on(tmp_path, GOOD, monkeypatch)
    assert rc == 0
    rows = list(csv.DictReader(open(target)))
    assert [r["status"] for r in rows] == ["DIAGNOSTIC", "DIAGNOSTIC"]
    assert not (tmp_path / "identifiability.csv.annotating").exists()

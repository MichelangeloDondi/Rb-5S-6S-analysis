"""The release-note checker fires on the defect class it was built for.

WHY THIS EXISTS. `scripts/check_release_notes.py` gained N3's mechanism on
2026-08-28, after the owner said the withdrawn v4.3 and v4.4 notes failed on
their physics: a quantity stated in a physical unit with no committed source
named. The mechanism was verified that night against a planted file in the
session scratchpad, which left NO artifact in the repository -- a verified
and unrecorded plant is indistinguishable from an unverified one, and the
same night's board proved the point twice over on other guards.

Both directions are asserted, because the first draft of the mechanism
passed its plant while failing every paragraph that OBEYED the rule: the
paragraph flattener strips inline code spans, a citation in this house is a
backticked path, so the check deleted every citation before looking for one.
A plant proves a guard fires on a defect; only clean prose proves it passes
compliance.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_release_notes.py"


def _run(note_text: str, tmp_path: Path) -> subprocess.CompletedProcess:
    f = tmp_path / "note.md"
    f.write_text(note_text, encoding="utf-8")
    return subprocess.run([sys.executable, str(CHECKER), str(f)],
                         capture_output=True, text=True)


def test_an_uncited_united_quantity_is_refused(tmp_path):
    r = _run("A heading line.\n\n"
             "The fit assumes a waist of 65 um and the limit falls.\n",
             tmp_path)
    assert r.returncode == 1, r.stdout
    assert "N3" in r.stdout


def test_a_cited_quantity_in_a_backticked_path_passes(tmp_path):
    """The false-positive direction: the citation IS a backticked path."""
    r = _run("A heading line.\n\n"
             "The effective mode area at that diameter is 0.615 um^2 in\n"
             "`results/guided_mode_tables.csv`, under the stated convention.\n",
             tmp_path)
    assert r.returncode == 0, r.stdout


def test_a_bare_count_is_not_this_rules_business(tmp_path):
    """A version, a date or an integer count carries no physical unit."""
    r = _run("A heading line.\n\n"
             "Three files were added and the release is the fourth of its "
             "line, dated this year.\n",
             tmp_path)
    assert r.returncode == 0, r.stdout

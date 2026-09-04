"""The chapter's per-entry bibliography checker refuses a capitalised title.

The checker lives under private/ and reads private/THESIS_CHAPTER.md and
private/thesis/bibliography.bib by its own path; a mirror or a clone without
them skips this test. It runs the checker on a SCRATCH tree with one entry:
matching, exit 0; the markdown title capitalised against the bib's, exit 1.
The commit that wired the checker ran this check by hand once; this test
keeps it run.
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "private" / "checks" / "check_chapter_bibliography_sync.py"

# the checker is private and absent from every public clone: the whole module skips there
pytestmark = pytest.mark.skipif(not CHECKER.exists(), reason="the chapter checker is private and absent here")

BIB = """@article{biraben1979,
  author  = {Biraben, F. and Bassini, M. and Cagnac, B.},
  title   = {Line-shapes in {D}oppler-free two-photon spectroscopy. The effect of finite transit time},
  journal = {J. Phys. (Paris)}, volume = {40}, number = {5},
  pages   = {445--455}, year = {1979},
}
"""
MD_OK = """# A chapter

## References

1. F. Biraben, M. Bassini and B. Cagnac, *Line-shapes in Doppler-free two-photon spectroscopy. The effect of finite transit time*, J. Phys. (Paris) 40, 445-455 (1979).
"""
MD_CAPITALISED = MD_OK.replace("Line-shapes in Doppler-free two-photon spectroscopy. The effect of finite transit time",
                               "Line-Shapes in Doppler-Free Two-Photon Spectroscopy. The Effect of Finite Transit Time")


def _run(tmp_path: Path, md: str) -> int:
    tree = tmp_path / "tree"
    (tree / "private" / "checks").mkdir(parents=True)
    (tree / "private" / "thesis").mkdir(parents=True)
    shutil.copy(CHECKER, tree / "private" / "checks" / CHECKER.name)
    (tree / "private" / "THESIS_CHAPTER.md").write_text(md)
    (tree / "private" / "thesis" / "bibliography.bib").write_text(BIB)
    r = subprocess.run([sys.executable, str(tree / "private" / "checks" / CHECKER.name)], capture_output=True, text=True)
    return r.returncode


def test_a_matching_entry_passes(tmp_path):
    assert _run(tmp_path, MD_OK) == 0


def test_a_capitalised_title_is_refused(tmp_path):
    assert _run(tmp_path, MD_CAPITALISED) == 1

"""Every results file is described where a reader lands, and vice versa.

Written 2026-08-11 after a count found FOURTEEN of the forty-six committed
result files with no entry in results/README.md. Eleven of those had been
undescribed for weeks and three were added the same day, which is the shape of
the failure: the index is written when a directory is tidied and not when a file
is added, so it drifts one producer at a time and nothing says so.

Both directions matter. A file with no entry is a file a reader cannot use. An
entry with no file is a reader sent looking for something that is not there,
which is worse, because it survives a deletion.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "results" / "README.md"


def _committed():
    return {p.name for p in (ROOT / "results").glob("*.csv")}


def test_every_results_file_is_described_in_the_index():
    text = INDEX.read_text(encoding="utf-8")
    missing = sorted(c for c in _committed() if c not in text)
    assert not missing, (
        "these result files have no entry in results/README.md, so a reader "
        "who opens the directory cannot tell what they are:\n  "
        + "\n  ".join(missing))


def test_the_index_names_no_file_that_is_not_there():
    text = INDEX.read_text(encoding="utf-8")
    named = set(re.findall(r"`([A-Za-z0-9_]+\.csv)`", text))
    committed = _committed()
    # the index legitimately discusses two files it does not hold: the manifest
    # lives in data_raw/, and one prose passage names a file by its OLD name
    # inside a dated correction, which is a record and not a pointer
    named -= {"MANIFEST.csv"}
    phantom = sorted(n for n in named if n not in committed)
    assert not phantom, (
        "results/README.md names files that are not in results/:\n  "
        + "\n  ".join(phantom))


SCRIPTS_INDEX = ROOT / "scripts" / "README.md"


def test_every_script_is_described_in_its_index():
    """The same drift, one directory over.

    Three of the sixty-one scripts had no entry when this was written, and one
    of them was the release-notes checker, which is the tool that guards prose
    nothing else guards. A tool nobody can find is a tool nobody runs.
    """
    text = SCRIPTS_INDEX.read_text(encoding="utf-8")
    missing = sorted(p.name for p in (ROOT / "scripts").glob("*.py")
                     if p.name not in text and p.stem not in text)
    assert not missing, (
        "these scripts have no entry in scripts/README.md:\n  "
        + "\n  ".join(missing))

"""Every test that reads the raw traces skips on the trace directory, so the public
mirror, which holds the manifest and not the traces, skips it instead of failing it.

FAILURE MODE IF THIS FILE IS DELETED: a test that calls a trace loader can pass in the
archive and fail on the mirror on its first file (2026-09-14: two determinism plants held
a port for a wave), and nothing says so until the mirror's own suite runs.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# THE POPULATION IS THE LOADER CALLS, not the word data_raw: twenty-one modules name the
# directory in a string or a manifest test and run on the mirror; six call a loader.
NAMES = re.compile(r"canonical_traces\(|load_trace\(|trace_path\(")
SKIP = re.compile(r"pytest\.skip|skipif|pytest\.mark\.skip|importorskip|requires_raw_traces|_raw_traces_present|is_dir\(\)")
ALLOWED = {
    # modules whose reference to the traces is a string in a message or an assertion about
    # the manifest alone; each names why
    "test_data_dependent_tests_skip.py": "this guard",
    "test_qc.py": "loads traces it writes itself under tmp_path, never the archive's",
    "test_tutorial_notebook_runs.py": "loads the example trace that ships inside the package (rb5s6s/data), not the archive's",
}


def test_every_trace_reading_test_module_skips_on_the_directory():
    bad = []
    for p in sorted((ROOT / "tests").glob("test_*.py")):
        if p.name in ALLOWED:
            continue
        text = p.read_text(encoding="utf-8")
        if NAMES.search(text) and not SKIP.search(text):
            bad.append(p.name)
    assert not bad, ("these test modules read the traces and never skip on their absence; add a skip on "
                     "the trace directory (the mirror holds the manifest and not the traces): " + ", ".join(bad))

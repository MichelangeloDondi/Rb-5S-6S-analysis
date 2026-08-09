"""
Pytest configuration: the ``slow`` marker and ``--runslow`` gate.

A handful of closure tests carry the statistical weight of the whole suite:
the full-campaign synthetic global-fit recoveries and the transit Monte-Carlo
scaling/convergence checks. They need large trace counts and 10^5 MC atoms to
be *thorough* rather than *flaky*, so they dominate the wall-clock (~90 s of a
~105 s run).

Under-sampling them would trade rigor for speed and invite intermittent
failures on the very tests meant to certify correctness, so instead they are
marked ``slow`` and skipped by default (93 fast tests, ~20 s, vs the full
101 at ~105 s). **CI always runs them** (``pytest --runslow``, see
``.github/workflows/tests.yml``), so full statistical coverage is never lost.
It just moves off the inner loop. Every module still keeps at least one fast
test in the default run, so no code path goes completely unexercised locally.

Run the full suite locally with:  ``pytest --runslow``
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run the slow, high-statistics closure tests (CI always does)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip_slow = pytest.mark.skip(
        reason="high-statistics closure test; run with --runslow (CI does)"
    )
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# --------------------------------------------------------------------------
# Raw-trace availability
# --------------------------------------------------------------------------
# The public repository ships the analysis, the committed results, the
# figures and the dataset's MANIFEST (filenames, conditions, md5s) -- but not
# the 297 raw traces themselves, which are held and available on request.
# A handful of tests verify the traces byte-for-byte against that manifest;
# they are meaningful only where the traces are present, so they SKIP rather
# than fail when they are not. Everything that certifies the analysis itself
# -- the synthetic injection-recovery closures, the coverage study, the
# transit-kernel asymptotics, every physics and statistics test -- runs
# regardless, because none of it needs the archive.
from pathlib import Path as _Path

import pytest as _pytest

_RAW = _Path(__file__).resolve().parents[1] / "data_raw"


def raw_traces_available() -> bool:
    """True when the raw trace files (not just the manifest) are present."""
    return any(_RAW.glob("**/*.csv")) and any(
        p.name != "MANIFEST.csv" for p in _RAW.glob("**/*.csv"))


requires_raw_traces = _pytest.mark.skipif(
    not raw_traces_available(),
    reason="raw traces not in this checkout (held privately, available on "
           "request); the manifest, results and analysis tests still run",
)

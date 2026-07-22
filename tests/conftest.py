"""
Pytest configuration: the ``slow`` marker and ``--runslow`` gate.

A handful of closure tests carry the statistical weight of the whole suite —
the full-campaign synthetic global-fit recoveries and the transit Monte-Carlo
scaling/convergence checks. They need large trace counts and 10^5 MC atoms to
be *thorough* rather than *flaky*, so they dominate the wall-clock (~90 s of a
~105 s run).

Rather than under-sample them (which trades rigor for speed and invites
intermittent failures on the very tests meant to certify correctness), they
are marked ``slow`` and skipped by default (93 fast tests, ~20 s, vs the full
101 at ~105 s). **CI always runs them** (``pytest --runslow``, see
``.github/workflows/tests.yml``), so full statistical coverage is never lost —
it just moves off the inner loop. Every module still keeps at least one fast
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

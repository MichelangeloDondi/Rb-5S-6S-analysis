#!/usr/bin/env bash
# The pre-push gate: exactly what CI runs, in CI's order, so a push can
# only turn red for a reason this machine could not have seen (an OS or
# dependency difference), never for one it could. The archive repository
# has no working CI of its own, so on the mirror this script is the only
# lint and the only slow battery that runs before the public one.
#
#   bash scripts/ci_gate.sh          # from either repository's root
#
# Mirrors .github/workflows/tests.yml: the lint job, then the full test
# battery with the slow closure tests, on this environment's python.
set -euo pipefail
cd "$(dirname "$0")/.."
# The checkout's own interpreter where there is one, the ambient python
# otherwise, which is the case in CI. Hard-coding either breaks the other:
# the bare python3 on a development machine need not carry ruff or pytest.
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
"$PY" -m ruff check rb5s6s scripts tests
"$PY" -m pytest -q --runslow
echo "ci_gate: clean"

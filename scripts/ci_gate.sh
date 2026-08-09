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
# A checkout that does not itself track the raw traces must not be able to
# reach them from anything a push would carry. On 2026-08-09 the public clone
# still had the archive registered as a remote, from an interrupted port, and
# 192 traces were reachable through its tracking refs. Two local backup tags
# kept them alive after that remote was dropped. Nothing had been pushed, but
# `git push --tags`, `--all` or `--mirror` would have published data this
# repository deliberately withholds. The check configures itself: where HEAD
# tracks the traces, as the working repository does, it says so and moves on.
if git rev-parse --git-dir >/dev/null 2>&1; then
  if git ls-files --error-unmatch data_raw/p_sweep >/dev/null 2>&1; then
    echo "ci_gate: this checkout tracks the raw traces, reachability check skipped"
  else
    reach=$(git rev-list --all --objects 2>/dev/null \
      | grep -cE 'data_raw/(p_sweep|t_sweep|rulers_|discarded|quarantine)/' || true)
    if [ "${reach:-0}" -gt 0 ]; then
      echo "ci_gate: FAIL. $reach raw-trace paths are reachable from a ref in a" >&2
      echo "  checkout that does not track them. Find the ref with:" >&2
      echo "    git for-each-ref --format='%(refname)' | while read r; do" >&2
      echo "      git ls-tree -r --name-only \$r | grep -q data_raw/p_sweep/ && echo \$r; done" >&2
      echo "  Then drop it and run: git reflog expire --expire=now --all && git gc --prune=now" >&2
      exit 1
    fi
    echo "ci_gate: no raw-trace path reachable from any ref"
  fi
fi
"$PY" -m ruff check rb5s6s scripts tests
"$PY" -m pytest -q --runslow
echo "ci_gate: clean"

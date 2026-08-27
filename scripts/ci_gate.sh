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
# THE VERDICT SENTINEL, and why a habit was not enough. Protocol rule 19.24
# says to read the exit code of the gate itself. On 2026-08-15 that rule was
# broken three times in one evening by callers of the form
#   ./scripts/ci_gate.sh > log; echo "EXIT: $?"
# which reports the echo's status, and once more in the other direction by
#   ./private/check_invariants.py | tail -3
# which reports tail's. Both read green over a red run. A shell construct
# placed after the command replaces its status, so no amount of care at the
# call site fixes this: the verdict has to live somewhere a later command
# cannot overwrite.
#
# So the gate writes its own verdict to a file, as its last act, on every
# path out including a crash. RUNNING is written first, so an interrupted
# gate reads as RUNNING and never as a pass. Read this file, not $?.
# THE GATE LOCK, and why a convention was not enough. Sibling sessions edit
# these same two trees, and the standing rule "never start a gate while
# another session's gate runs" lived only in each session's head. Two gates on
# one checkout share a verdict file and a working tree, so the second one's
# RUNNING erases the first one's result and each reads the other's tree
# mid-edit. The rule is mechanised here instead: an exclusive lock, taken
# BEFORE the verdict file is touched, so a refused gate cannot clobber the
# verdict of the gate it was refused for.
#
# mkdir rather than flock: the flock binary is absent on macOS and this script
# also runs in Linux CI, while mkdir is atomic on every POSIX filesystem and
# needs nothing installed. The lock lives outside the tree so it is never a
# tracked file, and it is keyed by the checkout's own path so the archive and
# the mirror lock independently. A lock whose owner is gone is stolen rather
# than waited on, which is what makes a killed gate recoverable.
GATE_LOCK="${CI_GATE_LOCK_DIR:-/tmp/rb5s6s_ci_gate$(pwd | tr '/' '_').lock}"
if ! mkdir "$GATE_LOCK" 2>/dev/null; then
  owner=$(cat "$GATE_LOCK/pid" 2>/dev/null || echo "")
  if [ -n "$owner" ] && kill -0 "$owner" 2>/dev/null; then
    echo "ci_gate: REFUSED, a gate is already running on this checkout (pid $owner)."
    echo "ci_gate: wait for it, or read its verdict file. Nothing was touched."
    exit 3
  fi
  echo "ci_gate: stale lock from pid ${owner:-unknown}, taking it over"
  rm -rf "$GATE_LOCK" && mkdir "$GATE_LOCK"
fi
printf '%s\n' "$$" > "$GATE_LOCK/pid"
trap 'rm -rf "$GATE_LOCK"' EXIT

GATE_VERDICT="${CI_GATE_VERDICT_FILE:-$(pwd)/.ci_gate_verdict}"
printf 'RUNNING\n' > "$GATE_VERDICT"
trap 'rc=$?; if [ "$rc" -eq 0 ]; then printf "PASS 0\n" > "$GATE_VERDICT";
      else printf "FAIL %s\n" "$rc" > "$GATE_VERDICT"; fi; rm -rf "$GATE_LOCK"' EXIT
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
      | grep -cE 'data_raw/(p_sweep|t_sweep|rulers_|discarded|excluded)/' || true)
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
# The protocol citation checker was written to catch the one propagation
# failure a grep of a claim cannot see, because the claim IS a pointer, and
# it had never been wired into the gate: it ran when someone remembered to
# run it. Skipped where private/ is absent, which is every clone but this one.
if [ -f private/checks/protocol_citations.py ]; then
  "$PY" private/checks/protocol_citations.py || exit 1
fi
# The board ledger, wired for the same reason and after the same finding.
# LOGIC 0c says five adversarial seats read the staged diff before every
# commit. The ledger that measures it was written, shipped, and called by
# NOTHING -- in the very commit whose best content was a docstring recording
# that the results annotator's deliberate KeyError had fired for nobody
# because nothing ever called it. Two dead guards, twenty-five lines apart.
# A guard that nothing calls is not a guard, so it is called here.
if [ -f private/checks/board_ledger.py ]; then
  "$PY" private/checks/board_ledger.py --verify || exit 1
fi
# The enforcement report is a REPORT and not a gate: it prints one line per
# standing owner rule and does not decide anything, so its exit code is not
# consulted. It runs here so the verdict a terminal state quotes is the
# verdict of the tree that just passed, rather than one remembered from
# earlier in the session.
if [ -f private/checks/enforcement_report.py ]; then
  "$PY" private/checks/enforcement_report.py || true
fi
echo "ci_gate: clean"

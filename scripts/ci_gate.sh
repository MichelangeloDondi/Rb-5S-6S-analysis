#!/usr/bin/env bash
[ -n "${BASH_VERSION:-}" ] || exec /bin/bash "$0" "$@"
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

# The verdict file is anchored to the MAIN checkout's root -- the parent
# of the common git dir -- which from a linked worktree is the main tree
# and from the main tree is itself, so the gate and the ledger can never read
# different files (the first form used --show-toplevel, which in a
# worktree IS the worktree, and its comment claimed the repair this line
# actually makes). The second line records the index tree at gate start;
# the ledger refuses a verdict stamped for any other tree.
GATE_COMMON="$(git rev-parse --git-common-dir 2>/dev/null || echo .git)"
GATE_ROOT="$(cd "$(dirname "$GATE_COMMON")" && pwd)"
GATE_VERDICT="${CI_GATE_VERDICT_FILE:-$GATE_ROOT/.ci_gate_verdict}"
GATE_TREE="$(git write-tree 2>/dev/null || echo unknown)"
# THE TARGETED FLOOR (owner redesign 2026-08-31, workflow v2). The gate is
# the certification instrument, spent once per wave on the final tree; the
# iteration instrument is scripts/targeted.sh, which stamps .targeted_ok
# with the tree it graded. A gate started without a matching stamp is a
# gate spent re-finding what seconds already find, so it refuses unless
# CI_GATE_SKIP_TARGETED carries a stated reason (a docs-only mirror run,
# an emergency re-certification): the reason is echoed into the gate's
# own log line rather than silently accepted.
if [ -n "${CI_GATE_SKIP_TARGETED:-}" ]; then
  echo "ci_gate: targeted floor SKIPPED, reason: $CI_GATE_SKIP_TARGETED"
elif [ ! -f "$GATE_ROOT/.targeted_ok" ] || ! grep -q "^tree $GATE_TREE$" "$GATE_ROOT/.targeted_ok"; then
  echo "ci_gate: REFUSED, no targeted pass stamped for this tree."
  echo "ci_gate: run scripts/targeted.sh first (seconds; on a fresh port or"
  echo "ci_gate: clean tree: git add -A, then targeted -- an unmapped change"
  echo "ci_gate: set stamps NOMODULES and this gate proceeds; scripts/README"
  echo "ci_gate: is the authority). Or set"
  echo "ci_gate: CI_GATE_SKIP_TARGETED=\"<reason>\" to certify without it."
  exit 4
fi
# The chimera sentinel's digest: a gate grades ONE tree. `git diff HEAD`
# hashes the CONTENT of staged and unstaged changes to tracked paths, so
# a second edit to an already-dirty file moves it; untracked files ride
# by NAME (an arrival or a departure moves it, an edit inside one does
# not). A MODIFIED tracked file that is then staged leaves this digest
# alone (its content was already counted) and is caught downstream
# instead: the ledger refuses any verdict stamped for a tree other than
# the one it grades (the tree line below); a NEW file staged mid-gate
# moves both halves and fails honestly here. results/
# is NOT special-cased: the freshness stage restores it byte-identically
# before the end recompute, so its by-design mutation never trips this,
# while a hand edit under the gate -- one half of the class that has
# shipped damage twice -- now does. The killed-restore half stays
# outside this bracket: a killed gate never reaches the end recompute,
# a later gate sees the damage at both ends, and the git status
# results/ reflex remains that half's only cover.
gate_dirty_digest() {
  { git diff HEAD -- .; git ls-files -o --exclude-standard; } | git hash-object --stdin
}
printf 'RUNNING\ntree %s\n' "$GATE_TREE" > "$GATE_VERDICT"
# The ONE exit trap for the rest of the script: any exit that leaves the
# first line at RUNNING writes FAIL with the real rc. PASS and
# PASS_MODULO have exactly one author, the explicit write at the end of
# the script, which runs only after every stage completed; the trap
# leaves finished verdicts alone. A single trap installed once is the
# whole design - bash keeps one EXIT trap, and an earlier version
# installed a second one further down, leaving this span's writer dead
# while a test still graded it.
trap 'rc=$?; if [ "$(head -n1 "$GATE_VERDICT" 2>/dev/null)" = "RUNNING" ]; then printf "FAIL %s\ntree %s\n" "$rc" "$GATE_TREE" > "$GATE_VERDICT"; fi; rm -rf "$GATE_LOCK"; { [ -n "${GATE_PYLOG:-}" ] && rm -f "$GATE_PYLOG"; } || true' EXIT
# Computed AFTER the trap is armed: a git failure inside the digest
# aborts through the trap and writes FAIL, instead of dying with the
# previous gate's verdict still on disk.
GATE_DIRTY_START="$(gate_dirty_digest)"
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
# THE REGISTER-AWARE VERDICT (LOGIC 0e.1). The decision lives in
# scripts/compute_gate_verdict.py - a tested python module, because a
# shell implementation of this decision is unreviewable by reading and
# the first one shipped dead under pipefail. PASS_MODULO does NOT exit here: the
# downstream stages always run, and the final verdict is written at the
# end of the script, so the register can never excuse the checkers.
GATE_PYLOG="$(mktemp)"
set +e
"$PY" -m pytest -q --runslow 2>&1 | tee "$GATE_PYLOG"
PYRC=${PIPESTATUS[0]:-$?}
set -e
# The module is invoked on every run, green included, so "rc 0 means
# PASS" is encoded in exactly one place. Only the first word of its
# output is matched: a partial line plus the fallback FAIL can never
# smuggle FAIL into PMOD.
GV=$("$PY" scripts/compute_gate_verdict.py "$PYRC" "$GATE_PYLOG" || echo FAIL)
read -r GVWORD GVREST <<< "$GV"
PMOD=""
case "$GVWORD" in
  PASS) ;;
  PASS_MODULO)
    PMOD="$GVREST"
    echo "ci_gate: every failure matches register entries ${PMOD} - continuing to the downstream stages, verdict PASS_MODULO at the end"
    ;;
  *)
    # Never exit 0 from this arm: with a green suite and an unusable
    # verdict module, exit "$PYRC" was exit 0 -- downstream checkers
    # skipped and the shell status green. The sentinel plants exactly
    # that input.
    if [ "$PYRC" -ne 0 ]; then exit "$PYRC"; fi
    echo "ci_gate: the verdict module is unusable on a green suite" >&2
    exit 1
    ;;
esac
# The protocol citation checker was written to catch the one propagation
# failure a grep of a claim cannot see, because the claim IS a pointer, and
# it had never been wired into the gate: it ran when someone remembered to
# run it. Skipped where private/ is absent, which is every clone but this one.
# The governance layer lives at the MAIN checkout. From a checkout that
# cannot reach it, skipping the four governance stages silently would
# print "clean" while grading nothing (the worktree blind region, three
# faces) -- so absence of the layer where it is EXPECTED is a refusal,
# and only a checkout with no private/ anywhere (CI, the mirror, a
# stranger's clone) passes through with the stages honestly not applicable.
if [ -d "$GATE_ROOT/private/checks" ] && [ ! -f private/checks/protocol_citations.py ]; then
  echo "ci_gate: FAIL. The governance layer exists at $GATE_ROOT but this" >&2
  echo "  checkout cannot reach it; a gate here would skip four stages." >&2
  exit 1
fi
if [ -f private/checks/protocol_citations.py ]; then
  "$PY" private/checks/protocol_citations.py || exit 1
fi
# Every literal a results/ cell held anywhere in the unpushed range is
# grepped for, which is the complement of check_references.py's population:
# that one resolves numbers carrying a ref: tag, so a plain typed copy is
# outside it. A wave on 2026-08-28 corrected every tagged copy of eighteen
# moved values and left the untagged ones standing on a campaign chapter, in
# a correction record and in four docstrings.
#
# WHAT IT DOES NOT CATCH, stated here because this comment claimed a
# detection of 1.00 until the rewrite's plant refuted it: a number that never
# matched the CSV in the first place. Two of the CSVs whose stale copies an
# audit found on 2026-08-29 did not exist at origin/main, so nothing in them
# had moved. That class is the ref: tag's, not this script's.
#
# EXIT 2 IS NOT A CLEAN BILL. It means the script could not run -- an
# unresolvable base, or no CSV carrying a `value` column -- and collapsing it
# with 1 was reported by a reader as a real confusion: a gate that dies on a
# usage error and a gate that found a defect should not read alike.
if [ -f scripts/check_moved_values.py ]; then
  _mv=0
  "$PY" scripts/check_moved_values.py "origin/main" || _mv=$?
  if [ "$_mv" = 2 ]; then
    echo "ci_gate: check_moved_values could not run (exit 2). That is not a"
    echo "         clean result; it compared nothing."
    exit 1
  elif [ "$_mv" != 0 ]; then
    exit 1
  fi
fi
# The commit-coverage ledger, wired for the same reason and after the same
# finding. LOGIC 0c says the staged diff is read (REQUIRED_SEATS sizes the
# team that reads) before every
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
# consulted. Its gate row always quotes this run's own RUNNING pre-write
# (the verdict file is rewritten before any stage runs), so inside a gate
# that row is red by construction; the row that describes this gate is
# read from the NEXT invocation, or from the verdict file directly.
# The cold-start summary must agree with the primary records it restates.
# Added 2026-08-28 after a cold-start reading found the summary claiming four ledger
# refusals where the ledger held five. It exits 1 on drift AND on a check that
# stopped matching its claim, so a reworded file cannot pass by going vacuous.
# `|| true` for the same reason the report has it: a stale summary blocks a
# terminal-state declaration, not a push.
if [ -f private/checks/summary_drift.py ]; then
  "$PY" private/checks/summary_drift.py || true
fi

# parse gate first, and hard: a checker that cannot parse reports nothing,
# and the advisory calls below would hide exactly that (E13). Guarded on
# the DIRECTORY, not on any one file it grades -- nesting it inside the
# enforcement_report existence test let a rename retire the gate over the
# other ten (confirmation round, 2026-09-01). Recursive so a future
# subdirectory stays in the population.
if [ -d private/checks ]; then
  "$PY" -c "import ast,glob; [ast.parse(open(f,encoding='utf-8').read(),f) for f in glob.glob('private/checks/**/*.py',recursive=True)]" \
    || { echo "ci_gate: a private/checks file does not parse"; exit 1; }
fi
if [ -f private/checks/enforcement_report.py ]; then
  "$PY" private/checks/enforcement_report.py || true
fi
# The chimera check, at the last possible moment so the digest brackets
# every stage above, not only the suite: an edit during the governance
# stages voids a verdict just as surely, and the first placement left
# them outside the bracket.
GATE_DIRTY_END="$(gate_dirty_digest)"
if [ "$GATE_DIRTY_START" != "$GATE_DIRTY_END" ]; then
  echo "ci_gate: FAIL. The working tree moved while the gate ran; this" >&2
  echo "  verdict would grade a chimera. Re-run on a still tree." >&2
  exit 1
fi
echo "ci_gate: clean"

# The final verdict. The exit trap writes only FAIL-on-RUNNING, so PASS
# and PASS_MODULO have no author but this block, which is reached only
# after every stage above completed. The verdict names the register
# entries that excused the suite, or PASS, and repeats the tree line.
if [ -n "$PMOD" ]; then
  printf 'PASS_MODULO %s\ntree %s\n' "$PMOD" "$GATE_TREE" > "$GATE_VERDICT"
else
  printf 'PASS 0\ntree %s\n' "$GATE_TREE" > "$GATE_VERDICT"
fi

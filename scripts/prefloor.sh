#!/usr/bin/env bash
# THE EDIT LOOP'S GUARD, so the floor runs ONCE and green.
#
# MEASURED ON THE WAVE THAT PROMPTED THIS (2026-09-13): the floor ran FIVE times
# for 1064 seconds and returned sixteen failures, and every one of the sixteen
# was in one of six fast modules -- the prose ratchets, the hygiene banks, the
# reference graph and coverage, the history form and the agonistic ratchet. Not
# one was in the slow science set the other 175 seconds of each run grades. The
# six together cost 35 seconds on four workers.
#
# So the loop was: edit, spend 212 seconds, learn about a semicolon. Four
# prefloor runs plus one floor is 352 seconds against 1064, and the 712 seconds
# saved is four performance cores idle while a laptop re-graded a tree that had
# not changed where the failure was.
#
# This is NOT a replacement for the floor and stamps .prefloor_ok with the index tree. It is the
# cheap answer to "have I broken the prose or the docs", asked after every edit
# batch, so the floor is spent once on the tree that is actually finished.
set -u
cd "$(dirname "$0")/.." || exit 2
PY=.venv/bin/python
# TEN WORKERS unless a measured reason says fewer (the standing rule). It defaulted to FOUR on a
# ten-core machine, which is the serialising defect that rule exists to forbid, and with
# --dist loadfile and eleven modules four workers idle six cores for the whole stage.
NW="${PREFLOOR_WORKERS:-10}"

# The six that caught every failure of the prompting wave, plus the two cheap
# doc guards that grade the same surfaces. Named explicitly rather than routed,
# because routing is what let `test_reproduction_routes` run zero times.
# ONE SOURCE OF TRUTH for which modules the floor owns, shared with gate_split.py so the REDUCED GATE
# skips exactly these and no others. Two hand-kept lists of one set drift, and the drift is silent: the
# gate would either re-run what is already green or, worse, skip what nothing ran.
MODULES=()
while IFS= read -r _m; do
  case "$_m" in ''|\#*) continue ;; esac
  MODULES+=("$_m")
done < scripts/floor_modules.txt

# --plant: skip the real stages and take rc, prc and agc from PLANT_RC, PLANT_PRC, PLANT_AGC,
# writing the stamp to PLANT_STAMP instead of .prefloor_ok, so the composition and the stamp
# can be checked both ways in under a second (private/checks/analysis_guards.py runs it).
PLANT=0; [ "${1:-}" = "--plant" ] && PLANT=1
STAMP=.prefloor_ok; [ $PLANT = 1 ] && STAMP="${PLANT_STAMP:-/tmp/prefloor_plant_stamp}"
if [ $PLANT = 1 ]; then
  rc=${PLANT_RC:-0}; prc=${PLANT_PRC:-0}; agc=${PLANT_AGC:-0}
else
# THE FLOOR IS FOUR LANES AT ONCE (2026-09-25, the owner: the forty-second floor "has to be kept under 1
# minute in some way (proper parallelisation, moving tests to the slow suite, solving bugs, etc)"). Measured
# that day it took 162 s: the pytest modules 46 s, because --dist loadfile handed test_repo_hygiene's 44 s to
# ONE worker; the precheck 39 s, in two scans that were quadratic in the pages they read; the plant pool 20 s;
# and about 55 s of guards run one after another on one core, each stage waiting for the one before. Every
# stage reads the tree and none writes a file another reads, so the pytest modules, the precheck, the
# instrument plants and the guard pool now start together, the floor waits for all four, and each lane's
# output is printed whole, in the order the floor always printed it, once that lane is in.
PFTMP=$(mktemp -d "${TMPDIR:-/tmp}/prefloor.XXXXXX")
trap 'kill ${PYTEST_PID:-} ${PRECHECK_PID:-} ${PLANTS_PID:-} ${POOL_PID:-} 2>/dev/null; rm -rf "$PFTMP"' INT TERM
# THE FLOOR WRITES NOTHING IT GRADES (F534): every tracked file's (mtime, size) before the lanes, compared after them.
$PY private/checks/tree_untouched.py --snapshot "$PFTMP/tracked.json"
echo "prefloor: ${#MODULES[@]} prose and doc modules on $NW worker(s), the precheck, the instrument plants and the guard pool, at once; this is not a floor and stamps .prefloor_ok with the index tree"
# --dist worksteal and not loadfile (2026-09-25): loadfile gives a whole module to one worker, so the 21
# parametrised cases of test_repo_hygiene set the stage at 46 s; worksteal spreads them and the same 3870
# tests took 17 s. None of these modules writes a file another reads: the one that rewrote a tracked file,
# the reference graph's freshness test, now writes its fresh graph beside itself.
$PY -m pytest -q -p no:randomly -n "$NW" --dist worksteal "${MODULES[@]}" > "$PFTMP/pytest.log" 2>&1 &
PYTEST_PID=$!

# The seconds floor reads the staged tree and is a different question, so it is
# asked here too rather than left for the floor to discover.
# THE GENERATED LITERATURE VIEWS ARE CHECKED HERE (2026-09-14: nine notes left the
# bib and the index stale and only the full gate saw it)
( $PY private/checks/precheck.py
  PRE_RC=$?
  $PY scripts/build_lit_index.py --check >/dev/null 2>&1 || { echo "prefloor: docs/references.bib or docs/LITERATURE_INDEX.md is stale (run scripts/build_lit_index.py)"; PRE_RC=1; }
  exit $PRE_RC ) > "$PFTMP/precheck.log" 2>&1 &
PRECHECK_PID=$!

# THE ANALYSIS GUARDS ARE CHECKED HERE, in the forty-second set, because a guard that is
# deleted and not noticed is the same as no guard (owner, 2026-09-14: enforce through
# mechanisms). It asserts each guard is still in the file it protects and plants each one.

# EVERY INSTRUMENT PLANT, IN ONE PARALLEL POOL, UNDER ONE EXIT CODE (2026-09-24, the owner: the
# forty-second floor is clearly still problematic, fix it once for all). Measured that day: 31 plant
# files run strictly SERIALLY -- no ampersand, no wait, no pool anywhere in 270 lines -- and summed
# through 68 hand-kept shell variables, which put the floor past thirteen minutes. run_plants.py
# DISCOVERS the plants by reading each file for the flag, so a new guard cannot be built and left
# unrun (F329's class retired rather than guarded); runs them longest-first in a pool; bounds each
# with a per-plant ceiling, so one blocked plant can never hold the floor again; and prints the
# slowest, so the next time this grows the growth is in the output instead of in the wall clock.
# THE PLANTS THIS FLOOR NAMED ONE BY ONE UNTIL 2026-09-24 ARE ALL DISCOVERED THERE, and the reasons each
# was added stand here with them. So are the plants of retired_values.py and register_recurrence.py, which
# this floor ALSO ran a second time by name until 2026-09-25.
# THE TWO GUARDS OF 2026-09-15, whose plants are a second each and whose
# absence from any caller this floor grades was reported by
# tests/test_checkers_are_wired.py after its caller population was repaired.
# They ran by hand all day while their own docstrings said they were wired.
# THE HOOK'S OWN PLANT, beside the guard's (2026-09-18). `prune_hook.py` is driven by the editor's own
# before-and-after-write hooks, whose settings file is gitignored by design, so a scan of the tracked tree
# cannot see that wiring and `test_checkers_are_wired` called it an orphan -- rightly, on what it can read.
# Running its plant here makes it a guard this floor exercises every time, which is the wiring that matters,
# and the tracked copy of those settings is private/checks/claude_settings.json.
# THE SSOT TRIGGER IS ARMED IN BOTH SETTINGS COPIES AND FIRES ON EVERY EDIT of constants.py, config.py
# or a results CSV, so it propagates against the TRACKED TREE without anyone asking it to. An armed hook
# whose plant nothing runs is the shape this file exists to refuse, and its self-test costs 0.15 s.
# THE QUIESCENCE GATE THE ALARM AND ssot_hook.py NOW SHARE (owner order O36, A66 to A71, T0i):
# `safety()` is the one predicate deciding whether the tracked tree may be rewritten, and a broken
# or fail-open predicate is the exact hazard A67 found already armed. Its plant costs about twenty
# seconds on this machine, almost all of it retired_values.py's own full-repository scan, which this
# floor already pays for twice below. It is the one place this self-test runs all four real debt
# sources against the live tree, and it never stages or writes outside private/cache/.
# THE SNAPSHOT INSTRUMENT: a clone is not isolated until the isolation is asserted in the exact
# invocation, and this is what asserts it -- it copies the node cache rather than linking it and refuses
# a cache and a package at different digests, which is the defect that split 976 artefacts into three
# populations. Its plant found a stale exception on its first run (2026-09-20).
# THE SECONDS CHECK FOR PROSE, this wave's kaizen with its number: this file ran SEVEN times on the
# wave that landed as e525160c and six of the seven reds were prose the wave had just written, 504
# seconds spent learning about punctuation. prose_precheck.py asks the same guards over the paths a
# session touched, in about twelve seconds, and reads BOTH repositories because private/ is its own
# and holds most of the governed prose. Its plant costs 0.15 s and is what found that scoping defect.
# THE BINDER'S PLANT (2026-09-22). `--bind` runs at every propagation since O50, and it read a cell's
# coordinates by column name while the resolver reads them by position, so on one table it would have
# written a link the resolver cannot find. Its plant covers every table schema and cross-checks the resolver.
# THE BASH HOOK'S PLANT (2026-09-20). It refuses a kill sharing a line with its own
# identification (F239) and a long run launched from a bare shell (the wave rule). A hook
# whose plant nobody re-runs is an assertion, so the floor runs it every time.
$PY private/checks/run_plants.py > "$PFTMP/plants.log" 2>&1 &
PLANTS_PID=$!

# THE GUARDS THAT GRADE THE TREE, IN ONE BOUNDED POOL UNDER ONE EXIT CODE (2026-09-25). Each line is
# `LABEL MODE SCRIPT [ARGS]`, run by private/checks/floor_pool.py four at a time, longest first; `quiet`
# prints a guard's output only when it fails, where this floor used to send it to /dev/null and re-run the
# guard to see why. A failed guard reaches the red line below as `label code`, the pair floor_red_diff.py
# reads, so a red guard is still named one by one.
$PY private/checks/floor_pool.py --workers 4 --failed-to "$PFTMP/pool.failed" > "$PFTMP/pool.log" 2>&1 <<'GUARDS' &
# GUARD ssot: no constant GAINS a literal copy. The polarizability move of
# 2026-09-15 took twelve edits because one value had been copied as a literal
# into twelve places, and three of those were found only when their tests failed.
# A RATCHET and not a cliff: the tree already carried 130 copies when this was
# wired, so it refuses an INCREASE per constant. DELTA_ALPHA_AU is at zero and
# can never regain one.
ssot-scan           show   private/checks/ssot_guard.py --scan
ssot-binding        show   private/checks/ssot_binding_ratchet.py
# DERIVED VALUES FOLLOW THEIR SOURCE (O40). The plant proves x=3 rewrites x+5 to 8 and that a
# frozen ssot-history span is never touched; the scan then grades the live tree, so a derived
# number that stopped matching its source is red in forty seconds rather than at a reader.
ssot-derived        quiet  private/checks/ssot_derived.py --scan
# AN INVARIANCE IS ENUMERATED OR IT IS NOT CLAIMED (F243, F244). A46 said the beam does not
# enter beta_self's density slope; measured, the transit drift EXCEEDS the whole signal. No
# propagation guard can see that class, because nothing in the claim ever moved.
invariance          quiet  private/checks/invariance_guard.py
# THE ONE-GATE REFUSAL, AND THE examples/ IMPORT SMOKE (2026-09-21).
# The first lived in a wrapper nothing could reach while 74 gates ran in a day; the second
# would have caught e525160c shipping an unrunnable campaign_twin.py in under a second.
one-gate            quiet  private/checks/plant_one_gate.py
examples            quiet  private/checks/smoke_examples.py
# A BIAS IS NEVER PUBLISHED WITHOUT ITS UNCERTAINTY (O35). report.py was built to enforce it
# and had ZERO call sites; ultra_joint_closure.csv carries sixteen bias_um rows with an empty
# err. Twenty-eight are carried as a declared debt and only a NEW one reds the floor.
bias-unc            quiet  private/checks/bias_uncertainty_guard.py
# THE WAVE RUNNER'S PLANT (owner, 2026-09-19: long computations run in waves of about half an hour).
# Its refusals are the only thing standing between a future eleven-hour pool and the three losses such a
# pool causes -- the work a kill destroys, the preliminary result nobody can inspect, and the gate that
# cannot run while it holds the cores. A mechanism nothing exercises is a mechanism nobody notices
# breaking, so its self-test runs here with the others. The runner's door at the pre-wave threshold (O50):
fanout-door         quiet  private/checks/fanout.py --self-test-parse
# THE BEAM THE MONTE CARLO USES IS THE ONE THING THE KERNEL GATE CANNOT GRADE (F368, 2026-09-23):
# the model and its Monte Carlo share it, so all seven readings pass while the chord sees a bare
# Gaussian and the bench has a bore. This is the WIRING half, milliseconds -- it refuses a census
# and a codebase that disagree in either direction. The GAP itself (mean +7.5 per cent, mu2 1.9x
# and mu3 4.3x the gate's own tolerances) is a DECLARED debt measured under --measure, not a red.
# `bfp` was beam_fidelity's own plant code and the plant now runs inside run_plants.py, so
# nothing assigns it and `set -u` ABORTED HERE on every real run (2026-09-24, F456); its guarded
# consumer, which could never fire, left with the move into this pool (2026-09-25).
beam-fidelity       quiet  private/checks/beam_fidelity.py
beam-callers        quiet  private/checks/beam_callers.py
twin-callers        quiet  private/checks/twin_callers.py
mc-contract         quiet  private/checks/mc_contract.py
# O56's coverage half: the contract was wired into ONE harness and 47 of 51 that draw
# randomness and write an artefact had no manifest. Keyed on MEMBERS so a masked gain
# still refuses; the list may only shrink.
mc-coverage         show   private/checks/mc_contract.py --coverage
# the enforcement report's wave-rule row grades actual against declared (T0y); deleting the row turns this red
wave-row            show   private/checks/plant_wave_rule_row.py
# the runner FLAGS a declared job at twice its declaration and never kills it (T0z, F257); planted through the real runner
overrun             show   private/checks/plant_fanout_overrun.py
# E87's code half (V7.1): an EXPENSIVE producer whose code moved since its table was proven is owed, and an
# owed producer outside the declared set is refused; its plant is the second line
code-stale          show   private/checks/code_staleness.py
code-stale-plant    quiet  private/checks/code_staleness.py --self-test
# a members ratchet over the governance prose; the baseline may only shrink
unc-digits          show   private/checks/uncertainty_digits.py
# a results table writes its uncertainty at two significant digits, or no page can print two (owner, 2026-09-24)
results-err         show   private/checks/results_err_digits.py
# AND THE GUARD MUST GRADE THE TREE, NOT ONLY ITSELF (2026-09-16). The line above
# runs the PLANT; until today nothing ran the guard. (The plant runs in the plant lane now.) A guard wired to its own
# self-test passes for ever, which is why a 30,000-word plan could be cut to 913
# and lose 216 live claims with the floor green. --scan needs no snapshot: git
# holds the before.
prune-scan          show   private/checks/prune_guard.py --scan
# THE COVERAGE METER, and it is a RATCHET and not a refusal: the covered
# fraction is 6.2 per cent, so refusing on it would block every commit and a
# guard that must be bypassed to work is not a guard. What it refuses is the
# fraction FALLING, which is what a wave that adds prose and cites nothing does.
coverage            show   private/checks/ssot_coverage.py
# THE DEPENDENCY HALF OF THE SSOT, and it is a REFUSAL and not a ratchet: a
# constant may not move without every producer whose import closure reads it
# regenerating in the same commit. This is the class a value sweep cannot
# reach, because a cell computed from a constant need never have spelled it.
deps                show   private/checks/ssot_deps.py
# A FILENAME IS A VALUE (2026-09-16). The 297-trace rename left seventy dangling
# names in four documents and nothing mentioned them; the dependency guard watches
# numbers and freshness watches producers, and prose was covered by neither.
trace-names         show   private/checks/trace_names.py
# AND A SET POINT IS NOT A TEMPERATURE: the record says two variac labels have
# already been taken for readings, and the rename made that error permanent if made.
variac              show   private/checks/variac_guard.py
# AND NOTHING REACHES THE REAL TRACES EXCEPT THROUGH THE LADDER (owner, 2026-09-15,
# restated 2026-09-16). `rb5s6s/ladder_gate.py` has carried that refusal since the
# 15th and NOTHING IMPORTED IT; `noise_ladder_gate.py` scanned one cache directory
# of a phase that had ended and no floor ran it, so the rule had a refusal nobody
# called and a scanner grading nothing. It reported zero offenders for a week and
# there were eleven. Wired here, scoped to the committed producers plus the one
# declared live phase, with a members-not-counts ratchet of what predates it.
noise-ladder        show   private/checks/noise_ladder_gate.py
# a NEW ledger or plan paragraph quoting a number names its artefact, page or finding (v4 M4)
finding-evidence    show   private/checks/finding_evidence.py
# every hook command starts from a worktree too: in a desktop-app worktree
# session they did not, so every hook refusal was silently off (2026-09-24)
hook-paths          show   private/checks/hook_paths.py
ssot-literals       show   private/checks/ssot_literals.py
ssot-quotations     show   private/checks/ssot_quotations.py
main-aim            show   private/checks/main_aim_guard.py
# the headings in the register a thesis uses (O26)
headings            show   private/checks/heading_register.py
# paragraphs a reader can finish (O26)
walls               show   private/checks/prose_walls.py
# bold pseudo-headings, the register the heading guard cannot see (O26)
bold-hooks          show   private/checks/bold_hooks.py
# a governance stamp ahead of its own file's mtime was typed, not read
stamp-sanity        show   private/checks/stamp_sanity.py
# a results table carrying a FAILED stop-class gate its producer refused to stand behind
stop-class          show   private/checks/stop_class_gate.py
# a declared constant inside a freshness EXCLUSION, which is where E81 hid for a month
uncovered-constants show   private/checks/uncovered_constants.py
# the plan's word count read, a heading the plan has marked as replaced and older than two commits refused
plan-prune          show   private/checks/plan_prune_debt.py
# a shell throttle counting jobs from a subshell, which launched 164 Python processes into a kernel panic (F93)
fanout-scan         show   private/checks/fanout.py --scan
# a second definition of a window set (owner 2026-09-19: solve the SSOT issue once for all)
window-ssot         show   private/checks/window_ssot.py
# THE RESULTS PAGE IS ITS GENERATOR'S OUTPUT (O59 S2, F537): regenerated to a temporary file and compared, so a hand
# edit, or a table that moved without its page, is refused here and not by a reader
results-page        show   private/checks/results_page_fresh.py
# a retired value outside private/history/, anywhere in the repository (owner, 2026-09-17: "strictly in the
# history folder"); its plant runs with the others
retired-values      show   private/checks/retired_values.py
GUARDS
POOL_PID=$!

wait $PYTEST_PID; rc=$?
cat "$PFTMP/pytest.log"
# GUARD prefloor-exit-code: the stage's result is PRE_RC, never `$?` of the `||` compound
# above, which is 0 whenever the recovery branch ran (2026-09-15: `prc=$?` read that
# compound, so precheck and the literature index could both fail and the floor still
# stamped GREEN on a tree the gate failed). Since 2026-09-25 PRE_RC is the precheck lane's
# own exit, which carries the literature index's refusal too.
wait $PRECHECK_PID; PRE_RC=$?
cat "$PFTMP/precheck.log"
prc=$PRE_RC
wait $PLANTS_PID; plants=$?
cat "$PFTMP/plants.log"
[ $plants = 0 ] || echo "prefloor: an instrument plant FAILED above -- re-run one with: .venv/bin/python private/checks/run_plants.py --only <file>"
# `agc` is set ONLY on the --plant path since the analysis-guard stage was folded into
# run_plants.py, so the real path left it unbound and `set -u` ABORTED THE FLOOR HERE --
# every stage below this line stopped being graded and the run ended without a verdict.
# ALL_RC already reads it as ${agc:-0}; this consumer must too (2026-09-24, F456).
[ ${agc:-0} = 0 ] || echo "prefloor: an analysis guard is missing or its plant failed (see above)"
wait $POOL_PID; grd=$?
cat "$PFTMP/pool.log"
poolfail=$(cat "$PFTMP/pool.failed" 2>/dev/null)
[ $grd = 0 ] || echo "prefloor: a guard FAILED above (${poolfail:-see the output of the pool above}) -- re-run one alone by the SCRIPT on its line"
# THE CONTROL PHASE IS READ AT EVERY FLOOR AND FAILS NOTHING: register_recurrence.py names the register's
# classes that fired more than once, which is the one distinction the c-chart rule draws (a recurrence is
# attributable, a movement is not). It is a reading for a person and deliberately not a refusal, because
# making the act of writing a class down expensive would stop classes being written at all.
$PY private/checks/register_recurrence.py --top 4 2>/dev/null | head -3 || true
# A check that wrote a tracked file raced every other lane and the gate beside the reading stage, and two did on the day the
# lanes went concurrent, one of them restoring its bytes in a `finally` (F534). Any tracked file that moved is named.
$PY private/checks/tree_untouched.py --compare "$PFTMP/tracked.json"; ttc=$?
rm -rf "$PFTMP"
trap - INT TERM
fi   # end of the real stages; a plant supplies rc, prc and agc instead

# EVERY COMPUTED EXIT CODE IS IN THE VERDICT (F329, 2026-09-22): nine codes of the six mechanisms of 2026-09-21 were
# computed and printed and summed nowhere, so any of them could fail on a GREEN floor, and the invariance scan was
# failing when this was found. The guard reads this file's own assignments against the sum below.
$PY private/checks/prefloor_sum_guard.py; psg=$?
# AN OUTPUT WRITTEN BEFORE ONE OF ITS OWN INPUTS (plan A137(b), F326, F328): the plant runs here, and the scan itself
# is read at the landing before the annotator, where its candidates are explained one by one.
# A MESSAGE TO ANOTHER SESSION NEVER CARRIES A RETIRED VALUE (plan v5.5 A151(a), RT59): the hook's plant.
# THE RED THAT NOBODY EXPECTED IS NAMED (plan v5.5 A151(b), RT60): the plant here; the reading runs on the red line below.

# GUARD prefloor-stamp-composed: ONE result from all three stages, and the stamp is written on
# it and on nothing narrower (the guards' self-test used to sit outside this `if`, so a deleted
# guard printed GREEN and stamped while the exit code alone said otherwise, and the stamp on disk
# is what idle_audit and the landing loop read).
ALL_RC=$(( ${plants:-0} != 0 || ${agc:-0} != 0 || rc != 0 || prc != 0 || ${grd:-0} != 0 || ${psg:-0} != 0 || ${ttc:-0} != 0 ))
if [ $ALL_RC -eq 0 ]; then
  # THE FAST STAMP. A reading stage reads a tree, it does not run one, so the
  # expensive question about that tree is answered by the gate running BESIDE
  # it rather than in front of it. Making the 212-second floor the gate-keeper
  # for the reading stage put that whole expense first for nothing: measured on
  # the wave that prompted this, the fast set held every one of sixteen
  # failures. Stamped with the INDEX tree, like .targeted_ok, so a stamp cannot
  # outlive the tree it graded.
  TREE=$(git write-tree)
  # The same SHAPE as .targeted_ok, because the ledger reads a marker line and
  # then `tree <sha>`. A stamp file that merely holds a sha would be read as an
  # unmarked file and refused, which is how a mechanism wired in one place and
  # not the other reports compliance while admitting nothing.
  printf 'PREFLOOR\ntree %s\n' "$TREE" > "$STAMP"
  echo "prefloor: GREEN, stamped ${TREE:0:12}. The reading stage may open on this; the gate runs beside it."
  $PY private/checks/floor_red_diff.py "prefloor: GREEN" >/dev/null   # a green floor clears the acknowledged red set
else
  rm -f "$STAMP"
  # EVERY TERM OF ALL_RC IS PRINTED (2026-09-19): six stages rode in the sum and in no message --
  # ssot-scan, bold-hooks, stamp-sanity, stop-class, uncovered-constants and fanout-scan -- so a floor
  # red on one of them printed every stage it named as 0 and looked like an arithmetic defect. A
  # verdict line that does not name each term of its own sum is the silent collapse this repository
  # has a rule about. The plant this comment used to name, `--plant-red`, was never implemented (F329); the one that
  # holds the sum is private/checks/prefloor_sum_guard.py, which refuses an exit code computed here and summed nowhere.
  # SINCE 2026-09-25 THE GUARDS ARE ONE POOL WITH ONE CODE, and each guard that failed is named inside the line as
  # `label code`, so the line still names every stage that failed and floor_red_diff.py still tracks each by name.
  RL="prefloor: RED (pytest $rc, precheck $prc, plants ${plants:-0}, guards ${agc:-0}, guard-pool ${grd:-0}${poolfail:+, $poolfail}, sum-guard ${psg:-0}, tree-untouched ${ttc:-0}). No stamp. Fix these before anything expensive."
  echo "$RL"
  $PY private/checks/floor_red_diff.py "$RL"
fi
# THE FLOOR TIMES ITSELF (2026-09-25). The owner's budget is 60 s; this row is what idle_audit.py reads, and it
# refuses a commit when the MEDIAN of the last five real runs is past the budget, so a floor slowed once by a science
# pool beside it passes and a floor that has grown does not. A plant run records nothing.
if [ $PLANT = 0 ]; then
  echo "prefloor: ${SECONDS} s wall against the 60 s budget"
  # O59 F3: the load the floor ran beside, so the audit can read the floors that ran beside a pool apart
  LOAD1=$(sysctl -n vm.loadavg 2>/dev/null | awk '{print $2}')
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$SECONDS" "$ALL_RC" "${LOAD1:-}" >> private/cache/floor_times.tsv
fi
exit $ALL_RC

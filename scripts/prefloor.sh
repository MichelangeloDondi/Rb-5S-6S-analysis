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
echo "prefloor: ${#MODULES[@]} prose and doc guards on $NW worker(s); this is not a floor and stamps .prefloor_ok with the index tree"
$PY -m pytest -q -p no:randomly -n "$NW" --dist loadfile "${MODULES[@]}"
rc=$?

# The seconds floor reads the staged tree and is a different question, so it is
# asked here too rather than left for the floor to discover.
$PY private/checks/precheck.py
PRE_RC=$?
# THE GENERATED LITERATURE VIEWS ARE CHECKED HERE (2026-09-14: nine notes left the
# bib and the index stale and only the full gate saw it)
$PY scripts/build_lit_index.py --check >/dev/null 2>&1 || { echo "prefloor: docs/references.bib or docs/LITERATURE_INDEX.md is stale (run scripts/build_lit_index.py)"; PRE_RC=1; }
# GUARD prefloor-exit-code: the stage's result is PRE_RC, never `$?` of the `||` compound
# above, which is 0 whenever the recovery branch ran (2026-09-15: `prc=$?` read that
# compound, so precheck and the literature index could both fail and the floor still
# stamped GREEN on a tree the gate failed).
prc=$PRE_RC

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
$PY private/checks/run_plants.py; plants=$?
[ $plants = 0 ] || echo "prefloor: an instrument plant FAILED above -- re-run one with: .venv/bin/python private/checks/run_plants.py --only <file>"

# `agc` is set ONLY on the --plant path since the analysis-guard stage was folded into
# run_plants.py, so the real path left it unbound and `set -u` ABORTED THE FLOOR HERE --
# every stage below this line stopped being graded and the run ended without a verdict.
# ALL_RC already reads it as ${agc:-0}; this consumer must too (2026-09-24, F456).
[ ${agc:-0} = 0 ] || echo "prefloor: an analysis guard is missing or its plant failed (see above)"

# GUARD ssot: no constant GAINS a literal copy. The polarizability move of
# 2026-09-15 took twelve edits because one value had been copied as a literal
# into twelve places, and three of those were found only when their tests failed.
# A RATCHET and not a cliff: the tree already carried 130 copies when this was
# wired, so it refuses an INCREASE per constant. DELTA_ALPHA_AU is at zero and
# can never regain one.
$PY private/checks/ssot_guard.py --scan; ssc=$?
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
$PY private/checks/ssot_binding_ratchet.py; sbc=$?
# THE BINDER'S PLANT (2026-09-22). `--bind` runs at every propagation since O50, and it read a cell's
# coordinates by column name while the resolver reads them by position, so on one table it would have
# written a link the resolver cannot find. Its plant covers every table schema and cross-checks the resolver.
# THE BASH HOOK'S PLANT (2026-09-20). It refuses a kill sharing a line with its own
# identification (F239) and a long run launched from a bare shell (the wave rule). A hook
# whose plant nobody re-runs is an assertion, so the floor runs it every time.
# DERIVED VALUES FOLLOW THEIR SOURCE (O40). The plant proves x=3 rewrites x+5 to 8 and that a
# frozen ssot-history span is never touched; the scan then grades the live tree, so a derived
# number that stopped matching its source is red in forty seconds rather than at a reader.
$PY private/checks/ssot_derived.py --scan >/dev/null; sds=$?
# AN INVARIANCE IS ENUMERATED OR IT IS NOT CLAIMED (F243, F244). A46 said the beam does not
# enter beta_self's density slope; measured, the transit drift EXCEEDS the whole signal. No
# propagation guard can see that class, because nothing in the claim ever moved.
$PY private/checks/invariance_guard.py >/dev/null; ivg=$?
# THE ONE-GATE REFUSAL, AND THE examples/ IMPORT SMOKE (2026-09-21).
# The first lived in a wrapper nothing could reach while 74 gates ran in a day; the second
# would have caught e525160c shipping an unrunnable campaign_twin.py in under a second.
$PY private/checks/plant_one_gate.py >/dev/null; ogp=$?
$PY private/checks/smoke_examples.py >/dev/null; sme=$?
# A BIAS IS NEVER PUBLISHED WITHOUT ITS UNCERTAINTY (O35). report.py was built to enforce it
# and had ZERO call sites; ultra_joint_closure.csv carries sixteen bias_um rows with an empty
# err. Twenty-eight are carried as a declared debt and only a NEW one reds the floor.
$PY private/checks/bias_uncertainty_guard.py >/dev/null; bug=$?
# THE WAVE RUNNER'S PLANT (owner, 2026-09-19: long computations run in waves of about half an hour).
# Its refusals are the only thing standing between a future eleven-hour pool and the three losses such a
# pool causes -- the work a kill destroys, the preliminary result nobody can inspect, and the gate that
# cannot run while it holds the cores. A mechanism nothing exercises is a mechanism nobody notices
# breaking, so its self-test runs here with the others.
$PY private/checks/fanout.py --self-test-parse >/dev/null; fdp=$?   # the runner's door at the pre-wave threshold (O50)

# THE BEAM THE MONTE CARLO USES IS THE ONE THING THE KERNEL GATE CANNOT GRADE (F368, 2026-09-23):
# the model and its Monte Carlo share it, so all seven readings pass while the chord sees a bare
# Gaussian and the bench has a bore. This is the WIRING half, milliseconds -- it refuses a census
# and a codebase that disagree in either direction. The GAP itself (mean +7.5 per cent, mu2 1.9x
# and mu3 4.3x the gate's own tolerances) is a DECLARED debt measured under --measure, not a red.
$PY private/checks/beam_fidelity.py >/dev/null; bfc=$?
$PY private/checks/beam_callers.py >/dev/null; bcc=$?
$PY private/checks/twin_callers.py >/dev/null; tcc=$?
$PY private/checks/mc_contract.py >/dev/null; mcc=$?
# O56's coverage half: the contract was wired into ONE harness and 47 of 51 that draw
# randomness and write an artefact had no manifest. Keyed on MEMBERS so a masked gain
# still refuses; the list may only shrink.
$PY -c "import importlib.util,sys,pathlib;sp=importlib.util.spec_from_file_location('mc','private/checks/mc_contract.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);rc,new,paid=m.coverage_report();print('mc-coverage: %d harness(es) still outside the contract, %d paid off'%(len(m.uncovered()),len(paid)));[print('  NEW ungated: '+n) for n in new];sys.exit(rc)"; mcv=$?
# `bfp` was beam_fidelity's own plant code and the plant now runs inside run_plants.py, so
# nothing assigns it and `set -u` ABORTED HERE on every real run (2026-09-24, F456).
[ ${bfp:-0} = 0 ] || echo "prefloor: beam_fidelity's own plant failed (see --self-test)"
[ $bfc = 0 ] || $PY private/checks/beam_fidelity.py
$PY private/checks/plant_wave_rule_row.py; wrr=$?   # the enforcement report's wave-rule row grades actual against declared (T0y); deleting the row turns this red
$PY private/checks/plant_fanout_overrun.py; foc2=$?  # the runner FLAGS a declared job at twice its declaration and never kills it (T0z, F257); planted through the real runner
$PY private/checks/uncertainty_digits.py; udg=$?   # a members ratchet over the governance prose; the baseline may only shrink
# THE CONTROL PHASE IS READ AT EVERY FLOOR AND FAILS NOTHING: register_recurrence.py names the register's
# classes that fired more than once, which is the one distinction the c-chart rule draws (a recurrence is
# attributable, a movement is not). It is a reading for a person and deliberately not a refusal, because
# making the act of writing a class down expensive would stop classes being written at all.
$PY private/checks/register_recurrence.py --top 4 --self-test >/dev/null 2>&1; $PY private/checks/register_recurrence.py --top 4 2>/dev/null | head -3 || true
# AND THE GUARD MUST GRADE THE TREE, NOT ONLY ITSELF (2026-09-16). The line above
# runs the PLANT; until today nothing ran the guard. A guard wired to its own
# self-test passes for ever, which is why a 30,000-word plan could be cut to 913
# and lose 216 live claims with the floor green. --scan needs no snapshot: git
# holds the before.
$PY private/checks/prune_guard.py --scan; pgs=$?
# THE COVERAGE METER, and it is a RATCHET and not a refusal: the covered
# fraction is 6.2 per cent, so refusing on it would block every commit and a
# guard that must be bypassed to work is not a guard. What it refuses is the
# fraction FALLING, which is what a wave that adds prose and cites nothing does.
$PY private/checks/ssot_coverage.py; scc=$?
# THE DEPENDENCY HALF OF THE SSOT, and it is a REFUSAL and not a ratchet: a
# constant may not move without every producer whose import closure reads it
# regenerating in the same commit. This is the class a value sweep cannot
# reach, because a cell computed from a constant need never have spelled it.
$PY private/checks/ssot_deps.py; sdc=$?
# A FILENAME IS A VALUE (2026-09-16). The 297-trace rename left seventy dangling
# names in four documents and nothing mentioned them; the dependency guard watches
# numbers and freshness watches producers, and prose was covered by neither.
$PY private/checks/trace_names.py; tnc=$?
# AND A SET POINT IS NOT A TEMPERATURE: the record says two variac labels have
# already been taken for readings, and the rename made that error permanent if made.
$PY private/checks/variac_guard.py; vgc=$?
# AND NOTHING REACHES THE REAL TRACES EXCEPT THROUGH THE LADDER (owner, 2026-09-15,
# restated 2026-09-16). `rb5s6s/ladder_gate.py` has carried that refusal since the
# 15th and NOTHING IMPORTED IT; `noise_ladder_gate.py` scanned one cache directory
# of a phase that had ended and no floor ran it, so the rule had a refusal nobody
# called and a scanner grading nothing. It reported zero offenders for a week and
# there were eleven. Wired here, scoped to the committed producers plus the one
# declared live phase, with a members-not-counts ratchet of what predates it.
$PY private/checks/noise_ladder_gate.py; nlc=$?
$PY private/checks/finding_evidence.py; fec=$?   # a NEW ledger or plan paragraph quoting a number names its artefact, page or finding (v4 M4)
$PY private/checks/hook_paths.py; hpc=$?   # every hook command starts from a worktree too: in a desktop-app worktree
                                            # session they did not, so every hook refusal was silently off (2026-09-24)
$PY private/checks/ssot_literals.py; slc=$?
$PY private/checks/ssot_quotations.py; sqc=$?
$PY private/checks/main_aim_guard.py; mac=$?
$PY private/checks/heading_register.py; hrc=$?   # the headings in the register a thesis uses (O26)
$PY private/checks/prose_walls.py; pwc=$?          # paragraphs a reader can finish (O26)
$PY private/checks/bold_hooks.py; bhc=$?          # bold pseudo-headings, the register the heading guard cannot see (O26)
$PY private/checks/stamp_sanity.py; stc=$?        # a governance stamp ahead of its own file's mtime was typed, not read
$PY private/checks/stop_class_gate.py; sgc=$?    # a results table carrying a FAILED stop-class gate its producer refused to stand behind
$PY private/checks/uncovered_constants.py; ucc=$?  # a declared constant inside a freshness EXCLUSION, which is where E81 hid for a month
$PY private/checks/plan_prune_debt.py; ppd=$?     # the plan's word count read, a heading the plan has marked as replaced and older than two commits refused
$PY private/checks/fanout.py --scan; foc=$?
$PY private/checks/window_ssot.py; wsc=$?   # a second definition of a window set (owner 2026-09-19: solve the SSOT issue once for all)      # a shell throttle counting jobs from a subshell, which launched 164 Python processes into a kernel panic (F93)
$PY private/checks/retired_values.py; rvc=$?   # a retired value outside private/history/, anywhere in the repository (owner, 2026-09-17: "strictly in the history folder")
$PY private/checks/retired_values.py --self-test > /dev/null || rvc=1
[ $ssc = 0 ] || echo "prefloor: a canonical value gained a literal copy (see above)"
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
ALL_RC=$(( ${plants:-0} != 0 || ${agc:-0} != 0 || rc != 0 || prc != 0 || ${ssc:-0} != 0 || ${sbc:-0} != 0 || ${pgs:-0} != 0 || ${scc:-0} != 0 || ${sdc:-0} != 0 || ${tnc:-0} != 0 || ${vgc:-0} != 0 || ${nlc:-0} != 0 || ${fec:-0} != 0 || ${hrc:-0} != 0 || ${pwc:-0} != 0 || ${bhc:-0} != 0 || ${stc:-0} != 0 || ${sgc:-0} != 0 || ${ucc:-0} != 0 || ${ppd:-0} != 0  || ${foc:-0} != 0 || ${wsc:-0} != 0 || ${rvc:-0} != 0 || ${slc:-0} != 0  || ${sqc:-0} != 0 || ${mac:-0} != 0 || ${wrr:-0} != 0 || ${foc2:-0} != 0 || ${sds:-0} != 0 || ${ivg:-0} != 0 || ${ogp:-0} != 0 || ${sme:-0} != 0 || ${bug:-0} != 0 || ${psg:-0} != 0 || ${fdp:-0} != 0 || ${udg:-0} != 0 || ${bfc:-0} != 0 || ${bcc:-0} != 0 || ${mcc:-0} != 0 || ${mcv:-0} != 0 || ${tcc:-0} != 0 || ${hpc:-0} != 0 ))
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
  RL="prefloor: RED (pytest $rc, precheck $prc, guards ${agc:-0}, prior-art ${pac:-0}, prune ${pgc:-0}, prune-hook ${phc:-0}, producer-lock ${plc:-0}, ssot-hook ${shc:-0}, snapshot ${snc:-0}, prose-precheck ${ppc:-0}, ssot-binding ${sbc:-0}, ssot-bind ${sbp:-0}, bash-hook ${bhk:-0}, core-watch ${cwk:-0}, ssot-derived ${sdp:-0}/${sds:-0}, invariance ${ivp:-0}/${ivg:-0}, one-gate ${ogp:-0}, examples ${sme:-0}, bias-unc ${bup:-0}/${bug:-0}, prune-scan ${pgs:-0}, coverage $scc, deps $sdc, trace-names ${tnc:-0}, variac ${vgc:-0}, ssot-literals ${slc:-0}, ssot-quotations ${sqc:-0}, ssot-scan ${ssc:-0}, main-aim ${mac:-0}, wave-runner ${wrc:-0}, launch ${lrc:-0}, beam-fidelity ${bfp:-0}/${bfc:-0}, beam-callers ${bcp:-0}/${bcc:-0}, mc-contract ${mcp:-0}/${mcc:-0}, mc-coverage ${mcv:-0}, probe ${prb:-0}, reply-numbers ${rnb:-0}, twin-gate ${twp:-0}, twin-callers ${tcp:-0}/${tcc:-0}, wave-row ${wrr:-0}, overrun ${foc2:-0}, sum-guard ${psp:-0}/${psg:-0}, staleness-plant ${isp:-0}, message-hook ${mhp:-0}, red-diff ${frp:-0}, fanout-door ${fdp:-0}, propagate-guard ${prg:-0}, unc-digits ${udp:-0}/${udg:-0}, noise-ladder ${nlc:-0}, finding-evidence ${fec:-0}, headings ${hrc:-0}, walls ${pwc:-0}, bold-hooks ${bhc:-0}, stamp-sanity ${stc:-0}, stop-class ${sgc:-0}, uncovered-constants ${ucc:-0}, fanout-scan ${foc:-0}, window-ssot ${wsc:-0}, plan-prune ${ppd:-0}, retired-values ${rvc:-0}, plants ${plants:-0}, hook-paths ${hpc:-0}). No stamp. Fix these before anything expensive."
  echo "$RL"
  $PY private/checks/floor_red_diff.py "$RL"
fi
exit $ALL_RC

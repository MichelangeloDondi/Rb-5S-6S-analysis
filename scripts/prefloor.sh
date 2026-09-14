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
NW="${PREFLOOR_WORKERS:-4}"

# The six that caught every failure of the prompting wave, plus the two cheap
# doc guards that grade the same surfaces. Named explicitly rather than routed,
# because routing is what let `test_reproduction_routes` run zero times.
MODULES=(
  tests/test_repo_hygiene.py
  tests/test_prose_style_ratchet.py
  tests/test_references.py
  tests/test_reference_coverage.py
  tests/test_history_form.py
  tests/test_agonistic_ratchet.py
  tests/test_docs_math_render.py
  tests/test_docs_links.py
  tests/test_docstring_counts.py
  tests/test_tqm_report.py
  tests/test_lit_consistency.py
)

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
prc=$?

if [ $rc -eq 0 ] && [ $prc -eq 0 ]; then
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
  printf 'PREFLOOR\ntree %s\n' "$TREE" > .prefloor_ok
  echo "prefloor: GREEN, stamped ${TREE:0:12}. The reading stage may open on this; the gate runs beside it."
else
  rm -f .prefloor_ok
  echo "prefloor: RED (pytest $rc, precheck $prc). No stamp. Fix these before anything expensive."
fi
exit $(( rc != 0 || prc != 0 ))

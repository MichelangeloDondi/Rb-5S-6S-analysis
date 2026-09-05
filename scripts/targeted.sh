#!/usr/bin/env bash
# The iteration instrument. ci_gate.sh is the certification instrument,
# spent once per wave on the final tree; this script maps the current
# change set to the guard modules that own it, runs them in seconds,
# and stamps .targeted_ok with the index tree it graded, which the
# ledger and the gate both read. The map mirrors the pre-commit
# hook's own change-set coverage (.git/hooks/pre-commit) rather than
# inventing a second authority; a change set neither maps covers stamps
# as NOMODULES so the full gate, which runs everything, can proceed.
set -euo pipefail
[ -n "${BASH_VERSION:-}" ] || exec /bin/bash "$0" "$@"
START_DIR=$(pwd)
cd "$(dirname "$(git rev-parse --git-common-dir)")"
# From a linked worktree the common dir resolves to the MAIN checkout, so
# this instrument always grades and stamps the main tree; say so out loud
# when invoked from anywhere else, because a session editing a worktree
# would otherwise read this green as covering edits it never saw.
[ "$START_DIR" = "$(pwd)" ] || echo "targeted: grading the MAIN checkout $(pwd), not $START_DIR"
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3
# untracked files cannot reach the map: the refusal below sends them to
# git add first, so CHANGED reads only tracked changes against HEAD
# `private/` is gitignored, so a private-only edit never appears in the
# ARCHIVE's diff. That hole was documented here and left open, with the
# full gate named as the mitigation. It is not one: the gate is sixteen
# to thirty minutes, and on 2026-09-05 it spent two of those runs finding
# three prose defects and then a fourth in private/THESIS_CHAPTER.md that
# the ratchets catch in seven seconds. A thirty-minute feedback loop on a
# seven-second check is a hole, not a mitigation.
#
# private/ IS ITS OWN GIT REPOSITORY, so its diff is readable. PRIVCHANGED
# below is the governance-side change set, and the prose branch fires on
# it exactly as it fires on docs/. Nothing else about the stamp changes:
# the stamp remains the ARCHIVE's index tree, because that is what the
# gate and the ledger key on, and a private edit does not move it.
CHANGED=$(git diff --name-only HEAD | sort -u)
PRIVCHANGED=$( { git -C private diff --name-only HEAD 2>/dev/null || true; \
                 git -C private diff --cached --name-only 2>/dev/null || true; \
                 git -C private ls-files -o --exclude-standard 2>/dev/null || true; \
               } | sort -u )
# THE STAMP IS THE INDEX TREE (git write-tree), so an unstaged edit would be
# tested here and then stamped as if it were not there -- the first live run
# did exactly that: 1201 tests green, stamp naming HEAD's own tree. Stage
# first; this refusal is what makes the stamp mean what it says.
if ! git diff --quiet; then
  echo "targeted: REFUSED, unstaged changes present. git add them first --"
  echo "targeted: the stamp is the index tree, and it must cover what ran."
  exit 5
fi
if [ -n "$(git ls-files -o --exclude-standard)" ]; then
  echo "targeted: REFUSED, untracked files present. git add them first --"
  echo "targeted: an untracked file is tested here but absent from the"
  echo "targeted: stamped tree, which is the guard-population hole by"
  echo "targeted: another door."
  exit 5
fi
declare -a MODS=()
add() { for m in "$@"; do [ -f "$m" ] && MODS+=("$m") || true; done; return 0; }
# a missing module must skip, never kill: under set -e the old form died
# silently when a listed file was absent (found 2026-09-01, first live run)
grep -q '^tests/' <<<"$CHANGED" && while read -r f; do
  case "$f" in tests/*.py) add "$f";; esac; done <<<"$CHANGED" && add \
  tests/test_repo_hygiene.py tests/test_prose_style_ratchet.py \
  tests/test_agonistic_ratchet.py
# ^ a tests-only change set skipped every bank that grades test
# docstrings, in this map and the pre-commit hook alike; the first
# tests-only wave stamped a red tree green through the hole (an audit
# finding, its own commit)
# GOVERNED PRIVATE PROSE: the gate's prose banks read private/*.md, so a
# governance edit must bring the same modules here. Without this the floor
# stamps green and the gate goes red half an hour later, which is what it
# did four times on 2026-09-05.
grep -qE '\.md$' <<<"$PRIVCHANGED" && add \
  tests/test_prose_style_ratchet.py tests/test_repo_hygiene.py \
  tests/test_agonistic_ratchet.py tests/test_history_tense.py || true
grep -qE '^(docs/|README|START_HERE)' <<<"$CHANGED" && add \
  tests/test_prose_style_ratchet.py tests/test_repo_hygiene.py \
  tests/test_open_apparatus_items.py tests/test_docs_platform_lane.py \
  tests/test_docs_structure.py \
  tests/test_references.py \
  tests/test_lit_consistency.py \
  tests/test_docs_no_duplicated_blocks.py \
  tests/test_history_tense.py tests/test_docs_math_render.py \
  tests/test_docs_links.py tests/test_reference_coverage.py \
  tests/test_reader_surface_budget.py tests/test_history_form.py \
  tests/test_docs_canonical.py tests/test_prose_shape.py \
  tests/test_ramp_geometry_docs.py
grep -q '^results/' <<<"$CHANGED" && add \
  tests/test_results_status.py tests/test_freshness_covers_every_result.py \
  tests/test_distribution_ratchet.py tests/test_results_err_format.py \
  tests/test_results_index_is_complete.py tests/test_references.py \
  tests/test_figures_fresh.py tests/test_every_claim_carries_an_uncertainty.py \
  tests/test_docs_canonical.py
grep -qE '^scripts/run_|^scripts/make_' <<<"$CHANGED" && add \
  tests/test_results_index_is_complete.py tests/test_pipeline_order.py \
  tests/test_checkers_are_wired.py tests/test_repo_hygiene.py \
  tests/test_docs_canonical.py
# AND THE TEST FILES THAT LOAD THAT PRODUCER BY PATH. The branch above
# adds a fixed generic set and stops, while the rb5s6s branch below maps
# a changed module to its own test file by name. A changed producer had
# no such mapping at all, and on 2026-09-02 that cost a CRITICAL: three
# producers gained an import that broke two sibling test files at
# COLLECTION and silently defanged a third, and this script stamped
# green over 2470 passing tests without ever loading any of the three.
# Producers are not named `tests/test_<stem>.py` by convention, so the
# map is by CONTENT: a test that names the producer in a
# spec_from_file_location owns it.
grep -qE '^scripts/(run_|make_|_)' <<<"$CHANGED" && while read -r f; do
  case "$f" in scripts/*.py)
    stem="$(basename "${f%.py}")"
    while read -r owner; do add "$owner"; done < <(
      # the file list is ENUMERATED, not filtered by --include: that
      # flag let stale __pycache__/*.pyc through, and a compiled test
      # carries both strings as constants, so pytest was handed .pyc
      # paths and refused to collect anything at all
      find tests -maxdepth 1 -name 'test_*.py' -print0 2>/dev/null | xargs -0 -r grep -l -- "$stem" 2>/dev/null | xargs -r grep -l 'spec_from_file_location' 2>/dev/null)
    ;; esac
  done <<<"$CHANGED"
grep -q '^rb5s6s/' <<<"$CHANGED" && while read -r f; do
  case "$f" in rb5s6s/*.py)
    t="tests/test_$(basename "${f%.py}").py"; add "$t";; esac
  done <<<"$CHANGED" && add tests/test_constants.py
# the gate scripts, the checkers and the ledger have owning modules too
# (the pre-commit hook already covers these by name; this map inherits
# rather than diverges -- a second, narrower map was an audit finding)
grep -qE '^scripts/(ci_gate|targeted)\.sh$' <<<"$CHANGED" && add \
  tests/test_gate_verdict_sentinel.py tests/test_repo_hygiene.py
grep -qE '^scripts/check_' <<<"$CHANGED" && add \
  tests/test_checkers_are_wired.py tests/test_repo_hygiene.py
grep -q '^private/checks/' <<<"$CHANGED" && add tests/test_board_ledger.py
grep -q '^figures/' <<<"$CHANGED" && add tests/test_figures_fresh.py
grep -qE '^(pyproject\.toml|CITATION\.cff)$' <<<"$CHANGED" && add \
  tests/test_repo_hygiene.py
# assembled without a pipeline: a py-less change set made the old
# grep-fed substitution die silently under set -e on its first
# py-less run, and the caller's tail masked the status (19.24's
# class, live again)
PYFILES=""
while IFS= read -r f; do
  case "$f" in *.py) [ -f "$f" ] && PYFILES="$PYFILES $f";; esac
done <<<"$CHANGED"
if [ -n "${PYFILES// /}" ]; then
  # ruff's verdict is part of the floor: a red lint must not stamp
  # (its status was thrown away here until an audit read the line).
  "$PY" -m ruff check $PYFILES
fi
if [ "${#MODS[@]}" -eq 0 ]; then
  echo "targeted: no owning modules for this change set; the FULL gate is"
  echo "targeted: the instrument. Stamping NOMODULES so the gate can start."
  printf 'TARGETED-NOMODULES\ntree %s\n' "$(git write-tree)" > .targeted_ok
  exit 2
fi
UNIQ=$(printf '%s\n' "${MODS[@]}" | sort -u | tr '\n' ' ')
echo "targeted: $UNIQ"
"$PY" -m pytest -q -p no:randomly $UNIQ
printf 'TARGETED\ntree %s\n' "$(git write-tree)" > .targeted_ok
echo "targeted: stamped $(git write-tree | cut -c1-12)"

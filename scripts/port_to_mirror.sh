#!/bin/bash
# Wholesale measured port, archive -> mirror, tracked set to tracked set.
#
# WHY WHOLESALE: a commit-window port (the first version used HEAD~3..HEAD)
# goes stale the moment the window moves, and a copy-only port cannot carry a
# rename, which this batch has (plan/01). The tracked SETS are compared
# instead: every archive-tracked file is copied in, every mirror-tracked file
# absent from the archive set is git-rm'ed, and data_raw/ is excluded in BOTH
# directions because the two copies differ by design (the mirror ships the
# manifest and a README saying the traces are absent).
#
# PRECONDITION: the mirror worktree is CLEAN. The script refuses otherwise,
# because a port onto strays carries them forward invisibly.
set -e
A=~/Documents/GitHub/Rb-5S-6S-analysis
M=~/Documents/GitHub/Rb-5S-6S-public

cd "$M"
if [ -n "$(git status --short)" ]; then
  echo "ABORT: mirror worktree is not clean"; git status --short | head; exit 1
fi

cd "$A"
if [ -n "$(git status --short)" ]; then
  echo "ABORT: archive worktree is not clean"; git status --short | head; exit 1
fi

# the tracked sets, with the BY-DESIGN divergences excluded both ways:
# data_raw/ (the mirror ships no traces and its README says so) and
# .github/ (the mirror's workflow is the reference green check with push
# triggers, the archive's is dispatch-only; the mirror's own
# test_ci_triggers.py caught the first port that ignored this).
(cd "$A" && git ls-files | grep -v '^data_raw/' | grep -v '^\.github/') | sort > /tmp/port_src.txt
(cd "$M" && git ls-files | grep -v '^data_raw/' | grep -v '^\.github/') | sort > /tmp/port_dst.txt

n_copy=0
while IFS= read -r p; do
  mkdir -p "$M/$(dirname "$p")"
  if ! cmp -s "$A/$p" "$M/$p" 2>/dev/null; then
    cp "$A/$p" "$M/$p"; n_copy=$((n_copy+1))
  fi
done < /tmp/port_src.txt

n_del=0
while IFS= read -r p; do
  if ! grep -qxF "$p" /tmp/port_src.txt; then
    (cd "$M" && git rm --quiet "$p"); n_del=$((n_del+1))
    echo "  removed (absent from archive): $p"
  fi
done < /tmp/port_dst.txt

cd "$M"
echo "copied-or-updated: $n_copy   removed: $n_del"
echo "mirror status after port:"
git status --short | head -30
echo "... $(git status --short | wc -l | tr -d ' ') paths changed in the mirror"

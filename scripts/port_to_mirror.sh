#!/bin/bash
# Wholesale measured port, archive -> mirror, tracked set to tracked set.
#
# TWO MODES.
#   port_to_mirror.sh            apply the port (copies, removals, as before)
#   port_to_mirror.sh --check    report drift and change NOTHING, exit 1 if any
#
# WHY --check IS THE CANONICAL PARITY INSTRUMENT (2026-08-21). The other tool,
# sync_public.sh --check, detects delivery by READING COMMIT MESSAGES for
# cherry-picked hashes. Every port these repositories actually perform is a
# hand-written wholesale commit that names no hash, so that check reports gaps
# that do not exist and would keep reporting them forever. Two repositories
# with deliberately divergent histories cannot be compared by history at all.
# The only honest ground truth is CONTENT: the tracked sets, file by file,
# with the by-design divergences excluded. That is what this mode computes,
# and it is what gates the release.
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

MODE=port
if [ "${1:-}" = "--check" ]; then MODE=check; fi

# The clean-tree precondition guards the PORT (a port onto strays carries them
# forward invisibly). A check writes nothing, so it must be runnable at any
# moment, including mid-edit, which is exactly when one wants to ask it.
if [ "$MODE" = port ]; then
  cd "$M"
  if [ -n "$(git status --short)" ]; then
    echo "ABORT: mirror worktree is not clean"; git status --short | head; exit 1
  fi

  cd "$A"
  if [ -n "$(git status --short)" ]; then
    echo "ABORT: archive worktree is not clean"; git status --short | head; exit 1
  fi
fi

# the tracked sets, with the BY-DESIGN divergences excluded both ways:
# data_raw/ (the mirror ships no traces and its README says so) and
# .github/ (the mirror's workflow is the reference green check with push
# triggers, the archive's is dispatch-only; the mirror's own
# test_ci_triggers.py caught the first port that ignored this).
(cd "$A" && git ls-files | grep -v '^data_raw/' | grep -v '^\.github/') | sort > /tmp/port_src.txt
(cd "$M" && git ls-files | grep -v '^data_raw/' | grep -v '^\.github/') | sort > /tmp/port_dst.txt

if [ "$MODE" = check ]; then
  n_diff=0; n_only_a=0; n_only_m=0
  # PARITY IS ABOUT WHAT EACH REPOSITORY SHIPS, NOT WHAT SITS ON ITS DISK.
  # The first version of this check tested `[ ! -f "$M/$p" ]`, comparing the
  # archive's TRACKED set against the mirror's FILESYSTEM. A file ported onto
  # the mirror but never `git add`ed then read as parity-clean while the
  # pushed mirror would not carry it at all, which is precisely the state a
  # port leaves behind (the porter copies, it does not stage). Found the hour
  # the instrument was born, by porting a new chapter and watching the check
  # go quiet over an untracked file. The mirror's TRACKED set is the referent.
  while IFS= read -r p; do
    if ! grep -qxF "$p" /tmp/port_dst.txt; then
      if [ -f "$M/$p" ]; then
        echo "  PRESENT BUT UNTRACKED IN MIRROR: $p"
      else
        echo "  ONLY IN ARCHIVE: $p"
      fi
      n_only_a=$((n_only_a+1))
    elif ! cmp -s "$A/$p" "$M/$p"; then
      echo "  CONTENT DIFFERS: $p"; n_diff=$((n_diff+1))
    fi
  done < /tmp/port_src.txt
  while IFS= read -r p; do
    if ! grep -qxF "$p" /tmp/port_src.txt; then
      echo "  ONLY IN MIRROR:  $p"; n_only_m=$((n_only_m+1))
    fi
  done < /tmp/port_dst.txt
  total=$((n_diff + n_only_a + n_only_m))
  echo "parity check: $n_diff differ, $n_only_a archive-only, $n_only_m mirror-only"
  if [ "$total" -eq 0 ]; then
    echo "PARITY CLEAN"; exit 0
  fi
  echo "PARITY DRIFT: $total path(s). Run without --check to port."; exit 1
fi

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

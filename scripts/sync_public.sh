#!/usr/bin/env bash
# Keep the public repository in step with this one.  RULE (2026-07-25): the two
# repositories must stay synchronised for as long as either is modified.
#
#   ~/Documents/GitHub/Rb-5S-6S-analysis   -> MichelangeloDondi/Rb-5S-6S-analysis-archive
#                                             PRIVATE. Canonical. Has the raw traces.
#                                             ALL work happens here.
#   ~/Documents/GitHub/Rb-5S-6S-public     -> MichelangeloDondi/Rb-5S-6S-analysis
#                                             PUBLIC. No raw traces. Receives changes.
#
# The two have DIVERGENT histories -- the public one was produced by
# filter-branch, so the same change has a different hash in each. They can
# therefore never simply track each other; changes are carried across as
# patches (cherry-pick), which keeps the public history append-only rather
# than force-pushed.
#
# Usage:
#   scripts/sync_public.sh              # carry every archive commit the public repo lacks
#   scripts/sync_public.sh <sha>...     # carry only these
#   scripts/sync_public.sh --check      # report drift, change nothing
#
# What it will NOT do: touch data_raw/ traces or data_recovered/ traces (they
# must never reach the public repo), or silently overwrite the files that
# intentionally differ -- a cherry-pick that conflicts in one of those stops
# and asks, which is the correct behaviour, not a failure.

set -euo pipefail

ARCHIVE="$HOME/Documents/GitHub/Rb-5S-6S-analysis"
PUBLIC="$HOME/Documents/GitHub/Rb-5S-6S-public"

# Files deliberately different between the two repos (the raw-trace honesty
# pass). A conflict here is expected and must be resolved by hand, keeping the
# PUBLIC wording.
DIVERGENT=(
  "README.md"
  "docs/BIG_PICTURE.md"
  "docs/DATA.md"
  "docs/methods.md"
  "docs/PREREGISTRATION_RESULTS.md"
  "data_raw/README.md"
)

# Paths that must never be carried across, whatever a commit touches.
NEVER=(
  "data_raw/traces" "data_raw/t_sweep" "data_raw/p_sweep" "data_raw/rulers_t"
  "data_raw/rulers_p" "data_raw/discarded" "data_raw/quarantine"
  "data_recovered/discarded_backup" "data_recovered/lineage_4192nm_225mw1"
)

die() { echo "sync_public: $*" >&2; exit 1; }

[ -d "$PUBLIC/.git" ] || die "public clone not found at $PUBLIC"
cd "$PUBLIC"
# Guard: origin here MUST be the public repository. (On 2026-07-25 the
# archive clone's origin still pointed at the pre-rename URL, which the rename
# had handed to the PUBLIC repo -- a push from there would have sent the full
# raw-data history public. It was refused only by a non-fast-forward. Never
# rely on that a second time.)
_origin="$(git remote get-url origin)"
case "$_origin" in
  *Rb-5S-6S-analysis-archive*) die "origin is the ARCHIVE ($_origin) -- refusing" ;;
  *Rb-5S-6S-analysis*)         : ;;
  *) die "origin is not the expected public repo: $_origin" ;;
esac

git remote get-url archive >/dev/null 2>&1 || git remote add archive "$ARCHIVE"
# --no-tags matters: the archive carries tags (raw-backup-2026-07-24, the
# msg-rewrite backup) that point at UNFILTERED commits, i.e. at the raw
# traces. A plain fetch drags them into the public clone. (Observed and
# cleaned 2026-07-25.)
git fetch --quiet --no-tags archive

# --- what does the public repo not have yet? -------------------------------
# Compare by SUBJECT, since hashes differ between the two histories.
# (bash 3.2 on macOS has no mapfile; use a temp file and plain loops)
_pubsubj="$(mktemp)"; _arch="$(mktemp)"
trap 'rm -f "$_pubsubj" "$_arch"' EXIT
{ git log --format='%s' origin/main 2>/dev/null || git log --format='%s'; } > "$_pubsubj"
git log --format='%H %s' archive/main | sed '1!G;h;$!d' > "$_arch"   # reverse: oldest first
missing=()
while IFS= read -r line; do
  sha="${line%% *}"; subj="${line#* }"
  if ! grep -Fxq "$subj" "$_pubsubj"; then missing+=("$sha"); fi
done < "$_arch"

if [ "${1:-}" = "--check" ]; then
  if [ ${#missing[@]} -eq 0 ]; then
    echo "sync_public: in step -- the public repo has every archive commit."
  else
    echo "sync_public: ${#missing[@]} commit(s) not yet in the public repo:"
    for s in "${missing[@]}"; do git --no-pager log -1 --format='  %h %s' "$s"; done
  fi
  exit 0
fi

targets=("$@")
[ ${#targets[@]} -eq 0 ] && targets=("${missing[@]}")
[ ${#targets[@]} -eq 0 ] && { echo "sync_public: nothing to carry."; exit 0; }

echo "sync_public: carrying ${#targets[@]} commit(s) to the public repo."
for sha in "${targets[@]}"; do
  git --no-pager log -1 --format='  -> %h %s' "$sha"
  if ! git cherry-pick -x "$sha"; then
    echo
    echo "sync_public: CONFLICT on $(git --no-pager log -1 --format='%h %s' "$sha")."
    echo "  Files that intentionally differ between the repos:"
    printf '    %s\n' "${DIVERGENT[@]}"
    echo "  Resolve keeping the PUBLIC wording, then: git cherry-pick --continue"
    echo "  (or 'git cherry-pick --abort' to stop.)"
    exit 1
  fi
  # belt and braces: no trace may ride along
  for p in "${NEVER[@]}"; do
    if git ls-files --error-unmatch "$p" >/dev/null 2>&1; then
      die "a raw-trace path ($p) entered the public tree -- aborting, fix by hand"
    fi
  done
done

echo
echo "sync_public: running the suite before pushing."
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi
$PY -m pytest -q || die "tests failed in the public repo -- not pushing"

git push origin main

# Do not leave raw-data objects sitting in the public clone: fetching the
# archive brings them in via remote-tracking refs, where a careless
# `git push --all/--mirror` could leak them. Drop the remote and prune.
git remote remove archive >/dev/null 2>&1 || true
git reflog expire --expire=now --all >/dev/null 2>&1 || true
git gc --prune=now --quiet >/dev/null 2>&1 || true

echo "sync_public: public repo updated and pushed; archive objects pruned."

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
git remote get-url archive >/dev/null 2>&1 || git remote add archive "$ARCHIVE"
git fetch --quiet archive

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
echo "sync_public: public repo updated and pushed."

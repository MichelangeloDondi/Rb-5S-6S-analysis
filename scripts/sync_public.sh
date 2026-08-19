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
# than force-pushed. A port that cannot be a clean cherry-pick says which
# source commits it carried, in its own message, as "(source <sha>)" or
# "(source <sha>, <sha>)" or "source commits <sha> through <sha>". Writing
# that line is what lets --check below tell a delivered commit from a missing
# one, so a port message without it is a port that will be re-reported for ever.
#
# Usage:
#   scripts/sync_public.sh              # carry every source commit the public repo lacks
#   scripts/sync_public.sh <sha>...     # carry only these
#   scripts/sync_public.sh --check      # report drift, change nothing
#
# What it will NOT do: touch data_raw/ traces or data_recovered/ traces (they
# must never reach the public repo), or silently overwrite the files that
# intentionally differ -- a cherry-pick that conflicts in one of those stops
# and asks, which is the correct behaviour, not a failure.

set -euo pipefail

SOURCE_REPO="$HOME/Documents/GitHub/Rb-5S-6S-analysis"
PUBLIC="$HOME/Documents/GitHub/Rb-5S-6S-public"

# Files deliberately different between the two repos (the raw-trace honesty
# pass). A conflict here is expected and must be resolved by hand, keeping the
# PUBLIC wording.
DIVERGENT=(
  "README.md"
  # Added 2026-08-09. The version guard names the incident that
  # motivated it, and in the public copy that story cannot be told
  # as one about two repositories. The public wording states the
  # same facts in the first person. Keep the public version on
  # conflict, like every other row here.
  "tests/test_version_surface.py"
  "docs/BIG_PICTURE.md"
  "docs/DATA.md"
  "docs/methods.md"
  "docs/PREREGISTRATION_RESULTS.md"
  "data_raw/README.md"
  # Added 2026-07-29. The source repository is a PRIVATE repo billed per Actions minute,
  # so its matrix is gated to tags and dispatch; the mirror is public and free,
  # so it runs the full --runslow battery on every push and is the reference
  # green check. Carrying the source repository's gates across silently disabled the slow
  # tests in BOTH repos, which is how the gate came to be justified by a mirror
  # that was no longer doing the job. Keep the public version on conflict.
  ".github/workflows/tests.yml"
  # Added 2026-07-30, after it conflicted for the first time. The two ignore
  # files differ in ONE line and the difference is load-bearing: in the mirror
  # .venv is a SYMLINK into the source repository checkout, so the rule there is `.venv`
  # with NO trailing slash -- a directory-only pattern does not match a symlink,
  # and `git add -A` staged it once on 2026-07-29. Resolve by keeping the
  # mirror's `.venv` line and porting any NEW rules across by hand.
  ".gitignore"
  # Added 2026-07-31, when the prose-style ratchet was introduced and failed on
  # its first sync. The budget is per file, and five of the files above are
  # DELIBERATELY different documents in the two repos, so their em-dash and
  # semicolon counts differ too. One shared baseline can therefore never
  # satisfy both. Each repo records its own with
  # `python tests/test_prose_style_ratchet.py --relax`; on conflict, keep the
  # mirror's numbers and re-record rather than merging them by hand.
  "tests/_style_baseline.json"
  # Added 2026-08-05, after the two copies were found to have diverged with
  # nothing here saying so. The source repository's `cdc1f82` added the
  # `proj_source_ -> CALIB` override to the status map. The mirror's port of
  # that commit, `c0d2ff4`, left the override out, and `127e430` then added the
  # mirror's own M28 status block and recorded the exclusion as durable. A sync
  # that carries this file across either reinstates the override the mirror
  # dropped or reports the source repository's edits as permanently missing. Resolve by
  # keeping the mirror's map and porting any NEW quantity block by hand.
  "scripts/annotate_results_status.py"
)

# Paths that must never be carried across, whatever a commit touches.
NEVER=(
  # this script itself: maintenance tooling that names the private source repo
  # and carries local paths -- removed from the public tree 2026-07-25
  "scripts/sync_public.sh"
  "data_raw/traces" "data_raw/t_sweep" "data_raw/p_sweep" "data_raw/rulers_t"
  "data_raw/rulers_p" "data_raw/discarded" "data_raw/excluded"
  "data_recovered/discarded_backup" "data_recovered/lineage_4192nm_225mw1"
)

die() { echo "sync_public: $*" >&2; exit 1; }

[ -d "$PUBLIC/.git" ] || die "public clone not found at $PUBLIC"
cd "$PUBLIC"
# Guard: origin here MUST be the public repository. (On 2026-07-25 the
# source clone's origin still pointed at the pre-rename URL, which the rename
# had handed to the PUBLIC repo -- a push from there would have sent the full
# raw-data history public. It was refused only by a non-fast-forward. Never
# rely on that a second time.)
_origin="$(git remote get-url origin)"
case "$_origin" in
  *Rb-5S-6S-analysis-archive*) die "origin is the SOURCE repository ($_origin) -- refusing" ;;
  *Rb-5S-6S-analysis*)         : ;;
  *) die "origin is not the expected public repo: $_origin" ;;
esac

git remote get-url source >/dev/null 2>&1 || git remote add source "$SOURCE_REPO"
# --no-tags matters: the source repository carries tags (raw-backup-2026-07-24, the
# msg-rewrite backup) that point at UNFILTERED commits, i.e. at the raw
# traces. A plain fetch drags them into the public clone. (Observed and
# cleaned 2026-07-25.)
git fetch --quiet --no-tags source

# --- what does the public repo not have yet? -------------------------------
# Hashes differ between the two histories, so delivery has to be inferred from
# the mirror's own commit messages. THREE conventions live in that history and
# all three have to be read, because reading only the first reported 51 already
# delivered commits as missing on 2026-08-04.
#
#   1. SUBJECT. A clean cherry-pick keeps the source repository subject verbatim.
#   2. NAMED SHA. A hand-resolved or batched port renames the subject and names
#      its source: "Port the ruler validity layer (source 50ea29d)", "(source
#      c74a0cc, 0bf2502)", "source commits 871415c through 9962074",
#      "(cherry picked from commit <full sha>)". Every hex token in the mirror's
#      messages that resolves to a commit on source/main is read as delivered,
#      and a "A through B" pair expands to the whole range.
#   NOTE, learned 2026-08-17: a whole-tree port whose message names ONE source
#   sha registers exactly that one commit as delivered, so --check goes on
#   reporting the other forty-seven for ever, which is the failure the
#   paragraph above warns about in the abstract. Use the range form,
#   "source commits A through B", or the "(source HEAD)" marker below. The
#   repair, if it is noticed after pushing, is an EMPTY follow-up commit
#   carrying the range: the mirror's history is append-only, so amending a
#   pushed port is the wrong instrument.
#
#   3. WHOLE-TREE PORT. "(source HEAD)" and "direct-copied" mark a port that
#      replaced the mirror's tree with the source repository's tree of that moment, so it
#      delivers the CONTENT of every source commit up to its own date, whatever
#      the subjects were. The latest such port therefore clears everything
#      behind it. This is about content and not about commits, which is the
#      right question for a drift detector: the DIVERGENT and NEVER lists below
#      still decide what such a port was allowed to carry.
#
# (bash 3.2 on macOS has no mapfile; use temp files and plain loops)
_pubsubj="$(mktemp)"; _arch="$(mktemp)"; _pubmsg="$(mktemp)"
_toks="$(mktemp)"; _delivered="$(mktemp)"
trap 'rm -f "$_pubsubj" "$_arch" "$_pubmsg" "$_toks" "$_delivered"' EXIT
_pubref=origin/main
git rev-parse --verify --quiet "$_pubref" >/dev/null 2>&1 || _pubref=HEAD
git log --format='%s' "$_pubref" > "$_pubsubj"
git log --format='%s%n%b' "$_pubref" > "$_pubmsg"
git log --format='%H %s' source/main | sed '1!G;h;$!d' > "$_arch"   # reverse: oldest first

# (2) every hex token the mirror's messages name, kept when it resolves to a
# commit that is actually on source/main. The ancestor test is what keeps the
# mirror's own hashes and stray words out.
: > "$_delivered"
grep -oE '[0-9a-f]{7,40}' "$_pubmsg" | sort -u > "$_toks" || true
while IFS= read -r _tok; do
  [ -z "$_tok" ] && continue
  _full="$(git rev-parse --verify --quiet "${_tok}^{commit}" 2>/dev/null)" || continue
  if git merge-base --is-ancestor "$_full" source/main 2>/dev/null; then
    echo "$_full" >> "$_delivered"
  fi
done < "$_toks"
grep -oE '[0-9a-f]{7,40} through [0-9a-f]{7,40}' "$_pubmsg" | while read -r _a _ _b; do
  _ra="$(git rev-parse --verify --quiet "${_a}^{commit}" 2>/dev/null)" || continue
  _rb="$(git rev-parse --verify --quiet "${_b}^{commit}" 2>/dev/null)" || continue
  git rev-list "${_ra}^..${_rb}" 2>/dev/null || true
done >> "$_delivered"

# (3) the newest whole-tree port. Each message is flattened to one line first,
# because a body spans lines and the date has to stay attached to it.
_whole="$(git log --format='%cI%x09%s %b%x00' "$_pubref" \
          | tr '\n' ' ' | tr '\0' '\n' \
          | grep -Ei '(archive|source) HEAD|direct[- ]cop(y|ied)' | cut -f1 | sort | tail -1)" || true
if [ -n "${_whole:-}" ]; then
  git rev-list source/main --before="$_whole" >> "$_delivered"
fi
sort -u "$_delivered" -o "$_delivered"

missing=()
while IFS= read -r line; do
  sha="${line%% *}"; subj="${line#* }"
  grep -Fxq "$subj" "$_pubsubj" && continue        # (1) carried under its own subject
  grep -qx "$sha" "$_delivered" && continue        # (2) and (3) named or whole-tree
  # A commit that touches ONLY source-private paths has no public effect --
  # carrying it would produce an empty cherry-pick and it would then be
  # reported as "missing" for ever. Treat it as delivered.
  _touched="$(git show --pretty=format: --name-only "$sha" | sed '/^$/d')"
  _public_effect=0
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    # A DIVERGENT file is resolved keeping the PUBLIC wording every time, so an
    # source-side change to one is never carried. A commit touching ONLY such
    # files therefore cherry-picks empty and would be re-reported for ever --
    # which is exactly what the 2026-07-29 CI-trigger commit did on 2026-07-30.
    _is_divergent=0
    for _d in "${DIVERGENT[@]}"; do
      [ "$f" = "$_d" ] && { _is_divergent=1; break; }
    done
    [ "$_is_divergent" -eq 1 ] && continue
    case "$f" in
      scripts/sync_public.sh) ;;                   # source-only tooling
      data_raw/t_sweep/*|data_raw/p_sweep/*|data_raw/rulers_*/*|\
      data_raw/discarded/*|data_raw/excluded/*|\
      data_recovered/discarded_backup/*|data_recovered/lineage_*/*) ;;
      *) _public_effect=1; break ;;
    esac
  done <<< "$_touched"
  [ "$_public_effect" -eq 1 ] && missing+=("$sha")
done < "$_arch"

if [ "${1:-}" = "--check" ]; then
  if [ ${#missing[@]} -eq 0 ]; then
    echo "sync_public: in step -- the public repo has every source commit."
  else
    echo "sync_public: ${#missing[@]} commit(s) not yet in the public repo:"
    for s in "${missing[@]}"; do git --no-pager log -1 --format='  %h %s' "$s"; done
  fi
  exit 0
fi

# bash 3.2 (macOS) errors on expanding an EMPTY array under `set -u`, so the
# count must be checked BEFORE "${missing[@]}" is expanded -- otherwise a
# run with nothing to carry dies with `missing[@]: unbound variable` instead
# of reporting that it is in step. ${#missing[@]} itself is safe; the
# expansion is not.
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  if [ ${#missing[@]} -eq 0 ]; then
    echo "sync_public: nothing to carry."; exit 0
  fi
  targets=("${missing[@]}")
fi

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
  # belt and braces after every cherry-pick.
  #   - this script may legitimately be re-introduced by a commit that edits
  #     it; drop it and amend, quietly.
  #   - a raw-trace path must NEVER appear: that is a bug, so stop.
  if git ls-files --error-unmatch "scripts/sync_public.sh" >/dev/null 2>&1; then
    git rm --quiet --cached "scripts/sync_public.sh"
    rm -f "scripts/sync_public.sh"
    git commit --quiet --amend --no-edit
  fi
  for p in "${NEVER[@]}"; do
    [ "$p" = "scripts/sync_public.sh" ] && continue
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
# source repository brings them in via remote-tracking refs, where a careless
# `git push --all/--mirror` could leak them. Drop the remote and prune.
git remote remove source >/dev/null 2>&1 || true
git reflog expire --expire=now --all >/dev/null 2>&1 || true
git gc --prune=now --quiet >/dev/null 2>&1 || true

echo "sync_public: public repo updated and pushed; source objects pruned."

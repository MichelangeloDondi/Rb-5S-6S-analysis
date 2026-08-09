"""The version surface: three metadata files, and the tag that makes the
version a released thing rather than a string.

Two failures, one shape. Both are silent, and both are visible to any reader
who opens the landing page and clicks Releases.

1. pyproject.toml and CITATION.cff diverged once already (pyproject stale at
   1.1.0 while CITATION.cff and the tags had advanced to 1.4.0, caught
   2026-07-25). That catch added a two-file comparison to
   tests/test_repo_hygiene.py. rb5s6s/__init__.py carries a third copy of the
   same string and was in neither that divergence nor the guard, so the
   surface was two thirds covered.

2. The metadata here reached 3.4.0 on 2026-08-06 and the newest tag
   stayed v3.2.0, thirty-one commits behind it. The installed package
   therefore announced a version with no tag, no release and no notes. The 2026-07-25 guard had ruled
   the tag out of scope on the grounds that tagging happens after the
   version-bump commit, which is true of the bump commit and false of every
   commit after it. This module keeps that exemption and bounds it: the bump
   commit and a short tail after it may run untagged, the fifth commit past a
   bump may not.

The invariant, stated once: the metadata version equals the newest version tag
reachable from HEAD, or it is one bump ahead of it inside the grace window.
Metadata BEHIND the newest reachable tag fails too, which is the other half of
the same decoupling. That direction was live here for weeks, the metadata
sitting at 3.0.0 under a v3.2.0 tag and release.

Environment. The tag half needs tags, and a default actions/checkout fetches
none, so it SKIPS on a checkout that has no version tags at all rather than
reporting the fetch depth as a repository defect. That is the same call the
raw-trace and not-a-git-checkout skips make. It also means the tag half is
load-bearing where the full clone is: the scripts/ci_gate.sh run before a
push. For CI to carry it as well, the pytest job's checkout needs
`fetch-depth: 0`. A checkout that has SOME version tags but not this one is
not an environment limitation, it is the defect this module is for, and it
fails.

WHAT THIS DOES NOT CATCH. These limits are stated rather than papered over.

* It cannot block the omission at the moment it happens. The release sequence
  is bump, gate, commit, push, tag, so at gate time the new version is not yet
  in committed history and at the release commit the distance is zero. The
  guard first speaks on the fifth commit after a bump. It is a detector with a
  four-commit fuse, not an interlock.
* A version the metadata never held is outside its reach. The comparison is
  against the newest reachable tag, so a number that was skipped entirely, as
  3.3.0 was here, leaves no trace for it to find.
* `git tag` is local. A tag made and never pushed satisfies this guard while
  the Releases page and the README badge, which read the API, stay behind. Two
  of this project's own `v*` tags have no release object at all, so the tag is a
  proxy for the release and not the release itself. Row 10 of section 16.7 of
  the rendering protocol names the Releases page as the evidence for that half.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The release sequence is: bump the three files, run the gate, push, tag. So
# the bump commit cannot be required to carry a tag, and neither can the
# regenerated-results commit that has followed a bump in the waves on record.
# Four is wider than any bump-to-tag distance in either repository's history
# and far narrower than the thirty-one commits this guard was written for.
_BUMP_GRACE_COMMITS = 4

_VERSION_FIELDS = (
    ("pyproject.toml", r'^version = "([^"]+)"'),
    ("rb5s6s/__init__.py", r'^__version__ = "([^"]+)"'),
    ("CITATION.cff", r"^version: (\S+)"),
)

_SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def _git(*args: str) -> str | None:
    """git stdout, or None when git cannot answer (tarball, no repository)."""
    out = subprocess.run(["git", "-C", str(ROOT), *args],
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def _key(version: str) -> tuple[int, int, int]:
    m = _SEMVER.match(version)
    assert m, f"not a semantic version: {version!r}"
    return tuple(int(g) for g in m.groups())  # type: ignore[return-value]


def _metadata_versions() -> dict[str, str]:
    found: dict[str, str] = {}
    for rel, pat in _VERSION_FIELDS:
        path = ROOT / rel
        assert path.is_file(), f"{rel} is missing from the checkout"
        m = re.search(pat, path.read_text(encoding="utf-8"), re.M)
        assert m, f"no version field matching {pat!r} in {rel}"
        found[rel] = m.group(1).strip().strip('"')
    return found


def _bump_commit(version: str) -> str | None:
    """The OLDEST commit whose pyproject.toml carries `version`.

    Oldest and not the start of the newest unbroken run, which is the repair
    of 2026-08-09. Stopping at the first differing version let any detour
    reset the grace window: a typo committed and undone, a revert, or a merge
    resolution that passed through another number re-armed four more commits
    of silence. Taking the earliest introduction makes the clock start when
    the version first appeared and never restart. The file's history is a
    dozen commits in both repositories, so walking all of it is cheap.

    Returns None when no committed revision carries this version, which is
    either a bump that is still uncommitted or a history too shallow to
    contain the introduction. The caller distinguishes those two.
    """
    log = _git("log", "--format=%H", "--", "pyproject.toml")
    if log is None:
        return None
    oldest = None
    for sha in [s for s in log.split("\n") if s]:
        blob = _git("show", f"{sha}:pyproject.toml")
        if blob is None:
            continue
        m = re.search(r'^version = "([^"]+)"', blob, re.M)
        if m and m.group(1) == version:
            oldest = sha
    return oldest


def _uncommitted_bump() -> bool:
    """True when the working tree's pyproject version differs from HEAD's.

    This is the sanctioned pre-release state, and telling it apart from a
    shallow clone is the difference between a correct skip and the first
    version's misattribution, which reported a truncated history on a full
    clone (defect D1 of the 2026-08-09 attack).
    """
    head = _git("show", "HEAD:pyproject.toml")
    if head is None:
        return False
    m = re.search(r'^version = "([^"]+)"', head, re.M)
    live = _metadata_versions().get("pyproject.toml")
    return bool(m) and m.group(1) != live


# Tags cut before this version were made when the metadata surface and the tag
# names ran independently: the pyproject read 3.0.0 at v3.1.0 and v3.2.0, and rb5s6s/__init__.py read 0.1.0 at fifteen tagged commits. So
# the tagged-tree check below starts here rather than rewriting that history.
_TAG_METADATA_FROM = (3, 5, 0)


def test_the_three_metadata_versions_agree():
    """pyproject.toml, rb5s6s/__init__.py and CITATION.cff carry one string.

    Always runs. It needs no git, no network and no data, so there is no
    environment in which this half is allowed to be silent.
    """
    found = _metadata_versions()
    distinct = set(found.values())
    assert len(distinct) == 1, (
        "version drift across the metadata surface:\n  "
        + "\n  ".join(f"{rel}: {v}" for rel, v in found.items())
        + "\nBump all three in one commit. Two of the three were compared "
          "from 2026-07-25, rb5s6s/__init__.py was not.")
    only = distinct.pop()
    assert _SEMVER.match(only), (
        f"the metadata version is {only!r}, which is not MAJOR.MINOR.PATCH. "
        "The tag guard and the release naming both read it as one.")


def test_the_metadata_version_is_the_released_version():
    """The metadata version has a git tag, and no newer tag has passed it.

    Skips only on an environment that cannot answer: no git, or a checkout
    carrying no version tags at all (a shallow clone, a default
    actions/checkout, an exported tarball). A checkout with version tags is
    held to the invariant.
    """
    distinct = set(_metadata_versions().values())
    if len(distinct) != 1 or not _SEMVER.match(next(iter(distinct))):
        pytest.skip("metadata versions disagree or are not semantic, which "
                    "the agreement guard is the one to report")
    meta = distinct.pop()

    tags = _git("tag", "--merged", "HEAD", "--list", "v*")
    if tags is None:
        pytest.skip("not a git checkout")
    reachable = sorted(
        (t[1:] for t in (x.strip() for x in tags.split("\n"))
         if t and _SEMVER.match(t[1:])),
        key=_key)
    if not reachable:
        pytest.skip("no version tags reachable from HEAD: a shallow clone or "
                    "a fetch without tags cannot be told apart from an "
                    "untagged repository. Set fetch-depth: 0 to make this "
                    "half run in CI.")
    newest = reachable[-1]

    # A tag is a name until the tree under it agrees with the name. Checking
    # only that the name exists passed a tag pointing at a tree declaring a
    # different version (defect D4 of the 2026-08-09 attack), which is exactly
    # the mistake available when back-cutting a tag someone missed.
    if _key(newest) >= _TAG_METADATA_FROM:
        blob = _git("show", f"v{newest}:pyproject.toml")
        if blob is not None:
            m = re.search(r'^version = "([^"]+)"', blob, re.M)
            assert m and m.group(1) == newest, (
                f"the tag v{newest} points at a tree whose pyproject.toml "
                f"declares {m.group(1) if m else 'no version'}. A tag is the "
                f"name of a released tree, so back-cutting one onto older "
                f"content states something false about that content. Tag the "
                f"commit that carries the metadata, or cut the version "
                f"forward instead.")

    if meta == newest:
        return

    assert _key(meta) > _key(newest), (
        f"the metadata says {meta} while v{newest} is already tagged and "
        f"reachable from HEAD. This repository ran for weeks with its "
        f"metadata at "
        f"3.0.0 under a v3.2.0 tag and release, so a reader's `pip show` "
        f"disagreed with the Releases page. Bump the three metadata files to "
        f"{newest}, or cut the tag the metadata claims.")

    bump = _bump_commit(meta)
    if bump is None:
        if _uncommitted_bump():
            pytest.skip(f"the bump to {meta} is not committed yet, which is "
                        f"the sanctioned pre-release state. The tag half "
                        f"cannot speak until the bump has a commit, so it is "
                        f"the release sequence and not this checkout that "
                        f"carries v{meta} from here.")
        pytest.skip("no committed revision carries this version and the "
                    "working tree agrees with HEAD, so the introduction is "
                    "outside a truncated history")
    since = _git("rev-list", "--count", f"{bump}..HEAD")
    assert since is not None, "git rev-list failed on a live checkout"
    distance = int(since.strip())
    assert distance <= _BUMP_GRACE_COMMITS, (
        f"the metadata has said {meta} since {bump[:7]}, {distance} commits "
        f"back, and the newest tag reachable from HEAD is still v{newest}. "
        f"The installed package announces a version this repository never "
        f"released. That is the state of 2026-08-06: the metadata moved to "
        f"3.4.0 and neither the tag nor the release followed. The distance is measured from the version's EARLIEST "
        f"introduction, so a detour through another number does not reset it. "
        f"Cut v{meta} here with its notes, or revert the metadata to "
        f"{newest} until the release is cut. The grace window is "
        f"{_BUMP_GRACE_COMMITS} commits, which covers the bump commit and the "
        f"regeneration that follows it.")

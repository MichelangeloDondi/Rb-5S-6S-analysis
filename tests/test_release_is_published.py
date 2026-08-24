"""The version this repository declares is PUBLISHED, not merely tagged.

WHY THIS EXISTS. On 2026-08-17 the owner reported that GitHub still showed
v3.8.0 while every file in the tree said 4.0. Both were correct. The tag `v4.0`
was pushed to both remotes and the metadata declared 4.0, but NO GITHUB RELEASE
OBJECT existed, and a Release is what GitHub's sidebar, its releases page and
the shields.io badge on the front page all read. So from outside, the project
had last released four days earlier.

Nothing in the suite could see it. `tests/test_version_surface.py` ties the
three metadata files to the newest reachable TAG, deliberately, and its own
docstring records that some tags carry no release. That is the correct scope
for a guard that must run without a network. The gap is that NOTHING checked
the surface outside the tree, and a version is declared in three files INSIDE
the repository and published in a fourth place OUTSIDE it.

WHAT THIS CHECKS, as a chain, where the last link is the one that catches a
release back-cut onto older content or a tag moved after release:

    declared version == tag name == release name, and tag commit == release
    commit.

WHY IT IS A RELEASE-INTEGRITY CHECK AND NOT AN ORDINARY GATE. It needs the
network and the GitHub CLI, neither of which a scientific test run may assume.
It therefore SKIPS, loudly and with a reason, wherever it cannot answer, and
fails only when it positively establishes a mismatch. A guard that reddens a
physics run because a laptop is offline would be turned off within a week, and
then it would protect nothing.

TWO SUBTLETIES, BOTH OF WHICH PRODUCED A WRONG COMPARISON WHILE THIS WAS BEING
WRITTEN, and both of which are the same mistake: comparing two things that are
not the same kind of thing.

FIRST, the tags here are ANNOTATED, so `git/ref/tags/<name>` returns the sha of
the TAG OBJECT rather than of the commit. Comparing that to `rev-parse
<tag>^{commit}` never matches. The dereference through `git/tags/<sha>` is
required and is what `_release_commit` does.

SECOND, and this one failed the guard on its first run, THE TWO REPOSITORIES
HAVE DIVERGENT HISTORIES. The public mirror was produced by filter-branch, so
the same content carries a different hash in each, which is why ports are
cherry-picks rather than pushes. Comparing the ARCHIVE's local tag commit
against the PUBLIC release commit therefore compares across two histories and
can never match, by construction. The commit half of the check is meaningful
only inside the public clone, and it is skipped elsewhere with that reason
stated. The existence half is meaningful everywhere.

Verified in both directions on 2026-08-17: it passes where it can answer, and
a version with no published release makes it fail rather than skip.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The public repository is the surface a reader meets. The archive is private
# and its release page has no audience, so this guard is aimed at the mirror.
PUBLIC_REPO = "MichelangeloDondi/Rb-5S-6S-analysis"


def _origin_is_the_public_repo() -> bool:
    """Whether THIS clone is the mirror, which is the only place a commit
    comparison means anything: the two histories are divergent by design."""
    out = subprocess.run(["git", "-C", str(ROOT), "remote", "get-url", "origin"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return False
    url = out.stdout.strip()
    return "Rb-5S-6S-analysis" in url and "archive" not in url


def _declared_version() -> str:
    m = re.search(r'^version = "([^"]+)"',
                  (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    assert m, "pyproject.toml declares no version"
    return m.group(1)


def _gh(*args: str):
    """gh stdout parsed as json, or None when gh cannot answer."""
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return out.stdout.strip()


def _release_commit(tag: str) -> str | None:
    """The COMMIT a tag ref resolves to on the remote, dereferencing annotation.

    An annotated tag's ref points at a tag OBJECT, so this needs a second call.
    Comparing the tag-object sha to a commit sha silently never matches, which
    is the mistake this function exists to make impossible.
    """
    ref = _gh("api", f"repos/{PUBLIC_REPO}/git/ref/tags/{tag}")
    if not isinstance(ref, dict):
        return None
    obj = ref.get("object", {})
    if obj.get("type") == "tag":
        deref = _gh("api", f"repos/{PUBLIC_REPO}/git/tags/{obj['sha']}")
        if not isinstance(deref, dict):
            return None
        return deref.get("object", {}).get("sha")
    return obj.get("sha")


@pytest.mark.slow
def test_the_declared_version_has_a_published_release():
    """The version in the metadata is published, at the commit it names."""
    if shutil.which("gh") is None:
        pytest.skip("the GitHub CLI is absent, so the published surface "
                    "cannot be read from here")

    version = _declared_version()
    tag = f"v{version}"

    releases = _gh("release", "list", "--repo", PUBLIC_REPO,
                   "--json", "tagName", "--limit", "100")
    if releases is None:
        pytest.skip("the GitHub CLI could not reach the remote (no network, "
                    "or not authenticated), so nothing is established here")

    published = {r["tagName"] for r in releases}

    if tag not in published:
        # The sanctioned mid-drill state, learnt releasing v4.3: the sequence
        # is bump, gate, push, tag, publish, so at the gate step the release
        # object CANNOT exist yet and this guard deadlocked the drill.
        # test_version_surface.py grants the bump _BUMP_GRACE_COMMITS of
        # grace for the same reason; this guard grants the same window,
        # measured the same way, from the version's earliest introduction.
        # Past the window the red returns, which is the v4.0 incident this
        # file exists for: metadata four days and many commits ahead of the
        # published surface.
        intro = subprocess.run(
            ["git", "-C", str(ROOT), "log", "--format=%H", "--reverse",
             "-S", f'version = "{version}"', "--", "pyproject.toml"],
            capture_output=True, text=True)
        first = intro.stdout.split()[0] if intro.returncode == 0 and intro.stdout.strip() else ""
        if first:
            since = subprocess.run(
                ["git", "-C", str(ROOT), "rev-list", "--count",
                 f"{first}..HEAD"], capture_output=True, text=True)
            if since.returncode == 0 and int(since.stdout.strip()) <= 4:
                pytest.skip(
                    f"{tag} is declared and not yet published, and the "
                    f"declaring commit is within the bump grace window: the "
                    f"sanctioned mid-drill state. The drill's publish step "
                    f"and the re-gate after it are what close this.")

    assert tag in published, (
        f"the metadata declares {version}, and {tag} is not among the "
        f"published releases of {PUBLIC_REPO}. A tag alone changes nothing a "
        f"visitor sees: the sidebar, the releases page and the README badge "
        f"all read RELEASE objects, so the front page still advertises the "
        f"previous one. Publish it with `gh release create {tag} "
        f"--verify-tag`.\n  published: {sorted(published)}")

    if not _origin_is_the_public_repo():
        pytest.skip("this clone is not the public mirror, and the two "
                    "repositories have divergent histories by design, so the "
                    "same content carries different hashes and a commit "
                    "comparison would be meaningless. The existence check "
                    "above has run and is the part that transfers.")

    remote_commit = _release_commit(tag)
    if remote_commit is None:
        pytest.skip(f"{tag} is published, but its commit could not be read "
                    "from the remote")

    local = subprocess.run(["git", "-C", str(ROOT), "rev-parse",
                            f"{tag}^{{commit}}"],
                           capture_output=True, text=True)
    if local.returncode != 0:
        pytest.skip(f"{tag} is not present locally, so the commit cannot be "
                    "compared")
    local_commit = local.stdout.strip()

    assert remote_commit == local_commit, (
        f"{tag} is published, but it names a different commit than the local "
        f"tag does.\n  published at: {remote_commit}\n  local tag at: "
        f"{local_commit}\nA release cut onto older content, or a tag moved "
        f"after release, states something false about what was released.")

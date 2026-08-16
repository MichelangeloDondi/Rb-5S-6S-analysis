"""No second copy of a committed artefact sitting where git cannot see it.

WHY THIS EXISTS. On 2026-08-17 the owner reported that a figure had been
reverted to an older version. It had not. The committed file carried both
repairs its history records, and regenerating it from its producer reproduced
it byte for byte. What existed was a SECOND COPY, three of them in fact, inside an IGNORED
TOOLING DIRECTORY holding abandoned worktrees from earlier sessions, carrying
the pre-repair drawing. Being ignored, git says nothing about it, GitHub never
receives it, and every guard in this suite walks tracked files and therefore
looks straight past it. Opened in a viewer it is indistinguishable from the
real figure, and it is one directory away from the real one.

That is the whole failure mode: an artefact that is WRONG, INVISIBLE TO EVERY
CHECK, and INDISTINGUISHABLE WHEN OPENED. The cost was an hour of hunting for
a revert that had never happened.

WHAT THIS GUARD DOES, in two parts, because the class has two shapes.

    1. NO NESTED CHECKOUT. Any directory holding a `.git` entry below the
       repository root is a whole second tree at some other commit. Worktrees
       are the common case and scratch clones are the other.
    2. NO SHADOW COPY OF A COMMITTED FIGURE. Any file anywhere under the root
       whose name matches a committed figure, sitting outside the directory
       that owns it, whose bytes differ.

WHAT IT DELIBERATELY DOES NOT DO. It does not ban ignored directories, which
would be absurd, and it does not compare documents by name, because a hundred
`README.md` files live in the virtual environment and mean nothing. The
figure check is by name AND content AND location, so a legitimate identical
copy is silently fine and only a DIVERGENT shadow fails.

VERIFIED IN BOTH DIRECTIONS on 2026-08-17. A temporary nested checkout fails
the first half and a one-byte-altered copy of a committed figure fails the
second, an IDENTICAL copy correctly does not, and removing each returns the
guard to green.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Directories that are someone else's tree by construction and are not this
# repository's business to police. `.venv` is an installed environment and
# `node_modules` is listed for the day one appears.
_SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache",
              ".ruff_cache", ".mypy_cache"}

# Where a figure legitimately lives. A copy inside one of these is the real
# thing, not a shadow.
_FIGURE_HOMES = ("figures", "docs/wiki/figures")


def _walk(root: Path):
    """Every file under root, INCLUDING ignored ones, minus the skip list.

    os.walk rather than git ls-files: the entire point is to see what git
    does not, since an ignored copy is exactly the case that went unnoticed.
    """
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def _tracked(pattern: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", pattern],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    return [line for line in out.stdout.split("\n") if line]


def _digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_no_nested_checkout_below_the_root():
    """A second working tree under this one is a stale copy waiting to happen.

    Worktrees are useful and this does not forbid making them. It forbids
    LEAVING them: remove one when its work lands, and prune after. Three
    abandoned ones produced the 2026-08-17 report of a reverted figure.
    """
    nested = []
    for dirpath, dirnames, _ in os.walk(ROOT):
        if Path(dirpath) == ROOT:
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            continue
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        if ".git" in os.listdir(dirpath):
            nested.append(str(Path(dirpath).relative_to(ROOT)))
    assert not nested, (
        "these directories hold a whole second checkout of this repository, at "
        "whatever commit they were made. Their files are ignored, so no guard "
        "here reads them and GitHub never sees them, and a figure or document "
        "opened from one is indistinguishable from the real one:\n  "
        + "\n  ".join(sorted(nested))
        + "\n  Remove with `git worktree remove --force <path>` then "
          "`git worktree prune`, or delete the directory if it is a stray "
          "clone. BEFORE removing, read its `git status` and its diff: one of "
          "the three removed on 2026-08-17 carried an uncommitted repair, "
          "which happened to be on main already but was claimed to hold "
          "nothing unique before anyone had looked.")


def test_no_divergent_shadow_copy_of_a_committed_figure():
    """A file named like a committed figure, living elsewhere, differing.

    By name AND content AND location, so an identical copy is fine and only a
    divergent one fails. That is the shape the 2026-08-17 hunt turned on: the
    shadows were byte-different from the committed drawing and looked
    plausible on their own.
    """
    committed: dict[str, Path] = {}
    for home in _FIGURE_HOMES:
        for rel in _tracked(f"{home}/*.png"):
            committed[Path(rel).name] = ROOT / rel
    if not committed:
        pytest.skip("no committed figures to shadow")

    homes = tuple((ROOT / h).resolve() for h in _FIGURE_HOMES)
    shadows = []
    for p in _walk(ROOT):
        if p.name not in committed:
            continue
        if p.resolve().parent in homes:
            continue                      # the real thing, in its own home
        if _digest(p) != _digest(committed[p.name]):
            shadows.append(str(p.relative_to(ROOT)))
    assert not shadows, (
        "these files carry the name of a committed figure and different bytes, "
        "from outside the directory that owns it. A reader who opens one sees "
        "a plausible figure that no guard checks and no commit contains:\n  "
        + "\n  ".join(sorted(shadows))
        + "\n  Delete them, or if one is the version that should ship, "
          "regenerate the committed figure from its producer instead of "
          "copying the file into place.")

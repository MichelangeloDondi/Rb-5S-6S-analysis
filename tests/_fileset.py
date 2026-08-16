"""The file list a guard should read: what this commit would ship.

WHY THIS MODULE EXISTS. `git ls-files` lists TRACKED files only, so a brand
new document is invisible to any guard built on it until someone stages it.
Write the file, run the gate, watch it pass, then add and commit, and the gate
never saw the thing that shipped. The gated tree and the pushed tree differ by
exactly the visibility of that file.

That has now happened twice. On 2026-08-13 a new test file's banned phrase
shipped through `test_repo_hygiene`. On 2026-08-15 `docs/HISTORY.md` shipped
in `0caf19a5` carrying a semicolon the prose ratchet has always banned, and
the commit was reported green.

Both times the remedy was written locally and did not travel. After the first
incident `test_repo_hygiene` grew `_about_to_be_tracked` and used it in seven
of its own checks, leaving four others on the bare tracked-only call in the
same file. After the second, the prose ratchet was repaired on its own. A
sweep on 2026-08-15 then found fourteen call sites across nine test modules
building the same list by hand, each with the same gap.

So the list lives here once, and guards import it. Protocol rule 19.24 states
the discipline (stage before gating). This module is the mechanism that makes
obeying it unnecessary for correctness rather than merely advisable.

THE SECOND HALF, which is the opposite defect. Several guards instead walk the
filesystem with `rglob` and a hand-maintained denylist of directories to skip
(`.venv`, `private`, `node_modules`, dot-directories). Those see content git
would never ship, and the denylist goes stale the moment a new ignored path
appears. `tracked_and_new` has that behaviour correctly by construction: it
asks git, so anything ignored is excluded and no list needs maintaining.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), *args],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return []
    return [p for p in out.stdout.split("\n") if p]


def tracked(*globs: str) -> list[str]:
    """Repo-relative paths git already tracks, matching `globs`."""
    return _git("ls-files", *globs)


def about_to_be_tracked(*globs: str) -> list[str]:
    """Repo-relative paths git would add on the next `git add -A`.

    Untracked and NOT ignored, so scratch files under an ignored directory
    stay out while a genuinely new document comes in.
    """
    return _git("ls-files", "--others", "--exclude-standard", *globs)


def tracked_and_new(*globs: str) -> list[str]:
    """What this commit would ship: tracked, plus untracked and not ignored.

    This is the list a content guard wants. Use it instead of a bare
    `git ls-files` (which misses new files) and instead of `Path.rglob` with a
    hand-maintained skip list (which sees ignored ones).
    """
    return sorted(set(tracked(*globs)) | set(about_to_be_tracked(*globs)))


def existing(paths: list[str]) -> list[str]:
    """Drop entries with no file on disk, which is what a staged deletion looks
    like between `git rm --cached` and the write."""
    return [p for p in paths if (ROOT / p).exists()]

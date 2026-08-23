"""No second file may wear a committed script's name.

THE FAILURE, 2026-08-20 and again 2026-08-23. `scripts/port_to_mirror.sh` is
committed in both repositories, excludes `.github/` from the port, and carries
a comment naming the incident that taught it: the mirror's workflow is the
reference green check with push triggers while the archive's is dispatch-only,
and the mirror's own `test_ci_triggers.py` caught the first port that ignored
that. It also has a `--check` mode for parity.

A 41-line script of THE SAME NAME was then written beside it, in a scratchpad,
and copied `.github/` at line 38. It disabled the public repository's CI
trigger. The commit that did it is in the log under my name, and a commit three
days earlier is titled "Restore the mirror's own CI triggers after the whole
tree port", so it was the second occurrence in three days.

WHY THE NAME IS THE WORST PART, and why this file exists rather than a note.
An outside reviewer investigated, read the COMMITTED `port_to_mirror.sh`, found
the exclusion and the comment, and concluded correctly from the evidence
available that the port could not have written the workflow. **A shadowing name
makes a failure unattributable.** The knowledge was encoded, in the right tool,
with its history attached. It was bypassed by not being looked for.

So the rule is two halves and only the first is usually stated. Encoding a rule
in the right tool is necessary. **Being found is the other half**, and a name
that is already taken is the cheapest way to be found.

THE BLAST RADIUS, measured before this file was written, per the lesson the
distribution ratchet taught the same week. 92 committed scripts. Zero tracked
`.py` or `.sh` outside `scripts/` shares a basename with one, so this ships as
a hard assertion at zero rather than as a ratchet. Restricting to executables
is deliberate and was measured too: 13 tracked `README.md` files collide with
`scripts/README.md`, and a guard that fired on those would be relaxed into
uselessness within a day.

THE BLIND REGION, stated because a guard's blind region matters more than its
holes.

  tested             tracked files in this repository
  UNTESTED           untracked files, and anything outside the repository
  false negative     the actual 2026-08-23 incident, which lived in a
                     scratchpad directory OUTSIDE the tree, where no in-tree
                     check can ever see it
  false positive     a deliberate vendored copy that legitimately shares a
                     name, which would have to be renamed or exempted here

**That false-negative row is not a defect to be fixed later, it is the shape of
the problem.** No test living in a repository can see a file that is not in it.
What this guard actually buys is that the shadow cannot be COMMITTED, which is
the step at which a scratchpad experiment becomes part of the record and starts
misleading audits. One untracked shadow exists today, a stashed copy of
`verify_results_fresh.py` under `private/`, which is gitignored and is a
deliberate snapshot of a mirror state rather than a tool anyone runs.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]

# Only executables. Documentation basenames collide by design: every directory
# carries a README.md and scripts/ is a directory.
EXECUTABLE_SUFFIXES = {".py", ".sh"}


def _tracked() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return out.stdout.splitlines()


def _committed_script_names() -> set[str]:
    return {
        Path(p).name
        for p in _tracked()
        if p.startswith("scripts/") and Path(p).suffix in EXECUTABLE_SUFFIXES
    }


def _shadows(paths: list[str], names: set[str]) -> list[str]:
    return [
        p
        for p in paths
        if not p.startswith("scripts/")
        and Path(p).suffix in EXECUTABLE_SUFFIXES
        and Path(p).name in names
    ]


def test_no_tracked_file_shadows_a_committed_script():
    names = _committed_script_names()
    assert names, "no committed scripts found, the guard would pass vacuously"

    shadows = _shadows(_tracked(), names)

    assert not shadows, (
        "a tracked file wears the name of a committed script. Rename it. A "
        "duplicate name does not merely invite running the wrong tool, it makes "
        "a later audit read the RIGHT tool and clear the wrong one, which is "
        "how the CI trigger incident was nearly filed as innocent.\n  "
        + "\n  ".join(shadows)
    )


def test_the_finder_sees_a_planted_shadow():
    """The ceiling test. A guard that has only passed on valid inputs has not
    demonstrated that it detects its intended failure mode, and this one would
    pass forever on an empty name set or a suffix typo."""
    names = {"port_to_mirror.sh", "verify_results_fresh.py"}

    planted = [
        "scripts/port_to_mirror.sh",          # the original, must NOT flag
        "tools/port_to_mirror.sh",            # the exact 2026-08-23 failure
        "private/verify_results_fresh.py",    # the untracked-stash shape
        "docs/README.md",                     # documentation, must NOT flag
        "scripts/sub/port_to_mirror.sh",      # nested under scripts, allowed
        "notes/port_to_mirror.txt",           # not an executable suffix
    ]
    found = _shadows(planted, names)

    assert found == ["tools/port_to_mirror.sh", "private/verify_results_fresh.py"], found


def test_the_guard_is_not_vacuous_on_this_repository():
    """The set it checks against must be non-trivial, or a rename of the
    scripts directory would silently switch the guard off."""
    names = _committed_script_names()
    assert len(names) > 50, f"only {len(names)} committed scripts seen, expected many"
    assert "port_to_mirror.sh" in names, "the tool that produced this guard is missing"

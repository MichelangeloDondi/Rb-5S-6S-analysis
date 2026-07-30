"""The two repositories need OPPOSITE CI triggers, and a cherry-pick nearly
erased the difference.

The private archive's Actions are billing-blocked: every job fails in 2-3 seconds
without starting. Scheduling them produced a red run and a failure email per
push, so on 2026-07-30 its workflow became `workflow_dispatch` only. The public
mirror is the opposite case -- public repos get free Actions, and it is the
reference green check, so it must run on every push.

That change propagated to the mirror silently. `.github/workflows/tests.yml` is
on `sync_public.sh`'s DIVERGENT list, but that list only tells a human to expect
a conflict; git conflicts on differing REGIONS, and the two `on:` blocks were
identical before the edit, so the cherry-pick applied cleanly and left the mirror
with a header promising "the full battery runs on EVERY push" above triggers that
said otherwise. The mirror would have gone quiet with nothing red to notice.

So the invariant is asserted here rather than trusted to a conflict:

    public mirror  ->  `on:` MUST include push
    private archive ->  `on:` must NOT include push (while billing is blocked)

Which repo a checkout is decides itself from the raw traces: the archive has
data_raw/p_sweep, the mirror deliberately does not.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
IS_ARCHIVE = (ROOT / "data_raw" / "p_sweep").is_dir()


def _triggers():
    """The keys of the workflow's `on:` block, without a yaml dependency.

    PyYAML parses the bare key `on` as the boolean True, which is a trap worth
    avoiding entirely -- this reads the block textually instead.
    """
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    keys, inside = [], False
    for ln in lines:
        if ln.startswith("on:"):
            inside = True
            continue
        if inside:
            if ln.startswith("jobs:"):
                break
            if ln[:1] not in (" ", "\t", "") and not ln.startswith("#"):
                break
            stripped = ln.strip()
            if (ln.startswith("  ") and not ln.startswith("    ")
                    and stripped.endswith(":") and not stripped.startswith("#")):
                keys.append(stripped[:-1])
    return keys


@pytest.mark.skipif(not WORKFLOW.exists(), reason="no workflow in this checkout")
def test_ci_triggers_match_the_repository_they_are_in():
    trig = _triggers()
    assert trig, f"could not parse an `on:` block from {WORKFLOW}"
    if IS_ARCHIVE:
        assert "push" not in trig, (
            f"the ARCHIVE workflow has a push trigger ({trig}). Its Actions are "
            "billing-blocked, so every push emails a failure for jobs that never "
            "start. Remove push/pull_request, or -- if billing is now cleared -- "
            "delete this branch of the assertion deliberately.")
        assert "workflow_dispatch" in trig, (
            f"the archive workflow must stay runnable by hand ({trig})")
    else:
        assert "push" in trig, (
            f"the PUBLIC mirror workflow lost its push trigger ({trig}). It is "
            "the reference green check while the archive is billing-blocked, and "
            "its own header promises the battery runs on every push. This is "
            "what a cherry-pick from the archive does when the `on:` blocks "
            "happen to match -- restore push and pull_request.")

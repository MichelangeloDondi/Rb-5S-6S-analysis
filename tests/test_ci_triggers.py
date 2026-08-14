"""The two checkouts need opposite CI triggers: the public mirror runs the full
battery on every push and is the reference green check, while the private
archive runs its workflow by hand only.

A cherry-pick between them once erased that difference, because the two `on:`
blocks were identical beforehand and so the patch applied without a conflict.
This test asserts the invariant directly instead of trusting a conflict to
raise it, and a checkout identifies itself by whether the raw traces are
present.
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"
HAS_RAW_TRACES = (ROOT / "data_raw" / "p_sweep").is_dir()


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
    if HAS_RAW_TRACES:
        assert "push" not in trig, (
            f"the ARCHIVE workflow has a push trigger ({trig}). Its Actions do "
            "not run, so every push reports a failure for jobs that never "
            "start. Remove push/pull_request, or -- once the archive can run "
            "Actions -- delete this branch of the assertion deliberately.")
        assert "workflow_dispatch" in trig, (
            f"the archive workflow must stay runnable by hand ({trig})")
    else:
        assert "push" in trig, (
            f"the PUBLIC mirror workflow lost its push trigger ({trig}). It is "
            "the reference green check, and its own header promises the battery "
            "runs on every push. This is what a cherry-pick from the archive "
            "does when the `on:` blocks happen to match -- restore push and "
            "pull_request.")

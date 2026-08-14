"""The one-command reproduction must be able to finish.

WHY THIS EXISTS. On 2026-08-14 `bash scripts/run_all.sh` was run end to end in
an isolated worktree, from the committed traces, for the first time. It failed
after 27 stages with `KeyError: 'status'` in `make_figures.py`, because the
runner called the status annotator LAST while `make_figures.py` and
`make_results_ledger.py` both READ the column the annotator writes. In a
working tree the committed CSVs already carry `status`, so the failure only
appears on a genuine full run, which is exactly what the README, START_HERE,
docs/methods.md and docs/REPRODUCING.md all tell a reader to do.

The rule the runner has to keep is not "the annotator runs last". It is:

    the annotator runs after every WRITER of results/*.csv
    and before every READER of the status column.

`make_figures.py` writes no CSV at all, so it is a pure reader and belongs
after the annotator. Same for `make_results_ledger.py`.

This test reads the shipped runner rather than a copy of it, so it cannot go
stale, and it is deliberately cheap: it checks ORDER, not behaviour, because
checking behaviour means a multi-hour pipeline run that no test suite can
carry.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_all.sh"

# Scripts that consume the status column and therefore must follow the
# annotator. Each is checked to still contain a status read, so that if one
# stops reading the column this list is pruned deliberately rather than
# quietly protecting nothing.
CONSUMERS = ("make_figures.py", "make_results_ledger.py")
ANNOTATOR = "annotate_results_status.py"


def _invocation_lines():
    """The runner's actual `python scripts/X.py` calls, in order."""
    out = []
    for raw in RUNNER.read_text().splitlines():
        line = raw.strip()
        if line.startswith("#") or not line:
            continue
        if "scripts/" in line and line.startswith("python"):
            out.append(line)
    return out


def test_the_annotator_runs_before_everything_that_reads_its_column():
    lines = _invocation_lines()
    assert lines, "no python invocations found in run_all.sh"
    joined = "\n".join(lines)
    assert ANNOTATOR in joined, f"{ANNOTATOR} is not called by run_all.sh"

    ann = next(i for i, s in enumerate(lines) if ANNOTATOR in s)
    for consumer in CONSUMERS:
        idx = [i for i, s in enumerate(lines) if consumer in s]
        if not idx:
            continue
        assert ann < idx[0], (
            f"{ANNOTATOR} is invoked at position {ann} but {consumer} runs at "
            f"{idx[0]}, so a clean `bash scripts/run_all.sh` reaches {consumer} "
            f"with freshly written CSVs that have no status column yet. That is "
            f"the KeyError: 'status' crash of 2026-08-14. Order:\n"
            + "\n".join(f"  {i}: {s}" for i, s in enumerate(lines)))


@pytest.mark.parametrize("consumer", CONSUMERS)
def test_the_consumers_really_do_read_the_status_column(consumer):
    """Keeps the list above honest.

    If a consumer stops reading `status`, this fails and the name is removed
    from CONSUMERS on purpose. Without this, the ordering test could go on
    guarding a dependency that no longer exists and read as protection it is
    not providing.
    """
    src = (ROOT / "scripts" / consumer).read_text()
    assert '["status"]' in src or "'status'" in src, (
        f"{consumer} no longer reads the status column, so it does not need to "
        f"follow the annotator. Remove it from CONSUMERS in this file.")


def test_the_annotator_still_runs_after_the_stage_loop():
    """The other half of the rule, and the reason this is not just a swap.

    The annotator must still follow every writer. The stage loop is where the
    writers are, so the annotator's invocation has to sit after the loop's
    `done`, not inside it and not before it.
    """
    text = RUNNER.read_text()
    done = text.index("\ndone")
    ann = text.index(ANNOTATOR, done)
    assert ann > done, (
        "annotate_results_status.py must be invoked after the stage loop "
        "closes, because every stage in that loop writes a CSV it annotates.")

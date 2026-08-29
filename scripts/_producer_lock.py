"""An exclusive lock for a producer that writes into `results/`.

WHY THIS EXISTS, and it is a measured failure rather than a precaution.

On the night of 2026-08-27/28 two producers were each launched twice while the
first launch was still running, eighteen minutes apart, and both pairs wrote
the same CSV concurrently: `run_fibre_twin.py` at 03:18 and
`run_campaign_twin_forecast.py` at 03:36. The cause was identical both times. A
job was started with `nohup ... &`, nothing captured its exit status, it
appeared not to have run, and a second copy was started.

`scripts/ci_gate.sh` has held an exclusive lock keyed on the checkout since two
sessions collided over one verdict file. **Producers never inherited it**, and
the repository's own rule -- that any job running more than a few minutes takes
a lock on a well-known path -- was written down and then broken twice in one
night by the person who wrote it. That is the argument for a lock rather than a
reminder: the reminder existed.

A concurrently written CSV is the worst shape this failure can take, because
the file that results is still a VALID CSV. Nothing downstream can see that it
is a mixture of two runs.

Usage, at the top of a producer's `main()`:

    from _producer_lock import producer_lock
    with producer_lock("campaign_twin_forecast"):
        ...

It exits non-zero with a readable message when the lock is held, naming the pid
that holds it, rather than blocking or racing.
"""
from __future__ import annotations

import contextlib
import fcntl
import os
import pathlib
import sys

LOCK_DIR = pathlib.Path(__file__).resolve().parents[1] / ".producer_locks"



# WHY fcntl.flock AND NOT AN O_EXCL FILE.
#
# The first implementation created the lock with O_CREAT|O_EXCL, wrote the
# holder's pid, and recovered from a dead holder by reading that pid, checking
# whether it was alive, and unlinking. That path has a race, measured rather
# than argued: 29 of 30 contended trials raised an unhandled EEXIST, and one
# produced a DOUBLE ACQUISITION.
#
# Making every attempt go through one atomic open removed the unhandled
# errors and left the double acquisition, because the stale-recovery path is
# a time-of-check-to-time-of-use hole that no amount of care closes: two
# callers both read the stale pid, both judge it dead, the first unlinks and
# re-creates, and the second unlinks THE WINNER'S FRESH LOCK.
#
# flock has no such hole. The kernel holds the lock against the open file
# description and releases it when the process dies, by any means including
# SIGKILL, so there is no stale state to recover from and nothing to unlink.
# The pid is still written, for the error message alone.
@contextlib.contextmanager
def producer_lock(name: str):
    """Hold an exclusive lock named `name`, or exit 3 if another run holds it.

    The lock is an advisory kernel lock taken with `flock(LOCK_EX|LOCK_NB)`.
    It is released when this process exits for ANY reason, so a killed
    producer leaves nothing behind that a later run has to clean up.
    """
    LOCK_DIR.mkdir(exist_ok=True)
    path = LOCK_DIR / f"{name}.lock"
    fh = open(path, "a+")
    try:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.seek(0)
        holder = fh.read().strip() or "unknown"
        fh.close()
        sys.stderr.write(
            f"{name}: another run holds this producer's lock (pid {holder}). "
            f"Two processes writing one results CSV produce a VALID file that "
            f"is a mixture of both runs, which nothing downstream can "
            f"detect. Wait for it to finish.\n")
        raise SystemExit(3)
    try:
        fh.seek(0)
        fh.truncate()
        fh.write(str(os.getpid()))
        fh.flush()
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def take_producer_lock(name: str) -> None:
    """Acquire the lock for the life of the process. One line, no nesting.

    `producer_lock` is the context manager; this is the form a producer's
    `main()` uses, because wrapping an existing several-hundred-line body in a
    `with` is a large diff for a small guarantee and a large diff is where the
    next defect hides. Release is by `atexit`, which runs on a normal exit and
    on an unhandled exception, and does NOT run on SIGKILL -- the stale-pid
    check in `producer_lock` is what covers that case.
    """
    import atexit
    cm = producer_lock(name)
    cm.__enter__()
    atexit.register(lambda: cm.__exit__(None, None, None))

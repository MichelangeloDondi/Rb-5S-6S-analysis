"""How many worker processes a producer may use, read in one place.

THE CONTRACT, and it is the whole reason this seam exists. A producer
that accepts workers must write a BYTE-IDENTICAL committed CSV at
every worker count, including zero. The word is CSV and not output:
pooled producers print from inside their workers, so stdout
interleaving is worker-count-dependent by construction and is not part
of the promise.

THE LICENCE IS EMPIRICAL, NOT ARGUED. Determinism-given-inputs is the
reason to expect byte-identity, not a proof of it: the pooled path
pins BLAS to one thread per worker while the sequential path runs
unpinned, and threaded reductions can reorder in the last bits. What
supports the contract is measurement:
`scripts/_m25_parallel_smoke.py` asserts exact equality of both pooled
paths against their sequential twins, and a full-scale run at eight
workers reproduced the committed file, its only deviations traced to a
numpy version change rather than to the pooling. A producer whose
bytes move with the worker count is not faster, it is broken.

WHAT ENFORCES IT, AND WHERE THAT IS VACUOUS.
`scripts/verify_results_fresh.py` calls such a move drift - but only
for a producer it can re-run. A producer that early-returns on an
absent input tree is compared against itself and reports green, so its
row in that file must say so, exactly as the `UNCOVERED` entries for
`stark_joint.csv` and `power_time_sign_test.csv` already do.

ZERO IS THE PATH OF RECORD. The default is sequential, every committed
CSV was produced that way unless its own docstring says otherwise, and
a reader who sets nothing gets exactly the committed numbers.

AND THE COLLAPSE TO ZERO NOW SPEAKS, because the silence was the whole
defect. The clamp above prints when a caller asks for MORE than the
machine has; the fall back to sequential printed nothing, so a producer
launched by hand ran on one core of ten and looked exactly like a
producer running correctly. Measured 2026-09-16: an ultra-joint
regeneration launched with nothing set took 3m42s for two of
seventy-eight cells before anyone noticed, against roughly five times
that throughput once RB5S6S_WORKERS was set. That is the same shape as
the gate splitter's silent collapse, which `gate_split` was taught to
narrate for the same reason: the number is cheap and the silence is
what costs. `RB5S6S_WORKERS_QUIET=1` silences it for a caller that
means sequential, which `verify_results_fresh` does.

THE TENSION THIS MAKES VISIBLE, rather than resolves. This module says
zero is the path of record; the repository's working rules say ten
workers unless a measured reason says fewer and the reason is printed.
Both are right about what they guard -- byte-identity against idle
cores -- and nothing reconciles them, so the announcement states the
cost and leaves the choice with the caller.

THE CEILING IS DELIBERATE. Unattended operation runs gates and
sessions beside these jobs, so a request above `MAX_WORKERS` is
clamped rather than honoured, and the clamp says so on stderr instead
of silently doing something else.

Failure mode this module guards against: each producer reading the
environment its own way, so that the contract above is stated four
times, drifts in three of them, and is enforced in none.
"""
from __future__ import annotations

import os
import sys

ENV_VAR = "RB5S6S_WORKERS"

# EVERY CORE (owner, 2026-09-14): the two-core holdback below was a cap no
# measurement set; the memory-justified pool is decided per run by the caller,
# and this ceiling is only what the machine has.
MAX_WORKERS = max(1, os.cpu_count() or 10)  # every core; the old cores-minus-two was a cap no measurement set (2026-09-14)


_announced = False


def _announce_sequential(src, why: str) -> None:
    """Say, ONCE per process, that this run will use one core of many.

    Silent on a single-core machine, where there is nothing to report, and
    under RB5S6S_WORKERS_QUIET for a caller that means sequential.
    """
    global _announced
    if _announced or MAX_WORKERS <= 1 or src.get("RB5S6S_WORKERS_QUIET"):
        return
    _announced = True
    print(f"workers: SEQUENTIAL ({why}); this run will use 1 core of "
          f"{MAX_WORKERS}. Set {ENV_VAR}=<n> to pool it -- the contract above "
          f"promises a byte-identical CSV at every worker count.",
          file=sys.stderr)


def n_workers(env: dict[str, str] | None = None) -> int:
    """The requested worker count, clamped, with 0 meaning sequential.

    Anything unparseable is 0: a typo must fall back to the path of
    record rather than to a guess.
    """
    src = os.environ if env is None else env
    raw = src.get(ENV_VAR, "0")
    try:
        n = int(raw)
    except ValueError:
        _announce_sequential(src, f"{ENV_VAR}={raw!r} is not an integer")
        return 0
    if n <= 0:
        _announce_sequential(src, f"{ENV_VAR} unset" if ENV_VAR not in src
                             else f"{ENV_VAR}={raw}")
        return 0
    if n > MAX_WORKERS:
        print(f"{ENV_VAR}={n} exceeds MAX_WORKERS={MAX_WORKERS}; "
              f"using {MAX_WORKERS}", file=sys.stderr)
        return MAX_WORKERS
    return n

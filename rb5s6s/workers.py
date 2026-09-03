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

# Two cores held back so a gate and a session stay responsive beside a
# pooled producer. DERIVED, not written: eight is right for the ten-core
# machine this record is developed on and wrong for a two-core runner,
# where a fixed eight would give no headroom and invert the reason. The
# ceiling cannot touch a committed number, because the contract above
# makes the bytes invariant to the worker count - so deriving it costs
# nothing and keeps the stated reason true everywhere.
MAX_WORKERS = max(1, (os.cpu_count() or 4) - 2)


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
        return 0
    if n <= 0:
        return 0
    if n > MAX_WORKERS:
        print(f"{ENV_VAR}={n} exceeds MAX_WORKERS={MAX_WORKERS}; "
              f"using {MAX_WORKERS}", file=sys.stderr)
        return MAX_WORKERS
    return n

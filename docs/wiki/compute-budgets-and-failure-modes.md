# Compute budgets and failure modes

*[wiki index](README.md) · method*

**The question.** Will a planned parallel fit or scan fit inside the
machine's memory, and can that be known before launch rather than by
watching it crash.
**Takes.** Nothing beyond arithmetic. No prior wiki page is required.
**Gives.** The per-worker memory estimate, the arithmetic that multiplies it
by worker count against a machine budget, and the discipline for what a
killed run's partial output is and is not.
**Skip if.** The reader wants the companion cost that scales with a trial
count rather than a worker count. That is
[Monte Carlo methods](monte-carlo-methods.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A scientific computation has a resource profile as real as its physics: how
much memory it needs, how long it runs, and how both change when the same
job is split across several workers to go faster. Finding that profile out
by launching the job and watching what happens is a choice, and usually the
wrong one, when a few minutes of arithmetic beforehand would have found it
out instead.

The constraint that most often bites first, and the one this page treats as
the headline case, is memory in a parallel least-squares fit. A least-squares
fit carries a Jacobian, one row per data point and one column per free
parameter, and a solver keeps that matrix resident for as long as the fit
runs, together with a few arrays of comparable size for the residual, the
trust-region step and a QR or SVD factorization of the Jacobian itself. The
memory a single fit needs therefore scales with the PRODUCT of the point
count and the parameter count, not their sum, and a fit that is comfortable
on ten thousand points and a dozen parameters can be uncomfortable on the
same data with several times as many parameters, or on several times as much
data with the same parameters.

Running many such fits in parallel, one per worker process, is the ordinary
way to turn a long queue of independent fits into a short one. Each worker
is a separate process with its own copy of everything the fit needs, so a
machine's memory is divided among however many workers are launched at once,
while its core count is the resource the parallelism is spending time to
buy. A per-fit footprint that is comfortable run one at a time therefore does
not stay comfortable under multiplication: ten workers holding the same
Jacobian each need ten times the memory one of them needed alone, and the
machine's memory, not its core count, is usually the first thing the job
runs into.

Memory failures and wall-time failures differ in character as well as in
cause. A process that crosses a fixed memory ceiling is usually killed
outright, an abrupt and legible failure. A process that is merely slow
degrades instead, sometimes because the operating system starts paging
memory to disk rather than refusing it outright, which can leave a run
appearing to progress for hours while doing almost no useful work.

## What problem it solves

Doing the arithmetic first replaces a launch-and-see approach with a short
calculation: estimate one fit's footprint, multiply by the number of workers
planned, and compare the total against the machine's memory. If the total
already exceeds the ceiling, nothing needs to run to discover that, and the
worker count or the size of each fit can be corrected before any wall time
is spent. A failed overnight run costs the night. The arithmetic that would
have predicted the failure costs a minute, and that asymmetry alone is the
case for doing it before launching rather than after.

The same care applies to what a run is allowed to do when it is stopped
before finishing, by a wall-clock timeout or by exhausting its memory
budget. A killed run produces whatever it had written up to that point, and
that partial output is not a random sample of what the finished run would
have produced. The cells that had already completed are the fast ones, or
the ones queued first, or the ones whose starting point happened to converge
quickly, never a representative draw across the grid the run was meant to
cover, so treating a partial result as a shrunken version of the intended
one substitutes a biased sample for the planned measurement without saying
so.

A related discipline governs what happens to the run itself once it has
failed. A script whose run did not complete should not be discarded before
it is recorded, because the reason it needed as much memory or as much time
as it did is information about the job, not only about the number the job
failed to produce. An instrument that produced nothing under a given load is
still the thing that would have to be repaired before the same job is
attempted again, and deleting it along with its unfinished output deletes
the ability to diagnose why it failed or to size the next attempt correctly.
Checkpointing, writing intermediate state to disk often enough that a killed
run can resume near where it stopped rather than from the beginning, and
simply reducing the worker count so each surviving worker gets a larger
share of the machine's memory, are the two standard remedies once the
arithmetic shows a job will not fit as planned.

## Where this repository uses it

The global dataset fit chain in
[`scripts/run_global_dataset_fit.py`](../../scripts/run_global_dataset_fit.py)
is exactly the shape this page describes. Its kappa profile and its waist
scan each run a warm-started least-squares chain that holds its own Jacobian
and solver state, and an optional parallel path, controlled by the
`RB5S6S_WORKERS` environment variable and implemented in `n_workers()` and
`profile2d()`, hands one such chain to each worker in a process pool. Because
every worker rebuilds its own residual and Jacobian machinery from scratch
rather than sharing state with its siblings, the memory argument above
applies directly rather than by analogy: the total footprint scales with the
worker count exactly as it does for any other parallel fit built this way.
That is stated in `n_workers()`'s own docstring as the reason the default
worker count is zero, sequential, described there as "the default and the
path of record," rather than the machine's full core count. The parallel
path is trusted only once
[`scripts/_m25_parallel_smoke.py`](../../scripts/_m25_parallel_smoke.py)
shows it reproduces the sequential chi-squared exactly, cell for cell, on a
small grid, before the same machinery is turned loose on the production-sized
one.

The same file's `_preflight()` function carries this repository's own
instance of the timeout-and-discipline point above, recorded there as
"Lesson 44": three hours of a run were lost when the operating system
withdrew read access to an input tree partway through, and the failure
surfaced six stack frames deep inside the multiprocessing library's own
startup code as an unhelpful permission error. The fix was not a longer
timeout but a cheap check run before the expensive part starts, testing
every path the run needs and naming the likely cause in a sentence a reader
can act on, so that a run measured in hours fails, when it is going to fail,
in seconds rather than after most of the wall time is already spent.

This repository has also paid for the mirror-image mistake directly, in an
earlier attempt at the same kappa grid. Splitting it across many worker
processes at once exhausted the machine's memory before the grid finished,
the run had to be killed partway through, and what it had written by then
was correctly not treated as a result, since the cells that had finished
were the ones that happened to run first rather than a representative sample
of the grid. The script from that attempt was not kept, because nothing
that had not finished seemed worth keeping at the time, which is the exact
mistake the section above warns against, learned once rather than argued for
in the abstract. The corrected practice budgets a candidate worker count
against the machine before launching, with the arithmetic shown in
[Try it](#try-it) below, instead of discovering the ceiling by crossing it.

## What can go wrong

The bare point-count-times-parameter-count estimate is a lower bound on a
fit's memory, not the actual figure. A solver keeps the Jacobian's residual,
its trust-region step and a QR or SVD factorization alongside the matrix
itself, so the true footprint runs to a few times the bare estimate, and
budgeting to the bare number under-provisions the real run.

A worker count is not free merely because the machine reports that many
cores. Cores and memory are independent resources, and a machine can hold
far more of one than the job's own arithmetic allows of the other, so the
binding constraint has to be checked rather than assumed to be whichever one
is easier to name.

Swapping is a quieter failure than an outright kill and is often worse to
diagnose. A run that crosses its memory budget by a little rather than a lot
may not be killed at all, and instead forces pages to disk, which slows
every worker by orders of magnitude without ending the run, so a job that
"is still going" long past its estimate may not be making progress, only
paging.

Checkpointing is only a safeguard once a real restart has exercised it. A
checkpoint that is written on schedule but never used to resume an
interrupted run is an untested assumption wearing the shape of a
precaution, and the gap tends to surface only during the failure it was
meant to cover.

## Try it

A hypothetical fit chain, several hundred thousand points combined across
many traces, against a joint model whose few shared physical parameters are
joined by one nuisance parameter per trace, running to a couple of hundred
parameters in total, sized under a rising worker count against a stated
machine budget. The per-worker footprint stays fixed. The total does not,
and it crosses the stated ceiling well before the worker count reaches the
values that would deliver a useful speed-up.

```python
def jacobian_gb(n_points, n_params, overhead=3.0, dtype_bytes=8):
    """Rule-of-thumb resident footprint of one running least-squares fit,
    in gigabytes: the dense Jacobian itself (n_points by n_params, one
    float64 entry per point per parameter) times a small multiplier for
    the residual, the trust-region step and the QR or SVD factors a
    solver such as scipy.optimize.least_squares keeps alongside it while
    it runs. `overhead` is a rounded estimate, not an exact accounting."""
    bare_bytes = n_points * n_params * dtype_bytes
    return bare_bytes * overhead / 1e9


n_points, n_params = 500_000, 200
machine_ram_gb = 16.0
per_worker_gb = jacobian_gb(n_points, n_params)

print(f"one fit: {n_points} points, {n_params} parameters")
print(f"estimated footprint per worker: {per_worker_gb:.2f} GB")
print(f"machine budget: {machine_ram_gb:.0f} GB\n")
print(f"{'workers':>8}{'total footprint':>19}{'fits on this machine':>24}")
for n_workers in (1, 2, 4, 8, 10, 16, 32):
    total_gb = per_worker_gb * n_workers
    fits = "yes" if total_gb <= machine_ram_gb else "no"
    print(f"{n_workers:8d}{total_gb:16.2f} GB{fits:>24}")

max_workers = int(machine_ram_gb // per_worker_gb)
print(f"\nmax workers this machine can hold: {max_workers}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- [SciPy: `scipy.optimize.least_squares`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html),
  for what a trust-region solver keeps resident while it runs and for the
  Jacobian-sparsity option this repository's own fit chain uses to shrink
  it.
- G. H. Golub and C. F. Van Loan, *Matrix Computations*, 4th ed. (Johns
  Hopkins University Press, 2013), for the memory cost of the QR and SVD
  factorizations a least-squares solver builds on.
- [Monte Carlo methods](monte-carlo-methods.md), for the companion case
  where a computation's cost is multiplied by a trial count rather than by a
  worker count, and needs the same arithmetic before it is launched.
- [Preregistration](preregistration.md), for the companion discipline of
  committing to what a run's outcome counts as before the run itself decides
  it by exhaustion rather than by design.

## See also

- [Methods chapter 6](../methods/06_the_statistics.md), whose Jacobian and
  SVD memory discussion is the worked version of this page's arithmetic.
- [Optimiser convergence](optimiser-convergence.md), the multi-start and
  bidirectional scans this page's memory arithmetic has to be run against
  before either is launched at scale.
- [Grids and discretisation](grids-and-discretisation.md), the point-count
  side of the same product that sets a fit's Jacobian size.
- [Monte Carlo methods](monte-carlo-methods.md), the companion computation
  whose cost multiplies by a trial count rather than a worker count.
- [Preregistration](preregistration.md), for committing to a run's stopping
  condition before a memory or wall-time ceiling makes that decision by
  exhaustion instead.

---

[← Optimiser convergence](optimiser-convergence.md) · *Simulation and computation, 4 of 4* · [wiki index →](README.md)

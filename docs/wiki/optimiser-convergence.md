# Optimiser convergence

*[wiki index](README.md) · method*

**The question.** Does a fit's convergence flag mean it found the surface's
true minimum, or only a stationary point somewhere nearby.
**Takes.** A parameter fit and its optimiser's stopping report. No prior
wiki page is required.
**Gives.** The three defences against a trapped scan, starting from several
places, chaining a scan in both directions, and a refitted audit, and why
only the audit tests a finished result rather than the process that built
it.
**Skip if.** The reader wants the correlated-parameter valleys a fit gets
trapped inside, ahead of the trapping mechanism itself. That is
[identifiability](identifiability.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A fit reports success once its optimiser's own stopping rule is satisfied.
That rule is local and mechanical: the step size has fallen below a
tolerance, the gradient has fallen below a tolerance, or the objective has
stopped improving from one iteration to the next. None of the three asks
whether the point the optimiser stopped at is the lowest the surface has
anywhere. Each asks only whether the immediate neighbourhood of the current
point looks flat enough that another step would not move things much. A
point that clears every stopping rule can still sit in a local minimum, with
a deeper one elsewhere on the surface that the optimiser never visited and
has no way of knowing about.

This gap is sharpest where parameters exchange against each other, because a
likelihood surface with correlated parameters is rarely a bowl with one
obvious floor. It is closer to a surface carrying a long, shallow valley:
a direction along which moving one parameter and compensating with another
leaves the objective almost unchanged over a wide stretch. An optimiser
dropped anywhere in that valley slides to the nearest point where the local
gradient vanishes and stops, reporting convergence, without ever asking
whether the valley connects to somewhere lower or whether a separate valley
elsewhere is deeper still.

The distinction worth holding onto is between two questions that the single
word "converged" is sometimes made to answer for both. The optimiser's
question is local: did the step size and the gradient shrink the way the
algorithm expects near a stationary point. The statistical question is
global: is that stationary point the minimum the objective actually has,
among however many stationary points the surface carries. An optimiser can
answer the first question correctly and say nothing at all about the second,
and the two get conflated whenever a convergence flag is read as a
correctness flag.

Warm starting sharpens the gap rather than closing it. Seeding a fit from the
solution of a neighbouring one, a nearby grid cell in a scan or a nearby
condition in a sweep, is standard practice because it is fast and because a
smoothly varying problem usually has a smoothly varying solution. But if the
very first cell of a scan lands in the wrong valley, warm starting carries
that choice forward rather than correcting it: every neighbour inherits a
seed already inside the same valley, follows the local gradient down to the
same local floor, and reports the same clean convergence its neighbours did.
The output is a surface that is smooth, that varies plausibly from one
condition to the next, and that is wrong across its whole extent, because the
one decision that mattered was made once, by accident, at the first cell, and
never revisited.

Three defences follow directly from where the exposure sits. Starting the search
from several places, including a start deliberately far from anywhere a
neighbour's solution would put it, gives the true minimum more than one
chance to be found. Running a scan in both directions across its grid and
keeping the better result at every point turns a single point of failure,
the first cell, into two chains that would have to fail the same way
independently. And auditing a finished surface by refitting a sample of its
points from fresh, uncontaminated seeds and checking that none of them
improves is the only one of the three that examines the result itself rather
than the process that produced it.

## What problem it solves

Naming the gap between the two questions above is what stops a converged fit
from being read as a correct one. Without it, a smooth run of results across
a scan looks like confirmation: nothing jumps, nothing resembles a bug, every
individual fit reports success. That smoothness is exactly what a trapped
scan produces, so it cannot be used as evidence that the scan is
trustworthy. Treating convergence and correctness as one question removes
the single signal, an isolated fit failing to converge, that would otherwise
have raised a flag, so the failure is silent almost by construction and
needs a defence that does not depend on the optimiser noticing its own
mistake.

## Where this repository uses it

The joint Stark-shift profile in
[`scripts/run_stark_joint.py`](../../scripts/run_stark_joint.py) scans its
parameter with a bidirectional, warm-chained construction: a forward chain
across the grid from a cold start, a backward chain run the other way from
the forward chain's far end, and, for the primary variant, a chain seeded
from the solution the wing-robustness variant's own cold start finds, since
that variant is the one that locates the true local minimum reliably first.
The pointwise minimum across every chain is what enters the profile, so a
seed can only improve the result, never worsen it.
[`docs/RESEARCH_DECISIONS.md`](../RESEARCH_DECISIONS.md) section 11 records
why the structure exists: an earlier run's primary cold chain parked in a
false minimum far above the true one, and a comparison between two scan
directions was computed on that stuck profile before a seeded twin caught
the gap.

The two-width profile map behind [identifiability](identifiability.md) runs
its defence at the level of individual grid cells rather than whole chains.
Each cell in [`rb5s6s/identifiability.py`](../../rb5s6s/identifiability.py)
is warm-started from its neighbour in the scan, refit again from an
independent lineage arriving from the row above, and, at a fixed stride,
refit once more from a fresh seed untouched by any neighbour's solution. Any
improvement the fresh seed finds is accepted into the map rather than
discarded. The largest improvement found this way, over the whole audited
sample, is committed as `audit_max_gain` in
[`results/identifiability.csv`](../../results/identifiability.csv),
separately for the zoomed grid and the wide grid, and it stands as a bound
on how far any warm-started cell in the map could still be sitting from its
true floor. Both figures the audit produced are small next to the contour
scale the module itself compares them against, which is what licenses
treating the warm-started map as trustworthy rather than merely smooth.

Both usages sit underneath [the profile likelihood](profile-likelihood.md):
a profile is a long chain of individual fits, one per grid point, and its
trustworthiness as a whole is exactly the question this page asks, answered
once per point on the curve.

## What can go wrong

The central failure is the one described above: a warm-started scan whose
first cell fell into the wrong valley produces a surface that is smooth,
internally consistent, and wrong everywhere at once. Nothing about any
single fit's convergence report distinguishes this case from a scan that
found the right valley throughout, because every individual fit genuinely
did converge, to a real stationary point, by every mechanical measure the
optimiser has.

A second failure sits in scanning one direction only. The first point then
carries the whole chain and nothing downstream can correct it. Comparing a
forward pass against a backward one turns that single point of failure into
two chains that would have to land in the same wrong valley independently,
which is far less likely, and any point where the two disagree is a direct
flag rather than something inferred from a surface that merely looks a
little off.

A third failure is trusting an audit that never really tested anything. An
audit that refits nothing, or whose stride happens to land only on cells the
warm start already got right, reports zero improvement for the wrong reason
and licenses a surface it never actually challenged. An audit is
informative only when its sample is large enough, and reported as such, to
have a real chance of landing on a trapped cell if one is there.

The refitted audit is the defence that matters most, because it is the only
one of the three that can catch trapping after the fact, on a surface that
already exists. Starting from several places and comparing both directions
of a scan are built into how the surface is generated, and they lower the
chance of trapping happening in the first place, but neither can prove a
finished map is free of it: a bidirectional scan can still agree with itself
if the wrong valley is wide enough to hold the whole grid, and a
good-looking multi-start can still miss a valley none of its starting
points happened to land near. Refitting a genuinely uncontaminated sample
from the finished surface and confirming that none of it improves is the
only step that looks at the result itself rather than at the process that
built it, which is why it is the one recorded as a number rather than
assumed from the shape of the map.

## Try it

A function with a deep global minimum and a shallower secondary minimum
nearby. A warm start standing in for a seed inherited from a neighbouring
cell finds the shallow one, a deliberately cold start finds the true global
minimum, and both report convergence.

```python
import numpy as np
from scipy.optimize import minimize

def f(x):
    x = x[0]
    return (x ** 2 - 1.0) ** 2 + 0.3 * x

warm = minimize(f, [1.0], method="BFGS")
cold = minimize(f, [-4.0], method="BFGS")

print(f"warm start from x0=1.0: x={warm.x[0]:+.4f} f={warm.fun:+.4f} converged={warm.success}")
print(f"cold start from x0=-4.0: x={cold.x[0]:+.4f} f={cold.fun:+.4f} converged={cold.success}")
gap = warm.fun - cold.fun
print(f"both report convergence, the warm start is worse by {gap:.4f}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- *Numerical Optimization* (Springer, 2nd ed., 2006), the standard graduate
  reference on line search and trust region methods, and on starting an
  optimiser from many points as a practical defence against local
  convergence.
- [Identifiability](identifiability.md), for the correlated-parameter
  valleys a converged fit can be trapped inside.
- [The profile likelihood](profile-likelihood.md), the construction whose
  trustworthiness reduces to exactly this question, one grid point at a
  time.
- [`docs/RESEARCH_DECISIONS.md`](../RESEARCH_DECISIONS.md), which records the
  run where an unseeded cold chain parked in a false minimum, and the
  structural fix that followed.

## See also

- [Methods chapter 6](../methods/06_the_statistics.md), which narrates the
  cold-start chain parking in a false minimum, the same incident this page
  cites.
- [Identifiability](identifiability.md), the correlated-parameter valleys a
  converged fit can be trapped inside.
- [The profile likelihood](profile-likelihood.md), the chain of individual
  fits whose overall trustworthiness reduces to exactly this question, one
  grid point at a time.
- [Grids and discretisation](grids-and-discretisation.md), the companion
  question of whether the grid underneath a fit is resolved finely enough to
  trust in the first place.
- [Compute budgets and failure modes](compute-budgets-and-failure-modes.md),
  the resource cost of running the multi-start and bidirectional defences
  this page recommends.

---

[← Grids and discretisation](grids-and-discretisation.md) · *Simulation and computation, 4 of 5* · [Compute budgets and failure modes →](compute-budgets-and-failure-modes.md)

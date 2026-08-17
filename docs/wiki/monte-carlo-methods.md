# Monte Carlo methods

*[wiki index](README.md) · method*

**The question.** What does it mean to compute a number by simulation
instead of by a formula, and how fast does that number sharpen as more
samples are drawn.
**Takes.** A basic sense of sampling and averaging. No other wiki page is
required first.
**Gives.** The $1/\sqrt{N}$ convergence law, the distinction between
simulating from a model and resampling data already in hand, and the seed
discipline that makes a simulated result checkable.
**Skip if.** You want to resample the data already collected rather than
simulate from a fitted model. That is [resampling](resampling.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A Monte Carlo method computes a quantity by simulation instead of by a formula: draw random samples according to some rule, evaluate a function of interest on each one, and average. It earns its place precisely where the direct computation is hard, an integral with no closed form, a distribution with no known shape, or the sampling behaviour of an estimator that only algebra under restrictive assumptions can describe. Sample enough times from the process that generates the number, and the average of the samples converges to the number itself.

How fast it converges is the one law worth carrying everywhere the method is used. For an estimate built by averaging $N$ independent draws, the standard error of that average falls as $\sigma/\sqrt{N}$, with $\sigma$ the standard deviation of the single-sample quantity being averaged. Nothing about that rate depends on what is being estimated, only on how many draws went into it. Cutting the error by a factor of ten therefore costs a factor of a hundred in samples, not ten, because $\sqrt{100}=10$: the first decade of samples buys the first digit, and the next two decades buy only the next one.

The same $1/\sqrt{N}$ rate holds whatever the dimension of the space being sampled. A grid built to evaluate an integral needs more points every time a dimension is added, since keeping the same spacing along every axis multiplies the point count by roughly the same factor each time, so a method that fills a grid becomes impractical once there are more than a handful of dimensions. A Monte Carlo estimate needs the same $N$ for the same precision whether the space sampled has one dimension or fifty, because the draws never have to fill a grid, only to average. That is the property that lets Monte Carlo win once the dimension is high enough to defeat a grid, at the cost of a rate that starts out slower than a good quadrature rule in one dimension.

Two uses of the idea matter for the methods on this wiki, and they ask different questions of different objects. The PARAMETRIC use samples from an assumed model: draw many synthetic datasets from a fitted line, or from a physical model of the apparatus, at the real design's own points and its own noise law, and see what an estimator run on each one does, its bias, its coverage, or where a comparison statistic falls relative to a threshold. Nothing about the real data enters except through the model already fitted to it. The other use resamples the OBSERVED data rather than a fitted model, which is the bootstrap and the jackknife covered on [resampling](resampling.md) and not repeated here. The distinction matters because a parametric simulation is only as good as the model it draws from, while a resampling of the data is only as good as the sample's own representativeness of the population behind it.

A Monte Carlo result is not evidence unless it can be reproduced to the same numbers. A pseudo-random generator run from an unrecorded starting state produces a different answer on every run, close to the last one but never identical, and a result that shifts every time it is rerun cannot be checked by anyone, including the person who ran it first. The generator's seed is therefore recorded beside whatever the simulation reports, so a disagreement on a rerun points at a real change in the procedure rather than at sampling noise nobody can now separate from one.

VARIANCE REDUCTION changes how the samples are drawn so a given $N$ buys a smaller error than the plain $\sigma/\sqrt{N}$ estimate promises. The most useful case here is COMMON RANDOM NUMBERS: when the goal is a comparison between two or more configurations rather than one estimate on its own, drive every configuration from the SAME underlying draws instead of independent ones. Whatever is shared between the configurations then cancels out of the difference, and the comparison is left showing only what actually changes between them, rather than carrying the full sampling noise each independent simulation would otherwise add on its own account.

## What problem it solves

An integral, a null distribution, or an estimator's own bias and coverage sometimes has no closed form, or has one only under an assumption nobody actually wants to make. Monte Carlo replaces the derivation with a direct simulation of the process being described, so an answer is available even where the algebra is not, at the cost of computer time rather than of an approximation nobody can check. It also replaces a threshold read off an asymptotic table, valid in a large-sample limit that may not be the situation at hand, with a threshold built from the actual design and the actual sample size.

## Where this repository uses it

[Influence diagnostics](influence-diagnostics.md) needed a null distribution for the largest Cook's distance across the four-point width-against-density fits behind the collisional-broadening bound, one construction per peak, each with only two free parameters left after fitting four points. Rather than reading a cutoff off a textbook rule built for a much larger sample, the audit simulated many synthetic datasets from each fitted line, at that peak's own design points and its own measured errors, refit each one, and recorded the resulting maximum Cook's distance, so the eventual comparison ran against the null distribution that specific design would actually produce. [Resampling](resampling.md) is where that construction, and what it found, are recorded in full.

Every simulation instrument in this record fixes a seed rather than leaving the generator wherever it happens to start. [`rb5s6s/config.py`](../../rb5s6s/config.py) carries a seed constant several modules draw on by default, and [`rb5s6s/transit_mc.py`](../../rb5s6s/transit_mc.py) uses it to compute the transit-broadening lineshape itself by simulation, an ensemble of atomic trajectories sampled across impact parameter, transverse speed and position along the beam, rather than by the closed-form approximation described on [transit-time broadening](transit-time-broadening.md). The coverage study behind the headline bound is the same idea turned on an estimator instead of a lineshape: many synthetic datasets drawn from a known truth, recovered through the analysis unchanged, to measure whether a quoted interval covers at the rate it claims. [Injection-recovery testing](injection-recovery.md) is where that construction, and what it found, are recorded.

None of these simulations is run cold. [Preregistration](preregistration.md) is what fixes, before any of them is run, which quantity the simulation is meant to score and at what threshold, so a Monte Carlo built after the real answer is already visible cannot be tuned to agree with it after the fact.

## What can go wrong

A Monte Carlo estimate carries its own sampling error on top of whatever it is estimating, and the two are easy to run together. A rate or a bound quoted from a simulation without the number of trials beside it lets a reader mistake the simulation's own noise floor for a feature of the thing being simulated, the same trap [injection-recovery testing](injection-recovery.md) and [resampling](resampling.md) each name for the constructions they cover. The number of samples belongs beside any figure a simulation produced, for the same reason a measurement's own error bar belongs beside it.

A parametric simulation is only as correct as the model it draws from. If the assumed noise law is wrong, or the model omits a mechanism the real process carries, every simulated dataset inherits the same gap, and the resulting null distribution or coverage figure is confidently wrong in the direction the model is wrong, with no internal sign that anything is off. [Injection-recovery testing](injection-recovery.md) states the general form of this limit directly: closure under the model tests the implementation, not the model.

A generator whose state is shared between the simulation and the code the simulation is meant to test makes the two only partly independent, and the check passes more easily than it should for a reason that has nothing to do with whether the procedure is sound. The same trap sits in feeding an estimator's own fitted values back into a simulation as ground truth, since a recovery of numbers the estimator itself produced is not a test of the estimator.

A rare event or a tail probability is the sharpest case of a general limit. Estimating a probability near the resolution of $1/N$ needs of order $N$ samples just to see the event occur a handful of times, and many more than that to pin its own relative error down, so a plain Monte Carlo undersamples exactly where a threshold set deep in a tail is being read, unless the sampling is redirected toward the tail on purpose.

## Try it

An integral with a known value, estimated by plain Monte Carlo sampling at several sample sizes. At each size several independent replicates are run so the root-mean-square error across replicates, rather than a single lucky or unlucky draw, is what is compared with the $1/\sqrt{N}$ law.

```python
import numpy as np

rng = np.random.default_rng(20260816)
true_value = 2.0  # integral of sin(x) dx from 0 to pi, the known analytic value

print("Monte Carlo estimate of the integral of sin(x) from 0 to pi")
print(f"known value: {true_value:.6f}")
print(f"{'N':>9}  {'replicates':>10}  {'rms error':>10}  {'rms * sqrt(N)':>14}")

sizes = [100, 1_000, 10_000, 100_000, 1_000_000]
budget = 20_000_000  # total draws per row stays bounded, so the run stays fast
prev_rms = None
for n in sizes:
    reps = max(30, min(4000, budget // n))
    x = rng.uniform(0.0, np.pi, size=(reps, n))
    estimate = np.pi * np.mean(np.sin(x), axis=1)
    error = estimate - true_value
    rms = float(np.sqrt(np.mean(error**2)))
    scaled = rms * np.sqrt(n)
    step = f"  decade ratio {prev_rms / rms:.2f}" if prev_rms else ""
    print(f"{n:9d}  {reps:10d}  {rms:10.6f}  {scaled:14.4f}{step}")
    prev_rms = rms
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`, so one that stops working fails the suite rather than sitting here misleading a reader.

## What this repository got wrong once

The transit-broadening Monte Carlo behind [`transit_mc.py`](../../rb5s6s/transit_mc.py) carried a real bug: the sampler weighted each atom by its excitation probability but omitted the atom-crossing flux factor the steady-state rate actually needs, which ran the simulated transit width about two times too narrow and pointed the fitted beam waist at a nominal 32 µm, a value [HISTORY.md](../HISTORY.md) now marks excluded. The flux factor was fixed on 2026-07-13. An earlier attempt at the same fix, before that date, concluded the waist was closer to 90 µm, and that conclusion itself carried an arithmetic error, a spurious factor of two, and was retracted. The corrected Monte Carlo settled on a beam waist of about 50 µm, later replaced by a direct measurement once one became available. HISTORY's beam-waist rows carry the full lineage.

What separated the corrected simulation from the retracted one was not a closer read of the code, since the retracted 90 µm figure had already survived one such read. It was a comparison against an answer the repository did not have to derive: Lehmann's worked transit example, which the closed-form width formula reproduces to 41.2 kHz, the value the corrected Monte Carlo matched. This is the point the sections above make in the abstract, that a Monte Carlo result earns trust by being checked, and here the check that actually caught the error was not a rerun of the same code but a comparison against an independent, external known answer. A self-consistency check against the simulation's own earlier output would have carried the same bug both times.

## Further reading

- [Wikipedia: Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method), for the general history and the family of variants.
- N. Metropolis and S. Ulam, "The Monte Carlo Method," *J. Amer. Statist. Assoc.* **44**, 335 (1949), the paper that named the method.
- C. P. Robert and G. Casella, *Monte Carlo Statistical Methods*, 2nd ed. (Springer, 2004), the standard reference for the parametric use of the method.
- A. B. Owen, *Monte Carlo theory, methods and examples* (2013), for common random numbers and the wider family of variance-reduction techniques.
- [Resampling](resampling.md), for the case that draws new samples from the data already in hand rather than from an assumed model.
- [Injection-recovery testing](injection-recovery.md), a parametric Monte Carlo applied to an estimator rather than to an integral or a null distribution.
- [Preregistration](preregistration.md), which fixes what a simulated null test or ceiling test is scoring before any of it is run.

## See also

- [Resampling](resampling.md), for simulation built from the data already
  collected rather than from a fitted model.
- [Injection-recovery testing](injection-recovery.md), a parametric Monte
  Carlo run on an estimator's bias and coverage rather than on an integral.
- [Preregistration](preregistration.md), the discipline that fixes what a
  simulated null test or ceiling test is allowed to claim before it runs.
- [Grids and discretisation](grids-and-discretisation.md), the alternative
  approach that fails once the sampled space grows past a handful of
  dimensions.

---

[← wiki index](README.md) · *Simulation and computation, 1 of 4* · [Grids and discretisation →](grids-and-discretisation.md)

# Resampling

*[wiki index](README.md) · method*

**The question.** How to get a standard error, a bias estimate or a
confidence interval for a statistic that has no closed-form sampling
distribution.
**Takes.** One sample in hand, or a fitted model to simulate from, and no
closed-form formula for the statistic's variance.
**Gives.** The nonparametric and parametric bootstrap, the jackknife,
jackknife-after-bootstrap, and why a block or stratified draw is needed once
the data are not individually exchangeable.
**Skip if.** You want to know whether one observation drives a fit rather
than how uncertain a statistic is. That is
[influence diagnostics](influence-diagnostics.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A fitted quantity comes with a standard error, and the textbook formula for
that standard error assumes something about how the data were generated,
usually that the noise is Gaussian and that a closed-form expression for the
estimator's variance exists. Resampling drops that assumption and estimates
the same thing by simulation instead: treat the one sample actually in hand
as a stand-in for the population it came from, draw new samples from that
stand-in, recompute the statistic of interest on each draw, and read the
estimator's variability directly off the spread of the results. The idea
generalizes past standard errors to bias and to confidence intervals, and
past those to the null distribution of almost any statistic, because none of
them needs an analytic formula once a computer can draw the resamples and
count.

The plain version is the nonparametric, or case-resampling, bootstrap. Given
$n$ observations, draw $n$ of them with replacement, so some appear more than
once and some not at all, compute the statistic of interest on that resample,
and repeat $B$ times. The empirical distribution of the $B$ resulting values
stands in for the statistic's true sampling distribution: its standard
deviation is a bootstrap standard error, and its percentiles are a bootstrap
confidence interval. Nothing here assumes a noise law. The only assumption is
that the observed sample's empirical distribution is a fair enough picture of
the population, which is the same assumption most other statistics computed
from the sample are already making.

The parametric bootstrap keeps the resampling logic and changes what gets
resampled. Instead of drawing new points from the observed sample, it draws
new datasets from a model fitted to that sample: at each design point,
simulate a new observation from the fitted curve plus noise drawn from the
assumed, or separately measured, noise law, recompute the statistic on the
simulated dataset, and repeat. Because the randomness now comes from the
model rather than from the empirical spread of the residuals, a parametric
bootstrap can be built at design points with no repeat measurement to
resample, and its null distribution answers a sharper question than the
nonparametric version does: what this statistic would look like if the
fitted model were the whole truth, so that anything the real data do beyond
that is attributable to something the model does not contain.

The jackknife is older and simpler. Leave one observation out, recompute the
statistic on the remaining $n-1$, and repeat once for every observation, so
$n$ deletions replace the bootstrap's $B$ random draws with a fixed,
exhaustive set. The spread of the $n$ leave-one-out estimates around their
mean gives a jackknife standard error, and the average shift between the
full-sample estimate and the leave-one-out estimates gives a jackknife bias
estimate. It needs no random-number generator and no choice of $B$, at the
cost of only $n$ points of support rather than however many the bootstrap can
afford, and it can fail outright for a statistic that does not respond
smoothly to dropping one observation, the sample median being the standard
example.

Jackknife-after-bootstrap turns the bootstrap's own output into a diagnostic
rather than running a second procedure. Every bootstrap resample either
happens to include a given observation or happens to leave it out, purely by
the luck of the draw, so the $B$ resamples already contain, for free,
something close to a leave-one-out experiment on the bootstrap distribution
itself. Comparing the resamples that omit one observation against those that
include it shows how much that single observation moves the bootstrap
distribution's spread or shape, with no new fit required. It answers a
question the bootstrap alone cannot: not how uncertain the estimate is, but
which observations are responsible for that uncertainty.

## What problem it solves

Resampling substitutes computation for a derivation. A median, a ratio of two
fitted parameters, or the maximum of several correlated residuals does not
have a closed-form sampling distribution in general, or has one only under
assumptions an analyst would rather not make. Deriving a standard error by
hand for every such statistic does not scale, and reaching for the nearest
textbook formula that happens to have a known distribution quietly
substitutes a convenient statistic for the one actually wanted. Resampling
answers the general question, how would this number vary if the measurement
were repeated, by simulation, so the answer is available the same way
regardless of how complicated the calculation behind the original number was.

It also supplies something a purely analytic threshold cannot: a null
distribution calibrated to the design actually in use rather than to a
generic large-sample approximation. A cutoff read from a table assumes the
data resemble the table's asymptotic case, and a small, unevenly spaced
dataset often does not. Simulating directly from the fitted model, or from
the observed sample, builds the comparison distribution that design would
really produce, rather than the one an off-the-shelf rule assumes.

## Where this repository uses it

An audit of this repository's own influence diagnostics needed a threshold
for the largest Cook's distance across the four-point width-against-density
fits behind the collisional-broadening bound, one fit per peak, each with
only two free parameters. A textbook rule of thumb for that threshold exists,
but with only two degrees of design left after fitting four points, the rule
of thumb mostly measures how uneven the design is rather than how outlying
any one point is. The audit built the threshold instead of assuming it: it
simulated many synthetic datasets from each fitted line, at the real design's
own points and its own measured errors, refit each one, and recorded the
resulting maximum Cook's distance, so the eventual comparison is against a
null distribution the design itself produces rather than an asymptotic
formula that takes no notice of how uneven this particular design is.

The joint fit behind the same coefficient carries a leave-one-out check of
its own, and it is a jackknife in substance even though nothing in the code
calls it that.
[`rb5s6s/lever_crosscheck.py`](../../rb5s6s/lever_crosscheck.py) drops one
whole peak at a time, refits, and records the largest resulting shift in
$\beta_\text{self}$, then separately drops one whole temperature block at a
time and does the same. Both are systematic leave-one-out at the level of a
block rather than a single point, and both are committed as diagnostics in
[`results/lever_crosscheck.csv`](../../results/lever_crosscheck.csv):
dropping the single peak whose absence moves the fit most shifts
$\beta_\text{self}$ by at most 0.0070 MHz per $10^{12} \text{cm}^{-3}$ for
$^{85}\text{Rb}$ and 0.0040 for $^{87}\text{Rb}$, while dropping the 110 C block moves it by
up to 0.1338 and 0.0745 respectively, the larger number because a temperature
block is also a density point, and removing one shortens the density lever
the whole fit leans on.

A third use is a case-resampling bootstrap of the power-lever grid behind the
AC-Stark bound, preregistered in
[`docs/notes/s0_block_bootstrap_prereg.md`](../notes/s0_block_bootstrap_prereg.md)
before any resample was drawn. That grid is not twenty independent points, it
is four peaks of five power settings each, and the four peaks do not share
their nuisance parameters. A plain bootstrap that pooled all twenty cells and drew twenty
with replacement would occasionally hand one peak all five of another peak's
cells and none of its own, breaking the per-peak structure the fit relies on.
The preregistered construction instead draws five cells with replacement from
each peak's own five, independently peak by peak, a stratified case bootstrap
built for exactly the reason a block bootstrap exists: to resample the unit
that is actually exchangeable, a whole peak's power sweep, rather than a unit
smaller than that.

## What can go wrong

Resampling cannot manufacture information the sample does not contain, and a
nonparametric bootstrap on a very small sample meets that limit early. A
four-point fit resampled nonparametrically has only $4^4=256$ distinct
resamples, most of which drop at least one of the four points entirely, so
the bootstrap distribution is coarse by construction and can look confidently
narrow while resting on almost no independent information. The sharper
version of the same limit showed up in the influence audit above: one of the
four design points sits at a leverage close to one, meaning the fitted line
passes almost exactly through it whatever value it carries, and no resampling
of the cases can expose a defect planted there. The fit is refit around it
every time, leaving no residual for any diagnostic to catch, bootstrap-based
or not. That is a property of the design's geometry rather than of the
resampling method, and it is why the audit could report no verdict at all for
that one point rather than a false clean bill.

A second failure is structural rather than a matter of sample size. Real data
are often not $n$ exchangeable individual points but a smaller number of
exchangeable blocks, each carrying an internal correlation or a shared
nuisance parameter that a single point does not carry alone, a whole peak's
power sweep sharing one systematic being the case above, or consecutive
samples in a trace sharing the correlation time
[weighted least squares](weighted-least-squares.md) already measures.
Resampling individual points out of such a structure, instead of resampling
whole blocks, treats correlated observations as if they were independent,
manufactures apparent precision the data do not have, and understates the
true uncertainty. That is exactly the shape of this repository's own
block-to-block scatter, one systematic per peak rather than one per point,
and it is why the S0 construction above stratifies rather than pooling.

Two narrower failures are worth naming. A parametric bootstrap inherits the
correctness of the model it draws from: if the assumed noise law is wrong,
every simulated dataset carries the same wrong noise law, and the resulting
null distribution is confidently wrong in the same direction the model is.
And the jackknife fails specifically for statistics that are not smooth
functions of the sample, the median chief among them, where dropping one
point leaves the leave-one-out estimate unchanged across many draws and then
jumps, producing a jackknife standard error with no reliable relation to the
statistic's real variability.

## Try it

A parametric-bootstrap null for a small, unevenly spaced design, three points
close together and one far off at the same measured precision, the shape
that hands one point most of the leverage. The threshold below is read off
the simulated distribution rather than taken from a textbook rule of thumb.

```python
import numpy as np

rng = np.random.default_rng(0)

# A small, unevenly spaced design, the shape a width-against-density fit
# takes when three conditions sit close together and one sits far off at
# the same measured precision: the far point alone then carries most of
# the leverage.
x = np.array([1.0, 1.6, 2.2, 4.0])
sigma = np.full_like(x, 0.05)
n, p = len(x), 2
X = np.column_stack([np.ones(n), x])

w = 1.0 / sigma**2
XtW = X.T * w
cov = np.linalg.inv(XtW @ X)
M = cov @ XtW                 # maps any y onto its fitted (intercept, slope)
H = X @ M
h = np.diag(H)                # leverage h_i, fixed by the design alone
dof = n - p

true_line = 0.30 + 0.05 * x   # the fitted line the null is simulated from

B = 20000
Y = true_line[None, :] + rng.normal(0.0, sigma[None, :], size=(B, n))
resid = Y - (X @ (M @ Y.T)).T
s2 = (w * resid**2).sum(axis=1) / dof
e2 = (w * resid**2) / (s2[:, None] * (1 - h)[None, :])
cooks_d = e2 * h[None, :] / (p * (1 - h)[None, :])
max_d = cooks_d.max(axis=1)

print(f"{B} datasets simulated from the fitted line, at the real design's "
      f"{n} points and measured errors")
print(f"leverage of the far point: {h[-1]:.3f} of a maximum of 1")
print(f"95th percentile of the null max-Cook's-distance distribution: "
      f"{np.percentile(max_d, 95):.2f}")
print(f"textbook rule-of-thumb cutoff 4/n: {4.0 / n:.2f}")
print("the design alone inflates the threshold this far above the rule of "
      "thumb, before any real data are read")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## What this repository got wrong once

Before 2026-07-16, the headline interval on the collisional-slope parameter
$\beta_\text{self}$ stood at 0.07-0.15 MHz per $10^{12}\text{cm}^{-3}$, built
from the between-block scatter multiplied by a hard-coded 2σ, the standard
large-sample Gaussian multiplier applied without checking whether the fit
behind it had enough degrees of freedom to earn it.
[HISTORY.md](../HISTORY.md) records what moved it: on 2026-07-16 the same
scatter, read instead through the Student-t quantile $t(0.95,1) = 6.31$ on
the single residual degree of freedom the fit actually carried, widened the
interval to 0.2-0.4, roughly a factor of three, with no new data behind the
change.

Neither number is a resample in the sense the rest of this page describes,
both are closed-form quantiles, but the mistake is the one this page's "What
problem it solves" section names directly: a cutoff read off a table assumes
the data resemble the table's large-sample case, and a fit with one residual
degree of freedom does not. A hard-coded 2σ is exactly such a table cutoff
wearing a constant's disguise. Building the null from the design actually in
hand, whether by the Student-t quantile that construction owed the fit or by
simulating from the fit directly the way this page's own methods do, is the
same check either way, and asking how many degrees of freedom a stated
multiplier stands in for, before quoting it, would have caught the
0.07-0.15 interval before it shipped.

## Further reading

- [Wikipedia: Bootstrapping (statistics)](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)),
  for the general history and the family of variants.
- B. Efron, "Bootstrap methods: another look at the jackknife," *Ann.
  Statist.* **7**, 1 (1979), the paper that introduced the nonparametric
  bootstrap and named it after the jackknife it generalizes.
- B. Efron and R. J. Tibshirani, *An Introduction to the Bootstrap* (Chapman
  and Hall/CRC, 1993), the standard reference for the bootstrap, the
  parametric bootstrap and the jackknife together.
- J. W. Tukey, "Bias and confidence in not-quite large samples" (abstract),
  *Ann. Math. Statist.* **29**, 614 (1958), the paper the jackknife takes its
  name from, building on M. H. Quenouille's 1949 bias-reduction construction.
- B. Efron, "Jackknife-after-bootstrap standard errors and influence
  functions," *J. R. Stat. Soc. B* **54**, 83 (1992), the diagnostic named on
  this page.
- H. R. Kunsch, "The jackknife and the bootstrap for general stationary
  observations," *Ann. Statist.* **17**, 1217 (1989), the origin of the block
  bootstrap for correlated data.
- [Weighted least squares](weighted-least-squares.md), whose closing section
  is the question this page answers.
- [The joint fit](joint-fit.md), whose leave-one-out checks are the jackknife
  described here.

## See also

- [Methods chapter 6](../methods/06_the_statistics.md), where the
  resampling constructions used on the record are specified.
- [Influence diagnostics](influence-diagnostics.md), the case-deletion idea
  this page's jackknife generalizes, applied one point or one block at a
  time.
- [Robust fitting](robust-fitting.md), a loss-based alternative for the same
  contamination problem, run beside a resampled interval rather than instead
  of it.
- [Heavy-tailed models](heavy-tailed-models.md), a likelihood-based
  alternative to a hard threshold, for the same large-residual question this
  page's parametric bootstrap addresses.
- [Sensitivity analysis](sensitivity-analysis.md), another Monte Carlo
  construction whose cost scales with the number of model evaluations rather
  than with the number of data points.

---

[← Robust fitting](robust-fitting.md) · *Robustness and influence, 3 of 7* · [Heavy-tailed models →](heavy-tailed-models.md)

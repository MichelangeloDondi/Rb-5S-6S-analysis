# Heavy-tailed models

*[wiki index](README.md) · concept*

## What it is

A point that sits far from a fitted curve is usually read as one of two
things: a mistake, to be found and removed, or a real feature the model has
not yet captured. There is a third possibility that is neither. The noise
generating every point may simply have heavier tails than a Gaussian, so
that a point several sigma away is not rare at all under the true noise law,
only rare under the Gaussian one an ordinary weighted fit assumes. On this
reading a large residual is evidence about the shape of the noise
distribution, not evidence about that one measurement, and rejecting the
point throws away exactly the information that would reveal the shape.

The Student-t distribution turns this reading into a model rather than a
judgement call. Its density carries a degrees-of-freedom parameter,
conventionally $\nu$, that dials continuously between two extremes: as $\nu$
grows large the distribution converges to the Gaussian, and as $\nu$ shrinks
toward one or below it develops tails heavy enough that even its variance
can fail to exist. A likelihood built on the Student-t distribution contains
the Gaussian likelihood as a limiting case rather than replacing it, so a
fit is free to land at either end or anywhere between.

Maximizing a Student-t likelihood turns out to be exactly an iteratively
reweighted least squares. At the maximum, each point carries a weight that
falls as its own residual grows, the same shape a Huber loss or Tukey's
biweight imposes by explicit construction rather than by a likelihood. This
is what connects a heavy-tailed model to the wider family of robust fitting
techniques: a weighted fit reweighted by a likelihood instead of by a
hand-chosen loss function. The useful property is that $\nu$ itself, and
therefore how fast the weight falls off, can be fitted rather than fixed in
advance, so a small recovered $\nu$ is a direct, quantitative statement that
the data prefer heavy tails to a wider Gaussian, made by the data rather
than assumed going in.

The general framing behind all of this is the scale mixture of normals. A
Student-t variable can be built as a Gaussian whose own variance is itself
drawn from an inverse-gamma distribution and then averaged over: every point
is Gaussian conditional on its own variance, and the mixture over that
variance is what produces the heavier tail seen once the variance is
integrated out. A different mixing distribution produces a different tail
shape, so a Student-t likelihood is one member of a family rather than an
isolated device.

None of this explains an outlier. A heavy-tailed likelihood accommodates a
population of large residuals by widening what the model calls plausible.
It does not say whether a given large residual came from a stray spark on a
detector, a mistimed trigger, or real structure the mean model has not
captured. A fitted $\nu$ describes the shape the residuals happen to have,
not why they have it, and the same fitted value is silent on whether the
next dataset shows the same tail or none at all.

## What problem it solves

A weighted fit under a Gaussian likelihood gives every point exactly the
influence its stated weight implies, with no headroom for a point whose
actual error is larger than its stated one. Both conventional responses to
that require a decision made outside the fit: reject points past some
threshold, which needs the threshold chosen and turns every borderline point
into a discrete in-or-out call, or accept an answer that a handful of large
residuals can still pull around. A heavy-tailed likelihood folds that
decision back into the same maximization the rest of the fit already runs.
Down-weighting becomes continuous, set by the size of a residual rather than
by where an analyst drew a line, and because the degrees-of-freedom
parameter is fitted rather than chosen, how much down-weighting happens is
answerable to the data instead of to a convention fixed in advance.

It also gives a second, principled fit to compare against the standard one.
Where the two agree, the ordinary weighted fit stands with more confidence
than it had alone, and where they disagree, the disagreement names which
points changed the answer, the same use the closing section of
[weighted least squares](weighted-least-squares.md) recommends for the
whole robust and influence family rather than a silent substitute for the
weighted fit itself.

## Where this repository uses it

No fit committed to this repository maximizes a Student-t or any other
heavy-tailed likelihood. The noise law behind every weighted fit is measured
directly from the raw signal rather than assumed, and it comes out Gaussian
by construction, with a variance that grows with the signal level rather
than a fixed width. [Weighted least squares](weighted-least-squares.md) sets
out that law, and [`rb5s6s/noise.py`](../../rb5s6s/noise.py) fits its
coefficients per condition into
[`results/noise_model.csv`](../../results/noise_model.csv). Nothing
downstream of it currently asks whether a heavier tail would describe the
same samples better than that measured Gaussian law does.

A Student-t quantile does already appear downstream, in
[`rb5s6s/beta.py`](../../rb5s6s/beta.py) and in
[methods chapter 6](../methods/06_the_statistics.md), but it answers a
different question. There the per-point noise stays Gaussian, and the
Student-t distribution describes the sampling distribution of a mean
estimated from only a few blocks, the small-sample correction applied
whenever a variance going into a confidence interval is itself estimated
from limited data rather than known exactly. That use widens an interval to
account for how few blocks went into estimating it. It is not a claim that
any single measurement's own noise has heavy tails, and the two roles
should not be read as the same idea under one name.

The question a heavy-tailed likelihood would actually answer is left open
by the record. The block-to-block scatter behind the collisional-slope fit
is larger than the within-block errors that go into it, and the current
construction absorbs that gap with a scale factor on the profile threshold
rather than with a different noise shape (see
[`docs/UNCERTAINTY.md`](../UNCERTAINTY.md), section 4). Whether that gap is
better described by a heavier-tailed noise model than by the larger
Gaussian width the scale factor already stands in for has not been tested,
and nothing in the committed analysis chain currently distinguishes the
two possibilities.

A related but separate check has been run against this record's own points.
An instrument built to examine the four-point density construction and the
[power sweep](../../results/power_sweep.csv) for influential or outlying
points found that the high-temperature anchor of the density ladder carries
leverage close to one on every peak, so an error planted at that point is
not detectable by a fit built almost entirely around it, and the
construction can return no influence verdict there rather than a clean one.
The 25 mW power condition, the case that motivated the check, came back
neither outlying nor influential on any peak, consistent with its large
stated uncertainty already doing the discounting a heavy tail or a
rejection rule would otherwise have to do by hand. One point elsewhere in
the power sweep was flagged as outlying without being influential, at a
rate the audit itself judged consistent with chance across the several
constructions it tested, worth a further look rather than a standing
result. None of this moves any committed bound. It narrows the open
question above: if the block-to-block scatter does carry a heavier tail
than a single Gaussian width can, that audit found no sign of one dominant
point responsible for it, so the shape would have to be a property of the
block population as a whole rather than of one condition an influence check
could isolate and explain away.

## What can go wrong

A heavy-tailed fit can paper over a problem that has a specific cause and
deserves to be found rather than absorbed. If a handful of large residuals
come from a single bad block, a detector glitch that struck one session and
not the others, a global $\nu$ describes the mixture of good and bad
residuals as one smooth tail and never names the block responsible, where a
per-condition variance check would isolate it directly.

A degrees-of-freedom parameter is a fitted quantity like any other, and
with few points it is poorly determined. A handful of large residuals can come from
truly heavy tails or can come from ordinary Gaussian noise that happened to
produce a few large draws, and a small sample often cannot tell the two
apart. A single recovered $\nu$ reported without its own uncertainty
invites a reader to treat a noisy estimate as a settled description of the
noise.

The optimization itself is not always well behaved. Past a certain size of
$\nu$ the Student-t likelihood is close to flat, since the distribution has
already converged to the Gaussian in every way the data can detect, so an
unconstrained fit on data that are genuinely Gaussian can drift to an
arbitrarily large $\nu$ without changing the fit it describes. Reading that
number at face value as a small, specific finding rather than as the
optimizer running out of signal is an implementation trap distinct from any
question about the physics.

Finally, a heavy tail is a statement about the spread of residuals around
one center. It does nothing for a location shift: points that are
systematically biased rather than merely more scattered do not look like
what this model was built to catch, and folding a biased subset into a
heavy-tailed fit tends to absorb it as a wider tail rather than reveal it
as a bias.

## Try it

A Student-t scale and degrees of freedom fitted by maximum likelihood to a
clean Gaussian sample and to the same construction with a handful of points
blown up, with no point in either sample labelled an outlier by hand.

```python
import numpy as np
from scipy.optimize import minimize
from scipy.stats import t as student_t


def fit_student_t(sample, dof_bounds=(0.5, 100.0)):
    """Maximum-likelihood scale and degrees of freedom, location fixed at 0.

    The dial is bounded above at 100: past that point the Student-t
    likelihood is numerically indistinguishable from the Gaussian one, and
    an unconstrained search on genuinely Gaussian data drifts to arbitrarily
    large values without changing the fit it describes.
    """
    def neg_log_lik(params):
        scale, dof = params
        return (-student_t.logpdf(sample / scale, dof).sum()
                 + sample.size * np.log(scale))

    fit = minimize(neg_log_lik, x0=[sample.std(), 20.0], method="L-BFGS-B",
                    bounds=[(1e-3, None), dof_bounds])
    scale, dof = fit.x
    return scale, dof


rng = np.random.default_rng(1)
n, frac, blowup = 400, 0.06, 12.0

clean = rng.standard_normal(n)
contaminated = clean.copy()
n_out = int(round(frac * n))
idx = rng.choice(n, size=n_out, replace=False)
contaminated[idx] = rng.standard_normal(n_out) * blowup

print(f"{n} points per sample, {n_out} blown up by a factor {blowup:.0f} "
      "in the contaminated case")
for label, sample in [("clean Gaussian sample       ", clean),
                       ("contaminated sample          ", contaminated)]:
    scale, dof = fit_student_t(sample)
    print(f"{label}: fitted scale = {scale:.3f}, fitted dof = {dof:6.1f}")

print("a small fitted dof says the data themselves prefer heavy tails "
      "over a wider Gaussian, decided by the likelihood, not by hand")
```

Every snippet on these pages is executed by
`tests/test_wiki_snippets_run.py`, so one that stops working fails the suite
rather than sitting here misleading a reader.

## Further reading

- K. L. Lange, R. J. A. Little and J. M. G. Taylor, "Robust Statistical
  Modeling Using the t Distribution," *Journal of the American Statistical
  Association* 84(408), 881 (1989), the paper that makes the Student-t and
  iteratively-reweighted-least-squares equivalence this page describes
  explicit and computable.
- D. F. Andrews and C. L. Mallows, "Scale Mixtures of Normal
  Distributions," *Journal of the Royal Statistical Society, Series B*
  36(1), 99 (1974), the origin of the general framing in the closing
  paragraph of What it is above.
- [Weighted least squares](weighted-least-squares.md), whose closing
  section this page answers, and the source of the noise law this
  repository fits instead of a heavy-tailed one.

---

[← Resampling](resampling.md) · *Robustness and influence, 4 of 5* · [Sensitivity analysis →](sensitivity-analysis.md)

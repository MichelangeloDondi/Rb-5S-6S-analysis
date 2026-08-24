# Weighted least squares

*[wiki index](README.md) · method*

**The question.** How should each measurement be weighted in a fit so that
noisy points do not dominate and the resulting chi-squared means something.
**Takes.** Familiarity with an ordinary least-squares fit and nothing more,
since this page starts from that baseline and corrects it.
**Gives.** The variance law that gives each point its weight, where the law
comes from, and the correlation-time correction a real detector needs.
**Skip if.** The question is how several repeats of the same measurement get
combined into one estimate rather than how one measurement is weighted. That
is [the joint fit](joint-fit.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An ordinary least-squares fit minimizes the sum of squared residuals between
a model and a set of measurements, treating every point as equally
trustworthy. That is the right thing to do only when every point genuinely
carries the same noise. When it does not, an unweighted fit lets the noisiest
points pull the model exactly as hard as the quietest ones, and the fitted
parameters come out less precise than the data actually allow.

Weighted least squares corrects this by minimizing

$$\chi^2 = \sum_i \frac{(d_i - m_i(\theta))^2}{\sigma_i^2}$$

instead, where $\sigma_i$ is point $i$'s own noise. A point known ten times
more precisely counts a hundred times more in the sum, because the weight is
$1/\sigma_i^2$. When the $\sigma_i$ used are the true ones, this is the
maximum-likelihood estimator for Gaussian noise, and the resulting $\chi^2$
becomes a genuine goodness-of-fit statistic, distributed as chi-squared with
one degree of freedom per point minus one per free parameter, so a reduced
$\chi^2$ near one is the signature of a model and a noise estimate that both
describe the data. Get the weights wrong and that signature is lost even when
the parameter estimates stay close, because the reported error bars inherit
whatever error the weights carried.

The weights have to come from somewhere, and two common sources are not
equivalent. The convenient one fits once with equal weights, treats the
residuals of that fit as an estimate of each point's noise, and refits with
those. This is circular in a specific way: the residuals already carry the
shape the first fit imposed, so a systematic mismatch between model and
signal, near a peak for instance, looks like a noisy point there and gets
downweighted instead of diagnosed. It also needs more residuals than a single
condition usually has: a handful of repeats give a handful of residuals per
point, too few to estimate a variance from with any confidence, so a
residual-based weight is often smoothed or shared across points in a way that
quietly assumes the very noise structure it was supposed to measure.

The alternative measures the noise directly from the raw signal, before any
model is asked to explain it. For a detector converting incident photons into
a voltage, the noise has a known form: a constant floor from the electronics
and the dark current, independent of how much light arrives, plus a term
that grows with the signal because photon detection is a counting process
and counting noise scales with the count. In variance,

$$\sigma^2(V) = a^2 + bV$$

with $a$ the electronic floor and $b$ the shot-noise coefficient, sometimes
called a Fano term when the counting statistics are not exactly Poissonian. A
further term proportional to $V^2$ can be added for multiplicative noise,
such as source-intensity fluctuations that scale with the signal rather than
its square root, and it earns its extra parameter only when the data actually
prefer it.

This law pools far more data than any one fit's residuals can: the whole
trace, every sample, across every repeat of a condition, rather than the
handful of points near a peak. Measured once and applied everywhere, it turns
a systematic mismatch between model and data into a bad $\chi^2$ instead of a
self-correcting reweighting, which is why it beats weights read off the
residuals.

Real detector noise is also not independent from sample to sample. Thermal
drift, amplifier bandwidth and mechanical vibration all correlate
neighboring samples, so a record of $N$ points carries less information than
$N$ independent draws would. The standard way to quantify this is an
integrated correlation time $\tau$, and the record behaves like an effective
sample of roughly $N_\text{eff}=N/\tau$ independent points rather than $N$: a
parameter's standard error, computed as if the noise were white, has to be
inflated by about $\sqrt{\tau}$ to state the true uncertainty.

The variance law also says where a photon counter beats an analog chain.
Below the signal level at which the constant floor $a^2$ equals the
proportional term $bV$, the electronics dominate the noise, and a detector
that never carries that floor, one that counts individual detection events
instead of integrating a current, keeps the shot-noise-limited performance an
analog chain only reaches near or above that crossover. Above it the two
converge, because both are shot-noise limited there and the floor is
negligible either way.

## What problem it solves

It turns measurements of unequal quality into a single estimate that neither
lets the noisiest points dominate nor discards the informative ones, and it
turns a converged fit into a genuine statistical statement, because a
$\chi^2$ evaluated against real, measured weights actually tests whether the
model describes the data rather than merely producing a set of numbers.

## Where this repository uses it

[`results/noise_model.csv`](../../results/noise_model.csv) holds the fitted
per-condition coefficients, one row per peak, temperature and, for the power
sweep, drive power, with columns `a_V`, `b_V` and `tau_int` among others.
[`rb5s6s/noise.py`](../../rb5s6s/noise.py) produces the file: it bins
second-difference noise samples by local signal level, fits the variance law
above, rescales it against the direct wing noise, and measures $\tau$ from
the autocorrelation of a signal-free wing segment. The method is set out in
[methods chapter 6, section 4.4](../methods/06_the_statistics.md).

Every later fit reads this table rather than estimating its own weights.
[`rb5s6s/linefit.py`](../../rb5s6s/linefit.py) weights the joint lineshape
fit by the noise law and inflates the reported parameter errors by
$\sqrt{\tau_\text{int}}$, and [`rb5s6s/beta.py`](../../rb5s6s/beta.py),
[`rb5s6s/ruler.py`](../../rb5s6s/ruler.py) and
[`rb5s6s/global_fit.py`](../../rb5s6s/global_fit.py) carry the same law and
the same correlation inflation into the ruler and the collisional-slope fits
downstream. [Methods chapter 6, section 4.1](../methods/06_the_statistics.md)
states the principle these modules all implement: fitting is weighted by the
measured noise, never by a fit's own residuals.

The law is specific to the detection chain it was measured on.
[`docs/plan/10_the-fixed-lock-instrument.md`](../plan/10_the-fixed-lock-instrument.md),
section 10c.6, works out where a photon counter would beat the analog chain
the 2025 campaign used, by inverting this same noise law to find the signal
level at which its two terms are equal (the Try it section below computes
that level directly from the committed coefficients). The same section is
explicit that a new termination, gain or instrument needs its own noise law
measured before any weighted fit downstream of it can be believed.

## What can go wrong

The clearest failure is the one this page argues against directly: weighting
by the residuals of a preliminary fit. It is circular by construction, and it
is worst exactly where a model failure would show up, at a line's peak,
where a systematic mismatch inflates the residuals and a residual-based
weight then discounts them instead of flagging them. A related
data-insufficiency version of the same failure is estimating weights per
point from a handful of repeats: five residuals do not constrain a variance,
and any smoothing or sharing applied to make them constrain one has quietly
reintroduced an assumption about the noise that was supposed to be measured.

A second failure is experimental rather than statistical: the noise law
belongs to the detection chain it was measured on, and $a$ and $b$ change
with the termination, the gain or the instrument. Reusing an old law after
such a change does not merely add scatter, it inflates or deflates weights
in a way that varies by signal level, which is harder to notice than a
uniformly wrong error bar.

A third is implementation, and this repository has one on record. The law's
floor is $a$, the noise at zero signal, and nothing physical can go below
it. An earlier version of
[`sigma_of_v`](../../rb5s6s/noise.py) floored the variance at only a fifth
of $a^2$, which meant that a condition with a negative curvature term could,
evaluated outside the level range it was measured on, hand out a near-zero
variance and therefore a runaway weight. The floor is now $a^2$ everywhere,
the physical bound rather than a tuned number.

Finally, correlated noise: treating $\tau_\text{int}$ as one when the wings
show it is not understates every reported error by roughly
$\sqrt{\tau_\text{int}}$, and a truncated correlation-time estimate is
itself conservative rather than exact, so the size of that understatement is
bounded but not zero.

## Try it

The crossover level, read directly from the coefficients
[`rb5s6s/noise.py`](../../rb5s6s/noise.py) fitted and committed to
[`results/noise_model.csv`](../../results/noise_model.csv): the signal at
which the constant floor and the proportional term contribute equally to the
variance, computed condition by condition rather than assumed.

```python
import csv

import numpy as np

with open("results/noise_model.csv", newline="") as f:
    rows = list(csv.DictReader(f))

crossover_mV = np.array(
    [float(r["a_V"]) ** 2 / float(r["b_V"]) * 1000.0 for r in rows])

print(f"{len(rows)} committed conditions in results/noise_model.csv")
print("signal level V* where a^2 (floor) equals b*V (shot term):")
print(f"  median  {np.median(crossover_mV):7.3f} mV")
print(f"  range   {crossover_mV.min():7.3f} to {crossover_mV.max():7.3f} mV")
print("below V*, the electronic floor dominates and a counting detector wins")
```

Every snippet on these pages is executed by
`tests/test_wiki_snippets_run.py`, so one that stops working fails the suite
rather than sitting here misleading a reader.

## When least squares is not enough

Weighting by the true noise law fixes the case where every point is honest
about its own uncertainty and the noise itself follows a smooth, measured
law. It does not fix the case where a handful of points are wrong for a
reason the noise law never modeled: a stray spark on a detector, a mistimed
trigger, a step in a mechanical mount. A correctly weighted fit still lets
such a point pull the answer in proportion to its stated weight, which can be
large precisely because the noise law expects that signal level to be quiet.

The standard repair is a family of robust and influence diagnostics: loss
functions that flatten for large residuals instead of squaring them, such as
Huber loss and Tukey's biweight, transformations like Winsorization that cap
an extreme value rather than deleting it, and influence measures, Cook's
distance, DFBETAS and DFFITS among them, that quantify how much a fit or a
single parameter moves if one point is removed. Case deletion, the bootstrap
and the jackknife all ask a version of the same question by resampling
rather than by reweighting.

None of that belongs silently in place of the weighted fit this page
describes. The right use is beside it, as a diagnostic: fit both ways, and if
they agree, the standard fit stands with more confidence than it had alone,
and if they disagree, the disagreement names which points to look at before
either answer is trusted. This repository does not yet carry that
comparison, and the robust and influence family gets its own pages in a
later wiki wave.

## What this repository got wrong once

This page's principle, that a stated error bar has to earn its multiplier
rather than assume one, was violated for the collisional-slope parameter
$\beta_\text{self}$ before 2026-07-16, when the headline interval
was built from the between-block scatter with a hard-coded 2-sigma
multiplier. That multiplier silently assumed a large
number of degrees of freedom. [HISTORY.md](../HISTORY.md) states plainly what
moved it: "the multiplier hid its own assumption about degrees of freedom".

The replacement, quoted from 2026-07-16, used the same between-block scatter
but read the interval off the Student-t quantile $t(0.95,1) = 6.31$ on the
single residual degree of freedom the data actually had, roughly a factor of
three wider, moving the interval to 0.2-0.4. HISTORY labels the change
"interval construction, not new data", the same measurement, correctly
propagated for the first time. This is the same shape of failure this page's
"What can go wrong" section names for correlated noise, an unexamined
assumption sitting inside a quoted error bar and understating it: an error
bar is only as honest as the assumption behind its multiplier, and a fixed
"2σ" is such an assumption dressed as a constant. Asking, before quoting any
multiplier, how many degrees of freedom it is standing in for would have
caught the 0.07-0.15 interval before it was replaced.

## Further reading

- P. R. Bevington and D. K. Robinson, *Data Reduction and Error Analysis for
  the Physical Sciences*, 3rd ed. (McGraw-Hill, 2003), the standard physics
  treatment of weighted least squares and $\chi^2$.
- W. H. Press, S. A. Teukolsky, W. T. Vetterling and B. P. Flannery,
  *Numerical Recipes*, 3rd ed. (Cambridge University Press, 2007), chapter
  15, for the algorithms and the general least-squares formulation.
- P. J. Huber, *Robust Statistics* (Wiley, 1981), the origin of the loss
  function named in the closing section above.
- [The joint fit](joint-fit.md), which shares these same weights across
  repeats.
- [Identifiability](identifiability.md), for what a correctly weighted
  covariance still cannot tell apart.

## See also

- [The joint fit](joint-fit.md), for how these same per-point weights carry
  across repeated traces of one condition.
- [Identifiability](identifiability.md), for what a correctly weighted fit
  still cannot separate.
- [Robust fitting](robust-fitting.md), for the point a stated weight does not
  cover, one that is wrong for a reason the noise law never modeled.
- [Influence diagnostics](influence-diagnostics.md), for measuring how much a
  single point moves the fitted answer.

---

[← wiki index](README.md) · *Statistical inference, 1 of 8* · [The joint fit →](joint-fit.md)

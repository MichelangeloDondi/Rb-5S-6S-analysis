# Identifiability

*[wiki index](README.md) · method*

**The question.** Whether the data can actually separate two parameters, or
only determine some combination of them.
**Takes.** A fitted model and its parameter covariance.
**Gives.** The structural-versus-practical distinction, three diagnostics
for a degeneracy, and what breaking one is worth.
**Skip if.** The question is building a confidence interval that already
accounts for a nuisance parameter's freedom, instead of whether two
parameters are separable at all. That is
[the profile likelihood](profile-likelihood.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A parameter is identifiable if the data could, in principle, distinguish its
true value from any other. This is a property of the model and the
experiment together, not of the fitting routine, and it is decided before
any data are collected. If two different parameter values predict exactly
the same observation, no amount of data, no better optimiser and no
cleverer algorithm will separate them.

The clean case is structural non-identifiability: the model is written so
that only a combination of parameters appears. If a prediction depends only
on the product $ab$, then $a$ and $b$ are separately unknowable and the
product is the only thing measured. A fit will still return values for
both, because software returns whatever the optimiser stopped at, and their
apparent precision is an artefact of where it started.

The commoner case is practical non-identifiability: the parameters are
distinguishable in principle, but only through a feature the data do not
resolve at the available signal-to-noise. Here the likelihood has a long
flat valley instead of an exactly flat direction, and estimates slide along
it. The same three diagnostics apply in both cases:

- the parameter covariance, whose near-unit correlations name the degenerate pairs
- the condition number of the sensitivity matrix, which says how nearly singular the problem is
- the [profile likelihood](profile-likelihood.md), which maps the valley directly instead of approximating it with an ellipse at one point

The remedy is to change the experiment, either by adding a measurement that
moves one parameter and not the other, or by reporting only the combination
the data determine.

## What problem it solves

It decides whether a number should be published, by asking whether the
dataset determines the quantity itself or only something the quantity is
part of. Answering it early turns an unfalsifiable result into either a
measurement or a stated bound.

## Where this repository uses it

It is the reason several quantities here are reported as bounds instead of
values. The analysis is worked in full in
[methods chapter 6 section 4.10](../methods/06_the_statistics.md), with the
numbers committed to
[`results/identifiability.csv`](../../results/identifiability.csv) and
drawn in the figure below.

![Profile-likelihood map of collisional and laser width](../../figures/fig7_identifiability_profile.png)

*The collisional-versus-laser-width plane at one bright condition: the
profile-likelihood valley against the local covariance ellipse a single fit
would report alone.*

The degeneracy is physical: the collisional width, the laser width and the
transit width all broaden the same line, so a single line constrains their
sum far better than their split. The chapter quantifies this at one bright
condition using a local covariance analysis and a global profile map, with
all three widths free.

A single-start fit of all three widths settles in one minimum. The profile
map exposed a second, deeper minimum elsewhere in the plane, separated from
the first by a gap the chapter records instead of smoothing over. A fit
that converges is not the same as a parameter that is determined, which is
why the map exists.

## What breaking it is worth

Non-identifiability is not always permanent. Where a degenerate pair can be
separated by measuring one member independently, the gain is concrete and
worth computing before deciding whether the measurement is affordable.

![Parameter identifiability status by design increment](../../figures/fig33_identifiability_matrix.png)

*Parameter status across four campaign design increments, from the 2025
archive to a beam profile measured on the day: bounded, identified, or
measured.*

In this repository the collisional and laser widths are the degenerate
pair. On a bright synthetic condition with signal-dependent noise
(`python scripts/run_width_pinning.py`), a fit with both widths free
recovers the collisional width with a scatter of 0.0070 MHz, and the same
fit with the laser width fixed recovers it with 0.0022 MHz, a ratio of 3.18
with a spread of 0.20 across nine seeds, since Monte Carlo ratios vary by
seed. An earlier version of this page quoted a single draw of 3.4, the
largest of the nine. The absolute scatters belong to this idealised
condition. The real record adds block drift and gain scatter on top, and
the ratio is what transfers: an independent laser diagnostic reduces the
collisional-width scatter by about this factor.

### The general formula for the factor

The general answer is arithmetic: conditioning a multivariate normal on one
member of a correlated pair reduces the other's variance to $(1-\rho^2)$ of
its joint value, so its uncertainty falls by $\sqrt{1-\rho^2}$, a factor of
$1/\sqrt{1-\rho^2}$ that depends only on the correlation and does not
improve with more traces.

| where the correlation was measured | $\rho$ | factor $1/\sqrt{1-\rho^2}$ |
|---|---|---|
| median across the 32 committed conditions | $-0.90$ | 2.29 |
| the twin's committed design condition ([`twin_span_sweep.csv`](../../results/twin_span_sweep.csv), 60 MHz span) | $-0.9421$ | 2.98 |
| the bright condition of the pinning simulation above | $-0.9417$ | 2.97 |

The last row checks the first two: the pinning simulation's measured
$3.18 \pm 0.20$ agrees with the arithmetic's 2.97, to 7 per cent, at the
same fitted correlation of $-0.9417$.

These are floor numbers, not numbers of record. The producer is a
diagnostic that writes to `private/run_logs/` and moves nothing in
`results/`, so it runs on the declared support floor (Python 3.12, numpy
2.5) instead of the older versions that reproduce the committed CSV
digits. [`results/ENVIRONMENT_OF_RECORD.md`](../../results/ENVIRONMENT_OF_RECORD.md)
explains why those are two different statements, and the producer stamps
the versions it ran under into every row it writes.

## Breaking a degeneracy by design

Two Lorentzian widths in one line, a collisional one and a laser one,
convolve to their sum exactly. At a fixed condition this is an exact
degeneracy, not one managed with priors: the sum is measurable and the
split is not, at any signal to noise. Six injected values confirm it, the
recovered sum tracking truth to a part in a thousand while the split
wanders.

No fit breaks that degeneracy. A change to the experiment does: the
collisional width scales with density and the laser width does not, so a
temperature ladder makes both widths identifiable. Injecting 0.600 MHz on
the ladder already in this archive returns 0.599 with a spread of 0.013
(`tests/test_gamma_l_identity.py`). The lever was already in the data. The
question was which measurements to compare, not which fit to run.

More generally, two quantities that reach the data only through their
product cannot be separated by any fit at a fixed setting: a control
scaling one factor and not the other turns repeated measurements into a
line instead of a point, with the two factors as slope and intercept.

No such control exists for the laser-versus-collisional pair. The search
was run, not assumed:
[`twin_span_sweep.csv`](../../results/twin_span_sweep.csv) rebuilds it in
the [digital twin](the-digital-twin.md) from a named committed condition.
The correlation between the laser and collisional widths moves by 0.0075
when the span widens from 60 to 300 MHz and by 0.0000 at ten times the
repeats, because a Lorentzian core inside a Gaussian envelope exchanges
the same way at every sample size. Repeats buy precision as sampling
predicts, a factor 3.16 at ten times the traces, while widening the span
costs a factor 2.72 at fixed points per trace, since the same points
spread over more baseline. Among the acquisition settings the asymmetric
knob does not exist, which is why the pinning approach above is used
instead.

## Leverage in a channel

Identifiability asks whether the data determine a parameter. A prior
question is whether the observable used is even sensitive to it: a channel
can be correctly modelled, well measured, and still nearly empty of the
parameter. The relevant number is the derivative of the observable with
respect to the parameter, in units of the observable's own scatter, its
leverage. Appearing in the forward model is not leverage. Constraining
such a channel harder adds almost no information.

### Matching the summary statistic to the perturbation

A one-sided perturbation moves the line's centre and asymmetry strongly
while barely changing its width, since a symmetric summary of an
antisymmetric perturbation is insensitive by construction. A width can be
the natural-seeming handle and the wrong one: in this repository the
light-shift term moves the composite width by a few kilohertz at its bound
but the line centre by a hundred and fifty kilohertz against an
eighty-eight kilohertz block scatter, a factor of forty in the same fit.
The fixed natural linewidth alone, 3.493 ± 0.013 MHz on the transition axis
from the measured 6S lifetime of 45.57 ± 0.17 ns
([Gomez 2005](../lit/gomez2005.md)), is about 0.65 of the observed 5.4 MHz
composite, a ratio of two defined widths, not an additive share, since a
convolution's width does not decompose additively.

The practical order is to build the component budget, compute the leverage
in each channel, and only then ask whether the parameter is identifiable in
the channel that carries it.

## The exact Lorentzian-sum degeneracy

Every other case here is a degeneracy the data cannot resolve well. This
one is different: the mathematics makes it exact, and the implementation
once broke that exactness by accident.

![Lever map for the collisional and laser width components](../../figures/fig35_orthogonal_information.png)

*Which lever moves which width component: density resolves the collisional
width, an independent laser diagnostic is the only lever on the laser
width, and without that diagnostic the two currently add to a single
measured sum.*

Lorentzians add: convolving one of FWHM $a$ with one of FWHM $b$ gives a
Lorentzian of FWHM $a+b$, exactly. If the laser's contribution is modelled
as a Lorentzian, the predicted line at a fixed condition depends on
$\gamma_{\rm coll}$ and the laser width only through their sum, and the
orthogonal direction is flat to machine zero. Any number reported for
$\gamma_{\rm coll}$ alone under that kernel marks only where the optimiser
stopped. A per-condition figure was withdrawn for exactly this reason
([the Voigt profile](voigt-profile.md)).

The code did not preserve that flat direction. It realised the sum
identity by convolving the two Lorentzians on a finite grid, and the grid
span was computed from the two widths separately, so grid truncation of
the Lorentzian tails made the predicted line depend on how a fixed total
width was split, by up to $3.7\times10^{-3}$ of peak. That size matters:
per-point noise here is $5.3\times10^{-3}$ of peak across about $10^4$
points, so a distortion at $3.7\times10^{-3}$ carries up to seventy sigma
of matched-filter leverage, enough for round-off alone to separate the two
widths confidently.

The fix imposes the identity instead of computing it: the laser width is
now added directly into the homogeneous width instead of convolved, exact
by construction and cheaper by one convolution, with a bit-identical guard
and a control confirming the Gaussian branch still moves under the same
transformation.

Density is what resolves the degeneracy here: the collisional part scales
with it and the laser part does not, so an estimator that varies density
separates them. The headline kernel result survived the fix almost
unchanged, while the per-condition number had no referent, and a density
ladder turns the exact degeneracy into one that is strong but finite. The
cost is visible in the correlation between $\beta_{\rm self}$ and the
shared laser width: $-0.82$ to $-0.89$ under the Gaussian kernel, $-0.91$
to $-0.98$ under the Lorentzian.
Measured in
[`results/kernel_identifiability.csv`](../../results/kernel_identifiability.csv),
which runs in seconds and needs no data.

### The collisional component across the archive

At a fixed condition the sum is all that exists, since the flatness is
algebraic, not statistical. Density moves one term of the sum and leaves
the other alone, which is why the collisional coefficient is estimated
across a temperature ladder instead of from any single condition, and why
the per-condition version was withdrawn.

Running that separation over the archive finds a component present at
every peak, by a nested likelihood ratio of 176 to 961 for one parameter on
its boundary, with peak-conditioned values of 0.315 to 0.449 MHz
(`results/kernel_k3.csv`), sized at 3.24 times the statistical error on a
matched footing (`results/kernel_budget.csv`): the model form, not the
noise, limits that coefficient.

This does not establish that the four peaks share one value, open at
$p = 0.097$, or what the component is (calling it the laser is a separate
claim, `results/kernel_k5.csv`), or that the model class is adequate, since
3.24 is only a sensitivity within the two forms tested. A residual check
finds a common cross-condition structure with no named mechanism and no
quantified effect on the coefficient (`results/kernel_k4.csv`). The lever
map above marks the one measurement that would settle its origin, still
untaken.

## Values that moved
Three figures on this page's subject were withdrawn or rebuilt. A
per-condition collisional-width split was traced to a grid-truncation
artefact rather than to physics. A background span sized on an assumed
signal retention was rebuilt once the true fraction was computed. And a
campaign-only bound that appeared to move across commits was traced to a
sample-count change landing on a discrete trim boundary in a nearly flat
profile direction. [HISTORY.md](../HISTORY.md) carries each row with its
before and after.

## What can go wrong

The failure that matters is mistaking a converged fit for a determined
parameter: an optimiser always returns a point, a covariance matrix always
returns error bars, and neither is evidence the data chose the answer. A
near-unit correlation between two parameters signals that their individual
values are not results.

A local covariance is a quadratic approximation at a single point,
describing the valley only near where the fit stopped. If the likelihood
has more than one minimum, the covariance around one says nothing about
the other, and its error bars imply a global statement the analysis did
not make.

An implementation failure can imitate non-identifiability exactly, through
a parameter railed at a bound, a mis-scaled Jacobian, or a wrong
derivative step size, all artefacts of the code and not genuine
degeneracy, distinguishable only by examining the model. Resolution is
also easy to overstate: adding data that moves the degenerate combination
only a little makes the valley shorter without making it narrower, and a
parameter that goes from unmeasurable to poorly measured is still not a
measurement.

## Try it

How similar the line looks when you widen the collisional part against
when you widen the laser part. An overlap near one means the data cannot
tell the two changes apart.

```python
import numpy as np
from rb5s6s import composite_profile, transit_fwhm_from_w0

t = transit_fwhm_from_w0(64e-6, 130.0)
grid = composite_profile(0.60, 1.40, t)[0]

def shape(gc, sl):
    g, p = composite_profile(gc, sl, t)
    return np.interp(grid, g, p / p.max(), left=0, right=0)

d_gamma = shape(0.66, 1.40) - shape(0.54, 1.40)
d_sigma = shape(0.60, 1.47) - shape(0.60, 1.33)
overlap = (d_gamma @ d_sigma) / np.sqrt((d_gamma @ d_gamma) * (d_sigma @ d_sigma))
print(f"overlap of the two shape changes: {overlap:+.3f}")
print("near +1 means one can be exchanged for the other almost freely")
```

Every snippet on these pages runs in `tests/test_wiki_snippets_run.py`, so
one that stops working fails the suite instead of sitting here misleading a
reader.

## Further reading

- A. Raue et al., "Structural and practical identifiability analysis of
  partially observed dynamical models by exploiting the profile likelihood",
  *Bioinformatics* **25**, 1923 (2009): the source of the distinction and the
  profile-based diagnostic used on this page.
- [The profile likelihood](profile-likelihood.md), the tool that maps the
  valley.
- [Injection-recovery testing](injection-recovery.md), for whether the
  intervals a degenerate problem produces actually cover.

## See also

- [The AC-Stark light shift](../quantities/ac-stark-light-shift.md) and
  [collisional self-broadening](../quantities/self-broadening.md), the
  quantity dossiers with their own limiting degeneracy and the measurement
  that would break it.
- [The profile likelihood](profile-likelihood.md), which maps a degenerate
  valley directly instead of approximating it by an ellipse.
- [Injection-recovery testing](injection-recovery.md), for whether a
  degenerate problem's intervals actually cover.
- [The joint fit](joint-fit.md), for what sharing a parameter across
  repeats does and does not do to a shared degeneracy.
- [Information criteria](information-criteria.md), for comparing models
  instead of separating a model's own parameters.

---

[← Information criteria](information-criteria.md) · *Statistical inference, 5 of 8* · [The profile likelihood →](profile-likelihood.md)

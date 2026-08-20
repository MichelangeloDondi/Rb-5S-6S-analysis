# Identifiability

*[wiki index](README.md) · method*

**The question.** Whether the data can actually separate two parameters, or
only determine some combination of them.
**Takes.** A fitted model and its parameter covariance. No new fitting, and
nothing beyond what a standard fit already produces.
**Gives.** The structural-versus-practical distinction, the three
diagnostics that expose a degeneracy, and what breaking one by design or by
an independent measurement is worth.
**Skip if.** The question is how to build a confidence interval that already
accounts for a nuisance parameter's freedom, rather than whether two
parameters are separable in the first place. That is
[the profile likelihood](profile-likelihood.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A parameter is identifiable if the data could, in principle, distinguish its
true value from any other. This is a property of the MODEL and the
EXPERIMENT together, not of the fitting routine, and it is decided before any
data are collected. If two different parameter values predict exactly the
same observation, no amount of data, no better optimiser and no cleverer
algorithm will separate them.

The clean case is structural non-identifiability: the model is written so
that only a combination of parameters appears. If a prediction depends only
on the product $ab$, then $a$ and $b$ are separately unknowable and the
product is the only thing measured. A fit will still return values for both,
because software returns whatever the optimiser stopped at, and their
apparent precision will be an artefact of where it started.

The commoner case is practical non-identifiability: the parameters are
distinguishable in principle, but only through a feature the data do not
resolve at the available signal-to-noise. Here the likelihood has a long
flat valley rather than an exactly flat direction, and estimates slide along
it. The diagnostics are the same in both cases and there are three worth
running: the parameter covariance, whose near-unit correlations name the
degenerate pairs, the condition number of the sensitivity matrix, which says
how nearly singular the problem is, and the
[profile likelihood](profile-likelihood.md), which maps the valley directly
instead of approximating it by an ellipse at one point.

The practical remedy is never a better fitter. It is to change the
experiment, by adding a measurement that moves one parameter and not the
other, or to stop reporting the individual parameters and report the
combination the data actually determine.

## What problem it solves

It answers the question that decides whether a number should be published:
does this dataset determine this quantity, or does it only determine
something the quantity is part of. Answering it early converts an
unfalsifiable result into either a real measurement or an honest bound.

## Where this repository uses it

It is the reason several quantities here are reported as bounds rather than
values, and the analysis is worked in full in
[methods chapter 6 section 4.10](../methods/06_the_statistics.md), with the
numbers committed to
[`results/identifiability.csv`](../../results/identifiability.csv) and drawn
in the figure below.

The degeneracy is physical and unavoidable: the collisional width, the laser
width and the transit width all broaden the same line, so a single line
constrains their sum far better than their split. The chapter makes that
quantitative on one bright condition, with all three widths free, in two
layers: a local covariance analysis and a global profile map over the pair.

The most instructive part is what the map found. A single-start fit of all
three widths settles in one minimum. The profile map exposed a second, deeper
one elsewhere in the plane, and the two are separated by a gap the chapter
records rather than smooths over. Both branches are committed. That is the
difference between a fit that converged and a parameter that is determined,
and it is why the map exists at all.

![the profile-likelihood map of the two-width decomposition](../../figures/fig7_identifiability_profile.png)

*The two-width plane at one condition, with the covariance ellipse over the
profile map. The valley is straight and long, which is the degeneracy made
visible.*

## What breaking it is worth

Non-identifiability is not always permanent. Where a degenerate pair can be
separated by measuring one member independently, the gain is concrete and
worth computing before deciding whether the measurement is affordable.

In this repository the collisional and laser widths are the degenerate pair.
Simulated on a bright synthetic condition with signal-dependent noise
(`python scripts/run_width_pinning.py`, the construction stated in its
docstring), a fit with both widths free recovers the collisional width with a
scatter of 0.0070 MHz across realisations, and the same fit with the laser
width KNOWN recovers it with 0.0022 MHz, a ratio of 3.18 with a spread of
0.20 across nine seeds. The spread is quoted because the ratio of two
Monte-Carlo standard deviations moves from seed to seed, and an earlier
version of this passage quoted a single draw of 3.4, which turned out to be
the largest of the nine. The absolute
scatters belong to that idealised condition, where the real record adds block
drift and gain scatter on top, and the ratio is the transferable part: an
independent laser diagnostic is worth more to this experiment than any
improvement to the fitting, by a factor the simulation now states with its
construction attached.

### The factor is not one number, and the arithmetic says which

A simulated scatter ratio answers the question at ONE condition. The general
answer is arithmetic, and it explains why different parts of this record quote
different factors for what looks like the same purchase.

Conditioning a multivariate normal on one member of a correlated pair reduces
the other's variance to $(1-\rho^2)$ of its joint value, so its uncertainty
falls by $\sqrt{1-\rho^2}$. The factor bought is therefore
$1/\sqrt{1-\rho^2}$, which depends on the correlation and on nothing else. It
does not improve with more traces.

| where the correlation was measured | $\rho$ | factor $1/\sqrt{1-\rho^2}$ |
|---|---|---|
| median across the 32 committed conditions | $-0.90$ | 2.29 |
| the tutorial's synthetic design point | $-0.9177$ | 2.52 |
| the bright condition of the pinning simulation above | $-0.9417$ | 2.97 |

The last row is the check on the first two. The pinning simulation MEASURES
$3.18 \pm 0.20$ by Monte Carlo at a condition whose own fitted correlation is
$-0.9417$, where the arithmetic predicts 2.97. The two agree to 7 per cent,
and the residual is what a scatter ratio carries that a covariance ratio does
not: twenty per-trace nuisance parameters, a boundary at zero collisional
width, and the non-Gaussian tail of a nonlinear fit. The correlation itself is
identical to four decimals in every seed, which is what the arithmetic
predicts, since a correlation is a property of the design rather than of the
noise draw.

These are floor numbers rather than numbers of record. The producer is a
DIAGNOSTIC that writes to `private/run_logs/` and moves nothing in
`results/`, so it is run on the declared support floor (Python 3.12, numpy
2.5) rather than on the older versions that reproduce the committed CSV
digits. [`results/ENVIRONMENT_OF_RECORD.md`](../../results/ENVIRONMENT_OF_RECORD.md)
explains why those are two different statements, and the producer stamps the
versions it ran under into every row it writes.

So what an independent laser width buys this experiment is a factor between
two and three and a half, and the spread across the sites that quote it is not
disagreement between sources. It is one formula evaluated at different
correlations. `rb5s6s.forecast.external_constraint_gain` computes it, and
`scripts/run_width_pinning.py` now reports the correlation and the predicted
factor beside its measured ratio, so the two cannot drift apart unnoticed.

THE GENERAL SHAPE OF THAT ARGUMENT is worth more than the number. When two
parameters trade, the question is never only how to fit better. It is which
of them can be measured by some other instrument, and what that would buy,
and both halves are computable in advance.

## Breaking a degeneracy by DESIGN rather than by fitting

The pinning example above buys its improvement by measuring one parameter
elsewhere. The stronger move is to arrange the measurement so the degeneracy
does not form, and it is worth stating because it is frequently available and
rarely looked for.

Take two quantities that reach the data only through their product, so that a
single measurement determines the product and neither factor. No fit can
separate them, and no amount of data at that setting will. But if some
experimental knob scales one factor and not the other, then repeating the
measurement at several settings of that knob makes the product a LINE rather
than a point, and the two factors become the slope and the intercept.

The general recipe: when two parameters are degenerate, look for a control
that enters them ASYMMETRICALLY. The fitting problem is unchanged and the
experiment has been changed instead, which is usually the cheaper repair.

**A case where the search came back empty, which is the part worth
recording.** For the two widths of this experiment the search was run rather
than assumed. Span, point count and repeat count were each varied in the
[digital twin](the-digital-twin.md), and the correlation did not move:
$-0.9177$ across a 60 MHz span, $-0.9166$ across 300 MHz, and $-0.881$ at ten
times the traces. Both uncertainties fell as the data grew and the direction
the data cannot see stayed invisible, because a Lorentzian core inside a
Gaussian envelope trades the same way at every sample size. Among the
acquisition settings the asymmetric knob does not exist, which is why this
experiment takes the pinning route of the previous section rather than the
design route of this one. Reporting a failed search matters here: without it,
the next reader spends a session widening scans.

## A parameter can be in a channel and carry almost none of it

Identifiability asks whether the data determine a parameter. A question comes
before it and is easy to skip: whether the OBSERVABLE being used is sensitive to
the parameter at all. The two are different, and a parameter can be perfectly
non-degenerate in a channel that barely responds to it.

The number to compute is the derivative of the observable with respect to the
parameter, expressed in units of the observable's own scatter. Call it the
leverage. Appearing in the forward model is not leverage. A channel can be
correctly modelled, well measured, and nearly empty of the parameter, in which
case constraining that channel harder buys almost nothing.

**Match the moment to the symmetry of the perturbation.** This is where the
leverage usually hides. If a perturbation is one-sided, it moves the line's
centre and its asymmetry strongly while barely changing its width, because a
symmetric summary of an antisymmetric perturbation is insensitive by
construction. A width can be the natural-seeming handle and the wrong one. In
this repository the light-shift term moves the composite width by a few kilohertz
at its bound while moving the line centre by a hundred and fifty kilohertz
against an eighty-eight kilohertz block scatter, a factor of forty in the same
fit. The fixed natural linewidth alone, 3.493 ± 0.013 MHz on the transition axis
from the measured 6S lifetime of 45.57 ± 0.17 ns
([Gomez 2005](../lit/gomez2005.md)), is about 0.65 of the observed
5.4 MHz composite. That is a ratio of two
defined widths rather than an additive share, since the width of a convolution
does not decompose additively, and it says only that most of the observed width
is a constant no lever moves.

The practical order is therefore: build the component budget, compute the
leverage in each available channel, and only then ask whether the parameter is
identifiable in the channel that carries it.

## What can go wrong

The failure that matters is mistaking a converged fit for a determined
parameter. An optimiser always returns a point and a covariance matrix
always returns error bars, and neither is evidence that the data chose the
answer. A near-unit correlation between two parameters is the signal that
their individual values are not results.

A second, subtler one: a local covariance is a quadratic approximation at a
single point, so it describes the valley only near where the fit stopped. If
the likelihood has more than one minimum, the covariance around one of them
says nothing about the other, and reporting its error bars implies a global
statement the analysis did not make.

Third, an implementation failure that imitates non-identifiability exactly.
A parameter railed at a bound, a mis-scaled Jacobian, or a numerical
derivative with the wrong step size all produce flat directions that are
artefacts of the code. Distinguishing these from genuine degeneracy needs
the model examined, not the fit re-run.

Fourth, the resolution is easy to overstate. Adding data that moves the
degenerate combination only a little makes the valley shorter without making
it narrow, and a parameter that goes from unmeasurable to poorly measured is
still not a measurement.

## Try it

How similar the line looks when you widen the collisional part against when
you widen the laser part. An overlap near one means the data cannot tell the
two changes apart.

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
print("near +1 means one can be traded for the other almost freely")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## An exact degeneracy that the implementation broke, 2026-08-21

Every other case on this page is a degeneracy the data cannot resolve well.
This one is different: it is a degeneracy the MATHEMATICS makes exact, and the
code broke it by accident.

Lorentzians add. Convolving a Lorentzian of FWHM $a$ with one of FWHM $b$ gives
a Lorentzian of FWHM $a+b$, exactly. So if the laser's contribution is modelled
as a Lorentzian, the predicted line at a FIXED condition depends on
$\gamma_{\rm coll}$ and the laser width only through their SUM. Not weakly.
Not approximately. The two directions in parameter space are one direction, and
the orthogonal one is flat: the profile is unchanged along it to machine zero.

**Two consequences, and the second is the surprising one.**

First, any number reported for $\gamma_{\rm coll}$ alone under that kernel is
not a measurement. It is wherever the optimiser stopped sliding along the flat
direction. A per-condition figure published on 2026-08-20 was withdrawn for
exactly this reason ([the Voigt profile](voigt-profile.md)).

Second, **the code did not have the flat direction it should have had**. It
realised the identity by CONVOLVING the two Lorentzians on a finite grid. Grids
truncate Lorentzian tails, the truncation depends on the grid span, and the
span was computed from the two widths separately. So the predicted line
depended on how a fixed total width was SPLIT, by up to $3.7\times10^{-3}$ of
peak, along the direction that is provably flat.

**Why that size is not small.** Against machine precision it is enormous, and
as a bare fraction it sounds ignorable. The units that decide are the data's:
per-point noise here is $5.3\times10^{-3}$ of peak and one condition carries
about $10^4$ points, so a coherent distortion at $3.7\times10^{-3}$ has up to
seventy sigma of matched-filter leverage. A fit asked to separate the two
widths would have separated them, confidently, using round-off. This is the
general lesson: **scale a numerical artefact against the noise of the data it
will be fitted to, across the number of points it will be fitted over.**

**The fix is the general one for exact identities.** Do not compute them, IMPOSE
them. The laser width is now added into the homogeneous width instead of
convolved, which is exact by construction and one convolution cheaper. The
guard asserts the invariance BIT-IDENTICALLY rather than within a tolerance,
since any tolerance would hide the artefact's return, and it sits beside a
control asserting that the Gaussian branch, where no such symmetry holds, DOES
move under the same transformation.

**What breaks the degeneracy for real is density**, which is this page's own
theme. The collisional part scales with density and the laser part does not, so
an estimator that varies density separates them and one that does not, cannot.
That is why the headline kernel result survived the fix almost unchanged while
the per-condition one had no referent at all. The cost is visible in the
correlation between $\beta_{\rm self}$ and the shared laser width: $-0.82$ to
$-0.89$ under the Gaussian kernel, $-0.91$ to $-0.98$ under the Lorentzian. The
density ladder turns an exact degeneracy into a strong but finite one.

Measured in [`results/kernel_identifiability.csv`](../../results/kernel_identifiability.csv),
which runs in seconds and takes no data, because the contract has to exist
before the inference does.

## An instability that was actually a discrete boundary, 2026-08-20

A campaign-only bound appeared to move between code versions, which reads at
first as the worst kind of finding: a result that depends on which commit
computed it. A commit sweep across the development range, holding one
environment fixed, closed it.

The code is bit-stable. Six commits spanning nine days return the same bound
to every printed digit. What moved was the number of SAMPLES the construction
loads, from 247783 to 247788, and it moved at exactly one commit, which had
renamed a vocabulary across the tree and regenerated the committed ruler
tables as a side effect. That regeneration moved fitted ruler rates in their
eleventh digit, and the trim that selects usable samples is a DISCRETE
comparison, so an eleventh-digit change was enough to carry a boundary across
a sample edge in a few traces.

The identifiability lesson is the one this page opens with. The primary bound
is well conditioned and absorbs five samples in 247785 without moving. The
subset that appeared to move is the one whose profile is nearly flat, and a
flat profile is precisely where an arbitrarily small change in the data can
relocate the reported minimum while changing nothing about what the data
knows. **The diagnostic that would have found this in minutes is the first one
this page names: ask which subset is nearly flat BEFORE asking why its
reported value moved.**

## A haircut that was actually a degeneracy, 2026-08-15

On 2026-08-15 the wide-scan span was set to 800 MHz, one Gaussian sigma of
the Doppler pedestal, on the reasoning that fitting a free per-trace
background over that window costs a fixed haircut of signal-to-noise, taken
as 0.7. The free background and the pedestal amplitude were not two
quantities that merely share a little signal: they form a near-degenerate
pair, and the retained SNR is √(1 − ⟨g⟩²/⟨g²⟩), which evaluates to 0.140 at
that span's one sigma of reach and not the assumed 0.7. The span was
replaced by 2400 MHz, three sigma of reach, once the retained SNR was worked
out properly. [docs/HISTORY.md](../HISTORY.md) carries the row.

A parameter-correlation check between the free background and the pedestal
amplitude, the first diagnostic this page names, would have shown the
near-unit correlation and the true retained SNR before the span was chosen
rather than after.

## Further reading

- A. Raue et al., "Structural and practical identifiability analysis of
  partially observed dynamical models by exploiting the profile likelihood",
  *Bioinformatics* **25**, 1923 (2009), which introduced the distinction used
  on this page and the profile-based diagnostic.
- [The profile likelihood](profile-likelihood.md), the tool that maps the
  valley.
- [Injection-recovery testing](injection-recovery.md), which shows whether the
  intervals a degenerate problem produces actually cover.

## See also

- The quantity dossiers that apply this page's argument end to end,
  [the AC-Stark light shift](../quantities/ac-stark-light-shift.md) and
  [collisional self-broadening](../quantities/self-broadening.md), each with
  its limiting degeneracy named and the measurement that would break it.
- [The profile likelihood](profile-likelihood.md), the tool that maps a
  degenerate valley directly instead of approximating it by an ellipse.
- [Injection-recovery testing](injection-recovery.md), for whether an
  interval built on a degenerate problem actually covers.
- [The joint fit](joint-fit.md), for what sharing a parameter across repeats
  does and does not do to a degeneracy the whole dataset carries.
- [Information criteria](information-criteria.md), for the separate question
  of comparing models rather than separating a model's own parameters.

---

[← Information criteria](information-criteria.md) · *Statistical inference, 5 of 8* · [The profile likelihood →](profile-likelihood.md)

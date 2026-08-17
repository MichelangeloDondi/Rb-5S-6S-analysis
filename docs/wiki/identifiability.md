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
Simulated at the measured noise law, a fit with both free recovers the
collisional width with a scatter of 0.0396 MHz across realisations, and the
same fit with the laser width KNOWN recovers it with 0.0235 MHz, a factor of
1.7 with the bias roughly halved as well. Against a committed uncertainty of
0.0965 MHz that is the difference between a bound and a measurement, which is
why an independent laser diagnostic is worth more to this experiment than any
improvement to the fitting.

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

- [The profile likelihood](profile-likelihood.md), the tool that maps a
  degenerate valley directly instead of approximating it by an ellipse.
- [Injection-recovery testing](injection-recovery.md), for whether an
  interval built on a degenerate problem actually covers.
- [The joint fit](joint-fit.md), for what sharing a parameter across repeats
  does and does not do to a degeneracy the whole dataset carries.
- [Information criteria](information-criteria.md), for the separate question
  of comparing models rather than separating a model's own parameters.

---

[← Information criteria](information-criteria.md) · *Statistical inference, 4 of 7* · [The profile likelihood →](profile-likelihood.md)

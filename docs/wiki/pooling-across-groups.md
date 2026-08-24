# Pooling across groups

*[wiki index](README.md) · method*

**The question.** Combining groups of measurements to constrain one shared
quantity should sharpen the answer. When does it instead make the answer worse,
and how would you know?
**Takes.** [The joint fit](joint-fit.md), for what sharing a parameter means
mechanically.
**Gives.** The condition under which pooling adds information, the observable
signature when that condition fails, and a runnable demonstration that more data
with a longer lever can widen a bound.
**Skip if.** You have one group, or every group is a repeat of one measurement
under identical conditions.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Pooling is fitting several groups of data at once with a parameter held common
to all of them. The groups can be repeats, sessions, days, samples, detectors or
sites. The parameter is whatever the groups are believed to share.

The belief is the whole content of the exercise. A shared parameter asserts that
one physical quantity produced every group, and the fit cannot check that
assertion, because assuming it is how the fit is built.

## What problem it solves

More data constrains a parameter better, and pooling is how groups that were not
recorded together contribute to one number. Where the groups genuinely share the
quantity, pooling is close to free: each group adds its own leverage, and a group
recorded over a wider range of the driving variable adds more than a group
recorded over a narrow one.

That last point is worth stating as a prediction rather than an intuition.
**Extending the lever should tighten the answer.** If a group covers three times
the range and the interval gets wider, something in the setup is not what the fit
assumes.

## The condition, and the two ways it fails

Pooling adds information when the shared parameter means the same thing in every
group. It fails in two distinguishable ways.

**The groups differ in a way some free parameter absorbs.** A different detector
gain, a different offset, a different noise scale. This is ordinary and is
handled by giving each group its own nuisance parameter. The shared parameter
survives intact, and the cost is a little precision.

**The groups differ in a way no free parameter can absorb.** This is the
dangerous case, and it has a signature you can look for in advance. Write down
what the shared parameter depends on. Then ask, for each dependency, whether the
groups could differ in it and whether any nuisance in the model corresponds to
it. A dependency that differs between groups and has no nuisance opposite it is
not absorbed, and the shared parameter is then a different quantity in each
group.

The common shape of this failure is a parameter that scales with something
geometric or instrumental that was never recorded per group. Nothing in the fit
misbehaves visibly. The optimiser returns a number, the errors look reasonable,
and the number is an average over quantities that were never the same.

## Where this repository uses it

The light-shift coefficient is fitted with one value shared across three
measurement sessions and four spectral lines, argued in full in
[when a joint fit is legitimate](../big_picture/08_when-a-joint-fit-is-legitimate.md).
The cross-line sharing rests on physics, since the effect is blind to the
hyperfine index. The cross-session sharing rests on an assumption the archive
cannot check, because the coefficient scales as one over the beam waist squared
and no session recorded its own waist.

Both diagnostics below are visible in that fit. The profile is scanned in both
directions and the two directions disagree by more than the entire interval
criterion. The session with the longest lever, covering 1.44 times the largest
squared-shift reach of the others, leaves the bound looser rather than tighter.

## Repeats do not buy root-n unless they are independent

The question the experimenter asked in exactly these words: for joint fits
over repetitions of the same condition, does the uncertainty fall as the
root of n the way separate fits averaged together would? Only for the noise
that is independent between the repeats. The variance of a shared parameter
behaves as the condition-common part plus the per-repeat part over n, so
the common part sets a floor that no amount of joint fitting removes, and a
fit that models the repeats as independent will report root-n shrinkage
whether or not it is earned. This record measured the split for the
collisional chain by restricted maximum likelihood
([`beta_self_probe.csv`](../../results/beta_self_probe.csv), the pooled
rows): per-repeat scatter 0.133 MHz, condition-common 0.073 MHz, common
fraction 0.23. At those numbers five repeats buy a factor 1.6 instead of
2.24, and the gains flatten beyond three or four repeats of the same
back-to-back configuration. Joint and separate-then-average agree for the
independent part, and joint is genuinely better only where a single trace
barely constrains a nonlinear parameter. The design fix is to break the
commonality itself: interleave and re-lock between repeats, spread a
condition's repeats across the session, which converts common scatter into
the kind that averages. Until then, quote the across-repeat empirical
spread whenever it exceeds the noise-law propagation, which is this
record's standing rule.

## What can go wrong

**Reading a converged fit as a checked assumption.** Convergence is a statement
about the optimiser. It says nothing about whether the groups shared the
quantity.

**Absorbing a group difference with a nuisance fitted from the same channel as
the answer.** If a group's calibration is fitted from the same widths the answer
is read from, that nuisance is not an independent absorber and the two are
coupled.

**Comparing a subset against the pool using a row that is not a subset fit.**
Reading one group's chi-square along the pooled profile gives a number that looks
like that group's answer and is not, because the nuisances were fitted on
everything. This record made exactly that mistake and did arithmetic on it.

**Treating a badly behaved likelihood as proof the groups disagree.** A second
local minimum is a statement about the surface. Establishing that the groups
genuinely differ needs a separate measurement.

## Try it

Two groups, each with its own free offset, one shared slope. The second group
covers three times the range of the first, so it carries much more leverage. The
only thing that changes between the two runs is whether its slope agrees.

```python
import numpy as np

rng = np.random.default_rng(7)

def bound_on_shared_slope(groups):
    """95% one-sided profile bound on ONE slope shared by every group."""
    grid = np.linspace(0.0, 4.0, 4001)
    chi2 = np.zeros_like(grid)
    for i, s in enumerate(grid):
        total = 0.0
        for x, y, sd in groups:            # each group keeps a free offset
            r = y - s * x
            total += (((r - r.mean()) / sd) ** 2).sum()
        chi2[i] = total
    d = chi2 - chi2.min()
    keep = grid >= grid[d.argmin()]        # the rising side only
    return float(np.interp(2.706, d[keep], grid[keep]))

def make(slope, xmax, n=40, sd=1.0):
    x = np.linspace(0.0, xmax, n)
    return x, slope * x + rng.normal(0, sd, n), sd

short = make(1.0, 1.0)              # the trusted group, a short lever
long_agree = make(1.0, 3.0)         # same slope, THREE TIMES the lever
long_differ = make(2.0, 3.0)        # a different slope, same long lever

print(f"short group alone         {bound_on_shared_slope([short]):.3f}")
print(f"+ long lever, agreeing    {bound_on_shared_slope([short, long_agree]):.3f}   tightens")
print(f"+ long lever, disagreeing {bound_on_shared_slope([short, long_differ]):.3f}   LOOSENS")
```

The agreeing group tightens the bound by about a quarter. The disagreeing group
carries identical statistical weight and leaves the bound wider than using the
short group by itself. **Adding data made the answer worse, and nothing in the
fit reported a problem.** The only tell available without knowing the truth is
that a longer lever failed to tighten.

## Further reading

The general treatment of hierarchical and partially pooled models is standard in
the statistics literature under random effects and multilevel models, where the
question of this page appears as whether a coefficient should be fixed across
groups or allowed to vary. The vocabulary differs and the decision is the same
one.

- A. Gelman and J. Hill, *Data Analysis Using Regression and
  Multilevel/Hierarchical Models* (Cambridge University Press, 2006), the
  standard reference for partial pooling and the shrinkage this page
  describes.
- W. Viechtbauer, "Bias and efficiency of meta-analytic variance
  estimators in the random-effects model," *J. Educ. Behav. Stat.* 30,
  261 (2005), for the between-group variance estimators the REML split
  above belongs to.

## See also

- [The AC-Stark dossier](../quantities/ac-stark-light-shift.md), whose
  pooled constructions are this page's worked case, with the literature
  benchmark attached.
- [The joint fit](joint-fit.md), for the mechanics of sharing and the levels a
  parameter can be shared at.
- [Identifiability](identifiability.md), for the case where the data do not
  determine the parameter at all, which pooling improves the precision of without
  resolving.
- [The profile likelihood](profile-likelihood.md), for the interval construction
  the demonstration above uses, and for why both scan directions are run.
- [When a joint fit is legitimate](../big_picture/08_when-a-joint-fit-is-legitimate.md),
  for this repository's own two sharing decisions and the six questions they
  generalise to.

---

[← The joint fit](joint-fit.md) · *Statistical inference, 3 of 8* · [Information criteria →](information-criteria.md)

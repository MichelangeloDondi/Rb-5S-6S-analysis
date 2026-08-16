# The profile likelihood

*[wiki index](README.md) · method*

## What it is

Most fits have one or two parameters of interest and a crowd of nuisance
parameters that have to be there but are not the point. The profile
likelihood handles the crowd by RE-OPTIMISING rather than fixing. For each
candidate value $\theta$ of the parameter of interest, every nuisance
parameter $\eta$ is re-fitted to its best value at that $\theta$:

$$L_p(\theta) = \max_{\eta} L(\theta, \eta)$$

The resulting curve in $\theta$ alone is the profile. An interval is read off
where it drops by a calibrated amount from its maximum, which for a
well-behaved single parameter is the value of $\Delta\chi^2$ that
corresponds to the desired coverage.

The contrast worth holding onto is with the two cheaper alternatives. FIXING
the nuisances at their best-fit values and scanning $\theta$ pretends the
nuisances are known, and gives an interval that is too narrow, sometimes by a
large factor. Approximating the likelihood by a QUADRATIC at the best fit,
which is what a covariance matrix does, gives a symmetric interval and is
exact only if the surface really is quadratic. The profile makes neither
assumption. It costs a full re-fit per grid point and it returns asymmetric
intervals when the problem is asymmetric, which is what the likelihood says
near a physical boundary.

The profile is also a diagnostic, and this is the part most easily missed. A
profile that is FLAT over a wide range is not a wide confidence interval, it
is a statement that the data do not determine the parameter at all. The
shape of the curve carries information the interval alone discards.

## What problem it solves

It produces an interval that accounts for what is not known. When a
systematic is represented by a free nuisance parameter, profiling propagates
the ignorance about that systematic into the quoted uncertainty
automatically, instead of requiring a separate error budget line that is
easy to forget.

## Where this repository uses it

It is the construction behind the intervals quoted here, and
[methods chapter 6 section 4.12](../methods/06_the_statistics.md) gives the
reasoning for choosing it over a Bayesian posterior. Three features of this
dataset drive that choice, and they are worth reading as a template rather
than as a preference.

The headline results are bounds, and a bound is only worth its frequentist
coverage, which the repository buys by simulation rather than by assertion
(see [injection-recovery](injection-recovery.md)). The dominant systematic,
the beam waist, is deliberately kept OUT of the likelihood: marginalising it
would fold a prior invisibly into the number, whereas quoting an explicit
band keeps the conditionality visible and lets the band collapse without
redoing the inference when a measurement lands. And where the data are
thinnest, a prior would dominate the answer, so a construction that states
the data poverty out loud is preferable to one that hides it.

Profiling is also how the width degeneracy is mapped rather than merely
asserted, which is the subject of [identifiability](identifiability.md).
Bayesian machinery is used in this repository where it is the right tool,
namely model selection through [information criteria](information-criteria.md).

## What can go wrong

The most consequential misreading is treating a flat profile as a
conservative interval. A flat direction means non-identifiability, and
quoting its endpoints as a confidence interval reports the edge of the scan
grid rather than a property of the data.

An implementation failure imitates that perfectly. If the nuisance
re-optimisation at each grid point fails to converge, or starts from the
previous point and follows a local branch, the resulting curve is smooth,
plausible and wrong. A profile scan needs its own convergence audit, and
scanning from both directions is the cheap check.

Two calibration traps. The $\Delta\chi^2$ threshold for a given coverage
assumes the asymptotic regime, and with few effective degrees of freedom the
nominal threshold under-covers, so a small-sample quantile is the honest
choice. And where the maximum sits AT a physical boundary, such as a width
pinned at zero, the standard threshold does not apply at all and the interval
is one-sided by construction.

Finally, a grid that is too coarse turns a curved minimum into a piecewise
line and can place an interval edge where the true curve does not lie, which
is an arithmetic failure rather than a statistical one and is caught by
refining until the interval stops moving.

## Try it

Scan the collisional width, re-fitting the laser width at every point, and
watch the profile stay flat. That flatness is the result, not a wide interval.

```python
import numpy as np
from scipy.optimize import least_squares
from rb5s6s import composite_profile, transit_fwhm_from_w0

t = transit_fwhm_from_w0(64e-6, 130.0)
grid, p = composite_profile(0.60, 1.40, t)
nu = np.linspace(-15, 15, 1500)
truth = np.interp(nu, grid, p / p.max(), left=0, right=0)
data = truth + 0.01 * np.random.default_rng(3).standard_normal(nu.size)

def chi2_at(gc):
    def r(q):
        g, pp = composite_profile(gc, abs(q[1]), t)
        return q[0] * np.interp(nu, g, pp / pp.max(), left=0, right=0) - data
    return float(np.sum(least_squares(r, [1.0, 1.40]).fun ** 2))

base = min(chi2_at(g) for g in (0.55, 0.60, 0.65))
for gc in (0.40, 0.60, 0.80):
    print(f"gamma = {gc:.2f} MHz: delta chi2 = {chi2_at(gc) - base:6.2f}")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- W. A. Rolke, A. M. Lopez and J. Conrad, "Limits and confidence intervals in
  the presence of nuisance parameters", *Nucl. Instrum. Meth. A* **551**, 493
  (2005), for profiling as used for bounds.
- [Identifiability](identifiability.md) for what a flat profile means.
- [Methods chapter 6](../methods/06_the_statistics.md) for this repository's
  own construction and its coverage study.

---

[← Identifiability](identifiability.md) · *Statistical inference, 5 of 7* · [Injection-recovery testing →](injection-recovery.md)

# Robust fitting

*[wiki index](README.md) · method*

**The question.** Once a point is suspected of pulling a fit too far, which
loss functions stop that pull without a person deciding by eye which points
to trust.
**Takes.** An ordinary weighted least-squares fit to compare against, and no
assumption about which points, if any, are contaminated.
**Gives.** Huber and Tukey's biweight losses, the breakdown point that
separates them, and the rule that a robust fit runs beside the standard fit
rather than in place of it.
**Skip if.** You want to find which point is doing the pulling before
choosing a loss. That is [influence diagnostics](influence-diagnostics.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An ordinary least-squares fit scores every residual by its square. The
consequence is that the pull a point exerts on the fit, the derivative of its
loss with respect to the residual, grows without bound as the residual grows:
a point twice as far from the model pulls four times as hard, not twice.
Nothing in the arithmetic distinguishes a large residual produced by ordinary
noise from one produced by something the model was never asked to describe, a
stray spark on a detector, a mistimed trigger, a step in a mechanical mount,
so a single such point, particularly one placed where the design gives it
strong leverage, can move the fitted parameters further than every other
point combined.

M-estimation keeps the same structure, a sum over residuals to be minimized,
and replaces the squared loss with one that grows more slowly in the tails.
Two forms are standard. Huber loss stays the ordinary square near zero and
switches to linear beyond a tuning constant $k$:

$$\rho_k(r) = \tfrac{1}{2}r^2 \text{ for } |r|\le k, \qquad
\rho_k(r) = k|r| - \tfrac{1}{2}k^2 \text{ for } |r| \gt k$$

A residual beyond $k$ still pulls the fit, since the loss keeps growing, but
only in proportion to its size rather than to its square, so no single point
can dominate a sum the way it could under a pure square.

Tukey's biweight is redescending: past its own tuning constant $c$, the pull
a point exerts turns over and returns all the way to zero rather than
leveling off. Expressed as the weight a point carries once the loss is
written as a weighted square,

$$w(r) = \left(1 - (r/c)^2\right)^2 \text{ for } |r| \le c, \qquad
w(r) = 0 \text{ for } |r| \gt c,$$

a point beyond $c$ contributes nothing further to the fit at all, which is
what it means for far points to carry exactly zero weight under this loss.

The breakdown point is the concept that separates these two families: the
largest fraction of contaminated points an estimator can carry before its
answer can be driven arbitrarily far from the truth. An ordinary
least-squares fit breaks down at a single point, since one badly placed
observation, given enough leverage, can send the fitted line anywhere.
Huber's monotone loss bounds each point's pull but never removes it, so its
breakdown point improves on an unweighted fit but is still limited by how
many bounded pulls can accumulate. A redescending loss can reach a
materially higher breakdown point, because a point pushed past $c$ stops
contributing however far it moves, at a real cost: the objective is no
longer convex, it can carry more than one local minimum, and the iteration
below can converge to different answers depending on where it starts,
typically an ordinary or a Huber fit rather than an arbitrary point.

Both tuning constants set the exchange this family always makes. A small
constant discounts the tails aggressively and tolerates heavier
contamination, at the cost of also discounting large residuals that are
genuinely honest, which loses precision on data that turn out to be clean. A
large constant recovers that precision by approaching the ordinary
least-squares answer, at the cost of tolerating exactly the contamination the
method exists to resist. The conventional choices, $k \approx 1.345$ for
Huber and $c \approx 4.685$ for the biweight, both stated in units of a
robust scale estimate, are calibrated to keep about ninety-five per cent of
the efficiency an ordinary least-squares fit would have on data that really
are Gaussian and uncontaminated. That five per cent is the cost of carrying
the protection at all, paid whether or not any given dataset turns out to
need it.

Neither loss has a closed-form minimizer, because the normal equations stop
being linear once the loss stops being a pure square everywhere. The way
these estimators are actually computed is iteratively reweighted least
squares: fit once, ordinarily, to get a starting residual for every point,
convert each residual into a weight through the loss's own weight function,
solve the ordinary weighted least-squares problem with those weights,
recompute the residuals and the weights from the new fit, and repeat until
the weights stop moving. Every step is an ordinary linear solve, so the
method is cheap, and each step can only lower the robust objective, which is
why it converges at all.

Trimming and Winsorization are the blunter alternatives to a smooth
reweighting, and each costs something specific. Trimming discards a stated
number or fraction of the largest residuals outright and refits on the rest,
which throws away everything a removed point carried, not only the part that
looked wrong, and turns the fit on a hard threshold decided from the same
data the threshold is applied to, unless that threshold was fixed before the
data were read. Winsorization caps an extreme value at a chosen percentile
rather than deleting it, which keeps the point count intact but replaces a
real measurement with a fabricated one at the cap, and that fabricated value
then carries full weight in the fit as though it were an ordinary
observation, understating how extreme the original point actually was
without saying so anywhere in the reported uncertainty.

## What problem it solves

A measured noise law fixes the case where every point is honest about its own
uncertainty. It does nothing for the case where a point is wrong for a reason
the noise law never modeled, because there the noise law's honest weight is
exactly what lets a mismodeled point pull the fit at full strength: the point
looks quiet, so it is trusted. Robust fitting substitutes a rule, a bounded or
redescending loss applied the same way to every point, for the alternative of
a person deciding, after seeing the fit, which points look wrong.

The rule this repository would follow is that a robust fit belongs beside the
standard weighted fit, as a diagnostic, and the comparison between the two is
the actual result. When the two agree, that agreement is informative: it
shows the reported answer does not depend on whichever points a robust loss
would have discounted, and the standard fit stands with more warrant for
having been checked against one that could have moved it. When they disagree,
the disagreement names which points to look at before either number is
trusted. A robust fit that silently replaces the standard one, reported as
the only fit run, discards that comparison, and with it the one signal able
to say whether an answer rests on the whole dataset or on a handful of points
within it.

## Where this repository uses it

Not in the committed analysis. Every fit here is
[weighted by a noise law measured directly from the detector](weighted-least-squares.md),
independent of any fit's own residuals, and that measured weighting is
already doing part of the job a robust loss would otherwise be asked to do:
a point whose true noise is large already counts for less before any fitting
happens, rather than being discounted afterward for looking inconvenient.

This page exists because the repository ran a check on itself and found the
configuration it describes. An audit of the case-deletion diagnostics behind
the committed lineshape fits, leverage, Cook's distance and the externally
studentized residual, examined both the power sweep and the density sweep
and asked directly whether a single point was carrying a result it should
not. One point in the power sweep, on one of the four hyperfine peaks, sits
far off the trend the rest of that sweep follows and yet does not move the
fitted slope: outlying by its residual, but not influential by its leverage
or by how much the fit shifts when it is left out. That audit's per-point
diagnostics were not committed to `results/`, so this sentence describes
what the audit found rather than a number a reader can open, and the
statement to trust in this paragraph is the general one about the
configuration rather than the identity of the point. That is exactly the
configuration in which a robust fit and the standard weighted fit are
expected to agree, since a point with little leverage already has little say
in an ordinary weighted fit, and downweighting it further under a Huber or a
biweight loss would change the fit by very little. Running both and
reporting the agreement would be the informative comparison the section
above describes, evidence that the slope does not hinge on how that one
point is handled rather than a changed number.

The same audit also shows what robust fitting cannot fix. A separate
construction, a four-point width-against-density fit, carries one
temperature condition at leverage close to one, because the sweep leaves it
far from the other three on the density axis by design. That leverage is
exactly computable, since in a two-parameter fit it depends only on where
the points sit and not on any fitted value: at the campaign's four
temperatures the density units run 0.56, 2.45, 9.10 and 29.43, and the
leverages are 0.43, 0.37, 0.25 and **0.94** against a four-point average of
0.5. The density lever that makes the collisional slope measurable at all is
the same lever that puts one point almost entirely in charge of it. A point at that
leverage is not tested by the fit, it is followed by it: the fitted line
passes almost through it whatever it says, and every diagnostic that decides
a weight from a residual, a robust loss among them, sees almost no residual
there to act on. [Collisional self-broadening](self-broadening.md) already
reports its density-based coefficient as a bound rather than a value for
this reason. A family built to discount misbehaving residuals has nothing to
discount when the design itself keeps the residual small however the point
behaves, which is a property of the experimental design and not something a
different loss function repairs.

## What can go wrong

The clearest failure is the one the governing rule above exists to prevent:
a robust fit reported in place of the standard one, with no comparison
shown, hides the one piece of information, whether the two agree, that made
running it worth anything.

**A redescending loss can discard itself into a fit that does not exist.**
The biweight assigns exactly zero weight beyond its tuning constant, which is
what gives it a high breakdown point, and on a small sample that is a hazard
rather than a virtue. With four or five points it can drive enough of them to
zero that fewer than two distinct positions on the horizontal axis survive, at
which point a straight line is no longer determined and the normal equations
are singular. This is not a coding error and it has no fix inside the
estimator: it is what a hard rejection rule does when there is little data to
reject from. The Huber loss never reaches zero weight and does not have this
mode, which is one concrete reason to prefer it at small sample sizes. Code
that runs a biweight on few points should treat an undefined result as an
outcome to report rather than an exception to suppress, because a fit that
could not run is evidence neither for agreement nor against it.

A second is a data-insufficiency failure that mimics a design flaw. At high
leverage, near one, a robust loss cannot distinguish a trustworthy point from
a wrong one, because both leave almost the same residual once the fit is
forced through them. Treating a robust fit as a safety net at exactly the
point where it is structurally blind is worse than not running one, since it
looks as though the check was made when it was not able to run at all.

A third is a choice made after the fact. Selecting a tuning constant, a
trimming fraction or a Winsorization percentile once the fit's sensitivity to
it is already visible reopens the freedom
[preregistration](preregistration.md) exists to close, because a threshold
tuned to produce a preferred slope is not a robustness check but a search for
one particular answer dressed as a robustness check.

A fourth is implementation. A redescending loss is nonconvex, so an
iteratively reweighted solver can converge to different parameter values
depending on its starting point or its exact stopping rule, and two runs
that both report convergence are not thereby reporting the same answer.

Finally, an efficiency failure that never raises an error: applying a robust
loss to data that are genuinely clean discards real precision, the several
per cent the tuning constant is calibrated to give up, for protection the
dataset did not need, and a reported uncertainty that does not say a robust
loss was used is not stating what it actually cost.

## Try it

A small dataset with one contaminated point, fit by ordinary least squares
and by a Huber M-estimator computed through iteratively reweighted least
squares. The contaminated point pulls the ordinary slope noticeably and the
Huber fit noticeably less, because by the end of the iteration that point
carries only a fraction of an ordinary point's weight.

```python
import numpy as np

rng = np.random.default_rng(3)
x = np.linspace(1.0, 10.0, 10)
true_slope, true_intercept = 2.0, 1.0
y = true_intercept + true_slope * x + rng.normal(scale=0.3, size=x.size)
y[7] += 25.0  # one point wrong for a reason the noise law never modeled

X = np.column_stack([np.ones_like(x), x])


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def huber_irls(X, y, k=1.345, n_iter=30, tol=1e-10):
    beta = ols(X, y)
    weights = np.ones_like(y)
    for _ in range(n_iter):
        resid = y - X @ beta
        scale = max(np.median(np.abs(resid - np.median(resid))) / 0.6745,
                    1e-12)
        scaled = np.abs(resid) / scale
        weights = np.where(scaled <= k, 1.0, k / scaled)
        beta_new = np.linalg.solve(X.T @ (weights[:, None] * X),
                                    X.T @ (weights * y))
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta, weights


beta_ols = ols(X, y)
beta_huber, weights = huber_irls(X, y)

print(f"true slope: {true_slope:.3f}")
print(f"ordinary least squares slope: {beta_ols[1]:.3f}")
print(f"Huber IRLS slope:             {beta_huber[1]:.3f}")
print(f"contaminated point's converged Huber weight: {weights[7]:.3f} "
      f"(1.0 is fully trusted, near 0 is discounted)")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## Further reading

- P. J. Huber, *Robust Statistics* (Wiley, 1981), the origin of the loss
  function and the tuning constant named above.
- A. E. Beaton and J. W. Tukey, "The fitting of power series, meaning
  polynomials, illustrated on band-spectroscopic data," *Technometrics*
  **16**, 147 (1974), the origin of the biweight loss.
- P. J. Rousseeuw and A. M. Leroy, *Robust Regression and Outlier Detection*
  (Wiley, 1987), for the breakdown point and the case-deletion diagnostics
  this page's forward pointer names.
- [Weighted least squares](weighted-least-squares.md), the fitting principle
  every committed analysis in this repository actually uses, and its closing
  section on where that principle stops being enough on its own.
- [Preregistration](preregistration.md), for freezing a tuning constant or a
  trimming rule before the data it would affect are read.
- [Collisional self-broadening](self-broadening.md), for the bound this
  page's leverage discussion explains.

## See also

- [Influence diagnostics](influence-diagnostics.md), for finding which point
  is doing the pulling before a loss is chosen.
- [Resampling](resampling.md), a different way to get an interval when no
  closed-form one exists, and the block structure that trips up both.
- [Heavy-tailed models](heavy-tailed-models.md), the same continuous
  downweighting, produced by a fitted likelihood instead of a hand-chosen
  loss.

---

[← Influence diagnostics](influence-diagnostics.md) · *Robustness and influence, 2 of 7* · [Resampling →](resampling.md)

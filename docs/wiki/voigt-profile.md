# The Voigt profile

*[wiki index](README.md) · concept*

**The question.** What line shape results when a homogeneous broadening
mechanism and an inhomogeneous one act together, and why splitting the two
is so fragile.
**Takes.** Nothing beyond a Lorentzian and a Gaussian kernel. No fitting, no
data.
**Gives.** The convolution form, the Olivero-Longbothum width
approximation, and the anti-correlation a free fit finds between the
Gaussian and Lorentzian widths.
**Skip if.** You want the non-Gaussian kernel transit time contributes,
covered in [Transit-time broadening](transit-time-broadening.md), instead
of the two-kernel convolution here.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Real spectral lines are broadened by more than one mechanism at once, and
when the mechanisms are independent their effects convolve. The Voigt
profile is the convolution of a Lorentzian with a Gaussian,

$$V(\nu)=\int_{-\infty}^{\infty}L(\nu', \Gamma) G(\nu-\nu', \sigma) d\nu'$$

and it is what a line looks like when a homogeneous mechanism (a finite
lifetime, collisions) acts together with an inhomogeneous one (thermal
motion, laser jitter). A jitter kernel is usually taken as Gaussian for a
specific reason: if the frequency wander is the sum of many small
independent contributions, the central limit theorem makes its
distribution Gaussian whatever the individual sources look like.

![four line-shape kernels compared](../../figures/fig26_lineshape_kernels.png)

*The four line-shape kernels this experiment convolves, drawn at the
campaign's own widths.*

The profile has a Gaussian-like core and Lorentzian wings, because far from
line centre the Lorentzian falls as $1/\nu^2$ while the Gaussian has
already vanished. It has no closed form, so it is evaluated numerically or
through the Faddeeva function, and for seeds and sanity checks the
Olivero-Longbothum approximation for its full width at half maximum,

$$f_V\approx 0.5346 f_L+\sqrt{0.2166 f_L^2+f_G^2}$$

is accurate to a few parts in ten thousand.

One property dominates everything downstream. Near line centre, a modest
increase in the Gaussian width and a modest increase in the Lorentzian
width change the profile in very similar ways, so a fit that frees both
finds them strongly anti-correlated. The total width is determined well
and the split between the two components is fragile.

## What problem it solves

It lets one model account for two broadening mechanisms at once. Fitting a
Lorentzian alone to a line that also carries Gaussian broadening returns a
width that is wrong, with the residuals showing little sign of the error.
The Voigt form fits both contributions as separate parameters, so neither
is silently absorbed into the other.

## Where this repository uses it

The composite line here is a Voigt with a third kernel added. The natural
and collisional widths give the Lorentzian, the laser jitter gives the
Gaussian, and transit time contributes a
[cusped exponential kernel](transit-time-broadening.md) instead of a
Gaussian, so the full model is the Voigt convolved once more.
[Methods chapter 2](../methods/02_the_lineshape.md) derives it and
[`rb5s6s/lineshape.py`](../../rb5s6s/lineshape.py) builds it.

The degeneracy above is why this repository builds a whole chapter on
inference instead of a single fitting routine. The measured correlation
between the laser and collisional widths at a single condition is strong
and negative, so neither is credible alone from one line. Two things break
it: sweeping the density, which moves only the collisional part, and
sharing the laser width across the four hyperfine lines measured within
one temperature dwell. That is the subject of [the joint fit](joint-fit.md)
and of [identifiability](identifiability.md), and the numbers are in
[RESULTS.md](../RESULTS.md).

## Lorentzian widths add

The Voigt profile convolves a Lorentzian with a Gaussian, and the two
widths combine in a way that lets a fit separate them. Two Lorentzians do
not behave that way: widths $a$ and $b$ convolve to a single Lorentzian of
width $a+b$ exactly, so a line carrying two Lorentzian contributions
carries no information about how the total divides between them.

![profile likelihood map of collisional and laser width](../../figures/fig7_identifiability_profile.png)

*Profile-likelihood map of collisional against laser FWHM at one bright
condition, showing the anti-correlation valley and where a free fit lands
in it.*

This matters here because the natural width, the collisional width and a
fast-noise laser contribution are all Lorentzian. At a fixed condition only
their sum is identifiable, and the split is recoverable only if something
makes the components enter differently, which for the collisional term is
density ([identifiability](identifiability.md)).

It also constrains how the code may be written. Convolving two Lorentzians
numerically on a finite grid is not merely wasteful: the truncated tails
make the result depend on how the total is split, a dependence the
continuum identity says cannot exist. In this repository that artefact
reached 3.7e-3 of peak along exactly the direction a laser-width inference
has to measure. The fix is to impose the identity by adding the widths
directly, after which the profile is invariant to the split at machine
zero.

## Gaussian versus Lorentzian laser kernels

`laser_kind` is a parameter of `composite_profile`, `model_profile`,
`fit_condition` and `beta.py`. It selects a Gaussian or a Lorentzian shape
for the laser's own contribution to the line.

The choice matters because Lorentzians add linearly. A Lorentzian laser
width is degenerate with $\gamma_{\rm coll}$ and competes with it for the
same wings, unlike the transit kernel's separate convolution. Density
breaks the degeneracy, because the collisional part scales with density
and the laser part does not. The correlation
between $\beta_{\rm self}$ and the shared laser width runs $-0.82$ to
$-0.89$ under the Gaussian kernel and $-0.91$ to $-0.98$ under the
Lorentzian, so the density ladder converts an exact degeneracy into a
strong but finite one (`results/kernel_identifiability.csv`). Switching the
kernel shifts the headline $\beta_{\rm self}$ by 45 to 67 per cent across
the four peaks, nine to eighteen sigma on the statistical error quoted
beside it (`results/kernel_headline.csv`).

Fit quality alone cannot settle which kernel is right. The Gaussian arm
builds a Lorentzian of width $\Gamma_{\rm nat}+\gamma_{\rm coll}$ convolved
with a Gaussian of width $\sigma$. The Lorentzian arm builds a single
Lorentzian of width $\Gamma_{\rm nat}+\gamma_{\rm coll}+\sigma$. Sending
$\sigma$ to zero in the first recovers the second exactly, verified
numerically to 1.5e-5 of peak, with both widths bounded $[0,50]$ MHz so the
containing point is reachable. The Gaussian kernel therefore cannot fit
worse at any condition, and it does give the lower reduced chi-square at
all 32, with a median difference of +0.023. That tally alone reflects
parameter counting more than it reflects the laser's noise type.

What is informative is the size of the improvement, read as a nested
likelihood ratio instead of a tally of wins: a median $\Delta\chi^2$ of 232
for one extra parameter sitting on its boundary, roughly fifteen sigma,
over a range from 0.1 to 1303 across the 32 conditions. The pure Lorentzian
is excluded at better than three sigma at 26 of the 32 conditions and at
better than ten sigma at 21, while the remaining six fall below three sigma
and the data there do not settle it. The line requires Gaussian-like
content at most but not all conditions, a constraint on the laser's noise
type obtained from the lineshape instead of from the comb ([laser
frequency noise](laser-frequency-noise-and-the-linewidth.md) carries what
the comb does and does not say).

Gaussian and Lorentzian are the two extremes compared here, and the true
kernel could sit anywhere between them. The next step is a laser kernel
with a fitted Lorentzian fraction, turning the choice between two
end-members into a bound on the Lorentzian content and a proper error bar
(`results/laser_kernel.csv`, `scripts/run_laser_kernel.py`).

## What can go wrong

The degeneracy is a data-insufficiency failure, and it is easy to mistake
for a result. A fit will always return a split between the Gaussian and
Lorentzian widths, with error bars, and those error bars describe what was
measured only if the full covariance is reported alongside them. Quoting
the two widths separately with their marginal uncertainties, and not their
correlation, overstates what was measured, and a total width quoted from
the same fit can be far better determined than either part.

![the same degeneracy across twenty power-sweep conditions](../../figures/fig10_degeneracy_vs_observable.png)

*The same degeneracy across twenty power-sweep conditions: fitted widths
scatter along the constant-total-width contour while the total width
itself sits flat against power.*

A Voigt is the right form only if the broadening mechanisms are genuinely
independent, since correlated mechanisms do not convolve. A mechanism
whose true kernel is not Gaussian, transit time being the case here, will
still be absorbed by a Gaussian component if one is offered, inflating
whatever that component is called.

An implementation trap worth naming: the Gaussian parameter may be a
standard deviation or a full width at half maximum, and the two differ by
a factor of about 2.355. Code that takes one and documentation that says
the other is a bug that survives every test whose expected value came from
the same code.

## Try it

Build the composite line this repository fits, and read its total width off
the profile the package returns.

```python
from rb5s6s import composite_profile, transit_fwhm_from_w0

nu, prof = composite_profile(0.60, 1.40, transit_fwhm_from_w0(64e-6, 130.0))
above = nu[prof >= prof.max() / 2]
print(f"total FWHM {above[-1] - above[0]:.3f} MHz")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite instead of sitting here misleading
a reader.

## Further reading

- J. J. Olivero and R. L. Longbothum, "Empirical fits to the Voigt line
  width", *J. Quant. Spectrosc. Radiat. Transfer* **17**, 233 (1977), the
  source of the width approximation above.
- [Wikipedia: Voigt profile](https://en.wikipedia.org/wiki/Voigt_profile) for
  the Faddeeva-function form and its limits.
- [Transit-time broadening](transit-time-broadening.md) for the kernel this
  experiment convolves in beyond the Voigt.

## See also

- [Transit-time broadening](transit-time-broadening.md), the non-Gaussian
  kernel this experiment convolves in beyond the Voigt.
- [Identifiability](identifiability.md), why the Gaussian and Lorentzian
  split is the hard part of the inference.
- [The joint fit](joint-fit.md), how sweeping density and sharing the
  laser width across lines breaks the degeneracy.
- [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md), the
  technique that fixes the Gaussian's laser-noise coefficient at twice a
  single-pass value.

---

[← Standing waves](standing-waves.md) · *Experimental spectroscopy, 3 of 11* · [Transit-time broadening →](transit-time-broadening.md)

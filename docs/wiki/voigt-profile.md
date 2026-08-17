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
**Skip if.** You want the specific non-Gaussian kernel transit time
contributes rather than the two-kernel convolution itself. That is
[Transit-time broadening](transit-time-broadening.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

Real spectral lines are broadened by more than one mechanism at once, and
when the mechanisms are independent their effects convolve. The Voigt profile
is the convolution of a Lorentzian with a Gaussian,

$$V(\nu)=\int_{-\infty}^{\infty}L(\nu', \Gamma) G(\nu-\nu', \sigma) d\nu'$$

and it is what a line looks like when a homogeneous mechanism (a finite
lifetime, collisions) acts together with an inhomogeneous one (thermal
motion, laser jitter). A jitter kernel is usually taken as Gaussian for a
specific reason: if the frequency wander is the sum of many small
independent contributions, the central limit theorem makes its distribution
Gaussian whatever the individual sources look like.

The profile has a Gaussian-like core and Lorentzian wings, because far from
line centre the Lorentzian falls as $1/\nu^2$ while the Gaussian has already
vanished. It has no closed form, so it is evaluated numerically or through
the Faddeeva function, and for seeds and sanity checks the
Olivero-Longbothum approximation for its full width at half maximum,

$$f_V\approx 0.5346 f_L+\sqrt{0.2166 f_L^2+f_G^2}$$

is accurate to a few parts in ten thousand.

![four line-shape kernels compared](../../figures/fig26_lineshape_kernels.png)

*The kernels that build a composite line, drawn at this experiment's own
widths so the comparison is concrete. They differ in SHAPE and not only in
width, which is the property the fits turn on.*

One property dominates everything downstream. Near line centre, a modest
increase in the Gaussian width and a modest increase in the Lorentzian width
change the profile in very similar ways, so a fit that frees both finds them
strongly anti-correlated. The TOTAL width is determined well and the SPLIT
between the two components is fragile. This is not a numerical weakness to be
tuned away, it is a property of the shape itself.

## What problem it solves

It lets one model carry two mechanisms honestly. Fitting a Lorentzian to a
line that also has Gaussian broadening does not fail loudly, it returns a
width that is wrong in a way the residuals barely show, and the Voigt form
removes that particular self-deception by making both contributions explicit
parameters.

## Where this repository uses it

The composite line here is a Voigt with a third kernel added. The natural and
collisional widths give the Lorentzian, the laser jitter gives the Gaussian,
and transit time contributes a
[cusped exponential kernel](transit-time-broadening.md) rather than a
Gaussian, so the full model is the Voigt convolved once more.
[Methods chapter 2](../methods/02_the_lineshape.md) derives it and
[`rb5s6s/lineshape.py`](../../rb5s6s/lineshape.py) builds it.

The degeneracy above is the reason this repository has a whole chapter on
inference rather than a fitting routine. The measured correlation between the
laser and collisional widths at a single condition is strong and negative, so
neither is credible alone from one line. Two things break it: sweeping the
density, which moves only the collisional part, and sharing the laser width
across the four hyperfine lines measured within one temperature dwell. That
is the subject of [the joint fit](joint-fit.md) and of
[identifiability](identifiability.md), and the numbers are in
[RESULTS.md](../RESULTS.md).

## What can go wrong

The degeneracy is a data-insufficiency failure, and it is easy to mistake for
a result. A fit will always return a split between the Gaussian and
Lorentzian widths, with error bars, and those error bars are honest only if
the full covariance is reported alongside. Quoting the two widths separately
with their marginal uncertainties, and not their correlation, overstates what
was measured, and a total width quoted from the same fit can be far better
determined than either part.

Two model-form traps. A Voigt is the right form only if the broadening
mechanisms are genuinely independent, and correlated mechanisms do not
convolve. And a mechanism whose true kernel is not Gaussian, transit time
being the case here, will still be absorbed by a Gaussian component if one is
offered, quietly inflating whatever that component is called.

An implementation trap worth naming: the Gaussian parameter may be a standard
deviation or a full width at half maximum, and the two differ by a factor of
about 2.355. Code that takes one and documentation that says the other is a
bug that survives every test whose expected value came from the same code.

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
so one that stops working fails the suite rather than sitting here misleading
a reader.

## A collisional width that depended on which curve was assumed, 2026-08-15

On 2026-08-15 the infinite-window collisional width was reported as
γ(∞) = 0.246 MHz, from a 1/w extrapolation of the window scan on peak 4154.
The frozen spec called for a spread across extrapolation forms rather than
a single one, and the alternatives disagreed: 1/w² gives 0.446 MHz and an
exponential approach gives 0.504 MHz, on the peak that is the lowest of the
four. The number was retracted. Only the direction survived, since every
physical form on every peak lands below the committed value.
[docs/HISTORY.md](../HISTORY.md) carries the row.

The trap is the same one named above for the Voigt form itself: a
functional-form assumption that fits the data in hand can still be wrong,
and a single extrapolation curve returns a number with no warning that a
different, equally defensible curve returns something else. Running the
spread of forms before quoting a value, rather than after a retraction,
would have caught it at the point the number was first computed.

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

[← Standing waves](standing-waves.md) · *Experimental spectroscopy, 3 of 8* · [Transit-time broadening →](transit-time-broadening.md)

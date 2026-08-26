# Transit-time broadening

*[wiki index](README.md) · physical effect*

**The question.** Why a finite-size beam broadens a line even though
nothing perturbs the atom, and why the resulting kernel is not Gaussian.
**Takes.** Nothing beyond the idea that a finite interaction time
Fourier-broadens a response. No fitting, no data.
**Gives.** The cusped-exponential transit kernel derived for Doppler-free
two-photon spectroscopy, its dependence on beam waist and temperature, and
its degeneracy with the laser width.
**Skip if.** You want the Gaussian-plus-Lorentzian convolution this kernel
is added to, not the transit kernel itself. That is
[The Voigt profile](voigt-profile.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An atom crossing a laser beam is illuminated only while it is inside. If the
beam has waist $w_0$ and the atom's transverse speed is $v$, the interaction
lasts

$$\tau_t\sim \frac{w_0}{v}$$

and a finite interaction time Fourier-broadens the response by
$\Delta\nu_t\sim 1/(2\pi\tau_t)\sim v/(2\pi w_0)$. Nothing about the atom is
disturbed. The line broadens because the measurement was cut short, the same
reason a short pulse has a wide spectrum.

![Four line-shape kernels compared](../../figures/fig26_lineshape_kernels.png)

*Four line-shape kernels compared, showing the cusped exponential against a Gaussian of matched width.*

For a single speed the atom sees a roughly Gaussian intensity envelope while
crossing, giving a roughly Gaussian response of width proportional to
$v/w_0$. But a thermal vapour presents every speed at once, averaged over
the Maxwell-Boltzmann distribution. Since the mean speed scales as
$\sqrt{T/m}$, the width scales as

$$\Delta\nu_\text{transit} \propto \frac{\sqrt{T}}{w_0}$$

and the shape matters as much as the width, since averaging Gaussians whose
widths span the whole thermal range does not give a Gaussian. Slow atoms
pile up sharp, narrow responses at line centre, producing a cusp at zero
detuning, while fast atoms contribute broad tails that fall off
exponentially, far fatter than a Gaussian's.

For Doppler-free two-photon spectroscopy, the finite-transit line is derived
as a Lorentzian convolved with a two-sided exponential, giving the transit
kernel

$$K_\text{transit}(\nu)\propto e^{-|\nu|/b},\qquad \text{FWHM}=2b\ln 2$$

Its excess kurtosis is close to the two-sided exponential's, the
quantitative statement of "more cusped than a Gaussian".

## What problem it solves

It sets the floor on how narrow a line can be made in a beam of finite size,
converting an optical geometry into a spectroscopic width. The relation also
runs in reverse, so a line whose width is transit-limited reports the beam
waist that produced it.

## Where this repository uses it

It is one of the four kernels of the composite model in
[methods chapter 2](../methods/02_the_lineshape.md), which carries the
geometry, the Monte-Carlo that computes the kernel for this cell's exact
conditions, and the beam-waist provenance. The Monte-Carlo matters because
the analytic forms idealise twice. A real atom moves in three dimensions
through a beam of varying radius, and the two-photon signal weights each
atom by intensity squared while the collection optics see only part of the
beam.

![Monte Carlo trajectory average of the transit kernel](../../figures/fig3_transit_mc.png)

*Monte Carlo trajectory average of the transit kernel for this cell's measured beam waist and operating temperature.*

Its width depends on the beam waist, which was measured on this bench
(Rajasree, same optical table, laser and lenses) but never re-read during
the campaign, so the transit width and the laser width are degenerate
through the waist, and a waist small enough would make the natural and
transit widths alone exceed the observed line. The cusp is a falsifiable
prediction this dataset was not designed to test, and
[what we found](../methods/07_what_we_found.md) reports the outcome.

## What can go wrong

The most consequential error here is modelling the kernel as a Gaussian.
The cusp is a real, derived feature, and a Gaussian stand-in absorbs the
difference into whichever other width the fit can move, typically the laser
width. On this dataset the two model forms differ by roughly a fifth on the
self-broadening coefficient.

The second is that the transit width is only as well known as the beam
waist, since the width depends on $1/w_0$. The waist is the same-bench
measurement (Rajasree) cited above, never re-read in this campaign's own
interaction volume, so every transit-derived number is conditional on drift
since then. The waist band is stated explicitly for that reason.

The third is an implementation trap. Averaging over speeds requires the
correct weighting for the flux of atoms crossing the beam, and an unweighted
average over trajectories gives a spurious divergence at zero speed,
producing an infinitely sharp cusp that looks physical.

## Try it

The transit width follows the beam waist, the inverse dependence that makes
the waist and the laser width degenerate.

```python
from rb5s6s import transit_fwhm_from_w0

for w0_um in (32, 64, 90):
    t = transit_fwhm_from_w0(w0_um * 1e-6, 130.0)
    print(f"w0 = {w0_um:3d} um -> transit FWHM {t:.3f} MHz")
```

## Further reading

- [`../lit/biraben1979.md`](../lit/biraben1979.md), the source of the
  Lorentzian-convolved-with-exponential derivation above.
- [`../lit/borde1976.md`](../lit/borde1976.md) for the general treatment.
- [`../lit/lehmann2021.md`](../lit/lehmann2021.md) for the modern closed form
  in the transit-time limit.

## See also

- [The campaign page](../quantities/campaign.md), where the waist dependence
  makes one measurement serve two quantities.
- [The Voigt profile](voigt-profile.md), the two-kernel convolution this
  kernel adds a third term to.
- [The beam waist](the-beam-waist.md), the provenance of the waist this
  kernel's width depends on and the page that carries this number's
  lineage to the 64 µm value now used.
- [Identifiability](identifiability.md), the transit-laser degeneracy
  through the waist.
- [Monte Carlo methods](monte-carlo-methods.md), the trajectory average
  that computes this kernel for the cell.

---

[← The Voigt profile](voigt-profile.md) · *Experimental spectroscopy, 4 of 11* · [The beam waist →](the-beam-waist.md)

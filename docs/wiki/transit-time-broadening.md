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
is added to rather than the transit kernel itself. That is
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
disturbed. The line is broadened because the measurement was cut short, which
is the same reason a short pulse has a wide spectrum.

For a SINGLE speed the atom sees a roughly Gaussian intensity envelope as it
crosses, giving a roughly Gaussian frequency response of width proportional
to $v/w_0$. But a thermal vapour presents every speed at once, and the
average has to be taken over the Maxwell-Boltzmann distribution. Since the
mean speed scales as $\sqrt{T/m}$, the width scales as

$$\Delta\nu_\text{transit} \propto \frac{\sqrt{T}}{w_0}$$

and the SHAPE matters as much as the width. Averaging Gaussians whose widths
span the whole thermal range does not give a Gaussian. Slow atoms pile up
sharp, narrow responses at line centre and produce a CUSP, a sharp point at
zero detuning, while fast atoms contribute broad tails that fall off
EXPONENTIALLY, far fatter than a Gaussian's.

This is not a phenomenological guess. For Doppler-free two-photon
spectroscopy the finite-transit line was derived as exactly a Lorentzian
convolved with a two-sided exponential, so the transit kernel is

$$K_\text{transit}(\nu)\propto e^{-|\nu|/b},\qquad \text{FWHM}=2b\ln 2$$

Its excess kurtosis is close to that of the two-sided exponential, which is
the quantitative statement of "more cusped than a Gaussian".

## What problem it solves

It sets the floor on how narrow a line can be made in a beam of finite size,
and it converts an optical geometry into a spectroscopic width. Read the other
way, it is a measurement: a line whose width is transit-limited reports the
beam waist that produced it.

## Where this repository uses it

It is one of the four kernels of the composite model in
[methods chapter 2](../methods/02_the_lineshape.md), and the chapter carries
the geometry, the Monte-Carlo that computes the kernel for this cell's exact
conditions, and the beam-waist provenance. The Monte-Carlo matters because
the analytic forms above idealise twice: a real atom moves in three
dimensions through a beam whose radius varies along its length, and the
two-photon signal weights each atom by the square of the intensity while the
collection optics see only part of the beam.

The kernel is where two of this repository's hardest problems meet. Its width
depends on the beam waist, which is not measured on this bench, so the transit
width and the laser width are degenerate through the waist, and a waist small
enough would make the natural and transit widths alone exceed the observed
line. The cusp is also a falsifiable prediction that this dataset was not
designed to test, and
[what we found](../methods/07_what_we_found.md) reports the outcome of asking.

## What can go wrong

The most consequential error here is modelling the kernel as a Gaussian
because that is convenient. The cusp is a real, derived feature, and a
Gaussian stand-in absorbs the difference into whichever other width the fit
can move, typically the laser width. On this dataset the two model forms
differ by roughly a fifth on the self-broadening coefficient, so the choice
is not cosmetic.

The second is an experimental limitation dressed as a parameter. Since the
width depends on $1/w_0$, the transit contribution is only as well known as
the beam waist, and a waist adopted from another beamline rather than
measured on this one makes every transit-derived number conditional on that
transfer. This repository states the adopted band explicitly for exactly that
reason.

The third is an implementation trap with a history: averaging over speeds
requires the correct weighting for the flux of atoms crossing the beam, and
an unweighted average over trajectories gives a spurious divergence at zero
speed, which produces an infinitely sharp cusp that looks physical.

## Try it

The transit width follows the beam waist. This is the inverse dependence that
makes the waist and the laser width degenerate.

```python
from rb5s6s import transit_fwhm_from_w0

for w0_um in (32, 64, 90):
    t = transit_fwhm_from_w0(w0_um * 1e-6, 130.0)
    print(f"w0 = {w0_um:3d} um -> transit FWHM {t:.3f} MHz")
```

Every snippet on these pages is executed by `tests/test_wiki_snippets_run.py`,
so one that stops working fails the suite rather than sitting here misleading
a reader.

## What this repository got wrong once

Before 2026-07-13, the transit Monte Carlo carried exactly the
implementation trap the third bullet above names: an average over atomic
trajectories that did not weight by the flux of atoms actually crossing the
beam, the same unweighted average that produces a spuriously sharp cusp at
zero speed. [HISTORY.md](../HISTORY.md) records that fixing the missing
crossing-flux factor on 2026-07-13, and validating the corrected kernel
against Lehmann's 41.2 kHz worked example, moved the beam waist this
repository worked with from the 32 µm design nominal to roughly 50 µm.
[The beam waist](the-beam-waist.md) carries the rest of that number's
lineage, including the 64 µm value that later replaced it. A reader who
checked the Monte Carlo's speed-averaging against the flux-weighting trap
this page names, rather than trusting a run that completed without error,
would have caught the 32 µm figure before the fix did.

## Further reading

- [`../lit/biraben1979.md`](../lit/biraben1979.md), where the Doppler-free
  two-photon transit lineshape is derived as a Lorentzian convolved with a
  two-sided exponential.
- [`../lit/borde1976.md`](../lit/borde1976.md) for the general treatment.
- [`../lit/lehmann2021.md`](../lit/lehmann2021.md) for the modern closed form
  in the transit-time limit.

## See also

- [The campaign page](../quantities/campaign.md), where the transit kernel's
  dependence on the waist makes one measurement serve two quantities.
- [The Voigt profile](voigt-profile.md), the two-kernel convolution this
  transit kernel adds a third term to.
- [The beam waist](the-beam-waist.md), the provenance of the waist this
  kernel's width depends on.
- [Identifiability](identifiability.md), why the transit width and the
  laser width are degenerate through the waist.
- [Monte Carlo methods](monte-carlo-methods.md), the trajectory average
  that computes this kernel for the cell's exact conditions.

---

[← The Voigt profile](voigt-profile.md) · *Experimental spectroscopy, 4 of 8* · [The beam waist →](the-beam-waist.md)

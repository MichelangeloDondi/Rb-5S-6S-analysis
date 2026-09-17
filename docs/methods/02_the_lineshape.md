*Chapter 2 of 8 · [methods index](../methods.md)*

What sets the width of a line this narrow, mechanism by mechanism, and which of those mechanisms the dataset can actually separate. This chapter builds on the measurement chapter for the apparatus and the Doppler cancellation. It forward-references the AC-Stark ramp and the results chapter inside the transit section. It sets out the four kernels the composite model convolves, the Voigt degeneracy the statistics chapter has to manage, and the open waist every absolute number is conditional on. Not covered here: the results rather than their derivation. The one thing to carry away is that transit and laser width exchange against each other through $w_0$.

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## 2. The lineshape, derived mechanism by mechanism

The measured line is a **convolution** ($\otimes$) of independent broadening
mechanisms, because independent random frequency contributions add and the
distribution of a sum is the convolution of the distributions:

$$
I(\nu) = A \Big[
\underbrace{L(\nu;\Gamma_\text{nat}+\gamma_\text{coll})}_{\text{homogeneous}}
 \otimes
\underbrace{G(\nu;\sigma_\text{laser})}_{\text{laser}}
 \otimes
\underbrace{K_\text{transit}(\nu;T,w_0)}_{\text{transit}}
 \otimes
\underbrace{R(\nu;S_0)}_{\text{AC-Stark}}
\Big] + \text{background}
$$

The factorization assumes the four contributions are **statistically independent**,
which holds because each is driven by a physically separate random process with no
coupling between them: spontaneous emission (natural), Rb–Rb collision times
(collisional), the laser's own frequency jitter (laser), and the atom's trajectory
through the beam (transit). The laser's instantaneous frequency does not depend on
which atom is crossing or how fast it moves, and vice versa, so the joint
distribution factorizes and the profiles convolve. (A correlation between, say,
laser frequency and transit *would* break the convolution, but there is no
mechanism here to produce one. A drifting *centre* is separate and is handled
per-trace, §4.2, not as a broadening.)

Each factor is built in turn.

![the four kernels drawn separately, and the line built one convolution at a time](../../figures/fig26_lineshape_kernels.png)

*The whole chapter in advance. On the left the four kernels at the campaign's
own representative widths, drawn together so the point is visible: they differ
in shape and not only in width, and the shapes are the only handle the fit has
for telling them apart. On the right the line assembled one convolution at a
time. The natural width is about two thirds of the observed 5.37 MHz and
everything above it is apparatus, which is why the sections below spend most of
their length on the apparatus terms.*

### 2.1 Natural width

An excited state that decays with lifetime $\tau$ has a radiating dipole whose
field is a damped oscillation,

$$E(t)=E_0e^{-t/2\tau}e^{-i\omega_0 t}\quad (t\ge 0)$$

where the amplitude decays with $2\tau$ because the *population* (intensity)
decays with $\tau$. The emitted spectrum is the squared Fourier transform,

$$|\tilde E(\omega)|^2  \propto  \frac{1}{(\omega-\omega_0)^2+(1/2\tau)^2}$$

a **Lorentzian** $L(\nu)$. Its FWHM in ordinary frequency is

$$\boxed{ \Gamma_\text{nat}=\frac{1}{2\pi\tau} }
 = \frac{1}{2\pi(45.57\ \text{ns})}=3.4925\ \text{MHz}$$

Two features matter later: the Lorentzian has slowly-decaying **wings**
($\propto 1/\nu^2$, far fatter than a Gaussian), and, as a subtlety worth
stating precisely, the $6S\to5P\to5S$ cascade adds **no** width to *this* line.
The natural linewidth of the $5S\to6S$ transition is set by the lifetime of the
excited $6S$ state, and that measured $6S$ lifetime already includes *all* of its
radiative decay channels ([the measurement chapter](01_the_measurement.md)), so the subsequent $5P\to5S$ decay affects only
the linewidth of the *emitted* 795 nm fluorescence, not that of the excitation
resonance. Put differently: the transition whose frequency is scanned (the
$5S\to6S$ two-photon resonance) determines the measured linewidth, not the
transition used for detection, since the PMT is simply a population monitor for
the excited state ($6S$). *Code:* `lorentzian()` in `rb5s6s/lineshape.py`, with
$\Gamma_\text{nat}$ computed from $\tau$ in `constants.py`.

### 2.2 Collisional broadening: the same Lorentzian, grown by density

In the **impact approximation** ([Baranger](../lit/baranger1958.md), *Phys. Rev.* **112**, 855 (1958)),
a collision randomizes the optical phase far faster than atoms collide, which
keeps the line Lorentzian and grows its width linearly with density:

$$\gamma_\text{coll}=\beta_\text{self}N$$

The derivation is in [collisional self-broadening](../wiki/self-broadening.md).

Baranger's own dilute-gas/binary-collision validity condition (his interaction
volume $U\ll n^{-1}$) holds by a margin of about five hundred thousand in volume at the densest point of this record,
130 °C ($2.9\times10^{13}\ \text{cm}^{-3}$): the mean spacing is about 130 times the Weisskopf
radius ([2.5219](../../results/cooperative_channel.csv "ref:cooperative_channel:size:rate ratio at 130 C:aux") nm),
and the cube of that length ratio is the volume margin, so this Lorentzian, $N$-linear
form is not in question anywhere in the sweep. What remains open is only the
separate, later step from a $-C_6/R^6$ potential to a cross-section
([Lewis 1980](../lit/lewis1980.md), `rb5s6s/vanderwaals.py`, M18), a step
Baranger's theorem does not itself supply.

Because the convolution of two Lorentzians is a Lorentzian whose **widths
add**, the natural and collisional contributions combine analytically into a
single Lorentzian of width $\Gamma_\text{nat}+\gamma_\text{coll}$, which
exploit in the code rather than convolving numerically. The density itself
follows the saturated-vapour curve, and across the sweep

$$\frac{N(130\ ^\circ\mathrm{C})}{N(70\ ^\circ\mathrm{C})}\approx 50$$

and that large lever arm is what makes $\beta_\text{self}$ accessible.
**$\beta_\text{self}$ for $5S\to6S$ is unpublished, and measuring or bounding it
is paper deliverable C1.** *Code:* $N(T)$ in `density.py` (Nesmeyanov/Steck
correlation), with $\gamma_\text{coll}$ entering the fits in
`linefit.py`/`beta.py`.

### 2.3 Laser linewidth, and why it enters *twice*

Because the two-photon detuning sums both photons, laser jitter enters twice
where the Doppler shift cancels, so the line is twice as sensitive to
laser-frequency noise as a single pass would be
([Doppler-free two-photon spectroscopy](../wiki/doppler-free-two-photon.md)
carries that derivation). The kernel is modelled as a **Gaussian** $G(\nu)$
on central-limit grounds ([the Voigt profile](../wiki/voigt-profile.md)), with
a Lorentzian variant retained as a model-form check, §2.4. **No independent diagnostic
of the laser's jitter exists for either epoch.** No reference-cavity beat
note or self-heterodyne measurement was recorded, so $\sigma_\text{laser}$ is
inferred purely from the fitted lineshape, never benchmarked against a
separate instrument. The closest external anchor is in-house: the group's own
nanofibre study on this same line ([Gokhroo 2022](../lit/gokhroo2022.md), J. Phys. B) describes the
same laser system (M Squared SolsTis) as having sub-MHz linewidth.

That is a quoted
figure, not a recorded diagnostic, and it speaks to the laser's intrinsic
linewidth rather than to the 2025 lock's behaviour, but it is consistent with
the shape-based bound $\sigma_\text{laser}$ below 1.2 MHz (laser axis) found
here, and it is the only published number for this laser on this line. The 2025
lock was misconfigured, and one deliverable (C2) is to characterize that epoch's
$\sigma_\text{laser}$, which from the 2025 data is an **upper bound**,
because it is degenerate with the transit width (see §2.5 and
[what we found](07_what_we_found.md)).
A direct beam-profile measurement of $w_0$ turns this into a measurement by
removing the transit degeneracy, not by adding an independent check on the laser
itself, so $\sigma_\text{laser}$ stays a lineshape-fit result throughout.
*Code:* `gaussian()`, and `sigma_laser` in the fits, already carrying the
factor 2.

**What a Lorentzian laser component is, and what one condition can say about
it.** If the jitter is fast rather than slow, the laser contributes a
lorentzian width rather than a Gaussian one. Two Lorentzians of FWHM $a$ and
$b$ convolve to a single Lorentzian of FWHM $a+b$ exactly, so a Lorentzian
laser contribution and the collisional width enter the fixed-condition model
only through their sum. This is an identity, not an approximation, and the code
imposes it by adding the two widths rather than convolving them: done by
convolution on a finite grid the truncated tails made the profile depend on how
a fixed total was split, at up to $3.7\times10^{-3}$ of peak, which is a
numerically manufactured separability pointing along exactly the direction a
laser-width inference has to measure.

The consequence is that **$\Gamma_{L,\text{equiv}}$ is not identifiable at a
single condition at all**, and this is measured rather than argued: injecting
six values from 0 to 2.5 MHz into synthetic data and fitting them back recovers
the sum to about one part in a thousand every time while the split is
arbitrary. The separating lever is density, because the collisional width is
$\beta_\text{self} N(T)$ and moves with temperature while a laser width does
not, so the identifiable object lives in the multi-condition fit of §2.4's
consumers and nowhere else. Injecting 0.600 MHz on the narrow 110 to 130 C
ladder returns 0.599 with a spread of 0.013 over four seeds
(`results/kernel_worlds.csv`, `tests/test_gamma_l_identity.py`).

Two readings follow that the earlier form of this section did not separate.
Switching the kernel wholesale moves the hierarchical $\beta_\text{self}$ by
45 to 67 per cent, nine to eighteen sigma on its statistical error, which is
the sensitivity of the coefficient to the choice. Whether the data prefer one
kernel is a different question, and it is answered by a nested likelihood
ratio rather than by counting wins, because the pure-Lorentzian model is
contained in the mixed one: a win count across conditions carries no
information when one model cannot fit worse than the other by construction.

### 2.4 The Voigt profile: Lorentzian $\otimes$ Gaussian

Convolving the homogeneous Lorentzian with the Gaussian laser kernel gives the
**Voigt profile**, a Gaussian-like core with Lorentzian wings and no closed
form, so it is built on a fine grid. Its definition, the Olivero-Longbothum
width approximation used for seeds, and the reason the two widths exchange
against each other are in [the Voigt profile](../wiki/voigt-profile.md).

The property that dominates the statistics is that exchange: in any real fit
$\sigma_\text{laser}$ and $\gamma_\text{coll}$ are strongly anti-correlated,
and the measured value here is $\mathrm{corr}\approx-0.85$. The *total* width is well
determined and the *split between the two* is fragile. Section 4 covers how
this split is handled. *Code:* `model_profile()`, `voigt_fwhm()`.

### 2.5 Transit-time broadening: the Lehmann cusp, not a Gaussian

A finite crossing time Fourier-broadens the line, and averaging over the
Maxwell-Boltzmann speed distribution gives a width scaling as

$$\boxed{ \Delta\nu_\text{transit} \propto \frac{\sqrt{T}}{w_0} }$$

against an estimate of $\sim0.9$ MHz at 110 °C. The **shape** matters as much as
the width. The thermal average of many Gaussians is not a Gaussian: it is a cusped
profile with exponential wings, derived as a Lorentzian convolved with a
two-sided exponential, and
[transit-time broadening](../wiki/transit-time-broadening.md) carries that
derivation with its Biraben, Borde and Lehmann lineage. The transit kernel used here is
that established two-sided exponential,

$$K_\text{transit}(\nu)\propto e^{-|\nu|/b},\qquad \text{FWHM}=2b\ln 2$$

And the derivation states a condition on the geometry, which this chapter
carried only implicitly until the source was read (2026-09-10).
[Biraben, Bassini and Cagnac](../lit/biraben1979.md) observe the atoms "over a
length L which is small compared to the Rayleigh length", so the analytic form
is a thin-slice result. `constants.collection_z_ratio` returns that ratio, and
`results/waist_ladder.csv` carries it per rung:
[0.260548](../../results/waist_ladder.csv "ref:waist_ladder:rung:1.000000:z_ratio")
at the archive's 64 um, where it holds, rising through
[0.667003](../../results/waist_ladder.csv "ref:waist_ladder:rung:0.625000:z_ratio")
at 40 um and
[1.707529](../../results/waist_ladder.csv "ref:waist_ladder:rung:0.390625:z_ratio")
at 25 um to
[4.168772](../../results/waist_ladder.csv "ref:waist_ladder:rung:0.250000:z_ratio")
at the campaign's 16 um, where it does not. The same ratio
already governs the collection window's effect on the ramp moments, so one
geometric number decides both questions.

Module **M9** (`transit_mc.py`) computes the kernel for this record's exact
conditions, a Monte-Carlo of 3D Maxwell–Boltzmann atoms crossing the full
$w(z)$ with $I^2$ weighting and the collection profile, i.e. it *builds in*
the two idealizations the analytic forms make. The first is a beam of constant
waist crossed in a plane, where a real atom moves in three dimensions through
the full $w(z)$. The second is an unweighted average over trajectories, where
the two-photon signal weights each atom by $I^2$ and the collection optics see
only part of the beam. Two lessons come out of it. First, the real kernel is *more cusped*
than a Gaussian (excess kurtosis $\sim3$, close to the two-sided exponential's
value), and a **finite** cusp once the crossing-flux weight is included (an
earlier version omitted it, weighting $\propto1/v$ near $v=0$, and produced a
spurious log-divergence, fixed 2026-07-13 and validated against
[Lehmann's](../lit/lehmann2021.md) 41.2 kHz NNO example).

The width quoted is the one the kernel *adds to the natural line* once
convolved. Second, the added width is $\sim2.1$ MHz at $w_0=32$ µm and
$\sim0.88$ MHz at 65 µm, the Monte-Carlo grid point beside the accepted
64 µm waist convention (it was $\sim1.2$ MHz at the replaced 50 µm prior). At
32 µm that is large enough that
natural⊗transit already exceeds the observed $\sim5.25$ MHz line, which
is why **$w_0=32$ µm is excluded** and why transit and the laser are degenerate
through $w_0$ ([what we found](07_what_we_found.md)).

A direct beam measurement, and whose it is matters. The owner retired this
paragraph's claim on 2026-09-10, and the retirement is stated here instead of
being edited away. The waist authority was taken to be the
[Rajasree-KP](../lit/rajasree2020.md) 2020 OIST thesis, which reports the
$1/e^2$ beam diameter as 128 µm with the same $f=150$ mm focusing lens, so
$w_0=64$ µm, and with the same 3 mm EOM aperture truncating the input beam
that the naive (untruncated) estimate misses.
[Nieddu](../lit/nieddu2019.md) (2019, Opt. Express 27, 6528, page 6530) states
the same figure, and this page preferred the thesis to the paper on the ground
that the paper's bench carried an earlier laser generation.

That preference was empty, because the thesis credits its underlying data
collection to T. Nieddu. The two reports are one measurement, taken on the
older laser, and choosing between them cannot recover a beam this campaign
ever had. The 2019 path ran a Coherent MBR 110 where the 2025 campaign ran an
M-Squared SolsTiS, and it carried no EOM where this one carries a 3 mm
aperture. **A focused waist is $w_0 = \lambda f/(\pi w_\text{in})$, a property
of the input beam and not of the lens, and the input beam is exactly what
changed.** So the record has no measurement of this bench's waist at all, and
what stood in its place was a transfer of somebody else's.

A correction to a correction, 2026-08-27, on the owner's own
statement. This paragraph previously credited the measurement to Nieddu and
demoted the thesis to a reprint, and carried a note saying that form was
itself a correction made on 2026-08-14 from an earlier "two independent
measurements". Collapsing the two reports into one removed the distinction
that actually matters, which is not how many measurements there were but
which laser each was taken on. That
direct measurement lands at the top of the transit-inferred band and
independently excludes 32 µm, agreeing with the corrected transit physics. The working prior
is $w_0=64$ µm with a 62–68 µm band (`constants.W0_BAND_M`, narrowed from
60 and 70 on 2026-08-10), and the wider ranges this section reached on the way
there, 45 to 70 and then 50 to 64 µm, are replaced by it for that purpose.

The band's width is now the weakest part of the statement: 62 to 68 µm
expresses confidence in a transfer whose lineage the paragraph above retires,
so it is a working convention and not a measured interval, and every absolute
result that rides on it stays BOUND.
Those ranges are a different quantity and are left standing where they are
stated as such: they are what this dataset's own line can accommodate with no
external input, while the band here expresses confidence in transferring a
measurement made on the beamline lineage to this bench. Only the band is
read from the constant, and only the band is what any prediction here rides
on.
[Nieddu](../lit/nieddu2019.md) additionally reports the same four two-photon peaks
at 2.43–2.60 MHz FWHM (laser axis, $\approx5$ MHz transition axis) with a
locked laser, consistent with the 2025 $\approx5.25$ MHz line.

The cusp is a *falsifiable prediction*: at the coldest, dimmest condition
(where transit is the largest fraction of a narrow line) a BIC comparison of a
Voigt against a Lorentzian⊗exponential can detect it, and to this record's
knowledge it is not cleanly resolved as a *cusp* in a thermal two-photon line
anywhere (a target for a fixed-lock session with a narrow laser). Caveat: $w_0$
is not measured on this beam, 64 µm with a 62–68 µm band, accepted from the beamline
lineage measurement above rather than measured on this beam (it was re-centred
from 32 to 50 µm when the transit physics was corrected, then from 50 to 64 µm
when that measurement was accepted, and the beam is clipped by a 3 mm aperture,
so it stays uncertain at the tens-of-% level) **until the
beam-profile measurement** (below), so every *absolute* width built on it is
preliminary. *Code:* `two_sided_exponential()`, and `transit_fwhm_at_T()`
enforces the $\sqrt T$ law.

#### Isotope dependence of the transit width
![the two transit kernels, and the gap against the density lever](../../figures/fig29_isotope_transit.png)

*The effect is real and the reason it is not corrected is the right-hand panel.
Against density, which is the lever the collisional coefficient is read from,
the misassignment is almost all constant offset, and a constant is what the free
per-line core width absorbs. The dashed line is one standard error on the
measured difference between the isotopes, drawn on the same axes.*

The $\sqrt T$ law above is really a law in $\sqrt{T/m}$, and the dataset has two
masses in the same cell. $^{85}\text{Rb}$ is the lighter, so at any temperature it
crosses the beam faster by $\sqrt{m_{87}/m_{85}}=1.011693$ and its transit
kernel is wider by that same 1.169 per cent. Every fit in this record shares one
transit width between the isotopes, which means the shared value misassigns
11.4 kHz at 130 °C.

That is stated rather than corrected, and the reason is worth giving because it
is not "the effect is small". Against density, which is the lever the
collisional coefficient is read from, the misassignment is almost entirely a
constant offset: it runs 10.53 to 11.42 kHz across the 52-fold density range, so
a straight line through it has an intercept of 10.71 kHz and a slope of
$2.61\times10^{-5}$ MHz per $10^{12}\ \text{cm}^{-3}$. The per-peak core width is free
in every construction here, so it absorbs the offset, and only the slope can
reach $\beta$. That slope is 0.41 per cent of one standard error on the measured
$\beta_{85}-\beta_{87}$, so switching the split on would move no collisional
number and would produce a diff with no physics in it.

Three places where the same 1.169 per cent is not negligible, and they are why
`transit_fwhm_at_T()` now takes an optional `isotope` argument rather than
carrying a comment:

* the transit width itself, quoted to 0.01 MHz, against an 11.4 kHz split.
* the crossing **time**, 1.156 per cent shorter for $^{85}\text{Rb}$, which sets the
  hyperfine-pumping depletion of
  [the composite model](04_the_composite_model.md) and is now taken per isotope
  in the script that computes it.
* the one-photon Doppler pedestal a wide scan would measure, 931 MHz on the
  transition axis, where 1.169 per cent is 10.9 MHz and is resolvable. On that
  observable the mass difference stops being a nuisance and becomes a handle,
  because the two pedestals are separable where the two Doppler-free cores are
  not.

The default of `transit_fwhm_at_T()` is the shared behaviour, so no committed
number moves. *Code:* `transit_fwhm_at_T(..., isotope=)`. Check 5 of
`scripts/run_zeeman_depletion.py` produces every number in this subsection.

#### Definition of the knife-edge $w_0$
$w_0$ is the beam waist, the radius at which the intensity falls to $1/e^2$ of
its on-axis value at the focus. A **knife-edge measurement** is the standard
way to measure it: a sharp opaque edge is translated (literally a
razor blade, hence "knife-edge") across the beam, perpendicular to its
propagation, and record the transmitted power $P(x)$ versus the blade position
$x$. For a Gaussian beam the blade integrates a Gaussian, so $P(x)$ traces an
error function, and its derivative is the beam's intensity profile:

$$\frac{dP}{dx} \propto \exp \Big(-\frac{2x^2}{w^2}\Big)$$

whose width gives the local radius $w$. Repeating at several positions along
the propagation axis $z$ near the focus and finding the minimum locates the
waist $w_0$. It is direct, needs no lineshape model, and is good to about a µm.

**Why a knife-edge rather than a camera?** Both are beam-profile measurements
that end in a Gaussian fit, and they differ only in the transducer, so this is a
choice of instrument, not of method. A camera's resolution is set by its pixel
spacing (typically 3–5 µm): at the fixed-lock session's small-waist config ($w_0\approx16$ µm,
so a $1/e^2$ diameter of only $\approx32$ µm) that is 6–9 pixels across the
entire beam, far too few to fit reliably, whereas the knife-edge's resolution
comes from the translation stage (sub-µm) and is indifferent to how tight the
focus is. The knife-edge also reads a power meter, with large dynamic range and
no saturation, where a camera at these powers needs attenuation that can itself
distort the mode. The trade-off is real, though: the knife-edge *assumes* a
Gaussian, returning a best-fit $w$ whether or not the beam is one.

A camera
image is the natural complement, since it shows astigmatism, ellipticity, and
any diffraction structure from aperture clipping, which is the very effect that
makes the 2025 $w_0$ uncertain, and [§2.6](03_the_ac_stark_ramp.md) derives the ramp law from a Gaussian
$I(r)$, so confirming Gaussianity would be a useful check rather than an
assumption. The planned $z$-scan (PLAN §4) already covers part of this for
free: fitting the $w(z)$ hyperbola returns $w_0$ and $z_R$ *separately*, and
since $z_R=\pi w_0^2/(M^2\lambda)$, the ratio $(\pi w_0^2/\lambda)/z_R$ is
exactly $M^2$, so the $z_R=\pi w_0^2/\lambda$ consistency test is also a
beam-quality test, albeit one that cannot separate an $M^2$ above 1 from a stage-scale
error without an independent image.

Why $w_0$ matters most here: $w_0$ sets the **transit width**
($\propto 1/w_0$, §2.5) *and* every AC-Stark magnitude ($\propto 1/w_0^2$,
[§2.6](03_the_ac_stark_ramp.md)), and it is **degenerate with $\sigma_\text{laser}$** in the fits (§2.4,
[what we found](07_what_we_found.md)). So as long as $w_0$ is only the clipped-beam prior, the transit/laser
split and all absolute coefficients stay preliminary. Measuring $w_0$ directly
in a fixed-lock session would collapse that degeneracy: transit becomes fixed, the leftover
Gaussian is then unambiguously the laser (turning the $\sigma_\text{laser}$
*bound* of [what we found](07_what_we_found.md) into a measurement,
retroactively for the 2025 data too), and $\beta_\text{self}$
and the Stark coefficient acquire their absolute scale. It constrains more
downstream numbers than any other single measurement, which is why the
specification in PLAN §3 puts it at the top of the priority order, and why it
is worth doing even on its own: it needs the beam, not the full session, and it
retroactively sharpens the existing record.

---

**Where the numbers live.** Modules M3, M5, M9, M18 · producers
`scripts/run_linefit.py`, `scripts/run_laser_epoch.py`,
`scripts/run_transit_mc.py` · results `results/linefit_conditions.csv`,
`results/laser_epoch.csv`, `results/transit_mc.csv` · figures:
`fig26_lineshape_kernels.png`, which draws the four kernels of this chapter and
assembles them, and the fit panels of later chapters, which show them at work.
Library code:
`rb5s6s/lineshape.py`, `rb5s6s/transit_mc.py`, `rb5s6s/density.py`,
`rb5s6s/vanderwaals.py`.

**What would falsify this.** A direct beam-profile measurement of $w_0$ that
disagreed with the transit width the fits return at the accepted prior. Every
absolute width in this chapter is conditional on that one number, and the
measurement can fall either side of it.

### 2.5b Hyperfine depletion along the chord

The cusp above weights every chord by its flux and its excitation probability and lets every
atom contribute its whole crossing. It is not what a two-photon line at this power sees, because
the atoms that cross are not a closed system: each excitation ends in a cascade, and a cascade
ends in the *other* ground hyperfine level with a probability $q$ this record computes on the
full Zeeman manifold (`cascade.BRANCHING_F`: [0.372](../../results/cascade_branching.csv "ref:cascade_branching:branching_f:993.4121"), [0.348](../../results/cascade_branching.csv "ref:cascade_branching:branching_f:993.4154"), [0.248](../../results/cascade_branching.csv "ref:cascade_branching:branching_f:993.4192"), [0.223](../../results/cascade_branching.csv "ref:cascade_branching:branching_f:993.4207") for the lines 4121, 4154,
4192, 4207). An atom that has cascaded into the other level is no longer resonant and is lost to
the signal for the rest of its crossing.

**The chord equation.** An atom enters the beam with the thermal populations (the wall relaxes
the hyperfine levels between crossings. the gas-phase refill is 180 times slower than one
transit, `docs/lit/jarrett1964.md`) and crosses on a chord at impact parameter $b$ with speed
$v$, seeing the intensity profile $u(t) = (w_0/w)^2 \exp[-2(b^2 + v^2 t^2)/w^2]$ at the beam
radius $w = w(z)$ of its slice. Its excitable population obeys

$$\frac{dN}{dt} = -q G(P u(t)) N,$$

with $G$ the 6S production rate per atom at the local power, the cascade's saturation carried
(`platforms.excitation_rate_per_atom`). The signal the chord contributes is $\int G N dt$ and
not $\int G dt$. the cycles it completes are $\int G dt \propto w/v$.

**Why the mean cycle count is the wrong guide.** The cycles go as $1/v$, so the slowest atoms
complete the most, and the slowest atoms are exactly the cusp's narrow core (their per-atom
width goes as $v/w$). Depletion therefore removes the narrow contributions preferentially and the
*surviving* kernel is wider than the cusp by far more than the mean cycle count suggests: at the
archive's shared condition (64 µm, 225 mW, 130 °C) the flux-weighted mean over chords is [0.012](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:cycles_mean_over_chords:mc") cycles, the
on-axis chord [0.081](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:cycles_on_axis:mc"), and the surviving kernel is wider by a fraction [0.050](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") on the line with the largest
$q$, [0.024](../../results/kernel_mc.csv "ref:kernel_mc:w90.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") at 90 µm.

Along the power arm the fraction runs [0.0015](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P25:depletion_fwhm_rel_4121:mc"), [0.0093](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P75:depletion_fwhm_rel_4121:mc"), [0.021](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P125:depletion_fwhm_rel_4121:mc"), [0.035](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P175:depletion_fwhm_rel_4121:mc"), [0.050](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") at
25 to 225 mW, faster than $P$ and slower than $P^2$ (the kernel Monte Carlo of `scripts/run_kernel_mc.py`, 100 000 chords
per node, importance-sampled in the speed and the impact parameter so the weights are flat in
the weak field, measured here at rung 3, the closed-form limit of the cusp recovered
with the window closed and the drive weak, to a third of a per cent). It is an *even* term in the transit's width with
a power of $P$ between one and two in the exponent table, which the exponent table of
the identifiability page did not have, and on the power arm a fit without it reads the transit
as a waist that shrinks with power, by far less than the FWHM says.

Depletion removes the
slowest atoms, which are the cusp's core, and leaves its wings: the surviving kernel sits three per cent
under the bare one at zero detuning and level with it at the half-width point, so a cusp fitted to it reads
only [0.0050](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:depletion_widening_rel_4121:mc") wider after the natural Lorentzian at the same condition
(a third of a micron at 64 µm), and that fitted ratio, not the FWHM's, is the factor the fit
carries. The FWHM stays the core-flattening diagnostic.

**What it does not do.** The four lines' shares move by [0.0008](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:shares_shift_abs:mc") from the thermal law at the record's own
cycle count (the reading against the model's per-crossing factor agrees to [0.0003](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:shares_abs:mc")), because the shares follow the mean depletion and not its slow tail. The measured
hyperfine-pair contrast the record measured at 225 mW is therefore not depletion, and a per-crossing
scalar at three mean cycles, which the twin and one fit arm carried, is excluded by the shares it
would move. Depletion is symmetric in the detuning to this order and enters the odd channel only
through the chirp's weighting.

**How the model carries it.** Not as a fitted parameter, which would be absorbed by the
saturation companion: the fit's transit at every node is the cusp's closed form, times the
collected column's window factor $\langle w^{-3} \rangle / \langle w^{-2} \rangle$
(`fullmodel.transit_collection_factor`: the collected kernel reads [0.948](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:transit_fwhm_rel:mc") MHz against the form's [0.947](../../results/kernel_mc.csv "ref:kernel_mc:w64.0_m1.00_r0.940_T130_P225:transit_fwhm_rel:model") at 64 µm and 225 mW), times the Monte Carlo's own
fitted-width factor at the trace's node (`kernel_gate.depletion_factor`, half a per cent at the
shared condition), read from an artefact the gate refuses to be without. Two approximations are named in every artefact: the per-atom pulse stays
Gaussian and depletion reweights atoms without reshaping it, and the loss rate is the line-centre
rate, seven per cent high at the transit's half-width. The detuning-resolved, non-convolutional
profile is the next refinement.

[← The measurement](01_the_measurement.md) · [The AC-Stark ramp →](03_the_ac_stark_ramp.md)

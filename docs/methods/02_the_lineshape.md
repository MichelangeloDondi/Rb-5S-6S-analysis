*Chapter 2 of 8 · [methods index](../methods.md)*

What sets the width of a line this narrow, mechanism by mechanism, and which of those mechanisms the dataset can actually separate. This chapter builds on the measurement chapter for the apparatus and the Doppler cancellation. It forward-references the AC-Stark ramp and the results chapter inside the transit section. It sets out the four kernels the composite model convolves, the Voigt degeneracy the statistics chapter has to manage, and the open waist every absolute number is conditional on. Not covered here: the results and not their derivation. The one thing to carry away is that transit and laser width exchange against each other through $w_0$.

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
 = \frac{1}{2\pi([45.57](../../rb5s6s/constants.py "ref:constant:TAU_6S_S:1e9")\ \text{ns})} =$$ [3.4925](../../rb5s6s/constants.py "ref:constant:GAMMA_NAT_HZ:MHz") MHz.

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
exploit in the code and not convolving numerically. The density itself
follows the saturated-vapour curve, and across the sweep

$$\frac{N(130\ ^\circ\mathrm{C})}{N(70\ ^\circ\mathrm{C})}\approx 50$$

and that large lever arm is what makes $\beta_\text{self}$ accessible.
**$\beta_\text{self}$ for $5S\to6S$ is unpublished, and measuring or bounding it
is paper deliverable C1.** *Code:* $N(T)$ in `density.py`, on the Alcock/Steck
correlation (Nesmeyanov, the central law until 2026-09-21, is now a
model-form arm), with $\gamma_\text{coll}$ entering the fits in
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
linewidth and not to the 2025 lock's behaviour, but it is consistent with
the shape-based BOUND $\sigma_\text{laser}$ below 1.2 MHz (laser axis) found
here, and it is the only published number for this laser on this line. The 2025
lock was misconfigured, and one deliverable (C2) is to characterize that epoch's
$\sigma_\text{laser}$, which from the 2025 data is an **upper BOUND**,
because it is degenerate with the transit width (see §2.5 and
[what we found](07_what_we_found.md)).
A direct beam-profile measurement of $w_0$ turns this into a measurement by
removing the transit degeneracy, not by adding an independent check on the laser
itself, so $\sigma_\text{laser}$ stays a lineshape-fit result throughout.
*Code:* `gaussian()`, and `sigma_laser` in the fits, already carrying the
factor 2.

**What a Lorentzian laser component is, and what one condition can say about
it.** If the jitter is fast and not slow, the laser contributes a
lorentzian width and not a Gaussian one. Two Lorentzians of FWHM $a$ and
$b$ convolve to a single Lorentzian of FWHM $a+b$ exactly, so a Lorentzian
laser contribution and the collisional width enter the fixed-condition model
only through their sum. This is an identity, not an approximation, and the code
imposes it by adding the two widths and not convolving them: done by
convolution on a finite grid the truncated tails made the profile depend on how
a fixed total was split, at up to $3.7\times10^{-3}$ of peak, which is a
numerically manufactured separability pointing along exactly the direction a
laser-width inference has to measure.

The consequence is that **$\Gamma_{L,\text{equiv}}$ is not identifiable at a
single condition at all**, and this is measured and not argued: injecting
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
5 to 48 per cent, 0.6 to 4.3 sigma on its statistical error, which is
the sensitivity of the coefficient to the choice. Whether the data prefer one
kernel is a different question, and it is answered by a nested likelihood
ratio and not by counting wins, because the pure-Lorentzian model is
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

And the derivation states a condition on the geometry, which this chapter carried only
implicitly until the source was read (2026-09-10). [Biraben, Bassini and
Cagnac](../lit/biraben1979.md) observe the atoms "over a length L which is small
compared to the Rayleigh length", so the analytic form is a thin-slice result.
`constants.collection_z_ratio` returns that ratio, and `results/waist_ladder.csv`
carries it per rung: [0.594191](../../results/waist_ladder.csv
"ref:waist_ladder:rung:1.000000:z_ratio") at the archive's 42.38 um
(`constants.W0_CENTRAL_M`, owner order O44), already above the 0.1–0.5 range the
thin-slice approximation assumes, not inside it, rising through
[1.521129](../../results/waist_ladder.csv "ref:waist_ladder:rung:0.625000:z_ratio") at
26.5 um and [3.894091](../../results/waist_ladder.csv
"ref:waist_ladder:rung:0.390625:z_ratio") at 16.6 um to
[9.507058](../../results/waist_ladder.csv "ref:waist_ladder:rung:0.250000:z_ratio") at
10.6 um, deep outside it.

The smaller central waist is a real, correctly computed consequence of the bore-limited
calculation and not an error. The same ratio already governs the collection window's
effect on the ramp moments, so one geometric number decides both questions.

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
$\sim1.66$ MHz at 40 µm, the Monte-Carlo grid point beside the accepted
42.38 µm waist convention (it was $\sim0.88$ MHz at the retired convention's own grid point
and $\sim1.2$ MHz at the earlier-replaced 50 µm prior). At
32 µm that is large enough that
natural⊗transit already exceeds the observed $\sim5.25$ MHz line, which
is why **$w_0=32$ µm is excluded** and why transit and the laser are degenerate
through $w_0$ ([what we found](07_what_we_found.md)).

A direct beam measurement, and whose it is matters. The owner retired this
paragraph's claim on 2026-09-10, and the retirement is stated here instead of
being edited away. The waist authority was taken to be the
[Rajasree-KP](../lit/rajasree2020.md) 2020 OIST thesis, which reports the
$1/e^2$ beam diameter as 128 µm with the same $f=150$ mm focusing lens,
and with the same 3 mm EOM aperture truncating the input beam
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
is the bore-limited [42.38](../../rb5s6s/constants.py "ref:constant:W0_CENTRAL_M:1e6") µm with a 40–45 µm band
(`constants.W0_BAND_M`, the interval stated on 2026-09-17, which replaced the
transferred band this section had narrowed from
60 and 70 on 2026-08-10), and the wider ranges this section reached on the way
there, 45 to 70 and then a tighter pair still, are replaced by it for that purpose.

The retired band's width had been the weakest part of the statement: a few microns
expressed confidence in a transfer whose lineage the paragraph above retires, so it was
a working convention and not a measured interval. The current band is the owner's own
stated interval instead, and every absolute result that rides on it stays BOUND. Those
ranges are a different quantity and are left standing where they are stated as such:
they are what this dataset's own line can accommodate with no external input, while the
band here expresses confidence in transferring a measurement made on the beamline
lineage to this bench.

Only the band is read from the constant, and only the band is what any prediction here
rides on. [Nieddu](../lit/nieddu2019.md) additionally reports the same four two-photon
peaks at 2.43–2.60 MHz FWHM (laser axis, $\approx5$ MHz transition axis) with a <!--
other-quantity: the laser-axis FWHM range, not the tilt table's residual-over-transit
ratio --> locked laser, consistent with the 2025 $\approx5.25$ MHz line.

**Retired by owner order O44, 2026-09-21.** The working prior stated above, and the band
it carried, are no longer this record's convention. `constants.W0_MEASURED_M` is renamed
`constants.W0_CENTRAL_M` and now holds 42.38 µm, this bench's own bore-limited actual focus: the
EOM's 3 mm bore truncates the input Gaussian ahead of the focusing lens, and the actual on-axis
waist is read from that clipped aperture's own diffraction (finite Hankel transform), calculated,
not transferred from the Rajasree/Nieddu lineage measurement this section traces (F104,
F105, F108, F280). `constants.W0_BAND_M` narrows to 40–45 µm, the owner's own stated interval,
not a margin computed around a transferred value. No number from the retired convention
is restated here. The history above stays as the record of how that convention was reached and
retired in turn.

That calculation has a genuine floor read from the bore's own diffraction, not fitted. As the
input radius grows large against the bore the clipped field tends to uniform illumination of the
aperture, and the focus becomes the Airy pattern, $[2J_1(v)/v]^2$ with $v=ka\rho/f$. That pattern
falls to $1/e^2$ of its peak at $v_e$, the root of $2J_1(v_e)/v_e=1/e$, which is $2.5838$
(reproduced here with scipy's `j1` and a root find). The floor is then

$$\rho_\text{floor}=\frac{v_e\lambda f}{2\pi a}=40.852\ \mu\text{m}$$

at $a=1.5$ mm (`constants.EOM_APERTURE_RADIUS_M`), $f=150$ mm (`constants.DRIVE_LENS_F_M`) and
$\lambda=993.4$ nm (`constants.LAMBDA_LASER_M`), reproduced here with the repository's own
constants, and it scales as $\lambda f/a$, so a wider bore lowers it in proportion. No input
radius through this bore focuses tighter, which is why `lineshape.aperture_onaxis_factor_actual`
raises instead of extrapolating past its own table floor (about 40.89 µm at the table's tightest
tabulated node, a near neighbour of the closed asymptote above and not the asymptote itself).

The clipped focus itself carries no independent $M^2$. Its diffraction rings fall as $r^{-3}$ in
the far field, so a second-moment radius computed by integrating $r^2$ against the intensity
depends on where the integration is cut and not on the beam, and an earlier reading of that kind
returned an $M^2$ below one, which is unphysical, and was retracted (F104). $M^2$ belongs to the
input beam instead, entering as an incoherent mixture of Laguerre-Gauss $LG(p,0)$ modes of the
input, each clipped and propagated on its own and summed in intensity, which is how
`beam_field.ClippedBeam` builds a beam of $M^2$ above 1.

A second, published check exists for the clipped focus's size and depth beside the on-axis closed
forms above. [Urey](../lit/urey2004.md) 2004 tabulates the truncated Gaussian focus's $1/e^2$
radius and Strehl-0.5 depth of focus as closed polynomial fits in the truncation ratio
$T=w_m/a$ (beam radius over aperture radius), valid for a Fresnel number above 5 and an $f$-number
above 2, where this bench sits at 15.1 and 50. At the bench's own truncation ratio, 1.64 (a
2.46 mm input into the 1.5 mm bore, aperture at the lens's front focal plane), Table 2 gives a
42.07 µm focal radius and an 8.81 mm depth. `beam_field.ClippedBeam`, the full Collins diffraction
integral through the aperture and the lens, reads 42.43 µm and 8.838 mm at the same truncation
ratio and aperture placement (reproduced here), within one per cent of both, a second validation
beside the Hankel-transform quadrature `aperture_onaxis_factor_actual` tabulates.

The aperture's distance before the lens is itself not on record. [APPARATUS](../APPARATUS.md)
places the EOM's bore ahead of the first $f=150$ mm lens and states no separation.
`beam_field.ClippedBeam` reads the same 42.43 µm focus with the aperture at the lens as with it a
focal length ahead of the lens (reproduced here, 8.785 mm depth at the aperture placed at the lens
itself), so the bore-limited central waist and its band do not depend on that distance, but where
the axial peak sits along the beam does, which bears on how much of it a fixed collection window
sees. The distance is carried as an open apparatus item
([`docs/plan/12`](../plan/12_open-apparatus-items.md)) and spanned in the twin's world through
`beam_field.ClippedBeam`'s `d_ap_m` argument, not fixed by assumption.

The cusp is a *falsifiable prediction*: at the coldest, dimmest condition
(where transit is the largest fraction of a narrow line) a BIC comparison of a
Voigt against a Lorentzian⊗exponential can detect it, and to this record's
knowledge it is not cleanly resolved as a *cusp* in a thermal two-photon line
anywhere (a target for a fixed-lock session with a narrow laser).

Caveat: $w_0$
is not measured on this beam: 42.38 µm with a 40–45 µm band, calculated from this bench's own
EOM-bore diffraction, no longer accepted from the beamline lineage measurement above (it was
re-centred from 32 to 50 µm when the transit physics was corrected, then to the beamline-lineage
prior when that measurement was accepted, and now to 42.38 µm under owner order O44's bore-limited
calculation, 2026-09-21, retiring the lineage transfer in turn), and the beam radius at the lens
itself stays an open apparatus item, so it stays uncertain **until the
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

That is stated and not corrected, and the reason is worth giving because it
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
`transit_fwhm_at_T()` now takes an optional `isotope` argument instead of
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
waist $w_0$. It is direct, needs no lineshape model, and is good to about a µm. **Why a knife-edge and not a camera?** Both are beam-profile measurements
that end in a Gaussian fit, and they differ only in the transducer, so this is a
choice of instrument, not of method.

A camera's resolution is set by its pixel
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
$I(r)$, so confirming Gaussianity would be a useful check and not an
assumption. The planned $z$-scan (PLAN §4) already covers part of this for
free: fitting the $w(z)$ hyperbola returns $w_0$ and $z_R$ *separately*, and
since $z_R=\pi w_0^2/(M^2\lambda)$, the ratio $(\pi w_0^2/\lambda)/z_R$ is
exactly $M^2$, so the $z_R=\pi w_0^2/\lambda$ consistency test is also a
beam-quality test, albeit one that cannot separate an $M^2$ above 1 from a stage-scale
error without an independent image.

That relation is the free-space one for a **second-moment width**, where
$W(z)^2=W_0^2[1+(z\lambda M^2/\pi W_0^2)^2]$ is exactly right, and **it does not
describe this bench's axial extent.** Two separate things go wrong, and they are
different quantities.

First, the on-axis half-intensity depth does not fall as $1/M^2$ even without an
aperture, because on the axis the embedded fundamental dominates: for an unclipped
mode mixture at $M^2=2$ the measured depth tracks $\pi w_0^2/\lambda$ and not
$\pi w_0^2/(M^2\lambda)$. So a second-moment Rayleigh range must not be read as
the depth of the collected volume.

Second, and specific to this geometry, the bore sets the spot. Propagating the
clipped aperture directly (`beam_field.ClippedBeam`) raises the one-sided depth as
$M^2$ rises, where the free-space relation halves it, and that direction holds for
every mode composition tested. The focal radius's own behaviour is **not**
determined by $M^2$ at all: the same $M^2$ carried in a low mode at high weight or
a high mode at low weight gives focal radii spanning the whole ruled band, because a
high-order halo is clipped before the lens while a low-order excess is not. Measured at
$M^2=3.00$ exactly, three compositions reaching that same $M^2$ give
**42.32, 45.79 and 48.31 um** (a Gaussian with a high-order halo, a Gaussian with
LG(4), and the pure LG(1) the two-mode family gives there). The two spans answer
two questions and neither corrects the other.

The first two compositions span **8.2 per cent**, on a band 40.9 to 45.0 um that is
itself only 10.0 per cent wide: that is the **forecast** span, what this bench's beam
plausibly does, and it is the number a campaign estimate takes. **That used to rest on
what a tapered amplifier typically emits, a Gaussian core with a broad low-weight
pedestal and not the pure LG(1) the two-mode family gives at $M^2=3$. Since 2026-09-23
it rests on a measurement instead.** The power through the modulator drops by about 60
per cent, and every non-clipping loss in that path lowers the total further, so the
bore's own transmission is bounded below by the measured one. A pure LG(1) input passes
about a quarter of its power at any input radius from 1.6 mm up, under that bound.

It survives only near 1.2 mm, where an ideal Gaussian would pass more than nine tenths
and almost the whole drop would have to be something other than clipping. So the
halo-dominated end is disfavoured by the bench and not merely by what amplifiers usually
do. That is an assumption replaced by a measurement on data already being collected. All
three span **14.2 per cent**: that is the **identifiability** span, and for the claim
that $M^2$ does not determine the focus a legitimate member of the family belongs in it
however unlikely this bench is to produce it, because the claim is about the parameter
and not about this beam. The earlier reading of "a few per cent" is too small on either
question. Under a hard bore an $M^2$ specification therefore does not predict the focus,
and what does is how the mode content fills the bore.

Nor is the clipped focus characterised by a single radius: its second-moment
radius is about a third larger than its $1/e^2$ radius and moves the other way
with $M^2$, and it is grid-dependent, which is the same diffraction-ring structure
recorded above. The consequences for the model are that the collected axial
fraction is far less sensitive to beam quality than the free-space relation makes
it, that no $M^2$ arm of the joint fit is quoted until the model reads its axial
profile from the propagated field, and that the unclipped scaling
$w_0\propto M^2$, which holds when no aperture sits in the focusing path, does not
apply here either.

**It must not be applied to the clipped focus in particular**: the
42.4 um this bench reads already contains the bore, whose 2.2-fold widening of the
19.3 um that the same input would give unclipped is the aperture's and does not scale
with beam quality, so multiplying 42.4 by $M^2$ counts the aperture twice. Through the
propagated field the clipped focus reads 42.43, 43.72, 45.14 and 48.31 um at $M^2=1$,
1.5, 2 and 3, against 42.4, 63.6, 84.9 and 127.3 for that multiplication. And the
unclipped power itself is a convention: at a fixed embedded scale the physical radius
grows as $M$ and the focus goes as $M$, while at a fixed physical radius it goes as
$M^2$, so a statement of the power names which radius is held. The apparatus items this leaves open are the input radius at
the bore and the mode content that fills it, not a beam-quality number.

Why $w_0$ matters most here: $w_0$ sets the **transit width** ($\propto 1/w_0$, §2.5)
*and* every AC-Stark magnitude ($\propto 1/w_0^2$, [§2.6](03_the_ac_stark_ramp.md)), and
it is **degenerate with $\sigma_\text{laser}$** in the fits (§2.4, [what we
found](07_what_we_found.md)). So as long as $w_0$ is only the clipped-beam prior, the
transit/laser split and all absolute coefficients stay preliminary.

Measuring $w_0$ directly in a fixed-lock session would collapse that degeneracy: transit
becomes fixed, the leftover Gaussian is then unambiguously the laser (turning the
$\sigma_\text{laser}$ *BOUND* of [what we found](07_what_we_found.md) into a
measurement, retroactively for the 2025 data too), and $\beta_\text{self}$ and the Stark
coefficient acquire their absolute scale. It constrains more downstream numbers than any
other single measurement, which is why the specification in PLAN §3 puts it at the top
of the priority order, and why it is worth doing even on its own: it needs the beam, not
the full session, and it retroactively sharpens the existing record.

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
the hyperfine levels between crossings. the gas-phase refill is 180 times slower than one <!-- other-quantity: a ratio of refill times -->
transit, `docs/lit/jarrett1964.md`) and crosses on a chord at impact parameter $b$ with speed
$v$, seeing the intensity profile $u(t) = (w_0/w)^2 \exp[-2(b^2 + v^2 t^2)/w^2]$ at the beam
radius $w = w(z)$ of its slice. Its excitable population obeys

$$\frac{dN}{dt} = -q G(P u(t)) N,$$

with $G$ the 6S production rate per atom at the local power, the cascade's saturation carried
(`platforms.excitation_rate_per_atom`). The signal the chord contributes is $\int G N dt$ and
not $\int G dt$. the cycles it completes are $\int G dt \propto w/v$. **Why the mean cycle count is the wrong guide.** The cycles go as $1/v$, so the slowest atoms
complete the most, and the slowest atoms are exactly the cusp's narrow core (their per-atom
width goes as $v/w$).

Depletion therefore removes the narrow contributions preferentially and the
*surviving* kernel is wider than the cusp by far more than the mean cycle count suggests: at the
node beside the calculated waist (42 µm, 225 mW, 130 °C) the flux-weighted mean over chords is [0.039](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:cycles_mean_over_chords:mc") cycles, the
on-axis chord [0.26](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:cycles_on_axis:mc"), and the surviving kernel is wider by a fraction [0.10](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") on the line with the largest
$q$, [0.024](../../results/kernel_mc.csv "ref:kernel_mc:w90.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") at 90 µm.

Along the power arm the fraction runs [0.0039](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P25:depletion_fwhm_rel_4121:mc"), [0.023](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P75:depletion_fwhm_rel_4121:mc"), [0.049](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P125:depletion_fwhm_rel_4121:mc"), [0.077](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P175:depletion_fwhm_rel_4121:mc"), [0.10](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:depletion_fwhm_rel_4121:mc") at
25 to 225 mW, faster than $P$ and slower than $P^2$ (the kernel Monte Carlo of `scripts/run_kernel_mc.py`, 100 000 chords
per node, importance-sampled in the speed and the impact parameter so the weights are flat in
the weak field, measured here at rung 3, the closed-form limit of the cusp recovered
with the window closed and the drive weak, to a third of a per cent). It is an *even* term in the transit's width with
a power of $P$ between one and two in the exponent table, which the exponent table of
the identifiability page did not have, and on the power arm a fit without it reads the transit
as a waist that shrinks with power, by far less than the FWHM says.

Depletion removes the
slowest atoms, which are the cusp's core, and leaves its wings: the surviving kernel sits under the bare one at
zero detuning and level with it at the half-width point, so a cusp fitted to it reads
only [0.014](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:depletion_widening_rel_4121:mc") wider after the natural Lorentzian at the same condition
(about six tenths of a micron at 42 µm), and that fitted ratio, not the FWHM's, is the factor the fit
carries. The FWHM stays the core-flattening diagnostic.

**What it does not do.** The four lines' shares move by [0.0021](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:shares_shift_abs:mc") from the thermal law at the record's own
cycle count (the reading against the model's per-crossing factor agrees to [0.0012](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:shares_abs:mc")), because the shares follow the mean depletion and not its slow tail. The measured
hyperfine-pair contrast the record measured at 225 mW is therefore not depletion, and a per-crossing
scalar at three mean cycles, which the twin and one fit arm carried, is excluded by the shares it
would move. Depletion is symmetric in the detuning to this order and enters the odd channel only
through the chirp's weighting.

**How the model carries it.** Not as a fitted parameter, which would be absorbed by the
saturation companion: the fit's transit at every node is the cusp's closed form, times the
collected column's window factor $\langle w^{-3} \rangle / \langle w^{-2} \rangle$
(`fullmodel.transit_collection_factor`: the collected kernel reads [1.385](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:transit_fwhm_rel:mc") MHz against the form's [1.388](../../results/kernel_mc.csv "ref:kernel_mc:w42.0_m1.00_r0.940_T130_P225:transit_fwhm_rel:model") at 42 µm and 225 mW), times the Monte Carlo's own
fitted-width factor at the trace's node (`kernel_gate.depletion_factor`, about one and a half per cent at that
node), read from an artefact the gate refuses to be without. Two approximations are named in every artefact: the per-atom pulse stays
Gaussian and depletion reweights atoms without reshaping it, and the loss rate is the line-centre
rate, seven per cent high at the transit's half-width. The detuning-resolved, non-convolutional
profile is the next refinement.


## The F statistics, and the velocity selection the model does not carry (2026-09-19)

The record treats the transit and the F statistics as one non-equilibrium process: atoms arrive from the
walls with thermal hyperfine populations, are excited along the chord, and cascade with a calculated
branching into the other ground level, depleting the excitable population as they cross. Examined
with numbers, three of its assumptions hold and one consequence is missing from the model.

[Stace and Luiten](../lit/stace2010.md) 2010 give the published framework for exactly this kind of
non-equilibrium process, worked through for one-photon absorption in an effusive vapour of
multilevel atoms: atoms enter the beam in the thermal state, justified by rapid rethermalisation
at the wall, are pumped along their straight chord by rate equations solved per velocity class in
the laboratory frame, and the surviving, optically pumped population does not follow the local
intensity, leaving a wake of pumped atoms downstream of the beam. The three assumptions examined
below adapt that same picture to the two-photon cascade and its calculated branching into the
other ground level, in place of a one-photon dark state.

**Holds: the F state an atom carries is the one it left the wall with.** Rubidium-rubidium spin exchange
at the hot end runs at about 6.3e3 per second against a transit time of 134 nanoseconds at a mean speed
of 313 metres per second, so the probability of exchanging hyperfine state during a crossing is 8.4e-4.
Hyperfine redistribution within one transit is negligible and the wall sets the entering population.

**Holds, conditionally: that entering population is statistical.** An uncoated glass wall is strongly
depolarising and hyperfine-randomising, so $(2F+1)/\sum_F(2F+1)$ is the right entering ratio. That is a
statement about an uncoated cell and it is the zero-power law besides: it describes atoms arriving, never
atoms in the beam, where the drive has already pumped. A surface treatment or a coating would break it,
and the record should say which cell it is describing wherever it uses the statistical ratio.

**Holds: the depletion is permanent within a crossing.** The two ground levels are split by gigahertz
against a line of megahertz, so an atom pumped into the other level is out of resonance for the rest of
its transit and cannot be pumped back. Recovery happens at the next wall collision, which begins a new
crossing.

**missing, and it acts on the waist: depletion velocity-selects.** Dwell time goes as one over the speed,
so a slow atom accumulates more excitation and is pumped out more readily than a fast one. If the mean
atom forfeits a tenth per crossing, an atom at half the mean speed forfeits 0.19 and one at twice the mean
forfeits 0.05. at a mean loss of a half those become 0.75 and 0.29.

**The surviving excitable population is
therefore biased fast, and a fast-biased velocity distribution produces a wider transit profile than the
thermal one.** Since the transit width goes as the speed over the waist, a width inflated by selection
reads as a waist that is too small, and the effect grows with drive power because the depletion does. The
model carries the depletion as a loss of amplitude. it does not carry the reshaping of the velocity
distribution that the same loss imposes, so the transit kernel it convolves is the undepleted one.

**And the selection is radial as well as axial, which couples it to the convolution problem.** Atoms
crossing the bright core depletes fastest, so the surviving population is also biased toward low
intensity, which is the same reweighting of the mixture that the first-order correction of the
convolution needs. The two effects are one effect seen in two coordinates, and treating either without
the other double-counts or misses depending on which is fitted.

**What to do, in order of cost.** The velocity reshaping is a one-line weight inside the chord integral
already in the model, the survival factor at each speed, so the corrected transit kernel costs no new
physics. Its size is then measured and not argued, by comparing the transit width with and without
the weight at the archive's own powers. And the comb gives the experimental handle: its orders drive the
same line at rates spanning a factor of twelve at fixed power, so the predicted power-dependence of the
selection is testable within one trace against everything else held fixed.

[← The measurement](01_the_measurement.md) · [The AC-Stark ramp →](03_the_ac_stark_ramp.md)

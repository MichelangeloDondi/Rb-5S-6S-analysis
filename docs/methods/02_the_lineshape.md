*Chapter 2 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

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
which atom is crossing or how fast it moves, and vice versa — so the joint
distribution factorizes and the profiles convolve. (A correlation between, say,
laser frequency and transit *would* break the convolution, but there is no
mechanism here to produce one; a drifting *centre* is separate and is handled
per-trace, §4.2, not as a broadening.)

We now build each factor.

### 2.1 Natural width — a finite lifetime is a Lorentzian

An excited state that decays with lifetime $\tau$ has a radiating dipole whose
field is a damped oscillation,

$$E(t)=E_0e^{-t/2\tau}e^{-i\omega_0 t}\quad (t\ge 0)$$

where the amplitude decays with $2\tau$ because the *population* (intensity)
decays with $\tau$. The emitted spectrum is the squared Fourier transform,

$$|\tilde E(\omega)|^2  \propto  \frac{1}{(\omega-\omega_0)^2+(1/2\tau)^2}$$

a **Lorentzian** $L(\nu)$. Its FWHM in ordinary frequency is

$$\boxed{ \Gamma_\text{nat}=\frac{1}{2\pi\tau} }
 = \frac{1}{2\pi(45.57\ \text{ns})}=3.4926\ \text{MHz}$$

Two features matter later: the Lorentzian has slowly-decaying **wings**
($\propto 1/\nu^2$, far fatter than a Gaussian), and — a subtlety worth stating
precisely — the $6S\to5P\to5S$ cascade adds **no** width to *this* line. The
natural linewidth of the $5S\to6S$ transition is set by the lifetime of the
excited $6S$ state; that measured $6S$ lifetime already includes *all* of its
radiative decay channels ([§1 — The measurement](01_the_measurement.md)), so the subsequent $5P\to5S$ decay affects only
the linewidth of the *emitted* 795 nm fluorescence, not that of the excitation
resonance. Put differently: the transition whose frequency is scanned (the
$5S\to6S$ two-photon resonance) determines the measured linewidth, not the
transition used for detection — the PMT is simply a population monitor for the
excited state ($6S$). *Code:* `lorentzian()` in `rb5s6s/lineshape.py`;
$\Gamma_\text{nat}$ computed from $\tau$ in `constants.py`.

### 2.2 Collisional broadening — the same Lorentzian, grown by density

In the **impact approximation** ([Baranger](../lit/baranger1958.md), *Phys. Rev.* **112**, 855 (1958)),
a collision with another Rb atom randomizes the optical phase in a time much
shorter than the mean time between collisions.
Random phase interruptions at mean rate $1/\tau_c$ are, statistically,
indistinguishable from an extra decay channel: they add a term $1/\tau_c$ to
the coherence decay rate. The line therefore *stays Lorentzian* and its width
grows linearly with collision rate, i.e. linearly with density:

$$\gamma_\text{coll}=\beta_\text{self}N$$

Because the convolution of two Lorentzians is a Lorentzian whose **widths
add**, the natural and collisional contributions combine analytically into a
single Lorentzian of width $\Gamma_\text{nat}+\gamma_\text{coll}$ — we exploit
this in the code rather than convolving numerically. The density itself
follows the saturated-vapour curve; across our sweep

$$\frac{N(130\ ^\circ\mathrm{C})}{N(70\ ^\circ\mathrm{C})}\approx 50$$

and that large lever arm is what makes $\beta_\text{self}$ accessible.
**$\beta_\text{self}$ for $5S\to6S$ is unpublished — measuring or bounding it
is paper deliverable C1.** *Code:* $N(T)$ in `density.py` (Nesmeyanov/Steck
correlation); $\gamma_\text{coll}$ enters the fits in `linefit.py`/`beta.py`.

### 2.3 Laser linewidth — and why it enters *twice*

Let the instantaneous laser frequency be $\nu_L(t)=\bar\nu_L+\delta(t)$, with
$\delta$ the frequency jitter. Unlike the Doppler shift ([§1.1 — The measurement](01_the_measurement.md)), which has
opposite signs for the two counter-propagating photons and therefore cancels,
the laser-frequency fluctuation is common to both photons — the same source,
retro-reflected onto itself — and therefore adds. For the counter-propagating
pair the two-photon detuning is

$$\big[\nu_L(1+\tfrac{v}{c})\big]+\big[\nu_L(1-\tfrac{v}{c})\big]-\nu_0
=2\nu_L-\nu_0=2\big(\bar\nu_L-\tfrac{\nu_0}{2}\big)+2\delta(t)$$

confirming the jitter appears as $2\delta$: the two-photon detuning is **twice
as sensitive to laser-frequency noise** as a single pass. If $\delta$ is the
sum of many small
independent wander sources, the central-limit theorem makes its distribution
Gaussian, so we model the laser kernel as a **Gaussian** $G(\nu)$ (a Lorentzian
variant is retained as a model-form check, §2.5). **No independent diagnostic
of the laser's jitter exists for either epoch** — no reference-cavity beat
note or self-heterodyne measurement was recorded — so $\sigma_\text{laser}$ is
inferred purely from the fitted lineshape, never benchmarked against a
separate instrument. The closest external anchor is in-house: the group's own
nanofibre study on this same line ([Gokhroo 2022](../lit/gokhroo2022.md), J. Phys. B) describes the
same laser system (M Squared SolsTis) as having sub-MHz linewidth. That is a quoted
figure, not a recorded diagnostic, and it speaks to the laser's intrinsic
linewidth rather than to the 2025 lock's behaviour — but it is consistent with
the shape-based bound $\sigma_\text{laser} \lesssim 1.0$ MHz found here, and it
is the only published number for this laser on this line. The 2025 lock was misconfigured; one deliverable (C2) is
to characterize that epoch's $\sigma_\text{laser}$ — from the archival data an
**upper bound** (it is degenerate with the transit width; see §2.5 and [§5 — What we found (2025 archive)](07_what_we_found.md)).
A direct beam-profile measurement of $w_0$ turns this into a measurement by removing the
transit degeneracy, not by adding an independent check on the laser itself —
$\sigma_\text{laser}$ stays a lineshape-fit result throughout. *Code:*
`gaussian()`; `sigma_laser` in the fits (already carrying the factor 2).

### 2.4 The Voigt profile — Lorentzian $\otimes$ Gaussian

Convolving the homogeneous Lorentzian with the Gaussian laser kernel gives the
**Voigt profile**,

$$V(\nu)=\int_{-\infty}^{\infty}L(\nu';\Gamma)G(\nu-\nu';\sigma)d\nu'$$

a Gaussian-like core with Lorentzian wings and no closed form (we build it on
a fine grid). For seeds and sanity we use the Olivero–Longbothum FWHM
approximation

$$f_V\approx 0.5346f_L+\sqrt{0.2166f_L^2+f_G^2}$$

**The property that dominates the statistics:** near the line centre, modest
increases in either the Gaussian or Lorentzian width produce very similar
changes in the Voigt profile, so in any real fit $\sigma_\text{laser}$ and
$\gamma_\text{coll}$ are strongly anti-correlated (we measure
$\mathrm{corr}\approx-0.85$). The *total* width is well determined; the
*split between the two* is fragile. Section 4 covers how this split is handled. *Code:* `model_profile()`, `voigt_fwhm()`.

### 2.5 Transit-time broadening — the Lehmann cusp (not a Gaussian)

An atom crossing a beam of waist $w_0$ with transverse speed $v$ is
"interviewed" by the light for only

$$\tau_t\sim \frac{w_0}{v}$$

and a finite interaction time Fourier-broadens the response by
$\Delta\nu_t\sim 1/(2\pi\tau_t)\sim v/(2\pi w_0)$. For a *single* speed the
atom sees a Gaussian intensity envelope in time as it crosses, giving a
roughly Gaussian frequency response of width $\propto v/w_0$. But we must
average over the MB speed distribution. Since the mean speed scales as
$\langle v\rangle\propto\sqrt{T/m}$, the **width scales as**

$$\boxed{ \Delta\nu_\text{transit} \propto \frac{\sqrt{T}}{w_0} }$$

— our estimate is $\sim0.9$ MHz at 110 °C. The **shape** is the key point:
averaging Gaussians whose widths span the whole thermal range (many narrow
ones from slow atoms, a few broad ones from fast atoms) does *not* give a
Gaussian. Slow atoms pile up sharp, narrow responses at line center → a
**cusp** (a sharp point) at $\nu=0$; fast atoms contribute broad tails → wings
that fall off **exponentially**, far fatter than a Gaussian's. This is not a
phenomenological guess: [Biraben, Bassini and Cagnac](../lit/biraben1979.md) (*J. Phys. (Paris)* **40**,
445 (1979)) derived the finite-transit Doppler-free two-photon line as exactly
a **Lorentzian convolved with a two-sided exponential** (the general treatment
is [Bordé](../lit/borde1976.md), *C. R. Acad. Sci. B* **282**, 341 (1976); the modern closed form in
the transit-time limit is [Lehmann](../lit/lehmann2021.md), *J. Chem. Phys.* **154**, 104105 (2021) —
hence "Lehmann lineshape"). So our transit kernel is that established
two-sided exponential,

$$K_\text{transit}(\nu)\propto e^{-|\nu|/b},\qquad \text{FWHM}=2b\ln 2$$

and module **M9** (`transit_mc.py`) computes the kernel for *our* exact
conditions — a Monte-Carlo of 3D Maxwell–Boltzmann atoms crossing the full
$w(z)$ with $I^2$ weighting and the collection profile, i.e. it *builds in*
objections (1) and (2) above (which the analytic forms idealize away). Two lessons come out of it. First, the real kernel is *more cusped*
than a Gaussian (excess kurtosis $\sim3$, close to the two-sided exponential's
value) — a **finite** cusp once the crossing-flux weight is included (an earlier
version omitted it, weighting $\propto1/v$ near $v=0$, and produced a spurious
log-divergence; fixed 2026-07-13, validated against [Lehmann's](../lit/lehmann2021.md) 41.2 kHz NNO
example). We quote the width the kernel *adds to the natural line* once
convolved. Second, that added width is $\sim2.1$ MHz at $w_0=32\ \mu$m and
$\sim1.2$ MHz at the $50\ \mu$m prior — so large that at 32 µm
natural$\otimes$transit already exceeds the observed $\sim5.25$ MHz line, which
is why **$w_0=32$ µm is excluded** and why transit and the laser are degenerate
through $w_0$ ([§5 — What we found (2025 archive)](07_what_we_found.md)).

**Independent corroboration.** The same 993 nm beamline was measured directly by
[Nieddu](../lit/nieddu2019.md) (2019, Opt. Express and OIST thesis) and by [Rajasree-KP](../lit/rajasree2020.md) (2020, OIST
thesis), both reporting a $1/e^2$ beam diameter of 128 µm with the same $f=150$
mm focusing lens — i.e. $w_0=64$ µm, with the same 3 mm EOM aperture truncating
the input beam that the naive (untruncated) estimate misses. That direct
measurement lands at the top of the transit-inferred 45–70 µm band and
independently excludes 32 µm, agreeing with the corrected transit physics on
$w_0\approx50$–64 µm. [Nieddu](../lit/nieddu2019.md) additionally reports the same four two-photon peaks
at 2.43–2.60 MHz FWHM (laser axis, $\approx5$ MHz transition axis) with a
locked laser — consistent with the archival $\approx5.25$ MHz line.

The cusp is a *falsifiable prediction*: at the coldest, dimmest condition
(where transit is the largest fraction of a narrow line) a BIC comparison of a
Voigt against a Lorentzian$\otimes$exponential can detect it — to our
knowledge not cleanly resolved as a *cusp* in a thermal two-photon line (an
target for a fixed-lock session with a narrow laser). Caveat: $w_0$
is only a prior ($\sim50\ \mu$m — re-centred from 32 µm when the transit physics
was corrected, since the corrected transit excludes 32 µm; the beam was clipped
by a 3 mm aperture, so it is uncertain at the tens-of-% level) **until the
beam-profile measurement** (below); every *absolute* width built on it is
therefore PRELIMINARY. *Code:* `two_sided_exponential()`; `transit_fwhm_at_T()` enforces
the $\sqrt T$ law.

#### What "the knife-edge $w_0$" means

$w_0$ is the beam waist — the radius at which the intensity falls to $1/e^2$ of
its on-axis value at the focus. A **knife-edge measurement** is the standard
way to measure it: you translate a sharp opaque edge (literally a
razor blade — hence "knife-edge") across the beam, perpendicular to its
propagation, and record the transmitted power $P(x)$ versus the blade position
$x$. For a Gaussian beam the blade integrates a Gaussian, so $P(x)$ traces an
error function, and its derivative is the beam's intensity profile:

$$\frac{dP}{dx} \propto \exp \Big(-\frac{2x^2}{w^2}\Big)$$

whose width gives the local radius $w$. Repeating at several positions along
the propagation axis $z$ near the focus and finding the minimum locates the
waist $w_0$. It is direct, needs no lineshape model, and is good to $\sim\mu$m.

**Why a knife-edge rather than a camera?** Both are beam-profile measurements
that end in a Gaussian fit; they differ only in the transducer, so this is a
choice of instrument, not of method. A camera's resolution is set by its pixel
pitch (typically 3–5 µm): at the fixed-lock session's small-waist config ($w_0\approx16$ µm,
so a $1/e^2$ diameter of only $\approx32$ µm) that is 6–9 pixels across the
entire beam, far too few to fit reliably, whereas the knife-edge's resolution
comes from the translation stage (sub-µm) and is indifferent to how tight the
focus is. The knife-edge also reads a power meter — large dynamic range, no
saturation — where a camera at these powers needs attenuation that can itself
distort the mode. The trade-off is real, though: the knife-edge *assumes* a
Gaussian, returning a best-fit $w$ whether or not the beam is one. A camera
image is the natural complement, since it shows astigmatism, ellipticity, and
any diffraction structure from aperture clipping — the very effect that makes
the archival $w_0$ uncertain — and [§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md) derives the ramp law from a Gaussian
$I(r)$, so confirming Gaussianity would be a useful check rather than an
assumption. The planned $z$-scan (PLAN §8.1) already covers part of this for
free: fitting the $w(z)$ hyperbola returns $w_0$ and $z_R$ *separately*, and
since $z_R=\pi w_0^2/(M^2\lambda)$, the ratio $(\pi w_0^2/\lambda)/z_R$ is
exactly $M^2$ — so the $z_R=\pi w_0^2/\lambda$ consistency test is also a
beam-quality test, albeit one that cannot separate $M^2>1$ from a stage-scale
error without an independent image.

Why $w_0$ matters most here: $w_0$ sets the **transit width**
($\propto 1/w_0$, §2.5) *and* every AC-Stark magnitude ($\propto 1/w_0^2$,
[§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)), and it is **degenerate with $\sigma_\text{laser}$** in the fits (§2.4,
[§5 — What we found (2025 archive)](07_what_we_found.md)) — so as long as $w_0$ is only the clipped-beam prior, the transit/laser
split and all absolute coefficients stay PRELIMINARY. Measuring $w_0$ directly
in a fixed-lock session would collapse that degeneracy: transit becomes fixed, the leftover
Gaussian is then unambiguously the laser (turning the [§5 — What we found (2025 archive)](07_what_we_found.md) $\sigma_\text{laser}$
*bound* into a measurement, retroactively for the 2025 data too), and $\beta_\text{self}$
and the Stark coefficient acquire their absolute scale. It unlocks more
downstream numbers than any other single measurement, which is why the
specification in PLAN §8 puts it at the top of the priority order — and why it
is worth doing even on its own: it needs the beam, not the full session, and it
retroactively sharpens the existing archive.

---

[← The measurement](01_the_measurement.md) · [The AC-Stark ramp →](03_the_ac_stark_ramp.md)

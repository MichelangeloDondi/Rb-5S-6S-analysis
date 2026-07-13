# Rb 5S→6S two-photon lineshape analysis

Analysis of the rubidium $5S_{1/2}\to 6S_{1/2}$ two-photon transition at
993 nm (data taken at OIST in 2025, follow-up planned October 2026). This
document doubles as the **methods draft** for the paper: every broadening
mechanism and every statistical choice is derived from first principles and
then tied to its implementation in the code. It is written to be read
top-to-bottom by someone new to the experiment. Nothing is
assumed beyond undergraduate quantum mechanics and statistics.

> **Status (2026-07-12):** the **archival data is exhausted** — every quantity
> it can yield has been extracted, and each is a documented **bound or null with
> a named October measurement that lifts it**; nothing here is an absolute
> measurement, because the dominant systematic (the beam waist $w_0$) is still an
> OPEN prior. That status is stated per-result in §5 **and now machine-attached**:
> every `results/*.csv` row carries a `status` column (BOUND/NULL/MEASURED/…), so
> a number never reads as more certain than it is. Modules M0→M10
> plus the lever-crosscheck (M4d) and Stark-sweep (M4e) analyses, **113 tests**
> passing on numpy 1.24 *and* 2.0;
> all Paper-1 deliverables (C1 collisional broadening, C2 laser epoch, C3
> power/ramp-law, C3d Stark-coefficient bound) delivered at bound/null level. A
> manuscript scaffold with drafted sections is in
> [`docs/PAPER1_SKELETON.md`](docs/PAPER1_SKELETON.md). Prose results in §5; the auto-generated
> single-source-of-truth table is [`docs/RESULTS.md`](docs/RESULTS.md); the
> prior-art delineation and collision-rate calibration are in
> [`docs/LITERATURE.md`](docs/LITERATURE.md); what October lifts is in §7.

### Notation and abbreviations (defined once, used throughout)

| symbol / term | meaning |
|---|---|
| $\nu$ | frequency; **transition axis** = the two-photon sum frequency (see §0) |
| FWHM | full width at half maximum of a lineshape |
| $\Gamma_\text{nat}$ | natural FWHM of the transition |
| $\gamma_\text{coll}$ | collisional (pressure) broadening FWHM |
| $\sigma_\text{laser}$ | laser-jitter contribution to the FWHM |
| $N$ | rubidium vapour number density (atoms cm$^{-3}$) |
| $\beta_\text{self}$ | collisional **self-broadening coefficient**, $\gamma_\text{coll}=\beta_\text{self}N$ |
| $w_0$ | laser beam waist (radius at which intensity falls to $1/e^2$) |
| $T$ | cell temperature (K unless °C stated) |
| EOM | electro-optic modulator (our frequency ruler) |
| PMT | photomultiplier tube (the detector) |
| SNR | signal-to-noise ratio |
| WLS | weighted least squares |
| MB | Maxwell–Boltzmann (speed distribution) |
| BIC | Bayesian information criterion (model-selection score) |

All width symbols above ($\Gamma_\text{nat}$, $\gamma_\text{coll}$,
$\sigma_\text{laser}$) are **FWHM**, for direct comparison with measured
linewidths. The one exception is $\sigma_\text{eff}$ in §2.6, which is a
**standard deviation** ($\sqrt{\kappa_2}$) because it sits in a cumulant
ratio — flagged again where it appears.

---

## 0. The frequency-axis convention (read this first)

Two photons are absorbed, so the resonance depends on the **sum** of their
frequencies. We therefore quote all physics on the **transition axis**,

$$\nu_\text{transition} = \nu_1 + \nu_2 = 2\nu_\text{laser}$$

which is exactly twice the laser frequency the atom sees. Anything expressed
per-photon (on the "laser axis") carries a `_LASER` suffix in the code. The
factor of two is a recurring trap (it appears again for the laser linewidth in
§2.3 and the ruler in §3), so we state it once and never mix silently. The
natural width, for example, is $\Gamma_\text{nat}=3.4926$ MHz on the transition
axis and would read $1.746$ MHz on the laser axis.

---

## 1. The measurement

A hot Rb vapour cell is illuminated by a 993 nm laser beam retro-reflected onto
itself, forming two counter-propagating fields. The laser frequency is slowly
swept across the two-photon $5S_{1/2}\to 6S_{1/2}$ transition while the
resulting fluorescence is recorded versus time — one such record is a
"trace" (mapped onto a frequency axis in §3). The observed narrow resonance
arises from atoms absorbing one photon from each counter-propagating beam, for
which the first-order Doppler shifts cancel (§1.1). The excited $6S_{1/2}$
state can decay through several channels; here we detect only the
$6S\to 5P_{1/2}\to 5S$ cascade, collecting the emitted 795 nm photons on a PMT
behind 50 dB of 795 nm filtering. Four hyperfine components are measured,
labelled by wavelength: 993.4207 nm ($^{87}$Rb $F{=}2\to2$), 993.4192 nm
($^{85}$Rb $F{=}3\to3$), 993.4154 nm ($^{85}$Rb $F{=}2\to2$), 993.4121 nm
($^{87}$Rb $F{=}1\to1$). Throughout we write these full labels; in code and
filenames the last four digits ("4207") are the key, and `constants.peak_label()`
renders the full form for all output.

### 1.1 Why two counter-propagating photons kill the Doppler width

An atom moving with velocity component $v$ along the beam sees a photon of lab
frequency $\nu$ shifted to $\nu(1+v/c)$ if it travels toward the source and
$\nu(1-v/c)$ if away. Absorbing one photon from each of the two
counter-propagating directions, the atom's two-photon resonance condition is

$$\nu\Big(1+\tfrac{v}{c}\Big) + \nu\Big(1-\tfrac{v}{c}\Big) = 2\nu$$

and the velocity term cancels **exactly to first order in $v/c$, for every
atom**. Without this trick the line would be Doppler-broadened to
$\sim 500$ MHz (the thermal spread); with it, the ~500 MHz smear collapses
and we are left with a line only a few MHz wide, whose residual width is the
stack of mechanisms below. (A second-order Doppler term $\propto (v/c)^2$
survives but is $\sim$ kHz here — negligible.)

---

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
radiative decay channels (§1), so the subsequent $5P\to5S$ decay affects only
the linewidth of the *emitted* 795 nm fluorescence, not that of the excitation
resonance. Put differently: the transition whose frequency is scanned (the
$5S\to6S$ two-photon resonance) determines the measured linewidth, not the
transition used for detection — the PMT is simply a population monitor for the
excited state ($6S$). *Code:* `lorentzian()` in `rb5s6s/lineshape.py`;
$\Gamma_\text{nat}$ computed from $\tau$ in `constants.py`.

### 2.2 Collisional broadening — the same Lorentzian, grown by density

In the **impact approximation** (Baranger, *Phys. Rev.* **112**, 855 (1958)),
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
$\delta$ the frequency jitter. For the counter-propagating pair the two-photon
detuning (using §1.1) is

$$\big[\nu_L(1+\tfrac{v}{c})\big]+\big[\nu_L(1-\tfrac{v}{c})\big]-\nu_0
=2\nu_L-\nu_0=2\big(\bar\nu_L-\tfrac{\nu_0}{2}\big)+2\delta(t)$$

The jitter appears as $2\delta$: **laser noise enters the two-photon line with
twice its single-pass magnitude.** If $\delta$ is the sum of many small
independent wander sources, the central-limit theorem makes its distribution
Gaussian, so we model the laser kernel as a **Gaussian** $G(\nu)$ (a Lorentzian
variant is retained as a model-form check, §2.5). **No independent diagnostic
of the laser's jitter exists for either epoch** — no reference-cavity beat
note or self-heterodyne measurement was recorded — so $\sigma_\text{laser}$ is
inferred purely from the fitted lineshape, never benchmarked against a
separate instrument. The 2025 lock was misconfigured; one deliverable (C2) is
to characterize that epoch's $\sigma_\text{laser}$ — from the archival data an
**upper bound** (it is degenerate with the transit width; see §2.5 and §5).
The October knife-edge $w_0$ turns this into a measurement by removing the
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

**The property that dominates the statistics:** near the core, a slightly wider
Gaussian mimics a slightly wider Lorentzian, so in any real fit
$\sigma_\text{laser}$ and $\gamma_\text{coll}$ are strongly anti-correlated (we
measure $\mathrm{corr}\approx-0.85$). The *total* width is well determined; the
*split between the two* is fragile. Section 4 is largely about handling this
honestly. *Code:* `model_profile()`, `voigt_fwhm()`.

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
phenomenological guess: Biraben, Bassini and Cagnac (*J. Phys. (Paris)* **40**,
445 (1979)) derived the finite-transit Doppler-free two-photon line as exactly
a **Lorentzian convolved with a two-sided exponential** (the general treatment
is Bordé, *C. R. Acad. Sci. B* **282**, 341 (1976); the modern closed form in
the transit-time limit is Lehmann, *J. Chem. Phys.* **154**, 104105 (2021) —
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
log-divergence; fixed 2026-07-13, validated against Lehmann's 41.2 kHz NNO
example). We quote the width the kernel *adds to the natural line* once
convolved. Second, that added width is $\sim2.1$ MHz at $w_0=32\ \mu$m and
$\sim1.2$ MHz at the $50\ \mu$m prior — so large that at 32 µm
natural$\otimes$transit already exceeds the observed $\sim5.25$ MHz line, which
is why **$w_0=32$ µm is excluded** and why transit and the laser are degenerate
through $w_0$ (§5).

**Independent corroboration.** The same 993 nm beamline was measured directly by
Nieddu (2019, Opt. Express and OIST thesis) and by Rajasree-KP (2020, OIST
thesis), both reporting a $1/e^2$ beam diameter of 128 µm with the same $f=150$
mm focusing lens — i.e. $w_0=64$ µm, with the same 3 mm EOM aperture truncating
the input beam that the naive (untruncated) estimate misses. That direct
measurement lands at the top of the transit-inferred 45–70 µm band and
independently excludes 32 µm, agreeing with the corrected transit physics on
$w_0\approx50$–64 µm. Nieddu additionally reports the same four two-photon peaks
at 2.43–2.60 MHz FWHM (laser axis, $\approx5$ MHz transition axis) with a
locked laser — consistent with the archival $\approx5.25$ MHz line.

The cusp is a *falsifiable prediction*: at the coldest, dimmest condition
(where transit is the largest fraction of a narrow line) a BIC comparison of a
Voigt against a Lorentzian$\otimes$exponential can detect it — to our
knowledge not cleanly resolved as a *cusp* in a thermal two-photon line (an
October target with a narrow laser). Caveat: $w_0$
is only a prior ($\sim50\ \mu$m — re-centred from 32 µm when the transit physics
was corrected, since the corrected transit excludes 32 µm; the beam was clipped
by a 3 mm aperture, so it is uncertain at the tens-of-% level) **until the
October knife-edge measurement** (below); every *absolute* width built on it is
therefore PRELIMINARY. *Code:* `two_sided_exponential()`; `transit_fwhm_at_T()` enforces
the $\sqrt T$ law.

#### What "the knife-edge $w_0$" means

$w_0$ is the beam waist — the radius at which the intensity falls to $1/e^2$ of
its on-axis value at the focus. A **knife-edge measurement** is the standard,
model-free way to measure it: you translate a sharp opaque edge (literally a
razor blade — hence "knife-edge") across the beam, perpendicular to its
propagation, and record the transmitted power $P(x)$ versus the blade position
$x$. For a Gaussian beam the blade integrates a Gaussian, so $P(x)$ traces an
error function, and its derivative is the beam's intensity profile:

$$\frac{dP}{dx} \propto \exp \Big(-\frac{2x^2}{w^2}\Big)$$

whose width gives the local radius $w$. Repeating at several positions along
the propagation axis $z$ near the focus and finding the minimum locates the
waist $w_0$. It is direct, needs no lineshape model, and is good to $\sim\mu$m.

Why it is the linchpin for this analysis: $w_0$ sets the **transit width**
($\propto 1/w_0$, §2.5) *and* every AC-Stark magnitude ($\propto 1/w_0^2$,
§2.6), and it is **degenerate with $\sigma_\text{laser}$** in the fits (§2.4,
§5) — so as long as $w_0$ is only the clipped-beam prior, the transit/laser
split and all absolute coefficients stay PRELIMINARY. Measuring $w_0$ directly
in October collapses that degeneracy: transit becomes fixed, the leftover
Gaussian is then unambiguously the laser (turning the §5 $\sigma_\text{laser}$
*bound* into a measurement, retroactively for the 2025 data too), and $\beta_\text{self}$
and the Stark coefficient acquire their absolute scale. It is the single
measurement that unlocks the most downstream numbers, so it is task #1 of the
October cell campaign (PLAN §7-adjacent).

### 2.6 AC-Stark shift — derivation of the triangular "ramp law"

Intense light shifts atomic levels (the AC-Stark or light shift) by an amount
proportional to the local intensity $I$; here the shift is toward the **red**
(lower frequency). Different atoms sit at different radii in the beam and so
feel different shifts — what does the *line* show? Two facts set it up:

- **Two-photon excitation rate** $\propto I^2$ (each photon contributes one
  power of $I$).
- **Shift** $s = -\kappa I$ for some constant $\kappa>0$ (red $\Rightarrow$
  minus).

Take a Gaussian beam, $I(r)=I_0e^{-2r^2/w_0^2}$, and let $u\equiv I/I_0\in(0,1]$.
The signal contributed by the annulus between $r$ and $r+dr$ is

$$dS  \propto  I^2(2\pi rdr) \propto  u^2rdr$$

Change variables from $r$ to $u$. From $u=e^{-2r^2/w_0^2}$,

$$\frac{du}{u}=-\frac{4r}{w_0^2}dr  \Longrightarrow   rdr=-\frac{w_0^2}{4}\frac{du}{u}$$

so

$$dS \propto  u^2\cdot\frac{du}{u} = udu$$

The shift at intensity $u$ is $s=-\kappa I_0u \equiv -S_0u$, where
$S_0=\kappa I_0>0$ is the on-axis (maximum) red shift. Substituting
$u=-s/S_0$, the **signal-weighted distribution of shifts** is

$$\boxed{f(s) \propto |s|\quad\text{on}\quad s\in[-S_0,0]}$$

— a triangular **ramp**. (Remarkably, the identical law holds for a nanofibre's
evanescent field, because the intensity is exponential in the flat coordinate
there too — that shared law is the physics bridge to Paper 2.) Normalizing,
$f(s)=2|s|/S_0^2$, we get the moments by direct integration:

$$\langle s\rangle=\int_{-S_0}^{0}  sf(s)ds=-\tfrac{2}{3}S_0,
\qquad
\mathrm{Var}(s)=\tfrac{1}{18}S_0^2,
\qquad
\kappa_3=\langle(s-\langle s\rangle)^3\rangle=+\tfrac{1}{135}S_0^3$$

So the **mean red pull is $\tfrac23 S_0$**, and the distribution is
positively skewed (peak pulled red, thin tail toward the blue). Here
$\kappa_2\equiv\mathrm{Var}$ and $\kappa_3$ are the second and third
*cumulants*; the ramp's own **standardized** skewness — the scale-free shape
number — is $\kappa_3/\kappa_2^{3/2}=18^{3/2}/135\approx0.566$, independent
of $S_0$ (a property of the triangle, not of the power). That fixed number is
the target of the October form test (below); what varies with power is the
*observed line's* asymmetry, which we get by folding the ramp into the rest
of the line.

**Cumulants add under convolution** (the cumulant of a sum of independent
variables is the sum of the cumulants), and the symmetric kernels contribute
nothing asymmetric: the Lorentzian, Gaussian and transit kernels all have
$\kappa_1=\kappa_3=0$. So the ramp's odd cumulants pass through the
convolution untouched — the *whole line's* first-moment pull is
$-\tfrac23 S_0$ and its third cumulant is $\kappa_3^{\text{tot}}=S_0^3/135$,
**exactly**, independent of the (unknown) laser/transit widths. These two
odd cumulants are the clean, apparatus-independent handles, and the mean
pull is the primary October observable (§7).

A literal *standardized* skewness of the full profile is more delicate,
because the homogeneous Lorentzian has divergent second and higher even
moments — $\kappa_2^{\text{tot}}$ is not finite, so one must work at fixed
fit window rather than with whole-line moments. Over the fit window the
symmetric part contributes an effective width $\sigma_\text{eff}$ (a standard
deviation, $\sim 2$MHz, set mostly by the $\sim 5$ MHz total FWHM and
nearly power-independent), against which the asymmetry reads as

$$g_1^{\text{obs}} \sim \frac{\kappa_3^{\text{tot}}}{\sigma_\text{eff}^3}
=\frac{S_0^3/135}{\sigma_\text{eff}^3} \propto S_0^3 \propto P^3$$

since $S_0\propto$ power $P$. (No contradiction with the fixed $0.566$: that
is the standardized skew of the ramp *alone*; here the same $\kappa_3$ is
divided by a much larger, nearly fixed symmetric width.) **Two consequences
for the archival data:** (i) the FWHM moves $\lesssim2\%$ across our power
sweep, so the old "power null" is a *prediction confirmed*, not a null
result; (ii) the observed asymmetry $\propto P^3$ is $\sim10^{-4}$ against a
$\sim10^{-3}$ noise floor — unmeasurable — so all AC-Stark *coefficients*
move to October (where the shift itself, $\propto P$, is measured directly
against a stable lock). *Code:* `stark_ramp()` — built from exact per-cell
integrals so the area is exactly 1 and the mean exactly $-\tfrac23 S_0$ even
for shifts far below the grid step.

#### The general law: the signal exponent sets the ramp shape

Nothing in the change of variables above used $n=2$ except the weight
$u^n$. For a signal $\propto I^n$ the same steps give

$$dS  \propto  u^n\frac{du}{u}  =  u^{n-1}du
\qquad\Longrightarrow\qquad
f(s) \propto |s|^{n-1}\ \ \text{on}\ [-S_0,0]$$

For a **one-photon** transition ($n=1$ — e.g. the Stark-induced forbidden
lines of the parity-violation literature) the distribution is **uniform**:
mean $-S_0/2$ and, being symmetric about its mean, $\kappa_3=0$ — **zero
skew**. The skewness observable exists at all *only because the two-photon
signal goes as $I^2$*. This one line is the delineation from the nearest
prior art (Stalnaker *et al.*, PRA **73**, 043416 (2006), who extracted an
AC-Stark parameter from asymmetric standing-wave lineshapes numerically, in
the $n=1$, fringe-resolved regime — full delineation in
`docs/LITERATURE.md`).

#### The parameter-free moment hierarchy (the October form test)

Dividing out $S_0$, the ramp component predicts *pure numbers*:

$$\frac{\mathrm{Var}(s)}{\langle s\rangle^2}=\frac{1/18}{4/9}=\frac18,
\qquad
g_1\equiv\frac{\kappa_3}{\mathrm{Var}(s)^{3/2}}
=\frac{1/135}{(1/18)^{3/2}}=\frac{18^{3/2}}{135}\approx+0.566$$

October tests them in order of statistical cost: (1) **mean pull vs
$P$** — the first cumulant, exact and apparatus-independent (§above), first
order in $S_0$, and the fixed lock makes centers usable; (2) **excess
variance vs $P^2$** — the symmetric second-moment growth
$\mathrm{Var}\propto S_0^2$ (exactly what the Cs 6S–8S literature reported as
a growing Gaussian width); (3) **skewness** — smallest signal, the only
moment that is
*zero unless* $n=2$. The pure numbers above are the ramp *alone*; in the
measured line each is diluted by the symmetric kernels (and read at fixed fit
window, per the divergence caveat above), so the hierarchy is fitted jointly,
not read off one trace.

#### Diverging-beam collection: the closed form and the sign flip

The triangle assumed a beam of constant waist across the detection region.
Really the fluorescence lens collects from an axial window $|z|\le Z_c$
around the focus while the beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$ with
$\zeta=z/z_R$, $z_R=\pi w_0^2/\lambda$. At each $\zeta$ the transverse law
holds with a *local* maximum shift $S(\zeta)=S_0/(1+\zeta^2)$, and the per-slice
signal weight is $\propto w^2 I_0^{n}\propto(1+\zeta^2)^{1-n}$ — which
exactly cancels the local normalization $S(\zeta)^{-n}$ up to one factor
$(1+\zeta^2)$. The $z$-integral then closes for any $n$:

$$f(s) \propto |s|^{n-1}\left[\zeta_m+\frac{\zeta_m^3}{3}\right],
\qquad
\zeta_m(s)=\min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

$Z_c/z_R\to0$ recovers the triangle; the hard edge at $-S_0$ softens to zero
(only the focal plane reaches the full shift). Numerically (uniform window,
$Z_c=2$ mm placeholder — OPEN until the October collection-profile
measurement):

| config | $Z_c/z_R$ | mean$/S_0$ | Var/mean$^2$ | $g_1$ |
|---|---|---|---|---|
| pure triangle | 0 | $-0.667$ | 0.125 | $+0.566$ |
| 60 µm (October L) | 0.18 | $-0.660$ | 0.125 | $+0.564$ |
| 50 µm (2025 archival) | 0.25 | $-0.653$ | 0.125 | $+0.558$ |
| 16 µm (October S) | 2.47 | $-0.431$ | 0.333 | $-0.354$ |

**The skewness flips sign** (crossover near $Z_c/z_R\approx1.2$): a long
window piles signal into weak out-of-focus shifts, leaving a tail toward
$-S_0$. So the October skew program is a **sign-flip test between beam
configurations** — $g_1>0$ at the large waist, $g_1<0$ at the small one —
a signature no instrumental asymmetry can mimic, because the instrument
knows nothing about $z_R$. At the re-centred 50 µm archival waist the
coefficients above carry only a few-% geometry caveat (its longer $z_R$ makes
the ramp nearly the pure-triangle $Z_c\to0$ limit, $g_1\approx+0.56$; it was
10–40% at the old 32 µm nominal). *Code:*
`stark_ramp_axial()`, table from `scripts/run_ramp_geometry.py`.

#### Standing-wave fringes: why the shift follows the envelope

The retro-reflected beam makes $\lambda/2$ intensity fringes — does an atom
feel the fringe *peak* intensity (a coherent $\times2$) or the average? The
frequency-modulation criterion (Stalnaker *et al.*, Sec. IV): as an atom
crosses fringes its AC-Stark shift is modulated with peak deviation
$\xi=S_0\lesssim1$ MHz at modulation frequency
$f_\text{mod}=2v/\lambda\approx0.56$ GHz (axial thermal speed $\sim280$ m/s,
fringe spacing $\lambda/2$). The FM modulation index is
$\xi/f_\text{mod}\sim2\times10^{-3}$:
deep in the narrow-band regime, so the shift response is a pure carrier and
the sidebands are negligible — the atom responds to the **time-averaged**
intensity. The shift is thus $\propto(1+\rho)I_{\text{fwd}}$ with $\rho$ the
retro power ratio, with **no coherent fringe enhancement**. (Atoms with axial
speed $\lesssim5$ m/s — 1–2% of the signal — are fringe-resolved; a
percent-level correction.) The remaining OPEN quantity in $S_0$ is the
measured $\rho$ per beam configuration (October, in situ at the cell).

#### The coefficient (field-intensity convention, pinned)

The ramp *shape* and its centred moments are convention-free, but the
*magnitude* of $S_0$ — which converts a measured centroid pull into the
differential polarizability $\Delta\alpha=\alpha_{6S}-\alpha_{5S}$ — needs the
$\langle E^2\rangle$ convention fixed. We adopt the standard AMO one (Grimm
*et al.* 2000; Steck): for $E(t)=E_0\cos\omega t$, $\langle E^2\rangle=E_0^2/2$,
so $\Delta E_i=-\tfrac14\alpha_i E_0^2=-\alpha_i I/(2\varepsilon_0 c)$ and

$$S_0=\frac{\Delta\alpha\ I_\text{eff}}{2\varepsilon_0 c h},\qquad
I_\text{eff}=(1+\rho)\frac{2P}{\pi w_0^2}$$

With $\Delta\alpha=1093$ a.u. this is $S_0=0.59$ MHz (transition) at 225 mW,
$w_0=50\ \mu$m (the archival prior; it was 1.43 at the old 32 µm nominal),
$\rho=1$, growing to 5.7 MHz at $w_0=16\ \mu$m (why October's
small waist makes the $\propto S_0^3$ skew measurable). The **sign** is
convention-independent — set by $\text{sign}(\Delta\alpha)$, here red
($\Delta\alpha>0$). *Code:* `lineshape.stark_shift_S0_mhz()`. The full
theorist-facing derivation, novelty position, and the open diverging-beam
question are in [`docs/THEORY_NOTE.md`](docs/THEORY_NOTE.md).

### 2.7 Radiation trapping — why it moves amplitudes, not the lineshape

At high density the cell becomes optically thick to the 795 nm detection
photons: a photon emitted deep inside can be **reabsorbed by a ground-state
atom** and re-emitted, possibly many times, before escaping. The optical depth
governing this is

$$\tau_\text{opt}=n_g\sigma_{795}L$$

with $n_g$ the ground-state density, $\sigma_{795}$ the absorption cross
section, $L$ the path. The decisive point: $n_g$ is the enormous *thermal*
ground-state population, essentially the full density $N$, which the weak
two-photon excitation barely perturbs — and it is the **same at every point of
the 993 nm frequency scan**. So the photon escape probability
$\epsilon(\tau_\text{opt})$ is a constant multiplier across the scan: trapping
**rescales the amplitude** (and can alter photon-counting *statistics*) but
does **not** distort the two-photon lineshape. Onset is at
$\tau_\text{opt}\sim1$, i.e. $N\sim1/(\sigma_{795}L)\sim10^{12}$–$10^{13}$
cm$^{-3}$, straddled by our T-sweep. We tested the statistics route: the
shot-noise coefficient $b$ in the noise law (§4.4) is **flat in temperature**
(no growth of the Fano factor 70→130 °C), so trapping, if it shows anywhere,
shows in *amplitude ratios* versus density (module M7, against Nieddu's 2019
same-channel baseline), never in the width. *Code:* the $b(T)$ table from
`noise.py`; the M7 finding is below.

There is one further subtlety that connects trapping to the **degeneracy law**
(§ amplitude ratios, module M10). Trapping is scan-constant *for a given peak*,
but it is **not** the same *across* peaks: the emitted 795 nm photon's frequency
is set by which $5P_{1/2}F'$ and $5SF''$ the cascade uses, so different
hyperfine paths and the two isotopes overlap the ground-state D1 absorption
differently. Crucially, $^{85}$Rb carries $\sim 2.6\times$ the ground-state
D1 absorbers of $^{87}$Rb (its 72 % abundance), so at equal density it is
trapped harder. Differential trapping is therefore a candidate mechanism for
breaking the pure population ratios (5/3, 7/5, 2.42) — and, unlike the
between-block drift, it is **monotonic in density and isotope-ordered**, which
is exactly the discriminator M7 now runs.

### 2.8 The composite model in code

`model_profile()` assembles §2.1–2.6 on a common fine grid (homogeneous
Lorentzians combined analytically, the rest convolved numerically), returns an
area-normalized profile, and `fit_condition()` fits it to data with the
per-trace nuisances of §4.2. It uses the pure triangular ramp
(`stark_ramp()`); the archival fits keep it because $S_0$ is fixed per power
and the geometry correction sits far below the 2025 noise. October
center-fits swap in `stark_ramp_axial()` (the diverging-beam kernel of §2.6)
once the collection profile is measured. The no-Stark composite shared by the
$\beta_\text{self}$ and global fits is `composite_profile()` in the same
module.

---

## 3. From volts-versus-time to a frequency axis (the EOM ruler)

The scope records fluorescence versus *time* while the laser sweeps; we need
$\nu$ versus time. The sweep is nonlinear and its rate unknown, so a ruler was
built into the scan: an EOM phase-modulates the light at exactly
$\Omega=12.5$ MHz, adding sidebands at $\nu_c\pm n\Omega$ around the carrier
$\nu_c$. Two-photon absorption picks any *pair* of sidebands whose frequencies
sum to the transition $\nu_0$:

$$(\nu_c+m\Omega)+(\nu_c+m'\Omega)=\nu_0
  \Longrightarrow
2\nu_c+(m+m')\Omega=\nu_0$$

Writing $k=m+m'$, resonances occur at carrier frequencies
$\nu_c=(\nu_0-k\Omega)/2$, i.e. a comb of line-copies spaced by

$$\boxed{ \Delta\nu_\text{tooth}=\frac{\Omega}{2}=6.25\ \text{MHz (laser axis)} }$$

— the same factor-2 as §0. Fitting the tooth spacing (in ms) per block gives
the sweep rate; we measure $0.04257(5)$ MHz/ms on the laser axis, and the
sweep is linear across the window to $<0.4\%$. A half-wave-plate trick mixes in
amplitude modulation on the ruler traces to suppress the carrier so the
sidebands stand tall — so the tooth *spacing* is exact, but tooth *heights*
carry no information about the modulation depth. *Code:* `ruler.py` (M2);
$\Omega/2$ locked by a permanent test in `test_constants.py`.

---

## 4. The statistics, from first principles

### 4.1 Weighted least squares with *measured* weights

A fit minimizes $\chi^2=\sum_i \big(d_i-m_i\big)^2/\sigma_i^2$. The correct
$\sigma_i$ is the real per-sample noise, which here is *not* constant: PMT shot
noise grows with signal. We measured (module M1, §4.4)

$$\sigma^2(V)=a^2+bV$$

per condition and use it as the weights. Unweighted fitting would let the
bright peak dominate and would misstate every error bar; using the measured
$\sigma(V)$ is what makes the reported uncertainties meaningful.

### 4.2 Hierarchical fitting — share what physics shares, free what drifts

Each condition has five back-to-back repeats of the *same* physical line, but
the drifting 2025 laser moves the line center and the PMT gain wanders. So we
fit the repeats **jointly**, sharing the physics and freeing the nuisances:

- **shared** across repeats: the lineshape parameters $\gamma_\text{coll}$,
  $\sigma_\text{laser}$ (and optionally transit);
- **per-trace**: amplitude $A_i$, center $\nu_i$, and a tilted baseline
  $b_{0,i}+b_{1,i}\nu$.

This is what makes drifted 2025 data usable: the drift lives in the per-trace
centers, the physics in the shared shape. The same idea extends across
temperatures — `fit_beta_self()` ties $\gamma_\text{coll}(T)=\beta_\text{self}N(T)$
with a single shared $\beta_\text{self}$, turning four widths into one slope.

**The full hierarchy** (`fit_global()`, module M4b) fits *all* peaks and
temperatures at once, sharing each parameter at the level the physics licenses
— and the choice of level is where the physics really enters:

- $\sigma_\text{laser}$ is shared **per temperature, across the four peaks**.
  The four lines are measured within one temperature dwell, so they see the
  *same* laser at that moment and jointly over-constrain $\sigma_\text{laser}(T)$
  — which lets its drift across the cooling session be *measured* rather than
  mistaken for collisions. (Sharing one *global* $\sigma_\text{laser}$ across
  all temperatures — as a naive fit does — is exactly what manufactures a false
  detection; see §4.5. For October's stable lock, global sharing becomes
  correct.)
- $\beta_\text{self}$ is shared **per isotope**, not globally: collision
  cross-sections need not be equal for $^{85}$Rb and $^{87}$Rb, so we *test*
  $\beta_{85}$ vs $\beta_{87}$ rather than assume them equal.
- the transit width is shared globally (same beam, same $\sqrt T$ law);
  amplitude, center, baseline stay per-trace.

This breaks the Voigt degeneracy (§4.3) two ways at once — the density lever
arm *and* the four peaks pinning one $\sigma_\text{laser}(T)$ — and comes with
a leave-one-condition-out check that no single block drives a shared
parameter. *Code:* `fit_condition()`, `fit_beta_self()`, `fit_global()`.

**The lever cross-check** (`lever_crosscheck_beta()`, module M4d) is the packaged form of
this hierarchy — the value and the *full error budget* the paper quotes. Its
headline is the **internally-consistent 70/90/110 °C cooling sweep** (one
session, monotonic cooling), fit across a model-form grid — transit cusp
(Lehmann) vs no-cusp (Voigt) $\times$ $\sigma_\text{laser}$ shared-per-$T$
(Model A) vs per-block (Model B). The spread of $\beta$ across those cells *is*
the model-form error bar; with the $w_0$-band and a leave-one-**peak** /
leave-one-**temperature** robustness scan it returns **one $\beta$ per isotope
carrying three separately-sourced error bars** (statistical, model-form,
confound/$w_0$). A synthetic-injection closure test (`tests/test_lever_crosscheck`)
recovers a known $\beta$ through the whole 20-trace machinery, so the pipeline
itself is validated, not just trusted.

The archive's curated 130 °C anchor (the `serves_t130` traces, 225 mW) would
triple the density lever ($N{\times}16\to{\times}53$), and the lever cross-check
uses it as a **lever test**: adding it pulls the joint $\beta$ far below the
cooling-sweep value. The lesson is not "bad block" — it is that
$\gamma_\text{coll}$ **barely grows with density**: it rises only ${\sim}1.5\times$
across a ${\times}52$ density span (70→130 °C), and the 130 °C widths sit *on*
that near-flat trend, whereas a real binary-collision width is *linear* in $N$.
So the fitted $\gamma_\text{coll}$ is a residual floor, not resolved collisions,
and $\beta$ is a **lever-dependent bound**, not a value — exactly why the
model-independent bound is the headline. (The 130 °C data are also a different
session, a secondary caveat we cannot fully separate; either way October needs
*same-session* high-density points to resolve any real slope.)
*Run:* `run_lever_crosscheck.py` → `results/lever_crosscheck.csv`; numbers in the
results ledger (`docs/RESULTS.md`).

### 4.3 The degeneracy and honest covariances

Because of the Voigt near-degeneracy (§2.4), a single-condition fit returns
$\sigma_\text{laser}$ and $\gamma_\text{coll}$ with correlation
$\approx-0.85$: individually shaky, sum robust. We therefore (i) always report
the full covariance, and (ii) design $\beta_\text{self}$ to ride on the
$\gamma_\text{coll}$ **difference** across densities, where the shared laser
contribution cancels. Reported errors are additionally inflated by
$\sqrt{\chi^2_\text{red}}$ (model imperfection) and $\sqrt{\tau_\text{int}}$
(wing-noise correlation, §4.4) — conservative by policy. Covariances are
obtained from a singular-value decomposition of the Jacobian rather than
$(J^{\mathsf T}J)^{-1}$, to stay numerically safe when parameters span very
different scales. *Code:* `fitutil.cov_from_jac()`.

### 4.4 The noise model and the second-difference estimator

To measure $\sigma(V)$ without contamination from the signal's slope, we use
**second differences**,

$$e_i=\frac{v_{i+1}-2v_i+v_{i-1}}{\sqrt{6}}$$

which annihilate any locally-linear trend exactly (so a bright line's steep
flank contributes nothing) while having unit response to white noise — for
white noise of standard deviation $\sigma$, $e_i$ also has standard deviation
$\sigma$. Binning $e_i$ by local signal level and fitting the variance law
$\sigma^2=a^2+bV$ then gives $a$ (electronics/dark floor) and $b$ (the
shot-noise, "Fano", term). Wing-noise **correlation** is measured separately
by the blocking method and summarized as an integrated correlation time
$\tau_\text{int}$, which inflates the fit errors as above. We found $b$ flat in
$T$ (the trapping test of §2.7) and $\tau_\text{int}$ small. *Code:*
`noise.py`.

### 4.5 Statistics versus systematics — the measurement-vs-bound rule

A large shared fit can return a beautifully small formal error that is
nonetheless *wrong*. If you share $\sigma_\text{laser}$ across blocks recorded
hours apart and the laser width actually drifted between them, the fit will
absorb that drift into $\gamma_\text{coll}$ and report a confident collisional
signal that is really instrument drift. Our guard is **pre-registered** and
model-independent:

1. Collisional broadening *must* be monotonic in density. So take **raw**
   line widths (smoothed half-max $\times$ the ruler rate, no fitting) and
   check monotonicity in $N$.
2. Fit $W(N)=W_0+\beta_\text{eff}N$; the RMS scatter of the blocks about this
   line is treated as a **between-block systematic** and added in quadrature
   to each point's error.
3. Claim a **measurement** only if $|\beta_\text{eff}|/\sigma_\text{syst}\ge3$;
   otherwise report a **bound**.

Deciding this rule *before* looking is what separates the honest answer from
the overconfident one (see §5). *Code:* `beta.collisional_slope()`,
`scripts/run_beta_self.py`.

### 4.6 Validation on synthetic data before real data

No fitter is allowed near real data until it recovers *known* injected truths
from campaign-like synthetics — checking bias, error coverage, and the
degeneracy — across 113 tests. Then every headline conclusion is re-derived by
an **independent method** (e.g. the sweep rate by FFT and autocorrelation; the
noise law by differencing sibling repeats). Several of our own bugs were caught
exactly this way; the verification records live in the module docstrings.

### 4.7 Choosing between competing lineshapes — the BIC

To ask *which* model form the data prefer — a smooth Gaussian extra-broadening
(a Voigt) versus the cusped transit exponential (the Lehmann shape, §2.5) — we
compare the **Bayesian information criterion**

$$\text{BIC}=\chi^2+k\ln N$$

with $k$ the number of free parameters and $N$ the data points. The $\chi^2$
rewards fit quality; the $k\ln N$ term penalizes complexity, so BIC asks "is
the better fit worth its extra parameters?". Lower BIC wins; on the
Kass–Raftery scale $|\Delta\text{BIC}|<2$ is "indistinguishable" and $>10$ is
"decisive". Voigt and Lehmann have the *same* $k$, so their comparison is
essentially which shape fits better. This is the tool for the Lehmann-cusp
test (module M8; §5). *Code:* `modelform.py`.

### 4.8 Restricting the fit window — the off-center-sweep mirror

The laser is swept by a triangular voltage ramp. When that ramp is not
centered on the transition, its *down-ramp* re-crosses the line and leaves a
**mirror image** of the peak elsewhere in the acquisition window (~40 MHz away
on the transition axis). A single-line fit over the full window would treat
that mirror as unmodelled signal and let it bias the baseline and width. So the
line fits are restricted to a window around each trace's peak, wide enough to
keep the fat Lorentzian wings (where $\gamma_\text{coll}$ lives — cutting too
tight would bias it) but tight enough to exclude the mirror: $\pm3.5\times$ the
trace's own measured FWHM, clipped to $[9,25]$ MHz. The rulers need no such cut
— a symmetric-triangle fold preserves the tooth *spacing*, so the ruler rate is
intrinsically fold-robust (only a single line, which literally appears twice,
is at risk). *Code:* `linefit.adaptive_halfwidth()`.

---

## 5. What we found (2025 archival data)

**Headline: the T-sweep *bounds* $\beta_\text{self}$ and shows why it cannot
measure it.** The raw, model-independent widths are **non-monotonic in
density** for three of four peaks (e.g. 993.4207 nm: 5.11 → 4.92 → 5.35 MHz for
70 → 90 → 110 °C — *narrower* at higher density, which no collision can
produce). Within-block repeat scatter is $\sim0.05$ MHz, but between-block
scatter is $\sim0.06$–$0.16$ MHz: the 2025 laser width drifted between cooling
steps by about as much as the entire collisional trend. Applying §4.5,

$$\boxed{ \beta_\text{self}\lesssim 0.07\text{–}0.15\ \text{MHz per }10^{12}\ \text{cm}^{-3}\ (\approx2\sigma,\ \text{per peak}). }$$

The between-block systematic here is an RMS over only 1–2 residual degrees of
freedom (3–4 density points), so each bound carries a **$\sim$factor-2
own-uncertainty** and the "$\approx2\sigma$" coverage is approximate — hence
the two-figure quote and the range, not a crisp number. (The scatter estimate
divides by the DOF, not by $n$; using $n$ would tighten the bound $\sim$40% —
a directional bug fixed 2026-07-12.) A naive global Voigt fit instead reports a
4–10$\sigma$ "detection" — the §4.5 cautionary tale made flesh. This bound is
the archival data *proving the two-epoch design was necessary*, and is itself a
Paper-1 result.

**A hierarchical cross-check ($\beta$ per isotope).** The full fit (§4.2,
`fit_global`) — which properly lets $\sigma_\text{laser}$ drift per temperature
and weights each block by its own correlation time — returns
$\beta_{85}=\beta_{87}=0.036(4)$ MHz per $10^{12}$ cm$^{-3}$: **no isotope
dependence** ($\beta_{85}-\beta_{87}=0.000\pm0.006$, $0.0\sigma$), robust to
leaving any block out. It is a *model-based* value: it sits above the per-peak model fits
($0.027$–$0.047$) but comfortably **below all four** model-independent per-peak
bounds ($0.07$–$0.15$, once those are computed with the correct
degrees-of-freedom denominator) — so it is consistent with the bound, not in
tension with it, though it still inherits the same $w_0$ and model-form limits.
Those limits are **not** hand-waved: this $0.036$ carries **three separate error
bars**, and the two systematics dominate the statistical one — statistical
$\pm0.004$ (joint-fit covariance); **transit model-form $\pm0.012$** (the
$|\text{Voigt}-\text{Lehmann}|$ shift, §4.7, `run_global_fit`: the Gaussian-transit
Voigt gives the *higher* $\beta\approx0.068$ because a narrower transit core forces
more width onto collisions); and — **largest of the three** — the $w_0$-band
$[0.025,0.065]$ (a factor ${\sim}2.5$, since every absolute $\beta$ rides on the
OPEN beam waist). The paper must quote all three, not the optimistic $\pm0.004$ alone.
So the conservative model-independent bound, not this value, stays the headline.
Its real value is the isotope test, and the validation (M4c, §sharing test) that
the four peaks at each temperature agree on a single $\sigma_\text{laser}$
(χ²/dof < 1) — so the per-temperature sharing is licensed. The fit's
$\sigma_\text{laser}(T)\approx2.1/2.2/1.6$ MHz is **not** a clean drift curve,
though: the free per-condition fit gives a *flat* $\sim$1.7 MHz, so that trend
is the $\beta \leftrightarrow \sigma_\text{laser}$ degeneracy under the density
tie, not a physical laser drift — the 110 °C dip is a model artifact, not a
stale block (and it does not corrupt $\beta$, which the density lever still
pins).

The **lever cross-check** (M4d, `run_lever_crosscheck`) packages exactly this — the
cooling-sweep $\beta$ with all three error bars and a leave-one-peak /
leave-one-temperature scan — and adds the honest lever test: folding in the
130 °C anchor (§4.2) pulls $\beta$ well below $0.036$, because $\gamma_\text{coll}$
rises only ${\sim}1.5\times$ across a ${\times}52$ density span — a residual floor,
not resolved collisions — so $\beta$ is a lever-dependent bound. The full audited
budget is in the results ledger (`docs/RESULTS.md`).

**The 2025 laser width (deliverable C2) — an upper bound.**
$\sigma_\text{laser}(2025)\lesssim2.0$ MHz (transition axis; $\lesssim1.0$ MHz
laser axis; it is $\sim0.84$ MHz laser-axis at the $w_0=50\ \mu$m prior) —
a bound, not a measurement, because that non-Lorentzian Gaussian
is degenerate with the transit width, and the transit Monte-Carlo (§2.5, M9)
now makes the degeneracy quantitative: the corrected transit adds $\sim2.1$ MHz
at $w_0=32\ \mu$m (which OVERSHOOTS the observed line, excluding 32 µm) but only
$\sim1.2$ MHz at the $50\ \mu$m prior, so below $w_0\approx38\ \mu$m transit
alone fills the observed 5.25 MHz and **the laser is narrow**, while at the
50 µm prior the laser carries $\sim0.8$ MHz laser-axis. The
archival data cannot locate that crossover; only the October knife-edge $w_0$
can. (Slow drift is *not* the culprit — only $\sim0.01$ MHz within a scan.) The
knife-edge $w_0$ (fixing transit) turns this bound into a measurement; meanwhile it is the
ONF starting linewidth for Paper 2.

**The power sweep, recast as confirmed predictions (deliverable C3).** At fixed
130 °C only the AC-Stark $S_0$ varies, so the ramp law (§2.6) predicts, and the
data confirm: (C3a) the linewidth is **flat** — no monotonic power broadening,
with 3–8% block scatter that is the same between-block wander seen elsewhere;
(C3b) the amplitude is **consistent with $P^2$** (log-log slopes 1.83–2.12,
clustered on the two-photon rate law; 993.4121 nm sits below at 1.83). We say
*consistent with*, not *confirms*: at the thick-cell end ($\tau/$cm up to 160)
a slope below 2 could be genuine saturation OR a weak power-dependence of the
trapping collection efficiency through the saturating emitter profile, and the
single-temperature archival sweep cannot separate the two — the 4121 low slope
is the visible symptom of that degeneracy, resolvable only by October's
multi-$T$ sweeps;
(C3c) the **ramp** skew (growing as $P^3$) is below detection, a bound — but the
committed residual skew is emphatically *not* zero: it is large and positive at
low power (up to $\sim$10$\sigma$ at 25 mW, e.g. 993.4154 nm $0.345\pm0.036$)
and *falls* with amplitude as $\sim$amp$^{-0.5}$. That is the Poisson
**shot-noise skewness** (the noise is right-skewed $\propto1/\sqrt{\text{counts}}$,
vanishing as the line brightens) — a statistical artifact with the *opposite*
sign and power dependence to the ramp, not a physical asymmetry. So the ramp is
the genuine null; the significant low-power skew is identified, not unexplained.
The old "power null" is thus a suite of confirmed predictions — with the
residual skew correctly attributed to shot noise, not laundered into "zero."

**Radiation trapping — thick cell, near-linear signal, drift-dominated ratios
(module M7).** Peak amplitude scales roughly *linearly* with density: log-log
slopes $0.94(13)$, $0.91(5)$, $0.85(15)$, $1.02(8)$ across $\times52$ in $N$ —
all consistent with slope 1 within $\sim1$–$2\sigma$, so any
trapping/993-absorption rollover is weak and not resolved, consistent with
M1's flat-$T$ shot-noise coefficient. This is at first sight *surprising*: the
D1 optical depth (§2.7) is $\tau/\text{cm}\approx1$–$60$ ($^{87}$Rb) and
$3$–$160$ ($^{85}$Rb) across the sweep, so over the few-cm path the cell is
optically **thick** and naive trapping should bite hard. The resolution is a
real physical statement about the geometry: a thick cell without quenching
still emits nearly one collected 795 nm photon per excitation — trapping
*redistributes* the photons (a random walk to the walls) rather than destroying
them, and the wide $f18$ mm collection captures the diffuse re-emission — so the
collected signal stays $\propto N$. The near-linearity thus **bounds
non-radiative quenching to be weak** over the trapping random-walk.

Trapping's degeneracy-breaking (peak-differential) effect (§2.7) is then sought
three ways, all model-independent. (i) The isotope-averaged slope difference is
the cleanest fingerprint: $^{87}$Rb $\langle s\rangle=1.00(7)$ vs $^{85}$Rb
$\langle s\rangle=0.91(5)$, i.e. $^{85}$Rb is $0.09(8)$ *more* sublinear — the
sign trapping predicts ($^{85}$Rb has $2.6\times$ the absorbers), but only
$\sim1\sigma$: a hint, not a detection. (ii) The peak-*height* ratios are
**non-monotonic** in density (e.g. 993.4207/993.4121 nm runs
$1.09\to1.01\to2.48\to1.94$), whereas trapping would bend them *monotonically* —
so the 30–50% degeneracy-law disagreement (module M10, on the *areas*) is
between-block **drift**, not trapping. (iii) A one-parameter trapping model does not improve
the fit over pure $\propto N$ (both $\chi^2_\text{red}\gg1$, dominated by the
drift scatter). *Verdict:* trapping is physically present and expected-large by
$\tau$, but its net effect on the collected amplitude is modest and its
degeneracy-breaking effect is $\lesssim10\%$, buried under drift; separating it
needs October's fixed-lock interleaved-peak run with a controlled collection
geometry. A clean separation of the trapping/993-absorption losses and an
absolute trapping fraction additionally want Nieddu's 2019 same-channel
baseline (not loaded here).

**The Lehmann cusp — not resolvable in 2025, as designed (module M8).** At the
cold-dim 70 °C corner the BIC comparison (§4.7) gives
$\Delta\text{BIC}(\text{Voigt}-\text{Lehmann})=+0.4/+0.9/+3.6/-0.1$ across
peaks — a **statistical null**: three of four are $|\Delta\text{BIC}|<2$
(the "not worth a mention" band) and the fourth is 3.6 (weak, and it is the
same peak, 993.4192 nm, whose fits are noisiest elsewhere), against a claim gate of
$\Delta\text{BIC}\gtrsim10$. The honest statement is that **the archival data
cannot distinguish a cusped (Lehmann) from a smooth (Voigt) extra-broadening**
— exactly as the two-epoch design anticipated, since the $\sim2$ MHz bad-lock
laser Gaussian smears the cusp and the transit/laser split is itself
unresolved (§2.5). No lean is claimed. The decisive cusp test is October's
narrow-laser data, for which this module (closure-tested to prefer the right
form when a cusp *is* present) is validated infrastructure.

**Area ratios vs the degeneracy law (module M10) — a parameter-free
prediction the archive cannot yet test.** For two *identical* photons the
$S\to S$ two-photon operator is purely **scalar** (rank 2 cannot connect
$J=\tfrac12\to\tfrac12$), so every $F,m_F$ has the same per-atom rate and the
line *areas* (not heights — heights confound with width) must be pure initial
population: $S\propto\text{abundance}\times(2F{+}1)$, i.e. within-isotope
ratios of exactly $5/3$ ($^{87}$Rb) and $7/5$ ($^{85}$Rb). Measured: the
within-block statistics are superb ($1$–$3\%$), but the area ratios swing
30–50% *between* temperatures, non-monotonically (the 993.4207/993.4121 nm
*area* ratio runs $1.10\to0.98\to2.53\to1.97$ against a constant $5/3$; the
slightly different height ratios in the trapping paragraph above tell the
same drift story) — that is between-block power/alignment drift, not physics
(real differential trapping would be smooth in density).
Two consequences: cross-peak amplitude comparisons in this archive carry
$\sim$30–50% systematics (per-peak, within-block analyses like M7 are
unaffected), and the clean degeneracy-law test is an October task — measure
the four peaks **interleaved**, with power logging.

**Foundational results underpinning all of the above.** The sweep rate is
$0.04257(5)$ MHz/ms (laser axis) — $\times11$ slower than the pre-analysis
seed, confirmed by three independent methods, sweep linear to $<0.4\%$ within a
block. The 20 blocks over-disperse ($\chi^2_\text{red}=6.8$) — block-level
ruler scatter (bracket-to-bracket drift, a likely 993.4207-nm-*after* outlier),
**not** a peak-ordered trend (bracket-resolved rates are non-monotonic) — and
the quoted error is already $\sqrt{\chi^2_\text{red}}$-inflated ($\approx$2.6×)
to absorb it, so it is a symmetric common-axis uncertainty, not a cross-peak
bias; the fits use each condition's own block rate. Total
line widths are 4.8–5.5 MHz, sitting exactly on the §2 budget; and the dataset
is decoded and frozen (722 files → **297 unique traces**, every anomaly —
double-saves, renames, discards, off-center-sweep mirrors — explained and
either quarantined or handled).

---

## 6. Load-bearing assumptions (the ones to challenge)

1. Comb teeth spaced $\Omega/2$, not $\Omega$ (everything scales $\times2$ if
   wrong; locked by tests + the 5-tooth amplitude pattern + a hyperfine
   label-spacing check).
2. Scope triggered on the sweep sync so file-time $=$ ramp-phase (evidence
   strong; experimenter confirmation pending — `A1` in PLAN).
3. Kernel *shapes*: laser Gaussian, transit two-sided exponential (the Voigt
   split depends on them). The model-form study (§4.7, M8) confirms the 2025
   data cannot distinguish these forms — so the *shape* assumption is untested
   by the archival data and is a genuine attack surface until October.
4. Transit width rides on the OPEN $w_0$ prior until the October knife-edge.
5. The non-monotonicity is laser drift, not a temperature-correlated *rate*
   artifact (block rates scatter only $0.6\%\approx0.03$ MHz on a 5 MHz line).
6. $N(T)$ correlation + a possible cell cold spot affect only *absolute*
   scales, not the *shape* of $N(T)$.
7. Discards and quarantine are curation-time (pre-analysis) decisions, audited
   symmetrically, so they cannot bias the fits.

---

## 7. Where this can go next

*Archival: done conditional on $w_0$.* Every archival module (M0–M8) is built,
tested, and reported in §5 — collisional bound + isotope test, laser-epoch
bound, power/ramp-law predictions, trapping, and the cusp model-form study.
What is left is not more archival analysis but the measurements the 2025 data
physically cannot yield — first among them the $w_0$ knife-edge on which every
absolute scale above rests.

*October 2026 (fixed lock) — the measurements that lift the bounds* (full
time-budgeted design: **PLAN §8**). Power is capped at
225 mW, so the intensity axis comes from the **beam waist instead**
($I\propto P/w_0^2$; a telescope unclips the EOM aperture and two working
waists, 60 µm and 16 µm, span a $\times16$ intensity range at fixed power).
Headline shots: the AC-Stark shift coefficient with the intensity axis
anchored by the *differential transit width* (knife-edge-independent); the
ramp-law **moment hierarchy** (§2.6) including the predicted **skewness sign
flip** between the two waists; $\beta_\text{self}$ measured — not bounded —
which the collision-rate literature says requires the **150–170 °C**
extension (expected $\beta\sim1$ kHz per $10^{12}$cm$^{-3}$, see
`docs/LITERATURE.md`); the Lehmann cusp in the cold-dim small-waist corner;
the knife-edge $w_0$ itself. Wavemeter calibration is folded in as a
byproduct (PLAN §7): the atoms ($\sim$ kHz) calibrate the wavemeter
($\sim$ 10 MHz), not the reverse.

*Paper 2 (nanofibre / ONF):* the same ramp law tested at the fibre; a
trajectory Monte-Carlo of the published pushing dip; the pulse-duration kill
test.

---

## 8. Conventions, repository map, reproduction

**Conventions (non-negotiable):** transition-frequency axis everywhere (laser
$=\tfrac12$, `_LASER` suffix) · a provenance tag on every number
(`ESTABLISHED` / `MEASURED-HERE` / `CALCULATED` / `ENVELOPE` / `OPEN` /
`DESCOPED`) · validation on synthetic data before real data · independent cross-checks of headline results ·
physics constants vs analysis choices split across `constants.py` / `config.py`
· count repeats from `MANIFEST.csv`, never filenames · quarantine and outlier
rejection pre-registered and QC-based, never result-based.

```
rb5s6s/   constants config ingest(M0) qc(M0) noise(M1) ruler(M2)
          lineshape(M3) linefit(M3) density(M4) beta(M4) global_fit(M4b)
          lever_crosscheck(M4d) stark(M4e) modelform(M8) transit_mc(M9)
          amplitudes(M10) fitutil _compat
scripts/  import_data (+ annotate_manifest_qc: qc_reason provenance)
          → run_qc → run_noise → run_ruler → run_linefit
          → run_beta_self(C1) · run_global_fit(M4b) · run_lever_crosscheck(M4d)
          · run_laser_epoch(C2,M5) · run_power_sweep(C3,M6) · run_stark_sweep(C3d,M4e) · run_amplitude_trapping(M7) · run_modelform(M8) · run_transit_mc(M9) · run_amplitude_ratios(M10) · run_sigma_laser_sharing(M4c) · run_ramp_geometry(§2.6/PLAN §8.3 predictions) · make_figures · make_results_ledger · annotate_results_status(status column, runs LAST)
data_raw/ frozen 2025 dataset (297 unique traces) + MANIFEST.csv
tests/    113-test battery (104 fast ~22 s + 9 `slow` high-statistics
          closure tests via --runslow, incl. the M4d synthetic-β and M4e
          synthetic-κ closures and the MANIFEST qc_reason guards);
          CI runs the full set on numpy-minimum AND latest
docs/     PLAN.md (plan of record) · DATA.md (archive provenance) · RESULTS.md (auto-generated ledger)
          · THEORY_NOTE.md (ramp theory, Brion-facing) · LITERATURE.md (prior-art ledger)
          · PAPER1_SKELETON.md (manuscript scaffold)
results/  committed CSVs (the documented run) + results/README.md
figures/  paper figures from make_figures.py (C1 width-vs-density, C3 power
          sweep, M9 transit degeneracy, M10 area ratios, C1 pooled-width money
          figure + σ_laser(T) anomaly companion, M4d γ-floor lever test)
```

The first five scripts form the pipeline (each reads the previous ones'
`results/`); the rest are the physics analyses keyed to the deliverables.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && pytest -q          # 104 fast tests (~22 s)
pytest -q --runslow                           # full 113 incl. slow closures (what CI runs)
# reproduce the pipeline + the headline results (data_raw/ is already in git,
# so import_data.py is NOT needed — it only re-imports from the old archive):
for s in run_qc run_noise run_ruler run_linefit \
         run_beta_self run_global_fit run_lever_crosscheck run_laser_epoch \
         run_power_sweep run_stark_sweep run_amplitude_trapping run_modelform; do
    python scripts/$s.py          # run_lever_crosscheck is the slow one (~5 min)
done
```

That loop is the headline subset; the remaining analyses named in the tree above
(`run_sigma_laser_sharing`, `run_transit_mc`, `run_amplitude_ratios`,
`run_ramp_geometry`), then `make_figures`, `make_results_ledger`, and
`annotate_results_status` (which appends the machine-readable `status` provenance
column to every `results/*.csv` and must run last, after every producer),
regenerate
the rest of `results/`, the figures, and the ledger — the complete set that
reproduces every committed CSV byte-for-byte.

Raw-data source and history: the 2025 dataset comes from the earlier
`Rb-5S-to-6S-broadening` project; this repository is a clean reimplementation, and
`docs/DATA.md` documents the provenance and every change made here.

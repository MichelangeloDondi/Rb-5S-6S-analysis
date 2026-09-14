# Collisional self-broadening

*[wiki index](README.md) · physical effect*

**The question.** Why an atom's radiating phase, interrupted by collisions,
shows up as a linear, density-dependent Lorentzian width and not a change of
line shape.
**Takes.** The impact approximation's regime: collision duration far
shorter than the interval between collisions. No fitting, no data.
**Gives.** The self-broadening coefficient $\beta_\text{self}$, the
linear-in-density law it sets, and why this repository reports a bound
instead of a value.
**Skip if.** You want the general Lorentzian-plus-Gaussian convolution this
coefficient feeds into, not the collisional mechanism itself. That is
[The Voigt profile](voigt-profile.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

An atom radiating in a gas is interrupted: a close encounter with another
atom shifts the emitter's levels for its duration, scrambling the light's
phase. In the impact approximation, a collision lasts far less time than
the mean interval between collisions, so each encounter is treated as an
instantaneous phase randomisation.

![Line width plotted against Rb number density at four temperatures](../../figures/fig1_width_vs_density.png)

*Line width against Rb number density at four temperatures, the four
hyperfine components shown separately.*

Random phase interruptions at mean rate $1/\tau_c$ are statistically
indistinguishable from an extra decay channel, adding $1/\tau_c$ to the
coherence's decay rate. Two consequences follow: the line stays Lorentzian,
since an exponentially decaying coherence always transforms to one, and its
width grows linearly with the collision rate, hence with density at fixed
temperature,

$$\gamma_\text{coll}=\beta_\text{self}N$$

with $\beta_\text{self}$ the slope of width against density. When the
perturber is the same species as the emitter, the effect is self-broadening,
from the van der Waals attraction between an excited atom and a
ground-state one.

Two Lorentzians convolve to a Lorentzian whose widths add, so a
collisionally broadened line carries the natural width plus the collisional
one, $\Gamma_\text{nat}+\gamma_\text{coll}$, with no change of shape.
Density is therefore the only signature of collisions, and must be varied
to measure the coefficient.

## What problem it solves

The coefficient connects a measured lineshape to an interatomic potential,
since $\beta_\text{self}$ depends on the long-range $C_6$ coefficient
between the two states involved. It is also a nuisance term to bound, not a
target, in any experiment raising vapour density for signal, since doing so
broadens the line being measured.

## Where this repository uses it

$\beta_\text{self}$ on the 5S to 6S transition is the repository's first
deliverable, built on the linear-in-density law above.
[Methods chapter 2](../methods/02_the_lineshape.md) sets out the mechanism
and validity condition, [chapter 6](../methods/06_the_statistics.md) the
inference, [what we found](../methods/07_what_we_found.md) the outcome.
Density is swept by changing cell temperature, the lever arm a temperature
sweep read through the vapour-pressure curve as density.

![The width-versus-density trend from the dataset, nearly flat](../../figures/fig6_gamma_floor.png)

*The 2025 dataset's width-vs-density trend is essentially flat, the
observation behind the bound-not-value call.*

The result is a bound, not a value. The fitted width barely grows across
the density span, where a genuine binary-collision width would be linear,
so the fitted $\gamma_\text{coll}$ reads as a residual floor, not resolved
collisions. The rule that decides measurement against bound was set before
the data were examined. Current numbers are in [RESULTS.md](../RESULTS.md).

## Values that moved
This bound has been rebuilt twice, and neither time on new data. The first
rebuild replaced a hard-coded multiplier, which silently assumed more
degrees of freedom than the fit had, with the Student-t quantile for the
degrees of freedom actually present. The second admitted a fourth
temperature session, stretching the density lever and producing the
headline this page quotes. the private correction record carries every
retired figure and its date.

## A second term

A Lorentzian-equivalent laser width adds to this channel just as the
collisional width does, since Lorentzians convolve to their exact sum. At a
fixed condition the two are unidentifiable: only the sum can be measured,
and a confident split from a fit is a numerical artefact.

Density separates them: $\beta_\text{self} N(T)$ moves with the temperature
ladder, a laser width does not, and both are recovered across the ladder.
Measured on this archive,
$\Gamma_{L,\text{equiv}} = 0.398$ MHz as an inverse-variance mean over four
peaks spanning 0.315 to 0.449 MHz, with a common scalar neither rejected nor
established at $p = 0.097$. Freeing it moves $\beta_\text{self}$ by 42 to 66
per cent ([the laser kernel](laser-frequency-noise-and-the-linewidth.md),
`results/kernel_k3.csv`).

This is the coefficient's binding systematic: the sensitivity to the kernel
representation, within the family tested, is 3.24 times the statistical
error, so repeating the same construction will not improve the number. It
is a sensitivity within that family, not an uncertainty on the coefficient.
The family's own adequacy is separate, addressed by
[identifiability](identifiability.md).

## A term this coefficient absorbs

A two-atom cooperative channel puts a satellite at twice the single-atom
magnetic position, since a pair of atoms can accept two units of angular
momentum where one atom accepts only one
([magnetic sublevels](magnetic-sublevels.md), `rb5s6s/cooperative.py`). Its
rate is linear in density, needing a second atom, and so is its width
contribution.

The two channels are degenerate under a density ladder: no number of
temperature blocks separates them, so whatever the pair channel contributes
is absorbed into $\beta_\text{self}$. This is harmless at the sizes
involved. At Earth's field and 130 °C it adds $3\times10^{-4}$ hertz to a
collisional width of 492 kHz.

A second lever, the field, separates them: this coefficient is indifferent
to it, while the satellite's contribution goes as $B^2$.

A laser contribution to the width is constant in density, not linear in
it, so density does separate it from this coefficient. That separation is
what makes the headline kernel comparison a measurement while its
per-condition version is not ([the Voigt profile](voigt-profile.md)).

## The coefficient from first principles, step by step

Written 2026-09-14, the day the question "is the theory value trustable" was
asked. Every number below is returned by `rb5s6s/vanderwaals.py` and checked
in `tests/test_vanderwaals.py`. Provenance: calculated unless marked.

**Step 1, the interaction.** A Rb atom in $6S$ and a ground-state Rb atom at
distance $R$ interact, at second order in the dipole-dipole coupling, through
$V(R) = -C_6/R^6$ with

$$C_6 = \frac{1}{6}\sum_{k}\sum_{l}\frac{d_k^2  d_l^2}{\Delta_k+\Delta_l},$$

where $k$ runs over the $nP$ levels reached from $6S$ and $l$ over those
reached from $5S$, $d$ the reduced electric-dipole matrix elements
(Safronova-group values, `rb5s6s/polarizability.py`) and $\Delta$ the
transition energy counted from the state, negative for the downward
$6S\to5P$ lines. The $1/6$ is the scalar angular factor for two $J=1/2$
states. This is `c6_direct`. For a ground-state pair every $\Delta$ is
positive and the sum equals the Casimir-Polder integral over imaginary
frequency, $(3/\pi)\int\alpha_A(i\omega)\alpha_B(i\omega) d\omega$, which is
how the module is validated: $C_6(5S+5S)$ comes out 4180 a.u. against the
measured 4688(198) (Stewart et al. 2022), 11 per cent low, the size of the
dropped core polarizability. For the excited pair the integral is not the
sum: its identity $1/(a+b)$ holds for positive $a$ and $b$ only, and a
downward line has $a \lt 0$, so it returns $-1/(|a|+b)$ where the sum has
$1/(b-|a|)$. The module used the integral for every pair until this
section was written, and undercounted $C_6(5S+6S)$ by a factor 1.87 and
$C_6(5S+7S)$ by 1.94 (measured here, planted). The corrected values:

| pair | $C_6$ (a.u.) | of which $5S+5S$ |
|---|---|---|
| $5S+5S$ | 4180 | |
| $5S+6S$ | 53985 | 7.7 per cent |
| $5S+7S$ | 161474 | 2.6 per cent |

**Step 2, which coefficient broadens the line.** The impact phase is set by
the difference of the two levels' interactions with the perturber
(Lewis 1980, eq. 2.39 and 4.13), so what enters is
$\Delta C_6 = C_6(5S+nS) - C_6(5S+5S)$, 49805 a.u. for $6S$ and 157294 for
$7S$. The exchange term of the same order, which couples $|6S,5S\rangle$ to
$|5S,6S\rangle$ through $|nP,n'P\rangle$, splits the potential into two
branches $C_6(1 \pm f)$ with $f$ near a quarter, and averaged as $(1 \pm f)^{2/5}$ they give 0.994 of
the single-branch width, so it is sized and not carried.

**Step 3, the impact cross-section.** Along a straight path with impact
parameter $b$ and relative speed $v$ the phase accumulated in one collision
is $\eta(b) = (3\pi/8) C_6/(\hbar v b^5)$. The width and shift
cross-sections are $\sigma_w = 2\pi\int_0^\infty[1-\cos\eta] b db$ and
$\sigma_d = 2\pi\int_0^\infty\sin\eta b db$. Substituting $t=\eta$ closes
both on the Gamma function,
$\int_0^\infty(1-\cos t) t^{-7/5}dt = -\Gamma(-2/5)\cos(\pi/5)$ and the sine
form with $\sin(\pi/5)$, and

$$\text{HWHM} = n v \sigma_w = 4.0414 n (C_6/\hbar)^{2/5} v^{3/5},
\qquad \frac{\text{shift}}{\text{HWHM}} = \tan\frac{\pi}{5} = 0.7265.$$

The full width is twice that, 8.0828, and the literature rounding 8.16 the
module carried was 1.0 per cent high (`impact_prefactors`). The impact
regime holds by a wide margin: the Weisskopf radius $(C_6/\hbar v)^{1/5}$ is
2.5 nm against a mean interatomic distance of 330 nm at 130 C, and a
collision lasts 6 ps against the 30 ns coherence time. Spin-exchange
collisions of the ground-state atom, which change its hyperfine state, act
at 0.8 nm, inside that radius, where $1-\cos\eta$ already averages to one,
so they add nothing the phase count has not counted.

**Step 4, the speed average.** The width goes as $v^{3/5}$ and the average
of a power is not the power of the average: over the Maxwell distribution
of the relative speed, $\langle v^{3/5}\rangle/\bar v^{3/5} = 0.9775$
(`speed_average_factor`), so the mean-speed form is 2.3 per cent high.

**Step 5, the number.** At 130 C ($\bar v$ = 444 m/s) and $10^{12}$ cm⁻³:

| route | $\beta_\text{self}(6S)$, kHz per $10^{12}$ cm⁻³ | its bar |
|---|---|---|
| first principles, steps 1 to 4 | 3.544 | the recipe's, below |
| anchored on the measured $7S$ rate, $\beta_7 [\Delta C_6(6S)/\Delta C_6(7S)]^{2/5}$ | 3.40 | 0.29, Zameroski's 8.5 per cent alone |
| the same recipe run on $7S$ against Zameroski's 5.39 | 5.61, 4 per cent above | inside the measurement's bar |

The two routes agree to 4 per cent, and the recipe reproduces the only
measured $nS$ self-broadening rate in rubidium within that measurement's own
error. Before the sign correction the recipe read 18 per cent low on $7S$
and the module's docstring blamed the dropped core for the gap, which the
corrected sum refutes.

**Step 6, what the bar really is.** The 0.29 is the $7S$ experiment's
statistical error scaled. The recipe's own terms, each sized: the core and
tail polarizabilities dropped from the sums (3 per cent on the pair
coefficient, 2 per cent on the anchor ratio), the matrix elements (2 per
cent, Safronova's stated accuracy), the exchange branches (0.6 per cent),
the speed average (now carried), the cell temperature at which the $7S$ rate
per millitorr was converted to a density (OPEN: 5 per cent per 20 K, the
paper's section 2.5 to be re-read for it), and one inelastic channel with
no size yet, $6S+5S\to4D+5S$ releasing 777 cm⁻¹
([the note](../notes/vdw_difference_potential_and_4d_channel.md)). Added in
quadrature without the last, the coefficient is known to about 11 per cent:
$3.40 \pm 0.37$ kHz per $10^{12}$ cm⁻³, ENVELOPE.

**Step 7, what the archive says about it.** Nothing yet. At 130 C the
collisional width this coefficient predicts is 0.10 MHz, against per-session
laser widths of 0.3 to 3.7 MHz that no instrument calibrated, and the
archive's own bound is ten times above the value. The ultra-joint gate's
"theory coefficient outside the profile" rows measure a kernel absorbing the
transit, not this coefficient, which is why the record keeps it as a prior
and not as a result. A campaign that reaches 170 C multiplies the density
by five and puts the collisional width at half a megahertz beside a
calibrated laser kernel, which is the first measurement of this number.

### Try it

```python
from rb5s6s.vanderwaals import beta_self_anchored, impact_prefactors, speed_average_factor

r = beta_self_anchored()
print(f"C6(5S+6S) {r['c6_5s6s_au']:.0f} a.u., C6(5S+5S) {r['c6_5s5s_au']:.0f} a.u.")
print(f"first principles {r['beta6_first_principles_khz']:.2f}, anchored {r['beta6_khz']:.2f} "
      f"+- {r['beta6_err_khz']:.2f} kHz per 1e12 cm^-3")
print(f"the recipe on 7S over the measurement: {r['prefactor_discrepancy']:.3f}")
print(f"FWHM prefactor {impact_prefactors()['fwhm']:.4f}, speed average {speed_average_factor():.4f}")
```

## What can go wrong

The impact approximation is a physical assumption with a checkable validity
condition. Outside it the lineshape is not Lorentzian: in the quasistatic
limit, the wings follow the potential directly and are strongly asymmetric.
The condition compares collision duration to the interval between
collisions, and this dataset satisfies it with a wide margin, as chapter 2
states.

A different failure mode lies in the inference: any effect that widens the
line and grows with temperature is absorbed into a fitted
$\beta_\text{self}$, since the fit sees only width against density.
Transit-time broadening scales as $\sqrt{T}$ and does this, as does a laser
whose linewidth drifts over a cooling sweep. The joint fit and the
model-independent bound above separate them, which is why a coefficient
from a single temperature series deserves scrutiny.

Treating $\beta_\text{self}$ as temperature-independent is a further
approximation: a power-law correction is predicted for a van der Waals
potential, and on this dataset the predicted size sits an order of
magnitude below the between-block scatter, so the assumption is unresolved,
not confirmed.

## Try it

The collisional width adds to the natural one. Density alone moves it.

```python
from rb5s6s import GAMMA_NAT_HZ

gamma_nat = GAMMA_NAT_HZ / 1e6
for N in (1.0e13, 2.9e13):
    print(f"N = {N:.1e} /cm3 -> Lorentzian {gamma_nat + 2.0e-13 * N:.3f} MHz")
```

## Further reading

- [`../lit/baranger1958.md`](../lit/baranger1958.md), the impact-approximation
  treatment this page follows, with its own validity bound.
- [`../lit/lewis1980.md`](../lit/lewis1980.md), the relation between the
  broadening coefficient, the interatomic potential, and temperature.
- [Wikipedia: pressure broadening](https://en.wikipedia.org/wiki/Spectral_line_shape#Pressure_broadening),
  the family of mechanisms this one belongs to.

## See also

- [The self-broadening dossier](../quantities/self-broadening.md), the
  literature ladder, current bound, and improvement levels on one page.
- [The Voigt profile](voigt-profile.md), the Lorentzian kernel this
  coefficient's width sets.
- [The joint fit](joint-fit.md), how sharing the laser width across lines
  separates collisional broadening from the rest.
- [Resampling](resampling.md), the leave-one-out diagnostic for how much of
  the bound's leverage sits on one point.
- [Transit-time broadening](transit-time-broadening.md), the mechanism most
  likely to be mistaken for collisional broadening in a temperature sweep.

---

[← Saturation](saturation.md) · *Experimental spectroscopy, 9 of 11* · [Vapour density and temperature →](vapour-density-and-temperature.md)

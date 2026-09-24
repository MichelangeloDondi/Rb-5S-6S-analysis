# Collisional self-broadening

*[wiki index](README.md) · physical effect*

Why an atom's radiating phase, interrupted by collisions, shows up as a linear, density-dependent Lorentzian width and not a change of line shape. This page builds on the impact approximation's regime: collision duration far shorter than the interval between collisions. No fitting, no data. It sets out the self-broadening coefficient $\beta_\text{self}$, the linear-in-density law it sets, and why this repository reports a bound instead of a value. Not covered here: the general Lorentzian-plus-Gaussian convolution this coefficient feeds into, not the collisional mechanism itself. That is [The Voigt profile](voigt-profile.md).

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## Definition

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

## The problem it addresses

The coefficient connects a measured lineshape to an interatomic potential,
since $\beta_\text{self}$ depends on the long-range $C_6$ coefficient
between the two states involved. It is also a nuisance term to bound, not a
target, in any experiment raising vapour density for signal, since doing so
broadens the line being measured.

## Application in this repository
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

## Revised values

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
$\Gamma_{L,\text{equiv}} = 0.078$ MHz as an inverse-variance mean over four
peaks spanning 0.009 to 0.115 MHz, with a common scalar neither rejected nor
established at $p = 0.16$. Freeing it moves $\beta_\text{self}$ by 5 to 48
per cent ([the laser kernel](laser-frequency-noise-and-the-linewidth.md),
`results/kernel_k3.csv`).

This is not the coefficient's binding systematic: the sensitivity to the
kernel representation, within the family tested, is 0.61 times the
statistical error, so repeating the same construction still improves the
number. It is a sensitivity within that family, not an uncertainty on the coefficient.
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

A foreign gas is the other constant term, and a glass cell cannot exclude
one. Laboratory air carries helium at 5.24 parts per million, so a sealed
cell reaches equilibrium near 4 mTorr of it, a density about
$1.3\times10^{14}\ \mathrm{cm}^{-3}$ that no run changes, since permeation through
the wall has a time constant of days. Against a rubidium density the oven
moves over more than a factor of fifty, that is 109 helium atoms per
rubidium atom at 70 °C and 2 at 130 °C. Zameroski and co-workers measure the
noble gases against a rubidium two-photon line and give helium at
$51.1(4)$ MHz per Torr of broadening and $2.06(7)$ of shift
([`../lit/zameroski2014.md`](../lit/zameroski2014.md)).

Those rates belong to
their line and not to this one. Their upper state is $5D$ and this record's is
the more compact $6S$, and the literature note's own verdict is that the upper
states differ, so the coefficients cannot carry across and no value there can be
taken as one here. **No width on the 5S-6S line follows from them**, which is
why the widths this page carried until 2026-09-18 are withdrawn and why
`lineshape.permeated_gas_width_mhz` refuses to run without coefficients its
caller supplies. What survives the change of upper state is the order of the
species by size and the sign of each shift.

Density separates it from this coefficient in principle, exactly as it
separates the laser's contribution. What decides whether the separation
happens is the shape, and that is where a foreign gas differs from the laser.
A helium width is a Lorentzian, and the constant the fit leaves free is
usually a Gaussian, for the laser. Lorentzian and Gaussian widths do not substitute for
one another, so a constant Lorentzian the model omits is absorbed by the one
Lorentzian the model does have, which is $\beta_\text{self}N(T)$ itself. A
term with no density dependence at all therefore biases a density slope, and
it biases it upward. The remedy is a free constant of the right shape, not a
finer density ladder.

Helium is not the only gas the wall admits, and it is not the largest.
Permeation carries the cell to the atmosphere's own partial pressure of every
species small enough to cross the glass, so abundance fixes where it ends and
permeability fixes only how long it takes to get there. Neon is 18.2 parts per
million of air against helium's 5.24, so its equilibrium pressure is 13.8
mTorr, and the same measurement gives it 24.7 MHz per Torr of broadening and a
shift of $-5.23$. On the source's own line that pressure makes neon the larger
of the two by about 1.7 and reverses the sign of the shift against helium's.
Both rates are measured on 5S-5D, so neither is carried to this line, and the
sign reversal is what survives the change of upper state.

Neon's permeability through a silicate wall is a hundredth to a thousandth of
helium's, so its time constant is years where helium's is days, and how far a
given cell has travelled toward equilibrium depends on its fill date and its
glass.

The heavier gases are ruled out by the line itself. Argon is 9340 parts per
million, so at equilibrium it would put 7.1 Torr in the cell and 324 MHz on the
line at 45.7 MHz per Torr. An observed line a few MHz wide therefore holds
argon below a few parts in a thousand of its equilibrium, a permeation bound
read off the data instead of assumed, and nitrogen and oxygen follow with
larger kinetic diameters still. Hydrogen sits an order below helium in partial
pressure and is removed chemically by the rubidium, so its steady state is
lower again.

One property of the family is worth stating precisely, because it is easy to
over-claim. The cell sits between two regimes and they differ in sign. Held at a fixed
count, as it is within any one session, the density is the figure above and the
width *rises* as $T^{3/10}$, five per cent across a 70 to 130 C ladder, since an
impact cross-section goes as the two-fifths power of the interaction
coefficient. Equilibrated at temperature it is the *pressure* that equalises,
so the density falls as one over the cell temperature, $1.30\times10^{14}$ per
cubic centimetre at room temperature against $9.54\times10^{13}$ at 130 C, and
the width *falls* as $T^{-7/10}$, 10.7 per cent across the same ladder.
Equilibration at temperature takes weeks, so a campaign of days sits between
the two and the figures are a band.

The family is flat where the
coefficient is steep, against a rubidium term that rises fifty-five fold over
the same span, and that is the separation the temperature ladder rests on.

The practical consequence is that the free constant above absorbs the whole
family at once. Enumerating the species adds no parameter. What it adds is the
shape of the prior on the parameter already there, a constant Lorentzian with no
temperature slope, and the order of the species inside it. Its centre is not
computable from what this record holds, because that would need the two
coefficients on the 5S-6S line and the note withholds the ones it has. The width
the fit returns for that constant is therefore a measurement and not a check
against a number derived here.

The two gases also separate, because their signatures are independent. Helium
broadens at 51.1 MHz per Torr and shifts at $+2.06$, neon at 24.7 and $-5.23$,
a pair whose determinant is $-318$ in those units at a condition number of 10. <!-- other-quantity: a determinant -->
A constant width and a constant shift measured together therefore separate the
two gases, the independence being structural. Inverting to partial pressures
needs the two coefficients on the line in question, which this record does not
hold for 5S-6S (the source's are 5S-5D and are not transferable), and on the
source's own line the inversion closes on its weak limit: a helium-only forward
pair returns the helium partial pressure it was built from and zero neon. The shift is the sharper of the two observables, swinging
59 kHz across the neon fill where the width only doubles, so an absolute
frequency reference measures the fill as a by-product.

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
$1/(b-|a|)$.

The module used the integral for every pair until this
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
$|5S,6S\rangle$ through $|nP,n'P\rangle$, is computed from the same tables
(`c6_exchange`). The tables carry magnitudes, and the relative signs of the
$nP$ legs follow from the off-diagonal Thomas-Reiche-Kuhn rule,
$\sum_k (\Delta_k(5S) + \Delta_k(6S))  d(5S,k)  d(6S,k) = 0$ for orthogonal
states. That rule does not constrain the legs equally, and the sentence this page
carried until 2026-09-15 -- that the elements satisfy it "for one pattern only"
-- claimed more than it had.

The per-group terms are 5P 1.308, 6P 1.284, 7P
0.069 and 8P 0.017, so every $6P$-positive pattern leaves 2.5 to 2.7 against
0.03 to 0.11 for the $6P$-negative ones: **the $6P$ sign is fixed at about fifty
tail widths and the $7P$ and $8P$ signs are not.** The tail from $9P$ to $12P$ is 0.02
to 0.05, which covers the $8P$ term outright and the gap between the two best
patterns, so two patterns close inside the tail. Across them the exchange
coefficient runs 17.4 to 17.5 thousand a.u. and the fraction 0.348 to 0.352, so
0.35 of $\Delta C_6$ for 6S stands to its two figures and a five-figure
coefficient does not. On the $7S$ rung two patterns are degenerate outright and
4.5 per cent is one of two readings.

It splits the
potential into two branches $C_6(1 \pm f)$ sampled with equal weight (an
equal superposition of the two exchange eigenstates), and since the width
goes as $C_6^{2/5}$ the factor is $((1+f)^{2/5} + (1-f)^{2/5})/2$, 0.985 for
6S and 1.000 for 7S. <!-- other-quantity: the 7S exchange-branch width factor, exactly 1 by construction, not a committed cell --> It does not cancel in the anchor.

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

Step 5, the number, and the two temperatures it has to keep apart. A rate
per millitorr becomes a rate per density only through $n = P/kT$ at the cell
temperature of the measurement itself, and the impact width then goes as
$\langle v^{3/5}\rangle$ and so as $T^{0.3}$ at fixed density. Those are two
steps, and this record has now got the second one wrong twice. It converted at
its own 403.15 K <!-- other-quantity: the archive's 130 C reference cell temperature, not the twin's radiation-temperature cell --> with no speed scaling until 2026-09-15. It then converted at
393 K for one afternoon, reading that number off a table note. The board's
physics seat retracted both the same day, against the source:

> The temperature of the cell ranged from 353 K to 438 K.  *(figure 7 caption, the <!-- other-quantity: a temperature -->
> plot the 129 kHz mTorr⁻¹ slope is fitted from)*

The rate is a slope across 85 K and has no single temperature. The 393 K
belongs to a table note giving the self-broadening contribution for a different
experiment's linewidth budget at that experiment's temperature, a number about
another quantity that happened to agree with the reading. Where the slope's
effective temperature sits depends on the weights, and the Rb pressure runs
0.056 mTorr at 353 K to 9.3 at 438, so the hot end carries the leverage: <!-- other-quantity: a temperature -->
weighting by pressure gives 428.5 K, equal weight in $T$ gives 420.4, weighting
by the inverse square of the width gives 368.3. The paper weights by the
standard deviation of its own linewidths and does not print them, so **the
effective temperature is not stated anywhere in the paper**, and the span is a budget row. Taken here: [429](../../results/beta_self_theory.csv "ref:beta_self_theory:anchor:effective_temperature_k") K, the centre of the
$\beta$ those weightings imply. At 130 C
($\bar v$ = 444 m/s) and $10^{12}$ cm⁻³:

| route | $\beta_\text{self}(6S)$, kHz per $10^{12}$ cm⁻³ | its bar |
|---|---|---|
| anchored on the measured $7S$ rate, $\beta_7 [\Delta C_6(6S)/\Delta C_6(7S)]^{2/5}$ times the ratio of branch factors | [3.50](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:anchored") | [0.37](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:anchored:err"), the whole budget of step 6 |
| first principles, steps 1 to 4, the exchange branches carried | [3.49](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:first_principles") | it carries the recipe's own scale, which the anchor divides out |
| the same recipe run on $7S$ against Zameroski's [5.62](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_7s:measured") | [5.61](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_7s:predicted"), 6.1 per cent above | 0.72 of the measurement's own bar |

The two routes differ by exactly that [-0.17](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_7s:recipe_scale_error") per cent, and **every
discrepancy this page reported on 2026-09-15 was its own conversion.** The two
are the same computation with and without the experimental scale, so their gap
measures the recipe's absolute error on the one state that has a measured rate.
It read 4 per cent, then 6.1, then 5.4 as the conversion temperature moved
through three wrong readings, and at the leverage-weighted temperature it is
under one part in five hundred. This is still not two independent estimates
agreeing -- the anchored route takes its scale from the measurement and the
first-principles route does not -- but a recipe reproducing an experiment it
never saw, to better than one per cent, is the strongest statement this page has
been able to make about the impact calculation.

The exchange branches, computed on
2026-09-14 in place of the hand estimate and signed by the sum rule, lower the
6S value by 1.5 per cent. Before the sign correction the recipe read 18 per
cent low on $7S$ and the module's docstring blamed the dropped core for the
gap, which the corrected sum refutes.

Step 6, what the bar really is, and every row of it is measured.
`vanderwaals.beta_self_budget` displaces one input at a time and reads the
fractional move in $\beta$, so no row below is an exponent typed into a
comment. In falling order:

| term | how it was sized | on $\beta$ |
|---|---|---|
| Zameroski's total bar, 13 on 129 (Table 3) | it enters linearly, the anchor taking its whole scale from that measurement | [10.08](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:anchor_measurement") per cent |
| the exchange branches | the whole term's size carried as its bar, the signs being fixed by the sum rule | [1.52](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:exchange_branches") per cent |
| the slope's conversion temperature, 402 to 429 K | the rate is a slope over 353 to 438 K and the paper does not print the weights that fix its effective temperature, so $\beta$ is displaced across the span the defensible weightings give | [2.51](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:anchor_conversion_temperature") per cent |
| the matrix elements, 2 per cent (Safronova's stated accuracy) | applied to the 6S sum alone, a common-mode error cancelling in the ratio | [1.71](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:matrix_elements_2pc_differential") per cent |
| the truncated ground-pair sum | this module's 4180 a.u. swapped for the literature 4691, a 12 per cent move | [0.28](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:ground_pair_truncation") per cent |

So the coefficient is known exactly as well as that one measurement is, and
no better. The quadrature sum is [10.64](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:rel_uncertainty") per cent,
of which the anchor measurement alone is [10.08](../../results/beta_self_theory.csv "ref:beta_self_theory:budget:anchor_measurement") per cent. Everything the
recipe contributes is 2.0 per cent in quadrature, and that is the whole distance
between those two numbers. The
value of record is $3.50 \pm 0.37$ kHz per $10^{12}$ cm⁻³, ENVELOPE, written in
the form this repository uses for every bar, two significant digits with the
value matching its decimals.

And the row this record deleted as a double count was not one. On
2026-09-15 it read section 2.5 -- "For the self-broadening and shift rates, a 5%
uncertainty is used for the temperature dependent vapor pressure (density)" --
as putting that term inside the $\pm 11$, and removed it, taking the bar from 11
per cent to 8.8. **The paper prints two bars and the larger is the total.**
Section 2.5 quotes $129 \pm 11$, Table 3 quotes $129 \pm 13$, and Table 4's
$107 \pm 11$ is $0.83 \times 13$. The arithmetic closes both ways on his own
stated recipe: $\sqrt{11^2 + 6.45^2 + 1.29^2} = 12.8$, printed 13, and
$\sqrt{13^2 - 6.45^2 - 1.29^2} = 11.2$, printed 11.

So the $\pm 11$ is the
linear-fit interval without the density term and the $\pm 13$ is the total with
it: the 5 per cent is the difference between them, deleting it narrowed a bar
that was already right, and **the source's total is what this page now carries.**
One convention does survive from that paragraph, and the record has been bitten
by its kind before: his rates are on the atomic axis, $\nu = 2\nu_L$, which is
the axis this page wants.

And the size of the conservatism is known, because he states what his bar is
made of. It is a 95 per cent linear-fit interval, a 1 per cent transducer
calibration and the 5 per cent density term, in quadrature. Solving for the fit
half gives [8.69](../../results/beta_self_theory.csv "ref:beta_self_theory:anchor_bar_one_sigma:fit_half_95pc") per
cent, and dividing that by the t-factor of a fit over a handful of pressure points
leaves a total of [5.78](../../results/beta_self_theory.csv "ref:beta_self_theory:anchor_bar_one_sigma:t_dof3_3.18") to
[6.76](../../results/beta_self_theory.csv "ref:beta_self_theory:anchor_bar_one_sigma:gaussian_1.96") per cent, or 0.18
to 0.27 kHz. So the coefficient carried here is about 1.3 times wider than a one-sigma
reading of the same measurement. That reading is recorded and not taken: the division
needs his degrees of freedom and the paper does not give them, and a bar a reader
cannot rebuild from the source is worse than one that is wide.

What it does say is
where the precision is: not in the recipe, and not in anything this repository can
compute, but in one 2014 linear fit.

**What the quadrature leaves out**, named and not absorbed. The recipe's
**his Rb pressure axis against this record's own density curve**, which is the
largest term in the problem and no reading of the paper spans it: he cites the
same correlation `rb5s6s/density.py` uses, yet his table notes give 0.83 mTorr at
393 K and 0.23 at 373 where that curve gives 0.671 and 0.184, a ratio of 1.24, so  <!-- other-quantity: a vapour-pressure scale ratio -->
either his slope is ~20 per cent low on this record's density scale or his
temperature labels are 3.4 K low. The inelastic exit on the anchor rung,
$7S+5S\to5P+5P$, open by 678 cm⁻¹ and first-order dipole-dipole coupled, worth 1
to 3 per cent, where the $6S+5S\to4D+5S$ channel this paragraph used to name sits
on the target rung, releases 777 cm⁻¹ and largely cancels
([the note](../notes/vdw_difference_potential_and_4d_channel.md)). And the
recipe's absolute scale error carrying an $n$-dependence.

Step 7, what the archive says about it. Nothing yet. At 130 C the
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

## Failure modes

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

## Related pages
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

[← Saturation](saturation.md) · *Experimental spectroscopy, 10 of 12* · [Vapour density and temperature →](vapour-density-and-temperature.md)

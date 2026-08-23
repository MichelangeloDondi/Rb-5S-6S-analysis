# Atomic saturation broadening is a companion to the width-channel light-shift lever

Status: OPEN, recorded 2026-08-09 for adjudication. Nothing here is retracted and
no committed number changes. The finding is that a term with the same power
signature as the one the C3d and C3f width lever is built on, and several times
larger, is absent from the forward model. The direction of the bias is favourable,
which is why this is a note rather than a correction.

`provenance: results/saturation_companion.csv` - **UPGRADED from NO_PRODUCER on 2026-08-23.** The probe now writes its C3d half, so the reproduced committed bound, both saturated bounds and both tightening factors are committed rows that the freshness machinery regenerates and checks. **The JOINT factor is deliberately NOT a row**: stage 4 reads two data trees outside this repository, and stage 3 states in terms that quoting a joint number before that fit runs would be inventing one, so the CSV records it as a classification with the date of the run that produced it rather than as a digit. **6 numeric claims on this page remain unaccounted for**, the stage-1 and stage-3 intermediates among them.


**The question.** Is the power-squared broadening the light-shift bound rests
on really the light shift?
**Takes.** [methods/04_the_composite_model.md](../methods/04_the_composite_model.md).
**Gives.** Two effects with the same power signature that are absent from that
model, their sizes measured rather than argued, and what they do and do not
license.
**Skip if.** You are not reading the light-shift bound closely. The short
version is that both bounds stand and are loose by a stated factor.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## How it came up

From a question about what a third 993 nm photon does. That answer is in
[THEORY_NOTE](../THEORY_NOTE.md) section 5.2 and is uninteresting: nothing
measurable. Getting there required the two-photon Rabi frequency, which the
repository had never computed, and that number turned out to matter for a
different reason.

## The number

The two-photon Rabi frequency for 5S(1/2) to 6S(1/2) at 993.4192 nm, at the
campaign maximum of 225 mW with the measured 64 um waist and rho = 0.94, is

    Omega_2ph / 2pi = 450 kHz   on axis

and it is now computed from the bench numbers up rather than tethered to
anything: `hyperpolarizability.two_photon_rabi_hz` walks power to intensity to
field to coupling, `scripts/run_saturation_probe.py` prints every step, and
Delta_alpha does not appear in the chain. That matters because the tether was
where the error was.

**Two corrections from the 2026-08-09 second reading, in order of size.**

![the standing wave, its mean and its fringe amplitude, and the gap between them](../../figures/fig25_retro_combination.png)

*The paragraph below in one picture. One field, two readings: the shift follows
the fringe MEAN because it is linear in intensity, and the Doppler-free
coupling takes the fringe AMPLITUDE because only the wavevector-cancelling term
survives. The right panel is the size of the difference against the retro
return fraction, which is why the formula carries the distinction even though
it moves no digit at this bench's own rho.*

*The retro enters the coupling as a geometric mean, not an arithmetic one.* The
shift is linear in |E|^2, whose fringe mean is (1 + rho) times one arm, and that
is what `lineshape.stark_shift_S0_mhz` uses. A two-photon amplitude is linear in
E^2 instead, and only its wavevector-cancelling term is Doppler-free, with
coefficient 2 sqrt(rho) times one arm. The correction is exactly the fringe
contrast 2 sqrt(rho)/(1 + rho) that `constants.DELTA_ALPHA_AU` already defines:
0.05 per cent at rho = 0.94, so 450 kHz stands to three digits, but 1.0 per cent
at rho = 0.75, so the formula carries it now. A corollary is worth more than the
correction: the Doppler-free coupling has no fringe dependence at all, so the
RATE is fringe-immune while the SHIFT is not.

*The earlier "correction" of the ratio was itself wrong.* This note first used
Omega/2pi = 1.294 x S0, then recorded 1.237 as a correction of "two field
conventions". That diagnosis was mistaken. Both numbers are right about
different denominators, because the project holds two values of |Delta_alpha|
that differ by a documented 4.7 per cent: the cited 1093 a.u. that every
committed S0 is written with, giving 2T/1093 = 1.2951, and this package's own
sum-over-states 1145 a.u., giving 1.2367. The ratio is therefore a 1.24 to 1.30
band whose width is the Delta_alpha discrepancy, and the probe below now reports
both ends. The matrix element itself, T = 707.75 a.u. and M = 225 kHz at the
campaign maximum, was confirmed independently to 0.04 per cent and does not
move.

Against the 3.4925 MHz natural width, 450 kHz is a saturation parameter s = 0.033
on axis and 0.0146 signal-weighted. The atom reaches steady state, since the 456 ns
beam chord is about ten natural lifetimes, so the homogeneous power-broadening
formula applies, and Omega times the crossing time is 1.29 radians, so there is
no Rabi flopping and the drive is weak throughout.

**The predicted broadening across the whole sweep is 24 kHz**, which is 0.45 per
cent of the line, one to two orders of magnitude below the 3 to 8 per cent
block-to-block scatter that C3a already reports, and below a single block's 82 kHz
width scatter. So the observed absence of a power trend in the width is consistent
with saturation and is not evidence about it either way. That part is a
confirmation of C3a with a number attached.

## Why it is worth a note

**The saturation broadening is larger than the ramp broadening the light-shift
width bound is built on, and carries the identical P-squared signature.** At the
predicted S0 = 0.3476 MHz the ramp broadens the line by 6.58 kHz, computed with
the fit's own `rb5s6s.stark._fwhm_of` at the campaign's representative widths
(collisional 0.60, laser 1.50, transit 0.96 MHz, unshifted FWHM 5.3737 MHz, which
reproduces the observed 5.37). Saturation contributes 24 to 25 kHz at the same
field. The ratio is **about 3.7**, and it is stable across the waist measurement band
because both terms scale as the inverse fourth power of the waist.

Two consequences follow.

1. The C3d and C3f construction fits one shared kappa to width against power with
   a forward model that contains the ramp and not the saturation. The two are
   degenerate at this order, so any P-squared broadening the fit does see is
   mostly the companion.
2. **The direction is favourable and should be stated as such.** If the observed
   P-squared broadening is mostly saturation, the true limit on the Stark kappa is
   *tighter* than the quoted bound, not looser. The fit rails at kappa = 0, so in
   practice the quoted bound is conservative rather than wrong. That is why this
   note opens no retraction.

## A second companion, found on the 2026-08-09 adversarial pass

Saturation broadening is not the only P-squared term missing from the width
model. The atom is not a closed two-level system: every real 6S decay cascades
through 5P, and the D-line decay back to the ground state does not preserve F, so
a fraction of transiting atoms are pumped into the other ground hyperfine level
and leave the resonance 3.0 GHz behind them. Nothing in this repository models
that, and a search for the vocabulary of it (optical pumping, hyperfine pumping,
dark state, repump) returns nothing.

The size is not negligible and the arithmetic is short. At the campaign maximum
the steady-state excited fraction is s/2/(1+s) = 0.0161 on axis, so real decays
occur at 3.5e5 per second, which is 0.16 cascades per 456 ns transit.

**TWO DIFFERENT NUMBERS COME OUT OF THAT AND THEY ARE EASY TO SWAP.** Stated
once here, since this note is where the arithmetic lives and every other
document should carry these and say which is which.

| quantity | signal-weighted | on axis | what its range spans |
|---|---|---|---|
| mean cascades per transit, n | 0.081 | 0.162 | the weighting only |
| **decays AT LEAST ONCE**, 1 - exp(-n) | **7.8%** | **15.0%** | the weighting only |
| **pumped into the OTHER ground state** | **1.8%** | **5.9%** | the weighting AND the per-line branching |

The first two rows differ because 1 - exp(-n) is not n, an 8 per cent gap at
this n, and quoting n while saying "decay at least once" is the specific error
this table exists to prevent. The third row is smaller than the second because
only a share f of cascades lands in the other hyperfine level, and its range is
wider IN KIND: it runs over the four lines' branching fractions as well as over
the weighting, so it is not a signal-weighted-to-axis span the way the row
above it is.

Recomputed 2026-08-15 from the repository's own `ramp_moments` at the
collection half-length the figure states, Z_c = 2.2 mm, which gives a
signal-weighted saturation parameter of 0.01624 against 0.03319 on axis, a
weighting factor of 0.489. The earlier "7 to 15" in this paragraph was built on
the 25.4 kHz weighted saturation quoted below, which carries no Z_c with it.
Figure 23 computes the same quantity at a stated Z_c and gets 28.2 kHz, as the
caption further down already records, and these rows use the figure's value.

A ground-state loss rate gamma_p adds gamma_p/2 to the coherence decay, hence
gamma_p/2pi to the Lorentzian FWHM.

What makes it worth writing down is that the ratio to the saturation term is
exactly the branching fraction, with everything else cancelling. In the weak-drive
limit the saturation increment is Gamma_FWHM x s/2, and the pumping increment is
f x (s/2) x Gamma_6S/2pi, and Gamma_6S/2pi IS Gamma_FWHM. So

    pumping width / saturation width = f,

independent of power, waist, retro ratio and Rabi frequency. Numerically, at the
campaign maximum: saturation 57.5 kHz on axis and 25.4 signal-weighted, pumping
18.7 to 37.4 kHz on axis and 8.4 to 16.8 signal-weighted over f = 1/3 to 2/3.

**f IS NOT A BRACKET, it is four numbers (2026-08-10).** The 1/3 to 2/3 range
below was a placeholder for an unresolved branching, and the branching resolves.

The two-photon operator here is SCALAR, K = 0 only (the ABUNDANCE_RB85 note), so
6S is populated in ONE hyperfine level F and not statistically. f is then the
product of the two cascade steps, 6S(F) to 5P_J(F'') and 5P_J(F'') to 5S, with
6j symbols throughout. Each J leg scales the naive degeneracy weight of the
undriven level by a clean fraction, 8/9 through 5P1/2 and 4/9 through 5P3/2, so
the combination is 0.596 and is the SAME for all four lines:

| line | isotope, driven F | naive weight | f | pumping width at 225 mW |
|---|---|---|---|---|
| 993.4121 nm | 87Rb, F = 1 | 5/8 | 0.372 | 10.5 kHz |
| 993.4154 nm | 85Rb, F = 2 | 7/12 | 0.348 | 9.8 kHz |
| 993.4192 nm | 85Rb, F = 3 | 5/12 | 0.248 | 7.0 kHz |
| 993.4207 nm | 87Rb, F = 2 | 3/8 | 0.223 | 6.3 kHz |

**Where the 8/9 and the 4/9 come from, added 2026-08-10 after the obvious
objection was put.** They are not a smoothing. Level by level the branching is
nothing like the naive weight, and every one of the four lines has an
intermediate level that is populated and **cannot reach the undriven ground
level at all**: 5P3/2 F=0 for the 4121 line, F=1 for 4154, F=4 for 4192, F=3 for
4207, carrying between 0.17 and 0.70 of the flux through that leg. A J=1 photon
cannot connect F=0 to F=2, so those paths return the atom to the level it came
from and are not losses. Check 6 of `scripts/run_zeeman_depletion.py` prints the
whole cascade resolved by intermediate F with those zeros in it.

The leg totals come out at the naive weight times 8/9 and 4/9 anyway, for both
isotopes and every driven level, and that is a sum rule rather than an accident.
A spontaneous decay evolves the density matrix as
$\rho\to\sum_q D_q\rho D_q^\dagger$, which is basis-free, and neither dipole
operator touches the nucleus, so evaluating it in $(m_J, m_I)$ makes the nuclear
spin a spectator and the answer factorises into a purely electronic two-step
transfer and a projection back onto the $F$ basis. The closed form is

$$\text{leg ratio} = 2(1-p), \qquad p = P(m_J \text{ unchanged over the cascade})$$

with $p = 5/9$ through $5P_{1/2}$ and $7/9$ through $5P_{3/2}$, giving 8/9 and
4/9 with no nuclear spin anywhere in the derivation. The blocked paths are real
and they cancel exactly against the paths that are enhanced.

**One step of that argument was stated too strongly at first and is corrected
here.** A sum of PROBABILITIES over an intermediate basis is not basis-free, so
"the hyperfine sum equals the $(m_J,m_I)$ sum" is not something the completeness
of the basis gives you. What licenses dropping the hyperfine coherences is that
the $5P$ splitting far exceeds the linewidth, so they dephase within the
intermediate lifetime, and what licenses dropping the $m$ coherences is that the
prepared state is unpolarised. Rather than rest on either, check 7 of
`scripts/run_zeeman_depletion.py` evaluates
$\rho\to\sum_q D_q\rho D_q^\dagger$ twice in the $|m_J,m_I\rangle$ basis with
every coherence kept, in exact rational arithmetic, never mentioning hyperfine
structure in the evolution. It returns 5/9, 14/27, 10/27, 1/3 and 5/18, 7/27,
5/27, 1/6, which are exactly 8/9 and 4/9 of the naive weights. So the coherences
a density-matrix treatment keeps make no difference to this observable, and that
is a computed fact rather than an argument.

A FIRST PASS ASSUMED A STATISTICAL 6S POPULATION and gave the naive column as f.
That was wrong by exactly the 0.596, and it is recorded because the error had a
direction: it made the pumping companion LARGER than it is. The lower two lines
fall outside the retired 1/3 to 2/3 bracket, so this does not merely narrow the
bracket, it moves the answer down. Drawn in
figures/fig23_hyperfine_pumping.png panel (b).

**AND THIS BREAKS THE DEGENERACY, in the one variable nobody was varying.** The
AC-Stark ramp and the saturation are the SAME on all four lines, because the
two-photon Rabi frequency is F-independent here (the hyperfine factor is
exactly 1, constants.ABUNDANCE_RB85). The pumping is not. So the three
same-signature terms are degenerate in power and in waist, as stated
everywhere, and are NOT degenerate across the line index. The lever between the
extreme lines is 0.625/0.375 = 1.67, which is 7 kHz of width at the campaign
maximum against an 88 kHz single-block width scatter. This dataset cannot spend
it. A session that controls the block scatter can, and it is the only handle
found so far that separates the pumping companion without a fixed lock.

Three consequences.

1. The companion-to-ramp ratio quoted above as 3.7 becomes **4.9 to 6.2** once
   this term is in it, because the two companions carry the identical P-squared
   signature and add.

   ![the hyperfine branch, how often it fires, and the three terms it competes with](../../figures/fig23_hyperfine_pumping.png)

   *This paragraph and the one above it, drawn. Figure 23 recomputes every
   number here at draw time and states the convention the prose above leaves
   implicit: the signal weighting runs over the collection volume at the
   record's own Z_c = 2.2 mm half-length, which is where its 28.2 kHz for the
   weighted saturation comes from against the 25.4 quoted above at an
   unstated Z_c. The ratio moves with it, 5.7 to 7.2 rather than 4.9 to 6.2.
   Quote the figure's numbers with the half-length attached, and read the
   prose ones as the same statement without it. Nothing downstream turns on
   the difference, since both say the companions dominate the ramp by rather
   more than a factor of four.*
2. The direction is unchanged and the effect on the argument is to strengthen it:
   more P-squared broadening from non-Stark sources means the true Stark limit is
   tighter still.
3. What f is remains open. It needs hyperfine-resolved 5P to 5S branching, which
   this repository does not hold, and the 1/3 to 2/3 bracket is a statement about
   plausible alkali branching rather than a calculation. Pinning it is cheap and
   is the natural next step on this note.

One thing this does NOT do is compete with the transit width. The transit
truncation rate, 2.2e6 per second, is twelve times the pumping rate, so transit
still sets that channel and the pumping term is a small addition on top of an
already-fitted 0.96 MHz. It matters because of its power signature, not its size.

## What it does not claim

The dataset's own data do carry a P-squared width feature, fitted at
c = -138 +/- 32 kHz with per-peak cores and one shared coefficient. **That is not
read here as saturation, and the sign is wrong for it.** It fails every stability
check (+180 +/- 120 kHz on the 25 to 125 mW subset against -152 +/- 30 kHz on 75
to 225 mW, a subset spread five to seven times the prediction), and the two peaks
carrying it, 993.4154 and 993.4192, are exactly the two that addendum 21's
postscript reports as pulled by -287 +/- 197 kHz when the Gaussian width is freed
on the brightest traces, while the two that postscript calls unpulled are the two
consistent with zero here. It reads as a brightness-correlated fitting artifact
the record has already named, and it swamps the saturation prediction by about
five.

## One structural result worth keeping

A two-photon S-to-S transition through one nP doublet **cannot** suffer
cancellation between its two fine-structure paths. Both legs of a given path
traverse the same P level, so the angular sign enters squared, and both paths
share the radial pair, so the radial sign cancels as well. The two paths here add
with weights 255 and 481 a.u., essentially the statistical one to two. The
interference that does exist is between nP *families*, where 6P, 7P and 8P are
destructive and reduce the total two-photon matrix element by 3.87 per cent, from
736 to 708 a.u.

This is recorded because the opposite was assumed at the start of this
calculation, and an estimate built on the assumed cancellation came out a factor
4.4 high. It is the kind of error a future estimate will make again.

## What would settle the adjudication

Adding the saturation term to `rb5s6s/stark.py`'s forward model and re-profiling
kappa. The prediction is that the bound tightens and the minimum stays at zero. It adds
no free parameter, because the term is a closed form in Omega_2ph, which is
itself a fixed multiple of S0.

Until that is run, the committed bounds stand as quoted and are conservative in
the direction that matters.

## Postscript, 2026-08-09: the probe was run, and the prediction half held

The adjudication above asked for the saturation term to be added to the width
model and kappa re-profiled. That was done the same day, as an opt-in probe that
modified no committed file: `stark._fwhm_of` was wrapped so the saturation
increment enters through the model's own Lorentzian argument, and the real
`fit_stark_sweep` was then called, so the shared kappa, the per-peak core
re-minimization, the profile scan and the over-dispersion rescaling are all the
shipped code rather than a reimplementation. Unpatched, the probe reproduces the
committed bound at 0.6325 MHz, which is the check that it is running production.

That first run was an in-session patch that was not preserved, so for two days
the headline could not be re-derived by anyone, including whoever wrote it. It is
now `scripts/run_saturation_probe.py`, which is deliberately outside
`run_all.sh`. It wrote nothing until 2026-08-23, when a `--emit` flag was
added so its C3d half lands in `results/saturation_companion.csv`. The joint
half deliberately persists nothing, because it cannot be computed here.

The injected physics is the homogeneous law Gamma to Gamma\*sqrt(1+s) with
s = 2\*Omega^2/Gamma^2, applied with the two-photon Rabi frequency. Folding the
increment into gamma_coll is exact rather than convenient, because power
broadening of a homogeneous line is Lorentzian and Lorentzian widths add.

| | kappa (MHz/W) | S0(225) bound | chi2_red |
|---|---|---|---|
| production, ramp only | 0.0 +/- 6.0 | 0.6325 MHz | 3.7047 |
| with saturation, ratio 1.2367 | +0.4 +/- 1.8 | **0.2299 MHz** | 3.7491 |
| with saturation, ratio 1.2951 | +0.4 +/- 1.8 | **0.2230 MHz** | 3.7601 |

**The bound tightens by a factor 2.8**, from 0.6325 to 0.23 MHz across the ratio
band, which is the direction this note predicted and a larger move than it
suggested. The mechanism is transparent: both models agree at kappa = 0, where S0
and therefore the saturation increment both vanish, but the with-saturation model
broadens faster as kappa rises, so it reaches any observed broadening at a
smaller kappa.

One bookkeeping defect is recorded rather than quietly fixed, because it is
instructive. The single number this note first published, 0.2231 MHz, is the
ratio-1.2951 row. The prose beside it said the probe used 1.237. So the note was
edited to carry the "corrected" ratio without the probe being re-run under it,
and the two disagreed by 3 per cent for two days. Both rows are printed above
now, and neither is a committed bound.

**The other half of the prediction is wrong, and this is the part worth keeping.**
The note said the minimum stays at zero. It does not. Production rails at exactly
kappa = 0 because the width response goes as S0^2 and has no gradient there.
Adding a companion term 3.7 times larger gives the width a resolvable response, so
the minimum un-rails to +0.4490 MHz/W. That is 0.25 sigma from zero and entirely
consistent with no shift, so the substance of the claim survives while its letter
does not. What actually changed is that the parameter stopped being unidentifiable
at the boundary, which is a different and better situation than a railed fit.

The fit quality is untouched, chi2_red moving 3.7047 to 3.76, as expected when
the added effect is far below the block-to-block scatter that dominates chi2.

**Robustness to the one number not independently re-derived at the time.** The ratio came
from the two-photon matrix element and the lead did not rebuild that sum. The bound
scales roughly inversely with it: 0.3732 MHz at half the ratio, 0.23 across the
1.24 to 1.30 band itself, 0.1479 at 1.5 times it. So even a factor-of-two error in
the Rabi frequency leaves the bound well below the committed 0.6325, and the
qualitative result is robust while the digits are not. The sum has since been
rebuilt twice, and the band is now the whole of the residual uncertainty in it.

## Postscript, 2026-08-09: what C3f would do, and why it was not run

C3d is the width-only bound. The number outside documents quote is C3f, the joint
three-session bound at S0(225 mW) below 0.26 MHz, and the obvious question is
whether the companion tightens that one too. **It was not re-run, and the reason
is a data-access fact rather than a modelling one:** the joint fit reads the
4 July evening session and the campaign-morning session from two excluded trees
outside the repository, and `run_stark_joint.py` exits early when they are absent,
which they are on the machine this probe ran on.

What the probe does instead is fix the DIRECTION, which is arithmetic at C3f's own
numbers. At C3f's profile minimum, kappa = 0.25 MHz/W, the ramp broadens the line
by 2.4 kHz and saturation by 1.4 to 1.5 kHz, so the companion is the smaller
term. At C3f's 95 per cent bound, kappa = 1.15 MHz/W, the ramp gives 3.9 kHz and
saturation 29 to 32 kHz, a ratio of 7.5 to 8.2. The companion therefore outgrows
the ramp exactly where the bound is set, so the joint bound must tighten as well.

Its SIZE was left unquoted here, pending the run. **The run has since happened, and
the paragraph above is replaced by the postscript below.**

## Postscript, 2026-08-10: the joint bound was re-profiled, and it tightens by 2.2

The excluded trees were on the machine the whole time, under names the script's
fallback path does not reach, so this was never manual work. Stage 4 of
`scripts/run_saturation_probe.py` now runs it: 100 campaign traces, 46 from the
4 July evening session and 26 from the campaign-morning session, the wing chain
then the primary seeded from it, patching the joint
fit's own profile builder so the shared coefficient, the per-peak priors, the free
per-trace centres and the chain seeding all stay production code. It writes
nothing, and `results/stark_joint.csv` is untouched.

| | minimum kappa | 95% bound | S0(225 mW) |
|---|---|---|---|
| production, ramp only | 0.25 MHz/W | 1.147 MHz/W | 0.258 MHz |
| with saturation, ratio 1.2367 | 0.00 MHz/W | 0.519 MHz/W | **0.117 MHz** |

**The unpatched chain reproduces the committed C3f bound exactly**, 1.147 MHz/W
and 0.258 MHz against the committed 0.26, which is the check that the probe is
driving the shipped fit rather than a reimplementation of it.

**The joint bound tightens by a factor 2.21**, from 0.258 to 0.117 MHz. That is
smaller than C3d's 2.8, which is what this note predicted before the run and for
the reason it gave: the joint fit carries a collisional-width prior that can absorb
part of an added Lorentzian width where the width-only fit cannot.

One behaviour runs opposite to C3d's and is worth recording rather than smoothing.
In the width-only fit, adding the companion UN-RAILED the minimum, from exactly
zero to +0.449 MHz/W, because it gave the width a resolvable gradient where the
ramp alone had none. In the joint fit the minimum moves the other way, from
+0.25 MHz/W to exactly zero. Both are consistent with no shift, and the difference
is that the joint fit already had a gradient from its other channels, so the extra
broadening is absorbed by lowering kappa rather than by raising it.

**The committed C3f bound does not move.** The injected law is still the two-level
homogeneous form used with a two-photon Rabi frequency, standard and steady-state
here but an approximation rather than a derivation, and no committed bound should
move on it. What changes is that C3f, like C3d, is now known to be conservative by
a measured factor rather than by argument: 2.21 for the joint construction and
2.8 for the width-only one.

**What is still not licensed.** The functional form is the two-level homogeneous
law used with a two-photon Rabi frequency. That is standard and the steady-state
condition holds here, the beam chord being about ten natural lifetimes, but it is
an approximation rather than a derivation for a two-photon transition, and no
committed bound should move on it without that step. **The committed C3d bound
therefore stands at 0.63 MHz and remains conservative**, now by a measured factor
of 2.8 rather than by argument.

## Postscript, 2026-08-10: the refit is specified, and it is predicted to fail

The obvious next step is to put both companions inside the fitted model rather
than around it, and the author asked for exactly that. It is preregistered at
[companion_inclusive_refit_prereg.md](companion_inclusive_refit_prereg.md),
which fixes the construction and the acceptance criteria before any code was
written, and the reason it is worth reading is that **the central prediction is
a prediction of failure, made in advance and with its arithmetic shown.**

The pumping term is the only one of the three that differs across the four
hyperfine lines, so a joint fit with the four branching fractions held fixed and
one free scale is the only construction that separates it without a fixed lock.
The lever is 0.149 of the saturation width, 3.06 kHz at 225 mW. A least-squares
power calculation on the actual design, four lines by five powers with the core
widths free, gives a standard error on that scale of 19 to 42 depending on
whether the block scatter is taken per width point or reduced by the five
repeats in a block. So this dataset would see its own computed companion at
0.02 to 0.05 sigma and would return a bound between 31 and 69 times too loose to
touch it.

Stating that in advance is what makes the eventual run informative. A separation
that appears anyway is then a finding about something else, and the record
already names the candidates.

## Postscript, 2026-08-11: the refit ran, and it failed in a different way

The prediction above was that the dataset would see the pumping companion at
0.02 to 0.05 sigma and return a bound 31 to 69 times too loose. **It returned no
bound at all**, and the reason is more basic than the lever being small.

The scale enters the model only as a multiple of the saturation width, which is
proportional to $S_0=\kappa P$. This dataset does not measure $\kappa$, it bounds
it from above, and zero is inside that bound. Profiling over $\kappa$ rather than
holding it, the fit sets $\hat\kappa=0$ for every nonzero scale, which switches
the companion off, and $\chi^2$ returns 55.5712 identically from a scale of 0.5
to a scale of 16. Against the right null, which is the saturation term alone,
$\Delta\chi^2$ is exactly zero at every one of those scales, so there is nothing
to interpolate a bound from.

The power calculation quoted above is not wrong arithmetic. It evaluated the
lever **at the committed $S_0$ bound**, which treats $\kappa$ as though it were
known to sit there. It is not, and that is the whole distance between a standard
error of 19 to 42 and no standard error at all.

Full scoring of all five predictions, including the two that this run did not
test and the two defects it found in the preregistration's own wording, is in
the [postscript to the preregistration](companion_inclusive_refit_prereg.md).
Producer: `scripts/run_companion_refit.py`, which prints its results and persists none of them.

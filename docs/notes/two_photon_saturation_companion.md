# Atomic saturation broadening is a companion to the width-channel light-shift lever

Status: OPEN, recorded 2026-08-09 for adjudication. Nothing here is retracted and
no committed number changes. The finding is that a term with the same power
signature as the one the C3d and C3f width lever is built on, and several times
larger, is absent from the forward model. The direction of the bias is favourable,
which is why this is a note rather than a correction.

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
occur at 3.5e5 per second, which is 0.16 cascades per 456 ns transit: **7 to 15
per cent of atoms crossing the beam decay at least once on the way through**. A
ground-state loss rate gamma_p adds gamma_p/2 to the coherence decay, hence
gamma_p/2pi to the Lorentzian FWHM.

What makes it worth writing down is that the ratio to the saturation term is
exactly the branching fraction, with everything else cancelling. In the weak-drive
limit the saturation increment is Gamma_FWHM x s/2, and the pumping increment is
f x (s/2) x Gamma_6S/2pi, and Gamma_6S/2pi IS Gamma_FWHM. So

    pumping width / saturation width = f,

independent of power, waist, retro ratio and Rabi frequency. Numerically, at the
campaign maximum: saturation 57.5 kHz on axis and 25.4 signal-weighted, pumping
18.7 to 37.4 kHz on axis and 8.4 to 16.8 signal-weighted over f = 1/3 to 2/3.

Three consequences.

1. The companion-to-ramp ratio quoted below as 3.7 becomes **4.9 to 6.2** once
   this term is in it, because the two companions carry the identical P-squared
   signature and add.
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

The archive's own data do carry a P-squared width feature, fitted at
c = -138 +/- 32 kHz with per-peak cores and one shared coefficient. **That is not
read here as saturation, and the sign is wrong for it.** It fails every stability
check (+180 +/- 117 kHz on the 25 to 125 mW subset against -152 +/- 30 kHz on 75
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
`run_all.sh` and writes nothing.

The injected physics is the homogeneous law Gamma to Gamma\*sqrt(1+s) with
s = 2\*Omega^2/Gamma^2, applied with the two-photon Rabi frequency. Folding the
increment into gamma_coll is exact rather than convenient, because power
broadening of a homogeneous line is Lorentzian and Lorentzian widths add.

| | kappa (MHz/W) | S0(225) bound | chi2_red |
|---|---|---|---|
| production, ramp only | 0.0000 +/- 5.9562 | 0.6325 MHz | 3.7047 |
| with saturation, ratio 1.2367 | +0.4490 +/- 1.8484 | **0.2299 MHz** | 3.7491 |
| with saturation, ratio 1.2951 | +0.4490 +/- 1.8190 | **0.2230 MHz** | 3.7601 |

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
2025-07-04 rehearsal and the campaign-morning pilot from two quarantine trees
outside the repository, and `run_stark_joint.py` exits early when they are absent,
which they are on the machine this probe ran on.

What the probe does instead is fix the DIRECTION, which is arithmetic at C3f's own
numbers. At C3f's profile minimum, kappa = 0.25 MHz/W, the ramp broadens the line
by 2.4 kHz and saturation by 1.4 to 1.5 kHz, so the companion is the smaller
term. At C3f's 95 per cent bound, kappa = 1.15 MHz/W, the ramp gives 3.9 kHz and
saturation 29 to 32 kHz, a ratio of 7.5 to 8.2. The companion therefore outgrows
the ramp exactly where the bound is set, so the joint bound must tighten as well.

Its SIZE is deliberately not quoted. The joint fit carries a gamma_coll prior that
can absorb part of an added Lorentzian width where the width-only fit cannot, so
the tightening will be smaller than C3d's factor 2.8, and by how much is a
property of that fit rather than of this arithmetic. Running it needs the
quarantine trees mounted, which is owner-side work.

Until then C3f stands at 0.26 MHz as quoted, and is conservative in the same
direction C3d is.

**What is still not licensed.** The functional form is the two-level homogeneous
law used with a two-photon Rabi frequency. That is standard and the steady-state
condition holds here, the beam chord being about ten natural lifetimes, but it is
an approximation rather than a derivation for a two-photon transition, and no
committed bound should move on it without that step. **The committed C3d bound
therefore stands at 0.63 MHz and remains conservative**, now by a measured factor
of 2.8 rather than by argument.

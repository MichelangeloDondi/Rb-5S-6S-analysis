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
campaign maximum of 225 mW with the adopted 64 um waist and rho = 0.94, is

    Omega_2ph / 2pi = 450 kHz   on axis

tethered to an already-validated quantity rather than to a fresh normalisation:
the ratio Omega_2ph/2pi to S0 is 1.294 and is field-independent, so the 450 kHz
inherits whatever confidence the 0.348 MHz predicted light shift has.

Against the 3.4925 MHz natural width that is a saturation parameter s = 0.033 on
axis and 0.0146 signal-weighted. The atom reaches steady state, since the 456 ns
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
field. The ratio is **about 3.7**, and it is stable across the waist prior band
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

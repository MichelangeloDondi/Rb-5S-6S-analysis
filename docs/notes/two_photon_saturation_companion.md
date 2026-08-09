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

tethered to an already-validated quantity rather than to a fresh normalisation:
the ratio Omega_2ph/2pi to S0 is field-independent, so the 450 kHz inherits
whatever confidence the predicted light shift has. (Corrected 2026-08-09 on
independent verification: the consistent same-field ratio is 2T/|Delta_alpha|
= 1.237, from `hyperpolarizability.two_photon_matrix_element`, T = 707.75 a.u.
The 1.294 first used here normalised M at one field by the committed predicted
S0 at another convention, 4.6 per cent high, inside the robustness band the
probe scanned. The matrix element itself, M = 225 kHz at the campaign maximum,
was confirmed to 0.04 per cent.)

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

The injected physics is the homogeneous law Gamma to Gamma\*sqrt(1+s) with
s = 2\*Omega^2/Gamma^2, applied with the two-photon Rabi frequency through the
field-independent ratio Omega_2ph/2pi = 1.237\*S0 (as corrected above). Folding the increment into
gamma_coll is exact rather than convenient, because power broadening of a
homogeneous line is Lorentzian and Lorentzian widths add.

| | kappa (MHz/W) | S0(225) bound | chi2_red |
|---|---|---|---|
| production, ramp only | 0.0000 +/- 5.9562 | 0.6325 MHz | 3.7047 |
| with saturation | +0.4490 +/- 1.8196 | **0.2231 MHz** | 3.7599 |

**The bound tightens by 65 per cent**, from 0.6325 to 0.2231 MHz, which is the
direction this note predicted and a larger move than it suggested. The mechanism
is transparent: both models agree at kappa = 0, where S0 and therefore the
saturation increment both vanish, but the with-saturation model broadens faster as
kappa rises, so it reaches any observed broadening at a smaller kappa.

**The other half of the prediction is wrong, and this is the part worth keeping.**
The note said the minimum stays at zero. It does not. Production rails at exactly
kappa = 0 because the width response goes as S0^2 and has no gradient there.
Adding a companion term 3.7 times larger gives the width a resolvable response, so
the minimum un-rails to +0.4490 MHz/W. That is 0.25 sigma from zero and entirely
consistent with no shift, so the substance of the claim survives while its letter
does not. What actually changed is that the parameter stopped being unidentifiable
at the boundary, which is a different and better situation than a railed fit.

The fit quality is untouched, chi2_red moving 3.7047 to 3.7599, as expected when
the added effect is far below the block-to-block scatter that dominates chi2.

**Robustness to the one number not independently re-derived at the time.** The ratio came
from the two-photon matrix element and the lead did not rebuild that sum. The bound
scales roughly inversely with it: 0.3732 MHz at half the ratio, 0.2231 at the
adopted value, 0.1479 at 1.5 times it. So even a factor-of-two error in the Rabi
frequency leaves the bound well below the committed 0.6325, and the qualitative
result is robust while the digits are not.

**What is still not licensed.** The functional form is the two-level homogeneous
law used with a two-photon Rabi frequency. That is standard and the steady-state
condition holds here, the beam chord being about ten natural lifetimes, but it is
an approximation rather than a derivation for a two-photon transition, and no
committed bound should move on it without that step. **The committed C3d bound
therefore stands at 0.63 MHz and remains conservative**, now by a measured factor
of 2.8 rather than by argument.

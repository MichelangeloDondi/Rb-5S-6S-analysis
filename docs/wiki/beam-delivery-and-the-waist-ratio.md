# Beam delivery and the waist ratio

*[wiki index](README.md) · concept*

Why a mode-cleaned delivery turns the beam waist from the record's largest open systematic into a scanned parameter, and why the ratio of two waists is known far better than either one. This page builds on Gaussian beam propagation and on the light-shift distribution of [the AC Stark shift](ac-stark-shift.md). No fitting and no data. It sets out the closed form for the focus behind a single-mode fibre, what cancels in a ratio of two rungs, why one fibre mode makes every rung the same shape, and the two design constraints that decide whether a scan is clean. Not covered here: what the waist is worth once known, which is [identifiability](identifiability.md).

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## The closed form

Place a single-mode fibre after the isolator and the modulator, and collimate
its output. A fibre of mode radius $w_f$ diverges at $\lambda / \pi w_f$, so a
collimator of focal length $f_c$ returns a beam of radius $f_c \lambda / \pi w_f$,
and a focusing lens $f_L$ brings that to

$$w_0 = \frac{w_f f_L}{f_c}.$$

The wavelength has cancelled, and the fibre's divergence with it. The focus is
the mode radius scaled by the ratio of two focal lengths.

## The cancellations in a ratio

Two rungs of a scan differ only in the collimator, so

$$\frac{w_0^{(1)}}{w_0^{(2)}} = \frac{f_c^{(2)}}{f_c^{(1)}}.$$

The mode radius cancels, the focusing lens cancels, the wavelength cancels, and
the beam quality cancels because one fibre mode feeds every rung. What remains
is the ratio of two catalogue focal lengths, known to about one per cent. The
absolute waist still needs the mode radius, the focal length at the working
wavelength and the beam quality, which is why this repository carries it as an
open item and the ratio as a design quantity.

Two camera stations at fixed separations along the collimated beam give the
same ratio a second time, from the measured radius and divergence. The two
routes share no input, so their agreement is a cross-check and not a
restatement.

## The bore's floor, and where a waist gets ruled

On the bench this page is written against, the beam passes a 3 mm clear
aperture before the focusing lens. Solved by diffraction through that bore
rather than by the unclipped Gaussian formula, which does not hold under heavy
truncation, the focal radius reads 79.1 microns at an input radius of 0.6 mm,
51.1 at 1.06, 45.4 at 1.5, 43.3 at 2.0 and 41.4 at 4.0, against 0.0, 1.8, 13.5,
32.5 and 75.5 per cent of the power clipped at those radii.

Two things follow. The focus saturates at 41 to 43 microns whatever is done
upstream, so widening the input buys nothing past that point and costs power
monotonically. And the beam that reaches the floor is the beam that gives up a
third to a half of its power, so the aperture's cost and the waist's value are
one fact and cannot be quoted apart.

That is also why a ruled effective waist in the low forties is no coincidence on
such a bench. It is the bore's own diffraction limit, and a mode-cleaned
delivery removes the floor along with the loss.

## The ratio against the absolute value

The terms of the line divide by how they scale with the waist. The light-shift
scale goes as $1 / w_0^2$, the transit width as $1 / w_0$, and the laser width
and the collisional width do not move. A scan whose ratios are known therefore
separates those four by their scaling and not by their shape, which is what one
lineshape cannot do: the transit and the laser width are degenerate within a
single line, and that degeneracy is why every absolute result in the 2025
record is a bound. Once a scan has separated the transit, the transit's own
form returns the absolute waist from the cell temperature alone.

A power ladder is no substitute. Saturation and depletion both follow the
excitation rate, so they lie on one ray in the drive and no power sweep splits
them. Their ratio goes as the crossing time $w_0 / v$, so the waist splits them
first.

## One mode, one shape, at every rung

A fibre transmits its own mode and nothing else, so every rung presents the
same transverse profile at a different scale. Every dimensionless shape number
of the light-shift distribution therefore takes one value across the whole
scan.
<!-- C6b: re-measured as a moment (A149) -->
For a Gaussian profile the standardised third cumulant is
$-2\sqrt{2}/5$ and the normalised fourth is $-3/5$, both read off the ramp's own
density and checkable from it. A shape number that moves across the scan is a
systematic and can be nothing else.

A truncated beam has no such test. Its focal profile is ringed rather than
Gaussian, its shape numbers sit elsewhere, and they drift as the collimated
radius changes for reasons that have nothing to do with the atoms. Third-order
diagnostics respond several times more strongly than the width to the same
degradation, which is what makes them the sharp probe of the beam and what puts
an uncleaned beam directly in the way of the higher-moment channel.

## Two constraints on a clean scan

The collimated radius goes as $f_c$, so the long rungs present the widest beam
to every surface downstream. A scan stays clean while the widest of them sits
well inside the clear aperture of the focusing lens and of the cell windows.
The shape numbers measure exactly that, so they are read on every rung before
the fit.

The Rayleigh range goes as $w_0^2$ while the imaged length is set by the
collection optics, so the ratio of the two goes as $1 / w_0^2$ and moves by four
across a factor of two in waist. The light-shift distribution's own skewness is
within a few per cent of its thin-window value at a quarter of a Rayleigh
range, has lost most of itself at one Rayleigh range, and changes sign at [1.117](../../results/prediction_band.csv "ref:prediction_band:collection_window:skew_null_z_ratio") Rayleigh ranges. A scan toward tighter waists walks the odd channel into its own null
unless the imaged length is narrowed with it. Holding the imaged length
proportional to $w_0^2$ keeps every rung at one axial mixture.

## Related

[The AC Stark shift](ac-stark-shift.md) for the distribution whose moments this
page keeps invariant, [identifiability](identifiability.md) for what a scan
buys the joint fit, [Doppler-free geometries](doppler-free-geometries.md) for
the retro whose self-imaging form returns the same waist on every rung, and
[designing an acquisition](designing-an-acquisition.md) for where a scan sits
in a campaign.

*Model status:* what the fitter, the twin and the Monte Carlo carry of this page's physics is generated from the registry on [the model terms](../methods/model_terms.md), for `bore_clipping`.

---

[← The beam waist](the-beam-waist.md) · *Experimental spectroscopy, 6 of 12* · [The AC-Stark shift →](ac-stark-shift.md)

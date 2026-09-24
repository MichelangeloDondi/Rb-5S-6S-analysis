# The beam waist

*[wiki index](README.md) · concept*

What the beam waist is, why it stands between a measured power and the intensity an atom feels, and how confidently this repository knows its value. This page is self-contained and sets out the waist's defining relations, its opposite-signed pull on the light shift and the transit width, and the value of record's provenance. beyond the idea of a focused beam, and no fitted data of its own. Not covered here: what the waist does to the line shape, not the length itself, covered in [the AC-Stark shift](ac-stark-shift.md).

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## Definition

A focused beam narrows to a minimum radius before spreading out again. That
minimum, $w_0$, is the beam waist, the radius at which the on-axis
intensity has fallen to $1/e^2$ of its peak. A bare "beam diameter" leaves a
reader guessing between a radius and a diameter, and among three
definitions of "edge".

![Beam radius about the waist, with the Rayleigh range and divergence angle marked](figures/wiki_the_beam_waist.png)

*Beam radius about the waist, with the Rayleigh range and far-field divergence angle marked.*

The waist sets two further lengths through diffraction: the Rayleigh range

$$z_R = \frac{\pi w_0^2}{\lambda}$$

over which the beam stays near $w_0$, and the far-field divergence
half-angle $\theta \approx \lambda/(\pi w_0)$ beyond it. Their product
$w_0\theta = \lambda/\pi$ is fixed: a tighter focus shortens the working
distance and widens the divergence angle by the same factor.

The waist converts a power-meter reading into the intensity that governs
light-matter interaction. For a single pass of power $P$, the on-axis peak
intensity at the waist is

$$I_0 = \frac{2P}{\pi w_0^2}$$

Intensity is what an atom responds to, and $w_0$ is the length that stands
between a measured power and it.

Two standard instruments measure it directly. A knife-edge scan translates a
blade across the beam at several axial positions, fitting the
transmitted-power transition at each to recover $w(z)$, $w_0$ and $z_R$ in
absolute power units. A camera scan images the transverse profile over the
same range, also recovering shape: ellipticity, astigmatism, whether the
profile is Gaussian at all. The two check each other.

## The problem it addresses

Because $I_0 \propto 1/w_0^2$, the waist multiplies every
intensity-dependent quantity by a different power, so the same fractional
uncertainty on $w_0$ propagates by different amounts, even different
directions.

![Monte Carlo transit width against beam waist in the thin-waist limit](../../figures/fig3_transit_mc.png)

*Monte Carlo transit width against beam waist in the thin-waist limit, the calculation whose crossing-flux weighting once put the design value at 32 micron before correction.*

The light shift is linear in intensity, so it runs as $1/w_0^2$. The
two-photon signal is quadratic, because it takes two photons acting
together, so it runs as $1/w_0^4$, and the saturation parameter built from
the same coupling carries the same fourth-power dependence: a tighter focus
stops paying off in signal before it stops paying off in shift, since the
safe regime narrows faster than the gain grows. Transit time runs the other
way: an atom crossing a beam of waist $w_0$ at thermal speed $v$ spends a
time of order $w_0/v$ inside it, so a bigger waist gives a longer transit
and a *narrower* width, opposite in sign to intensity.

A five percent error on $w_0$ becomes roughly a ten percent error on the
light shift, a twenty percent error on the two-photon signal or saturation
parameter, and about a five percent shift in the transit width the other
way. An unresolved waist dominates a two-photon campaign's propagated
uncertainty out of proportion to its own fractional size.

## Application in this repository

[`rb5s6s/constants.py`](../../rb5s6s/constants.py) holds `W0_CENTRAL_M` and
`W0_BAND_M`, the accepted value and working band every $w_0$-dependent
quantity reads from. **This waist is not measured on this bench**, and since owner order O44
(2026-09-21) it is no longer transferred from another one either: it is calculated from this
bench's own aperture geometry. Nor is it recovered from the
line.

The joint fit was closed on its own forward model, injecting a known [52.00](../../results/noiseless_floor.csv "ref:noiseless_floor:injected_truth:w0") µm on the
archive's own axes and levels, and the likelihood prefers **[52.25](../../results/noiseless_floor.csv "ref:noiseless_floor:recovered_w0:nfev_6000") µm at zero noise**, with
$\chi^2$ at the injected truth [16.0](../../results/noiseless_floor.csv "ref:noiseless_floor:chi2_at_injected_truth:nfev_6000") where a self-recovering fit returns zero. The profile is
identical to four decimals at 1200 and at 6000 optimiser iterations, so the fit is converged and
the preference belongs to the model: a parameter set a quarter of a micron above the truth reproduces the injected
data better than the true parameters do. The forward map is not injective over this grid, and w₀ is absorbed
by whatever the refit leaves free.

The transit goes as $1/w_0$, $S_0$ as $1/w_0^2$ and
$\Omega^2$ as $1/w_0^4$, so the compensating term is a nuisance with one of those exponents.
Every waist this estimator reports is conditional on that degeneracy before any noise argument
is reached, which is why the knife-edge settles the question instead of confirming it. The
figure once of record was one profiling of the OIST lineage, reported in both [Rajasree
2020](../lit/rajasree2020thesis.md) and [Nieddu 2019](../lit/nieddu2019.md) in
its $1/e^2$ convention, and taken on the laser generation preceding the one this
campaign used.

The owner retired it as the waist authority on 2026-09-10 and
restated why on 2026-09-15: a different laser source, and a 2025 beam that
additionally passes a 3 mm modulator aperture the profiled beam did not. Both
differences push the effective waist above the transferred value, so the
constant `W0_MEASURED_M` was a carried convention whose own name asserted what its
docstring denied. Owner order O44 (2026-09-21) retires that transfer in turn: the renamed
`W0_CENTRAL_M` now holds **42.38 µm**, this bench's own bore-limited actual focus, calculated
from the EOM's 3 mm bore truncating the input Gaussian ahead of the focusing lens, neither measured
nor transferred from another apparatus (F104, F105, F108, F280).

The campaign did not read the waist off its own beam at its own time. What remains open is no
longer a transfer's own uncertainty, since that question is retired along with the transfer, but
two apparatus facts the calculation still needs: the beam radius at the lens, which the
calculation is comparatively insensitive to but does not pin, and the focus position inside the
cell, which [APPARATUS](../APPARATUS.md) records
as placed near the collection lens with the standoff unrecorded. The 40 to 45 µm band is the
owner's own stated interval around the calculated centre, not a margin computed from a clipping
correction, and the same calculation puts a floor near 41 µm on the actual focus this
bore, lens and wavelength can make for any input radius, so the band's low edge sits close to a
limit the geometry itself may not reach. This is the repository's largest open systematic.

[`docs/big_picture/04_what-2025-delivered.md`](../big_picture/04_what-2025-delivered.md)
reports what the 2025 archive did with the value of record and its band.
[`docs/plan/03_optics-protocol.md` section
4.2](../plan/03_optics-protocol.md#42-two-instruments-for-the-waist)
specifies the knife-edge and camera measurements the next session runs to
replace it with a bench measurement, cross-checked against each other and
the geometric relation $z_R = \pi w_0^2/\lambda$. The fourth-power
saturation dependence is in [`docs/GLOSSARY.md`](../GLOSSARY.md) and [the
saturation companion](../notes/two_photon_saturation_companion.md).

## The pairing a band on the waist requires

The record's widest credible interval pairs the tight-waist edge with the high
retro ratio, since the shift rises with both, and a band that moves the waist
alone at a fixed ratio is a second convention for one quantity. The sweep-rate
producer carried that second convention until 2026-09-08, where it read nine
per cent of the shift against the record's eleven, in the direction that reads
as licence.

## Revised values

The value of record replaced a chain of earlier estimates. First a
design figure, retracted once a missing crossing-flux weighting in the
transit Monte Carlo was found and fixed, which is the same implementation
trap [transit-time broadening](transit-time-broadening.md) names in its
"What can go wrong" section. Then the corrected Monte Carlo figure,
validated against Lehmann's worked example. Then a stand-in used in three
documents before the waist was stated as measured. the private correction record
carries each with its date. Owner order O44 (2026-09-21) replaces that
transfer in turn, with 42.38 µm calculated from this bench's own bore-limited
focus, where it had been transferred from another apparatus (F104, F105, F108, F280). The
account above, of the transfer and why it no longer holds, stays as the
record of that chain's own last link.

## A knowable ratio and an unknowable scale

The waist is hard to measure absolutely and easy to move by a known factor.
An adjustable expander scales it by its magnification, a ratio of focal
lengths, so a ladder of settings has a calibrated abscissa while the absolute
scale stays open. That is worth more than it sounds, because every term of the
model carries a different power of the waist: the collisional and laser widths
none at all, the transit its inverse, the light shift and the two-photon Rabi
frequency its inverse square, and the excitation rate its inverse fourth power.
A fit across settings therefore measures the absolute scale from the line
itself, twice over and by two different powers, where a single setting has to
take it from a knife edge.

Two things move with the knob that are easy to forget. The Rayleigh range goes as the
waist squared, so the detector's fixed axial window covers a different fraction of the
beam at every setting, which changes the shape the light shift imprints and can reverse
the sign of its asymmetry ([the AC-Stark shift](ac-stark-shift.md)). And the collected
signal follows the arctangent of that same ratio, so tightening the beam buys far less
signal than the inverse square suggests, about five for a fourfold tightening where the
inverse square would give sixteen.

The peak height rises too, by about three over the same span, because the line broadens
by well under a factor of two: the transit is only about a fifth of the composite width
at these conditions. It is the light shift's own growth that eventually turns the peak
height over, at a waist inside the range the campaign proposes. [The ramp
chapter](../methods/03_the_ac_stark_ramp.md) derives both.

## The drive wavelength as a knob on the waist

The expander's magnification is not the only knowable ratio. The focused
waist through a lens is

$$w_0 = \frac{\lambda f}{\pi w_{\rm in}}$$

with $w_{\rm in}$ the beam radius arriving at the lens, so **the waist is
linear in the drive wavelength** at a fixed lens and a fixed input beam. A
campaign that retunes the laser to another two-photon line moves the waist
whether or not anyone touches the optics: through this bench's f = 150 mm lens
the 42.38 µm calculated at 993.4 nm becomes 32.17 µm at 760.1 nm and 32.96 µm at
778.1 nm, and the light shift, going as the inverse square, is larger by 1.74
and 1.65 at the same power. `rb5s6s.constants.waist_at_drive` computes it and
`tests/test_drive_waist.py` guards it.

Two smaller terms ride along and one open question dominates. The lens is a
singlet, so its own focal length disperses as $1/(n-1)$, worth 150.00 mm at
993.4 nm against 148.83 at 760.1, under a per cent. It is the same to within
0.02 mm whether the glass is fused silica or N-BK7, so the reading does not
turn on a fact the record lacks. The focus also moves 1.17 mm toward the lens,
a fixed lens property the 2026-09-21 recalculation does not touch, which at the
archive's now smaller central waist is about a quarter of a Rayleigh range, where it read
an eighth at the retired, larger convention. That still leaves the waist itself only weakly perturbed, but it is now a larger fraction of the collection window, so the
collection optics are refocused per wavelength or the axial-window correction is wrong by that
much, more so than before.

That
fraction read a fourteenth until 2026-09-10, when this page corrected it to compare against the
destination wavelength's own, smaller Rayleigh range and not the source's, which is what
1.17 mm is against the 760 nm rung's own range. At the archive's calculated 42.38 µm the
993.4 nm range is 5.68 mm and the 760 nm rung's own 32.17 µm range is 4.28 mm, both far smaller
than the 16.93 and 9.758 mm the retired, larger convention gave, which is why the same fixed
1.17 mm focal shift now costs proportionally more.

**What is not known is $w_{\rm in}$**, and it is the term that decides how big
the effect is. If the input beam is clipped by a fixed stop it is common to
every drive and the waist follows $\lambda$. If it is an unclipped
fixed-geometry resonator mode its radius follows $\sqrt{\lambda}$ and the
waist does too. The two regimes differ by 31 per cent in the light shift at
760 nm, and that spread is the ratio of the two scaling laws, so it does not
depend on which waist anchors it. **The line itself settles it**: the
transit width carries the same geometry to the first power, so the transit
ratio between two drives is 1.317 in one regime and 1.152 in the other, a
14 per cent separation the width precision resolves. A cross-transition ratio
quoted without that measurement carries an unstated beam assumption, which is
what happened here until 2026-09-09.

## Failure modes

The commonest error is a convention trap, not a measurement error: a bare
"diameter" with no $1/e^2$ stated, a $1/e^2$ diameter halved incorrectly, or
a $1/e$ width read as $1/e^2$, each hiding a factor of two or worse inside
one adjective, costing nothing to check since the source always states it.

A second is a model failure: a value measured once, treated as monitored.
Every quantity computed from it inherits whatever changed since, on top of
the quoted band, understating every downstream result.

A third: the transit width and the laser width broaden the same line and
exchange against each other in a fit, so a spectroscopic line alone
under-determines the waist behind its transit contribution. Only an
external, spatially resolved measurement settles it.

Fourth, an instrument trap, and the reason the two measurements run
together, not singly. A knife-edge integrates away the beam's
two-dimensional shape, so a clipped or structured profile can return a
confidently wrong waist. A camera keeps the shape but struggles at the
opposite end, undersampling a small spot and losing the faint wings a
power-based measurement needs to the same gain that keeps the peak off
saturation. Agreement between the two, and with the geometric $z_R$
relation, is the actual check.

Fifth, a drift trap: a measured waist can move between measurement and
data-taking if a lens position creeps. Intensity depends on the waist
quadratically, so a small mechanical shift moves every intensity-dependent
number more than it moves a caliper reading, so lens separations are worth
checking at setup and teardown, not trusted for a whole campaign.

## Try it

`rb5s6s.constants` holds the waist of record and its working band. Since
intensity runs as $1/w_0^2$, walking across the band shows directly how much
the light-shift prediction moves for a fixed power.

```python
from rb5s6s.constants import W0_CENTRAL_M, W0_BAND_M, RHO_RETRO
from rb5s6s import stark_shift_S0_mhz

power_w = 0.225  # 225 mW, the top of the 2025 campaign's power sweep
w0_lo, w0_hi = W0_BAND_M

print("rb5s6s.constants.W0_CENTRAL_M and W0_BAND_M:")
for label, w0 in (("band low", w0_lo), ("central", W0_CENTRAL_M),
                  ("band high", w0_hi)):
    intensity_ratio = (W0_CENTRAL_M / w0) ** 2
    s0_mhz = stark_shift_S0_mhz(power_w, w0, rho=RHO_RETRO)
    print(f"  {label:>9}: w0 = {w0 * 1e6:5.1f} um   "
          f"I / I(central) = {intensity_ratio:6.3f}   "
          f"S0(225 mW) = {s0_mhz:.4f} MHz")
print("intensity and the light shift both run as 1/w0^2: the same band "
      "moves both by the same fraction")
```

## Further reading

- [`../lit/rajasree2020thesis.md`](../lit/rajasree2020thesis.md), the
  thesis carrying the same-bench measurement this repository's waist of
  record is read from.
- [`../lit/nieddu2019.md`](../lit/nieddu2019.md), the earlier paper on the
  previous laser that quotes the same beam diameter, kept for lineage. The
  source measurement is Rajasree 2020.
- A. E. Siegman, *Lasers*, University Science Books (1986), the standard
  reference for Gaussian-beam propagation, the Rayleigh range and the
  divergence relation used above.
- [The AC-Stark shift](ac-stark-shift.md) for the effect the waist sets the
  scale of.
- [Transit-time broadening](transit-time-broadening.md) for the width that
  depends on the same length with the opposite sign.

## Related pages
- [The campaign page](../quantities/campaign.md), where the waist is the hub
  of the coupled system.
- [The AC-Stark shift](ac-stark-shift.md) for the shift distribution this
  length's intensity feeds directly.
- [Saturation](saturation.md) for the fourth-power waist dependence that sets
  the safe operating regime.
- [Sensitivity analysis](sensitivity-analysis.md) for how much a projection
  actually moves when an input like the waist is varied.

---

## The waist as the worst-conditioned self-calibrated quantity

**Added 2026-09-11 on the owner's reading.** Every other nuisance on this bench
is read from the trace that carries the signal: the frequency axis and the
scan's own non-linearity from the comb, the temperature from the Doppler
pedestal, the density from the collisional width, and the depth and the drift
from the centres and their order. **Two more are designed and not yet taken**,
and they belong on this page as designs: a field read from the Zeeman splitting
in the same scan, and the laser's own noise read from a ladder of scan rates,
which the acquisition chapter proposes and the archive does not carry.

**The geometry joins the list as a design too.** The same architecture can be
applied to the last input still taken on trust, by scanning the waist and
refitting the archive at each value instead of importing a lineage number.
**That producer is not in this repository**: it was written and withdrawn on
2026-09-11, because the composite it scans carries no light shift and its
default sharing lets a free laser width absorb the temperature lever, so a
profile from it would have had to be retracted.

And it is graded, because the grade is the useful part. The other
calibrations are well conditioned. This one is read through kernel shape, and
three things make that weak here:

* the kernel is the record's own known defect, a measured Lorentzian laser
  component the archive's fits do not carry,
* three width terms depend on the waist and are missing from the model: the
  ramp's own width and the saturation companion, which both add and both go as
  the inverse fourth power of the waist, and the transit's axial average over
  the collected window, which subtracts because the fit passes the value at the
  waist while the collected line averages a wider beam. Their net is a partial
  cancellation and not a bias,
* the one channel a shared laser width cannot absorb is the isotope
  differential, and it is read by comparing peaks, which is exactly what was
  taken at different vertical zoom.

The model also assumes a perfect Gaussian, which the apparatus note denies in
the same paragraph that states the waist: the lineage profile carried NO 3 mm
aperture while this campaign's beam passes one, and a truncated Gaussian carries
ring structure and does not obey `w0 = lam f / (pi w_in)`. Computed through this
bore the focus is floored near 42 µm and not widened (F105), which is why the
owner's own reading of 2026-09-17 is 40 to 45 µm.

Beam quality above
one is no longer absent: `rb5s6s/beam_field.py` propagates the truncated input
through the bore and the drive lens as a scalar angular spectrum, with $M^2$
entering as the mode content of the input beam and not as a factor on the focus,
and `scripts/run_kernel_mc.py` samples every atom's chord in that field. What
remains absent is astigmatism and the retro overlap. The transit reads an
effective radius and the light shift reads a peak intensity, so for a
non-Gaussian beam the two are not related by one waist at all.

### Beam quality behind a hard aperture

A beam-quality factor does not multiply this waist, and the arithmetic says why. The
bore-limited 42.4 µm already contains the aperture's 2.2-fold widening of the 19.3 µm
the same input gives unclipped, so writing $w_0 = 42.4 M^2$ counts the aperture twice.
More than that, $M^2$ does not fix the focus here at all, and the composition matters
more than the number. Three mixtures reaching one $M^2$ of 3.00 exactly give three
different focal radii: nine parts Gaussian to a high-order $LG(10)$ halo focuses to
42.32 µm, indistinguishable from an ideal beam.

Three parts Gaussian to one of $LG(4)$ gives 45.79, and the plain $LG(0)+LG(p_1)$
mixture, which at this $M^2$ is pure $LG(1)$, gives 48.31. The first two are the
physically plausible pair and they differ by 8.2 per cent. The whole family spans 14.2,
on a ruled band only 10.0 per cent wide. Two spans answering two different questions,
and neither corrects the other. Which mixture a real beam carries is not on record, so
the pure $LG(1)$ end is an assumption and not a measurement.

The bore also costs power, and the bench now settles that half instead of spanning it.
**The recorded power is read after the modulator**, so the transmitted fraction divides
out of the light shift per recorded watt and is not a systematic on it at all, and only
the focal radius matters. What the same measurement buys instead is a constraint on the
mode content, which nothing else here constrains. The drop through the modulator is
about 60 per cent of roughly a watt, and every non-clipping loss in that path reduces
the total further, so the bore's own transmission is bounded from below by the measured
one and not equal to it.

Read that way the measurement is a joint statement about the input radius and the halo:
a pure $LG(1)$ input, which is what this record's own mixture becomes at $M^2 = 3$,
passes about a quarter of its power at any input radius from 1.6 mm up, which is less
than the measurement's own lower edge. It survives only for an input radius near 1.2 mm,
and there an ideal Gaussian would pass more than nine tenths, so nearly the whole drop
would have to be something other than clipping. That is the opposite of the bench's
reading that clipping is most of it. So the pessimistic end of the span above is
disfavoured by a measurement, and is not excluded outright.

The mechanism is aperture filling, not radial structure. A first reading here
attributed the widening to an $LG(1)$ node falling inside the bore, and that is
refuted: its only zero sits at 1.764 mm against a bore radius of 1.50.

So the claim is the architecture and not the number. This apparatus carries
its own metrology for every nuisance including the geometry, and the geometry
is the one where the conditioning is poor. That says which calibration to
improve and by how much: a knife edge good to a few per cent, one afternoon,
no atoms and no lock. **For a new campaign it is a design instruction**, since
several measured waists, the acquisition factorial that already separates
drift, laser noise and the axis, and a vertical zoom held constant across the
peaks would turn the worst-conditioned self-calibration into an ordinary one.

[← Transit-time broadening](transit-time-broadening.md) · *Experimental spectroscopy, 5 of 12* · [Beam delivery and the waist ratio →](beam-delivery-and-the-waist-ratio.md)

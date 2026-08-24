# Glossary

*Every term and symbol this repository uses, in one place, defined for someone
meeting the work for the first time. Each entry says what the thing is, and
then where it is derived or measured, so this page is a set of doors rather
than a substitute for the chapters. If you are new here, read
[START_HERE.md](../START_HERE.md) first and keep this open beside it.*

Nothing on this page is a result. Numbers appear only where they are part of
the definition, and each one is read from the module or CSV named beside it.

## The measurement, in six sentences

Rubidium vapour in a sealed glass cell is warmed until enough atoms are in the
way. A 993 nm laser is sent through the cell and reflected straight back on
itself, so an atom sees two beams head on. An atom can absorb one photon from
each beam at once and climb from its ground state, 5S, to a higher state, 6S,
in a single step that never passes through a real level in between. Because the
two photons arrive from opposite directions, an atom's motion shifts one of
them up and the other down by the same amount, so the pair adds to the same
total whatever the atom's speed. The excited atom falls back down through 5P
and emits 795 nm light, which a detector counts. Sweeping the laser across the
resonance and recording that light is one **trace**, and every number in this
repository comes from the shape of those traces.

> **Want the full treatment of a term?** The [wiki](wiki/README.md) has one
> page per concept, method, effect and technique: the general theory, where
> this repository uses it, and how it fails. This page stays the quick
> lookup.

## Words for the physics

**Two-photon transition.** An excitation that takes two photons at once. The
signal grows as the *square* of the intensity, because each photon contributes
one factor, and that square is what gives the light-shift distribution its
usable shape ([methods 3](methods/03_the_ac_stark_ramp.md)). Full page: [doppler-free-two-photon](wiki/doppler-free-two-photon.md).

**Doppler-free.** The property above: because the two photons come from
opposite directions, the first-order Doppler shifts cancel and the line is not
smeared by the atoms' thermal motion. It is the reason a hot cell can give a
line a few MHz wide instead of a few hundred. Full page: [doppler-free-two-photon](wiki/doppler-free-two-photon.md).

**Transition axis and laser axis.** The transition is driven by two photons, so
the transition frequency is exactly twice the laser frequency. Every frequency
in this repository is on the **transition axis** unless its name ends in
`_LASER`. Mixing the two silently is the easiest mistake to make here, and it
is worth checking any number that looks off by a factor of two
([START_HERE](../START_HERE.md) section 3).

**Natural width, $\Gamma$.** The linewidth an isolated, motionless atom would
have, set by how long the excited state lives. For 6S it is 3.4925 MHz FWHM
(`rb5s6s.constants.GAMMA_NAT_HZ`), which is about two thirds of the observed
line. Everything above it is apparatus
([fig26](../figures/fig26_lineshape_kernels.png)).

**FWHM.** Full width at half maximum, the width of a line measured between the
two points where it has fallen to half its peak. All widths here are FWHM
unless said otherwise.

**The four peaks.** The 5S and 6S states each split into two levels by the
interaction with the nucleus, and rubidium has two isotopes, so the one
transition appears as four lines. They are named by wavelength: 993.4121 and
993.4207 nm are the two ⁸⁷Rb components, 993.4154 and 993.4192 nm the two ⁸⁵Rb
ones. Each pair is separated by 430 times the observed linewidth for ⁸⁵Rb and
973 times for ⁸⁷Rb, computed from those wavelengths, so they are four separate
lines rather than one broadened one.

**$F$, the hyperfine quantum number.** Which of those split ground levels an
atom is in. It matters because the 5P decay does not preserve it, so an atom
that decays while crossing the beam can land in the other one and leave the
line for good ([fig23](../figures/fig23_hyperfine_pumping.png)).

## Words for the things that broaden the line

**Kernel.** One contribution to the line's shape, drawn as a curve. The
observed line is all of them convolved together, which means each one smears
the others ([methods 2](methods/02_the_lineshape.md)).

**Collisional self-broadening, $\beta_\text{self}$.** How much wider the line
gets per unit of rubidium density, because atoms perturb each other. Measured
in MHz per 10¹² cm⁻³. This record reports a **bound** on it and explains why
([RESULTS.md](RESULTS.md) C1). Full page: [self-broadening](wiki/self-broadening.md).

**Transit broadening.** An atom crosses the beam in a finite time, and a wave
observed for a finite time cannot have a sharp frequency. Its kernel is a
two-sided exponential with a cusp at the centre, not a Gaussian, and that cusp
is the only thing that lets a fit tell it apart from the laser's own width.

**$\sigma_\text{laser}$.** The laser's own linewidth. It enters the transition
twice, once per photon.

**Radiation trapping.** At high density an emitted 795 nm photon can be
reabsorbed and re-emitted many times before escaping. It changes how much light
reaches the detector but not the shape of the line, because it is the same at
every point of a frequency scan ([methods 4](methods/04_the_composite_model.md)).
The same chapter checks the other two radiation fields in the cell, the trapped
infrared of the cascade itself and the cell's own thermal glow, and finds both
too small to matter here.

**Occupation number.** How many photons a thermal field puts in one mode at a
given wavelength. It is what decides whether the cell's own heat can drive a
transition, and it falls off exponentially as the transition moves away from
where the heat is. Here it runs from $10^{-6}$ on the longest line of the
cascade to $10^{-20}$ on the detected one, which is why thermal light does
nothing at all ([fig27](../figures/fig27_radiation_environment.png)).

**Escape factor.** The chance that a photon emitted inside the vapour gets out
without being reabsorbed. Below an optical depth of about one it is close to
one and trapping can be ignored. Above it, the photon random-walks to the wall,
and what matters for the shortest way out is the distance to the nearest window
rather than the cell's radius ([methods 4](methods/04_the_composite_model.md)).

**The branching fraction, $f$.** How often an atom that decays mid-flight lands
in the ground level that is not being driven, so it is lost from the line rather
than returned to it. It is a different number for each of the four lines, 0.372
down to 0.223, and it is the only thing in the width budget that differs between
them. Everything else that grows with power grows the same on all four, which is
why $f$ is the one handle that could tell those effects apart
([fig23](../figures/fig23_hyperfine_pumping.png)).

**Saturation parameter, $s$.** How hard the atom is being driven, as a number.
Small $s$ means the weak-driving formulas hold. It grows as the fourth power of
the inverse beam waist, which is why a tighter focus leaves the weak-field
regime faster than it gains signal
([fig24](../figures/fig24_weak_field_limit.png)).

## Words for the light shift

**AC-Stark shift, or light shift.** Intense light moves atomic energy levels,
so the drive laser shifts the very transition it is measuring. This is the
central difficulty of the whole method and the quantity the dataset bounds. Full page: [ac-stark-shift](wiki/ac-stark-shift.md).

**$S_0$.** The size of that shift for an atom sitting at the brightest point of
the beam, at a stated drive power. Quoted here at the campaign maximum of
225 mW.

**The ramp.** Atoms sit at every brightness in the beam, not one, so they do
not all shift by the same amount. The distribution of shifts across the atoms
has a closed form, a triangle running from zero to $S_0$, and that triangle is
the "ramp". It exists in this shape *because* the signal goes as the square of
the intensity ([methods 3](methods/03_the_ac_stark_ramp.md),
[fig12](../figures/fig12_ramp_construction.png)).

**$\kappa$ (kappa).** The AC-Stark coefficient, defined by $S_0=\kappa P$ with
$P$ the drive power. Bounding $\kappa$ is bounding the light shift.

**$\Delta\alpha$, the differential polarizability.** The atomic property that
sets how big the light shift is. Calculated rather than measured here, and its
*sign* is under an open disagreement that no result here depends on
([THEORY_NOTE](THEORY_NOTE.md) section 5).

**Skewness, $g_1$, and the third cumulant $\kappa_3$.** Numbers describing how
lopsided a distribution is. The ramp is lopsided in a calculable way, so
measuring the line's lopsidedness is a way to measure the light shift without
needing to know where the line's centre is. That is the method this repository
is built around, and in the 2025 data the effect sits below the noise. Full page: [third-cumulant](wiki/third-cumulant.md).

**The centre channel, or the pull.** The other way to measure a light shift:
watch the line's centre move as the power changes. It needs a frequency
reference that holds still, which the 2025 lock did not, so this dataset cannot
use it ([notes](notes/centre_channel_cannot_be_revived.md)).

## Three things that make the light shift hard to measure

Worth knowing before reading any bound, because all three shape how the numbers
are quoted. [BIG_PICTURE §1.3a](BIG_PICTURE.md) gives them in full.

**Saturation stops the square law.** The signal grows as the square of the
intensity only while the drive is weak, and the saturation parameter says how
weak. It grows as the fourth power of the inverse spot size while the shift
grows as the second, so a tighter focus leaves the safe regime faster than it
gains signal.

**Hyperfine pumping removes atoms mid-flight.** An excited atom returns through
an intermediate level whose decay does not preserve which half of the ground
state it lands in. Land in the wrong half and the atom is off resonance by
hundreds of linewidths, so it is gone rather than detuned. Between 8 and 15 per
cent of atoms crossing the beam decay at least once, signal-weighted to
on-axis. Of those decays only a share lands in the wrong half, so the fraction
actually pumped out is the smaller 2 to 6 per cent. The two numbers are
separately derived in
[the saturation companion](notes/two_photon_saturation_companion.md).

**All three broaden the line identically.** The light shift and both effects
above grow as the square of the power and as the fourth power of the inverse
spot size, so no sweep this dataset can run separates them. Only the line
centre does, because the two companions broaden without moving the line. That
needs a lock that holds still, which is why the light-shift results here are
bounds and are quoted as loose by a stated factor.

## Words for the apparatus

**The cell.** The sealed glass tube of rubidium vapour, about 25 mm across and
100 mm long, warmed in an oven. Warmer means denser
([APPARATUS.md](APPARATUS.md)).

**Beam waist, $w_0$.** The radius of the laser beam at its narrowest. Measured
here at 64 µm (`rb5s6s.config.W0_MEASURED_M`). Almost every intensity-dependent
number rides on it.

**Rayleigh range, $z_R$.** How far along the beam you can go before it has
spread appreciably. The ratio of the observed region to this length decides
whether the skewness above comes out positive or negative.

**$Z_c$, the collection half-length.** How much of the beam the detector
actually sees, along the beam direction.

**Retro, and the retro ratio $\rho$.** The mirror that sends the beam back
through the cell, and the fraction of the power that comes back. The two beams
interfere into a standing wave, and the shift and the excitation rate take
*different* combinations of the two arms
([fig25](../figures/fig25_retro_combination.png)).

**The lock.** The electronics that hold the laser at a fixed frequency. In 2025
it was misconfigured, so the line's absolute position wandered and was
re-centred by hand between blocks. This is the defining limitation of the
dataset ([fig11](../figures/fig11_laser_history.png)).

**EOM, the ruler, teeth, the comb.** An electro-optic modulator puts sidebands
on the laser at a frequency known to the accuracy of a radio source, 6.25 MHz
on the laser axis (`rb5s6s.constants.TOOTH_SPACING_LASER_HZ`). Those sidebands
appear as evenly spaced spikes, the "teeth" of a "comb", and they convert the
oscilloscope's time axis into a frequency axis. This is the **ruler**
([methods 5](methods/05_the_frequency_ruler.md),
[fig8](../figures/fig8_ruler.png)).

## Words for the data

**Trace.** One recorded sweep across the resonance, 2000 points.

**Condition.** One combination of settings: which peak, what temperature, what
power. Several traces are usually taken at each.

**Block.** A run of traces taken together without touching the apparatus.
Scatter *between* blocks is much larger than scatter within one, and that fact
governs most of the uncertainty analysis here.

**Epoch.** A run of traces sharing one oscilloscope horizontal setting, which
is the best available proxy for the lock not having been touched.

**The sessions, named by date.** The **campaign** is the 24 hour run of 17 to
18 July 2025 and the main dataset, and its manifest is committed here in every
copy of the repository. The **campaign-morning session** of 17 July
commissioned the frequency ruler and took its own four-power sweep, and the
**4 July evening session** carries an independent power dependence at an
internal 130 degrees C. Some fits use all three. The raw files of the two
earlier sessions stay outside the repository in every copy, with the committed
CSVs as the record for them. DATA.md section 0 names all four sessions,
including the 4 July first trials that fix the start of the clock. Whether the campaign's own traces sit beside
the manifest depends on the copy you are reading, and
[data_raw/README.md](../data_raw/README.md) says which this one is
([DATA.md](DATA.md)).

**Module, M0 to M38.** One analysis stage, with its script, its result file and
its tests. The map is [methods.md](methods.md).

## Words for how claims are made

**Bound.** A statement that a quantity is smaller than some value, at stated
confidence. Most headline results here are bounds rather than measurements, and
the reasons are stated rather than implied ([CLAIMS.md](CLAIMS.md)).

**Null.** A statement that a looked-for effect was not found, with the size it
would have had to have to be seen.

**Profile likelihood.** The preferred way of building a bound here: scan the
parameter, refit everything else at each step, and take the edge where the fit
quality has degraded by an agreed amount. Its alternatives, and when each is
valid, are in [UNCERTAINTY.md](UNCERTAINTY.md) section 4. Full page: [profile-likelihood](wiki/profile-likelihood.md).

**Over-dispersion, $\chi^2_\text{red}$.** A measure of the data scattering more
than its own error bars allow. Where it exceeds one, the bounds here are
widened by it rather than quoted as if it were one.

**Preregistration, and addenda.** Predictions and criteria written down
*before* the analysis was run, and a dated, append-only record of everything
later withdrawn, corrected or downgraded. Thirty addenda so far
([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)).

**Status codes.** Every row of every result file carries one word saying what
kind of number it is, from a closed vocabulary: MEASURED, BOUND, NULL, CALIB,
ENVELOPE, PRELIM, DIAGNOSTIC, ARTIFACT. The meanings are in
[UNCERTAINTY.md](UNCERTAINTY.md) section 2.

**Provenance tag.** The same idea for physical inputs: every constant says
where it came from and how much it can be trusted
([UNCERTAINTY.md](UNCERTAINTY.md) section 1).

---

Missing a word? It belongs here. The test that keeps this page honest is that
every link above resolves, which `tests/test_docs_links.py` checks.

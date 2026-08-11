# Two geometry choices for the fixed-lock session: a running wave, and the waist

Status: DESIGN, recorded 2026-08-09. Nothing here is a result and no committed
number changes. Both calculations are in `scripts/run_geometry_design.py`, which
writes nothing, and both are reported with the first pass that was wrong beside
the answer, because in each case the error was the interesting part.

**The question.** Two geometry choices for a future session: should one arm be
frequency-shifted so the fringes run, and how tight should the focus be?
**Takes.** [methods/03_the_ac_stark_ramp.md](../methods/03_the_ac_stark_ramp.md).
**Gives.** Both designs computed, each with the first pass that was wrong
printed beside the answer, because in both cases the wrong criterion was the
obvious one.
**Skip if.** You want the archival result rather than the next session's
design.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

The two questions come from the same worry. The ramp skew is the observable that
would turn the light-shift bound into a coefficient, and two features of the
present geometry attack it: the standing wave leaves a fringe-resolved tail that
suppresses the skew, and the small waist that would make the skew large also
changes the physics the skew is computed from. One design idea addresses each.

## Design 1: shift one arm in frequency so the fringes run

Put an acousto-optic modulator in the retro arm, offset by Delta. The
interference pattern then moves at Delta lambda / 2 instead of standing still, an
atom sees its intensity modulated, and the fringe averages away. The point of
doing it is specific: the shift carries a fringe cross term while the
Doppler-free coupling does not, so the fringe hurts the shift channel and nothing
else, and removing it removes a nuisance parameter from exactly the observable
the method rests on. `hyperpolarizability.two_photon_rabi_hz` states that
asymmetry and why it holds.

### The criterion is thermal, not spectroscopic, and the first pass got it wrong

The first pass chose Delta = 80 MHz, on the grounds that it is 23 natural widths,
so no atom can follow the modulation. That is necessary and not sufficient, and
choosing on it alone is a mistake worth recording, because the resulting design
does almost nothing.

A frozen fringe is not a slow modulation. It is a resonance between the atom and
the pattern. The fringe phase an atom sees advances at 2 k v_z minus Delta, so
offsetting Delta does not remove the frozen-fringe class: it MOVES it, from
v_z = 0 to the co-moving speed v_fringe = Delta lambda / 2. What decides whether
that helps is how many atoms sit at the new speed, which makes the criterion
thermal:

**v_fringe has to outrun the axial thermal spread, not the linewidth.**

At 130 C the one-dimensional rms axial speed is 196 m/s, so Delta must clear
2 sigma_v / lambda = 395 MHz. The Maxwell-Boltzmann weight at the co-moving speed
is the fraction of the frozen-fringe population that survives:

| Delta | v_fringe | in units of sigma_v | population still frozen | laser-axis offset | ruler teeth |
|---|---|---|---|---|---|
| 40 MHz | 20 m/s | 0.10 | 0.995 | 20 MHz | 3.20 |
| **80 MHz** | 40 m/s | 0.20 | **0.980** | 40 MHz | 6.40 |
| 200 MHz | 99 m/s | 0.51 | 0.880 | 100 MHz | 16.00 |
| 400 MHz | 199 m/s | 1.01 | 0.599 | 200 MHz | 32.00 |
| 800 MHz | 397 m/s | 2.02 | 0.129 | 400 MHz | 64.00 |
| 1600 MHz | 795 m/s | 4.05 | 0.000 | 800 MHz | 128.00 |

So the 80 MHz design removes 2 per cent of the effect it was proposed to remove.
A third of the population is still frozen at 400 MHz. Genuine suppression starts
around 800 MHz, which is a different piece of hardware: one high-frequency
device, or two ordinary ones in series, not a spare 80 MHz modulator.

### What survives, what does not, and one thing that has to be redesigned

What survives is the physics. At a Delta that clears the thermal spread the
fringe mean becomes exact for every velocity class rather than for the fast ones
only, and the Doppler-free rate is untouched, because the rate's
wavevector-cancelling term is the product of the two arm amplitudes and carries
no spatial dependence at all. The Doppler-free property survives too: at 800 MHz
the two arms differ fractionally by 2.7e-6, leaving 1.2 kHz of residual
first-order Doppler against a 3.49 MHz natural width.

Two claims from the first pass do not survive.

*The ruler aliasing is not automatically clear.* The resonance moves by Delta / 2
on the laser axis, and 400, 800 and 1600 MHz all land on exact integer multiples
of the 6.25 MHz tooth spacing, because 6.25 divides them. A working Delta has to
be detuned from the harmonic deliberately: 810 MHz gives 64.80 teeth, which is
5 MHz clear of the nearest one. The 80 MHz case was quoted as safe at 6.40 teeth,
which is only 2.5 MHz from tooth 6, about 1.4 laser-axis linewidths.

*The retro ratio was already going to be measured without this.* The first pass
claimed the geometry makes rho measurable and retires a separate task. It does
not: `docs/PLAN.md` items at section 3 and section 4.2 already measure rho in the
metrology afternoon with a pick-off, cross-checked against the Doppler-pedestal
area ratio, and no modulator is involved. What the running wave adds is a
different and better measurement rather than a first one, because a heterodyne
beat between the two arms reads the MODE-OVERLAP-WEIGHTED rho, which is the
quantity that actually enters the shift, where a power-meter ratio reads the
power. That is worth having, but it is an improvement on a planned measurement,
not a replacement for a missing one. The same correction applies to the pedestal:
the two same-beam pedestals do split by plus and minus Delta about the
Doppler-free peak, but each is about 931 MHz wide, so at any Delta below a
gigahertz they stay blended.

*And the retro is self-imaging, so a modulator cannot simply be inserted.* The
present arm maps the cell waist through a second lens to an intermediate waist
and time-reverses it on a flat mirror at that flat wavefront. A single-pass
diffracting element in that path sends the beam back at an angle and it does not
retrace, which is the standard reason frequency-shifted retroreflectors are built
double-pass, with a cat's eye and a quarter-wave plate. So this design is a retro
REBUILD, not an insertion, and the rebuild costs the double-pass loss on top of
the modulator's own.

### Where that leaves it

The idea is sound and the implementation in the first pass was not. As a design
it is worth carrying at 800 MHz or above, in a double-pass arm, with Delta chosen
off the ruler harmonics, and its value stated as making the fringe mean exact and
the shift channel clean rather than as making rho measurable. As a cheap
insertion at 80 MHz it should not be built, and the reason is one number in the
table above.

## Design 2: the waist, and the regime the record is actually in

Small waist raises the shift as one over the waist squared, and the skew grows as
the shift cubed, so the pull is strong. Three things push back. The axial average
over the collection region suppresses the skew and then reverses its sign,
crossing zero at Z_c/z_R = 1.12. Transit broadening grows as one over the waist.
And **saturation**, which the first pass ignored, and which turns out to be the
one that decides the answer.

The saturation parameter goes as the fourth power of one over the waist, so it
runs away: 0.033 at 64 um becomes 0.53 at 32 um and 8.5 at 16 um, all at 225 mW.
That matters because the ramp law weights each shift by the signal it produces,
and the two-photon signal goes as intensity squared only while the drive is weak.
Where saturation is large the weight flattens, the effective exponent falls toward
one, and the transverse skew vanishes at exactly n = 1 by `lineshape.py`'s own
statement. So the committed axial machinery, which assumes an unsaturated
intensity-squared weight, is being asked a question outside its range.

Integrating the moments with the saturated weight instead, at 225 mW and the
2.0 mm collection half-length `config.py` documents:

| w0 | Z_c/z_R | saturation | S0 | skew, saturated | skew, weak-field | width | figure of merit |
|---|---|---|---|---|---|---|---|
| 64 um | 0.15 | 0.033 | 0.348 MHz | +0.545 | +0.555 | 5.40 MHz | 1 |
| 48 um | 0.27 | 0.105 | 0.618 MHz | +0.516 | +0.546 | 5.86 MHz | 5 |
| 40 um | 0.40 | 0.217 | 0.890 MHz | +0.462 | +0.517 | 6.27 MHz | 13 |
| 32 um | 0.62 | 0.531 | 1.390 MHz | +0.294 | +0.393 | 6.96 MHz | 24 |
| 24 um | 1.10 | 1.678 | 2.472 MHz | -0.191 | +0.007 | 8.27 MHz | 54 |
| 16 um | 2.47 | 8.496 | 5.561 MHz | -1.067 | -0.358 | 11.27 MHz | 1100 |

The figure of merit is the shot-noise-limited significance of the third cumulant,
the cumulant over the cube of the observed width times the square root of the
collected signal, relative to the present waist. The width now includes the
saturation increment, without which the deeply saturated rows are flattered.

### Three results, in order of consequence

![the weak-field limit and what leaving it costs the predicted skewness](../../figures/fig24_weak_field_limit.png)

*The table above, in two panels, redrawn from this note's own `ramp_moments`.
Left is why the weak-field assumption fails at a tight focus rather than at a
high power: the saturation parameter carries the two-photon Rabi frequency
squared and so grows as the fourth power of the inverse waist, while the shift
grows only as the second, and the limit is left long before the shift becomes
large. Right is the last two columns of the table as a curve.*

**The weak-field skew is wrong by a factor of three at the waist the record plans
to use.** Read the two skew columns together. Saturation shrinks the skew where it
is positive and grows it where it is negative, because flattening the weight
lowers the effective exponent, the transverse contribution dies at n = 1, and what
survives is the axial term. At 16 um the prediction moves from -0.358 to -1.067.
The small-waist session is written around 16 um, so this is not a remote regime:
it is a factor-of-three error in the headline prediction for the planned
measurement, and it comes from a modelling assumption rather than from an input.

**A smaller waist buys no shift at all on its own, and the identity says so.** At
matched intensity the shift is identical at every waist: 0.348 MHz at 64 um and
225 mW, at 32 um and 56 mW, and at 16 um and 14 mW. What a smaller waist buys is
the intensity a limited power can reach. What it pays is saturation, which grows
as the square of the intensity while the shift grows as the first power, and the
axial average, which reverses the skew's sign past 1.12. Stated that way the trade
stops being a matter of opinion.

**The proposed 32 um sweet spot survives, with a different justification and a
smaller number.** The first pass claimed a thirtyfold gain from a figure of merit
built on a quadrature width and no saturation. The corrected figure is 24, and the
reason to prefer 32 um is not the size of the gain but that it is the tightest
waist that keeps the skew's sign positive while the saturation stays near a half,
where the weak-field weighting is bent by about a quarter rather than replaced.

### What has to happen before 16 um is chosen deliberately

The 16 um configuration is not ruled out. Its figure of merit is three orders of
magnitude above the present one, and the record's own plan already says that at
the small waist the SIGN is the robust observable and the magnitudes belong to a
later session. A large negative skew is a perfectly good observable. But it is a
different observable from the one the committed machinery predicts, and choosing
it deliberately needs the ramp machinery to carry saturation, which is a
contained piece of work: `stark_ramp_axial` takes an integer photon exponent, and
what the saturated case needs is the excited-fraction weight instead, with the
exponent emerging rather than being set.

Until that lands, the small-waist session's predicted skew is uncertain at the
factor-of-three level for a reason that has
nothing to do with the fringe tail or the beam divergence already in the budget.

## Design 3, 2026-08-10: which atoms resolve the fringes, over the 3D distribution

Design 1 above argues the running wave in terms of one modulation frequency
against one linewidth. That is the right shape of argument and the wrong
variable, and doing it properly over the three-dimensional Maxwell-Boltzmann
spread changes what the design has to achieve. Everything below is printed by
`scripts/run_geometry_design.py`, section DESIGN 3.

### Three velocity questions, three different components

The velocity distribution is three independent Gaussians of the same width,
196.4 m/s per component at 130 °C, and the three things that matter here read
different components of it.

**Along the beam, $v_z$, decides whether an atom sees fringes at all.** The
standing wave has period $\lambda/2$ = 496.7 nm, so an atom moving axially
sweeps through intensity maxima and minima at $2v_z/\lambda$. Fast atoms see a
modulation far above anything they can respond to and feel the time average.
Slow ones sit in a nearly fixed intensity and feel the local value, anywhere
from $(1-\sqrt{\rho})^2$ to $(1+\sqrt{\rho})^2$ times one arm.

**Across the beam, the two transverse components, decide how long an atom
interacts**, and through that the transit width, the excitation probability and
the pumping loss. Their combination is a Rayleigh distribution with mean
246.1 m/s.

**And the Doppler-free geometry selects on neither.** That is the whole point
of counter-propagating photons: the first-order shifts cancel for every atom at
once, so the narrow line is not a velocity-selected subset. The second-order
term is 0.4 kHz and is ignored throughout.

### The frozen class is small, and how small depends on a modelling choice

An atom sees a frozen fringe if it moves less than a quarter period while its
excitation stays coherent, so $|v_z| \lt \lambda/4\tau_c$. The coherence window
$\tau_c$ is the one open choice, and `rb5s6s.fringe_tail` sweeps it between the
excited-state lifetime and the crossing time. The fraction is then the
one-dimensional marginal of the three-dimensional distribution:

| cap on $\tau_c$ | $\tau_c$ | $v^*$ | fraction of atoms |
|---|---|---|---|
| excited-state lifetime | 46 ns | 5.45 m/s | 2.214 % |
| crossing time at 64 µm | 520 ns | 0.48 m/s | 0.194 % |
| crossing time at 16 µm | 130 ns | 1.91 m/s | 0.776 % |

The spread between the top and bottom rows is a factor of eleven, and it is a
modelling choice rather than a measurement, which is exactly why the fringe
tail is carried as a bracket rather than a correction.

### The running wave does not remove that class, it moves it

This is the part Design 1 got qualitatively right and quantitatively wrong.
Shifting one arm by $\Delta$ makes the pattern travel at
$v_\text{fringe} = \Delta\lambda/2$. An atom then sees the pattern pass at
$|v_\text{fringe} - v_z|$, so the atoms that still see a frozen fringe are the
ones **co-moving with it**, at $v_z \approx v_\text{fringe}$. The population
of that class is whatever the Maxwell-Boltzmann weight is there:

| $\Delta$ | $v_\text{fringe}$ | weight at that $v_z$ | residual Doppler |
|---|---|---|---|
| 40 MHz | 19.9 m/s | 0.995 | 62 Hz |
| 80 MHz | 39.7 m/s | 0.980 | 123 Hz |
| 200 MHz | 99.3 m/s | 0.880 | 309 Hz |
| 400 MHz | 198.7 m/s | 0.600 | 617 Hz |
| 800 MHz | 397.4 m/s | 0.129 | 1234 Hz |
| 1600 MHz | 794.7 m/s | 0.0003 | 2468 Hz |

So at the 80 MHz of a common AOM, 98 per cent of the frozen-fringe atoms are
still frozen. They are simply a different 2 per cent of the ensemble, sitting
at 39.7 m/s instead of at rest. **The criterion is thermal**: $\Delta$ has to
push $v_\text{fringe}$ into the tail of the distribution, not merely past a
linewidth. It becomes useful around $2\sigma_v/\lambda$ = 395 MHz, which is
where $v_\text{fringe}$ equals one standard deviation, and it is decisive an
octave above that.

### What that costs, and why the trade is comfortable

With the two arms at different frequencies the first-order Doppler no longer
cancels exactly. The residue is $\Delta v_z/c$, which smears the line by
$\Delta\sigma_v/c$, and the last column above is its full width. It grows
**linearly** in $\Delta$ while the fringe suppression improves as a **Gaussian**
in $\Delta$, so there is a wide window rather than a knife edge. At 800 MHz the
suppression is nearly eightfold and the residue is 1.2 kHz, which is 0.035 per
cent of the natural width. The design is not limited by this.

### And the contributing atoms are not a thermal sample

The last piece is the one the pumping finding of the same day forces, and it
belongs here because it is the same kind of selection.

The atoms contributing to the line are not the ensemble. A two-photon crossing
excites with a probability falling as $1/v_\perp^2$ while atoms arrive at a
rate rising as $v_\perp$, so the contributing weight goes as $1/v_\perp$ and the
mean contributing transverse speed is 157.3 m/s rather than the thermal
246.1 m/s. Slow atoms are over-represented.

Hyperfine pumping then removes preferentially the very atoms that weighting
favours, because the chance of decaying into the other ground state grows with
the dwell time. Over the unresolved branching bracket:

| branching $f$ | mean contributing $v_\perp$ | change | weight removed |
|---|---|---|---|
| 1/3 | 176.7 m/s | +12.3 % | 18.6 % |
| 2/3 | 188.2 m/s | +19.6 % | 29.6 % |

**A fifth to a third of the contributing weight is removed, and what remains is
biased fast by 12 to 20 per cent.** A faster contributing population means a
shorter effective dwell and a wider transit kernel, so this is the mechanism
behind the pumping width rather than a separate effect.

One thing it does *not* do, and the independence of the Cartesian components is
why: $v_z$ is uncorrelated with the transverse pair, so pumping biases the
transit width and leaves the frozen-fringe fraction alone. The two selections
are orthogonal, which is convenient and is not obvious in advance.

## Addendum, 2026-08-09: the collection region is smaller than assumed, and the crossing is inside reach

Written after the experimenter stated that the 993 nm focus sits close to the
collection lens rather than at the cell's mid-plane, chosen to raise the collected
solid angle. The tables above used Z_c = 2.0 mm, the middle of the envelope
`config.py` records for a source at a nominal object distance. That envelope is
too generous at the near end and the consequence runs both ways.

Z_c = L_parallel / 2M with the cathode's 12 mm axis along the beam, and M rises
steeply as the source approaches the f = 18 mm lens:

| object distance | M | Z_c | solid angle, relative |
|---|---|---|---|
| 25.2 mm | 2.5 | 2.40 mm | 1.00 |
| 24.0 mm | 3.0 | 2.00 mm | 1.10 |
| 22.0 mm | 4.5 | 1.33 mm | 1.31 |
| 21.0 mm | 6.0 | 1.00 mm | 1.44 |
| 20.5 mm | 7.2 | 0.83 mm | 1.51 |
| 20.0 mm | 9.0 | 0.67 mm | 1.59 |
| 19.5 mm | 12.0 | 0.50 mm | 1.67 |

So the choice made for signal also shrinks the axial average that suppresses the
skew. Those are not two knobs, they are one, and it happens to be turned the right
way. The axial-averaged skew across that band:

| w0 | z_R | Z_c = 2.40 | 2.00 | 1.33 | 1.00 | 0.83 | 0.67 | 0.50 mm |
|---|---|---|---|---|---|---|---|---|
| 64 um | 12.95 mm | +0.563 | +0.565 | +0.565 | +0.566 | +0.566 | +0.566 | +0.566 |
| 32 um | 3.24 mm | +0.301 | +0.402 | +0.521 | +0.550 | +0.558 | +0.562 | +0.565 |
| 24 um | 1.82 mm | -0.113 | +0.013 | +0.309 | +0.450 | +0.501 | +0.536 | +0.555 |
| 16 um | 0.81 mm | -0.386 | -0.354 | -0.231 | -0.071 | +0.062 | +0.230 | +0.402 |
| 12 um | 0.46 mm | -0.451 | -0.434 | -0.384 | -0.327 | -0.273 | -0.174 | +0.013 |

**Two results, and the second is a trap.**

First, a tight collection region removes the axial penalty almost entirely. At
Z_c below about 0.7 mm the skew is positive and within a few per cent of its
intrinsic +0.566 at every waist from 64 down to 16 um. That is the configuration
the earlier sections were looking for and did not find: the small waist's shift
gain with no axial suppression, which moves the binding constraint back onto
saturation where the second section left it.

Second, **the small-waist configuration's own zero sits inside the achievable
range.** The sign changes at Z_c/z_R = 1.12, which at 16 um is Z_c = 0.90 mm,
squarely inside the 0.5 to 2.4 mm band. Read the 16 um row: -0.071 at 1.00 mm and
+0.062 at 0.83 mm. A session that lands there measures nothing at all, whichever
sign it set out to confirm. The record's existing statement that the two-waist
sign flip survives every plausible magnification is correct on the sign and
carries the magnitude as still geometry-dependent, and this is what that
dependence looks like when the numbers are put in: the magnitude can vanish.

So the design instruction is not to pick a sign. It is to pick Z_c away from
1.12 z_R, and since the same parameter sets the photon budget, the sensible end is
the tight one. That makes the standoff from the near window, and hence the object
distance, a quantity to set deliberately and record rather than to discover
afterwards. It is currently not recorded at all.

## What this note does not settle

The collection half-length is an envelope, not a measurement: `config.py` gives
1.0 to 4.0 mm for the current imaging geometry and this note uses the middle. Z_c
is a collection-optics choice, so it is a free design variable, and aperturing the
detection axially can keep a small waist on the clean side of the crossing. That
two-dimensional optimisation over waist and collection length, folded with the
photon budget, is the natural next step and is not done here.

The saturated weight used here is the steady-state two-level excited fraction. It
inherits the same caveat the saturation companion note records: standard, correct
in the steady state that holds here, but an approximation rather than a derivation
for a two-photon transition. The weak-field branch of the same integral
reproduces the committed axial machinery to about two per cent, which is what
licenses the saturated column, and no committed number rests on it.

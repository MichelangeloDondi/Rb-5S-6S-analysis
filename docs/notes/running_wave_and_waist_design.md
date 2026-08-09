# Two geometry choices for the fixed-lock session: a running wave, and the waist

Status: DESIGN, recorded 2026-08-09. Nothing here is a result and no committed
number changes. Both calculations are in `scripts/run_geometry_design.py`, which
writes nothing, and both are reported with the first pass that was wrong beside
the answer, because in each case the error was the interesting part.

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

# EOM sidebands

*[wiki index](README.md) · technique*

What frequency ruler does a phase-modulated sweep carry, and how does a two-photon transition change that ruler's arithmetic. This page builds on no prior background. The sideband picture and the Bessel amplitudes are introduced from scratch. It sets out the one-photon and two-photon comb laws, the carrier-null depth for each, and where this repository's ruler and its design trade-off live. Not covered here: the sideband derivation is already familiar and only the two-photon consequences for reach and shape-fitting precision are wanted, a case covered by [The two-photon comb](the-two-photon-comb.md).

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## Definition

An electro-optic modulator is a crystal whose refractive index follows an
applied voltage. Driving it with a radio-frequency tone imposes a
periodically varying phase on the light passing through, equivalent to a
comb of pure tones spaced by the drive frequency. The tooth amplitudes are
[Bessel functions](bessel-functions.md) of the modulation depth $\beta$, and
the spacing is exactly the drive frequency, known as accurately as the
synthesiser that produces it.

![oscilloscope trace of five EOM sideband-pair teeth](../apparatus/2025-07-15_eom_comb_five_teeth.jpg)

*The modulator's comb as recorded on the bench: five sideband-pair teeth on an oscilloscope trace.*

The spacing is a known interval imposed on the light. Any spectral feature
the laser sweeps across is reproduced once per sideband, so a single sweep
records several copies of the same line at intervals known to many digits.
Measuring the separation of those copies in the raw axis, typically time,
converts that axis into frequency: the modulator becomes a ruler.

In a two-photon transition the arithmetic changes: the atom absorbs one
photon from each beam, so a tooth appears wherever a pair of sidebands sums
to the right total. The tooth at order $k$ therefore collects every pair
$m+m'=k$, and by Neumann's addition theorem the sum collapses:

$$A_k \propto \Big|\sum_m J_m(\beta) J_{k-m}(\beta)\Big|^2 = J_k(2\beta)^2$$

This bench's teeth do not follow that law, and the shares are measured. The
pure-phase form is rejected by `results/ruler_tooth_shares.csv` at a reduced
chi-squared of [6.11](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:chi2_red_depth_fixed:"). A free modulation depth does not
rescue it. A flat pedestal does, completely, at [0.62](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:chi2_red_depth_and_pedestal:"): the discrepancy is an
additive floor and not a depth's shape.

The excess sits in the wings, and its origin is not settled here. Both third
teeth sit above the pure-phase prediction by a comparable amount, $+2.8$ at
$k=-3$ and $+3.4$ at $k=+3$, against observed shares of
[0.0107](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:tooth_share_observed:-3") and [0.0108](../../results/ruler_tooth_shares.csv "ref:ruler_tooth_shares:tooth_share_observed:3") that agree to 0.04 sigma.
The first pair agrees to 0.01 sigma. **The second pair does not**: $k=\pm 2$
differ by 1.4 sigma and 17 per cent, with pulls of opposite sign. That is not
significant, but it is the one place a $k \to -k$ asymmetry appears, and it is
not evidence for a pedestal.

So no mechanism is claimed here. An additive floor fits the residual
completely, and an amplitude admixture is not refuted by these shares. The
absence of a significant asymmetry is weaker evidence than symmetry would be.
The fitted `signal_over_pedestal` column cannot decide it either, being built
from $J_k(2\beta)^2$, which is symmetric in $k$ by construction and not by
measurement. What the record does say is that the admixture is localised to the
carrier. The origin of the pedestal is an open question, classified as such.

The measured shares are the archive's abscissa. The Bessel form below is the
pure-modulation limit.

That collapse assumes the retro beam's modulation is in step with the forward
beam's. It is not: it lags by the round trip $2d/c$ to the mirror, so each
term in the pair sum carries a phase $e^{-i(k-m)\Omega\cdot 2d/c}$, and the
addition theorem then gives $A_k \propto J_k(2\beta\cos(\pi f\cdot 2d/c))^2$. The
depth the teeth report is that effective one, 0.3 per cent below the drive's at
12.5 MHz for a 0.3 m path, and at $f = c/4d$ every tooth collapses into the
carrier. Checked against the explicit delayed pair sum to $10^{-16}$ at five
geometries on 2026-09-06.

The pathways that feed a tooth from unequal sideband
orders are resonant with velocity classes spread by the order difference times
the modulation frequency times the speed over that of light, about 14 Hz per
unit of order difference at 12.5 MHz and the vapour's rms speed, three parts
in a million of the line, so the pair sum holds to that precision and nothing
in a trace can tell a crossover pathway from a diagonal one.

So a two-photon comb has the same form as a one-photon comb at twice the
modulation depth, with teeth one full drive step apart on the transition
axis and therefore half a step apart on the scanned laser axis: moving to
the next order shifts the summed pair by $\Omega$ while the laser itself
moves by $\Omega/2$.

![two comb shapes at different modulation depths](figures/wiki_eom_comb.png)

*The comb at two modulation depths: shallow, where nearly everything sits in
the central tooth, and beta = 1.202, where the carrier tooth nulls.*

## The problem it addresses

A laser sweep is driven by a voltage ramp, and the relation between that
ramp and the frequency it produces is neither linear nor stable enough to
trust. Without a ruler, every width in a spectrum is quoted in volts or in
milliseconds. The comb supplies the conversion from the same trace that
carries the data, so the calibration cannot drift away from the measurement
it calibrates.

## Application in this repository

The frequency axis of every trace comes from this.
[Methods chapter 3](../methods/05_the_frequency_ruler.md) derives the comb,
gives the measured sweep rate with its uncertainty, and explains why the
rate is clean: a differential measurement across several copies of the same
line, so whatever afflicts the line afflicts every copy and cancels.
[`rb5s6s/ruler.py`](../../rb5s6s/ruler.py) fits all the teeth
simultaneously.

![one EOM ruler trace with its seven-tooth comb fit and residuals](../../figures/fig8_ruler.png)

*One ruler trace and its seven-tooth comb fit, teeth spaced 6.25 MHz apart on
the laser axis, with fit residuals below.*

The comb shape also sets a design trade-off: at small modulation depth the
outer teeth sit within the central tooth's tails and are hard to resolve.
One workaround is admixing amplitude modulation via a half-wave plate to
suppress the carrier. A cleaner fix is driving at the depth that nulls the
carrier: for the two-photon comb that is $\beta \approx 1.202$, half the
value (2.405) a one-photon calculation gives.

Tooth amplitudes fall away once the order exceeds the modulation argument,
so near the carrier-null depth only the first few orders carry usable
power: the comb reaches only a few tens of megahertz around whatever line
it marks. Calibrating a wider span needs a separate frequency reference to
carry the scale across the gap.

## Failure modes

At shallow modulation depth only two or three teeth rise above the noise. A
ruler with few teeth over a short span constrains the fitted rate far less
than the same modulator would at a better depth: data insufficiency created
by the operating point, not a limit of the modulator.

A model failure: the Bessel law above holds for pure phase modulation.
Admixed amplitude modulation, whether deliberate or from a misaligned
polarisation axis, changes the tooth heights and breaks the symmetry of the
comb, so tooth amplitudes should not be used to infer $\beta$ unless the
modulation purity is established. The asymmetry is a useful diagnostic of
the modulator in its own right.

An implementation error: using $J_n(\beta)$ where the two-photon comb
requires $J_k(2\beta)$ puts the carrier null at the wrong drive amplitude by
a factor of two.

A subtler one is a calibration degeneracy. The rate and the width enter the
analysis as a product, so calibrating the rate by assuming a width cannot
then detect that the width has changed. The ruler has to be measured from
the comb itself, on the same trace, for the calibration to be independent
of what it calibrates.

## Try it

The comb at the two depths compared above.

```python
from scipy.special import jv

for beta in (0.30, 1.202):
    amps = [jv(k, 2 * beta) ** 2 for k in range(4)]
    tallest = max(amps)
    print(f"beta = {beta:.3f}: " + "  ".join(
        f"k={k} {a / tallest:.3f}" for k, a in enumerate(amps)))
print("at 1.202 the argument 2 beta reaches the first zero of J0, "
      "so the carrier vanishes")
```

Every snippet on these pages runs under `tests/test_wiki_snippets_run.py`,
so a broken one fails the suite instead of misleading a reader here.

## The spacings are known exactly, so every departure from equality is a measurement

The true spacings are exactly equal. A phase modulator driven by one synthesiser tone puts its orders at
integer multiples of that tone, and the two-photon features at half-integer multiples of it, to the
accuracy of a frequency standard. So every departure of the measured spacings from equality is an
artefact, and its pattern names which artefact it is.

| pattern of the departure | what it is |
|---|---|
| a smooth trend across the trace | the sweep's nonlinearity |
| adjacent pairs pulled together where they overlap | the fitter's own blending bias |
| a feature at a spacing that is not a multiple | harmonic distortion in the radio drive |
| an asymmetry between the $+k$ and $-k$ sides | residual amplitude modulation |

**The second row is the one that bears on a quantity this record quotes.** Two partially overlapping
features bias each other's fitted centres toward the blend, so a measured spacing shrinks where the
features are close. The same bias acts on the line centre, which is what the light-shift measurement
reads. It grows as the features approach, so it grows with the width, so it grows with the temperature:
a centre bias that varies across the temperature arm and would be read as physics if the comb were not
there to expose it. Nothing in the present model carries it.

**And the whole comb is an in-situ closure with a known answer, on real traces.** This record validates
its estimators by injecting a known value into synthetic data and asking for it back, and the waist
closure has just returned a structural bias on exactly that route. The comb offers the same test on real
data: the answer, equal spacings, is known in advance by construction, and any departure is the analysis
chain's own bias measured on the very traces the physics comes from, with the real noise, the real
baseline, the real detector and the real line shape. **A closure that runs on the data and not on a
simulation of it is worth more than either, because it cannot be wrong about the generator.**

So the measurement is cheap and it should be standing: fit every comb feature, take the successive
differences, and publish them. Their mean calibrates the axis, their trend gives the sweep nonlinearity,
their behaviour against separation gives the blending bias, and their scatter is the floor on any centre
this record quotes. None of it needs a new acquisition.

## Two observables the comb reaches that nothing else here does

**The hyperfine branching, which is a model input this record currently takes on theory.** The transit
and the F statistics are one non-equilibrium process here: atoms enter from the walls with thermal F
populations, are excited along the chord, and cascade with a computed probability into the other ground
hyperfine level, depleting the excitable population as they cross. That depletion is a function of the
excitation rate, and the branching probability is what sets how much of it is permanent rather than
recoverable. The comb varies the rate by an order of magnitude at fixed power, fixed alignment, fixed
volume and fixed temperatures, so the rate-dependence of the line across orders is a direct measurement
of the branching that the model presently supplies from calculation. It is the same measurement as the
saturation reading and it is a different parameter read out of it, because permanent loss into the other
level and reversible saturation have different rate dependences: one accumulates along the chord and the
other does not.

**The far-wing form, which the record flags as a model-form question and cannot currently probe
cleanly.** At a large depth the outer orders land far from line centre, out to about six tooth spacings,
so the comb places calibrated probes in the wing while the core is present in the same trace. The
record's per-session admission test already separates wing samples from core samples and grades them
against different references, and it draws them today from different parts of a swept trace with whatever
baseline lies between. The comb draws both at once, at known offsets, with known relative weights, so the
wing's shape is sampled at discrete points whose expected amplitudes are fixed by the measured shares. A
Lorentzian wing and any alternative predict different ratios between those points, which is a model-form
test and not a fitted parameter, and it is available from the traces a ruler acquisition already
takes.

**What the comb still cannot reach, restated because the list above is tempting.** Anything common to
every feature stays common: the light shift, the differential polarizability behind it, the permeated
gas, the collisional width and the Zeeman shift are properties of the levels or of the whole vapour, and
no comparison across the comb touches them. The comb is a lever on what depends on the rate, on what
depends on the instrument, and on what depends on position along the axis. It is silent on everything
else, and a campaign built on it should budget the observables it cannot reach to the knife-edge, to the
permeation log and to the temperature arm.

## The comb sorts systematics into common-mode and per-feature, and one it cannot reach

The comb's power over systematics comes from one structural fact: its features are coherent copies of one
Field measured at one instant through one chain. So every systematic divides cleanly into those that act
on all features alike and those that do not, and the comb separates the two classes without a model of
either.

| systematic | acts on the comb | where it shows |
|---|---|---|
| laser frequency jitter and drift | common to every feature | the comb's centroid moves, the relative positions do not |
| sweep nonlinearity | position-dependent | the separations between adjacent features depart from equality |
| laser amplitude noise | common in amplitude | the total fluctuates, the feature ratios do not |
| shot and detector noise | independent per feature | the ratios scatter |
| detector nonlinearity | amplitude-dependent | the ratios drift with total power |
| residual amplitude modulation | antisymmetric in order | the $+k$ and $-k$ weights differ |

Read as a recipe: the relative positions within a trace measure the axis and are blind to the laser's
frequency noise. the common centroid measures the laser's frequency noise and is blind to the axis. the
feature ratios measure the detector and are blind to the laser's amplitude noise. and the total measures
the amplitude noise. Four systematics, four observables, each blind to the others, all in one acquisition.
The record currently estimates several of these between traces, where they are entangled with everything
else that varies between acquisitions.

**And the firm negative, written so that nobody proposes it.** The EOM cannot measure the laser's
linewidth. A two-photon transition driven from one beam absorbs both photons essentially simultaneously,
so both carry the same instantaneous laser phase and the two-photon phase noise is twice that phase for
every feature of the comb, whatever its order. Every feature therefore has the same laser-noise
contribution to its width and no comparison between them reaches it. The same argument closes the
self-heterodyne route: a beat between the carrier and a sideband is the radio frequency itself, because
the two are coherent copies with no delay between them, and a self-heterodyne linewidth measurement needs
a delay longer than the coherence time. The laser width stays degenerate with the transit width and the
knife-edge stays the measurement that breaks it.

## Two more the crossovers give: the sweep's own nonlinearity, and a width meter that is an integer

**The comb measures the sweep's nonlinearity inside every trace, not merely its scale.** A ruler that
gives one number calibrates an axis globally. the comb puts markers at exactly equal spacings across the
Whole sweep, so the measured separation between adjacent features is a function of position along the
trace. Any departure of those separations from equality is the sweep nonlinearity, measured where it
occurs, in the same acquisition as the data it distorts. This record currently carries sweep linearity as
a modelled systematic and reads the axis from the ruler's scale. the crossovers turn it into a per-trace
measurement with no extra data and no assumption about the sweep's functional form. It is also the one
systematic that a frequency-axis calibration cannot remove by scaling, because it varies within the
trace.

**And the count of resolved crossovers is a width meter immune to every amplitude calibration.** As the
line broadens the features merge, one pair at a time, so the number still resolved is an integer that
steps down as the width grows. An integer cannot be moved by gain drift, by baseline error, by detector
nonlinearity or by any error in the tooth shares. It is coarse, one step per merge, and it is the most
robust width statement this apparatus can make: where the contrast method of the section above needs the
measured shares to invert, the count needs nothing at all. The two together give a robust bracket and a
precise reading inside it, which is the right shape for a quantity whose systematic is the thing under
suspicion.

## What these crossovers are, and what they are not

**These are modulation crossovers and not velocity crossovers, and the distinction is physical.** In
saturated absorption the word names a feature produced by a velocity class shared between two
transitions, sitting midway between them. A Doppler-free two-photon transition selects no velocity class
at all, since the counter-propagating pair cancels the first-order Doppler for every atom, so **no
velocity crossover exists here and none can**. Every half-integer feature in this spectrum is a
modulation crossover, produced by two components of the comb and not by two velocity classes. That
makes the identification unambiguous in a way saturated-absorption spectra never are: a feature at a half
tooth spacing is a modulation crossover by construction, it moves with the synthesiser and not with the
line, and it vanishes when the radio frequency is switched off within the same sweep. A reader arriving
from saturated absorption will assume the other meaning, and the record should say which it means
wherever it uses the word.

**And the coincidence condition measures the line splittings against the synthesiser.** Tune the tooth
spacing until order $k$ of one hyperfine line falls exactly on the centre of another: the coincidence
fixes that splitting at $k f_\text{RF}/2$, with the accuracy of the radio frequency and not of the
wavemeter. This record states plainly that its peak labels come from an uncalibrated wavemeter and
identify lines without measuring them, so the splittings it uses as a ruler are taken rather than
measured here. The coincidence turns them into an in-situ measurement, removes a literature dependence
from the frequency axis, and costs one scan of the synthesiser with the laser parked. The same scan is
also how a spacing is chosen to avoid coincidences, which matters because an accidental overlap fills a
crossover's valley and reads as width in the contrast method above.

## The optical null and the two-photon null are different depths

The optical spectrum carries $J_k(\beta)$ and the two-photon spectrum carries $J_k(2\beta)$, so the two
vanish at different modulation depths. At $\beta = 1.20241$ the two-photon line centre is extinguished
while the optical carrier still holds 45 per cent of the power. At $\beta = 2.40483$ the optical carrier
is extinguished completely and the two-photon centre still keeps **5.6 per cent** of its unmodulated rate,
because a photon from $+m$ and a photon from $-m$ sum to exactly the carrier two-photon energy. With no
light at all at the carrier frequency the resonance is still driven, by sideband pairs alone.

That makes a depth scan a test of the transition's order. A feature following $J_0(\beta)^2$ is not
two-photon and one following $J_0(2\beta)^2$ cannot be single-photon, and the two laws are separated by
the position of the null, which no amplitude calibration is needed to read.

## The crossovers are the half-integer features, and they can outshine the centre

A pair of components with orders $m$ and $n$ is resonant when the laser sits $(m+n)/2$ tooth spacings from
line centre, so the spectrum carries features at half-integer multiples of the RF frequency. Those
half-integer features exist only because two different components combine and have no single-photon
counterpart. At the optical null their weights, in units of $f_\text{RF}/2$, read 0.0564, 0.0901, 0.0127,
0.1552 and 0.1434 for $k$ from zero to four, so the first and third crossovers are 1.6 and 2.8 times the
centre. A depth scan redistributes the spectrum and not dimming it.

Whether they are usable is set by the width against half the tooth spacing, and the width rises with the
vapour temperature through the motional terms and far more steeply with the cold-spot temperature through
the self-broadening. So the crossovers wash out from the hot end, a tooth spacing is chosen against the
hottest condition a campaign intends to run, and the depth at which a crossover disappears is a contrast
reading of the total width that never passes through the lineshape fit.

## Modulating costs shift information, and buys a direction instead

The two-photon weights sum to one at every depth, so the comb redistributes the signal and never destroys
it. That does not mean the precision is preserved. The replicas share the same photons, so splitting a
fixed count among more peaks divides the signal and its shot noise together. Computed over the whole comb
with shot noise at every point, the Fisher information on a common frequency shift reads 1.000 unmodulated,
0.808 at a depth of 1.20 and 0.764 at 2.40: modulating to the optical null costs about a quarter of it.

So the reason to modulate is not precision. It is that the depth walks the excitation rate against a light
shift the sum rule holds fixed, which is a direction no power sweep reaches, and that the null positions
test the transition's order with no amplitude calibration. The replicas buy redundancy against a
systematic acting on part of the spectrum. A quarter of the shift information is what it costs for those.

## The depth is a knob that breaks a degeneracy, not only a ruler setting

Phase modulation conserves total power, since the Bessel squares sum to one, so the total AC-Stark shift
does not move with the modulation depth: every component shifts the levels whether or not it is resonant.
The two-photon amplitude at order zero goes as $J_0(2\beta)^2$, so the on-resonance rate falls while the
Shift stays put. Depth therefore walks the rate against a fixed shift, which is a direction a power sweep
cannot reach at any power, because there the two move together.

The acquisition form is sharper than the analysis form. Holding the carrier amplitude fixed and raising
total power as the depth opens keeps the excitation rate constant by construction and moves the shift
alone, so the signal stays where the detector wants it while the quantity under study varies.

Two cautions belong with it. The measured tooth shares depart from the ideal form above, so the shares are
measured per setting and carried as data, and the depth labels a configuration instead of being inferred
from the shares. And the tooth spacing sets where the crossovers fall, whose contrast washes out as the
line broadens with the vapour temperature, so a spacing is chosen against the hottest condition a campaign
intends to run and is quoted with that temperature or not at all.

## Further reading

- G. C. Bjorklund, "Frequency-modulation spectroscopy: a new method for
  measuring weak absorptions and dispersions", *Opt. Lett.* **5**, 15 (1980),
  for the sideband formalism.
- [Bessel functions](bessel-functions.md) for the amplitude law and the
  Jacobi-Anger identity behind it.
- [Methods chapter 3](../methods/05_the_frequency_ruler.md) for this
  bench's numbers and common-mode rejections.

## Related pages
- [The two-photon comb](the-two-photon-comb.md) for what the doubled
  argument costs in reach and fitting precision.
- [Bessel functions](bessel-functions.md) for the addition theorem and
  power-conservation identity behind the collapse above.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md)
  for how this differential ruler compares against absolute references.

---

[← wiki index](README.md) · *Driving, modulating and detecting, 1 of 8* · [The two-photon comb →](the-two-photon-comb.md)

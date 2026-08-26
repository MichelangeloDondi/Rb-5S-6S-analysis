# EOM sidebands

*[wiki index](README.md) · technique*

**The question.** What frequency ruler does a phase-modulated sweep carry,
and how does a two-photon transition change that ruler's arithmetic.
**Takes.** No prior background. The sideband picture and the Bessel
amplitudes are introduced from scratch.
**Gives.** The one-photon and two-photon comb laws, the carrier-null depth
for each, and where this repository's ruler and its design trade-off live.
**Skip if.** The sideband derivation is already familiar and only the
two-photon consequences for reach and shape-fitting precision are wanted,
a case covered by [The two-photon comb](the-two-photon-comb.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

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

So a two-photon comb has the same form as a one-photon comb at twice the
modulation depth, with teeth one full drive step apart on the transition
axis and therefore half a step apart on the scanned laser axis: moving to
the next order shifts the summed pair by $\Omega$ while the laser itself
moves by $\Omega/2$.

![two comb shapes at different modulation depths](figures/wiki_eom_comb.png)

*The comb at two modulation depths: shallow, where nearly everything sits in
the central tooth, and beta = 1.202, where the carrier tooth nulls.*

## What problem it solves

A laser sweep is driven by a voltage ramp, and the relation between that
ramp and the frequency it produces is neither linear nor stable enough to
trust. Without a ruler, every width in a spectrum is quoted in volts or in
milliseconds. The comb supplies the conversion from the same trace that
carries the data, so the calibration cannot drift away from the measurement
it calibrates.

## Where this repository uses it

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

## What can go wrong

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

## Further reading

- G. C. Bjorklund, "Frequency-modulation spectroscopy: a new method for
  measuring weak absorptions and dispersions", *Opt. Lett.* **5**, 15 (1980),
  for the sideband formalism.
- [Bessel functions](bessel-functions.md) for the amplitude law and the
  Jacobi-Anger identity behind it.
- [Methods chapter 3](../methods/05_the_frequency_ruler.md) for this
  bench's numbers and common-mode rejections.

## See also

- [The two-photon comb](the-two-photon-comb.md) for what the doubled
  argument costs in reach and fitting precision.
- [Bessel functions](bessel-functions.md) for the addition theorem and
  power-conservation identity behind the collapse above.
- [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md)
  for how this differential ruler compares against absolute references.

---

[← wiki index](README.md) · *Driving, modulating and detecting, 1 of 8* · [The two-photon comb →](the-two-photon-comb.md)

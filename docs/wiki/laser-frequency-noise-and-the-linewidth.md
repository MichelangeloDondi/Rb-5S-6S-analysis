# Laser frequency noise and the linewidth

*[wiki index](README.md) · concept*

**The question.** What does "the laser linewidth" actually mean, and why does
the same laser have different widths in different measurements?
**Takes.** [Shot noise and technical noise](shot-noise-and-technical-noise.md)
for the idea of a noise spectrum. Nothing else.
**Gives.** The map from a frequency-noise spectrum to a lineshape, why the
width depends on the band the measurement samples, and why the KERNEL a fit
assigns to the laser is a physics claim with a bias attached.
**Skip if.** You want the detector's noise rather than the laser's, which is
[the noise law](the-noise-law.md). The two are different quantities, and
conflating them is this page's first warning.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A laser's frequency wanders. The complete description is the frequency-noise
spectral density $S_\nu(f)$, the power of the wandering at each Fourier
frequency, and every statement about "the linewidth" is a compression of that
function into one number. The compression loses information, and which
information it loses depends on the noise type.

Two limits organise everything. **Fast noise**, where $S_\nu$ is flat (white
frequency noise), produces a LORENTZIAN line whose width is set by the noise
level alone. **Slow noise**, where the power sits at low frequency, produces
a GAUSSIAN line: the laser sits at a slowly moving frequency and the line is
the histogram of where it sat. Real lasers are between the two, and the
useful boundary is the beta-separation line: noise at Fourier frequencies
where $S_\nu(f) \gt 8\ln 2\ f/\pi^2$ contributes Gaussian width, and noise
below that threshold contributes wings.

The consequence that matters in practice: **the Gaussian part depends on how
long you look.** An observation of duration $T$ samples the noise from
roughly $1/T$ upward, so lengthening the observation admits more slow noise
and widens the measured line. "The linewidth" without its observation time is
not a specification.

## What problem it solves

A lineshape fit has to give the laser a kernel, and the choice is a physics
claim about $S_\nu$ rather than a convenience. The two candidates fail
differently. A GAUSSIAN kernel is right for slow noise, and if the truth is
fast, the real laser contribution is Lorentzian, which the fit then absorbs
into whatever other Lorentzian it holds, typically the collisional width.
That is a BIAS on a physical coefficient, not an inflated error bar. A
LORENTZIAN kernel has the mirror problem.

The same trap in instrument form: an external linewidth measurement is only
usable if its band matches the spectroscopy's. A scanning cavity that watches
the laser for seconds samples down to sub-hertz frequencies, while a line
crossed in forty milliseconds samples nothing below about twenty hertz. Under
low-frequency-heavy noise the two instruments report different widths for the
same laser, both correctly, and transplanting one number into the other's
band is a bias no averaging removes. The transportable object is $S_\nu(f)$
itself, never a single width.

```python
import numpy as np

# The same laser at three observation times, under 1/f frequency noise.
# S_nu = h1/f, and the Gaussian FWHM is sqrt(8 ln2 * integral over the band).
h1 = 4.9e10                      # Hz^2, an illustrative flicker coefficient
f_high = 1.5e6                   # Hz, the fast cutoff (inverse transit time)
LN2_8 = 8 * np.log(2)
for T_obs in (4.1e-3, 41e-3, 0.41):
    A = h1 * np.log(f_high * T_obs)          # band integral, 1/T to f_high
    fwhm = np.sqrt(LN2_8 * A) / 1e6
    print(f"observed for {T_obs*1e3:6.1f} ms -> Gaussian FWHM {fwhm:.2f} MHz")
print("one laser, three linewidths, each correct in its own band")
```

## Where this repository uses it

**The record fits a Gaussian laser kernel and states plainly that this is an
assumption** ([CLAIMS.md](../CLAIMS.md) section 2). The lineshape data cannot
settle the kernel: the model-form comparison of M8 puts a Gaussian against a
cusped exponential at $\Delta\text{BIC}$ between -0.1 and +3.7, which is
indistinguishable at this record's own gate.

**The record measures $S_\nu$ on three rungs, and none of them is the rung
that broadens the line.** The digitised wavemeter record of M22 puts
0.62 MHz rms of unmodelled laser motion BELOW 0.5 Hz, once re-lock kicks and
the scan ramps are removed. The comb clock bounds the excursion at 7 Hz
below 28 kHz. The width channel integrates from 24 Hz up, and in that band
the only handle is the fitted width, an upper bound degenerate with the
transit width through the beam waist. Read together the three rungs say the
spectrum falls steeply through the decade below the width band, which is
what a drift-and-kick-dominated laser looks like, and they leave the width
band itself measured by nothing. The measured noise law of M1 is the
DETECTION noise on the photodiode voltage, a different quantity again.

**What the record does hold is one direct in-situ statement**, the comb read
as a clock ([the wavemeter page](the-wavemeter-and-the-frequency-axis.md)):
the non-repeating excursion is below 28.3 kHz on the transition axis at an
averaging time of 0.15 s. That bound excludes the low-frequency-heavy
spectra by large factors, seventeen for flicker and eighty for a random
walk, which is evidence AGAINST the Gaussian kernel's justification rather
than for it. The measurement that settles the question, the frequency-noise
spectrum from the lock's own error signal, has not been made and costs no
cell time.

## Catching a narrow line with the line itself

A mains hum is not broadband noise but a LINE, and a line at a known
frequency is best sought by demodulation. The lineshape supplies its own
demodulator: on a flank, frequency wobble times the flank slope becomes
voltage wobble at the same frequency, so laser FM appears at the mains
frequency with OPPOSITE sign on the two flanks, while electronic pickup and
intensity noise appear with the SAME sign. That sign flip is the
discriminator, it needs no comb and no extra hardware, and its sensitivity
is set by the flank slope, which for a deep line beats a tooth-position
clock by an order of magnitude at the same noise. A diagnostic run of
exactly this test on the 2025 traces found no mains-scale line, and the
committed producer that will carry its number is pending, so the number is
not quoted here.

## What can go wrong

**Quoting a linewidth without its band.** The number is not portable. Carry
the observation time, or better, carry $S_\nu$.

**Reading a converged fit as a validated kernel.** A Voigt fit converges
happily on a line whose Lorentzian part is mislabelled, and the misfit lands
in the physical coefficient sharing that shape.

**Estimating slow noise with a statistic that has no limit.** Under $1/f$
noise the variance of a record GROWS with the record, so the raw scatter of
line centres saturates at the same fractional spread however long you
measure, and it looks like a convergence plateau while being nothing of the
kind. The [Allan deviation](allan-deviation.md) at fixed averaging time is
the statistic built for exactly this, and it converges as $1/\sqrt{N}$ on
the same data.

**Trusting the noise floor of the instrument instead of the band of the
instrument.** A measurement can be far more precise than the width it
reports and still report the wrong width for your use, because a band
mismatch is a systematic, not a noise.

## What this repository got wrong once

For most of one day, 2026-08-19, a design study sized a scan-rate ladder on
the assumption that the fitted 1.4 MHz Gaussian was flicker laser noise. The
record's own numbers then dismantled the assumption twice over: the measured
centre stability within a scan sits seventy-five times below what that
flicker would produce, and the comb-clock bound came in seventeen to eighty
times below the low-frequency spectra generally. The scan-rate lever the
model had promised shrank by a factor of nine, to below usefulness, and the
honest conclusion inverted: whatever broadens the line is FAST or is not the
laser, and if fast, the Gaussian kernel is the wrong shape and the bias runs
into the collisional width. The mistake is this page's thesis in miniature, a
noise TYPE assumed where only a noise SPECTRUM would do, and a day spent
computing consequences of the assumption rather than measuring it.

## Further reading

Di Domenico, Schilt and Thomann, "Simple approach to the relation between
laser frequency noise and laser line shape" (Applied Optics 49, 4801, 2010),
is the beta-separation-line paper. Any frequency-metrology text carries the
Allan-variance route from $S_\nu$ to a width and back.

## See also

[The noise law](the-noise-law.md), the detector's noise, which this page is
not · [Allan deviation](allan-deviation.md), the statistic that survives
$1/f$ · [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md),
where the comb-clock bound lives · [Shot noise and technical noise](shot-noise-and-technical-noise.md),
the same band-thinking on the detection side · [Identifiability](identifiability.md),
what the kernel choice does to the width budget · [The Voigt profile](voigt-profile.md),
the convolution the kernel enters

---

[← The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md) · *Driving, modulating and detecting, 4 of 8* · [Sweep rate and detection lag →](sweep-rate-and-detection-lag.md)

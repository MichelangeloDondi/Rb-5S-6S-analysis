*Chapter 1 of 8 · [methods index](../methods.md)*

**The question.** What was measured, on what apparatus, and why does driving a
two-photon transition from both sides remove the Doppler width?
**Takes.** Nothing. This is the first chapter.
**Gives.** The apparatus, the four hyperfine lines and the labels used for them
everywhere else, and the Doppler-cancellation condition every later chapter
assumes.
**Skip if.** You already know the OIST 993 nm two-photon bench, in which case
start at the lineshape chapter.

## 1. The measurement

A hot Rb vapour cell is illuminated by a 993 nm laser beam retro-reflected onto
itself, forming two counter-propagating fields. The beam is focused into the
cell by a lens (L1, $f=150$ mm); a second identical lens (L2) after the cell and
a flat mirror behind it return the beam along its own path — a self-imaging
arrangement that re-forms the same waist at the atoms on the return pass
([§2.6](03_the_ac_stark_ramp.md)). The laser frequency is slowly
swept across the two-photon $5S_{1/2}\to 6S_{1/2}$ transition while the
resulting fluorescence is recorded versus time — one such record is a
"trace" (mapped onto a frequency axis in
[the frequency-ruler chapter](05_the_frequency_ruler.md)). The observed narrow resonance
arises from atoms absorbing one photon from each counter-propagating beam, for
which the first-order Doppler shifts cancel (§1.1). The excited $6S_{1/2}$
state can decay through several channels; here we detect only the
$6S\to 5P_{1/2}\to 5S$ cascade, collecting the emitted 795 nm photons on a PMT
behind 50 dB of 795 nm filtering. Four hyperfine components are measured,
labelled by wavelength: 993.4207 nm (⁸⁷Rb $F{=}2\to2$), 993.4192 nm
(⁸⁵Rb $F{=}3\to3$), 993.4154 nm (⁸⁵Rb $F{=}2\to2$), 993.4121 nm
(⁸⁷Rb $F{=}1\to1$). Throughout we write these full labels; in code and
filenames the last four digits ("4207") are the key, and `constants.peak_label()`
renders the full form for all output. The readings come from an uncalibrated
wavemeter, so they identify the lines rather than measure them; the hyperfine
assignments are what fix which line is which.

![the level scheme](../../figures/fig13_level_scheme.png)

*Left: two 993 nm photons, one from each direction of the retro-reflected beam,
drive 5S₁/₂ → 6S₁/₂ through a virtual level that lies **below** the real 5P₁/₂;
taking one photon from each beam is what cancels the first-order Doppler shift.
The state is detected not directly but on the 795 nm arm of the 6S → 5P₁/₂ → 5S
cascade, the 780 nm arm being suppressed by about 50 dB. The 5P fine-structure
splitting is enlarged for legibility rather than drawn to scale. Right: the four
hyperfine components measured, two per isotope, all F → F, labelled by
uncalibrated wavemeter reading. Each is crossed once per sweep direction, so the
down-sweep repeats the same four mirrored about the ramp apex. Their relative
strengths follow the ground-state populations, abundance × (2F+1)/G_iso, which
predicts ⁸⁵Rb F = 3 at 7/5 = 1.40 times F = 2 against 1.42 integrated from the
digitised record on the up-sweep, 1.34 to 1.42 across integration rules, and the
⁸⁵Rb pair at the bare abundance ratio 2.59 times the ⁸⁷Rb pair against 2.45
measured. The photographed display compresses the tallest spikes and the whole
down-sweep, so peak heights are not read for ratios. The integration rules and
their caveats are [APPARATUS §6](../APPARATUS.md).*

### 1.1 Why two counter-propagating photons kill the Doppler width

An atom moving with velocity component $v$ along the beam sees a photon of lab
frequency $\nu$ shifted to $\nu(1+v/c)$ if it travels toward the source and
$\nu(1-v/c)$ if away. Absorbing one photon from each of the two
counter-propagating directions, the atom's two-photon resonance condition is

$$\nu\Big(1+\tfrac{v}{c}\Big) + \nu\Big(1-\tfrac{v}{c}\Big) = 2\nu$$

and the velocity term cancels **exactly to first order in $v/c$, for every
atom**. Without this trick the line would be Doppler-broadened to
$\sim 500$ MHz (the thermal spread); with it, the ~500 MHz smear collapses
and we are left with a line only a few MHz wide, whose residual width is the
stack of mechanisms below. (A second-order Doppler term $\propto (v/c)^2$
survives but is $\sim$ kHz here — negligible.)

This is the same cancellation condition that
[Biraben, Cagnac and Grynberg](../lit/biraben1974.md) first demonstrated
experimentally (*Phys. Rev. Lett.* **32**, 643 (1974)): driving the analogous
3S–5S transition in sodium, they showed the Doppler pedestal vanishes only
when the atom is forced to take one photon from each counter-propagating
beam, not merely by illuminating with a standing wave. That founding result
covers the demonstration and the algebra above. The transit-time lineshape
our line actually has, once a finite crossing time is added, is a separate,
later result, covered next in [§2, the lineshape kernel by
kernel](02_the_lineshape.md).

---

**Where the numbers live.** Modules M0 (ingest and QC) · producers
`scripts/run_qc.py` · results `results/qc_metrics.csv` · figures
`figures/fig13_level_scheme.png`. The line labels, the 6S lifetime and the
natural width are held in `rb5s6s/constants.py`.

**What would falsify this.** A hyperfine assignment that put a different
$F\to F$ pair behind one of the four wavemeter labels. The readings are
uncalibrated, so the assignment and not the reading is what identifies a line,
and the spacings between the four are the check on it.

[← methods index](../methods.md) · [The lineshape, kernel by kernel →](02_the_lineshape.md)

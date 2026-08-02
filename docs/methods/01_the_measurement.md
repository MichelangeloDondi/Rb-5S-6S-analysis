*Chapter 1 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

## 1. The measurement

A hot Rb vapour cell is illuminated by a 993 nm laser beam retro-reflected onto
itself, forming two counter-propagating fields. The beam is focused into the
cell by a lens (L1, $f=150$ mm); a second identical lens (L2) after the cell and
a flat mirror behind it return the beam along its own path — a self-imaging
arrangement that re-forms the same waist at the atoms on the return pass
([§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)). The laser frequency is slowly
swept across the two-photon $5S_{1/2}\to 6S_{1/2}$ transition while the
resulting fluorescence is recorded versus time — one such record is a
"trace" (mapped onto a frequency axis in [§3 — From volts to a frequency axis](05_the_frequency_ruler.md)). The observed narrow resonance
arises from atoms absorbing one photon from each counter-propagating beam, for
which the first-order Doppler shifts cancel (§1.1). The excited $6S_{1/2}$
state can decay through several channels; here we detect only the
$6S\to 5P_{1/2}\to 5S$ cascade, collecting the emitted 795 nm photons on a PMT
behind 50 dB of 795 nm filtering. Four hyperfine components are measured,
labelled by wavelength: 993.4207 nm ($^{87}$Rb $F{=}2\to2$), 993.4192 nm
($^{85}$Rb $F{=}3\to3$), 993.4154 nm ($^{85}$Rb $F{=}2\to2$), 993.4121 nm
($^{87}$Rb $F{=}1\to1$). Throughout we write these full labels; in code and
filenames the last four digits ("4207") are the key, and `constants.peak_label()`
renders the full form for all output. The readings come from an uncalibrated
wavemeter, so they identify the lines rather than measure them; the hyperfine
assignments are what fix which line is which.

![the level scheme](../../figures/fig13_level_scheme.png)

*Left: two 993 nm photons, one from each direction of the retro-reflected beam,
drive 5S₁/₂ → 6S₁/₂ through a virtual level that lies **below** the real 5P₁/₂;
taking one photon from each beam is what cancels the first-order Doppler shift.
The state is detected not directly but on the 795 nm arm of the 6S → 5P₁/₂ → 5S
cascade. Right: the four hyperfine components measured, two per isotope, all
F → F, labelled by uncalibrated wavemeter reading.*

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

---

[← methods index](../methods.md) · [The lineshape, kernel by kernel →](02_the_lineshape.md)
